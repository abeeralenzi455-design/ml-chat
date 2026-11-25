import hmac
import html
import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="مزح ولعب", page_icon="💬", layout="centered")

# ---------- الإعدادات ----------
PLATFORM_NAME = "mL"
ROOM_ID = "311130"
MAIN_COLOR = "#1ABC9C"   # غيّر اللون من هنا
MAX_LEN = 500

# القادة ورموزهم (الأفضل تحطها في Streamlit Secrets بدل الكود، شوف الشرح)
DEFAULT_ADMINS = {
    "3093": "الوليد",
    "9809": "BLACK",
}
try:
    ADMINS = dict(st.secrets["ADMINS"])   # شكلها في Secrets: [ADMINS]  1234 = "الاسم"
except Exception:
    ADMINS = DEFAULT_ADMINS



# ---------- مخزن الرسائل (مشترك بين كل المستخدمين) ----------
DATA_FILE = Path(__file__).with_name("messages_backup.json")


@st.cache_resource
def get_store():
    msgs = []
    try:  # يرجّع الرسائل المحفوظة لو الملف موجود
        msgs = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    nid = max([m.get("id", 0) for m in msgs], default=0)
    return {"messages": msgs, "next_id": nid, "fails": 0, "locked_until": 0.0}


store = get_store()


