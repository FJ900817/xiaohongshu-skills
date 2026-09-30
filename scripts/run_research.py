"""Run offline Research Core with an explicit local JSON source adapter."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validators'))
sys.path.insert(0,str(ROOT/'skills'/'research'))
sys.path.insert(0,str(ROOT/'adapters'/'research'))
from schema_validation import load_json,validate_instance
from engine import build_result
from local_json_source import load_sources

def main():
    p=argparse.ArgumentParser(); p.add_argument('--request',type=Path,required=True); p.add_argument('--sources',type=Path); p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); request=load_json(a.request)
    errors=validate_instance('research-request.schema.json',request)
    if errors:
        for field,reason in errors: print(f'FAIL Research Request | {field} | {reason}')
        return 1
    result=build_result(request,load_sources(a.sources) if a.sources else [])
    errors=validate_instance('research-result.schema.json',result)
    if errors:
        for field,reason in errors: print(f'FAIL Research Result | {field} | {reason}')
        return 1
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS Research Request Schema'); print('PASS Research Result Schema')
    return 0
if __name__=='__main__': raise SystemExit(main())
