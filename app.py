import streamlit as st
import pandas as pd
import os

# إعداد المنصة السيادية المتقدمة
st.set_page_config(
    page_title="مرصد الفرص السيادي | المنصة التشغيلية المتقدمة",
    page_icon="💎",
    layout="wide"
)

# تخصيص التصميم البصري الخرافي (خلفيات رفوف مموهة ومظلمة، فخامة مطلقة)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.96)), 
                    url('https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=1600&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f8fafc;
    }
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #d4af37; padding: 2rem; border-radius: 20px;
        box-shadow: 0 15px 35px -5px rgba(212, 175, 55, 0.25);
        margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center;
    }
    .shelf-category-box {
        background: rgba(30, 41, 59, 0.85); border-left: 6px solid #3b82f6;
        padding: 1.5rem; border-radius: 14px; margin-bottom: 1.5rem;
        backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05);
    }
    .product-row-card {
        background: rgba(15, 23, 42, 0.8); border: 1px solid #334155; border-radius: 12px;
        padding: 1.2rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center;
        transition: all 0.3s ease;
    }
    .product-row-card:hover {
        border-color: #d4af37; transform: translateX(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }
    .game-card-pkg {
        background: rgba(30, 41, 59, 0.9); border: 2px solid #d4af37; border-radius: 16px;
        padding: 1.8rem; text-align: center; transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .game-card-pkg:hover {
        transform: translateY(-8px); border-color: #60a5fa;
        box-shadow: 0 15px 30px rgba(59, 130, 246, 0.3);
    }
    .paywall-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff; padding: 2.5rem; border-radius: 18px; text-align: center;
        border: 2px solid #d4af37; box-shadow: 0 15px 30px rgba(0,0,0,0.7);
    }
    </style>
""", unsafe_allow_html=True)

# إدارة حالة الأمان والتفعيل
if "is_unlocked" not in st.session_state:
    st.session_state["is_unlocked"] = False

# الشريط الجانبي السيادي
st.sidebar.title("💎 مرصد الفرص | مخلد")
st.sidebar.markdown("**السيادة والتشغيل المتقدم**")

nav = st.sidebar.selectbox("اختر قسم المنصة السيادية:", [
    "🚀 الواجهة الرئيسية والتحليل الاستراتيجي",
    "🛒 الأرفف الذكية المترتبة (الشاي، الشامبو، الحفاظات)",
    "🎮 محطة الألعاب وباقات البطاقات الرقمية (50-700 ر.س)",
    "📚 المكتبة التشغيلية وأسرار منع الخسائر",
    "🧮 الحاسبة السرية والذكاء الاصطناعي (محمي)",
    "💳 بوابة التفعيل والتحقق البنكي"
])

# --- 1. الواجهة الرئيسية والتحليل الاستراتيجي ---
if nav == "🚀 الواجهة الرئيسية والتحليل الاستراتيجي":
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown("""
            <div class="hero-banner">
                <div>
                    <h1 style="color: #d4af37; margin:0; font-size: 2.2rem;">مرصد الفرص | المنصة السيادية للتجارة التشغيلية</h1>
                    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 0.8rem;">
                        النظام الأسطوري المتقدم لتمكين الأسواق الكبرى، هندسة المشتريات، منع الخسائر، واختراق الأسعار ميدانياً بدون عمولات أو وسطاء. متجر يتجاوز عقلية المتاجر التقليدية بعشر سنوات!
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.9); border: 2px solid #d4af37; padding: 1.5rem; border-radius: 16px; text-align: center;">
                <h3 style="color: #60a5fa; margin:0;">🎮 محطة مخرج (Exit)</h3>
                <p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 5px;">شعار مرصد & مخلد</p>
                <p style="color: #34d399; font-size: 0.8rem; font-weight: bold; margin-top: 5px;">قريباً الإصدار العالمي</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="paywall-box" style="text-align: right; margin-top: 2rem;">
            <h2 style="color: #d4af37; margin-top:0;">💡 رسالة استراتيجية لرواد الأسواق والمتاجر الكبرى</h2>
            <p style="font-size: 1.1rem; lineHeight: 1.8; color: #cbd5e1;">
                عندما يتصفح التاجر هذه المنصة، فإنه لا يرى مجرد سلع عادية، بل يرى <b>هندسة ميدانية حقيقية</b> تمنع الهدر، تقفل فجوات المخزون، وتوفر السلع من قلب عروض التطبيقات الرقمية الكبرى بهوامش ربح استثنائية. استقلالية كاملة عن منصات الوسطاء، وسيطرة تامة على الأصول الرقمية والتشغيلية.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- 2. الأرفف الذكية المترتبة (الشاي خلف الشاي، الشامبو خلف الشامبو، الحفاظات خلف الحفاظات) ---
