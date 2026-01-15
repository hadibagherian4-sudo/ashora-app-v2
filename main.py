import streamlit as st
import base64
import os

# تنظیمات اصلی صفحه
st.set_page_config(page_title="سامانه جامع نخبگان - موسسه عاشورا", layout="centered")

# --- تابع تبدیل عکس‌های لوکال به فرمت وب برای نمایش در HTML ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

# لود کردن فایل‌های گرافیکی شما
img_logo = get_image_base64("logo.png")  # همان لوگوی ستاره‌ای سبز
img_ai = get_image_base64("ai_assist.jpg") # مهندس کلاه آبی
img_bg = get_image_base64("digital_bg.jpg") # پس‌زمینه نئونی
img_highway = get_image_base64("highway_site.jpg") # اتوبان
img_welding = get_image_base64("welding.jpg") # جوشکاری
img_tech = get_image_base64("tech_manager.jpg") # مهندس با تبلت

# --- CSS اختصاصی برای استایل سازمان و موبایلی کردن ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700;900&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl; text-align: right; background-color: #f8fafc;
    }}
    header, footer, [data-testid="stSidebarNav"] {{visibility: hidden !important; height:0px;}}
    .block-container {{padding: 0 !important;}}

    /* هدر سامانه با لوگو */
    .app-nav {{
        background-color: #002d5b; color: white; display: flex; 
        justify-content: space-between; padding: 10px 20px; align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    
    .nav-logo {{ width: 45px; }}

    /* بنر طلایی */
    .title-banner {{
        background: linear-gradient(90deg, #1e3a8a, #002d5b); color: white;
        text-align: center; padding: 18px; font-weight: 900; font-size: 1.1rem;
        border-top: 2px solid #fbbf24;
    }}

    /* کارت‌های مشابه طرح عکس موبایلی شما */
    .standard-card {{
        background: white; border-radius: 22px; padding: 18px;
        margin: 15px; border-right: 12px solid #fbbf24;
        box-shadow: 0 5px 15px rgba(0,0,0,0.06); position: relative;
    }}
    
    .status-lbl {{
        position: absolute; top: 15px; left: 15px; background: #fef3c7;
        color: #92400e; padding: 3px 12px; border-radius: 30px; font-size: 10px; font-weight: 900;
    }}

    /* نوار پایین */
    .bottom-menu {{
        position: fixed; bottom: 0; width: 100%; background: #ffffff;
        display: flex; justify-content: space-around; padding: 12px;
        border-top: 1px solid #e2e8f0; z-index: 999;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
    }}
    .menu-icon {{ color: #94a3b8; font-size: 10px; text-align: center; font-weight: 700; }}
    .active-icon {{ color: #1e3a8a; font-weight: 900; }}

    /* صفحه ورود نئونی */
    .landing {{
        background: linear-gradient(180deg, #001f3f 0%, #002d5b 100%);
        height: 100vh; color: white; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }}
</style>
""", unsafe_allow_html=True)

# سیستم مدیریت ورود و نقش‌ها (Login Session)
if 'status' not in st.session_state:
    st.session_state.status = "portal"

# ۱. پورتال ورود اختصاصی با لوگوی سبز مؤسسه
if st.session_state.status == "portal":
    st.markdown(f"""
    <div class="landing">
        <img src="{img_logo}" style="width:140px; margin-bottom:20px;">
        <h2 style='margin:0; font-weight:900;'>سامانه نخبگان فنی عاشورا</h2>
        <p style='opacity:0.7; font-size:14px; margin-bottom:40px;'>هلدینگ تخصصی راه و شهرسازی</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:-200px;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button(" ورود نخبگان فنی (داوران) "):
            st.session_state.status = "admin"
            st.rerun()
    with c2:
        if st.button(" ورود پرسنل و مهندسین "):
            st.session_state.status = "user"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ۲. داشبورد عملیاتی
else:
    # هدر داشبورد با لوگوی کوچک
    st.markdown(f"""
    <div class="app-nav">
        <div>🔍 &nbsp; 🔔 &nbsp; <span style='font-size:20px;'>☰</span></div>
        <div style="display:flex; align-items:center;">
            <span style="font-size:13px; margin-left:12px; font-weight:bold; letter-spacing:-0.5px;">موسسه عاشورا</span>
            <img src="{img_logo}" class="nav-logo">
        </div>
    </div>
    <div class="title-banner">سامانه سناریو و ارزیابی و ارتقای محتوا</div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["📲 ویترین سناریوها", "🖊️ ثبت چالش جدید"])

    with t1:
        # کارت ۱ با عکس مهندس و بیل مکانیکی
        st.markdown(f"""
        <div class="standard-card">
            <div class="status-lbl">در انتظار ارزیابی</div>
            <div style="display:flex; align-items:center; margin-top:15px;">
                <img src="{img_tech}" style="width:100px; height:100px; border-radius:18px; object-fit:cover;">
                <div style="margin-right:15px; flex:1;">
                    <h4 style="margin:0; font-size:14px; font-weight:900; color:#002d5b;">سناریو: تکنولوژی آسفالت حفاظتی (SMA)</h4>
                    <p style="font-size:11px; color:#64748b; margin:5px 0;">فرستنده: بخش فنی مهندسی | جاده ساوه</p>
                    <div style="font-size:13px; color:#fbbf24;">امتیاز پیشنهادی: <span style="font-weight:900; color:black;">۹۲</span> ⭐⭐⭐⭐⭐</div>
                </div>
            </div>
            <button style="background:#002d5b; color:white; width:100%; border:none; padding:10px; border-radius:12px; margin-top:15px; font-weight:bold; font-size:13px;">مشاهده پرونده کامل</button>
        </div>
        """, unsafe_allow_html=True)

        # کارت ۲ با عکس اتوبان
        st.markdown(f"""
        <div class="standard-card" style="border-right-color:#10b981;">
            <div class="status-lbl" style="background:#d1fae5; color:#065f46;">منتشر شده</div>
            <div style="display:flex; align-items:center; margin-top:15px;">
                <img src="{img_highway}" style="width:100px; height:100px; border-radius:18px; object-fit:cover;">
                <div style="margin-right:15px; flex:1;">
                    <h4 style="margin:0; font-size:14px; font-weight:900; color:#002d5b;">درس‌آموخته: مدیریت نشست زمین در آزادراه‌ها</h4>
                    <p style="font-size:11px; color:#64748b; margin:5px 0;">مشاهده شده توسط ۳۵۰ کاربر</p>
                    <div style="font-size:13px; color:#fbbf24;">امتیاز نخبگان: <span style="font-weight:900; color:black;">۹۸</span> ⭐⭐⭐⭐⭐</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ناوبری پایینی
    st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="bottom-menu">
        <div class="menu-icon">👤<br>دستیار من</div>
        <div class="menu-icon active-icon">⭐<br>نخبگان</div>
        <div class="menu-icon">📂<br>آررشیو</div>
        <div class="menu-icon" style="color:#e11d48;" onclick="window.location.reload();">🚪<br>خروج</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("خروج از سیستم"):
        st.session_state.status = "portal"
        st.rerun()
