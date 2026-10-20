"""Defensive, tri-state structural diagnostics. Not a school-rule certification."""
from ziwei_engine import DI_ZHI, MAJOR_STARS, BIRTH_FOUR_TRANSFORMATIONS
STEMS='甲乙丙丁戊己庚辛壬癸'
HUAS=('化禄','化权','化科','化忌')

def inspect_chart(chart):
    checks=[]
    def record(code, condition, detail=''):
        checks.append({'id':code,'status':'passed' if condition is True else 'failed' if condition is False else 'not_checked','detail':detail})
    if not isinstance(chart,dict):
        return {'version':'v8.261','checks':[{'id':'chart_object','status':'failed','detail':'命盘必须是对象'}], 'passed':False,'event_certified':False,'traditional_rules_certified':False}
    record('chart_object',True)
    p=chart.get('palaces')
    valid_p=isinstance(p,dict) and set(p)==set(DI_ZHI) and all(isinstance(v,dict) for v in p.values())
    record('palaces_complete',valid_p)
    if not valid_p:
        return {'version':'v8.261','checks':checks,'passed':False,'event_certified':False,'traditional_rules_certified':False}
    stems=[v.get('gan') for v in p.values()]
    record('palace_stems',all(isinstance(s,str) and len(s)==1 and s in STEMS for s in stems))
    names=[v.get('name') for v in p.values()]
    record('palace_names',all(isinstance(s,str) and bool(s.strip()) and len(s)<=20 for s in names))
    record('palace_names_unique',all(isinstance(s,str) for s in names) and len(set(names))==12)
    stars=[]; lists_valid=True; duplicate=False; star_valid=True
    for v in p.values():
        a,b=v.get('mainStars'),v.get('minorStars')
        if not isinstance(a,list) or not isinstance(b,list): lists_valid=False; continue
        if not all(isinstance(s,str) and 0<len(s.strip())<=30 for s in a+b):star_valid=False
        if len(a+b)!=len(set(str(s) for s in a+b)):duplicate=True
        stars.extend(s for s in a+b if isinstance(s,str))
    record('star_lists',lists_valid)
    record('star_strings',star_valid if lists_valid else None)
    record('duplicate_stars_in_palace',not duplicate if lists_valid else None)
    record('major_star_uniqueness',all(stars.count(s)<=1 for s in MAJOR_STARS) if lists_valid else None)
    record('major_star_coverage',all(stars.count(s)==1 for s in MAJOR_STARS) if lists_valid else None)
    brightness_ok=True
    for v in p.values():
        bright=v.get('star_brightness',{})
        if not isinstance(bright,dict):brightness_ok=False;break
        available=(v.get('mainStars') or [])+(v.get('minorStars') or []) if isinstance(v.get('mainStars'),list) and isinstance(v.get('minorStars'),list) else []
        if any(not isinstance(k,str) or k not in available or not isinstance(val,str) or not val.strip() for k,val in bright.items()):brightness_ok=False;break
    record('brightness_references',brightness_ok if lists_valid else None)
    four=chart.get('birth_four')
    record('birth_four_structure',isinstance(four,dict) and set(four)==set(HUAS) if four is not None else None)
    if isinstance(four,dict):
        record('birth_four_values',all(isinstance(v,str) and bool(v.strip()) for v in four.values()))
        record('birth_four_star_positions',all(v in stars for v in four.values()) if lists_valid else None)
    else:
        record('birth_four_values',None);record('birth_four_star_positions',None)
    year=chart.get('year_gan_zhi')
    record('year_stem',isinstance(year,str) and len(year)==2 and year[0] in STEMS and year[1] in DI_ZHI if year is not None else None)
    record('four_table_match',four==BIRTH_FOUR_TRANSFORMATIONS.get(year[0]) if isinstance(four,dict) and isinstance(year,str) and len(year)==2 and year[0] in STEMS else None)
    for field in ('ming_gong','shen_gong'):
        value=chart.get(field)
        record(field,value in DI_ZHI if isinstance(value,str) else None if value is None else False)
    gm=chart.get('ganMap')
    record('ganmap_structure',isinstance(gm,dict) and set(gm)==set(DI_ZHI) if gm is not None else None)
    if isinstance(gm,dict) and set(gm)==set(DI_ZHI):
        record('ganmap_match',all(isinstance(gm[z],str) and isinstance(p[z].get('gan'),str) and gm[z]==p[z]['gan']+z for z in DI_ZHI))
    else:record('ganmap_match',None)
    return {'version':'v8.261','checks':checks,'passed':all(x['status']=='passed' for x in checks),
        'failed':[x['id'] for x in checks if x['status']=='failed'],
        'not_checked':[x['id'] for x in checks if x['status']=='not_checked'],
        'event_certified':False,'traditional_rules_certified':False,
        'note':'工程结构检查，不是排盘传统规则或人生事件准确性认证。'}
