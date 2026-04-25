import streamlit as st
import random
import time
import base64
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Aventura Matemàtica",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Helper to load image as base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    '''
    # st.markdown(page_bg_img, unsafe_allow_html=True) # Optional background

# Custom CSS for Premium Child-Friendly UI
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

    /* Main Container with Glassmorphism */
    .main-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 2.5rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Title Styling */
    .title-text {
        font-family: 'Bungee', cursive;
        color: #FF6B6B;
        font-size: 3.5rem;
        text-shadow: 3px 3px 0px #4ECDC4;
        margin-bottom: 0.5rem;
    }

    /* Problem Text */
    .problem-display {
        font-family: 'Bungee', cursive;
        font-size: 6rem;
        font-weight: 700;
        color: #2D3436;
        margin: 1rem 0;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 25px;
        display: inline-block;
        min-width: 350px;
        border: 5px dashed #FF6B6B;
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    /* Score Badge */
    .score-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 2rem;
    }

    .score-badge {
        background: white;
        padding: 10px 25px;
        border-radius: 50px;
        font-size: 1.8rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        gap: 10px;
        border: 3px solid #FFD93D;
    }

    /* Input Field Styling */
    div[data-baseweb="input"] {
        border-radius: 20px !important;
        border: 4px solid #4ECDC4 !important;
        font-size: 2.5rem !important;
        background: white !important;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53) !important;
        color: white !important;
        border-radius: 20px !important;
        padding: 1rem 2rem !important;
        font-size: 1.8rem !important;
        font-family: 'Bungee', cursive !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        width: 100% !important;
        height: 80px !important;
        box-shadow: 0 8px 0px #D63031 !important;
        margin-top: 10px !important;
    }

    .stButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 13px 0px #D63031 !important;
    }

    .stButton > button:active {
        transform: translateY(2px);
        box-shadow: 0 4px 0px #D63031 !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #F7F9FB;
    }

    .sidebar-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Overlay Messages */
    .overlay {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 40px 60px;
        border-radius: 40px;
        font-family: 'Bungee', cursive;
        font-size: 4rem;
        z-index: 9999;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: pop-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .overlay-success {
        background: #4CAF50;
        color: white;
        border: 8px solid #FFFFFF;
    }

    .overlay-error {
        background: #F44336;
        color: white;
        border: 8px solid #FFFFFF;
    }

    @keyframes pop-in {
        0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Session State Initialization
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'num1' not in st.session_state:
    st.session_state.num1 = 0
if 'num2' not in st.session_state:
    st.session_state.num2 = 0
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Sumes"
if 'last_status' not in st.session_state:
    st.session_state.last_status = None

def get_new_problem(mode):
    if mode == "Sumes":
        st.session_state.num1 = random.randint(1, 20)
        st.session_state.num2 = random.randint(1, 20)
    elif mode == "Restes":
        st.session_state.num1 = random.randint(5, 20)
        st.session_state.num2 = random.randint(1, st.session_state.num1)
    elif mode == "Multiplicació":
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

# Sidebar
st.sidebar.markdown("<h1 style='text-align: center; color: #FF6B6B; font-family: Bungee;'>🎮 JOC</h1>", unsafe_allow_html=True)

# Mascot in Sidebar
if Path("mascot.png").exists():
    st.sidebar.image("mascot.png", use_container_width=True)

with st.sidebar:
    st.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    mode = st.radio(
        "Tria operació:",
        ["Sumes", "Restes", "Multiplicació"],
        index=0
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Detect mode change
if mode != st.session_state.current_mode:
    st.session_state.current_mode = mode
    get_new_problem(mode)
    st.session_state.last_status = None

# Initialize first problem if numbers are 0
if st.session_state.num1 == 0 and st.session_state.num2 == 0:
    get_new_problem(mode)

# UI Layout
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.markdown("<h1 class='title-text'>🌟 AVENTURA 🌟</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #4ECDC4; font-size: 1.5rem; font-weight: 700; margin-top:-15px;'>MATEMÀTICA</p>", unsafe_allow_html=True)

# Score
st.markdown(f"""
<div class='score-container'>
    <div class='score-badge'>
        <span style='font-size: 2.5rem;'>⭐</span> 
        <span>{st.session_state.score} PUNTS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Problem Area
symbol = "+" if mode == "Sumes" else "-" if mode == "Restes" else "×"
st.markdown(f"""
    <div class='problem-display'>
        {st.session_state.num1} {symbol} {st.session_state.num2}
    </div>
""", unsafe_allow_html=True)

# Form for Input
with st.form(key="answer_form", clear_on_submit=True):
    st.markdown("<p style='font-weight: 700; color: #2D3436; font-size: 1.5rem; margin-bottom: 5px;'>Quant és?</p>", unsafe_allow_html=True)
    user_input = st.number_input("", step=1, value=None, format="%d", label_visibility="collapsed")
    submit = st.form_submit_button("COMPROVAR! 🚀")

st.markdown("</div>", unsafe_allow_html=True) # End main-card

if submit:
    if user_input is not None:
        # Calculate correct answer
        if mode == "Sumes":
            correct = st.session_state.num1 + st.session_state.num2
        elif mode == "Restes":
            correct = st.session_state.num1 - st.session_state.num2
        else:
            correct = st.session_state.num1 * st.session_state.num2
        
        if user_input == correct:
            st.session_state.score += 1
            st.session_state.last_status = "correct"
            st.balloons()
            get_new_problem(mode)
        else:
            st.session_state.last_status = "incorrect"
        st.rerun()

# Feedback Overlay
if st.session_state.last_status == "correct":
    st.markdown('<div class="overlay overlay-success">MOLT BÉ! 🎉</div>', unsafe_allow_html=True)
    st.session_state.last_status = None
    time.sleep(1.5)
    st.rerun()
elif st.session_state.last_status == "incorrect":
    st.markdown('<div class="overlay overlay-error">TORNA-HO A PROVAR! 🔄</div>', unsafe_allow_html=True)
    st.session_state.last_status = None
    time.sleep(1.5)
    st.rerun()

# Sidebar footer
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reiniciar Punts"):
    st.session_state.score = 0
    get_new_problem(mode)
    st.session_state.last_status = None
    st.rerun()

st.sidebar.markdown(f"""
<div style='background: #FFF9E1; padding: 20px; border-radius: 20px; border: 2px solid #FFD93D;'>
    <p style='color: #FF6B6B; font-weight: 700; margin: 0; font-size: 1.1rem;'>Dificultat:</p>
    <ul style='color: #2D3436; font-size: 0.95rem; margin-top: 10px; padding-left: 20px;'>
        <li><b>Sumes:</b> Fins a 40</li>
        <li><b>Restes:</b> Sempre positives</li>
        <li><b>Taules:</b> 1 al 10</li>
    </ul>
</div>
""", unsafe_allow_html=True)
