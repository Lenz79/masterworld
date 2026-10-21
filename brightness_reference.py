# -*- coding: utf-8 -*-
"""庙旺利陷公开资料读取器。资料仅为公开转录，未经独立流派校准。"""
import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / '庙旺利陷_312项_公开资料已填168项.csv'
BRANCHES = frozenset('子丑寅卯辰巳午未申酉戌亥')
LEVELS = frozenset(('庙','旺','得','利','平','陷','不','闲'))

def load_brightness_audit():
    rules = {}
    entries = 0
    if not DATA_FILE.is_file():
        return {}, {'verified_entries': 0, 'source_entries': 0, 'status': 'missing_data', 'message': '未找到庙旺利陷资料，暂不显示星曜亮度；排盘不受影响。'}
    with DATA_FILE.open('r', encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            star=(row.get('star') or '').strip()
            branch=(row.get('branch') or '').strip()
            level=(row.get('level') or '').strip()
            if not star or branch not in BRANCHES or not level or level not in LEVELS:
                continue
            if branch not in rules.setdefault(star, {}):
                rules[star][branch]=level
                entries += 1
    return rules, {'verified_entries': 0, 'source_entries': entries, 'unverified_entries': entries,
                   'status': 'public_source_not_independently_verified',
                   'message': f'公开亮度资料已录入{entries}项，尚未与标准命盘逐项校准。'}
