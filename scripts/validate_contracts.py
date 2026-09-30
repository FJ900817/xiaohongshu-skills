"""Dependency-free JSON Schema subset harness for this repo's Draft 2020-12 contracts.
Implements exactly the keywords used by the checked-in schemas; fail-closed on unsupported keywords.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "contracts"
DEMO = ROOT / "examples" / "synthetic" / "demo-v1"

class SchemaError(Exception): pass

def pointer(doc: Any, ref: str) -> Any:
    if ref.startswith("#/"):
        node = doc
        for part in ref[2:].split("/"):
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node
    raise SchemaError(f"unsupported external ref: {ref}")

def type_ok(value: Any, expected: Any) -> bool:
    types = expected if isinstance(expected, list) else [expected]
    for typ in types:
        if typ == "null" and value is None: return True
        if typ == "object" and isinstance(value, dict): return True
        if typ == "array" and isinstance(value, list): return True
        if typ == "string" and isinstance(value, str): return True
        if typ == "boolean" and isinstance(value, bool): return True
        if typ == "integer" and isinstance(value, int) and not isinstance(value, bool): return True
        if typ == "number" and isinstance(value, (int, float)) and not isinstance(value, bool): return True
    return False

def validate(value: Any, schema: dict, root_doc: dict, path: str = "$", stack: tuple = ()) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    supported = {"$schema", "$id", "title", "description", "$comment", "$defs", "$ref", "type", "enum", "const", "required", "properties", "additionalProperties", "items", "minItems", "maxItems", "uniqueItems", "minLength", "maxLength", "pattern", "minimum", "maximum", "format", "allOf", "if", "then", "not"}
    unknown = set(schema) - supported
    if unknown: return [(path, f"unsupported schema keyword(s): {sorted(unknown)}")]
    if "$ref" in schema:
        ref = schema["$ref"]
        try:
            if ref.endswith(".json") and "#/" not in ref:
                target_doc = json.loads((CONTRACTS / ref).read_text(encoding="utf-8-sig"))
                target = target_doc
            else:
                target_doc, target = root_doc, pointer(root_doc, ref)
            errors += validate(value, target, target_doc, path, stack + (ref,))
        except Exception as exc:
            return [(path, f"cannot resolve $ref {ref}: {exc}")]
    if "type" in schema and not type_ok(value, schema["type"]):
        return errors + [(path, f"expected type {schema['type']}, got {type(value).__name__}")]
    if "const" in schema and value != schema["const"]: errors.append((path, f"must equal {schema['const']!r}"))
    if "enum" in schema and value not in schema["enum"]: errors.append((path, f"must be one of {schema['enum']!r}"))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append((f"{path}.{key}", "required field is missing"))
        props = schema.get("properties", {})
        for key, item in value.items():
            child = f"{path}.{key}"
            if key in props: errors += validate(item, props[key], root_doc, child, stack)
            elif schema.get("additionalProperties") is False: errors.append((child, "additional property is not allowed"))
            elif isinstance(schema.get("additionalProperties"), dict): errors += validate(item, schema["additionalProperties"], root_doc, child, stack)
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0): errors.append((path, f"must contain at least {schema['minItems']} item(s)"))
        if len(value) > schema.get("maxItems", float("inf")): errors.append((path, f"must contain at most {schema['maxItems']} item(s)"))
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True, ensure_ascii=False) for x in value}) != len(value): errors.append((path, "items must be unique"))
        if "items" in schema:
            for i, item in enumerate(value): errors += validate(item, schema["items"], root_doc, f"{path}[{i}]", stack)
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0): errors.append((path, f"must have at least {schema['minLength']} character(s)"))
        if len(value) > schema.get("maxLength", float("inf")): errors.append((path, f"must have at most {schema['maxLength']} character(s)"))
        if "pattern" in schema and re.search(schema["pattern"], value) is None: errors.append((path, f"does not match pattern {schema['pattern']!r}"))
        if schema.get("format") == "date-time":
            try: dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError: errors.append((path, "must be an ISO date-time"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", float("-inf")): errors.append((path, f"must be >= {schema['minimum']}"))
        if value > schema.get("maximum", float("inf")): errors.append((path, f"must be <= {schema['maximum']}"))
    for sub in schema.get("allOf", []): errors += validate(value, sub, root_doc, path, stack)
    if "if" in schema:
        if not validate(value, schema["if"], root_doc, path, stack) and "then" in schema: errors += validate(value, schema["then"], root_doc, path, stack)
    if "not" in schema and not validate(value, schema["not"], root_doc, path, stack): errors.append((path, "matches a forbidden schema"))
    return errors

def load_schema(name: str) -> dict: return json.loads((CONTRACTS / name).read_text(encoding="utf-8-sig"))
def load_fixture(name: str) -> Any: return json.loads((DEMO / name).read_text(encoding="utf-8-sig"))
def report(label: str, result: list[tuple[str, str]]) -> bool:
    if not result: print(f"PASS {label}"); return True
    for field, why in result: print(f"FAIL {label} | {field} | {why}")
    return False

def main() -> int:
    fixtures = [
      ("Account Profile", "account-profile.schema.json", "account-profile.json"),
      ("Topic Planning Result", "topic-planning-result.schema.json", "topic-planning-result.json"),
      ("Task Card", "task-card.schema.json", "task-card.json"),
      ("Keyword Plan", "keyword-plan.schema.json", "keyword-plan.json"),
      ("Writing Result", "writing-result.schema.json", "writing-result.json"),
      ("Finalization", "finalization.schema.json", "finalization-approved.json"),
      ("Visual Output", "visual-output.schema.json", "visual-output.json"),
      ("Production Manifest", "production-manifest.schema.json", "production-manifest.json"),
    ]
    passed = True
    objs = {}
    for label, sn, fn in fixtures:
      schema = load_schema(sn); obj = load_fixture(fn); objs[label] = obj
      passed = report(label, validate(obj, schema, schema)) and passed
    note_type_obj = {"schema_version": "1.0.0", "note_type": objs["Topic Planning Result"]["note_type"]}
    nsch = load_schema("note-type.schema.json")
    passed = report("Note Type Contract", validate(note_type_obj, nsch, nsch)) and passed
    topic, task, keyword, writing, final, visual, manifest = (objs[x] for x in ("Topic Planning Result", "Task Card", "Keyword Plan", "Writing Result", "Finalization", "Visual Output", "Production Manifest"))
    cross = []
    if task["topic"]["topic_id"] != topic["topic_id"]: cross.append(("Task Card.topic.topic_id", "does not match Topic Planning Result.topic_id"))
    for field in ("note_type", "content_goal"):
      if task[field] != topic[field]: cross.append((f"Task Card.{field}", f"does not match Topic Planning Result.{field}"))
    if keyword["status"] != "approved" or keyword["approval"]["state"] != "approved" or any(k["approval_state"] != "approved" or k["status"] != "locked" for k in keyword["keywords"]): cross.append(("Keyword Plan", "must be approved with selected keywords locked"))
    if keyword["task_id"] != task["task_id"]: cross.append(("Keyword Plan.task_id", "does not match Task Card.task_id"))
    if writing["task_id"] != task["task_id"] or writing["keyword_plan_ref"] != keyword["plan_id"]: cross.append(("Writing Result", "task_id/keyword_plan_ref does not match approved upstream objects"))
    if final["writing_id"] != writing["writing_id"] or final["revision"] != writing["revision"] or final["body"] != writing["body"]: cross.append(("Finalization", "writing_id/revision/body differs from Writing Result"))
    if visual["content_ref"]["writing_id"] != final["writing_id"] or visual["content_ref"]["revision"] != final["revision"] or visual["content_ref"]["body_sha256"] != final["body_sha256"]: cross.append(("Visual Output.content_ref", "does not reference the finalized writing revision/hash"))
    page_ids = {p["page_id"] for p in visual["pages"]}; asset_ids = {a["asset_id"] for a in visual["assets"]}
    if any(ref not in asset_ids for p in visual["pages"] for ref in p["asset_refs"]): cross.append(("Visual Output.pages[].asset_refs", "references a missing asset"))
    if any(x["page_id"] not in page_ids for x in visual["render_outputs"] + visual["image_tasks"]): cross.append(("Visual Output.render_outputs/image_tasks", "references a missing page"))
    if manifest != visual["production_manifest"]: cross.append(("Production Manifest", "does not exactly match Visual Output.production_manifest"))
    if manifest["page_outputs"] != [x["path"] for x in visual["render_outputs"]]: cross.append(("Production Manifest.page_outputs", "does not match render outputs"))
    passed = report("Cross-contract references", cross) and passed
    # Finalization transitions and hard Visual gate.
    allowed = {"draft": {"review", "rejected"}, "review": {"approved", "rejected", "revision_required"}, "rejected": {"revision_required"}, "revision_required": {"review"}, "approved": {"revision_required"}}
    def sequence_ok(seq):
      return all(b in allowed.get(a, set()) for a, b in zip(seq, seq[1:]))
    lifecycle_cases = [
      ("draft -> review -> approved", ["draft", "review", "approved"], True),
      ("rejected -> revision_required -> review -> approved", ["rejected", "revision_required", "review", "approved"], True),
      ("approved -> body edit invalidates approval", ["approved", "revision_required"], True),
    ]
    life_errors=[]
    for label, seq, expected in lifecycle_cases:
      if sequence_ok(seq) != expected: life_errors.append((label, "transition sequence rejected or accepted unexpectedly"))
    passed = report("Finalization transitions PASS cases", life_errors) and passed
    gate_errors=[]
    for status in ("draft", "review"):
      candidate = json.loads(json.dumps(visual)); candidate["content_ref"]["status"] = status
      result = validate(candidate, load_schema("visual-output.schema.json"), load_schema("visual-output.schema.json"))
      if not result: gate_errors.append((f"Visual Gate {status}", "unapproved content was accepted"))
    passed = report("Finalization Visual Gate FAIL cases", gate_errors) and passed
    # Hash and local asset checks are part of the interface handoff.
    asset_errors=[]
    body_sha = hashlib.sha256(final["body"].encode("utf-8")).hexdigest()
    if body_sha != final["body_sha256"]: asset_errors.append(("Finalization.body_sha256", "does not match body"))
    for output in visual["render_outputs"]:
      path = Path(output["path"])
      if path.is_absolute() or ".." in path.parts: asset_errors.append(("Visual Output.render_outputs.path", "must be a safe relative path")); continue
      target = DEMO / path
      if not target.is_file(): asset_errors.append((str(path), "render output is missing"))
      elif hashlib.sha256(target.read_bytes()).hexdigest() != output["sha256"]: asset_errors.append((str(path), "render output hash mismatch"))
    passed = report("Finalized body / visual asset hashes", asset_errors) and passed
    print(f"CONTRACT_HARNESS={'PASS' if passed else 'FAIL'}; SCHEMA_FIXTURES={len(fixtures)}")
    return 0 if passed else 1
if __name__ == "__main__": raise SystemExit(main())


