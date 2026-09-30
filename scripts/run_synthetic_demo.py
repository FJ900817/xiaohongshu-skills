"""Deterministic, offline end-to-end executor for the four public production Skills.
All approvals are named synthetic mocks; never use this executor as a real approval system.
"""
from __future__ import annotations
import argparse, hashlib, html, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'examples'/'synthetic'/'demo-project'
INPUT=DEMO/'input'
OUT=DEMO/'artifacts'
VALIDATORS=ROOT/'validators'

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(data): return hashlib.sha256(data).hexdigest()
def validate_cli(script,*args):
    result=subprocess.run([sys.executable,str(VALIDATORS/script),*[str(x) for x in args]],cwd=ROOT,capture_output=True,text=True)
    print(result.stdout,end='')
    if result.stderr: print(result.stderr,end='',file=sys.stderr)
    if result.returncode: raise RuntimeError(f'{script} failed')
def validate_schema(schema,obj,label):
    sys.path.insert(0,str(VALIDATORS))
    from schema_validation import validate_instance
    errors=validate_instance(schema,obj)
    if errors:
        for field,reason in errors: print(f'FAIL {label} | {field} | {reason}')
        raise RuntimeError(f'{label} schema validation failed')
    print(f'PASS {label} schema')
def render_svg(page,number,config):
    bg=config['palette']['background']; ink=config['palette']['ink']; accent=config['palette']['accent']
    title=html.escape(page['title']); lines=''.join(f'<text x="88" y="{430+i*88}" font-size="42" fill="{ink}">{html.escape(line)}</text>' for i,line in enumerate(page['lines']))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1440" viewBox="0 0 1080 1440" role="img" aria-labelledby="title desc">
