from __future__ import annotations
import argparse,hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from schema_validation import load_json,validate_instance

def main():
    p=argparse.ArgumentParser(description='Validate approved Visual Output.'); p.add_argument('file',type=Path); p.add_argument('--finalization',type=Path,required=True); a=p.parse_args()
    try: obj=load_json(a.file); final=load_json(a.finalization)
    except Exception as e: print(f'FAIL Visual Output | $ | cannot read JSON: {e}'); return 1
    errors=validate_instance('visual-output.schema.json',obj)
    ref=obj.get('content_ref',{})
    if final.get('status')!='approved' or ref.get('status')!='approved': errors.append(('$.content_ref.status','Visual STOP: finalization must be human-approved'))
    if final.get('writing_id')!=ref.get('writing_id') or final.get('revision')!=ref.get('revision'): errors.append(('$.content_ref','writing_id/revision mismatch'))
    digest=hashlib.sha256(final.get('body','').encode('utf-8')).hexdigest()
    if digest!=final.get('body_sha256') or digest!=ref.get('body_sha256'): errors.append(('$.content_ref.body_sha256','finalized body hash mismatch'))
    pages={x.get('page_id') for x in obj.get('pages',[])}; assets={x.get('asset_id') for x in obj.get('assets',[])}
    if len(obj.get('pages',[]))!=8: errors.append(('$.pages','public Visual V1 requires exactly eight pages'))
    if len(pages)!=8: errors.append(('$.pages','page IDs must be unique across the eight pages'))
    for page in obj.get('pages',[]):
        for asset in page.get('asset_refs',[]):
            if asset not in assets: errors.append((f'$.pages[{page.get("page_id")}].asset_refs',f'missing asset {asset}'))
    for out in obj.get('render_outputs',[]):
        rel=Path(out.get('path',''))
        if rel.is_absolute() or '..' in rel.parts: errors.append(('$.render_outputs.path','unsafe path')); continue
        target=a.file.parent/rel
        if not target.is_file(): errors.append((f'$.render_outputs[{out.get("page_id")}].path','file missing'))
        elif hashlib.sha256(target.read_bytes()).hexdigest()!=out.get('sha256'): errors.append((f'$.render_outputs[{out.get("page_id")}].sha256','hash mismatch'))
        elif out.get('format')=='svg':
            try:
                root=ET.parse(target).getroot()
                if not root.tag.endswith('svg'): errors.append((f'$.render_outputs[{out.get("page_id")}].format','file is not an SVG document'))
                if int(root.attrib.get('width',0))!=out.get('width') or int(root.attrib.get('height',0))!=out.get('height'): errors.append((f'$.render_outputs[{out.get("page_id")}].dimensions','SVG dimensions do not match manifest'))
                texts=[(el.text or '').strip() for el in root.iter() if el.tag.endswith('text')]
                if not texts or any(not x for x in texts): errors.append((f'$.render_outputs[{out.get("page_id")}].text','SVG contains empty/missing text nodes'))
            except (ET.ParseError,ValueError,OSError) as exc: errors.append((f'$.render_outputs[{out.get("page_id")}].svg',f'invalid SVG: {exc}'))
        if out.get('page_id') not in pages: errors.append(('$.render_outputs.page_id','unknown page'))
    manifest=obj.get('production_manifest',{})
    if manifest.get('page_outputs')!=[x.get('path') for x in obj.get('render_outputs',[])]: errors.append(('$.production_manifest.page_outputs','output list mismatch'))
    if manifest.get('qa_status')!='pass' or obj.get('qa_result',{}).get('status')!='pass': errors.append(('$.qa_result.status','QA must pass'))
    for field,why in errors: print(f'FAIL Visual Output | {field} | {why}')
    if not errors: print('PASS Visual Output')
    return int(bool(errors))
if __name__=='__main__': raise SystemExit(main())
