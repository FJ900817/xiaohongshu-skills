"""Compute Phase 2D readiness; reports categories/counts, never matched private values."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))
    return ok

def main() -> int:
    outcomes=[]
    staging = ROOT / "00_staging"
    outcomes.append(check("public workspace excludes private staging", not staging.exists(), "private source copy must stay outside public root"))
    # Scan text/build inputs for high-confidence secret, identity and absolute-user-path patterns.
    patterns = {
      "user_absolute_path": re.compile(r"(?i)(?:[A-Z]:\\Users\\(?!\.\.\.|<)[A-Za-z0-9._-]+\\|/Users/(?!\.\.\.|<)[A-Za-z0-9._-]+/)"),
      "phone_number": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
      "email_address": re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Z]{2,}(?![\w.-])"),
      "token_prefix": re.compile(r"(?i)(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{15,})"),
      "credential_assignment": re.compile(r"(?i)(?:APP_SECRET|ACCESS_TOKEN|API_KEY)\s*[:=]\s*['\"]?(?!\$\{|\$)[A-Za-z0-9_./+=-]{12,}"),
      "feishu_real_id": re.compile(r"(?i)\b(?:bascn|tbl|fld|rec)[A-Za-z0-9]{12,}\b"),
      "uid_or_account_id": re.compile(r"(?i)\b(?:uid|user_id|account_id)\s*[:=]\s*[\x27\x22]?[A-Za-z0-9_-]{10,}"),
    }
    hit_counts={key:0 for key in patterns}
    for path in ROOT.rglob('*'):
      if not path.is_file() or '.git' in path.parts: continue
      try: text=path.read_text(encoding='utf-8-sig')
      except (UnicodeDecodeError, OSError): continue
      for key, pattern in patterns.items(): hit_counts[key] += len(pattern.findall(text))
    total_hits=sum(hit_counts.values())
    outcomes.append(check("public tree has no recognized private data patterns", total_hits == 0, f"pattern classes with hits={sum(v>0 for v in hit_counts.values())}"))
    # Every schema must parse as JSON Schema object; full fixture validation is done by the harness.
    schema_files=list((ROOT/'contracts').glob('*.schema.json'))
    schema_ok=True
    for path in schema_files:
      try:
        obj=json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(obj,dict) or obj.get('$schema') != 'https://json-schema.org/draft/2020-12/schema': schema_ok=False
      except Exception: schema_ok=False
    outcomes.append(check("all JSON Schemas load", bool(schema_files) and schema_ok, f"schemas={len(schema_files)}"))
    audit=(ROOT/'docs'/'PUBLIC_DEPENDENCY_AUDIT.md').read_text(encoding='utf-8-sig')
    allowed={"SAFE_TO_DISTRIBUTE","SAFE_AS_DEPENDENCY","USER_PROVIDED","OPTIONAL_EXTERNAL","PRIVATE_ONLY"}
    classified=[]
    for line in audit.splitlines():
      if line.startswith('|') and not line.startswith('|---'):
        cells=[c.strip().replace('`','').replace('*','') for c in line.strip('|').split('|')]
        if len(cells)>=3 and cells[0] not in {"类别/候选",""}: classified.append(cells[2])
    deps_ok=bool(classified) and all(x in allowed for x in classified)
    outcomes.append(check("dependency audit has no unresolved classifications", deps_ok, f"classified rows={len(classified)}"))
    harness=subprocess.run([sys.executable,str(ROOT/'scripts'/'validate_contracts.py')],capture_output=True,text=True)
    print(harness.stdout,end='')
    if harness.stderr: print(harness.stderr,end='',file=sys.stderr)
    outcomes.append(check("Contract Harness PASS", harness.returncode == 0))
    gi=ROOT/'.gitignore'
    gitignore=gi.read_text(encoding='utf-8-sig') if gi.exists() else ''
    runtime_ignored=all(x in gitignore for x in ('.user-data/','user-data/','user-project/','output/','.env'))
    public_runtime_visible=not any(line.strip()=='runtime/' for line in gitignore.splitlines())
    outcomes.append(check('user data ignored and public runtime source trackable', runtime_ignored and public_runtime_visible))
    no_git=not (ROOT/'.git').exists()
    outcomes.append(check("no Git repository initialized", no_git))
    ready=all(outcomes)
    print(f"PHASE 2D READY = {'YES' if ready else 'NO'}")
    return 0 if ready else 1
if __name__ == '__main__': raise SystemExit(main())



