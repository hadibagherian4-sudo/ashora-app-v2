import os
import re
import time
import base64
import sqlite3
import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Tuple, List

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
        likes INTEGER NOT NULL DEFAULT 0,
        views INTEGER NOT NULL DEFAULT 0,
        knowledge_code TEXT,
        created_ts REAL NOT NULL,
        FOREIGN KEY(sender_phone) REFERENCES users(phone) ON DELETE NO ACTION
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS submission_assignments(
        id TEXT PRIMARY KEY,
        submission_id TEXT NOT NULL,
        referee_phone TEXT NOT NULL,
        referee_name TEXT NOT NULL,
        referee_field TEXT NOT NULL,
        decision TEXT NOT NULL,
        feedback TEXT NOT NULL,
        score INTEGER NOT NULL DEFAULT 0,
        suggested_knowledge_code TEXT,
        reviewed_ts REAL,
        created_ts REAL NOT NULL,
        FOREIGN KEY(submission_id) REFERENCES submissions(id) ON DELETE CASCADE
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

# =========================================================
# Utils
# =========================================================
def normalize_phone(p: str) -> str:
    return re.sub(r"\s+", "", (p or "").strip())

def normalize_nid(n: str) -> str:
    return re.sub(r"\s+", "", (n or "").strip())

def ts_str(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))

def status_fa(s: str) -> str:
    return {
        "pending": "در انتظار بررسی مدیر سامانه",
        "waiting_referee": "ارجاع شده به داور/داوران",
        "waiting_manager": "در انتظار تایید نهایی مدیر",
        "correction_needed": "نیاز به اصلاح",
        "published": "منتشر شده در ویترین دانش",
        "rejected": "عدم تایید",
        "approved": "تایید شده",
        "user": "کاربر",
        "referee": "داور تخصصی / نخبگان دانشی",
        "manager": "مدیر سامانه",
        "guest": "مهمان",
    }.get(s, s)

def make_id(prefix: str) -> str:
    st.session_state._id_counter += 1
    return f"{prefix}{st.session_state._id_counter}"

def pick_existing(paths: List[str]) -> str:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return ""

def is_admin() -> bool:
    return st.session_state.role == "manager"

# =========================================================
# DB CRUD
# =========================================================
def db_user_get(phone: str):
    conn = db_conn()
    row = conn.execute("SELECT phone,name,nid,password FROM users WHERE phone=?", (phone,)).fetchone()
    conn.close()
    return row

def db_users_all():
    conn = db_conn()
    rows = conn.execute("SELECT phone,name,nid,password,created_ts FROM users ORDER BY created_ts DESC").fetchall()
    conn.close()
    return rows

def db_user_upsert(phone: str, name: str, nid: str, password: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO users(phone,name,nid,password,created_ts)
    VALUES(?,?,?,?,?)
    ON CONFLICT(phone) DO UPDATE SET name=excluded.name, nid=excluded.nid, password=excluded.password
    """, (phone, name, nid, password, time.time()))
    conn.commit()
    conn.close()

def db_user_update(phone: str, name: str, nid: str, password: str):
    conn = db_conn()
    conn.execute("UPDATE users SET name=?, nid=?, password=? WHERE phone=?", (name, nid, password, phone))
    conn.commit()
    conn.close()

def db_user_delete(phone: str):
    conn = db_conn()
    conn.execute("DELETE FROM users WHERE phone=?", (phone,))
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

def db_referees_all():
    conn = db_conn()
    rows = conn.execute("""
        SELECT phone,first_name,last_name,nid,field,password,is_active,created_ts
        FROM referees ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_referee_set_active(phone: str, active: bool):
    conn = db_conn()
    conn.execute("UPDATE referees SET is_active=? WHERE phone=?", (1 if active else 0, phone))
    conn.commit()
    conn.close()

def db_referee_delete(phone: str):
    conn = db_conn()
    conn.execute("DELETE FROM referees WHERE phone=?", (phone,))
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
    SELECT first_name,last_name,phone,nid,field
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
        file_name,file_mime,file_bytes,status,likes,views,knowledge_code,created_ts
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?, 'pending',0,0,'', ?)
    """, (id_, title, description, sender_phone, sender_name, sender_nid, suggested_topic_id,
          field_, content_type, file_name, file_mime, file_bytes, time.time()))
    conn.commit()
    conn.close()

def db_submission_update_content(sub_id: str, title: str, description: str, field_: str, content_type: str,
                                file_name: str, file_mime: str, file_bytes: bytes | None):
    conn = db_conn()
    conn.execute("""
    UPDATE submissions
    SET title=?, description=?, field=?, content_type=?, file_name=?, file_mime=?, file_bytes=?, status='pending', knowledge_code=''
    WHERE id=?
    """, (title, description, field_, content_type, file_name, file_mime, file_bytes, sub_id))
    conn.commit()
    conn.close()

def db_submissions_by_sender(phone: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,likes,views,knowledge_code,created_ts
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
           file_name,file_mime,file_bytes,status,likes,views,knowledge_code,created_ts
    FROM submissions
    WHERE status='published'
    ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_submissions_pending_or_waiting_manager():
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,title,description,sender_phone,sender_name,sender_nid,suggested_topic_id,field,content_type,
           file_name,file_mime,file_bytes,status,likes,views,knowledge_code,created_ts
    FROM submissions
    WHERE status IN ('pending','waiting_manager','waiting_referee','correction_needed')
    ORDER BY created_ts DESC
    """).fetchall()
    conn.close()
    return rows

