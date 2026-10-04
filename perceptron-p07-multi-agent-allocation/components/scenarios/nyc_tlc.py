"""NYC TLC yellow-taxi replay adapter for the DemandTrace contract.

The trace replays thinned real Manhattan yellow-taxi pickups on the 5x5 simulator grid. The
``rates`` field is not an oracle from TLC; it is a proxy formed from un-thinned test-day pickup
counts multiplied by the thinning probability and smoothed with a centred 15-minute moving average.
"""
from __future__ import annotations

import zipfile
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from architecture.contracts.contracts import DemandTrace

GRID = 5
ZONES = GRID * GRID
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / ".data" / "nyc_tlc"
MAPPING_CSV = Path(__file__).with_name("nyc_zone_to_cell.csv")
MONTH = "2025-07"
PARQUET = DATA_DIR / f"yellow_tripdata_{MONTH}.parquet"
LOOKUP_CSV = DATA_DIR / "taxi_zone_lookup.csv"
SHAPE_ZIP = DATA_DIR / "taxi_zones.zip"
CACHE_NPZ = DATA_DIR / f"yellow_tripdata_{MONTH}_grid{GRID}_manhattan.npz"


def _require_data() -> None:
    missing = [str(p) for p in (PARQUET, LOOKUP_CSV, SHAPE_ZIP) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "NYC TLC data files are missing. Run components/scenarios/fetch_nyc_tlc.sh. "
            f"Missing: {missing}"
        )


def _ring_centroid(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    if len(points) < 3:
        arr = np.asarray(points, dtype=float)
        return 0.0, float(arr[:, 0].mean()), float(arr[:, 1].mean())
    area2 = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
        cross = x0 * y1 - x1 * y0
        area2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area = area2 / 2.0
    if abs(area) < 1e-12:
        arr = np.asarray(points, dtype=float)
        return 0.0, float(arr[:, 0].mean()), float(arr[:, 1].mean())
    return area, cx / (6.0 * area), cy / (6.0 * area)


def _shape_centroids_by_location() -> dict[int, tuple[float, float]]:
    extract_dir = DATA_DIR / "taxi_zones_shp"
    shp_path = extract_dir / "taxi_zones.shp"
    if not shp_path.exists():
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(SHAPE_ZIP) as zf:
            zf.extractall(extract_dir)
        matches = list(extract_dir.rglob("taxi_zones.shp"))
        if matches:
            shp_path = matches[0]
    try:
        import shapefile  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError("Install pyshp to read taxi_zones.zip: uv pip install --python .venv/bin/python pyshp") from exc

    reader = shapefile.Reader(str(shp_path))
    out: dict[int, tuple[float, float]] = {}
    for shape_record in reader.iterShapeRecords():
        rec = shape_record.record.as_dict()
        loc = int(rec["LocationID"])
        shape = shape_record.shape
        parts = list(shape.parts) + [len(shape.points)]
        weighted: list[tuple[float, float, float]] = []
        fallback: list[tuple[float, float]] = []
        for start, end in zip(parts[:-1], parts[1:]):
            pts = [(float(x), float(y)) for x, y in shape.points[start:end]]
            fallback.extend(pts)
            area, cx, cy = _ring_centroid(pts)
            if abs(area) > 1e-12:
                weighted.append((abs(area), cx, cy))
        if weighted:
            w = np.array([a for a, _, _ in weighted])
            xs = np.array([x for _, x, _ in weighted])
            ys = np.array([y for _, _, y in weighted])
            out[loc] = (float((w * xs).sum() / w.sum()), float((w * ys).sum() / w.sum()))
        else:
            arr = np.asarray(fallback, dtype=float)
            out[loc] = (float(arr[:, 0].mean()), float(arr[:, 1].mean()))
    return out


def build_zone_mapping() -> pd.DataFrame:
    """Map Manhattan taxi zones to 5x5 cells using PCA-rotated, equal-width centroid bins."""
    _require_data()
    lookup = pd.read_csv(LOOKUP_CSV)
    lookup = lookup[(lookup["Borough"] == "Manhattan") & (~lookup["LocationID"].isin([264, 265]))].copy()
    centroids = _shape_centroids_by_location()
    lookup["x"] = lookup["LocationID"].map(lambda z: centroids[int(z)][0])
    lookup["y"] = lookup["LocationID"].map(lambda z: centroids[int(z)][1])

    xy = lookup[["x", "y"]].to_numpy(dtype=float)
    centered = xy - xy.mean(axis=0, keepdims=True)
    vals, vecs = np.linalg.eigh(np.cov(centered, rowvar=False))
    long_axis = vecs[:, int(np.argmax(vals))]
    if long_axis[1] < 0:
        long_axis = -long_axis
    cross_axis = np.array([-long_axis[1], long_axis[0]])
    if cross_axis[0] < 0:
        cross_axis = -cross_axis

    long_coord = centered @ long_axis
    cross_coord = centered @ cross_axis

    def bin_axis(v: np.ndarray) -> np.ndarray:
        lo, hi = float(v.min()), float(v.max())
        scaled = (v - lo) / max(hi - lo, 1e-12)
        return np.clip(np.floor(scaled * GRID).astype(int), 0, GRID - 1)

    row = bin_axis(long_coord)
    col = bin_axis(cross_coord)
    out = pd.DataFrame(
        {
            "zone_id": lookup["LocationID"].astype(int),
            "zone_name": lookup["Zone"].astype(str),
            "cell": (row * GRID + col).astype(int),
        }
    ).sort_values("zone_id")
    out.to_csv(MAPPING_CSV, index=False)
    return out


def _mapping() -> pd.DataFrame:
    if MAPPING_CSV.exists():
        return pd.read_csv(MAPPING_CSV)
    return build_zone_mapping()


def _load_month() -> dict[str, np.ndarray | float]:
    _require_data()
    mapping_mtime = MAPPING_CSV.stat().st_mtime if MAPPING_CSV.exists() else 0.0
    if CACHE_NPZ.exists() and CACHE_NPZ.stat().st_mtime > max(PARQUET.stat().st_mtime, mapping_mtime):
        with np.load(CACHE_NPZ, allow_pickle=False) as data:
            return {k: data[k] for k in data.files}

    mapping = _mapping()
    zone_to_cell = dict(zip(mapping["zone_id"].astype(int), mapping["cell"].astype(int)))
    import pyarrow.parquet as pq

    table = pq.read_table(
        PARQUET,
        columns=["tpep_pickup_datetime", "PULocationID", "DOLocationID"],
    )
    df = table.to_pandas()
    total_rows = len(df)
    df["origin_cell"] = df["PULocationID"].map(zone_to_cell)
    df["dest_cell"] = df["DOLocationID"].map(zone_to_cell)
    df = df.dropna(subset=["origin_cell", "dest_cell"]).copy()
    kept_rows = len(df)
    pickup = pd.to_datetime(df["tpep_pickup_datetime"])
    df["date"] = pickup.dt.strftime("%Y-%m-%d")
    df["minute"] = pickup.dt.hour.to_numpy() * 60 + pickup.dt.minute.to_numpy()
    df = df.sort_values(["date", "minute", "origin_cell", "dest_cell"], kind="stable")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        CACHE_NPZ,
        date=df["date"].to_numpy(dtype="U10"),
        minute=df["minute"].to_numpy(dtype=np.int16),
        origin=df["origin_cell"].to_numpy(dtype=np.int16),
        dest=df["dest_cell"].to_numpy(dtype=np.int16),
        total_rows=np.array(total_rows, dtype=np.int64),
        kept_rows=np.array(kept_rows, dtype=np.int64),
        kept_fraction=np.array(kept_rows / max(total_rows, 1), dtype=np.float64),
    )
    with np.load(CACHE_NPZ, allow_pickle=False) as data:
        return {k: data[k] for k in data.files}


