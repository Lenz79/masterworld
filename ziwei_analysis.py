"""可审计的紫微四化关系图。四化飞伏仅做路径追踪，不把路径自动认定为事件。"""
from collections import defaultdict
from ziwei_rule_registry import audit_rules
from ziwei_rule_gates import audit_gate_matrix
from ziwei_engine import BIRTH_FOUR_TRANSFORMATIONS, DI_ZHI, MAJOR_STARS

FOUR = ("化禄", "化权", "化科", "化忌")
KEYWORDS = {"化禄":"资源、机会、收益议题", "化权":"权责、主导、执行议题",
            "化科":"名誉、文书、协调议题", "化忌":"牵挂、阻滞、责任或耗损议题"}
ISSUES = {
 "事业":["事业宫","财帛宫","交友宫","迁移宫"],
 "合作":["兄弟宫","交友宫","夫妻宫","财帛宫"],
 "感情":["夫妻宫","福德宫","子女宫","命宫"],
 "财务":["财帛宫","田宅宫","兄弟宫","事业宫"],
 "家庭":["田宅宫","父母宫","夫妻宫","子女宫"],
 "健康管理":["疾厄宫","福德宫","命宫","迁移宫"],
}
PALACE_NAMES = ["命宫","兄弟宫","夫妻宫","子女宫","财帛宫","疾厄宫",
                "迁移宫","交友宫","事业宫","田宅宫","福德宫","父母宫"]

def layer_name(origin, zhi):
    if origin not in DI_ZHI or zhi not in DI_ZHI: return None
    return PALACE_NAMES[(DI_ZHI.index(origin)-DI_ZHI.index(zhi))%12]

def year_branch(year):
    return DI_ZHI[(int(year)-4)%12]

