import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional

# =========================
# Models
# =========================
@dataclass
class Comment:
    id: str
    user: str
    text: str


@dataclass
class Submission:
    id: str
    title: str
    description: str
    sender: str
    file_name: str
    field: str
    status: str = "pending"  # pending, waiting_referee, correction_needed, published
    score: int = 0
    likes: int = 0
    views: int = 0
    knowledge_code: str = ""
    referee_feedback: str = ""
    assigned_referee_phone: str = ""
    comments: List[Comment] = field(default_factory=list)


@dataclass
class RefereeProfile:
    first_name: str
    last_name: str
    phone: str
    national_id: str
    field: str


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

UNIVERSITY_MAJORS = ["عمران", "معماری", "مکانیک", "برق", "هوش مصنوعی", "صنایع", "مدیریت", "حقوق"]


def status_fa(s: str) -> str:
    return {
        "pending": "در انتظار ارجاع",
        "waiting_referee": "در انتظار نظر داور",
        "correction_needed": "نیاز به اصلاح",
        "published": "منتشر شده",
    }.get(s, s)


# =========================
# "DB" in session_state
# =========================
def ensure_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "role" not in st.session_state:
        st.session_state.role = "guest"  # user / manager / referee
    if "login_phone" not in st.session_state:
        st.session_state.login_phone = ""
    if "login_id" not in st.session_state:
        st.session_state.login_id = ""
    if "referee_phone" not in st.session_state:
        st.session_state.referee_phone = ""

    if "referees" not in st.session_state:
        st.session_state.referees = [
            RefereeProfile(
                first_name="استاد",
                last_name="نمونه",
                phone="0912",
                national_id="123",
                field="۲. حوزه فنی و مهندسی",
            )
        ]

    if "submissions" not in st.session_state:
        st.session_state.submissions = [
            Submission(
                id="s1",
                title="بهسازی زیرسازی آزادراه",
                description="سناریوی اصلاح لایه بیس",
                sender="واحد مهندسی",
                file_name="sample.pdf",
                field="۱۳. حوزه آسفالت",
                status="published",
                likes=25,
                views=500,
                knowledge_code="A-1301",
                comments=[],
            ),
            Submission(
                id="s2",
                title="اصلاح روش اجرای بتن‌ریزی",
                description="پیشنهاد بهبود فرآیند ویبره و کیورینگ",
                sender="کاربر",
                file_name="note.docx",
                field="۶. حوزه بتن",
                status="pending",
                likes=2,
                views=40,
                comments=[],
            ),
        ]

    if "id_counter" not in st.session_state:
        st.session_state.id_counter = 100

    if "selected_submission_id" not in st.session_state:
        st.session_state.selected_submission_id = None


def next_id() -> str:
    st.session_state.id_counter += 1
    return f"s{st.session_state.id_counter}"


def get_submission_by_id(sid: str) -> Optional[Submission]:
    for s in st.session_state.submissions:
        if s.id == sid:
            return s
    return None


def logout():
    st.session_state.logged_in = False
    st.session_state.role = "guest"
    st.session_state.login_phone = ""
    st.session_state.login_id = ""
    st.session_state.referee_phone = ""
    st.session_state.selected_submission_id = None
    st.rerun()


# =========================
# UI
# =========================
st.set_page_config(page_title="NEXA - Streamlit", layout="wide")
ensure_state()

st.markdown(
    """
    <div style="background:#002d5b;padding:18px;border-radius:12px;margin-bottom:12px;">
      <div style="color:white;font-size:28px;font-weight:900;">نکسا (NEXA)</div>
      <div style="color:#cfd8e3;font-size:12px;">نظام یکپارچه محتوا عاشورا</div>
    </div>
    """,
    unsafe_allow_html=True,
)

colA, colB, colC = st.columns([2, 6, 2])
with colA:
    st.caption("وضعیت ورود")
    st.write("✅ وارد شده" if st.session_state.logged_in else "⛔ وارد نشده")
with colB:
    st.caption("نقش")
    st.write(st.session_state.role)
with colC:
    if st.session_state.logged_in:
        if st.button("خروج", type="primary"):
            logout()

