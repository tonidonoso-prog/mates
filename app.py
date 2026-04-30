import streamlit as st
import random
import time
from pathlib import Path

# Page Config
st.set_page_config(page_title="Aventura Matemàtica", page_icon="🧮", layout="wide", initial_sidebar_state="expanded")

CELEBRATION_GIFS = ["https://i.giphy.com/osMIREQbo3s2c.gif", "https://i.giphy.com/BQAk13taTaKYw.gif", "https://i.giphy.com/8Do5PA5jPmTd3x8GI4.gif", "https://i.giphy.com/bCcxY1ADkAqfS.gif", "https://i.giphy.com/kHCc089grRFzSnVHvq.gif", "https://i.giphy.com/hDwYu8UEcUone.gif", "https://i.giphy.com/fCmnDUmpNYqnE2PidN.gif", "https://i.giphy.com/Z8wxB5I34Wl9Rx0ilC.gif", "https://i.giphy.com/bP9S3BMElQ5XAWQIR3.gif", "https://i.giphy.com/N5J5reSW1XkWKoaeij.gif", "https://i.giphy.com/TdfyKrN7HGTIY.gif", "https://i.giphy.com/VkUdMsK42kNgrPWuHd.gif", "https://i.giphy.com/kagE8uswvjrC2KanKI.gif", "https://i.giphy.com/IXB6mQUgOqWQM.gif", "https://i.giphy.com/XMvrleT9jksXm.gif", "https://i.giphy.com/IzBpqKzHLtfTa.gif", "https://i.giphy.com/hEIuLmpW9DmGA.gif", "https://i.giphy.com/HJQObm4T6xS2Q.gif", "https://i.giphy.com/0WQXGB5aOPLdBRFWyH.gif", "https://i.giphy.com/11sBLVxNs7v6WA.gif"]
LECTURA_WORDS = {
    "Fàcil": ["CASA", "GAT", "SOL", "PAPA", "MAMA", "PA", "MÀ", "SOPA", "BOLA", "RODA", "NEN", "NENA", "GOS", "LLIT", "PEIX", "MAR", "CEL", "POC", "MOLT", "BONA", "DALT", "BAIX", "LLUM", "FOC", "DIU", "VEU", "RIU", "PIS", "TREM", "COSA", "LLUNA", "PILA", "TAULA", "CUP", "DIT", "NAS", "ULL", "CAP", "COR", "FER", "DIR", "SER", "TOT", "NOM", "OU", "LLET", "PAU", "MIR", "VOL", "FIL", "MUL", "PEL", "XIC"],
    "Normal": ["FINESTRA", "ESTRELLA", "SABATA", "PILOTA", "GIRAFA", "GAT I GOS", "CASA GRAN", "UN PARE", "LA MARE", "SOL I LLUNA", "ELEFANT", "MOTXILLA", "CARAMEL", "FORQUILLA", "CULLERA", "ESCRIPTORI", "BICICLETA", "PANTALONS", "SAMARRETA", "CADIRA BLAVA", "PORTA OBERTA", "FINESTRA TANCADA", "MENJAR SA", "GELAT DOLÇ", "PINZELL NOU", "LLIBRE VELL", "COTXE RÀPID", "BOSC VERD", "MAR BLAVA", "VENT FORT", "PLUJA FREDA", "NEU BLANCA", "ESTIU CALENT", "HIVERN FRED", "TARDOR GROGA", "PRIMAVERA BONA"],
    "Difícil": ["ESQUIROL VELOÇ", "ORDINADOR VELL", "LLIBRETA NOVA", "ESTRABÒS DIVERTIT", "FRIGORÍFIC BLANC", "CONEIXEMENT PROFUND", "BOLÍGRAF BLAU", "MATEMÀTIQUES FÀCILS", "ENCICLOPÈDIA GRAN", "TRANSFORMACIÓ MÀGICA", "RECONEIXEMENT RÀPID", "EXCURSIÓ AL MUNTANYA", "VIATGE INTERSTEL·LAR", "PARAULA COMPLICADA", "BIBLIOTECA PÚBLICA", "IMAGINACIÓ INFINITA", "RESPONSABILITAT GRAN", "EXPERIMENT CIENTÍFIC", "INSTRUMENT MUSICAL", "FOTOGRAFIA BONICA", "ARQUITECTURA MODERNA", "ASTRONAUTA VALENT", "PALEONTÒLEG FAMÓS", "INVESTIGACIÓ SECRETA", "ESPECTACLE INCREÏBLE"]
}
CELEBRATION_MESSAGES = ["MOLT BÉ!", "FANTÀSTIC!", "QUIN NIVELL!", "IMPRESSIONANT!", "BRUTAL!", "GENIAL!", "SUPERBÉ!", "HO HAS CLAVAT!", "MOLT BONA FEINA!", "INCREÏBLE!", "CONTINUA AIXÍ!", "IMBATIBLE!", "QUINA PRECISIÓ!", "UN 10!", "HO HAS ACONSEGUIT!", "MÀGIC!", "ESPECTACULAR!", "MOLT BEN PENSAT!", "BRAVO!", "ÈXIT TOTAL!"]

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Bungee&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%); background-attachment: fixed; }
    .main-card { background: rgba(255, 255, 255, 0.9); border-radius: 30px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; width: 100%; max-width: 800px; margin: auto; }
    .problem-box { font-family: 'Bungee', cursive !important; font-size: 3.5rem; min-height: 120px; border-radius: 25px; background: white; border: 8px dashed #FF6B6B; display: flex; align-items: center; justify-content: center; margin: 15px auto; color: #2D3436; text-align: center; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] { background: white !important; border-radius: 25px !important; border: 8px solid #FF6B6B !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] input { height: 120px !important; font-family: 'Bungee', cursive !important; font-size: 3.5rem !important; text-align: center !important; }
    div.stButton > button { background: linear-gradient(180deg, #FF6B6B 0%, #EE5253 100%) !important; color: white !important; font-family: 'Bungee', cursive !important; font-size: 1.5rem !important; height: 60px !important; border-radius: 15px !important; box-shadow: 0 5px 0px #D63031 !important; border: none !important; }
    @media (min-width: 768px) { .mobile-only-section { display: none !important; } }
    @media (max-width: 767px) { section[data-testid="stSidebar"] { display: none !important; } .problem-box { font-size: 1.8rem !important; min-height: 80px !important; } }
    .race-track { background: #333; height: 60px; width: 100%; border-radius: 15px; position: relative; margin: 10px 0; border: 3px dashed white; overflow: hidden; }
    .car { font-size: 2rem; position: absolute; transition: left 0.5s ease; top: 50%; transform: translateY(-50%); }
    .gif-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 999999; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

def render_header():
    c1, c2 = st.columns([0.15, 0.85])
    with c1:
        if Path("mascot.png").exists(): st.image("mascot.png", width=45)
    with c2: st.markdown("<h2 style='font-family:Bungee; color:#FF6B6B; margin:0;'>AVENTURA MATEMÀTICA</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

# State initialization
if 'current_block' not in st.session_state: st.session_state.current_block = "Home"
if 'score' not in st.session_state: st.session_state.score = 0
if 'diff' not in st.session_state: st.session_state.diff = "Fàcil"
if 'mode' not in st.session_state: st.session_state.mode = "Sumes"
if 'reading_pos' not in st.session_state: st.session_state.reading_pos = 0
if 'rival_pos' not in st.session_state: st.session_state.rival_pos = 0
if 'reading_word' not in st.session_state: st.session_state.reading_word = ""
if 'word_start_time' not in st.session_state: st.session_state.word_start_time = time.time()
if 'words_pool' not in st.session_state: st.session_state.words_pool = []
if 'input_key' not in st.session_state: st.session_state.input_key = 0
if 'last_status' not in st.session_state: st.session_state.last_status = None

def get_new_problem():
    low, high = {"Fàcil": (1, 10), "Normal": (10, 50), "Difícil": (50, 200)}.get(st.session_state.diff, (1, 10))
    if st.session_state.current_block == "Lectura":
        if not st.session_state.words_pool:
            p = LECTURA_WORDS.get(st.session_state.diff, LECTURA_WORDS["Fàcil"]).copy()
            random.shuffle(p); st.session_state.words_pool = p
        st.session_state.reading_word = st.session_state.words_pool.pop()
        st.session_state.word_start_time = time.time()
    elif st.session_state.current_block == "Mates":
        m = st.session_state.mode
        if m == "Sumes": n1, n2 = random.randint(low, high), random.randint(low, high); st.session_state.problem_text, st.session_state.correct_answer = f"{n1} + {n2}", n1 + n2
        elif m == "Restes": n1 = random.randint(low + 5, high + 10); n2 = random.randint(1, n1); st.session_state.problem_text, st.session_state.correct_answer = f"{n1} - {n2}", n1 - n2
        elif m == "Multiplicació": n1, n2 = (random.randint(1, 5), random.randint(1, 10)) if st.session_state.diff == "Fàcil" else (random.randint(2, 10), random.randint(2, 10)); st.session_state.problem_text, st.session_state.correct_answer = f"{n1} x {n2}", n1 * n2
    elif st.session_state.current_block == "Innovamat":
        t = random.choice(["Amics", "Descompon", "Dobles", "Sèries", "Piràmide"])
        if t == "Amics": target = random.choice([10, 20, 100]); n1 = random.randint(1, target - 1); st.session_state.problem_text, st.session_state.correct_answer = f"{n1} + ? = {target}", target - n1
        elif t == "Descompon": target = random.randint(20, 999); base = (target // 10) * 10; st.session_state.problem_text, st.session_state.correct_answer = f"{target} = {base} + ?", target - base
        elif t == "Dobles":
            dm = "Doble" if st.session_state.diff == "Fàcil" else random.choice(["Doble", "Meitat"])
            n = random.randint(1, 50)
            if dm == "Meitat": 
                n = (n // 2) * 2
            st.session_state.problem_text, st.session_state.correct_answer = f"{dm.upper()} DE {n}", n * 2 if dm == "Doble" else n // 2
        elif t == "Sèries": s, stp = random.randint(1, 30), random.randint(2, 10); st.session_state.problem_text, st.session_state.correct_answer = f"{s}, {s+stp}, {s+2*stp}, ?", s+3*stp
        elif t == "Piràmide": n1, n2 = random.randint(1, 20), random.randint(1, 20); st.session_state.problem_text, st.session_state.correct_answer = f"{n1} | {n2} -> ?", n1 + n2

if 'problem_text' not in st.session_state: get_new_problem()

# RENDER
render_header()
if st.session_state.current_block == "Home":
    st.markdown("<p style='font-size:1.1rem;'>Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.button("🧮 MATES", on_click=lambda: st.session_state.update(current_block="Mates"), use_container_width=True)
    c2.button("💡 INNOVAMAT", on_click=lambda: st.session_state.update(current_block="Innovamat"), use_container_width=True)
    c3.button("📖 LECTURA", on_click=lambda: st.session_state.update(current_block="Lectura"), use_container_width=True)
else:
    with st.sidebar:
        st.markdown("<h2 style='font-family:Bungee;'>MENU</h2>", unsafe_allow_html=True)
        if st.button("🏠 INICI", use_container_width=True): st.session_state.current_block = "Home"; safe_rerun()
        st.markdown("---")
        if st.session_state.current_block == "Mates":
            if st.button("SUMA", use_container_width=True): st.session_state.mode = "Sumes"; get_new_problem(); safe_rerun()
            if st.button("RESTA", use_container_width=True): st.session_state.mode = "Restes"; get_new_problem(); safe_rerun()
            if st.button("MULT", use_container_width=True): st.session_state.mode = "Multiplicació"; get_new_problem(); safe_rerun()
            st.markdown("---")
        if st.button("FÀCIL", use_container_width=True): st.session_state.diff = "Fàcil"; get_new_problem(); safe_rerun()
        if st.button("NORMAL", use_container_width=True): st.session_state.diff = "Normal"; get_new_problem(); safe_rerun()
        if st.button("DIFÍCIL", use_container_width=True): st.session_state.diff = "Difícil"; get_new_problem(); safe_rerun()

    st.markdown("<div class='mobile-only-section'>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.button("FÀCIL", key="mf", use_container_width=True, on_click=lambda: st.session_state.update(diff="Fàcil"))
    m2.button("NORMAL", key="mn", use_container_width=True, on_click=lambda: st.session_state.update(diff="Normal"))
    m3.button("DIFÍCIL", key="md", use_container_width=True, on_click=lambda: st.session_state.update(diff="Difícil"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3>{st.session_state.current_block.upper()} • {st.session_state.diff.upper()}</h3>", unsafe_allow_html=True)
    if st.session_state.current_block == "Lectura":
        st.markdown(f'''<div class="race-track"><div class="car" style="left:{st.session_state.reading_pos}%; filter:hue-rotate(90deg);">🏎️</div></div>''', unsafe_allow_html=True)
        st.markdown(f'''<div class="race-track" style="background:#444;"><div class="car" style="left:{st.session_state.rival_pos}%;">🏎️</div></div>''', unsafe_allow_html=True)
        st.markdown(f"<div class='problem-box' style='border-color:#4BCffa;'>{st.session_state.reading_word}</div>", unsafe_allow_html=True)
        if st.button("LLEGIT! ✅", use_container_width=True):
            elapsed = time.time() - st.session_state.word_start_time
            spd = {"Fàcil": 1.5, "Normal": 4.5, "Difícil": 4.5}.get(st.session_state.diff, 3.0)
            st.session_state.reading_pos += 10; st.session_state.rival_pos += elapsed * spd
            if st.session_state.reading_pos >= 90: st.session_state.last_status = "correct"; st.session_state.reading_pos, st.session_state.rival_pos = 0, 0; st.session_state.score += 5
            elif st.session_state.rival_pos >= 90: st.session_state.last_status = "incorrect"; st.session_state.reading_pos, st.session_state.rival_pos = 0, 0
            get_new_problem(); safe_rerun()
    else:
        st.markdown(f"<div class='problem-box'>{st.session_state.problem_text}</div>", unsafe_allow_html=True)
        u_in = st.number_input("Resultat?", step=1, value=None, key=f"in_{st.session_state.input_key}", label_visibility="collapsed")
        if st.button("COMPROVAR! 🚀", use_container_width=True) and u_in is not None:
            st.session_state.input_key += 1
            if u_in == st.session_state.correct_answer: st.session_state.score += 1; st.session_state.last_status = "correct"; get_new_problem()
            else: st.session_state.last_status = "incorrect"
            safe_rerun()
    st.markdown(f"#### ⭐ PUNTS: {st.session_state.score}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.last_status:
    if st.session_state.last_status == "correct":
        gif, msg = random.choice(CELEBRATION_GIFS), random.choice(CELEBRATION_MESSAGES)
        st.markdown(f'''<div class="gif-overlay"><img src="{gif}"><h1 style="font-family:Bungee; color:#FF6B6B; font-size:3rem; margin-top:20px;">{msg} 🎉</h1></div>''', unsafe_allow_html=True)
    else: st.markdown('<div class="gif-overlay" style="background:rgba(244,67,54,0.9);"><h1 style="font-family:Bungee; color:white; font-size:3rem;">PROVA DE NOU! 🔄</h1></div>', unsafe_allow_html=True)
    st.session_state.last_status = None; time.sleep(2); safe_rerun()
