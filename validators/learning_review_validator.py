from __future__ import annotations
import argparse,hashlib
from pathlib import Path
from schema_validation import load_json,validate_instance

def main():
    p=argparse.ArgumentParser(description='Validate a proposed Learning Review; never apply suggestions.')
    p.add_argument('file',type=Path); p.add_argument('--original',type=Path); p.add_argument('--final',type=Path)
    a=p.parse_args()
    try: obj=load_json(a.file)
    except Exception as e: print(f'FAIL Learning Review | $ | cannot read JSON: {e}'); return 1
    errors=validate_instance('learning-review.schema.json',obj)
    if obj.get('status')!='proposed' or obj.get('approval_required') is not True: errors.append(('$.approval_required','review must remain a proposal requiring human approval'))
    categories={'core_rule_candidate':'core','account_adapter_candidate':'adapter','one_off_preference':'one_off'}
    for i,item in enumerate(obj.get('suggested_rules',[])):
        if categories.get(item.get('category'))!=item.get('scope'): errors.append((f'$.suggested_rules[{i}].scope','category and scope are inconsistent'))
    adapter_ids={x.get('proposal_id') for x in obj.get('suggested_adapter_changes',[])}
    expected={x.get('proposal_id') for x in obj.get('suggested_rules',[]) if x.get('category')=='account_adapter_candidate'}
    if adapter_ids!=expected: errors.append(('$.suggested_adapter_changes','must mirror only Account Adapter proposals'))
    if a.original:
        original=load_json(a.original)
        if original.get('writing_id')!=obj.get('writing_id'): errors.append(('$.writing_id','does not match original Writing Result'))
    if a.final:
        final=load_json(a.final)
        if final.get('status')!='approved': errors.append(('$.final','Learning requires an approved Finalization'))
        if final.get('writing_id')!=obj.get('writing_id') or final.get('revision')!=obj.get('revision'): errors.append(('$.final','writing_id/revision mismatch'))
        if hashlib.sha256(final.get('body','').encode('utf-8')).hexdigest()!=final.get('body_sha256'): errors.append(('$.final.body_sha256','approved body hash mismatch'))
    for field,reason in errors: print(f'FAIL Learning Review | {field} | {reason}')
    if not errors: print('PASS Learning Review')
    return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
