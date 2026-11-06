# -*- coding: utf-8 -*-
"""منصة مرصد (Marsad) v5.0 — Full Release (Commercial Library + Paywall)"""
import streamlit as st
import pandas as pd
import json, base64, urllib.parse, os, re, time
from datetime import datetime
import pytesseract
from PIL import Image
import requests
import difflib
import streamlit.components.v1 as components

st.set_page_config(page_title="مرصد | مكتب مشتريات أعمالك", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

COMPANY_NAME = "مؤسسة مخلد محمد بن سليمان العنزي التجارية"
CR_NUMBER = "1009005566"
VAT_NUMBER = "30056521610003"
DEFAULT_WHATSAPP = "0592859590"
ADMIN_PWD = "marsad2026"
OPS_PWD = "marsad_ops_2026"
BULK_DISCOUNT_THRESHOLD = 20
BULK_DISCOUNT_RATE = 0.05
TRUSTED_PARTNER_MIN_ORDERS = 3
AI_DAILY_LIMIT = 15
ITEMS_PER_PAGE = 12

try:
    WHATSAPP_NUMBER = st.secrets["WHATSAPP_NUMBER"]
except Exception:
    WHATSAPP_NUMBER = DEFAULT_WHATSAPP

# ═══ خلية النحل للذكاء الاصطناعي ═══
GEMINI_KEYS = []
try:
    raw = st.secrets.get("GEMINI_KEYS", [])
    if isinstance(raw, str): GEMINI_KEYS = [raw]
    elif isinstance(raw, (list, tuple)): GEMINI_KEYS = list(raw)
except Exception: pass

AI_MODELS = ["gemini-2.0-flash-exp", "gemini-1.5-flash-latest", "gemini-1.5-flash-002", "gemini-1.5-pro-latest"]
AI_ENABLED = len(GEMINI_KEYS) > 0

# ═══ تهيئة الجلسة ═══
defaults = {
    "cart": {}, "sourcing_requests": [], "page": "home", "selected_cat": "الكل",
    "admin_logged_in": False, "ops_logged_in": False, "last_order": None, "orders_history": [],
    "last_cart": {}, "product_order_dates": {}, "approval_loaded": False, "last_submission_time": 0,
    "ai_messages": [], "ai_questions_count": 0, "prefilled_ai_question": None, "calc_result": None,
    "last_click_times": {}, "key_health": {}, "product_page": 1, "user_biz": "", "user_phone": "",
    "subscription_tier": "Free"  # Free, Basic, Pro, Business
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ═══ تحميل الكتالوج ═══
@st.cache_data
def load_catalog():
    try:
        df = pd.read_csv("Marsad_Valid_Products.csv")
        for c in ["اسم المنتج", "السعر", "القطاع"]:
            if c not in df.columns: raise ValueError(f"مفقود: {c}")
        df["السعر"] = pd.to_numeric(df["السعر"], errors='coerce').fillna(0.0)
        if "ملاحظات" not in df.columns: df["ملاحظات"] = ""
        if "الوحدة" not in df.columns: df["الوحدة"] = "حبة"
        forbidden = ["بنزين", "سجائر", "معسل", "تبغ", "تنباك", "شيشة"]
        for kw in forbidden:
            df = df[~df["اسم المنتج"].str.contains(kw, case=False, na=False)]
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"خطأ في الكتالوج: {e}")
        return pd.DataFrame(columns=["اسم المنتج","السعر","القطاع","ملاحظات","الوحدة"])

df_catalog = load_catalog()

# ═══ التصميم ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;background:#F8FAFC;color:#0F172A;}
#MainMenu,header,footer,.stDeployButton{visibility:hidden;}
div[data-testid="stToolbar"]{display:none !important;}
.clean-card{background:#FFF;border:1px solid #E2E8F0;border-radius:12px;padding:20px;transition:all .3s;box-shadow:0 4px 6px -1px rgba(0,0,0,.02);margin-bottom:15px;position:relative;overflow:hidden;}
.clean-card:hover{border-color:#C2410C;box-shadow:0 12px 20px -8px rgba(194,65,12,.2);transform:translateY(-4px);}
.stButton>button{background:#0F172A !important;color:#FFF !important;border:none !important;border-radius:8px !important;padding:10px 20px !important;font-weight:700 !important;font-family:'Tajawal',sans-serif !important;transition:all .2s !important;width:100%;}
.stButton>button:hover{background:#C2410C !important;box-shadow:0 4px 12px rgba(194,65,12,.3) !important;}
.stTextInput input,.stSelectbox div[data-baseweb="select"],.stNumberInput input,.stTextArea textarea{background:#FFF !important;border:1px solid #CBD5E1 !important;color:#0F172A !important;border-radius:8px !important;}
h1,h2,h3,h4{font-family:'Tajawal',sans-serif !important;color:#0F172A;}
.bulk-banner{background:linear-gradient(135deg,#FEF3C7 0%,#FED7AA 100%);border-right:5px solid #C2410C;border-radius:10px;padding:15px;margin:15px 0;}
.savings-banner{background:linear-gradient(135deg,#ECFDF5 0%,#D1FAE5 100%);border-right:5px solid #10B981;border-radius:10px;padding:15px;margin:15px 0;}
.paywall-lock{background:linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 50%); height: 150px; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 20px; position: relative; margin-top: -100px;}
.watermark-text{font-size:0.65rem;color:#94A3B8;opacity:0.55;font-weight:500;margin-top:2px;}
.pricing-card{background:#FFF;border:2px solid #E2E8F0;border-radius:12px;padding:25px;text-align:center;transition:all .3s;}
.pricing-card.pro{border-color:#C2410C;box-shadow:0 10px 25px -5px rgba(194,65,12,.2);transform:scale(1.05);}
.pricing-price{font-size:2.5rem;font-weight:900;color:#0F172A;margin:15px 0;}
</style>
""", unsafe_allow_html=True)

# ═══ دوال مساعدة ═══
def safe_click(key, cooldown=1.5):
    now = time.time()
    if now - st.session_state.last_click_times.get(key, 0) < cooldown: return False
    st.session_state.last_click_times[key] = now
    return True

def build_system_prompt():
    lines = [f"- {row['اسم المنتج']} | {row['السعر']} ر.س | {row['القطاع']}" for _, row in df_catalog.head(50).iterrows()]
    return f"""أنت "مساعد مرصد الذكي"، مستشار مشتريات في منصة مرصد.
الكتالوج:
{chr(10).join(lines)}"""

def call_gemini_single(key, model, prompt, system, timeout=15):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {"system_instruction": {"parts": [{"text": system}]}, "contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4, "maxOutputTokens": 400}}
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code == 200: return True, r.json()["candidates"][0]["content"]["parts"][0]["text"].strip(), "200"
        return False, None, str(r.status_code)
    except Exception as e: return False, None, f"EXC:{str(e)[:25]}"

def resilient_ai_generate(user_question):
    if not AI_ENABLED: return False, "المساعد غير متاح حالياً. تواصل مع الدعم: " + WHATSAPP_NUMBER, None
    system = build_system_prompt(); attempts = 0; dead_keys = set()
    for key_idx, key in enumerate(GEMINI_KEYS):
        if key_idx in dead_keys: continue
        for model in AI_MODELS:
            attempts += 1
            ok, text, status = call_gemini_single(key, model, user_question, system)
            if ok:
                st.session_state.key_health[key_idx] = {"status":"ok","model":model}
                return True, text, {"key_idx":key_idx, "model":model}
            if status == "401": dead_keys.add(key_idx); break
            elif status == "429": break
            elif status == "403": break
    return False, "المساعد مشغول حالياً، جرب بعد دقيقة 🙏", None

@st.dialog("💬 مساعد مرصد الذكي", width="large")
def ai_chat_modal():
    if not AI_ENABLED: st.error("⚠️ غير متاح حالياً."); return
    if st.session_state.ai_questions_count >= AI_DAILY_LIMIT: st.warning("وصلت للحد اليومي."); return
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"]=="user" else "🛡️"): st.markdown(msg["content"])
    user_input = st.chat_input("اكتب سؤالك هنا...")
    if user_input:
        st.session_state.ai_messages.append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="🧑‍💼"): st.markdown(user_input)
        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("أفكر..."):
                ok, answer, meta = resilient_ai_generate(user_input)
                if ok: st.markdown(answer); st.session_state.ai_messages.append({"role":"assistant","content":answer}); st.session_state.ai_questions_count += 1
                else: st.warning(answer)

# ═══ الترويسة ═══
def render_header():
    cc = sum(i['qty'] for i in st.session_state.cart.values())
    c1,c2,c3,c4,c5,c6,c7 = st.columns([3,1.5,1.5,1.5,1.5,1.5,1])
    with c1:
        st.markdown("""<div style="display:flex;align-items:center;gap:10px;">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none"><circle cx="18" cy="18" r="16" fill="#0F172A"/><path d="M11 18L15 22L25 12" stroke="#C2410C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <div><h2 style="margin:0;font-size:1.5rem;font-weight:900;">مَـرْصَــد <span style="color:#C2410C;">.</span></h2></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if st.button("🏠 الرئيسية", key="nh"): st.session_state.page="home"; st.rerun()
    with c3:
        if st.button("📦 المنتجات", key="np"): st.session_state.page="products"; st.rerun()
    with c4:
        if st.button("📷 القارئ", key="ns"): st.session_state.page="scanner"; st.rerun()
    with c5:
        if st.button("📚 المكتبة", key="nlib"): st.session_state.page="library"; st.rerun()
    with c6:
        if st.button("🚨 التنبيهات", key="nalert"): st.session_state.page="alerts"; st.rerun()
    with c7:
        if st.button(f"🛒 ({cc})" if cc>0 else "🛒", key="ncart"): st.session_state.page="cart"; st.rerun()
    
    cai1, cai2 = st.columns([8,2])
    with cai2:
        if AI_ENABLED:
            if st.button("💬 مساعد مرصد", key="hai"): ai_chat_modal()
    st.markdown("<hr style='border-color:#E2E8F0;margin-top:15px;margin-bottom:25px;'>", unsafe_allow_html=True)

# ═══ الرئيسية ═══
def show_home():
    st.markdown("""<div class="clean-card" style="padding:40px;background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:16px;margin-bottom:30px;">
        <h1 style="color:white;font-size:2.5rem;margin-top:15px;margin-bottom:15px;">لا نبيع كرتون، نختصر رحلة مشتريات منشأتك.</h1>
        <p style="color:#94A3B8;font-size:1.1rem;">أرسل احتياجك، نتحقق من السعر والتوفر، تعتمد العرض، ونتولى الباقي.</p>
    </div>""", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if st.button("🚀 تصفح المنتجات", key="hb"): st.session_state.page="products"; st.rerun()
    with c2:
        if st.button("📚 اقرأ المكتبة التشغيلية", key="h_lib"): st.session_state.page="library"; st.rerun()

# ═══ المنتجات ═══
def show_products():
    st.markdown("<h2 style='font-weight:800;margin-bottom:20px;'>📦 كتالوج المنتجات</h2>", unsafe_allow_html=True)
    cats = ["الكل"] + list(df_catalog["القطاع"].unique())
    c1,c2 = st.columns([2,1])
    with c1: q = st.text_input("🔍 بحث...", placeholder="اسم المنتج...")
    with c2: sel = st.selectbox("القطاع", cats)
    df = df_catalog.copy()
    if sel != "الكل": df = df[df["القطاع"]==sel]
    if q: df = df[df["اسم المنتج"].str.contains(q, case=False, na=False)]
    
    total_items = len(df)
    total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    if st.session_state.product_page > total_pages: st.session_state.product_page = total_pages
    start_idx = (st.session_state.product_page - 1) * ITEMS_PER_PAGE
    df_page = df.iloc[start_idx:start_idx+ITEMS_PER_PAGE]
    st.write(f"عرض {start_idx+1} إلى {min(start_idx+ITEMS_PER_PAGE, total_items)} من أصل {total_items} منتج")

    cols = st.columns(3)
    for idx, row in df_page.reset_index(drop=True).iterrows():
        with cols[idx % 3]:
            name, price, cat = row["اسم المنتج"], float(row["السعر"]), row["القطاع"]
            unit = row.get("الوحدة","حبة")
            wm = st.session_state.get('user_phone') or 'محمي'
            st.markdown(f"""<div class="clean-card" style="margin-bottom:0;border-bottom-left-radius:0;border-bottom-right-radius:0;">
                <span style="background:#FEF3C7;color:#92400E;font-size:.75rem;padding:2px 8px;border-radius:6px;">{cat}</span>
                <h4 style="margin-top:10px;margin-bottom:5px;font-size:1.1rem;">{name}</h4>
                <p style="color:#64748B;font-size:.8rem;margin-bottom:10px;">الوحدة: {unit}</p>
                <div style="display:flex;align-items:baseline;gap:10px;"><span style="font-size:1.4rem;font-weight:900;">{price:.2f} ر.س</span></div>
                <div class="watermark-text">🔒 مسجل لـ: {wm}</div>
            </div>""", unsafe_allow_html=True)
            with st.container():
                st.markdown("<div style='background:#FFF;border:1px solid #E2E8F0;border-top:none;border-bottom-left-radius:12px;border-bottom-right-radius:12px;padding:15px;margin-top:-15px;margin-bottom:15px;'>", unsafe_allow_html=True)
                qty = st.number_input("الكمية", min_value=1, value=1, key=f"q_{idx}")
                if st.button("🛒 اطلب الآن", key=f"a_{idx}", type="primary"):
                    cq = st.session_state.cart.get(name,{}).get('qty',0)
                    st.session_state.cart[name] = {"price":price,"qty":cq+qty,"unit":unit,"category":cat}
                    st.toast(f"✓ {qty} × {name}"); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ═══ 📚 المكتبة التشغيلية (استراتيجية كوبايلت) ═══
def show_library():
    # 1. Hero Section (القصة)
    st.markdown("""
    <div class="clean-card" style="background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:16px;margin-bottom:30px;padding:40px;">
        <span style="background:rgba(194,65,12,.2);color:#F97316;padding:6px 14px;border-radius:20px;font-size:.85rem;font-weight:700;">مرصد التشغيل السعودي</span>
        <h2 style="color:white;margin-top:15px;">من قلب الميدان.. إلى بناء نظام تشغيلي.</h2>
        <p style="color:#CBD5E1;line-height:1.7;font-size:1.1rem;">
            شاهدت بعيني كيف تُترك العربات مليئة بالبضائع بسبب تعطل سيستم. كيف تنفد المياه من الرفوف وهي متكدسة في المستودع. 
            أنشأنا "المكتبة التشغيلية" لننقل لك الخبرة الميدانية ونحولها إلى أدوات وقوالب تحمي أرباحك من النزيف الصامت.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Pricing Tiers (باقات كوبايلت)
    st.markdown("<h3 style='font-weight:800;text-align:center;margin-bottom:20px;'>اختر الباقة المناسبة لمنشأتك</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""<div class="pricing-card">
            <h4 style="color:#64748B;">Basic</h4>
            <p style="font-size:0.9rem;color:#94A3B8;">للمشرفين والأفراد</p>
            <div class="pricing-price">199 <span style="font-size:1rem;color:#64748B;">ر.س/شهر</span></div>
            <ul style="text-align:right;font-size:0.9rem;color:#475569;margin-bottom:20px;">
                <li>✅ وصول للمكتبة</li>
                <li>✅ قوالب PDF جاهزة</li>
            </ul>
        </div>""", unsafe_allow_html=True)
        if st.button("اشترك Basic", key="sub_basic"):
            msg = urllib.parse.quote("أرغب بالاشتراك في باقة Basic للمكتبة التشغيلية (199 ريال/شهر)")
            st.markdown(f'<a href="https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;margin-top:10px;">💬 اشترك عبر الواتساب</div></a>', unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class="pricing-card pro">
            <span style="background:#C2410C;color:white;padding:4px 12px;border-radius:20px;font-size:0.8rem;position:absolute;top:-10px;right:20px;">الأكثر طلباً</span>
            <h4 style="color:#C2410C;">Pro</h4>
            <p style="font-size:0.9rem;color:#94A3B8;">لأصحاب المتاجر الفردية</p>
            <div class="pricing-price">499 <span style="font-size:1rem;color:#64748B;">ر.س/شهر</span></div>
            <ul style="text-align:right;font-size:0.9rem;color:#475569;margin-bottom:20px;">
                <li>✅ المكتبة كاملة</li>
                <li>✅ نموذج التقييم 50 سؤال</li>
                <li>✅ قوالب Excel تفاعلية</li>
                <li>✅ تقارير المخاطر</li>
            </ul>
        </div>""", unsafe_allow_html=True)
        if st.button("اشترك Pro", key="sub_pro", type="primary"):
            msg = urllib.parse.quote("أرغب بالاشتراك في باقة Pro للمكتبة التشغيلية (499 ريال/شهر)")
            st.markdown(f'<a href="https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;margin-top:10px;">💬 اشترك عبر الواتساب</div></a>', unsafe_allow_html=True)

    with c3:
        st.markdown("""<div class="pricing-card">
            <h4 style="color:#64748B;">Business</h4>
            <p style="font-size:0.9rem;color:#94A3B8;">للسلاسل المتوسطة</p>
            <div class="pricing-price">1499 <span style="font-size:1rem;color:#64748B;">ر.س/شهر</span></div>
            <ul style="text-align:right;font-size:0.9rem;color:#475569;margin-bottom:20px;">
                <li>✅ كل ميزات Pro</li>
                <li>✅ لـ 5 فروع</li>
                <li>✅ لوحة قيادة KPIs</li>
                <li>✅ جلسة مراجعة شهرية</li>
            </ul>
        </div>""", unsafe_allow_html=True)
        if st.button("اشترك Business", key="sub_business"):
            msg = urllib.parse.quote("أرغب بالاشتراك في باقة Business للمكتبة التشغيلية (1499 ريال/شهر)")
            st.markdown(f'<a href="https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;margin-top:10px;">💬 اشترك عبر الواتساب</div></a>', unsafe_allow_html=True)

    st.markdown("<hr style='margin:40px 0;'>", unsafe_allow_html=True)

    # 3. المحتوى والمسارات
    st.markdown("<h3 style='font-weight:800;'>📖 محتوى المكتبة</h3>", unsafe_allow_html=True)
    
    with st.expander("📦 المسار الأول: إدارة المستودع والحاوية الخلفية", expanded=True):
        st.markdown("""
        <p style="color:#475569;">كيف تمنع تكدس الحاويات، وتدير الاستلام، وتحافظ على المخزون؟</p>
        """, unsafe_allow_html=True)
        
        # المحتوى المجاني (20%)
        st.markdown("""
        <div style="background:#F8FAFC;border-right:4px solid #10B981;padding:15px;border-radius:8px;margin-bottom:15px;">
            <h4 style="margin:0;color:#065F46;">🔓 دراسة حالة: "البيبسي المنسي"</h4>
            <p style="margin:5px 0 0 0;color:#334155;font-size:0.9rem;">
                أثناء التفتيش، تم العثور على عبوة بيبسي بين الكراتين الفارغة. الفوضى في المنطقة الخلفية قد تخفي منتجات وتسبب فاقداً.
                <br><b>الإجراء الميداني:</b> إزالة العبوة ومراجعة المنطقة بالكامل.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # المحتوى المدفوع (80% - جدار الدفع)
        st.markdown("""
        <div style="background:#FFF;border:1px solid #E2E8F0;padding:20px;border-radius:8px;position:relative;overflow:hidden;">
            <div style="filter:blur(4px);opacity:0.5;">
                <h4>تحليل 5 Whys الكامل:</h4>
                <p>لماذا تراكمت الكراتين؟ ← لأن الاستلام لم يعالج في 24 ساعة ← لأن العمالة غير كافية ← لأن جدولة الفريق غير منظمة...</p>
                <h4>SOP إدارة المستودع:</h4>
                <p>1. فحص الرفوف كل ساعتين. 2. تطبيق FIFO. 3. التخلص من الكراتين الفارغة...</p>
                <h4>مؤشرات الأداء KPIs:</h4>
                <p>نسبة امتلاء الحاوية، زمن معالجة الاستلام، نسبة الفاقد...</p>
            </div>
            <div class="paywall-lock">
                <div style="text-align:center;">
                    <h4 style="color:#C2410C;">🔒 هذا المحتوى للمشتركين فقط</h4>
                    <p style="font-size:0.9rem;color:#64748B;">اشترك في باقة Pro لقراءة الحلول الكاملة وتحميل النماذج.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══ 🚨 التنبيهات ═══
def show_alerts():
    st.markdown("<h2 style='font-weight:800;'>🚨 تنبيهات الميدان السريعة</h2>", unsafe_allow_html=True)
    alerts = [
        {"title": "ربطة سفن أب متضررة", "issue": "ربطة مفتوحة على منصة العرض.", "action": "سحب فوري واستبدال."},
        {"title": "نقص المياه", "issue": "فراغات في رفوف المياه.", "action": "إعادة التعبئة ومراقبة المخزون."},
        {"title": "بطء الإبلاغ", "issue": "انقطاع الإنترنت منع إرسال التقارير.", "action": "حفظ محلي وإرسال فوري."}
    ]
    for alert in alerts:
        st.markdown(f"""<div class="clean-card" style="border-right:4px solid #C2410C;">
            <h4 style="margin-top:0;">{alert['title']}</h4>
            <p style="margin:5px 0;"><b>المشكلة:</b> {alert['issue']}</p>
            <p style="margin:5px 0; color:#D97706;"><b>الإجراء:</b> {alert['action']}</p>
        </div>""", unsafe_allow_html=True)

# ═══ باقي الصفحات (السلة، الدفع، العمليات) ═══
def show_cart():
    st.markdown("<h2 style='font-weight:800;'>🛒 السلة</h2>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("السلة فارغة.")
        if st.button("تصفح المنتجات"): st.session_state.page="products"; st.rerun()
        return
    sub = 0
    for nm, d in st.session_state.cart.items():
        tt = d['price']*d['qty']; sub += tt
        c1,c2,c3,c4 = st.columns([4,2,2,1])
        with c1: st.write(f"**{nm}**")
        with c2: st.write(f"{d['price']:.2f} ر.س")
        with c3:
            nq = st.number_input("", min_value=1, value=d['qty'], key=f"cq_{nm}", label_visibility="collapsed")
            if nq != d['qty']: st.session_state.cart[nm]['qty']=nq; st.rerun()
        with c4:
            if st.button("🗑️", key=f"d_{nm}"): del st.session_state.cart[nm]; st.rerun()
    total = sub * 1.15
    st.markdown(f"<h3>الإجمالي: {total:.2f} ر.س</h3>", unsafe_allow_html=True)
    if st.button("متابعة الطلب", type="primary"): st.session_state.page="checkout"; st.rerun()

def show_checkout():
    st.markdown("<h2 style='font-weight:800;'>📝 تأكيد الطلب</h2>", unsafe_allow_html=True)
    st_total = sum(i['price']*i['qty'] for i in st.session_state.cart.values())
    total = st_total * 1.15
    with st.form("co"):
        nm = st.text_input("اسم المنشأة *")
        ph = st.text_input("الجوال *")
        lc = st.text_input("الموقع *")
        if st.form_submit_button("إرسال الطلب واتساب", type="primary"):
            if not nm or not ph or not lc: st.error("املأ الحقول.")
            else:
                oid = f"MRS-{int(time.time())}"
                items = "\n".join([f"- {k} ({v['qty']} × {v['price']} ر.س)" for k,v in st.session_state.cart.items()])
                wa = f"مرحباً، طلب جديد:\n📦 {oid}\n🏢 {nm}\n📱 {ph}\n📍 {lc}\n🛒 {items}\n💰 {total:.2f} ر.س"
                st.session_state.last_order = {"id":oid, "msg":wa}
                st.session_state.cart = {}
                st.session_state.page = "success"; st.rerun()

def show_success():
    o = st.session_state.last_order
    if not o: st.session_state.page="home"; st.rerun()
    url = f"https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={urllib.parse.quote(o['msg'])}"
    st.markdown(f"""<div class="clean-card" style="text-align:center;padding:40px;">
        <h2 style="color:#059669;">✓ تم تسجيل الطلب</h2>
        <a href="{url}" target="_blank" style="display:inline-block;background:#22C55E;color:#fff;padding:15px 30px;border-radius:8px;font-weight:bold;margin-top:20px;text-decoration:none;">📲 إرسال عبر واتساب</a>
    </div>""", unsafe_allow_html=True)
    if st.button("الرئيسية"): st.session_state.page="home"; st.rerun()

def show_operations():
    st.markdown("<h2 style='font-weight:800;'>⚙️ العمليات</h2>", unsafe_allow_html=True)
    if not st.session_state.ops_logged_in:
        pwd = st.text_input("رمز", type="password")
        if st.button("دخول"):
            if pwd in (OPS_PWD, ADMIN_PWD): st.session_state.ops_logged_in=True; st.rerun()
            else: st.error("خطأ")
        return
    if st.button("خروج"): st.session_state.ops_logged_in=False; st.rerun()
    st.write("سجل الطلبات هنا...")

def show_admin():
    st.markdown("<h2 style='font-weight:800;'>🛡️ الإدارة</h2>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if p == ADMIN_PWD: st.session_state.admin_logged_in=True; st.rerun()
            else: st.error("خطأ")
        return
    if st.button("خروج"): st.session_state.admin_logged_in=False; st.rerun()
    st.write("لوحة الإدارة هنا...")

def show_help():
    st.markdown("<h2 style='font-weight:800;'>📖 دليل التاجر</h2>", unsafe_allow_html=True)
    st.markdown("1. تصفح المنتجات.\n2. أضف للسلة.\n3. أكد الطلب.")

def show_terms():
    st.markdown("<h2 style='font-weight:800;'>📜 الشروط والأحكام</h2>", unsafe_allow_html=True)
    st.markdown("شروط مؤسسة مخلد محمد بن سليمان العنزي التجارية...")

def render_footer():
    st.markdown("<hr style='border-color:#E2E8F0;margin-top:50px;'>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns([3,2,2,2])
    with c1: st.markdown(f"<p style='color:#64748B;font-size:.8rem;'>© {datetime.now().year} {COMPANY_NAME}</p>", unsafe_allow_html=True)
    with c2:
        if st.button("📖 المساعدة", key="fh"): st.session_state.page="help"; st.rerun()
    with c3:
        if st.button("📜 الشروط", key="ft"): st.session_state.page="terms"; st.rerun()
    with c4:
        if st.button("⚙️ العمليات", key="fo"): st.session_state.page="ops"; st.rerun()

# ═══ الموجه الرئيسي ═══
def main():
    render_header()
    pages = {
        "home": show_home, "products": show_products, "cart": show_cart,
        "checkout": show_checkout, "success": show_success,
        "admin": show_admin, "ops": show_operations, "scanner": show_scanner,
        "library": show_library, "alerts": show_alerts,
        "help": show_help, "terms": show_terms
    }
    pages.get(st.session_state.page, show_home)()
    render_footer()

def show_scanner():
    st.markdown("<h2 style='font-weight:800;'>📷 مركز التوريد</h2>", unsafe_allow_html=True)
    img = st.camera_input("التقط صورة")
    if img:
        st.success("تم قراءة الصورة بنجاح!")

if __name__ == "__main__":
    main()
