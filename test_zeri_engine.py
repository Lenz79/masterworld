import unittest
from unittest.mock import patch
import zeri_engine as z

class FakeLunar:
    def __init__(s,d): s.d=d
    def getDayZhi(s): return z.DI_ZHI[s.d.toordinal()%12]
    def getDayYi(s): return {0:['嫁娶','开市'],1:['嫁娶'],2:['开市']}[s.d.toordinal()%3]
    def getDayJi(s): return ['嫁娶'] if s.d.toordinal()%3==2 else []
    def getZhiXing(s): return '破' if s.d.day==10 else '成'
    def getYearZhi(s): return '辰'
    def getMonth(s): return 1
    def getDay(s): return 13 if s.d.day==5 else 2
    def toString(s): return 'fake'
    def getTimes(s): return []
class FakeSolar:
    def __init__(s,y,m,d): s.d=__import__('datetime').date(y,m,d)
    @staticmethod
    def fromYmd(y,m,d): return FakeSolar(y,m,d)
    def getLunar(s): return FakeLunar(s.d)

class ZeriTests(unittest.TestCase):
    def test_relations(self):
        self.assertEqual(z._relations('午',['鼠'])['chong'],['鼠'])
        self.assertEqual(z._relations('未',['鼠'])['hai'],['鼠'])
        self.assertEqual(z._relations('子',['兔'])['xing'],['兔'])
        self.assertEqual(z._relations('寅',['蛇'])['xing'],['蛇'])
        self.assertFalse(any(z._relations('子',['牛']).values()))  # 子丑合
        self.assertEqual(z._relations('子',[]),{'chong':[],'hai':[],'xing':[]})
        r=z._relations('午',['鼠','牛','马'])  # 多人：只列出相冲者
        self.assertEqual(r['chong'],['鼠'])
    def test_zodiac_lists(self):
        self.assertEqual(z._zodiacs({'zodiacs':['鼠','鼠','牛'],'zodiacs_minor':['牛','虎']}),(['鼠','牛'],['虎']))
        self.assertEqual(z._zodiacs({'zodiac':'龙'}),(['龙'],[]))
        self.assertEqual(z._zodiacs({}),([],[]))
        self.assertEqual(len(z._zodiacs({'zodiacs':list(z.SHENGXIAO)})[0]),12)
        for bad in ({'zodiacs':['猫']},{'zodiacs':'鼠'},{'zodiacs':list(z.SHENGXIAO)+['鼠']},{'zodiacs_minor':[1]}):
            with self.subTest(bad=bad),self.assertRaises(ValueError): z._zodiacs(bad)
    def test_classify(self):
        rel={'chong':[],'hai':[],'xing':[]}
        C=lambda *a,**k: z._classify(*a,**k)
        self.assertEqual(C(['嫁娶'],['嫁娶'],[],'成',rel,'jiaqu','子','辰')[0],'good')
        self.assertEqual(C(['嫁娶'],['嫁娶'],['嫁娶'],'成',rel,'jiaqu','子','辰')[0],'avoid')
        self.assertEqual(C(['嫁娶'],['嫁娶'],[],'破',rel,'jiaqu','子','辰')[0],'avoid')
        self.assertEqual(C(['嫁娶'],[],[],'成',rel,'jiaqu','子','辰')[0],'neutral')
        # 岁破：辰年戌日。施工类为避，其他为注意
        self.assertEqual(C(['动土'],['动土'],[],'成',rel,'dongtu','戌','辰')[0],'avoid')
        self.assertEqual(C(['嫁娶'],['嫁娶'],[],'成',rel,'jiaqu','戌','辰')[0],'ok')
        # 主要当事人相冲 → 避开；相关人相冲 → 仅提示
        lvl,_,cau,av=C(['嫁娶'],['嫁娶'],[],'成',{'chong':['鼠'],'hai':[],'xing':[]},'jiaqu','午','辰')
        self.assertEqual(lvl,'avoid'); self.assertIn('鼠',av[0])
        lvl,_,cau,av=C(['嫁娶'],['嫁娶'],[],'成',rel,'jiaqu','午','辰',{'chong':['鼠'],'hai':[],'xing':[]})
        self.assertEqual(lvl,'ok'); self.assertFalse(av); self.assertTrue(any('其他相关人' in c for c in cau))
    @patch.object(z,'Solar',FakeSolar)
    def test_calculate(self):
        r=z.ZeriEngine.calculate({'event':'jiaqu','year':2026,'month':3,'day':1,'days':31,'zodiacs':['鼠'],'zodiacs_minor':['牛','马']})
        self.assertEqual(len(r['days']),31)
        self.assertEqual(sum(r['summary'].values()),31)
        d10=[x for x in r['days'] if x['date']=='2026-03-10'][0]; self.assertEqual(d10['level'],'avoid')
        d5=[x for x in r['days'] if x['date']=='2026-03-05'][0]; self.assertIn('杨公忌日（部分流派）',d5['cautions'])
        self.assertIn('不保证吉凶',r['calculation_audit']['scope'])
    @patch.object(z,'Solar',FakeSolar)
    def test_validation(self):
        bad=[{'event':'x','year':2026,'month':1,'day':1},{'event':'jiaqu','year':2026,'month':2,'day':30},
             {'event':'jiaqu','year':2026,'month':1,'day':1,'days':0},{'event':'jiaqu','year':2026,'month':1,'day':1,'days':93},
             {'event':'jiaqu','year':2026,'month':1,'day':1,'zodiacs':['猫']},{'event':'jiaqu','year':2100,'month':12,'day':1,'days':60},
             {'event':'jiaqu','year':'2026','month':1,'day':1},{'event':'jiaqu','year':2026,'month':1,'day':1,'birth_year':True}]
        for b in bad:
            with self.subTest(b=b),self.assertRaises(ValueError): z.ZeriEngine.calculate(b)
    def test_dependency(self):
        with patch.object(z,'Solar',None),self.assertRaisesRegex(RuntimeError,'lunar_python'):
            z.ZeriEngine.calculate({})
if __name__=='__main__': unittest.main()
