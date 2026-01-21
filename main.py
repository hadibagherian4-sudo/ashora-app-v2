import os
import re
import time
import base64
import sqlite3
import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# =========================================================
# DB (SQLite)
# =========================================================
DB_PATH = "nexa.db"

def db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def db_init():
    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        phone TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        nid TEXT NOT NULL,
        password TEXT NOT NULL,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS referees(
        phone TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        nid TEXT NOT NULL,
        field TEXT NOT NULL,
        password TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS topics(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        field TEXT NOT NULL,
        description TEXT NOT NULL,
        file_name TEXT,
        file_bytes BLOB,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS research(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        field TEXT NOT NULL,
        summary TEXT NOT NULL,
        file_name TEXT,
        file_bytes BLOB,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_bytes BLOB NOT NULL,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        sender_phone TEXT NOT NULL,
        sender_name TEXT NOT NULL,
        sender_nid TEXT NOT NULL,
        suggested_topic_id TEXT,
        field TEXT NOT NULL,
        content_type TEXT NOT NULL,
        file_name TEXT,
        file_mime TEXT,
        file_bytes BLOB,
        status TEXT NOT NULL,
        score INTEGER NOT NULL DEFAULT 0,
        likes INTEGER NOT NULL DEFAULT 0,
        views INTEGER NOT NULL DEFAULT 0,
        knowledge_code TEXT,
        referee_feedback TEXT,
        assigned_referee_phone TEXT,
        assigned_referee_name TEXT,
        created_ts REAL NOT NULL,
        FOREIGN KEY(sender_phone) REFERENCES users(phone) ON DELETE NO ACTION
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS submission_likes(
        submission_id TEXT NOT NULL,
        user_phone TEXT NOT NULL,
        created_ts REAL NOT NULL,
        PRIMARY KEY(submission_id, user_phone),
        FOREIGN KEY(submission_id) REFERENCES submissions(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS submission_comments(
        id TEXT PRIMARY KEY,
        submission_id TEXT NOT NULL,
        user_name TEXT NOT NULL,
        text TEXT NOT NULL,
        created_ts REAL NOT NULL,
        FOREIGN KEY(submission_id) REFERENCES submissions(id) ON DELETE CASCADE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS forum_posts(
        id TEXT PRIMARY KEY,
        sender_phone TEXT NOT NULL,
        sender_name TEXT NOT NULL,
        sender_role TEXT NOT NULL,
        text TEXT NOT NULL,
        status TEXT NOT NULL,
        created_ts REAL NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS forum_replies(
        id TEXT PRIMARY KEY,
        post_id TEXT NOT NULL,
        referee_phone TEXT NOT NULL,
        referee_name TEXT NOT NULL,
        text TEXT NOT NULL,
        created_ts REAL NOT NULL,
        FOREIGN KEY(post_id) REFERENCES forum_posts(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

# ---------------- DB CRUD ----------------
def db_user_get(phone: str):
    conn = db_conn()
    row = conn.execute("SELECT phone,name,nid,password FROM users WHERE phone=?", (phone,)).fetchone()
    conn.close()
    return row

def db_user_upsert(phone: str, name: str, nid: str, password: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO users(phone,name,nid,password,created_ts)
    VALUES(?,?,?,?,?)
    ON CONFLICT(phone) DO UPDATE SET name=excluded.name, nid=excluded.nid, password=excluded.password
    """, (phone, name, nid, password, time.time()))
    conn.commit()
    conn.close()

def db_referee_upsert(phone: str, first: str, last: str, nid: str, field_: str, password: str, active: bool):
    conn = db_conn()
    conn.execute("""
    INSERT INTO referees(phone,first_name,last_name,nid,field,password,is_active,created_ts)
    VALUES(?,?,?,?,?,?,?,?)
    ON CONFLICT(phone) DO UPDATE SET first_name=excluded.first_name, last_name=excluded.last_name,
    nid=excluded.nid, field=excluded.field, password=excluded.password, is_active=excluded.is_active
    """, (phone, first, last, nid, field_, password, 1 if active else 0, time.time()))
    conn.commit()
    conn.close()

def db_referee_find(phone: str, nid: str, password: str):
    conn = db_conn()
    row = conn.execute("""
    SELECT first_name,last_name,phone,nid,field,password,is_active
    FROM referees
    WHERE phone=? AND nid=? AND password=? AND is_active=1
    """, (phone, nid, password)).fetchone()
    conn.close()
    return row

def db_referees_by_field(field_: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT first_name,last_name,phone,nid,field,password,is_active
    FROM referees
    WHERE field=? AND is_active=1
    ORDER BY last_name, first_name
    """, (field_,)).fetchall()
    conn.close()
    return rows

def db_topic_insert(id_: str, title: str, field_: str, description: str, file_name: str, file_bytes: bytes | None):
    conn = db_conn()
    conn.execute("""
    INSERT INTO topics(id,title,field,description,file_name,file_bytes,created_ts)
    VALUES(?,?,?,?,?,?,?)
    """, (id_, title, field_, description, file_name, file_bytes, time.time()))
    conn.commit()
    conn.close()

def db_topics_all():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,field,description,file_name,file_bytes,created_ts
    FROM topics ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_research_insert(id_: str, title: str, field_: str, summary: str, file_name: str, file_bytes: bytes | None):
    conn = db_conn()
    conn.execute("""
    INSERT INTO research(id,title,field,summary,file_name,file_bytes,created_ts)
    VALUES(?,?,?,?,?,?,?)
    """, (id_, title, field_, summary, file_name, file_bytes, time.time()))
    conn.commit()
    conn.close()

def db_research_all():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,field,summary,file_name,file_bytes,created_ts
    FROM research ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_doc_insert(id_: str, title: str, file_name: str, file_bytes: bytes):
    conn = db_conn()
    conn.execute("""
    INSERT INTO documents(id,title,file_name,file_bytes,created_ts)
    VALUES(?,?,?,?,?)
    """, (id_, title, file_name, file_bytes, time.time()))
    conn.commit()
    conn.close()

def db_docs_all():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,file_name,file_bytes,created_ts
    FROM documents ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_submission_insert(
    id_: str, title: str, description: str, sender_phone: str, sender_name: str, sender_nid: str,
    suggested_topic_id: str, field_: str, content_type: str, file_name: str, file_mime: str, file_bytes: bytes | None
):
    conn = db_conn()
    conn.execute("""
    INSERT INTO submissions(
        id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
        file_name,file_mime,file_bytes,status,score,likes,views,knowledge_code,referee_feedback,assigned_referee_phone,
        assigned_referee_name,created_ts
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'pending',0,0,0,'','', '', '', ?)
    """, (id_, title, description, sender_phone, sender_name, sender_nid, suggested_topic_id, field_, content_type,
          file_name, file_mime, file_bytes, time.time()))
    conn.commit()
    conn.close()

def db_submissions_by_sender(phone: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,score,likes,views,knowledge_code,referee_feedback,
           assigned_referee_phone,assigned_referee_name,created_ts
    FROM submissions
    WHERE sender_phone=?
    ORDER BY created_ts DESC
    """, (phone,)).fetchall()
    conn.close()
    return rows

def db_submissions_published():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,score,likes,views,knowledge_code,referee_feedback,
           assigned_referee_phone,assigned_referee_name,created_ts
    FROM submissions
    WHERE status='published'
    ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_submissions_pending():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,score,likes,views,knowledge_code,referee_feedback,
           assigned_referee_phone,assigned_referee_name,created_ts
    FROM submissions
    WHERE status='pending'
    ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_submissions_assigned_to(ref_phone: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,score,likes,views,knowledge_code,referee_feedback,
           assigned_referee_phone,assigned_referee_name,created_ts
    FROM submissions
    WHERE assigned_referee_phone=?
    ORDER BY created_ts DESC
    """, (ref_phone,)).fetchall()
    conn.close()
    return rows

def db_submission_assign(sub_id: str, ref_phone: str, ref_name: str):
    conn = db_conn()
    conn.execute("""
    UPDATE submissions
    SET status='waiting_referee', assigned_referee_phone=?, assigned_referee_name=?
    WHERE id=?
    """, (ref_phone, ref_name, sub_id))
    conn.commit()
    conn.close()

def db_submission_update_review(sub_id: str, status: str, feedback: str, score: int, knowledge_code: str):
    conn = db_conn()
    conn.execute("""
    UPDATE submissions
    SET status=?, referee_feedback=?, score=?, knowledge_code=?
    WHERE id=?
    """, (status, feedback, score, knowledge_code, sub_id))
    conn.commit()
    conn.close()

def db_submission_inc_view(sub_id: str):
    conn = db_conn()
    conn.execute("UPDATE submissions SET views = views + 1 WHERE id=?", (sub_id,))
    conn.commit()
    conn.close()

def db_like_toggle(sub_id: str, user_phone: str) -> Tuple[bool,int]:
    """
    returns (liked_now, new_like_count)
    """
    conn = db_conn()
    cur = conn.cursor()
    existing = cur.execute("SELECT 1 FROM submission_likes WHERE submission_id=? AND user_phone=?", (sub_id, user_phone)).fetchone()
    if existing:
        cur.execute("DELETE FROM submission_likes WHERE submission_id=? AND user_phone=?", (sub_id, user_phone))
    else:
        cur.execute("INSERT INTO submission_likes(submission_id,user_phone,created_ts) VALUES(?,?,?)", (sub_id, user_phone, time.time()))
    # recompute count
    cnt = cur.execute("SELECT COUNT(*) FROM submission_likes WHERE submission_id=?", (sub_id,)).fetchone()[0]
    cur.execute("UPDATE submissions SET likes=? WHERE id=?", (cnt, sub_id))
    conn.commit()
    conn.close()
    return (not bool(existing), cnt)

def db_comment_add(comment_id: str, sub_id: str, user_name: str, text: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO submission_comments(id,submission_id,user_name,text,created_ts)
    VALUES(?,?,?,?,?)
    """, (comment_id, sub_id, user_name, text, time.time()))
    conn.commit()
    conn.close()

def db_comments_for(sub_id: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,user_name,text,created_ts
    FROM submission_comments
    WHERE submission_id=?
    ORDER BY created_ts ASC
    """, (sub_id,)).fetchall()
    conn.close()
    return rows

def db_comment_delete(comment_id: str):
    conn = db_conn()
    conn.execute("DELETE FROM submission_comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()

def db_forum_post_add(id_: str, sender_phone: str, sender_name: str, sender_role: str, text: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO forum_posts(id,sender_phone,sender_name,sender_role,text,status,created_ts)
    VALUES(?,?,?,?,?,'pending',?)
    """, (id_, sender_phone, sender_name, sender_role, text, time.time()))
    conn.commit()
    conn.close()

def db_forum_posts(status: Optional[str] = None):
    conn = db_conn()
    if status:
        rows = conn.execute("""
        SELECT id,sender_phone,sender_name,sender_role,text,status,created_ts
        FROM forum_posts
        WHERE status=?
        ORDER BY created_ts DESC
        """, (status,)).fetchall()
    else:
        rows = conn.execute("""
        SELECT id,sender_phone,sender_name,sender_role,text,status,created_ts
        FROM forum_posts
        ORDER BY created_ts DESC
        """).fetchall()
    conn.close()
    return rows

def db_forum_set_status(post_id: str, status: str):
    conn = db_conn()
    conn.execute("UPDATE forum_posts SET status=? WHERE id=?", (status, post_id))
    conn.commit()
    conn.close()

def db_forum_reply_add(id_: str, post_id: str, ref_phone: str, ref_name: str, text: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO forum_replies(id,post_id,referee_phone,referee_name,text,created_ts)
    VALUES(?,?,?,?,?,?)
    """, (id_, post_id, ref_phone, ref_name, text, time.time()))
    conn.commit()
    conn.close()

def db_forum_replies(post_id: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,referee_phone,referee_name,text,created_ts
    FROM forum_replies
    WHERE post_id=?
    ORDER BY created_ts ASC
    """, (post_id,)).fetchall()
    conn.close()
    return rows


# =========================================================
# Theme + Fonts
# =========================================================
def pick_existing(paths: List[str]) -> str:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return ""

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

        .nexa-shell {{
          max-width: 1240px;
          margin: 14px auto 96px auto;
          padding: 0 12px;
        }}

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

        .stButton > button {{
          border-radius: 12px !important;
          font-weight: 900 !important;
        }}
        .stButton > button[kind="primary"] {{
          background: var(--accent) !important;
          color: #111827 !important;
          border: none !important;
        }}

        header[data-testid="stHeader"] {{
          background: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# App State / Config
# =========================================================
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

def normalize_phone(p: str) -> str:
    return re.sub(r"\s+", "", (p or "").strip())

def normalize_nid(n: str) -> str:
    return re.sub(r"\s+", "", (n or "").strip())

def ensure_state():
    st.session_state.setdefault("_id_counter", 5000)
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("role", "guest")   # user/referee/manager
    st.session_state.setdefault("phone", "")
    st.session_state.setdefault("nid", "")
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("selected_submission_id", None)
    st.session_state.setdefault("_show_signup", False)

    # manager credentials
    st.session_state.setdefault("manager_phone", "09146862029")
    st.session_state.setdefault("manager_nid", "1362362506")
    st.session_state.setdefault("manager_password", "Hadi136236")

    # page persistence via query params
    st.session_state.setdefault("page", "صفحه اصلی")

def is_admin() -> bool:
    return st.session_state.role == "manager"

def make_id(prefix: str) -> str:
    st.session_state._id_counter += 1
    return f"{prefix}{st.session_state._id_counter}"

def logout():
    st.session_state.logged_in = False
    st.session_state.role = "guest"
    st.session_state.phone = ""
    st.session_state.nid = ""
    st.session_state.name = ""
    st.session_state.selected_submission_id = None
    # page stays, but user logged out
    st.rerun()

def set_page(p: str):
    st.session_state.page = p
    # keep same page after refresh (while session remains)
    try:
        st.query_params["page"] = p
    except Exception:
        pass

def load_page_from_query():
    try:
        qp = st.query_params
        if "page" in qp and qp["page"]:
            p = qp["page"]
            if isinstance(p, list):
                p = p[0]
            if p in ["صفحه اصلی", "تالار گفتگو", "پروفایل", "اسناد"]:
                st.session_state.page = p
    except Exception:
        pass


# =========================================================
# Streamlit config
# =========================================================
st.set_page_config(page_title="NEXA", layout="wide")
db_init()
ensure_state()
load_page_from_query()
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
            set_page("صفحه اصلی")
            st.rerun()
        if st.button("🚪 خروج از سامانه", type="primary"):
            logout()
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
                if not p or not password:
                    st.error("شماره همراه و رمز عبور را وارد کنید.")
                    st.stop()
                row = db_user_get(p)
                if not row or row[3] != password:
                    st.error("کاربر یافت نشد یا رمز اشتباه است. لطفاً ثبت‌نام کنید.")
                    st.stop()
                st.session_state.name = row[1]
                st.session_state.nid = row[2]

            elif role == "manager":
                if not p or not n or not password:
                    st.error("شماره همراه، کد ملی و رمز عبور را وارد کنید.")
                    st.stop()
                if p != normalize_phone(st.session_state.manager_phone) or n != normalize_nid(st.session_state.manager_nid) or password != st.session_state.manager_password:
                    st.error("مشخصات مدیر سامانه اشتباه است.")
                    st.stop()
                st.session_state.name = "مدیر سامانه"
                st.session_state.nid = st.session_state.manager_nid

            else:  # referee
                if not p or not n or not password:
                    st.error("شماره همراه، کد ملی و رمز عبور را وارد کنید.")
                    st.stop()
                ref = db_referee_find(p, n, password)
                if not ref:
                    st.error("داور یافت نشد یا مشخصات اشتباه است.")
                    st.stop()
                st.session_state.name = f"{ref[0]} {ref[1]}"
                st.session_state.nid = ref[3]

            st.session_state.logged_in = True
            st.session_state.role = role
            st.session_state.phone = p
            st.success("ورود انجام شد ✅")
            st.rerun()

    with c2:
        st.caption("ثبت‌نام فقط برای کاربران")
        if st.button("ثبت نام"):
            st.session_state._show_signup = True

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
                db_user_upsert(p, su_name.strip(), n, su_pass1)
                st.success("ثبت‌نام انجام شد ✅ حالا می‌تونی وارد بشی")
                st.session_state._show_signup = False
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =========================================================
# Bottom Navigation (like app) + page persistence
# =========================================================
nav_labels = ["صفحه اصلی", "تالار گفتگو", "پروفایل", "اسناد"]
nav_icons = {"صفحه اصلی": "🏠", "تالار گفتگو": "💬", "پروفایل": "👤", "اسناد": "📄"}
nav_display = [f"{nav_icons[x]} {x}" for x in nav_labels]
current = f"{nav_icons[st.session_state.page]} {st.session_state.page}"

st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
choice = st.radio("", nav_display, index=nav_display.index(current), horizontal=True, label_visibility="collapsed")
st.markdown("</div>", unsafe_allow_html=True)

chosen_page = choice.split(" ", 1)[1]
if chosen_page != st.session_state.page:
    set_page(chosen_page)
    st.rerun()


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

        # ویترین دانش (فقط منتشر شده ها) - نمونه حذف
        with tabs[0]:
            st.header("ویترین دانش")
            published = db_submissions_published()
            if not published:
                st.info("فعلاً محتوایی منتشر نشده.")
            else:
                for row in published:
                    (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
                     fname,fmime,fbytes,status,score,likes,views,kcode,fb,ar_phone,ar_name,created_ts) = row

                    with st.container(border=True):
                        db_submission_inc_view(sid)
                        views += 1

                        # اگر فایل ارسالی تصویر باشد، همان را نمایش بده
                        if fbytes and fmime and fmime.startswith("image/"):
                            st.image(fbytes, use_container_width=True)
                        else:
                            # اگر نبود، لوگو نمایش بده
                            fallback = pick_existing(["official_logo.png", "logo.png"])
                            if fallback:
                                st.image(fallback, use_container_width=True)

                        st.subheader(title)
                        st.caption(f"{field_} | نوع محتوا: {ctype} | کد دانشی: {kcode or '-'} | بازدید: {views}")
                        st.write(desc)

                        # Like
                        if st.button(f"❤️ لایک ({likes})", key=f"like_{sid}"):
                            _, new_cnt = db_like_toggle(sid, st.session_state.phone)
                            st.success(f"ثبت شد ✅ (لایک‌ها: {new_cnt})")
                            st.rerun()

                        st.subheader("نظرات")
                        comments = db_comments_for(sid)
                        if comments:
                            for (cid, uname, ctext, cts) in comments:
                                st.write(f"- **{uname}**: {ctext}")
                                st.caption(time.strftime("%Y-%m-%d %H:%M", time.localtime(cts)))
                        else:
                            st.caption("نظری ثبت نشده.")

                        new_comment = st.text_input("افزودن نظر", key=f"cmt_{sid}", placeholder="نظرت رو بنویس...")
                        if st.button("ثبت نظر", key=f"cmt_btn_{sid}", type="primary"):
                            if new_comment.strip():
                                db_comment_add(make_id("c"), sid, st.session_state.name, new_comment.strip())
                                st.success("نظر ثبت شد ✅")
                                st.rerun()

        # ارسال محتوا (تصویر ویترین حذف شد)
        with tabs[1]:
            st.header("ارسال محتوا")

            topics = db_topics_all()
            topic_options = ["(بدون انتخاب موضوع)"] + [f"{t[1]} | {t[2]}" for t in topics]
            topic_pick = st.selectbox("انتخاب از پیشنهادات مدیر (اختیاری)", topic_options)

            picked_topic_id = ""
            default_title = ""
            default_desc = ""
            default_field = FIELDS[0]

            if topic_pick != "(بدون انتخاب موضوع)":
                for t in topics:
                    if f"{t[1]} | {t[2]}" == topic_pick:
                        picked_topic_id = t[0]
                        default_title = t[1]
                        default_desc = t[3]
                        default_field = t[2]
                        break

            title = st.text_input("عنوان", value=default_title)
            desc = st.text_area("توضیحات", value=default_desc, height=120)
            field_sel = st.selectbox("کمیته / حوزه تخصصی", FIELDS, index=FIELDS.index(default_field) if default_field in FIELDS else 0)
            content_type = st.selectbox("نوع محتوا", CONTENT_TYPES)

            uploaded = st.file_uploader("پیوست فایل", type=None)

            if st.button("ثبت و ارسال به مدیر سامانه", type="primary"):
                if not title.strip():
                    st.error("عنوان الزامی است.")
                else:
                    fname = uploaded.name if uploaded else "N/A"
                    fbytes = uploaded.getvalue() if uploaded else None
                    fmime = uploaded.type if uploaded else ""

                    db_submission_insert(
                        id_=make_id("s"),
                        title=title.strip(),
                        description=desc.strip(),
                        sender_phone=st.session_state.phone,
                        sender_name=st.session_state.name,
                        sender_nid=st.session_state.nid,
                        suggested_topic_id=picked_topic_id,
                        field_=field_sel,
                        content_type=content_type,
                        file_name=fname,
                        file_mime=fmime,
                        file_bytes=fbytes
                    )
                    st.success("ارسال شد ✅")
                    st.rerun()

        # وضعیت پیگیری (حذف متن‌های اضافی و نمونه)
        with tabs[2]:
            st.header("وضعیت پیگیری")
            my = db_submissions_by_sender(st.session_state.phone)
            if not my:
                st.info("هنوز محتوایی ارسال نکردی.")
            else:
                for row in my:
                    (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
                     fname,fmime,fbytes,status,score,likes,views,kcode,fb,ar_phone,ar_name,created_ts) = row

                    with st.container(border=True):
                        st.write(f"**{title}**")
                        st.caption(f"وضعیت: {status_fa(status)}")
                        # فقط موارد واقعی و مفید
                        st.write(f"حوزه: **{field_}**")
                        st.write(f"نوع محتوا: **{ctype}**")
                        if ar_name:
                            st.write(f"داور: **{ar_name}**")
                        if fb:
                            st.write(f"📝 نظر/اصلاحات داور: {fb}")
                        if score:
                            st.write(f"⭐ امتیاز: {score}")
                        if status == "published":
                            st.write(f"✅ منتشر شد در ویترین دانش | کد دانشی: **{kcode}**")

        # پیشنهاد موضوعات (حتماً برای کاربر قابل مشاهده)
        with tabs[3]:
            st.header("پیشنهاد موضوعات")
            topics = db_topics_all()
            if not topics:
                st.info("موضوعی ثبت نشده.")
            else:
                for t in topics:
                    (tid, ttitle, tfield, tdesc, tfname, tfbytes, tts) = t
                    with st.container(border=True):
                        st.write(f"**{ttitle}**")
                        st.caption(f"حوزه: {tfield} | تاریخ: {time.strftime('%Y-%m-%d %H:%M', time.localtime(tts))}")
                        st.write(tdesc)
                        if tfbytes:
                            st.download_button("دانلود پیوست", data=tfbytes, file_name=tfname or "file", key=f"dl_topic_{tid}")

        # تحقیقات
        with tabs[4]:
            st.header("تحقیقات صورت گرفته")
            res = db_research_all()
            if not res:
                st.info("تحقیقی ثبت نشده.")
            else:
                for r in res:
                    (rid, rtitle, rfield, rsum, rfname, rfbytes, rts) = r
                    with st.container(border=True):
                        st.write(f"**{rtitle}**")
                        st.caption(f"حوزه: {rfield} | تاریخ: {time.strftime('%Y-%m-%d %H:%M', time.localtime(rts))}")
                        st.write(rsum)
                        if rfbytes:
                            st.download_button("دانلود فایل", data=rfbytes, file_name=rfname or "file", key=f"dl_res_{rid}")

    # -----------------------------
    # MANAGER HOME
    # -----------------------------
    elif role == "manager":
        st.header("پنل مدیر سامانه")
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
            pending = db_submissions_pending()
            if not pending:
                st.info("موردی برای ارجاع نیست.")
            else:
                for row in pending:
                    (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
                     fname,fmime,fbytes,status,score,likes,views,kcode,fb,ar_phone,ar_name,created_ts) = row

                    with st.container(border=True):
                        st.write(f"**{title}**")
                        st.caption(f"فرستنده: {s_name} ({s_phone}) | حوزه: {field_} | نوع: {ctype}")
                        st.write(desc)
                        if fbytes:
                            st.download_button("دانلود فایل پیوست", data=fbytes, file_name=fname or "file", key=f"dl_sub_{sid}")

                        refs = db_referees_by_field(field_)
                        if not refs:
                            st.warning("برای این حوزه داور فعالی ثبت نشده.")
                        else:
                            # نمایش: "هادی باقریان (هوش مصنوعی)"
                            options = []
                            for r in refs:
                                first, last, rphone, rnid, rfield, rpass, ractive = r
                                options.append((f"{first} {last} ({rfield})", rphone, f"{first} {last}"))
                            label = st.selectbox(
                                "انتخاب داور",
                                options,
                                format_func=lambda x: x[0],
                                key=f"sel_ref_{sid}"
                            )
                            if st.button("بررسی و ارجاع", key=f"assign_{sid}", type="primary"):
                                db_submission_assign(sid, normalize_phone(label[1]), label[2])
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
                    st.error("همه فیلدها الزامی است.")
                else:
                    db_referee_upsert(p, first.strip(), last.strip(), n, field_sel, ref_pass, active)
                    st.success("داور ثبت شد ✅ (می‌تواند وارد شود)")
                    st.rerun()

        # مدیریت ویترین (حذف کامنت) - ادامه بخش مدیریت
        with tabs[2]:
            st.subheader("مدیریت ویترین دانش (نظارت بر نظرات)")
            published = db_submissions_published()
            if not published:
                st.info("محتوای منتشر شده‌ای وجود ندارد.")
            else:
                for row in published:
                    sid, title = row[0], row[1]
                    comments = db_comments_for(sid)
                    if comments:
                        with st.expander(f"نظرات محتوای: {title}"):
                            for (cid, uname, ctext, cts) in comments:
                                ccol1, ccol2 = st.columns([5, 1])
                                ccol1.write(f"**{uname}**: {ctext}")
                                if ccol2.button("🗑 حذف", key=f"del_c_{cid}"):
                                    db_comment_delete(cid)
                                    st.rerun()
                    else:
                        st.caption(f"بدون نظر: {title}")

        # پیشنهاد موضوعات (توسط مدیر - کاربر مشاهده می‌کند)
        with tabs[3]:
            st.subheader("ثبت موضوعات پیشنهادی برای نخبگان")
            t_title = st.text_input("عنوان موضوع", key="m_t_t")
            t_field = st.selectbox("حوزه موضوع", FIELDS, key="m_t_f")
            t_desc = st.text_area("توضیحات و ضرورت", key="m_t_d")
            t_file = st.file_uploader("پیوست راهنما (اختیاری)", key="m_t_file")
            
            if st.button("ثبت و انتشار موضوع", type="primary"):
                if not t_title.strip(): st.error("عنوان الزامی است")
                else:
                    db_topic_insert(make_id("top"), t_title, t_field, t_desc, 
                                   t_file.name if t_file else "", t_file.getvalue() if t_file else None)
                    st.success("موضوع با موفقیت ثبت شد.")
                    st.rerun()

        # تحقیقات صورت گرفته
        with tabs[4]:
            st.subheader("ثبت سوابق تحقیقاتی")
            r_title = st.text_input("عنوان تحقیق", key="m_r_t")
            r_field = st.selectbox("حوزه تحقیق", FIELDS, key="m_r_f")
            r_sum = st.text_area("خلاصه نتایج", key="m_r_s")
            r_up = st.file_uploader("فایل تحقیق", key="m_r_up")
            if st.button("ذخیره تحقیق"):
                db_research_insert(make_id("res"), r_title, r_field, r_sum, 
                                  r_up.name if r_up else "", r_up.getvalue() if r_up else None)
                st.success("تحقیق ثبت شد.")

        # اسناد
        with tabs[5]:
            st.subheader("بارگذاری اسناد و نشریات")
            doc_t = st.text_input("عنوان سند/آیین‌نامه")
            doc_f = st.file_uploader("انتخاب فایل PDF/Doc")
            if st.button("ثبت در کتابخانه اسناد"):
                if doc_t and doc_f:
                    db_doc_insert(make_id("doc"), doc_t, doc_f.name, doc_f.getvalue())
                    st.success("سند بارگذاری شد.")
                else: st.error("عنوان و فایل الزامی است.")

        # تایید پیام‌های تالار
        with tabs[6]:
            st.subheader("تایید پیام‌های جدید تالار گفتگو")
            pend_posts = db_forum_posts("pending")
            if not pend_posts:
                st.info("پیام جدیدی برای تایید وجود ندارد.")
            else:
                for p in pend_posts:
                    with st.container(border=True):
                        st.write(f"**فرستنده:** {p[2]} ({p[3]})")
                        st.write(p[4])
                        ac1, ac2 = st.columns(2)
                        if ac1.button("✅ تایید انتشار", key=f"fok_{p[0]}"):
                            db_forum_set_status(p[0], "approved")
                            st.rerun()
                        if ac2.button("❌ رد پیام", key=f"frej_{p[0]}"):
                            db_forum_set_status(p[0], "rejected")
                            st.rerun()

    # -----------------------------
    # REFEREE HOME (پنل داوری)
    # -----------------------------
    else:
        st.header("پنل داوری تخصصی")
        tasks = db_submissions_assigned_to(st.session_state.phone)
        
        if not tasks:
            st.info("فعلاً موردی برای بررسی به شما ارجاع نشده است.")
        else:
            col_list, col_det = st.columns([1, 2])
            
            with col_list:
                st.subheader("لیست ارجاعات")
                for tk in tasks:
                    if st.button(f"📄 {tk[1]}\n(فرستنده: {tk[4]})", key=f"tk_{tk[0]}", use_container_width=True):
                        st.session_state.selected_submission_id = tk[0]
            
            with col_det:
                if st.session_state.selected_submission_id:
                    # پیدا کردن جزییات از لیست (tk در حلقه بالا نیست، پس باید دوباره پیدا کرد یا از لیست کشید)
                    target = [t for t in tasks if t[0] == st.session_state.selected_submission_id][0]
                    (sid, title, desc, s_ph, s_nm, s_ni, tid, field, ctype, fname, fmime, fbytes, 
                     status, score, likes, views, kcode, fb, ar_ph, ar_nm, cts) = target
                    
                    st.subheader(f"بررسی: {title}")
                    st.write(f"**توضیحات:** {desc}")
                    if fbytes:
                        st.download_button("📩 دانلود فایل محتوا", fbytes, fname, key=f"dl_{sid}")
                    
                    st.divider()
                    new_status = st.selectbox("وضعیت بررسی", 
                                             ["waiting_referee", "correction_needed", "published", "rejected"],
                                             index=["waiting_referee", "correction_needed", "published", "rejected"].index(status),
                                             format_func=status_fa)
                    
                    new_fb = st.text_area("نظرات اصلاحی / داوری", value=fb or "")
                    new_score = st.number_input("امتیاز نخبگی (0-100)", 0, 100, int(score or 0))
                    new_kcode = st.text_input("کد دانشی (الزامی برای انتشار در ویترین)", value=kcode or "")
                    
                    if st.button("ثبت نهایی نتیجه داوری", type="primary"):
                        if new_status == "published" and not new_kcode.strip():
                            st.error("برای انتشار در ویترین دانش، وارد کردن 'کد دانشی' الزامی است.")
                        else:
                            db_submission_update_review(sid, new_status, new_fb, new_score, new_kcode)
                            st.success("داوری ثبت شد.")
                            st.rerun()
                else:
                    st.info("یک مورد را از لیست سمت راست انتخاب کنید.")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Forum (تالار گفتگو)
# =========================================================
elif st.session_state.page == "تالار گفتگو":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("تالار گفتگو و پرسش پاسخ")
    
    st.caption("پیام شما پس از تایید مدیر برای همه نمایش داده خواهد شد.")
    f_msg = st.text_area("پیام یا سوال خود را بنویسید...")
    if st.button("ارسال برای تایید", type="primary"):
        if f_msg.strip():
            db_forum_post_add(make_id("fp"), st.session_state.phone, st.session_state.name, st.session_state.role, f_msg)
            st.success("ارسال شد. منتظر تایید مدیر باشید.")
        else: st.error("متن پیام خالی است")

    st.divider()
    
    # نمایش پیام های تایید شده
    approved_posts = db_forum_posts("approved")
    for ap in approved_posts:
        with st.container(border=True):
            st.write(f"👤 **{ap[2]}** ({ap[3]})")
            st.write(ap[4])
            st.caption(f"زمان: {time.strftime('%Y-%m-%d %H:%M', time.localtime(ap[6]))}")
            
            # پاسخ‌های داوران
            replies = db_forum_replies(ap[0])
            for rep in replies:
                st.markdown(f"""
                <div style="background:#f0f7ff; padding:10px; border-right:4px solid #007bff; margin:5px 0; border-radius:5px;">
                <b>👨‍🏫 پاسخ {rep[2]}:</b><br>{rep[3]}
                </div>
                """, unsafe_allow_html=True)
            
            # اجازه پاسخ به داوران
            if st.session_state.role == "referee":
                r_text = st.text_input("پاسخ داور به این سوال", key=f"rinput_{ap[0]}")
                if st.button("ثبت پاسخ داور", key=f"rbtn_{ap[0]}"):
                    db_forum_reply_add(make_id("fr"), ap[0], st.session_state.phone, st.session_state.name, r_text)
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Documents (اسناد)
# =========================================================
elif st.session_state.page == "اسناد":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("کتابخانه اسناد و نشریات")
    docs = db_docs_all()
    if not docs:
        st.info("سندی بارگذاری نشده است.")
    else:
        for d in docs:
            (did, dtitle, dfname, dfbytes, dts) = d
            with st.container(border=True):
                col_d1, col_d2 = st.columns([4, 1])
                col_d1.write(f"📄 **{dtitle}**")
                col_d1.caption(f"فایل: {dfname}")
                col_d2.download_button("دریافت", dfbytes, dfname, key=f"dldoc_{did}")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Profile (پروفایل)
# =========================================================
elif st.session_state.page == "پروفایل":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("مشخصات کاربری")
    st.write(f"🆔 **نام:** {st.session_state.name}")
    st.write(f"📞 **شماره تماس:** {st.session_state.phone}")
    st.write(f"🪪 **کد ملی:** {st.session_state.nid}")
    st.write(f"🎭 **نقش در سامانه:** {st.session_state.role}")
    st.divider()
    if st.button("🚪 خروج از حساب کاربری", type="primary"):
        logout()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True) # پایان پوسته
