"""Offline Design 1 artifact checks; never import the project or call APIs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
EVIDENCE = ROOT / "evidence"
FOLDERS = ["assignment_01_empathy_map", "assignment_02_documented_research",
           "assignment_03_purpose_statement", "assignment_04_brainstormed_ideas",
           "assignment_05_conversational_prototype"]
SVG = "{http://www.w3.org/2000/svg}"
checks = []


def check(name, condition, detail=None):
    checks.append({"name":name, "status":"PASS" if condition else "FAIL", "detail":detail})


def load(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


check("Exactly five requested assignment folders", sorted(path.name for path in ROOT.glob("assignment_*") if path.is_dir()) == sorted(FOLDERS))
required = {
    FOLDERS[0]: ["README.md", "empathy-map.svg"],
    FOLDERS[1]: ["research.md", "research-sources.json"],
    FOLDERS[2]: ["README.md", "purpose.txt"],
    FOLDERS[3]: ["ideas.md"],
    FOLDERS[4]: ["walkthrough.md", "feedback-form.md", "prototype-screen.svg", "original-figjam-thumbnail.png", "original-figjam-metadata.json"],
}
for folder, names in required.items():
    check(folder + " required supporting files", all((ROOT/folder/name).is_file() for name in names))

map_text = (ROOT/FOLDERS[0]/"README.md").read_text()
map_svg = ET.parse(ROOT/FOLDERS[0]/"empathy-map.svg").getroot()
ids = [node.get("id") for node in map_svg.iter() if node.get("id")]
check("Empathy map is a complete valid visual with unique region IDs", map_svg.tag == SVG+"svg" and
      len(ids)==len(set(ids)) and all(region in ids for region in ("says", "thinks", "does", "feels", "pains", "gains")))
check("All six visual regions explicitly marked as assumptions", sum(
    "[A]" in "".join(node.itertext()) for node in map_svg.iter(SVG+"text")) >= 6 and
    "No interview" in map_text and "Casey" in map_text)
check("Map dimensions and text origins fit the canvas", map_svg.get("width")=="1360" and map_svg.get("height")=="1020" and
      all(0<=float(node.get("x",0))<1360 and 0<=float(node.get("y",0))<1020 for node in map_svg.iter(SVG+"text")))
check("New map is labelled synthesis, not a Figma export", "not a Figma export" in " ".join(map_svg.itertext()))

research = load(ROOT/FOLDERS[1]/"research-sources.json")
sources = research["sources"]
check("Three distinct credible primary-source publishers/URLs recorded", len(sources)==3 and
      len({source["publisher"] for source in sources})==3 and
      {urlsplit(source["url"]).netloc for source in sources}=={"help.netflix.com", "support.google.com", "www.smartraveller.gov.au"})
check("Every research source has reviewed content, finding, scope and design influence", all(
    source["verification"]=="Opened and relevant page content reviewed" and all(source[key] for key in
    ("id", "title", "sections", "finding", "scope", "design_inference")) for source in sources))
research_text = (ROOT/FOLDERS[1]/"research.md").read_text()
check("Research identifies secondary method, uncertainty and excluded blocked source", all(
    text in research_text for text in ("secondary desk research", "not a survey", "403", "not counted", "inferences")))

purpose = (ROOT/FOLDERS[2]/"purpose.txt").read_text().strip()
sentences = [sentence for sentence in re.split(r"(?<=[.!?])\s+", purpose) if sentence]
check("Purpose contains no more than two complete sentences", 1<=len(sentences)<=2 and purpose.endswith("."), {"sentences":len(sentences)})
check("Purpose explicitly identifies what, who and why", all(
    text in purpose for text in ("checkout checklist", "travelers", "remember which accounts", "before leaving")))
walkthrough = (ROOT/FOLDERS[4]/"walkthrough.md").read_text()
check("A3 statement appears verbatim in A3 explanation and A5", purpose in (ROOT/FOLDERS[2]/"README.md").read_text() and purpose in walkthrough)

ideas = (ROOT/FOLDERS[3]/"ideas.md").read_text()
check("Three distinct brainstormed alternatives documented", all(text in ideas for text in
      ("I1", "I2", "I3", "Physical departure cue", "Provider-specific recovery guide")))
check("Ideas include problem, benefits, limitations and reasoned preference", all(text.lower() in ideas.lower() for text in
      ("problem addressed", "Potential benefits", "Limitations", "preferred", "rationale", "not proof")))
check("New ideation is distinguished from historic meetings or feedback", "newly documented" in ideas and "not an invented" in ideas)

original_svg = REPO/"figma_1/assignment_1_frames/stay-data-stay-frame.svg"
copied_svg = ROOT/FOLDERS[4]/"prototype-screen.svg"
check("Prototype screen reuses existing asset byte for byte", copied_svg.read_bytes()==original_svg.read_bytes())
tree = ET.parse(copied_svg).getroot()
check("Existing concept screen retains its 1440x960 visual", tree.tag==SVG+"svg" and tree.get("width")=="1440" and tree.get("height")=="960")
with zipfile.ZipFile(REPO/"figma_1/Stay Data Stay.jam") as archive:
    image = (ROOT/FOLDERS[4]/"original-figjam-thumbnail.png").read_bytes()
    check("Authentic FigJam thumbnail extracted unchanged", image==archive.read("thumbnail.png") and image.startswith(b"\x89PNG") and struct.unpack(">II",image[16:24])==(400,372))
    check("Original metadata preserved without invented Figma activity", load(ROOT/FOLDERS[4]/"original-figjam-metadata.json")==json.loads(archive.read("meta.json")))
check("A5 includes A2 research, visual provenance and all three sources", all(text in walkthrough for text in
      ("A2", "Netflix", "Google", "Smartraveller", "not a live app", "NOT RUN", "NOT COLLECTED")))
check("Conversational prototype has seven prompts and exception/feedback planning", all(text in walkthrough for text in
      ("1 ·", "2 ·", "3 ·", "4 ·", "5 ·", "6 ·", "7 ·", "Exception prompts", "feedback-form.md")))
feedback = (ROOT/FOLDERS[4]/"feedback-form.md").read_text()
check("Feedback form contains no represented participant outcomes", "NOT EXECUTED" in feedback and
      "No participant, response or outcome" in feedback and feedback.count("Not collected")>=5)

for source in load(EVIDENCE/"source-manifest.json")["sources"]:
    path = REPO/source["path"]
    check("Protected original unchanged: "+source["path"], path.is_file() and digest(path)==source["sha256"])
broken, total = [], 0
for path in ROOT.rglob("*.md"):
    text = path.read_text()
    check(str(path.relative_to(ROOT))+" balanced code fences", sum(line.startswith("```") for line in text.splitlines())%2==0)
    for destination in re.findall(r"!?\[[^\]\n]*\]\(([^)\n]+)\)", text):
        link = urlsplit(destination)
        if link.scheme:
            continue
        total += 1
        target = (path.parent/unquote(link.path)).resolve()
        if not target.exists() and target != EVIDENCE/"validation.json":
            broken.append(str(path.relative_to(ROOT))+" -> "+destination)
check("All local links resolve", not broken, {"checked":total, "broken":broken})
readme = (ROOT/"README.md").read_text()
check("Root index covers all five criteria, citations, evidence and gaps", all(text in readme for text in
      ("A1", "A2", "A3", "A4", "A5", "5/5", "Research citations", "Outstanding requirements", "UNTESTED")))
git = subprocess.run(["git","status","--porcelain","-z","--untracked-files=all"],cwd=REPO,text=True,capture_output=True,check=True)
changed = [entry[3:] for entry in git.stdout.split("\0") if entry]
check("All working-tree changes stay inside existing Design 1 course", all(path.startswith("design_1/") for path in changed),
      {"paths":len(changed), "outside_course":[path for path in changed if not path.startswith("design_1/")]})
result = {"timestamp":datetime.now(timezone.utc).isoformat(),"scope":"Offline coursework artifact/source/provenance checks; no app or participant testing; does not refetch web sources",
          "passed":sum(row["status"]=="PASS" for row in checks),"failed":sum(row["status"]=="FAIL" for row in checks),
          "checks":checks,"rubric_coverage":"5/5 supplied design deliverables supported", "human_study":"NOT RUN", "application_tests":"NOT RUN", "new_figma_activity":"NONE"}
(EVIDENCE/"validation.json").write_text(json.dumps(result,indent=2)+"\n")
print(f'Artifact validation: {result["passed"]} PASS / {result["failed"]} FAIL; {total} local links.')
for row in checks:
    if row["status"]=="FAIL":
        print(row)
raise SystemExit(bool(result["failed"]))
