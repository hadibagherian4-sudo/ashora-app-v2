import re
import time
import os
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# =========================
# Models
# =========================
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
    suggested_topic_id: str  # "" if none
    field: str  # حوزه پیشنهادی
    content_type: str  # نوع محتوا
    file_name: str
    file_bytes: bytes | None
    cover_image_path: str  # مسیر عکس از ریپو (اختیاری)
    status: str = "pending"  # pending, waiting_referee, correction_needed, published, rejected
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
    text: str
    ts: float
    status: str = "pending"  # pending -> approved/rejected
    moderator_note: str = ""
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


def status_fa(s: str) -> str:
    return {
        "pending": "در انتظار ارجاع مدیر سامانه",
        "waiting_referee": "در انتظار نظر داور",
        "correction_needed": "نیاز به اصلاح",
        "published": "تایید و انتشار در ویترین دانش",
        "rejected": "عدم تایید",
    }.get(s, s)


# =========================
# Profanity guard (ساده)
# =========================
BAD_WORDS = ["کص", "کیر", "کس", "جنده", "fuck", "shit", "bitch", "asshole"]


def has_bad_words(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in BAD_WORDS)


def normalize_phone(p: str) -> str:
    return re.sub(r"\s+", "", p.strip())


def normalize_nid(n: str) -> str:
    return re.sub(r"\s+", "", n.strip())


def now_ts() -> float:
    return time.time()


def make_id(prefix: str) -> str:
    st.session_state._id_counter += 1
    return f"{prefix}{st.session_state._id_counter}"


def file_exists(path: str) -> bool:
    try:
        return os.path.exists(path)
    except Exception:
        return False


# =========================
# Session storage
# =========================
def ensure_state():
    if "_id_counter" not in st.session_state:
        st.session_state._id_counter = 1000

    # auth
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("role", "guest")  # user/manager/referee
    st.session_state.setdefault("phone", "")
    st.session_state.setdefault("nid", "")
    st.session_state.setdefault("name", "")

    # users registry (for user signup)
    st.session_state.setdefault("users", {})  # phone -> {name,nid}

    # manager fixed account
    st.session_state.setdefault("manager_phone", "09146862029")
    st.session_state.setdefault("manager_nid", "1362362506")

    # referees
    st.session_state.setdefault(
        "referees",
        [
            RefereeProfile(
                first_name="استاد",
                last_name="نمونه",
                phone="0912",
                national_id="123",
                field="۲. حوزه فنی و مهندسی",
            )
        ],
    )

    # topics + research + documents
    st.session_state.setdefault("topics", [])     # List[TopicItem]
    st.session_state.setdefault("research", [])   # List[ResearchItem]
    st.session_state.setdefault("documents", [])  # List[DocumentItem]

    # submissions
    st.session_state.setdefault(
        "submissions",
        [
            Submission(
                id="s1",
                title="بهسازی زیرسازی آزادراه",
                description="سناریوی اصلاح لایه بیس",
                sender_phone="09120000000",
                sender_name="واحد مهندسی",
                suggested_topic_id="",
                field="۱۳. حوزه آسفالت",
                content_type="نوشتاری",
                file_name="sample.pdf",
                file_bytes=None,
                cover_image_path="Picture1.png" if file_exists("Picture1.png") else "",
                status="published",
                likes=25,
                views=500,
                knowledge_code="A-1301",
            )
        ],
    )

    # forum posts
    st.session_state.setdefault("forum_posts", [])  # List[ForumPost]

    # UI state
    st.session_state.setdefault("selected_submission_id", None)
    st.session_state.setdefault("page", "صفحه اصلی")


def logout():
    st.session_state.logged_in = False
    st.session_state.role = "guest"
    st.session_state.phone = ""
    st.session_state.nid = ""
    st.session_state.name = ""
    st.session_state.selected_submission_id = None
    st.rerun()


def find_referee(phone: str, nid: str) -> Optional[RefereeProfile]:
    for r in st.session_state.referees:
        if (
            normalize_phone(r.phone) == normalize_phone(phone)
            and normalize_nid(r.national_id) == normalize_nid(nid)
            and r.is_active
        ):
            return r
    return None


