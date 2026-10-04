"""Read a slice of the official Open Bandit Dataset zip with HTTP range requests (no full download).

The zip (about 413 MB, https://research.zozo.com/data_release/open_bandit_dataset.zip, linked from
https://research.zozo.com/data.html) supports `Accept-Ranges: bytes`. This tool reads its central directory, then
streams one member's deflate data from the start up to a byte budget and decompresses it on the fly. The result is a
time-ordered prefix of that CSV (rows are sorted by timestamp), written to gitignored .data/obd_slice/.

Usage (from perceptron-p03-off-policy-eval/):
  .venv/bin/python eval/obd_zip_slice.py --list
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/random/all/all.csv --budget_mb 30    # full file (22.1 MB)
  .venv/bin/python eval/obd_zip_slice.py --member open_bandit_dataset/bts/all/all.csv --budget_mb 100      # time-ordered prefix
"""
from __future__ import annotations

import argparse
import struct
import sys
import time
import urllib.request
import zlib
from pathlib import Path

URL = "https://research.zozo.com/data_release/open_bandit_dataset.zip"
ROOT = Path(__file__).resolve().parents[1]


def get_range(start: int, end: int) -> bytes:
    for attempt in range(5):
        try:
            req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except Exception as e:  # flaky network tonight
            if attempt == 4:
                raise
            print(f"retry {attempt + 1}: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))


def total_size() -> int:
    req = urllib.request.Request(URL, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers["Content-Length"])


def central_directory():
    size = total_size()
    tail = get_range(max(0, size - 65_536 - 22), size - 1)
    i = tail.rfind(b"PK\x05\x06")
    _, _, _, _, n_entries, cd_size, cd_off, _ = struct.unpack("<IHHHHIIH", tail[i:i + 22])
    j = tail.rfind(b"PK\x06\x07")  # ZIP64 end-of-central-directory locator
    if j != -1:
        (z64_off,) = struct.unpack("<Q", tail[j + 8:j + 16])
        z = get_range(z64_off, z64_off + 55)
        n_entries, cd_size, cd_off = struct.unpack("<QQQ", z[32:56])
    cd = get_range(cd_off, cd_off + cd_size - 1)
    entries, p = [], 0
    for _ in range(n_entries):
        (sig, _, _, _, method, _, _, _, csize, usize, nlen, xlen, clen, _, _, _, loff) = struct.unpack(
            "<IHHHHHHIIIHHHHHII", cd[p:p + 46])
        assert sig == 0x02014B50
        name = cd[p + 46:p + 46 + nlen].decode()
        extra = cd[p + 46 + nlen:p + 46 + nlen + xlen]
        vals = [v for v in (usize, csize, loff)]
        k = 0
        while k < len(extra):  # ZIP64 extended information
            hid, hlen = struct.unpack("<HH", extra[k:k + 4])
            if hid == 0x0001:
                data, q = extra[k + 4:k + 4 + hlen], 0
                for idx, v in enumerate(vals):
                    if v == 0xFFFFFFFF:
                        vals[idx] = struct.unpack("<Q", data[q:q + 8])[0]
                        q += 8
            k += 4 + hlen
        entries.append(dict(name=name, method=method, usize=vals[0], csize=vals[1], offset=vals[2]))
        p += 46 + nlen + xlen + clen
    return entries


def iter_member(entry: dict, budget_bytes: int, chunk: int = 4 << 20):
    """Yield (header_line, block_of_complete_lines, stats) while streaming one member's deflate data."""
    head = get_range(entry["offset"], entry["offset"] + 29)
    nlen, xlen = struct.unpack("<HH", head[26:30])
    start = entry["offset"] + 30 + nlen + xlen
    stop = start + min(entry["csize"], budget_bytes)
    d = zlib.decompressobj(-15)
    header, pending, pos, got = None, b"", start, 0
    while pos < stop:
        raw = get_range(pos, min(pos + chunk, stop) - 1)
        got += len(raw)
        pos += len(raw)
        buf = pending + d.decompress(raw)
        if header is None:
            nl = buf.find(b"\n") + 1
            header, buf = buf[:nl], buf[nl:]
        cut = buf.rfind(b"\n") + 1
        pending = buf[cut:]
        yield header, buf[:cut], dict(compressed_read=got, compressed_total=entry["csize"])


def slice_compact(entry: dict, budget_bytes: int, out: Path) -> dict:
    """Keep only the columns the evaluation needs; user features stored as 64-bit hashes."""
    import io

    import numpy as np
    import pandas as pd

    keep = ["timestamp", "item_id", "position", "click", "propensity_score"] + [f"user_feature_{i}" for i in range(4)]
    parts, stats = [], {}
    for header, block, stats in iter_member(entry, budget_bytes):
        if not block:
            continue
        df = pd.read_csv(io.BytesIO(header + block), usecols=keep)
        part = {
            "ts": pd.to_datetime(df["timestamp"], format="ISO8601", utc=True).dt.as_unit("ns").astype("int64").to_numpy(),
            "item": df["item_id"].to_numpy(np.int16),
            "pos": df["position"].to_numpy(np.int8),
            "click": df["click"].to_numpy(np.int8),
            "ps": df["propensity_score"].to_numpy(np.float64),
        }
        for i in range(4):
            part[f"uf{i}"] = pd.util.hash_array(df[f"user_feature_{i}"].to_numpy(object))
        parts.append(part)
        n = sum(len(p["ts"]) for p in parts)
        print(f"  {stats['compressed_read'] / 1e6:7.1f}/{entry['csize'] / 1e6:.1f} MB compressed read, {n:,} rows", file=sys.stderr)
    arrays = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **arrays)
    return dict(member=entry["name"], rows=len(arrays["ts"]), complete=stats["compressed_read"] >= entry["csize"],
                compressed_read=stats["compressed_read"], compressed_total=entry["csize"], out=str(out),
                ts_sorted=bool((np.diff(arrays["ts"]) >= 0).all()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--member")
    ap.add_argument("--budget_mb", type=float, default=100)
    a = ap.parse_args()
    entries = central_directory()
    if a.list:
        for e in entries:
            if e["usize"]:
                print(f"{e['name']:60s} compressed {e['csize'] / 1e6:8.1f} MB  uncompressed {e['usize'] / 1e6:8.1f} MB  method {e['method']}")
        return
    e = next(x for x in entries if x["name"] == a.member)
    rel = a.member.split("open_bandit_dataset/", 1)[-1].replace(".csv", ".npz")
    print(slice_compact(e, int(a.budget_mb * 1e6), ROOT / ".data" / "obd_slice" / rel))


if __name__ == "__main__":
    main()
