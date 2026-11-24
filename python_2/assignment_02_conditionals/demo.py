"""New reduced if/else example using DeRexi's actual threshold and keyword helper."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import reused_symbols

symbols = reused_symbols("main")
CONFIDENCE_THRESHOLD = symbols["CONFIDENCE_THRESHOLD"]
contains_keyword = symbols["contains_keyword"]


def choose_response(score, policy_text, keywords):
    confident = score >= CONFIDENCE_THRESHOLD and bool(keywords) and contains_keyword(policy_text.lower(), keywords)
    if confident:
        return "Provide source-backed guidance"
    else:
        return "Request clarification"


def run_demo():
    return {"matching_at_threshold": choose_response(0.22, "Protect confidential data.", ["confidential"]),
            "below_threshold": choose_response(0.21, "Protect confidential data.", ["confidential"]),
            "high_score_without_evidence": choose_response(0.90, "Remote work guidance.", ["confidential"]),
            "empty_keywords": choose_response(0.90, "Remote work guidance.", [])}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
