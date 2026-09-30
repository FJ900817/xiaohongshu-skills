from __future__ import annotations
import argparse
from pathlib import Path
from schema_validation import load_json,validate_instance

def main():
    p=argparse.ArgumentParser(description='Validate a proposed Research Result and its evidence references.')
    p.add_argument('file',type=Path); p.add_argument('--request',type=Path)
    a=p.parse_args()
    try: obj=load_json(a.file)
    except Exception as e: print(f'FAIL Research Result | $ | cannot read JSON: {e}'); return 1
    errors=validate_instance('research-result.schema.json',obj)
    source_ids={x.get('source_id') for x in obj.get('sources',[])}
    evidence_ids={x.get('evidence_id') for x in obj.get('evidence',[])}
    for i,item in enumerate(obj.get('evidence',[])):
        if item.get('source_id') not in source_ids: errors.append((f'$.evidence[{i}].source_id','must reference an included source'))
    for group in ('signals','user_problems','candidate_topics','candidate_keywords'):
        for i,item in enumerate(obj.get(group,[])):
            for ref in item.get('evidence_refs',[]):
                if ref not in evidence_ids: errors.append((f'$.{group}[{i}].evidence_refs',f'unknown evidence reference {ref}'))
    if obj.get('status')!='proposed': errors.append(('$.status','Research cannot approve or finalize a topic'))
    if a.request:
        req=load_json(a.request)
        if obj.get('research_id')!=req.get('research_id'): errors.append(('$.research_id','does not match Research Request'))
    for field,reason in errors: print(f'FAIL Research Result | {field} | {reason}')
    if not errors: print('PASS Research Result')
    return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
