import streamlit as st
import base64
import os

# تنظیمات اصلی با نام جدید
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- تابع گرافیکی برای تصاویر ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

img_logo = get_image_base64("logo.png")
img_highway = get_image_base64("highway_site.jpg")
img_tech = get_image_base64("tech_manager.jpg")
img_bg = get_image_base64("digital_bg.jpg")

# --- دسته‌بندی‌ها ---
CATEGORIES = ["عمومی", "فنی و مهندسی", "HSSE", "نیروی انسانی", "مدیریتی", "ماشین آلات"]

# --- سیستم مدیریت مراحل ورود ---
if 'step' not in st.session_state:
    st.session_state.step = "welcome" 

# --- CSS حرفه‌ای برای شبیه‌سازی تصاویر ارسالی شما ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }}
    header, footer {{visibility: hidden !important;}}
    .main {{ background: #f4f7f9; }}

    .blue-header {{
        background: linear-gradient(135deg, #1e3a8a 0%, #0d1b2a 100%);
        height: 250px; width: 100%; position: absolute; top: 0; left: 0; z-index: 0;
    }}

    .login-card {{
        background: white; border-radius: 15px; padding: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-top: 50px;
        border-top: 5px solid #1e3a8a; position: relative; z-index: 1;
    }}

    .captcha-box {{
        background: #f1f5f9; border: 1px dashed #cbd5e1; padding: 10px;
        text-align: center; border-radius: 10px; margin: 10px 0;
        font-family: 'Courier New', monospace; font-weight: bold; font-size: 20px; color: #334155;
    }}

    .stButton>button {{
        background: #007bff; color: white; border-radius: 10px; width: 100%; height: 45px;
        font-weight: bold; border: none; margin-top: 15px;
    }}

    .active-nav {{
        position: fixed; bottom: 0; width: 100%; background: white;
        display: flex; justify-content: space-around; padding: 15px;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.05); z-index: 999;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# لایه ۱: انتخاب نقش (با نام جدید سامانه)
# -----------------------------
if st.session_state.step == "welcome":
    st.markdown('<div class="blue-header"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1: st.image(img_logo if img_logo else "https://via.placeholder.com/80")
    with col2: st.subheader("سامانه جامع محتوای عاشورا")
    
    st.info("لطفاً سطح دسترسی خود را جهت ورود انتخاب نمایید:")
    role = st.selectbox("نقش کاربر:", ["انتخاب کنید...", "مهندس / پرسنل اجرایی", "مدیر تولید محتوا", "کمیته تخصصی (داور)"])
    if role != "انتخاب کنید...":
        st.session_state.role = role
        if st.button("تایید و مرحله بعد"):
            st.session_state.step = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# لایه ۲: فرم لاگین
# -----------------------------
elif st.session_state.step == "login":
    st.markdown('<div class="blue-header"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>ورود به سامانه جامع</h4>", unsafe_allow_html=True)
    
    mobile = st.text_input("شماره موبایل سازمانی :", placeholder="09xxxxxxxxx")
    st.markdown("<div class='captcha-box'> r H o V N 🔄 </div>", unsafe_allow_html=True)
    st.text_input("کد امنیتی تصویر :")
    
    if st.button("ارسال کد فعال‌سازی"):
        if mobile:
            st.session_state.step = "verify"
            st.rerun()
        else: st.warning("لطفاً شماره همراه را وارد کنید")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# لایه ۳: فعال‌سازی
# -----------------------------
elif st.session_state.step == "verify":
    st.markdown('<div class="blue-header"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card" style="max-width:450px; margin:auto;">', unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>تایید نهایی هویت</h4>", unsafe_allow_html=True)
    st.write("کد ۵ رقمی ارسال شده به پیام‌رسان یا پیامک را وارد نمایید:")
    
    st.text_input("کد تایید :", type="password")
    st.markdown("<div class='captcha-box' style='font-size:16px;'> S 8 Q 7 </div>", unsafe_allow_html=True)
    st.text_input("تکرار کد امنیتی :")
    
    if st.button("ورود به داشبورد محتوای عاشورا"):
        st.session_state.step = "dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# لایه ۴: داشبورد عملیاتی
# -----------------------------
elif st.session_state.step == "dashboard":
    # هدر رسمی با لوگو و نام اصلاح شده
    st.markdown(f"""
    <div style="background:#002d5b; color:white; padding:10px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #fbbf24;">
        <div style="font-size:12px;">خوش آمدید | کاربر سامانه 👤</div>
        <div style="display:flex; align-items:center;"><span style="font-size:14px; font-weight:bold;">سامانه جامع محتوای عاشورا</span> <img src="{img_logo}" width="30" style="margin-right:10px;"></div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📚 ویترین دانش", "🖊️ میز کار محتوا"])

    with tab1:
        # کارت ۱ با عکس جاده (highway_site)
        st.markdown(f"""
        <div style="background:white; border-radius:15px; margin:15px; overflow:hidden; border:1px solid #ddd; border-right: 10px solid #fbbf24;">
            <img src="{img_highway}" style="width:100%; height:140px; object-fit:cover;">
            <div style="padding:15px;">
                <h4 style="margin:0; color:#1e3a8a;">سناریو فنی: تثبیت خاک در محورهای صعب‌العبور</h4>
                <p style="font-size:11px; color:grey; margin:5px 0;">واحد: فنی و مهندسی | وضعیت: تایید نهایی</p>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:bold; color:#1e3a8a; font-size:18px;">۹۸ ⭐⭐⭐⭐⭐</span>
                    <button style="background:#1e3a8a; color:white; border:none; padding:5px 15px; border-radius:8px; font-size:11px;">مشاهده</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        # میز کار با عکس مدیر فنی (tech_manager)
        st.markdown(f"""
        <div style="background:white; border-radius:15px; margin:15px; padding:20px; display:flex; align-items:center; border-right: 8px solid #48bb78;">
            <img src="{img_tech}" style="width:80px; height:80px; border-radius:12px; object-fit:cover;">
            <div style="margin-right:15px; flex:1;">
                <h5 style="margin:0; font-weight:bold;">فرآیند تولید محتوا</h5>
                <p style="font-size:11px; color:#666;">مهندس گرامی؛ تجربیات و سناریوهای خود را از این بخش جهت داوری به سازمان ارسال نمایید.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("+ ارسال محتوای جدید به دبیرخانه"):
            st.info("فرم ثبت محتوا در حال بارگذاری است...")

    # ناوبری ثابت پایینی
    st.markdown("""
    <div style="height: 100px;"></div>
    <div class="active-nav">
        <div style="text-align:center; color:#1e3a8a; font-weight:bold;">🏠<br><span style="font-size:10px;">خانه</span></div>
        <div style="text-align:center; color:grey;">📈<br><span style="font-size:10px;">نتایج</span></div>
        <div style="text-align:center; color:grey;">⚙️<br><span style="font-size:10px;">پروفایل</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج ایمن از حساب"):
        st.session_state.step = "welcome"
        st.rerun()
