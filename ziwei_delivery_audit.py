"""Independent advisory chart-integrity checks; never infer fate or traditional patterns."""
from collections import Counter
import json
from ziwei_engine import DI_ZHI, MAJOR_STARS
STEMS=set("甲乙丙丁戊己庚辛壬癸")

def _serialized_size(chart):
    try: return len(json.dumps(chart,ensure_ascii=False,allow_nan=False).encode("utf-8"))
    except (TypeError,ValueError,OverflowError): return 100000000

def audit_chart(chart):
    if not isinstance(chart,dict):
        return {"version":"v8.121","checks":{},"failed":[],"passed":False,"status":"invalid_chart","pattern_concluded":False,"event_concluded":False}
    palaces=chart.get("palaces")
    if not isinstance(palaces,dict): palaces={}
    safe_palaces=[p for p in palaces.values() if isinstance(p,dict)]
    palace_stars=[(p.get("mainStars",[]) if isinstance(p.get("mainStars",[]),list) else [])+(p.get("minorStars",[]) if isinstance(p.get("minorStars",[]),list) else []) for p in safe_palaces]
    counts=Counter(s for stars in palace_stars for s in stars if isinstance(s,str))
    names=[p.get("name") for p in safe_palaces if isinstance(p.get("name"),str)]
    checks={}
    # V8.102: 十二宫数量
    try:
        checks["palace_count"]=bool(len(palaces) == 12)
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_count"]=False
    # V8.103: 十二地支完整
    try:
        checks["palace_keys"]=bool(set(palaces) == set(DI_ZHI))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_keys"]=False
    # V8.104: 宫位结构类型
    try:
        checks["palace_object"]=bool(all(isinstance(p,dict) for p in palaces.values()))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_object"]=False
    # V8.105: 主星字段类型
    try:
        checks["main_stars_list"]=bool(all(isinstance(p.get("mainStars",[]),list) for p in safe_palaces))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["main_stars_list"]=False
    # V8.106: 辅星字段类型
    try:
        checks["minor_stars_list"]=bool(all(isinstance(p.get("minorStars",[]),list) for p in safe_palaces))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["minor_stars_list"]=False
    # V8.107: 主星字符串
    try:
        checks["main_star_strings"]=bool(all(all(isinstance(s,str) and bool(s.strip()) for s in p.get("mainStars",[])) for p in safe_palaces if isinstance(p.get("mainStars",[]),list)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["main_star_strings"]=False
    # V8.108: 辅星字符串
    try:
        checks["minor_star_strings"]=bool(all(all(isinstance(s,str) and bool(s.strip()) for s in p.get("minorStars",[])) for p in safe_palaces if isinstance(p.get("minorStars",[]),list)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["minor_star_strings"]=False
    # V8.109: 星名长度
    try:
        checks["star_length"]=bool(all(len(s)<=16 for p in safe_palaces for field in ("mainStars","minorStars") for s in p.get(field,[]) if isinstance(p.get(field,[]),list) and isinstance(s,str)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["star_length"]=False
    # V8.110: 宫内重复星曜
    try:
        checks["duplicate_in_palace"]=bool(all(len(stars)==len(set(stars)) for stars in palace_stars if all(isinstance(s,str) for s in stars)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["duplicate_in_palace"]=False
    # V8.111: 十四主星跨宫唯一
    try:
        checks["major_star_unique"]=bool(all(counts[s] <= 1 for s in MAJOR_STARS))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["major_star_unique"]=False
    # V8.112: 十四主星齐全
    try:
        checks["major_star_complete"]=bool(all(counts[s] == 1 for s in MAJOR_STARS))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["major_star_complete"]=False
    # V8.113: 宫名字段类型
    try:
        checks["palace_name_string"]=bool(all(isinstance(p.get("name",""),str) for p in safe_palaces))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_name_string"]=False
    # V8.114: 宫名非空
    try:
        checks["palace_name_nonempty"]=bool(all(bool(p.get("name","").strip()) for p in safe_palaces if isinstance(p.get("name",""),str)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_name_nonempty"]=False
    # V8.115: 宫名不重复
    try:
        checks["palace_name_unique"]=bool(len(names)==len(set(names)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_name_unique"]=False
    # V8.116: 宫干范围
    try:
        checks["palace_stem_valid"]=bool(all(p.get("gan") in STEMS for p in safe_palaces))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["palace_stem_valid"]=False
    # V8.117: 亮度字典类型
    try:
        checks["brightness_object"]=bool(all(isinstance(p.get("star_brightness",{}),dict) for p in safe_palaces))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["brightness_object"]=False
    # V8.118: 亮度星曜有落宫
    try:
        checks["brightness_keys"]=bool(all(set(p.get("star_brightness",{})).issubset(set(p.get("mainStars",[])+p.get("minorStars",[]))) for p in safe_palaces if isinstance(p.get("star_brightness",{}),dict) and isinstance(p.get("mainStars",[]),list) and isinstance(p.get("minorStars",[]),list)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["brightness_keys"]=False
    # V8.119: 亮度数据为文本
    try:
        checks["brightness_values"]=bool(all(all(isinstance(v,str) for v in p.get("star_brightness",{}).values()) for p in safe_palaces if isinstance(p.get("star_brightness",{}),dict)))
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["brightness_values"]=False
    # V8.120: 命盘序列化大小
    try:
        checks["chart_size"]=bool(_serialized_size(chart) <= 750000)
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["chart_size"]=False
    # V8.121: 审计不宣称格局或事件成立
    try:
        checks["interpretation_guard"]=bool(chart.get('pattern_concluded') is not True and chart.get('event_concluded') is not True)
    except (TypeError,ValueError,KeyError,AttributeError):
        checks["interpretation_guard"]=False
    failed=[key for key,ok in checks.items() if not ok]
    return {"version":"v8.121","checks":checks,"failed":failed,"passed":not failed,"status":"advisory_only","pattern_concluded":False,"event_concluded":False,"note":"资料一致性检查并非命理格局、流派起法或事件判断认证。"}
