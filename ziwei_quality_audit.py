"""逐项资料质量核验；不对传统命理规则或事件下结论。"""
from ziwei_engine import DI_ZHI, MAJOR_STARS, PALACE_NAMES, FIVE_ELEMENTS_BUREAU, BIRTH_FOUR_TRANSFORMATIONS
STEMS=set('甲乙丙丁戊己庚辛壬癸')
ZHIS=set(DI_ZHI)
FOUR=set(('化禄','化权','化科','化忌'))
RULES=[]

def audit_quality(chart):
    if not isinstance(chart,dict):
        return {'version':'v8.123','checks':{},'failed':['chart_type'],'passed':False,'status':'invalid_chart','pattern_concluded':False,'event_concluded':False}
    result={}; failed=[]; skipped=[]
    for key,label,field,fn in RULES:
        if field not in chart:
            result[key]={'status':'not_applicable','label':label,'reason':'字段缺失，不视为通过'}
            skipped.append(key)
            continue
        try: ok=bool(fn(chart))
        except (ValueError,TypeError,KeyError,AttributeError,IndexError): ok=False
        result[key]={'status':'passed' if ok else 'failed','label':label}
        if not ok: failed.append(key)
    return {'version':'v8.123','checks':result,'failed':failed,'skipped':skipped,'passed':not failed and not skipped,'status':'advisory_only','pattern_concluded':False,'event_concluded':False,'note':'字段缺失为未检，不可视为通过；此审计不认证传统格局、流派起法或人生事件。'}

# V8.122: 年干支文本格式
RULES.append(('year_ganzhi_type','年干支文本格式','year_gan_zhi',lambda c: isinstance(c.get('year_gan_zhi'),str) and len(c['year_gan_zhi'])>=2 and c['year_gan_zhi'][0] in STEMS and c['year_gan_zhi'][1] in ZHIS))

# V8.123: 生年四化四项齐备
RULES.append(('birth_four_structure','生年四化四项齐备','birth_four',lambda c: isinstance(c.get('birth_four'),dict) and set(c['birth_four'])==FOUR and all(isinstance(v,str) and bool(v.strip()) for v in c['birth_four'].values())))

# V8.124: 生年四化与现有表一致
RULES.append(('birth_four_table','生年四化与现有表一致','birth_four',lambda c: isinstance(c.get('birth_four'),dict) and c.get('year_gan_zhi','')[:1] in BIRTH_FOUR_TRANSFORMATIONS and c['birth_four']==BIRTH_FOUR_TRANSFORMATIONS[c['year_gan_zhi'][0]]))

# V8.125: 命宫地支合法
RULES.append(('ming_gong_branch','命宫地支合法','ming_gong',lambda c: c.get('ming_gong') in ZHIS))

# V8.126: 身宫地支合法
RULES.append(('shen_gong_branch','身宫地支合法','shen_gong',lambda c: c.get('shen_gong') in ZHIS))

# V8.127: 五行局名称合法
RULES.append(('bureau_name','五行局名称合法','bureau',lambda c: c.get('bureau') in FIVE_ELEMENTS_BUREAU))

# V8.128: 五行局数字匹配
RULES.append(('bureau_number','五行局数字匹配','bureau_number',lambda c: c.get('bureau') in FIVE_ELEMENTS_BUREAU and type(c.get('bureau_number')) is int and c['bureau_number']==FIVE_ELEMENTS_BUREAU[c['bureau']]))

# V8.129: 十二宫干支映射完整
RULES.append(('ganmap_structure','十二宫干支映射完整','ganMap',lambda c: isinstance(c.get('ganMap'),dict) and set(c['ganMap'])==ZHIS and all(isinstance(v,str) for v in c['ganMap'].values())))

# V8.130: 宫干支映射末字一致
RULES.append(('ganmap_suffix','宫干支映射末字一致','ganMap',lambda c: isinstance(c.get('ganMap'),dict) and all(isinstance(v,str) and len(v)==2 and v[0] in STEMS and v[1]==z for z,v in c['ganMap'].items())))

# V8.131: 宫干与宫干支映射一致
RULES.append(('ganmap_palace_consistency','宫干与宫干支映射一致','ganMap',lambda c: isinstance(c.get('ganMap'),dict) and isinstance(c.get('palaces'),dict) and all(isinstance(p,dict) and isinstance(c['ganMap'].get(z),str) and p.get('gan')==c['ganMap'][z][0] for z,p in c['palaces'].items())))

# V8.132: 十二宫名称符合现有标准表
RULES.append(('canonical_palace_names','十二宫名称符合现有标准表','palaces',lambda c: isinstance(c.get('palaces'),dict) and {p.get('name') for p in c['palaces'].values() if isinstance(p,dict)}==set(PALACE_NAMES)))

# V8.133: 主星与辅星不重复列出
RULES.append(('main_minor_disjoint','主星与辅星不重复列出','palaces',lambda c: isinstance(c.get('palaces'),dict) and all(isinstance(p,dict) and isinstance(p.get('mainStars'),list) and isinstance(p.get('minorStars'),list) and not (set(p['mainStars']) & set(p['minorStars'])) for p in c['palaces'].values())))

# V8.134: 十四主星不得放入辅星栏
RULES.append(('major_in_main_only','十四主星不得放入辅星栏','palaces',lambda c: isinstance(c.get('palaces'),dict) and all(isinstance(p,dict) and isinstance(p.get('minorStars'),list) and not (set(p['minorStars']) & set(MAJOR_STARS)) for p in c['palaces'].values())))

# V8.135: 主星栏仅列十四主星
RULES.append(('main_stars_known','主星栏仅列十四主星','palaces',lambda c: isinstance(c.get('palaces'),dict) and all(isinstance(p,dict) and isinstance(p.get('mainStars'),list) and set(p['mainStars']).issubset(set(MAJOR_STARS)) for p in c['palaces'].values())))

# V8.136: 亮度键值不得为空白
RULES.append(('brightness_nonempty','亮度键值不得为空白','palaces',lambda c: isinstance(c.get('palaces'),dict) and all(isinstance(p,dict) and isinstance(p.get('star_brightness'),dict) and all(isinstance(k,str) and bool(k.strip()) and isinstance(v,str) and bool(v.strip()) for k,v in p['star_brightness'].items()) for p in c['palaces'].values())))

# V8.137: 风险提示必须是文本列表
RULES.append(('warnings_type','风险提示必须是文本列表','warnings',lambda c: isinstance(c.get('warnings'),list) and all(isinstance(w,str) and bool(w.strip()) for w in c['warnings'])))

# V8.138: 核验说明必须是字典
RULES.append(('verification_type','核验说明必须是字典','verification',lambda c: isinstance(c.get('verification'),dict) and all(isinstance(k,str) and isinstance(v,str) for k,v in c['verification'].items())))

# V8.139: 排盘状态为已知成功标识
RULES.append(('chart_status','排盘状态为已知成功标识','status',lambda c: c.get('status')=='success'))

# V8.140: 农历出生月份范围
RULES.append(('birth_lunar_month','农历出生月份范围','birth_lunar_month',lambda c: type(c.get('birth_lunar_month')) is int and 1<=c['birth_lunar_month']<=12))

# V8.141: 出生时支属于十二地支
RULES.append(('birth_hour_branch','出生时支属于十二地支','birth_hour_branch',lambda c: c.get('birth_hour_branch') in ZHIS))
