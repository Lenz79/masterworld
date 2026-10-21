# -*- coding: utf-8 -*-
"""
八字核心计算与报告生成引擎 (Bazi Engine)
全方位终极稳健版：强化时间格式解析与多级字段容错，彻底杜绝前端 map 报错
"""
from lunar_python import Solar, Lunar

GAN_ELEMENTS = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
ZHI_ELEMENTS = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}
GAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

LIU_CHONG = {"子":"午", "午":"子", "丑":"未", "未":"丑", "寅":"申", "申":"寅", "卯":"酉", "酉":"卯", "辰":"戌", "戌":"辰", "巳":"亥", "亥":"巳"}
GAN_HE = {"甲":"己", "己":"甲", "乙":"庚", "庚":"乙", "丙":"辛", "辛":"丙", "丁":"壬", "壬":"丁", "戊":"癸", "癸":"戊"}
ZHI_HE = {"子":"丑", "丑":"子", "寅":"亥", "亥":"寅", "卯":"戌", "戌":"卯", "辰":"酉", "酉":"辰", "巳":"申", "申":"巳", "午":"未", "未":"午"}

SHISHEN_DATABASE = {
    "正官": {"meaning": "代表规范、自律、名誉。", "pros": ["遵纪守法", "处事公道"], "cons": ["固执保守"]},
    "七杀": {"meaning": "代表魄力、竞争、开拓精神。", "pros": ["果断有魄力"], "cons": ["脾气急躁"]},
    "正印": {"meaning": "代表学识、贵人。", "pros": ["心地善良"], "cons": ["依赖性强"]},
    "偏印": {"meaning": "代表灵感、玄学直觉。", "pros": ["悟性极高"], "cons": ["孤傲多疑"]},
    "正财": {"meaning": "代表稳健正财。", "pros": ["踏实务实"], "cons": ["过度计较"]},
    "偏财": {"meaning": "代表横财、投资。", "pros": ["交际广泛"], "cons": ["浮躁投机"]},
    "食神": {"meaning": "代表福气、口福。", "pros": ["温和优雅"], "cons": ["贪图安逸"]},
    "伤官": {"meaning": "代表才华横溢、高傲叛逆。", "pros": ["聪明绝顶"], "cons": ["高傲傲物"]},
    "比肩": {"meaning": "代表自我、独立。", "pros": ["独立自主"], "cons": ["固执己见"]},
    "劫财": {"meaning": "代表拼搏、投机。", "pros": ["拼搏心强"], "cons": ["冲动破财"]}
}

ELEMENT_DB = {
    "木": {"directions": "东方与东南方", "industries": ["文化教育", "出版传媒"]},
    "火": {"directions": "正南方", "industries": ["高新技术", "人工智能"]},
    "土": {"directions": "东北方与西南方", "industries": ["房地产", "建筑工程"]},
    "金": {"directions": "西方与西北方", "industries": ["金融证券", "五金珠宝"]},
    "水": {"directions": "正北方", "industries": ["国际贸易", "航运物流"]}
}

SPOUSE_ZHI_DB = {
    "子": {"sp_type": "身材匀称修长，聪明灵动。", "relation": "沟通注重精神共鸣。"},
    "午": {"sp_type": "身材高挑，性格开朗大方。", "relation": "感情浓烈真挚。"},
    "卯": {"sp_type": "气质温婉秀丽，为人重情义。", "relation": "相处如沐春风。"},
    "酉": {"sp_type": "五官精致，作风干练。", "relation": "处事讲求原则效率。"},
    "寅": {"sp_type": "身材挺拔，威严果断。", "relation": "事业助力大。"},
    "申": {"sp_type": "敏捷精明，适应力极强。", "relation": "生活充满新鲜感。"},
    "巳": {"sp_type": "外表沉稳，思维敏捷。", "relation": "互相扶持共同成长。"},
    "亥": {"sp_type": "体态丰润，待人随和。", "relation": "家庭氛围温馨。"},
    "辰": {"sp_type": "气场厚重，踏实稳重。", "relation": "互相作为强大后盾。"},
    "戌": {"sp_type": "忠诚可靠，重信守诺。", "relation": "感情稳如磐石。"},
    "丑": {"sp_type": "低调勤奋，吃苦耐劳。", "relation": "陪伴最为长情。"},
    "未": {"sp_type": "温和有礼，富有责任感。", "relation": "关怀备至。"}
}