elif nav == "🛒 الأرفف الذكية المترتبة (الشاي، الشامبو، الحفاظات)":
    st.title("🛒 الأرفف الذكية المترتبة بدقة متناهية")
    st.markdown("تصنيف سحبي هندسي: كل منتج خلفه شبيهه (الشاي خلف الشاي، الشامبو خلف الشامبو، الحفاظات خلف الحفاظات) لضمان انسيابية العرض وسرعة القرار التشغيلي.")

    # محاكاة لأقسام الأرفف المترتبة بدقة
    shelf_sections = [
        {"القسم": "☕ رف الشاي والمشروبات الساخنة", "الترتيب": "الشاي الفاخر خلف الشاي العادي بصفوف متناسقة", "المنتج": "شاي ليبتون براند (200 كيس)", "السعر": "38.00 ر.س", "السوق": "55.00 ر.س", "الهامش": "31%"},
        {"القسم": "🧴 رف الشامبو والعناية الشخصية", "الترتيب": "الشامبو التجاري خلف شامبو الصالونات", "المنتج": "شامبو بانتين للعناية المكثفة (600مل)", "السعر": "18.50 ر.س", "السوق": "28.00 ر.س", "الهامش": "34%"},
        {"القسم": "👶 رف الحفاظات ومستلزمات الأطفال", "الترتيب": "حفاظات بيبي جوي خلف بامبرز بترتيب مقاسات صارم", "المنتج": "حفاظات بيبي جوي مقاس 4 (كبير جداً)", "السعر": "65.00 ر.س", "السوق": "92.00 ر.س", "الهامش": "29%"},
        {"القسم": "🧻 رف الورقيات والمناديل الأساسية", "الترتيب": "مناديل الوجه خلف الرول الكبير للمطاعم", "المنتج": "سمايل مناديل وجه (10 عبوات)", "السعر": "15.00 ر.س", "السوق": "25.99 ر.س", "الهامش": "42%"}
    ]

    for item in shelf_sections:
        st.markdown(f"""
            <div class="shelf-category-box">
                <h3 style="color: #d4af37; margin-top:0;">📍 {item['القسم']}</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;"><b>هندسة الترتيب:</b> {item['الترتيب']}</p>
                <div class="product-row-card">
                    <div>
                        <h4 style="color: #f8fafc; margin:0;">{item['منتج'] if 'منتج' in item else item['المنتج']}</h4>
                        <span style="color: #34d399; font-weight: bold;">سعر الميدان: {item['السعر']}</span> | 
                        <span style="color: #94a3b8; text-decoration: line-through;">سعر السوق: {item['السوق']}</span>
                    </div>
                    <div style="background: rgba(212, 175, 55, 0.2); color: #d4af37; padding: 6px 14px; border-radius: 8px; font-weight: bold;">
                        هامش الربح: {item['الهامش']}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 3. محطة الألعاب وباقات البطاقات الرقمية ---
elif nav == "🎮 محطة الألعاب وباقات البطاقات الرقمية (50-700 ر.س)":
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.title("🎮 محطة الألعاب السيادية (مخرج / Exit)")
        st.markdown("عالم من الغموض، التحدي، وأكواد التشغيل السرية التي تدفع اللاعب للشراء بحماس جنوني.")
    with col_g2:
        st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.9); border: 1px dashed #d4af37; padding: 1rem; border-radius: 12px; text-align: center;">
                <h4 style="color: #60a5fa; margin:0;">شعار مخلد & مرصد</h4>
                <p style="color: #cbd5e1; font-size: 0.8rem; margin-top: 4px;">الهوية الرقمية المستقلة</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 💳 باقات البطاقات الرقمية الخاصة بالألعاب (الأسعار المعتمدة)")
    
    gc1, gc2, gc3, gc4 = st.columns(4)

    with gc1:
        st.markdown("""
            <div class="game-card-pkg">
                <h3 style="color: #60a5fa;">باقة التحدي الأساسي</h3>
                <h1 style="color: #d4af37; margin: 1rem 0;">50 ر.س</h1>
                <p style="color: #94a3b8; font-size: 0.85rem;">كود شحن فوري مع مفتاح أسرار خفيف للبدايات.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("شراء باقة 50 ريال", key="p_50"):
            st.success("✨ تم توليد كود الغموض (50 ر.س) بنجاح! جاهز للتسليم.")

    with gc2:
        st.markdown("""
            <div class="game-card-pkg">
                <h3 style="color: #34d399;">باقة المحترف المتمرد</h3>
                <h1 style="color: #d4af37; margin: 1rem 0;">150 ر.س</h1>
                <p style="color: #94a3b8; font-size: 0.85rem;">رصيد مضاعف + أداة كشف المسارات السرية في اللعبة.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("شراء باقة 150 ريال", key="p_150"):
            st.success("✨ تم توليد كود الغموض (150 ر.س) بنجاح! استعد للإثارة.")

    with gc3:
        st.markdown("""
            <div class="game-card-pkg">
                <h3 style="color: #f43f5e;">باقة السيادة الذهبية</h3>
                <h1 style="color: #d4af37; margin: 1rem 0;">300 ر.س</h1>
                <p style="color: #94a3b8; font-size: 0.85rem;">صلاحيات استثنائية، أسلحة حصرية، ومراتب متقدمة.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("شراء باقة 300 ريال", key="p_300"):
            st.success("✨ تم توليد كود الغموض (300 ر.س) بنجاح! مبروك السيطرة.")

    with gc4:
        st.markdown("""
            <div class="game-card-pkg">
                <h3 style="color: #a855f7;">باقة الأسطورة المطلقة</h3>
                <h1 style="color: #d4af37; margin: 1rem 0;">700 ر.س</h1>
                <p style="color: #94a3b8; font-size: 0.85rem;">القوة القصوى، مفاتيح الإمبراطورية، والوصول لكافة الأسرار.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("شراء باقة 700 ريال", key="p_700"):
            st.success("✨ تم توليد كود الغموض الأسطوري (700 ر.س) بنجاح! السيادة المطلقة بين يديك.")

# --- 4. المكتبة التشغيلية وأسرار منع الخسائر ---
elif nav == "📚 المكتبة التشغيلية وأسرار منع الخسائر":
    st.title("📚 المكتبة التشغيلية وأسرار الحماية الميدانية")
    st.markdown("أرشيفك المهني وخبرتك العميقة في إدارة المستودعات، فحص الطبالي، التعامل مع الفوارغ، ومنع التلف والخسائر.")

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown("""
            <div class="shelf-category-box">
                <h3 style="color: #d4af37;">📦 بروتوكول استلام الطبالي وفحص الفوارغ</h3>
                <p style="color: #cbd5e1; font-size: 0.95rem;">
                    كيفية تدقيق الشحنات الواردة، رصد العبوات المفتوحة، وتجنب الهدر المالي بنسبة 100% بناءً على الخبرة الميدانية المعتمدة.
                </p>
                <span style="color: #34d399; font-weight: bold;">مشمول في حزمة السيادة التشغيلية</span>
            </div>
        """, unsafe_allow_html=True)
    with col_l2:
        st.markdown("""
            <div class="shelf-category-box">
                <h3 style="color: #d4af37;">🛡️ هندسة منع الخسائر في الأسواق الكبرى</h3>
                <p style="color: #cbd5e1; font-size: 0.95rem;">
                    أدلة التشغيل السريعة والتقارير الأمنية والميدانية المخصصة لحماية البضائع ورفع كفاءة التخزين السريع دون مستودعات ضخمة.
                </p>
                <span style="color: #34d399; font-weight: bold;">مشمول في حزمة السيادة التشغيلية</span>
            </div>
        """, unsafe_allow_html=True)

# --- 5. الحاسبة السرية والذكاء الاصطناعي (محمي) ---
elif nav == "🧮 الحاسبة السرية والذكاء الاصطناعي (محمي)":
    st.title("🧮 الحاسبة السرية والذكاء الاصطناعي")
    if not st.session_state["is_unlocked"]:
        st.markdown("""
            <div class="paywall-box">
                <h2>🔒 حصن مرصد الأمني المحمي</h2>
                <p>هذا القسم مغلق تماماً بحراسة رقمية لمنع المتطفلين والمنافسين من الاطلاع على هوامش الأرباح السرية.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success("🔓 أهلاً بك يا دكتور مخلد! الحاسبة السرية والذكاء الاصطناعي مفعلة بالكامل.")

# --- 6. بوابة التفعيل والتحقق البنكي ---
elif nav == "💳 بوابة التفعيل والتحقق البنكي":
    st.title("💳 بوابة التحقق البنكي وتفعيل الصلاحيات السيادية")
    st.markdown("""
        <div class="paywall-box" style="text-align: center;">
            <h3 style="color: #d4af37; margin-top:0;">مؤسسة مرصد الفرص للتجارة التشغيلية والألعاب</h3>
            <p style="font-size: 1.1rem; color: #cbd5e1; margin-top: 10px;">حساب التحويل البنكي الرسمي المعتمد:</p>
            <p style="font-family: monospace; font-size: 1.4rem; font-weight: bold; color: #60a5fa;">IBAN: SA03 8000 0000 0000 0000 0000</p>
        </div>
    """, unsafe_allow_html=True)
    
    code_input = st.text_input("أدخل كود التفعيل المالي للوصول للمنطقة المحمية:", type="password")
    if st.button("تفعيل الصلاحيات السيادية"):
        if code_input == "2026":
            st.session_state["is_unlocked"] = True
            st.success("🎉 تم التفعيل بنجاح! الصلاحيات الكاملة أصبحت بين يديك.")
        else:
            st.error("❌ كود التفعيل غير صحيح.")
