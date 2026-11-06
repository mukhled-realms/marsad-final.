import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="مرصد الفرص | المنصة السيادية للتجارة والتشغيل",
    page_icon="💎",
    layout="wide"
)

# تخصيص تصميم بصري فخم وساطع يبرز صور المنتجات والرفوف بوضوح تام
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; }
    .shelf-container {
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
        padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .product-box {
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px;
        padding: 1rem; text-align: center; transition: all 0.3s ease;
    }
    .product-box:hover {
        transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    .paywall-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff; padding: 2.5rem; border-radius: 16px; text-align: center;
        border: 2px solid #d4af37;
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة الاشتراك والأمان
if "is_subscribed" not in st.session_state:
    st.session_state["is_subscribed"] = False

if "missing_demand" not in st.session_state:
    st.session_state["missing_demand"] = []

# قاعدة البيانات المحدثة مع تفاصيل الرفوف، التغليف، والصور الحقيقية الكاملة
shelf_catalog = [
    {
        "id": "S1", "الرف": "رف المشروبات والمياه الطازجة",
        "المنتج": "مياه صفا (48 عبوة × 0.2 لتر)",
        "سعر التطبيق الميداني": 10.0, "سعر السوق": 14.99, "هامش الربح": "33%",
        "طريقة التغليف والتنسيق": "تغليف حراري متماسك لسهولة الحمل، صف متناسق يضمن رؤية العلامة بوضوح.",
        "الصورة الحقيقية": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=600&auto=format&fit=crop&q=80",
        "ملاحظات الاستختراق": "يتم جلبها حصرياً من عروض التطبيق الرقمي لبنده لتوفير 4.99 ريال في كل كرتون."
    },
    {
        "id": "S2", "الرف": "رف المناديل والورقيات الأساسية",
        "المنتج": "سمايل مناديل وجه (10 عبوات)",
        "سعر التطبيق الميداني": 15.0, "سعر السوق": 25.99, "هامش الربح": "42%",
        "طريقة التغليف والتنسيق": "رص عمودي مزدوج على الرفوف الأمامية لزيادة معدل الدوران البصري وجذب انتباه الزبون.",
        "الصورة الحقيقية": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80",
        "ملاحظات الاستختراق": "منتج استهلاكي يومي متكرر، هامش ربحه العالي يغطي مصاريف التوصيل بالكامل."
    },
    {
        "id": "S3", "الرف": "رف المنظفات والعناية التجارية",
        "المنتج": "مسحوق غسيل تايد (٦ كيلو)",
        "سعر التطبيق الميداني": 45.0, "سعر السوق": 74.99, "هامش الربح": "40%",
        "طريقة التغليف والتنسيق": "وضع العبوات الكبرى في قاعدة الرف لتوزيع الوزن ومنع السقوط مع واظهار السعر البارز.",
        "الصورة الحقيقية": "https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?w=600&auto=format&fit=crop&q=80",
        "ملاحظات الاستختراق": "مطلوب بشدة من المغاسل والمقاهي لتنظيف الأدوات بأسعار جملة استثنائية."
    }
]

st.sidebar.title("💎 مرصد الفرص")
st.sidebar.markdown("**السيادة في الرفوف والتغليف التشغيلي**")

nav = st.sidebar.selectbox("اختر قسم المنصة:", [
    "🛒 هندسة الرفوف وعرض الصور الحقيقية",
    "📚 المكتبة التشغيلية وتسعير أسرار التغليف",
    "📷 كاميرا المسح والطلب الحصري",
    "🧮 الحاسبة الذكية والمساعد (محمي)",
    "💳 بوابة التفعيل البنكي"
])

# --- 1. هندسة الرفوف وعرض الصور الحقيقية ---
if nav == "🛒 هندسة الرفوف وعرض الصور الحقيقية":
    st.title("🛒 الرفوف الذكية وعرض المنتجات (الصورة الحقيقية الكاملة)")
    st.markdown("تصفح الرفوف الميدانية بعناية. اضغط على أي منتج لرؤية صورته الحقيقية بالكامل وتفاصيل تنسيقه وتغليفه:")

    for item in shelf_catalog:
        with st.container():
            st.markdown(f"""
                <div class="shelf-container">
                    <h3 style="color: #1e293b; margin-top:0;">📍 {item['الرف']}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(item['الصورة الحقيقية'], use_column_width=True)
            with c2:
                st.subheader(item['المنتج'])
                st.success(f"💰 سعر الشراء من التطبيق/الميدان: {item['سعر التطبيق الميداني']} ريال (سعر السوق: {item['سعر السوق']} ريال)")
                st.info(f"📈 هامش الربح التشغيلي: {item['هامش الربح']}")
                st.write(f"📦 **طريقة التغليف والتنسيق الاحترافي:** {item['طريقة التغليف والتنسيق']}")
                st.write(f"💡 **استراتيجية الاختراق:** {item['ملاحظات الاستختراق']}")
                
                if st.button(f"🔍 عرض معاينة الصورة الحقيقية الكاملة ({item['id']})", key=f"preview_{item['id']}"):
                    st.session_state['active_modal'] = item

    # النافذة المنبثقة للصورة الحقيقية الكاملة
    if 'active_modal' in st.session_state:
        m_item = st.session_state['active_modal']
        st.markdown("---")
        st.warning(f"✨ معاينة مكبرة للصورة الحقيقية لـ: **{m_item['المنتج']}**")
        st.image(m_item['الصورة الحقيقية'], use_column_width=True)
        if st.button("إغلاق المعاينة"):
            del st.session_state['active_modal']
            st.rerun()

# --- 2. المكتبة التشغيلية وتسعير أسرار التغليف ---
elif nav == "📚 المكتبة التشغيلية وتسعير أسرار التغليف":
    st.title("📚 المكتبة التشغيلية (أسرار الرفوف، التغليف، والاختراق)")
    st.markdown("هنا يتم توثيق أسرار الميدان التي لا يعرفها المنافسون، وتسعير الأدلة التشغيلية للراغبين بالاشتراك:")

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("""
            <div class="shelf-container">
                <h3 style="color: #d4af37;">📦 دليل هندسة التغليف الحصري</h3>
                <p>كيف تغلف السلع والكراتين بطريقة تمنع التلف وتزيد من جاذبية العرض للتاجر والمستهلك النهائي.</p>
                <p><b>سعر التقرير المستقل:</b> 1,500 ريال (مشمول في باقة الامتثال)</p>
            </div>
        """, unsafe_allow_html=True)
    with col_l2:
        st.markdown("""
            <div class="shelf-container">
                <h3 style="color: #d4af37;">🎯 استراتيجيات رص الرفوف (Shelf Space Optimization)</h3>
                <p>أين تضع المنتجات الأعلى ربحية؟ وكيف تستغل مستوى النظر لرفع المبيعات بنسبة 22% فوراً.</p>
                <p><b>سعر التقرير المستقل:</b> 2,500 ريال (مشمول في باقة الامتثال)</p>
            </div>
        """, unsafe_allow_html=True)

# --- 3. كاميرا المسح والطلب الحصري ---
elif nav == "📷 كاميرا المسح والطلب الحصري":
    st.title("📷 مسح الباركود والتقاط النواقص الحصرية")
    
    query = st.text_input("أدخل اسم المنتج أو الباركود للبحث أو تسجيل النقص:")
    if query:
        found = [p for p in shelf_catalog if query.lower() in p["المنتج"].lower()]
        if found:
            st.success("✅ المنتج متوفر في الرفوف المرصودة:")
            for f in found:
                st.write(f"- **{f['المنتج']}** | السعر: {f['سعر التطبيق الميداني']} ريال | الهامش: {f['هامش الربح']}")
        else:
            st.error("❌ المنتج غير متوفر حالياً على الرفوف!")
            st.session_state["missing_demand"].append(query)
            st.info("💡 تم تسجيل هذا المنتج في (قائمة الطلبات الحصرية المفقودة) لتقوم بتوفيره ميدانياً فوراً.")

# --- 4. الحاسبة الذكية والمساعد ---
elif nav == "🧮 الحاسبة الذكية والمساعد (محمي)":
    st.title("🧮 الحاسبة السرية والذكاء الاصطناعي")
    
    if not st.session_state["is_subscribed"]:
        st.markdown("""
            <div class="paywall-box">
                <h2>🔒 منطقة محمية بحصن أمني</h2>
                <p>حاسبة الأرباح السرية ومحرك الذكاء الاصطناعي مقفلان تماماً لحماية أسرار الرفوف والتسعير من المتطفلين والمنافسين.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success("🔓 أهلاً بك يا دكتور! الحاسبة السرية مفعلة بالكامل.")
        # تشغيل الحاسبة...

# --- 5. بوابة التفعيل البنكي ---
elif nav_choice == "💳 بوابة التفعيل البنكي" if 'nav_choice' in locals() else "💳 بوابة التفعيل البنكي":
    # تم معالجة القائمة باسم nav
    pass

if nav == "💳 بوابة التفعيل البنكي":
    st.title("💳 بوابة التحويل البنكي وتفعيل الصلاحيات السيادية")
    st.markdown("""
        <div class="shelf-container" style="text-align: center;">
            <h3 style="color: #1e293b;">مؤسسة مرصد الفرص للتجارة التشغيلية</h3>
            <p style="font-size: 1.1rem; margin-top: 1rem;">حساب التحويل الرسمي المعتمد:</p>
            <p style="font-family: monospace; font-size: 1.4rem; font-weight: bold; color: #d4af37;">IBAN: SA03 8000 0000 0000 0000 0000</p>
        </div>
    """, unsafe_allow_html=True)
    
    code = st.text_input("أدخل كود التفعيل المالي:")
    if st.button("تفعيل الوصول الكامل للمنصة"):
        st.session_state["is_subscribed"] = True
        st.success("🎉 تم تفعيل العضوية والوصول الكامل للرفوف والحاسبة بنجاح!")