def save():
    """حفظ الرسائل في ملف (يساعد لو التطبيق انعاد تشغيله، بس مو مضمون 100%)"""
    try:
        DATA_FILE.write_text(
            json.dumps(store["messages"], ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass

# ---------- زر الوضع الليلي / النهاري ----------
dark = st.toggle("🌙 الوضع الليلي", key="dark_mode")

if dark:
    GRAD = "#0b1f2a, #1a1038, #0a2e2b, #102040"
    TEXT, CARD, INPUT_BG = "#f1f1f1", "rgba(16,26,38,.85)", "#1b222c"
else:
    GRAD = "#d9fbf3, #e0e7ff, #fce7f3, #cffafe"
    TEXT, CARD, INPUT_BG = "#1f2937", "rgba(255,255,255,.88)", "#ffffff"
BG = "transparent"

# ---------- التصميم ----------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(-45deg, {GRAD});
        background-size: 400% 400%;
        animation: gradMove 18s ease infinite;
    }}
    @keyframes gradMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .bubbles {{ position: fixed; inset: 0; overflow: hidden; pointer-events: none; z-index: 0; }}
    .bubbles span {{ position: absolute; bottom: -60px; animation: rise linear infinite; }}
    @keyframes rise {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        10% {{ opacity: .6; }}
        100% {{ transform: translateY(-115vh) rotate(360deg); opacity: 0; }}
    }}
    .block-container {{ position: relative; z-index: 1; }}
    .stApp, .stApp p, .stApp label, .stApp span, .stApp h1, .stApp h2,
    .stApp h3, .stApp div[data-testid="stWidgetLabel"] {{ color: {TEXT} !important; }}
    header[data-testid="stHeader"] {{ background: {BG}; }}
    .block-container {{ direction: rtl; text-align: right; max-width: 700px; }}
    .stTextArea textarea {{
        background: {INPUT_BG}; color: {TEXT};
        border: 1px solid {MAIN_COLOR}; border-radius: 12px;
    }}
    .stButton button, div[data-testid="stFormSubmitButton"] button {{
        background: {MAIN_COLOR}; color: white; border: none; border-radius: 12px;
    }}
    div[data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: .3rem !important; }}
    div[data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }}
    .stButton button p, div[data-testid="stFormSubmitButton"] button p {{ color: white !important; }}
    .stButton button {{ padding: .15rem .3rem; min-height: 2rem; }}
    .reply {{ background: {CARD}; border-radius: 10px; padding: 6px 10px; margin: 4px 0; font-size: 14px; }}
    .who {{ font-weight: 700; font-size: 13px; opacity: .85; margin-bottom: 2px; }}
    div[data-testid="stColumn"]:has(.reply) {{ flex: 6 1 0 !important; }}
    .box {{
        background: {MAIN_COLOR};
        color: white !important;
        border-radius: 16px;
        padding: 14px 18px;
        margin-bottom: 10px;
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,.15);
    }}
    .box small {{ display:block; font-size:13px; font-weight:400; opacity:.9; color: white !important; }}
    .msg {{
        background: {CARD};
        border-right: 5px solid {MAIN_COLOR};
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        word-wrap: break-word;
        color: {TEXT};
    }}
    .msg .time {{ font-size: 12px; opacity: .6; margin-top: 4px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- خلفية الفقاعات ----------
st.markdown('<div class="bubbles"><span style="left:43%;font-size:22px;animation-duration:15s;animation-delay:-1s">🎈</span><span style="left:11%;font-size:35px;animation-duration:10s;animation-delay:-11s">✨</span><span style="left:76%;font-size:19px;animation-duration:17s;animation-delay:-6s">💬</span><span style="left:6%;font-size:20px;animation-duration:15s;animation-delay:-13s">🎭</span><span style="left:10%;font-size:25px;animation-duration:10s;animation-delay:-17s">😂</span><span style="left:56%;font-size:19px;animation-duration:18s;animation-delay:-3s">🫧</span><span style="left:30%;font-size:38px;animation-duration:19s;animation-delay:-18s">🎉</span><span style="left:9%;font-size:36px;animation-duration:18s;animation-delay:-12s">🤫</span><span style="left:8%;font-size:25px;animation-duration:9s;animation-delay:-17s">🎈</span><span style="left:19%;font-size:27px;animation-duration:15s;animation-delay:-4s">✨</span><span style="left:71%;font-size:21px;animation-duration:18s;animation-delay:-9s">💬</span><span style="left:73%;font-size:23px;animation-duration:10s;animation-delay:-18s">🎭</span><span style="left:75%;font-size:38px;animation-duration:12s;animation-delay:-11s">😂</span><span style="left:14%;font-size:35px;animation-duration:20s;animation-delay:-2s">🫧</span><span style="left:74%;font-size:19px;animation-duration:18s;animation-delay:-6s">🎉</span><span style="left:65%;font-size:35px;animation-duration:15s;animation-delay:-10s">🤫</span></div>', unsafe_allow_html=True)

# ---------- المربعات العلوية ----------
st.markdown(
    f'<div class="box">هنا تمزح وتلعب وتقول اللي بخاطرك<br>وانت مجهول 🎭</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="box">منصة رسائل مجهولة خاصة في مزح ولعب</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="box">ID: {ROOM_ID}</div>',
    unsafe_allow_html=True,
)

# ---------- الاسم (اختياري) ----------
use_name = st.toggle("✍️ أكتب باسمي (بدل مجهول)", key="use_name")
if use_name:
    st.text_input("اسمك", max_chars=20, key="my_name", placeholder="مثلاً: سعود")


def current_name():
    if st.session_state.get("use_name"):
        n = (st.session_state.get("my_name") or "").strip()
        return n or None
    return None


def who(name):
    return f"👤 {html.escape(name)}" if name else "🕵️ مجهول"


# ---------- مربع كتابة الرسالة ----------
with st.form("msg_form", clear_on_submit=True):
    text = st.text_area("اكتب رسالتك", max_chars=MAX_LEN, height=100)
    sent = st.form_submit_button("إرسال", use_container_width=True)

if sent:
    clean = text.strip()
    if clean:
        store["next_id"] += 1
        store["messages"].append(
            {
                "id": store["next_id"],
                "text": clean,
                "time": datetime.now().strftime("%H:%M"),
                "name": current_name(),
                "reactions": {},
                "replies": [],
                "status": "pending",   # وارد، بانتظار موافقة القائد
            }
        )
        save()
        st.success("وصلت رسالتك ✅ وبتظهر بعد ما القائد يوافق عليها")
    else:
        st.warning("اكتب شي قبل لا ترسل 😅")

# ---------- لوحة القائد (مسح الرسائل) ----------
def find_admin(code):
    for k, name in ADMINS.items():
        if hmac.compare_digest(str(k), code):
            return name
    return None


with st.expander("🔐 القائد"):
    if st.session_state.get("admin"):
        st.success(f"أهلاً {st.session_state['admin']} 👑")
        st.download_button(
            "⬇️ نسخة احتياطية من الرسائل",
            data=json.dumps(store["messages"], ensure_ascii=False, indent=2),
            file_name="messages_backup.json",
            mime="application/json",
            use_container_width=True,
        )
        if st.button("خروج", use_container_width=True):
            st.session_state["admin"] = None
            st.rerun()
    else:
        code = st.text_input("الرمز", type="password", max_chars=4, key="admin_code")
        if st.button("دخول", use_container_width=True):
            if time.time() < store["locked_until"]:
                st.error("محاولات كثيرة، انتظر دقيقة ⏳")
            else:
                name = find_admin(code.strip())
                if name:
                    store["fails"] = 0
                    st.session_state["admin"] = name
                    st.rerun()
                else:
                    store["fails"] += 1
                    if store["fails"] >= 10:
                        store["locked_until"] = time.time() + 60
                        store["fails"] = 0
                    st.error("الرمز غلط ❌")


# ---------- الرسائل الواردة (للقائد بس) ----------
@st.fragment(run_every=5)
def show_inbox():
    pending = [m for m in store["messages"] if m.get("status") == "pending"]
    st.subheader(f"📥 الرسائل الواردة ({len(pending)})")
    if not pending:
        st.caption("ما فيه رسائل جديدة")
        return
    for m in pending:
        mid = m["id"]
        st.markdown(
            f'<div class="msg"><div class="who">{who(m.get("name"))}</div>'
            f'{html.escape(m["text"])}<div class="time">{m["time"]}</div></div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("✅ نشر", key=f"pub_{mid}", use_container_width=True):
            m["status"] = "published"
            save()
            st.rerun()
        if c2.button("🗑️ حذف", key=f"rej_{mid}", use_container_width=True):
            store["messages"] = [x for x in store["messages"] if x["id"] != mid]
            save()
            st.rerun()


if st.session_state.get("admin"):
    show_inbox()

st.divider()
st.subheader("الرسائل")


# ---------- عرض الرسائل (تتحدث تلقائيًا كل 5 ثواني) ----------
EMOJIS = ["👍", "😂", "❤️", "🔥", "😮"]


@st.fragment(run_every=5)
def show_messages():
    msgs = [m for m in store["messages"] if m.get("status", "published") == "published"]
    if not msgs:
        st.info("ما فيه رسائل منشورة للحين، كن أول واحد يرسل!")
        return
    mine = st.session_state.setdefault("my_reacts", set())
    for m in reversed(msgs):  # الأحدث فوق
        mid = m["id"]
        st.markdown(
            f'<div class="msg"><div class="who">{who(m.get("name"))}</div>'
            f'{html.escape(m["text"])}<div class="time">{m["time"]}</div></div>',
            unsafe_allow_html=True,
        )

        # حذف رسالة وحدة (للقائد بس)
        if st.session_state.get("admin"):
            if st.button("🗑️ حذف هذي الرسالة", key=f"d_{mid}", use_container_width=True):
                store["messages"] = [x for x in store["messages"] if x["id"] != mid]
                save()
                st.rerun(scope="fragment")

        # التفاعل بالإيموجي (ضغطة تضيف، وضغطة ثانية تلغي)
        cols = st.columns(len(EMOJIS))
        for col, e in zip(cols, EMOJIS):
            n = m["reactions"].get(e, 0)
            label = f"{e} {n}" if n else e
            if col.button(label, key=f"r_{mid}_{e}", use_container_width=True):
                if (mid, e) in mine:
                    mine.discard((mid, e))
                    m["reactions"][e] = max(0, n - 1)
                else:
                    mine.add((mid, e))
                    m["reactions"][e] = n + 1
                save()
                st.rerun(scope="fragment")

        # الردود
        with st.expander(f"💬 الردود ({len(m['replies'])})"):
            for r in m["replies"]:
                if "id" not in r:  # ردود قديمة بدون رقم
                    store["next_id"] += 1
                    r["id"] = store["next_id"]
                reply_html = (
                    f'<div class="reply"><div class="who">{who(r.get("name"))}</div>'
                    f'{html.escape(r["text"])}<div class="time">{r["time"]}</div></div>'
                )
                if st.session_state.get("admin"):
                    rc1, rc2 = st.columns([6, 1])
                    rc1.markdown(reply_html, unsafe_allow_html=True)
                    if rc2.button("🗑️", key=f"dr_{mid}_{r['id']}", help="حذف الرد"):
                        m["replies"] = [x for x in m["replies"] if x.get("id") != r["id"]]
                        save()
                        st.rerun(scope="fragment")
                else:
                    st.markdown(reply_html, unsafe_allow_html=True)
            with st.form(f"rf_{mid}", clear_on_submit=True):
                rt = st.text_input("اكتب ردك", max_chars=200, key=f"rt_{mid}")
                if st.form_submit_button("رد", use_container_width=True):
                    if rt.strip():
                        store["next_id"] += 1
                        m["replies"].append(
                            {
                                "id": store["next_id"],
                                "text": rt.strip(),
                                "time": datetime.now().strftime("%H:%M"),
                                "name": current_name(),
                            }
                        )
                        save()
                        st.rerun(scope="fragment")


show_messages()
