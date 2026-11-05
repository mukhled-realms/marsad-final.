import streamlit as st
import pandas as pd
from pathlib import Path
import html
import re

st.set_page_config(page_title="مرصد | مشتريات أعمالك", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "Marsad_Valid_Products.csv"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; direction: rtl; }
.stApp { background: #F8FAFC; }
.marsad-header { background: #FFF; border: 1px solid #E8EDF2; border-radius: 18px; padding: 15px; margin-bottom: 24px; text-align: right; }
.brand { color: #123B2D; font-size: 27px; font-weight: 900; }
.hero { background: linear-gradient(120deg, #0F172A, #1E293B); color: white; padding: 35px; border-radius: 22px; margin-bottom: 25px; }
.hero h1 { font-size: 30px; font-weight: 900; margin: 0 0 8px 0; color: #EAB308; }
.category-card { background: #FFF; border: 1px solid #E5EBEF; border-radius: 18px; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.product-hidden-price { background: #F3F6F4; color: #557363; border-radius: 8px; padding: 7px; font-size: 12px; text-align: center; margin: 8px 0; }
div.stButton > button { background: #174B35; color: #FFF; border-radius: 11px; font-weight: 800; width: 100%; transition: 0.3s; }
div.stButton > button:hover { background: #236448; color: white; }
.invoice-total { background: #0F172A; color: #FFF; border-radius: 15px; padding: 20px; text-align: center; margin: 15px 0; }
.invoice-total strong { font-size: 27px; color: #EAB308; }
.price-anchor { background: #FEF3C7; border: 1px dashed #D97706; border-radius: 12px; padding: 15px; margin: 15px 0; text-align: center; }
.old-price { text-decoration: line-through; color: #EF4444; font-size: 18px; font-weight: bold; }
.new-price { color: #10B981; font-size: 28px; font-weight: 900; margin-right: 10px; }
.footer { text-align: center; color: #94A3B8; font-size: 12px; margin-top: 50px; padding-top: 20px; border-top: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_products():
    if not CSV_FILE.exists(): return pd.DataFrame()
    try: df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    except: return pd.DataFrame()
    df = df.rename(columns={"اسم المنتج": "name", "السعر": "price", "القطاع": "category", "ملاحظات": "notes", "الصورة": "image"})
    for col in ["name", "price", "category", "notes", "image"]:
        if col not in df.columns: df[col] = "" if col != "price" else 0
    df["name"] = df["name"].fillna("").astype(str).str.strip()
    df["price"] = pd.to_numeric(df["price"].astype(str).str.replace(",", "."), errors="coerce").fillna(0)
    def get_old_price(note, current_p):
        m = re.search(r"(?:السابق|قبل)\s*[:]?\s*(\d+(?:[.,]\d+)?)", str(note))
        if m:
            val = float(m.group(1).replace(",", "."))
            if val > current_p: return val
        return None
    df["old_price"] = df.apply(lambda row: get_old_price(row["notes"], row["price"]), axis=1)
    def normalize(c):
        c = str(c).lower()
        if "بقال" in c: return "بقالة"
        if "رقمي" in c or "بطاق" in c: return "بطاقة رقمية"
        return "أخرى"
    df["group"] = df["category"].apply(normalize)
    return df[(df["name"] != "") & (df["price"] > 0)].reset_index(drop=True)

products = load_products()
BUNDLES = {"باقة المقهى ☕": {"keywords": ["شاي", "سكر", "مياه", "حليب"], "desc": "كل احتياجات المقهى اليومية."}, "باقة النظافة 🧼": {"keywords": ["تايد", "كلور", "مناديل", "صابون"], "desc": "أساسيات النظافة للمطاعم والمقاهي."}}

if "screen" not in st.session_state: st.session_state.screen = "home"
if "category" not in st.session_state: st.session_state.category = "بقالة"
if "sel" not in st.session_state: st.session_state.sel = None
if "otp_ok" not in st.session_state: st.session_state.otp_ok = False

def go(s): st.session_state.screen = s; st.rerun()

st.markdown('<div class="marsad-header"><div class="brand">مرصد</div><p style="color:#7B8794; font-size:12px; margin:0;">مشتريات أعمالك، بوضوح أكبر</p></div>', unsafe_allow_html=True)

if st.session_state.screen == "home":
    st.markdown('<div class="hero"><h1>مشتريات أعمالك، بوضوح أكبر</h1><p style="color:#CBD5E1;">اختر القسم، أو اطلب باقة جاهزة توفر وقتك.</p></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 21px; font-weight: 900; margin-bottom: 15px;">الباقات الجاهزة (وفر وقتك)</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (b_name, b_data) in enumerate(BUNDLES.items()):
        with cols[i]:
            st.markdown(f'<div class="category-card"><h3 style="color:#0F172A;">{b_name}</h3><p style="color:#64748B; font-size:12px;">{b_data["desc"]}</p></div>', unsafe_allow_html=True)
            st.write("")
            if st.button(f"اطلب {b_name}", key=f"bundle_{b_name}"):
                st.session_state.category = b_name; go("products")
    st.markdown('<div style="font-size: 21px; font-weight: 900; margin: 30px 0 15px 0;">تصفح الأقسام</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, cat in zip(cols, ["بقالة", "بطاقة رقمية", "أخرى"]):
        with col:
            st.markdown(f'<div class="category-card"><h3 style="color:#0F172A;">{cat}</h3></div>', unsafe_allow_html=True)
            st.write("")
            if st.button("استعراض", key=f"c_{cat}"):
                st.session_state.category = cat; go("products")

elif st.session_state.screen == "products":
    if st.button("← العودة للرئيسية"): go("home")
    st.markdown(f"<h2 style='font-weight:900; color:#0F172A;'>{st.session_state.category}</h2>", unsafe_allow_html=True)
    if products.empty: st.error("⚠️ لا توجد منتجات.")
    else:
        if st.session_state.category in BUNDLES:
            keywords = BUNDLES[st.session_state.category]["keywords"]
            pattern = '|'.join(keywords)
            cat_df = products[products["name"].str.contains(pattern, na=False, case=False)]
            st.info("هذه الباقة تحتوي على أفضل المنتجات المختارة لك بضغطة زر.")
        else:
            cat_df = products[products["group"] == st.session_state.category]
        st.caption(f"عدد المنتجات: {len(cat_df)}")
        if len(cat_df) == 0: st.info("لا توجد منتجات.")
        else:
            for i in range(0, len(cat_df), 3):
                cols = st.columns(3)
                for col, (idx, row) in zip(cols, cat_df.iloc[i:i+3].iterrows()):
                    with col:
                        with st.container(border=True):
                            st.write(f"**{row['name']}**")
                            st.markdown('<div class="product-hidden-price">اعرف السعر بعد التحقق</div>', unsafe_allow_html=True)
                            if st.button("اطلب الآن", key=f"o_{idx}"):
                                st.session_state.sel = idx; st.session_state.otp_ok = False; go("verify")

elif st.session_state.screen == "verify":
    if st.button("← عودة"): go("products")
    st.markdown("<h2 style='font-weight:900;'>التحقق من الحساب</h2>", unsafe_allow_html=True)
    phone = st.text_input("رقم الجوال", placeholder="+9665XXXXXXXX")
    if not st.session_state.otp_ok:
        if st.button("إرسال رمز التحقق"):
            if re.fullmatch(r"\+9665\d{8}", phone.strip()): st.success("تم الإرسال. الرمز التجريبي هو 1234")
            else: st.error("أدخل رقم سعودي صحيح.")
        otp = st.text_input("رمز التحقق", type="password", max_chars=4)
        if st.button("تأكيد"):
            if otp == "1234": st.session_state.otp_ok = True; go("invoice")
            else: st.error("رمز خاطئ")
    else:
        if st.button("متابعة للفاتورة"): go("invoice")

elif st.session_state.screen == "invoice":
    if st.session_state.sel is None or not st.session_state.otp_ok: go("home")
    prod = products.iloc[st.session_state.sel]
    st.markdown("<h2 style='font-weight:900;'>ملخص الطلب</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#0F172A; font-weight:900;'>{prod['name']}</h3>", unsafe_allow_html=True)
    st.divider()
    qty = st.number_input("الكمية", min_value=1, value=1)
    unit_price = prod['price']
    subtotal = unit_price * qty; tax = subtotal * 0.15; total = subtotal + tax
    market_price = unit_price * 1.4 
    st.markdown(f'''
    <div class="price-anchor">
        <div style="font-size:14px; color:#92400E; margin-bottom:5px;">سعر السوق في التطبيقات:</div>
        <span class="old-price">{market_price:,.2f} ر.س</span>
        <span class="new-price">{unit_price:,.2f} ر.س</span>
        <div style="margin-top:10px; color:#D97706; font-weight:bold;">🏷️ مرصد وفّرت لك {market_price - unit_price:,.2f} ر.س!</div>
    </div>
    ''', unsafe_allow_html=True)
    st.write(f"سعر الوحدة: {unit_price} ر.س")
    st.write(f"الكمية: {qty}")
    st.write(f"الضريبة (15%): {tax:.2f} ر.س")
    st.markdown(f'<div class="invoice-total"><small>الإجمالي شامل الضريبة</small><br><strong>{total:.2f} ر.س</strong></div>', unsafe_allow_html=True)
    st.write("### طريقة الدفع")
    st.radio("اختر", ["دفع كامل", "عند الاستلام", "عربون 20%"])
    if st.button("تأكيد الطلب النهائي"):
        st.success("تم استلام طلبك بنجاح! 🎉")
        st.info("سيتواصل معك فريقنا قريباً لتجهيز الطلب.")
        if st.button("العودة للرئيسية"): st.session_state.screen = "home"; st.session_state.sel = None; st.rerun()

st.markdown("""
<div class="footer">
    <p><strong>مرصد</strong> - إحدى منصات مؤسسة مخلد محمد بن سليمان العنزي التجارية</p>
    <p>سجل تجاري: 1009005566 | الرقم الضريبي: 30056521610003</p>
</div>
""", unsafe_allow_html=True)
