#!/usr/bin/env bash
# Run eval/kvbench.py on an Azure CPU VM (MLX CPU backend, Linux wheels) when the shared Mac is saturated.
# Usage: eval/azure/run_on_azure.sh create|setup|run "<kvbench args>"|status|fetch|delete
# Defaults: one Standard_D8ds_v5 (8 vCPU, 32 GiB) in centralindia; delete the resource group after use.
# The SSH key is project-local and gitignored (.data/azure_p02), never committed.
set -euo pipefail
RG=${RG:-p02-kvcache-rg}; LOC=${LOC:-centralindia}; VM=${VM:-p02-kv-1}; SIZE=${SIZE:-Standard_D8ds_v5}
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KEY="$ROOT/.data/azure_p02"
OPTS="-i $KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=30"
ip() { az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv; }
case "${1:-}" in
  create)
    [ -f "$KEY" ] || ssh-keygen -q -t rsa -b 3072 -N "" -f "$KEY"
    az group create -n "$RG" -l "$LOC" --tags project=perceptron-p02-kv-cache purpose=kvbench -o none
    az vm create -g "$RG" -n "$VM" --image Ubuntu2204 --size "$SIZE" --admin-username azureuser \
      --ssh-key-values "$KEY.pub" --os-disk-size-gb 64 --public-ip-sku Standard -o none
    ip ;;
  setup)
    H="azureuser@$(ip)"
    ssh $OPTS "$H" 'mkdir -p p02/eval p02/.data'
    scp $OPTS "$ROOT/eval/kvbench.py" "$ROOT/eval/fetch_haystack.py" "$H:p02/eval/"
    ssh $OPTS "$H" 'curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 \
      && ~/.local/bin/uv venv -q --clear --python 3.11 ~/venv \
      && ~/.local/bin/uv pip install -q --python ~/venv/bin/python "mlx[cpu]==0.32.3" "mlx-lm==0.32.0" pyarrow huggingface_hub \
      && cd p02 && ~/venv/bin/python eval/fetch_haystack.py' ;;
  run)
    H="azureuser@$(ip)"; shift
    scp $OPTS "$ROOT/eval/kvbench.py" "$H:p02/eval/"
    ssh $OPTS "$H" "cd p02 && nohup ~/venv/bin/python -u eval/kvbench.py --device cpu $* > run_\$(date +%s).log 2>&1 &" ;;
  status)
    H="azureuser@$(ip)"; ssh $OPTS "$H" 'cd p02 && for f in run_*.log; do echo "== $f"; grep -v clean_up "$f" | tail -4; done; uptime' ;;
  fetch)
    H="azureuser@$(ip)"; mkdir -p "$ROOT/eval/results"
    scp $OPTS "$H:p02/eval/results/*" "$ROOT/eval/results/" ;;
  delete)
    az group delete -n "$RG" --yes --no-wait ;;
  *) echo "usage: $0 create|setup|run|status|fetch|delete"; exit 1 ;;
esac
