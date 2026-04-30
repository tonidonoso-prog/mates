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
    "Fàcil": [
        "CASA", "GAT", "SOL", "PAPA", "MAMA", "PA", "MÀ", "SOPA", "BOLA", "RODA", "NEN", "NENA", "GOS", "LLIT", "PEIX", "MAR", "CEL", "POC", "MOLT", "BONA", "DALT", "BAIX", "LLUM", "FOC", "DIU", "VEU", "RIU", "PIS", "TREM", "COSA", "LLUNA", "PILA", "TAULA", "CUP", "DIT", "NAS", "ULL", "CAP", "COR", "FER", "DIR", "SER", "TOT", "NOM", "OU", "LLET", "PAU", "MIR", "VOL", "FIL", "MUL", "PEL", "XIC"
    ],
    "Normal": [
        "FINESTRA", "ESTRELLA", "SABATA", "PILOTA", "GIRAFA", "GAT I GOS", "CASA GRAN", "UN PARE", "LA MARE", "SOL I LLUNA", "ELEFANT", "MOTXILLA", "CARAMEL", "FORQUILLA", "CULLERA", "ESCRIPTORI", "BICICLETA", "PANTALONS", "SAMARRETA", "CADIRA BLAVA", "PORTA OBERTA", "FINESTRA TANCADA", "MENJAR SA", "GELAT DOLÇ", "PINZELL NOU", "LLIBRE VELL", "COTXE RÀPID", "BOSC VERD", "MAR BLAVA", "VENT FORT", "PLUJA FREDA", "NEU BLANCA", "ESTIU CALENT", "HIVERN FRED", "TARDOR GROGA", "PRIMAVERA BONA"
    ],
    "Difícil": [
        "ESQUIROL VELOÇ", "ORDINADOR VELL", "LLIBRETA NOVA", "ESTRABÒS DIVERTIT", "FRIGORÍFIC BLANC", "CONEIXEMENT PROFUND", "BOLÍGRAF BLAU", "MATEMÀTIQUES FÀCILS", "ENCICLOPÈDIA GRAN", "TRANSFORMACIÓ MÀGICA", "RECONEIXEMENT RÀPID", "EXCURSIÓ AL MUNTANYA", "VIATGE INTERSTEL·LAR", "PARAULA COMPLICADA", "BIBLIOTECA PÚBLICA", "IMAGINACIÓ INFINITA", "RESPONSABILITAT GRAN", "EXPERIMENT CIENTÍFIC", "INSTRUMENT MUSICAL", "FOTOGRAFIA BONICA", "ARQUITECTURA MODERNA", "ASTRONAUTA VALENT", "PALEONTÒLEG FAMÓS", "INVESTIGACIÓ SECRETA", "ESPECTACLE INCREÏBLE"
    ]
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

    .card-mates { border-color: #FF6B6B; }
    .card-innovamat { border-color: #F7D716; }

    .main-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 40px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(31, 38, 135, 0.25);
        text-align: center;
        width: 100%;
        max-width: 850px;
        margin: auto;
    }

    .problem-box {
        font-family: 'Bungee', cursive !important;
        font-size: 4.5rem !important;
        min-height: 150px !important;
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

    div[data-testid="stNumberInput"] div[data-baseweb="input"] input {
        height: 120px !important;
        font-family: 'Bungee', cursive !important;
        font-size: 4rem !important;
        text-align: center !important;
    }

    div.stButton > button {
        background: linear-gradient(180deg, #FF6B6B 0%, #EE5253 100%) !important;
        color: white !important;
        font-family: 'Bungee', cursive !important;
        font-size: 2rem !important;
        height: 80px !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 0px #D63031 !important;
    }

    /* Amagar controls mòbil al PC */
    @media (min-width: 768px) {
        div[data-testid="stVerticalBlock"]:has(> div .mobile-marker) {
            display: none !important;
        }
    }

    @media (max-width: 767px) {
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .main-card { width: 98% !important; padding: 1rem !important; }
        .problem-box { font-size: 1.8rem !important; min-height: 80px !important; }
        div[data-testid="stNumberInput"] div[data-baseweb="input"] input {
            font-size: 2.2rem !important;
            height: 80px !important;
        }
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

    .race-track {
        background: #333;
        height: 80px;
        width: 100%;
        border-radius: 20px;
        position: relative;
        margin: 10px 0;
        border: 4px dashed white;
        overflow: hidden;
    }
    .car { font-size: 2rem; position: absolute; transition: left 0.5s ease; top: 50%; transform: translateY(-50%); }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- HEADER GLOBAL ---
def render_header():
    col_img, col_title = st.columns([0.5, 3.5])
    with col_img:
        if Path("mascot.png").exists():
            st.image("mascot.png", width=60)
    with col_title:
        st.markdown("<h1 style='text-align:left; font-family:Bungee; font-size:1.5rem; color:#FF6B6B; margin-bottom:0; line-height:1.2;'>AVENTURA MATEMÀTICA</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)

# Helper for compatibility
def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

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
if 'word_start_time' not in st.session_state: st.session_state.word_start_time = time.time()
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
                target = random.randint(100, 999); base = (target // 100) * 100
            else:
                target = random.randint(low + 10, high + 10); base = (target // 10) * 10
            st.session_state.problem_text = f"{target} = {base} + ?"
            st.session_state.correct_answer = target - base
        elif st.session_state.innovamat_type == "Dobles":
            type_dm = "Doble" if st.session_state.diff == "Fàcil" else random.choice(["Doble", "Meitat"])
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
        st.session_state.word_start_time = time.time()

# --- RENDER HOME ---
if st.session_state.current_block == "Home":
    render_header()
    st.markdown("<p style='text-align:left; font-size:1rem; margin-bottom:1rem;'>Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='mode-card card-mates'><p style='font-size:3rem; margin:0;'>🧮</p><h2 style='color:#FF6B6B; font-family:Bungee;'>MATES</h2>", unsafe_allow_html=True)
        if st.button("JUGAR! 🎮", key="btn_mates", use_container_width=True):
            st.session_state.current_block = "Mates"; get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='mode-card card-innovamat'><p style='font-size:3rem; margin:0;'>💡</p><h2 style='color:#F7D716; font-family:Bungee;'>INNOVAMAT</h2>", unsafe_allow_html=True)
        if st.button("EXPLORAR! 🔍", key="btn_innovamat", use_container_width=True):
            st.session_state.current_block = "Innovamat"; get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='mode-card' style='border-color:#4BCffa;'><p style='font-size:3rem; margin:0;'>📖</p><h2 style='color:#4BCffa; font-family:Bungee;'>LECTURA</h2>", unsafe_allow_html=True)
        if st.button("LLEGIR! 📚", key="btn_lectura", use_container_width=True):
            st.session_state.current_block = "Lectura"; st.session_state.reading_pos = 0; st.session_state.rival_pos = 0; get_new_problem(); safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- RENDER MATES / INNOVAMAT ---
elif st.session_state.current_block in ["Mates", "Innovamat"]:
    render_header()
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:#FF6B6B; font-family:Bungee;'>MENU</h1>", unsafe_allow_html=True)
        if st.button("🏠 INICI", use_container_width=True): st.session_state.current_block = "Home"; safe_rerun()
        if st.session_state.current_block == "Mates":
            st.markdown("<p style='font-weight:700;'>🧮 OPERACIÓ</p>", unsafe_allow_html=True)
            if st.button("SUMA", use_container_width=True): st.session_state.mode = "Sumes"; get_new_problem(); safe_rerun()
            if st.button("RESTA", use_container_width=True): st.session_state.mode = "Restes"; get_new_problem(); safe_rerun()
            if st.button("MULTIPLICACIÓ", use_container_width=True): st.session_state.mode = "Multiplicació"; get_new_problem(); safe_rerun()
        st.markdown("<p style='font-weight:700;'>📈 NIVELL</p>", unsafe_allow_html=True)
        if st.button("FÀCIL", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        if st.button("NORMAL", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        if st.button("DIFÍCIL", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    with st.container():
        st.markdown("<div class='mobile-marker'></div>", unsafe_allow_html=True)
        if st.button("🏠 INICI", key="m_home_full", use_container_width=True): st.session_state.current_block = "Home"; safe_rerun()
        if st.session_state.current_block == "Mates":
            st.markdown("<p style='text-align:center; font-weight:700; font-size:0.8rem;'>OPERACIÓ</p>", unsafe_allow_html=True)
            op_cols = st.columns(3)
            with op_cols[0]:
                if st.button("SUMA", key="m_suma", use_container_width=True): st.session_state.mode = "Sumes"; get_new_problem(); safe_rerun()
            with op_cols[1]:
                if st.button("RESTA", key="m_resta", use_container_width=True): st.session_state.mode = "Restes"; get_new_problem(); safe_rerun()
            with op_cols[2]:
                if st.button("MULT", key="m_mult", use_container_width=True): st.session_state.mode = "Multiplicació"; get_new_problem(); safe_rerun()
        st.markdown("<p style='text-align:center; font-weight:700; font-size:0.8rem;'>DIFICULTAT</p>", unsafe_allow_html=True)
        d_cols = st.columns(3)
        with d_cols[0]:
            if st.button("FÀCIL", key="m_facil", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        with d_cols[1]:
            if st.button("NORMAL", key="m_normal", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        with d_cols[2]:
            if st.button("DIFÍCIL", key="m_dificil", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

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
            st.session_state.score += 1; st.session_state.last_status = "correct"; get_new_problem()
        else: st.session_state.last_status = "incorrect"
        safe_rerun()

# --- RENDER LECTURA ---
elif st.session_state.current_block == "Lectura":
    render_header()
    with st.sidebar:
        st.markdown("<h1 style='text-align:center; color:#4BCffa; font-family:Bungee;'>LECTURA</h1>", unsafe_allow_html=True)
        if st.button("🏠 INICI", use_container_width=True): st.session_state.current_block = "Home"; safe_rerun()
        st.markdown("<p style='font-weight:700;'>📈 NIVELL</p>", unsafe_allow_html=True)
        if st.button("FÀCIL", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        if st.button("NORMAL", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        if st.button("DIFÍCIL", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    with st.container():
        st.markdown("<div class='mobile-marker'></div>", unsafe_allow_html=True)
        if st.button("🏠 INICI", key="m_home_lectura", use_container_width=True): st.session_state.current_block = "Home"; safe_rerun()
        st.markdown("<p style='text-align:center; font-weight:700; font-size:0.8rem;'>DIFICULTAT</p>", unsafe_allow_html=True)
        ld_cols = st.columns(3)
        with ld_cols[0]:
            if st.button("FÀCIL", key="ml_facil", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        with ld_cols[1]:
            if st.button("NORMAL", key="ml_normal", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        with ld_cols[2]:
            if st.button("DIFÍCIL", key="ml_dificil", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    st.markdown("<div class='main-card' style='border-color:#4BCffa;'>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:#4BCffa; font-family:Bungee;'>CURSA DE PARAULES • {st.session_state.diff.upper()}</h2>", unsafe_allow_html=True)
    st.markdown(f'''<div class="race-track"><div class="car" style="left: {st.session_state.reading_pos}%; filter: hue-rotate(90deg);">🏎️</div></div>''', unsafe_allow_html=True)
    st.markdown(f'''<div class="race-track" style="background:#555;"><div class="car" style="left: {st.session_state.rival_pos}%;">🏎️</div></div>''', unsafe_allow_html=True)
    st.markdown(f"<div class='problem-box' style='border-color:#4BCffa; font-size:3.5rem;'>{st.session_state.reading_word}</div>", unsafe_allow_html=True)
    if st.button("LLEGIT! ✅", use_container_width=True):
        elapsed = time.time() - st.session_state.word_start_time
        rival_speed_map = {"Fàcil": 1.5, "Normal": 4.5, "Difícil": 8.0}
        st.session_state.reading_pos += 10; st.session_state.rival_pos += elapsed * rival_speed_map.get(st.session_state.diff, 3.0)
        if st.session_state.reading_pos >= 90:
            st.session_state.last_status = "correct"; st.session_state.reading_pos = 0; st.session_state.rival_pos = 0; st.session_state.score += 5
        elif st.session_state.rival_pos >= 90:
            st.session_state.last_status = "incorrect"; st.session_state.reading_pos = 0; st.session_state.rival_pos = 0
        get_new_problem(); safe_rerun()
    st.markdown(f"### ⭐ PUNTS: {st.session_state.score}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_status:
    if st.session_state.last_status == "correct":
        selected_gif, selected_msg = random.choice(CELEBRATION_GIFS), random.choice(CELEBRATION_MESSAGES)
        st.markdown(f'''<div class="gif-overlay"><img src="{selected_gif}"><h1 style="font-family:'Bungee'; color:#FF6B6B; font-size:4rem; margin-top:20px; text-shadow: 3px 3px 0px white;">{selected_msg} 🎉</h1></div>''', unsafe_allow_html=True)
    else: st.markdown('<div class="gif-overlay" style="background:rgba(244, 67, 54, 0.9);"><h1 style="font-family:\'Bungee\'; color:white; font-size:4rem;">PROVA DE NOU! 🔄</h1></div>', unsafe_allow_html=True)
    st.session_state.last_status = None; time.sleep(2); safe_rerun()
