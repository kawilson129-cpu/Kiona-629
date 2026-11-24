"""New complete exception lifecycle; only synthetic temporary review intervals."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import temporary_workspace


def read_review_interval(path):
    reader = None
    interval_days = None
    status = "error"
    error_type = None
    events = []
    try:
        events.append("try")
        reader = path.open("r", encoding="utf-8")
        interval_days = int(reader.read())
        if interval_days <= 0:
            raise ValueError("Review interval must be positive")
    except (OSError, ValueError) as error:
        events.append("except")
        error_type = type(error).__name__
        interval_days = None
    else:
        events.append("else")
        status = "success"
    finally:
        if reader is not None:
            reader.close()
        events.append("finally")
    return {"status": status, "interval_days": interval_days, "error_type": error_type,
            "events": events, "resource_state": "not_opened" if reader is None else "closed" if reader.closed else "open"}


def run_demo():
    with temporary_workspace() as directory:
        workspace_path = Path(directory)
        results = {}
        for label, content in [("valid", "30"), ("invalid_number", "not a number"), ("nonpositive", "0")]:
            path = workspace_path / (label + ".txt")
            path.write_text(content, encoding="utf-8")
            results[label] = read_review_interval(path)
        results["missing_file"] = read_review_interval(workspace_path / "missing.txt")
    results["temporary_directory_removed"] = not workspace_path.exists()
    return results


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
