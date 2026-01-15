import streamlit as st
import base64
import os

# تنظیمات اصلی
st.set_page_config(page_title="سامانه جامع محتوای عاشورا", layout="centered")

# --- توابع گرافیکی ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return ""

img_logo = get_image_base64("logo.png")
img_tech = get_image_base64("tech_manager.jpg")
img_welding = get_image_base64("welding.jpg")

# --- دسته‌بندی‌های اعلام شده شما ---
CATEGORIES = [
    "عمومی", "فنی و مهندسی", "HSSE", "نیروی انسانی", 
    "مدیریتی", "برنامه ریزی و کنترل پروژه", "پشتیبانی", "ماشین آلات"
]

# --- دیتابیس مجازی در حافظه (Session State) ---
if 'contents' not in st.session_state:
    st.session_state.contents = [
        {"id": 101, "title": "روش تثبیت لایه بیس", "category": "فنی و مهندسی", "sender": "باقریان", "status": "انتشار یافته", "assigned_to": "کمیته فنی", "score": 95},
        {"id": 102, "title": "گزارش ایمنی کارگاه", "category": "HSSE", "sender": "احمدی", "status": "در انتظار ارجاع", "assigned_to": "نامشخص", "score": 0},
    ]
if 'role' not in st.session_state:
    st.session_state.role = "guest"

