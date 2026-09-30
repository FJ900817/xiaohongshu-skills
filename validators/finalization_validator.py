from __future__ import annotations
import argparse,hashlib
from pathlib import Path
from schema_validation import load_json,validate_instance
def main():
 p=argparse.ArgumentParser(description='Validate finalization lifecycle object.'); p.add_argument('file',type=Path); p.add_argument('--require-approved',action='store_true'); a=p.parse_args()
 try: obj=load_json(a.file)
 except Exception as e: print(f'FAIL Finalization | $ | cannot read JSON: {e}'); return 1
 errors=validate_instance('finalization.schema.json',obj)
 actual=hashlib.sha256(obj.get('body','').encode('utf-8')).hexdigest()
 if actual!=obj.get('body_sha256'): errors.append(('$.body_sha256','does not match body bytes; approval invalidated'))
 if a.require_approved and obj.get('status')!='approved': errors.append(('$.status','Visual requires human-approved status=approved'))
 if obj.get('status')=='approved' and (not obj.get('approved_by') or not obj.get('finalized_at')): errors.append(('$.approved_by','approved state requires approver and finalized_at'))
 for field,reason in errors: print(f'FAIL Finalization | {field} | {reason}')
 if not errors: print('PASS Finalization')
 return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
