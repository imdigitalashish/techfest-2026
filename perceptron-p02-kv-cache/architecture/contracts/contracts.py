"""Typed contracts between components (C1-C10). Arrays are mlx.core.array; shapes in comments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, TypedDict

Array = Any  # mlx.core.array


class Needle(TypedDict):
    key: str          # e.g. "amber-otter"
    value: str        # 7-digit string
    depth: float      # 0..1 position of the needle in the context


@dataclass
class Sample:                         # C1 -> C2
    ctx_ids: List[int]                # T tokens, chat-template prefix up to (not incl.) the question
    questions: List[tuple]            # [(question_ids: List[int], Needle)]


@dataclass
class FullCache:                      # C2 -> C3, C6, C7
    K: List[Array]                    # per layer [1, nkv, T, hd], RoPE applied at original positions
    V: List[Array]                    # per layer [1, nkv, T, hd]
    h2o_acc: Optional[List[Array]]    # per layer [nkv, T] attention mass received
    window_q: Optional[dict]          # layer -> [1, nh, W, hd] queries of the last W context tokens


Scores = List[Array]                  # C3 -> C5: per layer [nkv, T], higher = keep
Index = List[Array]                   # C5 -> C6: per layer [nkv, B] sorted int positions


@dataclass
class CompressedCache:                # C6 -> C7, C8
    K: List[Array]                    # per layer [1, nkv, B, hd] (dequantised view if quantised)
    V: List[Array]
    stored_bytes: int                 # actual bytes kept (packed values + scales + biases)


@dataclass
class Sketch:                         # C7a -> C7b
    layer: int
    keys_hat: Array                   # [1, nkv, T_evicted, hd] dequantised 2-bit keys of one layer
    span: tuple                       # (start, end) original positions of the evicted region
    bytes: int                        # packed sketch bytes
    token_ids_bytes: int              # 4 * T


@dataclass
class RecalledBlocks:                 # C7b -> C8
    blocks: List[int]                 # chosen block indices within the evicted span
    K: List[Array]                    # per layer [1, nkv, R, hd] re-prefilled at original positions
    V: List[Array]


@dataclass
class MemoryReport:                   # C9 -> C10
    kv_bytes: int
    meta_bytes: int = 0               # scales/biases, sketch, token ids
    answer_time_bytes: int = 0        # peak bytes held while answering (C7 adds recalled blocks)
    prefill_peak_bytes: int = 0       # mx.get_peak_memory() during prefill (shared by all methods)
    notes: dict = field(default_factory=dict)
