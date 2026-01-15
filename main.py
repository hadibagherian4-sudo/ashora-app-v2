import streamlit as st
import base64
import os

# تنظیمات اصلی سامانه با نام رسمی
st.set_page_config(page_title="سامانه جامع مدیریت دانش و محتوای عاشورا", layout="centered")

# --- تابع گرافیکی برای بارگذاری تصاویر ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

img_logo = get_image_base64("logo.png")
img_tech = get_image_base64("tech_manager.jpg")
img_highway = get_image_base64("highway_site.jpg")

# --- دسته‌بندی‌های تخصصی مورد نظر سازمان ---
CATEGORIES = [
    "فنی و مهندسی", 
    "HSSE (ایمنی، بهداشت و محیط زیست)", 
    "منابع انسانی", 
    "مدیریت و استراتژی", 
    "برنامه‌ریزی و کنترل پروژه", 
    "پشتیبانی و تدارکات", 
    "ماشین‌آلات و تجهیزات"
]

# --- قالب‌های رسانه‌ای محتوا ---
CONTENT_TYPES = [
    "ویدیو آموزشی (عملیاتی/رئال)", 
    "پادکست تخصصی (انتقال تجربه صوتی)", 
    "اینفوگرافیک و تصاویر فنی", 
    "مستندات و گزارش‌های تحلیلی (PDF)"
]

if 'step' not in st.session_state:
    st.session_state.step = "dashboard" 

# --- طراحی بصری مدرن و اداری (CSS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {{ 
        font-family: 'Vazirmatn', sans-serif; 
        direction: rtl; 
        text-align: right; 
    }}
    
    header, footer {{visibility: hidden !important; height:0px;}}
    .main {{ background: #f9fafb; }}

    /* استایل تب‌های مدیریتی */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; justify-content: center; border-bottom: 2px solid #e5e7eb; }}
    .stTabs [data-baseweb="tab"] {{ 
        height: 50px; 
        background-color: #f3f4f6; 
        border-radius: 8px 8px 0 0; 
        padding: 10px 25px;
        color: #374151;
        font-weight: bold;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #003a70 !important; color: white !important; }}

    /* محفظه فرم‌ها */
    .form-box {{
        background: white; border-radius: 12px; padding: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #d1d5db;
    }}
    
    .stButton>button {{
        background: #003a70; color: white; border-radius: 8px; width: 100%; height: 48px; 
        font-weight: bold; border: none; font-size: 16px;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# بخش داشبورد و میز کار
# -----------------------------
if st.session_state.step == "dashboard":
    
    # نوار ابزار فوقانی سامانه
    st.markdown(f"""
    <div style="background:#002147; color:white; padding:15px 25px; display:flex; justify-content:space-between; align-items:center; border-bottom: 3px solid #c5a059;">
        <div style="font-size:13px; font-weight:400;">پنل کاربری | جناب‌عالی خوش‌ آمدید 👤</div>
        <div style="display:flex; align-items:center;">
            <span style="margin-left:15px; font-weight:bold;">سامانه جامع محتوای عاشورا</span>
            <img src="{img_logo}" width="40">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ایجاد تب‌های عملیاتی
    tab1, tab2 = st.tabs(["📑 مشاهده دروس‌آموخته و محتوا", "📤 ارسال سناریو و محتوای جدید"])

    # --- تب اول: کتابخانه محتوا ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:white; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb; border-right: 8px solid #c5a059; margin-bottom:18px;">
            <img src="{img_highway}" style="width:100%; height:140px; object-fit:cover;">
            <div style="padding:15px;">
                <h4 style="margin:0; color:#002147; font-size:15px;">گزارش تحلیلی: روش‌های بهسازی لرزه‌ای ابنیه فنی</h4>
                <p style="font-size:11px; color:#6b7280; margin-top:5px;">حوزه: فنی و مهندسی | قالب: مستندات متنی | تراز کیفی: ۹۴/۱۰۰</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- تب دوم: ثبت و ارسال (بخش بازبینی شده) ---
    with tab2:
        st.markdown("### فرم ثبت محتوای دانش‌محور")
        st.info("پرسنل و نخبگان گرامی، مقتضی است اطلاعات سناریوی آموزشی خود را با دقت در فرم زیر تکمیل نمایید.")
        
        with st.container():
            st.markdown('<div class="form-box">', unsafe_allow_html=True)
            
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                topic = st.text_input("عنوان سناریو / موضوع آموزشی:")
            with row1_col2:
                field = st.selectbox("حیطه تخصصی مربوطه:", CATEGORIES)
            
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                format_type = st.selectbox("قالب رسانه‌ای محتوا:", CONTENT_TYPES)
            with row2_col2:
                # بارگذاری متناسب با نوع رسانه
                upload_label = f"بارگذاری فایل {format_type.split()[0]}"
                uploaded_file = st.file_uploader(upload_label, type=["mp4", "mp3", "pdf", "jpg", "png", "zip"])

            desc = st.text_area("شرح جزییات و چالش‌های فنی (توضیحات تکمیلی):")
            
            st.markdown("---")
            row3_col1, row3_col2 = st.columns([2,1])
            with row3_col1:
                st.caption("محتوای ارسالی پس از تأیید مدیر تولید محتوا، جهت امتیازدهی به کمیته‌های تخصصی ارجاع خواهد شد.")
            with row3_col2:
                verification = st.checkbox("صحت اطلاعات ارسالی مورد تایید است.")

            # دکمه ارسال نهایی
            if st.button("ثبت نهایی و ارسال به دبیرخانه محتوا"):
                if topic and uploaded_file and verification:
                    st.success(f"با موفقیت ثبت گردید. محتوای «{topic}» جهت طی فرآیند ارزیابی به دبیرخانه محتوا ارسال شد.")
                    st.balloons()
                else:
                    st.warning("لطفاً تمامی فیلدهای الزامی و چک‌باکس تاییدیه را تکمیل فرمایید.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # ناوبری ثابت پایینی (Footer Navigation)
    st.markdown("""
    <div style="height: 100px;"></div>
    <div style="position:fixed; bottom:0; left:0; width:100%; background:white; display:flex; justify-content:space-around; padding:15px; border-top:1px solid #e5e7eb; z-index:999;">
        <div style="text-align:center; color:#003a70; font-weight:bold; cursor:pointer;">🏛️<br><span style="font-size:10px;">میز کار</span></div>
        <div style="text-align:center; color:#9ca3af; cursor:pointer;">📊<br><span style="font-size:10px;">سوابق من</span></div>
        <div style="text-align:center; color:#9ca3af; cursor:pointer;">👤<br><span style="font-size:10px;">پروفایل</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("خروج از سیستم کاربر"):
        st.session_state.step = "welcome"
        st.rerun()
