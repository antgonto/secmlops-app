#!/usr/bin/env bash
# Stage: register. ModelScan + safetensors + cosign sign-blob (lesson 6.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
modelscan -p model/ -r json -o modelscan.json
sha256sum model/model.safetensors > model/model.safetensors.sha256
: "${BAO_TOKEN:?login to OpenBao first}"
bao kv get -field=key secret/mlops/cosign > cosign.key
COSIGN_PASSWORD="$(bao kv get -field=password secret/mlops/cosign)" \
  cosign sign-blob $COSIGN_SIGN_FLAGS --key cosign.key \
  --output-signature model/model.safetensors.sig model/model.safetensors
rm -f cosign.key
echo "MODEL-SIGNED"