<title id="title">{title}</title><desc id="desc">合成家居整理演示页 {number}/8，无真实品牌素材。</desc>
<rect width="1080" height="1440" fill="{bg}"/><circle cx="900" cy="180" r="115" fill="{accent}" opacity=".22"/>
<text x="88" y="118" font-family="sans-serif" font-size="30" fill="{accent}">SYNTHETIC HOME GUIDE · {number:02d}/08</text>
<text x="88" y="300" font-family="sans-serif" font-size="66" font-weight="700" fill="{ink}">{title}</text>
{lines}<path d="M88 1190h904" stroke="{accent}" stroke-width="3"/><text x="88" y="1280" font-family="sans-serif" font-size="25" fill="{ink}">合成演示内容｜请按实际户型自行调整</text></svg>'''
    return svg.encode('utf-8')
def main():
    parser=argparse.ArgumentParser(description='Run the offline six-Skill synthetic workflow.')
    parser.add_argument('--no-research',action='store_true',help='Skip optional Research; Topic Planning still runs from the brief.')
    parser.add_argument('--no-learning',action='store_true',help='Skip the independent Learning side loop.')
    args=parser.parse_args()
    # User inputs are synthetic, replaceable files; no external services or credentials.
    profile=read(INPUT/'account-profile.json'); brief=read(INPUT/'brief.json'); catalog=read(INPUT/'keyword_catalog.json'); visual_config=read(INPUT/'visual-config.json')
    if not all(x.get('synthetic') for x in (profile,catalog,brief,visual_config)): raise RuntimeError('E2E refuses non-synthetic fixture inputs')
    validate_schema('account-profile.schema.json',profile,'Account Profile')
    OUT.mkdir(parents=True,exist_ok=True)
    research_result=None
    if not args.no_research:
        request_path=INPUT/'research-request.json'; source_path=INPUT/'research-sources.json'; research_path=OUT/'research-result.json'
        command=[sys.executable,str(ROOT/'scripts'/'run_research.py'),'--request',str(request_path),'--sources',str(source_path),'--output',str(research_path)]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        print(result.stdout,end='')
        if result.stderr: print(result.stderr,end='',file=sys.stderr)
        if result.returncode: raise RuntimeError('Research adapter failed')
        research_result=read(research_path)
        validate_cli('research_result_validator.py',research_path,'--request',request_path)
    candidates=[
      {'topic_id':'home-topic-001','title_direction':'小户型玄关收纳：用三步整理进门物品','audience':profile['audience']['description'],'core_problem':'进门后的鞋包、钥匙和随身物品容易混放，取放不顺手。','core_answer':'先按使用频率分类，再划定临时放置区和固定归位点，最后用短流程维护。','note_type':'search','content_goal':brief['content_goal'],'why_this_topic':'与账号的玄关整理方向及本轮实用目标直接对应；步骤可在不购买新产品时尝试。','evidence':[{'kind':'synthetic','summary':'仅为合成场景推演，不代表真实调研。','source_ref':None,'synthetic':True,'limitations':['没有真实用户访谈或平台搜索数据']}],'risk':{'level':'low','flags':['synthetic_demo'],'notes':['不承诺收纳效果或面积变化']},'synthetic':True},
      {'topic_id':'home-topic-002','title_direction':'玄关总是复乱？从高频物品开始安排固定位置','audience':profile['audience']['description'],'core_problem':'高频物品没有固定位置，容易在玄关累积。','core_answer':'先挑出每天使用的物品，再为它们安排容易取放的固定位置。','note_type':'recommendation','content_goal':brief['content_goal'],'why_this_topic':'同一目标的维护角度候选，与第一题形成区分。','evidence':[{'kind':'synthetic','summary':'仅为合成候选。','source_ref':None,'synthetic':True,'limitations':['没有真实调研']}],'risk':{'level':'low','flags':['synthetic_demo'],'notes':[]},'synthetic':True}
    ]
    if research_result and research_result.get('candidate_topics'):
        researched=research_result['candidate_topics'][0]
        candidates[0].update({
            'topic_id':researched['topic_id'], 'title_direction':researched['title_direction'],
            'core_problem':researched['core_problem'], 'core_answer':researched['content_angle'],
            'note_type':researched['note_type'],
            'evidence':[{'kind':'synthetic' if research_result['synthetic'] else 'source',
                         'summary':f"Research evidence refs: {', '.join(researched['evidence_refs'])}",
                         'source_ref':research_result['research_id'],'synthetic':research_result['synthetic'],
                         'limitations':research_result['limitations']}]
        })
    candidate_bundle={'schema_version':'1.0.0','candidates':candidates,'decision_required':True,'synthetic':True,'research_result_ref':research_result['research_id'] if research_result else None}
    write(OUT/'topic-candidates.json',candidate_bundle)
    selected=candidates[0]
    topic_approval={'gate':'topic_approval_mock','decision':'approve','selected_topic_id':selected['topic_id'],'approved_by':'synthetic_human_mock','approved_at':datetime.now(timezone.utc).isoformat(),'synthetic':True}
    write(OUT/'topic-approval-mock.json',topic_approval)
    topic_result={'schema_version':'1.0.0','topic_id':selected['topic_id'],'note_type':selected['note_type'],'content_goal':selected['content_goal'],'topic':{'working_title':selected['title_direction'],'angle':selected['core_answer']},'synthetic':True}
    validate_schema('topic-planning-result.schema.json',topic_result,'Topic Planning Result')
    write(OUT/'topic-planning-result.json',topic_result)
    now=datetime.now(timezone.utc).isoformat()
    task={'schema_version':'1.0.0','task_id':'home-task-001','status':'approved','profile_ref':profile['profile_id'],'content_goal':selected['content_goal'],'audience':profile['audience'],'topic':{'topic_id':selected['topic_id'],'working_title':selected['title_direction'],'angle':selected['core_answer'],'source':'synthetic_topic_planning'},'note_type':selected['note_type'],'core_problem':selected['core_problem'],'core_answer':selected['core_answer'],'title_requirement':{'goal':'包含明确搜索问题和可执行收益','must_include':['小户型玄关收纳'],'avoid':['收纳空间翻倍','保证不再凌乱']},'keyword_request':{'mode':'plan','seed_terms':['小户型玄关收纳'],'priority':'相关、自然，不推断搜索量'},'writing_constraints':{'must_do':['解释适用边界','提供可执行步骤'],'must_avoid':['虚构亲身经历','无依据的产品效果承诺'],'body_length':{'min':100,'max':900}},'offer_ref':None,'cta':'邀请读者分享自己最难整理的玄关物品。','topics':['#小户型收纳','#玄关整理'],'risk':selected['risk'],'evidence':selected['evidence'],'approval':{'state':'approved','approved_by':'synthetic_human_mock','approved_at':now,'note':'Demo-only topic approval mock.'}}
    write(OUT/'task-card.json',task)
    validate_cli('task_card_validator.py',OUT/'task-card.json')
    # Keyword Skill: rank only the supplied synthetic catalog by priority; user approval is explicit mock.
    pool=catalog['keywords']; selected_terms=sorted(pool,key=lambda x:x['priority'])[:2]
    keywords=[]
    for idx,item in enumerate(selected_terms):
        keywords.append({'keyword_id':item['keyword_id'],'phrase':item['phrase'],'intent':item['intent'],'level':item['level'],'priority':item['priority'],'source':{'kind':'synthetic_catalog','label':'Synthetic Demo Catalog','uri':None},'evidence':[{'summary':'Synthetic phrase/intent fixture; no demand or performance claim.','synthetic':True}],'status':'locked','role':'main' if idx==0 else 'secondary','placement':['title','body','topic'] if idx==0 else ['body','tag'],'occurrence_rule':{'mode':'natural','note':'Use where semantically natural; no density target.'},'topic_tag_mapping':['#小户型收纳'] if idx==0 else ['#玄关收纳方法'],'approval_state':'approved'})
    plan={'schema_version':'1.0.0','plan_id':'home-keyword-plan-001','task_id':task['task_id'],'status':'approved','keywords':keywords,'approval':{'state':'approved','approved_by':'synthetic_human_mock','approved_at':now}}
    write(OUT/'keyword-plan.json',plan); write(OUT/'keyword-approval-mock.json',{'gate':'keyword_approval_mock','decision':'approve','approved_plan_id':plan['plan_id'],'approved_by':'synthetic_human_mock','approved_at':now,'synthetic':True})
    validate_cli('keyword_plan_validator.py',OUT/'keyword-plan.json','--task-card',OUT/'task-card.json')
    # Writing Skill consumes locked terms verbatim; output remains draft.
    title='小户型玄关收纳：不用添置新家具，先试这三步'
    body=('小户型玄关收纳，不一定要先买新的收纳家具。先观察每天带进带出的物品，再按使用频率安排位置。\n\n'
          '第一步，把鞋、包、钥匙等物品分开看：哪些每天用，哪些只是偶尔用。先处理最常出现的一类，不必一次整理整个家。\n\n'
          '第二步，为高频物品划出一个固定、顺手的位置。可以利用已有的托盘、挂钩或柜内空格；是否适合要看实际尺寸和租住条件。\n\n'
          '第三步，给临时物品留一个小区域，回家后再按用途归位。这个玄关收纳方法强调方便维护，不承诺空间变大或永远不乱。\n\n'
          '如果入口很窄，优先保证通行安全，不要把物品放在门扇、消防通道或容易绊倒的位置。\n\n'
          '这是合成演示稿，不含真实用户案例或产品推荐。你可以先从每天最常找不到的一件物品开始。')
    usage=[{'keyword_id':k['keyword_id'],'phrase':k['phrase'],'found':k['phrase'] in (title+'\n'+body),'placements':k['placement']} for k in keywords]
    writing={'schema_version':'1.0.0','writing_id':'home-writing-001','draft_id':'home-draft-001','revision':1,'task_id':task['task_id'],'note_type':task['note_type'],'keyword_plan_ref':plan['plan_id'],'title':title,'body':body,'topics':['#小户型收纳','#玄关整理','#玄关收纳方法'],'pinned_comment':'你最常在玄关找不到什么？（合成示例互动句）','secondary_comment':None,'keyword_usage_report':usage,'warnings':['Synthetic content only; verify dimensions, safety, and local requirements for real use.'],'status':'draft','synthetic':True}
    write(OUT/'writing-result.json',writing)
    validate_cli('writing_validator.py',OUT/'writing-result.json','--task-card',OUT/'task-card.json','--keyword-plan',OUT/'keyword-plan.json')
    # Human final approval is a named mock gate; it is not automatic approval in a real workflow.
    digest=sha(writing['body'].encode('utf-8'))
    final={'schema_version':'1.0.0','writing_id':writing['writing_id'],'revision':writing['revision'],'status':'approved','body':writing['body'],'body_sha256':digest,'updated_at':now,'submitted_by':'synthetic_author','approved_by':'synthetic_human_mock','finalized_at':now,'rejection_reason':None,'supersedes_revision':None}
    write(OUT/'finalization.json',final); write(OUT/'final-approval-mock.json',{'gate':'final_approval_mock','decision':'approve','writing_id':writing['writing_id'],'revision':writing['revision'],'body_sha256':digest,'approved_by':'synthetic_human_mock','approved_at':now,'synthetic':True})
    validate_cli('finalization_validator.py',OUT/'finalization.json','--require-approved')
    # Visual Skill: generate a fresh 8-page generic SVG set with no external assets.
    page_specs=[
      ('Cover','小户型玄关收纳：先试这三步',['不用急着买收纳家具','先观察每天带进带出的物品','按频率分区，再安排归位点']),
      ('Contrast','先分清“每天用”和“偶尔用”',['常用物品：顺手、好拿','偶尔用品：收在不挡路处','不要把过道变成临时仓库']),
      ('Framework','一个简单整理框架',['分类：先看物品用途','分区：按使用频率安排位置','归位：留出临时物品缓冲区']),
      ('Problems','容易反复变乱的三个原因',['高频物品没有固定位置','临时放置区越堆越大','收纳方案挡住门扇或通道']),
      ('Synthetic Case','合成场景：窄玄关',['设一个钥匙托盘和一个包袋挂点','鞋物按当前使用需求取舍','不适用时按实际户型调整']),
      ('Check Signals','用日常观察判断是否顺手',['进门时是否容易放下随身物品？','出门前是否能快速找到常用物？','通道是否保持畅通？不编造效果数字']),
      ('Steps','从一个小区域开始',['1. 选一种每天使用的物品','2. 找到不挡路的固定位置','3. 试用后再调整，不必一次买齐']),
      ('Summary','小结：先观察，再分区',['小户型玄关收纳从高频物品开始','留出安全通行和临时缓冲空间','本页内容为合成示例，不是效果保证'])]
    pages=[]; assets=[]; tasks=[]; renders=[]; outdir=OUT/'pages'; outdir.mkdir(parents=True,exist_ok=True)
    for i,(purpose,heading,lines) in enumerate(page_specs,1):
        page_id=f'page-{i:02d}'; asset_id=f'asset-{i:02d}'; rel=f'pages/{page_id}.svg'
        data=render_svg({'title':heading,'lines':lines},i,visual_config); target=OUT/rel; target.write_bytes(data); digest_page=sha(data)
        pages.append({'page_id':page_id,'sequence':i,'purpose':purpose,'text':[heading,*lines],'asset_refs':[asset_id]})
        assets.append({'asset_id':asset_id,'kind':'synthetic','uri':rel,'synthetic':True,'license_status':'not_applicable','credit':None})
        tasks.append({'task_id':f'image-task-{i:02d}','page_id':page_id,'description':'Render supplied synthetic page text using local generic SVG layout.','status':'ready','provider':None})
        renders.append({'page_id':page_id,'path':rel,'format':'svg','width':1080,'height':1440,'sha256':digest_page,'renderer_version':'public-svg-demo-1.0'})
    checks=[{'id':'approved-writing-hash','status':'pass','message':'Finalization status and body hash verified.'},{'id':'page-and-asset-refs','status':'pass','message':'All eight pages reference existing synthetic assets.'},{'id':'relative-paths-and-hashes','status':'pass','message':'Rendered SVG files exist with matching SHA-256.'},{'id':'external-assets','status':'pass','message':'No external fonts, images, APIs, or credentials.'}]
    versions={'task_card':'1.0.0','note_type':'1.0.0','keyword_plan':'1.0.0','writing_result':'1.0.0','finalization':'1.0.0','visual_output':'1.0.0','production_manifest':'1.0.0'}
    manifest={'manifest_version':'1.0.0','created_at':now,'contract_versions':versions,'writing_id':writing['writing_id'],'revision':writing['revision'],'body_sha256':digest,'page_outputs':[x['path'] for x in renders],'qa_status':'pass','generator_version':'public-svg-demo-1.0'}
    visual={'schema_version':'1.0.0','content_ref':{'writing_id':writing['writing_id'],'revision':writing['revision'],'status':'approved','body_sha256':digest},'visual_plan':{'content_type':task['note_type'],'page_count':8,'canvas':visual_config['canvas'],'style_preset':visual_config['style_preset'],'user_notes':'New generic synthetic template; no third-party images or font files.'},'pages':pages,'image_tasks':tasks,'assets':assets,'render_outputs':renders,'qa_result':{'status':'pass','checks':checks,'human_visual_review':'approved'},'production_manifest':manifest}
    write(OUT/'visual-output.json',visual); write(OUT/'production-manifest.json',manifest)
    validate_cli('visual_output_validator.py',OUT/'visual-output.json','--finalization',OUT/'finalization.json')
    validate_schema('production-manifest.schema.json',manifest,'Production Manifest')
    learning_status='SKIPPED'
    if not args.no_learning:
        # Separate synthetic edit: Learning observes a reviewed change without changing Core output.
        learning_final=dict(final)
        learning_final['body']=writing['body'].replace('先观察每天带进带出的物品','先观察每天实际取放的物品')
        learning_final['body_sha256']=sha(learning_final['body'].encode('utf-8'))
        learning_final['approved_by']='synthetic_learning_human_mock'
        learning_final['updated_at']=now; learning_final['finalized_at']=now
        learning_final_path=OUT/'learning-approved-finalization.json'
        write(learning_final_path,learning_final)
        validate_cli('finalization_validator.py',learning_final_path,'--require-approved')
        learning_path=OUT/'learning-review.json'
        review_command=[sys.executable,str(ROOT/'scripts'/'run_learning_review.py'),'--original',str(OUT/'writing-result.json'),'--final',str(learning_final_path),'--feedback',str(INPUT/'learning-feedback.json'),'--output',str(learning_path)]
        result=subprocess.run(review_command,cwd=ROOT,capture_output=True,text=True)
        print(result.stdout,end='')
        if result.stderr: print(result.stderr,end='',file=sys.stderr)
        if result.returncode: raise RuntimeError('Learning review failed')
        validate_cli('learning_review_validator.py',learning_path,'--original',OUT/'writing-result.json','--final',learning_final_path)
        decision_path=OUT/'learning-decision-mock.json'
        decision_command=[sys.executable,str(ROOT/'scripts'/'record_learning_decision.py'),'--review',str(learning_path),'--decision','accept','--output',str(decision_path),'--reviewer','synthetic_human_mock']
        result=subprocess.run(decision_command,cwd=ROOT,capture_output=True,text=True)
        print(result.stdout,end='')
        if result.stderr: print(result.stderr,end='',file=sys.stderr)
        if result.returncode: raise RuntimeError('Learning decision recording failed')
        learning_status='PASS'
    write(OUT/'run-report.json',{'status':'PASS','synthetic':True,'approvals':'mock-only','research_enabled':not args.no_research,'learning_status':learning_status,'steps':['Research Result (optional)' if not args.no_research else 'Research skipped','Topic candidates','Topic approval mock','Task Card compile','Keyword Plan','Keyword approval mock','Writing draft','Final approval mock','8-page SVG Visual','QA','Manifest','Learning proposal (independent side loop)' if not args.no_learning else 'Learning skipped'],'page_count':len(pages),'external_services':False,'private_staging_used':False,'limitations':['Deterministic mock executor; not an AI generation service.','Synthetic approval mocks must never be used for real publication.','Learning Accept mock records an approved proposal only; it never applies a rule.']})
    print(f'END_TO_END=PASS; pages={len(pages)}; output={OUT.relative_to(ROOT)}')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e: print(f'END_TO_END=FAIL | {e}',file=sys.stderr); raise
