# -*- coding: utf-8 -*-
"""
命理与风水系统总调度网关 (Main Gateway Server)
职责：接收 API 请求，调度 bazi_engine, ziwei_engine, fengshui_engine，并返回结果或存入数据库。
"""

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from http import HTTPStatus
import json
import os
import traceback
from urllib.parse import urlsplit, unquote

MAX_JSON_BYTES = 1024 * 1024
# V8.82–V8.101：本机开发网关的输入与响应边界。
import math
from urllib.parse import urlparse

def _hostname_and_port(value):
    """Parse Host/Origin authority safely (including bracketed IPv6)."""
    if not isinstance(value, str) or not value or any(c in value for c in ',@/\\\r\n '):
        return None
    try:
        parsed = urlparse('http://' + value)
        hostname, port = parsed.hostname, parsed.port
        if not hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
            return None
        return hostname.lower().rstrip('.'), port
    except (ValueError, TypeError):
        return None


def _host_allowed(host):
    parsed = _hostname_and_port(host)
    if not parsed:
        return False
    hostname, _ = parsed
    if hostname in ('localhost', '127.0.0.1', '::1'):
        return True
    # Render public service domains; do not accept arbitrary forwarded Host values.
    if hostname.endswith('.onrender.com') and hostname != 'onrender.com':
        return True
    custom = os.environ.get('PUBLIC_HOSTNAME', '').lower().strip().rstrip('.')
    return bool(custom and hostname == custom)


def _origin_allowed(origin, host_header=None):
    if not origin:
        return True
    try:
        parsed = urlparse(origin)
        if parsed.scheme not in ('http', 'https') or parsed.username or parsed.password:
            return False
        if parsed.path not in ('', '/') or parsed.query or parsed.fragment:
            return False
        origin_host = _hostname_and_port(parsed.netloc)
        target_host = _hostname_and_port(host_header)
        if not origin_host or not target_host or origin_host != target_host:
            return False
        return _host_allowed(host_header)
    except (ValueError, TypeError):
        return False

def _json_budget(value, max_depth=35, max_nodes=12000):
    stack=[(value,0)]; count=0
    while stack:
        node,depth=stack.pop(); count+=1
        if count>max_nodes or depth>max_depth: raise ValueError('JSON 对象层级或节点数量超过限制')
        if isinstance(node,dict): stack.extend((v,depth+1) for v in node.values())
        elif isinstance(node,list): stack.extend((v,depth+1) for v in node)
        elif isinstance(node,float) and not math.isfinite(node): raise ValueError('JSON 不允许非有限数值')
    return value

def _reject_json_constant(value):
    raise ValueError('JSON 不允许 NaN 或 Infinity')

def _require_int(value, label, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{label}必须为 {low}–{high} 的整数')
    return value

def _valid_decade_zhi(value):
    return value is None or (isinstance(value,str) and len(value)==1 and value in '子丑寅卯辰巳午未申酉戌亥')


def _customer_from_bazi(record):
    """Normalize a saved Bazi calculation into reusable solar birth fields."""
    import re
    stamp=str(record.get('birth_hour') or '')
    match=re.fullmatch(r'\s*(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})\s*',stamp)
    if not match:return None
    y,mo,d,h,mi=map(int,match.groups())
    from datetime import datetime
    datetime(y,mo,d,h,mi)
    name=str(record.get('user_name') or '').strip()
    gender=record.get('gender')
    if not name or gender not in ('男','女'):return None
    return dict(name=name[:100],gender=gender,calendar='solar',year=y,month=mo,day=d,hour=h,minute=mi)

def _upsert_customer(db,user_id,fields):
    """Deduplicate exact birth identity within this owner, without merging same-name people."""
    key={k:fields[k] for k in ('name','gender','calendar','year','month','day','hour','minute')}
    q=db.table('customer_profiles').select('id') .eq('user_id',user_id)
    for k,v in key.items():q=q.eq(k,v)
    existing=q.limit(1).execute().data or []
    if existing:return existing[0]['id']
    result=db.table('customer_profiles').insert({**key,'user_id':user_id}).execute()
    return result.data[0]['id'] if result.data else None

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = object

# ---------------------------------------------------------------------------
# 1. 导入三大独立模块引擎 (Module Engines)
# ---------------------------------------------------------------------------
try:
    from bazi_engine import BaziEngine
except ImportError:
    BaziEngine = None

try:
    from ziwei_engine import ZiweiEngine
except ImportError:
    ZiweiEngine = None

try:
    from fengshui_engine import FengshuiEngine
except ImportError:
    FengshuiEngine = None

# ---------------------------------------------------------------------------
# 2. Supabase 数据库连接配置
# ---------------------------------------------------------------------------
URL = os.environ.get("SUPABASE_URL", "")
KEY = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "") or os.environ.get("SUPABASE_KEY", "")

