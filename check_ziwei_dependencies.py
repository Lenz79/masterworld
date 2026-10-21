"""只读检查紫微分析模块是否齐全，不修改服务器或数据库。"""
from pathlib import Path
import ast
base=Path(__file__).resolve().parent
required=['ziwei_engine', 'ziwei_analysis', 'ziwei_rule_registry', 'ziwei_rule_gates', 'ziwei_rule_provenance', 'ziwei_annual_audit', 'ziwei_decade_audit', 'ziwei_layer_consistency', 'ziwei_verification', 'ziwei_delivery_audit', 'ziwei_quality_audit', 'ziwei_acceptance_audit', 'ziwei_adversarial']
for name in required:
 p=base/(name+'.py')
 if not p.is_file(): print('缺失',p.name);continue
 try: ast.parse(p.read_text(encoding='utf-8'));print('存在/语法正常',p.name)
 except Exception as e: print('语法异常',p.name,e)
print('检查结束。缺失文件须从原项目找回，不能用空壳文件代替。')
