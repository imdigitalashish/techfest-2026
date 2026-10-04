#!/usr/bin/env bash
# The grid environment used for every pre-registered run: ~/venv_kvp (torch 2.10.0 CPU + kvpress 0.5.5, which
# pins transformers<5.3 -> 5.2.0). Run after setup_torch.sh (which exports the weights using MLX in ~/venv).
set -e
UV=~/.local/bin/uv
$UV venv -q --clear --python 3.11 ~/venv_kvp
$UV pip install -q --python ~/venv_kvp/bin/python "torch==2.10.0" --index-url https://download.pytorch.org/whl/cpu
$UV pip install -q --python ~/venv_kvp/bin/python "kvpress==0.5.5" safetensors
~/venv_kvp/bin/python -c "import kvpress, transformers, torch; print('kvpress ok', transformers.__version__, torch.__version__)"
