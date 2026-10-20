# -*- coding: utf-8 -*-
"""
八字核心计算与报告生成引擎 (Bazi Engine)
全方位终极稳健版：强化时间格式解析与多级字段容错，彻底杜绝前端 map 报错
"""
try:
    from lunar_python import Solar
except ImportError:
    Solar = None
from datetime import date
import re

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

# 传统藏干顺序：本气、中气、余气。用于检查资料完整性，不代替流派校准。
HIDDEN_STEMS = {
    "子":"癸", "丑":"己癸辛", "寅":"甲丙戊", "卯":"乙", "辰":"戊乙癸", "巳":"丙戊庚",
    "午":"丁己", "未":"己丁乙", "申":"庚壬戊", "酉":"辛", "戌":"戊辛丁", "亥":"壬甲"
}

def parse_birth_time(value):
    """明确的时间输入：支持 HH:MM、0..23 整点及 3/4 位 HHMM；拒绝歧义小数。"""
    if isinstance(value, bool):
        raise ValueError("出生时间格式错误")
    if isinstance(value, str) and re.fullmatch(r"\d{1,2}:\d{2}", value.strip()):
        hh, mm = map(int, value.strip().split(':'))
    elif isinstance(value, (int, str)) and re.fullmatch(r"\d{1,4}", str(value).strip()):
        raw = str(value).strip()
        n = int(raw)
        if len(raw) <= 2 and n <= 23:
            hh, mm = n, 0
        elif len(raw) in (3,4):
            hh, mm = divmod(n,100)
        else:
            raise ValueError("出生时间格式错误，请输入 13:45 或 1345")
    else:
        raise ValueError("出生时间格式错误，请输入 13:45 或 1345")
    if not (0 <= hh <= 23 and 0 <= mm <= 59):
        raise ValueError("出生时间超出 00:00–23:59")
    return hh, mm

def safe_year_ganzhi(year):
    """流年以立春年柱标示，取该公历年七月以避开立春边界。"""
    ec = Solar.fromYmdHms(year,7,1,12,0,0).getLunar().getEightChar()
    return ec.getYearGan()+ec.getYearZhi()

def _unverified_section(title):
    return {"title":title,"text":"尚未完成独立流派校准，不提供个人吉凶定论。", "tips":"请结合原始命盘与专业判断。", "strengths":[], "weaknesses":[], "pros":[], "cons":[]}

