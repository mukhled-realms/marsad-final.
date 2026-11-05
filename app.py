import pandas as pd
import streamlit as st
import urllib.parse
import re
import os
from datetime import datetime

st.set_page_config(page_title="مرصد | B2B Supply Platform", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"]  { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .product-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 18px; margin-bottom: 15px; text-align: center; transition: 0.2s; }
    .product-card:hover { border-color: #D4AF37; transform: translateY(-2px); }
    .cat-card { background: linear-gradient(135deg, rgba(212,175,55,0.08) 0%, rgba(255,255,255,0.02) 100%); border: 1px solid rgba(212,175,55,0.2); border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 15px; }
    .bundle-card { background: linear-gradient(135deg, rgba(212,175,55,0.15) 0%, rgba(30,41,59,0.6) 100%); border: 1px solid #D4AF37; border-radius: 16px; padding: 20px; margin-bottom: 15px; }
    .offer-banner { background: linear-gradient(135deg, #D4AF37, #F4D03F); padding: 18px; border-radius: 14px; margin-bottom: 20px; text-align: center; color: #0E1117; font-weight: 800; font-size: 1.1rem; box-shadow: 0 8px 20px rgba(212,175,55,0.3); }
    .stButton > button { border-radius: 8px; font-family: 'Cairo', sans-serif; font-weight: 600; width: 100%; }
    div[data-testid="stForm"] { border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; }
    .footer-box { margin-top: 50px; padding: 20px; background: rgba(255,255,255,0.02); border-top: 1px solid rgba(255,255,255,0.08); border-radius: 12px; text-align: center; color: #888; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

COMPANY_NAME = "مؤسسة مخلد محمد بن سليمان العنزي التجارية"
CR_NUMBER = "1009005566"
TAX_NUMBER = "30056521610003"
DEFAULT_WHATSAPP = "966592859590"

# الباقات الجاهزة (3 باقات)
BUNDLES = {
    "باقة المقهى ☕": {
        "icon": "☕",
        "description": "كل احتياجات المقهى اليومية: شاي، قهوة، سكر، مناديل.",
        "items": [
            {"name": "شاي الكبوس أحمر (كرتون 100 كيس)", "qty": 2},
            {"name": "قهوة نسكافيه كلاسيك (200 جرام)", "qty": 3},
            {"name": "مبيض كوفي ميت (400 جرام)", "qty": 2},
            {"name": "سكر الأسرة الناعم (10 كيلو)", "qty": 1},
            {"name": "مناديل مشوار (كرتون 10 عبوات)", "qty": 1},
        ]
    },
    "باقة المطعم 🍽️": {
        "icon": "🍽️",
        "description": "احتياجات المطعم الأساسية: أرز، زيوت، معلبات، ومناديل.",
        "items": [
            {"name": "أرز الوليمة مزة (10 كيلو)", "qty": 2},
            {"name": "معجون السعودية (8 × 135 جرام)", "qty": 3},
            {"name": "زيت عافية (1.5 لتر)", "qty": 2},
            {"name": "تونة كالتيفا (كرتون 48 حبة)", "qty": 1},
            {"name": "مناديل سانيتا (كرتون 5 رولات)", "qty": 1},
        ]
    },
    "باقة النظافة 🧼": {
        "icon": "🧼",
        "description": "أساسيات النظافة للمطاعم والمقاهي والبقالات.",
        "items": [
            {"name": "مسحوق تايد (2.5 كيلو)", "qty": 3},
            {"name": "سائل فيري (1 لتر)", "qty": 4},
            {"name": "كلوركس (1 جالون)", "qty": 3},
            {"name": "ديتول أرضيات (3 لتر)", "qty": 2},
            {"name": "صابون لوكس (500 مل)", "qty": 5},
            {"name": "مناديل V-Fold", "qty": 1},
        ]
    }
}

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Marsad_Valid_Products.csv")
    except Exception:
        data = {
            "اسم المنتج": [f"منتج تجريبي {i}" for i in range(1, 41)],
            "السعر": [10.0 + i * 2.5 for i in range(40)],
            "القطاع": ["بقالة"] * 25 + ["بطاقة رقمية"] * 10 + ["أخرى"] * 5,
            "ملاحظات": ["جودة عالية"] * 40,
            "الصورة": ["📦"] * 40
        }
        df = pd.DataFrame(data)
    return df

df = load_data()

# Session state
defaults = {
    "page": "home",
    "selected_category": None,
    "cart": [],
    "phone": "",
    "is_verified": False,
    "otp_sent": False,
    "admin_logged_in": False,
    "admin_password": "marsad2026",
    "whatsapp_number": DEFAULT_WHATSAPP,
    "offer_dismissed": False,
    "search_term": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def add_to_cart(product_name, unit, price, qty=1):
    for item in st.session_state.cart:
        if item["product_name"] == product_name and item["unit"] == unit:
            item["quantity"] += qty
            st.toast(f"✅ تم زيادة {product_name} × {qty}")
            return
    st.session_state.cart.append({"product_name": product_name, "unit": unit, "price": price, "quantity": qty})
    st.toast(f"✅ تمت إضافة {product_name} × {qty}")

def remove_from_cart(index):
    st.session_state.cart.pop(index)
    st.rerun()

def validate_phone(phone_str):
    return bool(re.match(r"^(?:05|9665|\+9665|009665)\d{8}$", phone_str.strip()))

def normalize_phone(phone_str):
    clean = re.sub(r"\D", "", phone_str)
    if clean.startswith("05"): clean = "966" + clean[1:]
    elif clean.startswith("5"): clean = "966" + clean
    return clean

def log_order(phone, cart, total):
    order_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "phone": phone,
        "total": total,
        "items": " | ".join([f"{i['product_name']} ({i['quantity']} {i['unit']})" for i in cart])
    }
    file_path = "marsad_orders.csv"
    if not os.path.exists(file_path):
        pd.DataFrame([order_data]).to_csv(file_path, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame([order_data]).to_csv(file_path, mode='a', header=False, index=False, encoding="utf-8-sig")

def get_bundle_price(bundle):
    total = 0
    for item in bundle["items"]:
        prod = df[df["اسم المنتج"] == item["name"]]
        if not prod.empty:
            total += float(prod.iloc[0]["السعر"]) * item["qty"]
    return total

def add_bundle_to_cart(bundle_name, bundle):
    for item in bundle["items"]:
        prod = df[df["اسم المنتج"] == item["name"]]
        if not prod.empty:
            add_to_cart(item["name"], "حبة", float(prod.iloc[0]["السعر"]), item["qty"])

# Sidebar
with st.sidebar:
    st.markdown("### 🦅 مرصد - لوحة التحكم")
    if not st.session_state.admin_logged_in:
        with st.expander("🔐 دخول المدير"):
            pwd = st.text_input("كلمة المرور", type="password", key="admin_pwd_input")
            if st.button("تسجيل الدخول"):
                if pwd == st.session_state.admin_password:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("كلمة مرور خاطئة")
    else:
        st.success("مرحباً بك يا مدير 👑")
        if st.button("📊 لوحة التحليلات"): st.session_state.page = "admin"; st.rerun()
        if st.button("🚪 تسجيل خروج"):
            st.session_state.admin_logged_in = False
            st.session_state.page = "home"
            st.rerun()

# Header
st.markdown("<h1 style='text-align: center; color: #D4AF37; font-weight: 800;'>منصة مرصد للتوريد B2B 📦</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #AAA;'>المنصة المعتمدة لتوريد قطاعات البقالة والبطاقات الرقمية</p>", unsafe_allow_html=True)
st.divider()

# Navigation
col_nav1, col_nav2 = st.columns([3, 1])
with col_nav1:
    if st.session_state.page not in ["home", "admin"]:
        if st.button("⬅️ العودة للرئيسية"):
            st.session_state.page = "home"; st.rerun()
with col_nav2:
    cart_count = sum(item["quantity"] for item in st.session_state.cart)
    if cart_count > 0 and st.session_state.page != "admin":
        if st.button(f"🛒 السلة ({cart_count})", type="primary"):
            st.session_state.page = "cart"; st.rerun()

# PAGES
if st.session_state.page == "home":
    # بانر العروض
    if not st.session_state.offer_dismissed:
        col_offer1, col_offer2 = st.columns([5, 1])
        with col_offer1:
            st.markdown('<div class="offer-banner">🔥 عرض الأسبوع: خصم 5% على طلبات الطبليات + توصيل مجاني لأول 5 طلبات</div>', unsafe_allow_html=True)
        with col_offer2:
            if st.button("✖️", key="dismiss_offer"):
                st.session_state.offer_dismissed = True
                st.rerun()
    
    # الباقات الجاهزة
    st.markdown("### 🎁 الباقات الجاهزة (وفر وقتك)")
    bundle_cols = st.columns(3)
    for idx, (bname, bundle) in enumerate(BUNDLES.items()):
        with bundle_cols[idx]:
            bprice = get_bundle_price(bundle)
            st.markdown(f"""
            <div class="bundle-card">
                <div style="font-size: 2.5rem; text-align: center;">{bundle['icon']}</div>
                <h3 style="color: #D4AF37; text-align: center;">{bname}</h3>
                <p style="color: #AAA; font-size: 0.9rem;">{bundle['description']}</p>
                <p style="color: #D4AF37; font-weight: 800; font-size: 1.3rem; text-align: center;">ابتداءً من {bprice:.2f} ر.س</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 اطلب {bname}", key=f"bundle_{idx}"):
                add_bundle_to_cart(bname, bundle)
                st.rerun()
    
    st.divider()
    st.subheader("اختر القسم لاستعراض المنتجات")
    categories = [
        {"name": "بقالة", "icon": "🛒", "desc": "منتجات غذائية ومواد جافة"},
        {"name": "بطاقة رقمية", "icon": "💳", "desc": "بطاقات إعادة شحن"},
        {"name": "أخرى", "icon": "📦", "desc": "مستلزمات عامة"}
    ]
    cols = st.columns(3)
    for idx, cat in enumerate(categories):
        count = len(df[df["القطاع"] == cat["name"]])
        with cols[idx]:
            st.markdown(f"""
            <div class="cat-card">
                <div style="font-size: 2.5rem;">{cat['icon']}</div>
                <h3 style="color: #FAFAFA;">{cat['name']}</h3>
                <p style="color: #888;">{cat['desc']}</p>
                <h4 style="color: #D4AF37;">{count} منتج</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"استعراض {cat['name']}", key=f"cat_{idx}"):
                st.session_state.selected_category = cat["name"]
                st.session_state.page = "products"
                st.rerun()

elif st.session_state.page == "products":
    st.subheader(f"قسم: {st.session_state.selected_category}")
    
    # البحث
    search = st.text_input("🔍 ابحث عن منتج (في كل الأقسام)", placeholder="اكتب اسم المنتج...")
    
    if search.strip():
        filtered_df = df[df["اسم المنتج"].str.contains(search, case=False, na=False)].reset_index(drop=True)
    else:
        filtered_df = df[df["القطاع"] == st.session_state.selected_category].reset_index(drop=True)
    
    st.caption(f"عدد المنتجات: {len(filtered_df)}")
    
    if filtered_df.empty:
        st.info("لا توجد منتجات مطابقة.")
    else:
        for i in range(0, len(filtered_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_df):
                    row = filtered_df.iloc[i + j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="product-card">
                            <div style="font-size: 2rem;">{row.get('الصورة', '📦')}</div>
                            <h4 style="color: #FAFAFA;">{row['اسم المنتج']}</h4>
                            <p style="color: #D4AF37; font-weight: bold;">{row['السعر']} ريال</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        unit_choice = st.radio(
                            "الوحدة", ["حبة", "كرتون", "طبلية (50)"],
                            key=f"unit_{i+j}_{row['اسم المنتج']}", horizontal=True
                        )
                        
                        qty = 50 if "طبلية" in unit_choice else 1
                        
                        if st.button("➕ أضف للسلة", key=f"add_{i+j}_{row['اسم المنتج']}"):
                            add_to_cart(row['اسم المنتج'], unit_choice, float(row['السعر']), qty)

elif st.session_state.page == "cart":
    st.subheader("🛒 سلة المشتريات")
    if not st.session_state.cart:
        st.warning("السلة فارغة.")
        if st.button("العودة للتسوق"): st.session_state.page = "home"; st.rerun()
    else:
        total_sum = 0.0
        for idx, item in enumerate(st.session_state.cart):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.write(f"**{item['product_name']}**")
                st.caption(f"الوحدة: {item['unit']}")
            with col2: st.write(f"{item['price']:.2f} ريال")
            with col3:
                new_qty = st.number_input("الكمية", min_value=1, value=item['quantity'], key=f"qty_{idx}", label_visibility="collapsed")
                st.session_state.cart[idx]['quantity'] = new_qty
            with col4:
                sub = item['price'] * new_qty
                total_sum += sub
                st.write(f"**{sub:.2f}**")
            with col5:
                if st.button("🗑️", key=f"del_{idx}"): remove_from_cart(idx)
            st.divider()
        
        st.markdown(f"<h3 style='text-align: left; color: #D4AF37;'>الإجمالي: {total_sum:.2f} ريال</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("متابعة التسوق"): st.session_state.page = "home"; st.rerun()
        with c2:
            if st.button("إتمام الطلب ➔", type="primary"): st.session_state.page = "checkout"; st.rerun()

elif st.session_state.page == "checkout":
    st.subheader("🔐 التحقق من رقم الجوال")
    with st.form("otp_form"):
        phone_input = st.text_input("رقم الجوال", value=st.session_state.phone, placeholder="05XXXXXXXX")
        if st.form_submit_button("إرسال رمز التحقق"):
            if validate_phone(phone_input):
                st.session_state.phone = phone_input
                st.session_state.otp_sent = True
                st.success("✅ تم الإرسال. الرمز التجريبي: 1234")
            else:
                st.error("⚠️ رقم غير صحيح.")

    if st.session_state.otp_sent:
        with st.form("verify_form"):
            otp_code = st.text_input("رمز التحقق", placeholder="1234")
            if st.form_submit_button("تأكيد", type="primary"):
                if otp_code.strip() == "1234":
                    st.session_state.is_verified = True
                    st.session_state.page = "success"
                    st.rerun()
                else:
                    st.error("⚠️ رمز خاطئ!")

elif st.session_state.page == "success":
    st.balloons()
    st.success("✅ تم تأكيد الطلب بنجاح!")
    
    norm_phone = normalize_phone(st.session_state.phone)
    total_order = sum(i['price'] * i['quantity'] for i in st.session_state.cart)
    log_order(norm_phone, st.session_state.cart, total_order)
    
    items_text = ""
    for idx, item in enumerate(st.session_state.cart, 1):
        items_text += f"{idx}. {item['product_name']} | {item['quantity']} {item['unit']} | {item['price'] * item['quantity']:.2f} ريال\n"
    
    msg = f"طلب جديد من مرصد 📦\n\nالجوال: {norm_phone}\n-----------------\n{items_text}-----------------\nالإجمالي: {total_order:.2f} ريال"
    encoded = urllib.parse.quote(msg)
    wa_url = f"https://wa.me/{st.session_state.whatsapp_number}?text={encoded}"
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #25D366; color: white; padding: 18px 30px; border-radius: 12px; font-size: 1.2rem; font-weight: bold; display: inline-block; box-shadow: 0 4px 15px rgba(37,211,102,0.4);">📲 إرسال الطلب للمورد (واتساب)</div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("العودة للرئيسية"):
        st.session_state.cart = []
        st.session_state.page = "home"
        st.session_state.is_verified = False
        st.session_state.otp_sent = False
        st.rerun()

elif st.session_state.page == "admin" and st.session_state.admin_logged_in:
    st.title("👨‍💼 مكتب الإدارة - مرصد")
    tab1, tab2, tab3 = st.tabs(["📊 التحليلات والتقارير", "⚙️ الإعدادات", "📦 المنتجات"])
    
    with tab1:
        if os.path.exists("marsad_orders.csv"):
            orders = pd.read_csv("marsad_orders.csv")
            c1, c2, c3 = st.columns(3)
            c1.metric("📦 إجمالي الطلبات", len(orders))
            c2.metric("💰 إجمالي الإيرادات", f"{orders['total'].sum():.2f} ريال")
            c3.metric("📈 متوسط الطلب", f"{orders['total'].mean():.2f} ريال")
            
            st.divider()
            st.subheader("📈 المبيعات اليومية")
            daily = orders.groupby('date').agg({'total': 'sum'}).reset_index()
            daily.columns = ['التاريخ', 'الإيرادات']
            st.line_chart(daily.set_index('التاريخ'))
            
            st.subheader("🛍️ تفاصيل الطلبات")
            st.dataframe(orders, use_container_width=True)
            
            # إشعار SMS/واتساب
            st.divider()
            st.subheader("📲 إرسال إشعار للعميل")
            order_idx = st.selectbox("اختر طلباً", range(len(orders)), format_func=lambda i: f"{orders.iloc[i]['phone']} - {orders.iloc[i]['total']} ريال")
            if st.button("📱 إرسال تذكير واتساب"):
                customer_phone = orders.iloc[order_idx]['phone']
                reminder_msg = urllib.parse.quote(f"مرحباً، نذكرك بطلبك من مرصد بقيمة {orders.iloc[order_idx]['total']} ريال. شكراً لثقتك.")
                wa_reminder = f"https://wa.me/{customer_phone}?text={reminder_msg}"
                st.markdown(f"<a href='{wa_reminder}' target='_blank'>📲 اضغط هنا لإرسال الإشعار</a>", unsafe_allow_html=True)
        else:
            st.info("لا توجد طلبات حتى الآن.")
    
    with tab2:
        new_wa = st.text_input("رقم الواتساب لاستقبال الطلبات", value=st.session_state.whatsapp_number)
        if st.button("حفظ رقم الواتساب"):
            st.session_state.whatsapp_number = new_wa
            st.success("✅ تم التحديث!")
        st.divider()
        new_pwd = st.text_input("كلمة مرور جديدة", type="password")
        if st.button("تحديث كلمة المرور"):
            if len(new_pwd) >= 4:
                st.session_state.admin_password = new_pwd
                st.success("✅ تم التحديث!")
            else:
                st.error("كلمة قصيرة.")
    
    with tab3:
        st.dataframe(df[["اسم المنتج", "السعر", "القطاع"]], use_container_width=True)

st.markdown(f"""
<div class="footer-box">
    <p style="margin: 3px 0;"><strong>{COMPANY_NAME}</strong></p>
    <p style="margin: 3px 0;">السجل التجاري: {CR_NUMBER} | الرقم الضريبي: {TAX_NUMBER}</p>
    <p style="margin: 3px 0; color: #666;">جميع الحقوق محفوظة © منصة مرصد 2026</p>
</div>
""", unsafe_allow_html=True)
