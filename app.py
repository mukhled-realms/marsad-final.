# -*- coding: utf-8 -*-
"""
منصة مرصد (Marsad) - النسخة المبتكرة v2.5 (الصاروخية)
مكتب مشتريات أعمالك الخارجي
المؤسسة: مؤسسة مخلد محمد بن سليمان العنزي التجارية
"""
import streamlit as st
import pandas as pd
import json
import urllib.parse
import os
import re
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والهوية
# ==========================================
st.set_page_config(
    page_title="مرصد | مكتب مشتريات أعمالك",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# البيانات الأساسية
COMPANY_NAME = "مؤسسة مخلد محمد بن سليمان العنزي التجارية"
CR_NUMBER = "1009005566"
VAT_NUMBER = "30056521610003"
DEFAULT_WHATSAPP = "0592859590"
DEFAULT_ADMIN_PWD = "marsad2026"

# جلب الأسرار بأمان
try:
    WHATSAPP_NUMBER = st.secrets["WHATSAPP_NUMBER"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except (KeyError, FileNotFoundError, Exception):
    WHATSAPP_NUMBER = DEFAULT_WHATSAPP
    ADMIN_PASSWORD = DEFAULT_ADMIN_PWD

# ==========================================
# 2. إدارة الجلسة
# ==========================================
if "cart" not in st.session_state: st.session_state.cart = {}
if "page" not in st.session_state: st.session_state.page = "home"
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "الكل"
if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
if "last_order" not in st.session_state: st.session_state.last_order = None
if "orders_history" not in st.session_state: st.session_state.orders_history = []

# ==========================================
# 3. تحميل المنتجات (متوافق مع CSV الخاص بك)
# ==========================================
@st.cache_data
def load_catalog():
    try:
        df = pd.read_csv("Marsad_Valid_Products.csv")
        # التأكد من وجود الأعمدة
        required_cols = ["اسم المنتج", "السعر", "القطاع"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"العمود {col} مفقود")
        
        # تنظيف البيانات
        df["السعر"] = pd.to_numeric(df["السعر"], errors='coerce').fillna(0.0)
        if "الملاحظات" not in df.columns: df["الملاحظات"] = ""
        if "الوحدة" not in df.columns: df["الوحدة"] = "حبة"
        
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة ملف المنتجات: {e}")
        return pd.DataFrame(columns=["اسم المنتج", "السعر", "القطاع", "الملاحظات", "الوحدة"])

df_catalog = load_catalog()

# ==========================================
# 4. التصميم البصري (Desert Minimal)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl; text-align: right;
    background-color: #F8FAFC; color: #0F172A;
}
#MainMenu, header, footer, .stDeployButton {visibility: hidden;}
div[data-testid="stToolbar"] {display: none !important;}

/* البطاقات */
.clean-card {
    background: #FFFFFF; border: 1px solid #E2E8F0;
    border-radius: 12px; padding: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    margin-bottom: 15px;
}
.clean-card:hover {
    border-color: #C2410C;
    box-shadow: 0 10px 15px -3px rgba(194, 65, 12, 0.1);
    transform: translateY(-3px);
}

/* الأزرار */
.stButton > button {
    background: #0F172A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    padding: 10px 20px !important; font-weight: 700 !important;
    font-family: 'Tajawal', sans-serif !important;
    transition: all 0.2s ease !important; width: 100%;
}
.stButton > button:hover {
    background: #C2410C !important;
    box-shadow: 0 4px 12px rgba(194, 65, 12, 0.3) !important;
}

/* حقول الإدخال */
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #0F172A !important; border-radius: 8px !important;
}
h1, h2, h3, h4 { font-family: 'Tajawal', sans-serif !important; color: #0F172A; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. الهيدر والتنقل
# ==========================================
def render_header():
    cart_count = sum(item['qty'] for item in st.session_state.cart.values())
    c1, c2, c3 = st.columns([4, 4, 2])
    with c1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                <circle cx="18" cy="18" r="16" fill="#0F172A"/>
                <path d="M11 18L15 22L25 12" stroke="#C2410C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div>
                <h2 style="margin: 0; font-size: 1.5rem; font-weight: 900;">مَـرْصَــد <span style="color: #C2410C;">.</span></h2>
                <span style="font-size: 0.75rem; color: #64748B;">مكتب مشتريات أعمالك الخارجي</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        btn_cart = f"🛒 السلة ({cart_count})" if cart_count > 0 else "🛒 السلة"
        if st.button(btn_cart, key="nav_cart"):
            st.session_state.page = "cart"
            st.rerun()
    st.markdown("<hr style='border-color: #E2E8F0; margin-top: 15px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# ==========================================
# 6. الصفحة الرئيسية
# ==========================================
def show_home():
    st.markdown("""
    <div class="clean-card" style="padding: 40px; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: white; border-radius: 16px; margin-bottom: 30px;">
        <span style="background: rgba(194, 65, 12, 0.2); color: #F97316; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700;">مكتب مشتريات رقمي متكامل</span>
        <h1 style="color: white; font-size: 2.5rem; margin-top: 15px; margin-bottom: 15px;">لا نبيع كرتون، نختصر رحلة مشتريات منشأتك.</h1>
        <p style="color: #94A3B8; font-size: 1.1rem;">أرسل احتياجك، نتحقق من السعر والتوفر، تعتمد العرض، ونتولى الباقي حتى باب منشأتك.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 تصفح كتالوج المنتجات الآن", key="hero_browse"):
        st.session_state.page = "products"
        st.rerun()

# ==========================================
# 7. صفحة المنتجات (مع المرساة السعرية وحاسبة الأرباح)
# ==========================================
def show_products():
    st.markdown("<h2 style='font-weight: 800; margin-bottom: 20px;'>📦 كتالوج المنتجات</h2>", unsafe_allow_html=True)
    
    # الفلاتر
    categories = ["الكل"] + list(df_catalog["القطاع"].unique())
    c1, c2 = st.columns([2, 1])
    with c1:
        search = st.text_input("🔍 بحث ذكي...", placeholder="ابحث باسم المنتج...")
    with c2:
        selected_cat = st.selectbox("القطاع", categories)
        st.session_state.selected_cat = selected_cat
        
    df_filtered = df_catalog.copy()
    if selected_cat != "الكل":
        df_filtered = df_filtered[df_filtered["القطاع"] == selected_cat]
    if search:
        df_filtered = df_filtered[df_filtered["اسم المنتج"].str.contains(search, case=False, na=False)]
        
    st.write(f"عرض **{len(df_filtered)}** منتج")
    st.write("---")
    
    # عرض المنتجات
    cols = st.columns(3)
    for idx, row in df_filtered.reset_index(drop=True).iterrows():
        col = cols[idx % 3]
        name = row["اسم المنتج"]
        price = float(row["السعر"])
        cat = row["القطاع"]
        notes = str(row["الملاحظات"]) if pd.notna(row["الملاحظات"]) else ""
        unit = row.get("الوحدة", "حبة")
        
        # استخراج السعر القديم (المرساة السعرية)
        old_price = None
        match = re.search(r'(\d+\.?\d*)', notes)
        if match:
            old_price = float(match.group(1))
            
        with col:
            st.markdown(f"""
            <div class="clean-card">
                <span style="background: #FEF3C7; color: #92400E; font-size: 0.75rem; padding: 2px 8px; border-radius: 6px;">{cat}</span>
                <h4 style="margin-top: 10px; margin-bottom: 5px; font-size: 1.1rem;">{name}</h4>
                <p style="color: #64748B; font-size: 0.8rem; margin-bottom: 10px;">الوحدة: {unit}</p>
                <div style="display: flex; align-items: baseline; gap: 10px; margin-bottom: 15px;">
                    <span style="font-size: 1.4rem; font-weight: 900; color: #0F172A;">{price:.2f} ر.س</span>
                    {f'<span style="text-decoration: line-through; color: #EF4444; font-size: 0.9rem;">{old_price:.2f}</span>' if old_price else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # أدوات الإضافة وحاسبة الأرباح
            with st.expander("➕ خيارات الطلب وحاسبة الربح"):
                qty = st.number_input("الكمية المطلوبة", min_value=1, value=1, step=1, key=f"qty_{idx}")
                
                st.markdown("<hr style='margin: 10px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
                st.markdown("📊 **حاسبة هامش الربح:**")
                sell_price = st.number_input("سعر البيع للعميل (ر.س)", min_value=0.0, value=0.0, step=0.5, key=f"sell_{idx}")
                if sell_price > 0:
                    profit = sell_price - price
                    margin = (profit / sell_price) * 100 if sell_price > 0 else 0
                    color = "#059669" if profit > 0 else "#EF4444"
                    st.markdown(f"<p style='color: {color}; font-weight: bold;'>ربحك الصافي: {profit:.2f} ر.س ({margin:.1f}%)</p>", unsafe_allow_html=True)
                
                if st.button("إضافة للسلة", key=f"add_{idx}"):
                    current_q = st.session_state.cart.get(name, {}).get('qty', 0)
                    st.session_state.cart[name] = {"price": price, "qty": current_q + qty, "unit": unit}
                    st.toast(f"تمت إضافة {qty} × {name}")
                    st.rerun()

# ==========================================
# 8. السلة والدفع
# ==========================================
def show_cart():
    st.markdown("<h2 style='font-weight: 800;'>🛒 سلة المشتريات</h2>", unsafe_allow_html=True)
    if not st.session_state.cart:
        st.info("السلة فارغة.")
        if st.button("تصفح المنتجات"):
            st.session_state.page = "products"
            st.rerun()
        return
        
    subtotal = 0
    items_to_del = []
    for name, details in st.session_state.cart.items():
        total = details['price'] * details['qty']
        subtotal += total
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        with c1: st.write(f"**{name}** ({details['unit']})")
        with c2: st.write(f"{details['price']:.2f} ر.س")
        with c3:
            new_q = st.number_input("الكمية", min_value=1, value=details['qty'], key=f"cq_{name}", label_visibility="collapsed")
            if new_q != details['qty']:
                st.session_state.cart[name]['qty'] = new_q
                st.rerun()
        with c4:
            if st.button("🗑️", key=f"del_{name}"):
                items_to_del.append(name)
                
    for k in items_to_del: del st.session_state.cart[k]
    if items_to_del: st.rerun()
    
    vat = subtotal * 0.15
    total = subtotal + vat
    
    st.markdown(f"""
    <div class="clean-card" style="margin-top: 20px;">
        <p>المجموع الفرعي: <b>{subtotal:.2f} ر.س</b></p>
        <p>الضريبة (15%): <b>{vat:.2f} ر.س</b></p>
        <h3 style="color: #C2410C;">الإجمالي: {total:.2f} ر.س</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("متابعة الطلب 🚀"):
        st.session_state.page = "checkout"
        st.rerun()

def show_checkout():
    st.markdown("<h2 style='font-weight: 800;'>📝 تأكيد الطلب</h2>", unsafe_allow_html=True)
    subtotal = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
    total = subtotal * 1.15
    
    with st.form("checkout_form"):
        name = st.text_input("اسم المنشأة *")
        phone = st.text_input("رقم الجوال *")
        loc = st.text_input("الموقع (المدينة/الحي) *")
        otp = st.text_input("رمز التحقق (OTP تجريبي: 1234) *")
        
        submit = st.form_submit_button("تأكيد وإرسال الطلب عبر الواتساب")
        
        if submit:
            if not name or not phone or not loc or otp != "1234":
                st.error("الرجاء تعبئة الحقول بشكل صحيح، وتأكد أن رمز التحقق هو 1234.")
            else:
                order_id = f"MRS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                items_text = "\n".join([f"- {k} ({v['qty']} × {v['price']} ر.س)" for k, v in st.session_state.cart.items()])
                
                # تجهيز رسالة الواتساب
                wa_msg = f"""مرحباً مرصد، طلب جديد:
📦 رقم الطلب: {order_id}
🏢 المنشأة: {name}
📱 الجوال: {phone}
📍 الموقع: {loc}
🛒 المنتجات:
{items_text}
💰 الإجمالي: {total:.2f} ر.س"""
                
                st.session_state.last_order = {"id": order_id, "msg": wa_msg, "total": total, "name": name}
                st.session_state.orders_history.append(st.session_state.last_order)
                st.session_state.cart = {}
                st.session_state.page = "success"
                st.rerun()

def show_success():
    order = st.session_state.last_order
    if not order:
        st.session_state.page = "home"
        st.rerun()
        
    wa_url = f"https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={urllib.parse.quote(order['msg'])}"
    
    st.markdown(f"""
    <div class="clean-card" style="text-align: center; padding: 40px;">
        <h2 style="color: #059669;">✓ تم تسجيل الطلب بنجاح</h2>
        <p>رقم الطلب: <b>{order['id']}</b></p>
        <p>الإجمالي: <b>{order['total']:.2f} ر.س</b></p>
        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
            <div style="background: #22C55E; color: white; padding: 15px; border-radius: 8px; font-weight: bold; margin-top: 20px;">
                📲 إرسال الطلب للمورد على الواتساب
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("العودة للرئيسية"):
        st.session_state.page = "home"
        st.rerun()

# ==========================================
# 9. لوحة الإدارة
# ==========================================
def show_admin():
    st.markdown("<h2 style='font-weight: 800;'>🛡️ لوحة الإدارة</h2>", unsafe_allow_html=True)
    if not st.session_state.admin_logged_in:
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("كلمة مرور خاطئة")
        return
        
    if st.button("تسجيل الخروج"):
        st.session_state.admin_logged_in = False
        st.rerun()
        
    st.write("### سجل الطلبات (في هذه الجلسة)")
    if st.session_state.orders_history:
        for o in reversed(st.session_state.orders_history):
            st.write(f"- {o['id']} | {o['name']} | {o['total']} ر.س")
    else:
        st.info("لا توجد طلبات بعد.")

# ==========================================
# 10. الفوتر والموجه
# ==========================================
def render_footer():
    st.markdown("<hr style='border-color: #E2E8F0; margin-top: 50px;'>", unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"<p style='color: #64748B; font-size: 0.8rem;'>© {datetime.now().year} {COMPANY_NAME} | س.ت: {CR_NUMBER}</p>", unsafe_allow_html=True)
    with c2:
        if st.button("🔒 الإدارة"):
            st.session_state.page = "admin"
            st.rerun()

def main():
    render_header()
    if st.session_state.page == "home": show_home()
    elif st.session_state.page == "products": show_products()
    elif st.session_state.page == "cart": show_cart()
    elif st.session_state.page == "checkout": show_checkout()
    elif st.session_state.page == "success": show_success()
    elif st.session_state.page == "admin": show_admin()
    render_footer()

if __name__ == "__main__":
    main()
