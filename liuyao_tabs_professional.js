/* AstroMatrix 六爻三视图：独立 UI 扩展，保留现有排盘、登录、数据库和算法。 */
(function(){'use strict';
const host=document.getElementById('liuyao-tab-panel');
if(!host)return;
const trigramElement={乾:'金',兑:'金',离:'火',震:'木',巽:'木',坎:'水',艮:'土',坤:'土'};
const trigramBits={'111':'乾','110':'兑','101':'离','100':'震','011':'巽','010':'坎','001':'艮','000':'坤'};
const generates={木:'火',火:'土',土:'金',金:'水',水:'木'},controls={木:'土',土:'水',水:'火',火:'金',金:'木'};
const names=['初','二','三','四','五','上'];
// 日柱由用户核对输入，不根据公历日期擅自推算。
const gan='甲乙丙丁戊己庚辛壬癸',zhi='子丑寅卯辰巳午未申酉戌亥';
const ganzhi=Array.from({length:60},(_,i)=>gan[i%10]+zhi[i%12]);
// 月建由用户按节气核对输入；不从公历月份直接推断。
const monthBranches='寅卯辰巳午未申酉戌亥子丑';
const branchElement={子:'水',丑:'土',寅:'木',卯:'木',辰:'土',巳:'火',午:'火',未:'土',申:'金',酉:'金',戌:'土',亥:'水'};
const elementGenerates={木:'火',火:'土',土:'金',金:'水',水:'木'};
const elementControls={木:'土',土:'水',水:'火',火:'金',金:'木'};
function seasonElement(branch){if('寅卯辰'.includes(branch))return '木';if('巳午未'.includes(branch))return '火';if('申酉戌'.includes(branch))return '金';if('亥子丑'.includes(branch))return '水';return ''}
function seasonalStrength(element,branch){const s=seasonElement(branch);if(!s||!element)return '未计算';if(element===s)return '旺';if(elementGenerates[s]===element)return '相';if(elementGenerates[element]===s)return '休';if(elementControls[element]===s)return '囚';if(elementControls[s]===element)return '死';return '未计算'}
// 数字量化资料：按用户提供的《月建对爻数字量化表》《日辰对爻数字量化表》录入。
// 这是特定研究方法的参考分值，不是传统六爻通行的唯一旺衰定量标准。
const quantMonth={"寅":{"子":-0.1,"丑":-1,"寅":2,"卯":1,"辰":-1,"巳":1,"午":1,"未":-1,"申":-2,"酉":-0.1,"戌":-1,"亥":0.5},"卯":{"子":-0.1,"丑":-1,"寅":1,"卯":2,"辰":-1,"巳":1,"午":1,"未":-1,"申":-0.1,"酉":-2,"戌":-0.5,"亥":-0.1},"辰":{"子":-1,"丑":1,"寅":0.5,"卯":0.5,"辰":2,"巳":-0.1,"午":-0.1,"未":1,"申":1,"酉":2,"戌":-2,"亥":-1},"巳":{"子":-0.1,"丑":1,"寅":-0.1,"卯":-0.1,"辰":1,"巳":2,"午":1,"未":1,"申":-0.5,"酉":-1,"戌":1,"亥":-2},"午":{"子":-2,"丑":1,"寅":-0.1,"卯":-0.1,"辰":1,"巳":1,"午":2,"未":2,"申":-1,"酉":-1,"戌":1,"亥":-0.1},"未":{"子":-1,"丑":-2,"寅":-0.1,"卯":-0.1,"辰":1,"巳":0.5,"午":0.5,"未":2,"申":1,"酉":1,"戌":1,"亥":-1},"申":{"子":1,"丑":-0.1,"寅":-2,"卯":-1,"辰":-0.1,"巳":0.5,"午":-0.1,"未":-0.1,"申":2,"酉":1,"戌":-0.1,"亥":1},"酉":{"子":1,"丑":-0.1,"寅":-1,"卯":-2,"辰":0.5,"巳":-0.1,"午":-0.1,"未":-0.1,"申":1,"酉":2,"戌":-0.1,"亥":1},"戌":{"子":-1,"丑":1,"寅":-0.1,"卯":0.5,"辰":-2,"巳":-0.1,"午":-0.1,"未":1,"申":1,"酉":1,"戌":2,"亥":-1},"亥":{"子":1,"丑":-0.1,"寅":2,"卯":1,"辰":-0.1,"巳":-2,"午":-1,"未":-0.1,"申":-0.1,"酉":-0.1,"戌":-0.1,"亥":2},"子":{"子":2,"丑":0.5,"寅":1,"卯":1,"辰":-0.1,"巳":-1,"午":-2,"未":-0.1,"申":-0.1,"酉":-0.1,"戌":-0.1,"亥":1},"丑":{"子":-0.5,"丑":2,"寅":-0.1,"卯":-0.1,"辰":1,"巳":-0.1,"午":-0.1,"未":-2,"申":1,"酉":1,"戌":1,"亥":-1}};
const quantDay={"寅":{"子":0,"丑":-1,"寅":2,"卯":1,"辰":-1,"巳":1,"午":1,"未":-1,"申":null,"酉":0,"戌":-1,"亥":0},"卯":{"子":0,"丑":-1,"寅":1,"卯":2,"辰":-1,"巳":1,"午":1,"未":-1,"申":0,"酉":null,"戌":-1,"亥":0},"辰":{"子":-1,"丑":1,"寅":0,"卯":0,"辰":2,"巳":0,"午":0,"未":1,"申":1,"酉":2,"戌":null,"亥":-1},"巳":{"子":0,"丑":1,"寅":0,"卯":0,"辰":1,"巳":2,"午":1,"未":1,"申":-1,"酉":-1,"戌":1,"亥":null},"午":{"子":null,"丑":1,"寅":0,"卯":0,"辰":1,"巳":1,"午":2,"未":2,"申":-1,"酉":-1,"戌":1,"亥":0},"未":{"子":-1,"丑":null,"寅":0,"卯":0,"辰":1,"巳":0,"午":0,"未":2,"申":1,"酉":1,"戌":1,"亥":-1},"申":{"子":1,"丑":0,"寅":null,"卯":-1,"辰":0,"巳":0,"午":0,"未":0,"申":2,"酉":1,"戌":0,"亥":1},"酉":{"子":1,"丑":0,"寅":-1,"卯":null,"辰":0,"巳":0,"午":0,"未":0,"申":1,"酉":2,"戌":0,"亥":1},"戌":{"子":-1,"丑":1,"寅":0,"卯":0,"辰":null,"巳":0,"午":0,"未":1,"申":1,"酉":1,"戌":2,"亥":-1},"亥":{"子":1,"丑":0,"寅":2,"卯":1,"辰":0,"巳":null,"午":-1,"未":0,"申":0,"酉":0,"戌":0,"亥":2},"子":{"子":2,"丑":0,"寅":1,"卯":1,"辰":0,"巳":-1,"午":null,"未":0,"申":0,"酉":0,"戌":0,"亥":1},"丑":{"子":-1,"丑":2,"寅":0,"卯":0,"辰":1,"巳":0,"午":0,"未":null,"申":1,"酉":1,"戌":1,"亥":-1}};
function quantFormat(n){return (n>0?'+':'')+String(Math.round(n*10)/10)}
function quantMarkup(branch){
 const m=monthInfo()?.branch,d=dayBranch();
 if(!branch||!m)return '';
 const mv=quantMonth[m]?.[branch],dv=d?quantDay[d]?.[branch]:undefined;
 if(typeof mv!=='number')return '';
 const hasDay=typeof dv==='number',isClash=d&&dv===null;
 const total=hasDay?Math.round((mv+dv)*10)/10:mv;
 const tip='月建'+m+'对'+branch+'：'+quantFormat(mv)+(hasDay?'；日辰'+d+'对'+branch+'：'+quantFormat(dv)+'；合计：'+quantFormat(total):isClash?'；日辰'+d+'冲'+branch+'（日冲不计数字）':'；未指定日柱，不计日辰分');
 return ' <span class="am-quant" title="'+safe(tip)+'" aria-label="'+safe(tip)+'">'+quantFormat(total)+'</span>';
}
// 伏神独立按其自身地支计算：不得继承飞神的五行、旺衰或分数。
function fushenMarkup(fu){
 if(!fu?.najia)return '—';
 const branch=fu.branch||fu.najia.slice(-1),element=fu.element||branchElement[branch];
 return '<span class="am-fu-najia">'+safe(fu.najia)+'</span>'+emptyMark(branch)+tagsMarkup(branch)+
  '<br><span class="am-fu-element">'+safe(element||'')+'</span>'+
  (monthInfo()&&element?' <span class="am-strength">'+seasonalStrength(element,monthInfo().branch)+'</span>'+quantMarkup(branch):'');
}
function emptyMark(branch){const di=dayInfo();return di&&branch&&di.empty.includes(branch)?'<span class="am-void-char" title="日旬空：'+safe(di.empty)+'" aria-label="日旬空">空</span> ':''}
function setupMonthBranch(){const pillar=document.getElementById('liuyao-day-pillar');if(!pillar||document.getElementById('liuyao-month-branch'))return;const label=document.createElement('label');label.textContent='月建地支（按节气核对）';const select=document.createElement('select');select.id='liuyao-month-branch';select.innerHTML='<option value="">未选择月建</option>'+Array.from(monthBranches).map(b=>'<option value="'+b+'">'+b+'月（'+branchElement[b]+'）</option>').join('');label.appendChild(select);pillar.closest('label')?.insertAdjacentElement('afterend',label);select.addEventListener('change',refresh)}
function monthInfo(){const branch=document.getElementById('liuyao-month-branch')?.value||'';return branch?{branch,element:branchElement[branch]}:null}
const emptyByXun=['戌亥','申酉','午未','辰巳','寅卯','子丑'];
// 地支六冲、六合：仅作关系标注，不自动断吉凶。
const clashes={子:'午',丑:'未',寅:'申',卯:'酉',辰:'戌',巳:'亥',午:'子',未:'丑',申:'寅',酉:'卯',戌:'辰',亥:'巳'};
const harmonies={子:'丑',丑:'子',寅:'亥',亥:'寅',卯:'戌',戌:'卯',辰:'酉',酉:'辰',巳:'申',申:'巳',午:'未',未:'午'};
function dayBranch(){return dayInfo()?.value?.[1]||''}
function branchTags(branch){if(!branch)return [];const tags=[],d=dayBranch(),m=monthInfo()?.branch;
 if(d&&clashes[d]===branch)tags.push('日冲');
 if(m&&clashes[m]===branch)tags.push('月破（六冲）');
 if(d&&harmonies[d]===branch)tags.push('日合');
 if(m&&harmonies[m]===branch)tags.push('月合');
 return tags;
}
function tagsMarkup(branch){return branchTags(branch).map(t=>'<span class="am-branch-tag">'+t+'</span>').join('')}

function dayInfo(){const value=document.getElementById('liuyao-day-pillar')?.value||'';const idx=ganzhi.indexOf(value);return idx<0?null:{value,xun:Math.floor(idx/10),empty:emptyByXun[Math.floor(idx/10)]}}
function setupDayPillar(){
 const stem=document.getElementById('day-stem');if(!stem||document.getElementById('liuyao-day-pillar'))return;
 const label=document.createElement('label');label.textContent='日柱（请按万年历核对，用于旬空）';
 const select=document.createElement('select');select.id='liuyao-day-pillar';select.setAttribute('aria-label','日柱六十甲子');
 select.innerHTML='<option value="">未选择日柱（不计算旬空）</option>'+ganzhi.map(g=>'<option value="'+g+'">'+g+'日</option>').join('');
 label.appendChild(select);stem.closest('label')?.insertAdjacentElement('afterend',label);
 select.addEventListener('change',()=>{if(select.value){stem.value=select.value[0];stem.dispatchEvent(new Event('change',{bubbles:true}))}refresh()});
 stem.addEventListener('change',()=>{if(select.value&&select.value[0]!==stem.value){select.value='';refresh()}});
}

const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const $=sel=>host.querySelector(sel);
function tri(vals){return trigramBits[vals.map(v=>v%2).join('')]||'?'}
function changed(vals){return vals.map(v=>v===6?7:v===9?8:v)}
function mutual(vals){return [vals[1],vals[2],vals[3],vals[2],vals[3],vals[4]].map(v=>v%2?7:8)}
function relation(a,b){if(a===b)return '比和';if(generates[a]===b)return '体生用';if(generates[b]===a)return '用生体';if(controls[a]===b)return '体克用';if(controls[b]===a)return '用克体';return '待核对'}
function glyph(v){return '<span class="am-yao '+([6,9].includes(v)?'am-moving':'')+'"><i></i>'+(v%2===0?'<i></i>':'')+'</span>'}
function hexCard(title,vals){const h=XingguiLiuyaoHexagram.get(vals),up=tri(vals.slice(3)),lo=tri(vals.slice(0,3));return '<div class="am-hex"><div class="am-hex-heading">'+title+'</div><div class="am-half"><div class="am-glyphs">'+[...vals].slice(3).reverse().map(glyph).join('')+'</div><div>'+up+' · '+trigramElement[up]+'</div></div><div class="am-half"><div class="am-glyphs">'+[...vals].slice(0,3).reverse().map(glyph).join('')+'</div><div>'+lo+' · '+trigramElement[lo]+'</div></div><div class="am-hexname">'+safe(h.name)+'</div></div>'}
// 卦象解释为象征性辅助阅读；不替代六爻纳甲、用神、日月旺衰判断。
const trigramImages={乾:'天，刚健、主动、原则',兑:'泽，交流、喜悦、沟通',离:'火，光明、依附、辨明',震:'雷，启动、行动、震动',巽:'风，进入、渗透、顺势',坎:'水，险阻、流动、审慎',艮:'山，停止、边界、稳守',坤:'地，承载、柔顺、包容'};
const relationMeaning={比和:'体用同属一行，象征双方性质相近；仍须结合实际条件判断。',体生用:'体的一方生助用的一方，象征自身投入或付出；应关注投入与回报。',用生体:'用的一方生助体的一方，象征外部条件提供支持；仍需核对实际情况。',体克用:'体的一方克制用的一方，象征自身主动施加影响；需考虑执行成本。',用克体:'用的一方克制体的一方，象征外部条件形成约束；宜评估压力与风险。'};
// 现代白话主题提示（非《周易》原文、非吉凶断语），按卦名映射。
const plainThemes={'乾':'重在自强与持守原则，行动需把握时机。','坤':'重在包容与承载，宜稳健配合、厚积基础。','屯':'事情初起多阻滞，先理清资源与步骤。','蒙':'面对未知宜求教、学习，避免凭猜测行事。','需':'条件尚未成熟时，宜等待并做好准备。','讼':'分歧出现时，宜厘清事实、规则与边界。','师':'需要组织与纪律，行动宜明确责任。','比':'重在联结与互助，需辨别合作基础。','小畜':'力量仍在积累，宜从小处稳步推进。','履':'行动涉及分寸与礼序，宜谨慎守规。','泰':'上下沟通较顺畅，宜维持协调与秩序。','否':'交流受阻，宜先改善沟通与内部条件。','同人':'共同目标与协作是重点，宜求同存异。','大有':'资源较充裕，宜善用优势而不骄满。','谦':'以谦逊平衡关系，避免争强好胜。','豫':'气氛活跃，宜预作规划，防止松懈。','随':'顺势而行，关键在辨明值得追随的方向。','蛊':'旧问题需要整顿，宜从根源着手。','临':'面对新阶段，宜主动关照并审慎推进。','观':'先观察全局，再作判断与行动。','噬嗑':'障碍需要厘清并处理，宜坚持公正与规则。','贲':'形式与表达有价值，但不能忽略实质。','剥':'原有基础受到削弱，宜守住核心、减少冒进。','复':'经历变化后回归正轨，宜从小处重新开始。','无妄':'重在诚实与顺其自然，避免妄动。','大畜':'积蓄能力与资源，宜先充实再行动。','颐':'关注滋养与言行，保持适度和节制。','大过':'负担或压力偏重，宜及时调整支撑结构。','坎':'反复遇险时，宜守信审慎、寻找稳妥路径。','离':'重在辨明与依附，保持清晰判断。','咸':'相互感应与沟通是重点，宜真诚互动。','恒':'坚持长期原则，重在持续而非一时冲动。','遁':'适时退让是策略，宜审时度势保存实力。','大壮':'力量增强时更需守正，避免逞强。','晋':'有推进与发展之象，宜稳步争取认可。','明夷':'外部环境不明朗时，宜保护自身判断与实力。','家人':'重在内部秩序、责任分工与有效沟通。','睽':'观点不同时，宜理解差异并寻找共同点。','蹇':'前路受阻，宜调整路线并寻求支持。','解':'压力有望松动，宜处理遗留问题。','损':'有所减损以求平衡，宜辨别必要取舍。','益':'重在增益与互惠，宜把握实际可行的改善。','夬':'需要明确决断，但应注意方式与风险。','姤':'意外相遇或新因素出现，宜谨慎辨识。','萃':'人群与资源聚集，宜建立共同规则。','升':'逐步积累向上，宜循序渐进。','困':'资源或条件受限，宜守住信念并寻求突破。','井':'重在长期可用的基础与共享资源。','革':'旧模式需要改变，宜把握时机并争取共识。','鼎':'重在更新制度与承载责任，宜稳固基础。','震':'突发变化带来震动，宜镇定应对。','艮':'适时停止、划清边界，避免过度行动。','渐':'发展需要时间，宜按步骤稳步推进。','归妹':'关系或安排未必对等，宜审视角色与条件。','丰':'局面充实而繁盛，宜居安思危。','旅':'处于流动或陌生环境，宜谨慎适应。','巽':'以柔和方式深入推进，重在持续沟通。','兑':'交流与喜悦有助关系，宜真诚而有节制。','涣':'分散局面需要凝聚，宜化解隔阂。','节':'设立合理边界与节度，避免过犹不及。','中孚':'诚信是建立信任与合作的基础。','小过':'宜谨慎处理小事，不宜好高骛远。','既济':'阶段性完成后，仍需维护成果、防范松懈。','未济':'事情尚未完成，宜厘清步骤、谨慎收尾。'};
function plainTheme(h){
 const name=String(h?.name||'').trim();
 const aliases={'乾为天':'乾','坤为地':'坤','坎为水':'坎','离为火':'离','震为雷':'震','巽为风':'巽','艮为山':'艮','兑为泽':'兑'};
 const key=aliases[name]||name;
 return plainThemes[key]||'';
}
function movementDetails(original){
 const movements=original.map((v,i)=>v===6||v===9?{name:names[i]+'爻',change:v===6?'老阴（6）→阳爻':'老阳（9）→阴爻'}:null).filter(Boolean);
 if(!movements.length)return '本次没有动爻；变卦与本卦相同。';
 return '实际动爻：'+movements.map(x=>x.name+' '+x.change).join('；')+'。';
}
function imageExplain(title,values,kind,original){
 const h=XingguiLiuyaoHexagram.get(values),up=tri(values.slice(3)),lo=tri(values.slice(0,3)),t=classicEntry(h);
 const lead=kind==='base'?'本卦用于观察起卦时的整体处境。':kind==='mutual'?'互卦由本卦二、三、四爻及三、四、五爻构成，可辅助观察内部结构与发展过程。':'变卦由本卦实际动爻阴阳转换形成，可辅助观察变化后的卦象。';
 const movement=kind==='changed'?movementDetails(original):'';
 const theme=plainTheme(h);
 return '<section class="am-relation am-image-explain"><b>'+title+' · '+safe(h.name)+'｜卦象解释</b><div>'+lead+'</div>'+(theme?'<div><strong>白话核心：</strong>'+safe(theme)+'</div>':'')+'<div>上卦'+up+'：'+safe(trigramImages[up]||'待核对')+'；下卦'+lo+'：'+safe(trigramImages[lo]||'待核对')+'。</div>'+(t?.guaci?'<div><strong>经典卦辞：</strong>'+safe(t.guaci)+'</div>':'<div class="am-hint">该卦经典卦辞暂未读取；不以自动文字代替原文。</div>')+(t?.xiang?'<div><strong>大象辞：</strong>'+safe(t.xiang)+'</div>':'')+(movement?'<div>'+safe(movement)+'</div>':'')+'<div class="am-hint">卦象说明属于象征性辅助解读，不是针对占问的确定性预测。</div></section>';
}
function renderImage(vals){
 const change=changed(vals),mu=mutual(vals),base=XingguiLiuyaoHexagram.get(vals),up=tri(vals.slice(3)),lo=tri(vals.slice(0,3)),body=trigramElement[lo],use=trigramElement[up];
 const time=document.getElementById('when')?.value||'',rel=relation(body,use);
 return '<div class="am-date">起卦时间：'+safe(time.replace('T',' '))+'<div class="am-hint">四柱、节气与旺衰须经可靠历法计算后显示；不使用未经核对的干支。</div></div>'+
 '<div class="am-three">'+hexCard('本卦',vals)+hexCard('互卦',mu)+hexCard('变卦',change)+'</div>'+
 imageExplain('本卦',vals,'base',vals)+imageExplain('互卦',mu,'mutual',vals)+imageExplain('变卦',change,'changed',vals)+
 '<div class="am-relation"><b>体用分析｜五行关系说明</b><div>当前示例按下卦为体、上卦为用：体 '+lo+'（'+body+'） · 用 '+up+'（'+use+'）</div><div>五行关系：<strong>'+rel+'</strong></div><div>'+safe(relationMeaning[rel]||'关系待核对')+'</div><div class="am-hint">体用属于梅花易数的辅助框架，取法依流派与动爻位置而异；不等同于纳甲六爻断卦，不作未经校验的吉凶断语。</div></div>'+
 '<div class="am-relation"><b>本卦</b> '+safe(base.name)+' · '+safe(base.palace)+'宫　　<b>互卦</b> '+safe(XingguiLiuyaoHexagram.get(mu).name)+'　　<b>变卦</b> '+safe(XingguiLiuyaoHexagram.get(change).name)+'</div>';
}
function getNajia(vals,stem){try{return XingguiLiuyaoNajia.get(vals,stem)}catch(e){console.error('六爻纳甲排盘失败',e);return null}}
function getChangedNajia(vals,stem){try{return XingguiLiuyaoNajia.getChanged(vals,stem)}catch(e){console.error('变卦六亲失败',e);return null}}
function plainChart(vals){
 const h=XingguiLiuyaoHexagram.get(vals),c=XingguiLiuyaoHexagram.get(changed(vals));
 const stem=document.getElementById('day-stem')?.value||'';
 const a=getNajia(vals,stem),b=getChangedNajia(vals,stem);
 const di=dayInfo();const text=['星轨智盘 · 六爻卦盘','本卦：'+h.name+' → 变卦：'+c.name,'占问：'+(document.getElementById('question')?.value||'未填写'),'用神：'+(document.getElementById('yongshen')?.value||'未选择'),'起卦时间：'+(document.getElementById('when')?.value||'未填写'),'日干：'+(stem||'未选择'),'日柱：'+(di?.value||'未选择')+'；旬空：'+(di?.empty||'未计算'),'月建：'+(monthInfo()?.branch||'未选择')+'；月令：'+(monthInfo()?.element||'未计算'),''];
 [5,4,3,2,1,0].forEach(i=>{
  const v=vals[i],r=a?.lines[i],t=b?.lines[i];
  text.push([['初','二','三','四','五','上'][i]+'爻',r?.spirit||'—',r?.relative||'—',v%2?'阳':'阴',v===6||v===9?'动':'静',r?.najia||'—',monthInfo()?seasonalStrength(r?.element,monthInfo().branch):'—',r?.branch?branchTags(r.branch).join('、')||'—':'—','→',v===6||v===9?(t?.najia||'—')+' '+(t?.element||''):'—',v===6||v===9?(t?.relative||'—'):'—'].join(' | '));
 });
 text.push('六爻分析依据：所选日干 '+(stem||'未选')+'；所选日柱 '+(di?.value||'未选')+'；日旬空 '+(di?.empty||'未计算')+'；所选月建 '+(monthInfo()?.branch||'未选')+'。');
  text.push('历法参考（不用于覆盖手动选择）：'+(verifiedCalendar?.year||'—')+'年 '+(verifiedCalendar?.month||'—')+'月 '+(verifiedCalendar?.day||'—')+'日 '+(verifiedCalendar?.hour||'—')+'时。');
  text.push('说明：旬空依用户核对的日柱；旺相休囚死仅为四时五行关系，日冲、月破、日合、月合仅为地支关系。伏神按京房本宫纯卦补缺六亲；其他神煞尚未计算。');
 return text.join('\n');
}
function pillarColors(pillar){
 if(!pillar||pillar.length!==2)return '<span class="am-pillar-missing">—</span>';
 const colors={甲:'wood',乙:'wood',寅:'wood',卯:'wood',丙:'fire',丁:'fire',巳:'fire',午:'fire',戊:'earth',己:'earth',辰:'earth',戌:'earth',丑:'earth',未:'earth',庚:'metal',辛:'metal',申:'metal',酉:'metal',壬:'water',癸:'water',亥:'water',子:'water'};
 return [...pillar].map(c=>'<span class="am-five-'+(colors[c]||'neutral')+'">'+safe(c)+'</span>').join('');
}
function pillarVoid(p){const i=ganzhi.indexOf(p||'');return i<0?'未计算':emptyByXun[Math.floor(i/10)]}
function coloredVoid(p){const v=pillarVoid(p);return v==='未计算'?'<span class="am-void-missing">未计算</span>':'<strong class="am-void-value">'+safe(v)+'</strong>'}
function calendarBoard(summaryHtml=''){
 const stamp=document.getElementById('when')?.value||'';
 const d=verifiedCalendar?.stamp===stamp?verifiedCalendar:null;
 const p=d?[["时",d.hour],["日",d.day],["月",d.month],["年",d.year]]:[];
 return '<section class="am-calendar-board am-yiy-board" aria-label="起卦四柱与空亡">'+
 '<div class="am-yiy-grid"><div class="am-yiy-time"><div>'+safe(stamp.replace('T',' ')||'未设置')+'</div><small>本地起卦时间</small>'+summaryHtml+'</div>'+
 (d?p.map(([label,value])=>'<div class="am-yiy-pillar"><span class="am-yiy-heading '+(label==='日'?'am-yiy-day':'')+'">'+label+'</span><strong>'+pillarColors(value)+'</strong></div>').join(''):'<div class="am-yiy-pending">四柱未计算</div>')+'</div>'+
 '<div class="am-manual-choice"><b>六爻分析采用（以当前选择为准）</b><div>日干 <strong>'+safe(document.getElementById('day-stem')?.value||'未选')+'</strong>　日柱 <strong>'+safe(dayInfo()?.value||'未选')+'</strong>　月建 <strong>'+safe(monthInfo()?.branch||'未选')+'</strong>　日旬空 <strong>'+safe(dayInfo()?.empty||'未计算')+'</strong></div><small>六神依所选日干，日旬空及日冲／日合依所选日柱，月令旺衰及月破／月合依所选月建。上方四柱仅为服务器历法参考，不覆盖手动选择。</small></div>'+'<div class="am-yiy-void"><b>空亡</b><span>年参考 ['+coloredVoid(d?.year)+']</span><span>月参考 ['+coloredVoid(d?.month)+']</span><span>日旬空（排盘） ['+coloredVoid(dayInfo()?.value)+']</span><span>时参考 ['+coloredVoid(d?.hour)+']</span></div>'+(d&&((dayInfo()?.value&&d.day!==dayInfo().value)||(monthInfo()?.branch&&d.month_branch!==monthInfo().branch))?'<div class="am-calendar-mismatch" role="note">注意：手动日柱／月建与起卦时间历法参考不同；六爻分析仍以手动选择为准。</div>':'')+'</section>';
}
function renderYao(vals){const h=XingguiLiuyaoHexagram.get(vals),newVals=changed(vals),ch=XingguiLiuyaoHexagram.get(newVals),stem=document.getElementById('day-stem')?.value||'',na=getNajia(vals,stem),nb=getChangedNajia(vals,stem),fushen=XingguiLiuyaoNajia.getFushen(vals),rows=[5,4,3,2,1,0].map(i=>{const a=na?.lines[i],b=nb?.lines[i],v=vals[i],moving=v===6||v===9,di=dayInfo(),isEmpty=Boolean(di&&a?.branch&&di.empty.includes(a.branch));return '<tr><td class="am-fushen">'+fushenMarkup(fushen[i])+'</td><td>'+safe(fushen[i]?.relative||'—')+'</td><td class="am-spirit">'+safe(a?.spirit||'—')+'</td><td>'+safe(a?.relative||'—')+'</td><td class="am-yaocell"><span class="am-line-inline">'+glyph(v)+'<span class="am-line-markers">'+(h.shi===i+1?' <em class="am-shi">世</em>':h.ying===i+1?' <em class="am-ying">应</em>':'')+(moving?' <em class="am-change-mark">'+(v===6?'×':'○')+'</em>':'')+'</span></span></td><td>'+safe(a?.najia||'—')+emptyMark(a?.branch)+tagsMarkup(a?.branch)+'<br><span class="am-element">'+safe(a?.element||'')+'</span>'+(monthInfo()&&a?.element?' <span class="am-strength">'+seasonalStrength(a.element,monthInfo().branch)+'</span>'+quantMarkup(a?.branch):'')+'</td><td class="am-changed-cell">'+(moving&&b?'<span class="am-changed-najia"><span class="am-five-'+({木:'wood',火:'fire',土:'earth',金:'metal',水:'water'}[b.element]||'neutral')+'">'+safe(b.najia||((b.stem||'')+(b.branch||'')))+'</span>'+emptyMark(b.branch)+'<span class="am-changed-element am-five-'+({木:'wood',火:'fire',土:'earth',金:'metal',水:'water'}[b.element]||'neutral')+'">'+safe(b.element||'')+'</span></span>':'')+'</td><td class="am-changed-relative">'+(moving&&b?safe(b.relative||''):'')+'</td></tr>'}).join('');return calendarBoard('<div class="am-date am-hex-summary"><strong>六爻专业卦盘</strong><br>本卦 '+safe(h.name)+'（'+safe(h.palace)+'宫） → 变卦 '+safe(ch.name)+'（'+safe(ch.palace)+'宫）<div class="am-hint">动爻：'+(vals.map((v,i)=>v===6||v===9?names[i]+'爻':null).filter(Boolean).join('、')||'无')+' · 世'+h.shi+'应'+h.ying+'<br>日柱：'+safe(dayInfo()?.value||'未选择')+' · 旬空：'+safe(dayInfo()?.empty||'未计算')+' · 月建：'+safe(monthInfo()?.branch||'未选择')+'<br>'+(stem?'日干：'+stem+'（当前选择）':'六亲、纳甲、伏神已排出；请选择日柱以显示六兽及旬空')+'</div></div>')+'<div class="am-export"><button type="button" data-copy-chart="1">复制六爻卦盘文字</button><span data-copy-feedback="1" aria-live="polite"></span></div><div class="am-scroll"><table class="am-prof"><colgroup><col style="width:9%"><col style="width:9%"><col style="width:9%"><col style="width:9%"><col style="width:13%"><col style="width:26%"><col style="width:13%"><col style="width:12%"></colgroup><thead><tr><th>伏神</th><th>六亲</th><th>六兽</th><th>六亲</th><th>本卦</th><th>装卦</th><th>变卦</th><th>六亲</th></tr></thead><tbody>'+rows+'</tbody></table></div><div class="am-relation"><b>月建与五行旺相休囚死</b><div class="am-hint">'+(monthInfo()?'已选月建：'+monthInfo().branch+'（'+monthInfo().element+'）；装卦五行已按月令显示旺相休囚死。':'请按节气核对月建地支后选择；不根据公历月份推算。')+' 小数字为所附书籍的月建分与日辰分相加；悬停可查看分项。日冲不作数字相加，另以日冲标识；该量化法仅供研究参考。</div></div><div class="am-relation"><b>神煞、空亡与伏神</b><div class="am-hint">旬空根据手动核对的日柱显示；日冲、月破、日合、月合按地支关系标注，不代表吉凶。伏神按京房本宫纯卦补缺六亲；驿马、桃花、贵人、文昌仍待规则校验。</div></div><div class="am-relation"><b>本卦</b> '+safe(h.name)+' · '+safe(h.palace)+'宫 · '+safe(h.stage)+'　　<b>变卦</b> '+safe(ch.name)+'</div>'}
// 64卦经典资料由 liuyao_classics_data.js 本地载入；不更动排盘引擎。
let chosen='base';
function canonicalClassicName(name){
 const s=String(name||'').replace(/[\s·．・]/g,'');
 const shortNames={'乾':'乾为天','坤':'坤为地','坎':'坎为水','离':'离为火','震':'震为雷','巽':'巽为风','艮':'艮为山','兑':'兑为泽'};
 return shortNames[s]||s;
}
function classicEntry(h){
 const db=window.XingguiLiuyaoClassics||{};
 const name=canonicalClassicName(h.name);
 if(db[name]||db[h.name])return db[name]||db[h.name];
 // 卦象引擎使用「鼎、蒙、复」等简称；经典库使用「火风鼎、山水蒙、地雷复」。
 // 只接受唯一后缀匹配，避免错配；八纯卦仍使用上面的明确名称映射。
 const matches=Object.keys(db).filter(key=>key.endsWith(name));
 return matches.length===1?db[matches[0]]:null;
}
let classicsRetryStarted=false;
function ensureClassicsLoaded(){
 if(window.XingguiLiuyaoClassics||classicsRetryStarted)return;
 classicsRetryStarted=true;
 const script=document.createElement('script');
 script.src='liuyao_classics_data.js?remain_classics_retry=20261022';
 script.async=true;
 script.onload=()=>{if(window.XingguiLiuyaoClassics)refresh();else console.error('经典资料脚本已加载，但未建立 XingguiLiuyaoClassics 变量');};
 script.onerror=()=>console.error('经典资料加载失败，请检查 liuyao_classics_data.js 的访问状态');
 document.head.appendChild(script);
}

function renderClassic(vals){
  ensureClassicsLoaded();
 const options=[['base','本卦',vals],['mutual','互卦',mutual(vals)],['changed','变卦',changed(vals)]];
 const selected=options.find(o=>o[0]===chosen)||options[0];
 const h=XingguiLiuyaoHexagram.get(selected[2]),t=classicEntry(h),up=tri(selected[2].slice(3)),lo=tri(selected[2].slice(0,3));
 const tab='<div class="am-subtabs" role="tablist" aria-label="易经本互变卦">'+options.map(o=>'<button type="button" data-classic="'+o[0]+'" aria-selected="'+(o[0]===chosen)+'">'+o[1]+' · '+safe(XingguiLiuyaoHexagram.get(o[2]).name)+'</button>').join('')+'</div>';
 const head='<div class="am-classichead"><div class="am-glyphs">'+[...selected[2]].reverse().map(glyph).join('')+'</div><div><h3>'+safe(h.name)+'</h3><div>'+up+'上'+lo+'下 · '+safe(h.palace)+'宫 · '+safe(h.stage)+'</div>'+(t?'<div>《周易》第'+t.number+'卦</div>':'')+'</div></div>';
 if(!t)return tab+head+'<div class="am-classic-pending"><b>经典资料尚未载入</b><p>请先执行安装包中的导入工具，生成 liuyao_classics_data.js，放到六爻页面同一目录。不会以未经核对的内容代替原典。</p></div>';
 // 仅本卦爻辞与起卦动爻一一对应；互卦、变卦不沿用本卦动爻标记。
 const lines=(t.lines||[]).map((line,i)=>{
  const moving=chosen==='base'&&(vals[i]===6||vals[i]===9);
  const highlight=moving?' style="background:#fff4d8;border:2px solid #f59e0b;border-radius:10px;padding:12px;margin:8px 0"':'';
  const marker=moving?'<span style="display:inline-block;background:#f59e0b;color:#10213b;border-radius:6px;padding:2px 8px;margin-left:10px;font-weight:800">★ 动爻重点</span>':'';
  const explanation=window.XingguiLiuyaoLineExplanations?.[Object.keys(window.XingguiLiuyaoLineExplanations||{}).find(k=>k===canonicalClassicName(h.name)||k.endsWith(canonicalClassicName(h.name)))||'']?.[i];
  const explanationHtml=explanation?'<div class="am-line-interpretation" style="margin-top:10px;padding:10px 12px;background:#f4f7fb;border-left:3px solid #4775b5;border-radius:6px"><div style="font-weight:700;margin-bottom:6px">爻辞白话解读 <small style="font-weight:400">（解释性初稿，非经典原文）</small></div><p><b>白话释义：</b>'+safe(explanation.plain)+'</p><p><b>象义分析：</b>'+safe(explanation.symbolism)+'</p><p><b>占问启示：</b>'+safe(explanation.guidance)+'</p></div>':'';
  return '<div class="am-classic-line"'+highlight+'><b>'+safe(['初爻','二爻','三爻','四爻','五爻','上爻'][i])+'</b>'+marker+'<p>'+safe(line)+'</p>'+(t.line_xiang?.[i]?'<div class="am-classic-small"><b>小象：</b>'+safe(t.line_xiang[i])+'</div>':'')+explanationHtml+'</div>';
 }).join('');
 return tab+head+'<section class="am-classic-content"><div class="am-classic-section"><h4>卦辞</h4><p>'+safe(t.guaci)+'</p></div><div class="am-classic-section"><h4>彖曰</h4><p>'+safe(t.tuan)+'</p></div><div class="am-classic-section"><h4>大象曰</h4><p>'+safe(t.xiang)+'</p></div><div class="am-classic-section"><h4>六爻爻辞与小象</h4>'+lines+'</div>'+(t.extra?'<div class="am-classic-section"><h4>特别爻辞</h4><p>'+safe(t.extra)+'</p></div>':'')+'<p class="am-classic-source">来源：<a href="'+safe(t.source)+'" target="_blank" rel="noopener noreferrer">维基文库《周易》原文</a> · 修订号 '+safe(t.revision||'未记录')+'。原典存在版本异文，请以所标来源为准。</p></section>';
}
function refresh(){if(!Array.isArray(window.yaos)&&typeof yaos==='undefined')return;const vals=typeof yaos!=='undefined'?[...yaos]:window.yaos;if(vals.length!==6)return;const v0=$('[data-view="0"]'),v1=$('[data-view="1"]'),v2=$('[data-view="2"]');if(!v0||!v1||!v2)return;v0.innerHTML=renderYao(vals);v1.innerHTML=renderClassic(vals);v2.innerHTML=renderImage(vals)}
host.addEventListener('click',e=>{const copy=e.target.closest('[data-copy-chart]');if(copy){
 const vals=typeof yaos!=='undefined'?[...yaos]:window.yaos;
 if(!Array.isArray(vals)||vals.length!==6)return;
 const content=plainChart(vals),feedback=host.querySelector('[data-copy-feedback]');
 if(navigator.clipboard?.writeText){navigator.clipboard.writeText(content).then(()=>{if(feedback)feedback.textContent='已复制';}).catch(()=>{if(feedback)feedback.textContent='复制失败，请检查浏览器权限';});}
 else if(feedback)feedback.textContent='浏览器不支持直接复制';
 return;
 }const btn=e.target.closest('[data-classic]');if(btn){chosen=btn.dataset.classic;refresh()}});
const observer=new MutationObserver(()=>{if(host.hidden)return;refresh()});
// 旧三视图每次 draw() 后更新 DOM；只监听面板显隐及旧视图第一个内容区。
observer.observe(host,{attributes:true,attributeFilter:['hidden']});
const originalDraw=draw;draw=function(){originalDraw();refresh()};
document.getElementById('day-stem')?.addEventListener('change',refresh);
['question','yongshen','when'].forEach(id=>document.getElementById(id)?.addEventListener('change',refresh));
setupDayPillar();
setupMonthBranch();
// Auto-populate only when the server returns a verified calendar result.
const timeField=document.getElementById('when');
const daySelect=document.getElementById('liuyao-day-pillar');
const monthSelect=document.getElementById('liuyao-month-branch');
const note=document.createElement('div');note.id='liuyao-calendar-status';note.setAttribute('role','status');note.className='am-hint';
if(timeField){timeField.closest('label')?.insertAdjacentElement('afterend',note)}
let verifiedCalendar=null;
let lastCalendarRequest=0;
async function syncCalendar(){
 const stamp=timeField?.value||'';verifiedCalendar=null;if(!stamp)return;
 const request=++lastCalendarRequest;
 note.textContent='正在核对日柱与节气月建…';
 try{
  const response=await fetch('/api/liuyao/calendar?when='+encodeURIComponent(stamp),{credentials:'same-origin'});
  const data=await response.json();if(request!==lastCalendarRequest||timeField.value!==stamp)return;
  if(!response.ok||data.status!=='ok')throw Error(data.message||'历法服务不可用');
  if(!ganzhi.includes(data.day)||!monthBranches.includes(data.month_branch))throw Error('历法结果格式无效');
  verifiedCalendar={...data,stamp};
  window.XingguiLiuyaoVerifiedCalendar=verifiedCalendar;
  window.dispatchEvent(new CustomEvent('xinggui:liuyao-calendar-ready',{detail:verifiedCalendar}));
  if(window.XingguiLiuyaoCalendarMode!=='manual'){
    const stemSelect=document.getElementById('day-stem');
    if(stemSelect){stemSelect.value=data.day[0];stemSelect.dispatchEvent(new Event('change',{bubbles:true}));}
    daySelect.value=data.day;daySelect.dispatchEvent(new Event('change',{bubbles:true}));
    monthSelect.value=data.month_branch;monthSelect.dispatchEvent(new Event('change',{bubbles:true}));
  }
  note.textContent='已按本地起卦时间计算：'+data.year+'年 '+data.month+'月 '+data.day+'日 '+data.hour+'时；月建'+data.month_branch+'。不含真太阳时校正。';
 }catch(err){if(request!==lastCalendarRequest)return;verifiedCalendar=null;note.textContent='自动历法暂不可用：'+err.message+'。请手动核对日柱与月建，避免错误排盘。';}
}
timeField?.addEventListener('change',syncCalendar);
timeField?.addEventListener('input',syncCalendar);
// Remain: initAccount() is async; the original page sets #when only after
// awaiting authentication inside its DOMContentLoaded callback. A 0ms timer
// races that callback and can see an empty value forever. Wait for the actual
// datetime-local value before the first calendar request, without altering auth.
let initialAttempts=0;
function syncWhenReady(){
 if(timeField?.value){syncCalendar();return;}
 if(++initialAttempts<60)setTimeout(syncWhenReady,250);
 else note.textContent='尚未取得起卦时间；请选择时间后自动核对日柱与月建。';
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',syncWhenReady,{once:true});
else syncWhenReady();
refresh();
})();
