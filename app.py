import os,json,time,hmac,hashlib,secrets
from datetime import datetime,timezone
from functools import wraps
from urllib.parse import parse_qsl
import requests
from flask import Flask,request,jsonify,render_template_string,abort,make_response,redirect
import firebase_admin
from firebase_admin import credentials,firestore

APP_NAME = os.getenv("APP_NAME", "FoxiGrow")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8994000654:AAHtjDOWuh7oqrdICKrouuP-C1MEvGAWLgM")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7034779471"))
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "wh_sec_8f2d9a4b1c7e6f0a3b5d8e2c9a1f4e7b")
SETUP_SECRET = os.getenv("SETUP_SECRET", "set_sec_3e7a1c9f4b8d2e5a0c6f1b4d8e2a9c7f")
SESSION_TTL = int(os.getenv("SESSION_TTL", "86400"))
FIREBASE_SERVICE_ACCOUNT = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    r'{"type": "service_account", "project_id": "airavattest-e7835", "private_key_id": "1bce7f8eb7ea20c869362e4fd218f0a49f038eec", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCwGfgn/ZR+/ySs\ndV8DRpx5+i4pEbhmI/2UBqfMRAuS0lzBJmyd6oscOre+kDHio8D/xLR3OUiKQc+6\nl6YfDd/QyZewndSJeKypAPQR9q3A5xlqrL5dPJbBR4B/qS+f6Vy1/Ofy34D47eXY\nQ3csQXicbz0tNrt4DrBT5kYcGgambY78daGHRReuh5v7sjEa/VhxgtDSOeZ1KyXS\ndEpeG5X+xVVxCVTuALwGDq1r/vwQ2DBTns+nL1ZvMPNd3X9CEO0QT4v4Rvq2mWXb\n0vDY88U6QFHURaQIw2Vg9jzvUmnu4xQrlSoQECBZ38ri9T7yMttAFG+x64gsXeGH\nUTsUMCepAgMBAAECggEAEHi9X3A2nZJb6c2or3PBWx9theXka5leNKRSuaZ7tqX6\niw5/Bl5T2LYdTbPLFrneaY4Km0Q+ZsA1H+zjWvA/SRYyHBEHOjyRWdV+/tcl9W8o\nT3QM8keiij2X5Vj73WdEhrk7MNp7A82svAfDc95D284D2ODPtDEbiR123VYJ3TMm\nZ7vfw9270vrFBVcp42sQZm28Z8kthNQLeao4CfhsLT6pmbgsY5pCI23dcyj1ILNV\nv02W3//ByF2GlBPNzX3XCJUPb62c4QVSQlj00mzT2pllPGpUBfL7UJUVT0cjtdY2\nzy/JVEMnw6QbAqvS35Kwcs39lFMlvw1hhG5hAaJKaQKBgQDi9FumQ36sjVOz4ec6\nqh1LtqHKYM/yLhIJ/A4WHAl/d2yZoIYfk+hhuRA/Mhy1nevl2QuOQsKFEuCVOMYl\nQ/eYxskT9ghAMBxfQEjpLpGmcKRr7mKYHuJ4vADWSjRc15JJAqsuCJLpq6mx1tem\nVNc8RNv3lYwIHvu2MtCt508NJwKBgQDGo4cANBfzU7Wzz3L1/76Qd83Hpzh0JvWu\nmcYaBhTWkD+kKU7AQtk4PHS/M4TiPBy3SJJ/DMhJC33uqEp5F8FwwEq/pCdRl9pa\nD8DbLFxYcVsXL1KIRMs9Leu3exYTOyaA7qxSjsb2wGzHVClkWqQI/nWtDTmT1sui\nxtmx13bGrwKBgDoxNZ64B67uvduNvOBJ5iEXvvxJPoh2T6HHw0TgA39ve6UYh8to\n/VixPv01OC9JQsc4k8HyVDYS1Qrt98BuYPoHXl+D4jGzJFM4BHnluurWTxJtmVIv\n+RnD+uL3O93iWFvoF0RCZokLvwMed0Tq1BVcAprE+ZbLevcIqIEuohJZAoGAF2F0\nKH/5ObjmsE2AuJfrtFGFtTRnnrRfQrfy62k/1qmP9CCwlkzICKiFDWRhBcgRkTlH\nlRDKGl7x6b+BVJOJP15C7h/CSQZYuzUTfDjSfc6J7Eazrjp6ua7ICgbA6G6T76Uo\nP2dy3+RyaVvsq1VH7Y8WBtKBrncf7P7+7MHxxx0CgYAdT8f3ZkSgtKT6GLDDtRHA\nPkjWilmIIrJI4wluCrbarelCzWX+U5Stg/gn3/c/iOc1KFYlTz0+Z3ZUWNRKouEg\nw2hBmtvRnsZ1dFlEVwCtbXAxb5g58nj6/vGhKNVo7aYwsac8ohwYCVPGSDlFhfpY\nHHPrbWaMZO56nT9DEyofdQ==\n-----END PRIVATE KEY-----\n", "client_email": "firebase-adminsdk-gvvvt@airavattest-e7835.iam.gserviceaccount.com", "client_id": "102840458996653965127", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-gvvvt%40airavattest-e7835.iam.gserviceaccount.com", "universe_domain": "googleapis.com"}'
)
FIREBASE_CONFIGS_JSON = os.getenv(
    "FIREBASE_CONFIGS_JSON",
    '{"project_info":{"project_number":"340714210","firebase_url":"https://airavattest-e7835-default-rtdb.firebaseio.com","project_id":"airavattest-e7835","storage_bucket":"airavattest-e7835.firebasestorage.app"},"client":[{"client_info":{"mobilesdk_app_id":"1:340714210:android:976fd145ac91d1a82eb4bb","android_client_info":{"package_name":"Em.emon"}},"oauth_client":[{"client_id":"340714210-vrv3qvscdggj181erti873agb72liefv.apps.googleusercontent.com","client_type":3}],"api_key":[{"current_key":"AIzaSyAqhztOicfRfF5mXRqkFm5jHsOmX0SJ5fI"}],"services":{"appinvite_service":{"other_platform_oauth_client":[{"client_id":"340714210-vrv3qvscdggj181erti873agb72liefv.apps.googleusercontent.com","client_type":3}]}}},{"client_info":{"mobilesdk_app_id":"1:340714210:android:b0350c8e231fe1fe2eb4bb","android_client_info":{"package_name":"Emon.em"}},"oauth_client":[{"client_id":"340714210-vrv3qvscdggj181erti873agb72liefv.apps.googleusercontent.com","client_type":3}],"api_key":[{"current_key":"AIzaSyAqhztOicfRfF5mXRqkFm5jHsOmX0SJ5fI"}],"services":{"appinvite_service":{"other_platform_oauth_client":[{"client_id":"340714210-vrv3qvscdggj181erti873agb72liefv.apps.googleusercontent.com","client_type":3}]}}}],"configuration_version":"1"}'
)



app=Flask(__name__)
DB={}
SESSIONS={}
MAX_UPLOAD_BYTES=5*1024*1024