def _validate_days(days: Iterable[str]) -> list[str]:
    out = list(days)
    if not out:
        raise ValueError("at least one day is required")
    return out


def _counts_for_days(data: dict[str, np.ndarray | float], days: list[str]) -> np.ndarray:
    date = data["date"]
    minute = data["minute"].astype(np.int64)
    origin = data["origin"].astype(np.int64)
    counts = np.zeros((len(days) * 1440, ZONES), dtype=np.int32)
    for day_index, day in enumerate(days):
        mask = date == day
        flat_t = day_index * 1440 + minute[mask]
        np.add.at(counts, (flat_t, origin[mask]), 1)
    return counts


def _smooth_centered_15(counts: np.ndarray) -> np.ndarray:
    kernel = np.ones(15, dtype=np.float64) / 15.0
    padded = np.pad(counts.astype(np.float64), ((7, 7), (0, 0)), mode="edge")
    smoothed = np.empty_like(counts, dtype=np.float64)
    for z in range(counts.shape[1]):
        smoothed[:, z] = np.convolve(padded[:, z], kernel, mode="valid")
    return smoothed


def _profile_and_shares(data: dict[str, np.ndarray | float], train_days: list[str]) -> tuple[np.ndarray, np.ndarray]:
    train_counts = _counts_for_days(data, train_days)
    total = train_counts.sum(axis=1).astype(float)
    tod = np.arange(train_counts.shape[0]) % 1440
    bins = tod // 30
    sums = np.bincount(bins, weights=total, minlength=48)
    ns = np.bincount(bins, minlength=48)
    prof_bins = np.divide(sums, np.maximum(ns, 1), out=np.ones(48), where=ns > 0)
    if prof_bins.mean() <= 0:
        prof_bins = np.ones(48)
    profile = np.repeat(prof_bins / prof_bins.mean(), 30)[:1440].astype(np.float64)

    shares = train_counts.sum(axis=0).astype(np.float64)
    shares += 1e-9
    shares /= shares.sum()
    return profile, shares


def _od_from_train(data: dict[str, np.ndarray | float], train_days: list[str]) -> np.ndarray:
    date = data["date"]
    origin = data["origin"].astype(np.int64)
    dest = data["dest"].astype(np.int64)
    mat = np.ones((ZONES, ZONES), dtype=np.float64)
    mask = np.isin(date, np.asarray(train_days, dtype="U10"))
    np.add.at(mat, (origin[mask], dest[mask]), 1.0)
    return mat / mat.sum(axis=1, keepdims=True)


