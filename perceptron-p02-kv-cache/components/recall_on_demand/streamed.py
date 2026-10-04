"""Streamed RoD block scorer: identical maths to kvbench_torch.block_scores(..., "softmax_lift"), O(chunk) memory.

The unchunked scorer materialises a dense fp32 sketch and fp32 question/window logits over all E evicted keys
(tens of MiB at 4k tokens). Here the packed 4-bit sketch is decoded `chunk` keys at a time and each softmax over the
E keys is computed in two passes (online log-sum-exp, then normalised probabilities), so the transient working set
is O(chunk). verify_streamed.py checks that both scorers pick the same blocks.
"""
from __future__ import annotations

import torch


def packed_rows(pk, h, t0, t1, E):
    """Decode sketch rows (head h, tokens t0..t1) from a kvbench_torch.Packed of shape [1, nkv, E, hd] (group == hd)."""
    per, n = 8 // pk.bits, 2 ** pk.bits - 1
    r0, r1 = h * E + t0, h * E + t1
    q = torch.stack([(pk.q[r0:r1] >> (pk.bits * i)) & n for i in range(per)], -1).reshape(r1 - r0, pk.group)
    return q.float() * pk.scale[r0:r1].float() + pk.bias[r0:r1].float()


def _lse(Q, pk, h, E, chunk):
    m = torch.full(Q.shape[:-1], float("-inf"))
    s = torch.zeros(Q.shape[:-1])
    for t0 in range(0, E, chunk):
        lg = Q @ packed_rows(pk, h, t0, min(E, t0 + chunk), E).T
        mc = lg.amax(-1)
        nm = torch.maximum(m, mc)
        s = s * torch.exp(m - nm) + torch.exp(lg - nm[..., None]).sum(-1)
        m = nm
    return m + torch.log(s)


def softmax_lift_streamed(qq, wq, pk, scale, nkv, chunk=256):
    """qq [1,nh,Lq,hd], wq [1,nh,W,hd] (fp32), pk: Packed sketch [1,nkv,E,hd] -> per-key scores [E] (max over heads)."""
    E = pk.shape[2]
    g = qq.shape[1] // nkv
    out = torch.full((E,), float("-inf"))
    for h in range(nkv):
        Q = (qq[0, h * g:(h + 1) * g] * scale).reshape(-1, qq.shape[-1])   # [g*Lq, hd]
        Wq = (wq[0, h * g:(h + 1) * g] * scale).reshape(-1, wq.shape[-1])  # [g*W, hd]
        lq, lw = _lse(Q, pk, h, E, chunk), _lse(Wq, pk, h, E, chunk)
        for t0 in range(0, E, chunk):
            t1 = min(E, t0 + chunk)
            K = packed_rows(pk, h, t0, t1, E)
            pq = torch.exp(Q @ K.T - lq[:, None]).mean(0)
            pw = torch.exp(Wq @ K.T - lw[:, None]).mean(0)
            out[t0:t1] = torch.maximum(out[t0:t1], pq - pw)
    return out


def transient_bytes_streamed(Lq, nkv=8, g=4, hd=64, W=64, chunk=256, E=4096):
    """Upper bound of live tensors: one decoded chunk + its question/window logits and probabilities + outputs."""
    return chunk * hd * 4 + 2 * g * (Lq + W) * chunk * 4 + E * 4 + 4 * g * (Lq + W) * 4
