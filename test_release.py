"""作者：Wangyuan；日期：2026-11-08。职责：通过合成输入复验已确认缺陷。"""
import unittest,json
from pathlib import Path
from core import run
class ReleaseTests(unittest.TestCase):
 def test_price_cent_consistency(self) -> None:
  p=json.loads(Path('example.json').read_text());p['products'][0]['base_price']=12.34
  r=run(p);self.assertIn('12.34 元',json.dumps(r,ensure_ascii=False))
