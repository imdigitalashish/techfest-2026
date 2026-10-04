#!/usr/bin/env bash
# Deploy a built site (viewer + scene package) as an Azure Storage static website and print its public URL.
#   components/orchestrator/deploy_azure.sh <site_dir> <storage_account_name> [resource_group] [location]
# Requires `az login`. Only deploy captures you own: public datasets used for evaluation are non-commercial
# and must not be re-hosted.
set -euo pipefail
SITE="$1"; ACC="$2"; RG="${3:-namma-space-rg}"; LOC="${4:-centralindia}"
[ -f "$SITE/index.html" ] && [ -f "$SITE/scene/manifest.json" ] || { echo "not a built site: $SITE"; exit 1; }
az group create -n "$RG" -l "$LOC" -o none
az storage account show -n "$ACC" -g "$RG" -o none 2>/dev/null || \
  az storage account create -n "$ACC" -g "$RG" -l "$LOC" --sku Standard_LRS --kind StorageV2 -o none
KEY="$(az storage account keys list -n "$ACC" -g "$RG" --query '[0].value' -o tsv)"
az storage blob service-properties update --account-name "$ACC" --account-key "$KEY" \
  --static-website --index-document index.html -o none
az storage blob upload-batch --account-name "$ACC" --account-key "$KEY" -s "$SITE" -d '$web' --overwrite -o none
URL="$(az storage account show -n "$ACC" -g "$RG" --query primaryEndpoints.web -o tsv)"
echo "Deployed: $URL"
