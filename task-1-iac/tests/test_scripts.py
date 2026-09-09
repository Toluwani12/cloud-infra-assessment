import os, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1] / 'scripts'
FAKE='''#!/usr/bin/env python3
import os,sys
from pathlib import Path
with open(os.environ['CALL_LOG'],'a') as log: log.write(' '.join(sys.argv[1:])+'\\n')
if sys.argv[1]==os.environ.get('FAIL_COMMAND'): sys.exit(1)
if sys.argv[1]=='plan': Path('ci.tfplan').write_text('fake plan')
if sys.argv[1]=='apply': assert Path(sys.argv[-1]).read_text()=='fake plan'
'''
class Scripts(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);(self.root/'scripts').mkdir();(self.root/'bin').mkdir()
  for file in ROOT.glob('*.sh'): (self.root/'scripts'/file.name).write_text(file.read_text())
  tool=self.root/'bin/terraform';tool.write_text(FAKE);tool.chmod(0o755)
  self.env={**os.environ,'PATH':str(self.root/'bin')+':'+os.environ['PATH'],'CALL_LOG':str(self.root/'calls')}
 def run_script(self,name,action='plan',fail=''):
  return subprocess.run(['bash',str(self.root/'scripts'/name)],env={**self.env,'TF_ACTION':action,'FAIL_COMMAND':fail},capture_output=True)
 def test_validation_uses_no_backend(self):
  self.assertEqual(self.run_script('check.sh').returncode,0)
  self.assertIn('init -backend=false', (self.root/'calls').read_text())
 def test_plan_never_applies(self):
  self.assertEqual(self.run_script('run.sh').returncode,0)
  self.assertNotIn('apply',(self.root/'calls').read_text())
  self.assertFalse((self.root/'ci.tfplan').exists())
 def test_apply_uses_saved_plan(self):
  self.assertEqual(self.run_script('run.sh','apply').returncode,0)
  self.assertIn('apply -input=false -lock-timeout=120s ci.tfplan',(self.root/'calls').read_text())
  self.assertFalse((self.root/'ci.tfplan').exists())
 def test_failed_plan_never_applies(self):
  self.assertNotEqual(self.run_script('run.sh','apply','plan').returncode,0)
  self.assertNotIn('apply',(self.root/'calls').read_text())
 def test_rejects_unsupported_actions(self):
  self.assertNotEqual(self.run_script('run.sh','destroy').returncode,0)
  self.assertFalse((self.root/'calls').exists())
if __name__=='__main__':unittest.main(verbosity=2)
