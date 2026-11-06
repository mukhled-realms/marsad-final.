import streamlit as st

def show_enterprise_marsad():
    """
    منصة مرصد (v6.1 Enterprise Edition) - الطبعة الفاخرة
    تصميم داكن مع لمسات ذهبية، أسعار استثمارية استراتيجية، وجدار دفع بنكي.
    تم تصحيح الأرقام (ROI) لتكون منطقية (توفير 5 أضعاف).
    """
    
    # إعداد الصفحة وتصميم الـ CSS الفاخر (Dark Mode + Gold Accents)
    st.markdown("""
        <style>
        .stApp {
            background-color: #0b0f19;
            color: #f8fafc;
        }
        .hero-container {
            background: linear-gradient(135deg, #111827 0%, #030712 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            border: 1px solid #d4af37;
            box-shadow: 0 10px 25px -5px rgba(212, 175, 55, 0.1);
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .hero-title {
            font-size: 2.8rem;
            font-weight: 900;
            color: #d4af37;
            margin-bottom: 1rem;
            letter-spacing: -0.025em;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: #94a3b8;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f1f5f9;
            border-bottom: 2px solid #1e293b;
            padding-bottom: 0.75rem;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
        }
        .case-card {
            background-color: #111827;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-right: 4px solid #d4af37;
        }
        .pricing-card-gold {
            background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
            border: 2px solid #d4af37;
            border-radius: 16px;
            padding: 2.5rem 1.5rem;
            text-align: center;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
            position: relative;
        }
        .pricing-card-standard {
            background-color: #111827;
            border: 1px solid #374151;
            border-radius: 16px;
            padding: 2.5rem 1.5rem;
            text-align: center;
        }
        .price-tag {
            font-size: 2.2rem;
            font-weight: 800;
            color: #d4af37;
            margin: 1rem 0;
        }
        .roi-badge {
            background-color: rgba(212, 175, 55, 0.15);
            color: #d4af37;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            display: inline-block;
            margin-top: 1rem;
            border: 1px solid rgba(212, 175, 55, 0.3);
        }
        .paywall-box {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border: 2px solid #d4af37;
            padding: 2.5rem;
            border-radius: 16px;
            text-align: center;
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. قسم Hero: قصة المؤسس الفخمة ---
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">مرصد | المنهجية السيادية لمنع الخسائر التشغيلية</div>
            <div class="hero-subtitle">
                "عملت في قلب الميدان ورأيت بعيني كيف تتوقف أنظمة الكاشير لتترك 30 عربة تسوق مليئة بالبضائع؛ وكيف تُترك طبلية مبردة في المستودع الخلفي لـ 4 ساعات فتتلف بـ 140,000 ريال؛ وكيف تنفد المياه من الرفوف رغم امتلاء المستودعات. من هذا الوجع المالي الصامت.. وُلِدت <b>مرصد</b> لتعيد هندسة أرباحك."
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. المكتبة التشغيلية ودراسات الحالة ---
    st.markdown('<div class="section-header">🏛️ الأرشيف التشغيلي ودراسات الحالة الاستراتيجية</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class="case-card">
                <h3 style="color: #d4af37; margin-top:0;">📦 كارثة الطبالي (140,000 ر.س تلف)</h3>
                <p style="color: #cbd5e1;">التأخر في إدخال الطبالي المبردة للنظام يولد تلفاً صامتاً يلتهم رأس المال. نقدم بروتوكول فحص فوري يغلق هذه الثغرة خلال 15 دقيقة.</p>
            </div>
            <div class="case-card">
                <h3 style="color: #d4af37; margin-top:0;">🛒 عربات الكاشير المتروكة</h3>
                <p style="color: #cbd5e1;">تعطل سيستم الأسعار وقت الذروة يفقدك ولاء العملاء. نضع بين يديك بروتوكول طوارئ يدير الأزمة خلال أول 120 ثانية.</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="case-card">
                <h3 style="color: #d4af37; margin-top:0;">🚪 الحاوية الخلفية والفوارغ (هسر 8%+)</h3>
                <p style="color: #cbd5e1;">الكراتين المفتوحة والمهملة في الخلف تعني نزيفاً نقدياً مباشراً. نراقب الانكماش ونطبق منهجية 5 Whys لضبط المخزون.</p>
            </div>
            <div class="case-card">
                <h3 style="color: #d4af37; margin-top:0;">📊 المنهجية والمعايير (50 سؤال تشغيلي)</h3>
                <p style="color: #cbd5e1;">تغطية شاملة لـ 5 محاور (الرفوف، المستودع، الانكماش، العمليات، تجربة العميل) مع مؤشرات أداء (KPIs) ونمذجة Risk Score دقيقة.</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 3. جدول الأسعار الاستراتيجي بناءً على القيمة (ROI) ---
    st.markdown('<div class="section-header">💎 باقات الاستثمار التشغيلي (Value-Based Pricing)</div>', unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("""
            <div class="pricing-card-standard">
                <h3>التشخيص السريع</h3>
                <div class="price-tag">50,000 ر.س</div>
                <hr style="border-color: #374151;">
                <p style="color: #94a3b8; font-size: 0.95rem;">جلسة مكثفة لكشف الثغرات الحرجة في فرع رئيسي مع تقرير Risk Score تنفيذي.</p>
                <div class="roi-badge">تدفع 50 ألف ← توفر 250 ألف</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("اختيار باقة التشخيص", use_container_width=True, key="btn_p1"):
            st.session_state['selected_package'] = "باقة التشخيص السريع (50,000 ريال)"

    with p2:
        st.markdown("""
            <div class="pricing-card-gold">
                <span style="background: #d4af37; color: #000; padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800;">الأكثر طلباً للمؤسسات ⭐</span>
                <h3 style="margin-top: 10px;">التدقيق الشامل</h3>
                <div class="price-tag">150,000 ر.س</div>
                <hr style="border-color: #d4af37;">
                <p style="color: #cbd5e1; font-size: 0.95rem;">زيارة ميدانية وتطبيق 50 سؤال تقييم، هيكلة المستودعات ومنع الخسائر جذرياً.</p>
                <div class="roi-badge">تدفع 150 ألف ← توفر 750 ألف</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("اختيار التدقيق الشامل", use_container_width=True, key="btn_p2"):
            st.session_state['selected_package'] = "باقة التدقيق الشامل (150,000 ريال)"

    with p3:
        st.markdown("""
            <div class="pricing-card-standard">
                <h3>الامتثال السنوي</h3>
                <div class="price-tag">350,000 ر.س <span style="font-size:1rem; color:#94a3b8;">/سنوياً</span></div>
                <hr style="border-color: #374151;">
                <p style="color: #94a3b8; font-size: 0.95rem;">شراكة استراتيجية، تدقيق دوري ربع سنوي، شهادة اعتماد مرصد، وإشراف مباشر.</p>
                <div class="roi-badge">تدفع 350 ألف ← توفر 1.75 مليون</div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("اختيار الامتثال السنوي", use_container_width=True, key="btn_p3"):
            st.session_state['selected_package'] = "باقة الامتثال السنوي (350,000 ريال/سنوياً)"

    # --- 4. جدار الدفع (Paywall) الحصري ---
    st.markdown('<div class="section-header">🔒 بوابة تفعيل العضوية المؤسسية</div>', unsafe_allow_html=True)
    
    selected = st.session_state.get('selected_package', 'لم يتم اختيار الباقة بعد (يرجى الضغط على زر اختيار الباقة أعلاه)')
    
    st.markdown(f"""
        <div class="paywall-box">
            <h2 style="color: #d4af37; margin-bottom: 0.5rem;">الباقة المحددة: {selected}</h2>
            <p style="color: #94a3b8; margin-bottom: 1.5rem;">
                لتفعيل العضوية واعتماد الارتباط بـ "مرصد"، يرجى إتمام التحويل البنكي للحساب الرسمي للشركة.
            </p>
            <div style="background-color: #0b0f19; padding: 1.5rem; border-radius: 8px; border: 1px dashed #d4af37; display: inline-block; min-width: 350px; margin-bottom: 1.5rem;">
                <p style="color: #f8fafc; font-weight: bold; margin: 0;">اسم الحساب: مؤسسة مرصد الاستثمارية</p>
                <p style="color: #d4af37; font-family: monospace; font-size: 1.2rem; margin: 0.5rem 0 0 0;">IBAN: SA03 8000 0000 0000 0000 0000</p>
            </div>
            <p style="color: #cbd5e1; font-size: 0.9rem;">
                بعد إتمام التحويل، يرجى إرسال الإيصال للشريك المؤسس د. مخلد لتفعيل لوحة التحكم والصلاحيات السيادية فوراً.
            </p>
        </div>
    """, unsafe_allow_html=True)

# طريقة الاستدعاء في ملف app.py الرئيسي:
# show_enterprise_marsad()
