import html
from datetime import datetime

import streamlit as st

# ---------- الإعدادات ----------
PLATFORM_NAME = "mL"
ROOM_ID = "311130"
MAIN_COLOR = "#1ABC9C"   # غيّر اللون من هنا
MAX_LEN = 500

st.set_page_config(page_title=PLATFORM_NAME, page_icon="💬", layout="centered")


# ---------- مخزن الرسائل (مشترك بين كل المستخدمين) ----------
@st.cache_resource
def get_store():
    return {"messages": []}


store = get_store()

# ---------- زر الوضع الليلي / النهاري ----------
dark = st.toggle("🌙 الوضع الليلي", key="dark_mode")

if dark:
    BG, TEXT, CARD, INPUT_BG = "#0e1117", "#f1f1f1", "rgba(26,188,156,.18)", "#1b222c"
else:
    BG, TEXT, CARD, INPUT_BG = "#ffffff", "#1f2937", "rgba(26,188,156,.12)", "#f3f4f6"

# ---------- التصميم ----------
st.markdown(
    f"""
    <style>
    .stApp {{ background: {BG}; }}
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

# ---------- المربعات العلوية ----------
st.markdown(
    f'<div class="box">{PLATFORM_NAME}<small>منصة مزح ولعب</small></div>',
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
