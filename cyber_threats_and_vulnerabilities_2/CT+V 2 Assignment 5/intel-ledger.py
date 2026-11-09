"""Reconcile historical CTI observations without contacting indicators."""
import json
import re
from time import perf_counter

HASH = "02aac4d201886e01abd2e3d42a20edcb4e6c2381549de19df0b9166607cd3f51"
URL = "hxxp://160[.]119[.]69[.]4/x"

def reconcile(rows):
    ledger = {}
    for kind, raw, source, case in rows:
        value = raw.lower() if kind == "sha256" else raw
        valid = re.fullmatch(r"[0-9a-f]{64}", value) if kind == "sha256" else (
            kind == "url" and re.fullmatch(r"hxxps?://[^\s]+", value)
        )
        if not (valid and source and case):
            raise ValueError(f"Invalid indicator metadata for {kind}")
        record = ledger.setdefault((kind, value), {
            "type": kind, "value": value, "cases": [], "sources": [],
        })
        if source not in record["sources"]:
            record["sources"].append(source)
        if case not in record["cases"]:
            record["cases"].append(case)
    return list(ledger.values())

if __name__ == "__main__":
    start = perf_counter()
    rows = [(kind, value, source, "k.php") for source in ("E02", "E05")
            for kind, value in (("sha256", HASH), ("url", URL))]
    indicators = reconcile(rows)
    assert len(indicators) == 2
    assert all(record["sources"] == ["E02", "E05"] for record in indicators)
    assert all(record["cases"] == ["k.php"] for record in indicators)
    assert reconcile([("sha256", HASH.upper(), "E02", "k.php")])[0]["value"] == HASH
    try:
        reconcile([("sha256", "invalid", "E02", "k.php")])
    except ValueError:
        pass
    else:
        raise AssertionError("Malformed hash was accepted")
    print(json.dumps({
        "scope": "offline course ledger, E05 derives from E02",
        "input_records": len(rows),
        "unique_indicators": len(indicators),
        "duplicate_ratio": (len(rows) - len(indicators)) / len(rows),
        "provenance_complete": sum(bool(i["sources"]) for i in indicators),
        "assertions": "PASS: dedupe, provenance, case separation, hash normalization, malformed input",
        "elapsed_ms": round((perf_counter() - start) * 1000, 3),
        "indicators": indicators,
    }, indent=2))

