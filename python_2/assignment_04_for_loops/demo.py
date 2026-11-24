"""Execute DeRexi's original collection-iterating keyword function."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import reused_symbols

contains_keyword = reused_symbols("main")["contains_keyword"]


def run_demo():
    results = {}
    cases = [("later_match", "protect confidential data", ["remote", "confidential"]),
             ("singular_match", "apply each safeguard", ["safeguards"]),
             ("no_match", "remote access", ["confidential"]),
             ("empty_collection", "remote access", [])]
    for label, policy_text, keywords in cases:
        results[label] = contains_keyword(policy_text, keywords)
    return results


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
