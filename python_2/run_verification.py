"""Run safe Python 2 coursework checks using only Python's standard library."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EVIDENCE = ROOT / "evidence"
FOLDERS = ["assignment_01_constants", "assignment_02_conditionals", "assignment_03_while_loops",
           "assignment_04_for_loops", "assignment_05_functions", "assignment_06_lists",
           "assignment_07_file_operations", "assignment_08_exception_handling"]


def load_demo(folder):
    specification = importlib.util.spec_from_file_location(folder, ROOT / folder / "demo.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class CourseworkBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demos = [load_demo(folder) for folder in FOLDERS]

    def test_01_constant_value(self):
        self.assertEqual(self.demos[0].CONFIDENCE_THRESHOLD, 0.22)

    def test_02_constant_applied_at_boundary(self):
        self.assertEqual(self.demos[0].run_demo()["meets_numeric_gate"], [False, True, True])

    def test_03_if_matching_at_threshold(self):
        self.assertEqual(self.demos[1].choose_response(0.22, "Protect confidential data.", ["confidential"]), "Provide source-backed guidance")

    def test_04_else_low_score_absent_or_empty_keywords(self):
        for score, text, keywords in [(0.21999, "confidential", ["confidential"]),
                                      (0.9, "remote access", ["confidential"]), (0.9, "remote access", [])]:
            with self.subTest(score=score, keywords=keywords):
                self.assertEqual(self.demos[1].choose_response(score, text, keywords), "Request clarification")

    def test_05_while_progress_and_order(self):
        self.assertEqual(self.demos[2].process_questions([" first ", "second"]),
                         {"processed": ["first", "second"], "iterations": 2, "pending": []})

    def test_06_while_initial_false(self):
        self.assertEqual(self.demos[2].process_questions([]), {"processed": [], "iterations": 0, "pending": []})

    def test_07_while_input_not_consumed(self):
        questions = ["first"]
        self.demos[2].process_questions(questions)
        self.assertEqual(questions, ["first"])

    def test_08_for_matches_first_and_later_elements(self):
        function = self.demos[3].contains_keyword
        self.assertTrue(function("confidential data", ["confidential", "remote"]))
        self.assertTrue(function("confidential data", ["remote", "confidential"]))

    def test_09_for_singular_fallback(self):
        self.assertTrue(self.demos[3].contains_keyword("apply a safeguard", ["safeguards"]))

    def test_10_for_empty_and_absent_matches(self):
        self.assertFalse(self.demos[3].contains_keyword("remote access", []))
        self.assertFalse(self.demos[3].contains_keyword("", ["confidential"]))
        self.assertFalse(self.demos[3].contains_keyword("remote access", ["confidential"]))

    def test_11_function_returns_computed_same_day_score(self):
        self.assertEqual(self.demos[4].run_demo()["same_day"], 92.0)

    def test_12_function_recency_and_optional_argument(self):
        actual = self.demos[4].run_demo()
        self.assertEqual(actual["fifteen_days_old"], 84.0)
        self.assertEqual(actual["without_date_argument"], 68.0)

    def test_13_function_invalid_date_fallback(self):
        self.assertEqual(self.demos[4].run_demo()["invalid_date"], 68.0)

    def test_14_function_unknown_metadata_defaults(self):
        self.assertEqual(self.demos[4].relevance_score({}), 6.0)

    def test_15_list_indexed_edit_and_append(self):
        actual = self.demos[5].run_demo()
        self.assertEqual(actual["first_before"], " data handling ")
        self.assertEqual(actual["first_after"], "Data Handling")
        self.assertEqual(actual["prepared"], ["Data Handling", "Account Access", "Incident Response"])

    def test_16_list_empty_input(self):
        self.assertEqual(self.demos[5].normalize_titles([]), [])

    def test_17_list_preserves_input_and_duplicates(self):
        titles = [" policy ", " policy "]
        self.assertEqual(self.demos[5].normalize_titles(titles), ["Policy", "Policy"])
        self.assertEqual(titles, [" policy ", " policy "])

    def test_18_file_unicode_read_write_and_handles(self):
        text = "Practice only: données 🔒\n"
        actual = self.demos[6].file_round_trip(text)
        self.assertEqual(actual["read_text"], text)
        self.assertEqual(actual["written_characters"], len(text))
        self.assertTrue(actual["writer_closed"] and actual["reader_closed"])

    def test_19_empty_file_round_trip_and_cleanup(self):
        actual = self.demos[6].file_round_trip("")
        self.assertEqual(actual["read_text"], "")
        self.assertEqual(actual["written_characters"], 0)
        self.assertTrue(actual["temporary_directory_removed"])

    def test_20_exception_success_else_and_finally(self):
        actual = self.demos[7].run_demo()["valid"]
        self.assertEqual(actual["status"], "success")
        self.assertEqual(actual["interval_days"], 30)
        self.assertEqual(actual["events"], ["try", "else", "finally"])
        self.assertEqual(actual["resource_state"], "closed")

    def test_21_exception_invalid_number_except_finally(self):
        actual = self.demos[7].run_demo()["invalid_number"]
        self.assertEqual(actual["error_type"], "ValueError")
        self.assertEqual(actual["events"], ["try", "except", "finally"])
        self.assertEqual(actual["resource_state"], "closed")
        self.assertIsNone(actual["interval_days"])

    def test_22_exception_missing_file_finally_without_open_handle(self):
        actual = self.demos[7].run_demo()["missing_file"]
        self.assertEqual(actual["error_type"], "FileNotFoundError")
        self.assertEqual(actual["events"], ["try", "except", "finally"])
        self.assertEqual(actual["resource_state"], "not_opened")

    def test_23_exception_nonpositive_interval(self):
        module = self.demos[7]
        with module.temporary_workspace() as directory:
            path = Path(directory) / "interval.txt"
            for content in ("0", "-3"):
                path.write_text(content)
                actual = module.read_review_interval(path)
                self.assertEqual(actual["status"], "error")
                self.assertEqual(actual["error_type"], "ValueError")
                self.assertEqual(actual["resource_state"], "closed")

    def test_24_exception_directory_oserror(self):
        module = self.demos[7]
        with module.temporary_workspace() as directory:
            actual = module.read_review_interval(Path(directory))
            self.assertEqual(actual["error_type"], "IsADirectoryError")
            self.assertEqual(actual["events"], ["try", "except", "finally"])

    def test_25_file_demonstrations_remove_temporary_directories(self):
        self.assertTrue(self.demos[6].run_demo()["temporary_directory_removed"])
        self.assertTrue(self.demos[7].run_demo()["temporary_directory_removed"])

    def test_26_original_functions_keep_original_source_filename(self):
        self.assertEqual(Path(self.demos[3].contains_keyword.__code__.co_filename),
                         REPO / "derexi-policy-pilot/backend/main.py")
        self.assertEqual(Path(self.demos[4].relevance_score.__code__.co_filename),
                         REPO / "derexi-policy-pilot/backend/pulse/service.py")


def document_checks():
    checks = []
    def check(name, condition, detail=None):
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    check("Eight requested assignment directories", sorted(p.name for p in ROOT.glob("assignment_*") if p.is_dir()) == sorted(FOLDERS))
    for folder in FOLDERS:
        check(folder + " complete required files", all((ROOT/folder/name).is_file() for name in
              ("demo.py", "README.md", "evidence.md", "report_source.md")))
    check("Root submission and evidence navigation", all((ROOT/name).is_file() for name in
          ("README.md", "rubric_checklist.md", "final_summary.md", "EVIDENCE_INDEX.md")))
    map_path = EVIDENCE / "rubric-map.json"
    mapping = json.loads(map_path.read_text()) if map_path.exists() else []
    references_valid = len(mapping) == 8
    for row in mapping:
        for reference in row["references"]:
            path = REPO / reference["path"]
            references_valid = references_valid and path.is_file() and 1 <= reference["start"] <= reference["end"] <= len(path.read_text(encoding="utf-8-sig").splitlines())
    check("Original and demo line references valid", references_valid)
    bad_links, total = [], 0
    for path in ROOT.rglob("*.md"):
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", path.read_text()):
            link = urlsplit(target)
            if link.scheme:
                continue
            total += 1
            target = (path.parent/unquote(link.path)).resolve()
            if not target.exists() and target != EVIDENCE/"artifact-results.json":
                bad_links.append(str(path.relative_to(ROOT)) + " -> " + str(target))
    check("Markdown local links resolve", not bad_links, {"checked":total, "broken":bad_links})
    manifest = json.loads((EVIDENCE/"source-review.json").read_text())
    check("Reviewed backend, root memory and original screenshot unchanged", all(
        hashlib.sha256((REPO/item["path"]).read_bytes()).hexdigest()==item["sha256"] for item in manifest["sources"]))
    check("No disposable exercise files retained", not any((EVIDENCE/".runtime").glob("practice-*")))
    syntax_failures = []
    for path in ROOT.rglob("*.py"):
        try:
            compile(path.read_text(), str(path), "exec")
        except SyntaxError as error:
            syntax_failures.append(str(path.relative_to(ROOT)) + ": " + str(error))
    check("All course Python syntax compiles without bytecode writes", not syntax_failures, syntax_failures)
    trees = [ast.parse((ROOT/folder/"demo.py").read_text()) for folder in FOLDERS]
    main_tree = ast.parse((REPO/"derexi-policy-pilot/backend/main.py").read_text(encoding="utf-8-sig"))
    pulse_tree = ast.parse((REPO/"derexi-policy-pilot/backend/pulse/service.py").read_text(encoding="utf-8-sig"))
    keyword_function = next(node for node in main_tree.body if isinstance(node,ast.FunctionDef) and node.name=="contains_keyword")
    score_function = next(node for node in pulse_tree.body if isinstance(node,ast.FunctionDef) and node.name=="relevance_score")
    constructs = [
        any(isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=="CONFIDENCE_THRESHOLD" for target in node.targets) for node in trees[0].body),
        any(isinstance(node,ast.If) and node.orelse for node in ast.walk(trees[1])),
        any(isinstance(node,ast.While) and isinstance(node.test,ast.Name) and node.test.id=="has_pending_questions" for node in ast.walk(trees[2])),
        any(isinstance(node,ast.For) for node in ast.walk(keyword_function)),
        bool(score_function.args.args) and any(isinstance(node,ast.Return) and node.value is not None for node in ast.walk(score_function)),
        any(isinstance(node,ast.Assign) and any(isinstance(target,ast.Subscript) for target in node.targets) for node in ast.walk(trees[5])) and any(isinstance(node,ast.For) for node in ast.walk(trees[5])),
        all(any(isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=="open" and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value==mode for node in ast.walk(trees[6])) for mode in ("w","r")),
        any(isinstance(node,ast.Try) and node.handlers and node.orelse and node.finalbody for node in ast.walk(trees[7])),
    ]
    check("All eight literal rubric constructs present in executed/reference code", all(constructs),constructs)
    functional = json.loads((EVIDENCE/"test-results.json").read_text())
    lifecycle = json.loads((EVIDENCE/"assignment_08_exception_handling.json").read_text())["payload"]
    check("Recorded passes and both exception lifecycle outcomes reconcile", functional["unit_tests"]==26 and
          not any(functional[name] for name in ("unit_failures","unit_errors","unit_skipped","demo_failed")) and
          functional["demo_passed"]==8 and lifecycle["valid"]["events"]==["try","else","finally"] and
          lifecycle["invalid_number"]["events"]==["try","except","finally"])
    git = subprocess.run(["git","status","--porcelain","-z","--untracked-files=all"],cwd=REPO,text=True,capture_output=True,check=True)
    changed = [entry[3:] for entry in git.stdout.split("\0") if entry]
    check("Working tree changes confined to existing Python 2 course", all(path.startswith("python_2/") for path in changed),
          {"changed_paths":len(changed),"outside_course":[path for path in changed if not path.startswith("python_2/")]})
    result = {"timestamp":datetime.now(timezone.utc).isoformat(),"mode":"Offline document/source/artifact validation only",
              "passed":sum(row["status"]=="PASS" for row in checks),
              "failed":sum(row["status"]=="FAIL" for row in checks), "checks":checks}
    (EVIDENCE/"artifact-results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(f'Artifacts: {result["passed"]} PASS / {result["failed"]} FAIL')
    for row in checks:
        if row["status"] == "FAIL":
            print(row)
    return result["failed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents-only", action="store_true", help="Check documentation/hashes without repeating functional tests")
    args = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    if args.documents_only:
        raise SystemExit(bool(document_checks()))
    executions = []
    for folder in FOLDERS:
        command = [sys.executable, "-B", str(ROOT/folder/"demo.py")]
        process = subprocess.run(command, cwd=REPO, text=True, capture_output=True, timeout=10)
        try:
            payload = json.loads(process.stdout)
        except json.JSONDecodeError:
            payload = None
        row = {"assignment":folder,"command":f"python3 -B python_2/{folder}/demo.py",
               "exit_code":process.returncode,"status":"PASS" if process.returncode==0 and payload is not None else "FAIL",
               "stdout":process.stdout,"stderr":process.stderr,"payload":payload}
        executions.append(row)
        (EVIDENCE/(folder+".json")).write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CourseworkBehavior))
    transcript = stream.getvalue()
    (EVIDENCE/"unittest-transcript.txt").write_text(transcript)
    summary = {"timestamp":datetime.now(timezone.utc).isoformat(),"python":sys.version.split()[0],
               "mode":"Actual offline Python execution; selected original functions, synthetic in-memory and temporary-file inputs; no mocks, app startup, DB or API calls",
               "unit_tests":result.testsRun,"unit_failures":len(result.failures),"unit_errors":len(result.errors),
               "unit_skipped":len(result.skipped),"demo_passed":sum(row["status"]=="PASS" for row in executions),
               "demo_failed":sum(row["status"]=="FAIL" for row in executions),"executions":executions}
    (EVIDENCE/"test-results.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print(f'Unit tests: {result.testsRun} run / {len(result.failures)} FAIL / {len(result.errors)} ERROR / {len(result.skipped)} SKIP')
    print(f'Demo entry points: {summary["demo_passed"]} PASS / {summary["demo_failed"]} FAIL')
    if not result.wasSuccessful():
        print(transcript)
    raise SystemExit(bool(not result.wasSuccessful() or summary["demo_failed"]))


if __name__ == "__main__":
    main()
