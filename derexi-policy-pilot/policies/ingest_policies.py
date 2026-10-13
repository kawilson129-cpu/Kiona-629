"""Ingest the six consolidated Aurum Capital Bank policies into DeRexi.

Uses the application's existing ingestion pipeline: the FastAPI
``POST /policies`` endpoint (policy master record + first policy version).
The ``pg_trgm`` GIN search indexes are maintained automatically by Postgres,
so no separate reindex step is required.

Idempotent: any policy whose title already exists is skipped, so re-running
this script never creates duplicates.

Usage (from repo root, API running on :8000):
    derexi-policy-pilot/.venv/bin/python derexi-policy-pilot/policies/ingest_policies.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "http://127.0.0.1:8000"
EFFECTIVE_DATE = "2026-10-01"
REVIEW_DATE = "2027-09-30"

HERE = Path(__file__).resolve().parent

# (markdown file, policy title, category_id, owner_id, owner name)
POLICIES = [
    (
        "ACB-IT-001_information_security_acceptable_technology_use.md",
        "Information Security & Acceptable Technology Use",
        6,   # Acceptable Use & Technology
        7,   # Chris Tanaka
        "Chris Tanaka",
    ),
    (
        "ACB-IT-002_identity_access_management.md",
        "Identity & Access Management",
        5,   # Information Security & Operations
        7,   # Chris Tanaka
        "Chris Tanaka",
    ),
    (
        "ACB-LND-001_lending_operations_documentation.md",
        "Lending Operations & Documentation",
        3,   # Lending & Credit
        11,  # Marcus Webb
        "Marcus Webb",
    ),
    (
        "ACB-HR-001_employee_leave_hr_procedures.md",
        "Employee Leave & HR Procedures",
        7,   # Human Resources & Conduct
        9,   # Jordan Rivera
        "Jordan Rivera",
    ),
    (
        "ACB-OPS-001_operational_reporting_workflow_management.md",
        "Operational Reporting & Workflow Management",
        5,   # Information Security & Operations
        12,  # Rachel Sampson
        "Rachel Sampson",
    ),
    (
        "ACB-COMP-001_policy_governance_compliance_client_confidentiality.md",
        "Policy Governance, Compliance & Client Confidentiality",
        1,   # Privacy & Consumer Protection
        4,   # Maya Patel
        "Maya Patel",
    ),
]


def request(method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else None


def main() -> int:
    existing = {p["title"] for p in request("GET", "/policies")}
    created, skipped, failed = [], [], []

    for filename, title, category_id, owner_id, owner_name in POLICIES:
        if title in existing:
            skipped.append(title)
            print(f"SKIP   already present: {title}")
            continue

        body = (HERE / filename).read_text(encoding="utf-8")
        payload = {
            "title": title,
            "summary": f"Consolidated Aurum Capital Bank policy. Owner: {owner_name}.",
            "category_id": category_id,
            "owner_id": owner_id,
            "status": "approved",
            "version": {
                "version_no": "1.0",
                "title": title,
                "body": body,
                "effective_date": EFFECTIVE_DATE,
                "review_date": REVIEW_DATE,
                "requires_review": False,
                "created_by": owner_id,
            },
        }
        try:
            result = request("POST", "/policies", payload)
            created.append((result["id"], result["title"]))
            print(f"CREATE id={result['id']:>3} v{result['latest_version']}  {result['title']}")
        except urllib.error.HTTPError as exc:
            failed.append((title, exc.code, exc.read().decode()))
            print(f"FAIL   {title}: HTTP {exc.code} {exc.read().decode()}")

    print("\n--- summary ---")
    print(f"created={len(created)} skipped={len(skipped)} failed={len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
