# -*- coding: utf-8 -*-
"""择日引擎：基于 lunar_python 的黄历资料做逐日筛选。
只展示传统黄历条目与可复核的规则命中，不保证吉凶、不声称流派验证。
"""
from datetime import date, timedelta

try:
    from lunar_python import Solar
except ImportError:  # 由调用方转成 503 提示
    Solar = None

SHENGXIAO = '鼠牛虎兔龙蛇马羊猴鸡狗猪'
DI_ZHI = '子丑寅卯辰巳午未申酉戌亥'
LIU_HAI = {frozenset(p) for p in ('子未', '丑午', '寅巳', '卯辰', '申亥', '酉戌')}
SAN_XING = (frozenset('寅巳申'), frozenset('丑戌未'))
ZI_XING = frozenset('辰午酉亥')
# 杨公十三忌（农历月、日），属部分流派口径，仅作提示
YANGGONG = {(1, 13), (2, 11), (3, 9), (4, 7), (5, 5), (6, 3), (7, 1), (7, 29),
            (8, 27), (9, 25), (10, 23), (11, 21), (12, 19)}
CONSTRUCTION = {'dongtu', 'zhuangxiu', 'shangliang', 'anmen', 'zuozao', 'ruzhai', 'anchuang'}

# key: (显示名, 黄历宜忌里对应的条目, 分组)
EVENTS = {
    'jiaqu': ('嫁娶', ['嫁娶'], '婚姻'), 'lingzheng': ('领证', ['领证', '嫁娶'], '婚姻'),
    'dinghun': ('订婚纳采', ['订盟', '纳采', '问名', '订婚'], '婚姻'),
    'anchuang': ('安床', ['安床'], '婚姻'), 'qiusi': ('求嗣', ['求嗣'], '婚姻'),
    'kaiye': ('开业开市', ['开市'], '事业'), 'jiaoyi': ('交易纳财', ['交易', '纳财'], '事业'),
    'qianyue': ('立券签约', ['立券'], '事业'), 'guabian': ('挂匾', ['挂匾'], '事业'),
    'fuze': ('赴任', ['赴任'], '事业'), 'kaicang': ('开仓', ['开仓'], '事业'),
    'ruzhai': ('入宅搬家', ['入宅', '移徙'], '居家'), 'dongtu': ('动土破土', ['动土', '破土', '起基'], '居家'),
    'zhuangxiu': ('装修修造', ['修造', '动土'], '居家'), 'shangliang': ('上梁竖柱', ['上梁', '竖柱'], '居家'),
    'anmen': ('安门', ['安门'], '居家'), 'zuozao': ('作灶', ['作灶'], '居家'),
    'chuxing': ('出行', ['出行'], '出行'), 'ruxue': ('入学', ['入学'], '学业'),
    'qiyi': ('求医治病', ['求医', '治病'], '健康'), 'caiyi': ('裁衣', ['裁衣'], '其他'),
    'jisi': ('祭祀', ['祭祀'], '祭祀'), 'qifu': ('祈福', ['祈福'], '祭祀'),
    'kaiguang': ('开光', ['开光'], '祭祀'), 'zaizhong': ('栽种', ['栽种'], '农事'),
    'naxu': ('纳畜', ['纳畜', '牧养'], '农事'),
    'anzang': ('安葬', ['安葬', '破土'], '丧葬'), 'xiufen': ('修坟立碑', ['修坟', '立碑'], '丧葬'),
    'rulian': ('入殓成服', ['入殓', '成服'], '丧葬'),
}


def _call(obj, name, default=None):
    fn = getattr(obj, name, None)
    try:
        return fn() if callable(fn) else default
    except Exception:
        return default


def _zodiac_list(value, label):
    if value in (None, ''):
        return []
    if not isinstance(value, list) or len(value) > 12:
        raise ValueError(label + '必须是最多 12 项的生肖列表')
    out = []
    for z in value:
        if not isinstance(z, str) or len(z) != 1 or z not in SHENGXIAO:
            raise ValueError('生肖必须是 鼠牛虎兔龙蛇马羊猴鸡狗猪 之一')
        if z not in out:
            out.append(z)
    return out