try:
    supabase: Client = create_client(URL, KEY) if create_client and URL and KEY else None
except Exception:
    supabase = None


# ---------------------------------------------------------------------------
# 3. 主 API 请求处理器
# ---------------------------------------------------------------------------
class MainGatewayHandler(SimpleHTTPRequestHandler):
    """Serve only allowlisted web assets; source, tests and private files stay inaccessible."""
    PUBLIC_ASSETS = {'/', '/index.html', '/ziwei_view.html', '/bazi_view.html', '/fengshui_view.html', '/xinggui_session.js', '/qimen_view.html', '/liuyao_view.html', '/liuyao_hexagram.js', '/liuyao_najia.js', '/liuyao_methods_app.js', '/liuyao_tabs_professional.js', '/liuyao_tabs_professional.css', '/zeri_view.html'}

    def _authenticated_user_id(self):
        """Verify the Supabase access token server-side; never trust a client user_id."""
        authorization = self.headers.get('Authorization', '')
        if not authorization.startswith('Bearer ') or not supabase:
            return None
        token = authorization[7:].strip()
        if not token or len(token) > 8192 or any(ch.isspace() for ch in token):
            return None
        try:
            response = supabase.auth.get_user(token)
            user = getattr(response, 'user', None)
            return str(user.id) if user and getattr(user, 'id', None) else None
        except Exception:
            return None

    def _authenticated_session(self):
        """Return (verified_user_id, token), or (None, None)."""
        authorization = self.headers.get('Authorization', '')
        if not authorization.startswith('Bearer ') or not supabase:
            return None, None
        token = authorization[7:].strip()
        if not token or len(token) > 8192 or any(ch.isspace() for ch in token):
            return None, None
        try:
            response = supabase.auth.get_user(token)
            user = getattr(response, 'user', None)
            if user and getattr(user, 'id', None):
                return str(user.id), token
        except Exception:
            pass
        return None, None

    def _user_db(self, access_token):
        """Create an isolated PostgREST client using this user's verified JWT.

        The publishable key alone is anonymous and must not be used to
        read/write authenticated rows under RLS.
        """
        if not supabase or not create_client or not access_token:
            return None
        client = create_client(URL, KEY)
        client.postgrest.auth(access_token)
        return client

    def _is_public_asset(self):
        path = urlsplit(self.path).path
        return '%' not in path and path in self.PUBLIC_ASSETS


    def do_GET(self):
        if not _host_allowed(self.headers.get('Host')):
            self.send_error(403, 'Forbidden')
            return
        """处理 GET 请求：拉取历史排盘记录等"""
        if urlsplit(self.path).path == '/api/public-config':
            # Only expose the public browser key; never expose SUPABASE_KEY or service_role.
            public_url = os.environ.get('SUPABASE_URL', '').strip().rstrip('/')
            public_key = os.environ.get('SUPABASE_PUBLISHABLE_KEY', '').strip()
            if not public_url.startswith('https://') or not public_key:
                self._send_json({'status': 'not_configured',
                    'message': '本地认证配置缺失：请设置 SUPABASE_URL 和 SUPABASE_PUBLISHABLE_KEY，然后重启 server.py'}, 503)
            else:
                self._send_json({'status': 'ok', 'supabase_url': public_url,
                    'supabase_publishable_key': public_key})
        elif urlsplit(self.path).path == '/api/zeri/events':
            try:
                from zeri_engine import ZeriEngine
                self._send_json({'status': 'success', 'events': ZeriEngine.events()})
            except Exception:
                traceback.print_exc()
                self._send_json({'status': 'error', 'message': '择日事项暂不可用'}, 503)
        elif urlsplit(self.path).path == '/api/liuyao/calendar':
            # Calendar conversion is optional; never silently approximate sexagenary dates.
            from urllib.parse import parse_qs
            from datetime import datetime
            import re
            q = parse_qs(urlsplit(self.path).query)
            stamp = q.get('when', [''])[0]
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', stamp):
                self._send_json({'status':'error','message':'起卦时间格式错误'},400)
                return
            try:
                dt = datetime.strptime(stamp, '%Y-%m-%dT%H:%M')
                if not 1900 <= dt.year <= 2100:
                    raise ValueError('日期超出范围')
            except ValueError:
                self._send_json({'status':'error','message':'起卦日期时间无效'},400)
                return
            try:
                from lunar_python import Solar
            except ImportError:
                self._send_json({'status':'missing_dependency','message':'请安装 lunar_python：python -m pip install lunar_python'},503)
                return
            try:
                lunar = Solar.fromYmdHms(dt.year,dt.month,dt.day,dt.hour,dt.minute,0).getLunar()
                # Exact day GanZhi and JieQi month branch, not Gregorian-month guesses.
                day = lunar.getDayInGanZhiExact()
                month = lunar.getMonthZhiExact()
                year = lunar.getYearInGanZhiExact()
                month_gz = lunar.getMonthInGanZhiExact()
                time_gz = lunar.getTimeInGanZhi()
                self._send_json({'status':'ok','day':day,'month_branch':month,'year':year,'month':month_gz,'hour':time_gz,'note':'采用本地时间；日界以历法库精确日柱规则为准，未自动校正真太阳时'})
            except Exception as err:
                print('六爻历法换算失败:',err,flush=True)
                self._send_json({'status':'error','message':'历法计算失败，请手动核对日柱与月建'},503)
        elif urlsplit(self.path).path == '/api/ziwei/diagnostics':

            import importlib.util
            lunar_ok = importlib.util.find_spec('lunar_python') is not None
            brightness_ok = importlib.util.find_spec('brightness_reference') is not None
            brightness_data_ok = os.path.isfile(os.path.join(os.path.dirname(__file__), '庙旺利陷_312项_公开资料已填168项.csv'))
            ready = ZiweiEngine is not None and lunar_ok and brightness_ok
            self._send_json({'status':'ok' if ready else 'missing_dependency',
                'engine_loaded':ZiweiEngine is not None,
                'lunar_python_installed':lunar_ok,
                'brightness_reference_installed':brightness_ok,
                'brightness_data_present':brightness_data_ok,
                'ready_for_calculation':ready,
                'message':'排盘必要模块已就绪，可重新排盘' if ready else '排盘必要模块不完整，请检查 lunar_python 与 brightness_reference.py'})
        elif urlsplit(self.path).path == '/api/health':
            self._send_json({'status':'ok','service':'xinggui-gateway','database_configured':bool(supabase),
                             'production_ready':False,'gateway_audit_version':'8.101',
                             'message':'服务在线；完整审计与上线验收尚未完成'})
        elif urlsplit(self.path).path == '/api/customers':
            user_id,token=self._authenticated_session()
            if not user_id:self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                rows=(self._user_db(token).table('customer_profiles').select('id,name,gender,calendar,year,month,day,hour,minute,created_at').eq('user_id',user_id).order('created_at',desc=True).limit(200).execute()).data or []
                self._send_json({'status':'success','data':rows})
            except Exception as err:
                print('统一客户档案读取失败:',err,flush=True)
                self._send_json({'status':'error','message':'统一客户档案读取失败，请先执行新版 SQL'},503)
        elif urlsplit(self.path).path == '/api/ziwei/records':
            user_id, token = self._authenticated_session()
            if not user_id:
                self._send_json({'status':'error','message':'请先登录'},401); return
            try:
                res=(self._user_db(token).table('ziwei_records').select('id,name,gender,year,month,day,hour,minute,calendar,created_at').eq('user_id',user_id).order('created_at',desc=True).limit(100).execute())
                self._send_json({'status':'success','data':res.data or []})
            except Exception as err:
                print('紫微档案查询失败:',err,flush=True)
                self._send_json({'status':'error','message':'紫微档案读取失败，请先执行附带 SQL'},503)
        elif urlsplit(self.path).path == '/api/records/detail':
            from urllib.parse import parse_qs
            from uuid import UUID
            user_id,token=self._authenticated_session()
            if not user_id:
                self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                params=parse_qs(urlsplit(self.path).query)
                record_id=str(UUID(params.get('id',[''])[0]))
                res=(self._user_db(token).table('bazi_records').select('*').eq('user_id',user_id).eq('id',record_id).limit(1).execute())
                if not res.data:
                    self._send_json({'status':'error','message':'记录不存在'},404);return
                self._send_json({'status':'success','data':res.data[0]})
            except (ValueError,IndexError):
                self._send_json({'status':'error','message':'无效记录编号'},400)
            except Exception as err:
                print('八字档案读取失败:',err,flush=True)
                self._send_json({'status':'error','message':'档案读取失败'},503)
        elif urlsplit(self.path).path == '/api/records':
            user_id, token = self._authenticated_session()
            if not user_id:
                self._send_json({'status':'error','message':'请先登录'}, 401)
                return
            if not supabase:
                self._send_json({'status':'error','message':'数据库暂不可用'}, 503)
                return
            try:
                # Explicit owner filter even when the configured server key bypasses RLS.
                user_db = self._user_db(token)
                res = (user_db.table('bazi_records')
                       .select('id, user_name, gender, birth_hour, created_at')
                       .eq('user_id', user_id)
                       .order('created_at', desc=True).limit(20).execute())
                self._send_json({'status':'success','data':res.data or []})
            except Exception as err:
                print('⚠️ 八字记录查询失败（请确认 user_id 字段与 RLS）:', err, flush=True)
                self._send_json({'status':'error','message':'记录查询暂不可用'}, 503)
        else:
            # 默认静态文件服务 (如 html, css, js)
            if not self._is_public_asset():
                self.send_error(404, 'Not Found')
                return
            super().do_GET()

    def do_POST(self):
        # 127.0.0.1 / localhost loopback policy is implemented by _host_allowed.
        if not _host_allowed(self.headers.get('Host')):
            self._send_json({'status':'error','message':'不允许的主机'},403)
            return
        if not _origin_allowed(self.headers.get('Origin'), self.headers.get('Host')):
            self._send_json({'status':'error','message':'不允许的请求来源'},403)
            return
        """处理 POST 请求：路由分发至对应引擎"""
        
        # ------------------------------------------------------------------
        # 路由 1：八字计算接口 -> 调度 bazi_engine
        # ------------------------------------------------------------------
        if self.path == '/api/zeri/calculate':
            try:
                from zeri_engine import ZeriEngine
                request = self._parse_json_body()
                self._send_json(ZeriEngine.calculate(request))
            except (ValueError, TypeError, OverflowError) as err:
                self._send_json({'status': 'error', 'message': str(err)}, 400)
            except RuntimeError as err:
                self._send_json({'status': 'error', 'message': str(err)}, 503)
            except Exception:
                traceback.print_exc()
                self._send_json({'status': 'error', 'message': '择日计算暂不可用'}, 500)

        elif self.path == '/api/calculate':
            try:
                if not BaziEngine:
                    raise Exception("bazi_engine.py 模块未引入，请检查文件是否存在！")

                req_data = self._parse_json_body()
                record = BaziEngine.calculate(req_data)

                # Only persist records belonging to a verified signed-in user.
                # Unauthenticated calculations remain available; no anonymous records are stored.
                user_id, token = self._authenticated_session()
                if supabase and user_id:
                    try:
                        user_db = self._user_db(token)
                        user_db.table("bazi_records").insert({**record, 'user_id': user_id}).execute()
                        # Only after the Bazi record is saved, register its reusable birth identity.
                        try:
                            fields=_customer_from_bazi(record)
                            if fields:_upsert_customer(user_db,user_id,fields)
                        except Exception as profile_err:
                            print('⚠️ 统一客户索引保存失败（八字报告已保存）:',profile_err,flush=True)
                    except Exception as db_err:
                        print("⚠️ Supabase 插入失败（请确认 user_id 字段与 RLS）:", db_err, flush=True)

                self._send_json({
                    "status": "success",
                    "data": record,
                    "strength": record.get("wang_du", "")
                })
            except (ValueError, TypeError) as err:
                self._send_json({"status":"error","message":str(err)}, 400)
            except Exception as err:
                print("💥 八字引擎计算异常:", err, flush=True)
                traceback.print_exc()
                self._send_json({"status": "error", "message": "服务暂不可用"}, 500)

        # ------------------------------------------------------------------
        # 路由 2：紫微斗数计算接口 -> 调度 ziwei_engine
        # ------------------------------------------------------------------
        elif self.path == '/api/ziwei/analyze':
            try:
                from ziwei_analysis import build_analysis, build_sanhe_analysis, build_school_readings, build_transfer_ji_paths
                request = self._parse_json_body()
                if request.get('school') not in (None, 'sanhe', 'flying', 'feixing'):
                    raise ValueError('不支持的分析流派')
                if not isinstance(request.get('chart'), dict):
                    raise ValueError('chart 必须是完整命盘对象')
                if len(json.dumps(request['chart'],ensure_ascii=False)) > 750000:
                    raise ValueError('命盘对象超过分析限制')
                if request.get('decade_zhi') is not None and not _valid_decade_zhi(request['decade_zhi']):
                    raise ValueError('大限地支无效')
                if request.get('year') is not None:
                    if type(request['year']) is not int or not 1900 <= request['year'] <= 2200:
                        raise ValueError('流年年份必须是 1900–2200 的整数')
                result = (build_sanhe_analysis(request.get('chart') or {})
                          if request.get('school') == 'sanhe'
                          else build_analysis(request.get('chart') or {},
                                              request.get('decade_zhi'), request.get('year')))
                if request.get('school') != 'sanhe':
                    result.setdefault('transfer_ji_paths', build_transfer_ji_paths(request['chart']))
                result['school_readings'] = build_school_readings(request['chart'], 'sanhe' if request.get('school') == 'sanhe' else 'flying', result)
                result['client_readings'] = result['school_readings']
                from ziwei_delivery_audit import audit_chart
                result['delivery_audit'] = audit_chart(request['chart'])
                from ziwei_quality_audit import audit_quality
                result['quality_audit'] = audit_quality(request['chart'])
                from ziwei_acceptance_audit import audit_acceptance
                result['acceptance_audit'] = audit_acceptance(request['chart'], result)
                from ziwei_adversarial import inspect_chart
                result['adversarial_audit'] = inspect_chart(request['chart'])
                self._send_json({'status':'success','analysis':result})
            except (ValueError, TypeError) as err:
                self._send_json({'status':'error','message':str(err)}, 400)
            except Exception as err:
                traceback.print_exc()
                self._send_json({'status':'error','message':'分析引擎暂不可用'}, 500)

        elif self.path == '/api/customers/save':
            user_id,token=self._authenticated_session()
            if not user_id:self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                p=self._parse_json_body()
                if not isinstance(p.get('name'),str) or not p['name'].strip() or len(p['name'].strip())>100:raise ValueError('客户姓名必须为1至100字')
                if p.get('gender') not in ('男','女') or p.get('calendar') not in ('solar','lunar'):raise ValueError('性别或历法无效')
                for k,lo,hi in [('year',1900,2200),('month',1,12),('day',1,31),('hour',0,23),('minute',0,59)]:_require_int(p.get(k),k,lo,hi)
                if p['calendar']=='solar':
                    from datetime import datetime
                    datetime(p['year'],p['month'],p['day'],p['hour'],p['minute'])
                fields={k:(p[k].strip() if k=='name' else p[k]) for k in ('name','gender','calendar','year','month','day','hour','minute')}
                cid=_upsert_customer(self._user_db(token),user_id,fields)
                self._send_json({'status':'success','id':cid})
            except (ValueError,TypeError) as err:self._send_json({'status':'error','message':str(err)},400)
            except Exception as err:
                print('统一客户保存失败:',err,flush=True)
                self._send_json({'status':'error','message':'保存失败，请确认统一客户表和 RLS'},503)
        elif self.path == '/api/customers/manage':
            from uuid import UUID
            user_id,token=self._authenticated_session()
            if not user_id:self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                p=self._parse_json_body();cid=str(UUID(p.get('id','')));action=p.get('action')
                if action not in ('rename','delete','update'):raise ValueError('不支持的操作')
                db=self._user_db(token);q=db.table('customer_profiles')
                if action=='rename':
                    name=p.get('name')
                    if not isinstance(name,str) or not 1<=len(name.strip())<=100:raise ValueError('客户姓名必须为1至100字')
                    result=q.update({'name':name.strip()}).eq('user_id',user_id).eq('id',cid).execute()
                elif action=='update':
                    if not isinstance(p.get('name'),str) or not 1<=len(p['name'].strip())<=100:raise ValueError('客户姓名必须为1至100字')
                    if p.get('gender') not in ('男','女') or p.get('calendar') not in ('solar','lunar'):raise ValueError('性别或历法无效')
                    for k,lo,hi in [('year',1900,2200),('month',1,12),('day',1,31),('hour',0,23),('minute',0,59)]:_require_int(p.get(k),k,lo,hi)
                    if p['calendar']=='solar':
                        from datetime import datetime
                        datetime(p['year'],p['month'],p['day'],p['hour'],p['minute'])
                    fields={k:(p[k].strip() if k=='name' else p[k]) for k in ('name','gender','calendar','year','month','day','hour','minute')}
                    result=q.update(fields).eq('user_id',user_id).eq('id',cid).execute()
                else:result=q.delete().eq('user_id',user_id).eq('id',cid).execute()
                if not result.data:self._send_json({'status':'error','message':'记录不存在或无权操作'},404);return
                self._send_json({'status':'success'})
            except (ValueError,TypeError) as err:self._send_json({'status':'error','message':str(err)},400)
            except Exception as err:
                print('统一客户档案操作失败:',err,flush=True)
                self._send_json({'status':'error','message':'档案操作失败'},503)
        elif self.path == '/api/ziwei/records/save':
            user_id,token=self._authenticated_session()
            if not user_id:
                self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                p=self._parse_json_body()
                if not isinstance(p.get('name'),str) or not p['name'].strip() or len(p['name'])>100: raise ValueError('姓名无效')
                if p.get('gender') not in ('男','女') or p.get('calendar') not in ('solar','lunar'): raise ValueError('性别或历法无效')
                for k,lo,hi in [('year',1900,2200),('month',1,12),('day',1,31),('hour',0,23),('minute',0,59)]: _require_int(p.get(k),k,lo,hi)
                fields={k:p[k] for k in ('name','gender','calendar','year','month','day','hour','minute')}
                fields['user_id']=user_id
                db=self._user_db(token)
                _upsert_customer(db,user_id,{k:fields[k] for k in ('name','gender','calendar','year','month','day','hour','minute')})
                res=db.table('ziwei_records').insert(fields).execute()
                self._send_json({'status':'success','data':res.data or []})
            except (ValueError,TypeError) as err: self._send_json({'status':'error','message':str(err)},400)
            except Exception as err:
                print('紫微档案保存失败:',err,flush=True)
                self._send_json({'status':'error','message':'保存失败，请检查紫微档案表与 RLS'},503)
        elif self.path == '/api/records/manage':
            from uuid import UUID
            user_id,token=self._authenticated_session()
            if not user_id:
                self._send_json({'status':'error','message':'请先登录'},401);return
            try:
                p=self._parse_json_body()
                kind=p.get('kind');action=p.get('action')
                if kind not in ('bazi','ziwei') or action not in ('delete','rename'): raise ValueError('不支持的档案操作')
                record_id=str(UUID(p.get('id','')))
                table='bazi_records' if kind=='bazi' else 'ziwei_records'
                q=self._user_db(token).table(table)
                if action=='delete':
                    result=q.delete().eq('user_id',user_id).eq('id',record_id).execute()
                else:
                    name=p.get('name')
                    if not isinstance(name,str) or not name.strip() or len(name)>100: raise ValueError('姓名必须为1至100字')
                    result=q.update({'user_name' if kind=='bazi' else 'name':name.strip()}).eq('user_id',user_id).eq('id',record_id).execute()
                if not result.data:
                    self._send_json({'status':'error','message':'记录不存在或无权操作'},404);return
                self._send_json({'status':'success'})
            except (ValueError,TypeError) as err:self._send_json({'status':'error','message':str(err)},400)
            except Exception as err:
                print('档案操作失败:',err,flush=True)
                self._send_json({'status':'error','message':'档案操作失败'},503)
        elif self.path == '/api/ziwei/calculate':
            try:
                req_data = self._parse_json_body()

                # 如果存在独立 Zip Engine 类，则直接实例化计算
                if ZiweiEngine:
                    name = req_data.get('name', '小叶')
                    if not isinstance(name, str) or len(name) > 100 or not name.strip():
                        raise ValueError('姓名必须是非空字符串，最多100字')
                    if req_data.get('gender', '男') not in ('男','女'):
                        raise ValueError('性别仅支持男或女')
                    if req_data.get('calendar', 'solar') not in ('solar','lunar'):
                        raise ValueError('历法仅支持 solar 或 lunar')
                    gender = req_data.get('gender', '男')
                    year = _require_int(req_data.get('year', 1988), 'year', 1900, 2200)
                    month = _require_int(req_data.get('month', 11), 'month', 1, 12)
                    day = _require_int(req_data.get('day', 12), 'day', 1, 31)
                    hour = _require_int(req_data.get('hour', 1345), 'hour', 0, 2359)
                    if not 1900 <= year <= 2200 or not 1 <= month <= 12 or not 1 <= day <= 31:
                        raise ValueError('出生年月日超出支持范围')
                    if req_data.get('calendar', 'solar') == 'solar':
                        from datetime import date
                        date(year,month,day)

                    minute = req_data.get('minute',0)
                    if type(minute) is not int or not 0 <= minute <= 59:
                        raise ValueError('分钟必须为0至59的整数')
                    if hour >= 24 and (hour % 100 > 59 or hour // 100 > 23):
                        raise ValueError('时间编码无效')
                    engine = ZiweiEngine(name, gender, year, month, day, hour, minute, req_data.get("calendar", "solar"))
                    result = engine.calculate_full_chart()
                else:
                    # 回退降级方案
                    result = {
                        "status": "error",
                        "message": "ziwei_engine 未能加载"
                    }

                self._send_json(result)
            except (ValueError, TypeError) as err:
                self._send_json({'status':'error','message':str(err)}, 400)
            except RuntimeError as err:
                if 'lunar_python' in str(err):
                    self._send_json({'status':'error','code':'MISSING_LUNAR_PYTHON','message':'缺少 lunar_python 历法库，无法计算真实命盘。请在系统目录执行 python -m pip install -r requirements.txt，然后重启服务器。'}, 503)
                else:
                    traceback.print_exc()
                    self._send_json({'status':'error','message':'紫微引擎运行错误：'+str(err)},500)
            except Exception as err:
                print("💥 紫微引擎计算异常:", err, flush=True)
                traceback.print_exc()
                self._send_json({"status": "error", "message": "服务暂不可用"}, 500)

        # ------------------------------------------------------------------
        # 路由 3：风水宅命计算接口 -> 调度 fengshui_engine
        # ------------------------------------------------------------------
        elif self.path == '/api/fengshui/calculate':
            try:
                if not FengshuiEngine:
                    raise Exception("fengshui_engine.py 模块未引入，请检查文件是否存在！")

                req_data = self._parse_json_body()
                result = FengshuiEngine.calculate(req_data)

                self._send_json(result)
            except (ValueError, TypeError) as err:
                self._send_json({"status":"error","message":str(err)}, 400)
            except Exception as err:
                print("💥 风水引擎计算异常:", err, flush=True)
                traceback.print_exc()
                self._send_json({"status": "error", "message": "服务暂不可用"}, 500)

        else:
            self._send_json({"status": "error", "message": "未知的 API 路径"}, 404)

    # ---------------------------------------------------------------------------
    # 辅助工具函数
    # ---------------------------------------------------------------------------
    def _parse_json_body(self):
        """解析 POST 请求体中的 JSON 数据"""
        if self.headers.get('Transfer-Encoding') is not None:
            raise ValueError('不支持 Transfer-Encoding 请求体')
        if len(self.headers.get_all('Content-Length', []) if hasattr(self.headers,'get_all') else ([self.headers['Content-Length']] if 'Content-Length' in self.headers else [])) != 1:
            raise ValueError('请求必须有且仅有一个 Content-Length')
        if (self.headers.get_content_type() if hasattr(self.headers,'get_content_type') else self.headers.get('Content-Type','application/json').split(';')[0].strip()) != 'application/json':
            raise ValueError('请求 Content-Type 必须是 application/json')
        try:
            content_length = int(self.headers.get('Content-Length', '0'))
        except (ValueError, TypeError):
            raise ValueError('无效请求长度')
        if not 0 < content_length <= MAX_JSON_BYTES:
            raise ValueError('请求内容大小超出允许范围或为空')
        try:
            data = json.loads(self.rfile.read(content_length).decode('utf-8'), parse_constant=_reject_json_constant)
        except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise ValueError('请求必须是有效 UTF-8 JSON') from exc
        _json_budget(data, max_depth=35, max_nodes=12000)
        if not isinstance(data, dict):
            raise ValueError('请求顶层必须是 JSON 对象')
        return data

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Cache-Control','no-store')
        super().end_headers()

    def _send_json(self, data, status_code=200):
        """统一发送 JSON 格式响应"""
        response_json = json.dumps(data, ensure_ascii=False)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(response_json.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))

    def do_PUT(self):
        self.send_error(405, 'Method Not Allowed')

    do_PATCH = do_PUT
    do_DELETE = do_PUT
    do_TRACE = do_PUT

    def do_OPTIONS(self):
        if not _host_allowed(self.headers.get('Host')):
            self.send_error(403, 'Forbidden')
            return
        """处理 CORS 预检请求"""
        if not _origin_allowed(self.headers.get('Origin'), self.headers.get('Host')):
            self.send_error(403, 'Forbidden')
            return
        self.send_response(200)
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()


# ---------------------------------------------------------------------------
# 服务器启动入口
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = _require_int(int(os.environ.get('PORT', '8000')), 'PORT', 1, 65535)
    print("--------------------------------------------------", flush=True)
    print(f"🚀 命理总调度 Server 正在监听 0.0.0.0:{port}", flush=True)
    print("--------------------------------------------------", flush=True)
    server = ThreadingHTTPServer(('0.0.0.0', port), MainGatewayHandler)
    server.serve_forever()