def calc_tai_yuan(month_gan, month_zhi):
    g_idx = GAN_LIST.index(month_gan)
    z_idx = ZHI_LIST.index(month_zhi)
    return GAN_LIST[(g_idx + 1) % 10], ZHI_LIST[(z_idx + 3) % 12]

def calc_tai_xi(day_gan, day_zhi):
    return GAN_HE.get(day_gan, "甲"), ZHI_HE.get(day_zhi, "子")

def calc_ming_gong(year_gan, month_zhi, time_zhi):
    m_idx = ZHI_LIST.index(month_zhi) + 1
    t_idx = ZHI_LIST.index(time_zhi) + 1
    mg_zhi_idx = (26 - m_idx - t_idx) % 12
    if mg_zhi_idx == 0: mg_zhi_idx = 12
    mg_zhi = ZHI_LIST[mg_zhi_idx - 1]
    y_gan_idx = GAN_LIST.index(year_gan)
    start_gan_idx = ((y_gan_idx % 5) * 2 + 2) % 10
    mg_offset = (ZHI_LIST.index(mg_zhi) - 2) % 12
    return GAN_LIST[(start_gan_idx + mg_offset) % 10], mg_zhi

def calc_ming_ge(day_gan, month_star, month_zhi):
    if month_star in ["比肩", "劫财"]:
        yangren_map = {"甲":"卯", "乙":"辰", "丙":"午", "丁":"未", "戊":"午", "己":"未", "庚":"酉", "辛":"戌", "壬":"子", "癸":"丑"}
        return "羊刃格" if month_zhi == yangren_map.get(day_gan) else "建禄格"
    return f"{month_star}格"

def calc_yong_xi(day_gan_elem, is_strong):
    sheng_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    ke_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
    elements = ["木", "火", "土", "金", "水"]
    if is_strong:
        yong = ke_map[day_gan_elem]
        idx = elements.index(yong)
        xi = elements[(idx + 1) % 5]
        xian = elements[(idx + 2) % 5]
        chou = elements[(idx + 3) % 5]
        ji = sheng_map[day_gan_elem]
    else:
        yong = sheng_map[day_gan_elem]
        idx = elements.index(yong)
        xi = elements[(idx + 1) % 5]
        xian = elements[(idx + 2) % 5]
        chou = elements[(idx + 3) % 5]
        ji = ke_map[day_gan_elem]
    return {"yong": yong, "xi": xi, "xian": xian, "chou": chou, "ji": ji, "str_repr": f"用:{yong} | 喜:{xi}"}


# 月令五行旺相休囚死：按月支所属季节的五行循环推算（不等同于命局喜用神）。
SEASON_MASTER = {"寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土",
                 "申":"金","酉":"金","戌":"土","亥":"水","子":"水","丑":"土"}
GENERATES = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
CONTROLS = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
GENERATED_BY = {v:k for k,v in GENERATES.items()}
CONTROLLED_BY = {v:k for k,v in CONTROLS.items()}

def calc_wang_xiang(month_zhi):
    """传统月令五行的旺相休囚死，土月按土旺处理。"""
    wang = SEASON_MASTER[month_zhi]
    return {"旺":wang, "相":GENERATES[wang], "休":GENERATED_BY[wang],
            "囚":CONTROLS[wang], "死":CONTROLLED_BY[wang]}

def estimate_element_balance(pillars, month_zhi):
    """透明的显示用简化权重，不冒充完整通根、藏干、调候及格局判定。"""
    scores={e:0.0 for e in ("木","火","土","金","水")}
    for p in pillars:
        scores[p["gan_elem"]]+=1.0
        scores[p["zhi_elem"]]+=1.0
    # 月令季节只作为附加权重，避免伪造精确学术分数。
    scores[SEASON_MASTER[month_zhi]]+=1.0
    return scores

def estimate_five_roles(day_element, scores):
    """供界面使用的五行倾向参考；不能替代传统格局、调候、病药取用。"""
    supporting={day_element, GENERATED_BY[day_element]}
    support=sum(scores[e] for e in supporting)
    strong=support >= sum(scores.values()) / 2
    if strong:
        order=[CONTROLS[day_element], GENERATES[day_element],
               CONTROLLED_BY[day_element], day_element, GENERATED_BY[day_element]]
    else:
        order=[GENERATED_BY[day_element], day_element,
               CONTROLS[day_element], GENERATES[day_element], CONTROLLED_BY[day_element]]
    return dict(zip(("用","喜","闲","仇","忌"),order)),strong,support

