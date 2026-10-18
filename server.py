# -*- coding: utf-8 -*-
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import traceback
from lunar_python import Solar, Lunar
from supabase import create_client, Client

URL = "https://qistykwqmwtacknrhifq.supabase.co"
KEY = "sb_publishable_gL3EJrq87UcGb-RFMgF1hg_4x-H3rif"

try:
    supabase = create_client(URL, KEY)
except Exception:
    supabase = None

GAN_ELEMENTS = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
ZHI_ELEMENTS = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}

GAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

LIU_CHONG = {"子":"午", "午":"子", "丑":"未", "未":"丑", "寅":"申", "申":"寅", "卯":"酉", "酉":"卯", "辰":"戌", "戌":"辰", "巳":"亥", "亥":"巳"}
XING_MAP = {"子":["卯"], "卯":["子"], "寅":["巳","申"], "巳":["寅","申"], "申":["寅","巳"], "丑":["未","戌"], "未":["丑","戌"], "戌":["丑","未"], "辰":["辰"], "午":["午"], "酉":["酉"], "亥":["亥"]}
PO_MAP = {"子":"酉", "酉":"子", "丑":"辰", "辰":"丑", "寅":"亥", "亥":"寅", "卯":"午", "午":"卯", "巳":"申", "申":"巳", "未":"戌", "戌":"未"}
HAI_MAP = {"子":"未", "未":"子", "丑":"午", "午":"丑", "寅":"巳", "巳":"寅", "卯":"辰", "辰":"卯", "申":"亥", "亥":"申", "酉":"戌", "戌":"酉"}

GAN_HE = {"甲":"己", "己":"甲", "乙":"庚", "庚":"乙", "丙":"辛", "辛":"丙", "丁":"壬", "壬":"丁", "戊":"癸", "癸":"戊"}
ZHI_HE = {"子":"丑", "丑":"子", "寅":"亥", "亥":"寅", "卯":"戌", "戌":"卯", "辰":"酉", "酉":"辰", "巳":"申", "申":"巳", "午":"未", "未":"午"}

SHISHEN_DATABASE = {
    "正官": {"meaning": "代表规范、自律、名誉、责任心、领导力与体制契约。", "pros": "遵纪守法，处事公道，具领导力", "cons": "固执保守，不善变通"},
    "七杀": {"meaning": "代表魄力、竞争、开拓精神、权威、危机意识与高压爆发力。", "pros": "果断有魄力，具开拓精神", "cons": "脾气急躁，防金创伤灾"},
    "正印": {"meaning": "代表学识、贵人、母亲庇荫、慈悲心、契约文书与安全感。", "pros": "心地善良，学识渊博，多贵人", "cons": "依赖性强，缺乏魄力"},
    "偏印": {"meaning": "代表灵感、玄学直觉、独到思维、冷门技术、孤傲与非传统创新。", "pros": "悟性极高，思维独到，利艺术玄学", "cons": "孤傲多疑，不易合群"},
    "正财": {"meaning": "代表稳健正财、薪资收益、不动产、踏实经营与精打细算。", "pros": "勤俭持家，踏实务实，财运稳健", "cons": "过度计较，缺乏大局观"},
    "偏财": {"meaning": "代表横财、投资、商业商机、交际手腕与流动资产。", "pros": "慷慨大方，交际广泛，商业敏锐", "cons": "浮躁投机，花钱无节制"},
    "食神": {"meaning": "代表福气、口福、温和优雅、艺术才华、表现力与包容心。", "pros": "温和优雅，艺术才华，具包容心", "cons": "贪图安逸，缺乏危机感"},
    "伤官": {"meaning": "代表才华横溢、高傲叛逆、演说辩论、技术突破与打破常规。", "pros": "聪明绝顶，才华横溢，具创新力", "cons": "高傲傲物，易招口舌官非"},
    "比肩": {"meaning": "代表自我、独立、同辈兄弟朋友、自信心与坚持。", "pros": "独立自主，重情重义，坚持不懈", "cons": "固执己见，不听人劝"},
    "劫财": {"meaning": "代表拼搏、投机、对财富的强烈掌控欲与敏捷行动力。", "pros": "拼搏心强，行动敏捷，具爆发力", "cons": "冲动投机，易破财争财"}
}

ELEMENT_DB = {
    "木": {"directions": "【东方】与【东南方】", "bad_directions": "【西方】与【西北方】", "industries": "文化教育、出版传媒、木材家居、农林园艺、医疗医药、设计策划、绿色环保", "health_tips": "肝胆气血、筋骨关节、神经系统及眼睛视力保养", "colors": "【绿色、青色】", "numbers": "【3、8】", "floors": "【3楼、8楼、13楼、18楼】"},
    "火": {"directions": "【正南方】", "bad_directions": "【正北方】", "industries": "高新科技、人工智能、能源光伏、餐饮娱乐、美妆美容、广告传媒、照明电子", "health_tips": "心脑血管、血液循环、小肠、视力及情绪焦虑防范", "colors": "【红色、紫色】", "numbers": "【2、7】", "floors": "【2楼、7楼、12楼、17楼】"},
    "土": {"directions": "【东北方】与【西南方】", "bad_directions": "【正东方】与【东南方】", "industries": "房地产, 建筑工程, 基础建设, 矿产资源, 仓储物流, 古玩农业, 不动产中介", "health_tips": "脾胃消化系统、皮肤屏障、肌肉劳损及腹部消化调理", "colors": "【黄色、棕色】", "numbers": "【5、0】", "floors": "【5楼、10楼、15楼、20楼】"},
    "金": {"directions": "【西方】与【西北方】", "bad_directions": "【正南方】", "industries": "金融证券、机械制造、五金珠宝、汽车交运、军警法务、精密仪器、医疗器械", "health_tips": "呼吸系统、肺部气管、大肠咽喉及皮肤过敏防范", "colors": "【白色、金色】", "numbers": "【4、9】", "floors": "【4楼、9楼、14楼、19楼】"},
    "水": {"directions": "【正北方】", "bad_directions": "【东北方】与【西南方】", "industries": "国际贸易、航运物流、水产旅游、文化传播、电商直播、饮料餐饮、清洁水利", "health_tips": "肾脏泌尿系统、生殖健康、内分泌及腰部气血调理", "colors": "【黑色、蓝色】", "numbers": "【1、6】", "floors": "【1楼、6楼、11楼、16楼】"}
}

