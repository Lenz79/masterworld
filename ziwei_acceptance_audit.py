"""V8.142–V8.181: conservative release evidence acceptance gates.
Checks are engineering consistency assertions, NOT divination or tradition certification.
Every check has pass/fail/not_checked semantics; absent evidence never passes.
"""
from ziwei_engine import DI_ZHI, MAJOR_STARS, BIRTH_FOUR_TRANSFORMATIONS
STEMS = set('甲乙丙丁戊己庚辛壬癸')
HUAS = set(('化禄','化权','化科','化忌'))

def _chart_palaces(c):
    return c.get('palaces') if isinstance(c,dict) and isinstance(c.get('palaces'),dict) else None

def _stars(p):
    if not isinstance(p,dict): return None
    a,b=p.get('mainStars'),p.get('minorStars')
    if not isinstance(a,list) or not isinstance(b,list): return None
    if not all(isinstance(s,str) for s in a+b): return None
    return a+b

def _records(a,key):
    if not isinstance(a,dict): return None
    return a.get(key)

def _all_palaces(c):
    p=_chart_palaces(c)
    return p if p is not None and set(p)==set(DI_ZHI) and all(isinstance(v,dict) for v in p.values()) else None

def _star_map(c):
    p=_all_palaces(c)
    if p is None: return None
    out={}
    for z,pal in p.items():
        ss=_stars(pal)
        if ss is None:return None
        for s in ss:out.setdefault(s,set()).add(z)
    return out

