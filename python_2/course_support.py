"""Reuse reviewed pure source without importing DeRexi's app/configuration.

AST selection is an adapter for this repository, not a security sandbox.
Only hashed, explicitly listed definitions are compiled; no module startup runs.
"""
import ast
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

COURSE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = COURSE_ROOT.parent
SELECTIONS = {
    "main": ("derexi-policy-pilot/backend/main.py",
             ("CONFIDENCE_THRESHOLD", "contains_keyword")),
    "pulse": ("derexi-policy-pilot/backend/pulse/service.py",
              ("STATUS_WEIGHT", "CATEGORY_WEIGHT", "SOURCE_WEIGHT", "RECENCY_POINTS",
               "RECENCY_HORIZON_DAYS", "relevance_score")),
}


@lru_cache(maxsize=2)
def reused_symbols(group):
    """Return original constants/functions with only their standard-library globals."""
    relative_path, names = SELECTIONS[group]
    source_path = REPO_ROOT / relative_path
    raw = source_path.read_bytes()
    manifest = json.loads((COURSE_ROOT / "evidence/source-review.json").read_text())
    expected = next(item["sha256"] for item in manifest["sources"] if item["path"] == relative_path)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError("Reviewed source changed; review and refresh evidence before reuse.")
    tree = ast.parse(raw.decode("utf-8-sig"), filename=str(source_path))
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in names:
                ast.literal_eval(node.value)  # These selected constants must be literals.
                selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            if node.decorator_list:
                raise RuntimeError("Unexpected decorated source function.")
            selected.append(node)
    if len(selected) != len(names):
        raise RuntimeError("Reviewed source definitions are missing or ambiguous.")
    namespace = {"re": re, "datetime": datetime}
    subset = ast.Module(body=selected, type_ignores=[])
    exec(compile(subset, str(source_path), "exec"), namespace)
    return {name: namespace[name] for name in names}


def temporary_workspace():
    """Create disposable exercise files only under the course's ignored runtime dir."""
    runtime_root = COURSE_ROOT / "evidence/.runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    return TemporaryDirectory(prefix="practice-", dir=runtime_root)
