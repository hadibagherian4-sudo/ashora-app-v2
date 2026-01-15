import streamlit as st
import base64
import os

# --- تنظیمات سیستمی سامانه ---
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- تابع گرافیکی برای تبدیل تصاویر به کد ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return "https://via.placeholder.com/300"

img_logo = get_image_base64("logo.png")
img_tech = get_image_base64("tech_manager.jpg")
img_highway = get_image_base64("highway_site.jpg")
img_welding = get_image_base64("welding.jpg")

# --- لیست نهایی ۱۴ کمیته تخصصی مصوب ---
COMMITTEES = [
    "۱. کمیته معماری و منظر", "۲. کمیته فنی و مهندسی", "۳. کمیته برنامه‌ریزی و مدیریت پروژه",
    "۴. کمیته کنترل پروژه", "۵. کمیته نقشه‌برداری و فتوگرامتری", "۶. کمیته بتن",
    "۷. کمیته هوش مصنوعی", "۸. کمیته ICT", "۹. کمیته نگهداری و ماشین‌آلات (نت)",
    "۱۰. کمیته کنترل کیفیت (QC)", "۱۱. کمیته HSSE", "۱۲. کمیته BIM",
    "۱۳. کمیته آسفالت", "۱۴. کمیته مالی و حسابداری"
]

FILE_TYPES = ["ویدیو آموزشی", "پادکست فنی", "عکس/اینفوگرافیک", "مستندات PDF"]

# --- پایگاه داده مجازی جهت ویترین محتوا ---
if 'db' not in st.session_state:
    st.session_state.db = [
        {
            "id": 1, "title": "گزارش تخصصی بهسازی زیرسازی محور شمال", 
            "status": "انتشار یافته", "category": "۱۳. کمیته آسفالت", 
            "type": "سند متنی PDF", "score": 98, "img": img_highway
        },
        {
            "id": 2, "title": "متدولوژی نوین جوشکاری اسکلت فلزی", 
            "status": "انتشار یافته", "category": "۲. کمیته فنی و مهندسی", 
            "type": "ویدیو آموزشی", "score": 92, "img": img_welding
        },
        {
            "id": 3, "title": "مدیریت ماشین‌آلات هوشمند کارگاهی", 
            "status": "انتشار یافته", "category": "۹. کمیته نگهداری و ماشین‌آلات (نت)", 
            "type": "اینفوگرافیک", "score": 85, "img": img_tech
        }
    ]

if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'role' not in st.session_state: st.session_state.role = "guest"

