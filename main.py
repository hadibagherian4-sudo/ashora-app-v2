import streamlit as st

# تنظیمات اصلی صفحه
st.set_page_config(page_title="موسسه عاشورا - پنل نخبگان", layout="centered")

# --- استایل جادویی برای تبدیل سایت به اپلیکیشن حرفه‌ای ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #f4f7f9;
    }

    /* حذف هدر پیش‌فرض استریم‌لیت */
    header {visibility: hidden;}
    .main .block-container {padding-top: 1rem;}

    /* هدر طلایی/سرمه‌ای طرح شما */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        padding: 30px 20px;
        border-radius: 0 0 40px 40px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        margin-bottom: 25px;
        text-align: center;
    }

    /* کارت‌های مدرن و شیشه‌ای (Glassmorphism) */
    .card {
        background: white;
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 20px;
        border-right: 12px solid #fbbf24; /* نوار طلایی */
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        position: relative;
    }

    .badge-status {
        background: #fef3c7;
        color: #92400e;
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 11px;
        font-weight: 900;
    }

    .star-rating {
        color: #fbbf24;
        font-size: 18px;
    }

    /* دکمه‌های اکشن */
    .action-btn {
        background: #1e3a8a;
        color: white !important;
        padding: 8px 20px;
        border-radius: 12px;
        text-decoration: none;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }

    /* سیستم ناوبری پایین (Bottom Nav) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: white;
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.05);
        z-index: 999;
    }
    .nav-item { text-align: center; color: #64748b; font-size: 10px; }
    .nav-item.active { color: #1e3a8a; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- دیتابیس موقت در حافظه ---
if 'data' not in st.session_state:
    st.session_state.data = [
        {"title": "روش‌های نوین تثبیت خاک", "unit": "فنی مهندسی", "score": 4.9, "status": "تایید شده", "date": "1402/10/24"},
        {"title": "بهینه‌سازی مصرف سوخت ماشین‌آلات", "unit": "ماشین‌آلات", "score": 4.2, "status": "در حال داوری", "date": "1402/10/25"}
    ]

# --- هدر ثابت ---
st.markdown("""
    <div class="app-header">
        <img src="https://img.icons8.com/color/96/000000/shield.png" width="50"><br>
        <h2 style='margin:10px 0 0; font-weight:900;'>سامانه مدیریت نخبگان عاشورا</h2>
        <p style='opacity:0.8; font-size:14px;'>میز هوشمند ارزیابی و تولید محتوا</p>
    </div>
""", unsafe_allow_html=True)

# --- منوی انتخاب صفحات (با دکمه‌های زیبا) ---
page = st.radio("", ["📺 ویترین محتوا", "➕ ارسال سناریو", "📊 پروفایل و امتیازها"], horizontal=True)

st.markdown("---")

if page == "📺 ویترین محتوا":
    st.markdown("### 🔍 برترین‌های هفته")
    for item in st.session_state.data:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="badge-status">{item['status']}</span>
                <span style="font-size:11px; color:#94a3b8;">{item['date']}</span>
            </div>
            <h3 style="margin:15px 0 5px 0; color:#0f172a;">{item['title']}</h3>
            <p style="font-size:13px; color:#64748b;">واحد سازمانی: {item['unit']}</p>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:15px;">
                <div class="star-rating">{'⭐' * int(item['score'])} <span style="color:#0f172a; font-size:14px;">{item['score']}</span></div>
                <a href="#" class="action-btn">مشاهده جزئیات</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "➕ ارسال سناریو":
    st.markdown("### 📝 ثبت تجربه فنی جدید")
    with st.container():
        title = st.text_input("عنوان موضوع (چالش فنی)")
        unit = st.selectbox("واحد مربوطه", ["فنی مهندسی", "ماشین‌آلات", "اجرایی", "HSE"])
        content = st.text_area("شرح کامل سناریو یا راهکار")
        file = st.file_uploader("آپلود مستندات (ویدئو/عکس)")
        
        if st.button("🚀 ارسال برای کمیته داوری"):
            new_item = {"title": title, "unit": unit, "score": 0.0, "status": "در انتظار", "date": "1402/10/26"}
            st.session_state.data.append(new_item)
            st.success("حاجی دمت گرم، سناریو فرستاده شد برای نخبگان سطح A.")
            st.balloons()

elif page == "📊 پروفایل و امتیازها":
    st.markdown("### 🏆 شناسنامه نخبگی شما")
    col1, col2 = st.columns(2)
    col1.metric("کل امتیاز کسب شده", "1,250", "+12")
    col2.metric("رتبه در موسسه", "4", "از 120")
    
    st.markdown("""
    <div class="card" style="border-right-color: #1e3a8a; text-align:center;">
        <h4>تعداد محتوای تایید شده</h4>
        <h2 style="color:#1e3a8a;">14</h2>
        <p style="font-size:12px;">شما در زمره <b>5 درصد برتر</b> نخبگان موسسه هستید.</p>
    </div>
    """, unsafe_allow_html=True)

# --- شبیه‌ساز Bottom Nav در انتهای صفحه ---
st.markdown("""
    <div style="height: 100px;"></div>
    <div class="nav-bar">
        <div class="nav-item active">🏠<br>داشبورد</div>
        <div class="nav-item">📚<br>کتابخانه</div>
        <div class="nav-item">🤖<br>دستیار</div>
        <div class="nav-item">👤<br>پروفایل</div>
    </div>
""", unsafe_allow_html=True)