def get_shishen(day_gan, target_gan):
    if not day_gan or not target_gan or day_gan not in GAN_ELEMENTS or target_gan not in GAN_ELEMENTS: return "比肩"
    elements = ["木", "火", "土", "金", "水"]
    d_idx, t_idx = elements.index(GAN_ELEMENTS[day_gan]), elements.index(GAN_ELEMENTS[target_gan])
    is_same_yin_yang = (day_gan in "甲丙戊庚壬") == (target_gan in "甲丙戊庚壬")
    if d_idx == t_idx: return "比肩" if is_same_yin_yang else "劫财"
    elif (d_idx + 1) % 5 == t_idx: return "食神" if is_same_yin_yang else "伤官"
    elif (t_idx + 1) % 5 == d_idx: return "偏印" if is_same_yin_yang else "正印"
    elif (d_idx + 2) % 5 == t_idx: return "偏财" if is_same_yin_yang else "正财"
    elif (t_idx + 2) % 5 == d_idx: return "七杀" if is_same_yin_yang else "正官"
    return "比肩"

def get_kongwang(gan, zhi):
    g_idx = "甲乙丙丁戊己庚辛壬癸".index(gan) if gan in "甲乙丙丁戊己庚辛壬癸" else 0
    z_idx = "子丑寅卯辰巳午未申酉戌亥".index(zhi) if zhi in "子丑寅卯辰巳午未申酉戌亥" else 0
    diff = (z_idx - g_idx) % 12
    return {0: "戌亥", 10: "申酉", 8: "午未", 6: "辰巳", 4: "寅卯", 2: "子丑"}.get(diff, "辰巳")


# 报告推演辅助函数：只处理报告层，保留既有排盘接口和返回字段。
REPORT_TOPICS = {
    "marriage": ("婚姻感情", "伴侣沟通、关系承诺与相处边界", "重要关系宜明确双方期待，避免以猜测代替沟通"),
    "career": ("职业事业", "职责变化、专业能力与升迁机会", "优先建立可衡量成果，并保留重要沟通记录"),
    "wealth": ("财运投资", "收入结构、现金流与风险承担", "将日常储备与高风险资金分开，避免冲动决策"),
    "health": ("健康生活", "作息、压力调节与生活节律", "以规律睡眠和体检为主，身体不适应咨询医生"),
    "parents": ("父母缘份", "长辈关系、照顾责任与家庭沟通", "提早商量家庭分工，保持稳定联系"),
    "siblings": ("兄弟姐妹", "同辈互助、利益边界与家庭协作", "金钱与责任宜事先说清，减少误解"),
    "children": ("子女缘份", "下一代沟通、教育与陪伴", "尊重个人差异，避免以单一标准衡量亲子关系"),
    "accident": ("出行安全", "行程安排、分心风险与应变能力", "交通安全以现实路况和防护措施为准"),
    "social": ("交友人缘", "合作关系、信任建立与人事分寸", "合作先厘清角色和利益，再逐步扩大承诺"),
    "property": ("田宅不动产", "居住稳定、长期资产与家庭安排", "购置资产先核实负担能力、产权和现金流"),
    "inner_world": ("内心世界", "自我要求、情绪表达与长期目标", "保留休息与反思空间，避免长期压抑需求"),
}
STAR_CONTEXT = {
    "正官": "规则、责任与正式考核较突出", "七杀": "竞争、压力与需要果断应对的任务较突出",
    "正印": "学习、支持资源与长辈协助较突出", "偏印": "研究、独立思考与重新规划较突出",
    "正财": "稳定收入、预算与务实经营较突出", "偏财": "外部资源、交易机会与收益波动较突出",
    "食神": "表达、作品与生活节奏较突出", "伤官": "创新、沟通与挑战惯例较突出",
    "比肩": "自主决策、同辈关系与竞争较突出", "劫财": "资源分配、合作边界与财务纪律较突出",
}
ELEMENT_EFFECT = {"木":"成长、学习及长期规划", "火":"曝光、表达与行动效率", "土":"稳定、承诺与资源整合", "金":"制度、判断与执行", "水":"沟通、流动与适应"}

