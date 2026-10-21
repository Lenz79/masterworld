#!/usr/bin/env python3
"""Generate an offline, read-only audit report for Ziwei brightness entries."""
import argparse
import html
from pathlib import Path
from brightness_reference import load_brightness_audit
from ziwei_brightness_schema import STAR_NAMES, BRANCHES

def generate(database, output):
    verified, audit = load_brightness_audit(database)
    rows=[]
    for star in STAR_NAMES:
        cells=[]
        for branch in BRANCHES:
            entry=verified.get(star,{}).get(branch)
            if entry:
                cells.append('<td class="yes" title="{}">{}</td>'.format(html.escape(str(entry.get('source',''))),html.escape(str(entry.get('level','')))))
            else:
                cells.append('<td class="no">待核</td>')
        rows.append('<tr><th>{}</th>{}</tr>'.format(html.escape(star),''.join(cells)))
    total=sum(len(v) for v in verified.values())
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>星轨智盘 · 庙旺利陷核验进度</title>
<style>body{font-family:system-ui,"Microsoft YaHei",sans-serif;max-width:1200px;margin:32px auto;padding:0 16px;color:#1e293b}h1{color:#b45309}table{border-collapse:collapse;width:100%%;font-size:13px}td,th{border:1px solid #cbd5e1;padding:8px;text-align:center}thead{background:#fef3c7}.yes{background:#dcfce7}.no{color:#94a3b8}p{line-height:1.7}.scroll{overflow:auto}.bar{height:12px;background:#e2e8f0;border-radius:10px}.fill{height:100%%;background:#16a34a;border-radius:10px}</style>
<h1>星轨智盘 · 庙旺利陷核验进度</h1><p>已核验 <strong>%(total)s / 312</strong> 项（%(percent).1f%%）。绿色为已核验，灰色为待核对。此报告只反映已导入且通过校验的记录，不代表所有流派均采用同一亮度等级。</p>
<div class="bar"><div class="fill" style="width:%(percent).2f%%"></div></div><p>数据来源：%(db)s</p><div class="scroll"><table><thead><tr><th>星曜</th>%(headers)s</tr></thead><tbody>%(rows)s</tbody></table></div>
<p>使用方法：在 CSV 核验模板中填写等级、来源和核对人，运行 brightness_import.py 导入，再重新生成此报告。未核实的条目不会出现在命盘亮度显示中。</p></html>''' % dict(total=total,percent=100*total/312,db=html.escape(str(database)),headers=''.join('<th>'+b+'</th>' for b in BRANCHES),rows=''.join(rows))
    Path(output).write_text(page,encoding='utf-8')
    return total

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--database',default='ziwei_brightness_verified.json');p.add_argument('--output',default='庙旺利陷_核验进度.html');a=p.parse_args();n=generate(a.database,a.output);print(f'已核验 {n}/312 项；报告：{a.output}')
