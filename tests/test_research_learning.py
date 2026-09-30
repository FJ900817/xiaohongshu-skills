import hashlib, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'examples'/'synthetic'/'demo-project'/'artifacts'

def run(*args, **kwargs):
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,capture_output=True,text=True,env=env,**kwargs)

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

class ResearchLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result=run(ROOT/'scripts'/'run_synthetic_demo.py')
        if result.returncode:
            raise RuntimeError(result.stdout+'\n'+result.stderr)

    def test_research_result_valid_and_proposed_only(self):
        result=run(ROOT/'validators'/'research_result_validator.py',ART/'research-result.json','--request',ROOT/'examples/synthetic/demo-project/input/research-request.json')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        obj=json.loads((ART/'research-result.json').read_text(encoding='utf-8'))
        self.assertEqual(obj['status'],'proposed')
        self.assertTrue(obj['candidate_topics'])
        self.assertFalse({'task_card','approval','approved_task_card'} & set(obj))

    def test_research_request_can_omit_seed_and_sources(self):
        request=json.loads((ROOT/'examples/synthetic/demo-project/input/research-request.json').read_text(encoding='utf-8'))
        request.pop('seed_keywords',None); request.pop('data_sources',None)
        with tempfile.TemporaryDirectory() as temp:
            request_path=Path(temp)/'request.json'; output=Path(temp)/'result.json'
            request_path.write_text(json.dumps(request,ensure_ascii=False),encoding='utf-8')
            result=run(ROOT/'scripts'/'run_research.py','--request',request_path,'--output',output)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            obj=json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(obj['status'],'proposed')
        self.assertEqual(obj['sources'],[])
        self.assertTrue(obj['limitations'])

    def test_topic_planning_consumes_research_evidence(self):
        result=run(ROOT/'scripts'/'run_synthetic_demo.py','--no-learning')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads((ART/'run-report.json').read_text(encoding='utf-8'))
        research=json.loads((ART/'research-result.json').read_text(encoding='utf-8'))
        candidates=json.loads((ART/'topic-candidates.json').read_text(encoding='utf-8'))
        card=json.loads((ART/'task-card.json').read_text(encoding='utf-8'))
        self.assertEqual(candidates['research_result_ref'],research['research_id'])
        self.assertEqual(candidates['candidates'][0]['topic_id'],research['candidate_topics'][0]['topic_id'])
        self.assertEqual(card['topic']['topic_id'],research['candidate_topics'][0]['topic_id'])
        self.assertEqual(card['status'],'approved') # only after the topic approval mock in the demo
        self.assertEqual(report['learning_status'],'SKIPPED')
        self.assertEqual(report['status'],'PASS')

    def test_research_can_be_disabled_without_blocking_topic(self):
        result=run(ROOT/'scripts'/'run_synthetic_demo.py','--no-research','--no-learning')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report=json.loads((ART/'run-report.json').read_text(encoding='utf-8'))
        candidates=json.loads((ART/'topic-candidates.json').read_text(encoding='utf-8'))
        card=json.loads((ART/'task-card.json').read_text(encoding='utf-8'))
        self.assertFalse(report['research_enabled'])
        self.assertIsNone(candidates['research_result_ref'])
        self.assertEqual(card['status'],'approved')

    def test_learning_compares_final_and_classifies_three_scopes(self):
        result=run(ROOT/'validators'/'learning_review_validator.py',ART/'learning-review.json','--original',ART/'writing-result.json','--final',ART/'learning-approved-finalization.json')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        review=json.loads((ART/'learning-review.json').read_text(encoding='utf-8'))
        self.assertTrue(review['observed_changes'])
        self.assertTrue(review['approval_required'])
        self.assertEqual(review['status'],'proposed')
        self.assertEqual({x['scope'] for x in review['suggested_rules']},{'core','adapter','one_off'})
        self.assertGreaterEqual(len(review['suggested_adapter_changes']),1)

    def test_learning_accept_is_record_only_and_does_not_modify_rules(self):
        protected=[p for folder in ('skills','contracts','rules','adapters') for p in (ROOT/folder).rglob('*') if p.is_file()]
        before={p:digest(p) for p in protected}
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'decision.json'
            result=run(ROOT/'scripts'/'record_learning_decision.py','--review',ART/'learning-review.json','--decision','accept','--output',output,'--reviewer','synthetic-human')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            decision=json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(decision['recorded_status'],'approved_proposal')
        self.assertFalse(decision['applied'])
        self.assertEqual(decision['modified_paths'],[])
        self.assertEqual(before,{p:digest(p) for p in protected})

    def test_learning_reject_is_also_record_only(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'decision.json'
            result=run(ROOT/'scripts'/'record_learning_decision.py','--review',ART/'learning-review.json','--decision','reject','--output',output,'--reviewer','synthetic-human')
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            decision=json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(decision['recorded_status'],'rejected_proposal')
        self.assertFalse(decision['applied'])
        self.assertEqual(decision['modified_paths'],[])

if __name__=='__main__': unittest.main(verbosity=2)
