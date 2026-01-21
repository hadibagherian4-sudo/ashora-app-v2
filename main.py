import os
import re
import time
import base64
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional

# =========================================================
# Helpers
# =========================================================
def _file_exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False

def pick_existing(paths: List[str]) -> str:
    for p in paths:
        if p and _file_exists(p):
            return p
    return ""

def normalize_phone(p: str) -> str:
    return re.sub(r"\s+", "", (p or "").strip())

def normalize_nid(n: str) -> str:
    return re.sub(r"\s+", "", (n or "").strip())

def now_ts() -> float:
    return time.time()

def ts_str(ts: float) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
    except Exception:
        return str(ts)

def make_id(prefix: str) -> str:
    st.session_state._id_counter += 1
    return f"{prefix}{st.session_state._id_counter}"

def status_fa(s: str) -> str:
    return {
        "pending": "در انتظار ارجاع مدیر سامانه",
        "waiting_referee": "در انتظار نظر داور",
        "correction_needed": "نیاز به اصلاح",
        "published": "تایید و انتشار در ویترین دانش",
        "rejected": "عدم تایید",
    }.get(s, s)

# =========================================================
# Theme + Fonts (BTir.ttf, BNazanin.ttf)
# =========================================================
def inject_theme():
    btitr_path = pick_existing(["assets/fonts/BTir.ttf", "BTir.ttf"])
    bnazanin_path = pick_existing(["assets/fonts/BNazanin.ttf", "BNazanin.ttf"])

    btitr_css = ""
    bnazanin_css = ""

    if btitr_path:
        with open(btitr_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        btitr_css = f"""
        @font-face {{
          font-family: 'BTitr';
          src: url(data:font/ttf;base64,{b64}) format('truetype');
          font-weight: 700;
          font-style: normal;
        }}
        """

    if bnazanin_path:
        with open(bnazanin_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        bnazanin_css = f"""
        @font-face {{
          font-family: 'BNazaninBold';
          src: url(data:font/ttf;base64,{b64}) format('truetype');
          font-weight: 700;
          font-style: normal;
        }}
        """

    title_font = "BTitr" if btitr_path else "Tahoma"
    body_font = "BNazaninBold" if bnazanin_path else "Tahoma"

    st.markdown(
        f"""
        <style>
        {btitr_css}
        {bnazanin_css}

        :root {{
          --navy: #071a30;
          --navy2:#0b2a4a;
          --paper:#ffffff;
          --paper2:#f3f4f6;
          --ink:#0b1220;
          --muted:#475569;
          --accent:#f6c445;
          --border: rgba(15,23,42,0.14);
          --danger:#dc2626;
          --ok:#16a34a;
        }}

        .stApp {{
          background: var(--paper2) !important;
        }}

        html, body, [class*="css"], * {{
          direction: rtl !important;
          text-align: right !important;
          font-family: {body_font} !important;
          color: var(--ink) !important;
        }}

        h1,h2,h3 {{
          text-align: center !important;
          font-family: {title_font} !important;
          color: var(--ink) !important;
          margin-bottom: 8px !important;
        }}

        /* shell */
        .nexa-shell {{
          max-width: 1240px;
          margin: 14px auto 96px auto;
          padding: 0 12px;
        }}

        /* header */
        .nexa-header {{
          background: linear-gradient(135deg, var(--navy), var(--navy2));
          border: 1px solid rgba(255,255,255,0.14);
          border-radius: 18px;
          padding: 14px 16px;
          display:flex;
          align-items:center;
          justify-content:space-between;
          gap: 10px;
        }}

        .nexa-title {{
          font-family: {title_font} !important;
          font-size: 30px;
          font-weight: 900;
          color: #fff !important;
          text-align:center !important;
          line-height: 1.2;
        }}

        .nexa-subtitle {{
          color: rgba(255,255,255,0.9) !important;
          text-align:center !important;
          font-size: 14px;
          margin-top: 4px;
        }}

        .panel {{
          background: var(--paper) !important;
          border-radius: 16px;
          padding: 18px;
          border: 1px solid var(--border);
          box-shadow: 0 10px 22px rgba(2,6,23,0.06);
        }}

        .muted {{
          color: var(--muted) !important;
        }}

        /* bottom nav like app */
        .bottom-nav {{
          position: fixed;
          left:0; right:0; bottom:0;
          padding: 10px 14px;
          background: rgba(7, 26, 48, 0.98);
          border-top: 1px solid rgba(255,255,255,0.12);
          z-index: 9999;
        }}
        .bottom-nav .stRadio > div {{
          justify-content: center !important;
          gap: 18px;
        }}
        .bottom-nav label {{
          color: white !important;
          font-weight: 900 !important;
          font-size: 14px !important;
        }}

        /* buttons */
        .stButton > button {{
          border-radius: 12px !important;
          font-weight: 900 !important;
        }}
        .stButton > button[kind="primary"] {{
          background: var(--accent) !important;
          color: #111827 !important;
          border: none !important;
        }}

        /* cards */
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stExpander"]) {{
          border-radius: 12px;
        }}

        header[data-testid="stHeader"] {{
          background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# Data Models
# =========================================================
@dataclass
class Comment:
    id: str
    user: str
    text: str
    ts: float

@dataclass
class Submission:
    id: str
    title: str
    description: str
    sender_phone: str
    sender_name: str
    sender_nid: str
    suggested_topic_id: str
    field: str
    content_type: str
    file_name: str
    file_bytes: bytes | None
    cover_image_path: str
    status: str = "pending"
    score: int = 0
    likes: int = 0
    views: int = 0
    knowledge_code: str = ""
    referee_feedback: str = ""
    assigned_referee_phone: str = ""
    assigned_referee_name: str = ""
    comments: List[Comment] = field(default_factory=list)

@dataclass
class RefereeProfile:
    first_name: str
    last_name: str
    phone: str
    national_id: str
    field: str
    password: str
    is_active: bool = True

@dataclass
class ForumReply:
    id: str
    referee_phone: str
    referee_name: str
    text: str
    ts: float

@dataclass
class ForumPost:
    id: str
    sender_phone: str
    sender_name: str
    sender_role: str
    text: str
    ts: float
    status: str = "pending"   # pending/approved/rejected
    replies: List[ForumReply] = field(default_factory=list)

@dataclass
class TopicItem:
    id: str
    title: str
    field: str
    description: str
    file_name: str
    file_bytes: bytes | None
    ts: float

@dataclass
class ResearchItem:
    id: str
    title: str
    field: str
    summary: str
    file_name: str
    file_bytes: bytes | None
    ts: float

@dataclass
class DocumentItem:
    id: str
    title: str
    file_name: str
    file_bytes: bytes
    ts: float

FIELDS = [
    "۱. حوزه معماری و منظر",
    "۲. حوزه فنی و مهندسی",
    "۳. حوزه برنامه‌ریزی و مدیریت پروژه",
    "۴. حوزه کنترل پروژه",
    "۵. حوزه نقشه‌برداری و فتوگرامتری",
    "۶. حوزه بتن",
    "۷. حوزه هوش مصنوعی",
    "۸. حوزه ICT",
    "۹. حوزه نگهداری و ماشین‌آلات (نت)",
    "۱۰. حوزه کنترل کیفیت (QC)",
    "۱۱. حوزه HSSE",
    "۱۲. حوزه BIM",
    "۱۳. حوزه آسفالت",
    "۱۴. حوزه مالی و حسابداری",
]

CONTENT_TYPES = [
    "ایده‌های خلاقانه",
    "نوشتاری",
    "ویدیویی",
    "پادکست یا صوتی",
    "موشن گرافیک",
    "اینفوگرافیک",
    "پوستر",
    "سایر",
]

# =========================================================
# State
# =========================================================
def ensure_state():
    st.session_state.setdefault("_id_counter", 2000)

    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("role", "guest")  # user/referee/manager
    st.session_state.setdefault("phone", "")
    st.session_state.setdefault("nid", "")
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("page", "صفحه اصلی")
    st.session_state.setdefault("selected_submission_id", None)

    # Users: phone -> {name, nid, password}
    st.session_state.setdefault("users", {})

    # Manager credentials (طبق حرف تو)
    st.session_state.setdefault("manager_phone", "09146862029")
    st.session_state.setdefault("manager_nid", "1362362506")
    st.session_state.setdefault("manager_password", "Hadi136236")

    # Referees
    st.session_state.setdefault("referees", [
        RefereeProfile(first_name="استاد", last_name="نمونه", phone="0912", national_id="123",
                       field="۲. حوزه فنی و مهندسی", password="1234", is_active=True)
    ])

    # Content
    st.session_state.setdefault("topics", [])
    st.session_state.setdefault("research", [])
    st.session_state.setdefault("documents", [])
    st.session_state.setdefault("forum_posts", [])

    # Submissions
    cover_default = pick_existing(["Picture1.png", "official_logo.png", "logo.png"])
    st.session_state.setdefault("submissions", [
        Submission(
            id="s1",
            title="بهسازی زیرسازی آزادراه",
            description="سناریوی اصلاح لایه بیس",
            sender_phone="09120000000",
            sender_name="واحد مهندسی",
            sender_nid="0000000000",
            suggested_topic_id="",
            field="۱۳. حوزه آسفالت",
            content_type="نوشتاری",
            file_name="sample.pdf",
            file_bytes=None,
            cover_image_path=cover_default,
            status="published",
            likes=25,
            views=500,
            knowledge_code="A-1301",
        )
    ])

def is_admin() -> bool:
    return st.session_state.role == "manager"

def find_referee(phone: str, nid: str, password: str) -> Optional[RefereeProfile]:
    p = normalize_phone(phone)
    n = normalize_nid(nid)
    for r in st.session_state.referees:
        if normalize_phone(r.phone) == p and normalize_nid(r.national_id) == n and r.password == password and r.is_active:
            return r
    return None

def get_submission(sid: str) -> Optional[Submission]:
    for s in st.session_state.submissions:
        if s.id == sid:
            return s
    return None

def logout():
    st.session_state.logged_in = False
    st.session_state.role = "guest"
    st.session_state.phone = ""
    st.session_state.nid = ""
    st.session_state.name = ""
    st.session_state.page = "صفحه اصلی"
    st.session_state.selected_submission_id = None
    st.rerun()

# =========================================================
# App
# =========================================================
st.set_page_config(page_title="NEXA", layout="wide")
ensure_state()
inject_theme()

st.markdown('<div class="nexa-shell">', unsafe_allow_html=True)

# Header
logo_path = pick_existing(["logo.png", "official_logo.png"])
logo_html = ""
if logo_path:
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    logo_html = f'<img src="data:image/png;base64,{b64}" style="width:58px;height:58px;object-fit:contain;" />'

h1, h2, h3 = st.columns([1.1, 3.6, 2.0], vertical_alignment="center")

with h1:
    st.markdown(f'<div class="nexa-header" style="justify-content:flex-start;">{logo_html}</div>', unsafe_allow_html=True)

with h2:
    st.markdown(
        """
        <div class="nexa-header" style="justify-content:center;">
          <div style="text-align:center;">
            <div class="nexa-title">نکسا (NEXA)</div>
            <div class="nexa-subtitle">نظام یکپارچه محتوا عاشورا</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with h3:
    st.markdown('<div class="nexa-header" style="justify-content:flex-end;">', unsafe_allow_html=True)
    if st.session_state.logged_in:
        if st.button("🏠 برگشت به صفحه اصلی"):
            st.session_state.page = "صفحه اصلی"
            st.rerun()
        if st.button("🚪 خروج از سامانه", type="primary"):
            logout()
    else:
        st.markdown('<div style="color:white;font-weight:900;">وارد نشده</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

# =========================================================
# Login / Signup
# =========================================================
if not st.session_state.logged_in:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("ورود به سامانه")

    role = st.selectbox(
        "نوع کاربری",
        ["user", "referee", "manager"],
        format_func=lambda x: {"user": "کاربر", "referee": "داور تخصصی / نخبگان دانشی", "manager": "مدیر سامانه"}[x],
    )

    phone = st.text_input("شماره همراه")
    nid = st.text_input("کد ملی")
    password = st.text_input("رمز عبور", type="password")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("ورود", type="primary"):
            p = normalize_phone(phone)
            n = normalize_nid(nid)

            if role == "user":
                # برای کاربر: ورود با شماره + رمز (کد ملی داخل حساب ذخیره می‌شود)
                if not p or not password:
                    st.error("شماره همراه و رمز عبور را وارد کنید.")
                    st.stop()
                u = st.session_state.users.get(p)
                if not u or u["password"] != password:
                    st.error("کاربر یافت نشد یا رمز اشتباه است. لطفاً ثبت‌نام کنید.")
                    st.stop()
                st.session_state.name = u["name"]
                st.session_state.nid = u["nid"]

            elif role == "manager":
                # برای مدیر: شماره + کد ملی + رمز
                if not p or not n or not password:
                    st.error("شماره همراه، کد ملی و رمز عبور را وارد کنید.")
                    st.stop()
                if p != normalize_phone(st.session_state.manager_phone) or n != normalize_nid(st.session_state.manager_nid) or password != st.session_state.manager_password:
                    st.error("مشخصات مدیر سامانه اشتباه است.")
                    st.stop()
                st.session_state.name = "مدیر سامانه"
                st.session_state.nid = st.session_state.manager_nid

            else:
                # برای داور: شماره + کد ملی + رمز
                if not p or not n or not password:
                    st.error("شماره همراه، کد ملی و رمز عبور را وارد کنید.")
                    st.stop()
                ref = find_referee(p, n, password)
                if not ref:
                    st.error("داور یافت نشد یا مشخصات اشتباه است.")
                    st.stop()
                st.session_state.name = f"{ref.first_name} {ref.last_name}"
                st.session_state.nid = ref.national_id

            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.phone = p
            st.session_state.page = "صفحه اصلی"
            st.success("ورود انجام شد ✅")
            st.rerun()

    with c2:
        st.caption("ثبت‌نام فقط برای کاربران")
        if st.button("ثبت نام"):
            st.session_state._show_signup = True

    # Signup (Form) - کار می‌کند
    if st.session_state.get("_show_signup", False):
        st.divider()
        st.subheader("ثبت نام")

        with st.form("signup_form"):
            su_name = st.text_input("نام و نام خانوادگی")
            su_phone = st.text_input("شماره همراه")
            su_nid = st.text_input("کد ملی")
            su_pass1 = st.text_input("رمز عبور", type="password")
            su_pass2 = st.text_input("تکرار رمز عبور", type="password")
            submit = st.form_submit_button("ایجاد حساب", type="primary")

        if submit:
            p = normalize_phone(su_phone)
            n = normalize_nid(su_nid)

            if not su_name.strip() or not p or not n or not su_pass1:
                st.error("همه فیلدها الزامی است.")
            elif su_pass1 != su_pass2:
                st.error("رمز عبور و تکرار آن یکسان نیست.")
            else:
                st.session_state.users[p] = {"name": su_name.strip(), "nid": n, "password": su_pass1}
                st.success("ثبت‌نام انجام شد ✅ حالا می‌تونی وارد بشی")
                st.session_state._show_signup = False
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =========================================================
# Bottom Navigation (like app)
# =========================================================
nav_labels = ["صفحه اصلی", "تالار گفتگو", "پروفایل", "اسناد"]
nav_icons = {"صفحه اصلی": "🏠", "تالار گفتگو": "💬", "پروفایل": "👤", "اسناد": "📄"}
nav_display = [f"{nav_icons[x]} {x}" for x in nav_labels]
current = f"{nav_icons[st.session_state.page]} {st.session_state.page}"

st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
choice = st.radio("", nav_display, index=nav_display.index(current), horizontal=True, label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)
st.session_state.page = choice.split(" ", 1)[1]

# =========================================================
# Page: Home
# =========================================================
if st.session_state.page == "صفحه اصلی":
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    role = st.session_state.role

    # -----------------------------
    # USER HOME
    # -----------------------------
    if role == "user":
        tabs = st.tabs(["ویترین دانش", "ارسال محتوا", "وضعیت پیگیری", "پیشنهاد موضوعات", "تحقیقات صورت گرفته"])

        # ویترین دانش
        with tabs[0]:
            st.header("ویترین دانش")
            published = [s for s in st.session_state.submissions if s.status == "published"]
            if not published:
                st.info("فعلاً محتوایی منتشر نشده.")
            else:
                for s in published:
                    with st.container(border=True):
                        s.views += 1

                        # تصاویر موجود در ریپو (طبق خواسته)
                        cover = s.cover_image_path
                        if cover and _file_exists(cover):
                            st.image(cover, use_container_width=True)
                        else:
                            fallback = pick_existing(["Picture1.png", "official_logo.png", "logo.png"])
                            if fallback:
                                st.image(fallback, use_container_width=True)

                        st.subheader(s.title)
                        st.caption(f"{s.field} | نوع محتوا: {s.content_type} | کد دانشی: {s.knowledge_code or '-'} | بازدید: {s.views}")
                        st.write(s.description)

                        cA, cB = st.columns([1.2, 3])
                        with cA:
                            if st.button(f"❤️ لایک ({s.likes})", key=f"like_{s.id}"):
                                s.likes += 1
                                st.rerun()
                        with cB:
                            st.caption(" ")

                        st.subheader("نظرات")
                        if s.comments:
                            for cm in sorted(s.comments, key=lambda x: x.ts):
                                st.write(f"- **{cm.user}**: {cm.text}")
                                st.caption(ts_str(cm.ts))
                        else:
                            st.caption("نظری ثبت نشده.")

                        new_comment = st.text_input("افزودن نظر", key=f"cmt_{s.id}", placeholder="نظرت رو بنویس...")
                        if st.button("ثبت نظر", key=f"cmt_btn_{s.id}", type="primary"):
                            if new_comment.strip():
                                s.comments.append(Comment(id=make_id("c"), user=st.session_state.name, text=new_comment.strip(), ts=now_ts()))
                                st.success("نظر ثبت شد ✅")
                                st.rerun()

        # ارسال محتوا
        with tabs[1]:
            st.header("ارسال محتوا")

            topic_options = ["(بدون انتخاب موضوع)"] + [f"{t.title} | {t.field}" for t in st.session_state.topics]
            topic_pick = st.selectbox("انتخاب از پیشنهادات مدیر (اختیاری)", topic_options)

            picked_topic_id = ""
            if topic_pick != "(بدون انتخاب موضوع)":
                for t in st.session_state.topics:
                    if f"{t.title} | {t.field}" == topic_pick:
                        picked_topic_id = t.id
                        break

            default_title = ""
            default_desc = ""
            default_field = FIELDS[0]
            if picked_topic_id:
                for t in st.session_state.topics:
                    if t.id == picked_topic_id:
                        default_title = t.title
                        default_desc = t.description
                        default_field = t.field
                        break

            title = st.text_input("عنوان", value=default_title)
            desc = st.text_area("توضیحات", value=default_desc, height=120)
            field_sel = st.selectbox("کمیته / حوزه تخصصی", FIELDS, index=FIELDS.index(default_field) if default_field in FIELDS else 0)
            content_type = st.selectbox("نوع محتوا", CONTENT_TYPES)

            # آپلود فایل واقعی
            uploaded = st.file_uploader("پیوست فایل", type=None)

            cover_pick = st.selectbox("تصویر ویترین (اختیاری)", ["(خالی)", "Picture1.png", "official_logo.png", "logo.png"])
            cover_path = "" if cover_pick == "(خالی)" else cover_pick
            if cover_path and not _file_exists(cover_path):
                cover_path = ""

            if st.button("ثبت و ارسال به مدیر سامانه", type="primary"):
                if not title.strip():
                    st.error("عنوان الزامی است.")
                else:
                    fname = uploaded.name if uploaded else "N/A"
                    fbytes = uploaded.getvalue() if uploaded else None
                    st.session_state.submissions.insert(
                        0,
                        Submission(
                            id=make_id("s"),
                            title=title.strip(),
                            description=desc.strip(),
                            sender_phone=st.session_state.phone,
                            sender_name=st.session_state.name,
                            sender_nid=st.session_state.nid,
                            suggested_topic_id=picked_topic_id,
                            field=field_sel,
                            content_type=content_type,
                            file_name=fname,
                            file_bytes=fbytes,
                            cover_image_path=cover_path,
                            status="pending",
                        ),
                    )
                    st.success("ارسال شد ✅")
                    st.rerun()

        # وضعیت پیگیری
        with tabs[2]:
            st.header("وضعیت پیگیری")
            my = [s for s in st.session_state.submissions if s.sender_phone == st.session_state.phone]
            if not my:
                st.info("هنوز محتوایی ارسال نکردی.")
            else:
                for s in my:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)} | نوع محتوا: {s.content_type} | حوزه: {s.field}")
                        if s.assigned_referee_name:
                            st.write(f"داور: **{s.assigned_referee_name}**")
                        if s.referee_feedback:
                            st.write(f"📝 نظر/اصلاحات داور: {s.referee_feedback}")
                        if s.score:
                            st.write(f"⭐ امتیاز: {s.score}")
                        if s.status == "published":
                            st.write(f"کد دانشی: **{s.knowledge_code}**")

        # پیشنهاد موضوعات
        with tabs[3]:
            st.header("پیشنهاد موضوعات")
            if not st.session_state.topics:
                st.info("موضوعی ثبت نشده.")
            else:
                for t in st.session_state.topics:
                    with st.container(border=True):
                        st.write(f"**{t.title}**")
                        st.caption(f"حوزه: {t.field} | تاریخ: {ts_str(t.ts)}")
                        st.write(t.description)
                        if t.file_bytes:
                            st.download_button("دانلود پیوست", data=t.file_bytes, file_name=t.file_name, key=f"dl_topic_{t.id}")

        # تحقیقات صورت گرفته
        with tabs[4]:
            st.header("تحقیقات صورت گرفته")
            if not st.session_state.research:
                st.info("تحقیقی ثبت نشده.")
            else:
                for r in st.session_state.research:
                    with st.container(border=True):
                        st.write(f"**{r.title}**")
                        st.caption(f"حوزه: {r.field} | تاریخ: {ts_str(r.ts)}")
                        st.write(r.summary)
                        if r.file_bytes:
                            st.download_button("دانلود فایل", data=r.file_bytes, file_name=r.file_name, key=f"dl_res_{r.id}")

    # -----------------------------
    # MANAGER HOME (سوپرادمین)
    # -----------------------------
    elif role == "manager":
        st.header("پنل مدیر سامانه (سوپرادمین)")
        tabs = st.tabs([
            "میز ارجاع",
            "ثبت داور تخصصی",
            "مدیریت ویترین (حذف کامنت)",
            "پیشنهاد موضوعات",
            "تحقیقات صورت گرفته",
            "اسناد",
            "تالار گفتگو (تایید پیام‌ها)",
        ])

        # میز ارجاع
        with tabs[0]:
            st.subheader("میز ارجاع مدیر سامانه")
            pending = [s for s in st.session_state.submissions if s.status == "pending"]
            if not pending:
                st.info("موردی برای ارجاع نیست.")
            else:
                for s in pending:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"فرستنده: {s.sender_name} ({s.sender_phone}) | حوزه: {s.field} | نوع: {s.content_type}")
                        st.write(s.description)
                        if s.file_bytes:
                            st.download_button("دانلود فایل پیوست", data=s.file_bytes, file_name=s.file_name, key=f"dl_sub_{s.id}")

                        # انتخاب داورهای همان حوزه
                        refs = [r for r in st.session_state.referees if r.is_active and r.field == s.field]
                        if not refs:
                            st.warning("برای این حوزه داور فعالی ثبت نشده.")
                        else:
                            ref = st.selectbox(
                                "انتخاب داور",
                                refs,
                                format_func=lambda r: f"{r.first_name} {r.last_name} | {r.phone}",
                                key=f"sel_ref_{s.id}",
                            )
                            if st.button("بررسی و ارجاع", key=f"assign_{s.id}", type="primary"):
                                s.status = "waiting_referee"
                                s.assigned_referee_phone = normalize_phone(ref.phone)
                                s.assigned_referee_name = f"{ref.first_name} {ref.last_name}"
                                st.success("ارجاع شد ✅")
                                st.rerun()

        # ثبت داور
        with tabs[1]:
            st.subheader("ثبت داور تخصصی / نخبگان (با رمز عبور)")
            c1, c2 = st.columns(2)
            with c1:
                first = st.text_input("نام", key="rf_first")
                phone = st.text_input("شماره همراه", key="rf_phone")
                field_sel = st.selectbox("حوزه فعالیت داوری", FIELDS, key="rf_field")
            with c2:
                last = st.text_input("نام خانوادگی", key="rf_last")
                nid = st.text_input("کد ملی", key="rf_nid")
                ref_pass = st.text_input("رمز عبور داور", key="rf_pass", type="password")

            active = st.checkbox("فعال باشد", value=True)

            if st.button("ثبت نهایی داور", type="primary"):
                p = normalize_phone(phone)
                n = normalize_nid(nid)
                if not (first.strip() and last.strip() and p and n and ref_pass):
                    st.error("همه فیلدها (نام، نام خانوادگی، شماره، کد ملی، رمز) الزامی است.")
                else:
                    # اگر داور با همین شماره وجود داشت، آپدیت شود
                    updated = False
                    for r in st.session_state.referees:
                        if normalize_phone(r.phone) == p:
                            r.first_name = first.strip()
                            r.last_name = last.strip()
                            r.national_id = n
                            r.field = field_sel
                            r.password = ref_pass
                            r.is_active = active
                            updated = True
                            break
                    if not updated:
                        st.session_state.referees.append(
                            RefereeProfile(
                                first_name=first.strip(),
                                last_name=last.strip(),
                                phone=p,
                                national_id=n,
                                field=field_sel,
                                password=ref_pass,
                                is_active=active,
                            )
                        )
                    st.success("داور ثبت/به‌روزرسانی شد ✅ (می‌تواند وارد شود)")
                    st.rerun()

        # حذف کامنت‌ها (مدیریت ویترین)
        with tabs[2]:
            st.subheader("مدیریت ویترین دانش (حذف کامنت)")
            published = [s for s in st.session_state.submissions if s.status == "published"]
            if not published:
                st.info("محتوای منتشر شده‌ای وجود ندارد.")
            else:
                for s in published:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        if not s.comments:
                            st.caption("کامنت ندارد.")
                        else:
                            for idx, cm in enumerate(list(s.comments)):
                                cc1, cc2 = st.columns([5, 1])
                                with cc1:
                                    st.write(f"- **{cm.user}**: {cm.text}")
                                with cc2:
                                    if st.button("🗑 حذف", key=f"del_cmt_{s.id}_{cm.id}"):
                                        s.comments.pop(idx)
                                        st.success("کامنت حذف شد ✅")
                                        st.rerun()

        # پیشنهاد موضوعات
        with tabs[3]:
            st.subheader("پیشنهاد موضوعات (مدیر)")
            title = st.text_input("عنوان موضوع", key="topic_title")
            field_sel = st.selectbox("حوزه", FIELDS, key="topic_field")
            desc = st.text_area("توضیحات", key="topic_desc", height=120)
            up = st.file_uploader("فایل پیوست (اختیاری)", key="topic_file")

            if st.button("ثبت موضوع", type="primary", key="topic_save"):
                if not title.strip():
                    st.error("عنوان موضوع الزامی است.")
                else:
                    fname = up.name if up else "N/A"
                    fbytes = up.getvalue() if up else None
                    st.session_state.topics.insert(
                        0,
                        TopicItem(
                            id=make_id("t"),
                            title=title.strip(),
                            field=field_sel,
                            description=desc.strip(),
                            file_name=fname,
                            file_bytes=fbytes,
                            ts=now_ts(),
                        )
                    )
                    st.success("موضوع ثبت شد ✅")
                    st.rerun()

            st.divider()
            if st.session_state.topics:
                st.caption("لیست موضوعات ثبت‌شده:")
                for t in st.session_state.topics:
                    with st.container(border=True):
                        st.write(f"**{t.title}**")
                        st.caption(f"{t.field} | {ts_str(t.ts)}")
                        st.write(t.description)

        # تحقیقات
        with tabs[4]:
            st.subheader("تحقیقات صورت گرفته (مدیر)")
            title = st.text_input("عنوان تحقیق", key="res_title")
            field_sel = st.selectbox("حوزه", FIELDS, key="res_field")
            summary = st.text_area("خلاصه / توضیحات", key="res_sum", height=120)
            up = st.file_uploader("فایل تحقیق (اختیاری)", key="res_file")

            if st.button("ثبت تحقیق", type="primary", key="res_save"):
                if not title.strip():
                    st.error("عنوان تحقیق الزامی است.")
                else:
                    fname = up.name if up else "N/A"
                    fbytes = up.getvalue() if up else None
                    st.session_state.research.insert(
                        0,
                        ResearchItem(
                            id=make_id("r"),
                            title=title.strip(),
                            field=field_sel,
                            summary=summary.strip(),
                            file_name=fname,
                            file_bytes=fbytes,
                            ts=now_ts(),
                        )
                    )
                    st.success("تحقیق ثبت شد ✅")
                    st.rerun()

            st.divider()
            if st.session_state.research:
                st.caption("لیست تحقیقات ثبت‌شده:")
                for r in st.session_state.research:
                    with st.container(border=True):
                        st.write(f"**{r.title}**")
                        st.caption(f"{r.field} | {ts_str(r.ts)}")
                        st.write(r.summary)

        # اسناد
        with tabs[5]:
            st.subheader("اسناد / نشریه‌ها (فقط مدیر)")
            doc_title = st.text_input("عنوان سند", key="doc_title")
            doc_file = st.file_uploader("فایل سند/نشریه", key="doc_file")

            if st.button("ثبت سند", type="primary", key="doc_save"):
                if not doc_title.strip() or not doc_file:
                    st.error("عنوان و فایل سند الزامی است.")
                else:
                    st.session_state.documents.insert(
                        0,
                        DocumentItem(
                            id=make_id("d"),
                            title=doc_title.strip(),
                            file_name=doc_file.name,
                            file_bytes=doc_file.getvalue(),
                            ts=now_ts(),
                        )
                    )
                    st.success("سند ثبت شد ✅")
                    st.rerun()

            st.divider()
            if not st.session_state.documents:
                st.info("سندی ثبت نشده.")
            else:
                for d in st.session_state.documents:
                    with st.container(border=True):
                        st.write(f"**{d.title}**")
                        st.caption(f"{d.file_name} | {ts_str(d.ts)}")
                        st.download_button("دانلود", data=d.file_bytes, file_name=d.file_name, key=f"dl_doc_{d.id}")

        # تایید پیام‌های تالار گفتگو
        with tabs[6]:
            st.subheader("تالار گفتگو - تایید پیام‌ها (مدیر)")
            pend = [p for p in st.session_state.forum_posts if p.status == "pending"]
            if not pend:
                st.info("پیامی برای تایید وجود ندارد.")
            else:
                for p in pend:
                    with st.container(border=True):
                        st.write(f"**از:** {p.sender_name} ({p.sender_role}) | {ts_str(p.ts)}")
                        st.write(p.text)

                        a, b = st.columns(2)
                        with a:
                            if st.button("تایید", key=f"ap_{p.id}", type="primary"):
                                p.status = "approved"
                                st.success("تایید شد ✅")
                                st.rerun()
                        with b:
                            if st.button("رد", key=f"rej_{p.id}"):
                                p.status = "rejected"
                                st.warning("رد شد")
                                st.rerun()

    # -----------------------------
    # REFEREE HOME
    # -----------------------------
    else:
        st.header("پنل داور تخصصی / نخبگان دانشی")

        mine = [s for s in st.session_state.submissions if normalize_phone(s.assigned_referee_phone) == normalize_phone(st.session_state.phone)]
        if not mine:
            st.info("فعلاً محتوایی به شما ارجاع نشده.")
        else:
            left, right = st.columns([2, 3])

            with left:
                st.subheader("ارجاع‌های من")
                for s in mine:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)} | حوزه: {s.field}")
                        if st.button("باز کردن", key=f"open_{s.id}"):
                            st.session_state.selected_submission_id = s.id
                            st.rerun()

            with right:
                s = get_submission(st.session_state.selected_submission_id) if st.session_state.selected_submission_id else None
                if not s:
                    st.info("از سمت چپ یک ارجاع انتخاب کن.")
                else:
                    st.subheader(f"بررسی: {s.title}")
                    st.caption(f"ارسال‌کننده: {s.sender_name} | {s.sender_phone} | نوع محتوا: {s.content_type}")
                    st.write(s.description)

                    if s.file_bytes:
                        st.download_button("دانلود فایل پیوست", data=s.file_bytes, file_name=s.file_name, key=f"dl_ref_{s.id}")

                    st.divider()

                    new_status = st.selectbox(
                        "نتیجه داوری",
                        ["waiting_referee", "correction_needed", "published", "rejected"],
                        format_func=status_fa,
                        key=f"ns_{s.id}"
                    )
                    feedback = st.text_area("ثبت اصلاحات / نظر داور", value=s.referee_feedback, height=120, key=f"fb_{s.id}")
                    score = st.number_input("امتیاز (0 تا 100)", 0, 100, int(s.score or 0), key=f"sc_{s.id}")
                    kcode = st.text_input("کد دانشی (برای انتشار)", value=s.knowledge_code, key=f"kc_{s.id}")

                    if st.button("ثبت نهایی داوری", type="primary", key=f"save_{s.id}"):
                        s.status = new_status
                        s.referee_feedback = feedback.strip()
                        s.score = int(score)

                        if new_status == "published" and not kcode.strip():
                            st.error("برای انتشار باید کد دانشی وارد شود.")
                            st.stop()
                        s.knowledge_code = kcode.strip()
                        st.success("ثبت شد ✅ (کاربر و مدیر نتیجه را می‌بینند)")
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Forum
# =========================================================
elif st.session_state.page == "تالار گفتگو":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("تالار گفتگو")

    st.caption("پیام‌ها ابتدا برای مدیر ارسال می‌شود و بعد از تایید در تالار نمایش داده می‌شود.")

    msg = st.text_area("درج پیام در تالار گفتگو", placeholder="پیام خود را بنویسید...", height=120)

    if st.button("ارسال پیام برای تایید مدیر", type="primary"):
        if not msg.strip():
            st.error("متن پیام خالی است.")
        else:
            st.session_state.forum_posts.insert(
                0,
                ForumPost(
                    id=make_id("p"),
                    sender_phone=st.session_state.phone,
                    sender_name=st.session_state.name,
                    sender_role=st.session_state.role,
                    text=msg.strip(),
                    ts=now_ts(),
                    status="pending",
                )
            )
            st.success("ارسال شد ✅ (بعد از تایید مدیر نمایش داده می‌شود)")
            st.rerun()

    st.divider()

    approved = [p for p in st.session_state.forum_posts if p.status == "approved"]
    if not approved:
        st.info("هنوز پیامی تایید نشده.")
    else:
        for p in approved:
            with st.container(border=True):
                st.write(f"**{p.sender_name}**: {p.text}")
                st.caption(f"{ts_str(p.ts)} | نقش: {p.sender_role}")

                st.subheader("پاسخ داور تخصصی / نخبگان")

                # پاسخ‌دهی داور: باکس بالا (طبق خواسته)
                if st.session_state.role == "referee":
                    reply = st.text_input("پاسخ شما", key=f"rep_{p.id}", placeholder="پاسخ را بنویسید...")
                    if st.button("ثبت پاسخ", key=f"rep_btn_{p.id}", type="primary"):
                        if reply.strip():
                            p.replies.append(
                                ForumReply(
                                    id=make_id("rr"),
                                    referee_phone=st.session_state.phone,
                                    referee_name=st.session_state.name,
                                    text=reply.strip(),
                                    ts=now_ts(),
                                )
                            )
                            st.success("پاسخ ثبت شد ✅")
                            st.rerun()

                # لیست پاسخ‌ها
                if p.replies:
                    for r in sorted(p.replies, key=lambda x: x.ts):
                        st.write(f"- **{r.referee_name}**: {r.text}")
                        st.caption(ts_str(r.ts))
                else:
                    st.caption("هنوز پاسخی ثبت نشده.")

    # مدیر: تایید/رد پیام‌های pending (اینجا هم گذاشتم که از صفحه اصلی هم نیاز نباشه)
    if is_admin():
        st.divider()
        st.header("تایید پیام‌ها (مدیر سامانه)")
        pend = [pp for pp in st.session_state.forum_posts if pp.status == "pending"]
        if not pend:
            st.info("پیامی برای تایید وجود ندارد.")
        else:
            for pp in pend:
                with st.container(border=True):
                    st.write(f"**از:** {pp.sender_name} ({pp.sender_role}) | {ts_str(pp.ts)}")
                    st.write(pp.text)
                    a, b = st.columns(2)
                    with a:
                        if st.button("تایید", key=f"ap_forum_{pp.id}", type="primary"):
                            pp.status = "approved"
                            st.success("تایید شد ✅")
                            st.rerun()
                    with b:
                        if st.button("رد", key=f"rej_forum_{pp.id}"):
                            pp.status = "rejected"
                            st.warning("رد شد")
                            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Profile
