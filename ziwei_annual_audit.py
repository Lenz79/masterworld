"""V8.62: independently audit calendar-year stem transformations as observations.
Not a validated lunar/solar boundary, decade stem or event engine.
"""
from collections import defaultdict
from ziwei_engine import BIRTH_FOUR_TRANSFORMATIONS, DI_ZHI

STEMS='甲乙丙丁戊己庚辛壬癸'

def audit_annual_stem(chart, year, annual_four):
    year=int(year)
    if not 1900 <= year <= 2200: raise ValueError('流年超出支持范围')
    palaces=chart.get('palaces') or {}
    if set(palaces)!=set(DI_ZHI): raise ValueError('十二宫数据不完整')
    stem=STEMS[(year-4)%10]
    expected=BIRTH_FOUR_TRANSFORMATIONS.get(stem,{})
    star_at=defaultdict(set)
    for zhi in DI_ZHI:
        p=palaces[zhi]
        for star in (p.get('mainStars') or [])+(p.get('minorStars') or []):
            star_at[star].add(zhi)
    checks=[]
    for hua,star in expected.items():
        expected_zhi=sorted(star_at.get(star,()))
        actual=[x for x in annual_four if x.get('hua')==hua]
        valid=[x for x in actual if x.get('gan')==stem and x.get('star')==star and x.get('target') in expected_zhi]
        actual_targets=[x.get('target') for x in valid]
        consistent=(len(actual)==len(expected_zhi) and sorted(actual_targets)==expected_zhi and len(set(actual_targets))==len(actual_targets))
        checks.append({'hua':hua,'star':star,'expected_positions':expected_zhi,
          'recorded_positions':actual_targets,'observed':bool(expected_zhi),
          'integrity':'consistent' if consistent else 'mismatch',
          'status':'已找到实际星曜落宫' if expected_zhi else '星曜未落宫；不可补造目标'})
    extra=[x for x in annual_four if x.get('hua') not in expected]
    return {'version':'v8.62-annual-integrity','year':year,'stem':stem,
      'calendar_basis':'公历年份换算干支的试算；未按立春或农历新年校准',
      'checks':checks,'all_consistent':all(x['integrity']=='consistent' for x in checks) and not extra,
      'unrecognized_records':len(extra),
      'independent_from_palace_stems':True,
      'decade_stem_calibrated':False,'year_boundary_calibrated':False,'annual_date_supplied':False,'year_stem_status':'公历年试算，年界未校准',
      'event_formed':None,
      'limitations':['仅校验年度天干四化与命盘实际星曜落点的一致性','大限四化、限年宫干规则尚未校准','交界日期及流派四化表尚待核验']}
