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

def _is_loopback_host(host):
    return isinstance(host, str) and host.lower() in ('localhost','127.0.0.1','::1')

def _origin_allowed(origin, host_header=None):
    if not origin: return True
    try:
        parsed = urlparse(origin)
        if parsed.scheme not in ('http','https') or not _is_loopback_host(parsed.hostname): return False
        if parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment: return False
        if host_header:
            host_port = urlparse('http://' + host_header).port
            return parsed.port == host_port
        return True
    except (ValueError, TypeError): return False

def _host_allowed(host):
    if not isinstance(host,str) or not host or ',' in host or '@' in host: return False
    try:
        parsed = urlparse('http://' + host)
        return _is_loopback_host(parsed.hostname) and (parsed.port is None or 1 <= parsed.port <= 65535)
    except (ValueError,TypeError): return False

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
KEY = os.environ.get("SUPABASE_KEY", "")

try:
    supabase: Client = create_client(URL, KEY) if create_client and URL and KEY else None
except Exception:
    supabase = None


# ---------------------------------------------------------------------------
# 3. 主 API 请求处理器
# ---------------------------------------------------------------------------
class MainGatewayHandler(SimpleHTTPRequestHandler):
    """Serve only allowlisted web assets; source, tests and private files stay inaccessible."""
    PUBLIC_ASSETS = {'/', '/index.html', '/ziwei_view.html', '/bazi_view.html', '/fengshui_view.html'}

    def _is_public_asset(self):
        path = urlsplit(self.path).path
        return '%' not in path and path in self.PUBLIC_ASSETS


    def do_GET(self):
        if not _host_allowed(self.headers.get('Host')):
            self.send_error(403, 'Forbidden')
            return
        """处理 GET 请求：拉取历史排盘记录等"""
        if self.path == '/api/ziwei/diagnostics':
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
        elif self.path == '/api/health':
            self._send_json({'status':'ok','service':'xinggui-local','database_configured':bool(supabase),
                             'production_ready':False,'gateway_audit_version':'8.101'})
        elif self.path == '/api/records':
            try:
                records = []
                if supabase:
                    res = supabase.table("bazi_records").select(
                        "id, user_name, gender, birth_hour, created_at"
                    ).order("created_at", desc=True).limit(20).execute()
                    records = res.data if hasattr(res, 'data') else []
                
                self._send_json({"status": "success", "data": records})
            except Exception as err:
                self._send_json({"status": "error", "message": "服务暂不可用"}, 500)
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
        if self.path == '/api/calculate':
            try:
                if not BaziEngine:
                    raise Exception("bazi_engine.py 模块未引入，请检查文件是否存在！")

                req_data = self._parse_json_body()
                record = BaziEngine.calculate(req_data)

                # 将计算记录保存至 Supabase
                if supabase:
                    try:
                        supabase.table("bazi_records").insert(record).execute()
                    except Exception as db_err:
                        print("⚠️ Supabase 插入失败:", db_err, flush=True)

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
                from ziwei_analysis import build_analysis, build_sanhe_analysis
                request = self._parse_json_body()
                if request.get('school') not in (None, 'sanhe', 'flying'):
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
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# ---------------------------------------------------------------------------
# 服务器启动入口
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = _require_int(int(os.environ.get('PORT', '8000')), 'PORT', 1, 65535)
    print("--------------------------------------------------", flush=True)
    print(f"🚀 命理总调度 Server 已成功启动！监听端口: 127.0.0.1:{port}", flush=True)
    print("--------------------------------------------------", flush=True)
    server = ThreadingHTTPServer(('127.0.0.1', port), MainGatewayHandler)
    server.serve_forever()