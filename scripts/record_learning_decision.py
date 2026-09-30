"""Record an explicit accept/reject decision without applying the proposal."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validators'))
from schema_validation import load_json,validate_instance

def main():
    p=argparse.ArgumentParser(); p.add_argument('--review',type=Path,required=True); p.add_argument('--decision',choices=['accept','reject'],required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--reviewer',required=True)
    a=p.parse_args(); review=load_json(a.review); errors=validate_instance('learning-review.schema.json',review)
    if errors or review.get('status')!='proposed' or review.get('approval_required') is not True:
        for field,reason in errors: print(f'FAIL Learning Review | {field} | {reason}')
        if not errors: print('FAIL Learning Decision | $ | decision requires an unapproved proposal')
        return 1
    obj={'schema_version':'1.0.0','review_id':review['review_id'],'decision':a.decision,'recorded_status':'approved_proposal' if a.decision=='accept' else 'rejected_proposal','reviewer':a.reviewer,'recorded_at':datetime.now(timezone.utc).isoformat(),'applied':False,'modified_paths':[],'synthetic':review.get('synthetic',False)}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS Decision recorded; applied=false; modified_paths=0')
    return 0
if __name__=='__main__': raise SystemExit(main())
