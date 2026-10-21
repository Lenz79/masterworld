"""可追溯的星曜亮度数据读取器：只接纳逐项确认的星曜/地支记录。"""
import json
from pathlib import Path
from ziwei_brightness_schema import STAR_NAMES, BRANCHES, LEVELS

DEFAULT_PATH = Path(__file__).with_name('ziwei_brightness_verified.json')


def load_brightness_audit(path=DEFAULT_PATH):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(raw, dict):
        raise ValueError('亮度文件必须是 JSON 对象')
    status = raw.get('status', 'unverified')
    if status not in ('unverified', 'partial', 'verified'):
        raise ValueError('status 只能是 unverified、partial 或 verified')
    records = raw.get('stars', {})
    if not isinstance(records, dict):
        raise ValueError('stars 必须是对象')
    checked = {}
    for star, entries in records.items():
        if star not in STAR_NAMES:
            raise ValueError(f'未知星曜：{star}')
        if not isinstance(entries, dict):
            raise ValueError(f'{star} 的宫位表格式错误')
        for branch, record in entries.items():
            if branch not in BRANCHES:
                raise ValueError(f'未知地支：{branch}')
            if not isinstance(record, dict):
                raise ValueError(f'{star}{branch} 必须有 level、source、checked_by 字段')
            level = record.get('level')
            if level not in LEVELS:
                raise ValueError(f'{star}{branch} 亮度等级无效：{level}')
            if not str(record.get('source', '')).strip() or not str(record.get('checked_by', '')).strip():
                raise ValueError(f'{star}{branch} 缺少核对来源或核对人')
            checked.setdefault(star, {})[branch] = level
    total = len(STAR_NAMES) * len(BRANCHES)
    count = sum(map(len, checked.values()))
    if status == 'verified' and count != total:
        raise ValueError(f'不能标为全部核验：只有 {count}/{total} 条')
    if status == 'unverified' and count:
        raise ValueError('有已核验记录时，请把 status 改为 partial')
    note = f'庙旺利陷已核验 {count}/{total} 项；未核验的不显示'
    return checked, {'status': 'verified' if count == total else ('partial' if count else 'pending'),
                     'message': note, 'verified_entries': count, 'total_entries': total,
                     'star_count': len(STAR_NAMES)}


def load_verified_brightness(path=DEFAULT_PATH):
    data, audit = load_brightness_audit(path)
    return data, audit['message']
