# -*- coding: utf-8 -*-
"""منصة مرصد (Marsad) v3.9 — Final Release (Large Fingerprint)"""
import streamlit as st
import pandas as pd
import json, base64, urllib.parse, os, re, time
from datetime import datetime
import pytesseract
from PIL import Image
import requests

st.set_page_config(page_title="مرصد | مكتب مشتريات أعمالك", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

COMPANY_NAME = "مؤسسة مخلد محمد بن سليمان العنزي التجارية"
CR_NUMBER = "1009005566"
VAT_NUMBER = "30056521610003"
DEFAULT_WHATSAPP = "0592859590"
ADMIN_PWD = "marsad2026"
OPS_PWD = "marsad_ops_2026"
APP_BASE_URL = "https://marsad-store.streamlit.app"
BULK_DISCOUNT_THRESHOLD = 20
BULK_DISCOUNT_RATE = 0.05
TRUSTED_PARTNER_MIN_ORDERS = 3
NEIGHBORHOOD_NAME = "حي النظيم"
AI_DAILY_LIMIT = 15

try:
    WHATSAPP_NUMBER = st.secrets["WHATSAPP_NUMBER"]
except Exception:
    WHATSAPP_NUMBER = DEFAULT_WHATSAPP

# ═══ خلية النحل ═══
GEMINI_KEYS = []
try:
    raw = st.secrets.get("GEMINI_KEYS", [])
    if isinstance(raw, str):
        GEMINI_KEYS = [raw]
    elif isinstance(raw, (list, tuple)):
        GEMINI_KEYS = list(raw)
except Exception:
    pass

AI_MODELS = ["gemini-2.0-flash-exp", "gemini-1.5-flash-latest", "gemini-1.5-flash-002", "gemini-1.5-pro-latest"]
AI_ENABLED = len(GEMINI_KEYS) > 0

# ═══ الجلسة ═══
defaults = {
    "cart": {}, "sourcing_requests": [], "page": "home", "selected_cat": "الكل",
    "admin_logged_in": False, "ops_logged_in": False,
    "last_order": None, "orders_history": [], "last_cart": {},
    "product_order_dates": {}, "approval_loaded": False,
    "last_submission_time": 0, "ai_messages": [], "ai_questions_count": 0,
    "prefilled_ai_question": None, "calc_result": None, "last_click_times": {},
    "key_health": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══ الكتالوج ═══
@st.cache_data
def load_catalog():
    try:
        df = pd.read_csv("Marsad_Valid_Products.csv")
        for c in ["اسم المنتج", "السعر", "القطاع"]:
            if c not in df.columns: raise ValueError(f"مفقود: {c}")
        df["السعر"] = pd.to_numeric(df["السعر"], errors='coerce').fillna(0.0)
        if "ملاحظات" not in df.columns: df["ملاحظات"] = ""
        if "الوحدة" not in df.columns: df["الوحدة"] = "حبة"
        return df
    except Exception as e:
        st.error(f"خطأ: {e}")
        return pd.DataFrame(columns=["اسم المنتج","السعر","القطاع","ملاحظات","الوحدة"])

df_catalog = load_catalog()

CROSS_SELL_RULES = {
    "مياه بيرين (كرتون 24 × 330 مل)": ["سكر الأسرة الناعم (10 كيلو)", "شاي الكبوس أحمر (كرتون 100 كيس)"],
    "أرز الوليمة مزة (10 كيلو)": ["زيت عافية (1.5 لتر)", "معجون طماطم السعودية (8 × 135 جرام)"],
    "قهوة نسكافيه كلاسيك (200 جرام)": ["مبيض كوفي ميت (400 جرام)", "سكر الأسرة الناعم (10 كيلو)"],
    "شاي الكبوس أحمر (كرتون 100 كيس)": ["سكر الأسرة الناعم (10 كيلو)", "مياه بيرين (كرتون 24 × 330 مل)"],
}

# ═══ CSS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Tajawal',sans-serif;direction:rtl;text-align:right;background:#F8FAFC;color:#0F172A;}
#MainMenu,header,footer,.stDeployButton{visibility:hidden;}
div[data-testid="stToolbar"]{display:none !important;}
.clean-card{background:#FFF;border:1px solid #E2E8F0;border-radius:12px;padding:20px;transition:all .3s;box-shadow:0 4px 6px -1px rgba(0,0,0,.02);margin-bottom:15px;}
.clean-card:hover{border-color:#C2410C;box-shadow:0 12px 20px -8px rgba(194,65,12,.2);transform:translateY(-4px);}
.stButton>button{background:#0F172A !important;color:#FFF !important;border:none !important;border-radius:8px !important;padding:10px 20px !important;font-weight:700 !important;font-family:'Tajawal',sans-serif !important;transition:all .2s !important;width:100%;}
.stButton>button:hover{background:#C2410C !important;box-shadow:0 4px 12px rgba(194,65,12,.3) !important;}
.stTextInput input,.stSelectbox div[data-baseweb="select"],.stNumberInput input,.stTextArea textarea{background:#FFF !important;border:1px solid #CBD5E1 !important;color:#0F172A !important;border-radius:8px !important;}
h1,h2,h3,h4{font-family:'Tajawal',sans-serif !important;color:#0F172A;}
.bulk-banner{background:linear-gradient(135deg,#FEF3C7 0%,#FED7AA 100%);border-right:5px solid #C2410C;border-radius:10px;padding:15px;margin:15px 0;}
.predictive-banner{background:linear-gradient(135deg,#DBEAFE 0%,#BFDBFE 100%);border-right:5px solid #2563EB;border-radius:10px;padding:15px;margin:15px 0;}
.savings-banner{background:linear-gradient(135deg,#ECFDF5 0%,#D1FAE5 100%);border-right:5px solid #10B981;border-radius:10px;padding:15px;margin:15px 0;}
.trust-banner{background:linear-gradient(135deg,#F3E8FF 0%,#E9D5FF 100%);border-right:5px solid #9333EA;border-radius:10px;padding:15px;margin:15px 0;}
div[data-testid="stDialog"]>div{animation:slideIn .3s ease-out;}
@keyframes slideIn{from{opacity:0;transform:scale(.95) translateY(10px);}to{opacity:1;transform:scale(1) translateY(0);}}
</style>
""", unsafe_allow_html=True)

# ═══ دوال مساعدة ═══
def safe_click(key, cooldown=1.5):
    now = time.time()
    if now - st.session_state.last_click_times.get(key, 0) < cooldown: return False
    st.session_state.last_click_times[key] = now
    return True

def compute_bulk_discount(cart):
    tq = sum(i['qty'] for i in cart.values())
    return (BULK_DISCOUNT_RATE, tq) if tq >= BULK_DISCOUNT_THRESHOLD else (0, tq)

def is_trusted_partner():
    return len(st.session_state.orders_history) >= TRUSTED_PARTNER_MIN_ORDERS

def get_predictive_reminders():
    r = []
    for p, ds in st.session_state.product_order_dates.items():
        if len(ds) >= 2:
            iv = [(ds[i+1]-ds[i]).total_seconds()/86400 for i in range(len(ds)-1)]
            avg = sum(iv)/len(iv)
            since = (datetime.now()-ds[-1]).total_seconds()/86400
            if since >= avg*0.9: r.append({"product":p,"avg_days":round(avg,1),"days_ago":round(since,1)})
    return r

# ═══ 🐝 محرك خلية النحل ═══
def build_system_prompt():
    lines = []
    for _, row in df_catalog.head(50).iterrows():
        lines.append(f"- {row['اسم المنتج']} | {row['السعر']} ر.س | {row['القطاع']} | {row['الوحدة']}")
    catalog = "\n".join(lines)
    return f"""أنت "مساعد مرصد الذكي"، مستشار مشتريات في منصة مرصد السعودية.
شخصيتك: ودود، محلي بثقة، مختصر. تستخدم "طال عمرك"، "أبشر"، "يا هلا".
مهامك: الإجابة عن المنتجات، توجيه التاجر، اقتراح مكمل واحد فقط.
الكتالوج:
{catalog}
ممنوعات (لن تكشف): هوامش الربح، تكلفة الشراء، أسماء الموردين، أي أرقام داخلية، اسم أي منافس.
قواعد: إذا سُئلت عن محظور اعتذر بلطف. إذا لم تجد المنتج اقترح رفعه عبر "قارئ المنتجات". لا تتجاوز 80 كلمة."""

def call_gemini_single(key, model, prompt, system, timeout=15):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 400}
    }
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            return True, data["candidates"][0]["content"]["parts"][0]["text"].strip(), "200"
        return False, None, str(r.status_code)
    except Exception as e:
        return False, None, f"EXC:{str(e)[:25]}"

def resilient_ai_generate(user_question):
    if not AI_ENABLED:
        return False, "المساعد غير متاح حالياً. تواصل مع الدعم: " + WHATSAPP_NUMBER, None
    system = build_system_prompt()
    attempts = 0
    dead_keys = set()
    for key_idx, key in enumerate(GEMINI_KEYS):
        if key_idx in dead_keys: continue
        for model in AI_MODELS:
            attempts += 1
            ok, text, status = call_gemini_single(key, model, user_question, system)
            if ok:
                st.session_state.key_health[key_idx] = {"status":"ok","model":model,"at":datetime.now().isoformat()}
                return True, text, {"key_idx":key_idx, "model":model, "attempts":attempts}
            if status == "401":
                st.session_state.key_health[key_idx] = {"status":"dead","at":datetime.now().isoformat()}
                dead_keys.add(key_idx); break
            elif status == "429":
                st.session_state.key_health[key_idx] = {"status":"quota","at":datetime.now().isoformat()}
                break
            elif status == "403":
                st.session_state.key_health[key_idx] = {"status":"restricted","at":datetime.now().isoformat()}
                break
            else:
                continue
    return False, "المساعد مشغول حالياً يا طال عمرك، جرب بعد دقيقة 🙏", {"attempts":attempts, "all_failed":True}

# ═══ 🤖 نافذة المساعد ═══
@st.dialog("💬 مساعد مرصد الذكي", width="large")
def ai_chat_modal():
    if not AI_ENABLED:
        st.error("⚠️ المساعد غير متاح حالياً. تواصل مع الدعم: " + WHATSAPP_NUMBER)
        return
    st.markdown(f"<p style='color:#64748B;font-size:0.85rem;'>💡 أسئلتك اليوم: {st.session_state.ai_questions_count}/{AI_DAILY_LIMIT} | لن أكشف أي معلومات داخلية.</p>", unsafe_allow_html=True)
    if st.session_state.ai_questions_count >= AI_DAILY_LIMIT:
        st.warning(f"وصلت للحد اليومي ({AI_DAILY_LIMIT} سؤال). تصفح المنتجات مباشرة.")
        if st.button("🗑️ إعادة تعيين (تجريبي)"):
            st.session_state.ai_questions_count = 0; st.rerun()
        return
    if not st.session_state.ai_messages:
        st.markdown("""<div style="background:#F0FDF4;border-right:4px solid #22C55E;padding:12px;border-radius:8px;margin-bottom:15px;">
            <p style="margin:0;color:#166534;">أهلاً يا طال عمرك! 👋 أنا مساعدك في مرصد. اسألني عن أي منتج، سعر، أو نصيحة.</p>
        </div>""", unsafe_allow_html=True)
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💼" if msg["role"]=="user" else "🛡️"):
            st.markdown(msg["content"])
    user_input = st.chat_input("اكتب سؤالك هنا...")
    if st.session_state.prefilled_ai_question and not user_input:
        user_input = st.session_state.prefilled_ai_question
        st.session_state.prefilled_ai_question = None
    if user_input:
        st.session_state.ai_messages.append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("أفكر..."):
                ok, answer, meta = resilient_ai_generate(user_input)
                if ok:
                    st.markdown(answer)
                    st.session_state.ai_messages.append({"role":"assistant","content":answer})
                    st.session_state.ai_questions_count += 1
                else:
                    st.warning(answer)

# ═══ 🧮 حاسبة التسعير ═══
def show_pricing_calculator():
    st.markdown("<h2 style='font-weight:800;'>🧮 حاسبة التسعير الذكية</h2>", unsafe_allow_html=True)
    st.markdown("""<div class="clean-card" style="background:linear-gradient(135deg,#F0F9FF,#E0F2FE);border-color:#38BDF8;">
        <p style="margin:0;color:#075985;line-height:1.7;"><b>💡 مجانية 100%</b> — احسب السعر المثالي. <b>خصوصية:</b> كل الحسابات في جوالك.</p>
    </div>""", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        pname = st.text_input("1️⃣ اسم المنتج النهائي", placeholder="كوب قهوة لاتيه")
        ing = st.number_input("2️⃣ تكلفة المكونات (ر.س)", min_value=0.0, value=2.0, step=0.5)
        opr = st.number_input("3️⃣ مصاريف التشغيل (ر.س)", min_value=0.0, value=1.0, step=0.5)
    with c2:
        cur = st.number_input("4️⃣ سعر البيع الحالي (ر.س)", min_value=0.0, value=15.0, step=1.0)
        target = st.selectbox("5️⃣ هامش الربح المستهدف", ["منخفض (20%)", "متوازن (40%)", "عالي (60%+)"])
    if st.button("🧮 احسب", type="primary"):
        if not pname: st.error("أدخل اسم المنتج")
        else:
            cost = ing + opr
            m = {"منخفض (20%)":0.20, "متوازن (40%)":0.40, "عالي (60%+)":0.60}[target]
            sugg = cost / (1 - m) if m < 1 else cost * 2
            profit = sugg - cost
            margin_actual = (profit/sugg)*100 if sugg > 0 else 0
            st.session_state.calc_result = {"product":pname,"cost":cost,"suggested":sugg,"profit":profit,"margin":margin_actual,"current":cur,"target":target}
    if st.session_state.calc_result:
        r = st.session_state.calc_result
        st.markdown("---")
        st.markdown("### 📊 النتيجة:")
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("التكلفة", f"{r['cost']:.2f} ر.س")
        with c2: st.metric("السعر المقترح", f"{r['suggested']:.2f} ر.س", delta=f"{r['suggested']-r['current']:.2f}")
        with c3: st.metric("ربحك الصافي", f"{r['profit']:.2f} ر.س", delta=f"{r['margin']:.1f}%")
        if AI_ENABLED:
            if st.button("💬 اسأل مساعد مرصد: هل السعر منافس؟"):
                st.session_state.prefilled_ai_question = f"حسبت تكاليف '{r['product']}' بسعر مقترح {r['suggested']:.2f} ر.س. هل هذا السعر منافس في حي النظيم؟"
                ai_chat_modal()

# ═══ الهيدر ═══
def render_header():
    cc = sum(i['qty'] for i in st.session_state.cart.values())
    c1,c2,c3,c4,c5,c6 = st.columns([3,2,2,2,2,1])
    with c1:
        st.markdown("""<div style="display:flex;align-items:center;gap:10px;">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                <circle cx="18" cy="18" r="16" fill="#0F172A"/>
                <path d="M11 18L15 22L25 12" stroke="#C2410C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div><h2 style="margin:0;font-size:1.5rem;font-weight:900;">مَـرْصَــد <span style="color:#C2410C;">.</span></h2>
            <span style="font-size:0.75rem;color:#64748B;">مكتب مشتريات أعمالك</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if st.button("🏠 الرئيسية", key="nh"): st.session_state.page="home"; st.rerun()
    with c3:
        if st.button("📦 المنتجات", key="np"): st.session_state.page="products"; st.rerun()
    with c4:
        if st.button("📷 القارئ", key="ns"): st.session_state.page="scanner"; st.rerun()
    with c5:
        if st.button("🧮 الحاسبة", key="nc"): st.session_state.page="calculator"; st.rerun()
    with c6:
        if st.button(f"🛒 ({cc})" if cc>0 else "🛒", key="ncart"): st.session_state.page="cart"; st.rerun()
    cai1, cai2 = st.columns([8,2])
    with cai2:
        if AI_ENABLED:
            if st.button("💬 مساعد مرصد", key="hai"): ai_chat_modal()
        else:
            st.button("💬 المساعد (غير متاح)", disabled=True)
    st.markdown("<hr style='border-color:#E2E8F0;margin-top:15px;margin-bottom:25px;'>", unsafe_allow_html=True)

# ═══ الرئيسية ═══
def show_home():
    st.markdown("""<div class="clean-card" style="padding:40px;background:linear-gradient(135deg,#0F172A,#1E293B);color:white;border-radius:16px;margin-bottom:30px;">
        <span style="background:rgba(194,65,12,.2);color:#F97316;padding:6px 14px;border-radius:20px;font-size:.85rem;font-weight:700;">مكتب مشتريات رقمي متكامل</span>
        <h1 style="color:white;font-size:2.5rem;margin-top:15px;margin-bottom:15px;">لا نبيع كرتون، نختصر رحلة مشتريات منشأتك.</h1>
        <p style="color:#94A3B8;font-size:1.1rem;">أرسل احتياجك، نتحقق من السعر والتوفر، تعتمد العرض، ونتولى الباقي حتى باب منشأتك.</p>
    </div>""", unsafe_allow_html=True)
    for rem in get_predictive_reminders()[:2]:
        st.markdown(f"""<div class="predictive-banner">
            <h4 style="color:#1E40AF;margin:0;">🔔 تذكير: {rem['product']}</h4>
            <p style="color:#1E3A8A;margin:5px 0 0 0;font-size:.9rem;">آخر طلب قبل {rem['days_ago']} يوم.</p>
        </div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("🚀 تصفح المنتجات", key="hb"): st.session_state.page="products"; st.rerun()
    with c2:
        if st.button("🧮 حاسبة التسعير", key="hc"): st.session_state.page="calculator"; st.rerun()
    with c3:
        if st.session_state.last_cart and st.button("🔄 إعادة آخر سلة", key="hr"):
            st.session_state.cart = dict(st.session_state.last_cart); st.rerun()

# ═══ المنتجات (v3.9 - البصمة الكبيرة) ═══
def show_products():
    st.markdown("<h2 style='font-weight:800;margin-bottom:20px;'>📦 كتالوج المنتجات</h2>", unsafe_allow_html=True)
    cats = ["الكل"] + list(df_catalog["القطاع"].unique())
    c1,c2 = st.columns([2,1])
    with c1: q = st.text_input("🔍 بحث...", placeholder="اسم المنتج...")
    with c2: sel = st.selectbox("القطاع", cats)
    df = df_catalog.copy()
    if sel != "الكل": df = df[df["القطاع"]==sel]
    if q: df = df[df["اسم المنتج"].str.contains(q, case=False, na=False)]
    st.write(f"عرض **{len(df)}** منتج")
    st.write("---")
    
    cols = st.columns(3)
    for idx, row in df.reset_index(drop=True).iterrows():
        with cols[idx % 3]:
            name, price, cat = row["اسم المنتج"], float(row["السعر"]), row["القطاع"]
            notes = str(row["ملاحظات"]) if pd.notna(row["ملاحظات"]) else ""
            unit = row.get("الوحدة","حبة")
            old = None
            m = re.search(r'(\d+\.?\d*)', notes)
            if m: old = float(m.group(1))
            
            st.markdown(f"""<div class="clean-card" style="margin-bottom:0;border-bottom-left-radius:0;border-bottom-right-radius:0;">
                <span style="background:#FEF3C7;color:#92400E;font-size:.75rem;padding:2px 8px;border-radius:6px;">{cat}</span>
                <h4 style="margin-top:10px;margin-bottom:5px;font-size:1.1rem;">{name}</h4>
                <p style="color:#64748B;font-size:.8rem;margin-bottom:10px;">الوحدة: {unit}</p>
                <div style="display:flex;align-items:baseline;gap:10px;">
                    <span style="font-size:1.4rem;font-weight:900;color:#0F172A;">{price:.2f} ر.س</span>
                    {f'<span style="text-decoration:line-through;color:#EF4444;font-size:.9rem;">{old:.2f}</span>' if old else ''}
                </div>
            </div>""", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("<div style='background:#FFF;border:1px solid #E2E8F0;border-top:none;border-bottom-left-radius:12px;border-bottom-right-radius:12px;padding:15px;margin-top:-15px;margin-bottom:15px;'>", unsafe_allow_html=True)
                qty = st.number_input("الكمية", min_value=1, value=1, key=f"q_{idx}", label_visibility="collapsed")
                if st.button("🛒 اطلب الآن", key=f"a_{idx}", type="primary"):
                    if safe_click(f"a_{idx}"):
                        cq = st.session_state.cart.get(name,{}).get('qty',0)
                        st.session_state.cart[name] = {"price":price,"qty":cq+qty,"unit":unit,"category":cat}
                        st.toast(f"✓ {qty} × {name}", icon="✅"); st.rerun()
                
                # --- البصمة التفاعلية الكبيرة (توصية جيمناي) ---
                with st.expander("🫆 حاسبة الأرباح السريعة", expanded=False):
                    st.markdown("""
                        <div style="text-align: center; margin-bottom: 15px;">
                            <svg width="70" height="70" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#C2410C"/>
                                <path d="M12 6C9.24 6 7 8.24 7 11V13C7 13.55 6.55 14 6 14C5.45 14 5 13.55 5 13V11C5 7.13 8.13 4 12 4C15.87 4 19 7.13 19 11V16C19 16.55 18.55 17 18 17C17.45 17 17 16.55 17 16V11C17 8.24 14.76 6 12 6Z" fill="#C2410C"/>
                                <path d="M12 8C10.34 8 9 9.34 9 11V15C9 15.55 8.55 16 8 16C7.45 16 7 15.55 7 15V11C7 8.24 9.24 6 12 6C14.76 6 17 8.24 17 11V18C17 18.55 16.55 19 16 19C15.45 19 15 18.55 15 18V11C15 9.34 13.66 8 12 8Z" fill="#C2410C"/>
                                <path d="M12 10C11.45 10 11 10.45 11 11V16C11 16.55 11.45 17 12 17C12.55 17 13 16.55 13 16V11C13 10.45 12.55 10 12 10Z" fill="#C2410C"/>
                            </svg>
                            <p style="color:#C2410C; font-weight:900; font-size:1rem; margin:5px 0 0 0;">بصمة حساب الربح</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    quick_margin = st.radio("اختر هامش سريع:", ["يدوي", "+20%", "+30%", "+50%"], horizontal=True, key=f"m_{idx}", label_visibility="collapsed")
                    
                    default_sell = 0.0
                    if quick_margin == "+20%": default_sell = round(price * 1.2, 2)
                    elif quick_margin == "+30%": default_sell = round(price * 1.3, 2)
                    elif quick_margin == "+50%": default_sell = round(price * 1.5, 2)
                    
                    sell_price = st.number_input("سعر البيع للعميل (ر.س)", min_value=0.0, value=default_sell if default_sell > 0 else price, step=0.5, key=f"sell_{idx}")
                    
                    if sell_price > 0:
                        profit = sell_price - price
                        margin = (profit / sell_price) * 100 if sell_price > 0 else 0
                        color = "#059669" if profit > 0 else "#EF4444"
                        st.markdown(f"<div style='background:#ECFDF5;padding:10px;border-radius:8px;text-align:center;border:1px solid #10B981;'><span style='color:{color};font-weight:bold;font-size:1.1rem;'>ربحك الصافي: {profit:.2f} ر.س ({margin:.1f}%)</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# ═══ قارئ المنتجات ═══
def show_scanner():
    st.markdown("<h2 style='font-weight:800;'>📷 مركز التوريد</h2>", unsafe_allow_html=True)
    st.markdown("""<div class="clean-card" style="background:linear-gradient(135deg,#F0F9FF,#E0F2FE);border-color:#38BDF8;">
        <p style="margin:0;color:#075985;line-height:1.7;">صور منتجاتك، ارفع صورها، أو اكتبها. <b>حماية:</b> 30 ثانية بين كل طلب.</p>
    </div>""", unsafe_allow_html=True)
    def can_sub():
        if time.time() - st.session_state.last_submission_time < 30:
            st.warning(f"⏳ انتظر {int(30-(time.time()-st.session_state.last_submission_time))} ثانية")
            return False
        return True
    t1,t2,t3 = st.tabs(["📷 كاميرا","📤 رفع","📝 إدخال"])
    with t1:
        st.markdown("""<div style="background:#ECFDF5;border-right:4px solid #10B981;padding:12px;border-radius:8px;margin-bottom:15px;">
            <p style="margin:0;color:#065F46;font-size:.85rem;">🛡️ الكاميرا تقرأ النص فقط. لا نحفظ صورتك.</p>
        </div>""", unsafe_allow_html=True)
        img = st.camera_input("التقط صورة")
        if img:
            im = Image.open(img)
            with st.spinner("🔄 يقرأ..."):
                try:
                    txt = pytesseract.image_to_string(im, lang='ara+eng')
                    for ln in [l.strip() for l in txt.split('\n') if l.strip()]:
                        pm = re.search(r'(\d+[\.,]?\d*)', ln)
                        if pm:
                            pr = float(pm.group(1).replace(',','.'))
                            nm = re.sub(r'\d+[\.,]?\d*','',ln).strip()
                            nm = re.sub(r'[^\u0600-\u06FF\w\s\(\)\-]','',nm).strip()
                            if nm and len(nm) > 2:
                                mt = df_catalog[df_catalog["اسم المنتج"].str.contains(nm[:5], case=False, na=False)]
                                if not mt.empty:
                                    off = mt.iloc[0]
                                    st.success(f"✅ متوفر: **{off['اسم المنتج']}** ({off['السعر']} ر.س)")
                                    if st.button(f"أضف", key=f"o_{nm}"):
                                        cq = st.session_state.cart.get(off['اسم المنتج'],{}).get('qty',0)
                                        st.session_state.cart[off['اسم المنتج']] = {"price":float(off['السعر']),"qty":cq+1,"unit":off['الوحدة'],"category":off['القطاع']}
                                        st.toast("✓", icon="✅"); st.rerun()
                                else:
                                    st.warning(f"⚠️ غير متوفر: **{nm}**")
                                    if st.button("📡 سجل احتياجك", key=f"r_{nm}"):
                                        if can_sub():
                                            st.session_state.sourcing_requests.append({"name":nm,"notes":"من الكاميرا"})
                                            st.session_state.last_submission_time = time.time()
                                            st.toast("✓ في الرادار", icon="✅"); st.rerun()
                except Exception as e: st.error(f"خطأ: {e}")
    with t2:
        fs = st.file_uploader("ارفع صوراً", type=["jpg","jpeg","png"], accept_multiple_files=True)
        if fs:
            st.success(f"✓ {len(fs)} صورة")
            nt = st.text_area("تفاصيل (اختياري):")
            if st.button("🚀 إرسال"):
                if can_sub():
                    imgs = [f.read() for f in fs]
                    st.session_state.sourcing_requests.append({"name":nt or f"طلب ({len(fs)} صور)","notes":"مرفق","images":imgs})
                    st.session_state.last_submission_time = time.time()
                    st.toast("✓", icon="✅"); st.rerun()
    with t3:
        with st.form("m"):
            nm = st.text_input("اسم المنتج *")
            nt = st.text_area("تفاصيل")
            if st.form_submit_button("إضافة"):
                if nm and can_sub():
                    st.session_state.sourcing_requests.append({"name":nm,"notes":nt})
                    st.session_state.last_submission_time = time.time()
                    st.toast("✓", icon="✅"); st.rerun()

# ═══ السلة ═══
def show_cart():
    st.markdown("<h2 style='font-weight:800;'>🛒 السلة</h2>", unsafe_allow_html=True)
    if not st.session_state.cart and not st.session_state.sourcing_requests:
        st.info("السلة فارغة.")
        c1,c2 = st.columns(2)
        with c1:
            if st.session_state.last_cart and st.button("🔄 إعادة آخر سلة"):
                st.session_state.cart = dict(st.session_state.last_cart); st.rerun()
        with c2:
            if st.button("تصفح"): st.session_state.page="products"; st.rerun()
        return
    sub, sav, td = 0, 0, []
    for nm, d in st.session_state.cart.items():
        tt = d['price']*d['qty']; sub += tt
        pr = df_catalog[df_catalog["اسم المنتج"]==nm]
        if not pr.empty:
            mt = re.search(r'(\d+\.?\d*)', str(pr.iloc[0]["ملاحظات"]))
            if mt and float(mt.group(1)) > d['price']: sav += (float(mt.group(1))-d['price'])*d['qty']
        c1,c2,c3,c4 = st.columns([4,2,2,1])
        with c1: st.write(f"**{nm}** ({d['unit']})")
        with c2: st.write(f"{d['price']:.2f} ر.س")
        with c3:
            nq = st.number_input("", min_value=1, value=d['qty'], key=f"cq_{nm}", label_visibility="collapsed")
            if nq != d['qty']: st.session_state.cart[nm]['qty']=nq; st.rerun()
        with c4:
            if st.button("🗑️", key=f"d_{nm}"): td.append(nm)
    for k in td: del st.session_state.cart[k]
    if td: st.rerun()
    if st.session_state.sourcing_requests:
        st.markdown("### 📡 طلبات توريد:")
        for i, req in enumerate(st.session_state.sourcing_requests):
            c1,c2 = st.columns([8,2])
            with c1: st.markdown(f"<b style='color:#C2410C;'>⚠️ {req['name']}</b>", unsafe_allow_html=True)
            with c2:
                if st.button("🗑️", key=f"dr_{i}"): st.session_state.sourcing_requests.pop(i); st.rerun()
    dr, tq = compute_bulk_discount(st.session_state.cart)
    if dr > 0: st.markdown(f"""<div class="bulk-banner"><h4 style="color:#9A3412;margin:0;">🔥 خصم جماعي (5%)!</h4></div>""", unsafe_allow_html=True)
    if sav > 0: st.markdown(f"""<div class="savings-banner"><h4 style="color:#065F46;margin:0;">🎉 وفّرت {sav:.2f} ر.س!</h4></div>""", unsafe_allow_html=True)
    st.write("---")
    da = sub*dr; sa = sub-da; vat = sa*0.15; total = sa+vat
    st.markdown(f"""<div class="clean-card">
        <p>المجموع: <b>{sub:.2f} ر.س</b></p>
        {f'<p style="color:#059669;">خصم: <b>-{da:.2f}</b></p>' if da>0 else ''}
        <p>الضريبة: <b>{vat:.2f} ر.س</b></p>
        <h3 style="color:#C2410C;">الإجمالي: {total:.2f} ر.س</h3>
    </div>""", unsafe_allow_html=True)
    if st.button("✅ متابعة الطلب", type="primary"): st.session_state.page="checkout"; st.rerun()

# ═══ الدفع ═══
def show_checkout():
    st.markdown("<h2 style='font-weight:800;'>📝 تأكيد الطلب</h2>", unsafe_allow_html=True)
    st_total = sum(i['price']*i['qty'] for i in st.session_state.cart.values())
    dr, _ = compute_bulk_discount(st.session_state.cart)
    total = (st_total - st_total*dr)*1.15
    opts = ["الدفع عند الاستلام","تحويل بنكي","عربون 20%"]
    if is_trusted_partner(): opts.append("⭐ شريك موثوق (48h)")
    with st.form("co"):
        nm = st.text_input("اسم المنشأة *")
        ph = st.text_input("الجوال *")
        lc = st.text_input("الموقع *")
        otp = st.text_input("رمز التحقق (1234) *")
        pm = st.selectbox("طريقة الدفع", opts)
        if st.form_submit_button("تأكيد وإرسال واتساب", type="primary"):
            if not nm or not ph or not lc or otp != "1234":
                st.error("املأ الحقول. OTP=1234")
            else:
                oid = f"MRS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                items = "\n".join([f"- {k} ({v['qty']} × {v['price']} ر.س)" for k,v in st.session_state.cart.items()])
                src = ""
                if st.session_state.sourcing_requests:
                    src = "\n\n⚠️ طلبات توريد:\n" + "\n".join([f"- {r['name']}" for r in st.session_state.sourcing_requests])
                wa = f"""مرحباً مرصد، طلب:
📦 {oid}
🏢 {nm}
📱 {ph}
📍 {lc}
💳 {pm}
🛒 {items}
💰 {total:.2f} ر.س{src}"""
                now = datetime.now()
                for it in st.session_state.cart: st.session_state.product_order_dates.setdefault(it,[]).append(now)
                st.session_state.last_cart = dict(st.session_state.cart)
                st.session_state.last_order = {"id":oid,"msg":wa,"total":total,"name":nm,"payment":pm}
                st.session_state.orders_history.append(st.session_state.last_order)
                st.session_state.cart = {}; st.session_state.sourcing_requests = []
                st.session_state.page = "success"; st.rerun()

def show_success():
    o = st.session_state.last_order
    if not o: st.session_state.page="home"; st.rerun()
    url = f"https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={urllib.parse.quote(o['msg'])}"
    st.markdown(f"""<div class="clean-card" style="text-align:center;padding:40px;">
        <h2 style="color:#059669;">✓ تم تسجيل الطلب</h2>
        <p>رقم: <b>{o['id']}</b> | إجمالي: <b>{o['total']:.2f} ر.س</b></p>
        <a href="{url}" target="_blank" style="display:inline-block;background:#22C55E;color:#fff;padding:15px 30px;border-radius:8px;font-weight:bold;margin-top:20px;text-decoration:none;">📲 إرسال عبر واتساب</a>
    </div>""", unsafe_allow_html=True)
    if st.button("الرئيسية"): st.session_state.page="home"; st.rerun()

# ═══ العمليات ═══
def show_operations():
    st.markdown("<h2 style='font-weight:800;'>⚙️ غرفة العمليات</h2>", unsafe_allow_html=True)
    if not st.session_state.ops_logged_in:
        pwd = st.text_input("رمز", type="password", key="op")
        if st.button("دخول"):
            if pwd in (OPS_PWD, ADMIN_PWD): st.session_state.ops_logged_in=True; st.rerun()
            else: st.error("خطأ")
        return
    if st.button("خروج"): st.session_state.ops_logged_in=False; st.rerun()
    tabs = st.tabs(["📦 الطلبات","📡 الرادار","📊 التحليلات","🐝 صحة المفاتيح"])
    with tabs[0]:
        if st.session_state.orders_history:
            df = pd.DataFrame([{"الرقم":o["id"],"المنشأة":o["name"],"الإجمالي":o["total"],"الدفع":o.get("payment","-")} for o in st.session_state.orders_history])
            st.dataframe(df, use_container_width=True)
        else: st.info("لا طلبات")
    with tabs[1]:
        if st.session_state.sourcing_requests:
            from collections import Counter
            cnt = Counter([r['name'] for r in st.session_state.sourcing_requests])
            df = pd.DataFrame([{"المنتج":n,"الطلب":c} for n,c in cnt.items()]).sort_values("الطلب", ascending=False)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 CSV", csv, "radar.csv", "text/csv")
            st.dataframe(df, use_container_width=True)
            sel = st.selectbox("اختر:", list(cnt.keys()))
            if st.button(f"📲 إشعار: {sel}"):
                msg = f"مرحباً، وفرنا ({sel}). اطلبه الآن!"
                st.markdown(f'<a href="https://wa.me/?text={urllib.parse.quote(msg)}" target="_blank" style="background:#25D366;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;">📲 واتساب</a>', unsafe_allow_html=True)
        else: st.info("الرادار فارغ")
    with tabs[2]:
        if st.session_state.orders_history:
            df = pd.DataFrame(st.session_state.orders_history)
            c1,c2,c3 = st.columns(3)
            with c1: st.metric("الإيرادات", f"{df['total'].sum():.2f} ر.س")
            with c2: st.metric("الطلبات", len(df))
            with c3: st.metric("متوسط السلة", f"{df['total'].mean():.2f} ر.س")
        else: st.info("لا بيانات")
    with tabs[3]:
        st.markdown(f"### 🐝 حالة خلية النحل ({len(GEMINI_KEYS)} مفتاح)")
        if st.session_state.key_health:
            for idx, h in st.session_state.key_health.items():
                icon = "✅" if h["status"]=="ok" else "⏳" if h["status"]=="quota" else "❌" if h["status"]=="dead" else "🚫"
                st.write(f"- المفتاح #{idx+1}: {icon} {h['status']} {h.get('model','')}")
        else:
            st.info("لم يُستخدم المساعد بعد.")

# ═══ الإدارة ═══
def show_admin():
    st.markdown("<h2 style='font-weight:800;'>🛡️ الإدارة</h2>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if p == ADMIN_PWD: st.session_state.admin_logged_in=True; st.rerun()
            else: st.error("خطأ")
        return
    if st.button("خروج"): st.session_state.admin_logged_in=False; st.rerun()
    for o in reversed(st.session_state.orders_history):
        st.write(f"- {o['id']} | {o['name']} | {o['total']} ر.س")

# ═══ المساعدة والشروط ═══
def show_help():
    st.markdown("<h2 style='font-weight:800;'>📖 دليل التاجر</h2>", unsafe_allow_html=True)
    with st.expander("كيف تبدأ؟", expanded=True):
        st.markdown("1. تصفح → 2. أضف للسلة → 3. أكد بـ OTP: 1234")
    with st.expander("الأزرار"):
        st.markdown("🏠 الرئيسية | 📦 المنتجات | 📷 القارئ | 🧮 الحاسبة | 💬 المساعد | 🛒 السلة")
    with st.expander("المميزات"):
        st.markdown("مرساة سعرية، حاسبة ربح، خصم جماعي 5%، رادار سوق، مساعد AI")
    with st.expander("خطط الاشتراك"):
        st.markdown("الآن: مجاني 100% | لاحقاً: مجاني + احترافي 29 ر.س/شهر")
    with st.expander("الخصوصية"):
        st.markdown("وفق نظام PDPL السعودي. لا نحفظ صور الكاميرا.")
    with st.expander("التواصل"):
        st.markdown(f"واتساب: {WHATSAPP_NUMBER} | بريد: mkhld0336@gmail.com")

def show_terms():
    st.markdown("<h2 style='font-weight:800;'>📜 الشروط والأحكام</h2>", unsafe_allow_html=True)
    st.markdown("""
### 1. المقدمة
اتفاقية ملزمة بين مؤسسة مخلد محمد بن سليمان العنزي التجارية والمستخدم.

### 2. القبول
الدخول أو الطلب = موافقة كاملة.

### 3. تسجيل الحساب
بيانات صحيحة، العمر 18+، تراخيص نظامية.

### 4. مسؤوليات التاجر
سداد الطلبات، عدم إساءة الاستخدام، مراجعة الفواتير.

### 5. مسؤوليات المنصة
خدمة سريعة ودقيقة، شفافية أسعار، حماية بيانات (PDPL).

### 6. الأسعار والدفع
بالريال + ضريبة 15%. تحويل/عند الاستلام/ائتمان للشركاء.

### 7. التوصيل
الرياض - النظيم والمناطق المجاورة.

### 8. الإرجاع
يحق الإرجاع للتالف فوراً. لا إرجاع للمواد الغذائية المفتوحة.

### 9. الملكية الفكرية
كل حقوق المنصة ملك حصري للمؤسسة.

### 10. حدود المسؤولية
لا نتحمل أضراراً غير مباشرة أو أرباحاً فائتة.

### 11. التعديل
يحق لنا التعديل. الاستمرار = موافقة.

### 12. الاختصاص القضائي
الأنظمة السعودية — محاكم الرياض.

### 13. التواصل
س.ت: 1009005566 | ر.ض: 30056521610003 | 0592859590
    """)

# ═══ الفوتر ═══
def render_footer():
    st.markdown("<hr style='border-color:#E2E8F0;margin-top:50px;'>", unsafe_allow_html=True)
    st.markdown("""<div style="text-align:center;margin-bottom:20px;">
        <span style="background:#F1F5F9;color:#475569;padding:6px 15px;border-radius:20px;font-size:.8rem;">🔒 اتصال آمن | 🛡️ لا نجمع بياناتك | ✅ منصة موثوقة</span>
    </div>""", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns([3,2,2,2,2])
    with c1: st.markdown(f"<p style='color:#64748B;font-size:.8rem;'>© {datetime.now().year} {COMPANY_NAME}</p>", unsafe_allow_html=True)
    with c2:
        if st.button("📖 المساعدة", key="fh"): st.session_state.page="help"; st.rerun()
    with c3:
        if st.button("📜 الشروط", key="ft"): st.session_state.page="terms"; st.rerun()
    with c4:
        if st.button("⚙️ العمليات", key="fo"): st.session_state.page="ops"; st.rerun()
    with c5:
        if st.button("🔒 الإدارة", key="fa"): st.session_state.page="admin"; st.rerun()

def handle_approval():
    if st.session_state.approval_loaded: return
    try:
        token = st.query_params.get("approve")
        if token:
            cart_json = base64.urlsafe_b64decode(token.encode()).decode()
            st.session_state.cart = json.loads(cart_json)
            st.session_state.approval_loaded = True
            st.session_state.page = "cart"
            st.query_params.clear()
    except Exception: pass

def main():
    handle_approval()
    render_header()
    pages = {"home":show_home,"products":show_products,"cart":show_cart,"checkout":show_checkout,
             "success":show_success,"admin":show_admin,"ops":show_operations,"scanner":show_scanner,
             "help":show_help,"terms":show_terms,"calculator":show_pricing_calculator}
    pages.get(st.session_state.page, show_home)()
    render_footer()

if __name__ == "__main__":
    main()