def build_analysis(chart, decade_zhi=None, year=None):
    palaces=chart.get("palaces") or {}
    if len(palaces)!=12 or any(z not in palaces for z in DI_ZHI):
        raise ValueError("需要十二宫完整排盘数据")
    year=int(year or 2026)
    if not 1900<=year<=2200: raise ValueError("流年超出支持范围")
    decade_zhi=decade_zhi if decade_zhi in DI_ZHI else None
    annual_zhi=year_branch(year)
    star_at=defaultdict(list)
    for zhi,p in palaces.items():
        for star in set((p.get("mainStars") or [])+(p.get("minorStars") or [])):
            star_at[star].append(zhi)
    # 三层宫位映射；流年天干四化沿用现有十干表，但流年农历交界尚未核验
    stems="甲乙丙丁戊己庚辛壬癸"
    annual_stem=stems[(year-4)%10]
    # 本命、大限、流年：均以同一十二宫物理落点，按不同层级解释宫名。
    # 宫干四化为试算规则；限年宫干的起法须与目标流派核对。
    layers={"本命":list(DI_ZHI), "大限":list(DI_ZHI) if decade_zhi else [],
            "流年":list(DI_ZHI)}
    edges=[]
    for layer,sources in layers.items():
        for zhi in sources:
            p=palaces[zhi]
            # 宫干飞化：三层十二宫各自用本命盘的宫干；流年干四化另作年度层记录。
            gan=p.get("gan")
            for hua,star in BIRTH_FOUR_TRANSFORMATIONS.get(gan,{}).items():
                for dest in star_at.get(star,[]):
                    edges.append({"layer":layer,"source":zhi,"source_natal":p.get("name"),
                      "source_layer_palace":layer_name(decade_zhi,zhi) if layer=="大限" else layer_name(annual_zhi,zhi) if layer=="流年" else p.get("name"),
                      "gan":gan,"hua":hua,"star":star,"target":dest,
                      "target_natal":palaces[dest].get("name"),
                      "target_decade":layer_name(decade_zhi,dest) if decade_zhi else None,
                      "target_annual":layer_name(annual_zhi,dest),
                      "self":zhi==dest,"status":"path_only","method":"宫干四化（待核对限年宫干规则）"})
    # 年干四化与宫干飞化分开标记，避免把年度天干当作流年命宫宫干。
    annual_four=[]
    for hua,star in BIRTH_FOUR_TRANSFORMATIONS.get(annual_stem,{}).items():
        for dest in star_at.get(star,[]):
            annual_four.append({"gan":annual_stem,"hua":hua,"star":star,"target":dest,
                                "target_natal":palaces[dest].get("name"),
                                "target_annual":layer_name(annual_zhi,dest)})
    # 双向路径：层A的宫位主题指向层B的目标主题；另有反向关系时记录双方证据。
    # 这里仅为关系图交叉验证，不能直接视为事件成立。
    cross=[]
    layer_pairs=[("本命","大限"),("大限","本命"),("大限","流年"),
                 ("流年","大限"),("本命","流年"),("流年","本命")]
    for from_layer,to_layer in layer_pairs:
        if from_layer=="大限" or to_layer=="大限":
            if not decade_zhi:continue
        matches=[e for e in edges if e["layer"]==from_layer]
        for e in matches:
            target_name=(palaces[e["target"]].get("name") if to_layer=="本命" else
                         layer_name(decade_zhi,e["target"]) if to_layer=="大限" else
                         layer_name(annual_zhi,e["target"]))
            cross.append({"from_layer":from_layer,"to_layer":to_layer,
                "source":e["source"],"source_palace":e["source_layer_palace"],
                "target":e["target"],"target_palace":target_name,
                "star":e["star"],"hua":e["hua"],"self":e["self"],
                "natal_overlay":palaces[e["target"]].get("name")})
    # 两层主题间相互飞化的候选：不要求同一颗星，保留双方路径。
    reciprocal=[]
    for i,first in enumerate(cross):
        for second in cross[i+1:]:
            if (first["from_layer"]==second["to_layer"] and
                first["to_layer"]==second["from_layer"] and
                first["source"]==second["target"] and
                first["target"]==second["source"]):
                reciprocal.append({"forward":first,"backward":second,
                  "classification":"双向飞化路径候选（非事件成立）"})
    # 伏象: 同一目标宫位有不同层级的飞化汇集，或本命原有的化象被限/年触动；
    # 此为软件的待验证关系标签，不冒称统一的流派术语定义。
    by_target=defaultdict(list)
    for e in edges: by_target[e["target"]].append(e)
    latent=[]
    for target,items in by_target.items():
        layer_set={e["layer"] for e in items}
        if len(layer_set)>=2:
            latent.append({"target":target,"natal_palace":palaces[target].get("name"),
               "layers":sorted(layer_set),"paths":[
                 {"layer":e["layer"],"source":e["source"],"hua":e["hua"],"star":e["star"]}
                 for e in items],"classification":"多层飞化汇集（伏象候选，待流派核验）"})
    events=[]
    for topic,related in ISSUES.items():
        relevant=[e for e in edges if e["source_natal"] in related or e["target_natal"] in related or
                  e["target_decade"] in related or e["target_annual"] in related]
        distinct={e["layer"] for e in relevant}
        events.append({"topic":topic,"layers":sorted(distinct),"paths":relevant[:36],
          "status":"可观察的议题线索；不等于事件成立",
          "needs":["双向飞化与冲照规则校准","星曜性质与组合核验","本命/大限/流年宫位重叠核验",
                   "现实背景或应期佐证"]})
    annual_audit=__import__("ziwei_annual_audit").audit_annual_stem(chart,year,annual_four)
    decade_audit=__import__("ziwei_decade_audit").audit_decade_stem(chart,decade_zhi)
    layer_audit=__import__("ziwei_layer_consistency").audit_layers({"edges":edges,"annual_integrity_audit":annual_audit,"decade_integrity_audit":decade_audit})
    return {"version":"0.2-cross-layer","school":"飞星派","year":year,
      "decade_zhi":decade_zhi,"annual_zhi":annual_zhi,"edges":edges,
      "latent_candidates":latent,"topics":events,
      "cross_layer_paths":cross,"reciprocal_candidates":reciprocal,
      "annual_stem_four":annual_four,
      "annual_integrity_audit":annual_audit,
      "decade_integrity_audit":decade_audit,
      "layer_consistency_audit":__import__("ziwei_layer_consistency").audit_layers({"edges":edges,"annual_integrity_audit":annual_audit,"decade_integrity_audit":__import__("ziwei_decade_audit").audit_decade_stem(chart,decade_zhi)}),
      "event_evidence":build_event_evidence({"edges":edges,"cross_layer_paths":cross,"reciprocal_candidates":reciprocal}),
      "transformation_patterns":build_transformation_patterns(edges,palaces),
      "independence_audit":audit_cross_layer_independence(edges),
      "palace_evidence":build_palace_evidence(edges,palaces,decade_zhi,annual_zhi),
      "event_conditions":build_event_conditions(edges,palaces),
      "event_readiness":build_event_readiness({"edges":edges},palaces),
      "verification":__import__("ziwei_verification").verify_evidence({"edges":edges,"annual_stem_four":annual_four},chart),
      "palace_narratives":build_palace_narratives(edges,palaces,decade_zhi,annual_zhi,annual_four),
      "direction_audit":__import__("ziwei_verification").audit_directional_claims(
          {"edges":edges,"cross_layer_paths":cross,"reciprocal_candidates":reciprocal,
           "annual_stem_four":annual_four},chart),
      "limitations":["本命/大限/流年十二宫均已建立宫干四化路径，但限年宫干规则暂沿用本命宫干，尚未按流派校准。",
       "四化飞伏在不同派别定义不一，伏象候选仅标记多层飞化汇集，不能视作已成立事件。",
       "流年按公历干支试算，立春/农历年交界未校准。",
       "双向路径仅是物理落点互指候选，未实现严格事件成立判据、流月四化；三合星曜结构已独立输出但格局判据未校准。",
       "禄忌、权忌、科忌、自化、对宫冲照均为物理路径模式，未加入派别专属成格判据。"]}



