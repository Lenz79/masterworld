"""V8.58: versioned, explicitly provisional location-only rule registry.

No historical-school attribution or predictive validity is asserted.
"""
from ziwei_rule_provenance import validate_registry, provenance
RULESET_VERSION = 'v8.59-provenance-gates-1'
RULES = (
 {'id':'zi_fu_same','title':'紫微、天府同宫位置','stars':('紫微','天府')},
 {'id':'chang_qu_same','title':'文昌、文曲同宫位置','stars':('文昌','文曲')},
 {'id':'zuo_you_same','title':'左辅、右弼同宫位置','stars':('左辅','右弼')},
 {'id':'kui_yue_same','title':'天魁、天钺同宫位置','stars':('天魁','天钺')},
)

def audit_rules(contributions):
    """Only necessary co-location facts are evaluated; all interpretation gates unknown."""
    registry_check=validate_registry(RULES)
    if not registry_check['valid']:
        raise ValueError('规则库校验失败：'+'; '.join(registry_check['issues']))
    palaces={c['zhi']:c for c in contributions}
    results=[]
    for rule in RULES:
        a,b=rule['stars']
        present={s:[z for z,c in palaces.items() if s in c.get('stars',[])] for s in (a,b)}
        common=sorted(set(present[a])&set(present[b]))
        missing=[s for s in (a,b) if not present[s]]
        if common: state='位置条件符合'
        elif missing: state='位置条件不足'
        else: state='分宫出现，未满足同宫条件'
        witnesses=[]
        for z in common:
            c=palaces[z]
            witnesses.append({'zhi':z,'role':c.get('role'), 'palace':c.get('palace'), 'stars':[a,b]})
        results.append({'id':rule['id'],'title':rule['title'], 'source':'本项目内部位置核对规则（非经考证的传统格局定义）',
          'version':RULESET_VERSION,'provenance':provenance(rule),'necessary_conditions':[f'{a}与{b}位于同一物理宫位'],
          'exclusion_conditions':['两星仅分布于不同宫位','任一星在当前三方四正范围未出现'],
          'observed_positions':present,'witnesses':witnesses,'missing_stars':missing,
          'position_state':state,'position_condition_met':bool(common),
          'sha_impact_verified':None,'brightness_threshold_verified':None,
          'four_transformations_verified':None,'school_definition_verified':None,
          'traditional_pattern_formed':None,'event_formed':None,
          'unresolved':['传统格局原始定义与流派差异','煞忌条件','亮度数据与门槛','四化配合与限年独立规则']})
    return {'version':RULESET_VERSION,'registry_validation':registry_check,'rules':results,
            'verified_traditional_patterns':0,
            'note':'规则库仅校验可复核的星曜同宫位置；不提供格局成败或事件结论。'}