# =========================================================
elif st.session_state.page == "پروفایل":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("پروفایل")
    st.text_input("نام و نام خانوادگی", value=st.session_state.name, disabled=True)
    st.text_input("شماره همراه", value=st.session_state.phone, disabled=True)
    st.text_input("کد ملی", value=st.session_state.nid, disabled=True)
    st.caption(f"نقش: {st.session_state.role}")
    if st.button("🚪 خروج از سامانه", type="primary"):
        logout()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Documents
# =========================================================
else:  # اسناد
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("اسناد")

    if not is_admin():
        st.warning("این بخش فقط برای مدیر سامانه فعال است.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.subheader("بارگذاری اسناد/نشریه‌ها (مدیر)")
        doc_title = st.text_input("عنوان سند", key="doc_title_page")
        doc_file = st.file_uploader("فایل سند/نشریه", key="doc_file_page")

        if st.button("ثبت سند", type="primary", key="doc_save_page"):
            if not doc_title.strip() or not doc_file:
                st.error("عنوان و فایل سند الزامی است.")
            else:
                st.session_state.documents.insert(
                    0,
                    DocumentItem(
                        id=make_id("d"),
                        title=doc_title.strip(),
                        file_name=doc_file.name,
                        file_bytes=doc_file.getvalue(),
                        ts=now_ts(),
                    )
                )
                st.success("سند ثبت شد ✅")
                st.rerun()

        st.divider()
        if not st.session_state.documents:
            st.info("سندی ثبت نشده.")
        else:
            for d in st.session_state.documents:
                with st.container(border=True):
                    st.write(f"**{d.title}**")
                    st.caption(f"{d.file_name} | {ts_str(d.ts)}")
                    st.download_button("دانلود", data=d.file_bytes, file_name=d.file_name, key=f"dl_doc_page_{d.id}")

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