def build_transformation_patterns(edges, palaces):
    """物理宫干路径的组合特征。仅提供证据，不作应期或吉凶断言。"""
    seen={}
    for e in edges:
        k=(e["source"],e["target"],e["hua"],e["star"],e.get("gan"))
        if k not in seen:seen[k]=e
    unique=list(seen.values())
    opposite=lambda z: DI_ZHI[(DI_ZHI.index(z)+6)%12]
    patterns=[]
    for e in unique:
        if e["source"]==e["target"]:
            patterns.append({"kind":"自化","target":e["target"],"paths":[e],
                             "explanation":"发射宫与落宫相同；具体自化类别及含义需按流派核验"})
        if opposite(e["source"])==e["target"]:
            patterns.append({"kind":"对宫冲照路径","target":e["target"],"paths":[e],
                             "explanation":"飞化落在发射宫对宫；是否构成冲、照及应事需结合派别规则"})
    # 禄忌/权忌/科忌同宫只记录独立宫干路径，且要求至少两条不同物理来源。
    grouped=defaultdict(list)
    for e in unique:grouped[e["target"]].append(e)
    for target,es in grouped.items():
        for a,b,kind in (("化禄","化忌","禄忌同宫"),("化权","化忌","权忌同宫"),
                         ("化科","化忌","科忌同宫")):
            pairs=[(x,y) for x in es for y in es if x["hua"]==a and y["hua"]==b
                   and x["source"]!=y["source"]]
            if pairs:
                x,y=pairs[0]
                patterns.append({"kind":kind,"target":target,"paths":[x,y],
                   "explanation":"两条不同宫干路径汇入同一物理宫位；并不等同于事件成立"})
    return patterns


def audit_cross_layer_independence(edges):
    """揭示不同层使用同一宫干计算时产生的伪独立印证。"""
    groups=defaultdict(set)
    for e in edges:
        groups[(e["source"],e["target"],e["hua"],e["star"],e.get("gan"))].add(e["layer"])
    repeated=[{"source":k[0],"target":k[1],"hua":k[2],"star":k[3],
               "gan":k[4],"layers":sorted(layers)} for k,layers in groups.items() if len(layers)>1]
    return {"raw_layer_paths":len(edges),"independent_physical_paths":len(groups),
            "repeated_across_layers":repeated,
            "warning":"同一宫干飞化在本命/限/年重命名，不可作为独立三重验证；限年宫干未校准前禁止判定事件成立。"}

def build_event_evidence(analysis, max_evidence=12):
    """分层审计事件线索：只输出证据、缺口与状态，不将命理规则冒充事实预测。"""
    edges=analysis.get("edges",[])
    cross=analysis.get("cross_layer_paths",[])
    reciprocal=analysis.get("reciprocal_candidates",[])
    records=[]
    for topic, names in ISSUES.items():
        relevant=[e for e in edges if any(x in names for x in (
            e.get("source_natal"),e.get("target_natal"),e.get("target_decade"),e.get("target_annual"),e.get("source_layer_palace")))]
        involved={e["layer"] for e in relevant}
        pair_candidates=[]
        for r in reciprocal:
            f,b=r["forward"],r["backward"]
            if any(x in names for x in (f.get("source_palace"),f.get("target_palace"),
                b.get("source_palace"),b.get("target_palace"),f.get("natal_overlay"))):
                pair_candidates.append(r)
        # 不将层间重复使用的同一宫干路径当成独立的印证。
        unique_physical={(e["source"],e["target"],e["hua"],e["star"]) for e in relevant}
        unique_per_layer={layer:len({(e["source"],e["target"],e["hua"],e["star"])
            for e in relevant if e["layer"]==layer}) for layer in ("本命","大限","流年")}
        records.append({"topic":topic,"status":"规则待核验，不判定事件成立",
            "observed_layers":sorted(involved),"distinct_physical_paths":len(unique_physical),
            "path_counts_by_layer":unique_per_layer,"reciprocal_candidate_count":len(pair_candidates),
            "evidence":[{"layer":e["layer"],"source":e["source"],"source_palace":e["source_layer_palace"],
              "target":e["target"],"natal_palace":e["target_natal"],
              "decade_palace":e["target_decade"],"annual_palace":e["target_annual"],
              "star":e["star"],"hua":e["hua"]} for e in relevant[:max_evidence]],
            "missing_checks":["限年宫干起法及双向飞化判据未校准", "四化飞伏的流派定义尚未确认",
              "星曜组合、三方四正与冲照条件未逐项验证", "流年交界与应期尚未校准"],
            "interpretation":"只表示涉及该主题的飞化落点，不能据此认定事件发生、性质或时间。"})
    return records


