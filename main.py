import streamlit as st
import base64
import os

# --- تنظیمات سیستمی ---
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- توابع گرافیکی ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

img_logo = get_image_base64("logo.png")
img_tech = get_image_base64("tech_manager.jpg")
img_highway = get_image_base64("highway_site.jpg")

# --- لیست جدید ۱۴ کمیته تخصصی ---
COMMITTEES = [
    "۱. کمیته معماری و منظر",
    "۲. کمیته فنی و مهندسی",
    "۳. کمیته برنامه‌ریزی و مدیریت پروژه",
    "۴. کمیته کنترل پروژه",
    "۵. کمیته نقشه‌برداری و فتوگرامتری",
    "۶. کمیته بتن",
    "۷. کمیته هوش مصنوعی",
    "۸. کمیته ICT",
    "۹. کمیته نگهداری و ماشین‌آلات (نت)",
    "۱۰. کمیته کنترل کیفیت (QC)",
    "۱۱. کمیته HSSE",
    "۱۲. کمیته BIM",
    "۱۳. کمیته آسفالت",
    "۱۴. کمیته مالی و حسابداری"
]

# قالب‌های فایل
FILE_TYPES = ["ویدیو آموزشی", "پادکست فنی", "عکس/اینفوگرافیک", "مستندات PDF"]

# --- دیتابیس مجازی ---
if 'db' not in st.session_state:
    st.session_state.db = [
        {"id": 1, "title": "گزارش ایمنی محور شمال", "status": "در انتظار ارجاع", "sender": "مهندسین پروژه"}
    ]
if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'role' not in st.session_state: st.session_state.role = "guest"