SETTINGS_DEFAULT={
"app_name":APP_NAME,"maintenance":False,"tasks_enabled":True,
"withdrawals_enabled":True,"ads_enabled":True,"spin_enabled":True,
"streak_enabled":True,"referrals_enabled":True,"leaderboard_enabled":True,
"min_withdrawal":1.0,"max_withdrawal":1000.0,"daily_ad_limit":10,
"daily_ad_reward":0.01,"daily_checkin_reward":0.01,"referral_reward":0.05,
"withdrawal_methods":["binance","bkash","nagad","rocket"],
"spin_slots":[
{"label":"0.10 USDT","reward":0.10},{"label":"0.25 USDT","reward":0.25},
{"label":"0.50 USDT","reward":0.50},{"label":"1.00 USDT","reward":1.00},
{"label":"Try Again","reward":0.00},{"label":"2.00 USDT","reward":2.00}],
"referral_milestones":[{"valid":3,"bonus":1.0},{"valid":10,"bonus":5.0},{"valid":25,"bonus":15.0}]
}

LEVELS=[
{"level":1,"xp":0,"badge":"Rookie"},{"level":2,"xp":100,"badge":"Bronze"},
{"level":3,"xp":300,"badge":"Silver"},{"level":4,"xp":700,"badge":"Gold"},
{"level":5,"xp":1500,"badge":"VIP"},{"level":6,"xp":3000,"badge":"Legend"}]

def now():
    return datetime.now(timezone.utc).isoformat()

def ts():
    return int(time.time())

def s(v,n=5000):
    return str(v or "").strip()[:n]

def i(v):
    try:return int(v)
    except:return 0

def f(v):
    try:return round(float(v),8)
    except:return 0.0

def j(v,d=None):
    try:return json.loads(v)
    except:return d

def init_firebase():
    configs={}
    if FIREBASE_CONFIGS_JSON:
        parsed=j(FIREBASE_CONFIGS_JSON,{})
        if isinstance(parsed,dict):configs.update(parsed)
    if FIREBASE_SERVICE_ACCOUNT and "default" not in configs:
        raw=FIREBASE_SERVICE_ACCOUNT
        try:raw=__import__("base64").b64decode(raw).decode()
        except:pass
        parsed=j(raw,{})
        if isinstance(parsed,dict):configs["default"]=parsed
    for alias,cfg in configs.items():
        if not isinstance(cfg,dict) or not cfg:continue
        try:
            name=f"{APP_NAME}-{alias}"
            try:firebase_admin.get_app(name)
            except ValueError:firebase_admin.initialize_app(credentials.Certificate(cfg),name=name)
            DB[alias]=firestore.client(firebase_admin.get_app(name))
        except:pass

init_firebase()

def db(alias="default"):
    if alias not in DB:raise RuntimeError("Firebase is not configured")
    return DB[alias]

def ref(c,d,alias="default"):
    return db(alias).collection(c).document(str(d))

def get(c,d,alias="default"):
    x=ref(c,d,alias).get()
    return x.to_dict() if x.exists else None

def put(c,d,data,alias="default",merge=True):
    ref(c,d,alias).set(data,merge=merge)
    return data

def update(c,d,data,alias="default"):
    ref(c,d,alias).update(data)
    return data

def delete(c,d,alias="default"):
    ref(c,d,alias).delete()

def all_docs(c,alias="default",limit=5000):
    out=[]
    for x in db(alias).collection(c).limit(limit).stream():
        z=x.to_dict();z["id"]=x.id;out.append(z)
    return out

def settings(alias="default"):
    x=get("settings","global",alias)
    if not x:
        put("settings","global",SETTINGS_DEFAULT,alias,False)
        return dict(SETTINGS_DEFAULT)
    z=dict(SETTINGS_DEFAULT);z.update(x);return z

def set_settings(data,alias="default"):
    z={}
    for k,v in data.items():
        if k not in SETTINGS_DEFAULT:continue
        if k in {"maintenance","tasks_enabled","withdrawals_enabled","ads_enabled","spin_enabled","streak_enabled","referrals_enabled","leaderboard_enabled"}:z[k]=bool(v)
        elif k in {"min_withdrawal","max_withdrawal","daily_ad_reward","daily_checkin_reward","referral_reward"}:z[k]=f(v)
        elif k=="daily_ad_limit":z[k]=max(0,i(v))
        else:z[k]=v
    z["updated_at"]=now();put("settings","global",z,alias);return settings(alias)

def user(uid,alias="default"):
    return get("users",str(uid),alias)

