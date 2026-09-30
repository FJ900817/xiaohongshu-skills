"""Offline smoke-check for the static synthetic fixture (Python stdlib only)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

DEMO = Path(__file__).resolve().parent.parent / "examples" / "synthetic" / "demo-v1"

def load(name: str):
    with (DEMO / name).open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)

task = load("task-card.json")
catalog = load("synthetic-keyword-catalog.json")
keywords = load("keyword-plan.json")
final = load("finalization-approved.json")
visual = load("visual-output.json")
profile = load("account-profile.json")

required_task = {"schema_version", "task_id", "status", "profile_ref", "content_goal", "audience", "topic", "note_type", "core_problem", "core_answer", "title_requirement", "keyword_request", "writing_constraints", "topics", "risk", "evidence", "approval"}
if not required_task.issubset(task):
    fail(f"task card missing fields: {sorted(required_task - set(task))}")
if task["note_type"] not in {"search", "recommendation", "editorial_trend"}:
    fail("unknown note_type")
if not profile.get("synthetic") or not catalog.get("synthetic") or not all(k.get("source", {}).get("kind") == "synthetic_catalog" for k in keywords["keywords"]):
    fail("profile/keyword fixture must be synthetic")
if sum(k.get("role") == "main" for k in keywords["keywords"]) != 1:
    fail("keyword plan must contain exactly one main keyword")
if keywords.get("status") != "approved" or any(k.get("approval_state") != "approved" for k in keywords["keywords"]):
    fail("keyword plan is not approved")
if final.get("status") != "approved" or visual.get("content_ref", {}).get("status") != "approved":
    fail("visual gate requires approved content")
body_hash = hashlib.sha256(final["body"].encode("utf-8")).hexdigest()
if body_hash != final.get("body_sha256") or body_hash != visual["content_ref"].get("body_sha256"):
    fail("final body hash mismatch")
if final["body"] != (DEMO / "writing-draft.md").read_text(encoding="utf-8-sig"):
    fail("final approved body differs from writing draft fixture")
if visual["production_manifest"].get("body_sha256") != body_hash:
    fail("manifest body hash mismatch")
if visual["qa_result"].get("status") != "pass" or visual["production_manifest"].get("qa_status") != "pass":
    fail("QA/manifest is not passing")
if not visual["assets"] or any(not a.get("synthetic") for a in visual["assets"]):
    fail("all fixture assets must be declared synthetic")
for out in visual["render_outputs"]:
    path = out["path"]
    if Path(path).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", path) or path.startswith(("/", "\\\\")):
        fail(f"absolute output path is forbidden: {path}")
    actual = hashlib.sha256((DEMO / path).read_bytes()).hexdigest()
    if actual != out["sha256"]:
        fail(f"asset hash mismatch: {path}")
if visual["production_manifest"].get("page_outputs") != [o["path"] for o in visual["render_outputs"]]:
    fail("manifest output list mismatch")
print("PASS: static synthetic Topic -> Keyword -> Writing -> approval mock -> Visual -> QA/Manifest fixture")
print("NOTE: this validates fixture consistency only; it does not execute the six Skills or render images.")



