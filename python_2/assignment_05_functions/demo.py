"""Execute the original Pulse computed-ranking function with synthetic records."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import reused_symbols

relevance_score = reused_symbols("pulse")["relevance_score"]


def run_demo():
    article = {"status": "Final Rule", "category": "Regulations", "source": "Federal Register",
               "published": "2026-01-01"}
    invalid_date = dict(article, published="not-a-date")
    return {"same_day": relevance_score(article, "2026-01-01"),
            "fifteen_days_old": relevance_score(article, "2026-01-16"),
            "without_date_argument": relevance_score(article),
            "invalid_date": relevance_score(invalid_date, "2026-01-16"),
            "unknown_metadata": relevance_score({})}


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
