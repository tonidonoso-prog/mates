import streamlit as st
import random
import time
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Aventura Matemàtica",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Bungee&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* SIDEBAR: sempre visible, sense scroll */
    section[data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 300px !important;
        transform: none !important;
        visibility: visible !important;
        display: block !important;
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important;
        width: 300px !important;
        min-width: 300px !important;
    }

    /* Amaga botó de col·lapsar */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Close sidebar"],
    button[aria-label="Collapse sidebar"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    /* Contingut sidebar: sense scroll, compacte */
    [data-testid="stSidebarUserContent"] {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebarUserContent"] > div {
        overflow: hidden !important;
        gap: 0 !important;
    }

    /* Elimina espai entre títol i imatge */
    [data-testid="stSidebar"] h1 {
        font-size: 1.4rem !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    [data-testid="stSidebar"] img {
        margin-top: 0 !important;
        padding-top: 0 !important;
        display: block !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stImageContainer"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] p {
        font-size: 0.85rem !important;
        margin: 4px 0 2px 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }

    /* Botons sidebar compactes */
    [data-testid="stSidebar"] button {
        font-family: 'Bungee', cursive !important;
        font-size: 0.9rem !important;
        height: 38px !important;
        margin-bottom: 3px !important;
        border-radius: 10px !important;
        background: white !important;
        border: 2px solid #FF6B6B !important;
        color: #FF6B6B !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] div.stButton {
        margin-bottom: 0 !important;
    }

    /* MAIN */
    .block-container {
        padding-top: 1rem !important;
        max-width: 900px !important;
    }
    .stApp {
        background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%);
        background-attachment: fixed;
    }

    /* Títol principal */
    .app-title {
        font-family: 'Bungee', cursive;
        font-size: 2.2rem;
        color: #FF6B6B;
        text-align: center;
        margin: 0 0 0.8rem 0;
        padding: 0;
        letter-spacing: 1px;
    }

    /* Main Card */
    .main-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 40px;
        padding: 1.5rem 2rem 2rem 2rem;
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.25);
        text-align: center;
        margin: auto;
    }

    /* Caixa problema */
    .problem-box {
        font-family: 'Bungee', cursive !important;
        font-size: 5rem !important;
        height: 160px !important;
        width: 100% !important;
        max-width: 600px !important;
        border-radius: 30px !important;
        background: white !important;
        border: 8px dashed #FF6B6B !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 10px auto !important;
        color: #2D3436 !important;
        text-align: center !important;
    }

    /* Input numèric gran */
    div[data-testid="stNumberInput"] {
        height: 160px !important;
        width: 100% !important;
        max-width: 600px !important;
        margin: 10px auto !important;
        display: flex !important;
        align-items: stretch !important;
    }
    div[data-testid="stNumberInput"] > div {
        height: 160px !important;
        width: 100% !important;
        background: transparent !important;
        border: none !important;
        display: flex !important;
        align-items: stretch !important;
    }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        height: 160px !important;
        background: white !important;
        border: 8px dashed #FF6B6B !important;
        border-radius: 30px !important;
    }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] input {
        height: 160px !important;
        font-family: 'Bungee', cursive !important;
        font-size: 5rem !important;
        text-align: center !important;
        background: transparent !important;
        border: none !important;
        color: #2D3436 !important;
    }
    div[data-testid="stNumberInput"] button {
        height: 160px !important;
        border-radius: 0 30px 30px 0 !important;
    }

    /* Botó comprovar */
    .main-card div.stButton > button {
        background: linear-gradient(180deg, #FF6B6B 0%, #EE5253 100%) !important;
        color: white !important;
        font-family: 'Bungee', cursive !important;
        font-size: 2.5rem !important;
        height: 90px !important;
        max-width: 600px !important;
        border-radius: 20px !important;
        border: none !important;
        box-shadow: 0 10px 0px #D63031 !important;
        margin: 15px auto !important;
        display: block !important;
        text-transform: uppercase !important;
    }
    .main-card div.stButton > button:active {
        transform: translateY(8px) !important;
        box-shadow: 0 2px 0px #D63031 !important;
    }

    /* Overlay */
    .overlay {
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 40px 60px;
        border-radius: 40px;
        font-family: 'Bungee', cursive;
        font-size: 4rem;
        z-index: 9999;
        text-align: center;
        border: 10px solid white;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Session State
if 'score' not in st.session_state: st.session_state.score = 0
if 'num1' not in st.session_state: st.session_state.num1, st.session_state.num2 = 0, 0
if 'last_status' not in st.session_state: st.session_state.last_status = None
if 'mode' not in st.session_state: st.session_state.mode = "Sumes"
if 'diff' not in st.session_state: st.session_state.diff = "Normal"
if 'input_key' not in st.session_state: st.session_state.input_key = 0

def get_new_problem():
    ranges = {"Fàcil": (1, 10), "Normal": (1, 20), "Difícil": (1, 50)}
    low, high = ranges.get(st.session_state.diff, (1, 10))
    mode = st.session_state.mode
    if mode == "Sumes":
        st.session_state.num1, st.session_state.num2 = random.randint(low, high), random.randint(low, high)
    elif mode == "Restes":
        st.session_state.num1 = random.randint(low + 5, high + 5)
        st.session_state.num2 = random.randint(1, st.session_state.num1)
    elif mode == "Multiplicació":
        m_high = 10 if st.session_state.diff != "Difícil" else 12
        st.session_state.num1, st.session_state.num2 = random.randint(1, m_high), random.randint(1, m_high)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#FF6B6B; font-family:Bungee; margin:0; padding:0;'>🎮 JOC</h1>", unsafe_allow_html=True)
    if Path("mascot.png").exists():
        st.image("mascot.png", width=100)

    st.markdown("<p style='font-weight:700;'>🧮 OPERACIÓ</p>", unsafe_allow_html=True)
    if st.button("SUMA " + ("✅" if st.session_state.mode == "Sumes" else ""), use_container_width=True):
        st.session_state.mode = "Sumes"; get_new_problem(); st.rerun()
    if st.button("RESTA " + ("✅" if st.session_state.mode == "Restes" else ""), use_container_width=True):
        st.session_state.mode = "Restes"; get_new_problem(); st.rerun()
    if st.button("MULTIPLICACIÓ " + ("✅" if st.session_state.mode == "Multiplicació" else ""), use_container_width=True):
        st.session_state.mode = "Multiplicació"; get_new_problem(); st.rerun()

    st.markdown("<p style='font-weight:700;'>📈 NIVELL</p>", unsafe_allow_html=True)
    if st.button("FÀCIL " + ("✅" if st.session_state.diff == "Fàcil" else ""), use_container_width=True):
        st.session_state.diff = "Fàcil"; get_new_problem(); st.rerun()
    if st.button("NORMAL " + ("✅" if st.session_state.diff == "Normal" else ""), use_container_width=True):
        st.session_state.diff = "Normal"; get_new_problem(); st.rerun()
    if st.button("DIFÍCIL " + ("✅" if st.session_state.diff == "Difícil" else ""), use_container_width=True):
        st.session_state.diff = "Difícil"; get_new_problem(); st.rerun()

    if st.button("🔄 REINICIAR", use_container_width=True):
        st.session_state.score = 0; get_new_problem(); st.rerun()

if st.session_state.num1 == 0: get_new_problem()

# --- MAIN UI ---
st.markdown("<div class='app-title'>🧮 Aventura Matemàtica</div>", unsafe_allow_html=True)

st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#FF6B6B; font-weight:700; font-size:1.8rem; margin:0;'>{st.session_state.mode.upper()} • {st.session_state.diff.upper()} • {st.session_state.score} ⭐</p>", unsafe_allow_html=True)

symbol = "+" if st.session_state.mode == "Sumes" else "-" if st.session_state.mode == "Restes" else "×"
st.markdown(f"<div class='problem-box'>{st.session_state.num1} {symbol} {st.session_state.num2}</div>", unsafe_allow_html=True)

user_input = st.number_input("Resultat?", step=1, value=None, format="%d", label_visibility="collapsed", key=f"input_{st.session_state.input_key}")
submit = st.button("COMPROVAR! 🚀", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if submit and user_input is not None:
    correct = (st.session_state.num1 + st.session_state.num2 if st.session_state.mode == "Sumes" else
               st.session_state.num1 - st.session_state.num2 if st.session_state.mode == "Restes" else
               st.session_state.num1 * st.session_state.num2)
    st.session_state.input_key += 1
    if user_input == correct:
        st.session_state.score += 1
        st.session_state.last_status = "correct"
        st.balloons()
        get_new_problem()
    else:
        st.session_state.last_status = "incorrect"
    st.rerun()

if st.session_state.last_status:
    msg, color = ("MOLT BÉ! 🎉", "#4CAF50") if st.session_state.last_status == "correct" else ("PROVA DE NOU! 🔄", "#F44336")
    st.markdown(f'<div class="overlay" style="background:{color}; color:white;">{msg}</div>', unsafe_allow_html=True)
    st.session_state.last_status = None
    time.sleep(1)
    st.rerun()
