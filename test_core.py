import unittest,tempfile,json
from pathlib import Path
from core import run

class Tests(unittest.TestCase):
 def test_draft(self):self.assertEqual(len(run(json.loads(Path('example.json').read_text()))['listings']),1)
 def test_empty(self):self.assertEqual(run({})['listings'],[])
 def test_bad(self):
  with self.assertRaises(TypeError):run({'products':5})
 def test_flag(self):self.assertTrue(run({'text':'保证100%通过'})['blockers'])

if __name__=="__main__":unittest.main()
