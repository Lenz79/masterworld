"""V8.63 selected decade transformation integrity audit, not school validation."""
from collections import defaultdict
from ziwei_engine import BIRTH_FOUR_TRANSFORMATIONS, DI_ZHI


def audit_decade_stem(chart, decade_zhi):
    if decade_zhi is None:
        return {'version':'v8.63','selected':False,'status':'未选择大限','checks':[],
                'all_consistent':None,'school_rule_calibrated':False,'event_formed':None}
    if decade_zhi not in DI_ZHI:
        raise ValueError('无效大限地支')
    palaces=chart.get('palaces') or {}
    if set(palaces)!=set(DI_ZHI):
        raise ValueError('十二宫数据不完整')
    palace=palaces[decade_zhi]
    stem=palace.get('gan')
    if stem not in BIRTH_FOUR_TRANSFORMATIONS:
        return {'version':'v8.63','selected':True,'decade_zhi':decade_zhi,'stem':stem,
                'status':'大限宫干缺失或无效','checks':[],'all_consistent':False,
                'school_rule_calibrated':False,'event_formed':None}
    entries=[x for x in chart.get('decade_charts',[]) if x.get('zhi')==decade_zhi]
    star_at=defaultdict(set)
    for zhi in DI_ZHI:
        p=palaces[zhi]
        for star in (p.get('mainStars') or [])+(p.get('minorStars') or []):
            star_at[star].add(zhi)
    expected=BIRTH_FOUR_TRANSFORMATIONS[stem]
    checks=[]
    recorded=entries[0].get('flying_transformations',[]) if len(entries)==1 else []
    for hua,star in expected.items():
        targets=sorted(star_at.get(star,()))
        matched=[e for e in recorded if e.get('transformation')==hua]
        accepted=[e['to'] for e in matched if e.get('from')==decade_zhi and
                  e.get('star')==star and e.get('to') in targets]
        ok=(len(matched)==len(targets) and sorted(accepted)==targets and
            len(accepted)==len(set(accepted)))
        checks.append({'hua':hua,'star':star,'expected_positions':targets,
                       'recorded_positions':accepted,'integrity':'consistent' if ok else 'mismatch',
                       'observed':bool(targets)})
    unknown=[e for e in recorded if e.get('transformation') not in expected]
    metadata_ok=len(entries)==1 and entries[0].get('gan')==stem and entries[0].get('four')==expected
    return {'version':'v8.63','selected':True,'decade_zhi':decade_zhi,
            'decade_range':palace.get('decade'),'stem':stem,'checks':checks,
            'metadata_consistent':metadata_ok,'unrecognized_records':len(unknown),
            'all_consistent':metadata_ok and not unknown and all(c['integrity']=='consistent' for c in checks),
            'status':'已核对大限宫干四化物理落点；流派起法未校准',
            'school_rule_calibrated':False,'event_formed':None,
            'limitations':['使用所选大限宫位本命宫干及项目现有四化表；并非独立验证的流派大限起法',
                           '未核实大限起止岁数、交界日期、事件应期']}
