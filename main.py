import streamlit as st

# تنظیمات اولیه صفحه
st.set_page_config(page_title="سامانه مدیریت محتوا - موسسه عاشورا", layout="centered")

# بخش استایل اختصاصی برای شبیه سازی موبایل (سرمه‌ای و طلایی)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main { background-color: #f0f2f5; }
    
    /* هدر */
    .app-header {
        background: linear-gradient(90deg, #0d1b2a, #1e3a8a);
        color: white;
        padding: 25px;
        border-radius: 0 0 30px 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* کارت‌ها */
    .content-card {
        background: white;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border-right: 10px solid #fbbf24;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .status-badge {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 15px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .score-tag {
        color: #fbbf24;
        font-weight: bold;
        font-size: 1.2rem;
    }

    /* دکمه ثبت امتیاز */
    .stButton>button {
        background: #1e3a8a;
        color: white;
        border-radius: 15px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# هدر اصلی اپلیکیشن
st.markdown("""
    <div class="app-header">
        <h2 style='margin:0;'>سامانه ستاریو و ارزیابی محتوا</h2>
        <p style='margin:5px 0 0; opacity:0.8;'>مدیریت هوشمند محتوای آموزشی - موسسه عاشورا</p>
    </div>
""", unsafe_allow_html=True)

# منوی پایین (Tabs)
tab1, tab2, tab3 = st.tabs(["📺 ویترین محتوا", "➕ ارسال سناریو", "⚖️ میز داوری"])

with tab1:
    st.markdown("### محتواهای در انتظار تایید")
    
    # کارت ۱
    st.markdown("""
    <div class="content-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="status-badge">در حال بررسی</span>
            <span style="font-size:0.7rem; color:#888;">۱۴۰۲/۱۰/۲۴</span>
        </div>
        <h4 style="margin:15px 0 5px 0;">گزارش فنی: روش‌های برنامه‌ریزی پروژه</h4>
        <p style="font-size:0.85rem; color:#555;">واحد: فنی و مهندسی | فرستنده: مهندس باقریان</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px;">
            <span class="score-tag">امتیاز: ۹۸ ⭐</span>
            <button style="background:#1e3a8a; color:white; border:none; padding:8px 20px; border-radius:10px; font-size:0.8rem;">مشاهده جزئیات</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # کارت ۲
    st.markdown("""
    <div class="content-card" style="border-right-color: #10b981;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="status-badge" style="background:#d1fae5; color:#065f46;">منتشر شده</span>
            <span style="font-size:0.7rem; color:#888;">۱۴۰۲/۱۰/۱۵</span>
        </div>
        <h4 style="margin:15px 0 5px 0;">فیلم آموزشی: تکنیک‌های جوشکاری حرفه‌ای</h4>
        <p style="font-size:0.85rem; color:#555;">واحد: اجرایی | فرستنده: واحد آموزش</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px;">
            <span class="score-tag">امتیاز: ۸۵ ⭐⭐⭐⭐</span>
            <button style="background:#1e3a8a; color:white; border:none; padding:8px 20px; border-radius:10px; font-size:0.8rem;">مشاهده جزئیات</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.subheader("ثبت سناریوی جدید")
    st.text_input("نام و نام خانوادگی فرستنده")
    st.text_input("عنوان موضوع محتوا")
    st.selectbox("واحد مربوطه", ["فنی و مهندسی", "ماشین‌آلات", "مالی", "HSSE"])
    st.text_area("شرح کامل سناریو یا چالش آموزشی")
    st.file_uploader("آپلود مستندات (ویدئو/عکس)")
    if st.button("ارسال نهایی برای کمیته داوری"):
        st.success("محتوا با موفقیت ارسال شد.")

with tab3:
    st.subheader("پنل ارزیابی و امتیازدهی نخبگان")
    content_id = st.selectbox("انتخاب محتوا برای داوری", ["روش‌های برنامه‌ریزی", "تکنیک‌های جوشکاری"])
    score = st.slider("امتیاز فنی (۰ تا ۱۰۰)", 0, 100, 85)
    feedback = st.multiselect("نقاط قوت و بهبود", ["دقت علمی بالا", "بروزرسانی موضوع", "کیفیت بصری", "نوآوری"])
    if st.button("ثبت امتیاز و تایید انتشار"):
        st.balloons()
        st.info("امتیاز شما ثبت شد.")
