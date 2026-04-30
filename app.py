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

CELEBRATION_GIFS = [
    "https://i.giphy.com/osMIREQbo3s2c.gif",
    "https://i.giphy.com/BQAk13taTaKYw.gif",
    "https://i.giphy.com/8Do5PA5jPmTd3x8GI4.gif",
    "https://i.giphy.com/bCcxY1ADkAqfS.gif",
    "https://i.giphy.com/kHCc089grRFzSnVHvq.gif",
    "https://i.giphy.com/hDwYu8UEcUone.gif",
    "https://i.giphy.com/fCmnDUmpNYqnE2PidN.gif",
    "https://i.giphy.com/Z8wxB5I34Wl9Rx0ilC.gif",
    "https://i.giphy.com/bP9S3BMElQ5XAWQIR3.gif",
    "https://i.giphy.com/N5J5reSW1XkWKoaeij.gif",
    "https://i.giphy.com/TdfyKrN7HGTIY.gif",
    "https://i.giphy.com/VkUdMsK42kNgrPWuHd.gif",
    "https://i.giphy.com/kagE8uswvjrC2KanKI.gif",
    "https://i.giphy.com/IXB6mQUgOqWQM.gif",
    "https://i.giphy.com/XMvrleT9jksXm.gif",
    "https://i.giphy.com/IzBpqKzHLtfTa.gif",
    "https://i.giphy.com/hEIuLmpW9DmGA.gif",
    "https://i.giphy.com/HJQObm4T6xS2Q.gif",
    "https://i.giphy.com/0WQXGB5aOPLdBRFWyH.gif",
    "https://i.giphy.com/11sBLVxNs7v6WA.gif"
]

LECTURA_WORDS = {
    "Fàcil": ["CASA", "PALA", "MÀ", "PA", "SOPA", "MAMA", "PAPA", "GAT", "GOS", "RIU", "SOL", "NEN", "NENA", "BOLA", "RODA"],
    "Normal": ["FINESTRA", "BUTACA", "ESTRELLA", "SABATA", "PILOTA", "FORQUILLA", "GIRAFA", "ELEFANT", "MOTXILLA", "CARAMEL"],
    "Difícil": ["ESQUIROL", "ORDINADOR", "FRIGORÍFIC", "ESTRABÒS", "CONEIXEMENT", "MATEMÀTIQUES", "LLIBRETA", "BOLÍGRAF"]
}

CELEBRATION_MESSAGES = [
    "MOLT BÉ!", "FANTÀSTIC!", "QUIN NIVELL!", "IMPRESSIONANT!", "BRUTAL!",
    "GENIAL!", "SUPERBÉ!", "HO HAS CLAVAT!", "MOLT BONA FEINA!", "INCREÏBLE!",
    "CONTINUA AIXÍ!", "IMBATIBLE!", "QUINA PRECISIÓ!", "UN 10!", "HO HAS ACONSEGUIT!",
    "MÀGIC!", "ESPECTACULAR!", "MOLT BEN PENSAT!", "BRAVO!", "ÈXIT TOTAL!"
]