def db_submission_set_status(sub_id: str, status: str):
    conn = db_conn()
    conn.execute("UPDATE submissions SET status=? WHERE id=?", (status, sub_id))
    conn.commit()
    conn.close()

def db_submission_publish(sub_id: str, knowledge_code: str):
    conn = db_conn()
    conn.execute("UPDATE submissions SET status='published', knowledge_code=? WHERE id=?", (knowledge_code, sub_id))
    conn.commit()
    conn.close()

def db_submission_delete(sub_id: str):
    conn = db_conn()
    conn.execute("DELETE FROM submissions WHERE id=?", (sub_id,))
    conn.commit()
    conn.close()

def db_submission_inc_view(sub_id: str):
    conn = db_conn()
    conn.execute("UPDATE submissions SET views = views + 1 WHERE id=?", (sub_id,))
    conn.commit()
    conn.close()

def db_like_toggle(sub_id: str, user_phone: str) -> Tuple[bool, int]:
    conn = db_conn()
    cur = conn.cursor()
    existing = cur.execute("SELECT 1 FROM submission_likes WHERE submission_id=? AND user_phone=?", (sub_id, user_phone)).fetchone()
    if existing:
        cur.execute("DELETE FROM submission_likes WHERE submission_id=? AND user_phone=?", (sub_id, user_phone))
    else:
        cur.execute("INSERT INTO submission_likes(submission_id,user_phone,created_ts) VALUES(?,?,?)", (sub_id, user_phone, time.time()))
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

# ---- Assignments / Reviews ----
def db_assignment_create(assign_id: str, sub_id: str, ref_phone: str, ref_name: str, ref_field: str):
    conn = db_conn()
    conn.execute("""
    INSERT INTO submission_assignments(id,submission_id,referee_phone,referee_name,referee_field,decision,feedback,score,suggested_knowledge_code,reviewed_ts,created_ts)
    VALUES(?,?,?,?,?,'waiting_referee','',0,'',NULL,?)
    """, (assign_id, sub_id, ref_phone, ref_name, ref_field, time.time()))
    conn.commit()
    conn.close()

