#!/usr/bin/env bash
# Promote the SAME digest verified in test to production. Re-verifies everything; never rebuilds.
set -euo pipefail
source "$(dirname "$0")/versions.env"
DIGEST="$(cat image.digest)"
cosign verify $COSIGN_VERIFY_FLAGS --key cosign.pub "$IMAGE@$DIGEST" >/dev/null && echo "signature OK"
cosign verify-attestation $COSIGN_VERIFY_FLAGS --key cosign.pub --type https://slsa.dev/provenance/v1 "$IMAGE@$DIGEST" >/dev/null && echo "provenance OK"
sed -e "s|__IMAGE__|$IMAGE@$DIGEST|" -e "s|__ENV__|prod|" -e "s|__VERSION__|${GIT_SHA:-unknown}|" k8s/serve.yaml \
  | kubectl --context production apply -f -
kubectl --context production -n apps rollout status deploy/serve --timeout=180s
API_URL="${PROD_URL:-https://apps.secmlops.com}" pytest tests/smoke -q
echo "PROMOTE-DONE: $DIGEST -> production"
