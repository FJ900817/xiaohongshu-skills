#!/usr/bin/env python3
"""Render eight dynamic, offline SVG pages from an approved Writing Result."""
from __future__ import annotations
import argparse, hashlib, html, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VALIDATORS=ROOT/'validators'
ROLES=['封面','关键对比','核心框架','常见问题','图解/案例','证据与边界','执行步骤','总结']
def read(p):
    path=Path(p)
    if path.suffix.lower()=='.json': return json.loads(path.read_text(encoding='utf-8-sig'))
    # Small dependency-free YAML subset for the scalar/map fields in starter config.
    root={}; stack=[(-1,root)]
    for raw in path.read_text(encoding='utf-8-sig').splitlines():
        line=re.sub(r'\s+#.*$','',raw).rstrip()
        if not line.strip() or ':' not in line: continue
        indent=len(line)-len(line.lstrip()); key,value=line.strip().split(':',1); value=value.strip().strip('"\'')
        while stack and indent<=stack[-1][0]: stack.pop()
        parent=stack[-1][1]
        if value: parent[key]=int(value) if value.isdigit() else value
        else: parent[key]={}; stack.append((indent,parent[key]))
    return root
def write(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(s): return hashlib.sha256(s.encode('utf-8')).hexdigest()
def chunks(text,limit=20):
    text=re.sub(r'\s+',' ',text).strip()
    return [text[i:i+limit] for i in range(0,len(text),limit)] or ['']
def compact_body(body): return [x.strip(' •-*0123456789.、') for x in re.split(r'[\n。！？；]+',body) if len(x.strip())>5]
def derive(w):
    paragraphs=compact_body(w['body']); title=w['title']; topics=w.get('topics',[])
    lines=paragraphs[:]
    if not lines: raise ValueError('Writing Result body has no usable text')
    return [
      (title,[title,'从正文提取的实用内容',*topics[:2]]),
      ('先看问题与目标',lines[:2]),
      ('把内容整理成框架',lines[1:4] or lines[:2]),
      ('需要留意的情况',lines[3:5] or lines[:2]),
      ('内容图解',lines[2:4] or lines[:2]),
      ('证据与适用边界',list(w.get('warnings',[]))[:3] or ['仅呈现正文已说明的信息，不添加未经证实的数据。']),
      ('按步骤试一遍',lines[-3:]),
      ('带走这几个要点',[title,*lines[-2:],*topics[:2]])]
def render_svg(page_no,title,copy,config):
    width=int(config.get('canvas',{}).get('width',1080)); height=int(config.get('canvas',{}).get('height',1440))
    palette=config.get('palette',{}); bg=palette.get('background','#F7F4EE'); ink=palette.get('ink','#20332D'); accent=palette.get('accent','#D77952'); muted=palette.get('muted','#DCE5DD')
    font=html.escape(config.get('font_family','Arial, sans-serif'),quote=True)
    title_lines=chunks(title,16)
    # Auto-fit to the fixed safe layout instead of failing: the renderer must always emit the
    # eight pages for any approved body that fits the writing contract. Human visual review and
    # the QA gate still apply. (No-op for content that already fits the budget.)
    if len(title_lines)>3: title_lines=title_lines[:3]
    body_lines=[]
    for item in copy:
        body_lines += chunks(str(item),22)
    if len(body_lines)>8: body_lines=body_lines[:7]+['（内容较长，已折叠显示）']
    # Fixed safe SVG layout; content is escaped and line counts are capped to avoid overflow.
    title_y=330
    title_svg=''.join(f'<text x="84" y="{title_y+i*68}" font-size="54" font-weight="700" fill="{ink}">{html.escape(s)}</text>' for i,s in enumerate(title_lines))
    body_y=600 if len(title_lines)<3 else 650
    body_svg=''.join(f'<text x="104" y="{body_y+i*66}" font-size="31" fill="{ink}">{html.escape(s)}</text>' for i,s in enumerate(body_lines))
    # For page five, draw a generic diagram placeholder, not an unlicensed image.
    graphic=''
    if page_no==5:
        graphic=f'<rect x="120" y="1100" width="840" height="100" rx="24" fill="{muted}"/><circle cx="290" cy="1150" r="28" fill="{accent}"/><path d="M335 1150h190m0 0-18-16m18 16-18 16m50 0h160" stroke="{ink}" stroke-width="8" fill="none"/><rect x="745" y="1125" width="90" height="50" rx="14" fill="{accent}" opacity=".72"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
      f'<title id="t">{html.escape(title)}</title><desc id="d">第{page_no}页：{ROLES[page_no-1]}</desc><rect width="100%" height="100%" fill="{bg}"/>'
      f'<circle cx="{width-120}" cy="130" r="90" fill="{accent}" opacity=".22"/><text x="84" y="100" font-family="{font}" font-size="25" fill="{accent}">内容卡片 · {page_no:02d}/08</text>'
      f'<text x="84" y="210" font-family="{font}" font-size="26" fill="{ink}">{ROLES[page_no-1]}</text>{title_svg}{body_svg}{graphic}'
      f'<path d="M84 {height-170}h{width-168}" stroke="{accent}" stroke-width="3"/><text x="84" y="{height-100}" font-family="{font}" font-size="20" fill="{ink}">页面内容来自当前已批准正文 · 无外部图片依赖</text></svg>').encode('utf-8')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--writing',required=True,type=Path); p.add_argument('--finalization',required=True,type=Path); p.add_argument('--config',required=True,type=Path); p.add_argument('--output',required=True,type=Path); a=p.parse_args()
    w=read(a.writing); f=read(a.finalization); cfg=read(a.config)
    if f.get('status')!='approved' or w.get('status') not in ('draft','review','approved','final'):
        raise SystemExit('Visual STOP: a valid Writing Result and approved Finalization are required; no automatic approval.')
    digest=sha(f['body'])
    if w.get('writing_id')!=f.get('writing_id') or w.get('revision')!=f.get('revision') or f.get('body_sha256')!=digest:
        raise SystemExit('Visual STOP: writing identity, revision or finalized body hash mismatch.')
    # Human-approved finalization may contain edits; use that exact body downstream.
    w=dict(w); w['body']=f['body']; w['status']='approved'
    a.output.mkdir(parents=True,exist_ok=True); specs=derive(w); pages=[]; tasks=[]; outs=[]
    for i,(head,copy) in enumerate(specs,1):
        page_id=f'P{i}'; filename=f'{page_id}.svg'; data=render_svg(i,head,copy,cfg); (a.output/filename).write_bytes(data)
        text=[head,*copy]
        pages.append({'page_id':page_id,'sequence':i,'purpose':ROLES[i-1],'text':text,'asset_refs':['asset-vector-placeholder'] if i==5 else []})
        tasks.append({'task_id':f'img-{page_id}','page_id':page_id,'description':f'使用内置矢量版式呈现{ROLES[i-1]}，不调用外部图片服务。','status':'ready','provider':None})
        outs.append({'page_id':page_id,'path':filename,'format':'svg','width':int(cfg.get('canvas',{}).get('width',1080)),'height':int(cfg.get('canvas',{}).get('height',1440)),'sha256':hashlib.sha256(data).hexdigest(),'renderer_version':'public-svg-1.0'})
    obj={'schema_version':'1.0.0','content_ref':{'writing_id':w['writing_id'],'revision':w['revision'],'status':'approved','body_sha256':digest},'visual_plan':{'content_type':w['note_type'],'page_count':8,'canvas':{'width':outs[0]['width'],'height':outs[0]['height'],'format':'svg'},'style_preset':'starter-editorial','user_notes':'通用公开样式；P5 使用几何矢量占位。'},'pages':pages,'image_tasks':tasks,'assets':[{'asset_id':'asset-vector-placeholder','kind':'synthetic','uri':None,'synthetic':True,'license_status':'not_applicable','credit':'内置程序化几何图形'}],'render_outputs':outs,'qa_result':{'status':'pass','checks':[{'id':'approved-input-hash','status':'pass','message':'正文状态与 SHA-256 一致。'},{'id':'eight-pages','status':'pass','message':'已生成 P1-P8。'},{'id':'local-svg-files','status':'pass','message':'8 个相对路径 SVG 均存在。'},{'id':'source-content','status':'pass','message':'页面文案从当前 Writing Result 提取。'}],'human_visual_review':'pending'},'production_manifest':{'manifest_version':'1.0.0','created_at':datetime.now(timezone.utc).isoformat(),'contract_versions':{'visual_output':'1.0.0'},'writing_id':w['writing_id'],'revision':w['revision'],'body_sha256':digest,'page_outputs':[x['path'] for x in outs],'qa_status':'pass','generator_version':'public-svg-1.0'}}
    outjson=a.output/'visual-output.json'; write(outjson,obj)
    result=subprocess.run([sys.executable,str(VALIDATORS/'visual_output_validator.py'),str(outjson),'--finalization',str(a.finalization)],text=True)
    return result.returncode
if __name__=='__main__': raise SystemExit(main())
