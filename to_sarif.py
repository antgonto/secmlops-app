#!/usr/bin/env python3
"""Lab 13.2 — generic scanner-JSON -> SARIF converter driven by a per-tool field map.
usage: to_sarif.py <tool> <input.json> <output.sarif>"""
import json
import sys

MAPS = {
    "testssl": {"list": lambda d: d, "id": "id", "msg": "finding", "sev": "severity", "loc": "ip",
                "levels": {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note", "INFO": "note"}},
    "giskard": {"list": lambda d: d["issues"], "id": "detector", "msg": "description", "sev": "level", "loc": None,
                "levels": {"major": "error", "medium": "warning", "minor": "note"}},
}
tool, src, dst = sys.argv[1:4]
m = MAPS[tool]
results = []
for it in m["list"](json.load(open(src))):
    lvl = m["levels"].get(str(it.get(m["sev"], "")).upper() if tool == "testssl" else it.get(m["sev"]))
    if not lvl:
        continue
    r = {"ruleId": str(it.get(m["id"])), "level": lvl, "message": {"text": str(it.get(m["msg"], ""))}}
    if m["loc"]:
        r["locations"] = [{"physicalLocation": {"artifactLocation": {"uri": str(it.get(m["loc"], "target"))}}}]
    results.append(r)
json.dump({"version": "2.1.0", "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
           "runs": [{"tool": {"driver": {"name": tool}}, "results": results}]}, open(dst, "w"), indent=2)
print(f"{tool}: {len(results)} findings -> {dst}")
