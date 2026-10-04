"""Flower RecordDict serialization for C10 LoRA messages."""
from __future__ import annotations

from collections.abc import Mapping

import torch
from flwr.app import ArrayRecord, ConfigRecord

LayerState = dict[str, tuple[torch.Tensor, torch.Tensor]]
Payload = dict[str, torch.Tensor | tuple[torch.Tensor, torch.Tensor]]

_A_SUFFIX = "::A"
_B_SUFFIX = "::B"
_T_SUFFIX = "::T"


def layer_state_to_record(state: Mapping[str, tuple[torch.Tensor, torch.Tensor]]) -> tuple[ArrayRecord, ConfigRecord]:
    """Encode a LoRA layer state into Flower ArrayRecord + schema ConfigRecord."""
    flat: dict[str, torch.Tensor] = {}
    names = []
    for name in sorted(state):
        a, b = state[name]
        names.append(name)
        flat[f"{name}{_A_SUFFIX}"] = a.detach().cpu().contiguous()
        flat[f"{name}{_B_SUFFIX}"] = b.detach().cpu().contiguous()
    return ArrayRecord(flat), ConfigRecord({"format": "layer_state", "layers": names})


def record_to_layer_state(arrays: ArrayRecord, schema: ConfigRecord | None = None) -> LayerState:
    """Decode a Flower ArrayRecord produced by :func:`layer_state_to_record`."""
    tensors = arrays.to_torch_state_dict()
    if schema is not None and "layers" in schema:
        names = list(schema["layers"])
    else:
        names = sorted(k[: -len(_A_SUFFIX)] for k in tensors if k.endswith(_A_SUFFIX))
    return {name: (tensors[f"{name}{_A_SUFFIX}"].clone(), tensors[f"{name}{_B_SUFFIX}"].clone()) for name in names}


def payload_to_record(payload: Mapping[str, torch.Tensor | tuple[torch.Tensor, torch.Tensor]]) -> tuple[ArrayRecord, ConfigRecord]:
    """Encode either FedAvgAB ``(A, B)`` payloads or Anchor tensor deltas."""
    flat: dict[str, torch.Tensor] = {}
    names = []
    tuple_payload = None
    for name in sorted(payload):
        value = payload[name]
        names.append(name)
        is_tuple = isinstance(value, tuple)
        if tuple_payload is None:
            tuple_payload = is_tuple
        elif tuple_payload != is_tuple:
            raise ValueError("mixed payload formats are not supported")
        if is_tuple:
            a, b = value
            flat[f"{name}{_A_SUFFIX}"] = a.detach().cpu().contiguous()
            flat[f"{name}{_B_SUFFIX}"] = b.detach().cpu().contiguous()
        else:
            flat[f"{name}{_T_SUFFIX}"] = value.detach().cpu().contiguous()
    fmt = "tuple_payload" if tuple_payload else "tensor_payload"
    return ArrayRecord(flat), ConfigRecord({"format": fmt, "layers": names})


def record_to_payload(arrays: ArrayRecord, schema: ConfigRecord) -> Payload:
    """Decode a payload Flower ArrayRecord."""
    tensors = arrays.to_torch_state_dict()
    names = list(schema["layers"])
    fmt = schema["format"]
    if fmt == "tuple_payload":
        return {name: (tensors[f"{name}{_A_SUFFIX}"].clone(), tensors[f"{name}{_B_SUFFIX}"].clone()) for name in names}
    if fmt == "tensor_payload":
        return {name: tensors[f"{name}{_T_SUFFIX}"].clone() for name in names}
    raise ValueError(f"unknown payload format {fmt!r}")
