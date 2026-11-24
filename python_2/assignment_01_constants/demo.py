"""Reused DeRexi threshold; only synthetic numerical examples are evaluated."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import reused_symbols

CONFIDENCE_THRESHOLD = reused_symbols("main")["CONFIDENCE_THRESHOLD"]


def run_demo():
    scores = [0.21, 0.22, 0.30]
    return {"constant": "CONFIDENCE_THRESHOLD", "value": CONFIDENCE_THRESHOLD,
            "scores": scores, "meets_numeric_gate": [score >= CONFIDENCE_THRESHOLD for score in scores]}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
