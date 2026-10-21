#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
AI 智能玄学 SaaS 平台 - 紫微斗数核心引擎 (ziwei_engine.py)
功能包含：
1. 十天干、十二地支、十二宫位基础常数。
2. 三合派与飞星派共用的吉星、六煞星、杂曜数据结构与分类。
3. 生年四化及飞星派核心流转逻辑。
4. 基础排盘定位与三方四正关联查询。
====================================================================
"""

# ==================== 一、 基础常数与数组定义 ====================

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 十二宫位固定顺序（以命宫为起点逆时针排列）
PALACE_NAMES = [
    "命宫", "兄弟宫", "夫妻宫", "子女宫", 
    "财帛宫", "疾厄宫", "迁移宫", "交友宫", 
    "事业宫", "田宅宫", "福德宫", "父母宫"
]

# 五行局定义
FIVE_ELEMENTS_BUREAU = {
    "水二局": 2,
    "木三局": 3,
    "金四局": 4,
    "土五局": 5,
    "火六局": 6
}


# ==================== 二、 星曜与煞星分类数据库 ====================

# 1. 十四主星
MAJOR_STARS = [
    "紫微", "天机", "太阳", "武曲", "天同", "廉贞",
    "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"
]

# 2. 六吉星（三合重组合、飞星重契约/贵人）
SIX_LUCKY_STARS = {
    "文昌": {"category": "吉星", "nature": "主科甲、文才、契约、文书"},
    "文曲": {"category": "吉星", "nature": "主才艺、口才、契约、桃花"},
    "左辅": {"category": "吉星", "nature": "主助力、贵人、伙伴、成双"},
    "右弼": {"category": "吉星", "nature": "主助力、暗贵、包容、对宫延伸"},
    "天魁": {"category": "吉星", "nature": "主昼贵人、机遇、公开提携"},
    "天钺": {"category": "吉星", "nature": "主夜贵人、机遇、暗中相助"}
}

# 3. 六煞星（三合重夹冲破败、飞星重动象与突发忌冲）
SIX_SHA_STARS = {
    "擎羊": {"category": "煞星", "nature": "北斗·刑星，主刚烈、急躁、血光、手术、突发阻碍"},
    "陀罗": {"category": "煞星", "nature": "北斗·忌星，主拖延、纠缠、暗中阴谋、固执、是非"},
    "火星": {"category": "煞星", "nature": "南斗·暴星，主刚烈、爆发、暴躁、突发"},
    "铃星": {"category": "煞星", "nature": "南斗·煞星，主暗发、阴险、声音、心计"},
    "地空": {"category": "煞星", "nature": "主虚空、精神世界、灵性、计划落空、破财"},
    "地劫": {"category": "煞星", "nature": "主大起大落、破败、玄学缘分、财来财去"}
}

# 4. 其他重要杂曜与四化飞星特需星曜
MINOR_STARS = {
    "禄存": {"category": "吉曜", "nature": "北斗·富星，主实禄、解厄、固守（前后必遭羊陀夹）"},
    "天刑": {"category": "杂曜", "nature": "主自律、官非、医药、刑律"},
    "天姚": {"category": "桃花", "nature": "主异性缘、魅力、风流、人际"},
    "红鸾": {"category": "桃花", "nature": "主婚姻、喜庆、桃花"},
    "天喜": {"category": "桃花", "nature": "主喜庆、好心情、人缘"}
}


# ==================== 三、 四化核心数据与飞星规则 ====================

# 生年四化对照表（天干 -> 化禄, 化权, 化科, 化忌）
BIRTH_FOUR_TRANSFORMATIONS = {
    "甲": {"化禄": "廉贞", "化权": "破军", "化科": "武曲", "化忌": "太阳"},
    "乙": {"化禄": "天机", "化权": "天梁", "化科": "紫微", "化忌": "太阴"},
    "丙": {"化禄": "天同", "化权": "天机", "化科": "文昌", "化忌": "廉贞"},
    "丁": {"化禄": "太阴", "化权": "天同", "化科": "天机", "化忌": "巨门"},
    "戊": {"化禄": "贪狼", "化权": "太阴", "化科": "右弼", "化忌": "天机"},
    "己": {"化禄": "武曲", "化权": "贪狼", "化科": "天梁", "化忌": "文曲"},
    "庚": {"化禄": "太阳", "化权": "武曲", "化科": "太阴", "化忌": "天同"},
    "辛": {"化禄": "巨门", "化权": "太阳", "化科": "文曲", "化忌": "文昌"},
    "壬": {"化禄": "天梁", "化权": "紫微", "化科": "左辅", "化忌": "武曲"},
    "癸": {"化禄": "破军", "化权": "巨门", "化科": "太阴", "化忌": "贪狼"}
}


# ==================== 四、 宫位关联与三方四正核心算法 ====================

class ZiWeiEngine:
    def __init__(self, birth_year_gan: str):
        """
        初始化紫微引擎
        :param birth_year_gan: 出生年天干，例如 "丙"
        """
        self.birth_gan = birth_year_gan
        self.birth_four = BIRTH_FOUR_TRANSFORMATIONS.get(birth_year_gan, {})

    def get_birth_four_transformations(self) -> dict:
        """获取生年四化"""
        return self.birth_four

    @staticmethod
    def get_opposite_palace(palace_index: int) -> int:
        """
        计算对宫索引 (相差6位)
        :param palace_index: 0-11 的宫位索引
        :return: 对宫索引
        """
        return (palace_index + 6) % 12

    @staticmethod
    def get_san_he_palaces(palace_index: int) -> list:
        """
        计算三合方索引 (隔4位，共3个宫位构成三合)
        :param palace_index: 0-11 的宫位索引
        :return: 包含三个宫位索引的列表 [本宫, 三合1, 三合2]
        """
        return [
            palace_index,
            (palace_index + 4) % 12,
            (palace_index + 8) % 12
        ]

    def get_san_fang_si_zheng(self, palace_index: int) -> dict:
        """
        计算三方四正（核心论断区间：本宫 + 对宫 + 三合方）
        :param palace_index: 宫位索引
        :return: 包含本宫、对宫、三合宫的字典
        """
        opposite = self.get_opposite_palace(palace_index)
        san_he = self.get_san_he_palaces(palace_index)
        return {
            "ben_gong": palace_index,
            "dui_gong": opposite,
            "san_he": [p for p in san_he if p != palace_index]
        }

    @staticmethod
    def check_sha_xing_presence(palace_stars: list) -> dict:
        """
        检查某宫位内包含的煞星情况（三合派/飞星派通用检索）
        :param palace_stars: 该宫位内的星曜列表
        :return: 命盘该宫见煞统计
        """
        found_shas = [star for star in palace_stars if star in SIX_SHA_STARS]
        found_lucy = [star for star in palace_stars if star in SIX_LUCKY_STARS]
        return {
            "has_sha": len(found_shas) > 0,
            "sha_stars": found_shas,
            "lucky_stars": found_lucy
        }



# 下列规则采用常见传统安星口径；四化表沿用用户原始文件。
# 不同派别差异须通过参考命盘校验后才能用于正式命理报告。
from datetime import date

PALACE_ORDER = ["命宫", "兄弟宫", "夫妻宫", "子女宫", "财帛宫", "疾厄宫", "迁移宫", "交友宫", "事业宫", "田宅宫", "福德宫", "父母宫"]
GAN_START = {"甲":2,"己":2,"乙":4,"庚":4,"丙":6,"辛":6,"丁":8,"壬":8,"戊":0,"癸":0}
BUREAU_BY_ELEMENT = {"水":("水二局",2),"木":("木三局",3),"金":("金四局",4),"土":("土五局",5),"火":("火六局",6)}
NAYIN_ELEMENTS = ["金","火","木","土","金","火","水","土","金","木","水","土","火","木","水","金","火","木","土","金","火","水","土","金","木","水","土","火","木","水"]
FOUR_KEYS = {"化禄":"lu","化权":"quan","化科":"ke","化忌":"ji"}
ANIMALS = list("鼠牛虎兔龙蛇马羊猴鸡狗猪")

class ZiweiEngine(ZiWeiEngine):
    def __init__(self, name="", gender="男", year=1988, month=11, day=12, hour=13, minute=0, calendar="solar"):
        self.name = str(name or "命主")
        self.gender = str(gender)
        self.year, self.month, self.day = int(year), int(month), int(day)
        raw_hour = str(hour).strip()
        if ':' in raw_hour:
            h,m = raw_hour.split(':',1); self.hour,self.minute=int(h),int(m)
        elif raw_hour.isdigit() and int(raw_hour)>23:
            self.hour,self.minute=divmod(int(raw_hour),100)
        else:
            self.hour,self.minute=int(hour),int(minute)
        if not (0<=self.hour<=23 and 0<=self.minute<=59): raise ValueError('出生时间不合法')
        self.calendar=calendar
        if self.gender not in ('男','女','男 (乾造)','女 (坤造)'): raise ValueError('性别必须为男或女')
        if calendar not in ('solar','lunar'): raise ValueError('calendar 只能是 solar 或 lunar')
        try:
            from lunar_python import Solar, Lunar
        except ImportError as exc:
            raise RuntimeError('缺少 lunar_python，请执行 pip install -r requirements.txt') from exc
        if calendar=='solar':
            date(self.year,self.month,self.day)
            self.solar=Solar.fromYmdHms(self.year,self.month,self.day,self.hour,self.minute,0)
            self.lunar=self.solar.getLunar()
        else:
            if not 1<=abs(self.month)<=12: raise ValueError('农历月份请输入 1 至 12；闰月请使用负数')
            self.lunar=Lunar.fromYmdHms(self.year,self.month,self.day,self.hour,self.minute,0)
            self.solar=self.lunar.getSolar()
        self.birth_gan=self.lunar.getYearGan()
        super().__init__(self.birth_gan)

    def calculate_full_chart(self):
        ly,lm,ld=self.lunar.getYear(),abs(self.lunar.getMonth()),self.lunar.getDay()
        if ld<1 or ld>30: raise ValueError('农历日期无效')
        hi=((self.hour+1)//2)%12
        birth_shichen=DI_ZHI[hi]+'时'
        birth_time_label=f'{birth_shichen}（{self.hour:02d}:{self.minute:02d}）'
        # 寅宫为正月，顺数生月；逆数生时为命宫，顺数生时为身宫
        month_idx=(2+lm-1)%12
        ming=(month_idx-hi)%12
        shen=(month_idx+hi)%12
        gan_by_zhi={DI_ZHI[(2+i)%12]:TIAN_GAN[(GAN_START[self.birth_gan]+i)%10] for i in range(12)}
        ming_gan=gan_by_zhi[DI_ZHI[ming]]
        sexagenary=(TIAN_GAN.index(ming_gan)*12+DI_ZHI.index(DI_ZHI[ming])*10)%60
        # 60甲子索引以同余方式定位，纳音每两位同一元素
        pair=next(i for i in range(60) if i%10==TIAN_GAN.index(ming_gan) and i%12==ming)
        bureau_name,bureau=BUREAU_BY_ELEMENT[NAYIN_ELEMENTS[pair//2]]
        # 紫微星安法：以生日与局数求商余，补至整除并按补数奇偶顺逆定位
        q,r=divmod(ld,bureau)
        if r:
            supplement=bureau-r
            zi_pos=(2+q+(supplement if supplement%2==0 else -supplement))%12
        else:
            zi_pos=(2+q-1)%12
        # 紫微系逆行；天府系顺行。修正天府镜像起点（旧版整体偏移一宫）
        stars={z:[] for z in DI_ZHI}
        def put(star,idx): stars[DI_ZHI[idx%12]].append(star)
        for star,offset in {'紫微':0,'天机':-1,'太阳':-3,'武曲':-4,'天同':-5,'廉贞':-8}.items():put(star,zi_pos+offset)
        fu_pos=(4-zi_pos)%12
        for star,offset in {'天府':0,'太阴':1,'贪狼':2,'巨门':3,'天相':4,'天梁':5,'七杀':6,'破军':10}.items():put(star,fu_pos+offset)
        # 常用六吉星、禄存与羊陀；火铃按年支三合及出生时辰安置
        put('左辅',(4+lm-1)%12);put('右弼',(10-(lm-1))%12)
        put('文昌',(10-hi)%12);put('文曲',(4+hi)%12)
        kui_yue={'甲':(1,7),'戊':(1,7),'庚':(1,7),'乙':(0,8),'己':(0,8),'丙':(11,9),'丁':(11,9),'辛':(6,2),'壬':(3,5),'癸':(3,5)}
        k,y=kui_yue[self.birth_gan];put('天魁',k);put('天钺',y)
        lu_map={'甲':2,'乙':3,'丙':5,'丁':6,'戊':5,'己':6,'庚':8,'辛':9,'壬':11,'癸':0}
        lu=lu_map[self.birth_gan];put('禄存',lu);put('擎羊',lu+1);put('陀罗',lu-1)
        put('地空',11-hi);put('地劫',11+hi)
        year_zhi=self.lunar.getYearZhi(); group=DI_ZHI.index(year_zhi)%4
        fire_start={0:2,1:3,2:1,3:9}[group];bell_start={0:10,1:10,2:3,3:10}[group]
        put('火星',fire_start+hi);put('铃星',bell_start+hi)
        # V8.8：四颗常见杂曜的传统安星规则（独立列出，待文墨同设置样盘核验）
        # 红鸾：子年起卯，逆数年支；天喜与红鸾对冲。
        # 天刑：正月起酉，顺数生月；天姚：正月起丑，顺数生月。
        year_idx=DI_ZHI.index(year_zhi)
        extra_positions={
            '红鸾': (3-year_idx)%12,
            '天喜': (9-year_idx)%12,
            '天刑': (9+lm-1)%12,
            '天姚': (1+lm-1)%12,
        }
        for star,idx in extra_positions.items(): put(star,idx)
        # V8.15: 第二批常见辅杂曜，按公开流传的传统口诀试算。
        # 不同派别安星细节可能不同；此批尚未与文墨天机逐宫核对。
        horse_by_group={0:2, 1:11, 2:8, 3:5}  # 申子辰寅、巳酉丑亥、寅午戌申、亥卯未巳
        left_pos=(4+lm-1)%12
        right_pos=(10-(lm-1))%12
        # 三台：左辅宫起初一顺数生日；八座：右弼宫起初一逆数生日。
        # 台辅：子时午宫起顺数；封诰：子时寅宫起顺数。
        # 龙池：子年辰宫起顺数；凤阁：子年戌宫起逆数。
        # 天才/天寿：命宫/身宫起子年顺数。
        # 孤辰寡宿：以生年三会方定孤寡位置。
        orphan_group={0:(2,10),1:(5,1),2:(8,4),3:(11,7)}
        orphan_group_id=next(i for i,group_set in enumerate(({11,0,1},{2,3,4},{5,6,7},{8,9,10})) if year_idx in group_set)
        orphan, widow=orphan_group[orphan_group_id]
        extended_positions={
            '天马':horse_by_group[group],
            '三台':(left_pos+ld-1)%12,
            '八座':(right_pos-(ld-1))%12,
            '台辅':(6+hi)%12,
            '封诰':(2+hi)%12,
            '龙池':(4+year_idx)%12,
            '凤阁':(10-year_idx)%12,
            '天才':(ming+year_idx)%12,
            '天寿':(shen+year_idx)%12,
            '孤辰':orphan,
            '寡宿':widow,
        }
        for star,idx in extended_positions.items(): put(star,idx)
        # V8.16：博士十二神按禄存宫起博士，依生年阴阳与性别顺逆。
        # 长生十二神按五行局长生起宫，依阴阳男女顺逆。
        yang_year=self.birth_gan in '甲丙戊庚壬'
        male_birth=self.gender.startswith('男')
        star_direction=1 if yang_year==male_birth else -1
        boshi_names=['博士','力士','青龙','小耗','将军','奏书','飞廉','喜神','病符','大耗','伏兵','官府']
        changsheng_names=['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养']
        changsheng_start={2:8,3:11,4:5,5:8,6:2}[bureau]
        series_positions={}
        for i,star in enumerate(boshi_names):
            idx=(lu+star_direction*i)%12;put(star,idx);series_positions[star]=DI_ZHI[idx]
        for i,star in enumerate(changsheng_names):
            idx=(changsheng_start+star_direction*i)%12;put(star,idx);series_positions[star]=DI_ZHI[idx]
        # 天哭/天虚常用年支安星：午宫起子年，哭逆虚顺。
        for star,idx in {'天哭':(6-year_idx)%12,'天虚':(6+year_idx)%12}.items():
            put(star,idx);series_positions[star]=DI_ZHI[idx]
        # V8.17: 固定108项目清单。岁前/将前十二神使用前缀，避免与博士十二神同名混淆。
        # 以下为常见安星口径的工程实现，尚未完成逐宫参考校准。
        sui_names=['岁建','晦气','丧门','贯索','官符','小耗','岁破','龙德','白虎','天德','吊客','病符']
        jiang_names=['将星','攀鞍','岁驿','息神','华盖','劫煞','灾煞','天煞','指背','咸池','月煞','亡神']
        # 岁前十二神：岁建在生年支，逐宫顺布。
        # 将前十二神：将星从生年三合帝旺支起，逐宫顺布。
        jiang_start={0:0,1:9,2:6,3:3}[group]
        cycle_positions={}
        for i,star in enumerate(sui_names):
            label='岁前·'+star;idx=(year_idx+i)%12;put(label,idx);cycle_positions[label]=DI_ZHI[idx]
        for i,star in enumerate(jiang_names):
            label='将前·'+star;idx=(jiang_start+i)%12;put(label,idx);cycle_positions[label]=DI_ZHI[idx]
        # 常见补充杂曜：公式口径不完全统一，作为试算数据标记。
        # 天伤、天使依宫位安置，不能视为独立年/月/日固定支。
        servants_idx=next(i for i in range(12) if PALACE_ORDER[(ming-i)%12]=='交友宫')
        illness_idx=next(i for i in range(12) if PALACE_ORDER[(ming-i)%12]=='疾厄宫')
        month_offset=lm-1
        # 旬空：按出生年干支所属旬定位空亡二支；此处截空使用同旬空位作占位，待流派核验。
        sexagenary_year=next(i for i in range(60) if i%10==TIAN_GAN.index(self.birth_gan) and i%12==year_idx)
        xun_start=sexagenary_year-(sexagenary_year%10)
        xun_empty=((xun_start%12+10)%12,(xun_start%12+11)%12)
        supplemental_positions={
            '天空':(year_idx+1)%12,
            '月德':(year_idx+9)%12,
            '解神':(8+month_offset)%12,
            '天巫':(5+month_offset)%12,
            '天月':(10+month_offset)%12,
            '阴煞':(2+month_offset)%12,
            '天伤':servants_idx,
            '天使':illness_idx,
            '截空':xun_empty[0],
            '旬空':xun_empty[1],
            '天官':(2+TIAN_GAN.index(self.birth_gan))%12,
            '天福':(4+TIAN_GAN.index(self.birth_gan))%12,
            '天厨':(5+TIAN_GAN.index(self.birth_gan))%12,
            '破碎':(year_idx*3+5)%12,
            '天贵':(4+hi+ld-2)%12,
            '恩光':(10-hi+ld-2)%12,
        }
        for star,idx in supplemental_positions.items():put(star,idx)
        # 机器校验：108个不同名称且每个在十二宫恰好出现一次。
        flattened=[star for items in stars.values() for star in items]
        if len(flattened)!=108 or len(set(flattened))!=108:
            raise AssertionError(f'108星完整性检查失败：总数={len(flattened)}，唯一数={len(set(flattened))}')
        extra_star_audit={
            'positions':{star:DI_ZHI[idx] for star,idx in extra_positions.items()},
            'extended_positions':{star:DI_ZHI[idx] for star,idx in extended_positions.items()},
            'series_positions':series_positions,
            'cycle_positions':cycle_positions,
            'supplemental_positions':{star:DI_ZHI[idx] for star,idx in supplemental_positions.items()},
            'reference_validation':'新增40项仅完成公式实现及结构测试；部分安星规则需逐项核验',
            'rules':{'红鸾':'子年卯宫起，逆数年支','天喜':'红鸾对宫',
                     '天刑':'正月酉宫起，顺数生月','天姚':'正月丑宫起，顺数生月',
                     '博士十二神':'禄存宫起博士，阳男阴女顺、阴男阳女逆',
                     '长生十二神':'按五行局定长生起宫，阳男阴女顺、阴男阳女逆',
                     '天哭天虚':'子年午宫起，哭逆虚顺'},
            'status':'traditional_rules_provisional_not_reference_verified',
            'total_charted_stars':len(MAJOR_STARS)+len(SIX_LUCKY_STARS)+len(SIX_SHA_STARS)+1+len(extra_positions)+len(extended_positions)+len(series_positions)+len(cycle_positions)+len(supplemental_positions),
            'message':'常用安星口诀试算；不同流派、星曜层级及文墨天机设置尚未全面核对'
        }
        # 六吉六煞核查：所有十二颗星必须恰好各出现一次。
        audit_names=list(SIX_LUCKY_STARS)+list(SIX_SHA_STARS)
        secondary_positions={name:[zhi for zhi,items in stars.items() if name in items] for name in audit_names}
        secondary_audit={'positions':{name:positions[0] if len(positions)==1 else None for name,positions in secondary_positions.items()},
                         'counts_valid':all(len(positions)==1 for positions in secondary_positions.values()),
                         'reference_case':'1988-08-24 17:45 男命，农历七月十三酉时',
                         'reference_status':'此指定样盘已按文墨天机截图人工核对十二星；其他命盘未验证'}
        from brightness_reference import load_brightness_audit
        brightness_rules, brightness_audit = load_brightness_audit()
        brightness_note = brightness_audit["message"]
        palaces={}; birth_four=self.get_birth_four_transformations(); fly=[]
        for zidx,zhi in enumerate(DI_ZHI):
            palace_index=(ming-zidx)%12
            name=PALACE_ORDER[palace_index]
            all_stars=stars[zhi]
            main=[s for s in all_stars if s in MAJOR_STARS]
            minor=[s for s in all_stars if s not in main]
            sheng={s:{'val':key[-1], 'type':FOUR_KEYS[key]} for key,s in birth_four.items() if s in all_stars}
            self_map=BIRTH_FOUR_TRANSFORMATIONS[gan_by_zhi[zhi]]
            zihua={s:{'val':'◆'+key[-1],'type':FOUR_KEYS[key]} for key,s in self_map.items() if s in all_stars}
            for key,s in self_map.items():
                targets=[t for t,ls in stars.items() if s in ls]
                for target in targets:
                    fly.append({'from':zhi,'from_palace':name,'to':target,'to_palace':PALACE_ORDER[(ming-DI_ZHI.index(target))%12],'star':s,'transformation':key,'self_transform':target==zhi})
            palaces[zhi]={'name':name,'mainStars':main,'minorStars':minor,'shengian':sheng,'zihua':zihua,'age':'','year':'','centerText':'','tagMonth':'','tagLiunian':'','decade':'','gan':gan_by_zhi[zhi], 'gan_zhi':gan_by_zhi[zhi]+zhi,'shen':zidx==shen,'san_fang_si_zheng':[DI_ZHI[(zidx+d)%12] for d in (0,4,6,8)], 'star_brightness':{s:brightness_rules[s][zhi] for s in all_stars if s in brightness_rules and zhi in brightness_rules[s]}, 'brightness_status':brightness_note}
        # 大限按阴阳男女顺逆，起始年龄为五行局数
        yang=self.birth_gan in '甲丙戊庚壬'; male=self.gender.startswith('男')
        direction=1 if yang==male else -1
        for i in range(12):
            idx=(ming+direction*i)%12
            palaces[DI_ZHI[idx]]['decade']=f'{bureau+i*10}-{bureau+i*10+9}'
        # 大限四化：以所选大限宫位的宫干查现有四化表；仅沿用当前项目流派表。
        decade_charts=[]
        for zhi in DI_ZHI:
            palace=palaces[zhi]
            four=BIRTH_FOUR_TRANSFORMATIONS.get(palace['gan'],{})
            edges=[]
            for transformation,star in four.items():
                for target, placed in stars.items():
                    if star in placed:
                        edges.append({'from':zhi,'from_palace':palace['name'],
                                      'to':target,'to_palace':palaces[target]['name'],
                                      'star':star,'transformation':transformation,
                                      'self_transform':target==zhi})
            decade_charts.append({'zhi':zhi,'palace':palace['name'],
                                  'range':palace['decade'],'gan':palace['gan'],
                                  'four':four,'flying_transformations':edges})
        return {'status':'success','name':self.name,'gender':self.gender,'solar':f'{self.solar.getYear()}-{self.solar.getMonth():02d}-{self.solar.getDay():02d} {self.hour:02d}:{self.minute:02d}', 'lunar':f'{ly}年{("闰" if self.lunar.getMonth()<0 else "")}{lm}月{ld}日 {birth_time_label}', 'birth_lunar_month':lm,'birth_hour_branch':DI_ZHI[hi],'birth_shichen':birth_shichen, 'birth_time_label':birth_time_label, 'year_gan_zhi':self.lunar.getYearInGanZhi(), 'animal':ANIMALS[(ly-4)%12], 'bureau':bureau_name,'bureau_number':bureau,'ming_gong':DI_ZHI[ming], 'shen_gong':DI_ZHI[shen], 'birth_four':birth_four, 'ganMap':{z:gan_by_zhi[z]+z for z in DI_ZHI},'palaces':palaces,'flying_transformations':fly,'decade_charts':decade_charts,'secondary_star_audit':secondary_audit,'extra_star_audit':extra_star_audit,'brightness_reference':{**brightness_audit,'coverage':sum(len(p['star_brightness']) for p in palaces.values())},'verification':{'reference':'文墨天机 1988-08-24 17:45、1988-10-29 05:45 男命截图','scope':'两张指定样盘的十四主星、命身宫、五行局；其他日期未全面验证','reverse_water_ji':'待规则核实，不自动判断','secondary_stars':'108项已排布且数量结构验证；新增40项未与文墨天机逐宫核对，部分规则暂为试算','four_transformations':'采用项目现有四化表，流派差异待核实'},'methodology':'V8.2 修正六十甲子纳音表后五组错位（庚戌至己未），校验火六局；庙旺利陷待标准表校准','warnings':['当前以民用日期（午夜00:00换日）计算，23:00至23:59子时的子初换日派别尚未实现。','仅针对两张指定样盘校验部分计算；108项中的新增40项尚未逐宫校准，部分安星规则为临时试算，不宜用于正式命理判断；逆水忌、真太阳时及四化流派仍待验证。']}

ZiWeiEngineLegacy=ZiWeiEngine