class BaziEngine:
    @staticmethod
    def calculate(req_data):
        if Solar is None:
            raise RuntimeError("缺少 lunar_python 依赖；请先安装 requirements.txt 所列依赖")
        if not isinstance(req_data,dict):
            raise ValueError("请求必须为 JSON 对象")
        name = req_data.get('name','')
        gender = req_data.get('gender','男')
        if not isinstance(name,str) or len(name.strip()) > 80:
            raise ValueError("姓名格式不正确")
        if gender not in ('男','女'):
            raise ValueError("性别必须为男或女")
        def read_int(key):
            val = req_data.get(key)
            if isinstance(val,bool) or not isinstance(val,(int,str)) or not re.fullmatch(r"\d{1,4}",str(val)):
                raise ValueError(f"{key} 必须为整数")
            return int(val)
        year,month,day = (read_int(k) for k in ('year','month','day'))
        if not 1900 <= year <= 2099:
            raise ValueError("出生年份仅支持 1900–2099")
        try:
            date(year,month,day)
        except ValueError:
            raise ValueError("出生日期不是有效公历日期") from None
        hh,mm = parse_birth_time(req_data.get('hour'))
        if (year,month,day) > (date.today().year,date.today().month,date.today().day):
            raise ValueError("出生日期不能晚于今天")
        solar = Solar.fromYmdHms(year,month,day,hh,mm,0)
        lunar = solar.getLunar()
        ec = lunar.getEightChar()
        ec.setSect(1)  # 晚子时换日：作为明确配置，尚需流派对照校准
        day_gan, day_zhi = ec.getDayGan(),ec.getDayZhi()
        specs = [('year','Year'),('month','Month'),('day','Day'),('hour','Time')]
        pillars = {}
        element_counts = {x:0 for x in ('金','木','水','火','土')}
        for key,prefix in specs:
            gan=getattr(ec,f'get{prefix}Gan')()
            zhi=getattr(ec,f'get{prefix}Zhi')()
            if gan not in GAN_ELEMENTS or zhi not in ZHI_ELEMENTS:
                raise ValueError("历法库返回无效干支")
            element_counts[GAN_ELEMENTS[gan]] += 1
            element_counts[ZHI_ELEMENTS[zhi]] += 1
            hides = list(getattr(ec,f'get{prefix}HideGan')())
            if not hides or any(h not in GAN_ELEMENTS for h in hides):
                hides=list(HIDDEN_STEMS[zhi])
            pillars[f'{key}_pillar']={
                'gan':gan,'zhi':zhi,'gan_elem':GAN_ELEMENTS[gan],'zhi_elem':ZHI_ELEMENTS[zhi],
                'shishen':'命主' if key=='day' else get_shishen(day_gan,gan),
                'cangan_details':[{'gan':h,'star':get_shishen(day_gan,h)} for h in hides],
                'yun':'待校准','shensha':[],
                'nayin':getattr(ec,f'get{prefix}NaYin')(),
            }
        mg, mz = pillars['month_pillar']['gan'],pillars['month_pillar']['zhi']
        yg, yz = pillars['year_pillar']['gan'],pillars['year_pillar']['zhi']
        tg, tz = pillars['hour_pillar']['gan'],pillars['hour_pillar']['zhi']
        ty_g,ty_z=calc_tai_yuan(mg,mz)
        tx_g,tx_z=calc_tai_xi(day_gan,day_zhi)
        mc_g,mc_z=calc_ming_gong(yg,mz,tz)
        pillars['extra']={
            'tai_yuan':{'gan':ty_g,'zhi':ty_z},
            'tai_xi':{'gan':tx_g,'zhi':tx_z,'star':get_shishen(day_gan,tx_g)},
            'ming_gong':{'gan':mc_g,'zhi':mc_z},
            'ming_ge':'待流派校准','ming_gua':'待校准',
            'day_kong':get_kongwang(day_gan,day_zhi),
            'year_kong':get_kongwang(yg,yz),
            'yong_xi':'未评估（不以简单五行计数断定）',
            'wang_xiang':'未评估',
            'strength_details':'旺衰、调候与格局需综合月令、透干、通根及流派规则判断。',
            'pillar_scan':['四柱结构已计算；刑冲合害的吉凶判断尚未校准。'],
        }
        sections=('marriage','career','wealth','health','parents','siblings','children','accident','social','property','inner_world')
        dayun=[]
        try:
            yun=ec.getYun(1 if gender=='男' else 0)
            for dy in yun.getDaYun():
                if dy.getIndex()==0: continue
                gz=dy.getGanZhi()
                start_age=dy.getStartAge()
                start_year=dy.getStartYear()
                liunian=[]
                for i in range(10):
                    ly_year=start_year+i
                    ly_gz=safe_year_ganzhi(ly_year) if 1900<=ly_year<=2099 else '未计算'
                    ly_gan=ly_gz[0] if ly_gz!='未计算' else None
                    analysis={k:_unverified_section(k) for k in ('career','wealth','health','marriage','social','accident')}
                    analysis.update({'taisui':'未评估','shensha':[],'liuyue':[]})
                    liunian.append({'year':ly_year,'age':start_age+i,'gan_zhi':ly_gz,
                                    'main_star':get_shishen(day_gan,ly_gan) if ly_gan else '未计算','analysis':analysis})
                dayun.append({'age':start_age,'start_year':start_year,'end_year':start_year+9,
                              'gan_zhi':gz,'main_star':get_shishen(day_gan,gz[0]),'status':'unassessed',
                              'dayun_analysis':{k:_unverified_section(k) for k in sections},'liunian':liunian})
        except Exception as exc:
            # 不伪造大运；将失败原因写入可审计的诊断字段。
            dayun=[]
            dayun_error=f'大运计算未完成：{type(exc).__name__}'
        else:
            dayun_error=None
        lunar_label=f"农历 {lunar.getYear()}年 {lunar.getMonth()}月 {lunar.getDay()}日"
        return {
            'user_name':name.strip(),'gender':gender,'birth_year':year,'birth_month':month,'birth_day':day,
            'birth_hour':f'{year:04d}-{month:02d}-{day:02d} {hh:02d}:{mm:02d}',
            'virtual_age':date.today().year-year+1,'lunar_date':lunar_label,
            'wang_du':'未评估','ruo_du':'未评估',
            'bazi_chart':pillars,'five_elements':element_counts,'dayun_list':dayun,
            'detailed_report':{'personality':{'summary':'四柱已排出。个性及吉凶论断尚未校准。',
                'strengths':[],'weaknesses':[],
                'global_analysis':{k:_unverified_section(k) for k in sections}}},
            'ai_report':'本报告提供四柱与运程干支计算，不提供未经验证的吉凶结论。',
            'calculation_audit':{
                'calendar_library':'lunar_python','calendar':'公历输入 / 农历转换',
                'sect':1,'sect_note':'子时换日采用 lunar_python sect=1；需独立对照',
                'time_zone':'用户输入的当地钟表时间；未做真太阳时或时区换算',
                'four_pillars':'library_computed','five_elements':'8个显干支五行计数，不代表旺衰',
                'dayun_status':'computed' if dayun else 'unavailable',
                'dayun_error':dayun_error,'liuyue_status':'not_implemented',
                'strength_status':'not_calibrated','interpretation_status':'not_calibrated',
            }
        }
