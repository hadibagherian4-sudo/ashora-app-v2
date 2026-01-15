import streamlit as st
import base64
import os

# --- تنظیمات سیستمی ---
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- توابع گرافیکی برای تصاویر لوکال ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

img_logo = get_image_base64("logo.png")
img_highway = get_image_base64("highway_site.jpg")
img_tech = get_image_base64("tech_manager.jpg")
img_welding = get_image_base64("welding.jpg")
img_ai = get_image_base64("ai_assist.jpg")

# --- تعریف ثابت‌های سامانه ---
CATEGORIES = ["فنی و مهندسی", "HSSE", "نیروی انسانی", "مدیریتی", "برنامه‌ریزی و کنترل پروژه", "پشتیبانی", "ماشین‌آلات"]
FILE_TYPES = ["ویدیو آموزشی", "پادکست (صوتی)", "عکس/اینفوگرافیک", "مستندات (PDF)"]

# --- دیتابیس مجازی ---
if 'db' not in st.session_state:
    st.session_state.db = [
        {"id": 1, "title": "اصول نگهداری فینیشر", "cat": "ماشین‌آلات", "status": "انتشار یافته", "assigned_to": "کمیته تخصصی", "score": 98},
        {"id": 2, "title": "گزارش ایمنی محور شمال", "cat": "HSSE", "status": "در انتظار ارجاع", "assigned_to": "نامشخص", "score": 0}
    ]
if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'role' not in st.session_state: st.session_state.role = "guest"

