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
        padding: 2.5rem;
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
    div[data-testid="stNumberInput"] button {
        height: 160px !important;
        border-radius: 0 35px 35px 0 !important;
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

    /* Botons mobile controls sempre petits */
    .mobile-controls-marker + div div.stButton > button {
        font-size: 1.2rem !important;
        height: 45px !important;
        min-height: 45px !important;
        box-shadow: 0 4px 0px #D63031 !important;
        margin: 2px auto !important;
        text-transform: none !important;
    }

    @media (min-width: 768px) {
        div[data-testid="stVerticalBlock"]:has(#mobile-trigger) {
            display: none !important;
        }
    }




    /* MOBILE: amaga sidebar, mostra controls inline */
    @media (max-width: 767px) {
        section[data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            min-width: 0 !important;
        }
        button[data-testid="stSidebarCollapseButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Collapse sidebar"],
        button[aria-label="Open sidebar"] {
            display: none !important;
        }
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
        .problem-box {
            font-size: 3rem !important;
            height: 120px !important;
        }
        div[data-testid="stNumberInput"],
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInput"] div[data-baseweb="input"] {
            height: 110px !important;
        }
        div[data-testid="stNumberInput"] div[data-baseweb="input"] input {
            font-size: 3rem !important;
            height: 110px !important;
        }
        div[data-testid="stNumberInput"] button {
            height: 110px !important;
        }
        div.stButton > button {
            font-size: 1.6rem !important;
            height: 70px !important;
        }
        .main-card {
            padding: 1.5rem !important;
            border-radius: 30px !important;
            width: 95% !important;
            max-width: 95vw !important;
        }
        div.stButton > button {
            font-size: 1.2rem !important;
            height: 60px !important;
            padding: 0 5px !important;
        }
    }

    
    [data-testid="stSidebarUserContent"] {
        padding-top: 0.1rem !important;
        padding-bottom: 0.1rem !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebarUserContent"] > div {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.1rem !important;
        margin: 0 0 2px 0 !important;
        padding: 0 !important;
        line-height: 1.1 !important;
    }
    [data-testid="stSidebar"] p {
        font-size: 0.75rem !important;
        margin: 2px 0 1px 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 2px 0 !important;
        padding: 0 !important;
    }
    [data-testid="stSidebar"] button {
        font-family: 'Bungee', cursive !important;
        font-size: 0.85rem !important;
        height: 32px !important;
        min-height: 32px !important;
        margin-bottom: 2px !important;
        border-radius: 8px !important;
        background: white !important;
        border: 2px solid #FF6B6B !important;
        color: #FF6B6B !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    [data-testid="stSidebar"] div.stButton {
        margin: 0 0 2px 0 !important;
    }

    .overlay {
        position: fixed;
        top: 40%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 50px 80px;
        border-radius: 50px;
        font-family: 'Bungee', cursive;
        font-size: 4rem;
        z-index: 9999;
        text-align: center;
        border: 15px solid white;
        box-shadow: 0 30px 100px rgba(0,0,0,0.5);
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
if 'diff' not in st.session_state: st.session_state.diff = "Normal"
if 'innovamat_type' not in st.session_state: st.session_state.innovamat_type = "Amics"
if 'problem_text' not in st.session_state: st.session_state.problem_text = ""
if 'correct_answer' not in st.session_state: st.session_state.correct_answer = 0
if 'input_key' not in st.session_state: st.session_state.input_key = 0

def get_new_problem():
    ranges = {"Fàcil": (1, 10), "Normal": (1, 20), "Difícil": (1, 50)}
    low, high = ranges.get(st.session_state.diff, (1, 10))
    
    if st.session_state.current_block == "Mates":
        mode = st.session_state.mode
        if mode == "Sumes":
            st.session_state.num1, st.session_state.num2 = random.randint(low, high), random.randint(low, high)
            st.session_state.problem_text = f"{st.session_state.num1} + {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 + st.session_state.num2
        elif mode == "Restes":
            st.session_state.num1 = random.randint(low + 5, high + 5)
            st.session_state.num2 = random.randint(1, st.session_state.num1)
            st.session_state.problem_text = f"{st.session_state.num1} - {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 - st.session_state.num2
        elif mode == "Multiplicació":
            m_high = 10 if st.session_state.diff != "Difícil" else 12
            st.session_state.num1, st.session_state.num2 = random.randint(1, m_high), random.randint(1, m_high)
            st.session_state.problem_text = f"{st.session_state.num1} x {st.session_state.num2}"
            st.session_state.correct_answer = st.session_state.num1 * st.session_state.num2
            
    elif st.session_state.current_block == "Innovamat":
        types = ["Amics", "Descompon", "Dobles", "Sèries"]
        st.session_state.innovamat_type = random.choice(types)
        
        if st.session_state.innovamat_type == "Amics":
            target = random.choice([10, 20, 100] if st.session_state.diff == "Difícil" else [10, 20])
            n1 = random.randint(1, target - 1)
            st.session_state.problem_text = f"{n1} + ? = {target}"
            st.session_state.correct_answer = target - n1
            
        elif st.session_state.innovamat_type == "Descompon":
            target = random.randint(low + 10, high + 10)
            base = (target // 10) * 10
            st.session_state.problem_text = f"{target} = {base} + ?"
            st.session_state.correct_answer = target - base
            
        elif st.session_state.innovamat_type == "Dobles": # Dobles o Meitats
            type_dm = random.choice(["Doble", "Meitat"])
            if type_dm == "Doble":
                n = random.randint(1, 12)
                st.session_state.problem_text = f"EL DOBLE DE {n}"
                st.session_state.correct_answer = n * 2
            else:
                n = random.randint(1, 10) * 2
                st.session_state.problem_text = f"LA MEITAT DE {n}"
                st.session_state.correct_answer = n // 2
                
        elif st.session_state.innovamat_type == "Sèries":
            start = random.randint(1, 10)
            step = random.randint(2, 5)
            n1, n2, n3 = start, start + step, start + 2*step
            st.session_state.problem_text = f"{n1}, {n2}, {n3}, ?"
            st.session_state.correct_answer = n3 + step

# --- RENDER HOME ---
if st.session_state.current_block == "Home":
    col_img, col_title = st.columns([1, 3])
    with col_img:
        if Path("mascot.png").exists():
            st.image("mascot.png", use_container_width=True)
    with col_title:
        st.markdown("<h1 style='text-align:left; font-family:Bungee; font-size:3.5rem; color:#FF6B6B; margin-bottom:0; line-height:1;'>AVENTURA MATEMÀTICA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:left; font-size:1.5rem; margin-bottom:1rem;'>Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='mode-card card-mates'><h2 style='font-family:Bungee; color:#FF6B6B; font-size:2.5rem;'>MATES</h2><p style='font-size:1.2rem;'>Sumes, restes i multiplicacions</p></div>", unsafe_allow_html=True)
        if st.button("JUGAR MATES", use_container_width=True):
            st.session_state.current_block = "Mates"; get_new_problem(); safe_rerun()
    with col2:
        st.markdown("<div class='mode-card card-innovamat'><h2 style='font-family:Bungee; color:#F7D716; font-size:2.5rem;'>INNOVAMAT</h2><p style='font-size:1.2rem;'>Lògica, descomposició i sèries</p></div>", unsafe_allow_html=True)
        if st.button("JUGAR INNOVAMAT", use_container_width=True):
            st.session_state.current_block = "Innovamat"; get_new_problem(); safe_rerun()


# --- RENDER GAME ---
else:
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
    # Controls mòbil (visibles només en mòbil via CSS)
    with st.container():
        st.markdown("<span id='mobile-trigger'></span>", unsafe_allow_html=True)
        # Botó Inici

        if st.button("🏠 INICI", key="m_home_full", use_container_width=True):
            st.session_state.current_block = "Home"; safe_rerun()
            
        # Bloc 1: Operacions (si és Mates)
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
        
        # Bloc 2: Dificultat
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
    
    # Problem Box
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
            st.balloons()
            get_new_problem()
        else:
            st.session_state.last_status = "incorrect"
        safe_rerun()

    if st.session_state.last_status:
        msg, color = ("MOLT BÉ! 🎉", "#4CAF50") if st.session_state.last_status == "correct" else ("PROVA DE NOU! 🔄", "#F44336")
        st.markdown(f'<div class="overlay" style="background:{color}; color:white;">{msg}</div>', unsafe_allow_html=True)
        st.session_state.last_status = None
        time.sleep(1)
        safe_rerun()
