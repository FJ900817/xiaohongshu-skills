"""Evidence-based Learning Core; builds proposals and never edits production assets."""
from __future__ import annotations
import difflib,hashlib

def build_review(original: dict, final: dict, feedback_bundle: dict, review_id: str) -> dict:
    if final.get('status')!='approved': raise ValueError('Learning requires an approved Finalization')
    if original.get('writing_id')!=final.get('writing_id') or original.get('revision')!=final.get('revision'):
        raise ValueError('original and approved final must identify the same writing revision')
    digest=hashlib.sha256(final.get('body','').encode('utf-8')).hexdigest()
    if digest!=final.get('body_sha256'): raise ValueError('approved final body hash mismatch')
    evidence=[]; observed=[]
    before=original.get('body','').splitlines(); after=final.get('body','').splitlines()
    matcher=difflib.SequenceMatcher(a=before,b=after)
    for n,(tag,i1,i2,j1,j2) in enumerate(matcher.get_opcodes(),1):
        if tag=='equal': continue
        ref=f'text-diff-{n:03d}'
        evidence.append({'evidence_id':ref,'kind':'text_diff','summary':f'正文差异：{tag}，原稿行 {i1+1}-{i2}，终稿行 {j1+1}-{j2}','source_ref':f'{original["writing_id"]}/revision-{original["revision"]}'})
        observed.append({'field':'body','change_kind':'added' if tag=='insert' else 'removed' if tag=='delete' else 'revised','before':'\n'.join(before[i1:i2]) or None,'after':'\n'.join(after[j1:j2]) or None,'evidence_refs':[ref]})
    rules=[]; adapters=[]; patterns=[]; scopes=[]; confidences=[]
    category={'core':'core_rule_candidate','adapter':'account_adapter_candidate','one_off':'one_off_preference'}
    inputs=[]
    inputs.extend((x,'user_feedback',x['feedback_id'],x['text']) for x in feedback_bundle.get('feedback',[]))
    inputs.extend((x,'revision_history',x['entry_id'],x['summary']) for x in feedback_bundle.get('revision_history',[]))
    inputs.extend((x,'visual_qa',x['feedback_id'],x['summary']) for x in feedback_bundle.get('visual_qa_feedback',[]))
    for item,kind,item_id,text in inputs:
        scope=item['scope_hint']; cat=category[scope]; evidence_ref=item['evidence_ref']
        evidence.append({'evidence_id':evidence_ref,'kind':kind,'summary':text,'source_ref':item_id})
        conf=0.78 if item['occurrences']>=2 else 0.48
        confidences.append(conf); scopes.append(scope)
        proposal={'proposal_id':f'proposal-{item_id}','category':cat,'scope':scope,'proposal':text,'rationale':item['rationale'],'evidence_refs':[evidence_ref], 'confidence':conf,'status':'proposal'}
        rules.append(proposal)
        if scope=='adapter':
            adapters.append({'proposal_id':proposal['proposal_id'],'profile_ref':item.get('target_profile_ref') or feedback_bundle.get('account_profile_ref'),'proposal':text,'evidence_refs':[evidence_ref],'confidence':conf,'status':'proposal'})
        if item.get('occurrences',1)>=2:
            patterns.append({'pattern_id':f'pattern-{item_id}','summary':item['rationale'],'occurrences':item['occurrences'],'evidence_refs':[evidence_ref],'confidence':conf})
    unique=set(scopes); overall_scope=next(iter(unique)) if len(unique)==1 else 'mixed' if unique else 'one_off'
    all_synthetic=bool(original.get('synthetic')) and bool(feedback_bundle.get('synthetic'))
    return {'schema_version':'1.0.0','review_id':review_id,'writing_id':original['writing_id'],'revision':original['revision'],'observed_changes':observed,'repeated_patterns':patterns,'evidence':evidence,'suggested_rules':rules,'suggested_adapter_changes':adapters,'confidence':round(sum(confidences)/max(1,len(confidences)),2),'scope':overall_scope,'approval_required':True,'status':'proposed','synthetic':all_synthetic}