# --- CSS مدرن (رنگ سفید روشن + فونت B Nazanin) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');

    /* شبیه‌سازی فونت B Nazanin با فونت‌های استاندارد وب فارسی */
    html, body, [class*="css"] {{
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif;
        direction: rtl; 
        text-align: right;
        background-color: #ffffff !important; /* رنگ بک‌گراند کاملاً سفید */
    }}
    
    .main {{ background-color: #ffffff; }}
    header, footer {{visibility: hidden !important;}}
    .block-container {{padding-top: 0rem;}}

    /* هدر سامانه (رنگ سرمه‌ای تیره با فونت خوانا) */
    .app-header {{
        background: #002d5b; color: white; padding: 25px;
        border-radius: 0 0 20px 20px; text-align: center;
        margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    /* کارت‌های سفید با حاشیه ظریف */
    .bright-card {{
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 15px; 
        padding: 20px;
        margin: 15px 0; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-right: 8px solid #002d5b;
    }}

    /* باکس کپچا */
    .captcha-style {{
        background: #f1f5f9; border: 1px dashed #64748b;
        padding: 10px; text-align: center; border-radius: 8px;
        font-weight: bold; font-size: 22px; color: #1e293b;
    }}

    /* استایل دکمه‌های آبی سامانه */
    .stButton>button {{
        background: #007bff; color: white; border-radius: 10px;
        width: 100%; height: 48px; font-weight: bold; border: none;
    }}
    
    .nav-bar {{
        position: fixed; bottom: 0; left: 0; right: 0; background: white;
        display: flex; justify-content: space-around; padding: 12px;
        border-top: 1px solid #e2e8f0; z-index: 1000;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ۱. مراحل ورود (Light Theme Login)
# ---------------------------------------------------------

if st.session_state.step in ["welcome", "login", "verify"]:
    st.markdown(f'<div class="app-header"><img src="{img_logo}" width="80"><h2>سامانه جامع محتوای عاشورا</h2></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="bright-card" style="max-width:500px; margin:auto; border-right:none; border-top:6px solid #002d5b;">', unsafe_allow_html=True)
    
    if st.session_state.step == "welcome":
        st.markdown("<h3 style='text-align:center;'>ورود به درگاه کاربری</h3>", unsafe_allow_html=True)
        choice = st.selectbox("لطفاً نقش خود را انتخاب فرمایید:", ["انتخاب کنید...", "پرسنل پروژه", "مدیر تولید محتوا (Manager)", "کمیته نخبگان (داور)"])
        if choice != "انتخاب کنید...":
            if "مدیر" in choice: st.session_state.role = "manager"
            elif "نخبگان" in choice: st.session_state.role = "referee"
            else: st.session_state.role = "user"
            
            if st.button("ادامه مسیر ورود"): 
                st.session_state.step = "login"
                st.rerun()

    elif st.session_state.step == "login":
        st.markdown("<h4 style='text-align:center;'>احراز هویت پیامکی</h4>", unsafe_allow_html=True)
        st.text_input("شماره موبایل سازمانی :", placeholder="09xxxxxxxxx")
        st.markdown('<div class="captcha-style"> r H o V N 🔄 </div>', unsafe_allow_html=True)
        st.text_input("کد امنیتی بالا را وارد کنید:")
        if st.button("درخواست کد فعال‌سازی"): 
            st.session_state.step = "verify"
            st.rerun()

    elif st.session_state.step == "verify":
        st.markdown("<h4 style='text-align:center;'>تایید نهایی</h4>", unsafe_allow_html=True)
        st.text_input("کد فعال‌سازی پیامک شده را وارد کنید:", type="password")
        if st.button("ورود به داشبورد محتوای عاشورا"):
            st.session_state.step = "dashboard"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ۲. داشبورد عملیاتی (White Mode Dashboard)
# ---------------------------------------------------------

elif st.session_state.step == "dashboard":
    # هدر داشبورد
    st.markdown(f"""
    <div style="background:#ffffff; border-bottom:1px solid #edf2f7; padding:15px 25px; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:14px; color:#002d5b; font-weight:bold;">نقش کاربر: {st.session_state.role} | خوش آمدید 👤</div>
        <img src="{img_logo}" width="45">
    </div>
    <div style="background:#002d5b; color:white; padding:8px; text-align:center; font-weight:bold;">سامانه جامع محتوای عاشورا</div>
    """, unsafe_allow_html=True)

    # الف) پورتال پرسنل (User)
    if st.session_state.role == "user":
        tab1, tab2 = st.tabs(["🏛️ ویترین محتوا", "➕ ارسال محتوا"])
        with tab2:
            st.markdown('<div class="bright-card">', unsafe_allow_html=True)
            st.markdown("##### ثبت سناریو جدید")
            st.text_input("عنوان موضوع سناریو :")
            st.selectbox("حیطه تخصصی :", COMMITTEES) # استفاده از لیست جدید ۱۴ تایی
            st.selectbox("نوع محتوا :", FILE_TYPES)
            st.file_uploader("بارگذاری فایل مربوطه")
            st.text_area("توضیحات تکمیلی فنی :")
            if st.button("ارسال محتوا به دبیرخانه"):
                st.success("محتوا با موفقیت ثبت گردید.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ب) پورتال مدیر (Manager) - طبق اصلاحیه درخواستی شما
    elif st.session_state.role == "manager":
        st.markdown("<h3 style='text-align:center; padding:20px;'>کارتابل مدیریت ارجاع</h3>", unsafe_allow_html=True)
        st.info("در این بخش محتواهای ارسالی پرسنل را بررسی و به کمیته‌های تخصصی ارجاع دهید.")
        
        # نمایش موارد در انتظار ارجاع
        pending = [i for i in st.session_state.db if i["status"] == "در انتظار ارجاع"]
        if pending:
            for item in pending:
                st.markdown(f'<div class="bright-card"><b>عنوان سناریو: {item["title"]}</b><br>فرستنده: واحد مهندسی پروژه</div>', unsafe_allow_html=True)
                
                # متن دقیق درخواستی شما: "ارجاع به کمیته تخصصی:"
                selected_ref = st.selectbox("ارجاع به کمیته تخصصی:", COMMITTEES, key=f"mgr_list_{item['id']}")
                
                if st.button(f"تایید و ارجاع به {selected_ref.split('.')[-1]}", key=f"btn_mgr_{item['id']}"):
                    st.success(f"محتوای مورد نظر با موفقیت به {selected_ref} ارجاع گردید.")
        else:
            st.warning("در حال حاضر مورد جدیدی برای ارجاع وجود ندارد.")

    # ج) پورتال داوران (Referee)
    elif st.session_state.role == "referee":
        st.subheader("میز ارزیابی تخصصی داوران")
        committee_role = st.selectbox("شما عضو کدام کمیته هستید؟", COMMITTEES)
        st.markdown(f'<div class="bright-card">امتیازدهی نهایی به سناریوها در حیطه <b>{committee_role}</b></div>', unsafe_allow_html=True)
        st.slider("امتیاز از ۰ تا ۱۰۰ :", 0, 100, 90)
        if st.button("ثبت امتیاز و انتشار"):
            st.balloons()
            st.success("امتیاز ثبت شد.")

    # --- ناوبری پایین صفحه ---
    st.markdown("""
    <div style="height: 100px;"></div>
    <div class="nav-bar">
        <div style="text-align:center; color:#002d5b; font-weight:bold;">🏛️<br><span style="font-size:10px;">داشبورد</span></div>
        <div style="text-align:center; color:grey;">📚<br><span style="font-size:10px;">آرشیو</span></div>
        <div style="text-align:center; color:grey;">👤<br><span style="font-size:10px;">پروفایل</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج از سیستم"):
        st.session_state.step = "welcome"
        st.session_state.role = "guest"
        st.rerun()