SPOUSE_ZHI_DB = {
    "子": {"sp_type": "身材匀称修长，皮肤白皙，聪明灵动，极具幽默感与艺术品位。", "relation": "双方沟通注重精神共鸣，情绪价值丰富，相处充满灵动趣味。"},
    "午": {"sp_type": "身材高挑身材有型，性格尊贵开朗，言谈举止极具张力与感染力。", "relation": "感情浓烈真挚，相处需互相给予包容与赞美，避免性格过于刚烈。"},
    "卯": {"sp_type": "气质温婉秀丽，身材纤细，为人重情重义，带有天然文雅气质。", "relation": "相处如沐春风，感情生活追求浪漫细腻，情感表达真挚深沉。"},
    "酉": {"sp_type": "五官精致棱角分明，讲究生活品质，作风干练，气场干脆利落。", "relation": "处事讲求原则与效率，互相尊重独立空间，能够共同把持家业。"},
    "寅": {"sp_type": "身材挺拔，性格威严果断，有领导风范，做事富有拼搏精神。", "relation": "伴侣能在事业上给予建设性建议与实质助力，宜多合作共赢。"},
    "申": {"sp_type": "敏捷精明，眼神锐利，适应力极强，擅长社交与资源整合。", "relation": "生活充满变化与新鲜感，沟通宜开诚布公，互相坦诚相待。"},
    "巳": {"sp_type": "外表沉稳内隐爆发力，思维敏捷，对事业与生活有极高目标。", "relation": "互相扶持成长，能共同制定长远发展计划并建立稳固财库。"},
    "亥": {"sp_type": "体态丰盈圆润，待人随和善良，包容心强，具有极佳福气。", "relation": "家庭氛围温馨融洽，注重饮食生活品质，物质生活踏实丰足。"},
    "辰": {"sp_type": "气场厚重，性格踏实稳重，城府深沉，注重家庭实质利益。", "relation": "相处贵在务实与信任，互相作为强大后盾，家庭资产积累稳固。"},
    "戌": {"sp_type": "忠诚可靠，重信守诺，做事坚持到底，对家庭极其忠诚。", "relation": "感情稳如磐石，富有责任担当，是平淡生活中最坚实可靠的避风港。"},
    "丑": {"sp_type": "为人低调勤奋，吃苦耐劳，精打细算，性格沉稳内敛。", "relation": "陪伴最为长情，默默付出，宜多表达内心爱意与认可。"},
    "未": {"sp_type": "性格温和有礼，为人热心，富有爱心，极具家庭责任感。", "relation": "关怀备至，家庭生活充满烟火气息与温馨，善于调和家庭矛盾。"}
}