# =========================
# LOGIN
# =========================
if not st.session_state.logged_in:
    st.subheader("ورود")
    role = st.selectbox(
        "نوع کاربری",
        options=["user", "referee", "manager"],
        format_func=lambda x: {"user": "کاربر", "referee": "داور", "manager": "مدیر"}.get(x, x),
    )
    phone = st.text_input("شماره همراه", value=st.session_state.login_phone)
    nid = st.text_input("کد ملی (رمز)", value=st.session_state.login_id, type="password")

    if st.button("ورود نهایی", type="primary"):
        st.session_state.role = role
        st.session_state.login_phone = phone.strip()
        st.session_state.login_id = nid.strip()

        if role == "referee":
            ok = any(
                (r.phone == st.session_state.login_phone and r.national_id == st.session_state.login_id)
                for r in st.session_state.referees
            )
            if not ok:
                st.error("هویت داوری شما توسط مدیر ثبت نشده است.")
                st.stop()
            st.session_state.referee_phone = st.session_state.login_phone

        st.session_state.logged_in = True
        st.success("ورود انجام شد ✅")
        st.rerun()

    st.info("برای ورود داور: مدیر باید داور را در «ثبت داور» اضافه کند (شماره + کد ملی).")
    st.stop()

# =========================
# MAIN NAV
# =========================
tabs = st.tabs(["میز کار", "تالار گفتگو", "پروفایل"])