SANHE_STAR_GROUPS = {
    "六吉": ("文昌", "文曲", "左辅", "右弼", "天魁", "天钺"),
    "六煞": ("擎羊", "陀罗", "火星", "铃星", "地空", "地劫"),
}

def build_sanhe_star_evidence(contributions):
    """仅以实际星曜列出三方四正的分布、共现及数据覆盖；不推断格局吉凶。"""
    by_star={}
    for item in contributions:
        for star in item['stars']:
            by_star.setdefault(star,[]).append({'role':item['role'],'zhi':item['zhi']})
    groups=[]
    for group, members in SANHE_STAR_GROUPS.items():
        present=[{'star':star,'positions':by_star[star]} for star in members if star in by_star]
        groups.append({'group':group,'present':present,'count':len(present),
                       'status':'星曜分布记录，不代表吉凶权重或格局成立'})
    major=[{'star':star,'positions':by_star[star]} for star in MAJOR_STARS if star in by_star]
    brightness=[]
    for item in contributions:
        data=item['brightness']
        for star in item['primary_stars']:
            if star in data and data[star] not in (None,'','待核验'):
                brightness.append({'star':star,'zhi':item['zhi'],'role':item['role'],
                                   'grade':data[star],'verified':False})
    return {'major_star_distribution':major,'supporting_star_groups':groups,
            'brightness_observations':brightness,
            'star_count':len(by_star),
            'notes':['仅统计三方四正实际排出的星曜，未出现的星曜不计入。',
                     '亮度来自现有排盘数据，未完成来源逐项核验，不参与自动评分。',
                     '吉煞同现只表示结构共现，不代表吉凶抵消或格局成立。']}

def build_sanhe_conditional_observations(contributions, star_evidence):
    """透明的三方四正结构条件检查；不将共现冒充传统格局或吉凶。"""
    locations={}
    for item in contributions:
        for star in item['stars']:
            locations.setdefault(star, set()).add((item['role'],item['zhi']))
    def witnesses(names):
        return [{'star':name,'positions':[{'role':role,'zhi':zhi} for role,zhi in sorted(locations.get(name,set()))]}
                for name in names if name in locations]
    lucky=witnesses(SANHE_STAR_GROUPS['六吉'])
    sha=witnesses(SANHE_STAR_GROUPS['六煞'])
    main=witnesses(MAJOR_STARS)
    checks=[
        {'id':'main_present','label':'三方四正存在主星','met':bool(main),'evidence':main,
         'meaning':'仅说明主星分布可供分析'},
        {'id':'lucky_present','label':'三方四正存在六吉','met':bool(lucky),'evidence':lucky,
         'meaning':'不自动判定吉格或有利事件'},
        {'id':'sha_present','label':'三方四正存在六煞','met':bool(sha),'evidence':sha,
         'meaning':'不自动判定凶格或不利事件'},
        {'id':'mixed_present','label':'六吉与六煞在三方四正共现','met':bool(lucky and sha),
         'evidence':lucky+sha,'meaning':'共现不代表互相抵消或产生特定格局'},
        {'id':'brightness_available','label':'存在未核验的主星亮度参考','met':bool(star_evidence['brightness_observations']),
         'evidence':star_evidence['brightness_observations'],
         'meaning':'亮度未校准，不用于判断强弱或吉凶'},
    ]
    return {'checks':checks,'observed_count':sum(c['met'] for c in checks),
            'traditional_pattern_verified':False,'event_formed':None,
            'status':'仅完成结构条件检查；传统格局与事件成立规则未核验',
            'missing':['主星组合的流派定义及必要/排除条件','亮度来源逐项核验',
                       '四化与三方四正的流派判据','大限流年独立起法及应期条件']}


