"""New UTF-8 read/write exercise using self-cleaning course-local temporary files."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from course_support import temporary_workspace


def file_round_trip(text):
    with temporary_workspace() as directory:
        workspace_path = Path(directory)
        note_path = workspace_path / "practice_policy.txt"
        with note_path.open("w", encoding="utf-8") as writer:
            written_characters = writer.write(text)
        with note_path.open("r", encoding="utf-8") as reader:
            recovered_text = reader.read()
        result = {"written_characters": written_characters, "read_text": recovered_text,
                  "writer_closed": writer.closed, "reader_closed": reader.closed}
    result["temporary_directory_removed"] = not workspace_path.exists()
    return result


def run_demo():
    return file_round_trip("Practice policy: protéger les données.\n")


if __name__ == "__main__":
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))
