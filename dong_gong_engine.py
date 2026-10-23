# -*- coding: utf-8 -*-
"""董公擇日模式：只使用《董公選要覽》已轉錄的表格與條文（見 dong_gong_data.py）。
不用通行黃曆的宜忌補寫；書中沒有轉錄的月份顯示「原文尚未錄入」。"""
from datetime import date, timedelta

import zeri_engine as ze
import dong_gong_data as D

ZHI, GAN = ze.DI_ZHI, '甲乙丙丁戊己庚辛壬癸'
JIAN_CHU = ['建', '除', '滿', '平', '定', '執', '破', '危', '成', '收', '開', '閉']


def month_number(month_zhi):
    return (ZHI.index(month_zhi) - 2) % 12 + 1   # 寅月=正月


def _scoped(scope, event):
    return scope == D.ALL or event in scope


def day_flags(ganzhi, m, jian_chu, xiu, year_gan):
    """返回本日命中的書中凶日、吉星標記：[(名稱, 頁碼, 說明)]。"""
    gan, zhi, g = ganzhi[0], ganzhi[1], D.group(m)
    s, flags = D.season(m), []
    def add(name, note=''): flags.append((name, D.PAGE[name], note))
    if ganzhi in D.HUOXING[g]: add('火星日')
    if zhi == D.HUANGSHA[g]: add('黃沙日')
    if zhi == D.XIAOHONGSHA[g]: add('小紅沙日')
    if zhi == D.TIANZEI[m]: add('天賊日')
    if zhi == D.YUEYAN[m]: add('月厭大禍日')
    if zhi == D.SHOUSI[m]: add('受死日')
    if zhi == D.BINGXIAO[m]: add('冰消瓦陷日')
    if zhi == D.WANGWANG[m]: add('往亡日')
    if zhi == D.GOUJIAO[m]: add('勾絞日')
    if zhi == D.ZHUQUE[m]: add('朱雀黑道日')
    if zhi == D.BAIHU[m]: add('白虎黑道日')
    if zhi == D.YUANWU[m]: add('元武黑道日')
    if zhi == D.GOUCHEN[m]: add('勾陳黑道日', '書中注文模糊，不作事項判定')
    if year_gan and ganzhi == D.SHIE.get(year_gan, {}).get(m): add('十惡大敗日')
    if ganzhi in D.DASHA_BAIHU: add('大煞白虎入中宮日')
    if ganzhi in D.JIUTUGUI: add('九土鬼日', '與建破平收日並則凶')
    if ganzhi in D.ZHUANSHA[s]: add('天地轉煞日')
    if ganzhi in D.SIFEI[s]: add('正四廢日')
    if xiu in D.JINSHEN_XIU: add('金神七煞日', '煞貢直星人專不能解金神七煞（論略第五頁）')
    if jian_chu == '破': add('月破日')
    return flags


def good_stars(ganzhi, m):
    g = D.group(m)
    return [n for n, lst in D.SHAGONG[g].items() if ganzhi in lst]


def judge(flags, stars, event, jian_chu, rel_main, rel_minor):
    avoid, caution, reasons = [], [], []
    for name, page, note in flags:
        scope = D.SCOPE.get(name)
        label = f'{name}（{page}）'
        if scope is None:
            caution.append(f'{label}：{note}'); continue
        if name == '九土鬼日':
            if _scoped(scope, event):
                (avoid if jian_chu in ('建', '破', '平', '收') else caution).append(label + ('：與建破平收日並則凶' if jian_chu in ('建', '破', '平', '收') else '：單獨出現，書云與吉星並則不忌'))
            continue
        if _scoped(scope, event): avoid.append(label)
    j = lambda z: '、'.join(z)
    if rel_main['chong']: avoid.append('日支與主要當事人生肖（' + j(rel_main['chong']) + '）相冲')
    if rel_main['hai']: caution.append('日支與主要當事人生肖（' + j(rel_main['hai']) + '）相害')
    if rel_main['xing']: caution.append('日支與主要當事人生肖（' + j(rel_main['xing']) + '）相刑')
    for k, n in (('chong', '相冲'), ('hai', '相害'), ('xing', '相刑')):
        if rel_minor[k]: caution.append('其他相關人生肖（' + j(rel_minor[k]) + '）' + n)
    if stars: reasons.append('書列最吉三星：' + '、'.join(stars) + '（附錄三、四）')
    level = 'avoid' if avoid else 'good' if stars and not caution else 'ok' if stars else 'caution' if caution else 'neutral'
    return level, reasons, caution, avoid


def hours(day_gan, day_zhi, clash_set, qinglong_start=D.QINGLONG_START):
    start = ZHI.index(qinglong_start[day_zhi])
    zi_gan = (GAN.index(day_gan) % 5) * 2        # 五鼠遁：甲己起甲子，乙庚起丙子…
    out = []
    for i, z in enumerate(ZHI):
        name = D.HOUR_ORDER[(i - start) % 12]
        chong = ZHI[(i + 6) % 12]
        out.append({'zhi': z, 'ganzhi': GAN[(zi_gan + i) % 10] + z, 'tianshen': name,
                    'type': '黑道' if name in D.HOUR_BLACK else '黃道',
                    'chong': ze.SHENGXIAO[(i + 6) % 12], 'clash_user': ze.SHENGXIAO[(i + 6) % 12] in clash_set})
    return out


