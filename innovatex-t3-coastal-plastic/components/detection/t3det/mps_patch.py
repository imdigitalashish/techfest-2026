"""Workaround for MPS indexing bugs (torch 2.10 + ultralytics 8.4.12) in the training label assigner.

On this machine, TaskAlignedAssigner on MPS fails on the first batch: boolean-mask indexing of expanded
views returns the wrong number of elements ("shape mismatch: value tensor of shape [1436] cannot be
broadcast to indexing result of shape [1562]"), and `nonzero` returns out-of-range indices
("index 192 is out of bounds: 0, range 0 to 16"). Fix: run the assigner (no-grad target assignment,
no learnable parameters) on CPU and move its outputs back. The network forward/backward stay on MPS.
The assignment maths is unchanged (ultralytics' own `_forward`, the path it already uses on CUDA OOM).
"""
import torch
from ultralytics.utils import tal

_orig_forward = tal.TaskAlignedAssigner._forward


@torch.no_grad()
def _forward_cpu(self, pd_scores, pd_bboxes, anc_points, gt_labels, gt_bboxes, mask_gt):
    device = gt_bboxes.device
    if device.type != "mps":
        return _orig_forward(self, pd_scores, pd_bboxes, anc_points, gt_labels, gt_bboxes, mask_gt)
    cpu = [t.detach().float().cpu() if t.is_floating_point() else t.cpu()
           for t in (pd_scores, pd_bboxes, anc_points, gt_labels, gt_bboxes, mask_gt)]
    out = _orig_forward(self, *cpu)
    return tuple(t.to(device) for t in out)


def apply() -> None:
    tal.TaskAlignedAssigner._forward = _forward_cpu


# NMS time limit: ultralytics' non_max_suppression stops processing the rest of a batch once a wall-clock limit
# (2 s + 0.05 s/img) is exceeded, leaving those images with no detections. On this shared, loaded machine that would
# silently lower validation mAP (and make best.pt selection noisy), so the limit is lifted for train/val/eval.
from ultralytics.utils import nms as _nms  # noqa: E402

_orig_nms = _nms.non_max_suppression


def _nms_no_time_limit(*args, **kwargs):
    if len(args) < 10:
        kwargs["max_time_img"] = 1e3
    return _orig_nms(*args, **kwargs)


def apply_all() -> None:
    apply()
    _nms.non_max_suppression = _nms_no_time_limit
