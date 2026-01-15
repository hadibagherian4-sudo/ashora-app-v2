import streamlit as st
import base64
import os

# تنظیمات اصلی صفحه
st.set_page_config(page_title="سامانه مدیریت نخبگان عاشورا", layout="centered")

# --- تابع کمکی برای خواندن عکس‌های محلی و نمایش در HTML ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()
    return "https://via.placeholder.com/150" # اگر عکس نبود این جایگزین میشه

# خواندن تصاویر شما
img_ai = get_image_base64("ai_assist.jpg")
img_bg = get_image_base64("digital_bg.jpg")
img_highway = get_image_base64("highway_site.jpg")
img_welding = get_image_base64("welding.jpg")
img_tech = get_image_base64("tech_manager.jpg")

# --- استایل حرفه‌ای و شیک ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl; text-align: right; background-color: #f4f7f6;
    }}
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 0rem;}}

    /* هدر با عکس اتوبان شما */
    .app-header {{
        background: linear-gradient(rgba(0, 45, 91, 0.8), rgba(0, 45, 91, 0.8)), url('{img_highway}');
        background-size: cover; background-position: center;
        color: white; padding: 40px 20px; border-radius: 0 0 35px 35px;
        text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}

    /* نوار جستجوی شیک */
    .search-bar {{
        background: white; margin: -25px 20px 20px; padding: 15px;
        border-radius: 15px; display: flex; justify-content: space-between;
        align-items: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}

    /* کارت‌های محتوا با عکس‌های شما */
    .card {{
        background: white; border-radius: 20px; padding: 15px;
        margin: 15px; border-right: 10px solid #fbbf24;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); display: flex; align-items: center;
    }}
    .card-img {{
        width: 100px; height: 100px; border-radius: 15px; object-fit: cover;
    }}
    .card-content {{ flex: 1; padding-right: 15px; }}
    .card-title {{ margin: 0; font-size: 15px; color: #002d5b; font-weight: 900; }}
    
    /* بخش امتیازدهی با پس‌زمینه انتزاعی شما */
    .rating-section {{
        background: linear-gradient(rgba(255,255,255,0.9), rgba(255,255,255,0.9)), url('{img_bg}');
        background-size: cover; margin: 20px; padding: 25px;
        border-radius: 20px; text-align: center; border: 1px solid #e2e8f0;
    }}

    .btn-submit {{
        background-color: #1e3a8a; color: white !important;
        width: 100%; border: none; padding: 12px; border-radius: 12px;
        font-weight: bold; margin-top: 15px; cursor: pointer;
    }}
</style>
""", unsafe_allow_html=True)

# --- محتوای اپلیکیشن ---

# هدر اصلی
st.markdown("""
<div class="app-header">
    <h1 style='margin:0; font-size:22px;'>سامانه ستاریو و ارزیابی محتوا</h1>
    <p style='margin:10px 0 0; opacity:0.9; font-size:13px;'>مرکز برنامه‌ریزی و توسعه موسسه عاشورا</p>
</div>
""", unsafe_allow_html=True)

# نوار جستجو
st.markdown("""
<div class="search-bar">
    <div style="background:#48bb78; color:white; width:35px; height:35px; border-radius:50%; text-align:center; line-height:35px; font-weight:bold;">+</div>
    <div style="color:#666; font-size:14px;">جستجوی سناریو یا موضوعات جدید...</div>
    <div style="font-size:18px;">🔍</div>
</div>
""", unsafe_allow_html=True)

# کارت ۱ - گزارش فنی (عکس مهندس و بیل مکانیکی)
st.markdown(f"""
<div class="card">
    <img src="{img_tech}" class="card-img">
    <div class="card-content">
        <span style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:5px; font-size:10px;">در حال بررسی</span>
        <h4 class="card-title">تحلیل برنامه‌ریزی عملیات زیرسازی</h4>
        <div style="font-size:11px; color:#666; margin-top:5px;">📅 ۱۴۰۲/۱۰/۲۴ | فرستنده: مهندس باقریان</div>
        <div style="margin-top:10px; font-weight:bold; color:#fbbf24;">امتیاز: ۹۸ ⭐⭐⭐⭐⭐</div>
    </div>
</div>
""", unsafe_allow_html=True)

# کارت ۲ - آموزش (عکس جوشکاری)
st.markdown(f"""
<div class="card" style="border-right-color: #10b981;">
    <img src="{img_welding}" class="card-img">
    <div class="card-content">
        <span style="background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:5px; font-size:10px;">منتشر شده</span>
        <h4 class="card-title">تکنیک‌های حرفه‌ای جوشکاری سازه</h4>
        <div style="font-size:11px; color:#666; margin-top:5px;">📅 ۱۴۰۲/۱۰/۲۰ | ۵ فایل پیوست فنی</div>
        <div style="margin-top:10px; font-weight:bold; color:#fbbf24;">امتیاز: ۸۵ ⭐⭐⭐⭐</div>
    </div>
</div>
""", unsafe_allow_html=True)

# بخش ارزیابی تولیدکننده (عکس مهندس کلاه آبی برای آواتار)
st.markdown(f"""
<div class="rating-section">
    <img src="{img_ai}" style="width:80px; height:80px; border-radius:50%; border: 3px solid #1e3a8a; object-fit:cover;">
    <h4 style="margin:10px 0; font-size:16px;">ارزیابی نهایی تولیدکننده</h4>
    <div style="font-size:12px; color:#444;">مجموع تراز علمی تولیدکننده در این سناریو</div>
    <div style="font-size:24px; margin:10px 0;">⭐⭐⭐⭐⭐ <b>4.9</b></div>
    <div style="display:flex; justify-content:center; gap:5px; margin-top:10px;">
        <span style="background:#e2e8f0; padding:4px 10px; border-radius:5px; font-size:11px;">نوآوری فنی ✕</span>
        <span style="background:#e2e8f0; padding:4px 10px; border-radius:5px; font-size:11px;">بروزرسانی موضوع ✕</span>
    </div>
    <button class="btn-submit">ثبت امتیاز نهایی در شناسنامه</button>
</div>
""", unsafe_allow_html=True)

# ناوبری پایین
st.markdown("""
<div style="height: 100px;"></div>
<div style="position:fixed; bottom:0; left:0; width:100%; background:white; display:flex; justify-content:space-around; padding:15px; border-top:1px solid #ddd; z-index:999;">
    <div style="text-align:center; font-size:10px; color:#1e3a8a; font-weight:bold;">🏠<br>مرکز سناریو</div>
    <div style="text-align:center; font-size:10px; color:#666;">📂<br>محتوای من</div>
    <div style="text-align:center; font-size:10px; color:#666;">💬<br>پیام‌ها</div>
    <div style="text-align:center; font-size:10px; color:#666;">👤<br>دستیار من</div>
</div>
""", unsafe_allow_html=True)