def _gz_for_year(y):
    return GAN_LIST[(y - 4) % 10] + ZHI_LIST[(y - 4) % 12]

def _month_gz(y, month_idx):
    # 五虎遁：甲己丙寅、乙庚戊寅、丙辛庚寅、丁壬壬寅、戊癸甲寅。
    start = {0:2, 5:2, 1:4, 6:4, 2:6, 7:6, 3:8, 8:8, 4:0, 9:0}[GAN_LIST.index(_gz_for_year(y)[0])]
    return GAN_LIST[(start + month_idx) % 10] + ZHI_LIST[(2 + month_idx) % 12]

# 分领域的命理解释模板：每个主题有独立观察指标，不共用一段泛用文案。
DOMAIN_RULES = {
 "marriage": ("夫妻宫（日支）与关系承诺", "日支代表传统命理中的夫妻宫；观察运支是否冲合日支，比单看财官更贴近关系议题。", "关系出现重要决定时，先谈清双方期待、责任分配及时间安排。"),
 "career": ("月柱事业环境与官杀印食", "月柱反映传统命理中的社会环境；官杀重规则与竞争，印星重学习支持，食伤重表达成果。", "把工作职责、成果指标及合作权限写清楚，避免职责不明。"),
 "wealth": ("财星、资金流动与守财", "正偏财主题涉及资源配置；比劫主题则提醒留意合伙与资源分摊，不能只凭财星断定收入。", "先检查现金流、债务与风险承受能力，再作投资决定。"),
 "health": ("五行偏重与生活节律", "传统五行仅能提供象征性观察，不可据此推断疾病；重点仍是作息、压力和日常负荷。", "以健康检查和专业医疗意见为准，勿用命理代替诊断。"),
 "parents": ("年柱、印星与长辈支持", "年柱与印星可作为传统命理观察家庭支持、长辈期望及照顾责任的线索。", "与家人提前沟通照顾安排及资源分工。"),
 "siblings": ("比劫、同辈协作与竞争", "比肩劫财象征同辈、合作与资源分配；是否互助仍需看具体家庭关系。", "涉及金钱、借贷或共同责任时，明确约定。"),
 "children": ("时柱、食伤与下一代", "时柱和食伤可作为传统命理观察子女、作品与传承议题的线索，并非生育结果预测。", "优先关注陪伴质量与沟通，不以命盘替代家庭选择。"),
 "accident": ("冲动支、出行变动与安全", "六冲通常象征节奏改变或外部干扰，不意味着一定发生事故。", "出行预留时间，遵守安全规范，不以命盘判断实际危险。"),
 "social": ("比劫食伤与交际合作", "比劫偏向同辈合作竞争，食伤偏向表达与对外连接；须结合原局及运势观察。", "先厘清合作边界与利益分配，再扩大合作。"),
 "property": ("田宅安排、土气与稳定性", "土的象征常与承载、长期安排相关；地支冲合也可作为居住变化的传统观察线索。", "房地产决定须核实产权、负担能力及现金流。"),
 "inner_world": ("日主、印比与自我调节", "日主与印比主题可用于反思自主性、支持需求和应对压力的习惯。", "建立休息、学习和沟通的固定节奏，避免自我要求过高。"),
}

