"""Offline source assessment. No backend imports, sockets or configuration reads."""
import ast
import hashlib
import json
from importlib import metadata
from pathlib import Path
import re
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1] / "derexi-policy-pilot"

def assess():
    started = perf_counter()
    source = (ROOT / "backend/main.py").read_bytes()
    tree = ast.parse(source)
    routes = []
    for handler in tree.body:
        if not isinstance(handler, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for call in handler.decorator_list:
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                continue
            if ast.unparse(call.func.value) != "app" or call.func.attr not in {"get", "post", "patch", "delete", "put"}:
                continue
            defaults = handler.args.defaults + handler.args.kw_defaults
            routes.append({
                "method": call.func.attr.upper(),
                "path": ast.literal_eval(call.args[0]),
                "line": call.lineno,
                "dependencies": [ast.unparse(d) for d in defaults if isinstance(d, ast.Call)],
            })
    packages = []
    for declaration in (ROOT / "requirements.txt").read_text().splitlines():
        name = re.match(r"^[a-zA-Z0-9_-]+", declaration)
        if not name:
            continue
        try:
            installed = metadata.version(name[0])
        except metadata.PackageNotFoundError:
            installed = None
        packages.append({"declaration": declaration, "installed": installed})
    return {
        "scope": "static local source and direct package metadata only",
        "main_sha256": hashlib.sha256(source).hexdigest(),
        "routes": routes,
        "packages": packages,
        "elapsed_ms": round((perf_counter() - started) * 1000, 2),
    }

if __name__ == "__main__":
    print(json.dumps(assess(), indent=2))