class DongGongEngine:
    @staticmethod
    def calculate(req):
        Solar = ze.Solar
        if Solar is None:
            raise RuntimeError('缺少 lunar_python，請執行 pip install -r requirements.txt')
        if not isinstance(req, dict): raise ValueError('請求必須為 JSON 對象')
        event = req.get('event')
        if event not in ze.EVENTS: raise ValueError('不支持的擇日事項')
        for k in ('year', 'month', 'day'):
            if type(req.get(k)) is not int: raise ValueError('起始日期必須為整數年月日')
        days = req.get('days', 31)
        if type(days) is not int or not 1 <= days <= 92: raise ValueError('查詢天數必須為 1–92')
        start = date(req['year'], req['month'], req['day'])
        if not 1900 <= start.year <= 2100 or (start + timedelta(days=days)).year > 2100:
            raise ValueError('日期範圍僅支持 1900–2100 年')
        main_z, minor_z = ze._zodiacs(req)
        clash_set = set(main_z) | set(minor_z)
        label, _, group = ze.EVENTS[event]
        rows, covered = [], set()
        for i in range(days):
            d = start + timedelta(days=i)
            lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
            ganzhi = ze._call(lunar, 'getDayInGanZhi')
            ec = ze._call(lunar, 'getEightChar')
            mz = ze._call(ec, 'getMonthZhi') if ec else None
            if not ganzhi or mz not in ZHI: continue
            m = month_number(mz)
            jian_chu = JIAN_CHU[(ZHI.index(ganzhi[1]) - ZHI.index(mz)) % 12]
            year_gan = ze._call(lunar, 'getYearGanByLiChun') or ze._call(lunar, 'getYearGan')
            flags = day_flags(ganzhi, m, jian_chu, ze._call(lunar, 'getXiu'), year_gan)
            stars = good_stars(ganzhi, m)
            level, reasons, caution, avoid = judge(flags, stars, event, jian_chu,
                                                   ze._relations(ganzhi[1], main_z), ze._relations(ganzhi[1], minor_z))
            jie = ze._call(lunar, 'getJie')
            if jie: caution.append(f'本日交「{jie}」，月令以交節時刻為準，請核對節氣時刻')
            entry = D.BOOK_TEXT.get((m, ganzhi[1]))
            book = ({'title': D.MONTH_HEAD.get(m, f'{m}月') .split('　')[0] + '·' + entry[0], 'text': entry[1], 'page': entry[2]}
                    if entry else None)
            covered.add(m)
            rows.append({
                'date': d.isoformat(), 'weekday': '一二三四五六日'[d.weekday()], 'lunar': ze._call(lunar, 'toString'),
                'ganzhi': ganzhi, 'jian_chu': jian_chu, 'month_label': f'{m}月建{mz}',
                'level': level, 'reasons': reasons, 'cautions': caution, 'avoids': avoid,
                'flags': [f'{n}（{p}）' + ('' if D.SCOPE.get(n) is not None and _scoped(D.SCOPE[n], event) else '·不涉本事項') for n, p, _ in flags], 'good_stars': stars,
                'month_head': D.MONTH_HEAD.get(m), 'book': book,
                'book_missing': None if entry else '《董公選要覽》本月本日條文尚未錄入本系統（不以通行黃曆代替）',
                'xishen': D.XISHEN[ganzhi[0]], 'caishen': D.CAISHEN[ganzhi[0]],
                'hours': hours(ganzhi[0], ganzhi[1], clash_set) if level in ('good', 'ok', 'caution', 'neutral') else []})
        order = ['good', 'ok', 'caution', 'neutral', 'avoid']
        return {'status': 'success', 'school': 'donggong', 'event': {'key': event, 'label': label, 'group': group},
                'zodiacs': main_z, 'zodiacs_minor': minor_z, 'days': rows,
                'summary': {k: sum(r['level'] == k for r in rows) for k in order},
                'calculation_audit': {
                    'source': '《董公選要覽》（上海文明書局，民國十五年）人工轉錄，見 dong_gong_data.py',
                    'transcribed': '附錄凶日表（火星、黃沙、小紅沙、天賊、月厭、受死、冰消瓦陷、往亡、勾絞、四黑道、十惡大敗、大煞白虎、九土鬼、天地轉煞、正四廢）、金神七煞、煞貢直星人專、喜神財神方、十二時辰黃黑道；正文正月至三月（共三十六條全錄）',
                    'not_included': ['正文四月至十二月（待錄入）', '六十甲子日吉凶時辰表中的截路、空亡、貴人等附註', '命宮與東四西四宅配合', '吉星（黃羅紫檀、天皇地皇等）逐日判定', '勾陳黑道日書中注文模糊'],
                    'book_notes': D.BOOK_NOTES,
                    'rules_here': ['以節氣月定月建（lunar_python），按月建起建除十二神', '各表命中即標記；事項範圍依書中「忌…」字句對應', '生肖冲害刑沿用通行算法（書中未載）'],
                    'scope': '依古籍條文列示，不保證吉凶；事項對應與判定級別為本系統的工程對應，需人工對照原書。'}}
