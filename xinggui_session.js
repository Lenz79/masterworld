/* 星轨智盘：Supabase Auth 统一登录。密码不进入本地存储。 */
(function(root){
'use strict';
let client=null,active=null,loaded=false;
const listeners=[];
function emit(){for(const f of listeners){try{f(active)}catch(e){console.warn(e)}}}
function profile(){return active?.profile?{...active.profile}:null}
function account(){return active?{id:active.id,email:active.email,profile:profile()}:null}
function moduleContext(kind){const a=account();return a?{module:kind,userId:a.id,profile:a.profile,birth:a.profile?{...a.profile}:null}:null}
function requireLogin(){if(active)return true;location.replace('index.html');return false}
function onChange(fn){listeners.push(fn);if(loaded)fn(active)}
async function init(){
 const response=await fetch('/api/public-config',{cache:'no-store'});
 if(!response.ok)throw Error('无法获取认证配置（HTTP '+response.status+'），请检查 server.py');
 const cfg=await response.json();
 if(cfg.status!=='ok')throw Error(cfg.message||'Supabase 尚未配置');
 if(!root.supabase?.createClient)throw Error('Supabase SDK 加载失败，请检查网络');
 client=root.supabase.createClient(cfg.supabase_url,cfg.supabase_publishable_key,{auth:{autoRefreshToken:true,persistSession:true,detectSessionInUrl:true}});
 client.auth.onAuthStateChange((_event,_session)=>{setTimeout(()=>refresh().catch(console.error),0)});
 await refresh();return client;
}
async function refresh(){
 if(!client)return null;
 const {data:authData,error}=await client.auth.getUser();
 const user=authData?.user;
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
 if(!client)throw Error('登录服务尚未就绪');
 const redirectTo=new URL('index.html',root.location.href).href;
 const {data,error}=await client.auth.signInWithOAuth({provider:'google',options:{redirectTo}});
 if(error)throw Error(error.message);
 return data;
}
async function sendPhoneOtp(phone){
 if(!client)throw Error('登录服务尚未就绪');
 const {error}=await client.auth.signInWithOtp({phone,options:{shouldCreateUser:true}});
 if(error)throw Error(error.message);
}
async function verifyPhoneOtp(phone,token){
 if(!client)throw Error('登录服务尚未就绪');
 const {error}=await client.auth.verifyOtp({phone,token,type:'sms'});
 if(error)throw Error(error.message);
 return refresh();
}
async function saveProfile(p){
 const {data:{user},error:ue}=await client.auth.getUser();if(ue||!user)throw Error('请先完成邮箱验证并登录');
 const fields={id:user.id,name:p.name,gender:p.gender,calendar:p.calendar||'solar',year:Number(p.year),month:Number(p.month),day:Number(p.day),hour:Number(p.hour),minute:Number(p.minute||0)};
 const {error}=await client.from('profiles').upsert(fields,{onConflict:'id'});if(error)throw Error(error.message);
 return refresh();
}
async function sendPasswordReset(email){
 if(!client)throw Error('登录服务尚未就绪');
 const redirectTo=new URL('index.html',root.location.href).href;
 const {error}=await client.auth.resetPasswordForEmail(email,{redirectTo});
 if(error)throw Error(error.message);
}
async function updatePassword(password){
 if(!client)throw Error('登录服务尚未就绪');
 const {error}=await client.auth.updateUser({password});
 if(error)throw Error(error.message);
}
function onPasswordRecovery(fn){
 if(!client)throw Error('登录服务尚未就绪');
 return client.auth.onAuthStateChange((event,session)=>{if(event==='PASSWORD_RECOVERY')fn(session)});
}
async function logout(){if(client)await client.auth.signOut();active=null;loaded=true;emit()}
const ready=init().catch(e=>{loaded=true;emit();console.error(e);throw e});
root.XingguiSession=Object.freeze({ready,refresh,account,profile,moduleContext,requireLogin,onChange,signup,login,loginWithGoogle,sendPhoneOtp,verifyPhoneOtp,saveProfile,logout,sendPasswordReset,updatePassword,onPasswordRecovery});
})(window);
