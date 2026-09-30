import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
    return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,text=True,capture_output=True,env=env)

class FirstRunTests(unittest.TestCase):
    def test_initializer_copies_starters_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'new-project'
            result=run(ROOT/'scripts/init_project.py','--destination',target)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual({p.name for p in (target/'config').iterdir()},{'account-profile.yaml','project-config.yaml','keyword-catalog.yaml','visual-config.yaml'})
            self.assertTrue(all((target/x).is_dir() for x in ('workspace','outputs','learning')))
            before=(target/'config'/'account-profile.yaml').read_bytes()
            second=run(ROOT/'scripts/init_project.py','--destination',target)
            self.assertNotEqual(second.returncode,0)
            self.assertEqual((target/'config'/'account-profile.yaml').read_bytes(),before)

    def test_runtime_execution_context_schema_loads(self):
        obj=json.loads((ROOT/'runtime/execution_context.schema.json').read_text(encoding='utf-8'))
        self.assertIn('skill_id',obj['required']); self.assertIn('runtime_mode',obj['properties'])

    def test_six_real_ai_quality_cases_documented(self):
        text=(ROOT/'tests'/'quality'/'REAL_AI_QUALITY_CASES.md').read_text(encoding='utf-8')
        self.assertEqual(text.count('## Search '),2)
        self.assertEqual(text.count('## Recommendation '),2)
        self.assertEqual(text.count('## Editorial Trend '),2)

    def test_first_run_inputs_validate_and_render_eight_pages(self):
        d=ROOT/'examples'/'first-run'
        for script,args in [
            ('task_card_validator.py',[d/'task-card.json']),
            ('keyword_plan_validator.py',[d/'keyword-plan.json','--task-card',d/'task-card.json']),
            ('writing_validator.py',[d/'writing-result.json','--task-card',d/'task-card.json','--keyword-plan',d/'keyword-plan.json']),
            ('finalization_validator.py',[d/'finalization.json','--require-approved']),
            ('visual_output_validator.py',[d/'outputs'/'visual-output.json','--finalization',d/'finalization.json'])]:
            result=run(ROOT/'validators'/script,*args)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(len(list((d/'outputs').glob('P*.svg'))),8)
        obj=json.loads((d/'outputs'/'visual-output.json').read_text(encoding='utf-8'))
        writing=json.loads((d/'writing-result.json').read_text(encoding='utf-8'))
        self.assertEqual(obj['pages'][0]['text'][0],writing['title'])
        self.assertTrue(any(text and text in writing['body'] for page in obj['pages'] for text in page['text']))
        self.assertEqual({p['sequence'] for p in obj['pages']},set(range(1,9)))

    def test_research_local_csv_and_markdown_sources(self):
        sys.path.insert(0,str(ROOT/'adapters'/'research'))
        from local_json_source import load_sources
        with tempfile.TemporaryDirectory() as td:
            base=Path(td); csvp=base/'source.csv'
            csvp.write_text('source_id,title,summary,synthetic,user_questions,user_problems,phrases_text\ns1,本地访谈,用户提供摘要,false,如何开始,不清楚步骤,窗台种植::入门意图\n',encoding='utf-8')
            md=base/'notes.md'; md.write_text('# 用户笔记\n先观察窗台。',encoding='utf-8')
            self.assertEqual(load_sources(csvp)[0]['source_type'],'csv')
            self.assertEqual(load_sources(md)[0]['source_type'],'user_upload')

if __name__=='__main__': unittest.main(verbosity=2)