SANHE_PAIR_RULES = (
    {"id":"zi_fu_same","label":"紫微、天府同宫位置核对","stars":("紫微","天府")},
    {"id":"chang_qu_same","label":"文昌、文曲同宫位置核对","stars":("文昌","文曲")},
    {"id":"zuo_you_same","label":"左辅、右弼同宫位置核对","stars":("左辅","右弼")},
    {"id":"kui_yue_same","label":"天魁、天钺同宫位置核对","stars":("天魁","天钺")},
)

def build_sanhe_pair_audit(contributions):
    """可追溯的同宫双星位置检查；不是传统格局的充分条件。"""
    by_branch={item['zhi']:set(item['stars']) for item in contributions}
    roles={item['zhi']:item['role'] for item in contributions}
    results=[]
    for rule in SANHE_PAIR_RULES:
        a,b=rule['stars']
        matched=[{'zhi':zhi,'role':roles[zhi],'stars':[a,b]}
                 for zhi,stars in by_branch.items() if a in stars and b in stars]
        found_a=[{'zhi':zhi,'role':roles[zhi]} for zhi,stars in by_branch.items() if a in stars]
        found_b=[{'zhi':zhi,'role':roles[zhi]} for zhi,stars in by_branch.items() if b in stars]
        results.append({'id':rule['id'],'label':rule['label'],'required_stars':[a,b],
                        'necessary_conditions':[f'{a}与{b}必须出现在同一物理地支宫位'],
                        'excluded_by':['任一星未出现在当前三方四正范围','两星仅在不同宫位出现'],
                        'observed':bool(matched),'witnesses':matched,
                        'individual_positions':{a:found_a,b:found_b},
                        'traditional_pattern_verified':False,'event_formed':None,
                        'status':'仅验证同宫位置；未核验流派格局名称、四化、煞忌与亮度条件'})
    return {'rules':results,'observed_count':sum(r['observed'] for r in results),
            'traditional_pattern_verified':False,
            'notes':['同宫双星只是一项必要位置条件，不代表传统格局成立。',
                     '没有将三合两宫或对宫的两颗星误认为同宫。',
                     '未校准的庙旺利陷与流派条件不参与结论。']}


def build_sanhe_pattern_candidates(contributions, pair_audit):
    """位置层面的候选审计：同宫、会照与缺项分开，绝不自动断格局。"""
    positions={}
    for item in contributions:
        for star in set(item['stars']):
            positions.setdefault(star, []).append({'zhi':item['zhi'],'role':item['role']})
    results=[]
    for rule in SANHE_PAIR_RULES:
        a,b=rule['stars']
        pa=positions.get(a,[]);pb=positions.get(b,[])
        same=sorted(set(x['zhi'] for x in pa)&set(x['zhi'] for x in pb))
        if same: state='同宫位置成立'
        elif pa and pb: state='三方四正范围内分宫出现（非同宫）'
        else: state='星曜位置条件不足'
        results.append({'id':rule['id'],'label':rule['label'],'state':state,
                        'stars':[a,b],'positions':{a:pa,b:pb},
                        'same_palace_branches':same,
                        'missing_stars':[st for st in (a,b) if st not in positions],
                        'checks':[
                            {'name':'两星均在三方四正范围','met':bool(pa and pb)},
                            {'name':'两星同一物理宫位','met':bool(same)},
                            {'name':'煞忌及亮度格局判据','met':None},
                            {'name':'流派传统格局定义核验','met':None}],
                        'traditional_pattern_verified':False,'event_formed':None})
    return {'candidates':results,'status':'仅检查星曜位置；未实现传统格局成立或吉凶判据'}


SANHE_SHA_STARS = ("擎羊", "陀罗", "火星", "铃星", "地空", "地劫")

