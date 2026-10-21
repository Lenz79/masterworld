# -*- coding: utf-8 -*-
"""传统象意规则引擎（可追溯的条件式推演；非已验证的预测模型）。"""
GAN="甲乙丙丁戊己庚辛壬癸"
ZHI="子丑寅卯辰巳午未申酉戌亥"
ELEM=dict(zip(GAN,["木","木","火","火","土","土","金","金","水","水"]))
CLASH={"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥"}
CLASH.update({v:k for k,v in list(CLASH.items())})
COMBINE={"子":"丑","寅":"亥","卯":"戌","辰":"酉","巳":"申","午":"未"}
COMBINE.update({v:k for k,v in list(COMBINE.items())})
HARM={"子":"未","丑":"午","寅":"巳","卯":"辰","申":"亥","酉":"戌"}
HARM.update({v:k for k,v in list(HARM.items())})
NAMES={"career":"事业","wealth":"财运","health":"健康","marriage":"婚姻感情","social":"人际合作","accident":"出行安全","parents":"父母长辈","siblings":"兄弟姐妹","children":"子女","property":"田宅资产","inner_world":"心理与成长"}
DOMAIN={
"career":("岗位职责、升迁竞争、业务调整与工作转型","先辨清权责、绩效指标和合约条款；变动前准备替代方案","事业上的变化可能表现为调岗、合作结构调整或工作节奏改变"),
"wealth":("收入结构、支出安排、债务和投资风险","保留流动资金；签约或投资前独立核实资料，不以命理决定买卖","财务上的变化可能表现为现金流调整、额外开支或收益模式改变"),
"health":("生活节奏、劳逸安排和压力管理","维持作息；有症状应由医护人员评估，不能用命盘判断疾病","这类象意只提示留意压力和节奏，不代表会生病或发生意外"),
"marriage":("伴侣沟通、关系承诺和家庭角色","把财务、家务与双方期待说清楚；避免在情绪高点做决定","感情层面的变化可能表现为关系重新协商、生活安排或相处方式变化"),
"social":("同事朋友、合作关系及口舌争议","重要合作保留书面记录，明确边界与交付责任","人际变化可能表现为团队更替、新合作或既有关系重新磨合"),
"accident":("交通、出差、搬迁与行程安排","遵守交通规则，留出行程缓冲；风险判断以实际环境为准","变动象意不等于必有交通事故"),
"parents":("长辈沟通、家庭分工及照护责任","重大家庭事项及早协调，避免把意见差异当作关系破裂","家庭议题可能转向责任分配与时间安排"),
"siblings":("手足协作、资源分配和边界","涉及金钱与共同责任先谈清规则","手足间可能出现协作或分工调整"),
"children":("亲子互动、教育计划和家庭期待","尊重个体差异，重要教育决定依据实际需求","亲子议题可能侧重陪伴、教育或责任安排"),
"property":("居住、装修、搬迁及不动产规划","先核实产权、负债、现金流及维修预算","田宅方面可能出现居住安排或资产配置的讨论"),
"inner_world":("压力调适、学习转型及个人目标","以可执行的小目标检验计划，必要时寻求专业支持","个人发展可能侧重重新安排优先次序")}
STAR_CONTEXT={
"正官":("规章、职位、考核和责任","按制度争取认可，注意合规与承诺"),
"七杀":("竞争、压力、挑战和决断","先评估承受力，不宜以强硬方式处理冲突"),
"正印":("学习、资格、文书和支持","适合整理资质与长期规划，避免依赖他人"),
"偏印":("研究、转型、非惯常方案","先验证想法再投入资源"),
"正财":("稳定收入、预算和现实责任","重视收入质量与现金流"),
"偏财":("项目收入、商业机会与资金流动","防范杠杆与未经核实的高回报承诺"),
"食神":("成果输出、技能发挥与生活节奏","持续交付成果，避免松懈"),
"伤官":("表达、创新、制度摩擦","提出改进意见时兼顾关系和程序"),
"比肩":("自主性、同辈协作和竞争","明确利益边界，减少重复投入"),
"劫财":("资源分配、同业竞争与合伙","慎重担保与借贷，核实合作责任")}
def star(day_gan, target):
    order=["木","火","土","金","水"]
    d=order.index(ELEM[day_gan]); t=order.index(ELEM[target]); same=(GAN.index(day_gan)%2)==(GAN.index(target)%2)
    if d==t:return "比肩" if same else "劫财"
    if (d+1)%5==t:return "食神" if same else "伤官"
    if (t+1)%5==d:return "偏印" if same else "正印"
    if (d+2)%5==t:return "偏财" if same else "正财"
    return "七杀" if same else "正官"