def _report_item(topic, day_gan, day_zhi, month_zhi, active_gz, period, base_stars):
    title, _, _ = REPORT_TOPICS[topic]
    focus, interpretation, action = DOMAIN_RULES[topic]
    stem, branch = active_gz[0], active_gz[1]
    star = get_shishen(day_gan, stem)
    natal_star = base_stars.get(topic)
    # 根据主题选取有意义的原局对照支，而不是把同一段冲合解释复制给所有主题。
    reference_zhi = day_zhi if topic in ('marriage','children','inner_world','health') else month_zhi
    if LIU_CHONG.get(branch) == reference_zhi:
        relation = f"{active_gz}的地支{branch}冲原局{reference_zhi}，传统上提示该领域的安排可能出现调整；宜核对现实条件。"
        signal = "调整期"
    elif ZHI_HE.get(branch) == reference_zhi:
        relation = f"{active_gz}的地支{branch}与原局{reference_zhi}六合，传统上侧重协商、联结与资源协调。"
        signal = "协调期"
    else:
        relation = f"运支{branch}与所观察的原局{reference_zhi}没有直接六合或六冲，不能据此断言重大事件。"
        signal = "观察期"
    # 每一领域均有独立论述，并保留传统十神及四柱依据。
    intro = f"【{period}·{title}】观察重点：{focus}。命主日柱{day_gan}{day_zhi}、月令{month_zhi}；本期{active_gz}天干{stem}对日主为{star}。"
    natal = f"原局相关十神为{natal_star}，须结合整盘强弱与刑冲合害再定轻重。" if natal_star else "本项需结合年、月、日、时四柱综合观察，不能只凭一柱断吉凶。"
    star_explain = f"{star}在此阶段对应的象征主题为{STAR_CONTEXT[star]}。"
    text = intro + interpretation + natal + star_explain + relation + f"综合来看属于{signal}的命理提示，不构成确定的事件预言。"
    return {"title":title,"text":text,"tips":"建议："+action,
            "strengths":[f"可借{star}主题重新梳理{focus}"],
            "weaknesses":[f"注意{focus}的现实条件与个人差异"],
            "pros":[action],"cons":["不可仅凭八字判断重大决定"]}

def _month_summary(day_gan, natal_day_zhi, month_gz, year_gz, month_name):
    star = get_shishen(day_gan, month_gz[0])
    relation = "月支冲动日支，关系与行程宜预留弹性。" if LIU_CHONG.get(month_gz[1]) == natal_day_zhi else ("月支与日支相合，适合讨论合作与承诺。" if ZHI_HE.get(month_gz[1]) == natal_day_zhi else "本月重点是把计划落实到可执行步骤。")
    return f"{month_name}（{month_gz}）以{star}为主要观察线索，{STAR_CONTEXT[star]}。{relation}与{year_gz}流年合看，工作、财务和人际决定仍应以现实证据为准。"

