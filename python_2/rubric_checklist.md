# Python 2 · Rubric checklist

Status means the language requirement is supported by actual isolated execution,
not that the full production application was exercised or an instructor grade assigned.

| # | Requirement | Supporting file | Strongest original source reference | Verification status |
|---|---|---|---|---|
| 01 | Define and apply a descriptively named constant in Python. | [assignment_01_constants/demo.py](assignment_01_constants/demo.py) · [report](assignment_01_constants/report_source.md) | `derexi-policy-pilot/backend/main.py:65` / `CONFIDENCE_THRESHOLD` | VERIFIED; unit tests 1, 2 + executed demo |
| 02 | Use if-else logic to control execution based on a condition. | [assignment_02_conditionals/demo.py](assignment_02_conditionals/demo.py) · [report](assignment_02_conditionals/report_source.md) | `derexi-policy-pilot/backend/main.py:423` / `ask` | VERIFIED; unit tests 3, 4 + executed demo |
| 03 | Demonstrate a while loop using a boolean condition. | [assignment_03_while_loops/demo.py](assignment_03_while_loops/demo.py) · [report](assignment_03_while_loops/report_source.md) | `derexi-policy-pilot/backend/document_limits.py:29` / `_supervise_mac` | VERIFIED; unit tests 5, 6, 7 + executed demo |
| 04 | Demonstrate a for loop iterating through a collection or range. | [assignment_04_for_loops/demo.py](assignment_04_for_loops/demo.py) · [report](assignment_04_for_loops/report_source.md) | `derexi-policy-pilot/backend/main.py:210` / `contains_keyword` | VERIFIED; unit tests 8, 9, 10, 26 + executed demo |
| 05 | Use functions accepting arguments, including a function returning a computed value. | [assignment_05_functions/demo.py](assignment_05_functions/demo.py) · [report](assignment_05_functions/report_source.md) | `derexi-policy-pilot/backend/pulse/service.py:399` / `relevance_score` | VERIFIED; unit tests 11, 12, 13, 14, 26 + executed demo |
| 06 | Access and modify list elements and process individual elements using loops. | [assignment_06_lists/demo.py](assignment_06_lists/demo.py) · [report](assignment_06_lists/report_source.md) | `derexi-policy-pilot/backend/pulse/service.py:748` / `get_feed` | VERIFIED; unit tests 15, 16, 17 + executed demo |
| 07 | Demonstrate both file reading and writing. | [assignment_07_file_operations/demo.py](assignment_07_file_operations/demo.py) · [report](assignment_07_file_operations/report_source.md) | `derexi-policy-pilot/backend/document_intake.py:219` / `retain` | VERIFIED; unit tests 18, 19, 25 + executed demo |
| 08 | Demonstrate try, except, else and finally on successful and exception-producing paths. | [assignment_08_exception_handling/demo.py](assignment_08_exception_handling/demo.py) · [report](assignment_08_exception_handling/report_source.md) | `derexi-policy-pilot/backend/database.py:57` / `get_db` | VERIFIED; unit tests 20, 21, 22, 23, 24, 25 + executed demo |

**Coverage: 8/8 VERIFIED.** Source line ranges and direct links are preserved in each
report/evidence file and [rubric-map.json](evidence/rubric-map.json).
[Functional results](evidence/test-results.json) · [Unit transcript](evidence/unittest-transcript.txt)
· [Document checks](evidence/artifact-results.json).

Assignments 03, 06, 07 and 08 add necessary safe/explicit examples; they are not
represented as pre-existing production functions. Assignment 02 is a reduced new
conditional wrapper; Assignments 01/04/05 execute selected original definitions.
