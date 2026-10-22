/* 星轨智盘六爻：京房纳甲与六亲、六神。独立增量，不影响既有模块。 */
(function(root){'use strict';
const na={
 '乾':{inner:['甲子','甲寅','甲辰'],outer:['壬午','壬申','壬戌']},
 '兑':{inner:['丁巳','丁卯','丁丑'],outer:['丁亥','丁酉','丁未']},
 '离':{inner:['己卯','己丑','己亥'],outer:['己酉','己未','己巳']},
 '震':{inner:['庚子','庚寅','庚辰'],outer:['庚午','庚申','庚戌']},
 '巽':{inner:['辛丑','辛亥','辛酉'],outer:['辛未','辛巳','辛卯']},
 '坎':{inner:['戊寅','戊辰','戊午'],outer:['戊申','戊戌','戊子']},
 '艮':{inner:['丙辰','丙午','丙申'],outer:['丙戌','丙子','丙寅']},
 '坤':{inner:['乙未','乙巳','乙卯'],outer:['癸丑','癸亥','癸酉']}
};
const element={'乾':'金','兑':'金','离':'火','震':'木','巽':'木','坎':'水','艮':'土','坤':'土'};
const branchElement={'子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火','午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'};
const generates={'木':'火','火':'土','土':'金','金':'水','水':'木'};
const controls={'木':'土','土':'水','水':'火','火':'金','金':'木'};
const spirits=['青龙','朱雀','勾陈','螣蛇','白虎','玄武'];
const start={'甲':0,'乙':0,'丙':1,'丁':1,'戊':2,'己':3,'庚':4,'辛':4,'壬':5,'癸':5};
function relative(palace,branch){const me=element[palace],other=branchElement[branch];if(!me||!other)throw Error('未知五行');if(me===other)return '兄弟';if(generates[me]===other)return '子孙';if(generates[other]===me)return '父母';if(controls[me]===other)return '妻财';if(controls[other]===me)return '官鬼';throw Error('六亲计算失败')}
function get(values,dayStem){const hex=root.XingguiLiuyaoHexagram.get(values);const stem=String(dayStem||'').trim();if(stem&&!Object.prototype.hasOwnProperty.call(start,stem))throw Error('请选择有效的日干');const arr=[...na[hex.lower].inner,...na[hex.upper].outer];return {hex,dayStem:stem,lines:arr.map((gz,i)=>({index:i+1,najia:gz,branch:gz[1],element:branchElement[gz[1]],relative:relative(hex.palace,gz[1]),spirit:(stem?spirits[(start[stem]+i)%6]:'待日干'),shi:i+1===hex.shi,ying:i+1===hex.ying,moving:[6,9].includes(values[i])}))}}
// 伏神按本宫纯卦六亲补足本卦缺失六亲；使用同一京房宫五行基准。
function getFushen(values){
 const hex=root.XingguiLiuyaoHexagram.get(values),base=get(values,''),seen=new Set(base.lines.map(x=>x.relative));
 const pure=Object.keys(na).find(k=>k===hex.palace);
 if(!pure)return Array(6).fill(null);
 const pureValues=({乾:[7,7,7],兑:[7,7,8],离:[7,8,7],震:[7,8,8],巽:[8,7,7],坎:[8,7,8],艮:[8,8,7],坤:[8,8,8]})[pure];
 const pureData=get([...pureValues,...pureValues],'');
 return pureData.lines.map(x=>seen.has(x.relative)?null:{relative:x.relative,najia:x.najia,branch:x.branch,element:x.element});
}
function getChanged(values,dayStem){
 const next=values.map(v=>v===6?7:v===9?8:v),original=get(values,dayStem),changed=get(next,dayStem);
 return {...changed,lines:changed.lines.map((x,i)=>({...x,relative:relative(original.hex.palace,x.branch)}))};
}
root.XingguiLiuyaoNajia=Object.freeze({get,getFushen,getChanged});
})(window);
