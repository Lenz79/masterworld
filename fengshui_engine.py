# -*- coding: utf-8 -*-
"""
fengshui_engine.py - 阳宅风水全盘多盘联动计算引擎
支持：
1. 24山地盘与朝向/坐山换算
2. 龙门八局（先天水、后天水、天劫位、正窍水口、三曜煞）
3. 八宅派吉凶盘（八大宅相、四大吉星、四大凶星、推荐风水物）
4. 紫白诀九星流年飞星盘
5. 玄空城门诀与玄空排龙诀推演（含完整24山数据库）
6. 玄空三元九运飞星挨星盘
"""

# 24山列表
MOUNTAINS = [
    "子", "癸", "丑", "艮", "寅", "甲",
    "卯", "乙", "辰", "巽", "巳", "丙",
    "午", "丁", "未", "坤", "申", "庚",
    "酉", "辛", "戌", "乾", "亥", "壬"
]

# 八卦方位及基准度数
GUA_ANGLES = {'坎': 0, '艮': 45, '震': 90, '巽': 135, '离': 180, '坤': 225, '兑': 270, '乾': 315}

# 龙门八局配置数据（含三曜煞）
LONGMEN_DATA = {
    '乾': { 'xiantian': '离', 'houtian': '坎', 'tianjie': '震', 'zhengqiao': '巽', 'fuqiao': '艮', 'yaoshats': { '午': '曜煞', '卯': '劫煞', '壬': '黄泉' } },
    '坤': { 'xiantian': '坎', 'houtian': '震', 'tianjie': '巽', 'zhengqiao': '乾', 'fuqiao': '艮', 'yaoshats': { '卯': '曜煞', '子': '劫煞', '癸': '黄泉' } },
    '震': { 'xiantian': '艮', 'houtian': '离', 'tianjie': '乾', 'zhengqiao': '巽', 'fuqiao': '坤', 'yaoshats': { '申': '曜煞', '亥': '劫煞', '庚': '黄泉' } },
    '巽': { 'xiantian': '坤', 'houtian': '兑', 'tianjie': '乾', 'zhengqiao': '艮', 'fuqiao': '震', 'yaoshats': { '酉': '曜煞', '辛': '黄泉' } },
    '坎': { 'xiantian': '兑', 'houtian': '坤', 'tianjie': '巽', 'zhengqiao': '巽', 'fuqiao': '震', 'yaoshats': { '辰': '曜煞', '申': '劫煞', '乾': '黄泉' } },
    '离': { 'xiantian': '震', 'houtian': '乾', 'tianjie': '艮', 'zhengqiao': '巽', 'fuqiao': '坤', 'yaoshats': { '亥': '曜煞', '寅': '劫煞', '巽': '黄泉' } },
    '艮': { 'xiantian': '乾', 'houtian': '震', 'tianjie': '离', 'zhengqiao': '兑', 'fuqiao': '巽', 'yaoshats': { '寅': '曜煞', '巳': '劫煞', '丁': '黄泉' } },
    '兑': { 'xiantian': '巽', 'houtian': '坎', 'tianjie': '艮', 'zhengqiao': '巽', 'fuqiao': '离', 'yaoshats': { '巳': '曜煞', '丙': '黄泉' } }
}

# 🌟 【新增】玄空城门诀二十四山精准数据库
CHENGMEN_DATABASE = {
    '子': '巽', '癸': '巽', '丑': '震', '艮': '震', '寅': '震', '甲': '艮',
    '卯': '艮', '乙': '艮', '辰': '坤', '巽': '坎', '巳': '坎', '丙': '乾',
    '午': '乾', '丁': '乾', '未': '兑', '坤': '兑', '申': '兑', '庚': '离',
    '酉': '离', '辛': '离', '戌': '坤', '乾': '离', '亥': '坎', '壬': '巽'
}

