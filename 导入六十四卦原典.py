#!/usr/bin/env python3
"""从公开来源导入64卦原典为独立本地 JS，不需任何第三方 Python 库。"""
import json,urllib.request,pathlib,sys
URL='https://raw.githubusercontent.com/toastedqu/meihua/main/app/data/classics.json'
OUTPUT=pathlib.Path(__file__).resolve().parent/'liuyao_classics_data.js'
EXPECTED=set(range(1,65))
def main():
    req=urllib.request.Request(URL,headers={'User-Agent':'AstroMatrix-Classics-Importer/1.0'})
    with urllib.request.urlopen(req,timeout=35) as response: raw=json.load(response)
    entries=raw.get('hexagrams',{})
    if len(entries)!=64:raise ValueError('卦数不足64: '+str(len(entries)))
    records={};numbers=[]
    for entry in entries.values():
        name=entry.get('name','');num=entry.get('number');lines=entry.get('lines',[]);small=entry.get('line_xiang',[])
        if not name or len(lines)!=6 or len(small)!=6 or not all(entry.get(k) for k in ('judgment','tuan','xiang','source')):
            raise ValueError('原典缺少必需字段: '+repr(name))
        if name in records:raise ValueError('卦名重复: '+name)
        records[name]={'number':num,'guaci':entry['judgment'],'tuan':entry['tuan'],'xiang':entry['xiang'],'lines':lines,'line_xiang':small,'source':entry['source'],'revision':entry.get('revision','')}
        numbers.append(num)
    if set(numbers)!=EXPECTED:raise ValueError('文王卦序编号缺失或重复')
    # 乾坤的用九/用六属于额外经文，不能错误充作第七爻。
    records['乾为天']['extra']='用九：见群龙无首，吉。'
    records['坤为地']['extra']='用六：利永贞。'
    payload='/* 本地经典资料；来源：'+URL+'；请保留各卦source和revision */\nwindow.XingguiLiuyaoClassics='+json.dumps(records,ensure_ascii=False,separators=(',',':'))+';\n'
    OUTPUT.write_text(payload,encoding='utf-8')
    print('成功导入：',len(records),'卦、',sum(len(v['lines']) for v in records.values()),'条爻辞、',sum(len(v['line_xiang']) for v in records.values()),'条小象；文件：',OUTPUT)
if __name__=='__main__':
    try:main()
    except Exception as e:print('导入失败，未覆盖旧资料：',e,file=sys.stderr);sys.exit(1)
