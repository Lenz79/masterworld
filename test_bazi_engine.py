import unittest
from unittest.mock import patch
import bazi_engine as b

class FakeEight:
    stems=('甲','丙','戊','庚')
    branches=('子','寅','辰','午')
    def setSect(self,sect): self.sect=sect
    def getYun(self,sex): return FakeYun()
    def __getattr__(self,key):
        for i,p in enumerate(('Year','Month','Day','Time')):
            if key==f'get{p}Gan':return lambda i=i:self.stems[i]
            if key==f'get{p}Zhi':return lambda i=i:self.branches[i]
            if key==f'get{p}HideGan':return lambda i=i:list(b.HIDDEN_STEMS[self.branches[i]])
            if key==f'get{p}NaYin':return lambda:'测试纳音'
        raise AttributeError(key)
class FakeYun:
    def getDaYun(self):return [FakeDaYun()]
class FakeDaYun:
    def getIndex(self):return 1
    def getGanZhi(self):return '辛未'
    def getStartAge(self):return 8
    def getStartYear(self):return 2008
class FakeLunar:
    def getEightChar(self):return FakeEight()
    def getYear(self):return 2000
    def getMonth(self):return 1
    def getDay(self):return 1
class FakeSolar:
    @staticmethod
    def fromYmdHms(*args):return FakeSolar()
    def getLunar(self):return FakeLunar()

class BaziTests(unittest.TestCase):
    def test_time(self):
        for raw,expected in [('13:45',(13,45)),(1345,(13,45)),('945',(9,45)),(23,(23,0)),('00:00',(0,0))]:
            self.assertEqual(b.parse_birth_time(raw),expected)
    def test_invalid_time(self):
        for raw in ('24:00','13:60','13.75',-1,None,True,2460,'9999'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):b.parse_birth_time(raw)
    @patch.object(b,'Solar',FakeSolar)
    def test_pillars_are_distinct_and_hidden_stems(self):
        r=b.BaziEngine.calculate({'name':'测试','gender':'男','year':2000,'month':3,'day':1,'hour':1345})
        self.assertEqual([r['bazi_chart'][k+'_pillar']['zhi'] for k in ('year','month','day','hour')],['子','寅','辰','午'])
        self.assertEqual([x['gan'] for x in r['bazi_chart']['day_pillar']['cangan_details']],['戊','乙','癸'])
        self.assertEqual(r['bazi_chart']['extra']['tai_yuan']['gan'],'丁')
        self.assertEqual(r['five_elements'],{'金':1,'木':2,'水':1,'火':2,'土':2})
        self.assertEqual(r['dayun_list'][0]['liunian'][0]['gan_zhi'],'甲子')
        self.assertEqual(r['dayun_list'][0]['liunian'][0]['main_star'],b.get_shishen('戊','甲'))
        self.assertEqual(r['calculation_audit']['interpretation_status'],'not_calibrated')
        self.assertEqual(r['detailed_report']['personality']['strengths'],[])
    @patch.object(b,'Solar',FakeSolar)
    def test_invalid_date_rejected(self):
        with self.assertRaisesRegex(ValueError,'有效公历'):b.BaziEngine.calculate({'year':2023,'month':2,'day':29,'hour':13})
    @patch.object(b,'Solar',FakeSolar)
    def test_ambiguous_decimal_rejected(self):
        with self.assertRaisesRegex(ValueError,'出生时间'):b.BaziEngine.calculate({'year':2000,'month':2,'day':29,'hour':13.75})
    def test_shishen_examples(self):
        self.assertEqual(b.get_shishen('甲','甲'),'比肩')
        self.assertEqual(b.get_shishen('甲','乙'),'劫财')
        self.assertEqual(b.get_shishen('甲','丙'),'食神')
        self.assertEqual(b.get_shishen('甲','辛'),'正官')
        self.assertEqual(b.get_shishen('甲','癸'),'正印')
    def test_kongwang(self):self.assertEqual(b.get_kongwang('甲','子'),'戌亥')
    def test_dependency_failure(self):
        with patch.object(b,'Solar',None),self.assertRaisesRegex(RuntimeError,'lunar_python'):
            b.BaziEngine.calculate({'year':2000,'month':1,'day':1,'hour':10})

if __name__=='__main__':unittest.main()
