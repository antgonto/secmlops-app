#!/usr/bin/env bash
# Promotion gate: block if any open critical remains in SecObserve (lesson 14.1).
set -euo pipefail
source "$(dirname "$0")/versions.env"
: "${SO_TOKEN:?set SO_TOKEN}"
OPEN="$(curl -sf "$SO_URL/api/observations/?current_severity=Critical&resolved=false" \
  -H "Authorization: APIToken $SO_TOKEN" | jq '.count')"
[ "$OPEN" -eq 0 ] && echo "PROMOTE-OK" || { echo "BLOCKED: $OPEN open criticals"; exit 1; }