# --- CSS حرفه‌ای موبایل-محور ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    html, body, [class*="css"] {{ font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; background-color: #f8fafc; }}
    header, footer {{visibility: hidden !important; height:0px;}}
    .block-container {{padding: 0 !important;}}
    .nav-bar {{ background: #002d5b; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; }}
    .card {{ background: white; border-radius: 18px; padding: 15px; margin: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-right: 8px solid #fbbf24; position: relative; }}
    .badge {{ padding: 2px 10px; border-radius: 20px; font-size: 10px; font-weight: bold; position: absolute; top: 10px; left: 10px; }}
    .login-box {{ background: linear-gradient(135deg, #002d5b, #001f3f); height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; }}
    .stButton>button {{ border-radius: 12px; width: 100%; font-weight: bold; }}
    .category-tag {{ background: #e2e8f0; color: #475569; padding: 2px 8px; border-radius: 5px; font-size: 11px; margin-left: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- منطق ورود و خروج ---
if st.session_state.role == "guest":
    st.markdown(f"""<div class="login-box"><img src="{img_logo}" width="120"><h2 style='margin-top:20px;'>سامانه نخبگان موسسه عاشورا</h2><p>انتخاب نوع ورود</p></div>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:-200px; padding:20px;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🔑 ورود مدیر تولید"): st.session_state.role = "manager"; st.rerun()
    if c2.button("⚖️ ورود داوران"): st.session_state.role = "referee"; st.rerun()
    if c3.button("👤 ورود کاربران"): st.session_state.role = "user"; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- هدر ثابت داشبورد ---
    st.markdown(f"""
    <div class="nav-bar">
        <div style="font-size:12px;">🎭 نقش: {st.session_state.role}</div>
        <div style="display:flex; align-items:center;"><b>موسسه عاشورا</b> <img src="{img_logo}" width="30" style="margin-left:10px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------
    # ۱. پورتال کاربران (ثبت و مشاهده)
    # -----------------------------
    if st.session_state.role == "user":
        menu = st.tabs(["📚 ویترین محتوا", "➕ ارسال محتوا"])
        
        with menu[1]:
            st.markdown("### ثبت محتوای آموزشی")
            with st.form("user_upload"):
                title = st.text_input("عنوان موضوع")
                cat = st.selectbox("دسته‌بندی", CATEGORIES)
                desc = st.text_area("توضیحات فنی سناریو")
                up = st.file_uploader("فایل ویدئو یا عکس")
                if st.form_submit_button("ارسال به مدیر تولید محتوا"):
                    st.session_state.contents.append({"id": 105, "title": title, "category": cat, "sender": "مهندس (شما)", "status": "در انتظار ارجاع", "assigned_to": "نامشخص", "score": 0})
                    st.success("ارسال شد! محتوا ابتدا توسط مدیر بررسی و سپس به کمیته مربوطه ارجاع می‌شود.")
        
        with menu[0]:
            st.markdown("### محتواهای برگزیده")
            for item in st.session_state.contents:
                if item["status"] == "انتشار یافته":
                    st.markdown(f"""<div class="card"><h4 style='margin:0;'>{item['title']}</h4><p style='font-size:12px; color:grey;'>بخش: {item['category']} | امتیاز: {item['score']} ⭐</p></div>""", unsafe_allow_html=True)

    # -----------------------------
    # ۲. پورتال مدیر تولید محتوا (ارجاع‌دهنده)
    # -----------------------------
    elif st.session_state.role == "manager":
        st.markdown("### کارتابل ارجاع هوشمند")
        pending_mgr = [i for i in st.session_state.contents if i["status"] == "در انتظار ارجاع"]
        
        if not pending_mgr: st.info("محتوای جدیدی برای ارجاع وجود ندارد.")
        
        for idx, item in enumerate(pending_mgr):
            with st.expander(f"📥 {item['title']} (فرستنده: {item['sender']})"):
                st.write(f"دسته‌بندی پیشنهادی کاربر: {item['category']}")
                ref_target = st.selectbox(f"ارجاع به کمیته داوری برای محتوای {idx}:", CATEGORIES, key=f"sel_{idx}")
                if st.button(f"تایید و ارجاع به کمیته {ref_target}", key=f"btn_{idx}"):
                    # پیدا کردن آیتم در دیتابیس و تغییر وضعیت
                    for real_item in st.session_state.contents:
                        if real_item["id"] == item["id"]:
                            real_item["status"] = "در حال داوری"
                            real_item["assigned_to"] = ref_target
                    st.success(f"محتوا برای داوران بخش {ref_target} ارسال شد.")
                    st.rerun()

    # -----------------------------
    # ۳. پورتال داوران (امتیازدهی تخصصی)
    # -----------------------------
    elif st.session_state.role == "referee":
        st.markdown("### میز ارزیابی تخصصی داوران")
        # داور باید تخصص خودش را انتخاب کند (شبیه‌سازی کمیته‌ها)
        specialty = st.selectbox("شما داور کدام کمیته هستید؟", CATEGORIES)
        pending_ref = [i for i in st.session_state.contents if i["status"] == "در حال داوری" and i["assigned_to"] == specialty]
        
        if not pending_ref: st.warning(f"در حال حاضر سناریویی برای کمیته {specialty} ارسال نشده است.")
        
        for idx, item in enumerate(pending_ref):
            st.markdown(f"""<div class="card" style="border-right-color:#1e3a8a;"><h4>{item['title']}</h4><p style='font-size:11px;'>ارسالی از واحد مدیریت محتوا</p></div>""", unsafe_allow_html=True)
            sc = st.slider(f"امتیاز فنی (کمیته {specialty})", 0, 100, 80, key=f"sc_{idx}")
            if st.button(f"تایید نهایی و انتشار", key=f"apr_{idx}"):
                for real_item in st.session_state.contents:
                    if real_item["id"] == item["id"]:
                        real_item["status"] = "انتشار یافته"
                        real_item["score"] = sc
                st.balloons()
                st.success("با سپاس؛ محتوا منتشر شد و در ویترین کاربران قرار گرفت.")
                st.rerun()

    # --- دکمه خروج و منوی پایین ثابت ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 خروج و تغییر نقش"):
        st.session_state.role = "guest"; st.rerun()

    st.markdown(f"""
    <div style="position:fixed; bottom:0; width:100%; background:white; display:flex; justify-content:space-around; padding:15px; border-top:1px solid #ddd; z-index:999;">
        <div style="font-size:10px; color:#1e3a8a;"><b>🏠 داشبورد</b></div>
        <div style="font-size:10px; color:grey;"><b>📂 آرشیو</b></div>
        <div style="font-size:10px; color:grey;"><b>👤 پروفایل</b></div>
    </div>
    """, unsafe_allow_html=True)