def _zodiacs(payload):
    """返回 (主要当事人生肖, 其他相关人生肖)。同一生肖在两边都有时按主要处理。
    人数不限：同生肖的人只需选一次。"""
    main = _zodiac_list(payload.get('zodiacs'), 'zodiacs')
    if not main and payload.get('zodiac') not in (None, ''):  # 兼容旧接口
        main = _zodiac_list([payload['zodiac']], 'zodiac')
    by = payload.get('birth_year')
    if not main and by not in (None, ''):
        if type(by) is not int or not 1900 <= by <= 2100:
            raise ValueError('出生年份必须为 1900–2100 的整数')
        main = [SHENGXIAO[(by - 4) % 12]]  # 公历年近似，未按立春校准
    minor = [z for z in _zodiac_list(payload.get('zodiacs_minor'), 'zodiacs_minor') if z not in main]
    return main, minor


def _relations(day_zhi, zodiacs):
    """返回与日支相冲/相害/相刑的生肖列表。"""
    out = {'chong': [], 'hai': [], 'xing': []}
    for z in zodiacs or []:
        uz = DI_ZHI[SHENGXIAO.index(z)]
        pair = frozenset((day_zhi, uz))
        if abs(DI_ZHI.index(day_zhi) - DI_ZHI.index(uz)) == 6: out['chong'].append(z)
        if pair in LIU_HAI: out['hai'].append(z)
        if (day_zhi == uz and day_zhi in ZI_XING) or pair == frozenset('子卯') or \
                (day_zhi != uz and any(pair <= t for t in SAN_XING)):
            out['xing'].append(z)
    return out


def _classify(terms, yi, ji, jian_chu, relations, event_key, day_zhi, year_zhi, minor_relations=None):
    hit_yi = [t for t in terms if t in yi]
    hit_ji = [t for t in terms if t in ji]
    avoid, caution, reasons = [], [], []
    if hit_ji: avoid.append('黄历忌：' + '、'.join(hit_ji))
    if jian_chu == '破': avoid.append('建除为破日（月破）')
    j = lambda zs: '、'.join(zs)
    if relations['chong']: avoid.append('日支与主要当事人生肖（' + j(relations['chong']) + '）相冲')
    if relations['hai']: caution.append('日支与主要当事人生肖（' + j(relations['hai']) + '）相害')
    if relations['xing']: caution.append('日支与主要当事人生肖（' + j(relations['xing']) + '）相刑')
    for key, name in (('chong', '相冲'), ('hai', '相害'), ('xing', '相刑')):
        if minor_relations and minor_relations[key]:
            caution.append('其他相关人生肖（' + j(minor_relations[key]) + '）' + name)
    if year_zhi and abs(DI_ZHI.index(day_zhi) - DI_ZHI.index(year_zhi)) == 6:
        (avoid if event_key in CONSTRUCTION else caution).append('岁破日')
    if hit_yi: reasons.append('黄历宜：' + '、'.join(hit_yi))
    if avoid: level = 'avoid'
    elif hit_yi and not caution: level = 'good'
    elif hit_yi: level = 'ok'
    else: level = 'neutral'
    return level, reasons, caution, avoid


def _hours(lunar, clash_set):
    out = []
    for t in _call(lunar, 'getTimes', []) or []:
        zhi = _call(t, 'getZhi')
        if not zhi: continue
        out.append({'zhi': zhi, 'ganzhi': _call(t, 'getGanZhi'),
                    'tianshen': _call(t, 'getTianShen'), 'type': _call(t, 'getTianShenType'),
                    'chong': _call(t, 'getChongShengXiao'),
                    'clash_user': _call(t, 'getChongShengXiao') in clash_set})
    return [h for h in out if h['zhi'] in DI_ZHI][:12]


