#!/usr/bin/env python3
"""人工核验亮度 CSV 导入器；仅导入有来源和核对人的记录。"""
import argparse
import csv
import json
from pathlib import Path
from ziwei_brightness_schema import STAR_NAMES, BRANCHES, LEVELS
from brightness_reference import load_brightness_audit

FIELDS = ('star', 'branch', 'level', 'source', 'checked_by')

def make_template(path):
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        writer=csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for star in STAR_NAMES:
            for branch in BRANCHES:
                writer.writerow({'star':star,'branch':branch,'level':'','source':'','checked_by':''})

def import_reviewed_csv(csv_path, json_path, output_path=None):
    json_path=Path(json_path)
    output_path=Path(output_path) if output_path else json_path
    existing, _ = load_brightness_audit(json_path)
    raw=json.loads(json_path.read_text(encoding='utf-8'))
    records=raw.get('stars',{})
    updates=0
    seen=set()
    with Path(csv_path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError('CSV 必须包含 star,branch,level,source,checked_by 五列')
        for line, row in enumerate(reader, 2):
            star=(row.get('star') or '').strip(); branch=(row.get('branch') or '').strip()
            level=(row.get('level') or '').strip(); source=(row.get('source') or '').strip()
            checker=(row.get('checked_by') or '').strip()
            if not any((star,branch,level,source,checker)): continue
            if star not in STAR_NAMES or branch not in BRANCHES:
                raise ValueError(f'第 {line} 行：星曜或地支无效')
            if (star,branch) in seen: raise ValueError(f'第 {line} 行：重复星曜宫位 {star}{branch}')
            seen.add((star,branch))
            if not level: continue  # 模板中的空白项，不计入已核验
            if level not in LEVELS or not source or not checker:
                raise ValueError(f'第 {line} 行：等级无效或缺少来源／核对人')
            old=records.get(star,{}).get(branch)
            if old and old['level'] != level:
                raise ValueError(f'第 {line} 行：{star}{branch} 与既有已核验等级冲突；请人工复核')
            records.setdefault(star,{})[branch]={'level':level,'source':source,'checked_by':checker}
            updates+=1
    raw['stars']=records
    total=sum(len(x) for x in records.values())
    raw['status']='verified' if total==len(STAR_NAMES)*len(BRANCHES) else ('partial' if total else 'unverified')
    # 验证完整数据后才落盘；避免破坏原始文件
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/'check.json'
        p.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
        _, audit=load_brightness_audit(p)
    output_path.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return updates, audit

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template',help='生成 312 项空白核验 CSV')
    parser.add_argument('--import-csv',help='导入已人工核验的 CSV')
    parser.add_argument('--database',default='ziwei_brightness_verified.json')
    parser.add_argument('--output',help='输出 JSON；默认更新 database')
    args=parser.parse_args()
    if args.template: make_template(args.template);print('模板已生成：',args.template)
    if args.import_csv:
        n,audit=import_reviewed_csv(args.import_csv,args.database,args.output)
        print(f'已导入 {n} 项；{audit["message"]}')
    if not args.template and not args.import_csv: parser.error('请选择 --template 或 --import-csv')