class BaziEngine:
    @staticmethod
    def calculate(req_data):
        name = req_data.get('name', '小叶')
        gender = req_data.get('gender', '男')
        year = int(req_data.get('year', 1988))
        month = int(req_data.get('month', 11))
        day = int(req_data.get('day', 12))
        
        # 稳健解析时辰参数（支持 1345, 17, 13.75 等格式）
        raw_hour = req_data.get('hour', 1345)
        try:
            val = float(raw_hour)
            if val > 23:
                s_val = str(int(val))
                if len(s_val) == 3:
                    h_int, m_int = int(s_val[0]), int(s_val[1:])
                elif len(s_val) == 4:
                    h_int, m_int = int(s_val[:2]), int(s_val[2:])
                else:
                    h_int, m_int = 13, 45
            else:
                h_int = int(val)
                m_int = int(round((val - h_int) * 60))
        except Exception:
            h_int, m_int = 13, 45

        if h_int > 23: h_int = 23
        if m_int > 59: m_int = 59

        solar = Solar.fromYmdHms(year, month, day, h_int, m_int, 0)
        lunar = solar.getLunar()
        eight_char = lunar.getEightChar()
        eight_char.setSect(1)

        day_gan = eight_char.getDayGan()
        day_zhi = eight_char.getDayZhi()
        birth_year_gan = eight_char.getYearGan()
        birth_year_zhi = eight_char.getYearZhi()
        month_gan = eight_char.getMonthGan()
        month_zhi = eight_char.getMonthZhi()
        time_gan = eight_char.getTimeGan()
        time_zhi = eight_char.getTimeZhi()

        def build_cangan(zhi_char):
            try:
                if zhi_char == birth_year_zhi: hides = list(eight_char.getYearHideGan())
                elif zhi_char == month_zhi: hides = list(eight_char.getMonthHideGan())
                elif zhi_char == day_zhi: hides = list(eight_char.getDayHideGan())
                else: hides = list(eight_char.getTimeHideGan())
            except Exception: hides = ["甲"]
            return [{"gan": hg, "star": get_shishen(day_gan, hg)} for hg in hides]

        year_p = {"shishen": get_shishen(day_gan, birth_year_gan), "gan": birth_year_gan, "gan_elem": GAN_ELEMENTS.get(birth_year_gan, "木"), "zhi": birth_year_zhi, "zhi_elem": ZHI_ELEMENTS.get(birth_year_zhi, "木"), "cangan_details": build_cangan(birth_year_zhi), "yun": "冠带", "shensha": ["羊刃"], "nayin": eight_char.getYearNaYin()}
        month_p = {"shishen": get_shishen(day_gan, month_gan), "gan": month_gan, "gan_elem": GAN_ELEMENTS.get(month_gan, "金"), "zhi": month_zhi, "zhi_elem": ZHI_ELEMENTS.get(month_zhi, "火"), "cangan_details": build_cangan(month_zhi), "yun": "临官", "shensha": ["禄神"], "nayin": eight_char.getMonthNaYin()}
        day_p = {"shishen": "命主", "gan": day_gan, "gan_elem": GAN_ELEMENTS.get(day_gan, "土"), "zhi": day_zhi, "zhi_elem": ZHI_ELEMENTS.get(day_zhi, "水"), "cangan_details": build_cangan(day_zhi), "yun": "胎", "shensha": ["天德"], "nayin": eight_char.getDayNaYin()}
        hour_p = {"shishen": get_shishen(day_gan, time_gan), "gan": time_gan, "gan_elem": GAN_ELEMENTS.get(time_gan, "金"), "zhi": time_zhi, "zhi_elem": ZHI_ELEMENTS.get(time_zhi, "土"), "cangan_details": build_cangan(time_zhi), "yun": "死", "shensha": ["亡神"], "nayin": eight_char.getTimeNaYin()}

        natal_stars = {"career":month_p["shishen"], "wealth":year_p["shishen"], "marriage":hour_p["shishen"],
                       "parents":year_p["shishen"], "siblings":month_p["shishen"], "children":hour_p["shishen"],
                       "inner_world":month_p["shishen"], "social":year_p["shishen"]}
        counts = {e: 0 for e in ("金", "木", "水", "火", "土")}
        for pp in (year_p, month_p, day_p, hour_p):
            counts[pp["gan_elem"]] += 1
            counts[pp["zhi_elem"]] += 1
        scores = estimate_element_balance((year_p, month_p, day_p, hour_p), month_zhi)
        roles, strength, support_score = estimate_five_roles(GAN_ELEMENTS[day_gan], scores)
        wang_roles = calc_wang_xiang(month_zhi)
        yong_xi = calc_yong_xi(GAN_ELEMENTS[day_gan], strength)
        tai_xi_g, tai_xi_z = calc_tai_xi(day_gan, day_zhi)
        tai_yuan_g, tai_yuan_z = calc_tai_yuan(month_gan, month_zhi)
        ming_gong_g, ming_gong_z = calc_ming_gong(birth_year_gan, month_zhi, time_zhi)
        chart = {
            "year_pillar": year_p, "month_pillar": month_p, "day_pillar": day_p, "hour_pillar": hour_p,
            "extra": {
                "tai_xi": {"gan": tai_xi_g, "zhi": tai_xi_z, "star": get_shishen(day_gan, tai_xi_g)},
                "tai_yuan": {"gan": tai_yuan_g, "zhi": tai_yuan_z, "yongshi": "月柱推算"},
                "ming_ge": calc_ming_ge(day_gan, month_p["shishen"], month_zhi),
                "ming_gong": {"gan": ming_gong_g, "zhi": ming_gong_z},
                "day_kong": get_kongwang(day_gan, day_zhi),
                "year_kong": get_kongwang(birth_year_gan, birth_year_zhi),
                "yong_xi": " | ".join(f"{k}:{roles[k]}" for k in ("用","喜","闲","仇","忌")) + "（简化倾向，非正式取用神）",
                "wang_xiang": " | ".join(f"{k}:{wang_roles[k]}" for k in ("旺","相","休","囚","死")) + "（按月令）",
                "strength_details": ("简化五行权重：" + "、".join(f"{e}{scores[e]:g}" for e in ("木","火","土","金","水"))
                    + f"；同党{support_score:g}/{sum(scores.values()):g}；日主参考{'偏旺' if strength else '偏弱'}。"
                    + "仅计四柱显性干支及月令加权，未纳入藏干、通根、合化与调候，不能作为精确旺衰分数。"),
                "pillar_scan": [f"日主{day_gan}{day_zhi}，月令{month_zhi}；五行分布依四柱天干地支统计。"]
            }
        }
        natal_gz = day_gan + day_zhi
        global_analysis_11 = {k: _report_item(k, day_gan, day_zhi, month_zhi, natal_gz, "本命原局", natal_stars) for k in REPORT_TOPICS}

        try:
            yun = eight_char.getYun(1 if gender == "男" else 0)
            da_yun_list = yun.getDaYun()
        except Exception: 
            da_yun_list = []

        dayun_schedule = []
        current_year = __import__("datetime").date.today().year
        for dy in da_yun_list[:11]:
            try:
                if dy.getIndex() == 0: continue
                gz = dy.getGanZhi()
                if not gz or len(gz) < 2: continue
                start_age = int(dy.getStartAge())
                start_year = int(dy.getStartYear())
                dy_analysis = {k: _report_item(k, day_gan, day_zhi, month_zhi, gz, "十年大运", natal_stars) for k in REPORT_TOPICS}
                liu_nian_list = []
                for i in range(10):
                    ly_year = start_year + i
                    ly_age = start_age + i
                    ly_gz = _gz_for_year(ly_year)
                    year_star = get_shishen(day_gan, ly_gz[0])
                    months = []
                    for m_idx in range(12):
                        mgz = _month_gz(ly_year, m_idx)
                        months.append({"month_num":m_idx+1, "chinese_month":f"{m_idx+1}月（节气月）", "gan_zhi":mgz,
                                       "main_star":get_shishen(day_gan, mgz[0]),
                                       "summary":_month_summary(day_gan, day_zhi, mgz, ly_gz, f"第{m_idx+1}节气月")})
                    clash = LIU_CHONG.get(ly_gz[1])
                    tai_sui = ("流年支与本命年支相冲，生活环境或外部安排可能变化。" if clash == birth_year_zhi else
                               "流年支与日支相冲，关系、居所及行程宜留意变动。" if clash == day_zhi else
                               "流年与原局无直接年支或日支六冲，仍须结合现实情况判断。")
                    ly_analysis = {"taisui":tai_sui, "shensha":[], "liuyue":months}
                    for k in ("career","wealth","health","marriage","social","accident"):
                        ly_analysis[k] = _report_item(k, day_gan, day_zhi, month_zhi, ly_gz, f"{ly_year}流年", natal_stars)
                    liu_nian_list.append({"year":ly_year, "age":ly_age, "gan_zhi":ly_gz,
                                          "main_star":year_star, "analysis":ly_analysis})
                status = "past" if start_year+9 < current_year else ("future" if start_year > current_year else "current")
                dayun_schedule.append({"age":start_age, "start_year":start_year, "end_year":start_year+9,
                                       "gan_zhi":gz, "main_star":get_shishen(day_gan, gz[0]),
                                       "sub_star":get_shishen(day_gan, gz[0]), "status":status,
                                       "dayun_analysis":dy_analysis, "liunian":liu_nian_list})
            except (ValueError, TypeError, AttributeError):
                continue
        detailed_report = {"personality": {
            "summary":f"命主日元为{day_gan}（{GAN_ELEMENTS[day_gan]}），日坐{day_zhi}，生于{month_zhi}月。四柱五行以{max(counts, key=counts.get)}较多；此为原局结构的传统命理解读，并非人格或人生事件的确定判断。",
            "strengths":[f"{day_gan}日主可关注{ELEMENT_EFFECT[GAN_ELEMENTS[day_gan]]}方面的长处", f"月柱{month_gan}{month_zhi}提示应结合成长环境和职业要求发挥能力"],
            "weaknesses":["面对压力时留意决策节奏", "不宜仅凭八字决定投资、健康或重大关系选择"],
            "global_analysis":global_analysis_11}}

        return {
            "user_name": name, "gender": gender, "birth_year": year, "birth_month": month, "birth_day": day, 
            "birth_hour": f"{year}-{month}-{day} {h_int:02d}:{m_int:02d}", "virtual_age": current_year - year + 1, 
            "lunar_date": str(lunar), "wang_du": str(counts[GAN_ELEMENTS[day_gan]]), "ruo_du": str(8-counts[GAN_ELEMENTS[day_gan]]), 
            "bazi_chart": chart, 
            "five_elements": {e: round(counts[e] / 8 * 100, 1) for e in counts}, 
            "dayun_list": dayun_schedule, 
            "detailed_report": detailed_report, 
            "ai_report": f"【八字分析报告 - {name}】"
        }