def build_sanhe_pattern_context(contributions, candidates):
    """Record physical co-location of sha, optional four-transform metadata and brightness.

    No unverified traditional rule is applied and missing data is never treated as absence.
    """
    by_zhi={c['zhi']:c for c in contributions}
    observations=[]
    for candidate in candidates['candidates']:
        witnesses=[]
        for zhi in candidate['same_palace_branches']:
            c=by_zhi[zhi]
            stars=set(c['stars'])
            sha=[x for x in SANHE_SHA_STARS if x in stars]
            brightness=c.get('brightness') or {}
            grades={star:brightness[star] for star in candidate['stars'] if star in brightness and brightness[star] not in (None,'')}
            missing=[star for star in candidate['stars'] if star not in grades]
            witnesses.append({'zhi':zhi,'role':c['role'],'sha_same_palace':sha,
                'sha_observed':bool(sha),'brightness_observed':grades,
                'brightness_missing':missing,
                'transformation_verified':False,
                'status':'同宫煞星为观察记录；亮度和四化未经过格局规则校准'})
        observations.append({'id':candidate['id'],'label':candidate['label'],
            'position_state':candidate['state'],'witnesses':witnesses,
            'sha_rule_met':None,'brightness_rule_met':None,'four_transformation_rule_met':None,
            'traditional_pattern_verified':False,'event_formed':None,
            'unresolved':['煞星影响的流派规则','亮度等级来源与格局门槛','四化配合与独立限年规则','传统格局完整成立判据']})
    return {'observations':observations,
            'status':'只记录同宫煞星与已提供的亮度；未验证煞忌、四化或格局成败'}


def build_sanhe_analysis(chart):
    """三合派独立证据：本宫、三合两宫、对宫及星曜结构，不使用飞化事件判据。"""
    palaces=chart.get("palaces") or {}
    if len(palaces)!=12 or any(z not in palaces for z in DI_ZHI):
        raise ValueError("需要十二宫完整排盘数据")
    primary=set(MAJOR_STARS)
    records=[]
    for zhi in DI_ZHI:
        p=palaces[zhi];i=DI_ZHI.index(zhi)
        related=[DI_ZHI[(i+offset)%12] for offset in (0,4,8,6)]
        contributions=[]
        for idx,branch in enumerate(related):
            q=palaces[branch]
            stars=list(dict.fromkeys((q.get("mainStars") or [])+(q.get("minorStars") or [])))
            contributions.append({"role":["本宫","三合一","三合二","对宫"][idx],
                "zhi":branch,"palace":q.get("name"),"stars":stars,
                "primary_stars":[st for st in stars if st in primary],
                "brightness":q.get("star_brightness") or {}})
        star_evidence=build_sanhe_star_evidence(contributions)
        pair_audit=build_sanhe_pair_audit(contributions)
        pattern_candidates=build_sanhe_pattern_candidates(contributions,pair_audit)
        registry_audit=audit_rules(contributions)
        records.append({"zhi":zhi,"palace":p.get("name"),"three_harmony_four_positions":contributions,
            "star_evidence":star_evidence,
            "conditional_observations":build_sanhe_conditional_observations(contributions,star_evidence),
            "pair_audit":pair_audit,
            "pattern_candidates":pattern_candidates,
            "pattern_context":build_sanhe_pattern_context(contributions,pattern_candidates),
            "rule_registry_audit":registry_audit,
            "rule_gate_matrix":audit_gate_matrix(registry_audit,contributions),
            "status":"星曜证据结构已生成；格局成败、庙旺利陷权重尚未核验"})
    return {"school":"三合派","version":"0.8.60-evidence-gates","palaces":records,
            "limitations":["仅提供三方四正与星曜组合的可追溯证据，尚未自动断定格局或事件。",
                           "庙旺利陷存在未核验数据，报告只展示已提供的等级。"]}


def build_palace_evidence(edges, palaces, decade_zhi, annual_zhi):
    """十二物理宫位的独立证据摘要，附各层宫名、星曜及来源；跨层复用路径只算一次。"""
    result=[]
    for zhi in DI_ZHI:
        p=palaces[zhi]
        incoming=[e for e in edges if e['target']==zhi]
        outgoing=[e for e in edges if e['source']==zhi]
        def unique(items):
            return list({(e['source'],e['target'],e['gan'],e['star'],e['hua']):{
                'source':e['source'],'target':e['target'],'gan':e['gan'],
                'star':e['star'],'hua':e['hua'],'self':e['self']}
                for e in items}.values())
        result.append({'zhi':zhi,'natal_palace':p.get('name'),
           'decade_palace':layer_name(decade_zhi,zhi) if decade_zhi else None,
           'annual_palace':layer_name(annual_zhi,zhi),
           'main_stars':p.get('mainStars') or [],'minor_stars':p.get('minorStars') or [],
           'incoming':unique(incoming),'outgoing':unique(outgoing),
           'reused_layer_paths':len(incoming)-len(unique(incoming)),
           'status':'宫位四化证据（不是事件结论）'})
    return result


