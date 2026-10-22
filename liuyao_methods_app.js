/* 星轨智盘：Remain 增量。保留原手动六爻，移除重复的「自定义组合卦象」入口；保留时间起卦。 */
(function(){'use strict';
const trigramBits={乾:[1,1,1],兑:[1,1,0],离:[1,0,1],震:[1,0,0],巽:[0,1,1],坎:[0,1,0],艮:[0,0,1],坤:[0,0,0]};
const order=['乾','兑','离','震','巽','坎','艮','坤'];
function byId(id){return document.getElementById(id)}
function timeMethod(){
 const val=byId('when').value;
 const m=/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(val||'');
 if(!m)throw Error('请先选择完整起卦日期与时间');
 const y=+m[1],mo=+m[2],d=+m[3],h=+m[4],minute=+m[5];
 const check=new Date(y,mo-1,d,h,minute);
 if(check.getFullYear()!==y||check.getMonth()!==mo-1||check.getDate()!==d||check.getHours()!==h||check.getMinutes()!==minute)throw Error('日期或时间无效');
 const upper=order[(y+mo+d-1)%8],lower=order[(y+mo+d+h-1)%8],moving=(y+mo+d+h-1)%6+1;
 const bits=[...trigramBits[lower],...trigramBits[upper]];
 yaos=bits.map((bit,i)=>i+1===moving?(bit?9:6):(bit?7:8));
 draw();
 byId('ly-method-info').textContent=`公历数字时间法：${upper}上${lower}下，第${moving}爻动。使用公历年＋月＋日与24小时制小时取余；不是传统农历梅花时间起卦。`;
}
function setup(){
 const mode=byId('mode'),manual=byId('manual');if(!mode||!manual)return;
 // 清理旧版重复入口，保留原手动六爻的全部控件及实时预览。
 [...mode.options].filter(o=>o.value==='custom'||o.value==='time').forEach(o=>o.remove());
 mode.add(new Option('时间起卦（公历数字法）','time'));
 const pane=document.createElement('div');pane.id='ly-extra';pane.className='panel';pane.style.display='none';
 pane.innerHTML='<h2>时间起卦</h2><p class="notice">目前为公历数字时间法，不等同于传统农历梅花易数时间起卦。请先选择上方日期时间。</p><button type="button" id="ly-time-apply">按所选时间起卦</button><p class="small" id="ly-method-info" aria-live="polite"></p>';
 manual.insertAdjacentElement('afterend',pane);
 const previous=mode.onchange;
 mode.onchange=function(){
   if(typeof previous==='function')previous.call(mode);
   const v=mode.value;
   pane.style.display=v==='time'?'block':'none';
   byId('toss').style.display=v==='coins'?'':'none';
   byId('random').style.display=v==='coins'?'':'none';
   // 避免从一种方法切换到另一种时，仍显示上一卦。
   yaos=[];draw();
   byId('ly-method-info').textContent='';
 };
 byId('ly-time-apply').onclick=()=>{try{timeMethod()}catch(e){alert(e.message)}};
 const css=document.createElement('style');css.textContent='#ly-extra button{min-height:46px}#ly-extra{margin-top:12px}';document.head.appendChild(css);
 mode.onchange();
}
window.addEventListener('DOMContentLoaded',setup);
})();
