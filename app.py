# -*- coding: utf-8 -*-
"""
منصة مرصد (Marsad) - النسخة المبتكرة v2.0
مكتب مشتريات أعمالك الخارجي
المؤسسة: مؤسسة مخلد محمد بن سليمان العنزي التجارية
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import json
import urllib.parse
from datetime import datetime

# ==========================================
# 1. إعدادات الصفحة والهيكلية العامة
# ==========================================
st.set_page_config(
    page_title="مرصد | مكتب مشتريات أعمالك الخارجي",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# بيانات المؤسسة
COMPANY_NAME = "مؤسسة مخلد محمد بن سليمان العنزي التجارية"
CR_NUMBER = "1009005566"
VAT_NUMBER = "30056521610003"
DEFAULT_WHATSAPP = "0592859590"
DEFAULT_ADMIN_PWD = "marsad2026"

# جلب الإعدادات من secrets إن وجدت
WHATSAPP_NUMBER = st.secrets.get("WHATSAPP_NUMBER", DEFAULT_WHATSAPP)
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PWD)

# ==========================================
# 2. إعداد قاعدة البيانات (SQLite للتخزين الموثوق)
# ==========================================
def init_db():
    conn = sqlite3.connect("marsad_core.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            date TEXT,
            business_name TEXT,
            business_type TEXT,
            phone TEXT,
            location TEXT,
            total_amount REAL,
            items_count INTEGER,
            items_detail TEXT,
            notes TEXT,
            payment_method TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# إدارة الجلسة (Session State)
if "cart" not in st.session_state:
    st.session_state.cart = {}  # {name: {'price': X, 'qty': Y, 'unit': Z, 'category': C}}
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# ==========================================
# 3. بيانات المنتجات الافتراضية والكتالوج
# ==========================================
@st.cache_data
def load_catalog():
    data = [
        # المقاهي والمطاعم وبقالة (35 منتج)
        ("مياه بيرين (كرتون 24 × 330 مل)", 11.00, "المقاهي", "كرتون"),
        ("مياه نوفا (كرتون 24 × 600 مل)", 13.00, "المقاهي", "كرتون"),
        ("مياه ارامكو / صفا (كرتون 40 × 200 مل)", 14.99, "المقاهي", "كرتون"),
        ("مياه هضاب (كرتون 12 × 1.5 لتر)", 18.00, "المقاهي", "كرتون"),
        ("مياه نقية (كرتون 24 × 330 مل)", 10.00, "المقاهي", "كرتون"),
        ("أرز الوليمة مزة (10 كيلو)", 75.00, "المطاعم", "كيس"),
        ("سكر الأسرة الناعم (10 كيلو)", 34.00, "المحلات", "كيس"),
        ("دقيق الكويتي (كرتون 10 أكياس)", 38.00, "المطاعم", "كرتون"),
        ("أرز الشعلان (5 كيلو)", 40.00, "المطاعم", "كيس"),
        ("سكر أبيض فاخر (5 كيلو)", 18.00, "المحلات", "كيس"),
        ("شاي الكبوس أحمر (كرتون 100 كيس)", 18.00, "المقاهي", "كرتون"),
        ("قهوة نسكافيه كلاسيك (200 جرام)", 22.00, "المقاهي", "عبوة"),
        ("مبيض كوفي ميت (400 جرام)", 15.00, "المقاهي", "عبوة"),
        ("شاي ليبتون (كرتون 100 فتلة)", 21.00, "المقاهي", "كرتون"),
        ("قهوة تركي فاخرة (250 جرام)", 15.00, "المقاهي", "عبوة"),
        ("مسحوق تايد (2.5 كيلو)", 23.00, "المنشآت", "كيس"),
        ("سائل فيري (1 لتر)", 9.00, "المنشآت", "عبوة"),
        ("كلوركس منظف (1 جالون)", 14.00, "المنشآت", "جالون"),
        ("ديتول أرضيات (3 لتر)", 22.00, "المنشآت", "عبوة"),
        ("صابون لوكس (500 مل)", 8.00, "المنشآت", "عبوة"),
        ("مناديل سانيتا (كرتون 5 رولات)", 24.00, "المنشآت", "كرتون"),
        ("مناديل فاين (كرتون 10 رولات)", 20.00, "المنشآت", "كرتون"),
        ("مناديل مشوار (كرتون 10 عبوات)", 26.00, "المنشآت", "كرتون"),
        ("رول مناديل جامبو للمنشآت", 12.00, "المنشآت", "رول"),
        ("مناديل V-Fold", 30.00, "المنشآت", "كرتون"),
        ("معجون طماطم السعودية (8 × 135 جرام)", 13.00, "المطاعم", "ربطة"),
        ("تونة كالتيفا (كرتون 48 حبة)", 135.00, "السوبر ماركت", "كرتون"),
        ("فول كاليفورنيا (كرتون 24 علبة)", 45.00, "السوبر ماركت", "كرتون"),
        ("ذرة معلبة (كرتون 12 حبة)", 32.00, "السوبر ماركت", "كرتون"),
        ("صويا صوص (700 مل)", 10.00, "المطاعم", "عبوة"),
        ("زيت عافية (1.5 لتر)", 26.00, "المطاعم", "عبوة"),
        ("حليب نيدو (2.25 كيلو)", 52.00, "المقاهي", "علبة"),
        ("كاتشب هينز (910 جرام)", 18.00, "المطاعم", "عبوة"),
        ("شطة كريستال (88 مل)", 10.00, "المطاعم", "عبوة"),
        ("مايونيز هينز (940 جرام)", 20.00, "المطاعم", "عبوة"),
        # البطاقات الرقمية (5 منتجات)
        ("بطاقة Google Play 50 ريال", 50.00, "الهدايا والبطاقات الرقمية", "بطاقة"),
        ("بطاقة Google Play 100 ريال", 100.00, "الهدايا والبطاقات الرقمية", "بطاقة"),
        ("بطاقة iTunes 50 ريال", 50.00, "الهدايا والبطاقات الرقمية", "بطاقة"),
        ("بطاقة STC Pay 50 ريال", 50.00, "الهدايا والبطاقات الرقمية", "بطاقة"),
        ("بطاقة PlayStation 50 ريال", 50.00, "الهدايا والبطاقات الرقمية", "بطاقة"),
    ]
    df = pd.DataFrame(data, columns=["اسم المنتج", "السعر", "القطاع", "الوحدة"])
    df["توفير_مقدر"] = "توفير 12% مقارنة بالسوق"
    return df

df_catalog = load_catalog()

# ==========================================
# 4. التصميم وأنماط CSS المخصصة (Desert Minimal / Industrial Tech)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* إخفاء عناصر Streamlit غير المرغوبة */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {display: none !important;}

    /* بطاقات عصرية نظيفة */
    .clean-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .clean-card:hover {
        border-color: #C2410C;
        box-shadow: 0 10px 15px -3px rgba(194, 65, 12, 0.08);
        transform: translateY(-2px);
    }

    /* الأزرار المؤسسية */
    .stButton > button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid #0F172A !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        font-family: 'Tajawal', sans-serif !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: #C2410C !important;
        border-color: #C2410C !important;
        box-shadow: 0 4px 12px rgba(194, 65, 12, 0.2) !important;
    }

    /* حقول الإدخال والفلاتر */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #C2410C !important;
        box-shadow: 0 0 0 2px rgba(194, 65, 12, 0.15) !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Tajawal', sans-serif !important;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. الترويسة العلوية والملاحة الاحترافية
# ==========================================
def render_header():
    cart_count = sum(item['qty'] for item in st.session_state.cart.values())
    
    col_logo, col_space, col_nav = st.columns([3, 2, 4])
    
    with col_logo:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="18" cy="18" r="16" fill="#0F172A"/>
              <path d="M11 18L15 22L25 12" stroke="#C2410C" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div>
                <h2 style="margin: 0; font-size: 1.5rem; font-weight: 900; letter-spacing: -0.5px;">مَـرْصَــد <span style="color: #C2410C;">.</span></h2>
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 500;">مكتب مشتريات أعمالك الخارجي</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_nav:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("الرئيسية", key="nav_home"):
                st.session_state.page = "home"
                st.rerun()
        with c2:
            if st.button("المنتجات", key="nav_prod"):
                st.session_state.page = "products"
                st.rerun()
        with c3:
            cart_label = f"السلة ({cart_count})" if cart_count > 0 else "السلة"
            if st.button(cart_label, key="nav_cart"):
                st.session_state.page = "cart"
                st.rerun()
        with c4:
            if st.button("من نحن", key="nav_about"):
                st.session_state.page = "about"
                st.rerun()

    st.markdown("<hr style='border-color: #E2E8F0; margin-top: 15px; margin-bottom: 25px;'>", unsafe_allow_html=True)

# ==========================================
# 6. الصفحة الرئيسية (Home Page)
# ==========================================
def show_home():
    # Hero Section
    st.markdown("""
    <div class="clean-card" style="padding: 50px 30px; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: #FFFFFF; border-radius: 16px; margin-bottom: 30px;">
        <div style="max-width: 750px;">
            <span style="background: rgba(194, 65, 12, 0.2); color: #F97316; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; border: 1px solid rgba(249, 115, 22, 0.3);">
                مكتب مشتريات رقمي متكامل للقطاع التجاري
            </span>
            <h1 style="color: #FFFFFF; font-size: 2.5rem; font-weight: 900; margin-top: 15px; margin-bottom: 15px; line-height: 1.3;">
                لا نبيع كرتون، نختصر رحلة مشتريات منشأتك.
            </h1>
            <p style="color: #94A3B8; font-size: 1.1rem; line-height: 1.6; margin-bottom: 25px;">
                أرسل احتياجك بكل سهولة، نتحقق من السعر والتوفر فوراً، تعتمد العرض، ونتولى الشراء والتجهيز والتسليم لغاية باب منشأتك.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2, c_btn3 = st.columns([2, 2, 2])
    with c_btn1:
        if st.button("🚀 تصفح كتالوج المنتجات الآن", key="hero_browse"):
            st.session_state.page = "products"
            st.rerun()

    # شريط التصنيفات الوسيعة الجديدة
    st.markdown("<h3 style='margin-top: 40px; margin-bottom: 20px; font-weight: 800;'>اختر قطاع منشأتك لتخصيص التجربة:</h3>", unsafe_allow_html=True)
    
    cat_cols = st.columns(6)
    categories_list = [
        ("☕ المقاهي", "المقاهي"),
        ("🍽️ المطاعم", "المطاعم"),
        ("🏪 المحلات", "المحلات"),
        ("🛒 السوبر ماركت", "السوبر ماركت"),
        ("🏢 المنشآت", "المنشآت"),
        ("🎁 البطاقات الرقمية", "الهدايا والبطاقات الرقمية")
    ]
    
    for idx, (label, val) in enumerate(categories_list):
        with cat_cols[idx]:
            if st.button(label, key=f"cat_btn_{idx}"):
                st.session_state.selected_category = val
                st.session_state.page = "products"
                st.rerun()

    # قسم كيف يعمل مرصد (3 خطوات)
    st.markdown("""
    <div style="margin: 50px 0 30px 0;">
        <h3 style="font-size: 1.8rem; font-weight: 800; text-align: center;">كيف يعمل مكتب مشتريات مرصد؟</h3>
        <p style="color: #64748B; text-align: center; font-size: 0.95rem;">ثلاث خطوات بسيطة تفصلك عن توريد سلس وموثوق</p>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("""
        <div class="clean-card" style="height: 100%; text-align: center;">
            <div style="font-size: 2rem; color: #C2410C; font-weight: 900; margin-bottom: 10px;">01</div>
            <h4 style="margin-bottom: 10px;">أرسل احتياجك</h4>
            <p style="color: #64748B; font-size: 0.9rem;">أضف المنتجات المطلوبة للسلة أو اختر من الباقات الجاهزة المعتمدة.</p>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="clean-card" style="height: 100%; text-align: center;">
            <div style="font-size: 2rem; color: #C2410C; font-weight: 900; margin-bottom: 10px;">02</div>
            <h4 style="margin-bottom: 10px;">اعتمد العرض</h4>
            <p style="color: #64748B; font-size: 0.9rem;">تحقق من الفاتورة والأسعار الشفافة بدقة، ثم أكد الطلب عبر التحقق برمز الجوال.</p>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="clean-card" style="height: 100%; text-align: center;">
            <div style="font-size: 2rem; color: #C2410C; font-weight: 900; margin-bottom: 10px;">03</div>
            <h4 style="margin-bottom: 10px;">استلم بسلام</h4>
            <p style="color: #64748B; font-size: 0.9rem;">نتولى التجهيز والشحن المباشر لمنشأتك مع فاتورة ضريبية رسمية.</p>
        </div>
        """, unsafe_allow_html=True)

    # قسم لماذا مرصد؟
    st.markdown("""
    <div style="margin: 60px 0 30px 0; text-align: center;">
        <h3 style="font-size: 1.8rem; font-weight: 800;">لماذا مرصد هي الخيار الأول للمنشآت؟</h3>
    </div>
    """, unsafe_allow_html=True)
    
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.markdown("<div class='clean-card' style='text-align:center;'><h4>أسعار شفافة</h4><p style='color:#64748B;font-size:0.85rem;'>بدون رسوم مخفية أو زيادات عشوائية.</p></div>", unsafe_allow_html=True)
    with w2:
        st.markdown("<div class='clean-card' style='text-align:center;'><h4>توريد موثوق</h4><p style='color:#64748B;font-size:0.85rem;'>التزام بالمواعيد ومواصفات المنتجات.</p></div>", unsafe_allow_html=True)
    with w3:
        st.markdown("<div class='clean-card' style='text-align:center;'><h4>دعم مستمر 24/7</h4><p style='color:#64748B;font-size:0.85rem;'>فريق متابعة مخصص لكل منشأة تجارية.</p></div>", unsafe_allow_html=True)
    with w4:
        st.markdown("<div class='clean-card' style='text-align:center;'><h4>سجل تجاري موثق</h4><p style='color:#64748B;font-size:0.85rem;'>تحت مظلة مؤسسة رسمية معتمدة.</p></div>", unsafe_allow_html=True)

# ==========================================
# 7. صفحة المنتجات مع البحث والفلترة المتقدمة
# ==========================================
def show_products():
    st.markdown("<h2 style='font-weight: 800; margin-bottom: 20px;'>📦 كتالوج المنتجات وتوريد الأعمال</h2>", unsafe_allow_html=True)

    # شريط البحث الحي والفلاتر الجانبية
    col_filter1, col_filter2, col_filter3 = st.columns([3, 2, 2])
    
    with col_filter1:
        search_query = st.text_input("🔍 بحث ذكي في المنتجات...", value="", placeholder="ابحث باسم المنتج، الصنف...")
    
    with col_filter2:
        categories = ["الكل", "المقاهي", "المطاعم", "المحلات", "السوبر ماركت", "المنشآت", "الهدايا والبطاقات الرقمية"]
        selected_cat = st.selectbox("تصنيف القطاع", categories, index=categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0)
        st.session_state.selected_category = selected_cat

    with col_filter3:
        sort_by = st.selectbox("ترتيب المنتجات", ["الافتراضي", "السعر: الأقل للأعلى", "السعر: الأعلى للأقل"])

    # تصفية البيانات
    filtered_df = df_catalog.copy()
    if selected_cat != "الكل":
        filtered_df = filtered_df[filtered_df["القطاع"] == selected_cat]
    
    if search_query:
        filtered_df = filtered_df[filtered_df["اسم المنتج"].str.contains(search_query, case=False, na=False)]

    if sort_by == "السعر: الأقل للأعلى":
        filtered_df = filtered_df.sort_values(by="السعر", ascending=True)
    elif sort_by == "السعر: الأعلى للأقل":
        filtered_df = filtered_df.sort_values(by="السعر", ascending=False)

    st.write(f"عدد المنتجات المتوفرة تطابق بحثك: **{len(filtered_df)}** منتج")
    st.write("---")

    # عرض المنتجات بنظام الشبكة (Grid) مع نافذة التأكيد الآمنة
    cols = st.columns(3)
    for idx, row in filtered_df.reset_index(drop=True).iterrows():
        col = cols[idx % 3]
        name = row["اسم المنتج"]
        price = float(row["السعر"])
        cat = row["القطاع"]
        unit = row["الوحدة"]
        saving = row["توفير_مقدر"]

        with col:
            st.markdown(f"""
            <div class="clean-card" style="margin-bottom: 20px; height: 100%;">
                <span style="background: #FEF3C7; color: #92400E; font-size: 0.75rem; padding: 2px 8px; border-radius: 6px; font-weight: 700;">{cat}</span>
                <h4 style="font-size: 1.05rem; margin-top: 10px; margin-bottom: 8px; height: 45px;">{name}</h4>
                <div style="color: #059669; font-size: 0.8rem; font-weight: 700; margin-bottom: 10px;">✨ {saving}</div>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 15px;">
                    <div>
                        <span style="font-size: 1.3rem; font-weight: 900; color: #0F172A;">{price:.2f}</span>
                        <span style="font-size: 0.8rem; color: #64748B;"> ر.س / {unit}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # نافذة الإضافة الآمنة للكميات والوحدة
            with st.expander("➕ تحديد الكمية والإضافة للسلة"):
                q_val = st.number_input("الكمية المطلوبة", min_value=1, value=1, step=1, key=f"q_{idx}_{name}")
                if st.button("إضافة آمنة للسلة", key=f"btn_add_{idx}_{name}"):
                    current_qty = st.session_state.cart.get(name, {}).get('qty', 0)
                    st.session_state.cart[name] = {
                        "price": price,
                        "qty": current_qty + q_val,
                        "unit": unit,
                        "category": cat
                    }
                    st.toast(f"تمت إضافة {q_val} × {name} للسلة بنجاح!")
                    st.rerun()

# ==========================================
# 8. صفحة سلة المشتريات (Cart Page)
# ==========================================
def show_cart():
    st.markdown("<h2 style='font-weight: 800; margin-bottom: 20px;'>🛒 سلة مشتريات المنشأة</h2>", unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("""
        <div class="clean-card" style="text-align: center; padding: 50px;">
            <p style="color: #64748B; font-size: 1.1rem;">سلة المشتريات فارغة حالياً.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("العودة لتصفح المنتجات"):
            st.session_state.page = "products"
            st.rerun()
        return

    subtotal = 0.0
    items_to_delete = []

    for item_name, details in st.session_state.cart.items():
        price = details["price"]
        qty = details["qty"]
        unit = details["unit"]
        item_total = price * qty
        subtotal += item_total

        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
        with c1:
            st.markdown(f"**{item_name}**<br><span style='color:#64748B; font-size:0.8rem;'>الوحدة: {unit}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div style='text-align:center;'>{price:.2f} ر.س</div>", unsafe_allow_html=True)
        with c3:
            new_q = st.number_input("", min_value=1, value=qty, key=f"cart_q_{item_name}", label_visibility="collapsed")
            if new_q != qty:
                st.session_state.cart[item_name]["qty"] = new_q
                st.rerun()
        with c4:
            st.markdown(f"<div style='text-align:center; font-weight:800; color:#C2410C;'>{item_total:.2f} ر.س</div>", unsafe_allow_html=True)
        with c5:
            if st.button("🗑️", key=f"del_{item_name}"):
                items_to_delete.append(item_name)

    for k in items_to_delete:
        del st.session_state.cart[k]
        st.rerun()

    vat_amount = subtotal * 0.15
    total_amount = subtotal + vat_amount

    st.markdown("<hr style='border-color: #E2E8F0; margin: 30px 0;'>", unsafe_allow_html=True)

    col_space, col_sum = st.columns([1, 1])
    with col_sum:
        st.markdown(f"""
        <div class="clean-card">
            <h4 style="margin-bottom: 20px;">ملخص الحساب المالي</h4>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #64748B;">المجموع الفرعي:</span>
                <span>{subtotal:.2f} ر.س</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #64748B;">ضريبة القيمة المضافة (15%):</span>
                <span>{vat_amount:.2f} ر.س</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span style="color: #64748B;">التوصيل واللوجستيات:</span>
                <span style="color: #059669; font-weight: 700;">يحسب عند التأكيد</span>
            </div>
            <hr style="border-color: #E2E8F0;">
            <div style="display: flex; justify-content: space-between; font-size: 1.25rem; font-weight: 900; margin-bottom: 20px;">
                <span>الإجمالي الكلي:</span>
                <span style="color: #C2410C;">{total_amount:.2f} ر.س</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("متابعة إتمام الطلب والتحقق 🚀"):
            st.session_state.page = "checkout"
            st.rerun()

# ==========================================
# 9. صفحة تأكيد الطلب مع التحقق OTP (Checkout Page)
# ==========================================
def show_checkout():
    st.markdown("<h2 style='font-weight: 800; margin-bottom: 20px;'>📝 تأكيد طلب التوريد والتحقق</h2>", unsafe_allow_html=True)

    if not st.session_state.cart:
        st.session_state.page = "home"
        st.rerun()

    subtotal = sum(i['price'] * i['qty'] for i in st.session_state.cart.values())
    vat_amount = subtotal * 0.15
    total_amount = subtotal + vat_amount

    with st.form("checkout_form"):
        st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
        
        biz_name = st.text_input("اسم المنشأة التجاري *", placeholder="مثال: مقهى أفق الشرق")
        biz_type = st.selectbox("نوع النشاط", ["المقاهي", "المطاعم", "المحلات", "السوبر ماركت", "المنشآت", "أخرى"])
        phone = st.text_input("رقم جوال المسؤول للتواصل *", placeholder="05XXXXXXXX")
        location = st.text_input("المدينة / الحي / تفاصيل الموقع *", placeholder="الرياض - حي النظيم - شارع الأخدود")
        notes = st.text_area("ملاحظات إضافية على التوريد", placeholder="أوقات التسليم المفضلة، تفاصيل خاصة...")

        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        
        # نظام التحقق OTP التجريبي (الكود 1234)
        st.markdown("#### التحقق من الجوال عبر رمز OTP")
        col_otp1, col_otp2 = st.columns([2, 1])
        with col_otp1:
            otp_input = st.text_input("أدخل رمز التحقق (جرب 1234)", value="", type="default")
        with col_otp2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("رمز التحقق التجريبي هو: 1234")

        submit_order = st.form_submit_button("إرسال واعتماد الطلب نهائياً 📲")

    if submit_order:
        if not biz_name or not phone or not location:
            st.error("يرجى تعبئة كافة الحقول الإجبارية.")
        elif otp_input != "1234":
            st.error("رمز التحقق (OTP) غير صحيح. يرجى إدخال 1234.")
        else:
            order_id = f"MRS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            items_summary = []
            for name, details in st.session_state.cart.items():
                items_summary.append(f"• {name} ({details['qty']} {details['unit']}) - {details['price']*details['qty']:.2f} ر.س")
            
            items_text = "\n".join(items_summary)

            # حفظ الطلب في قاعدة البيانات SQLite
            conn = sqlite3.connect("marsad_core.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_id, date, business_name, business_type, phone, location, total_amount, items_count, items_detail, notes, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                biz_name,
                biz_type,
                phone,
                location,
                round(total_amount, 2),
                sum(i['qty'] for i in st.session_state.cart.values()),
                json.dumps(st.session_state.cart, ensure_ascii=False),
                notes,
                "الدفع عند الاستلام / تحويل بنكي معتمد"
            ))
            conn.commit()
            conn.close()

            wa_message = f"""مرحباً، طلب توريد جديد من مكتب مشتريات *مرصد*:

📦 *رقم الطلب:* {order_id}
🏢 *المنشأة:* {biz_name} ({biz_type})
📱 *الجوال:* {phone}
📍 *الموقع:* {location}

🛒 *المنتجات المطلوبة:*
{items_text}

💵 *المجموع الفرعي:* {subtotal:.2f} ر.س
🏛️ *الضريبة (15%):* {vat_amount:.2f} ر.س
💰 *الإجمالي الكلي:* {total_amount:.2f} ر.س
📝 *ملاحظات:* {notes if notes else 'لا يوجد'}"""

            st.session_state.last_order = {
                "order_id": order_id,
                "biz_name": biz_name,
                "total_amount": total_amount,
                "wa_message": wa_message
            }
            st.session_state.cart = {}
            st.session_state.page = "success"
            st.rerun()

# ==========================================
# 10. صفحة النجاح (Success Page)
# ==========================================
def show_success():
    if "last_order" not in st.session_state:
        st.session_state.page = "home"
        st.rerun()

    order_info = st.session_state.last_order
    wa_encoded = urllib.parse.quote(order_info["wa_message"])
    wa_url = f"https://wa.me/966{WHATSAPP_NUMBER[1:]}?text={wa_encoded}"

    st.markdown(f"""
    <div class="clean-card" style="text-align: center; padding: 50px; max-width: 700px; margin: 0 auto;">
        <div style="background: #D1FAE5; color: #065F46; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; font-size: 1.8rem; font-weight: bold;">✓</div>
        <h2 style="font-weight: 900; margin-bottom: 10px;">تم تسجيل طلبك واعتماده بنجاح!</h2>
        <p style="color: #64748B; font-size: 1.05rem;">رقم الطلب المرجعي: <strong style="color: #C2410C;">{order_info['order_id']}</strong></p>
        <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 30px;">انقر على الزر أدناه لإرسال الطلب فوراً لمكتب المشتريات عبر الواتساب لتأكيد الشحن والتوصيل.</p>
        
        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
            <div style="background: #22C55E; color: white; padding: 14px 28px; border-radius: 8px; font-weight: 800; font-size: 1.1rem; display: inline-block; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);">
                📲 إرسال الطلب للمورد على واتساب
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    c1, c2, c3 = st.columns([2, 2, 2])
    with c2:
        if st.button("العودة للرئيسية"):
            st.session_state.page = "home"
            st.rerun()

# ==========================================
# 11. لوحة الإدارة السرية (Admin Dashboard)
# ==========================================
def show_admin():
    st.markdown("<h2 style='font-weight: 800; margin-bottom: 20px;'>🛡️ لوحة إدارة مرصد المركزية</h2>", unsafe_allow_html=True)

    if not st.session_state.admin_logged_in:
        st.markdown("<div class='clean-card' style='max-width: 400px; margin: 0 auto;'>", unsafe_allow_html=True)
        pwd = st.text_input("أدخل كلمة مرور الإدارة", type="password")
        if st.button("دخول الإدارة"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.success("أهلاً بك، تم تسجيل الدخول بصلاحيات الإدارة الكاملة.")
    if st.button("تسجيل الخروج من الإدارة"):
        st.session_state.admin_logged_in = False
        st.rerun()

    st.markdown("### 📋 سجل الطلبات المستلمة (قاعدة البيانات)")
    conn = sqlite3.connect("marsad_core.db")
    df_orders = pd.read_sql_query("SELECT * FROM orders ORDER BY date DESC", conn)
    conn.close()

    if not df_orders.empty:
        st.dataframe(df_orders, use_container_width=True)
        
        st.markdown("### 📈 مؤشرات الأداء والمبيعات")
        if "total_amount" in df_orders.columns:
            st.line_chart(df_orders["total_amount"])
    else:
        st.info("لا توجد طلبات مسجلة في قاعدة البيانات حتى الآن.")

# ==========================================
# 12. صفحة من نحن (About Page)
# ==========================================
def show_about():
    st.markdown("""
    <div class="clean-card" style="padding: 40px; max-width: 800px; margin: 0 auto;">
        <h2 style="font-weight: 900; margin-bottom: 20px;">قصة تأسيس "مرصد"</h2>
        <p style="color: #334155; font-size: 1.05rem; line-height: 1.8; margin-bottom: 20px;">
            من قلب التجربة الميدانية القاسية، وسط سلات متروكة وأنظمة معطلة وتجار غاضبين، ولدت فكرة <strong>مرصد</strong>. شاهدنا عن قرب معاناة أصحاب المنشآت الصغيرة والمتوسطة في الحصول على توريد مستقر وبأسعار عادلة شفافة.
        </p>
        <p style="color: #334155; font-size: 1.05rem; line-height: 1.8; margin-bottom: 20px;">
            قررنا أن نبني مكتب مشتريات خارجي يحل الفوضى جذرياً: التاجر يرسل طلبه بكل سهولة، الأسعار واضحة كالشمس، والبضاعة تصل إلى باب المنشأة بدون عناء الموردين التقليديين.
        </p>
        <hr style="border-color: #E2E8F0; margin: 30px 0;">
        <h4 style="font-weight: 800; margin-bottom: 10px;">البيانات النظامية والتجارية:</h4>
        <p style="color: #64748B; font-size: 0.95rem; line-height: 1.6;">
            <strong>الكيان:</strong> مؤسسة مخلد محمد بن سليمان العنزي التجارية<br>
            <strong>السجل التجاري:</strong> 1009005566<br>
            <strong>الرقم الضريبي:</strong> 30056521610003<br>
            <strong>المقر الرئيسي:</strong> الرياض — حي النظيم
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 13. التذييل العام (Footer) مع زر الإدارة السري
# ==========================================
def render_footer():
    st.markdown("<hr style='border-color: #E2E8F0; margin-top: 60px; margin-bottom: 30px;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([4, 4, 2])
    with col1:
        st.markdown(f"""
        <h4 style="font-weight: 800; color: #0F172A; margin-bottom: 10px;">مرصد | Marsad</h4>
        <p style="color: #64748B; font-size: 0.85rem; line-height: 1.6;">
            مكتب مشتريات أعمالك الخارجي الأول في المملكة.<br>
            جميع الحقوق محفوظة © {datetime.now().year} {COMPANY_NAME}
        </p>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <h4 style="font-weight: 800; color: #0F172A; margin-bottom: 10px;">معلومات التراخيص والاعتماد</h4>
        <p style="color: #64748B; font-size: 0.85rem; line-height: 1.6;">
            س.ت: {CR_NUMBER} | ر.ض: {VAT_NUMBER}<br>
            الرياض، المملكة العربية السعودية<br>
            واتساب المبيعات والدعم: {WHATSAPP_NUMBER}
        </p>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 لوحة الإدارة", key="footer_admin_btn"):
            st.session_state.page = "admin"
            st.rerun()

# ==========================================
# 14. موجه الصفحات الرئيسي (Router)
# ==========================================
def main():
    render_header()

    if st.session_state.page == "home":
        show_home()
    elif st.session_state.page == "products":
        show_products()
    elif st.session_state.page == "cart":
        show_cart()
    elif st.session_state.page == "checkout":
        show_checkout()
    elif st.session_state.page == "success":
        show_success()
    elif st.session_state.page == "admin":
        show_admin()
    elif st.session_state.page == "about":
        show_about()

    render_footer()

if __name__ == "__main__":
    main()
