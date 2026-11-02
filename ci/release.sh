#!/usr/bin/env bash
# Stage: release. Push by digest + Cosign sign + attest SBOM/ML-BOM (lesson 8.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
docker push "$IMAGE:$GIT_SHA"
DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "$IMAGE:$GIT_SHA" | cut -d@ -f2)"
echo "digest=$DIGEST"
: "${BAO_TOKEN:?login to OpenBao first}"
bao kv get -field=key secret/mlops/cosign > cosign.key
export COSIGN_PASSWORD="$(bao kv get -field=password secret/mlops/cosign)"
cosign sign $COSIGN_SIGN_FLAGS --key cosign.key "$IMAGE@$DIGEST"
cosign attest $COSIGN_SIGN_FLAGS --key cosign.key --type cyclonedx --predicate sbom.cdx.json "$IMAGE@$DIGEST"
cosign attest $COSIGN_SIGN_FLAGS --key cosign.key --type https://secmlops.com/mlbom/v1 --predicate mlbom.cdx.json "$IMAGE@$DIGEST"
rm -f cosign.key
echo "$DIGEST" > image.digest
echo "RELEASE-PASS"