# --- استایل حرفه‌ای: پس‌زمینه سفید روشن و نوشتار مشکی تیره ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');

    /* اجبار به پس‌زمینه سفید */
    .stApp {{ background-color: #ffffff !important; }}

    /* تیره کردن تمام متون سامانه */
    html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #111827 !important; /* رنگ مشکی تیره و خوانا */
    }}

    header, footer {{visibility: hidden !important; height:0px;}}
    .block-container {{padding-top: 0rem !important;}}

    /* هدر سرمه‌ای با متن سفید (جهت کنتراست) */
    .app-header {{
        background: #002d5b; padding: 25px;
        border-radius: 0 0 25px 25px; text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    .app-header h2, .app-header p {{ color: white !important; }}

    /* کارت‌های ویترین محتوا */
    .content-card {{
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 18px;
        margin-bottom: 22px;
        overflow: hidden;
        border-right: 12px solid #002d5b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }}
    .card-title {{ color: #002d5b !important; font-weight: bold; margin: 0; font-size: 16px; }}
    .card-info {{ color: #374151 !important; font-size: 12px; margin-top: 5px; }}
    
    /* استایل دکمه‌ها */
    .stButton>button {{
        background: #007bff; color: #ffffff !important; border-radius: 12px;
        width: 100%; height: 50px; font-weight: bold; border: none; font-size: 16px;
    }}

    /* استایل کپچا */
    .captcha-container {{
        background: #f3f4f6; border: 1px dashed #9ca3af; padding: 12px;
        text-align: center; border-radius: 10px; color: #111827 !important;
        font-weight: bold; font-size: 24px; margin-bottom: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# بخش اول: درگاه‌های ورود (Login Flows)
# ---------------------------------------------------------

if st.session_state.step in ["welcome", "login", "verify"]:
    st.markdown(f'<div class="app-header"><img src="{img_logo}" width="85"><h2>سامانه جامع محتوای عاشورا</h2></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div style="background:white; padding:30px; border-radius:18px; border:1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.05); max-width:500px; margin:auto; margin-top:25px;">', unsafe_allow_html=True)
        
        if st.session_state.step == "welcome":
            st.markdown("<h3 style='text-align:center;'>انتخاب درگاه ورود به سامانه</h3>", unsafe_allow_html=True)
            user_choice = st.selectbox("مقام ارجمند؛ نقش خود را تعیین فرمایید:", ["انتخاب کنید...", "مهندس / پرسنل اجرایی", "مدیر تولید محتوا (کارتابل ارجاع)", "داور فنی / کمیته نخبگان"])
            if user_choice != "انتخاب کنید...":
                if "مدیر" in user_choice: st.session_state.role = "manager"
                elif "داور" in user_choice: st.session_state.role = "referee"
                else: st.session_state.role = "user"
                if st.button("تایید و انتقال به درگاه احراز هویت"): st.session_state.step = "login"; st.rerun()

        elif st.session_state.step == "login":
            st.markdown("<b>شماره همراه سازمانی :</b>", unsafe_allow_html=True)
            st.text_input("Mobile", label_visibility="collapsed", placeholder="0912*******")
            st.markdown('<div class="captcha-container"> r H o V N 🔄 </div>', unsafe_allow_html=True)
            st.text_input("کد امنیتی را وارد نمایید:")
            if st.button("ارسال کد تایید پیامکی"): st.session_state.step = "verify"; st.rerun()

        elif st.session_state.step == "verify":
            st.markdown("<b>کد فعال‌سازی دریافت شده :</b>", unsafe_allow_html=True)
            st.text_input("Verification Code", type="password", label_visibility="collapsed")
            if st.button("ورود به پنل جامع محتوا"): st.session_state.step = "dashboard"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# بخش دوم: داشبورد عملیاتی (White Theme Dashboard)
# ---------------------------------------------------------

elif st.session_state.step == "dashboard":
    # هدر داشبورد با نام سامانه
    st.markdown(f"""
    <div style="background:#ffffff; padding:15px 25px; border-bottom:1px solid #e5e7eb; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:13px; color:#111827;">نقش کاربری: <b>{st.session_state.role}</b> | خوش‌ آمدید 👤</div>
        <img src="{img_logo}" width="42">
    </div>
    <div style="background:#002d5b; color:white; padding:12px; text-align:center; font-weight:bold; font-size:18px;">سامانه جامع محتوای عاشورا</div>
    """, unsafe_allow_html=True)

    # محتوای داشبورد بر اساس نقش کاربر
    if st.session_state.role == "user":
        t1, t2 = st.tabs(["🏛️ ویترین دروس‌آموخته (تایید شده)", "📥 ارسال سناریو و محتوای جدید"])
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            for item in st.session_state.db:
                st.markdown(f"""
                <div class="content-card">
                    <img src="{item['img']}" style="width:100%; height:165px; object-fit:cover;">
                    <div class="card-text-box" style="padding:15px;">
                        <h4 class="card-title">{item['title']}</h4>
                        <p class="card-info">کمیته مرجع: {item['category']} | فرمت رسانه: {item['type']}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                            <span style="font-weight:900; color:#111827; font-size:20px;">تراز علمی: {item['score']} ⭐</span>
                            <a href="#" style="background:#002d5b; color:white; padding:8px 20px; border-radius:10px; text-decoration:none; font-size:12px; font-weight:bold;">مشاهده و یادگیری</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with t2:
            st.write("##### میز کار ارسال محتوا")
            st.text_input("عنوان سناریو فنی یا موضوع آموزشی :")
            st.selectbox("کمیته تخصصی مورد نظر جهت داوری :", COMMITTEES)
            st.selectbox("قالب فایل ضمیمه :", FILE_TYPES)
            st.file_uploader("انتخاب فایل (ویدیو/صوت/PDF/تصویر)")
            if st.button("ثبت نهایی و ارسال به مدیریت تولید"):
                st.success("محتوای جناب‌عالی با موفقیت ثبت شد.")

    elif st.session_state.role == "manager":
        st.markdown("<h4 style='text-align:center; padding:20px; color:#002d5b;'>میز کارگزاری و ارجاع محتوا</h4>", unsafe_allow_html=True)
        st.info("مهندس گرامی؛ لطفاً محتوای درخواستی را به یکی از ۱۴ کمیته ذیل ارجاع فرمایید.")
        # شبیه‌سازی انتخاب و ارجاع
        st.markdown("<div style='background:white; padding:20px; border-radius:15px; border:1px solid #ddd;'>", unsafe_allow_html=True)
        st.write("📌 محتوا: <b>گزارش ایمنی محور شمال</b>", unsafe_allow_html=True)
        st.selectbox("ارجاع به کمیته تخصصی:", COMMITTEES)
        st.button("تایید و ارجاع نهایی به کمیته منتخب")
        st.markdown("</div>", unsafe_allow_html=True)

    # نوار هدایت پایین سامانه (Footer Nav)
    st.markdown("""
    <div style="height: 100px;"></div>
    <div style="position: fixed; bottom: 0; left: 0; right: 0; background: white; display: flex; justify-content: space-around; padding: 15px; border-top: 1px solid #e5e7eb; z-index: 1000; box-shadow: 0 -5px 15px rgba(0,0,0,0.05);">
        <div style="text-align:center; color:#002d5b; font-weight:bold; cursor:pointer;">🏠<br><span style="font-size:10px;">خانه</span></div>
        <div style="text-align:center; color:#9ca3af; cursor:pointer;">📚<br><span style="font-size:10px;">کتابخانه</span></div>
        <div style="text-align:center; color:#9ca3af; cursor:pointer;">⚙️<br><span style="font-size:10px;">تنظیمات</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج ایمن از سامانه"):
        st.session_state.step = "welcome"; st.rerun()
