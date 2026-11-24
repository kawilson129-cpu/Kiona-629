"""Offline Figma coursework audit. This does not open or test Figma imports."""
import base64
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
SVG = "{http://www.w3.org/2000/svg}"
XLINK = "{http://www.w3.org/1999/xlink}href"
checks = []


def check(name, condition, detail=None):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def load(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    return struct.unpack(">II", data[16:24])


folders = ["assignment_1_frames", "assignment_2_images", "assignment_3_styling", "assignment_4_components"]
check("Exactly four requested assignment folders", sorted(path.name for path in ROOT.glob("assignment_*") if path.is_dir()) == folders)
for folder in folders:
    readme = ROOT / folder / "README.md"
    text = readme.read_text() if readme.is_file() else ""
    check(folder + " README, sources, status and rubric checklist", all(word in text for word in
          ("Requirement:", "Status:", "Rubric checklist", "Figma")))
check("Course index and concise native implementation handoff exist", all((ROOT/name).is_file() for name in ("COURSE_INDEX.md", "FIGMA_HANDOFF.md")))
for source in load(EVIDENCE / "source-manifest.json")["sources"]:
    path = REPO / source["path"]
    check("Original hash unchanged: " + source["path"], path.is_file() and digest(path.read_bytes()) == source["sha256"])

inventory = load(EVIDENCE / "archive-inventory.json")
check("All three existing native FigJam archives inventoried", len(inventory) == 3 and all(row["path"].endswith(".jam") for row in inventory))
for record in inventory:
    with zipfile.ZipFile(REPO / record["path"]) as archive:
        check(Path(record["path"]).name + " ZIP integrity", archive.testzip() is None)
        check(Path(record["path"]).name + " metadata and original thumbnail size", json.loads(archive.read("meta.json")) == record["metadata"] and
              png_size(archive.read("thumbnail.png")) == (record["metadata"]["client_meta"]["thumbnail_size"]["width"], record["metadata"]["client_meta"]["thumbnail_size"]["height"]))
with zipfile.ZipFile(ROOT / "Stay Data Stay.jam") as archive:
    check("Primary archive is FigJam format, not inferred Design frame", archive.read("canvas.fig").startswith(b"fig-jam."))
    check("Primary historical thumbnail preserved byte for byte", (EVIDENCE / "stay-data-stay-original-thumbnail.png").read_bytes() == archive.read("thumbnail.png"))
    check("Four original embedded image entries, not four assumed unique subjects", len([name for name in archive.namelist() if name.startswith("images/") and not name.endswith("/")]) == 4)
for image in load(EVIDENCE / "extracted-image-provenance.json"):
    path = REPO / image["path"]
    with zipfile.ZipFile(REPO / image["archive"]) as archive:
        original = archive.read(image["archive_member"])
    check(path.name + " matches original archived image", path.read_bytes() == original and digest(original) == image["sha256"], {"width_height": png_size(original)})

trees = {}
for path in ROOT.glob("assignment_*/*.svg"):
    tree = ET.parse(path).getroot()
    trees[path.name] = tree
    ids = [node.get("id") for node in tree.iter() if node.get("id")]
    check(path.name + " valid SVG root and unique layer IDs", tree.tag == SVG+"svg" and len(ids) == len(set(ids)))
    check(path.name + " no executable elements or remote image links", all(
        node.tag not in (SVG+"script", SVG+"foreignObject") and
        all(not attribute.lower().startswith("on") for attribute in node.attrib) and
        (node.tag != SVG+"image" or node.get(XLINK, "").startswith("data:image/png;base64,"))
        for node in tree.iter()))

frame = trees["stay-data-stay-frame.svg"]
spec = load(ROOT / "assignment_1_frames/frame-spec.json")
check("Prepared screen dimensions match proposed frame spec", frame.get("width") == str(spec["width"]) == "1440" and frame.get("height") == str(spec["height"]) == "960")
image = frame.find(".//" + SVG + "image")
image_bytes = base64.b64decode(image.get(XLINK).split(",", 1)[1], validate=True)
check("Prepared image embeds unchanged existing project artwork", image_bytes == (REPO / "docs/assets/images/stay-data-stay-project.png").read_bytes())
width, height = png_size(image_bytes)
check("Prepared image preserves PNG aspect ratio and stays inside screen", abs(float(image.get("height")) - float(image.get("width")) * height / width) < .001 and
      float(image.get("x")) + float(image.get("width")) <= spec["width"] and float(image.get("y")) + float(image.get("height")) <= spec["height"])
row = trees["account-row.svg"]
check("Row candidate matches 600x88 spec and required named layers", row.get("width") == "600" and row.get("height") == "88" and
      all(any(node.get("id") == name for node in row.iter()) for name in ("AccountRow", "Background", "Marker", "Content", "AccountName", "Status")))
check("Three prepared row copies identified as groups, not native instances", len([node for node in frame.iter(SVG+"g") if node.get("id", "").startswith("AccountRow") and "-" not in node.get("id", "")]) == 3)
tokens = load(ROOT / "assignment_3_styling/design-tokens.json")
check("Proposed primitive, semantic and component tokens complete", all(key in tokens for key in ("primitive", "semantic", "component", "typography")) and
      len(tokens["primitive"]["colors"]) == 7 and all(style["family"] and style["size"] > 0 for style in tokens["typography"].values()))
color_values = set(tokens["primitive"]["colors"].values())
used_colors = {value for tree in trees.values() for node in tree.iter() for key, value in node.attrib.items() if key in ("fill", "stroke") and value.startswith("#")}
check("All authored SVG fills/strokes use proposed palette", used_colors <= color_values)
tools = load(EVIDENCE / "tool-availability.json")
check("Tool limitation honestly recorded", tools["figma_specific_tools_discovered"] == 0 and tools["connected_document_sessions"] == [])
index = (ROOT / "COURSE_INDEX.md").read_text()
check("Coverage preserves native gaps and FigJam/Design distinction", all(text.lower() in index.lower() for text in
      ("1/4", "0/4", "PARTIAL", "FigJam", "UNVERIFIED")))

broken, total = [], 0
for path in ROOT.rglob("*.md"):
    text = path.read_text()
    check(path.name + " balanced code fences", sum(line.startswith("```") for line in text.splitlines()) % 2 == 0)
    for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
        link = urlsplit(target)
        if link.scheme:
            continue
        total += 1
        destination = (path.parent / unquote(link.path)).resolve()
        if not destination.exists() and destination != EVIDENCE / "validation.json":
            broken.append(str(path.relative_to(ROOT)) + " -> " + target)
check("Local source/evidence/navigation links resolve", not broken, {"checked": total, "broken": broken})
git = subprocess.run(["git", "status", "--porcelain", "-z", "--untracked-files=all"], cwd=REPO, text=True, capture_output=True, check=True)
changed = [entry[3:] for entry in git.stdout.split("\0") if entry]
observation = load(EVIDENCE / "concurrent-worktree-observation.json")
concurrent_paths = {observation["old_path"], observation["new_path"]}
outside = [path for path in changed if not path.startswith("figma_1/")]
relocated = REPO / observation["new_path"]
check("Scope: Figma coursework plus preserved observed concurrent PDF move", set(outside) <= concurrent_paths and
      relocated.is_file() and digest(relocated.read_bytes()) == observation["old_head_sha256"],
      {"changed_paths": len(changed), "observed_concurrent_paths": outside, "course_task_edits": "figma_1 only"})
result = {"timestamp": datetime.now(timezone.utc).isoformat(), "scope": "OFFLINE artifact validation ONLY; no Figma imports/editor actions or screenshot claims",
          "passed": sum(row["status"] == "PASS" for row in checks), "failed": sum(row["status"] == "FAIL" for row in checks),
          "checks": checks, "rubric_status": {"frames": "PARTIAL", "images": "VERIFIED_ARCHIVED_FIGJAM_ONLY", "styling": "PARTIAL", "components": "PARTIAL"},
          "verified_existing_evidence_criteria": 1, "native_design_criteria_verified": 0,
          "not_tested": ["Figma native import", "native frame properties", "native editable font/style properties", "component creation/instance propagation"]}
(EVIDENCE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(f'Offline checks: {result["passed"]} PASS / {result["failed"]} FAIL; {total} local links.')
for row in checks:
    if row["status"] == "FAIL":
        print(row)
raise SystemExit(bool(result["failed"]))
