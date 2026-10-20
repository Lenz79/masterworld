"""V8.50: source-aware cross-layer evidence. No event predictions."""
from collections import defaultdict
from ziwei_engine import DI_ZHI, BIRTH_FOUR_TRANSFORMATIONS


def verify_evidence(analysis, chart):
    """Separate natal-palace reuse from genuine annual-stem evidence.

    A layer label is never counted as a new independent rule. Annual stem
    transformation is separately classified; its year boundary remains provisional.
    """
    palaces = chart.get('palaces') or {}
    if any(z not in palaces for z in DI_ZHI):
        raise ValueError('十二宫资料不完整')
    edges = analysis.get('edges', [])
    annual = analysis.get('annual_stem_four', [])
    physical = defaultdict(list)
    for edge in edges:
        key = (edge.get('source'), edge.get('target'), edge.get('gan'),
               edge.get('star'), edge.get('hua'))
        physical[key].append(edge.get('layer'))
    paths = []
    for key, layers in physical.items():
        paths.append({'source':key[0], 'target':key[1], 'gan':key[2],
                      'star':key[3], 'hua':key[4], 'layer_labels':sorted(set(layers)),
                      'independence':'同一物理宫干路径；不同层级仅重命名'})
    year_paths = []
    for edge in annual:
        year_paths.append({'source':'流年天干', 'target':edge['target'],
                           'gan':edge['gan'], 'star':edge['star'], 'hua':edge['hua'],
                           'independence':'独立年度干四化规则；年界未校准'})
    # Real 'unresolved' star transformations must be visible instead of silently omitted.
    star_at = set()
    for p in palaces.values():
        star_at.update(p.get('mainStars') or [])
        star_at.update(p.get('minorStars') or [])
    unresolved = []
    for zhi in DI_ZHI:
        gan = palaces[zhi].get('gan')
        if gan not in BIRTH_FOUR_TRANSFORMATIONS:
            unresolved.append({'source':zhi, 'gan':gan, 'reason':'宫干缺失或四化表不支持'})
            continue
        for hua, star in BIRTH_FOUR_TRANSFORMATIONS[gan].items():
            if star not in star_at:
                unresolved.append({'source':zhi, 'gan':gan, 'hua':hua,
                                   'star':star, 'reason':'该星未出现在当前排盘数据中'})
    groups = defaultdict(list)
    for edge in paths:
        groups[edge['target']].append(edge)
    for edge in year_paths:
        groups[edge['target']].append(edge)
    overlaps=[]
    for zhi, members in groups.items():
        natal=[m for m in members if m['source']!='流年天干']
        yearly=[m for m in members if m['source']=='流年天干']
        if natal and yearly:
            overlaps.append({'target':zhi,'natal_palace':palaces[zhi].get('name'),
                             'natal_paths':len(natal),'annual_stem_paths':len(yearly),
                             'classification':'本命宫干与年干四化同宫呼应（不是事件成立）'})
    return {'version':'1.0-source-aware', 'physical_natal_paths':paths,
            'annual_stem_paths':year_paths,'unresolved_transformations':unresolved,
            'natal_annual_overlaps':overlaps,
            'independent_rule_families':['本命宫干四化','流年天干四化（年界待校准）'],
            'decade_independent':False,'annual_palace_independent':False,
            'event_confirmed':False,
            'warning':'大限与流年十二宫目前仍复用本命宫干，不构成独立证据；年干四化不等于事件应期。'}


def audit_directional_claims(analysis, chart):
    """Check if claimed reciprocal relations are independent, not mirrored aliases.

    The same natal palace stem reused in a decade/year view is a relabelled
    physical edge. This function deliberately refuses to certify reciprocity
    unless the two directions use genuinely distinct calculation families.
    """
    palaces=chart.get('palaces') or {}
    reciprocal=analysis.get('reciprocal_candidates') or []
    cross=analysis.get('cross_layer_paths') or []
    def physical_id(e):
        return (e.get('source'),e.get('target'),e.get('star'),e.get('hua'))
    checked=[]
    for candidate in reciprocal:
        a,b=candidate['forward'],candidate['backward']
        a_id,b_id=physical_id(a),physical_id(b)
        # Existing cross-layer paths share the same natal-palace-stem family.
        checked.append({'forward':a_id,'backward':b_id,
            'physical_distinct':a_id!=b_id,
            'independent_rule_families':False,
            'verdict':'跨层重命名路径，不能确认为独立双向飞化',
            'source_layers':[a.get('from_layer'),b.get('from_layer')]})
    annual=analysis.get('annual_stem_four') or []
    natal=analysis.get('edges') or []
    natal_unique={ (e['source'],e['target'],e['star'],e['hua'],e.get('gan')):e
        for e in natal if e.get('layer')=='本命'}
    yearly_pairs=[]
    for a in annual:
        for e in natal_unique.values():
            if a['target']!=e['target']:continue
            yearly_pairs.append({'target':a['target'],
                'natal_source':e['source'],'natal_stem':e.get('gan'),
                'natal_star':e['star'],'natal_hua':e['hua'],
                'annual_stem':a['gan'],'annual_star':a['star'],'annual_hua':a['hua'],
                'classification':'本命宫干与年度天干两类规则同宫；不是双向飞化或应事'})
    return {'version':'1.0-direction-audit','cross_layer_paths_checked':len(cross),
      'reciprocal_aliases_checked':len(checked),
      'reciprocal_aliases':checked,
      'certified_reciprocal_count':0,
      'natal_annual_pairs':yearly_pairs,
      'status':'仅可确认不同计算规则同宫呼应；未校准真正双向飞化与飞伏判据',
      'required_for_confirmation':['明确大限与流年独立宫干起法','验证两条反向路径各自的宫干与星曜',
        '验证本命叠宫、星系及派别特定飞伏条件','校准年界及应期']}