def db_assignments_for_submission(sub_id: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT id,submission_id,referee_phone,referee_name,referee_field,decision,feedback,score,suggested_knowledge_code,reviewed_ts,created_ts
    FROM submission_assignments
    WHERE submission_id=?
    ORDER BY created_ts ASC
    """, (sub_id,)).fetchall()
    conn.close()
    return rows

def db_assignments_for_referee(ref_phone: str):
    conn = db_conn()
    rows = conn.execute("""
    SELECT a.id, a.submission_id, a.referee_phone, a.referee_name, a.referee_field, a.decision, a.feedback, a.score, a.suggested_knowledge_code, a.reviewed_ts, a.created_ts,
           s.title, s.description, s.sender_name, s.sender_phone, s.field, s.content_type, s.file_name, s.file_mime, s.file_bytes, s.status, s.knowledge_code
    FROM submission_assignments a
    JOIN submissions s ON s.id = a.submission_id
    WHERE a.referee_phone=?
    ORDER BY a.created_ts DESC
    """, (ref_phone,)).fetchall()
    conn.close()
    return rows

def db_assignment_update(assign_id: str, decision: str, feedback: str, score: int, sugg_code: str):
    conn = db_conn()
    conn.execute("""
    UPDATE submission_assignments
    SET decision=?, feedback=?, score=?, suggested_knowledge_code=?, reviewed_ts=?
    WHERE id=?
    """, (decision, feedback, score, sugg_code, time.time(), assign_id))
    conn.commit()
    conn.close()

# ---- Forum ----
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
# Theme + Fonts (BTir.ttf / BNazanin.ttf)
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
        }}

        .stApp {{ background: var(--paper2) !important; }}

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

        header[data-testid="stHeader"] {{ background: transparent; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# App State / Navigation
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

def ensure_state():
    st.session_state.setdefault("_id_counter", 5000)
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("role", "guest")   # user/referee/manager
    st.session_state.setdefault("phone", "")
    st.session_state.setdefault("nid", "")
    st.session_state.setdefault("name", "")
    st.session_state.setdefault("selected_submission_id", None)
    st.session_state.setdefault("_show_signup", False)

    # view state for published content (detail page)
    st.session_state.setdefault("view_mode", "list")  # list | detail
    st.session_state.setdefault("selected_publication_id", None)

    # manager credentials
    st.session_state.setdefault("manager_phone", "09146862029")
    st.session_state.setdefault("manager_nid", "1362362506")
    st.session_state.setdefault("manager_password", "Hadi136236")

    # page persistence
    st.session_state.setdefault("page", "صفحه اصلی")

def logout():
    st.session_state.logged_in = False
    st.session_state.role = "guest"
    st.session_state.phone = ""
    st.session_state.nid = ""
    st.session_state.name = ""
    st.session_state.selected_submission_id = None
    st.session_state.view_mode = "list"
    st.session_state.selected_publication_id = None
    st.rerun()

def set_page(p: str):
    st.session_state.page = p
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
# File rendering (preview)
# =========================================================
def render_file_preview(file_bytes: bytes | None, file_mime: str | None, file_name: str | None):
    if not file_bytes:
        st.caption("پیوست ندارد.")
        return

    m = (file_mime or "").lower()

    if m.startswith("image/"):
        st.image(file_bytes, use_container_width=True)
        return

    if m.startswith("video/"):
        st.video(file_bytes)
        return

    if m.startswith("audio/"):
        st.audio(file_bytes)
        return

    if m == "application/pdf":
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        pdf_html = f"""
        <iframe
            src="data:application/pdf;base64,{b64}"
            width="100%"
            height="720"
            style="border:1px solid rgba(0,0,0,0.12); border-radius:12px;"
        ></iframe>
        """
        components.html(pdf_html, height=740)
        st.download_button("دانلود PDF", data=file_bytes, file_name=file_name or "file.pdf")
        return

    st.download_button("دانلود فایل", data=file_bytes, file_name=file_name or "file")

def show_submission_detail(sid: str):
    published = db_submissions_published()
    row = next((r for r in published if r[0] == sid), None)
    if not row:
        st.error("این محتوا پیدا نشد یا دیگر منتشر نیست.")
        return

    (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
     fname,fmime,fbytes,status,likes,views,kcode,created_ts) = row

    st.subheader(title)
    st.caption(f"{field_} | نوع محتوا: {ctype} | کد دانشی: {kcode or '-'} | بازدید: {views}")
    st.write(f"ارسال‌کننده: **{s_name}** | تاریخ: {ts_str(created_ts)}")

    st.divider()
    render_file_preview(fbytes, fmime, fname)

    st.divider()
    st.write(desc)

    st.divider()
    if st.button("⬅️ برگشت به ویترین"):
        st.session_state.view_mode = "list"
        st.session_state.selected_publication_id = None
        st.rerun()

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

            else:
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
# Bottom Navigation
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

    # ===================== USER =====================
    if role == "user":
        tabs = st.tabs(["ویترین دانش", "ارسال محتوا", "وضعیت پیگیری", "پیشنهاد موضوعات", "تحقیقات صورت گرفته"])

        # ویترین دانش
        with tabs[0]:
            st.header("ویترین دانش")

            # اگر در حالت جزئیات هستیم
            if st.session_state.view_mode == "detail" and st.session_state.selected_publication_id:
                show_submission_detail(st.session_state.selected_publication_id)
            else:
                published = db_submissions_published()
                if not published:
                    st.info("فعلاً محتوایی منتشر نشده.")
                else:
                    for row in published:
                        (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
                         fname,fmime,fbytes,status,likes,views,kcode,created_ts) = row

                        with st.container(border=True):
                            # پیش‌نمایش سبک فقط برای عکس (بدون لوگوی جایگزین)
                            if fbytes and (fmime or "").startswith("image/"):
                                st.image(fbytes, use_container_width=True)

                            st.subheader(title)
                            st.caption(f"{field_} | نوع محتوا: {ctype} | کد دانشی: {kcode or '-'} | بازدید: {views}")
                            st.write(desc[:240] + ("..." if len(desc) > 240 else ""))

                            c1, c2 = st.columns([1.2, 3.0])
                            with c1:
                                if st.button("👁️ مشاهده", key=f"open_{sid}", type="primary"):
                                    db_submission_inc_view(sid)  # بازدید واقعی اینجا ثبت میشه
                                    st.session_state.selected_publication_id = sid
                                    st.session_state.view_mode = "detail"
                                    st.rerun()
                            with c2:
                                if st.button(f"❤️ لایک ({likes})", key=f"like_{sid}"):
                                    _, new_cnt = db_like_toggle(sid, st.session_state.phone)
                                    st.success(f"ثبت شد ✅ (لایک‌ها: {new_cnt})")
                                    st.rerun()

        # ارسال محتوا
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
            field_sel = st.selectbox(
    "کمیته / حوزه تخصصی",
    FIELDS,
    index=FIELDS.index(default_field) if default_field in FIELDS else 0
)
content_type = st.selectbox("نوع محتوا", CONTENT_TYPES)
uploaded = st.file_uploader("پیوست فایل", type=None)

if st.button("ثبت و ارسال", type="primary"):
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

# وضعیت پیگیری + ویرایش
with tabs[2]:
    st.header("وضعیت پیگیری")
    my = db_submissions_by_sender(st.session_state.phone)
    if not my:
        st.info("هنوز محتوایی ارسال نکردی.")
    else:
        for row in my:
            (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
             fname,fmime,fbytes,status,likes,views,kcode,created_ts) = row

            assigns = db_assignments_for_submission(sid)

            with st.container(border=True):
                st.write(f"**{title}**")
                st.caption(f"وضعیت: {status_fa(status)}")
                st.write(f"حوزه: **{field_}**")
                st.write(f"نوع محتوا: **{ctype}**")

                if assigns:
                    st.subheader("نتایج داوران")
                    for a in assigns:
                        (aid, subid, rph, rname, rfield, decision, feedback, score, skc, rts, cts2) = a
                        st.write(f"- **{rname} ({rfield})** | امتیاز: {score} | نتیجه: {decision}")
                        if feedback:
                            st.write(f"  📝 {feedback}")
                        if skc:
                            st.caption(f"کد پیشنهادی: {skc}")

                if status == "published":
                    st.success(f"✅ منتشر شد | کد دانشی: {kcode}")

                if status == "correction_needed":
                    with st.expander("✏️ ویرایش و ارسال مجدد"):
                        new_title = st.text_input("عنوان", value=title, key=f"et_{sid}")
                        new_desc = st.text_area("توضیحات", value=desc, height=120, key=f"ed_{sid}")
                        new_field = st.selectbox(
                            "کمیته / حوزه تخصصی",
                            FIELDS,
                            index=FIELDS.index(field_) if field_ in FIELDS else 0,
                            key=f"ef_{sid}"
                        )
                        new_type = st.selectbox(
                            "نوع محتوا",
                            CONTENT_TYPES,
                            index=CONTENT_TYPES.index(ctype) if ctype in CONTENT_TYPES else 0,
                            key=f"ect_{sid}"
                        )
                        new_up = st.file_uploader("پیوست جدید (اختیاری)", key=f"eu_{sid}")

                        if st.button("ارسال مجدد برای مدیر", key=f"resend_{sid}", type="primary"):
                            nf = new_up.name if new_up else fname
                            nfb = new_up.getvalue() if new_up else fbytes
                            nfm = new_up.type if new_up else (fmime or "")
                            db_submission_update_content(
                                sid,
                                new_title.strip(),
                                new_desc.strip(),
                                new_field,
                                new_type,
                                nf,
                                nfm,
                                nfb
                            )
                            st.success("ارسال مجدد انجام شد ✅")
                            st.rerun()

# پیشنهاد موضوعات
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
                st.caption(f"حوزه: {tfield} | تاریخ: {ts_str(tts)}")
                st.write(tdesc)
                if tfbytes:
                    st.download_button(
                        "دانلود پیوست",
                        data=tfbytes,
                        file_name=tfname or "file",
                        key=f"dl_topic_{tid}"
                    )

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
                st.caption(f"حوزه: {rfield} | تاریخ: {ts_str(rts)}")
                st.write(rsum)
                if rfbytes:
                    st.download_button(
                        "دانلود فایل",
                        data=rfbytes,
                        file_name=rfname or "file",
                        key=f"dl_res_{rid}"
                    )

# ===================== MANAGER =====================
elif role == "manager":
    st.header("پنل مدیر سامانه")
    tabs = st.tabs([
        "میز ارجاع",
        "نتایج داوری و تایید نهایی",
        "ثبت داور تخصصی",
        "مدیریت ویترین (حذف کامنت)",
        "پیشنهاد موضوعات",
        "تحقیقات صورت گرفته",
        "اسناد",
        "تالار گفتگو (تایید پیام‌ها)",
    ])

    with tabs[0]:
        st.subheader("میز ارجاع مدیر سامانه")
        items = db_submissions_pending_or_waiting_manager()
        if not items:
            st.info("موردی وجود ندارد.")
        else:
            for row in items:
                (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
                 fname,fmime,fbytes,status,likes,views,kcode,created_ts) = row

                if status not in ("pending", "waiting_referee"):
                    continue

                with st.expander(f"📌 {title} | {status_fa(status)} | {field_}"):
                    st.caption(f"فرستنده: {s_name} ({s_phone}) | نوع: {ctype}")
                    st.write(desc)
                    if fbytes:
                        st.download_button(
                            "دانلود فایل پیوست",
                            data=fbytes,
                            file_name=fname or "file",
                            key=f"dl_sub_{sid}"
                        )

                    refs = db_referees_by_field(field_)
                    if not refs:
                        st.warning("برای این حوزه داور فعالی ثبت نشده.")
                    else:
                        options = [(f"{r[0]} {r[1]} ({r[4]})", r[2], f"{r[0]} {r[1]}", r[4]) for r in refs]
                        chosen = st.multiselect(
                            "انتخاب داور/داوران",
                            options,
                            format_func=lambda x: x[0],
                            key=f"ms_{sid}",
                        )

                        if st.button("ارجاع به داور(ها)", key=f"assign_{sid}", type="primary"):
                            if not chosen:
                                st.error("حداقل یک داور انتخاب کن.")
                            else:
                                for item in chosen:
                                    _, rphone, rname, rfield = item
                                    db_assignment_create(
                                        make_id("a"),
                                        sid,
                                        normalize_phone(rphone),
                                        rname,
                                        rfield
                                    )
                                db_submission_set_status(sid, "waiting_referee")
                                st.success("ارجاع انجام شد ✅")
                                st.rerun()

    with tabs[1]:
        st.subheader("نتایج داوری و تایید نهایی")
        items = db_submissions_pending_or_waiting_manager()
        found = False

        for row in items:
            (sid,title,desc,s_phone,s_name,s_nid,topic_id,field_,ctype,
             fname,fmime,fbytes,status,likes,views,kcode,created_ts) = row

            assigns = db_assignments_for_submission(sid)
            if not assigns:
                continue

            recommend_publish = any(a[5] == "recommend_publish" for a in assigns)
            any_correction = any(a[5] == "correction_needed" for a in assigns)
            any_reject = any(a[5] == "rejected" for a in assigns)

            if not (recommend_publish or any_correction or any_reject):
                continue

            found = True
            with st.expander(f"🧾 {title} | {field_}"):
                st.caption(f"فرستنده: {s_name} ({s_phone}) | وضعیت فعلی: {status_fa(status)}")
                st.write(desc)

                st.subheader("گزارش داوران")
                for a in assigns:
                    (aid, subid, rph, rname, rfield, decision, feedback, score, skc, rts, cts2) = a
                    st.write(f"- **{rname} ({rfield})** | نتیجه: **{decision}** | امتیاز: **{score}**")
                    if feedback:
                        st.write(f"  📝 {feedback}")
                    if skc:
                        st.caption(f"کد پیشنهادی: {skc}")

                st.divider()

                manager_choice = st.selectbox(
                    "تصمیم نهایی مدیر",
                    ["waiting_manager", "published", "correction_needed", "rejected"],
                    format_func=status_fa,
                    key=f"mgr_dec_{sid}"
                )

                suggested_codes = [a[8] for a in assigns if a[8]]
                default_code = suggested_codes[0] if suggested_codes else ""
                mgr_code = st.text_input("کد دانشی (برای انتشار)", value=default_code, key=f"mgr_code_{sid}")

                if st.button("ثبت تصمیم نهایی", key=f"mgr_save_{sid}", type="primary"):
                    if manager_choice == "published":
                        if not mgr_code.strip():
                            st.error("برای انتشار باید کد دانشی وارد شود.")
                        else:
                            db_submission_publish(sid, mgr_code.strip())
                            st.success("منتشر شد ✅")
                            st.rerun()
                    else:
                        db_submission_set_status(sid, manager_choice)
                        st.success("ثبت شد ✅")
                        st.rerun()

        if not found:
            st.info("فعلاً نتیجه داوری قابل تصمیم‌گیری وجود ندارد.")

    with tabs[2]:
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

    with tabs[3]:
        st.subheader("مدیریت ویترین دانش (حذف کامنت)")
        published = db_submissions_published()
        if not published:
            st.info("محتوایی جهت مدیریت نظرات یافت نشد.")
        else:
            for row in published:
                sid, title = row[0], row[1]
                comments = db_comments_for(sid)
                with st.expander(f"نظرات محتوای: {title}"):
                    if not comments:
                        st.caption("نظری برای این محتوا ثبت نشده است.")
                    else:
                        for (cid, uname, ctext, cts) in comments:
                            col_c1, col_c2 = st.columns([5, 1])
                            col_c1.write(f"**{uname}**: {ctext}")
                            if col_c2.button("🗑 حذف", key=f"del_c_{cid}"):
                                db_comment_delete(cid)
                                st.success("نظر حذف شد ✅")
                                st.rerun()

    with tabs[4]:
        st.subheader("مدیریت موضوعات پیشنهادی")
        with st.form("mgr_topic_form"):
            mt_title = st.text_input("عنوان موضوع")
            mt_field = st.selectbox("حوزه موضوع", FIELDS)
            mt_desc = st.text_area("توضیحات و اهداف موضوع")
            mt_file = st.file_uploader("پیوست راهنما (اختیاری)", type=None)
            submitted = st.form_submit_button("ثبت موضوع جدید", type="primary")
            if submitted:
                if not mt_title.strip():
                    st.error("عنوان الزامی است")
                else:
                    db_topic_insert(
                        make_id("top"),
                        mt_title.strip(),
                        mt_field,
                        mt_desc.strip(),
                        mt_file.name if mt_file else "",
                        mt_file.getvalue() if mt_file else None
                    )
                    st.success("موضوع با موفقیت منتشر شد ✅")
                    st.rerun()

    with tabs[5]:
        st.subheader("مدیریت تحقیقات صورت گرفته")
        with st.form("mgr_res_form"):
            mr_title = st.text_input("عنوان تحقیق")
            mr_field = st.selectbox("حوزه تحقیق", FIELDS)
            mr_summary = st.text_area("خلاصه تحقیق")
            mr_file = st.file_uploader("فایل تحقیق (اختیاری)", type=None)
            submitted = st.form_submit_button("ثبت سوابق تحقیق", type="primary")
            if submitted:
                if not mr_title.strip():
                    st.error("عنوان الزامی است")
                else:
                    db_research_insert(
                        make_id("res"),
                        mr_title.strip(),
                        mr_field,
                        mr_summary.strip(),
                        mr_file.name if mr_file else "",
                        mr_file.getvalue() if mr_file else None
                    )
                    st.success("تحقیق ثبت شد ✅")
                    st.rerun()

    with tabs[6]:
        st.subheader("بارگذاری اسناد و نشریات تخصصی")
        with st.form("mgr_doc_form"):
            md_title = st.text_input("عنوان سند/آیین‌نامه")
            md_file = st.file_uploader("انتخاب فایل سند", type=None)
            submitted = st.form_submit_button("ذخیره در کتابخانه اسناد", type="primary")
            if submitted:
                if not md_title.strip() or not md_file:
                    st.error("عنوان و فایل الزامی است")
                else:
                    db_doc_insert(make_id("doc"), md_title.strip(), md_file.name, md_file.getvalue())
                    st.success("سند با موفقیت بارگذاری شد ✅")
                    st.rerun()

    with tabs[7]:
        st.subheader("مدیریت و تایید پیام‌های تالار گفتگو")
        pend_posts = db_forum_posts("pending")
        if not pend_posts:
            st.info("پیامی در انتظار تایید وجود ندارد.")
        else:
            for p in pend_posts:
                with st.container(border=True):
                    st.write(f"**از طرف:** {p[2]} ({status_fa(p[3])})")
                    st.info(p[4])
                    f_col1, f_col2 = st.columns(2)
                    if f_col1.button("✅ تایید انتشار عمومی", key=f"fok_{p[0]}", type="primary", use_container_width=True):
                        db_forum_set_status(p[0], "approved")
                        st.rerun()
                    if f_col2.button("❌ رد پیام", key=f"fno_{p[0]}", use_container_width=True):
                        db_forum_set_status(p[0], "rejected")
                        st.rerun()

# ===================== REFEREE (پنل داوری) =====================
elif st.session_state.role == "referee":
    st.header("پنل داوری تخصصی نخبگان دانشی")
    tasks = db_assignments_for_referee(st.session_state.phone)

    if not tasks:
        st.info("محتوایی جهت ارزیابی به شما ارجاع نشده است.")
    else:
        ref_l, ref_r = st.columns([1.5, 2.5])
        with ref_l:
            st.subheader("لیست ارجاعات شما")
            for t in tasks:
                assign_id, sid = t[0], t[1]
                decision = t[5]
                title = t[11]
                if st.button(f"📄 {title}\n({status_fa(decision)})", key=f"open_{assign_id}", use_container_width=True):
                    st.session_state.selected_submission_id = assign_id
                    st.rerun()

        with ref_r:
            if not st.session_state.selected_submission_id:
                st.info("یک مورد را برای ارزیابی انتخاب کنید.")
            else:
                target = [x for x in tasks if x[0] == st.session_state.selected_submission_id][0]
                st.subheader(f"ارزیابی: {target[11]}")
                st.caption(f"فرستنده: {target[13]} | حوزه: {target[15]} | نوع: {target[16]}")
                st.write(f"**شرح محتوا:**\n{target[12]}")
                if target[19]:
                    st.download_button(
                        "📩 دریافت فایل ارسالی کاربر",
                        data=target[19],
                        file_name=target[17] or "content",
                        key=f"dl_ref_{target[0]}"
                    )

                st.divider()
                st.subheader("ثبت نتیجه ارزیابی")
                rev_status = st.selectbox(
                    "نظر شما:",
                    ["waiting_referee", "correction_needed", "rejected", "recommend_publish"],
                    index=0,
                    format_func=lambda x: {
                        "waiting_referee":"در حال بررسی",
                        "correction_needed":"نیاز به اصلاح",
                        "rejected":"عدم تایید",
                        "recommend_publish":"تایید و پیشنهاد انتشار"
                    }[x]
                )
                rev_feedback = st.text_area("نکات اصلاحی / دلایل داوری (برای کاربر نمایش داده می‌شود)", value=target[6] or "")
                rev_score = st.number_input("امتیاز تخصصی (۰ تا ۱۰۰)", 0, 100, int(target[7] or 0))
                rev_code = st.text_input("کد دانشی پیشنهادی (الزامی برای انتشار)", value=target[8] or "")

                if st.button("ثبت نهایی و ارسال برای مدیر سامانه", type="primary", use_container_width=True):
                    if rev_status == "recommend_publish" and not rev_code:
                        st.error("برای پیشنهاد انتشار، حتماً یک کد دانشی وارد کنید.")
                    else:
                        db_assignment_update(target[0], rev_status, rev_feedback, rev_score, rev_code)
                        m_status = "waiting_manager" if rev_status == "recommend_publish" else rev_status
                        db_submission_set_status(target[1], m_status)
                        st.success("ارزیابی شما با موفقیت ثبت شد و به مدیر سامانه ارجاع یافت ✅")
                        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Page: Forum
# =========================================================
elif st.session_state.page == "تالار گفتگو":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("تالار گفتگو و پرسش و پاسخ")

    st.caption("پیام شما پس از تایید مدیر برای همه نمایش داده خواهد شد.")
    f_msg = st.text_area("پیام یا سوال خود را بنویسید...", height=120)

    if st.button("ارسال برای تایید", type="primary"):
        if f_msg.strip():
            db_forum_post_add(
                make_id("fp"),
                st.session_state.phone,
                st.session_state.name,
                st.session_state.role,
                f_msg.strip()
            )
            st.success("ارسال شد ✅ منتظر تایید مدیر باشید.")
            st.rerun()
        else:
            st.error("متن پیام خالی است.")

    st.divider()

    approved_posts = db_forum_posts("approved")
    if not approved_posts:
        st.info("هنوز پیامی تایید نشده.")
    else:
        for ap in approved_posts:
            post_id = ap[0]
            sender_name = ap[2]
            sender_role = ap[3]
            text = ap[4]
            created_ts = ap[6]

            with st.container(border=True):
                st.write(f"👤 **{sender_name}** ({sender_role})")
                st.write(text)
                st.caption(f"زمان: {ts_str(created_ts)}")

                replies = db_forum_replies(post_id)
                if replies:
                    st.subheader("پاسخ‌ها")
                    for rep in replies:
                        rep_name = rep[2]
                        rep_text = rep[3]
                        rep_ts = rep[4]
                        st.markdown(
                            f"""
                            <div style="background:#f0f7ff; padding:10px; border-right:4px solid #0b2a4a; margin:6px 0; border-radius:10px;">
                              <b>👨‍🏫 {rep_name}:</b><br>{rep_text}
                              <div style="font-size:12px; margin-top:6px; color:#334155;">{ts_str(rep_ts)}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                if st.session_state.role == "referee":
                    st.divider()
                    r_text = st.text_input("پاسخ داور به این سوال", key=f"rinput_{post_id}")
                    btn_key = f"btn_rep_{post_id}"
                    if st.button("ثبت پاسخ نخبگان ✅", key=btn_key, type="primary"):
                        if r_text.strip():
                            db_forum_reply_add(
                                make_id("fr"),
                                post_id,
                                st.session_state.phone,
                                st.session_state.name,
                                r_text.strip()
                            )
                            st.success("پاسخ شما ثبت شد و برای همه قابل مشاهده است ✅")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("متن پاسخ نمی‌تواند خالی باشد.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PAGE: PROFILE (پروفایل)
# =========================================================
elif st.session_state.page == "پروفایل":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.header("پروفایل کاربری")
    st.write(f"🆔 **نام:** {st.session_state.name}")
    st.write(f"📞 **همراه:** {st.session_state.phone}")
    st.write(f"🎭 **نقش شما:** {status_fa(st.session_state.role)}")
    if st.session_state.role == "user":
        st.write(f"🪪 **کد ملی:** {st.session_state.get('nid','---')}")

    st.divider()
    if st.button("🚪 خروج از سامانه", type="primary", use_container_width=True):
        logout()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # End Shell

