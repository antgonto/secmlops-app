#!/usr/bin/env bash
set -uo pipefail
: "${STAGING:=https://staging.secmlops.com}" ; : "${ENTRA_APP_ID:?}"
TOKEN=$(az account get-access-token --resource "$ENTRA_APP_ID" --query accessToken -o tsv) || { echo "token request failed"; exit 1; }
export TOKEN
export STAGING_TOKEN="$TOKEN"
katana -u "$STAGING" -H "Authorization: Bearer $TOKEN" -jc -kf all -o urls-auth.txt || true
nuclei -l urls-auth.txt -H "Authorization: Bearer $TOKEN" -severity medium,high,critical -sarif-export nuclei-auth.sarif -silent || true
[ -f rapidast.yaml ] && docker run --rm -v "$PWD:/work" -e TOKEN ghcr.io/rapidast/rapidast:latest rapidast.py --config /work/rapidast.yaml || true
comm -13 <(sort -u urls-unauth.txt 2>/dev/null) <(sort -u urls-auth.txt) > auth-only-endpoints.txt
sarif_gate() {  # sarif_gate FILE...  every report must exist, parse, and carry no error-level result
  for s in "$@"; do
    [ -f "$s" ] || { echo "MISSING REPORT: $s (the scanner did not run or did not write it)"; exit 1; }
    n=$(jq '[.runs[].results[] | select(.level=="error")] | length' "$s" 2>/dev/null) || n=""
    case "$n" in
      0) ;;
      "") echo "UNREADABLE REPORT: $s (not valid SARIF)"; exit 1 ;;
      *) echo "CRITICAL in $s: $n error-level finding(s)"; exit 1 ;;
    esac
  done
}
sarif_gate nuclei-auth.sarif
python live_art.py            # NOT || true: below-threshold robustness fails the stage
python live_giskard.py || true
python extract.py 500 | tee extraction.txt || true
echo "PHASE2-DONE: $(wc -l < auth-only-endpoints.txt) auth-only endpoints"