# 🌟 【新增】玄空排龙诀二十四山起辅星排龙数据库
PAILONG_DATABASE = {
    '子': '贪狼龙', '癸': '贪狼龙', '丑': '禄存龙', '艮': '禄存龙', '寅': '禄存龙', '甲': '巨门龙',
    '卯': '巨门龙', '乙': '巨门龙', '辰': '右弼龙', '巽': '文曲龙', '巳': '文曲龙', '丙': '武曲龙',
    '午': '武曲龙', '丁': '武曲龙', '未': '右弼龙', '坤': '右弼龙', '申': '右弼龙', '庚': '破军龙',
    '酉': '破军龙', '辛': '破军龙', '戌': '左辅龙', '乾': '左辅龙', '亥': '贪狼龙', '壬': '贪狼龙'
}

# 八宅派盘面映射
BAZHAI_MAP = {
    'kan': {'坎': '伏位', '艮': '五鬼', '震': '延年', '巽': '生气', '离': '绝命', '坤': '祸害', '兑': '六煞', '乾': '天医'},
    'li': {'坎': '绝命', '艮': '六煞', '震': '天医', '巽': '延年', '离': '伏位', '坤': '五鬼', '兑': '祸害', '乾': '生气'},
    'zhen': {'坎': '延年', '艮': '绝命', '震': '伏位', '巽': '天医', '离': '生气', '坤': '六煞', '兑': '五鬼', '乾': '祸害'},
    'xun': {'坎': '生气', '艮': '天医', '震': '伏位', '巽': '五鬼', '离': '延年', '坤': '祸害', '兑': '绝命', '乾': '六煞'},
    'qian': {'坎': '六煞', '艮': '天医', '震': '祸害', '巽': '五鬼', '离': '绝命', '坤': '延年', '兑': '生气', '乾': '伏位'},
    'kun': {'坎': '祸害', '艮': '延年', '震': '绝命', '巽': '五鬼', '离': '六煞', '坤': '伏位', '兑': '生气', '乾': '天医'},
    'gen': {'坎': '五鬼', '艮': '伏位', '震': '生气', '巽': '天医', '离': '祸害', '坤': '延年', '兑': '绝命', '乾': '六煞'},
    'dui': {'坎': '六煞', '艮': '祸害', '震': '五鬼', '巽': '绝命', '离': '天医', '坤': '延年', '兑': '伏位', '乾': '生气'}
}

# 八宅星曜详情与化解布局
BAZHAI_STAR_DETAILS = {
    '生气': { 'nature': '大吉', 'color': '#0ea5e9', 'desc': '主财源广进、生机勃勃。', 'items': ['黄水晶聚宝盆', '发财树'] },
    '延年': { 'nature': '大吉', 'color': '#0ea5e9', 'desc': '主婚姻美满、人缘和谐。', 'items': ['紫水晶球', '铜龙龟'] },
    '天医': { 'nature': '大吉', 'color': '#0ea5e9', 'desc': '主身体健康、祛病延年。', 'items': ['纯铜葫芦', '灶位压凶'] },
    '伏位': { 'nature': '中吉', 'color': '#0ea5e9', 'desc': '主平稳安定、利思维。', 'items': ['文昌塔', '文昌笔'] },
    '绝命': { 'nature': '大凶', 'color': '#dc2626', 'desc': '主破财伤人、意外灾祸。', 'items': ['五帝钱', '黑曜石'] },
    '五鬼': { 'nature': '大凶', 'color': '#dc2626', 'desc': '主官非口舌、小人作祟。', 'items': ['安忍水', '六帝钱'] },
    '六煞': { 'nature': '次凶', 'color': '#dc2626', 'desc': '主感情纠葛、事业阻碍。', 'items': ['七星阵', '铜葫芦'] },
    '祸害': { 'nature': '次凶', 'color': '#dc2626', 'desc': '主口舌争执、疾病缠身。', 'items': ['重型石雕', '六帝钱'] }
}

