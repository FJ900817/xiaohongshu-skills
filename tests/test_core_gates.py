import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DEMO=ROOT/'examples/synthetic/demo-project/artifacts'; V=ROOT/'validators'
def run(script,*args): return subprocess.run([sys.executable,str(V/script),*[str(x) for x in args]],capture_output=True,text=True)
def load(name): return json.loads((DEMO/name).read_text(encoding='utf-8-sig'))
class HumanGateTests(unittest.TestCase):
    def reject(self,label,script,*args):
        r=run(script,*args); self.assertNotEqual(r.returncode,0,label+' should fail closed')
        self.assertIn('FAIL',r.stdout+r.stderr)
    def test_task_card_waiting_for_approval_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            x=load('task-card.json'); x['status']='awaiting_approval'; x['approval']={'state':'pending'}; p=Path(d)/'task.json'; p.write_text(json.dumps(x),encoding='utf-8'); self.reject('topic gate','task_card_validator.py',p)
    def test_keyword_plan_pending_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            x=load('keyword-plan.json'); x['status']='review'; x['approval']['state']='pending'; x['keywords'][0]['status']='candidate'; x['keywords'][0]['approval_state']='pending'; p=Path(d)/'keyword.json'; p.write_text(json.dumps(x),encoding='utf-8'); self.reject('keyword gate','keyword_plan_validator.py',p)
    def test_writer_cannot_drop_locked_keyword(self):
        with tempfile.TemporaryDirectory() as d:
            x=load('writing-result.json'); x['body']=x['body'].replace('小户型玄关收纳','被替换的词'); p=Path(d)/'writing.json'; p.write_text(json.dumps(x,ensure_ascii=False),encoding='utf-8'); self.reject('keyword lock','writing_validator.py',p,'--task-card',DEMO/'task-card.json','--keyword-plan',DEMO/'keyword-plan.json')
    def test_unapproved_finalization_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            x=load('finalization.json'); x['status']='review'; p=Path(d)/'final.json'; p.write_text(json.dumps(x,ensure_ascii=False),encoding='utf-8'); self.reject('final gate','finalization_validator.py',p,'--require-approved')
    def test_visual_rejects_review_finalization(self):
        with tempfile.TemporaryDirectory() as d:
            x=load('finalization.json'); x['status']='review'; p=Path(d)/'final.json'; p.write_text(json.dumps(x,ensure_ascii=False),encoding='utf-8'); self.reject('visual gate','visual_output_validator.py',DEMO/'visual-output.json','--finalization',p)
if __name__=='__main__': unittest.main(verbosity=2)