def save_user(tg,alias="default"):
    uid=str(tg["id"]);old=user(uid,alias)
    data={
        "telegram_id":uid,"first_name":s(tg.get("first_name"),100),
        "last_name":s(tg.get("last_name"),100),"username":s(tg.get("username"),100).lstrip("@"),
        "updated_at":now()
    }
    if not old:
        data.update({"balance":0.0,"fg_coin":0.0,"xp":0,"level":1,"badge":"Rookie",
        "completed_tasks":0,"valid_referrals":0,"referrer_id":"","first_withdrawal_validated":False,
        "blocked":False,"suspended":False,"fraud_score":0,"daily_ads":0,
        "daily_ads_date":datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_spin":0,"last_checkin":"","streak":0,"created_at":now()})
    merged=dict(old or {});merged.update(data);put("users",uid,merged,alias,False);return merged

def refresh_level(uid,alias="default"):
    u=user(uid,alias)
    if not u:return None
    x=LEVELS[0]
    for q in LEVELS:
        if i(u.get("xp"))>=i(q["xp"]):x=q
    update("users",uid,{"level":x["level"],"badge":x["badge"],"updated_at":now()},alias)
    u.update(x);return u

def verify_init(raw):
    if not raw or not BOT_TOKEN:return None
    try:
        p=dict(parse_qsl(raw,keep_blank_values=True));received=p.pop("hash","")
        ad=i(p.get("auth_date"))
        if not received or not ad or ts()-ad>SESSION_TTL:return None
        check="\n".join(f"{k}={p[k]}" for k in sorted(p))
        secret=hmac.new(b"WebAppData",BOT_TOKEN.encode(),hashlib.sha256).digest()
        calc=hmac.new(secret,check.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(received,calc):return None
        u=j(p.get("user"),{})
        return u if isinstance(u,dict) and u.get("id") else None
    except:return None

def init_data():
    return request.headers.get("X-Telegram-Init-Data","") or request.args.get("initData","") or request.form.get("initData","")

def make_session(uid,admin,lang):
    x=secrets.token_urlsafe(32)
    SESSIONS[x]={"uid":str(uid),"admin":bool(admin),"lang":lang,"exp":ts()+SESSION_TTL}
    return x

def sess():
    k=request.cookies.get("fg_session")
    x=SESSIONS.get(k or "")
    if not x:return None
    if x["exp"]<ts():SESSIONS.pop(k,None);return None
    return x

def need_user(fn):
    @wraps(fn)
    def w(*a,**kw):
        x=sess()
        if not x:return jsonify({"ok":False,"error":"telegram_session_required"}),403
        u=user(x["uid"])
        if not u:return jsonify({"ok":False,"error":"user_not_found"}),404
        if u.get("blocked") or u.get("suspended"):return jsonify({"ok":False,"error":"account_restricted"}),403
        return fn(*a,**kw)
    return w

def need_admin(fn):
    @wraps(fn)
    def w(*a,**kw):
        x=sess()
        if not x or not x.get("admin") or str(x.get("uid"))!=str(ADMIN_ID):return jsonify({"ok":False,"error":"admin_only"}),403
        return fn(*a,**kw)
    return w

def tg(method,payload=None):
    if not BOT_TOKEN:raise RuntimeError("BOT_TOKEN is missing")
    r=requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",json=payload or {},timeout=15)
    data=r.json()
    if not data.get("ok"):raise RuntimeError(data.get("description","Telegram error"))
    return data

def set_webhook():
    p={"url":f"{PUBLIC_URL}/telegram/webhook"}
    if WEBHOOK_SECRET:p["secret_token"]=WEBHOOK_SECRET
    return tg("setWebhook",p)

def send_language(chat):
    tg("sendMessage",{"chat_id":chat,"text":"<b>FoxiGrow</b>\n\nভাষা নির্বাচন করুন / Choose your language","parse_mode":"HTML",
      "reply_markup":{"inline_keyboard":[
        [{"text":"🇧🇩 বাংলা","web_app":{"url":f"{PUBLIC_URL}/app?lang=bn"}}],
        [{"text":"🇬🇧 English","web_app":{"url":f"{PUBLIC_URL}/app?lang=en"}}]
      ]}})

def webhook_update(data):
    m=data.get("message") or {};tg_user=m.get("from") or {};chat=m.get("chat") or {};text=s(m.get("text"))
    if tg_user.get("id"):u=save_user(tg_user)
    else:u=None
    if chat.get("id") and text.startswith("/start"):
        parts=text.split(maxsplit=1)
        if u and len(parts)==2 and parts[1].startswith("ref_") and not u.get("referrer_id"):
            r=parts[1][4:]
            if r.isdigit() and r!=str(u["telegram_id"]):update("users",u["telegram_id"],{"referrer_id":r,"updated_at":now()})
        send_language(chat["id"])
    elif chat.get("id") and text=="/admin":
        if str(tg_user.get("id"))==str(ADMIN_ID):tg("sendMessage",{"chat_id":chat["id"],"text":f"{PUBLIC_URL}/admin"})
        else:tg("sendMessage",{"chat_id":chat["id"],"text":"Access denied."})

def change_balance(uid,amount=0,coins=0,alias="default"):
    database=db(alias);document=database.collection("users").document(str(uid))
    tx=database.transaction()
    @firestore.transactional
    def action(t):
        snap=document.get(transaction=t)
        if not snap.exists:raise ValueError("user_not_found")
        x=snap.to_dict();nb=f(x.get("balance"))+f(amount);nc=f(x.get("fg_coin"))+f(coins)
        if nb<0 or nc<0:raise ValueError("insufficient_balance")
        t.update(document,{"balance":nb,"fg_coin":nc,"updated_at":now()});return nb,nc
    return action(tx)

def task_available(task,uid):
    if not task.get("active",True):return False
    max_limit=i(task.get("max_limit"))
    if max_limit and i(task.get("completed_count"))>=max_limit:return False
    p=i(task.get("publish_at"));e=i(task.get("expires_at"))
    if p and ts()<p:return False
    if e and ts()>=e:return False
    c=get("claims",f"{uid}_{task['id']}")
    return not (c and c.get("status")=="completed")

def available_tasks(uid):
    st=settings()
    if not st.get("tasks_enabled"):return []
    rows=[x for x in all_docs("tasks") if task_available(x,uid)]
    rows.sort(key=lambda x:i(x.get("priority")),reverse=True)
    return rows

def start_task(uid,tid):
    x=get("tasks",tid)
    if not x:raise ValueError("task_not_found")
    x["id"]=tid
    if not task_available(x,uid):raise ValueError("task_unavailable")
    put("claims",f"{uid}_{tid}",{"telegram_id":str(uid),"task_id":tid,"status":"started","started_at":now()},merge=True)
    return x

def complete_task(uid,tid):
    x=get("tasks",tid)
    if not x:raise ValueError("task_not_found")
    c=get("claims",f"{uid}_{tid}")
    if c and c.get("status")=="completed":raise ValueError("already_completed")
    change_balance(uid,f(x.get("reward")),f(x.get("coin_reward")))
    u=user(uid)
    update("users",uid,{"completed_tasks":i(u.get("completed_tasks"))+1,"xp":i(u.get("xp"))+i(x.get("xp") or 10),"updated_at":now()})
    refresh_level(uid)
    count=i(x.get("completed_count"))+1
    changes={"completed_count":count,"updated_at":now()}
    if i(x.get("max_limit")) and count>=i(x.get("max_limit")):changes["active"]=False
    update("tasks",tid,changes)
    put("claims",f"{uid}_{tid}",{"status":"completed","completed_at":now()},merge=True)

def checkin(uid):
    st=settings();u=user(uid);today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not st.get("streak_enabled"):raise ValueError("streak_disabled")
    if u.get("last_checkin")==today:raise ValueError("already_checked")
    reward=f(st.get("daily_checkin_reward"));change_balance(uid,reward,0)
    update("users",uid,{"last_checkin":today,"streak":i(u.get("streak"))+1,"updated_at":now()})
    return reward

def ad_complete(uid):
    st=settings();u=user(uid);today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not st.get("ads_enabled"):raise ValueError("ads_disabled")
    used=i(u.get("daily_ads"));stored=u.get("daily_ads_date")
    if stored!=today:used=0
    limit=i(st.get("daily_ad_limit"))
    if used>=limit:raise ValueError("daily_ad_limit")
    reward=f(st.get("daily_ad_reward"));change_balance(uid,reward,0)
    update("users",uid,{"daily_ads":used+1,"daily_ads_date":today,"updated_at":now()})
    return reward,max(0,limit-used-1)

def spin(uid):
    st=settings();u=user(uid)
    if not st.get("spin_enabled"):raise ValueError("spin_disabled")
    if i(u.get("last_spin")) and ts()-i(u.get("last_spin"))<86400:raise ValueError("spin_cooldown")
    slots=st.get("spin_slots") or SETTINGS_DEFAULT["spin_slots"];index=secrets.randbelow(len(slots));slot=slots[index];reward=f(slot.get("reward"))
    update("users",uid,{"last_spin":ts(),"updated_at":now()})
    if reward:change_balance(uid,reward,0)
    return index,slot.get("label"),reward

def create_withdrawal(uid,amount,method,account):
    st=settings()
    if not st.get("withdrawals_enabled"):raise ValueError("withdrawals_disabled")
    amount=f(amount);method=s(method,40).lower();account=s(account,300)
    if amount<f(st.get("min_withdrawal")):raise ValueError("below_minimum")
    if amount>f(st.get("max_withdrawal")):raise ValueError("above_maximum")
    if method not in st.get("withdrawal_methods",[]):raise ValueError("method_disabled")
    if not account:raise ValueError("account_required")
    change_balance(uid,-amount,0)
    wid=secrets.token_hex(12)
    item={"id":wid,"telegram_id":str(uid),"amount":amount,"method":method,"account":account,"status":"pending","manager_id":"","fraud_score":i(user(uid).get("fraud_score")),"created_at":now(),"updated_at":now()}
    put("withdrawals",wid,item,merge=False);auto_manager(wid);return item

def list_withdrawals(status=None):
    rows=all_docs("withdrawals")
    if status:rows=[x for x in rows if x.get("status")==status]
    rows.sort(key=lambda x:x.get("created_at",""),reverse=True);return rows

def auto_manager(wid):
    item=get("withdrawals",wid)
    if not item:return
    managers=all_docs("managers");pending=list_withdrawals("pending");best=None;score=10**9
    for m in managers:
        if not m.get("enabled",True):continue
        limit=max(1,i(m.get("max_open") or 10))
        count=sum(1 for x in pending if x.get("manager_id")==m["id"])
        if count<limit and count<score:best=m;score=count
    if best:update("withdrawals",wid,{"manager_id":best["id"],"updated_at":now()})

def process_withdrawal(wid,status,note=""):
    item=get("withdrawals",wid)
    if not item:raise ValueError("withdrawal_not_found")
    old=item.get("status");status=s(status,30).lower()
    if status not in {"pending","processing","approved","rejected","paid","cancelled"}:raise ValueError("invalid_status")
    if old in {"approved","paid","rejected","cancelled"} and old!=status:raise ValueError("final_status")
    if status in {"rejected","cancelled"} and old=="pending":change_balance(item["telegram_id"],item["amount"],0)
    update("withdrawals",wid,{"status":status,"note":s(note,2000),"updated_at":now()})
    if status=="approved":validate_first_withdraw(item["telegram_id"])

def validate_first_withdraw(uid):
    u=user(uid)
    if not u or u.get("first_withdrawal_validated"):return
    update("users",uid,{"first_withdrawal_validated":True,"updated_at":now()})
    parent=str(u.get("referrer_id") or "")
    if not parent:return
    p=user(parent)
    if not p:return
    count=i(p.get("valid_referrals"))+1
    update("users",parent,{"valid_referrals":count,"updated_at":now()})
    for m in settings().get("referral_milestones",[]):
        if i(m.get("valid"))==count:
            key=f"{parent}_{count}"
            if not get("referral_rewards",key):
                bonus=f(m.get("bonus"));change_balance(parent,bonus,0);put("referral_rewards",key,{"bonus":bonus,"created_at":now()},merge=False)

def bind_social(uid,platform,username,profile_url,bio_text):
    platform=s(platform,30).lower()
    if platform not in {"youtube","facebook","twitter","instagram","tiktok"}:raise ValueError("unsupported_platform")
    item={"telegram_id":str(uid),"platform":platform,"username":s(username,100).lstrip("@"),"profile_url":s(profile_url,1500),"bio_text":s(bio_text,2000),"verified":False,"status":"pending","created_at":now(),"updated_at":now()}
    put("social_bindings",f"{uid}_{platform}",item,merge=False);return item

def verify_social(uid,platform):
    item=get("social_bindings",f"{uid}_{platform}")
    if not item:raise ValueError("binding_not_found")
    rules=[x for x in all_docs("tasks") if x.get("active") and x.get("type")=="social_bio" and x.get("platform")==platform]
    if not rules:raise ValueError("verification_rule_missing")
    rule=rules[0];expected=s(rule.get("verification_marker"),500).lower();mode=s(rule.get("verification_mode"),50)
    verified=False
    if mode=="provided_text":verified=bool(expected and expected in s(item.get("bio_text"),3000).lower())
    elif mode=="url_contains" and item.get("profile_url"):
        try:
            r=requests.get(item["profile_url"],timeout=12,headers={"User-Agent":"Mozilla/5.0"})
            verified=bool(expected and expected in r.text.lower())
        except:verified=False
    if verified:
        key=f"{uid}_{platform}"
        if not get("binding_rewards",key):
            change_balance(uid,f(rule.get("reward")),f(rule.get("coin_reward")));put("binding_rewards",key,{"created_at":now()},merge=False)
        update("social_bindings",key,{"verified":True,"status":"verified","verified_at":now(),"updated_at":now()})
    return verified

BLOCKED_HTML="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#08090e"><title>{{title}}</title><style>body{margin:0;background:#08090e;color:#fff;font-family:system-ui}.box{width:min(460px,90%);margin:16vh auto;padding:30px;text-align:center;border:1px solid #2b2f38;border-radius:25px;background:#11141b}.logo{width:80px;height:80px;border-radius:25px;background:linear-gradient(135deg,#ff7138,#ff9d4c);display:grid;place-items:center;margin:auto;font-weight:950;font-size:28px}</style></head><body><div class="box"><div class="logo">FG</div><h2>Telegram থেকে প্রবেশ করুন</h2><p>This Mini App can only be opened from Telegram.</p></div></body></html>"""

USER_HTML="""<!doctype html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><meta name="theme-color" content="#08090e"><title>{{title}}</title><script src="https://telegram.org/js/telegram-web-app.js"></script><style>body{margin:0;background:#08090e;color:#fff;font-family:system-ui}.app{max-width:760px;margin:auto;padding:15px 12px 100px}.top{display:flex;justify-content:space-between;padding:8px 2px 16px}.brand{font-size:24px;font-weight:950}.pill{border:1px solid #56372c;background:#211613;color:#ffad80;border-radius:99px;padding:7px 11px}.hero,.card{background:linear-gradient(145deg,#151920,#0f1116);border:1px solid #292d35;border-radius:22px;padding:17px;margin-top:11px}.avatar{width:62px;height:62px;border-radius:21px;background:linear-gradient(135deg,#ff7138,#ff9e50);display:grid;place-items:center;font-weight:950;font-size:24px}.name{font-size:24px;font-weight:950;margin-top:9px}.muted{color:#9198a8;line-height:1.5}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:15px}.stat{padding:13px;background:#0c0e13;border:1px solid #292d35;border-radius:17px}.stat b{font-size:21px}.stat span{display:block;color:#9198a8;font-size:11px;margin-top:4px}.task{display:flex;gap:10px;align-items:center;border:1px solid #292d35;padding:13px;border-radius:18px;margin-top:10px}.icon{width:45px;height:45px;border-radius:15px;display:grid;place-items:center;background:#191c24}.main{flex:1}.taskname{font-weight:900}.reward{color:#ffc62c;font-weight:900}.btn{border:0;border-radius:13px;padding:10px 14px;font-weight:900}.primary{background:linear-gradient(135deg,#ff7138,#ff9c4c);color:#fff}.secondary{border:1px solid #593a2e;background:#211613;color:#ffab7c}.input,.select,.textarea{width:100%;background:#0a0c11;border:1px solid #292d35;border-radius:13px;color:#fff;padding:12px;margin:5px 0}.textarea{min-height:100px}.nav{position:fixed;left:50%;bottom:0;transform:translateX(-50%);width:min(760px,100%);display:grid;grid-template-columns:repeat(5,1fr);background:#090b10ef;border-top:1px solid #242832;padding:8px 7px calc(8px + env(safe-area-inset-bottom));z-index:10}.nav button{border:0;background:transparent;color:#747b88;padding:8px 2px;font-size:11px}.nav button.active{color:#ff7b42;background:#211714;border-radius:13px}.section{font-size:19px;font-weight:900;margin:20px 2px 8px}.wheel{width:min(82vw,300px);aspect-ratio:1;border-radius:50%;margin:10px auto 15px;background:conic-gradient(#201817 0 60deg,#181820 60deg 120deg,#211817 120deg 180deg,#181820 180deg 240deg,#211817 240deg 300deg,#181820 300deg 360deg);border:9px solid #1d2029;transition:transform 1.8s cubic-bezier(.2,.8,.2,1);display:grid;place-items:center;box-shadow:0 0 50px #ff713822}.center{width:72px;height:72px;border-radius:50%;background:#0d1016;border:3px solid #343945;display:grid;place-items:center;font-weight:900}.empty{text-align:center;padding:28px;color:#9198a8}.toast{display:none;position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#191c24;border:1px solid #363b46;padding:12px 15px;border-radius:14px;z-index:50}@media(max-width:520px){.stats{gap:5px}}</style></head><body><div id="toast" class="toast"></div><div id="root" class="app"></div><script>const TG=window.Telegram&&window.Telegram.WebApp?window.Telegram.WebApp:null;if(TG){TG.ready();TG.expand()}const LANG={{language|tojson}},BN=LANG==="bn";const T=(a,b)=>BN?a:b;const S={user:null,settings:null,tasks:[],page:"home",bindings:{}};function e(x){return String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[c]))}async function api(u,o={}){o.headers=Object.assign({"Content-Type":"application/json","X-Telegram-Init-Data":TG?TG.initData:""},o.headers||{});const r=await fetch(u,o),d=await r.json();if(!r.ok||d.ok===false)throw new Error(d.error||"Request failed");return d}function m(v){return Number(v||0).toFixed(3).replace(/\.0+$/,"")}function toast(v){const x=document.getElementById("toast");x.textContent=v;x.style.display="block";setTimeout(()=>x.style.display="none",2600)}function nav(){return `<div class="nav"><button class="${S.page==="home"?"active":""}" onclick="go('home')">⌂<br>${T("হোম","Home")}</button><button class="${S.page==="tasks"?"active":""}" onclick="go('tasks')">◎<br>${T("টাস্ক","Tasks")}</button><button class="${S.page==="rank"?"active":""}" onclick="go('rank')">♜<br>${T("র‍্যাঙ্ক","Rank")}</button><button class="${S.page==="activity"?"active":""}" onclick="go('activity')">▣<br>${T("কার্যক্রম","Activity")}</button><button class="${S.page==="profile"?"active":""}" onclick="go('profile')">♙<br>${T("প্রোফাইল","Profile")}</button></div>`}function head(){return `<div class="top"><div class="brand">✦ ${e(S.settings?.app_name||"FoxiGrow")}</div><div class="pill">${BN?"বাংলা":"English"}</div></div>`}function taskCard(x){return `<div class="task"><div class="icon">${e(x.icon||"✓")}</div><div class="main"><div class="taskname">${e(BN?(x.title_bn||x.title_en):(x.title_en||x.title_bn))}</div><div class="muted">${e(BN?(x.description_bn||""):(x.description_en||""))}</div><div class="reward">+${m(x.reward)} USDT · +${i(x.xp||10)} XP</div></div><button class="btn primary" onclick="start('${e(x.id)}')">${T("শুরু","Start")}</button></div>`}function home(){let u=S.user||{};return head()+`<div class="hero"><div class="avatar">${e((u.first_name||"U")[0].toUpperCase())}</div><div class="name">${e(u.first_name||"User")}</div><div class="muted">@${e(u.username||"user")}</div><div>${e("Lv."+i(u.level)+" · "+(u.badge||"Rookie"))}</div><div class="stats"><div class="stat"><b>${m(u.balance)}</b><span>USDT</span></div><div class="stat"><b>${m(u.fg_coin)}</b><span>FG Coin</span></div><div class="stat"><b>${i(u.completed_tasks)}</b><span>${T("কাজ","Tasks")}</span></div></div></div><div class="section">🔥 ${T("ডেইলি চেক-ইন","Daily Check-in")}</div><div class="card"><button class="btn primary" onclick="checkin()">${T("চেক ইন","Check in")}</button></div><div class="section">🎡 ${T("ডেইলি স্পিন","Daily Spin")}</div><div class="card"><div class="wheel" id="wheel"><div class="center">SPIN</div></div><button class="btn primary" style="width:100%" onclick="spin()">${T("স্পিন","Spin")}</button></div><div class="section">🔥 ${T("জনপ্রিয় টাস্ক","Popular Tasks")}</div><div class="card">${S.tasks.slice(0,5).map(taskCard).join("")||`<div class="empty">${T("কোনো টাস্ক নেই","No tasks")}</div>`}</div>${nav()}`}function tasks(){return head()+`<div class="section">${T("টাস্ক সেন্টার","Task Center")}</div><div class="card">${S.tasks.map(taskCard).join("")||`<div class="empty">${T("কোনো টাস্ক নেই","No tasks")}</div>`}</div>${nav()}`}async function rank(){let d=await api("/api/leaderboard");return head()+`<div class="section">🏆 ${T("লিডারবোর্ড","Leaderboard")}</div><div class="card">${d.items.map((x,n)=>`<div class="row" style="padding:11px 0;border-bottom:1px solid #292d35"><div><b>#${n+1} ${e(x.name)}</b><div class="muted">${i(x.completed_tasks)} ${T("কাজ","tasks")}</div></div><div class="reward">${m(x.balance)} USDT</div></div>`).join("")||'<div class="empty">No data</div>'}</div>${nav()}`}async function activity(){let d=await api("/api/activity");return head()+`<div class="section">▣ ${T("কার্যক্রম","Activity")}</div><div class="card">${d.items.map(x=>`<div style="padding:10px 0;border-bottom:1px solid #292d35"><b>${e(x.type)}</b><div class="muted">${e(x.created_at)}</div></div>`).join("")||'<div class="empty">No activity</div>'}</div>${nav()}`}function social(p){let b=S.bindings[p]||{};return `<div class="card"><div class="row"><b>${p.toUpperCase()}</b><span class="reward">${b.verified?"Verified":"Not verified"}</span></div><input id="${p}u" class="input" value="${e(b.username||"")}" placeholder="Username"><input id="${p}p" class="input" value="${e(b.profile_url||"")}" placeholder="Profile URL"><textarea id="${p}b" class="textarea" placeholder="Bio/About text">${e(b.bio_text||"")}</textarea><button class="btn secondary" onclick="bind('${p}')">Bind / Verify</button></div>`}function profile(){return head()+`<div class="section">♙ ${T("প্রোফাইল","Profile")}</div><div class="card"><b>${e(S.user?.first_name||"User")}</b><div class="muted">ID: ${e(S.user?.telegram_id)}</div><div class="reward">${m(S.user?.balance)} USDT</div></div><div class="section">🔗 ${T("সোশ্যাল বাইন্ড","Social Binding")}</div>${["tiktok","youtube","facebook","twitter","instagram"].map(social).join("")}<div class="section">💸 ${T("উত্তোলন","Withdrawal")}</div><div class="card"><input id="wa" class="input" type="number" step="0.001" placeholder="Amount"><select id="wm" class="select">${(S.settings.withdrawal_methods||[]).map(x=>`<option value="${e(x)}">${e(x)}</option>`).join("")}</select><input id="wc" class="input" placeholder="Account / Wallet"><button class="btn primary" onclick="withdraw()" style="width:100%">${T("রিকোয়েস্ট পাঠান","Submit")}</button></div>${nav()}`}async function render(){let h=home();if(S.page==="tasks")h=tasks();if(S.page==="rank")h=await rank();if(S.page==="activity")h=await activity();if(S.page==="profile")h=profile();document.getElementById("root").innerHTML=h}function go(p){S.page=p;render()}async function load(){let d=await api("/api/bootstrap");S.user=d.user;S.settings=d.settings;S.tasks=d.tasks;S.bindings=d.bindings;await render()}async function start(id){try{await api("/api/tasks/"+encodeURIComponent(id)+"/start",{method:"POST"});let x=S.tasks.find(z=>z.id===id);if(x&&x.link){if(TG&&TG.openLink)TG.openLink(x.link);else window.open(x.link,"_blank")}setTimeout(async()=>{try{let r=await api("/api/tasks/"+encodeURIComponent(id)+"/complete",{method:"POST"});toast(r.message);await load()}catch(err){toast(err.message)}},1200)}catch(err){toast(err.message)}}async function checkin(){try{let r=await api("/api/checkin",{method:"POST"});toast("+"+r.reward+" USDT");await load()}catch(err){toast(err.message)}}async function spin(){try{let r=await api("/api/spin",{method:"POST"});let w=document.getElementById("wheel");if(w)w.style.transform=`rotate(${1440+r.slot*60+30}deg)`;setTimeout(async()=>{toast(r.message);await load()},1800)}catch(err){toast(err.message)}}async function bind(p){try{await api("/api/social/"+p+"/bind",{method:"POST",body:JSON.stringify({username:document.getElementById(p+"u").value,profile_url:document.getElementById(p+"p").value,bio_text:document.getElementById(p+"b").value})});let r=await api("/api/social/"+p+"/verify",{method:"POST"});toast(r.verified?"Verified":"Verification pending");await load()}catch(err){toast(err.message)}}async function withdraw(){try{let r=await api("/api/withdraw",{method:"POST",body:JSON.stringify({amount:Number(document.getElementById("wa").value),method:document.getElementById("wm").value,account:document.getElementById("wc").value})});toast(r.message);await load()}catch(err){toast(err.message)}}load();</script></body></html>"""

ADMIN_HTML="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#08090e"><title>FoxiGrow Admin</title><script src="https://telegram.org/js/telegram-web-app.js"></script><style>*{box-sizing:border-box}body{margin:0;background:#08090e;color:#fff;font-family:system-ui}.wrap{max-width:1250px;margin:auto;padding:16px}.head{display:flex;justify-content:space-between}.brand{font-size:27px;font-weight:950}.pill{border:1px solid #58382d;background:#211613;color:#ffad80;border-radius:99px;padding:8px 12px}.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:14px}.stat,.card,.side{background:#11141b;border:1px solid #292d35;border-radius:19px;padding:15px}.stat b{font-size:23px}.stat span{display:block;color:#9198a8;font-size:12px}.layout{display:grid;grid-template-columns:210px 1fr;gap:12px;margin-top:12px}.side button{display:block;width:100%;border:0;background:transparent;color:#9ba2b0;text-align:left;padding:11px;border-radius:12px}.side button.active{background:#281914;color:#ff9d70}.row{display:flex;justify-content:space-between;align-items:center;gap:10px}.table{overflow:auto}table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:10px 8px;border-bottom:1px solid #252832;text-align:left;font-size:13px}th{color:#ffad7d}.btn{border:0;border-radius:12px;padding:10px 13px;font-weight:900}.primary{background:linear-gradient(135deg,#ff7138,#ff9d4d);color:#fff}.danger{border:1px solid #6c2c36;background:#271419;color:#ff8796}.input,.select,.textarea{width:100%;padding:11px;border-radius:12px;border:1px solid #292d35;background:#0b0d12;color:#fff;margin:5px 0}.textarea{min-height:95px}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.full{grid-column:1/-1}.muted{color:#9198a8;font-size:12px}@media(max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}.layout{grid-template-columns:1fr}.side{display:grid;grid-template-columns:repeat(3,1fr)}}@media(max-width:520px){.formgrid{grid-template-columns:1fr}.full{grid-column:auto}}</style></head><body><div class="wrap"><div class="head"><div class="brand">✦ {{name}} Admin</div><div class="pill">7034779471</div></div><div id="stats" class="stats"></div><div class="layout"><div class="side"><button class="active" onclick="tab('dashboard',this)">Dashboard</button><button onclick="tab('tasks',this)">Tasks</button><button onclick="tab('withdrawals',this)">Withdrawals</button><button onclick="tab('users',this)">Users</button><button onclick="tab('social',this)">Social Bindings</button><button onclick="tab('managers',this)">Managers</button><button onclick="tab('settings',this)">Settings</button></div><div id="content"></div></div></div><script>const TG=window.Telegram&&window.Telegram.WebApp?window.Telegram.WebApp:null;if(TG){TG.ready();TG.expand()}function e(x){return String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",""":"&quot;","'":"&#039;"}[c]))}async function api(u,o={}){o.headers=Object.assign({"Content-Type":"application/json","X-Telegram-Init-Data":TG?TG.initData:""},o.headers||{});let r=await fetch(u,o),d=await r.json();if(!r.ok||d.ok===false)throw new Error(d.error||"Request failed");return d}async function dash(){let d=await api("/api/admin/dashboard");document.getElementById("stats").innerHTML=Object.entries(d.stats).map(([k,v])=>`<div class="stat"><b>${e(v)}</b><span>${e(k)}</span></div>`).join("");document.getElementById("content").innerHTML='<div class="card"><h2>Admin Control Center</h2><div class="muted">Only Telegram ID 7034779471 can access this panel.</div></div>'}async function tab(n,b){document.querySelectorAll(".side button").forEach(x=>x.classList.remove("active"));b.classList.add("active");if(n==="dashboard")return dash();if(n==="tasks")return tasks();if(n==="withdrawals")return wds();if(n==="users")return users();if(n==="social")return social();if(n==="managers")return managers();if(n==="settings")return settings()}async function tasks(){let d=await api("/api/admin/tasks");document.getElementById("content").innerHTML=`<div class="card"><h2>Create Task</h2><div class="formgrid"><input id="bn" class="input" placeholder="Bengali title"><input id="en" class="input" placeholder="English title"><input id="type" class="input" placeholder="Task type"><input id="platform" class="input" placeholder="Platform"><input id="reward" class="input" type="number" placeholder="Reward"><input id="xp" class="input" type="number" placeholder="XP"><input id="max" class="input" type="number" placeholder="Limit"><input id="priority" class="input" type="number" placeholder="Priority"><input id="link" class="input full" placeholder="Task link"><textarea id="db" class="textarea full" placeholder="Bengali description"></textarea><textarea id="de" class="textarea full" placeholder="English description"></textarea><input id="marker" class="input full" placeholder="Verification marker"></div><button class="btn primary" onclick="createTask()">Create</button></div><div class="card"><h2>Tasks</h2><div class="table"><table><tr><th>Title</th><th>Type</th><th>Reward</th><th>Limit</th><th>Active</th><th></th></tr>${d.tasks.map(x=>`<tr><td>${e(x.title_en)}</td><td>${e(x.type)}</td><td>${e(x.reward)}</td><td>${e(x.completed_count)}/${e(x.max_limit)}</td><td>${x.active?"ON":"OFF"}</td><td><button class="btn danger" onclick="delTask('${e(x.id)}')">Delete</button></td></tr>`).join("")}</table></div></div>`}async function createTask(){try{await api("/api/admin/tasks",{method:"POST",body:JSON.stringify({title_bn:bn.value,title_en:en.value,type:type.value,platform:platform.value,reward:Number(reward.value||0),xp:Number(xp.value||10),max_limit:Number(max.value||0),priority:Number(priority.value||0),link:link.value,description_bn:db.value,description_en:de.value,verification_marker:marker.value,active:true})});await tasks()}catch(x){alert(x.message)}}async function delTask(id){if(confirm("Delete task?")){await api("/api/admin/tasks/"+id,{method:"DELETE"});await tasks()}}async function wds(){let d=await api("/api/admin/withdrawals");document.getElementById("content").innerHTML=`<div class="card"><h2>Withdrawals</h2><div class="table"><table><tr><th>User</th><th>Amount</th><th>Method</th><th>Account</th><th>Manager</th><th>Status</th><th></th></tr>${d.withdrawals.map(x=>`<tr><td>${e(x.telegram_id)}</td><td>${e(x.amount)}</td><td>${e(x.method)}</td><td>${e(x.account)}</td><td>${e(x.manager_id||"Auto")}</td><td>${e(x.status)}</td><td>${x.status==="pending"?`<button class="btn primary" onclick="wd('${e(x.id)}','approved')">Approve</button><button class="btn danger" onclick="wd('${e(x.id)}','rejected')">Reject</button>`:"Done"}</td></tr>`).join("")}</table></div></div>`}async function wd(id,status){try{await api("/api/admin/withdrawals/"+id,{method:"POST",body:JSON.stringify({status})});await wds()}catch(x){alert(x.message)}}async function users(){let d=await api("/api/admin/users");document.getElementById("content").innerHTML=`<div class="card"><h2>Users</h2><div class="table"><table><tr><th>ID</th><th>Name</th><th>Username</th><th>Balance</th><th>Tasks</th><th>Status</th><th></th></tr>${d.users.map(x=>`<tr><td>${e(x.telegram_id)}</td><td>${e(x.first_name)}</td><td>@${e(x.username)}</td><td>${e(x.balance)}</td><td>${e(x.completed_tasks)}</td><td>${x.blocked?"Blocked":"Active"}</td><td><button class="btn ${x.blocked?"primary":"danger"}" onclick="block('${e(x.telegram_id)}',${x.blocked?"false":"true"})">${x.blocked?"Unblock":"Block"}</button></td></tr>`).join("")}</table></div></div>`}async function block(id,v){await api("/api/admin/users/"+id+"/block",{method:"POST",body:JSON.stringify({blocked:v})});await users()}async function social(){let d=await api("/api/admin/social");document.getElementById("content").innerHTML=`<div class="card"><h2>Social Bindings</h2><div class="table"><table><tr><th>User</th><th>Platform</th><th>Username</th><th>Status</th><th></th></tr>${d.bindings.map(x=>`<tr><td>${e(x.telegram_id)}</td><td>${e(x.platform)}</td><td>${e(x.username)}</td><td>${e(x.status)}</td><td><button class="btn primary" onclick="review('${e(x.id)}','verified')">Verify</button><button class="btn danger" onclick="review('${e(x.id)}','rejected')">Reject</button></td></tr>`).join("")}</table></div></div>`}async function review(id,status){await api("/api/admin/social/"+id,{method:"POST",body:JSON.stringify({status})});await social()}async function managers(){let d=await api("/api/admin/managers");document.getElementById("content").innerHTML=`<div class="card"><h2>Managers</h2><div class="table"><table><tr><th>ID</th><th>Name</th><th>Max open</th><th>Enabled</th></tr>${d.managers.map(x=>`<tr><td>${e(x.id)}</td><td>${e(x.name)}</td><td>${e(x.max_open)}</td><td>${x.enabled}</td></tr>`).join("")}</table></div></div>`}async function settings(){let d=await api("/api/admin/settings"),s=d.settings;document.getElementById("content").innerHTML=`<div class="card"><h2>Settings</h2><div class="formgrid"><input id="smin" class="input" value="${e(s.min_withdrawal)}" placeholder="Minimum withdrawal"><input id="smax" class="input" value="${e(s.max_withdrawal)}" placeholder="Maximum withdrawal"><input id="sad" class="input" value="${e(s.daily_ad_reward)}" placeholder="Ad reward"><input id="sdl" class="input" value="${e(s.daily_ad_limit)}" placeholder="Daily ad limit"><input id="sch" class="input" value="${e(s.daily_checkin_reward)}" placeholder="Daily check-in"><input id="sref" class="input" value="${e(s.referral_reward)}" placeholder="Referral reward"><label>Withdrawals <input id="sw" type="checkbox" ${s.withdrawals_enabled?"checked":""}></label><label>Tasks <input id="st" type="checkbox" ${s.tasks_enabled?"checked":""}></label><label>Ads <input id="sa" type="checkbox" ${s.ads_enabled?"checked":""}></label><label>Spin <input id="ss" type="checkbox" ${s.spin_enabled?"checked":""}></label><label>Maintenance <input id="sm" type="checkbox" ${s.maintenance?"checked":""}></label></div><button class="btn primary" onclick="save()">Save</button></div>`}async function save(){await api("/api/admin/settings",{method:"PUT",body:JSON.stringify({min_withdrawal:Number(smin.value),max_withdrawal:Number(smax.value),daily_ad_reward:Number(sad.value),daily_ad_limit:Number(sdl.value),daily_checkin_reward:Number(sch.value),referral_reward:Number(sref.value),withdrawals_enabled:sw.checked,tasks_enabled:st.checked,ads_enabled:sa.checked,spin_enabled:ss.checked,maintenance:sm.checked})});alert("Saved")}dash();</script></body></html>"""

@app.get("/")
def root():
    return render_template_string("""<!doctype html><html><body style="margin:0;background:#08090e;color:white;font-family:system-ui;text-align:center;padding:100px 20px"><h1>FoxiGrow</h1><p>Open the Mini App from Telegram.</p></body></html>""")

@app.get("/app")
def app_page():
    user=verify_init(request_init_data())
    if not user:return render_template_string(BLOCKED_HTML,title=APP_NAME)
    lang=request.args.get("lang","bn")
    if lang not in {"bn","en"}:lang="bn"
    save_user(user)
    sid=make_session(user["id"],str(user["id"])==str(ADMIN_ID),lang)
    response=make_response(render_template_string(USER_HTML,title=APP_NAME,language=lang))
    response.set_cookie("fg_session",sid,httponly=True,secure=True,samesite="None",max_age=SESSION_TTL)
    return response

@app.get("/admin")
def admin_page():
    user=verify_init(request_init_data())
    if not user or str(user.get("id"))!=str(ADMIN_ID):
        return render_template_string(BLOCKED_HTML,title=f"{APP_NAME} Admin")
    sid=make_session(user["id"],True,"en")
    response=make_response(render_template_string(ADMIN_HTML,title=f"{APP_NAME} Admin",name=APP_NAME))
    response.set_cookie("fg_session",sid,httponly=True,secure=True,samesite="None",max_age=SESSION_TTL)
    return response

@app.post("/telegram/webhook")
def webhook():
    if WEBHOOK_SECRET:
        got=request.headers.get("X-Telegram-Bot-Api-Secret-Token","")
        if not hmac.compare_digest(got,WEBHOOK_SECRET):abort(403)
    try:webhook_update(request.get_json(silent=True) or {})
    except:pass
    return jsonify({"ok":True})

@app.get("/setup-webhook")
def setup():
    if SETUP_SECRET and request.args.get("secret")!=SETUP_SECRET:abort(403)
    try:return jsonify(set_webhook())
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),500

@app.get("/health")
def health():
    return jsonify({"ok":True,"firebase":list(DB.keys()),"telegram":bool(BOT_TOKEN),"time":now()})

@app.get("/api/bootstrap")
@need_user
def bootstrap():
    x=sess();uid=x["uid"];u=refresh_level(uid) or user(uid);st=settings();items=available_tasks(uid)
    binds={p:get("social_bindings",f"{uid}_{p}") or {} for p in ["youtube","facebook","twitter","instagram","tiktok"]}
    return jsonify({"ok":True,"user":u,"settings":st,"tasks":items,"bindings":binds})

@app.post("/api/tasks/<tid>/start")
@need_user
def api_task_start(tid):
    try:return jsonify({"ok":True,"task":start_task(sess()["uid"],tid)})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/tasks/<tid>/complete")
@need_user
def api_task_complete(tid):
    try:complete_task(sess()["uid"],tid);return jsonify({"ok":True,"message":"Reward added"})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/checkin")
@need_user
def api_checkin():
    try:return jsonify({"ok":True,"message":f"+{checkin(sess()['uid'])} USDT","reward":checkin})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/ads/complete")
@need_user
def api_ads():
    try:
        reward,remaining=ad_complete(sess()["uid"])
        return jsonify({"ok":True,"reward":reward,"remaining":remaining,"message":f"+{reward} USDT"})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/spin")
@need_user
def api_spin():
    try:
        slot,label,reward=spin(sess()["uid"])
        return jsonify({"ok":True,"slot":slot,"label":label,"reward":reward,"message":label})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.get("/api/leaderboard")
@need_user
def leaderboard():
    rows=all_docs("users");rows.sort(key=lambda x:(f(x.get("balance")),i(x.get("completed_tasks"))),reverse=True)
    return jsonify({"ok":True,"items":[{"name":x.get("first_name") or x.get("username") or "User","balance":f(x.get("balance")),"completed_tasks":i(x.get("completed_tasks"))} for x in rows[:100]]})

@app.get("/api/activity")
@need_user
def activity():
    uid=str(sess()["uid"]);rows=[x for x in all_docs("activity") if str(x.get("telegram_id"))==uid];rows.sort(key=lambda x:x.get("created_at",""),reverse=True)
    return jsonify({"ok":True,"items":rows[:100]})

@app.post("/api/social/<platform>/bind")
@need_user
def api_bind(platform):
    data=request.get_json(silent=True) or {}
    try:return jsonify({"ok":True,"binding":bind_social(sess()["uid"],platform,data.get("username"),data.get("profile_url"),data.get("bio_text"))})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/social/<platform>/verify")
@need_user
def api_verify(platform):
    try:
        return jsonify({"ok":True,"verified":verify_social(sess()["uid"],platform)})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.post("/api/withdraw")
@need_user
def api_withdraw():
    data=request.get_json(silent=True) or {}
    try:return jsonify({"ok":True,"message":"Withdrawal request submitted","withdrawal":create_withdrawal(sess()["uid"],data.get("amount"),data.get("method"),data.get("account"))})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.get("/api/admin/dashboard")
@need_admin
def ad_dash():
    return jsonify({"ok":True,"stats":{"users":len(all_docs("users")),"tasks":len(all_docs("tasks")),"withdrawals":len(all_docs("withdrawals"))}})

@app.get("/api/admin/users")
@need_admin
def ad_users():return jsonify({"ok":True,"users":all_docs("users")})

@app.post("/api/admin/users/<uid>/block")
@need_admin
def ad_block(uid):
    data=request.get_json(silent=True) or {};update("users",uid,{"blocked":bool(data.get("blocked")),"updated_at":now()});return jsonify({"ok":True})

@app.get("/api/admin/tasks")
@need_admin
def ad_tasks():return jsonify({"ok":True,"tasks":all_docs("tasks")})

@app.post("/api/admin/tasks")
@need_admin
def ad_create_task():
    data=request.get_json(silent=True) or {};tid=secrets.token_hex(10)
    item={"id":tid,"title_bn":s(data.get("title_bn")),"title_en":s(data.get("title_en")),"description_bn":s(data.get("description_bn"),2500),"description_en":s(data.get("description_en"),2500),"type":s(data.get("type"),40),"platform":s(data.get("platform"),40),"link":s(data.get("link"),1500),"reward":f(data.get("reward")),"coin_reward":f(data.get("coin_reward")),"xp":max(0,i(data.get("xp") or 10)),"max_limit":max(0,i(data.get("max_limit"))),"completed_count":0,"publish_at":max(0,i(data.get("publish_at"))),"expires_at":max(0,i(data.get("expires_at"))),"priority":i(data.get("priority")),"require_screenshot":bool(data.get("require_screenshot")),"require_profile_link":bool(data.get("require_profile_link")),"verification_mode":s(data.get("verification_mode"),40),"verification_marker":s(data.get("verification_marker"),500),"active":True,"created_at":now(),"updated_at":now()}
    if not item["title_bn"] or not item["title_en"]:return jsonify({"ok":False,"error":"title_required"}),400
    put("tasks",tid,item,merge=False);return jsonify({"ok":True,"task":item})

@app.delete("/api/admin/tasks/<tid>")
@need_admin
def ad_del_task(tid):delete("tasks",tid);return jsonify({"ok":True})

@app.get("/api/admin/withdrawals")
@need_admin
def ad_wds():return jsonify({"ok":True,"withdrawals":list_withdrawals()})

@app.post("/api/admin/withdrawals/<wid>")
@need_admin
def ad_wd(wid):
    data=request.get_json(silent=True) or {}
    try:process_withdrawal(wid,data.get("status"),data.get("note",""));return jsonify({"ok":True})
    except Exception as exc:return jsonify({"ok":False,"error":str(exc)}),400

@app.get("/api/admin/social")
@need_admin
def ad_social():return jsonify({"ok":True,"bindings":all_docs("social_bindings")})

@app.post("/api/admin/social/<bid>")
@need_admin
def ad_social_review(bid):
    data=request.get_json(silent=True) or {};status=s(data.get("status"),30)
    if status not in {"pending","verified","rejected"}:return jsonify({"ok":False,"error":"invalid_status"}),400
    update("social_bindings",bid,{"status":status,"verified":status=="verified","reviewed_at":now(),"updated_at":now()});return jsonify({"ok":True})

@app.get("/api/admin/managers")
@need_admin
def ad_mgrs():return jsonify({"ok":True,"managers":all_docs("managers")})

@app.post("/api/admin/managers")
@need_admin
def ad_mgr_create():
    data=request.get_json(silent=True) or {};mid=s(data.get("id"),80) or secrets.token_hex(10);item={"id":mid,"name":s(data.get("name"),100),"max_open":max(1,i(data.get("max_open") or 10)),"enabled":bool(data.get("enabled",True)),"created_at":now()};put("managers",mid,item,merge=False);return jsonify({"ok":True,"manager":item})

@app.get("/api/admin/settings")
@need_admin
def ad_settings():return jsonify({"ok":True,"settings":settings()})

@app.put("/api/admin/settings")
@need_admin
def ad_set_settings():return jsonify({"ok":True,"settings":set_settings(request.get_json(silent=True) or {})})

@app.get("/api/admin/firebase-health")
@need_admin
def ad_firebase():return jsonify({"ok":True,"databases":{k:True for k in DB}})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","10000")))