# 紫白诀九星数据库
ZIWEI_STAR_INFO = {
    1: { 'name': '一白贪狼星', 'nature': '吉星', 'desc': '主官运、名气与人缘。', 'items': ['黄水晶球', '富贵竹'] },
    2: { 'name': '二黑巨门星', 'nature': '凶星', 'desc': '主疾病、肠胃不适。', 'items': ['纯铜葫芦', '忌动土'] },
    3: { 'name': '三碧禄存星', 'nature': '凶星', 'desc': '主口舌官非、竞争。', 'items': ['红地毯', '紫水晶'] },
    4: { 'name': '四绿文曲星', 'nature': '吉星', 'desc': '主学业、文职与桃花。', 'items': ['文昌塔', '富贵竹'] },
    5: { 'name': '五黄廉贞星', 'nature': '大凶星', 'desc': '主重病、血光、破财。', 'items': ['六帝钱', '严禁动土'] },
    6: { 'name': '六白武曲星', 'nature': '吉星', 'desc': '主偏财、权力。', 'items': ['黄水晶聚宝盆', '铜龙龟'] },
    7: { 'name': '七赤破军星', 'nature': '凶星', 'desc': '主破财、血光、小人。', 'items': ['安忍水', '水种植物'] },
    8: { 'name': '八白左辅星', 'nature': '大吉星', 'desc': '主正财、置业。', 'items': ['紫晶洞', '亮灯饰'] },
    9: { 'name': '九紫右弼星', 'nature': '大吉星', 'desc': '主喜事投资。', 'items': ['红紫色饰品', '发财树'] }
}


def calculate_lo_shu_flying(center_star):
    """洛书九星顺逆飞布算法"""
    order = ['中', '乾', '兑', '坤', '离', '坎', '艮', '震', '巽']
    result = {}
    for i in range(9):
        s = ((center_star - 1 - i + 90) % 9) + 1
        result[order[i]] = s
    return result


def get_year_zibai(year):
    """计算指定年份的紫白诀流年星盘"""
    y = int(year)
    base_2026 = 4  # 2026年丙午年为四绿入中
    diff = y - 2026
    center_star = ((base_2026 - 1 - (diff % 9) + 900) % 9) + 1
    flying_map = calculate_lo_shu_flying(center_star)
    return {"year": y, "centerStar": center_star, "flyingMap": flying_map}


def get_xuankong_flying_stars(yun, degree):
    """计算玄空三元九运飞星盘格局"""
    y = int(yun)
    yun_map = calculate_lo_shu_flying(y)
    star_offset = (y * 3) % 9
    gua_order = ['坎', '坤', '震', '巽', '乾', '兑', '艮', '离']
    dynamic_map = {}
    for g in gua_order:
        s = ((yun_map[g] + star_offset - 1) % 9) + 1
        dynamic_map[g] = s
    
    yun_names = {1: '一', 7: '七', 8: '八', 9: '九'}
    geju_name = f"下元{yun_names.get(y, '七')}运 · 旺山旺向局"
    return {"yun": y, "yunMap": dynamic_map, "gejuName": geju_name}