def build_nyc_trace(
    test_days: list[str],
    train_days: list[str],
    seed: int,
    target_rate: float = 10.0,
) -> tuple[DemandTrace, dict]:
    test_days = _validate_days(test_days)
    train_days = _validate_days(train_days)
    data = _load_month()
    counts_full = _counts_for_days(data, test_days)
    mean_rate = float(counts_full.sum() / counts_full.shape[0])
    q = min(1.0, float(target_rate) / mean_rate) if mean_rate > 0 else 1.0

    date = data["date"]
    minute = data["minute"].astype(np.int64)
    origin = data["origin"].astype(np.int64)
    dest = data["dest"].astype(np.int64)
    rng = np.random.default_rng(seed)
    selected_t: list[np.ndarray] = []
    selected_o: list[np.ndarray] = []
    selected_d: list[np.ndarray] = []
    for day_index, day in enumerate(test_days):
        mask = date == day
        keep = rng.random(int(mask.sum())) < q
        selected_t.append(day_index * 1440 + minute[mask][keep])
        selected_o.append(origin[mask][keep])
        selected_d.append(dest[mask][keep])

    if selected_t:
        tt = np.concatenate(selected_t)
        oo = np.concatenate(selected_o)
        dd = np.concatenate(selected_d).astype(np.int16)
    else:
        tt = oo = np.array([], dtype=np.int64)
        dd = np.array([], dtype=np.int16)

    counts = np.zeros_like(counts_full, dtype=np.int32)
    np.add.at(counts, (tt, oo), 1)
    flat = counts.reshape(-1)
    offsets = (np.cumsum(flat, dtype=np.int64) - flat).reshape(counts.shape).astype(np.int64)

    req_dest = np.empty(int(flat.sum()), dtype=np.int16)
    if req_dest.size:
        order = np.lexsort((dd, oo, tt))
        tt, oo, dd = tt[order], oo[order], dd[order]
        positions = offsets[tt, oo].copy()
        _, starts = np.unique(np.stack([tt, oo], axis=1), axis=0, return_index=True)
        for start, end in zip(starts, list(starts[1:]) + [len(tt)]):
            positions[start:end] += np.arange(end - start)
        req_dest[positions] = dd

    od = _od_from_train(data, train_days)
    profile, hist_shares = _profile_and_shares(data, train_days)
    rates = _smooth_centered_15(counts_full) * q
    trace = DemandTrace(
        rates=rates.astype(np.float64),
        counts=counts.astype(np.int32),
        req_dest=req_dest,
        offsets=offsets,
        od_prob=od,
        change_points=[],
        name=f"nyc-{test_days[0]}",
    )
    meta = {
        "grid": GRID,
        "n_zones": ZONES,
        "od_prob": od,
        "profile": profile,
        "hist_shares": hist_shares,
        "init_level": hist_shares * float(target_rate),
        "init_level_raw": hist_shares * float(target_rate),
        "rates": trace.rates,
    }
    return trace, meta


def find_surges(day: str, train_days: list[str] | None = None, window: int = 30, min_volume: int = 20) -> list[dict]:
    data = _load_month()
    all_days = sorted(set(str(d) for d in data["date"]))
    if train_days is None:
        train_days = [d for d in all_days if d != day and d.startswith(MONTH)]
    test = _counts_for_days(data, [day])
    train = _counts_for_days(data, train_days).reshape(len(train_days), 1440, ZONES)
    out: list[dict] = []
    day0 = datetime.strptime(day, "%Y-%m-%d")
    for cell in range(ZONES):
        for start in range(0, 1440, window):
            end = min(1440, start + window)
            count = int(test[start:end, cell].sum())
            if count < min_volume:
                continue
            train_mean = float(train[:, start:end, cell].sum(axis=1).mean()) if len(train_days) else 0.0
            ratio = float(count / train_mean) if train_mean >= 1.0 else float(count)
            out.append(
                {
                    "cell": cell,
                    "start": (day0 + timedelta(minutes=start)).strftime("%Y-%m-%d %H:%M"),
                    "end": (day0 + timedelta(minutes=end)).strftime("%Y-%m-%d %H:%M"),
                    "count": count,
                    "train_mean": train_mean,
                    "ratio": ratio,
                }
            )
    out.sort(key=lambda r: (r["ratio"], r["count"]), reverse=True)
    return out[:10]


def data_summary(test_days: list[str], target_rate: float = 10.0) -> dict:
    data = _load_month()
    counts_full = _counts_for_days(data, test_days)
    mean_rate = float(counts_full.sum() / counts_full.shape[0])
    q = min(1.0, float(target_rate) / mean_rate) if mean_rate > 0 else 1.0
    return {
        "month": MONTH,
        "kept_fraction": float(data["kept_fraction"]),
        "q": q,
        "mean_unthinned_rate": mean_rate,
    }
