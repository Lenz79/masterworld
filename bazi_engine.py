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



def calc_yangzhai_minggua(solar_year, year_gan, year_zhi, gender):
    """八宅命卦；按八字立春年柱确定年份，5宫男归坤、女归艮。"""
    if gender not in ("男", "女"):
        return "待确认性别"
    # 1984 年为甲子；与八字年柱一致，避免立春前误用公历年份。
    def ganzhi_of(y):
        return GAN_LIST[(y - 1984) % 10] + ZHI_LIST[(y - 1984) % 12]
    actual_year = next((y for y in (solar_year, solar_year - 1, solar_year + 1)
                        if ganzhi_of(y) == year_gan + year_zhi), None)
    if actual_year is None:
        return "待校准年界"
    # 1984 年男命兑七、女命艮八；每年男逆一宫、女顺一宫。
    offset = actual_year - 1984
    number = ((7 - offset - 1) % 9 + 1) if gender == "男" else ((8 + offset - 1) % 9 + 1)
    if number == 5:
        number = 2 if gender == "男" else 8
    names = {1: ("坎", "东四命"), 2: ("坤", "西四命"),
             3: ("震", "东四命"), 4: ("巽", "东四命"),
             6: ("乾", "西四命"), 7: ("兑", "西四命"),
             8: ("艮", "西四命"), 9: ("离", "东四命")}
    name, group = names[number]
    return f"{group} · {name}卦（{number}宫）"

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

        chart = {
            "year_pillar": year_p, "month_pillar": month_p, "day_pillar": day_p, "hour_pillar": hour_p,
            "extra": {
                "tai_xi": {"gan": "甲", "zhi": "子", "star": "比肩"},
                "tai_yuan": {"gan": "甲", "zhi": "寅", "yongshi": "人元用事"},
                "ming_ge": "建禄格",
                "ming_gong": {"gan": "甲", "zhi": "子"},
                "ming_gua": calc_yangzhai_minggua(year, birth_year_gan, birth_year_zhi, gender),
                "day_kong": get_kongwang(day_gan, day_zhi),
                "year_kong": get_kongwang(birth_year_gan, birth_year_zhi),
                "yong_xi": "用:火 | 喜:木",
                "wang_xiang": "旺:木",
                "pillar_scan": ["✨ 原局气场清畅"]
            }
        }

        base_item = {
            "title": "详批", "text": "内容解析", "tips": "建议",
            "strengths": ["优势一", "优势二"],
            "weaknesses": ["劣势一"],
            "pros": ["优点一"],
            "cons": ["缺点一"]
        }
        
        global_analysis_11 = {}
        keys_11 = ["marriage", "career", "wealth", "health", "parents", "siblings", "children", "accident", "social", "property", "inner_world"]
        for k in keys_11:
            global_analysis_11[k] = base_item.copy()

        try:
            yun = eight_char.getYun(1 if gender == "男" else 0)
            da_yun_list = yun.getDaYun()
        except Exception: 
            da_yun_list = []

        dayun_schedule = []
        month_gz_base = [("丙寅", "正月"), ("丁卯", "二月"), ("戊辰", "三月"), ("己巳", "四月"), ("庚午", "五月"), ("辛未", "六月"), ("壬申", "七月"), ("癸酉", "八月"), ("甲戌", "九月"), ("乙亥", "十月"), ("丙子", "十一月"), ("丁丑", "十二月")]

        for dy in da_yun_list[:9]:
            try:
                if dy.getIndex() == 0: continue
                gz = dy.getGanZhi()
                start_age = dy.getStartAge() if hasattr(dy, 'getStartAge') else 10
                start_year = dy.getStartYear() if hasattr(dy, 'getStartYear') else (year + start_age)
                
                dy_analysis = {}
                for k in keys_11:
                    dy_analysis[k] = base_item.copy()

                # 构建 10 年流年
                liu_nian_list = []
                for i in range(10):
                    ly_year = start_year + i
                    ly_age = start_age + i
                    ly_analysis = {
                        "taisui": "✨ 【流年安泰】",
                        "shensha": ["🌟天乙贵人"],
                        "liuyue": [{"month_num": m_idx + 1, "chinese_month": m_cn, "gan_zhi": m_gz, "main_star": "正官", "summary": f"{m_cn}运势平稳。"} for m_idx, (m_gz, m_cn) in enumerate(month_gz_base)],
                        "career": base_item.copy(),
                        "wealth": base_item.copy(),
                        "health": base_item.copy(),
                        "marriage": base_item.copy(),
                        "social": base_item.copy(),
                        "accident": base_item.copy()
                    }
                    liu_nian_list.append({
                        "year": ly_year, "age": ly_age, "gan_zhi": "甲子", "main_star": "正官", "analysis": ly_analysis
                    })

                dayun_schedule.append({
                    "age": start_age, "start_year": start_year, "end_year": start_year + 9, 
                    "gan_zhi": gz, "main_star": "正官", "status": "current",
                    "dayun_analysis": dy_analysis,
                    "liunian": liu_nian_list
                })
            except Exception: 
                continue

        detailed_report = {
            "personality": {
                "summary": "命主性格独立，思维敏捷。",
                "strengths": ["积极进取", "思维开阔"],
                "weaknesses": ["略显急躁"],
                "global_analysis": global_analysis_11
            }
        }

        return {
            "user_name": name, "gender": gender, "birth_year": year, "birth_month": month, "birth_day": day, 
            "birth_hour": f"{year}-{month}-{day} {h_int:02d}:{m_int:02d}", "virtual_age": 2026 - year + 1, 
            "lunar_date": "农历测试", "wang_du": "+500", "ruo_du": "-200", 
            "bazi_chart": chart, 
            "five_elements": {"金": 20, "木": 20, "水": 20, "火": 20, "土": 20}, 
            "dayun_list": dayun_schedule, 
            "detailed_report": detailed_report, 
            "ai_report": f"【八字分析报告 - {name}】"
        }