ZODIAC_VIP_DB = {
    "子": {"vip": "生肖【牛】、生肖【猴】、生肖【龙】", "taboo": "生肖【马】、生肖【羊】"},
    "丑": {"vip": "生肖【鼠】、生肖【蛇】、生肖【鸡】", "taboo": "生肖【羊】、生肖【马】"},
    "寅": {"vip": "生肖【猪】、生肖【马】、生肖【狗】", "taboo": "生肖【猴】、生肖【蛇】"},
    "卯": {"vip": "生肖【狗】、生肖【猪】、生肖【羊】", "taboo": "生肖【鸡】、生肖【鼠】"},
    "辰": {"vip": "生肖【鸡】、生肖【猴】、生肖【鼠】", "taboo": "生肖【狗】、生肖【兔】"},
    "巳": {"vip": "生肖【猴】、生肖【鸡】、生肖【牛】", "taboo": "生肖【猪】、生肖【虎】"},
    "午": {"vip": "生肖【羊】、生肖【虎】、生肖【狗】", "taboo": "生肖【鼠】、生肖【牛】"},
    "未": {"vip": "生肖【马】、生肖【猪】、生肖【兔】", "taboo": "生肖【牛】、生肖【鼠】"},
    "申": {"vip": "生肖【蛇】、生肖【鼠】、生肖【龙】", "taboo": "生肖【虎】、生肖【猪】"},
    "酉": {"vip": "生肖【龙】、生肖【蛇】、生肖【牛】", "taboo": "生肖【兔】、生肖【狗】"},
    "戌": {"vip": "生肖【兔】、生肖【虎】、生肖【马】", "taboo": "生肖【龙】、生肖【鸡】"},
    "亥": {"vip": "生肖【虎】、生肖【兔】、生肖【羊】", "taboo": "生肖【蛇】、生肖【猴】"}
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
        
    return {"yong": yong, "xi": xi, "xian": xian, "chou": chou, "ji": ji, "str_repr": f"用:{yong} | 喜:{xi} | 闲:{xian} | 仇:{chou} | 忌:{ji}"}

def calc_wang_xiang(month_zhi):
    zhi_elem = ZHI_ELEMENTS.get(month_zhi, "木")
    elements = ["木", "火", "土", "金", "水"]
    idx = elements.index(zhi_elem)
    wang = zhi_elem
    xiang = elements[(idx + 1) % 5]
    si = elements[(idx + 2) % 5]
    qiu = elements[(idx + 3) % 5]
    xiu = elements[(idx + 4) % 5]
    return f"旺:{wang} | 相:{xiang} | 死:{si} | 囚:{qiu} | 休:{xiu}"

def scan_four_pillars_interactions(pillars):
    # 扫描原局四柱之间的合、冲、刑、害、破
    results = []
    zhis = [p['zhi'] for p in pillars]
    gans = [p['gan'] for p in pillars]
    
    # 地支六冲
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            if LIU_CHONG.get(zhis[i]) == zhis[j]:
                results.append(f"⚡ 地支相冲：[{zhis[i]}]与[{zhis[j]}]相冲，主多动荡或心神不定。")
    # 地支六合
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            if ZHI_HE.get(zhis[i]) == zhis[j]:
                results.append(f"🤝 地支相合：[{zhis[i]}]与[{zhis[j]}]相合，主贵人相助、人缘融洽。")
    # 天干五合
    for i in range(len(gans)):
        for j in range(i+1, len(gans)):
            if GAN_HE.get(gans[i]) == gans[j]:
                results.append(f"✨ 天干五合：{gans[i]}与{gans[j]}相合，主多得契约情谊。 ")
                
    return results if results else ["✨ 原局气场清畅，无剧烈刑冲破害交战。"]

def get_liunian_shensha(day_gan, birth_year_zhi, ly_zhi):
    shensha_list = []
    tianyi_map = {"甲":["丑","未"], "戊":["丑","未"], "庚":["丑","未"], "乙":["子","申"], "己":["子","申"], "丙":["亥","酉"], "丁":["亥","酉"], "辛":["午","寅"], "壬":["卯","巳"], "癸":["卯","巳"]}
    if ly_zhi in tianyi_map.get(day_gan, []): shensha_list.append("🌟天乙贵人（逢凶化吉，多得贵人扶持）")
    yima_map = {"申":"寅", "子":"寅", "辰":"寅", "寅":"申", "午":"申", "戌":"申", "亥":"巳", "卯":"巳", "未":"巳", "巳":"亥", "酉":"亥", "丑":"亥"}
    if ly_zhi == yima_map.get(birth_year_zhi): shensha_list.append("🐎驿马星（主走动、搬迁、岗位变动或出差）")
    taohua_map = {"申":"酉", "子":"酉", "辰":"酉", "寅":"卯", "午":"卯", "戌":"卯", "巳":"午", "酉":"午", "丑":"午", "亥":"子", "卯":"子", "未":"子"}
    if ly_zhi == taohua_map.get(birth_year_zhi): shensha_list.append("🌸咸池桃花（异性缘旺、魅力提升，防烂桃花）")
    huagai_map = {"申":"辰", "子":"辰", "辰":"辰", "寅":"戌", "午":"戌", "戌":"戌", "巳":"丑", "酉":"丑", "丑":"丑", "亥":"未", "卯":"未", "未":"未"}
    if ly_zhi == huagai_map.get(birth_year_zhi): shensha_list.append("🧘华盖星（悟性天赋高，利于学术玄学）")
    yangren_map = {"甲":"卯", "乙":"辰", "丙":"午", "丁":"未", "戊":"午", "己":"未", "庚":"酉", "辛":"戌", "壬":"子", "癸":"丑"}
    if ly_zhi == yangren_map.get(day_gan): shensha_list.append("⚔️羊刃临值（性格易急躁，谨防金创伤灾）")
    if not shensha_list: shensha_list.append("✨岁运平顺（气场中和，无重大凶煞冲击）")
    return shensha_list

def check_taisuibai(birth_year_zhi, liunian_zhi):
    taisuicheck = []
    if birth_year_zhi == liunian_zhi: taisuicheck.append(f"【值太岁/本命年】生肖与流年相同（{birth_year_zhi}值太岁），运势多变，宜静不宜动。")
    if LIU_CHONG.get(birth_year_zhi) == liunian_zhi: taisuicheck.append(f"【冲太岁】生肖与流年相冲（{birth_year_zhi}冲{liunian_zhi}），冲击力最强，主职场变动或远行。")
    if liunian_zhi in XING_MAP.get(birth_year_zhi, []):
        if birth_year_zhi != liunian_zhi: taisuicheck.append(f"【刑太岁】生肖与流年相刑（{birth_year_zhi}刑{liunian_zhi}），多主精神压力或合约纠纷。")
    if HAI_MAP.get(birth_year_zhi) == liunian_zhi: taisuicheck.append(f"【害太岁】生肖与流年相害（{birth_year_zhi}害{liunian_zhi}），易遭人际口舌或背后是非。")
    if PO_MAP.get(birth_year_zhi) == liunian_zhi: taisuicheck.append(f"【破太岁】生肖与流年相破（{birth_year_zhi}破{liunian_zhi}），主计划受损或暗破财务。")
    return " ⚠️ ".join(taisuicheck) if taisuicheck else "✨ 【流年安泰】 命主生肖与当年流年无犯太岁冲击，气场平稳顺遂。"

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

def generate_dynamic_global_analysis(day_gan, gender, is_strong, day_zhi, birth_year_zhi, month_star, elem_scores):
    day_gan_elem = GAN_ELEMENTS.get(day_gan, "木")
    yx_obj = calc_yong_xi(day_gan_elem, is_strong)
    yong_elem = yx_obj["yong"]
    xi_elem = yx_obj["xi"]
    
    yong_info = ELEMENT_DB.get(yong_elem, ELEMENT_DB["木"])
    xi_info = ELEMENT_DB.get(xi_elem, ELEMENT_DB["火"])
    ji_elem = yx_obj["ji"]
    ji_info = ELEMENT_DB.get(ji_elem, ELEMENT_DB["金"])
    
    sorted_elems = sorted(elem_scores.items(), key=lambda x: x[1])
    weakest_elem = sorted_elems[0][0]
    weak_health_info = ELEMENT_DB.get(weakest_elem, ELEMENT_DB["土"])["health_tips"]
    spouse_info = SPOUSE_ZHI_DB.get(day_zhi, SPOUSE_ZHI_DB["子"])
    vips = ZODIAC_VIP_DB.get(birth_year_zhi, ZODIAC_VIP_DB["子"])
    strength_desc = "日元格局【身强】，气场雄厚，自信有魄力，具备强烈的掌控欲与突破精神" if is_strong else "日元格局【身弱】，气场中和，处事细腻稳健，擅长借力打力与团队合作"

    return {
        "marriage": {
            "title": "💍 1. 婚姻感情",
            "text": f"【夫妻婚姻宫 · 基于日支【{day_zhi}】与日元【{day_gan}{day_gan_elem}】专属解构】\n\n一、 伴侣外貌与体型特质：\n命主夫妻宫地支临【{day_zhi}】。{spouse_info['sp_type']}\n\n二、 婚姻情感气场与沟通机制：\n{spouse_info['relation']}夫妻相处如水相融，相互尊重对方的个人隐私与独立思考空间。\n\n三、 寻缘与桃花大吉方位（严格区分用神与喜神）：\n• 核心用神【{yong_elem}】方位：建议向常住地的{yong_info['directions']}拓展核心生活圈，最易遇上能互相扶持、价值观契合的正缘伴侣。\n• 喜神【{xi_elem}】催化方位：亦可向{xi_info['directions']}活动，能显著提升个人情感魅力与社交运势。\n• 忌讳寻缘方位：严禁向{ji_info['directions']}盲目社交，容易遇到烂桃花或情感波折。",
            "tips": "💡 【婚姻实操调理与避坑建议】：\n• 严格执行“冷静10分钟”沟通法则，切忌冷战与说伤人狠话。\n• 主卧床头宜朝向用神喜用方位（{yong_info['directions']}），卧室保持整洁明亮以催旺家运。"
        },
        "career": {
            "title": "💼 2. 职业分析",
            "text": f"【职业与事业发展 · 基于月令【{month_star}】与用神【{yong_elem}】/喜神【{xi_elem}】独立解构】\n\n一、 命格局与职场定位：\n命局表现为{strength_desc}。月令核心主星临【{month_star}】，赋予命主出色的职业敏锐度与执行力。\n\n二、 用神与喜神行业精准匹配（分项论断）：\n👉 **核心用神【{yong_elem}】主赛道**（筑牢根基、稳健立足）：\n适宜深耕属【{yong_elem}】性质的行业：{yong_info['industries']}。\n👉 **喜神【{xi_elem}】发光发热赛道**（突破创新、名气变现）：\n适宜结合属【{xi_elem}】性质的行业：{xi_info['industries']}。\n\n三、 事业吉凶方位分布：\n• 事业大吉发展方位：首选{yong_info['directions']}（用神方）与{xi_info['directions']}（喜神方）。\n• 不利事业方位：{ji_info['directions']}气场受阻，在此方位求职或签协议需多加谨慎。",
            "tips": "💡 【职场实操调理与避坑建议】：\n• 专注于核心竞争力的突破，切忌盲目频繁跨行。\n• 办公桌青龙方（左手边）保持高于白虎方（右手边），可摆放喜用五行风水植物以催旺贵人。"
        },
        "wealth": {
            "title": "💰 3. 财运 / 投资分析",
            "text": f"【财富与投资理财 · 基于日元【{day_gan}】与用喜神专属解构】\n\n一、 当老板运势与商业格局评估：\n月令临【{month_star}】，自身具备深厚的商业思考力与财商逻辑。\n\n二、 用神与喜神财富爆发力分析：\n• **用神【{yong_elem}】代表正财与稳健资产**：主实体经营、长期长线投资与储蓄积累，风险极低。\n• **喜神【{xi_elem}】代表偏财与商业机遇**：主投资眼光、商业灵感与多元化变现。\n\n三、 求财吉凶方位：\n• 求财大吉方位：{yong_info['directions']}（用神方）与{xi_info['directions']}（喜神方）是财源汇聚之地。\n• 破财防范方位：{ji_info['directions']}易引发资金链紧张或无谓耗损。",
            "tips": "💡 【财运实操理财与避坑建议】：\n• 严禁参与民间高息借贷、高杠杆股票投机或不合规的盲目项目投资。\n• 建立家庭专项储备基金，时刻留足 6 个月以上的流动现金流。"
        },
        "health": {
            "title": "🏥 4. 健康分析",
            "text": f"【健康养生与体质 · 基于最弱五行【{weakest_elem}】与用喜神调理专属解构】\n\n一、 先天五行体质密码：\n八字五行中【{weakest_elem}】元素相对薄弱，先天体质需重点关照相关脏腑健康：\n👉 {weak_health_info}。\n\n二、 用神与喜神养生机制：\n• 借助用神【{yong_elem}】气场（如生活在{yong_info['directions']}或调理相关作息）来固本培元。\n• 借助喜神【{xi_elem}】气场（如保持积极乐观心态、接触{xi_info['directions']}阳光活力）。",
            "tips": "💡 【健康实操调理与避坑建议】：\n• 坚持每晚热水泡脚 15~20 分钟，加入艾叶或生姜以促进血液循环。\n• 保持每周 3 次以上的有氧运动（如快走、慢跑或游泳），排解身体毒素与精神压力。"
        },
        "parents": {
            "title": "👨‍👩‍👦 5. 父母缘份",
            "text": f"【父母长辈缘份 · 全局总论】\n\n一、 长辈庇荫与缘份厚薄：\n命局中印星气场中和，与父母长辈缘份深厚。早年多得长辈在生活与价值观上的悉心教导与庇荫。\n\n二、 长辈健康关照：\n需重点关照双方父母的心脑血管、骨质关节及慢性消化的日常调理。\n\n三、 孝道沟通法则：\n与长辈沟通宜多倾听、少争辩，顺从长辈心意，在精神与物质上给予双重关怀。",
            "tips": "💡 【孝道实操调理建议】：\n• 每年安排父母进行一次深度体检。\n• 经常主动沟通倾听长辈心声，顺从长辈心意即是最上等之孝顺。"
        },
        "siblings": {
            "title": "👫 6. 兄弟姐妹缘份",
            "text": f"【手足与合伙人助力 · 基于年支【{birth_year_zhi}】专属解构】\n\n一、 同辈与合伙气场：\n同辈兄弟姐妹及朋友手足交往顺畅，但在涉及重大商业合作或资金往来时，必须做到“亲兄弟明算账”。\n\n二、 贵人生肖与忌讳生肖指南：\n• 贵人生肖：{vips['vip']}。\n• 忌讳生肖：{vips['taboo']}。",
            "tips": "💡 【合伙实操避坑建议】：\n• 避免盲目为亲朋好友提供经济担保或借贷。\n• 君子之交淡如水，保持适度界限反而能使友情与合作更加长久。"
        },
        "children": {
            "title": "👶 7. 子女缘份",
            "text": f"【子女成长与教育 · 全局总论】\n\n一、 子女性格与天赋特质：\n命局中食伤/官杀气场清透，预示子女聪明伶俐，富有探索精神与独立主见。\n\n二、 亲子互动与教育法则：\n教育上切忌采用专制施压或强加意愿的方式，宜采取启发式与鼓励式教育。",
            "tips": "💡 【教育实操调理建议】：\n• 多倾听孩子的真实心声，给予其充分的信任与成长空间。\n• 营造温馨和谐的家庭学习氛围，榜样示范胜过千言万语。"
        },
        "accident": {
            "title": "⚠️ 8. 交通意外防范",
            "text": f"【交通意外防范 · 全局总论】\n\n一、 出行安全与气场评估：\n日常行车与出差远行频率较高时，需时刻保持高度专注，防范因情绪急躁或疲劳驾驶引发的突发车辆擦碰。\n\n二、 凶煞出行防范方位：\n自驾或长途远行时，需严加防范前往{ji_info['bad_directions']}方向。",
            "tips": "💡 【交通安全防范建议】：\n• 驾车时严格遵守交通法规，拒绝酒驾、超速与疲劳驾驶。\n• 车内保持整洁，可摆放平安符或平稳气场之饰物。"
        },
        "social": {
            "title": "🤝 9. 交友人缘 - 人事是非",
            "text": f"【交友人缘与是非 · 全局总论】\n\n一、 社交圈层与人脉品质：\n命主待人热情真诚，社交圈层广阔，容易结识各行各业的朋友。\n\n二、 小人是非防范：\n处事高调时易引来小人无端的嫉妒或背后口舌是非。",
            "tips": "💡 【社交实操避坑建议】：\n• 远离满身负能量与爱议论他人是非的圈子。\n• 重大决策不盲从他人劝说，保持独立的理智判断。"
        },
        "property": {
            "title": "🏡 10. 田宅不动产分析",
            "text": f"【田宅不动产置业 · 基于用神【{yong_elem}】与喜神【{xi_elem}】方位专属解构】\n\n一、 置业运势与资产配置：\n命局田宅宫安定，置业安家运势顺遂。\n\n二、 买房大吉朝向与采光方位（分项论断）：\n• **用神【{yong_elem}】置业朝向**：首选房屋大门或主要阳台采光朝向{yong_info['directions']}的户型。\n• **喜神【{xi_elem}】置业朝向**：亦可选择朝向{xi_info['directions']}的户型。\n• 忌讳房屋朝向：不宜购买大门或阳台朝向{ji_info['directions']}的房屋。",
            "tips": "💡 【置业实操避坑建议】：\n• 购房前务必做好未来 3~5 年的现金流压力测试，切忌过度高杠杆负债。\n• 选房注重房企品质与地段升值潜力。"
        },
        "inner_world": {
            "title": "🧘 11. 内心世界分析",
            "text": f"【内心世界与精神修炼 · 基于日元【{day_gan}{day_gan_elem}】与用喜神专属解构】\n\n一、 精神世界与哲学悟性深度剖析：\n命主内心世界极其丰富细腻，表面上或许随和务实，但内心里始终保有对生命本质、哲学玄学或艺术美学的深层思考。\n\n二、 情绪解压与精神修复机制：\n• 借助用神【{yong_elem}】的能量（如静心阅读、书画、大自然静坐）来沉淀心绪。\n• 借助喜神【{xi_elem}】的能量（如运动发汗、与挚友聚会、接触阳光）来释放压力。",
            "tips": "💡 【心灵内修实操调理指引】：\n• 每天给自己预留 20 分钟绝对安静的“独处冥想时间”，关闭手机，清空杂念。\n• 定期清理居住与办公环境，定期丢弃无用之物（断舍离），环境清爽则心灵自然澄明。"
        }
    }

class BaziAPIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # 🛠️ 新增：获取历史档案列表 API
        if self.path == '/api/records':
            try:
                if supabase:
                    res = supabase.table("bazi_records").select("id, user_name, gender, birth_hour, created_at").order("created_at", desc=True).limit(20).execute()
                    records = res.data if hasattr(res, 'data') else []
                else:
                    records = []
                response_json = json.dumps({"status": "success", "data": records}, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
            except Exception as err:
                err_resp = json.dumps({"status": "error", "message": str(err)}, ensure_ascii=False)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(err_resp.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/calculate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                req_data = json.loads(post_data.decode('utf-8'))

                name = req_data.get('name', '小叶')
                gender = req_data.get('gender', '男')
                year = int(req_data.get('year', 1979))
                month = int(req_data.get('month', 1))
                day = int(req_data.get('day', 20))
                
                raw_hour = req_data.get('hour', 10)
                if isinstance(raw_hour, (int, float)) and raw_hour > 23:
                    hour_str = str(int(raw_hour))
                    if len(hour_str) == 3:
                        hour = int(hour_str[0]) + int(hour_str[1:]) / 60.0
                    elif len(hour_str) == 4:
                        hour = int(hour_str[:2]) + int(hour_str[2:]) / 60.0
                    else:
                        hour = int(raw_hour)
                else:
                    hour = float(raw_hour) if '.' in str(raw_hour) else int(raw_hour)

                h_int = int(hour)
                m_int = int(round((hour - h_int) * 60))

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

                current_year = 2026
                virtual_age = current_year - year + 1
                lunar_str = f"农历 {lunar.getYearInGanZhi()}年 {lunar.getMonthInChinese()}月{lunar.getDayInChinese()} {eight_char.getTimeZhi()}时"

                time_formatted = f"{h_int:02d}:{m_int:02d}"

                def build_cangan(zhi_char):
                    try:
                        if zhi_char == birth_year_zhi: hides = list(eight_char.getYearHideGan())
                        elif zhi_char == month_zhi: hides = list(eight_char.getMonthHideGan())
                        elif zhi_char == day_zhi: hides = list(eight_char.getDayHideGan())
                        else: hides = list(eight_char.getTimeHideGan())
                    except Exception: hides = ["甲"]
                    return [{"gan": hg, "star": get_shishen(day_gan, hg)} for hg in hides]

                year_p = {"shishen": get_shishen(day_gan, birth_year_gan), "gan": birth_year_gan, "gan_elem": GAN_ELEMENTS.get(birth_year_gan, "木"), "zhi": birth_year_zhi, "zhi_elem": ZHI_ELEMENTS.get(birth_year_zhi, "木"), "cangan_details": build_cangan(birth_year_zhi), "yun": "冠带", "shensha": ["羊刃", "华盖"], "nayin": eight_char.getYearNaYin()}
                month_p = {"shishen": get_shishen(day_gan, month_gan), "gan": month_gan, "gan_elem": GAN_ELEMENTS.get(month_gan, "金"), "zhi": month_zhi, "zhi_elem": ZHI_ELEMENTS.get(month_zhi, "火"), "cangan_details": build_cangan(month_zhi), "yun": "临官", "shensha": ["太极贵人", "禄神"], "nayin": eight_char.getMonthNaYin()}
                day_p = {"shishen": "命主", "gan": day_gan, "gan_elem": GAN_ELEMENTS.get(day_gan, "土"), "zhi": day_zhi, "zhi_elem": ZHI_ELEMENTS.get(day_zhi, "水"), "cangan_details": build_cangan(day_zhi), "yun": "胎", "shensha": ["天德"], "nayin": eight_char.getDayNaYin()}
                hour_p = {"shishen": get_shishen(day_gan, time_gan), "gan": time_gan, "gan_elem": GAN_ELEMENTS.get(time_gan, "金"), "zhi": time_zhi, "zhi_elem": ZHI_ELEMENTS.get(time_zhi, "土"), "cangan_details": build_cangan(time_zhi), "yun": "死", "shensha": ["亡神"], "nayin": eight_char.getTimeNaYin()}

                ty_gan, ty_zhi = calc_tai_yuan(month_gan, month_zhi)
                tx_gan, tx_zhi = calc_tai_xi(day_gan, day_zhi)
                mg_gan, mg_zhi = calc_ming_gong(birth_year_gan, month_zhi, time_zhi)
                month_star = month_p["shishen"]
                calculated_ming_ge = calc_ming_ge(day_gan, month_star, month_zhi)

                elem_scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
                for g in [birth_year_gan, month_gan, day_gan, time_gan]: elem_scores[GAN_ELEMENTS.get(g, "土")] += 100
                for idx, z in enumerate([birth_year_zhi, month_zhi, day_zhi, time_zhi]): elem_scores[ZHI_ELEMENTS.get(z, "土")] += (300 if idx == 1 else 100)

                total_score = sum(elem_scores.values()) or 1000
                five_elements = {k: round((v / total_score) * 100) for k, v in elem_scores.items()}

                day_gan_elem = GAN_ELEMENTS.get(day_gan, "土")
                sheng_elems = {"木": ["木", "水"], "火": ["火", "木"], "土": ["土", "火"], "金": ["金", "土"], "水": ["水", "金"]}.get(day_gan_elem, [day_gan_elem])
                plus_score = sum(elem_scores[e] for e in sheng_elems)
                minus_score = total_score - plus_score

                wang_du = f"+{plus_score}"
                ruo_du = f"-{minus_score}"

                is_strong = plus_score >= (total_score * 0.42)
                strength_text = "🔥 【身强】" if is_strong else "💧 【身弱】"

                yx_obj = calc_yong_xi(day_gan_elem, is_strong)
                dynamic_wang_xiang = calc_wang_xiang(month_zhi)
                
                # 🛠️ 新增：原局刑冲合害扫描
                pillar_scan = scan_four_pillars_interactions([year_p, month_p, day_p, hour_p])

                extra_p = {
                    "tai_xi": {"gan": tx_gan, "zhi": tx_zhi, "star": get_shishen(day_gan, tx_gan)},
                    "tai_yuan": {"gan": ty_gan, "zhi": ty_zhi, "yongshi": "人元用事"},
                    "ming_ge": calculated_ming_ge,
                    "ming_gong": {"gan": mg_gan, "zhi": mg_zhi},
                    "day_kong": get_kongwang(day_gan, day_zhi),
                    "year_kong": get_kongwang(birth_year_gan, birth_year_zhi),
                    "yong_xi": yx_obj["str_repr"],
                    "wang_xiang": dynamic_wang_xiang,
                    "pillar_scan": pillar_scan,
                    "strength_details": f"同党得分: {plus_score} | 异党得分: {minus_score} | 月令({month_zhi})权重最高"
                }

                chart = {"year_pillar": year_p, "month_pillar": month_p, "day_pillar": day_p, "hour_pillar": hour_p, "extra": extra_p}

                ys_info = SHISHEN_DATABASE.get(year_p["shishen"], {"meaning": "主社会交往与祖业缘分。", "pros": "做事稳重", "cons": "略显保守"})
                ms_info = SHISHEN_DATABASE.get(month_star, {"meaning": "月令核心星曜，主中年事业与性格核心。", "pros": "事业心强", "cons": "压力较大"})
                hs_info = SHISHEN_DATABASE.get(hour_p["shishen"], {"meaning": "时柱归宿星曜，主晚运与子女。", "pros": "晚运安泰", "cons": "操心较多"})

                pers_summary = f"命主日元属{day_gan}（{day_gan_elem}），格局表现为{strength_text}。\n\n【核心主星拆解】：\n1. 月柱主星【{month_star}】：{ms_info['meaning']}\n2. 年柱主星【{year_p['shishen']}】：{ys_info['meaning']}\n3. 时柱主星【{hour_p['shishen']}】：{hs_info['meaning']}"

                global_analysis_11 = generate_dynamic_global_analysis(day_gan, gender, is_strong, day_zhi, birth_year_zhi, month_star, elem_scores)

                try:
                    yun = eight_char.getYun(1 if gender == "男" else 0)
                    da_yun_list = yun.getDaYun()
                except Exception: da_yun_list = []

                dayun_schedule = []
                month_gz_base = [("丙寅", "正月"), ("丁卯", "二月"), ("戊辰", "三月"), ("己巳", "四月"), ("庚午", "五月"), ("辛未", "六月"), ("壬申", "七月"), ("癸酉", "八月"), ("甲戌", "九月"), ("乙亥", "十月"), ("丙子", "十一月"), ("丁丑", "十二月")]

                for dy in da_yun_list[:9]:
                    try:
                        if dy.getIndex() == 0: continue
                        gz = dy.getGanZhi()
                        dy_gan, dy_zhi = gz[0], gz[1]
                        main_star = get_shishen(day_gan, dy_gan)
                        start_age = dy.getStartAge() if hasattr(dy, 'getStartAge') else getattr(dy, 'getAge', lambda: 10)()
                        start_year = dy.getStartYear() if hasattr(dy, 'getStartYear') else (year + start_age)
                        end_year = start_year + 9
                        status = "past" if current_year > end_year else ("current" if start_year <= current_year <= end_year else "future")
                        dy_xi_elem = GAN_ELEMENTS.get(dy_gan, "木")
                        dy_info = ELEMENT_DB.get(dy_xi_elem, ELEMENT_DB["木"])
                        vips = ZODIAC_VIP_DB.get(birth_year_zhi, ZODIAC_VIP_DB["子"])

                        dayun_analysis_11 = {
                            "marriage": {"title": "💍 大限夫妻婚姻宫深度解构", "text": f"【大限 {gz} 期间 · 婚姻感情全景剖析】\n当前大运逢【{main_star}】临值主事。", "tips": "💡 【婚姻实操调理】：严格执行冷静10分钟沟通。"},
                            "career": {"title": "💼 大限职业与事业方位详批", "text": f"【大限 {gz} 期间 · 事业发展与职场定位】\n大运十神【{main_star}】主事。前往{dy_info['directions']}事业贵人多。", "tips": "💡 【职场实操调理】：办公桌青龙方置放绿植。"},
                            "wealth": {"title": "💰 大限财运格局与求财方位解析", "text": f"【大限 {gz} 期间 · 财富爆发与投资解析】\n大运十神【{main_star}】主事。求财大吉方位为{dy_info['directions']}。", "tips": "💡 【财运实操调理】：保持财位明亮洁净。"},
                            "health": {"title": "🏥 大限健康养生与调理指南", "text": f"【大限 {gz} 期间 · 健康管理与体质防范】\n大运十神【{main_star}】主事。", "tips": "💡 【健康实操调理】：每晚坚持热水泡脚。"},
                            "parents": {"title": "👨‍👩‍👦 大限父母长辈缘份与健康", "text": f"【大限 {gz} 期间 · 长辈缘份全景剖析】", "tips": "💡 【孝道建议】：定期安排全面体检。"},
                            "siblings": {"title": "👫 大限手足与合伙人助力分析", "text": f"【大限 {gz} 期间 · 同辈助力与合伙】", "tips": "💡 【合伙建议】：亲兄弟明算账。"},
                            "children": {"title": "👶 大限子女成长与教育指引", "text": f"【大限 {gz} 期间 · 子女教育全景剖析】", "tips": "💡 【教育建议】：多做良师益友。"},
                            "accident": {"title": "⚠️ 大限交通出行与凶险方位防范", "text": f"【大限 {gz} 期间 · 出行安全与防范】", "tips": "💡 【安全建议】：严禁酒驾与疲劳驾驶。"},
                            "social": {"title": "🤝 大限交友合伙与生肖喜忌全解", "text": f"【大限 {gz} 期间 · 人脉交友与生肖指南】贵人生肖：{vips['vip']}。", "tips": "💡 【交友建议】：择善而从。"},
                            "property": {"title": "🏡 大限田宅不动产与买房方位指南", "text": f"【大限 {gz} 期间 · 不动产置业指南】首选朝向{dy_info['directions']}的户型。", "tips": "💡 【置业建议】：做好现金流压力测试。"},
                            "inner_world": {"title": "🧘 大限内心世界与精神修炼", "text": f"【大限 {gz} 期间 · 心灵内修与精神世界】", "tips": "💡 【内修建议】：活在当下，知足常乐。"}
                        }

                        liu_nian_list = []
                        for i in range(10):
                            ly_year = start_year + i
                            ly_age = start_age + i
                            try:
                                ly_solar = Solar.fromYmdHms(ly_year, 6, 1, 12, 0, 0)
                                ly_lunar = ly_solar.getLunar()
                                ly_gz = ly_lunar.getYearInGanZhi()
                                ly_gan, ly_zhi = ly_gz[0], ly_gz[1]
                                ly_star = get_shishen(day_gan, ly_gan)
                            except Exception: ly_gz, ly_gan, ly_zhi, ly_star = "甲子", "甲", "子", "比肩"

                            taisui_info = check_taisuibai(birth_year_zhi, ly_zhi)
                            ly_shensha = get_liunian_shensha(day_gan, birth_year_zhi, ly_zhi)

                            liu_yue_list = []
                            for m_idx, (m_gz, m_cn) in enumerate(month_gz_base):
                                m_star = get_shishen(day_gan, m_gz[0])
                                liu_yue_list.append({"month_num": m_idx + 1, "chinese_month": m_cn, "gan_zhi": m_gz, "main_star": m_star, "summary": f"{m_cn}（{m_gz} · {m_star}临值）：气场起伏，稳健为上。"})

                            ly_analysis = {
                                "taisui": taisui_info, "shensha": ly_shensha, "liuyue": liu_yue_list,
                                "career": {"title": f"💼 {ly_year}年事业方位", "text": f"流年主星【{ly_star}】临值。吉利方位：{dy_info['directions']}。", "tips": "💡 避免顶撞上司。"},
                                "wealth": {"title": f"💰 {ly_year}年财运投资", "text": f"求财大吉方：{dy_info['directions']}。", "tips": "💡 严禁高风险投机。"},
                                "health": {"title": f"🏥 {ly_year}年健康调理", "text": "注意劳逸结合，调理脾胃。", "tips": "💡 保证规律作息。"},
                                "marriage": {"title": f"💍 {ly_year}年婚姻感情", "text": "多包容体谅伴侣。", "tips": "💡 坦诚沟通。"},
                                "social": {"title": f"🤝 {ly_year}年交友人脉", "text": f"贵人生肖：{vips['vip']}。", "tips": "💡 保持边界感。"},
                                "accident": {"title": f"⚠️ {ly_year}年出行安全", "text": f"防范前往{dy_info['bad_directions']}方向。", "tips": "💡 遵守交通规则。"}
                            }
                            liu_nian_list.append({"year": ly_year, "age": ly_age, "gan_zhi": ly_gz, "main_star": ly_star, "analysis": ly_analysis})

                        dayun_schedule.append({"age": start_age, "start_year": start_year, "end_year": end_year, "gan_zhi": gz, "main_star": main_star, "sub_star": main_star, "status": status, "dayun_analysis": dayun_analysis_11, "liunian": liu_nian_list})
                    except Exception as dy_err: continue

                detailed_report = {"personality": {"summary": pers_summary, "strengths": [f"主星【{month_star}】：{ms_info.get('pros','')}"], "weaknesses": [f"主星【{month_star}】：{ms_info.get('cons','')}"], "global_analysis": global_analysis_11}}
                ai_report = f"【大师级真实八字分析报告 - {name}】"

                solar_display_str = f"{year}-{month}-{day} {time_formatted}"

                record = {"user_name": name, "gender": gender, "birth_year": year, "birth_month": month, "birth_day": day, "birth_hour": solar_display_str, "virtual_age": virtual_age, "lunar_date": lunar_str, "wang_du": wang_du, "ruo_du": ruo_du, "bazi_chart": chart, "five_elements": five_elements, "dayun_list": dayun_schedule, "detailed_report": detailed_report, "ai_report": ai_report}

                if supabase:
                    try: supabase.table("bazi_records").insert(record).execute()
                    except Exception: pass

                response_json = json.dumps({"status": "success", "data": record, "strength": strength_text}, ensure_ascii=False)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(response_json.encode('utf-8'))
            except Exception as err:
                print("💥 后端计算严重异常:", err, flush=True)
                traceback.print_exc()
                err_resp = json.dumps({"status": "error", "message": str(err)}, ensure_ascii=False)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(err_resp.encode('utf-8'))
        else: super().do_GET()

if __name__ == '__main__':
    print("--------------------------------------------------", flush=True)
    print("🚀 API Server Running OK on 0.0.0.0:8000", flush=True)
    print("--------------------------------------------------", flush=True)
    server = HTTPServer(('0.0.0.0', 8000), BaziAPIHandler)
    server.serve_forever()