# =========================
# TAB: WORKBENCH
# =========================
with tabs[0]:
    role = st.session_state.role

    if role == "user":
        t1, t2, t3, t4 = st.tabs(["ویترین دانش", "ارسال محتوا", "وضعیت پیگیری", "پیشنهاد موضوعات"])

        with t1:
            st.subheader("ویترین دانش")
            for s in st.session_state.submissions:
                with st.container(border=True):
                    st.markdown(f"### {s.title}")
                    st.caption(f"{s.field} | وضعیت: {status_fa(s.status)} | کد دانشی: {s.knowledge_code or '-'}")
                    st.write(s.description)
                    c1, c2, c3 = st.columns([1, 2, 3])
                    with c1:
                        if st.button(f"❤️ پسندیدن ({s.likes})", key=f"like_{s.id}"):
                            s.likes += 1
                            st.rerun()
                    with c2:
                        st.write(f"👁️ بازدید: {s.views}")
                    with c3:
                        open_cm = st.checkbox("نمایش نظرات", key=f"show_comments_{s.id}")
                    if open_cm:
                        if not s.comments:
                            st.info("نظری ثبت نشده.")
                        else:
                            for cm in s.comments:
                                st.write(f"- **{cm.user}**: {cm.text}")

                        new_text = st.text_input("دیدگاه جدید", key=f"new_comment_{s.id}")
                        if st.button("ثبت دیدگاه", key=f"add_comment_{s.id}"):
                            if new_text.strip():
                                s.comments.append(Comment(id="c", user="کاربر", text=new_text.strip()))
                                st.success("ثبت شد ✅")
                                st.rerun()

        with t2:
            st.subheader("ارسال محتوا")
            title = st.text_input("عنوان", key="sub_title")
            desc = st.text_area("توضیحات", key="sub_desc")
            field_sel = st.selectbox("حوزه تخصصی", FIELDS, key="sub_field")
            uploaded = st.file_uploader("فایل پیوست", type=None)

            if st.button("ثبت و ارسال", type="primary"):
                if not title.strip():
                    st.error("عنوان الزامی است.")
                else:
                    fname = uploaded.name if uploaded is not None else "N/A"
                    new = Submission(
                        id=next_id(),
                        title=title.strip(),
                        description=desc.strip(),
                        sender="کاربر",
                        file_name=fname,
                        field=field_sel,
                        status="pending",
                        comments=[],
                    )
                    st.session_state.submissions.insert(0, new)
                    st.success("ثبت شد و در صف ارجاع قرار گرفت ✅")
                    st.rerun()

        with t3:
            st.subheader("وضعیت پیگیری")
            my = [s for s in st.session_state.submissions if s.sender == "کاربر"]
            if not my:
                st.info("هنوز چیزی ارسال نکردی.")
            else:
                for s in my:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)}")
                        if s.referee_feedback:
                            st.write(f"📝 بازخورد: {s.referee_feedback}")

        with t4:
            st.subheader("پیشنهاد موضوعات")
            for m in UNIVERSITY_MAJORS:
                st.write(f"- رشته **{m}**: پیشنهاد موضوعات خدمت و پایان‌نامه")

    elif role == "manager":
        t1, t2 = st.tabs(["میز ارجاع", "ثبت داور"])

        with t1:
            st.subheader("میز ارجاع")
            pending = [s for s in st.session_state.submissions if s.status == "pending"]
            if not pending:
                st.info("موردی برای ارجاع وجود ندارد.")
            else:
                for s in pending:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"فرستنده: {s.sender} | حوزه: {s.field}")
                        if st.session_state.referees:
                            ref = st.selectbox(
                                "انتخاب داور",
                                options=st.session_state.referees,
                                format_func=lambda r: f"{r.first_name} {r.last_name} ({r.phone}) - {r.field}",
                                key=f"ref_sel_{s.id}",
                            )
                            if st.button("ارجاع", key=f"assign_{s.id}", type="primary"):
                                s.status = "waiting_referee"
                                s.assigned_referee_phone = ref.phone
                                st.success("ارجاع انجام شد ✅")
                                st.rerun()
                        else:
                            st.warning("داوری ثبت نشده. از تب «ثبت داور» اضافه کن.")

        with t2:
            st.subheader("ثبت داور تخصصی")
            c1, c2 = st.columns(2)
            with c1:
                first = st.text_input("نام", key="rf_first")
                phone = st.text_input("شماره همراه", key="rf_phone")
                field_sel = st.selectbox("حوزه", FIELDS, key="rf_field")
            with c2:
                last = st.text_input("نام خانوادگی", key="rf_last")
                nid = st.text_input("کد ملی (ID ورود)", key="rf_nid")

            if st.button("ثبت داور", type="primary"):
                if not phone.strip() or not nid.strip():
                    st.error("شماره همراه و کد ملی الزامی است.")
                else:
                    st.session_state.referees.append(
                        RefereeProfile(
                            first_name=first.strip() or "داور",
                            last_name=last.strip() or "جدید",
                            phone=phone.strip(),
                            national_id=nid.strip(),
                            field=field_sel,
                        )
                    )
                    st.success("داور ثبت شد ✅")
                    st.rerun()

    else:  # referee
        st.subheader("پنل داور")

        mine = [
            s for s in st.session_state.submissions
            if s.assigned_referee_phone == st.session_state.referee_phone
        ]

        if not mine:
            st.info("فعلاً چیزی به شما ارجاع نشده.")
        else:
            left, right = st.columns([2, 3])

            with left:
                st.caption("ارجاع‌های شما")
                for s in mine:
                    with st.container(border=True):
                        st.write(f"**{s.title}**")
                        st.caption(f"وضعیت: {status_fa(s.status)}")
                        if st.button("انتخاب", key=f"pick_{s.id}"):
                            st.session_state.selected_submission_id = s.id
                            st.rerun()

            with right:
                sid = st.session_state.selected_submission_id
                s = get_submission_by_id(sid) if sid else None
                if s is None:
                    st.info("یک مورد را از ستون چپ انتخاب کن.")
                else:
                    st.markdown(f"### بررسی: {s.title}")
                    st.write(s.description)
                    st.caption(f"حوزه: {s.field} | فایل: {s.file_name}")

                    new_status = st.selectbox(
                        "نتیجه بررسی",
                        options=["waiting_referee", "correction_needed", "published"],
                        index=["waiting_referee", "correction_needed", "published"].index(
                            s.status if s.status in ["waiting_referee", "correction_needed", "published"] else "waiting_referee"
                        ),
                    )
                    feedback = st.text_area("بازخورد داور", value=s.referee_feedback)
                    kcode = st.text_input("کد دانشی (اختیاری)", value=s.knowledge_code)

                    if st.button("ثبت نتیجه", type="primary"):
                        s.status = new_status
                        s.referee_feedback = feedback.strip()
                        s.knowledge_code = kcode.strip()
                        st.success("نتیجه ثبت شد ✅")
                        st.rerun()

# =========================
# TAB: CHAT
# =========================
with tabs[1]:
    st.subheader("تالار گفتگو (دمو)")
    st.info("این بخش نمونه است. می‌تونیم بعداً چت واقعی (DB/Socket) اضافه کنیم.")
    msg = st.text_input("پیام")
    if st.button("ارسال پیام"):
        st.success("ارسال شد (دمو) ✅")

# =========================
# TAB: PROFILE
# =========================
with tabs[2]:
    st.subheader("پروفایل (دمو)")
    st.text_input("نام و نام خانوادگی", key="pf_name")
    st.text_input("کد ملی", key="pf_nid")
    st.text_input("شماره همراه", key="pf_phone")
    st.button("ذخیره")
