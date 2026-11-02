# Taxonomy map — OWASP ML Top 10, OWASP LLM Top 10, MITRE ATLAS → this system (Milestone 1)

| entry | status | control | evidence |
|---|---|---|---|
| OWASP ML01 Input manipulation | covered | ART gate (5.1), live re-check (12.1) | art_gate.py 0.865 / 0.492 |
| OWASP ML02 Data poisoning | partial | Pandera + DVC (3.1); subtle poisoning needs conditional checks (exercise 37) | validate.py --poison red run |
| OWASP ML05 Model theft | partial | query budget + alert (12.2) | extract.py fidelity drop |
| OWASP ML06 AI supply chain | covered | SBOM/ML-BOM, signing, provenance, admission (7–9) | cosign verify, Kyverno denials |
| OWASP ML10 Model poisoning | partial | evidence-tagged promotion (6.2); no training-pipeline attestation yet | promote_model.py BLOCKED |
| ATLAS AML.T0020 Poison training data | partial | as ML02 | as ML02 |
| ATLAS AML.T0043 Craft adversarial data | covered | as ML01 | as ML01 |
| ATLAS AML.T0024 Exfiltration via inference API | partial | as ML05 | as ML05 |
| OWASP LLM Top 10 | out-of-scope | no LLM component in fraud-clf; Garak probes reserved for Lab 12.1's LLM variant | — |