def get_submission(sid: str) -> Optional[Submission]:
    for s in st.session_state.submissions:
        if s.id == sid:
            return s
    return None


def get_topic(tid: str) -> Optional[TopicItem]:
    for t in st.session_state.topics:
        if t.id == tid:
            return t
    return None


# =========================
# Page config + header
# =========================
st.set_page_config(page_title="NEXA - Ashora", layout="wide")
ensure_state()

header_left, header_mid, header_right = st.columns([1.2, 6, 1.2])
with header_left:
    # لوگو در ریپو: logo.png یا official_logo.png
    if file_exists("logo.png"):
        st.image("logo.png", width=90)
    elif file_exists("official_logo.png"):
        st.image("official_logo.png", width=90)
    else:
        st.write("")

with header_mid:
    st.markdown(
        """
        <div style="padding:10px 0;">
          <div style="font-size:34px;font-weight:900;color:#002d5b;">نکسا (NEXA)</div>
          <div style="color:#4b5563;font-size:14px;">نظام یکپارچه محتوا عاشورا</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    if st.session_state.logged_in:
        st.caption(f"نقش: {st.session_state.role}")
        if st.button("خروج", type="primary"):
            logout()
    else:
        st.caption("وارد نشده")

st.divider()

# =========================
# LOGIN + SIGNUP
# =========================
if not st.session_state.logged_in:
    st.subheader("ورود به سامانه")

    role = st.selectbox(
        "نوع کاربری",
        options=["user", "referee", "manager"],
        format_func=lambda x: {
            "user": "کاربر",
            "referee": "داور تخصصی / نخبگان دانشی",
            "manager": "مدیر سامانه",
        }.get(x, x),
    )

    phone = st.text_input("شماره همراه", value=st.session_state.phone)
    nid = st.text_input("کد ملی", value=st.session_state.nid, type="password")

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("ورود", type="primary"):
            phone_n = normalize_phone(phone)
            nid_n = normalize_nid(nid)

            if not phone_n or not nid_n:
                st.error("شماره همراه و کد ملی را وارد کنید.")
                st.stop()

            if role == "user":
                u = st.session_state.users.get(phone_n)
                if not u or normalize_nid(u["nid"]) != nid_n:
                    st.error("کاربر یافت نشد. لطفاً ثبت‌نام کنید یا مشخصات را درست وارد کنید.")
                    st.stop()
                st.session_state.name = u["name"]

            if role == "manager":
                if (
                    phone_n != normalize_phone(st.session_state.manager_phone)
                    or nid_n != normalize_nid(st.session_state.manager_nid)
                ):
                    st.error("شماره همراه یا کد ملی مدیر سامانه اشتباه است.")
                    st.stop()
                st.session_state.name = "مدیر سامانه"

            if role == "referee":
                ref = find_referee(phone_n, nid_n)
                if not ref:
                    st.error("داور با این مشخصات ثبت نشده یا غیرفعال است.")
                    st.stop()
                st.session_state.name = f"{ref.first_name} {ref.last_name}"

            st.session_state.role = role
            st.session_state.phone = phone_n
            st.session_state.nid = nid_n
            st.session_state.logged_in = True
            st.success("ورود انجام شد ✅")
            st.rerun()

    with c2:
        st.caption("ثبت‌نام فقط برای کاربران")
        if st.button("ثبت‌نام کاربر"):
            st.session_state._show_signup = True

    if st.session_state.get("_show_signup", False):
        st.divider()
        st.subheader("ثبت‌نام کاربر")
        name = st.text_input("نام و نام خانوادگی")
        phone_s = st.text_input("شماره همراه (برای ثبت‌نام)", key="signup_phone")
        nid_s = st.text_input("کد ملی (برای ثبت‌نام)", key="signup_nid", type="password")

        if st.button("ایجاد حساب کاربری", type="primary"):
            p = normalize_phone(phone_s)
            n = normalize_nid(nid_s)
            if not name.strip() or not p or not n:
                st.error("نام، شماره همراه و کد ملی الزامی است.")
                st.stop()
            st.session_state.users[p] = {"name": name.strip(), "nid": n}
            st.success("ثبت‌نام انجام شد ✅ حالا می‌تونی وارد بشی.")
            st.session_state._show_signup = False

    st.stop()

# =========================
# Bottom Navigation (شبیه نرم افزار)
# =========================
nav_labels = ["صفحه اصلی", "تالار گفتگو", "پروفایل", "اسناد"]
nav_icons = {"صفحه اصلی": "🏠", "تالار گفتگو": "💬", "پروفایل": "👤", "اسناد": "📄"}

nav_display = [f"{nav_icons[x]} {x}" for x in nav_labels]
current_display = f"{nav_icons[st.session_state.page]} {st.session_state.page}"

choice = st.radio(
    "",
    options=nav_display,
    index=nav_display.index(current_display),
    horizontal=True,
    label_visibility="collapsed",
)

st.session_state.page = choice.split(" ", 1)[1]  # after emoji

st.divider()


# =========================
# PAGE: HOME (Role-based)
# =========================
if st.session_state.page == "صفحه اصلی":
    role = st.session_state.role

    # ---------- USER ----------
    if role == "user":
        t1, t2, t3, t4, t5 = st.tabs(["ویترین دانش", "ارسال محتوا", "وضعیت پیگیری", "پیشنهاد موضوعات", "تحقیقات صورت گرفته"])

        # ویترین دانش (فقط published)
        with t1:
            st.subheader("ویترین دانش")
            published = [s for s in st.session_state.submissions if s.status == "published"]
            if not published:
                st.info("فعلاً محتوایی منتشر نشده.")

            for s in published:
                with st.container(border=True):
                    s.views += 1

                    # عکس ویترین: از فایل‌های موجود در ریپو
                    cover = s.cover_image_path
                    if cover and file_exists(cover):
                        st.image(cover, use_container_width=True)
                    elif file_exists("Picture1.png"):
                        st.image("Picture1.png", use_container_width=True)

                    st.markdown(f"### {s.title}")
                    st.caption(f"{s.field} | نوع محتوا: {s.content_type} | کد دانشی: {s.knowledge_code or '-'} | بازدید: {s.views}")
                    st.write(s.description)

                    c1, c2 = st.columns([1, 3])
                    with c1:
                        if st.button(f"❤️ لایک ({s.likes})", key=f"like_{s.id}"):
                            s.likes += 1
                            st.rerun()
                    with c2:
                        st.write("")

                    st.markdown("#### نظرات")
                    if s.comments:
                        for cm in sorted(s.comments, key=lambda x: x.ts):
                            st.write(f"- **{cm.user}**: {cm.text}")
                    else:
                        st.caption("نظری ثبت نشده.")

                    new_comment = st.text_input("افزودن نظر", key=f"cmt_{s.id}", placeholder="نظرت رو بنویس...")
                    if st.button("ثبت نظر", key=f"cmt_btn_{s.id}"):
                        if new_comment.strip():
                            s.comments.append(
                                Comment(
                                    id=make_id("c"),
                                    user=st.session_state.name,
                                    text=new_comment.strip(),
                                    ts=now_ts(),
                                )
                            )
                            st.success("نظر ثبت شد ✅")
                            st.rerun()

        # ارسال محتوا
        with t2:
            st.subheader("ارسال محتوا")

            # انتخاب موضوع پیشنهادی (اگر مدیر گذاشته باشد)
            topic_options = ["(بدون انتخاب موضوع)"] + [f"{t.title} | {t.field}" for t in st.session_state.topics]
            topic_pick = st.selectbox("انتخاب موضوع از پیشنهادات مدیر (اختیاری)", topic_options)
            picked_topic_id = ""
            if topic_pick != "(بدون انتخاب موضوع)":
                # پیدا کردن آیتم
                for t in st.session_state.topics:
                    if f"{t.title} | {t.field}" == topic_pick:
                        picked_topic_id = t.id
                        break

            # اگر موضوع انتخاب شد، عنوان/توضیح پر شود
            default_title = ""
            default_desc = ""
            default_field = FIELDS[0]
            if picked_topic_id:
                t = get_topic(picked_topic_id)
                if t:
                    default_title = t.title
                    default_desc = t.description
                    default_field = t.field

            title = st.text_input("عنوان", value=default_title)
            desc = st.text_area("توضیحات", value=default_desc, height=120)

            field_sel = st.selectbox("حوزه پیشنهادی", FIELDS, index=FIELDS.index(default_field) if default_field in FIELDS else 0)
            content_type = st.selectbox("نوع محتوا", CONTENT_TYPES)

            st.markdown("#### پیوست فایل")
            uploaded = st.file_uploader("برای انتخاب فایل کلیک کنید", type=None, accept_multiple_files=False)

            st.markdown("#### تصویر ویترین (اختیاری)")
            cover_pick = st.selectbox(
                "انتخاب تصویر از فایل‌های موجود در ریپو",
                options=["(خالی)", "Picture1.png", "official_logo.png", "logo.png"],
            )
            cover_path = "" if cover_pick == "(خالی)" else cover_pick
            if cover_path and not file_exists(cover_path):
                cover_path = ""

            if st.button("ثبت و ارسال به مدیر سامانه", type="primary"):
                if not title.strip():
                    st.error("عنوان الزامی است.")
                else:
                    fname = uploaded.name if uploaded is not None else "N/A"
                    fbytes = uploaded.getvalue() if uploaded is not None else None

                    new = Submission(
                        id=make_id("s"),
                        title=title.strip(),
                        description=desc.strip(),
                        sender_phone=st.session_state.phone,
                        sender_name=st.session_state.name,
                        suggested_topic_id=picked_topic_id,
                        field=field_sel,
                        content_type=content_type,
                        file_name=fname,
                        file_bytes=fbytes,
                        cover_image_path=cover_path,
                        status="pending",
                    )
                    st.session_state.submissions.insert(0, new)
                    st.success("ارسال شد ✅ (منتظر ارجاع مدیر سامانه)")
                    st.rerun()

            st.caption("اگر پنجره انتخاب فایل باز نمی‌شود: با مرورگر Chrome تست کنید.")

        # وضعیت پیگیری
        with t3:
            st.subheader("وضعیت پیگیری")
            my = [s for s in st.session_state.submissions if s.sender_phone == st.session_state.phone]
            if not my:
                st.info("هنوز محتوایی ارسال نکردی.")
            else:
                for s in my:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)} | نوع محتوا: {s.content_type} | حوزه: {s.field}")
                        if s.assigned_referee_name:
                            st.write(f"داور: {s.assigned_referee_name}")
                        if s.referee_feedback:
                            st.write(f"📝 اصلاحات/نظر داور: {s.referee_feedback}")
                        if s.score:
                            st.write(f"⭐ امتیاز داور: {s.score}")
                        if s.status == "published":
                            st.write(f"کد دانشی: **{s.knowledge_code}**")

        # پیشنهاد موضوعات (نمایش از مدیر)
        with t4:
            st.subheader("پیشنهاد موضوعات")
            if not st.session_state.topics:
                st.info("مدیر سامانه هنوز موضوعی بارگذاری نکرده.")
            else:
                for t in sorted(st.session_state.topics, key=lambda x: x.ts, reverse=True):
                    with st.container(border=True):
                        st.write(f"**{t.title}**")
                        st.caption(f"حوزه: {t.field}")
                        st.write(t.description)
                        if t.file_bytes:
                            st.download_button("دانلود پیوست موضوع", data=t.file_bytes, file_name=t.file_name, key=f"dl_topic_{t.id}")

        # تحقیقات صورت گرفته
        with t5:
            st.subheader("تحقیقات صورت گرفته")
            if not st.session_state.research:
                st.info("مدیر سامانه هنوز تحقیقی بارگذاری نکرده.")
            else:
                for r in sorted(st.session_state.research, key=lambda x: x.ts, reverse=True):
                    with st.container(border=True):
                        st.write(f"**{r.title}**")
                        st.caption(f"حوزه: {r.field}")
                        st.write(r.summary)
                        if r.file_bytes:
                            st.download_button("دانلود فایل تحقیق", data=r.file_bytes, file_name=r.file_name, key=f"dl_res_{r.id}")

    # ---------- MANAGER ----------
    elif st.session_state.role == "manager":
        t1, t2, t3, t4 = st.tabs(["میز ارجاع", "ثبت داور تخصصی", "پیشنهاد موضوعات", "تحقیقات صورت گرفته"])

        # میز ارجاع مدیر
        with t1:
            st.subheader("میز ارجاع مدیر سامانه")
            pending = [s for s in st.session_state.submissions if s.status == "pending"]
            if not pending:
                st.info("محتوای جدید برای ارجاع وجود ندارد.")
            else:
                for s in pending:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"فرستنده: {s.sender_name} ({s.sender_phone}) | حوزه پیشنهادی: {s.field} | نوع محتوا: {s.content_type}")
                        if s.suggested_topic_id:
                            t = get_topic(s.suggested_topic_id)
                            if t:
                                st.caption(f"موضوع انتخاب‌شده از پیشنهادات مدیر: {t.title}")

                        st.write(s.description)

                        if s.file_bytes:
                            st.download_button("دانلود فایل پیوست", data=s.file_bytes, file_name=s.file_name, key=f"dl_sub_{s.id}")

                        refs_in_field = [r for r in st.session_state.referees if r.is_active and r.field == s.field]
                        if not refs_in_field:
                            st.warning("برای این حوزه داور فعالی ثبت نشده.")
                        else:
                            ref = st.selectbox(
                                "انتخاب داور",
                                options=refs_in_field,
                                format_func=lambda r: f"{r.first_name} {r.last_name} - {r.phone}",
                                key=f"ref_{s.id}",
                            )
                            if st.button("بررسی و ارجاع", key=f"assign_{s.id}", type="primary"):
                                s.status = "waiting_referee"
                                s.assigned_referee_phone = normalize_phone(ref.phone)
                                s.assigned_referee_name = f"{ref.first_name} {ref.last_name}"
                                st.success("ارجاع انجام شد ✅")
                                st.rerun()

        # ثبت داور
        with t2:
            st.subheader("ثبت داور تخصصی / نخبگان دانشی")
            c1, c2 = st.columns(2)
            with c1:
                first = st.text_input("نام", key="rf_first")
                phone = st.text_input("شماره همراه", key="rf_phone")
                field_sel = st.selectbox("حوزه فعالیت داوری", FIELDS, key="rf_field")
            with c2:
                last = st.text_input("نام خانوادگی", key="rf_last")
                nid = st.text_input("کد ملی (ID ورود)", key="rf_nid", type="password")

            active = st.checkbox("فعال باشد", value=True)

            if st.button("ساخت حساب داوری و تایید نهایی", type="primary"):
                p = normalize_phone(phone)
                n = normalize_nid(nid)
                if not p or not n:
                    st.error("شماره همراه و کد ملی الزامی است.")
                else:
                    updated = False
                    for r in st.session_state.referees:
                        if normalize_phone(r.phone) == p:
                            r.first_name = first.strip() or r.first_name
                            r.last_name = last.strip() or r.last_name
                            r.national_id = n
                            r.field = field_sel
                            r.is_active = active
                            updated = True
                            break
                    if not updated:
                        st.session_state.referees.append(
                            RefereeProfile(
                                first_name=first.strip() or "داور",
                                last_name=last.strip() or "جدید",
                                phone=p,
                                national_id=n,
                                field=field_sel,
                                is_active=active,
                            )
                        )
                    st.success("داور ثبت شد ✅ حالا می‌تواند با همین شماره و کد ملی وارد شود.")
                    st.rerun()

            st.divider()
            st.caption("لیست داوران")
            for r in st.session_state.referees:
                st.write(f"- {r.first_name} {r.last_name} | {r.phone} | {r.field} | {'فعال' if r.is_active else 'غیرفعال'}")

        # پیشنهاد موضوعات (مدیر بارگذاری کند)
        with t3:
            st.subheader("پیشنهاد موضوعات (بارگذاری توسط مدیر)")
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
            st.markdown("### لیست موضوعات")
            if not st.session_state.topics:
                st.info("موضوعی ثبت نشده.")
            else:
                for t in st.session_state.topics:
                    with st.container(border=True):
                        st.write(f"**{t.title}**")
                        st.caption(f"حوزه: {t.field}")
                        st.write(t.description)
                        if t.file_bytes:
                            st.download_button("دانلود پیوست", data=t.file_bytes, file_name=t.file_name, key=f"dl_topic_m_{t.id}")

        # تحقیقات صورت گرفته (مدیر بارگذاری کند)
        with t4:
            st.subheader("تحقیقات صورت گرفته (بارگذاری توسط مدیر)")
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
            st.markdown("### لیست تحقیقات")
            if not st.session_state.research:
                st.info("تحقیقی ثبت نشده.")
            else:
                for r in st.session_state.research:
                    with st.container(border=True):
                        st.write(f"**{r.title}**")
                        st.caption(f"حوزه: {r.field}")
                        st.write(r.summary)
                        if r.file_bytes:
                            st.download_button("دانلود فایل", data=r.file_bytes, file_name=r.file_name, key=f"dl_res_m_{r.id}")

    # ---------- REFEREE ----------
    else:
        st.subheader("پنل داور تخصصی / نخبگان دانشی")

        mine = [s for s in st.session_state.submissions if normalize_phone(s.assigned_referee_phone) == normalize_phone(st.session_state.phone)]

        if not mine:
            st.info("فعلاً محتوایی به شما ارجاع نشده.")
        else:
            left, right = st.columns([2, 3])

            with left:
                st.markdown("### ارجاع‌های من")
                for s in mine:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)} | حوزه: {s.field} | نوع محتوا: {s.content_type}")
                        if st.button("باز کردن", key=f"open_{s.id}"):
                            st.session_state.selected_submission_id = s.id
                            st.rerun()

            with right:
                sid = st.session_state.selected_submission_id
                s = get_submission(sid) if sid else None
                if not s:
                    st.info("یک مورد را از سمت چپ انتخاب کن.")
                else:
                    st.markdown(f"### بررسی: {s.title}")
                    st.write(f"ارسال‌کننده: **{s.sender_name}** ({s.sender_phone})")
                    st.write(f"حوزه: **{s.field}** | نوع محتوا: **{s.content_type}**")
                    st.write(s.description)

                    if s.file_bytes:
                        st.download_button("دانلود فایل پیوست", data=s.file_bytes, file_name=s.file_name, key=f"dl_ref_{s.id}")

                    st.divider()
                    st.markdown("#### ثبت اصلاحات / امتیاز / نتیجه")

                    new_status = st.selectbox(
                        "نتیجه",
                        options=["waiting_referee", "correction_needed", "published", "rejected"],
                        index=["waiting_referee", "correction_needed", "published", "rejected"].index(
                            s.status if s.status in ["waiting_referee", "correction_needed", "published", "rejected"] else "waiting_referee"
                        ),
                    )
                    feedback = st.text_area("اصلاحات / نظر داور", value=s.referee_feedback, height=120)
                    score = st.number_input("امتیاز (0 تا 100)", min_value=0, max_value=100, value=int(s.score or 0), step=1)
                    kcode = st.text_input("کد دانشی (برای انتشار در ویترین دانش)", value=s.knowledge_code)

                    if st.button("ثبت نهایی", type="primary"):
                        s.status = new_status
                        s.referee_feedback = feedback.strip()
                        s.score = int(score)

                        if new_status == "published" and not kcode.strip():
                            st.error("برای انتشار باید کد دانشی وارد شود.")
                            st.stop()

                        s.knowledge_code = kcode.strip()
                        st.success("ثبت شد ✅")
                        st.rerun()


# =========================
# PAGE: Forum
# =========================
elif st.session_state.page == "تالار گفتگو":
    st.subheader("تالار گفتگو")

    role = st.session_state.role

    st.markdown("### درج پیام در تالار گفتگو")
    msg = st.text_area("متن پیام", placeholder="پیام خود را بنویسید...", height=120)

    if st.button("ارسال پیام به مدیر برای تایید", type="primary"):
        if not msg.strip():
            st.error("متن پیام خالی است.")
        else:
            flagged = has_bad_words(msg)
            post = ForumPost(
                id=make_id("p"),
                sender_phone=st.session_state.phone,
                sender_name=st.session_state.name,
                text=msg.strip(),
                ts=now_ts(),
                status="pending",
                moderator_note="(مشکوک به کلمات نامناسب)" if flagged else "",
                replies=[],
            )
            st.session_state.forum_posts.insert(0, post)
            st.success("ارسال شد ✅ (منتظر تایید مدیر)")
            st.rerun()

    st.divider()

    # نمایش تایید شده‌ها
    approved = [p for p in st.session_state.forum_posts if p.status == "approved"]
    if not approved:
        st.info("هنوز پیامی تایید نشده.")
    else:
        st.markdown("### پیام‌های تایید شده")
        for p in approved:
            with st.container(border=True):
                st.write(f"**{p.sender_name}**: {p.text}")
                st.caption(time.strftime("%Y-%m-%d %H:%M", time.localtime(p.ts)))

                st.markdown("**پاسخ داور تخصصی / نخبگان**")
                if p.replies:
                    for r in sorted(p.replies, key=lambda x: x.ts):
                        st.write(f"- **{r.referee_name}**: {r.text}")

                if role == "referee":
                    reply = st.text_input("پاسخ شما", key=f"reply_{p.id}", placeholder="پاسخ را بنویسید...")
                    if st.button("ثبت پاسخ", key=f"reply_btn_{p.id}"):
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

    # مدیریت تایید پیام‌ها برای مدیر
    if role == "manager":
        st.divider()
        st.subheader("مدیریت تایید پیام‌ها")
        pend = [p for p in st.session_state.forum_posts if p.status == "pending"]
        if not pend:
            st.info("پیامی برای تایید وجود ندارد.")
        else:
            for p in pend:
                with st.container(border=True):
                    st.write(f"**از:** {p.sender_name} ({p.sender_phone})")
                    st.write(p.text)
                    note = st.text_input("یادداشت مدیر (اختیاری)", key=f"note_{p.id}")
                    cA, cB = st.columns(2)
                    with cA:
                        if st.button("تایید", key=f"ap_{p.id}", type="primary"):
                            p.status = "approved"
                            p.moderator_note = note.strip()
                            st.success("تایید شد ✅")
                            st.rerun()
                    with cB:
                        if st.button("رد", key=f"rej_{p.id}"):
                            p.status = "rejected"
                            p.moderator_note = note.strip()
                            st.warning("رد شد.")
                            st.rerun()


# =========================
# PAGE: Profile
# =========================
elif st.session_state.page == "پروفایل":
    st.subheader("پروفایل")
    st.text_input("نام و نام خانوادگی", value=st.session_state.name, disabled=True)
    st.text_input("شماره همراه", value=st.session_state.phone, disabled=True)
    st.text_input("کد ملی", value="********", disabled=True)
    if st.session_state.role == "manager":
        st.caption("حساب مدیر سامانه فعال است.")


# =========================
# PAGE: Documents (Manager only)
# =========================
else:
    st.subheader("اسناد")

    if st.session_state.role != "manager":
        st.warning("این بخش فقط برای مدیر سامانه فعال است.")
        st.stop()

    st.markdown("### بارگذاری اسناد و نشریه‌های مرتبط")
    title = st.text_input("عنوان سند")
    up = st.file_uploader("فایل سند/نشریه", type=None)

    if st.button("ثبت سند", type="primary"):
        if not title.strip() or not up:
            st.error("عنوان و فایل سند الزامی است.")
        else:
            st.session_state.documents.insert(
                0,
                DocumentItem(
                    id=make_id("d"),
                    title=title.strip(),
                    file_name=up.name,
                    file_bytes=up.getvalue(),
                    ts=now_ts(),
                )
            )
            st.success("سند ثبت شد ✅")
            st.rerun()

    st.divider()
    st.markdown("### لیست اسناد")
    if not st.session_state.documents:
        st.info("سندی ثبت نشده.")
    else:
        for d in st.session_state.documents:
            with st.container(border=True):
                st.write(f"**{d.title}**")
                st.caption(d.file_name)
                st.download_button("دانلود", data=d.file_bytes, file_name=d.file_name, key=f"dl_doc_{d.id}")
