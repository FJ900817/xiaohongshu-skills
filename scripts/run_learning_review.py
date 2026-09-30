"""Compare a draft to an approved Finalization and emit proposals only."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validators'))
sys.path.insert(0,str(ROOT/'skills'/'learning'))
from schema_validation import load_json,validate_instance
from engine import build_review

def main():
    p=argparse.ArgumentParser(); p.add_argument('--original',type=Path,required=True); p.add_argument('--final',type=Path,required=True); p.add_argument('--feedback',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--review-id',default='learning-review-demo-001')
    a=p.parse_args(); original=load_json(a.original); final=load_json(a.final); feedback=load_json(a.feedback)
    for name,obj in [('writing-result.schema.json',original),('finalization.schema.json',final),('learning-feedback.schema.json',feedback)]:
        errors=validate_instance(name,obj)
        if errors:
            for field,reason in errors: print(f'FAIL Input {name} | {field} | {reason}')
            return 1
    result=build_review(original,final,feedback,a.review_id)
    errors=validate_instance('learning-review.schema.json',result)
    if errors:
        for field,reason in errors: print(f'FAIL Learning Review | {field} | {reason}')
        return 1
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS Learning Review proposal emitted; no rule assets were modified.')
    return 0
if __name__=='__main__': raise SystemExit(main())
