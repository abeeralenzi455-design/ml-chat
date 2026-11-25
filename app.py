import hmac
import html
import time
from datetime import datetime

import streamlit as st

# ---------- الإعدادات ----------
PLATFORM_NAME = "mL"
ROOM_ID = "311130"
MAIN_COLOR = "#1ABC9C"   # غيّر اللون من هنا
MAX_LEN = 500

# القادة ورموزهم (الأفضل تحطها في Streamlit Secrets بدل الكود، شوف الشرح)
DEFAULT_ADMINS = {
    "4839": "أبو داحم",
    "3093": "الوليد",
    "9809": "BLACK",
    "6472": "فطومه",
}
try:
    ADMINS = dict(st.secrets["ADMINS"])   # شكلها في Secrets: [ADMINS]  1234 = "الاسم"
except Exception:
    ADMINS = DEFAULT_ADMINS

st.set_page_config(page_title="مزح ولعب", page_icon="💬", layout="centered")


# ---------- مخزن الرسائل (مشترك بين كل المستخدمين) ----------
@st.cache_resource
def get_store():
    return {"messages": [], "fails": 0, "locked_until": 0.0}


store = get_store()

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
    f'<div class="box">ID: {ROOM_ID}</div>',
    unsafe_allow_html=True,
)

# ---------- مربع كتابة الرسالة ----------
with st.form("msg_form", clear_on_submit=True):
    text = st.text_area("اكتب رسالتك (مجهولة 🕵️)", max_chars=MAX_LEN, height=100)
    sent = st.form_submit_button("إرسال", use_container_width=True)

if sent:
    clean = text.strip()
    if clean:
        store["messages"].append(
            {"text": clean, "time": datetime.now().strftime("%H:%M")}
        )
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
        c1, c2 = st.columns(2)
        if c1.button("🗑️ مسح كل الرسائل", use_container_width=True):
            store["messages"].clear()
            st.rerun()
        if c2.button("خروج", use_container_width=True):
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


st.divider()
st.subheader("الرسائل")


# ---------- عرض الرسائل (تتحدث تلقائيًا كل 3 ثواني) ----------
@st.fragment(run_every=3)
def show_messages():
    msgs = store["messages"]
    if not msgs:
        st.info("ما فيه رسائل للحين، كن أول واحد يرسل!")
        return
    for m in reversed(msgs):  # الأحدث فوق
        st.markdown(
            f'<div class="msg">{html.escape(m["text"])}'
            f'<div class="time">{m["time"]}</div></div>',
            unsafe_allow_html=True,
        )


show_messages()
