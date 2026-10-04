"""C4 Local trainer: HF PEFT LoRA on a frozen base model, one simulated device at a time.

All devices share one in-memory base model; only the LoRA tensors differ per device, so the
simulator loads a device's view, trains, and reads the adapter back. A device's rank budget
r_k < r_max is enforced by masking gradients (A rows / B columns >= r_k never move).
PEFT's scaling alpha / r_max is the same for every device, so ranks nest exactly.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass

import torch

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

LayerState = dict[str, tuple[torch.Tensor, torch.Tensor]]  # name -> (A [r, d_in], B [d_out, r])


@dataclass
class LoraModel:
    model: torch.nn.Module
    layers: dict[str, tuple[torch.nn.Parameter, torch.nn.Parameter]]
    device: torch.device

    def get_state(self) -> LayerState:
        return {k: (A.detach().clone(), B.detach().clone()) for k, (A, B) in self.layers.items()}

    def set_state(self, state: LayerState) -> None:
        with torch.no_grad():
            for k, (A, B) in self.layers.items():
                a, b = state[k]
                A.copy_(a)
                B.copy_(b)


def pick_device() -> torch.device:
    return torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")


def build_lora_model(model_id: str, r_max: int, alpha: float, targets: list[str]) -> LoraModel:
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM

    device = pick_device()
    base = AutoModelForCausalLM.from_pretrained(model_id, local_files_only=True, dtype=torch.float32)
    cfg = LoraConfig(r=r_max, lora_alpha=alpha, target_modules=list(targets), lora_dropout=0.0, bias="none",
                     task_type="CAUSAL_LM")
    model = get_peft_model(base, cfg).to(device)
    layers = {}
    for name, mod in model.named_modules():
        la = getattr(mod, "lora_A", None)
        if isinstance(la, torch.nn.ModuleDict) and "default" in la:
            layers[name] = (la["default"].weight, mod.lora_B["default"].weight)
    for p in model.parameters():
        p.requires_grad_(False)
    return LoraModel(model=model, layers=layers, device=device)


def reset_lora(lm: LoraModel, seed: int) -> LayerState:
    """Seeded re-init matching PEFT's default (A ~ kaiming-uniform(a=√5), B = 0). Returns the state.

    The A matrices are a pure function of the seed, so devices can regenerate the shared anchor
    locally instead of downloading it.
    """
    g = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        for name in sorted(lm.layers):
            A, B = lm.layers[name]
            a = torch.empty(A.shape)
            torch.nn.init.kaiming_uniform_(a, a=math.sqrt(5), generator=g)
            A.copy_(a)
            B.zero_()
    return lm.get_state()


def local_train(lm: LoraModel, blocks: torch.Tensor, rank: int, steps: int, batch_size: int, lr: float,
                train_A: bool, seed: int) -> tuple[float, float]:
    """Run `steps` AdamW steps on the device's blocks. Returns (mean train loss, wall seconds)."""
    t0 = time.time()
    trainable, masks = [], []
    for A, B in lm.layers.values():
        B.requires_grad_(True)
        trainable.append(B)
        mb = torch.zeros_like(B)
        mb[:, :rank] = 1
        masks.append((B, mb))
        A.requires_grad_(train_A)
        if train_A:
            trainable.append(A)
            ma = torch.zeros_like(A)
            ma[:rank] = 1
            masks.append((A, ma))
    opt = torch.optim.AdamW(trainable, lr=lr, weight_decay=0.0)
    g = torch.Generator().manual_seed(seed)
    lm.model.train()
    losses = []
    for _ in range(steps):
        idx = torch.randint(0, blocks.shape[0], (batch_size,), generator=g)
        x = blocks[idx].to(lm.device)
        loss = lm.model(input_ids=x, labels=x).loss
        loss.backward()
        for p, m in masks:
            p.grad.mul_(m)
        torch.nn.utils.clip_grad_norm_(trainable, 1.0)
        opt.step()
        opt.zero_grad(set_to_none=True)
        losses.append(loss.item())
    for A, B in lm.layers.values():
        A.requires_grad_(False)
        B.requires_grad_(False)
    return (sum(losses) / len(losses) if losses else float("nan")), time.time() - t0


@torch.no_grad()
def evaluate(lm: LoraModel, eval_blocks: dict[str, torch.Tensor], batch_size: int = 16) -> dict[str, float]:
    """Mean next-token cross-entropy (nats/token) per domain on held-out blocks."""
    lm.model.eval()
    out = {}
    for dom, blocks in eval_blocks.items():
        tot, n = 0.0, 0
        for i in range(0, blocks.shape[0], batch_size):
            x = blocks[i : i + batch_size].to(lm.device)
            tot += lm.model(input_ids=x, labels=x).loss.item() * x.shape[0]
            n += x.shape[0]
        out[dom] = tot / n
    return out