# Custom CSS for THE PERFECT UI
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Bungee&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .block-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem !important;
    }

    .stApp {
        background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%);
        background-attachment: fixed;
    }

    .mode-card {
        background: white;
        border-radius: 40px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 10px solid transparent;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .mode-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 30px 60px rgba(0,0,0,0.2);
    }

    .card-mates { border-color: #FF6B6B; }
    .card-innovamat { border-color: #F7D716; }

    .main-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 40px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.25);
        text-align: center;
        width: 100%;
        max-width: 850px;
        margin: auto;
    }

    .problem-box {
        font-family: 'Bungee', cursive !important;
        font-size: 4.5rem !important;
        height: 180px !important;
        width: 100% !important;
        border-radius: 35px !important;
        background: white !important;
        border: 10px dashed #FF6B6B !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 20px auto !important;
        color: #2D3436 !important;
        text-align: center !important;
    }

    div[data-testid="stNumberInput"] {
        height: 160px !important;
        width: 100% !important;
        max-width: 700px !important;
        margin: 10px auto !important;
        display: flex !important;
        align-items: stretch !important;
    }
    div[data-testid="stNumberInput"] > div {
        height: 160px !important;
        width: 100% !important;
        border: none !important;
        background: transparent !important;
        display: flex !important;
        align-items: stretch !important;
    }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        height: 160px !important;
        background: white !important;
        border: 10px dashed #FF6B6B !important;
        border-radius: 35px !important;
    }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] input {
        height: 160px !important;
        font-family: 'Bungee', cursive !important;
        font-size: 4.5rem !important;
        text-align: center !important;
        background: transparent !important;
        border: none !important;
        color: #2D3436 !important;
    }

    div.stButton > button {
        background: linear-gradient(180deg, #FF6B6B 0%, #EE5253 100%) !important;
        color: white !important;
        font-family: 'Bungee', cursive !important;
        font-size: 2.5rem !important;
        height: 100px !important;
        width: 100% !important;
        max-width: 600px !important;
        border-radius: 25px !important;
        border: none !important;
        box-shadow: 0 10px 0px #D63031 !important;
        margin: 20px auto !important;
        display: block !important;
        text-transform: uppercase !important;
    }

    /* DESKTOP: sidebar fixa visible */
    @media (min-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 300px !important;
            min-width: 300px !important;
            transform: none !important;
            visibility: visible !important;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            margin-left: 0 !important;
            width: 300px !important;
            min-width: 300px !important;
        }
        button[data-testid="stSidebarCollapseButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Collapse sidebar"],
        button[aria-label="Open sidebar"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        .mobile-controls { display: none !important; }
    }

    @media (max-width: 767px) {
        section[data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
        }
        .main-card { width: 95% !important; padding: 1.5rem !important; }
        .problem-box { font-size: 3rem !important; height: 120px !important; }
        div.stButton > button { font-size: 1.6rem !important; height: 70px !important; }
    }

    .gif-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 999999;
    }
    .gif-overlay img {
        max-width: 85%;
        max-height: 50%;
        border-radius: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        border: 8px solid #FF6B6B;
    }

    .race-track {
        background: #333;
        height: 100px;
        width: 100%;
        border-radius: 20px;
        position: relative;
        margin: 10px 0;
        border: 4px dashed white;
        overflow: hidden;
    }
    .car {
        font-size: 2.5rem;
        position: absolute;
        transition: left 0.5s ease;
        top: 50%;
        transform: translateY(-50%);
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Helper for compatibility
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# Session State
if 'current_block' not in st.session_state: st.session_state.current_block = "Home"
if 'score' not in st.session_state: st.session_state.score = 0
if 'num1' not in st.session_state: st.session_state.num1, st.session_state.num2 = 0, 0
if 'last_status' not in st.session_state: st.session_state.last_status = None
if 'mode' not in st.session_state: st.session_state.mode = "Sumes"
if 'diff' not in st.session_state: st.session_state.diff = "Fàcil"
if 'innovamat_type' not in st.session_state: st.session_state.innovamat_type = "Amics"
if 'reading_pos' not in st.session_state: st.session_state.reading_pos = 0
if 'rival_pos' not in st.session_state: st.session_state.rival_pos = 0
if 'reading_word' not in st.session_state: st.session_state.reading_word = ""
if 'problem_text' not in st.session_state: st.session_state.problem_text = ""
if 'correct_answer' not in st.session_state: st.session_state.correct_answer = 0
if 'input_key' not in st.session_state: st.session_state.input_key = 0

def get_new_problem():
    ranges = {"Fàcil": (1, 10), "Normal": (1, 50), "Difícil": (1, 200)}
    low, high = ranges.get(st.session_state.diff, (1, 10))
    
    if st.session_state.current_block == "Mates":
        mode = st.session_state.mode
        if mode == "Sumes":
            if st.session_state.diff == "Difícil":
                st.session_state.num1, st.session_state.num2 = random.randint(50, 250), random.randint(50, 250)
            elif st.session_state.diff == "Normal":
                st.session_state.num1, st.session_state.num2 = random.randint(10, 100), random.randint(10, 100)
            else:
                st.session_state.num1, st.session_state.num2 = random.randint(1, 15), random.randint(1, 15)
            st.session_state.problem_text = f"{st.session_state.num1} + {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 + st.session_state.num2
        elif mode == "Restes":
            if st.session_state.diff == "Difícil":
                st.session_state.num1 = random.randint(100, 500)
                st.session_state.num2 = random.randint(50, st.session_state.num1)
            elif st.session_state.diff == "Normal":
                st.session_state.num1 = random.randint(20, 100)
                st.session_state.num2 = random.randint(1, st.session_state.num1)
            else:
                st.session_state.num1 = random.randint(5, 20)
                st.session_state.num2 = random.randint(1, st.session_state.num1)
            st.session_state.problem_text = f"{st.session_state.num1} - {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 - st.session_state.num2
        elif mode == "Multiplicació":
            if st.session_state.diff == "Fàcil":
                st.session_state.num1, st.session_state.num2 = random.randint(1, 5), random.randint(1, 10)
            elif st.session_state.diff == "Normal":
                st.session_state.num1, st.session_state.num2 = random.randint(2, 10), random.randint(2, 10)
            else: # Difícil
                st.session_state.num1, st.session_state.num2 = random.randint(2, 15), random.randint(11, 25)
            st.session_state.problem_text = f"{st.session_state.num1} x {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 * st.session_state.num2
    elif st.session_state.current_block == "Innovamat":
        types = ["Amics", "Descompon", "Dobles", "Sèries", "Piràmide"]
        st.session_state.innovamat_type = random.choice(types)
        if st.session_state.innovamat_type == "Amics":
            target = random.choice([10, 20, 100, 1000] if st.session_state.diff == "Difícil" else [10, 20, 100])
            n1 = random.randint(1, target - 1)
            st.session_state.problem_text = f"{n1} + ? = {target}"
            st.session_state.correct_answer = target - n1
        elif st.session_state.innovamat_type == "Descompon":
            if st.session_state.diff == "Difícil":
                target = random.randint(100, 999)
                base = (target // 100) * 100
                st.session_state.problem_text = f"{target} = {base} + ?"
            else:
                target = random.randint(low + 10, high + 10)
                base = (target // 10) * 10
                st.session_state.problem_text = f"{target} = {base} + ?"
            st.session_state.correct_answer = target - base
        elif st.session_state.innovamat_type == "Dobles":
            type_dm = random.choice(["Doble", "Meitat"])
            if st.session_state.diff == "Difícil":
                n = random.randint(25, 150) if type_dm == "Doble" else random.randint(20, 200) * 2
            else:
                n = random.randint(1, 20) if type_dm == "Doble" else random.randint(1, 20) * 2
            st.session_state.problem_text = f"{type_dm.upper()} DE {n}"
            st.session_state.correct_answer = n * 2 if type_dm == "Doble" else n // 2
        elif st.session_state.innovamat_type == "Sèries":
            start = random.randint(1, 50)
            step = random.choice([-15, -7, 12, 15, 25]) if st.session_state.diff == "Difícil" else random.randint(2, 10)
            n1, n2, n3 = start, start + step, start + 2*step
            st.session_state.problem_text = f"{n1}, {n2}, {n3}, ?"
            st.session_state.correct_answer = n3 + step
        elif st.session_state.innovamat_type == "Piràmide":
            n1, n2 = (random.randint(20, 100), random.randint(20, 100)) if st.session_state.diff == "Difícil" else (random.randint(1, 20), random.randint(1, 20))
            st.session_state.problem_text = f"{n1} | {n2} -> ?"
            st.session_state.correct_answer = n1 + n2
    elif st.session_state.current_block == "Lectura":
        words = LECTURA_WORDS.get(st.session_state.diff, LECTURA_WORDS["Fàcil"])
        st.session_state.reading_word = random.choice(words)

# --- RENDER HOME ---
if st.session_state.current_block == "Home":
    col_img, col_title = st.columns([0.5, 3.5])
    with col_img:
        if Path("mascot.png").exists():
            st.image("mascot.png", width=80)
    with col_title:
        st.markdown("<h1 style='text-align:left; font-family:Bungee; font-size:1.8rem; color:#FF6B6B; margin-bottom:0; line-height:1.2;'>AVENTURA MATEMÀTICA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:left; font-size:1rem; margin-bottom:1rem;'>Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='mode-card card-mates'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:3rem; margin:0;'>🧮</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#FF6B6B; font-family:Bungee;'>MATES</h2>", unsafe_allow_html=True)
        if st.button("JUGAR! 🎮", key="btn_mates", use_container_width=True):
            st.session_state.current_block = "Mates"; get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='mode-card card-innovamat'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:3rem; margin:0;'>💡</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#F7D716; font-family:Bungee;'>INNOVAMAT</h2>", unsafe_allow_html=True)
        if st.button("EXPLORAR! 🔍", key="btn_innovamat", use_container_width=True):
            st.session_state.current_block = "Innovamat"; get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='mode-card' style='border-color:#4BCffa;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:3rem; margin:0;'>📖</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#4BCffa; font-family:Bungee;'>LECTURA</h2>", unsafe_allow_html=True)
        if st.button("LLEGIR! 📚", key="btn_lectura", use_container_width=True):
            st.session_state.current_block = "Lectura"
            st.session_state.reading_pos = 0; st.session_state.rival_pos = 0
            get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- RENDER MATES / INNOVAMAT ---
elif st.session_state.current_block in ["Mates", "Innovamat"]:
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:#FF6B6B; font-family:Bungee;'>MENU</h1>", unsafe_allow_html=True)
        if st.button("🏠 INICI", use_container_width=True):
            st.session_state.current_block = "Home"; safe_rerun()
        if st.session_state.current_block == "Mates":
            st.markdown("<p style='font-weight:700;'>🧮 OPERACIÓ</p>", unsafe_allow_html=True)
            if st.button("SUMA", use_container_width=True): st.session_state.mode = "Sumes"; get_new_problem(); safe_rerun()
            if st.button("RESTA", use_container_width=True): st.session_state.mode = "Restes"; get_new_problem(); safe_rerun()
            if st.button("MULTIPLICACIÓ", use_container_width=True): st.session_state.mode = "Multiplicació"; get_new_problem(); safe_rerun()
        st.markdown("<p style='font-weight:700;'>📈 NIVELL</p>", unsafe_allow_html=True)
        if st.button("FÀCIL", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        if st.button("NORMAL", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        if st.button("DIFÍCIL", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    st.markdown("<div class='mobile-marker'></div>", unsafe_allow_html=True)
    with st.container():
        if st.button("🏠 INICI", key="m_home_full", use_container_width=True):
            st.session_state.current_block = "Home"; safe_rerun()
        if st.session_state.current_block == "Mates":
            st.markdown("<p style='text-align:center; font-weight:700; margin-top:5px; margin-bottom:2px; font-size:0.8rem;'>OPERACIÓ</p>", unsafe_allow_html=True)
            op_cols = st.columns(3)
            with op_cols[0]:
                if st.button("SUMA", key="m_suma", use_container_width=True):
                    st.session_state.mode = "Sumes"; get_new_problem(); safe_rerun()
            with op_cols[1]:
                if st.button("RESTA", key="m_resta", use_container_width=True):
                    st.session_state.mode = "Restes"; get_new_problem(); safe_rerun()
            with op_cols[2]:
                if st.button("MULT", key="m_mult", use_container_width=True):
                    st.session_state.mode = "Multiplicació"; get_new_problem(); safe_rerun()
        st.markdown("<p style='text-align:center; font-weight:700; margin-top:5px; margin-bottom:2px; font-size:0.8rem;'>DIFICULTAT</p>", unsafe_allow_html=True)
        d_cols = st.columns(3)
        with d_cols[0]:
            if st.button("FÀCIL", key="m_facil", use_container_width=True):
                st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        with d_cols[1]:
            if st.button("NORMAL", key="m_normal", use_container_width=True):
                st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        with d_cols[2]:
            if st.button("DIFÍCIL", key="m_dificil", use_container_width=True):
                st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    title = "MATES" if st.session_state.current_block == "Mates" else "INNOVAMAT"
    st.markdown(f"<h2 style='color:#FF6B6B; font-family:Bungee;'>{title} • {st.session_state.diff.upper()}</h2>", unsafe_allow_html=True)
    border = "#FF6B6B" if st.session_state.current_block == "Mates" else "#F7D716"
    st.markdown(f"<div class='problem-box' style='border-color:{border};'>{st.session_state.problem_text}</div>", unsafe_allow_html=True)
    user_input = st.number_input("Resultat?", step=1, value=None, format="%d", label_visibility="collapsed", key=f"input_{st.session_state.input_key}")
    submit = st.button("COMPROVAR! 🚀", use_container_width=True)
    st.markdown(f"### ⭐ PUNTS: {st.session_state.score}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submit and user_input is not None:
        st.session_state.input_key += 1
        if user_input == st.session_state.correct_answer:
            st.session_state.score += 1
            st.session_state.last_status = "correct"
            get_new_problem()
        else:
            st.session_state.last_status = "incorrect"
        safe_rerun()

# --- RENDER LECTURA ---
elif st.session_state.current_block == "Lectura":
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:#4BCffa; font-family:Bungee;'>LECTURA</h1>", unsafe_allow_html=True)
        if st.button("🏠 INICI", use_container_width=True):
            st.session_state.current_block = "Home"; safe_rerun()
        st.markdown("<p style='font-weight:700;'>📈 NIVELL</p>", unsafe_allow_html=True)
        if st.button("FÀCIL", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        if st.button("NORMAL", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        if st.button("DIFÍCIL", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    st.markdown("<div class='main-card' style='border-color:#4BCffa;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#4BCffa; font-family:Bungee;'>CURSA DE PARAULES • {st.session_state.diff.upper()}</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:left; margin-bottom:2px; font-size:0.8rem;'>TU (Blau)</p>", unsafe_allow_html=True)
    st.markdown(f'''<div class="race-track"><div class="car" style="left: {st.session_state.reading_pos}%;">🏎️</div></div>''', unsafe_allow_html=True)
    st.markdown("<p style='text-align:left; margin-bottom:2px; font-size:0.8rem;'>RIVAL (Vermell)</p>", unsafe_allow_html=True)
    st.markdown(f'''<div class="race-track" style="background:#555;"><div class="car" style="left: {st.session_state.rival_pos}%; filter: hue-rotate(140deg);">🏎️</div></div>''', unsafe_allow_html=True)

    st.markdown(f"<div class='problem-box' style='border-color:#4BCffa; font-size:4rem;'>{st.session_state.reading_word}</div>", unsafe_allow_html=True)
    
    if st.button("LLEGIT! ✅", use_container_width=True):
        st.session_state.reading_pos += 8
        st.session_state.rival_pos += random.randint(3, 7)
        if st.session_state.reading_pos >= 90:
            st.session_state.last_status = "correct"
            st.session_state.reading_pos = 0; st.session_state.rival_pos = 0
            st.session_state.score += 5
        elif st.session_state.rival_pos >= 90:
            st.session_state.last_status = "incorrect"
            st.session_state.reading_pos = 0; st.session_state.rival_pos = 0
        get_new_problem(); safe_rerun()
    
    st.markdown(f"### ⭐ PUNTS: {st.session_state.score}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_status:
    if st.session_state.last_status == "correct":
        selected_gif = random.choice(CELEBRATION_GIFS)
        selected_msg = random.choice(CELEBRATION_MESSAGES)
        st.markdown(f'''<div class="gif-overlay"><img src="{selected_gif}"><h1 style="font-family:'Bungee'; color:#FF6B6B; font-size:4rem; margin-top:20px; text-shadow: 3px 3px 0px white;">{selected_msg} 🎉</h1></div>''', unsafe_allow_html=True)
    else:
        st.markdown('<div class="gif-overlay" style="background:rgba(244, 67, 54, 0.9);"><h1 style="font-family:\'Bungee\'; color:white; font-size:4rem;">PROVA DE NOU! 🔄</h1></div>', unsafe_allow_html=True)
    st.session_state.last_status = None
    time.sleep(2)
    safe_rerun()