def relations(natal, gz, label):
    z=gz[1]; out=[]
    for p, name in (("year","年柱"),("month","月柱"),("day","日支（夫妻宫）"),("hour","时柱")):
        n=natal[p][1]
        if CLASH.get(z)==n:out.append(("冲",f"{label}{gz}冲原局{name}{n}",p))
        elif COMBINE.get(z)==n:out.append(("合",f"{label}{gz}与原局{name}{n}六合",p))
        elif HARM.get(z)==n:out.append(("害",f"{label}{gz}与原局{name}{n}相害",p))
    return out
def period_context(natal, dayun=None, year=None):
    lines=[]
    if dayun:lines += [r[1] for r in relations(natal,dayun,"大运")]
    if year:lines += [r[1] for r in relations(natal,year,"流年")]
    if dayun and year:
        if CLASH.get(dayun[1])==year[1]:lines.append(f"流年{year}与大运{dayun}地支相冲（岁运冲）")
        elif COMBINE.get(dayun[1])==year[1]:lines.append(f"流年{year}与大运{dayun}地支六合（岁运合）")
    return "；".join(lines) if lines else "本期未触发本模块已实现的六冲、六合、六害；不代表全盘没有其他刑破或吉凶条件"
def build_report(domain,natal,period,dayun=None,year=None):
    title=NAMES[domain]; focus,action,example=DOMAIN[domain]
    active=year or dayun
    label=f"{year}流年（{dayun}大运内）" if year else (f"{dayun}大运" if dayun else "原局")
    triggers=[]
    if dayun:triggers+=relations(natal,dayun,"大运")
    if year:triggers+=relations(natal,year,"流年")
    if dayun and year:
        if CLASH.get(dayun[1])==year[1]:triggers.append(("冲",f"{year}流年冲{dayun}大运", "period"))
        elif COMBINE.get(dayun[1])==year[1]:triggers.append(("合",f"{year}流年合{dayun}大运", "period"))
    relevant={"career":{"month","year","period"},"wealth":{"month","year","period"},"health":{"day","hour","period"},"marriage":{"day","period"},"social":{"year","month","period"},"accident":{"year","hour","period"},"parents":{"year","month"},"siblings":{"year","month"},"children":{"hour","day"},"property":{"month","day","period"},"inner_world":{"day","hour","period"}}[domain]
    selected=[r for r in triggers if r[2] in relevant]
    positives=sum(r[0]=="合" for r in selected); negatives=sum(r[0] in ("冲","害") for r in selected)
    if negatives>positives: tendency="变动与摩擦信号较突出，宜谨慎处理"
    elif positives>negatives: tendency="协调与整合信号较突出，可积极筹划"
    else:tendency="吉凶未能凭现有规则明确区分，应以实际条件判断"
    if active:
        role=star(natal['day'][0],active[0]); meaning,guide=STAR_CONTEXT[role]
        base=f"{label}，传统十神象意偏向{meaning}。在{title}方面，主要观察{focus}。{guide}。"
    else:
        base=f"原局{natal['year']}年、{natal['month']}月、{natal['day']}日、{natal['hour']}时；在{title}方面应结合{focus}观察长期倾向。"
    details="；".join(r[1] for r in selected)
    if not details:details="与本主题直接关联的已实现冲合害规则未见明显触发，不能据此断言必吉或必凶"
    text=(f"【{tendency}】{base}本期依据：{details}。"
          f"情境推演：{example}。如果现实中已有相关计划或矛盾，可能更需要关注上述环节；若无对应事实，不应硬套事件。"
          f"论断边界：这只是传统八字局部规则推演，未纳入经校验的旺衰、调候、格局及全部刑破组合，不能预测必然发生的具体事件。")
    return {"title":title,"text":text,"tips":f"重点建议：{action}。", "strengths":["留意与当期干支有关的实际机会"],"weaknesses":["避免把象意当作必然事件"],"pros":["主动规划"],"cons":["防止过度推断"],"evidence":[r[1] for r in selected],"period":label}
def monthly_context(natal,dayun,year,month_gz,month):
    role=star(natal['day'][0],month_gz[0]);meaning,guide=STAR_CONTEXT[role]
    cues=relations(natal,month_gz,"月柱")
    if CLASH.get(month_gz[1])==year[1]:cues.append(("冲",f"月柱{month_gz}冲流年{year}","year"))
    if CLASH.get(month_gz[1])==dayun[1]:cues.append(("冲",f"月柱{month_gz}冲大运{dayun}","period"))
    cue="；".join(x[1] for x in cues) if cues else "未触发已实现的六冲、六合、六害"
    return f"公历{month}月中旬节气月柱{month_gz}，侧重{meaning}。关系提示：{cue}。{guide}。月初及节气交接需按具体日期重新取柱；不可据此断言必有事件。"