class ZeriEngine:
    @staticmethod
    def events():
        return [{'key': k, 'label': v[0], 'group': v[2]} for k, v in EVENTS.items()]

    @staticmethod
    def calculate(req):
        if Solar is None:
            raise RuntimeError('缺少 lunar_python，请执行 pip install -r requirements.txt')
        if not isinstance(req, dict):
            raise ValueError('请求必须为 JSON 对象')
        event = req.get('event')
        if event not in EVENTS:
            raise ValueError('不支持的择日事项')
        for k in ('year', 'month', 'day'):
            if type(req.get(k)) is not int:
                raise ValueError('起始日期必须为整数年月日')
        days = req.get('days', 31)
        if type(days) is not int or not 1 <= days <= 92:
            raise ValueError('查询天数必须为 1–92')
        start = date(req['year'], req['month'], req['day'])
        if not 1900 <= start.year <= 2100 or (start + timedelta(days=days)).year > 2100:
            raise ValueError('日期范围仅支持 1900–2100 年')
        main_z, minor_z = _zodiacs(req)
        clash_set = set(main_z) | set(minor_z)
        label, terms, group = EVENTS[event]
        rows = []
        for i in range(days):
            d = start + timedelta(days=i)
            lunar = Solar.fromYmd(d.year, d.month, d.day).getLunar()
            day_zhi = _call(lunar, 'getDayZhi') or ''
            if day_zhi not in DI_ZHI: continue
            yi, ji = list(_call(lunar, 'getDayYi', []) or []), list(_call(lunar, 'getDayJi', []) or [])
            jian_chu = _call(lunar, 'getZhiXing')
            rel, rel_minor = _relations(day_zhi, main_z), _relations(day_zhi, minor_z)
            level, reasons, caution, avoid = _classify(
                terms, yi, ji, jian_chu, rel, event, day_zhi, _call(lunar, 'getYearZhi'), rel_minor)
            if (abs(_call(lunar, 'getMonth', 0) or 0), _call(lunar, 'getDay', 0)) in YANGGONG:
                caution.append('杨公忌日（部分流派）')
            rows.append({
                'date': d.isoformat(), 'weekday': '一二三四五六日'[d.weekday()],
                'lunar': _call(lunar, 'toString'), 'ganzhi': _call(lunar, 'getDayInGanZhi'),
                'jian_chu': jian_chu, 'xiu': _call(lunar, 'getXiu'),
                'tianshen': _call(lunar, 'getDayTianShen'), 'tianshen_type': _call(lunar, 'getDayTianShenType'),
                'chong': _call(lunar, 'getDayChongDesc'), 'sha': _call(lunar, 'getDaySha'),
                'pengzu': [_call(lunar, 'getPengZuGan'), _call(lunar, 'getPengZuZhi')],
                'yi': yi, 'ji': ji, 'ji_shen': list(_call(lunar, 'getDayJiShen', []) or []),
                'xiong_sha': list(_call(lunar, 'getDayXiongSha', []) or []),
                'level': level, 'reasons': reasons, 'cautions': caution, 'avoids': avoid,
                'hours': _hours(lunar, clash_set) if level in ('good', 'ok') else []})
        order = {'good': 0, 'ok': 1, 'neutral': 2, 'avoid': 3}
        return {'status': 'success', 'event': {'key': event, 'label': label, 'group': group},
                'zodiacs': main_z, 'zodiacs_minor': minor_z, 'days': rows,
                'summary': {k: sum(r['level'] == k for r in rows) for k in order},
                'calculation_audit': {
                    'source': 'lunar_python 内置黄历宜忌、建除、二十八宿、天神数据',
                    'rules_added_here': ['事项与黄历宜忌条目对应', '建除破日', '主要当事人生肖冲（避开）/害/刑（提示）', '其他相关人生肖冲害刑（仅提示）', '岁破日', '杨公忌日提示'],
                    'not_included': ['四离四绝', '三煞/太岁方位细则', '真太阳时', '节气交界日的流派差异'],
                    'scope': '传统黄历资料筛选，不同流派取舍不同；不保证吉凶，重大事项请自行核对并咨询专业人士。'}}
