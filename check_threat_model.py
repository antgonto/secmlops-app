#!/usr/bin/env python3
"""Gate: every zone row in threat-model.md must have all five cells filled. Exit 1 otherwise. (Lab 1.1)"""
import re, sys
path = sys.argv[1] if len(sys.argv) > 1 else "threat-model.md"
rows = [l for l in open(path, encoding="utf-8") if l.startswith("|") and not re.match(r"^\|\s*-", l) and not l.lower().startswith("| zone")]
bad = []
for l in rows:
    cells = [c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells) != 5 or any(not c for c in cells):
        bad.append(cells[0] if cells and cells[0] else "<unnamed>")
if bad:
    print("THREAT-MODEL-INCOMPLETE: " + ", ".join(f"{z} has an empty cell" for z in bad)); sys.exit(1)
print(f"THREAT-MODEL-OK: {len(rows)} zones covered"); sys.exit(0)
