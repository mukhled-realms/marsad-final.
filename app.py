import streamlit as st
import pandas as pd
import os

# إعداد المنصة السيادية
st.set_page_config(
    page_title="مرصد الفرص | المنصة السيادية للتجارة والتشغيل",
    page_icon="💎",
    layout="wide"
)

# تصميم بصري ساطع، مريح، ويبرز الرفوف والصور الحقيقية
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .hero-box {
        background: #ffffff; border-right: 6px solid #2563eb;
        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        margin-bottom: 2rem;
    }
    .product-card {
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 14px;
        padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .paywall-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff; padding: 2rem; border-radius: 16px; text-align: center;
        border: 2px solid #d4af37;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة التفعيل والاشتراك الأمني
if "is_unlocked" not in st.session_state:
    st.session_state["is_unlocked"] = False

# تحميل ملف مرصد الحقيقي (Marsad_MASTER.csv)
@st.cache_data
def load_master_data():
    csv_path = "/content/drive/MyDrive/مرصد/app/Marsad_MASTER.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        # جدول افتراضي احتياطي في حال لم يتم ربط المسار المحلي بعد
        data = {
            'name': ["سمايل مناديل وجه (10 عبوات)", "مياه صفا (48 عبوة × 0.2 لتر)", "Closeup Toothpaste (120ml)"],
            'price': [15.00, 10.00, 5.00],
            'old_price': [25.99, 14.99, 8.00],
            'category': ["الورقيات والمناديل", "المياه والمشروبات", "العناية الشخصية"],
            'notes': ["رص عمودي مزدوج، وفر 10.99", "عرض تطبيق بنده الحصري", "سعر توريد جملة ممتاز"],
            'image': ["", "", ""],
            'savings_pct': ["42%", "33%", "37%"]
        }
        return pd.DataFrame(data)

df = load_master_data()

# الشريط الجانبي للتنقل السيادي
st.sidebar.title("💎 مرصد الفرص")
st.sidebar.markdown("**السيادة في الرفوف والتغليف والتشغيل**")

nav = st.sidebar.selectbox("اختر قسم المنصة:", [
    "🛒 الأرفف الذكية وعرض المنتجات الحقيقية",
    "🔍 محرك البحث السريع في الـ 557 منتج",
    "🧮 الحاسبة السرية والذكاء الاصطناعي (محمي)",
    "💳 بوابة التفعيل والتحقق البنكي"
])

# --- 1. الأرفف الذكية وعرض المنتجات الحقيقية ---
if nav == "🛒 الأرفف الذكية وعرض المنتجات الحقيقية":
    st.markdown("""
        <div class="hero-box">
            <h2 style="color: #0f172a; margin: 0;">🛒 الأرفف الذكية المرصودة (557 منتجاً حقيقياً)</h2>
            <p style="color: #64748b; margin: 0.5rem 0 0 0;">استعراض السلع، الأسعار الحقيقية، والصور المقصوصة بدقة من الميدان.</p>
        </div>
    """, unsafe_allow_html=True)

    categories = ["الكل"] + list(df['category'].dropna().unique())
    selected_cat = st.selectbox("تصفية حسب الرف / التصنيف:", categories)

    if selected_cat != "الكل":
        display_df = df[df['category'] == selected_cat]
    else:
        display_df = df

    for _, row in display_df.iterrows():
        st.markdown(f"""
            <div class="product-card">
                <h3 style="color: #1e293b; margin-top: 0;">{row['name']}</h3>
                <p style="color: #475569;"><b>التصنيف:</b> {row['category']}</p>
                <div style="display: flex; gap: 15px; margin: 10px 0;">
                    <span style="background: #dcfce7; color: #166534; padding: 5px 12px; border-radius: 6px; font-weight: bold;">سعر التطبيق/الميدان: {row['price']} ر.س</span>
                    <span style="background: #f1f5f9; color: #475569; padding: 5px 12px; border-radius: 6px; text-decoration: line-through;">سعر السوق: {row['old_price']} ر.س</span>
                    <span style="background: #fef3c7; color: #92400e; padding: 5px 12px; border-radius: 6px; font-weight: bold;">الهامش: {row['savings_pct']}</span>
                </div>
                <p style="color: #2563eb; margin: 0;"><b>ملاحظات التشغيل:</b> {row['notes']}</p>
            </div>
        """, unsafe_allow_html=True)

# --- 2. محرك البحث السريع في الـ 557 منتج ---
elif nav == "🔍 محرك البحث السريع في الـ 557 منتج":
    st.title("🔍 محرك البحث الفوري في أرشيف مرصد")
    query = st.text_input("ابحث عن أي منتج أو باركود ضمن الـ 557 سلعة:")
    if query:
        res = df[df['name'].str.contains(query, case=False, na=False) | df['category'].str.contains(query, case=False, na=False)]
        if not res.empty:
            st.success(f"✅ تم العثور على {len(res)} منتج مطابق:")
            st.dataframe(res, use_container_width=True)
        else:
            st.error("❌ المنتج غير موجود في أرشيف مرصد الحالي.")

# --- 3. الحاسبة السرية والذكاء الاصطناعي (محمي) ---
elif nav == "🧮 الحاسبة السرية والذكاء الاصطناعي (محمي)":
    st.title("🧮 الحاسبة السرية والذكاء الاصطناعي")
    if not st.session_state["is_unlocked"]:
        st.markdown("""
            <div class="paywall-box">
                <h2>🔒 منطقة محمية بحصن أمني</h2>
                <p>هذا القسم محمي تماماً لمنع المتطفلين والمنافسين من سرقة أسرار التسعير والأرباح.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success("🔓 مرحباً بك يا دكتور! الحاسبة والذكاء الاصطناعي مفعلة بالكامل.")
        # حاسبة الأرباح
        chosen_item = st.selectbox("اختر المنتج لحساب الأرباح:", df['name'].tolist())
        item_row = df[df['name'] == chosen_item].iloc[0]
        buy_p = float(item_row['price'])
        sell_p = float(item_row['old_price'])
        qty = st.number_input("الكمية المطلوبة:", min_value=1, value=30)
        st.success(f"إجمالي التكلفة: {buy_p * qty:.2f} ر.س | إجمالي العائد: {sell_p * qty:.2f} ر.س | صافي الربح: {(sell_p - buy_p) * qty:.2f} ر.س")

# --- 4. بوابة التفعيل والتحقق البنكي ---
elif nav == "💳 بوابة التفعيل والتحقق البنكي":
    st.title("💳 بوابة التحقق البنكي وتفعيل الصلاحيات")
    st.markdown("""
        <div class="product-card" style="text-align: center;">
            <h3>مؤسسة مرصد الفرص للتجارة التشغيلية</h3>
            <p style="font-family: monospace; font-size: 1.3rem; font-weight: bold; color: #d4af37;">IBAN: SA03 8000 0000 0000 0000 0000</p>
        </div>
    """, unsafe_allow_html=True)
    
    code_input = st.text_input("أدخل كود التفعيل المالي للوصول للمنطقة المحمية:", type="password")
    if st.button("تفعيل الصلاحيات السيادية"):
        if code_input == "2026":
            st.session_state["is_unlocked"] = True
            st.success("🎉 تم التفعيل بنجاح! يمكنك الآن الوصول للحاسبة والذكاء الاصطناعي.")
        else:
            st.error("❌ كود التفعيل غير صحيح.")