def build_event_conditions(edges, palaces):
    """条件审计：只认可不同物理来源的禄/忌组合，不把跨层复用当作应事。"""
    unique={(e['source'],e['target'],e['gan'],e['star'],e['hua']):e for e in edges}
    by_target=defaultdict(list)
    for e in unique.values():by_target[e['target']].append(e)
    records=[]
    for zhi,items in by_target.items():
        hua_set={e['hua'] for e in items}
        sources={e['source'] for e in items}
        self_paths=[e for e in items if e['self']]
        opposite=DI_ZHI[(DI_ZHI.index(zhi)+6)%12]
        opposing=[e for e in items if e['source']==opposite]
        pairs=[]
        for kind,a,b in [('禄忌','化禄','化忌'),('权忌','化权','化忌'),('科忌','化科','化忌')]:
            found=[(x,y) for x in items for y in items if x['hua']==a and y['hua']==b and x['source']!=y['source']]
            if found:
                x,y=found[0]
                pairs.append({'kind':kind,'paths':[{'source':e['source'],'star':e['star'],'hua':e['hua']} for e in (x,y)]})
        if not pairs and not self_paths and not opposing:continue
        records.append({'zhi':zhi,'palace':palaces[zhi].get('name'),
          'distinct_sources':len(sources),'four_types':sorted(hua_set),
          'combinations':pairs,'self_count':len(self_paths),'opposite_count':len(opposing),
          'stage':'结构条件已检出，事件成立未判定',
          'required':['确认限年宫干起法','按选定飞星流派核对飞伏/冲照规则',
                      '检验相关星系与三方四正','验证时间边界与现实应事条件']})
    return records


def build_event_readiness(analysis, palaces):
    """逐议题解释可见路径与不能确认的关键前提。绝不把层名重贴当独立验证。"""
    edges=analysis.get('edges',[])
    by_topic=[]
    for topic, names in ISSUES.items():
        matching=[e for e in edges if any(p in names for p in (
            e.get('source_natal'),e.get('target_natal'),e.get('source_layer_palace'),
            e.get('target_decade'),e.get('target_annual')))]
        physical={}
        for e in matching:
            key=(e['source'],e['target'],e['gan'],e['star'],e['hua'])
            physical.setdefault(key,e)
        selected=list(physical.values())
        by_palace=defaultdict(list)
        for e in selected:by_palace[e['target']].append(e)
        evidence=[]
        for zhi, paths in by_palace.items():
            if len(evidence)>=12:break
            p=palaces[zhi]
            stars=list(dict.fromkeys((p.get('mainStars') or [])+(p.get('minorStars') or [])))
            types={e['hua'] for e in paths}
            evidence.append({
                'zhi':zhi,'palace':p.get('name'),'stars':stars,
                'transformations':sorted(types),
                'sources':sorted({e['source'] for e in paths}),
                'paths':[{'source':e['source'],'star':e['star'],'hua':e['hua'],
                          'gan':e['gan']} for e in paths[:8]],
                'has_self':any(e['source']==zhi for e in paths),
                'has_opposition':any((DI_ZHI.index(e['source'])-DI_ZHI.index(zhi))%12==6 for e in paths),
                'has_lu_ji':'化禄' in types and '化忌' in types,
                'has_quan_ji':'化权' in types and '化忌' in types,
                'has_ke_ji':'化科' in types and '化忌' in types,
            })
        by_topic.append({
            'topic':topic,'status':'证据可追溯／事件未获验证',
            'physical_path_count':len(selected),
            'palace_evidence':evidence,
            'gate_checks':[
                {'name':'本命物理飞化证据','passed':bool(selected),
                 'note':'只证明排盘数据内存在可追溯路径，不证明事件'},
                {'name':'大限独立飞化规则','passed':False,
                 'note':'目前沿用本命宫干重贴层名，不能视为独立印证'},
                {'name':'流年独立飞化与年界','passed':False,
                 'note':'流年宫干及换年边界未校准'},
                {'name':'四化飞伏派别判据','passed':False,
                 'note':'伏象候选、冲照、自化尚无已核准的派别规则'},
                {'name':'星曜组合与应期核验','passed':False,
                 'note':'星系性质及具体应期条件尚未逐项验证'},
            ],
            'conclusion':'当前只可提出议题线索，不能断定事件性质、是否发生或应期。'
        })
    return by_topic