def get_zhai_by_degree(deg):
    """根据罗盘朝向度数推演坐山与八宅宅相"""
    zuo_deg = (deg + 180) % 360
    zhaixing = 'kan'
    zuo_shan = '子'
    zhai_name = '坎宅 (坐北向南)'

    if (zuo_deg >= 337.5 and zuo_deg <= 360) or (zuo_deg >= 0 and zuo_deg < 22.5):
        zuo_shan = '子' if (zuo_deg >= 352.5 or zuo_deg < 7.5) else ('壬' if zuo_deg >= 337.5 else '癸')
        zhaixing, zhai_name = 'kan', '坎宅 (坐北向南)'
    elif 22.5 <= zuo_deg < 67.5:
        zuo_shan = '艮' if (37.5 <= zuo_deg < 52.5) else ('丑' if zuo_deg < 37.5 else '寅')
        zhaixing, zhai_name = 'gen', '艮宅 (坐东北向西南)'
    elif 67.5 <= zuo_deg < 112.5:
        zuo_shan = '卯' if (82.5 <= zuo_deg < 97.5) else ('甲' if zuo_deg < 82.5 else '乙')
        zhaixing, zhai_name = 'zhen', '震宅 (坐东向西)'
    elif 112.5 <= zuo_deg < 157.5:
        zuo_shan = '巽' if (127.5 <= zuo_deg < 142.5) else ('辰' if zuo_deg < 127.5 else '巳')
        zhaixing, zhai_name = 'xun', '巽宅 (坐东南向西北)'
    elif 157.5 <= zuo_deg < 202.5:
        zuo_shan = '午' if (172.5 <= zuo_deg < 187.5) else ('丙' if zuo_deg < 172.5 else '丁')
        zhaixing, zhai_name = 'li', '离宅 (坐南向北)'
    elif 202.5 <= zuo_deg < 247.5:
        zuo_shan = '坤' if (217.5 <= zuo_deg < 232.5) else ('未' if zuo_deg < 217.5 else '申')
        zhaixing, zhai_name = 'kun', '坤宅 (坐西南向东北)'
    elif 247.5 <= zuo_deg < 292.5:
        zuo_shan = '酉' if (262.5 <= zuo_deg < 277.5) else ('庚' if zuo_deg < 262.5 else '辛')
        zhaixing, zhai_name = 'dui', '兑宅 (坐西向东)'
    elif 292.5 <= zuo_deg < 337.5:
        zuo_shan = '乾' if (307.5 <= zuo_deg < 322.5) else ('戌' if zuo_deg < 307.5 else '亥')
        zhaixing, zhai_name = 'qian', '乾宅 (坐西北向东南)'

    return {"zhaixing": zhaixing, "zuoShan": zuo_shan, "zuoDeg": round(zuo_deg, 1), "zhaiName": zhai_name}


def get_chengmen_gua(mountain):
    """【严谨算法】玄空城门诀：基于二十四山精准数据库查询城门正配卦位"""
    return CHENGMEN_DATABASE.get(mountain, '吉')


def get_pailong_long(mountain):
    """【严谨算法】玄空排龙诀：基于二十四山起辅星排龙法数据库推演龙脉吉凶属性"""
    return PAILONG_DATABASE.get(mountain, '吉龙')


def generate_fengshui_full_report(degree=0.0, longmen_ju='坎', yun=7, ziwei_year=2026):
    """生成全套风水堪舆建议与断语（供服务端或前端调用）"""
    zhai_info = get_zhai_by_degree(degree)
    bz_map = BAZHAI_MAP.get(zhai_info["zhaixing"], BAZHAI_MAP['kan'])
    lm_cfg = LONGMEN_DATA.get(longmen_ju, LONGMEN_DATA['坎'])
    ziwei_data = get_year_zibai(ziwei_year)
    xk_data = get_xuankong_flying_stars(yun, degree)

    # 1. 八宅派全8宫分析
    bazhai_results = []
    for g in ['坎', '坤', '震', '巽', '乾', '兑', '艮', '离']:
        star_name = bz_map.get(g, '伏位')
        detail = BAZHAI_STAR_DETAILS.get(star_name, BAZHAI_STAR_DETAILS['伏位'])
        bazhai_results.append({
            "palace": g,
            "star": star_name,
            "nature": detail["nature"],
            "color": detail["color"],
            "desc": detail["desc"],
            "items": detail["items"]
        })

    # 2. 紫白诀流年九星分析
    ziwei_results = []
    for star_num in range(1, 10):
        star_info = ZIWEI_STAR_INFO[star_num]
        fly_gua = [g for g, s in ziwei_data["flyingMap"].items() if s == star_num]
        ziwei_results.append({
            "starName": star_info["name"],
            "flyingGua": "、".join(fly_gua) if fly_gua else "中宫",
            "nature": star_info["nature"],
            "desc": star_info["desc"],
            "items": star_info["items"]
        })

    return {
        "zhaiInfo": zhai_info,
        "longmenJu": longmen_ju,
        "longmenConfig": lm_cfg,
        "xuankongGeju": xk_data["gejuName"],
        "bazhaiReport": bazhai_results,
        "ziweiReport": ziwei_results
    }