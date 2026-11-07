import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(
    page_title="مرصد | لوحة العمليات",
    page_icon="📖",
    layout="wide"
)

# تصميم بسيط
st.markdown("""
<style>
    .stApp { background-color: #F4F7FC; }
    .main-title { color: #0A2540; font-size: 2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. حماية لوحة التحكم (PIN 5590)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'>🔒 لوحة الإدارة المحمية</div>", unsafe_allow_html=True)
    st.markdown("الرجاء إدخال رمز الحماية (PIN) للدخول.")
    pin = st.text_input("رمز الحماية", type="password")
    if st.button("دخول"):
        if pin == "5590":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ رمز غير صحيح")
    st.stop()

# ==========================================
# 2. لوحة التحكم الرئيسية (بعد الدخول)
# ==========================================
st.sidebar.title("📖 مرصد | MARSAD")
st.sidebar.markdown("مرحباً بك يا مدير العمليات.")

menu = st.sidebar.radio("اختر القسم:", [
    "📋 طلبات الزبائن",
    "📦 إدارة المنتجات",
    "📝 كتاب الملاحظات",
    "📢 إدارة الإعلانات"
])

# ==========================================
# 3. قسم طلبات الزبائن
# ==========================================
if menu == "📋 طلبات الزبائن":
    st.title("📋 طلبات الزبائن الواردة")
    st.info("هنا تظهر الطلبات التي يرسلها الزبائن من الموقع. (ملاحظة: الطلبات حالياً تصل عبر الواتساب، وسيتم ربطها هنا لاحقاً).")
    
    # جدول تجريبي للطلبات
    orders = pd.DataFrame([
        {"رقم الطلب": "ORD-001", "الزبون": "بقالة النظيم", "الموقع": "حي النظيم", "الحالة": "جديد"},
        {"رقم الطلب": "ORD-002", "الزبون": "مطعم الشرق", "الموقع": "حي العليا", "الحالة": "قيد التجهيز"},
    ])
    st.dataframe(orders, use_container_width=True)

# ==========================================
# 4. قسم إدارة المنتجات
# ==========================================
elif menu == "📦 إدارة المنتجات":
    st.title("📦 إدارة المنتجات")
    st.info("هنا يمكنك مراجعة المنتجات الموجودة في المتجر وتحديث حالتها.")
    
    # محاولة قراءة ملف المنتجات
    try:
        df = pd.read_csv("Marsad_Valid_Products.csv", encoding='utf-8-sig')
        st.write(f"إجمالي المنتجات: {len(df)}")
        
        # عرض المنتجات
        for index, row in df.head(10).iterrows():
            with st.expander(f"📦 {row['اسم المنتج']} — {row['السعر']} ر.س"):
                st.write(f"**القطاع:** {row['القطاع']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ متوفر في 140", key=f"avail_{index}"):
                        st.success("تم التحديد كمتوفر!")
                with col2:
                    if st.button(f"🚫 إخفاء من المتجر", key=f"hide_{index}"):
                        st.warning("تم الإخفاء (أرشفة).")
    except Exception as e:
        st.error(f"لم يتم العثور على ملف المنتجات: {e}")

# ==========================================
# 5. كتاب الملاحظات
# ==========================================
elif menu == "📝 كتاب الملاحظات":
    st.title("📝 كتاب الملاحظات")
    st.info("هنا تكتب ملاحظاتك اليومية، وسيتم حفظها وعرضها.")
    
    if "notes" not in st.session_state:
        st.session_state.notes = []
    
    # إضافة ملاحظة جديدة
    new_note = st.text_area("أضف ملاحظة جديدة (مثال: منتج كذا متوفر في 140، أو تغير سعره):")
    if st.button("حفظ الملاحظة"):
        if new_note:
            st.session_state.notes.append(new_note)
            st.success("تم حفظ الملاحظة بنجاح!")
    
    st.divider()
    st.subheader("الملاحظات السابقة:")
    for note in reversed(st.session_state.notes):
        st.info(note)

# ==========================================
# 6. إدارة الإعلانات
# ==========================================
elif menu == "📢 إدارة الإعلانات":
    st.title("📢 إدارة الإعلانات (الشريط المتحرك)")
    st.info("أضف إعلاناً هنا وسيظهر مباشرة في الشريط المتحرك في الموقع.")
    
    if "ads" not in st.session_state:
        st.session_state.ads = ["🔥 عروض الأسبوع: خصم خاص على كراتين المياه والمنظفات!"]
    
    new_ad = st.text_input("نص الإعلان الجديد:")
    if st.button("نشر الإعلان"):
        if new_ad:
            st.session_state.ads.append(new_ad)
            st.success("تم نشر الإعلان!")
    
    st.divider()
    st.subheader("الإعلانات النشطة حالياً:")
    for ad in st.session_state.ads:
        st.write(f"- {ad}")

# ==========================================
# 7. زر تسجيل الخروج
# ==========================================
st.sidebar.divider()
if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()
