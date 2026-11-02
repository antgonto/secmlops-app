# Threat model — fraud-clf (Milestone 1)

Every zone has a threat, a gate that closes it, how we'd detect a breach, and the lab that builds the gate. `check_threat_model.py` fails CI if any cell is empty.

| zone | threat | gate | detection | lab |
|---|---|---|---|---|
| data | poisoned or tampered training data (out-of-range rows, label flips, remote object edited) | Pandera schema + distribution checks; DVC content hashes verified on pull | validate.py exit 1; dvc pull checksum error | 3.1 |
| build | vulnerable or malicious dependencies; secrets in code; mutable action refs | Trivy fs, Gitleaks, Opengrep, pinned refs; required PR checks | gates stage red; workflow_scan.sh | 4.1, 4.2 |
| model | evasion-weak model; unsafe serialization; tampered artifact | ART robustness gate; safetensors; verify-before-load; evidence tags on promotion | art_gate.py FAIL; MODEL-LOAD-DENIED; promote_model.py BLOCKED | 5.1, 6.1, 6.2 |
| deploy | unsigned/unprovenanced/root/tagged images; rogue registry | Cosign signature + attestations; Kyverno admission; Harbor robot scoping | admission denied messages | 7.1, 8.1, 8.2, 9.1 |
| serve | malformed/oversized input; extraction via many queries; live evasion | pydantic schema + max instances; per-identity 200/h; live ART re-check | 422 rate; 429 count alert; live_art.py exit 1 | 12.1, 12.2 |
| access | unauthenticated or wrong-group access; in-cluster bypass | Pomerium identity-aware proxy by Entra group; default-deny NetworkPolicy | 302/403 in proxy logs; bypass curl times out | 10.1, 10.2 |