# --- CSS مدرن با رنگ‌های روشن (Bright/Light Theme) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl; text-align: right;
    }}
    
    /* پس‌زمینه روشن و لایت */
    .main {{ background-color: #ffffff; }}
    header, footer {{visibility: hidden !important;}}
    .block-container {{padding-top: 0rem;}}

    /* هدر سامانه با رنگ سرمه‌ای و نوار طلایی */
    .top-header {{
        background: #002d5b; color: white; padding: 20px;
        border-radius: 0 0 25px 25px; text-align: center;
        margin-bottom: 20px; border-bottom: 4px solid #fbbf24;
    }}

    /* کارت‌های شیک و سفید با سایه نرم */
    .bright-card {{
        background: #fdfdfd; border-radius: 18px; padding: 20px;
        margin: 15px 0; border: 1px solid #edf2f7;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        border-right: 10px solid #1e3a8a;
    }}

    /* فیلد ورودی‌های اختصاصی (کپچا و غیره) */
    .captcha-zone {{
        background: #f8fafc; border: 1px dashed #cbd5e1;
        padding: 15px; text-align: center; border-radius: 12px;
        font-weight: bold; font-size: 20px; letter-spacing: 5px;
    }}

    /* استایل دکمه‌ها */
    .stButton>button {{
        background: #0056b3; color: white; border-radius: 12px;
        width: 100%; height: 50px; font-weight: bold; border: none;
    }}

    /* ناوبری پایین صفحه */
    .bottom-nav {{
        position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff;
        display: flex; justify-content: space-around; padding: 15px;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.03); border-top: 1px solid #e2e8f0;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ۱. مراحل ورود (Welcome -> Login -> Verify)
# ---------------------------------------------------------

if st.session_state.step in ["welcome", "login", "verify"]:
    st.markdown(f'<div class="top-header"><img src="{img_logo}" width="70"><h2 style="margin:10px 0;">سامانه جامع محتوای عاشورا</h2></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="bright-card" style="max-width:500px; margin:auto; border-right:none; border-top:8px solid #1e3a8a;">', unsafe_allow_html=True)
        
        if st.session_state.step == "welcome":
            st.markdown("<h4 style='text-align:center;'>ورود به درگاه کاربری</h4>", unsafe_allow_html=True)
            role_choice = st.selectbox("نقش خود را انتخاب فرمایید:", ["انتخاب کنید...", "پرسنل و مهندسین", "مدیر تولید محتوا", "کمیته تخصصی نخبگان (داور)"])
            if role_choice != "انتخاب کنید...":
                if role_choice == "پرسنل و مهندسین": st.session_state.role = "user"
                elif role_choice == "مدیر تولید محتوا": st.session_state.role = "manager"
                else: st.session_state.role = "referee"
                
                if st.button("مرحله بعد"): 
                    st.session_state.step = "login"
                    st.rerun()

        elif st.session_state.step == "login":
            st.markdown("<h4 style='text-align:center;'>احراز هویت شماره همراه</h4>", unsafe_allow_html=True)
            st.text_input("شماره موبایل سازمانی :", placeholder="09xxxxxxxxx")
            st.markdown('<div class="captcha-zone"> r H o V N 🔄 </div>', unsafe_allow_html=True)
            st.text_input("کد امنیتی تصویر:")
            if st.button("ارسال کد تایید"): 
                st.session_state.step = "verify"
                st.rerun()

        elif st.session_state.step == "verify":
            st.markdown("<h4 style='text-align:center;'>فعال‌سازی حساب</h4>", unsafe_allow_html=True)
            st.text_input("کد فعال‌سازی ۵ رقمی:", type="password")
            st.markdown('<div class="captcha-zone" style="font-size:16px;"> S 8 Q 7 </div>', unsafe_allow_html=True)
            if st.button("ورود به سامانه محتوای عاشورا"):
                st.session_state.step = "dashboard"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ۲. داشبورد اصلی (Dashboard)
# ---------------------------------------------------------

elif st.session_state.step == "dashboard":
    # هدر داشبورد (Bright Layout)
    st.markdown(f"""
    <div style="background:#ffffff; border-bottom:2px solid #edf2f7; padding:15px 25px; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:14px; color:#1e3a8a; font-weight:bold;">نقش کاربر: {st.session_state.role} | خوش آمدید 👤</div>
        <img src="{img_logo}" width="40">
    </div>
    <div style="background:#002d5b; color:white; padding:10px; text-align:center; font-size:16px; font-weight:bold;">سامانه جامع محتوای عاشورا</div>
    """, unsafe_allow_html=True)

    # تفکیک صفحات بر اساس نقش
    
    # --- الف) پورتال پرسنل (User) ---
    if st.session_state.role == "user":
        tab1, tab2 = st.tabs(["📚 کتابخانه محتوا", "📥 ثبت سناریو جدید"])
        
        with tab1:
            st.markdown("<h5 style='margin-top:10px;'>آخرین دروس‌آموخته منتشر شده</h5>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="bright-card">
                <div style="display:flex; gap:15px; align-items:center;">
                    <img src="{img_highway}" style="width:100px; height:100px; border-radius:12px; object-fit:cover;">
                    <div>
                        <h4 style="margin:0;">تحلیل فنی بستر در آزادراه ساوه</h4>
                        <p style="font-size:12px; color:#64748b;">بخش: فنی و مهندسی | امتیاز نخبگان: ۹۸ ⭐</p>
                        <span style="background:#dcfce7; color:#166534; font-size:10px; padding:3px 8px; border-radius:5px;">منتشر شده</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab2:
            st.markdown("##### فرم ارسال سناریو و محتوای آموزشی")
            with st.container():
                st.markdown('<div style="background:#f8fafc; padding:20px; border-radius:15px; border:1px solid #e2e8f0;">', unsafe_allow_html=True)
                t_title = st.text_input("عنوان سناریو / محتوا :")
                t_cat = st.selectbox("حیطه تخصصی :", CATEGORIES)
                t_type = st.selectbox("قالب رسانه‌ای محتوا :", FILE_TYPES)
                t_file = st.file_uploader("انتخاب فایل ضمیمه (ویدیو/صوت/سند)")
                t_desc = st.text_area("شرح کامل چالش فنی و راهکار پیشنهادی :")
                
                if st.button("ثبت نهایی و ارسال به مدیر تولید محتوا"):
                    if t_title and t_file:
                        st.success("محتوای جناب‌عالی با موفقیت ثبت گردید و جهت ارجاع به مدیر تولید محتوا ارسال شد.")
                        st.balloons()
                    else: st.warning("لطفاً تمامی موارد الزامی را تکمیل نمایید.")
                st.markdown('</div>', unsafe_allow_html=True)

    # --- ب) پورتال مدیر تولید (Manager) ---
    elif st.session_state.role == "manager":
        st.subheader("کارتابل مدیریت ارجاع")
        st.info("در این بخش محتواهای ارسالی پرسنل را بررسی و به کمیته‌های تخصصی ارجاع دهید.")
        
        # نمایش آیتم‌هایی که در انتظار ارجاع هستند
        pending = [i for i in st.session_state.db if i["status"] == "در انتظار ارجاع"]
        if pending:
            for item in pending:
                st.markdown(f'<div class="bright-card"><b>عنوان: {item["title"]}</b><br>ارسال کننده: پرسنل پروژه</div>', unsafe_allow_html=True)
                ref_target = st.selectbox(f"ارجاع {item['title']} به کمیته تخصصی:", CATEGORIES, key=f"mgr_{item['id']}")
                if st.button(f"تایید و ارجاع به بخش {ref_target}", key=f"btn_{item['id']}"):
                    st.success("محتوا با موفقیت برای داوران ارسال گردید.")
        else: st.write("مورد جدیدی یافت نشد.")

    # --- ج) پورتال داوران (Referee) ---
    elif st.session_state.role == "referee":
        st.subheader("پنل ارزیابی تخصصی نخبگان")
        st.markdown(f"""
        <div style="background:white; border-radius:15px; padding:15px; margin-bottom:20px; display:flex; align-items:center; border:1px solid #e2e8f0;">
            <img src="{img_ai}" style="width:70px; height:70px; border-radius:50%; object-fit:cover;">
            <div style="margin-right:15px;"><b>میز ارزیابی تخصصی</b><br><small>کمیته فنی و مهندسی</small></div>
        </div>
        """, unsafe_allow_html=True)
        
        sc_score = st.slider("امتیازدهی نهایی محتوا (۰ تا ۱۰۰):", 0, 100, 85)
        st.multiselect("شاخص‌های برتری:", ["بروز بودن موضوع", "نوآوری فنی", "کیفیت نمایش", "دقت محاسباتی"])
        if st.button("تایید نهایی و انتشار در ویترین"):
            st.success("محتوا با امتیاز ثبت شده تایید گردید و در سامانه منتشر شد.")

    # --- ناوبری پایین صفحه ---
    st.markdown("""
    <div style="height: 100px;"></div>
    <div class="bottom-nav">
        <div style="text-align:center; color:#1e3a8a;">🏠<br><span style="font-size:10px;">میز کار</span></div>
        <div style="text-align:center; color:#94a3b8;">📋<br><span style="font-size:10px;">سوابق</span></div>
        <div style="text-align:center; color:#94a3b8;">👤<br><span style="font-size:10px;">پروفایل</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج ایمن از سیستم"):
        st.session_state.step = "welcome"
        st.session_state.role = "guest"
        st.rerun()
