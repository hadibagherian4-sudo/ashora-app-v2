import streamlit as st
import base64
import os

# --- تنظیمات سیستمی ---
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- توابع گرافیکی برای تصاویر ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return "https://via.placeholder.com/300"

img_logo = get_image_base64("logo.png")
img_tech = get_image_base64("tech_manager.jpg")
img_highway = get_image_base64("highway_site.jpg")
img_welding = get_image_base64("welding.jpg")

# --- لیست ۱۴ کمیته تخصصی ---
COMMITTEES = [
    "۱. کمیته معماری و منظر", "۲. کمیته فنی و مهندسی", "۳. کمیته برنامه‌ریزی و مدیریت پروژه",
    "۴. کمیته کنترل پروژه", "۵. کمیته نقشه‌برداری و فتوگرامتری", "۶. کمیته بتن",
    "۷. کمیته هوش مصنوعی", "۸. کمیته ICT", "۹. کمیته نگهداری و ماشین‌آلات (نت)",
    "۱۰. کمیته کنترل کیفیت (QC)", "۱۱. کمیته HSSE", "۱۲. کمیته BIM",
    "۱۳. کمیته آسفالت", "۱۴. کمیته مالی و حسابداری"
]

# --- دیتابیس مجازی با ۳ سناریوی پیش‌فرض (ویترین محتوا) ---
if 'db' not in st.session_state:
    st.session_state.db = [
        {
            "id": 1, 
            "title": "اصول بهسازی زیرسازی محور شمال-جنوب", 
            "status": "انتشار یافته", 
            "category": "۱۳. کمیته آسفالت", 
            "type": "گزارش PDF",
            "score": 98,
            "img": img_highway
        },
        {
            "id": 2, 
            "title": "تکنیک‌های نوین جوشکاری در اسکلت فلزی", 
            "status": "انتشار یافته", 
            "category": "۲. کمیته فنی و مهندسی", 
            "type": "ویدیو آموزشی",
            "score": 92,
            "img": img_welding
        },
        {
            "id": 3, 
            "title": "مدیریت یکپارچه تجهیزات با تبلت کارگاهی", 
            "status": "انتشار یافته", 
            "category": "۹. کمیته نگهداری و ماشین‌آلات (نت)", 
            "type": "اینفوگرافیک",
            "score": 85,
            "img": img_tech
        }
    ]

if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'role' not in st.session_state: st.session_state.role = "guest"

