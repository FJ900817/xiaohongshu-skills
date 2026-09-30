"""Evidence-bounded Research Core for explicitly supplied local records."""
from __future__ import annotations
from collections import Counter
from typing import Any

def build_result(request: dict[str, Any], source_rows: list[dict[str, Any]]) -> dict[str, Any]:
    sources=[]; evidence=[]; questions={}; problems={}; phrases={}; topic_rows=[]
    for row in source_rows:
        sid=row['source_id']; kind=row.get('source_type','local_json')
        if kind not in {'local_json','user_upload','csv','web','platform_adapter'}: kind='user_upload'
        sources.append({'source_id':sid,'source_type':kind,'title':row['title'],'uri':row.get('uri'),'captured_at':row.get('captured_at'),'synthetic':bool(row.get('synthetic',False))})
        summary=row.get('summary') or row.get('excerpt') or row['title']; ref=f'evidence-{sid}'
        evidence.append({'evidence_id':ref,'source_id':sid,'summary':str(summary)[:1000],'excerpt':row.get('excerpt'),'synthetic':bool(row.get('synthetic',False)),'limitations':row.get('limitations',[])})
        for q in row.get('user_questions',[]): questions.setdefault(str(q),[]).append(ref)
        for item in row.get('user_problems',[]): problems.setdefault(str(item),[]).append(ref)
        for pair in row.get('phrases',[]):
            if isinstance(pair,(list,tuple)) and len(pair)>=2: phrases.setdefault(str(pair[0]),[]).append((ref,str(pair[1])))
        for topic in row.get('candidate_topics',[]): topic_rows.append((topic,ref))
    signals=[{'signal_id':f'signal-{i:03d}','signal_type':'repeated_question' if len(set(refs))>1 else 'need','summary':f'用户提问：{question}','evidence_refs':sorted(set(refs)),'confidence':round(min(.9,.45+.12*(len(set(refs))-1)),2)} for i,(question,refs) in enumerate(questions.items(),1)]
    user_problems=[{'problem_id':f'problem-{i:03d}','summary':problem,'evidence_refs':sorted(set(refs)),'confidence':round(min(.9,.5+.1*(len(set(refs))-1)),2)} for i,(problem,refs) in enumerate(problems.items(),1)]
    candidate_topics=[]
    for topic,ref in topic_rows:
        candidate_topics.append({'topic_id':topic['topic_id'],'title_direction':topic['title_direction'],'core_problem':topic['core_problem'],'content_angle':topic['content_angle'],'note_type':topic.get('note_type','search'),'evidence_refs':[ref],'confidence':float(topic.get('confidence',.6))})
    if not candidate_topics:
        for i,problem in enumerate(user_problems[:5],1):
            candidate_topics.append({'topic_id':f'research-topic-{i:03d}','title_direction':f'如何应对：{problem["summary"]}','core_problem':problem['summary'],'content_angle':'先解释问题，再提出可执行步骤并说明适用边界。','note_type':'search','evidence_refs':problem['evidence_refs'],'confidence':problem['confidence']})
    candidate_keywords=[]
    for phrase,rows in phrases.items():
        refs=sorted({ref for ref,_ in rows}); intent=Counter(x for _,x in rows).most_common(1)[0][0]
        candidate_keywords.append({'phrase':phrase,'intent':intent,'evidence_refs':refs,'confidence':round(min(.9,.5+.1*(len(refs)-1)),2)})
    synthetic=bool(request.get('synthetic',False)) and all(bool(r.get('synthetic',False)) for r in source_rows)
    limits=['结果只反映明确提供的来源，不代表整体市场、平台实时趋势或搜索热度。']
    if not source_rows: limits.append('未提供可分析来源；结果不包含外部市场证据。')
    if synthetic: limits.append('来源均为合成示例，不代表真实用户、搜索或经营数据。')
    entries=signals+user_problems+candidate_topics+candidate_keywords
    confidence=round(sum(x['confidence'] for x in entries)/len(entries),2) if entries else 0.0
    return {'schema_version':'1.0.0','research_id':request['research_id'],'request':{'research_request':request['research_request'],'audience':request['audience'],'content_domain':request['content_domain'],'research_goal':request['research_goal'],'seed_keywords':request.get('seed_keywords',[]),'profile_ref':request.get('profile_ref')},'sources':sources,'signals':signals,'user_problems':user_problems,'candidate_topics':candidate_topics,'candidate_keywords':candidate_keywords,'evidence':evidence,'confidence':confidence,'limitations':limits,'status':'proposed','synthetic':synthetic}
