import unittest
from datetime import date
from unittest.mock import patch
import zeri_engine as ze, dong_gong_engine as E, dong_gong_data as D

Z=ze.DI_ZHI; G='甲乙丙丁戊己庚辛壬癸'
def ganzhi_of(d):                      # 2000-01-01 為戊午日
    i=(54+(d-date(2000,1,1)).days)%60; return G[i%10]+Z[i%12]
def month_zhi_of(d):                   # 測試用：以每月5日為節（遠離邊界的日期才用）
    m=d.month if d.day>=5 else d.month-1
    return Z[m%12]
class FakeEC:
    def __init__(s,d): s.d=d
    def getMonthZhi(s): return month_zhi_of(s.d)
class FakeLunar:
    def __init__(s,d): s.d=d
    def getDayInGanZhi(s): return ganzhi_of(s.d)
    def getEightChar(s): return FakeEC(s.d)
    def getXiu(s): return '箕'
    def getYearGanByLiChun(s): return '丙'
    def getJie(s): return ''
    def toString(s): return 'fake'
class FakeSolar:
    def __init__(s,d): s.d=d
    @staticmethod
    def fromYmd(y,m,d): return FakeSolar(date(y,m,d))
    def getLunar(s): return FakeLunar(s.d)

class T(unittest.TestCase):
    def test_hours_match_book_yichou(self):
        # 《董公選要覽》六十甲子吉凶時辰表（乙丑日）逐時核對
        book={'丙子':'天刑','壬午':'天牢','丁丑':'朱雀','癸未':'元武','戊寅':'金匱','甲申':'司命',
              '己卯':'天德','乙酉':'勾陳','庚辰':'白虎','丙戌':'青龍','辛巳':'玉堂','丁亥':'明堂'}
        got={h['ganzhi']:h['tianshen'] for h in E.hours('乙','丑',set())}
        # 午時天牢/未時元武等按書列；子午、丑未... 共 12 個時辰全部比對
        self.assertEqual({k:got[k] for k in book if k in got},book)
        self.assertEqual(len([k for k in book if k in got]),12)
    def test_hours_jiazi(self):
        got={h['ganzhi']:h['tianshen'] for h in E.hours('甲','子',set())}
        for gz,name in {'甲子':'金匱','庚午':'司命','乙丑':'天德','辛未':'勾陳','丙寅':'白虎','壬申':'青龍','丁卯':'玉堂','癸酉':'明堂'}.items():
            self.assertEqual(got[gz],name)
    def test_month_and_jianchu(self):
        self.assertEqual(E.month_number('寅'),1); self.assertEqual(E.month_number('丑'),12)
        self.assertEqual(E.JIAN_CHU[(Z.index('午')-Z.index('寅'))%12],'定')   # 正月定午日（書）
    def test_flags(self):
        f=lambda gz,m,jc='成',xiu='箕',yg='丙':[n for n,_,_ in E.day_flags(gz,m,jc,xiu,yg)]
        self.assertIn('往亡日',f('甲寅',1)); self.assertIn('小紅沙日',f('己巳',1)); self.assertIn('黃沙日',f('庚午',1))
        self.assertIn('天賊日',f('丙辰',1)); self.assertIn('月厭大禍日',f('甲戌',1)); self.assertIn('受死日',f('丙戌',1))
        self.assertIn('十惡大敗日',f('戊戌',3,yg='甲')); self.assertNotIn('十惡大敗日',f('戊戌',3,yg='丁'))
        self.assertIn('火星日',f('乙丑',1)); self.assertIn('天地轉煞日',f('乙卯',2)); self.assertIn('正四廢日',f('庚申',1))
        self.assertIn('金神七煞日',f('甲子',1,xiu='角')); self.assertIn('月破日',f('庚申',1,'破'))
        self.assertEqual(E.good_stars('丁卯',1),['煞貢']); self.assertEqual(E.good_stars('辛未',1),['人專'])
    def test_scope(self):
        rel={'chong':[],'hai':[],'xing':[]}
        fl=[('往亡日','附錄七','')]
        self.assertEqual(E.judge(fl,[],'jiaqu','成',rel,rel)[0],'avoid')
        self.assertEqual(E.judge(fl,[],'anzang','成',rel,rel)[0],'neutral')      # 往亡不涉安葬
        self.assertEqual(E.judge([('小紅沙日','附錄六','')],[],'anzang','成',rel,rel)[0],'avoid')  # 百事忌
        self.assertEqual(E.judge([],['人專'],'jiaqu','成',rel,rel)[0],'good')
        self.assertEqual(E.judge([('九土鬼日','附錄九','')],[],'dongtu','平',rel,rel)[0],'avoid')
        self.assertEqual(E.judge([('九土鬼日','附錄九','')],[],'dongtu','定',rel,rel)[0],'caution')
        self.assertEqual(E.judge([('勾陳黑道日','附錄八','')],[],'dongtu','成',rel,rel)[0],'caution')  # 無範圍僅提示
    def test_book_coverage(self):
        for m in (1,2,3,4,5,6):
            self.assertEqual(sorted(z for (mm,z) in D.BOOK_TEXT if mm==m),sorted(Z),m)   # 正文各月十二日全錄
            for z in Z:   # 條文標題必須與月建、建除對應（月建寅起：建除十二神順序）
                title=D.BOOK_TEXT[(m,z)][0]
                self.assertEqual(title,E.JIAN_CHU[(Z.index(z)-(m+1))%12]+z+'日')
        self.assertEqual(len(D.BOOK_TEXT),72)
    @patch.object(ze,'Solar',FakeSolar)
    def test_calculate(self):
        r=E.DongGongEngine.calculate({'event':'jiaqu','year':2026,'month':6,'day':20,'days':60,'zodiacs':['鼠']})
        self.assertEqual(sum(r['summary'].values()),60)
        low=[x for x in r['days'] if x['month_label'][0] in '123456' and x['month_label'][1]=='月']
        self.assertTrue(low and all(x['book'] for x in low))                           # 一至六月全有原文
        high=[x for x in r['days'] if x['month_label'].startswith('7月')]
        self.assertTrue(high and all(x['book_missing'] for x in high))                 # 七月尚未錄入
        for x in r['days']: self.assertIn(len(x['hours']),(0,12))
        self.assertIn('不保證吉凶',r['calculation_audit']['scope'])
    def test_validation(self):
        with patch.object(ze,'Solar',FakeSolar):
            for b in ({'event':'x','year':2026,'month':1,'day':1},{'event':'jiaqu','year':2026,'month':1,'day':1,'days':99},
                      {'event':'jiaqu','year':2026,'month':1,'day':1,'zodiacs':['猫']}):
                with self.subTest(b=b),self.assertRaises(ValueError): E.DongGongEngine.calculate(b)
if __name__=='__main__': unittest.main()