def audit_acceptance(chart,analysis=None):
    """Returns tri-state checks; all_passed requires all 40 checks checked and passing."""
    a=analysis if isinstance(analysis,dict) else {}
    p=_all_palaces(chart); sm=_star_map(chart)
    annual=_records(a,'annual_integrity_audit')
    decade=_records(a,'decade_integrity_audit')
    layer=_records(a,'layer_consistency_audit')
    quality=_records(a,'quality_audit')
    delivery=_records(a,'delivery_audit')
    rules=[]
    def check(code,group,available,predicate):
        if not available: status='not_checked'
        else:
            try: status='passed' if bool(predicate()) else 'failed'
            except (TypeError,ValueError,KeyError,IndexError,AttributeError,OverflowError):status='failed'
        rules.append({'id':code,'group':group,'status':status})
    # 142–151: physical chart structural consistency
    check('palaces_complete','chart',p is not None,lambda:True)
    check('palace_stems','chart',p is not None,lambda:all(v.get('gan') in STEMS for v in p.values()))
    check('palace_names','chart',p is not None,lambda:all(isinstance(v.get('name'),str) and bool(v['name'].strip()) for v in p.values()))
    check('palace_names_unique','chart',p is not None,lambda:len({v.get('name') for v in p.values()})==12)
    check('star_lists','chart',p is not None,lambda:all(_stars(v) is not None for v in p.values()))
    check('star_strings_nonempty','chart',sm is not None,lambda:all(s.strip() for s in sm))
    check('no_palace_duplicate','chart',sm is not None,lambda:all(len(_stars(v))==len(set(_stars(v))) for v in p.values()))
    check('major_stars_unique','chart',sm is not None,lambda:all(len(sm.get(s,set()))<=1 for s in MAJOR_STARS))
    check('major_stars_complete','chart',sm is not None,lambda:all(len(sm.get(s,set()))==1 for s in MAJOR_STARS))
    check('brightness_targets','chart',sm is not None,lambda:all(isinstance(v.get('star_brightness',{}),dict) and set(v.get('star_brightness',{})).issubset(set(_stars(v))) for v in p.values()))
    # 152–161: chart metadata / birth four consistency
    check('birth_four_object','metadata',isinstance(chart,dict) and 'birth_four' in chart,lambda:isinstance(chart['birth_four'],dict))
    check('birth_four_keys','metadata',isinstance(chart,dict) and 'birth_four' in chart,lambda:set(chart['birth_four'])==HUAS)
    check('birth_four_values','metadata',isinstance(chart,dict) and 'birth_four' in chart,lambda:all(isinstance(s,str) and bool(s.strip()) for s in chart['birth_four'].values()))
    check('year_stem_present','metadata',isinstance(chart,dict) and 'year_gan_zhi' in chart,lambda:isinstance(chart['year_gan_zhi'],str) and len(chart['year_gan_zhi'])>=2 and chart['year_gan_zhi'][0] in STEMS)
    check('birth_four_table_match','metadata',isinstance(chart,dict) and 'birth_four' in chart and 'year_gan_zhi' in chart,lambda:chart['birth_four']==BIRTH_FOUR_TRANSFORMATIONS[chart['year_gan_zhi'][0]])
    check('ming_branch','metadata',isinstance(chart,dict) and 'ming_gong' in chart,lambda:chart['ming_gong'] in DI_ZHI)
    check('shen_branch','metadata',isinstance(chart,dict) and 'shen_gong' in chart,lambda:chart['shen_gong'] in DI_ZHI)
    check('ganmap_12','metadata',isinstance(chart,dict) and 'ganMap' in chart,lambda:isinstance(chart['ganMap'],dict) and set(chart['ganMap'])==set(DI_ZHI))
    check('ganmap_stem_match','metadata',isinstance(chart,dict) and 'ganMap' in chart and p is not None,lambda:all(isinstance(chart['ganMap'][z],str) and chart['ganMap'][z][0]==v['gan'] for z,v in p.items()))
    check('ganmap_branch_match','metadata',isinstance(chart,dict) and 'ganMap' in chart,lambda:all(isinstance(v,str) and len(v)==2 and v[1]==z for z,v in chart['ganMap'].items()))
    # 162–171: actual audits, never substitute synthetic green status
    check('delivery_present','audit',delivery is not None,lambda:isinstance(delivery,dict))
    check('delivery_checks','audit',delivery is not None,lambda:isinstance(delivery.get('checks'),dict) and bool(delivery['checks']))
    check('delivery_no_events','audit',delivery is not None,lambda:delivery.get('event_concluded') is False)
    check('delivery_no_patterns','audit',delivery is not None,lambda:delivery.get('pattern_concluded') is False)
    check('quality_present','audit',quality is not None,lambda:isinstance(quality,dict))
    check('quality_checks','audit',quality is not None,lambda:isinstance(quality.get('checks'),dict) and bool(quality['checks']))
    check('quality_no_events','audit',quality is not None,lambda:quality.get('event_concluded') is False)
    check('quality_no_patterns','audit',quality is not None,lambda:quality.get('pattern_concluded') is False)
    check('quality_missing_not_passed','audit',quality is not None,lambda:all(v.get('status') in ('passed','failed','not_applicable') for v in quality.get('checks',{}).values()) and not (quality.get('skipped') and quality.get('passed')))
    check('delivery_failed_not_passed','audit',delivery is not None,lambda:not (delivery.get('failed') and delivery.get('passed')))
    # 172–181: annual/decade/cross-layer and conclusion safety
    check('annual_audit_present','layers',annual is not None,lambda:isinstance(annual,dict))
    check('annual_boundary_disclosed','layers',annual is not None,lambda:annual.get('year_boundary_calibrated') is False)
    check('annual_events_unclaimed','layers',annual is not None,lambda:annual.get('event_formed') is None)
    check('annual_integrity_boolean','layers',annual is not None,lambda:type(annual.get('all_consistent')) is bool)
    check('decade_audit_present','layers',decade is not None,lambda:isinstance(decade,dict))
    check('decade_school_disclosed','layers',decade is not None,lambda:decade.get('school_rule_calibrated') is False)
    check('decade_events_unclaimed','layers',decade is not None,lambda:decade.get('event_formed') is None)
    check('decade_integrity_state','layers',decade is not None,lambda:decade.get('all_consistent') in (True,False,None))
    check('cross_layer_no_false_confirmation','layers',layer is not None,lambda:layer.get('independent_layer_confirmation') is False)
    check('analysis_no_event_certification','layers',isinstance(analysis,dict),lambda:a.get('event_formed') is not True and a.get('confirmed_events',0)==0)
    failures=[x['id'] for x in rules if x['status']=='failed']
    missing=[x['id'] for x in rules if x['status']=='not_checked']
    return {'version':'v8.181','checks':rules,'passed':not failures and not missing,
      'failed':failures,'not_checked':missing,'counts':{'passed':sum(x['status']=='passed' for x in rules),'failed':len(failures),'not_checked':len(missing)},
      'pattern_certified':False,'event_certified':False,'production_ready':False,
      'note':'工程资料与证据边界检查，不代表流派规则、历法交界或预测结论获得验证。'}
