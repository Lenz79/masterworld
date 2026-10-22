/* 星轨智盘六爻：独立六十四卦与京房八宫世应索引；不修改原有起卦流程。 */
(function(root){'use strict';
const names=['乾','兑','离','震','巽','坎','艮','坤'];
const bits={'乾':'111','兑':'110','离':'101','震':'100','巽':'011','坎':'010','艮':'001','坤':'000'};
// 行为上卦，列为下卦；列顺序：乾兑离震巽坎艮坤。
const matrix=[
['乾','履','同人','无妄','姤','讼','遁','否'],
['夬','兑','革','随','大过','困','咸','萃'],
['大有','睽','离','噬嗑','鼎','未济','旅','晋'],
['大壮','归妹','丰','震','恒','解','小过','豫'],
['小畜','中孚','家人','益','巽','涣','渐','观'],
['需','节','既济','屯','井','坎','蹇','比'],
['大畜','损','贲','颐','蛊','蒙','艮','剥'],
['泰','临','明夷','复','升','师','谦','坤']];
const stages=['本宫','一世','二世','三世','四世','五世','游魂','归魂'];
const changes=[[],[0],[0,1],[0,1,2],[0,1,2,3],[0,1,2,3,4],[0,1,2,4],[4]];
const shi=[6,1,2,3,4,5,4,3];
const palaceIndex=new Map();
for(const palace of names){const base=(bits[palace]+bits[palace]).split('').map(Number);for(let i=0;i<8;i++){
 const line=base.map((v,j)=>changes[i].includes(j)?1-v:v).join('');
 if(palaceIndex.has(line))throw Error('京房八宫索引重复：'+line);
 palaceIndex.set(line,{palace,stage:stages[i],shi:shi[i],ying:(shi[i]+2)%6+1});
}}
if(palaceIndex.size!==64)throw Error('京房八宫索引数量错误');
function get(values){if(!Array.isArray(values)||values.length!==6||values.some(v=>![6,7,8,9,0,1].includes(v)))throw Error('需要六条有效爻');
 const line=values.map(v=>v%2).join('');const low=line.slice(0,3),up=line.slice(3);
 const lower=names.find(n=>bits[n]===low),upper=names.find(n=>bits[n]===up);
 const name=matrix[names.indexOf(upper)][names.indexOf(lower)];
 return {name,upper,lower,...palaceIndex.get(line)};
}
root.XingguiLiuyaoHexagram=Object.freeze({get});
})(window);