def build_palace_narratives(edges, palaces, decade_zhi=None, annual_zhi=None, annual_four=None):
    """Traceable descriptions of physical transformations, not predictive claims.

    Count only natal physical paths; layer aliases are display labels, not
    independent corroboration. Annual stem paths are separate rule-family data.
    """
    annual_four=annual_four or []
    natal={}
    for e in edges:
        if e.get('layer')!='本命':
            continue
        key=(e.get('source'),e.get('target'),e.get('gan'),e.get('star'),e.get('hua'))
        natal[key]=e
    cards=[]
    for zhi in DI_ZHI:
        palace=palaces[zhi]
        outgoing=sorted((e for e in natal.values() if e['source']==zhi),key=lambda e:(e['target'],e['hua'],e['star']))
        incoming=sorted((e for e in natal.values() if e['target']==zhi),key=lambda e:(e['source'],e['hua'],e['star']))
        yearly=sorted((e for e in annual_four if e['target']==zhi),key=lambda e:(e['hua'],e['star']))
        def describe(e, direction):
            source=e['source']; target=e['target']
            return {'source':source,'target':target,'star':e['star'],'hua':e['hua'],
                    'gan':e.get('gan'),'direction':direction,
                    'source_natal':palaces[source].get('name'),
                    'target_natal':palaces[target].get('name'),
                    'self_path':source==target,
                    'opposite_path':(DI_ZHI.index(source)-DI_ZHI.index(target))%12==6,
                    'description':f"{palaces[source].get('name') or source}（{source}，{e.get('gan') or '未载'}干）{e['hua']}：{e['star']}落{palaces[target].get('name') or target}（{target}）"}
        stars=list(dict.fromkeys((palace.get('mainStars') or [])+(palace.get('minorStars') or [])))
        cards.append({'zhi':zhi,'natal_palace':palace.get('name'),
          'decade_palace':layer_name(decade_zhi,zhi) if decade_zhi else None,
          'annual_palace':layer_name(annual_zhi,zhi) if annual_zhi else None,
          'stars':stars,'outgoing':[describe(e,'飞出') for e in outgoing],
          'incoming':[describe(e,'飞入') for e in incoming],
          'annual_stem':[{'gan':e['gan'],'hua':e['hua'],'star':e['star'],
                           'target':zhi} for e in yearly],
          'status':'物理宫干路径证据，非事件成立',
          'note':'大限及流年宫名为同一物理宫位叠宫映射，不代表独立宫干飞化。'})
    return cards

# Independent school-specific reading summaries for the high-level analysis API.
# This is an interpretive rule-based reading, not an assertion of real-world events.
def build_school_readings(chart, school, analysis_result):
    palaces = chart.get("palaces") or {}
    records = []
    if school == "sanhe":
        for item in analysis_result.get("palaces", []):
            parts = item.get("three_harmony_four_positions") or []
            local = parts[0] if parts else {}
            related = parts[1:]
            supportive = sorted({s for p in related for s in p.get("stars", []) if s in SANHE_STAR_GROUPS["六吉"]})
            stressful = sorted({s for p in related for s in p.get("stars", []) if s in SANHE_STAR_GROUPS["六煞"]})
            records.append({
                "palace": item.get("palace"), "zhi": item.get("zhi"), "school": "三合派",
                "focus": "本宫星曜、三方四正与吉煞会照",
                "observed": "本宫可见：" + ("、".join(local.get("stars") or []) or "暂无已排星曜") +
                    "；三方四正可见：" + ("、".join(sorted({s for p in related for s in p.get("stars", [])})) or "暂无已排星曜"),
                "favorable": "会照的辅助星曜：" + ("、".join(supportive) or "未观察到已核验吉曜"),
                "unfavorable": "会照的压力星曜：" + ("、".join(stressful) or "未观察到已核验煞曜"),
                "caveat": "星曜分布只支持条件式分析；格局和庙旺利陷尚未校准。"
            })
    else:
        for item in analysis_result.get("palace_narratives", []):
            incoming = item.get("incoming") or []
            outgoing = item.get("outgoing") or []
            records.append({
                "palace": item.get("natal_palace"), "zhi": item.get("zhi"), "school": "飞星派",
                "focus": "本宫四化飞入、飞出与来源去向",
                "observed": "飞入：" + ("；".join(x.get("description", "") for x in incoming[:5]) or "无已记录路径") +
                    "；飞出：" + ("；".join(x.get("description", "") for x in outgoing[:5]) or "无已记录路径"),
                "favorable": "可追溯的禄科飞入：" + str(sum("禄" in x.get("hua", "") or "科" in x.get("hua", "") for x in incoming)),
                "unfavorable": "可追溯的忌飞入：" + str(sum("忌" in x.get("hua", "") for x in incoming)),
                "caveat": "限年独立宫干规则尚未校准，飞化路径不等于事件成立或应期。"
            })
    return records
