/* 星轨智盘：Supabase Auth 统一登录。密码不进入本地存储。 */
(function(root){
'use strict';
let client=null,active=null,loaded=false;
const listeners=[];
function emit(){for(const f of listeners){try{f(active)}catch(e){console.warn(e)}}}
function profile(){return active?.profile?{...active.profile}:null}
function account(){return active?{id:active.id,profile:profile()}:null}
function moduleContext(kind){const a=account();return a?{module:kind,userId:a.id,profile:a.profile,birth:{...a.profile}}:null}
function requireLogin(){if(active)return true;location.replace('index.html');return false}
function onChange(fn){listeners.push(fn);if(loaded)fn(active)}
async function init(){
 const cfg=await fetch('/api/public-config',{cache:'no-store'}).then(r=>r.json());
 if(cfg.status!=='ok')throw Error(cfg.message||'Supabase 尚未配置');
 if(!root.supabase?.createClient)throw Error('Supabase SDK 加载失败，请检查网络');
 client=root.supabase.createClient(cfg.supabase_url,cfg.supabase_publishable_key,{auth:{autoRefreshToken:true,persistSession:true,detectSessionInUrl:true}});
 client.auth.onAuthStateChange((event,_session)=>{
   if(event==='PASSWORD_RECOVERY'){for(const fn of recoveryListeners){try{fn()}catch(e){console.warn(e)}}}
   setTimeout(()=>refresh().catch(console.error),0);
 });
 await refresh();return client;
}
async function refresh(){
 if(!client)return null;
 const {data:{user},error}=await client.auth.getUser();
 if(error||!user){active=null;loaded=true;emit();return null}
 const {data, error:pe}=await client.from('profiles').select('name,gender,calendar,year,month,day,hour,minute').eq('id',user.id).maybeSingle();
 if(pe)console.warn('档案读取失败:',pe.message);
 active={id:user.id,profile:data?{...data,email:user.email}:null,email:user.email};loaded=true;emit();return active;
}
async function signup(email,password){
 const {data,error}=await client.auth.signUp({email,password});if(error)throw Error(error.message);
 return data;
}
async function login(email,password){
 const {error}=await client.auth.signInWithPassword({email,password});if(error)throw Error(error.message);
 return refresh();
}
async function loginWithGoogle(){
 await ready;
 if(!client)throw Error('Supabase 尚未初始化');
 const redirectTo=new URL('index.html',root.location.href).href;
 const {data,error}=await client.auth.signInWithOAuth({provider:'google',options:{redirectTo}});
 if(error)throw Error(error.message);
 return data;
}

/* 与现有 index.html 认证界面保持一致：仅补齐缺少的公开方法。 */
const recoveryListeners=[];
function onPasswordRecovery(fn){
 if(typeof fn!=='function')throw TypeError('密码恢复回调必须是函数');
 recoveryListeners.push(fn);
 return ()=>{const i=recoveryListeners.indexOf(fn);if(i>=0)recoveryListeners.splice(i,1)};
}
async function sendPasswordReset(email){
 await ready;
 if(!client)throw Error('Supabase 尚未初始化');
 const redirectTo=new URL('index.html',root.location.href).href;
 const {data,error}=await client.auth.resetPasswordForEmail(email,{redirectTo});
 if(error)throw Error(error.message);
 return data;
}
async function updatePassword(password){
 await ready;
 if(!client)throw Error('Supabase 尚未初始化');
 const {data,error}=await client.auth.updateUser({password});
 if(error)throw Error(error.message);
 return data;
}
async function sendPhoneOtp(phone,channel='sms',shouldCreateUser=false){
 await ready;
 if(!client)throw Error('Supabase 尚未初始化');
 if(!['sms','whatsapp'].includes(channel))throw Error('不支持的手机验证渠道');
 const {data,error}=await client.auth.signInWithOtp({phone,options:{channel,shouldCreateUser:!!shouldCreateUser}});
 if(error)throw Error(error.message);
 return data;
}
async function verifyPhoneOtp(phone,token){
 await ready;
 if(!client)throw Error('Supabase 尚未初始化');
 const {data,error}=await client.auth.verifyOtp({phone,token,type:'sms'});
 if(error)throw Error(error.message);
 await refresh();
 return data;
}

async function saveProfile(p){
 const {data:{user},error:ue}=await client.auth.getUser();if(ue||!user)throw Error('请先完成邮箱验证并登录');
 const fields={id:user.id,name:p.name,gender:p.gender,calendar:p.calendar||'solar',year:Number(p.year),month:Number(p.month),day:Number(p.day),hour:Number(p.hour),minute:Number(p.minute||0)};
 const {error}=await client.from('profiles').upsert(fields,{onConflict:'id'});if(error)throw Error(error.message);
 return refresh();
}
async function accessToken(){
 if(!client)return null;
 const {data,error}=await client.auth.getSession();
 if(error)return null;
 return data?.session?.access_token||null;
}
async function logout(){if(client)await client.auth.signOut();active=null;loaded=true;emit()}
const ready=init().catch(e=>{loaded=true;emit();console.error(e);throw e});
root.XingguiSession=Object.freeze({ready,refresh,account,profile,moduleContext,requireLogin,onChange,signup,login,loginWithGoogle,onPasswordRecovery,sendPasswordReset,updatePassword,sendPhoneOtp,verifyPhoneOtp,saveProfile,accessToken,logout});
})(window);
