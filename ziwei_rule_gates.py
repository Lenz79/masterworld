"""V8.60: evidence-gate matrix. Position evidence is not interpretive validation."""
GATES=('position','source','sha','brightness','four_transformations','school_definition')

def evaluate_gates(rule, contributions):
    claimed_witnesses=rule.get('witnesses') or []
    by_zhi={p['zhi']:p for p in contributions}
    # Never trust a cached witness without checking the underlying physical palace.
    witnesses=[]; rejected=[]; seen=set()
    for w in claimed_witnesses:
        z=w.get('zhi'); required=set(w.get('stars') or [])
        actual=set(by_zhi.get(z,{}).get('stars') or [])
        if z not in by_zhi or not required or not required.issubset(actual):
            rejected.append({'zhi':z,'claimed_stars':sorted(required),'actual_stars':sorted(actual),
                             'reason':'证据宫位缺失或所声称星曜与实际宫位不符'})
        elif z not in seen:
            witnesses.append(w); seen.add(z)
    position='met' if witnesses else 'not_met'
    source='verified_metadata_only' if rule.get('provenance',{}).get('traditional_definition_verified') else 'unverified'
    sha=[]; brightness=[]
    for w in witnesses:
        p=by_zhi.get(w['zhi'],{})
        stars=set(p.get('stars') or [])
        sha.append({'zhi':w['zhi'],'observed':sorted(stars & {'擎羊','陀罗','火星','铃星','地空','地劫'})})
        grades=p.get('brightness') or {}
        brightness.append({'zhi':w['zhi'],'provided':{s:grades[s] for s in w['stars'] if s in grades and grades[s]},
                           'missing':[s for s in w['stars'] if not grades.get(s)]})
    return {'rule_id':rule['id'],'title':rule['title'],
            'gates':{'position':position,'source':source,'sha':'observed_not_interpreted' if witnesses else 'not_applicable',
                     'brightness':'partial_observation' if witnesses else 'not_applicable',
                     'four_transformations':'not_calibrated','school_definition':'not_calibrated'},
            'sha_evidence':sha,'brightness_evidence':brightness,
            'rejected_witnesses':rejected,'validated_witness_count':len(witnesses),
            'eligible_for_pattern_conclusion':False,'eligible_for_event_conclusion':False,
            'missing_requirements':['经校验的流派格局定义','煞忌解释及排除门槛','亮度判据与数据核验','独立四化配合规则'],
            'note':'位置必要条件不等于传统格局成立；观测到煞星不代表吉凶已确定。'}

def audit_gate_matrix(rule_audit, contributions):
    records=[evaluate_gates(r,contributions) for r in rule_audit.get('rules',[])]
    return {'version':'v8.60-gates-1','rules':records,'formed_patterns':0,'confirmed_events':0,
            'note':'所有规则均只输出证据及未校准门槛，不输出格局成败或事件断语。'}