# --- CSS مدرن (رنگ سفید مطلق + فونت B Nazanin) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    
    /* اجبار به رنگ سفید برای بک‌گراند */
    .stApp {{
        background-color: #ffffff !important;
    }}
    
    html, body, [class*="css"] {{
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif;
        direction: rtl; text-align: right;
        color: #1a202c;
    }}
    
    header, footer {{visibility: hidden !important;}}
    .block-container {{padding-top: 0rem;}}

    /* هدر سرمه‌ای سامانه */
    .header-box {{
        background: #002d5b; color: white; padding: 25px;
        border-radius: 0 0 20px 20px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}

    /* کارت‌های ویترین محتوا */
    .showcase-card {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        margin-bottom: 20px;
        overflow: hidden;
        transition: transform 0.3s;
        border-right: 10px solid #002d5b;
    }}
    .showcase-card:hover {{ transform: scale(1.01); }}
    
    .card-img-box {{
        width: 100%; height: 160px; object-fit: cover;
    }}
    .card-text-box {{ padding: 15px; }}

    .stButton>button {{
        background: #007bff; color: white; border-radius: 10px;
        width: 100%; height: 48px; font-weight: bold; border: none;
    }}

    .bottom-navbar {{
        position: fixed; bottom: 0; left: 0; right: 0; background: white;
        display: flex; justify-content: space-around; padding: 12px;
        border-top: 1px solid #e2e8f0; z-index: 1000;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.05);
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# بخش ۱: پورتال ورود
# -----------------------------
if st.session_state.step in ["welcome", "login", "verify"]:
    st.markdown(f'<div class="header-box"><img src="{img_logo}" width="80"><h2>سامانه جامع محتوای عاشورا</h2></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div style="background:white; padding:30px; border-radius:15px; border:1px solid #edf2f7; box-shadow: 0 10px 30px rgba(0,0,0,0.05); max-width:500px; margin:auto; margin-top:20px;">', unsafe_allow_html=True)
        
        if st.session_state.step == "welcome":
            st.markdown("<h3 style='text-align:center;'>انتخاب درگاه کاربری</h3>", unsafe_allow_html=True)
            choice = st.selectbox("لطفاً نقش خود را تعیین فرمایید:", ["انتخاب کنید...", "مهندس/کارمند پروژه", "مدیر تولید محتوا", "داور / کمیته تخصصی"])
            if choice != "انتخاب کنید...":
                if "مدیر" in choice: st.session_state.role = "manager"
                elif "داور" in choice: st.session_state.role = "referee"
                else: st.session_state.role = "user"
                if st.button("تایید و ورود به صفحه احراز هویت"): st.session_state.step = "login"; st.rerun()

        elif st.session_state.step == "login":
            st.text_input("شماره موبایل :")
            st.markdown('<div style="background:#f7fafc; border:1px dashed #cbd5e0; padding:10px; text-align:center; font-weight:bold; font-size:20px; border-radius:8px;"> r H o V N 🔄</div>', unsafe_allow_html=True)
            st.text_input("کد امنیتی تصویر بالا:")
            if st.button("دریافت رمز موقت"): st.session_state.step = "verify"; st.rerun()

        elif st.session_state.step == "verify":
            st.text_input("کد فعال‌سازی :", type="password")
            if st.button("ورود به پنل کاربری"): st.session_state.step = "dashboard"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# بخش ۲: داشبورد اصلی
# -----------------------------
elif st.session_state.step == "dashboard":
    # هدر بالایی
    st.markdown(f"""
    <div style="background:#ffffff; padding:10px 25px; border-bottom:1px solid #edf2f7; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:12px; color:#4a5568;">نقش کاربری: <b>{st.session_state.role}</b> | جناب‌عالی خوش‌ آمدید 👤</div>
        <img src="{img_logo}" width="40">
    </div>
    <div style="background:#002d5b; color:white; padding:10px; text-align:center; font-weight:bold;">سامانه جامع محتوای عاشورا</div>
    """, unsafe_allow_html=True)

    # --- صفحات بر اساس نقش ---
    
    if st.session_state.role == "user":
        t1, t2 = st.tabs(["🏛️ ویترین محتوا (تایید شده)", "📥 ثبت سناریو جدید"])
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            # نمایش ۳ سناریو در ویترین
            published = [i for i in st.session_state.db if i["status"] == "انتشار یافته"]
            for item in published:
                st.markdown(f"""
                <div class="showcase-card">
                    <img src="{item['img']}" class="card-img-box">
                    <div class="card-text-box">
                        <h4 style="margin:0; color:#002d5b;">{item['title']}</h4>
                        <p style="font-size:11px; color:#718096; margin-top:5px;">بخش: {item['category']} | قالب: {item['type']}</p>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#002d5b; font-size:18px;">امتیاز: {item['score']} ⭐</span>
                            <a href="#" style="background:#002d5b; color:white; padding:5px 15px; border-radius:8px; text-decoration:none; font-size:11px;">مطالعه فایل</a>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with t2:
            st.write("##### فرم ارسال سناریوی فنی")
            st.text_input("عنوان موضوع سناریو :")
            st.selectbox("کمیته تخصصی ارجاع :", COMMITTEES)
            st.file_uploader("بارگذاری فایل اصلی (فیلم/پادکست/سند)")
            if st.button("ارسال نهایی"): st.success("با موفقیت به مدیریت تولید محتوا ارسال شد.")

    elif st.session_state.role == "manager":
        st.markdown("<h4 style='text-align:center; padding:20px;'>کارتابل مدیریت ارجاع و عارضه‌یابی</h4>", unsafe_allow_html=True)
        # این فیلتر برای نمایش کارهای ارجاع نشده است (مثل عکسی که فرستادی)
        st.selectbox("ارجاع به کمیته تخصصی:", COMMITTEES)
        st.button("تایید و ارجاع به کمیته منتخب")

    # نوار پایین
    st.markdown("""
    <div style="height: 100px;"></div>
    <div class="bottom-navbar">
        <div style="text-align:center; color:#002d5b;">🏛️<br><span style="font-size:10px;">خانه</span></div>
        <div style="text-align:center; color:#a0aec0;">📚<br><span style="font-size:10px;">آرشیو</span></div>
        <div style="text-align:center; color:#a0aec0;">👤<br><span style="font-size:10px;">پروفایل</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج ایمن"):
        st.session_state.step = "welcome"; st.rerun()
        
