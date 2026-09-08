import streamlit as st
import streamlit.components.v1 as components
import random
import time
import json
import datetime
from pathlib import Path
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Aventura Matemàtica", page_icon="🧮", layout="wide", initial_sidebar_state="expanded")

BLOCKS = [
    ("🧮", "MATES", "Mates", "Sumes, restes i taules"),
    ("💡", "INNOVAMAT", "Innovamat", "Amics, dobles, sèries i piràmides"),
    ("📖", "LECTURA", "Lectura", "Carrera de lectura"),
    ("✏️", "LLETRES I NÚMEROS", "Lletres", "Resseguir lletres i números amb el dit"),
    ("🔍", "SOPA DE LLETRES", "Sopa", "Troba les paraules amagades"),
    ("🧠", "MEMORY", "Memory", "Gira les cartes i troba les parelles"),
    ("🎨", "COLOREJA", "Colors", "Pinta 100 dibuixos amb la paleta"),
    ("🏆", "REPTE", "Repte", "10 exercicis i informe final"),
]
SENSE_NIVELL = ("Lletres", "Colors")   # blocs sense Facil/Normal/Dificil

# ---- Caligrafia: l'abecedari catala amb una paraula d'exemple per a cada lletra ----
# (glif, paraula d'exemple, dibuix, com es diu la lletra en veu alta)
ABECEDARI = [
    ("A", "AVIÓ", "✈️", "a"), ("B", "BALENA", "🐋", "be"), ("C", "CASA", "🏠", "ce"),
    ("D", "DAU", "🎲", "de"), ("E", "ELEFANT", "🐘", "e"), ("F", "FLOR", "🌸", "efa"),
    ("G", "GAT", "🐱", "ge"), ("H", "HOTEL", "🏨", "hac"), ("I", "ILLA", "🏝️", "i"),
    ("J", "JOGUINA", "🧸", "jota"), ("K", "KIWI", "🥝", "ca"), ("L", "LUPA", "🔍", "ela"),
    ("M", "MÀ", "✋", "ema"), ("N", "NAS", "👃", "ena"), ("O", "OS", "🐻", "o"),
    ("P", "PILOTA", "⚽", "pe"), ("Q", "QUADRE", "🖼️", "cu"), ("R", "RODA", "🛞", "erra"),
    ("S", "SOL", "☀️", "essa"), ("T", "TAULA", "🪑", "te"), ("U", "UNGLA", "💅", "u"),
    ("V", "VACA", "🐮", "ve"), ("W", "WIFI", "📶", "ve doble"), ("X", "XOCOLATA", "🍫", "ics"),
    ("Y", "IOGURT", "🥛", "i grega"), ("Z", "ZEBRA", "🦓", "zeta"),
    ("Ç", "TAÇA", "☕", "ce trencada"), ("LL", "LLUNA", "🌙", "ela doble"),
    ("NY", "MUNTANYA", "⛰️", "ena i grega"),
]
NUMEROS = [
    ("0", "ZERO", "", "zero"), ("1", "U", "🍎", "u"), ("2", "DOS", "🍎🍎", "dos"),
    ("3", "TRES", "🍎🍎🍎", "tres"), ("4", "QUATRE", "🍎🍎🍎🍎", "quatre"),
    ("5", "CINC", "🍎🍎🍎🍎🍎", "cinc"), ("6", "SIS", "🍎🍎🍎🍎🍎🍎", "sis"),
    ("7", "SET", "🍎🍎🍎🍎🍎🍎🍎", "set"), ("8", "VUIT", "🍎🍎🍎🍎🍎🍎🍎🍎", "vuit"),
    ("9", "NOU", "🍎🍎🍎🍎🍎🍎🍎🍎🍎", "nou"), ("10", "DEU", "🍎🍎🍎🍎🍎🍎🍎🍎🍎🍎", "deu"),
]
DIFFS = [("Fàcil", "facil"), ("Normal", "normal"), ("Difícil", "dificil")]
OPS = [("SUMA", "Sumes", "suma"), ("RESTA", "Restes", "resta"), ("MULT", "Multiplicació", "mult")]
INNO_KINDS = [("TOTS", "Tots"), ("AMICS", "Amics"), ("DESCOMPON", "Descompon"),
              ("DOBLES", "Dobles"), ("MEITATS", "Meitats"), ("SÈRIES", "Sèries"),
              ("PIRÀMIDE", "Piràmide"), ("REPARTIR", "Repartir"), ("DESENES", "Desenes"),
              ("QUÈ FALTA", "Inversa"), ("SUMA DE 3", "Suma3"), ("PROBLEMES", "Problema")]
INNO_ALL = [k for _, k in INNO_KINDS if k != "Tots"]


def slugify(txt):
    """Clau CSS segura a partir d'un nom amb accents.

    Es diu slugify i no slug perque els bucles de DIFFS i OPS fan servir una
    variable 'slug', i abans tapaven la funcio -> TypeError a Innovamat."""
    return "".join(c if c.isalnum() else "_" for c in
                   txt.lower().replace("è", "e").replace("é", "e").replace("à", "a")
                      .replace("í", "i").replace("ó", "o").replace("ú", "u"))
REPTE_LEN = 10  # exercicis per sessio
BASE_DIR = Path(__file__).parent

# La classificacio es publica i hi juguen menors. Per defecte es GUARDA el nom
# sencer (aixi el mestre sap qui es) pero es MOSTRA abreujat: "Jan D.".
# Posa-ho a True si vols els cognoms sencers a la pantalla de tothom.
MOSTRA_NOMS_SENCERS = False


@st.cache_resource
def get_engine():
    """Postgres si hi ha secret 'db_url' (Supabase/Neon), si no SQLite local.

    IMPORTANT: a Streamlit Cloud el disc s'esborra a cada redesplegament, o sigui
    que SQLite alla nomes serveix per provar. Per a la classe cal el secret.
    """
    url = None
    try:
        url = st.secrets.get("db_url")
    except Exception:
        url = None
    fallback = not url
    eng = create_engine(url or f"sqlite:///{BASE_DIR / 'ranking.db'}", pool_pre_ping=True)
    with eng.begin() as c:
        c.execute(text("""
            CREATE TABLE IF NOT EXISTS ranking (
                nom TEXT PRIMARY KEY,
                punts INTEGER DEFAULT 0,
                encerts INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                millor_ratxa INTEGER DEFAULT 0,
                partides INTEGER DEFAULT 0,
                actualitzat TEXT
            )"""))
    return eng, fallback


def db_load(nom):
    eng, _ = get_engine()
    with eng.begin() as c:
        r = c.execute(text("SELECT punts, encerts, errors, millor_ratxa, partides"
                           " FROM ranking WHERE nom = :n"), {"n": nom}).fetchone()
    if not r:
        return {"punts": 0, "encerts": 0, "errors": 0, "millor_ratxa": 0, "partides": 0}
    return {"punts": r[0], "encerts": r[1], "errors": r[2], "millor_ratxa": r[3], "partides": r[4]}


def db_save(nom, punts, encerts, errors, millor_ratxa, partides):
    """Escriu el TOTAL (base d'abans + el d'aquesta sessio). Idempotent."""
    eng, _ = get_engine()
    with eng.begin() as c:
        c.execute(text("""
            INSERT INTO ranking (nom, punts, encerts, errors, millor_ratxa, partides, actualitzat)
            VALUES (:n, :p, :e, :x, :r, :g, :t)
            ON CONFLICT (nom) DO UPDATE SET
                punts = :p, encerts = :e, errors = :x,
                millor_ratxa = :r, partides = :g, actualitzat = :t"""),
            {"n": nom, "p": punts, "e": encerts, "x": errors, "r": millor_ratxa,
             "g": partides, "t": datetime.datetime.now().isoformat(timespec="seconds")})


def db_top(n=20):
    eng, _ = get_engine()
    with eng.begin() as c:
        return c.execute(text("SELECT nom, punts, encerts, errors, millor_ratxa"
                              " FROM ranking ORDER BY punts DESC, millor_ratxa DESC"
                              " LIMIT :n"), {"n": n}).fetchall()


def normalitza_nom(nom):
    """Els nens escriuran 'jan donoso', 'JAN DONOSO' i 'Jan  Donoso'. Sense
    normalitzar serien tres files diferents al rànquing i es repartirien els punts."""
    return " ".join(w.capitalize() for w in nom.split())


def nom_public(nom):
    if MOSTRA_NOMS_SENCERS:
        return nom
    parts = nom.split()
    return parts[0] + (f" {parts[1][0]}." if len(parts) > 1 else "")


# Nomes dibuixos, animals i nens. Revisats un a un mirant el primer fotograma:
# fora els 4 que eren el cartell 'THIS CONTENT IS NOT AVAILABLE' i tots els
# d'actors i adults (Trump, DiCaprio, Morgan Freeman, Borat...).
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
    "https://i.giphy.com/hEIuLmpW9DmGA.gif",
    "https://i.giphy.com/HJQObm4T6xS2Q.gif",
    "https://i.giphy.com/0WQXGB5aOPLdBRFWyH.gif",
    "https://i.giphy.com/11sBLVxNs7v6WA.gif",
    "https://i.giphy.com/3o7abKhOpu0NwenH3O.gif",
    "https://i.giphy.com/3oz8xAFtqoOUUrsh7W.gif",
    "https://i.giphy.com/QvBoMEcQ7DQXK.gif",
]
# Motivadores i valides per a nens i nenes (formes dobles: CAMPIÓ/NA, LLEST/A...).
CELEBRATION_MESSAGES = [
    "MOLT BÉ!",
    "HO HAS CLAVAT!",
    "MOLT BONA FEINA!",
    "SEGUEIX AIXÍ!",
    "IMPRESSIONANT!",
    "QUIN NIVELL!",
    "HO ESTÀS PETANT!",
    "CADA COP MILLOR!",
    "QUIN CAP!",
    "HO HAS ACONSEGUIT!",
    "UN 10!",
    "PERFECTE!",
    "EXCEL·LENT!",
    "QUINA PRECISIÓ!",
    "SENSE ERRORS!",
    "ETS UN/A CRACK!",
    "CAMPIÓ/NA!",
    "MOLT LLEST/A!",
    "T'HI ESTÀS POSANT!",
    "NO ET PARIS!",
    "AIXÒ ÉS TEU!",
    "QUINA MÀQUINA!",
    "BRAVO!",
    "GENIAL!",
    "INCREÏBLE!",
    "ESPECTACULAR!",
    "MÀGIC!",
    "BRUTAL!",
    "ENDAVANT!",
    "HO TENS!",
    "CADA VEGADA MÉS RÀPID!",
    "QUIN PROGRÉS!",
    "T'ESTÀS SUPERANT!",
    "MOLT BEN PENSAT!",
    "AIXÍ ES FA!",
    "SUPER!",
    "RÈCORD PERSONAL!",
    "NIVELL PRO!",
    "IMPARABLE!",
    "CONTINUA, HO FAS MOLT BÉ!",
]

# Vocabulari revisat: corregides paraules inventades o mal escrites (TREM, MIR, MUL,
# ESTRABOS, LLIT TOST, CADIRA COMODA, SENSE LIMITS...)
LECTURA_WORDS = {
    "Fàcil": ["CASA", "GAT", "SOL", "PAPA", "MAMA", "PA", "MÀ", "SOPA", "BOLA", "RODA", "NEN", "NENA", "GOS", "LLIT", "PEIX", "MAR", "CEL", "POC", "MOLT", "BONA", "DALT", "BAIX", "LLUM", "FOC", "DIU", "VEU", "RIU", "PIS", "TREN", "COSA", "LLUNA", "PILA", "TAULA", "CUC", "DIT", "NAS", "ULL", "CAP", "COR", "FER", "DIR", "SER", "TOT", "NOM", "OU", "LLET", "PAU", "MEL", "VOL", "FIL", "PEU", "NEU", "XIC"],
    "Normal": ["LA CASA BLANCA", "EL GAT NEGRE", "UN SOL GROC", "EL MEU PAPA", "LA MEVA MAMA", "MENJAR PA", "TENIR POR", "SOPA BONA", "BOLA GRAN", "RODA RÀPIDA", "NEN CONTENT", "NENA DOLÇA", "GOS PETIT", "LLIT TOU", "PEIX BLAU", "MAR SALADA", "CEL BLAU", "POC A POC", "MOLT CONTENT", "BONA NIT", "DALT DE TOT", "A BAIX DE TOT", "LLUM FORTA", "FOC CALENT", "FINESTRA OBERTA", "PORTA TANCADA", "SABATA NOVA", "PILOTA VERMELLA", "GIRAFA ALTA", "ELEFANT GRIS", "ESQUIROL VELOÇ", "ORDINADOR NOU", "LLIBRE VELL", "CADIRA CÒMODA", "PINTURA BLAVA", "ESTRELLA BRILLANT", "LLUNA PLENA", "DIA DE SOL", "NIT DE LLUNA", "PLUJA FREDA"],
    "Difícil": ["L'ORDINADOR ÉS VELL", "EL LLIBRE ÉS DIVERTIT", "L'ESTRUÇ CORRE MOLT", "EL FRIGORÍFIC ÉS BLANC", "UN CONEIXEMENT PROFUND", "EL BOLÍGRAF ÉS BLAU", "LES MATEMÀTIQUES SÓN FÀCILS", "UNA ENCICLOPÈDIA MOLT GRAN", "UNA TRANSFORMACIÓ MÀGICA", "UN RECONEIXEMENT RÀPID", "EXCURSIÓ A LA MUNTANYA", "UN VIATGE MOLT LLUNY", "UNA PARAULA COMPLICADA", "LA BIBLIOTECA PÚBLICA", "IMAGINACIÓ SENSE LÍMITS", "UNA GRAN RESPONSABILITAT", "UN EXPERIMENT CIENTÍFIC", "UN INSTRUMENT MUSICAL", "UNA FOTOGRAFIA BONICA", "L'ARQUITECTURA MODERNA", "UN ASTRONAUTA VALENT", "UN PALEONTÒLEG FAMÓS", "UNA INVESTIGACIÓ SECRETA", "UN ESPECTACLE INCREÏBLE", "EL MEU GAT ÉS BLANC", "LA NENA ÉS BONA", "EL SOL ÉS GROC", "M'AGRADA MOLT LLEGIR", "JUGAR AMB ELS AMICS", "ANAR A L'ESCOLA", "MENJAR UNA POMA", "VEURE LA TELEVISIÓ", "DORMIR MOLT BÉ", "CANTAR UNA CANÇÓ", "BALLAR TOTA LA NIT", "ESCRIURE UNA CARTA", "DIBUIXAR UN QUADRE", "CÓRRER PEL CAMP", "SALTAR MOLT ALT", "NEDAR A LA MAR"]
}

# ---- Sopa de lletres: paraules en majuscules i sense accents (com a les sopes de
# paper). Cap paraula amb apostrof, amb C-trencada ni palindroma (es trobaria dos cops).
SOPA_WORDS = {
    "Fàcil": ["GAT", "GOS", "SOL", "MAR", "CASA", "NENA", "POMA", "BOLA", "RODA",
              "LLIT", "PEIX", "FOC", "CEL", "MEL", "NEU", "PEU", "DIT", "NAS", "ULL",
              "COR", "TREN", "LLUNA", "TAULA", "FLOR", "VACA", "RIU", "PILA",
              "LLET", "PAU", "FIL", "VOL", "ARBRE", "SOPA", "PARC", "CASC", "PORC",
              "LLOP", "MICO", "GALL", "RATA", "NIU", "MOTO", "BUS", "DAU", "BEC"],
    "Normal": ["ESCOLA", "AMIC", "AMIGA", "LLIBRE", "PILOTA", "GIRAFA", "ELEFANT",
               "SABATA", "PORTA", "FINESTRA", "CADIRA", "CUINA", "JARDI", "PLATJA",
               "BOSC", "MUNTANYA", "ESTRELLA", "CAMIO", "AVIO", "CONILL", "TORTUGA",
               "POLLET", "FORMIGA", "DOFI", "BALENA", "TIGRE", "LLEO", "COTXE",
               "VAIXELL", "PASTIS", "GALETA", "TARONJA", "MADUIXA", "PLATAN", "PERA",
               "RAIM", "LLIMONA", "CIRERA", "PIRATA", "CASTELL", "TRESOR", "DRAC",
               "BRUIXA", "MAGIA", "PLUJA", "VENT", "ARENA",
               "OVELLA", "CAVALL", "ANEC", "GRANOTA", "SERP", "CARGOL", "ABELLA"],
    "Difícil": ["BICICLETA", "PAPALLONA", "ORDINADOR", "DINOSAURE", "ASTRONAUTA",
                "XOCOLATA", "BIBLIOTECA", "MATEMATIQUES", "ESQUIROL", "HIPOPOTAM",
                "COCODRIL", "RINOCERONT", "HELICOPTER", "SUBMARI", "TELEVISIO",
                "FRIGORIFIC", "EXCURSIO", "GUITARRA", "TROMPETA", "VOLCA", "PLANETA",
                "UNIVERS", "AVENTURA", "PRINCESA", "CAVALLER", "FANTASMA", "ESQUELET",
                "CARBASSA", "PINGUI", "CANGUR", "GIRASOL", "ARCOIRIS", "TEMPESTA",
                "LABERINT", "MISTERI", "DETECTIU", "CIENTIFIC", "ROBOT", "COET",
                "SATELLIT", "GALAXIA", "MUNTANYA", "ESTRELLA", "FINESTRA", "PAPERERA",
                "MOTXILLA", "ESTOIG", "LLAPIS", "PISSARRA", "CALCULADORA"],
}
# n = mida de la graella, k = paraules per sopa, dirs = direccions en que s'amaguen
# (fila, columna), bonus = punts extra per acabar-la
SOPA_CFG = {
    "Fàcil":   {"n": 8,  "k": 5, "dirs": [(0, 1), (1, 0)], "bonus": 2},
    "Normal":  {"n": 10, "k": 7, "dirs": [(0, 1), (1, 0), (1, 1), (-1, 1)], "bonus": 4},
    "Difícil": {"n": 13, "k": 9, "dirs": [(0, 1), (1, 0), (1, 1), (-1, 1),
                                          (0, -1), (-1, 0), (-1, -1), (1, -1)], "bonus": 6},
}
DIRS8 = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]

# ---- Memory: parelles d'emojis (es veuen igual a qualsevol mobil, sense descarregar res)
MEMORY_SETS = {
    "Animals": ["🐶", "🐱", "🐭", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸",
                "🐵", "🐔", "🐧", "🦉", "🦄", "🐝", "🦋", "🐢", "🐙", "🐬", "🐳", "🦒", "🐘"],
    "Menjar": ["🍎", "🍌", "🍇", "🍓", "🍒", "🍑", "🍍", "🥝", "🍉", "🍋", "🥕", "🌽", "🍕",
               "🍔", "🍟", "🌭", "🍿", "🧁", "🍩", "🍪", "🍫", "🍭", "🍦", "🥐", "🧀", "🥑"],
    "Coses": ["🚗", "🚀", "✈️", "🚂", "🚲", "⛵", "🎈", "🎁", "⚽", "🏀", "🎸", "🎹", "🎲",
              "🧩", "🪁", "🎯", "🔑", "⏰", "💡", "📚", "🖍️", "✂️", "🧸", "🎪", "🏰", "🌈"],
}
# n = parelles, bonus = punts extra per acabar
MEMORY_CFG = {"Fàcil": {"n": 6, "bonus": 2}, "Normal": {"n": 8, "bonus": 4},
              "Difícil": {"n": 15, "bonus": 6}}

# ---- Coloreja: 100 dibuixos. Cada un es un emoji convertit en dibuix de linia
# dins del navegador (contorn negre, interior blanc) que el nen omple amb la paleta.
DIBUIXOS = [
    ("🐶", "GOS"), ("🐱", "GAT"), ("🐭", "RATOLÍ"), ("🐰", "CONILL"), ("🦊", "GUINEU"),
    ("🐻", "OS"), ("🐼", "PANDA"), ("🐨", "COALA"), ("🐯", "TIGRE"), ("🦁", "LLEÓ"),
    ("🐮", "VACA"), ("🐷", "PORC"), ("🐸", "GRANOTA"), ("🐵", "MICO"), ("🐔", "GALLINA"),
    ("🐧", "PINGÜÍ"), ("🦉", "MUSSOL"), ("🦄", "UNICORN"), ("🐝", "ABELLA"), ("🦋", "PAPALLONA"),
    ("🐢", "TORTUGA"), ("🐙", "POP"), ("🐬", "DOFÍ"), ("🐳", "BALENA"), ("🦒", "GIRAFA"),
    ("🐘", "ELEFANT"), ("🦓", "ZEBRA"), ("🐴", "CAVALL"), ("🐑", "OVELLA"), ("🐊", "COCODRIL"),
    ("🦖", "DINOSAURE"), ("🐞", "MARIETA"), ("🐌", "CARGOL"), ("🐟", "PEIX"), ("🦀", "CRANC"),
    ("🦈", "TAURÓ"), ("🐿️", "ESQUIROL"), ("🦔", "ERIÇÓ"), ("🦜", "LLORO"), ("🦚", "PAÓ"),
    ("🍎", "POMA"), ("🍌", "PLÀTAN"), ("🍇", "RAÏM"), ("🍓", "MADUIXA"), ("🍒", "CIRERES"),
    ("🍍", "PINYA"), ("🍉", "SÍNDRIA"), ("🍋", "LLIMONA"), ("🥕", "PASTANAGA"), ("🍕", "PIZZA"),
    ("🍔", "HAMBURGUESA"), ("🧁", "MAGDALENA"), ("🍩", "DÒNUT"), ("🍦", "GELAT"), ("🎂", "PASTÍS"),
    ("🚗", "COTXE"), ("🚀", "COET"), ("✈️", "AVIÓ"), ("🚂", "TREN"), ("🚲", "BICICLETA"),
    ("⛵", "VELER"), ("🚁", "HELICÒPTER"), ("🚜", "TRACTOR"), ("🚒", "BOMBERS"), ("🚌", "AUTOBÚS"),
    ("🎈", "GLOBUS"), ("🎁", "REGAL"), ("⚽", "PILOTA"), ("🎸", "GUITARRA"), ("🎲", "DAU"),
    ("🧸", "OSSET"), ("🪁", "ESTEL"), ("🏰", "CASTELL"), ("🌈", "ARC DE SANT MARTÍ"), ("⭐", "ESTRELLA"),
    ("🌞", "SOL"), ("🌙", "LLUNA"), ("☁️", "NÚVOL"), ("🌸", "FLOR"), ("🌻", "GIRA-SOL"),
    ("🌵", "CACTUS"), ("🌳", "ARBRE"), ("🍄", "BOLET"), ("🏠", "CASA"), ("⛄", "NINOT DE NEU"),
    ("🎃", "CARBASSA"), ("🎄", "ARBRE DE NADAL"), ("👑", "CORONA"), ("🧙", "MAG"), ("🧚", "FADA"),
    ("🤖", "ROBOT"), ("👻", "FANTASMA"), ("🦸", "SUPERHEROI"), ("🧜", "SIRENA"), ("🐉", "DRAC"),
    ("🎪", "CIRC"), ("🎠", "CAVALLET"), ("🚤", "LLANXA"), ("🛸", "OVNI"), ("🏄", "SURFISTA"),
]
assert len(DIBUIXOS) == 100, len(DIBUIXOS)
# lletres de farciment amb la frequencia aproximada del catala
SOPA_FARCIT = "AAAAAEEEEEIIIOOOOUURRRSSSTTTLLLNNNMMCCDDPPBGVFXJZH"


def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Bungee&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: linear-gradient(135deg, #FFDEE9 0%, #B5FFFC 100%); background-attachment: fixed; }
    /* dins de cada columna, el botó i la seva descripció han d'anar junts;
       Streamlit hi posa un buit vertical per defecte que els separava massa */
    .st-key-homeblocks div[data-testid="stVerticalBlock"] { gap: 0.15rem !important; }
    .desc { background: rgba(255,255,255,0.92); border-radius: 14px; padding: 8px 10px;
             margin: 4px 0 0 0; min-height: 62px; display: flex; align-items: center;
             justify-content: center; text-align: center; font-size: 0.86rem;
             line-height: 1.25; color: #2D3436; box-shadow: 0 3px 0 rgba(0,0,0,0.06); }
    .st-key-controlbar { margin-bottom: 8px; }
    .st-key-controlbar button { height: 46px !important; font-size: 1.05rem !important; }
    .st-key-maincard { background: rgba(255,255,255,0.9); border-radius: 30px; padding: 1.5rem 1.5rem 0.5rem 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    .problem-box { font-family: 'Bungee', cursive !important; font-size: 3.5rem; min-height: 140px; border-radius: 25px; background: white; border: 8px dashed #FF6B6B; display: flex; align-items: center; justify-content: center; margin: 15px auto; color: #2D3436; text-align: center; padding: 10px; }
    div[data-testid="stNumberInput"] { height: 140px !important; }
    div[data-testid="stNumberInput"] > div { height: 140px !important; border: none !important; box-shadow: none !important; background: transparent !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] { border: none !important; background: transparent !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] { background: white !important; border-radius: 25px !important; border: 8px solid #FF6B6B !important; height: 140px !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] input { height: 140px !important; font-family: 'Bungee', cursive !important; font-size: 3.5rem !important; text-align: center !important; border: none !important; outline: none !important; }
    button[data-testid="stNumberInputStepUp"], button[data-testid="stNumberInputStepDown"] { display: none !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { -moz-appearance: textfield; }
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { background: linear-gradient(180deg, #FF6B6B 0%, #EE5253 100%) !important; color: white !important; font-family: 'Bungee', cursive !important; font-size: 1.5rem !important; min-height: 60px !important; height: auto !important; border-radius: 15px !important; box-shadow: 0 5px 0px #D63031 !important; border: none !important; padding: 8px 10px !important; }
    div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { white-space: normal !important; word-break: break-word !important; line-height: 1.15 !important; }
    /* els 6 blocs de la home: lletra més petita perquè hi càpiga "LLETRES I NÚMEROS" */
    .st-key-homeblocks div.stButton > button { font-size: 1.05rem !important; min-height: 66px !important; }
    /* ---------------- TAULETA I MÒBIL ----------------
       Molts nens hi jugaran des del mòbil, així que tot s'ha d'adaptar:
       columnes que s'apilen, botons i tipografies més petits, GIF que no se'n surt. */
    @media (max-width: 1024px) {
      .st-key-homeblocks div.stButton > button { font-size: 0.95rem !important; }
    }
    @media (max-width: 767px) {
      section[data-testid="stSidebar"] { display: none !important; }
      div[data-testid="stMainBlockContainer"] { padding: 0.6rem 0.7rem 3rem 0.7rem !important; }
      /* les columnes deixen de ser una fila estreta i passen a dues per línia */
      div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important;
        column-gap: 6px !important; row-gap: 30px !important; }
      div[data-testid="stColumn"] { flex: 1 1 calc(50% - 6px) !important; min-width: calc(50% - 6px) !important; }
      h2 { font-size: 1.3rem !important; }
      h3 { font-size: 1rem !important; }
      .desc { min-height: 50px; font-size: 0.76rem; padding: 6px 8px; margin-top: 3px; }
      .problem-box { font-size: 1.9rem !important; min-height: 92px !important; border-width: 5px !important; padding: 6px !important; }
      div[data-testid="stNumberInput"], div[data-testid="stNumberInput"] > div,
      div[data-testid="stNumberInput"] div[data-baseweb="input"] { height: 92px !important; }
      div[data-testid="stNumberInput"] div[data-baseweb="input"] { border-width: 5px !important; }
      div[data-testid="stNumberInput"] div[data-baseweb="input"] input { height: 92px !important; font-size: 2.2rem !important; }
      div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        min-height: 52px !important; font-size: 1.02rem !important; }
      .st-key-homeblocks div.stButton > button { font-size: 0.9rem !important; min-height: 58px !important; }
      .st-key-controlbar div[data-testid="stColumn"] { flex: 1 1 0 !important; min-width: 0 !important; }
      /* Coloreja: la columna de "SORPRESA" necessita mes ample que les d'icona */
      .st-key-controlbar div[data-testid="stColumn"]:has(.st-key-ctl_dib_rand) { flex: 2.6 1 0 !important; }
      .st-key-controlbar div[data-testid="stHorizontalBlock"] { row-gap: 6px !important; }
      .st-key-controlbar button { min-height: 44px !important; font-size: 0.74rem !important;
        padding: 4px 2px !important; }
      .st-key-maincard { padding: 0.9rem 0.8rem 0.4rem 0.8rem !important; border-radius: 20px !important; }
      .brick { min-width: 56px !important; height: 46px !important; font-size: 1.15rem !important; border-width: 3px !important; }
      .chip { font-size: 0.78rem !important; padding: 5px 10px !important; }
      .race-track { height: 46px !important; }
      .car { font-size: 1.5rem !important; }
      .gif-overlay img { max-width: 86vw !important; max-height: 45vh !important; height: auto !important; }
      .gif-overlay h1 { font-size: 1.8rem !important; text-align: center !important; padding: 0 12px !important; }
      .rank-row { font-size: 0.85rem !important; padding: 6px 8px !important; gap: 6px !important; }
      .rank-row .rank-pct { display: none !important; }
    }
    /* mòbils molt estrets: un botó per línia */
    @media (max-width: 380px) {
      div[data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 100% !important; }
      .desc { min-height: 0; }
      .problem-box { font-size: 1.5rem !important; }
    }
    .race-track { height: 46px !important; }
      .car { font-size: 1.5rem !important; }
      .gif-overlay img { max-width: 86vw !important; max-height: 45vh !important; height: auto !important; }
      .gif-overlay h1 { font-size: 1.8rem !important; text-align: center !important; padding: 0 12px !important; }
      .rank-row { font-size: 0.85rem !important; padding: 6px 8px !important; gap: 6px !important; }
      .rank-row .rank-pct { display: none !important; }
    }
    /* mòbils molt estrets: un botó per línia als blocs de la home */
    @media (max-width: 430px) {
      .st-key-homeblocks div[data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 100% !important; }
      .problem-box { font-size: 1.55rem !important; }
    }
    .race-track { background: #333; height: 60px; width: 100%; border-radius: 15px; position: relative; margin: 10px 0; border: 3px dashed white; overflow: hidden; }
    .car { font-size: 2rem; position: absolute; transition: left 0.5s ease; top: 50%; transform: translateY(-50%); }
    .gif-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(10px); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 999999; }
    .scoreboard { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 10px; }
    .chip { background: white; border-radius: 15px; padding: 6px 14px; font-family: 'Bungee', cursive; color: #2D3436; box-shadow: 0 3px 0 rgba(0,0,0,0.1); font-size: 1rem; }
    /* Piramide de veritat */
    .pyr { display: flex; flex-direction: column; align-items: center; gap: 8px; font-family: 'Bungee', cursive; }
    .pyr-row { display: flex; gap: 8px; }
    .brick { min-width: 90px; height: 62px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.9rem; background: #FFF4CC; border: 4px solid #F7B731; color: #2D3436; }
    .brick.empty { background: #F1F2F6; border-style: dashed; border-color: #B2BEC3; color: #B2BEC3; }
    .brick.ask { background: white; border: 5px dashed #EE5253; color: #EE5253; }
    .st-key-autofocus { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-autofocus iframe { height: 0 !important; border: 0 !important; display: block !important; }
    [data-testid="stHeaderActionElements"] { display: none !important; }
    [data-testid="InputInstructions"] { display: none !important; }
    /* el llenç de caligrafia s'ajusta sol: el contenidor l'ha de seguir */
    div[data-testid="stElementContainer"]:has(> iframe[data-testid="stIFrame"]) { height: auto !important; }
    @media (max-width: 767px) { .st-key-caligrafia iframe[data-testid="stIFrame"] { max-height: 300px; } }
    /* boto invisible que la sopa de lletres clica sola quan s'han trobat totes les paraules */
    .st-key-sopa_done { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-sopa_done button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    .st-key-memory_done { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-memory_done button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

def safe_rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

def autofocus_answer(nonce):
    """Posa el cursor dins la casella del resultat a cada nova operacio."""
    with st.container(key="autofocus"):
        components.html("""
            <script>
            const NONCE = "%s";
            function focusAnswer() {
              try {
                const doc = window.parent.document;
                const el = doc.querySelector('div[data-testid="stNumberInput"] input');
                if (!el || el.offsetParent === null) return false;
                if (doc.activeElement !== el) { el.focus({preventScroll: true}); el.select(); }
                return doc.activeElement === el;
              } catch (e) { return false; }
            }
            let tries = 0;
            const timer = setInterval(() => { if (focusAnswer() || ++tries > 40) clearInterval(timer); }, 50);
            </script>
        """ % nonce, height=0)

def canvas_caligrafia(glif, nonce, frase=""):
    """Llenc per resseguir la lletra amb el dit (tauleta) o el ratoli.

    Fet a ma amb <canvas> en lloc de streamlit-drawable-canvas: cap dependencia
    externa que pugui petar al desplegament, i funciona amb el dit al mobil.
    """
    minus = glif.lower()
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Andika:wght@400;700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent; }
  #wrap { display:flex; flex-direction:column; gap:8px; align-items:center; }
  #c { background:#fff; border:6px dashed #4BCFFA; border-radius:22px; touch-action:none;
       width:100%; max-width:640px; display:block; cursor:crosshair; }
  #barra { display:flex; gap:8px; width:100%; max-width:640px; }
  button { flex:1; font-family:'Andika',sans-serif; font-weight:700; font-size:1rem;
           color:#fff; border:none; border-radius:14px; height:46px; cursor:pointer; }
  #escolta { background:#4B7BEC; box-shadow:0 4px 0 #2D5BC7; }
  #esborra { background:#EE5253; box-shadow:0 4px 0 #B33; }
  #gruix   { background:#20BF6B; box-shadow:0 4px 0 #0B7A45; }
  #avis { font-size:0.72rem; color:#888; text-align:center; min-height:14px; }
  @media (max-width:420px) { button { font-size:0.82rem; } }
  button:active { transform:translateY(3px); box-shadow:none; }
</style>
<div id="wrap">
  <canvas id="c"></canvas>
  <div id="barra">
    <button id="escolta">🔊 ESCOLTA</button>
    <button id="esborra">🧽 ESBORRA</button>
    <button id="gruix">✏️ GRUIX</button>
  </div>
  <div id="avis"></div>
</div>
<script>
  const GLIF = "__GLIF__", MINUS = "__MINUS__", NONCE = "__NONCE__";
  const c = document.getElementById('c'), ctx = c.getContext('2d');
  const GRUIXOS = [16, 26, 9]; let ig = 0;
  let pintant = false, traces = [];

  function mida() {
    // l'alcada la mana la finestra del component (no l'amplada): aixi no queda
    // mai un buit blanc a sota, ni al mobil ni al PC
    const w = Math.min(c.parentElement.clientWidth, 640);
    const h = Math.max(140, window.innerHeight - 62);
    const dpr = window.devicePixelRatio || 1;
    c.width = w * dpr; c.height = h * dpr;
    c.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    redibuixa();
  }
  function guia() {
    const w = c.clientWidth, h = c.clientHeight;
    ctx.clearRect(0, 0, w, h);
    // pauta: linies del quadern
    ctx.strokeStyle = '#EAF6FF'; ctx.lineWidth = 2;
    [0.25, 0.5, 0.75].forEach(f => {
      ctx.beginPath(); ctx.moveTo(14, h*f); ctx.lineTo(w-14, h*f); ctx.stroke();
    });
    // el glif, gran i clar, per resseguir a sobre
    const txt = GLIF + '  ' + MINUS;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    let px = h * 0.72;
    ctx.font = px + "px Andika, 'Trebuchet MS', sans-serif";
    while (ctx.measureText(txt).width > w - 40 && px > 12) {
      px -= 2; ctx.font = px + "px Andika, 'Trebuchet MS', sans-serif";
    }
    ctx.fillStyle = '#EDEDED';
    ctx.fillText(txt, w/2, h/2);
    ctx.strokeStyle = '#C9C9C9'; ctx.lineWidth = 2; ctx.setLineDash([8, 7]);
    ctx.strokeText(txt, w/2, h/2);
    ctx.setLineDash([]);
  }
  function redibuixa() {
    guia();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.strokeStyle = '#EE5253';
    for (const t of traces) {
      if (t.p.length < 2) continue;
      ctx.lineWidth = t.w; ctx.beginPath();
      ctx.moveTo(t.p[0].x, t.p[0].y);
      for (let i = 1; i < t.p.length; i++) ctx.lineTo(t.p[i].x, t.p[i].y);
      ctx.stroke();
    }
  }
  function pos(e) {
    const r = c.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }
  c.addEventListener('pointerdown', e => {
    pintant = true; c.setPointerCapture(e.pointerId);
    traces.push({ w: GRUIXOS[ig], p: [pos(e)] }); redibuixa();
  });
  c.addEventListener('pointermove', e => {
    if (!pintant) return;
    traces[traces.length-1].p.push(pos(e)); redibuixa();
  });
  ['pointerup','pointercancel','pointerleave'].forEach(ev =>
    c.addEventListener(ev, () => { pintant = false; }));
  // ---- Veu: Web Speech API, ja inclosa al navegador ----
  const FRASE = "__FRASE__";
  function veuCatalana() {
    const vs = window.speechSynthesis ? speechSynthesis.getVoices() : [];
    return vs.find(v => /^ca(-|_|$)/i.test(v.lang))          // catala
        || vs.find(v => /^es(-|_|$)/i.test(v.lang))          // si no n'hi ha, castella
        || vs[0] || null;
  }
  function parla() {
    if (!window.speechSynthesis) {
      document.getElementById('avis').textContent = "Aquest navegador no pot llegir en veu alta.";
      return;
    }
    speechSynthesis.cancel();                                 // no encavalcar veus
    const u = new SpeechSynthesisUtterance(FRASE);
    const v = veuCatalana();
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = 'ca-ES'; }
    u.rate = 0.85;                                            // a poc a poc, son nens
    speechSynthesis.speak(u);
    const av = document.getElementById('avis');
    av.textContent = (v && /^ca/i.test(v.lang)) ? "" :
      (v ? "Sense veu catalana al dispositiu: es fa servir " + v.lang : "");
  }
  document.getElementById('escolta').onclick = parla;
  if (window.speechSynthesis) speechSynthesis.onvoiceschanged = () => {};  // forca carregar-les
  document.getElementById('esborra').onclick = () => { traces = []; redibuixa(); };
  document.getElementById('gruix').onclick = () => { ig = (ig + 1) % GRUIXOS.length; };
  window.addEventListener('resize', mida);
  document.fonts && document.fonts.ready.then(redibuixa);
  mida();
</script>
"""
        .replace("__GLIF__", glif)
        .replace("__MINUS__", minus)
        .replace("__NONCE__", nonce)
        .replace("__FRASE__", frase.replace('"', "'")))
    with st.container(key="caligrafia"):
        components.html(html, height=330)


def sopa_component(sopa, nonce):
    """Graella interactiva de la sopa de lletres.

    Es marca arrossegant amb el dit (mobil) o el ratoli en linia recta. Tot es
    resol dins del navegador; quan s'han trobat totes les paraules, el script
    clica el boto invisible 'sopa_done' de la pagina i Streamlit suma els punts.
    Sense dependencies externes (com el llenc de caligrafia). Mai format amb %.
    """
    n = sopa["n"]
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Andika:wght@400;700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent;
         user-select:none; -webkit-user-select:none; }
  #wrap { display:flex; flex-direction:column; gap:8px; align-items:center; }
  #llista { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; max-width:640px; }
  .paraula { background:#fff; border:2px solid #F7B731; border-radius:12px; padding:2px 10px;
             font-weight:700; font-size:0.95rem; color:#2D3436; letter-spacing:1px; }
  .paraula.trobada { background:#20BF6B; border-color:#0B7A45; color:#fff; text-decoration:line-through; }
  #graella { display:grid; background:#fff; border:6px dashed #4BCFFA; border-radius:22px;
             padding:8px; touch-action:none; gap:2px; cursor:pointer; }
  .cel { display:flex; align-items:center; justify-content:center; font-weight:700;
         color:#2D3436; border-radius:8px; line-height:1; }
  .cel.sel { background:#FFE08A; }
  .cel.ok { color:#fff; }
  #msg { font-weight:700; color:#EE5253; text-align:center; min-height:22px; font-size:1.1rem; }
  @media (max-width:420px) { .paraula { font-size:0.78rem; padding:1px 7px; } }
</style>
<div id="wrap">
  <div id="llista"></div>
  <div id="graella"></div>
  <div id="msg"></div>
</div>
<script>
  const GRID = __GRID__, WORDS = __WORDS__, N = __N__, NONCE = "__NONCE__";
  const COLORS = ['#FF6B6B','#4B7BEC','#20BF6B','#F7B731','#A55EEA','#FD9644','#2BCBBA','#EB3B5A','#0FB9B1','#8854D0'];
  const graella = document.getElementById('graella'), llista = document.getElementById('llista'),
        msg = document.getElementById('msg');
  const trobades = new Set(); let cels = [], start = null, cur = [], acabat = false;

  WORDS.forEach(w => { const d = document.createElement('div'); d.className = 'paraula';
                       d.id = 'p_' + w; d.textContent = w; llista.appendChild(d); });
  for (let r = 0; r < N; r++) { cels.push([]);
    for (let c = 0; c < N; c++) {
      const d = document.createElement('div'); d.className = 'cel';
      d.dataset.r = r; d.dataset.c = c; d.textContent = GRID[r][c];
      graella.appendChild(d); cels[r].push(d);
    } }
  function mida() {
    const W = Math.min(document.body.clientWidth, 640);
    const H = window.innerHeight - llista.offsetHeight - msg.offsetHeight - 24;
    const cel = Math.max(22, Math.floor(Math.min((W - 30) / N, (H - 30) / N, 56)));
    graella.style.gridTemplateColumns = 'repeat(' + N + ',' + cel + 'px)';
    cels.flat().forEach(d => { d.style.width = d.style.height = cel + 'px';
                               d.style.fontSize = Math.round(cel * 0.58) + 'px'; });
  }
  function celA(e) {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    return (el && el.classList.contains('cel')) ? {r: +el.dataset.r, c: +el.dataset.c} : null;
  }
  function linia(a, b) {
    const dr = b.r - a.r, dc = b.c - a.c;
    if (dr !== 0 && dc !== 0 && Math.abs(dr) !== Math.abs(dc)) return null;
    const n = Math.max(Math.abs(dr), Math.abs(dc)), sr = Math.sign(dr), sc = Math.sign(dc), out = [];
    for (let i = 0; i <= n; i++) out.push({r: a.r + sr * i, c: a.c + sc * i});
    return out;
  }
  function marca(l) {
    cur.forEach(p => cels[p.r][p.c].classList.remove('sel'));
    cur = l; cur.forEach(p => cels[p.r][p.c].classList.add('sel'));
  }
  function comprova() {
    const s = cur.map(p => GRID[p.r][p.c]).join('');
    const inv = s.split('').reverse().join('');
    const w = WORDS.find(x => !trobades.has(x) && (x === s || x === inv));
    if (!w) return;
    trobades.add(w);
    const col = COLORS[(trobades.size - 1) % COLORS.length];
    cur.forEach(p => { const d = cels[p.r][p.c]; d.classList.add('ok'); d.style.background = col; });
    document.getElementById('p_' + w).classList.add('trobada');
    if (trobades.size === WORDS.length) acaba();
  }
  function acaba() {
    if (acabat) return; acabat = true;
    msg.textContent = 'LES HAS TROBAT TOTES! 🎉';
    setTimeout(() => {
      try {
        const b = window.parent.document.querySelector('.st-key-sopa_done button');
        if (b) { b.click(); return; }
      } catch (e) {}
      msg.textContent = 'LES HAS TROBAT TOTES! Prem NOVA SOPA 🎉';
    }, 900);
  }
  graella.addEventListener('pointerdown', e => {
    if (acabat) return;
    const c = celA(e); if (!c) return;
    start = c; graella.setPointerCapture(e.pointerId); marca([c]); e.preventDefault();
  });
  graella.addEventListener('pointermove', e => {
    if (!start) return;
    const c = celA(e); if (!c) return;
    const l = linia(start, c); if (l) marca(l);
  });
  ['pointerup', 'pointercancel'].forEach(ev => graella.addEventListener(ev, () => {
    if (!start) return;
    comprova(); start = null; marca([]);
  }));
  window.addEventListener('resize', mida);
  document.fonts && document.fonts.ready.then(mida);
  mida();
</script>
"""
        .replace("__GRID__", json.dumps(sopa["grid"]))
        .replace("__WORDS__", json.dumps(sopa["words"]))
        .replace("__N__", str(n))
        .replace("__NONCE__", nonce))
    components.html(html, height={8: 520, 10: 610, 13: 740}.get(n, 60 * n))


def memory_component(mem, nonce):
    """Joc de memory: cartes que es giren en tocar-les. Tot passa al navegador i,
    en trobar totes les parelles, el script clica el boto invisible 'memory_done'."""
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Andika:wght@700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent;
         user-select:none; -webkit-user-select:none; }
  #wrap { display:flex; flex-direction:column; align-items:center; gap:8px; }
  #info { font-weight:700; color:#2D3436; font-size:1rem; }
  #taula { display:grid; gap:8px; justify-content:center; }
  .carta { perspective:600px; cursor:pointer; }
  .cara { position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
          border-radius:14px; backface-visibility:hidden; -webkit-backface-visibility:hidden; }
  .darrere { background:linear-gradient(135deg,#4B7BEC,#A55EEA); color:#fff; box-shadow:0 4px 0 #2D5BC7; }
  .davant { background:#fff; border:3px solid #F7B731; transform:rotateY(180deg); }
  .interior { position:relative; width:100%; height:100%; transition:transform 0.35s; transform-style:preserve-3d; }
  .carta.girada .interior { transform:rotateY(180deg); }
  .carta.parella .davant { border-color:#20BF6B; background:#E9FFF3; }
  #msg { font-weight:700; color:#EE5253; text-align:center; min-height:22px; font-size:1.1rem; }
</style>
<div id="wrap">
  <div id="info"></div>
  <div id="taula"></div>
  <div id="msg"></div>
</div>
<script>
  const CARDS = __CARDS__, NONCE = "__NONCE__";
  const taula = document.getElementById('taula'), info = document.getElementById('info'),
        msg = document.getElementById('msg');
  let obertes = [], bloquejat = false, intents = 0, parelles = 0, acabat = false, els = [];
  function pinta() { info.textContent = 'Parelles: ' + parelles + ' / ' + (CARDS.length / 2) + '   ·   Intents: ' + intents; }
  CARDS.forEach((e, i) => {
    const c = document.createElement('div'); c.className = 'carta'; c.dataset.i = i;
    c.innerHTML = '<div class="interior"><div class="cara darrere">?</div><div class="cara davant">' + e + '</div></div>';
    c.addEventListener('pointerdown', ev => { ev.preventDefault(); gira(c); });
    taula.appendChild(c); els.push(c);
  });
  function gira(c) {
    if (bloquejat || acabat || c.classList.contains('girada')) return;
    c.classList.add('girada'); obertes.push(c);
    if (obertes.length < 2) return;
    intents++; bloquejat = true;
    const [a, b] = obertes;
    if (CARDS[a.dataset.i] === CARDS[b.dataset.i]) {
      a.classList.add('parella'); b.classList.add('parella'); parelles++;
      obertes = []; bloquejat = false; pinta();
      if (parelles === CARDS.length / 2) acaba();
    } else {
      setTimeout(() => { a.classList.remove('girada'); b.classList.remove('girada');
                         obertes = []; bloquejat = false; }, 800);
    }
    pinta();
  }
  function acaba() {
    acabat = true; msg.textContent = 'TOTES LES PARELLES! 🎉';
    setTimeout(() => {
      try {
        const b = window.parent.document.querySelector('.st-key-memory_done button');
        if (b) { b.click(); return; }
      } catch (e) {}
      msg.textContent = 'TOTES LES PARELLES! Prem NOVA PARTIDA 🎉';
    }, 900);
  }
  function mida() {
    const W = Math.min(document.body.clientWidth, 720), n = CARDS.length;
    const H = window.innerHeight - info.offsetHeight - msg.offsetHeight - 24;
    let millor = {cols: 4, mida: 0};
    [3, 4, 5, 6].forEach(cols => {
      const files = Math.ceil(n / cols);
      const m = Math.min((W - 8 * (cols - 1)) / cols, (H - 8 * (files - 1)) / files, 120);
      if (m > millor.mida) millor = {cols: cols, mida: m};
    });
    const m = Math.floor(millor.mida);
    taula.style.gridTemplateColumns = 'repeat(' + millor.cols + ',' + m + 'px)';
    els.forEach(c => { c.style.width = c.style.height = m + 'px';
                       c.querySelector('.davant').style.fontSize = Math.round(m * 0.58) + 'px';
                       c.querySelector('.darrere').style.fontSize = Math.round(m * 0.5) + 'px'; });
  }
  window.addEventListener('resize', mida);
  pinta(); mida();
</script>
"""
        .replace("__CARDS__", json.dumps(mem["cards"], ensure_ascii=False))
        .replace("__NONCE__", nonce))
    components.html(html, height={6: 430, 8: 470, 15: 600}.get(len(mem["cards"]) // 2, 500))


def coloreja_component(emoji, nom, nonce):
    """Pagina per pintar: l'emoji es converteix en un dibuix de linia (contorn negre)
    i el nen omple les zones amb el cubell o pinta amb el pinzell. Paleta a la dreta.
    Dues capes: a sota els colors, a sobre les linies (sempre nitides)."""
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Andika:wght@700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent;
         user-select:none; -webkit-user-select:none; }
  #wrap { display:flex; gap:8px; align-items:flex-start; justify-content:center; }
  #zona { position:relative; border:6px dashed #4BCFFA; border-radius:22px; background:#fff;
          overflow:hidden; touch-action:none; }
  canvas { display:block; position:absolute; left:0; top:0; }
  #linies { pointer-events:none; }
  #paleta { display:grid; grid-template-columns:repeat(2, 1fr); gap:6px; }
  .color { width:34px; height:34px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 0 2px #ccc;
           cursor:pointer; }
  .color.actiu { box-shadow:0 0 0 4px #2D3436; transform:scale(1.12); }
  #eines { display:flex; flex-direction:column; gap:6px; margin-top:8px; grid-column:1 / -1; }
  .eina { font-family:inherit; font-weight:700; font-size:0.9rem; color:#fff; border:none;
          border-radius:12px; height:40px; cursor:pointer; background:#4B7BEC; box-shadow:0 3px 0 #2D5BC7; }
  .eina.actiu { background:#20BF6B; box-shadow:0 3px 0 #0B7A45; }
  .eina.vermell { background:#EE5253; box-shadow:0 3px 0 #B33; }
  .eina:active { transform:translateY(3px); box-shadow:none; }
  #avis { position:absolute; left:0; right:0; bottom:8px; text-align:center; font-size:0.8rem; color:#888; }
  @media (max-width:420px) { .color { width:28px; height:28px; } .eina { font-size:0.8rem; height:36px; } }
</style>
<div id="wrap">
  <div id="zona"><canvas id="pintura"></canvas><canvas id="linies"></canvas><div id="avis"></div></div>
  <div id="paleta">
    <div id="eines">
      <button class="eina actiu" id="cubell">🪣 OMPLE</button>
      <button class="eina" id="pinzell">🖌️ PINTA</button>
      <button class="eina" id="desfes">↩️ DESFÉS</button>
      <button class="eina vermell" id="neteja">🧽 NETEJA</button>
    </div>
  </div>
</div>
<script>
  const EMOJI = "__EMOJI__", NONCE = "__NONCE__", S = 480;
  const COLORS = ['#EE5253','#FF9F43','#FECA57','#F9E79F','#20BF6B','#7BED9F','#1E90FF','#48DBFB',
                  '#5F27CD','#A55EEA','#FF6B81','#FFC0CB','#8B4513','#D2B48C','#2D3436','#95A5A6','#FFFFFF','#00CEC9'];
  const zona = document.getElementById('zona'), pintura = document.getElementById('pintura'),
        linies = document.getElementById('linies'), paleta = document.getElementById('paleta'),
        eines = document.getElementById('eines'), avis = document.getElementById('avis');
  const pctx = pintura.getContext('2d', {willReadFrequently: true}), lctx = linies.getContext('2d');
  pintura.width = pintura.height = linies.width = linies.height = S;
  let color = COLORS[0], mode = 'cubell', mask = null, historial = [], pintant = false, teLinies = false;

  COLORS.forEach((c, i) => {
    const d = document.createElement('div'); d.className = 'color' + (i === 0 ? ' actiu' : '');
    d.style.background = c;
    d.onclick = () => { color = c; paleta.querySelectorAll('.color').forEach(x => x.classList.remove('actiu')); d.classList.add('actiu'); };
    paleta.insertBefore(d, eines);
  });
  function setMode(m) {
    mode = m;
    document.getElementById('cubell').classList.toggle('actiu', m === 'cubell');
    document.getElementById('pinzell').classList.toggle('actiu', m === 'pinzell');
  }
  document.getElementById('cubell').onclick = () => setMode('cubell');
  document.getElementById('pinzell').onclick = () => setMode('pinzell');
  document.getElementById('desfes').onclick = () => { if (historial.length) pctx.putImageData(historial.pop(), 0, 0); };
  document.getElementById('neteja').onclick = () => { guarda(); pctx.fillStyle = '#fff'; pctx.fillRect(0, 0, S, S); };
  function guarda() { historial.push(pctx.getImageData(0, 0, S, S)); if (historial.length > 15) historial.shift(); }

  // ---- de l'emoji al dibuix de linia ----
  // Gradient de Sobel sobre color + silueta: capta tambe les vores suaus
  // (antialiasing) que una simple comparacio de veins es deixava, i aixi el
  // cubell no s'escapa entre zones. Despres s'engruixeix 1px i s'esborren
  // les taques petites (punts solts que fa el propi emoji).
  function dibuixaLinies() {
    const off = document.createElement('canvas'); off.width = off.height = S;
    const o = off.getContext('2d', {willReadFrequently: true});
    o.textAlign = 'center'; o.textBaseline = 'middle';
    o.font = Math.round(S * 0.72) + 'px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif';
    o.fillText(EMOJI, S / 2, S / 2 + S * 0.03);
    const d = o.getImageData(0, 0, S, S).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 60) n++;
    if (n < 500) return false;                       // l'emoji no s'ha pogut dibuixar
    const ch = [0, 1, 2, 3].map(() => new Float32Array(S * S));
    for (let i = 0; i < S * S; i++) {
      const a = d[i*4+3] / 255, w = 255 * (1 - a);
      ch[0][i] = d[i*4] * a + w; ch[1][i] = d[i*4+1] * a + w; ch[2][i] = d[i*4+2] * a + w; ch[3][i] = d[i*4+3];
    }
    const T = 60, linia = new Uint8Array(S * S);
    for (let y = 1; y < S - 1; y++) for (let x = 1; x < S - 1; x++) {
      const i = y * S + x; let mag = 0;
      for (let c = 0; c < 4; c++) { const v = ch[c];
        const gx = -v[i-S-1] + v[i-S+1] - 2*v[i-1] + 2*v[i+1] - v[i+S-1] + v[i+S+1];
        const gy = -v[i-S-1] - 2*v[i-S] - v[i-S+1] + v[i+S-1] + 2*v[i+S] + v[i+S+1];
        mag += Math.sqrt(gx*gx + gy*gy) * (c === 3 ? 2 : 1); }
      if (mag > T * 4) linia[i] = 1;
    }
    mask = new Uint8Array(S * S);
    for (let y = 1; y < S - 1; y++) for (let x = 1; x < S - 1; x++) {
      const i = y * S + x;
      if (linia[i] || linia[i-1] || linia[i+1] || linia[i-S] || linia[i+S]) mask[i] = 1;
    }
    // fora les taques de menys de 50 pixels
    const etiq = new Uint8Array(S * S);
    for (let s0 = 0; s0 < S * S; s0++) {
      if (!mask[s0] || etiq[s0]) continue;
      const comp = [s0], pila = [s0]; etiq[s0] = 1;
      while (pila.length) {
        const i = pila.pop(), x = i % S;
        for (const j of [x > 0 ? i-1 : -1, x < S-1 ? i+1 : -1, i >= S ? i-S : -1, i < S*(S-1) ? i+S : -1]) {
          if (j >= 0 && mask[j] && !etiq[j]) { etiq[j] = 1; pila.push(j); comp.push(j); }
        }
      }
      if (comp.length < 50) comp.forEach(i => { mask[i] = 0; });
    }
    const img = lctx.createImageData(S, S), p = img.data;
    for (let i = 0; i < S * S; i++) { if (mask[i]) { p[i*4] = p[i*4+1] = p[i*4+2] = 34; p[i*4+3] = 255; } }
    lctx.putImageData(img, 0, 0);
    return true;
  }
  function hex2rgb(h) { return [parseInt(h.slice(1,3),16), parseInt(h.slice(3,5),16), parseInt(h.slice(5,7),16)]; }
  function omple(x0, y0) {
    if (mask && mask[y0 * S + x0]) return;
    guarda();
    const img = pctx.getImageData(0, 0, S, S), p = img.data, [R, G, B] = hex2rgb(color);
    const i0 = (y0 * S + x0) * 4, tr = p[i0], tg = p[i0+1], tb = p[i0+2];
    if (tr === R && tg === G && tb === B) return;
    const vist = new Uint8Array(S * S), pila = [y0 * S + x0];
    while (pila.length) {
      const i = pila.pop();
      if (vist[i] || (mask && mask[i])) continue;
      const k = i * 4;
      if (Math.abs(p[k] - tr) + Math.abs(p[k+1] - tg) + Math.abs(p[k+2] - tb) > 60) continue;
      vist[i] = 1; p[k] = R; p[k+1] = G; p[k+2] = B; p[k+3] = 255;
      const x = i % S;
      if (x > 0) pila.push(i - 1); if (x < S - 1) pila.push(i + 1);
      if (i >= S) pila.push(i - S); if (i < S * (S - 1)) pila.push(i + S);
    }
    pctx.putImageData(img, 0, 0);
  }
  function pos(e) {
    const r = pintura.getBoundingClientRect();
    return {x: Math.floor((e.clientX - r.left) * S / r.width), y: Math.floor((e.clientY - r.top) * S / r.height)};
  }
  let ultim = null;
  zona.addEventListener('pointerdown', e => {
    e.preventDefault(); const p = pos(e);
    if (p.x < 0 || p.y < 0 || p.x >= S || p.y >= S) return;
    if (mode === 'cubell') { omple(p.x, p.y); return; }
    guarda(); pintant = true; zona.setPointerCapture(e.pointerId); ultim = p;
    pctx.strokeStyle = color; pctx.lineWidth = S / 28; pctx.lineCap = 'round'; pctx.lineJoin = 'round';
    pctx.beginPath(); pctx.moveTo(p.x, p.y); pctx.lineTo(p.x + 0.1, p.y); pctx.stroke();
  });
  zona.addEventListener('pointermove', e => {
    if (!pintant) return; const p = pos(e);
    pctx.beginPath(); pctx.moveTo(ultim.x, ultim.y); pctx.lineTo(p.x, p.y); pctx.stroke(); ultim = p;
  });
  ['pointerup', 'pointercancel'].forEach(ev => zona.addEventListener(ev, () => { pintant = false; }));

  function mida() {
    const pal = paleta.offsetWidth + 8;
    const side = Math.max(160, Math.min(document.body.clientWidth - pal, window.innerHeight - 4, 640));
    zona.style.width = zona.style.height = side + 'px';
    pintura.style.width = pintura.style.height = linies.style.width = linies.style.height = (side - 12) + 'px';
  }
  pctx.fillStyle = '#fff'; pctx.fillRect(0, 0, S, S);
  window.addEventListener('resize', mida);
  mida();
  function inicia() {
    teLinies = dibuixaLinies();
    if (!teLinies) avis.textContent = 'Aquest dispositiu no pot dibuixar-lo: pinta lliurement! 🖌️';
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(inicia); else inicia();
</script>
"""
        .replace("__EMOJI__", emoji)
        .replace("__NONCE__", nonce))
    components.html(html, height=560)


# ------------------------------------------------------------ GENERADORS
def _pyramid_html(bottom, ask_top=True):
    rows = ["<div class='pyr-row'><div class='brick ask'>?</div></div>",
            "<div class='pyr-row'>" + "".join("<div class='brick empty'>+</div>" for _ in range(len(bottom) - 1)) + "</div>",
            "<div class='pyr-row'>" + "".join(f"<div class='brick'>{b}</div>" for b in bottom) + "</div>"]
    if len(bottom) == 2: rows.pop(1)
    return "<div class='pyr'>" + "".join(rows) + "</div>"

def _pyramid_top(bottom):
    row = list(bottom)
    while len(row) > 1:
        row = [row[i] + row[i + 1] for i in range(len(row) - 1)]
    return row[0]

def _pick(gen, ok, tries=80):
    """Genera fins que compleixi la condicio de dificultat (amb sortida segura)."""
    cand = gen()
    for _ in range(tries):
        if ok(cand): return cand
        cand = gen()
    return cand

def make_math(diff, op):
    """Cada nivell te un SOL minim de dificultat: abans un '2 x 10' podia sortir
    a Dificil i un '2 x 2' a Normal, mes facils que exercicis de Facil."""
    R = random.randint
    if op == "Sumes":
        if diff == "Fàcil":
            a, b = _pick(lambda: (R(2, 9), R(2, 9)), lambda c: c[0] + c[1] >= 5)
        elif diff == "Normal":
            a, b = _pick(lambda: (R(11, 49), R(11, 49)), lambda c: c[0] % 10 + c[1] % 10 >= 10)
        else:
            a, b = _pick(lambda: (R(101, 499), R(101, 499)),
                         lambda c: c[0] % 10 + c[1] % 10 >= 10 or (c[0] // 10) % 10 + (c[1] // 10) % 10 >= 10)
        return f"{a} + {b}", a + b
    if op == "Restes":
        if diff == "Fàcil":
            a, b = _pick(lambda: (R(5, 18), R(2, 9)), lambda c: c[0] - c[1] >= 1)
        elif diff == "Normal":
            a, b = _pick(lambda: (R(21, 80), R(11, 60)), lambda c: c[0] - c[1] >= 5 and c[0] % 10 < c[1] % 10)
        else:
            a, b = _pick(lambda: (R(150, 900), R(30, 400)), lambda c: c[0] - c[1] >= 30 and c[0] % 10 < c[1] % 10)
        return f"{a} - {b}", a - b
    if diff == "Fàcil":
        a, b = R(2, 5), R(2, 10)
    elif diff == "Normal":
        a, b = _pick(lambda: (R(3, 10), R(3, 10)), lambda c: max(c) >= 6)
    else:
        a, b = _pick(lambda: (R(6, 12), R(11, 30)), lambda c: c[1] % 10 != 0)
    return f"{a} x {b}", a * b

def make_inno(diff, kind="Tots"):
    """Retorna (text, resposta, html_opcional)."""
    R = random.randint
    if kind == "Tots":
        kind = random.choice(INNO_ALL)
    if kind == "Amics":
        if diff == "Fàcil":
            target = random.choice([10, 20]); a = R(1, target - 1)
        elif diff == "Normal":
            target = random.choice([20, 50, 100])
            a = _pick(lambda: R(1, target - 1), lambda x: target - x >= 5)
        else:
            target = random.choice([100, 200, 500])
            a = _pick(lambda: R(1, target - 1), lambda x: target - x >= 20 and x % 10 != 0)
        return f"{a} + ? = {target}", target - a, None
    if kind == "Descompon":
        # Cap xifra pot ser 0: si no sortien exercicis degenerats com "70 = 70 + ?"
        if diff == "Fàcil":
            n = _pick(lambda: R(11, 99), lambda x: x % 10 != 0)
            parts = [(n // 10) * 10, n % 10]
        elif diff == "Normal":
            n = _pick(lambda: R(101, 999), lambda x: all(d != "0" for d in str(x)))
            parts = [(n // 100) * 100, ((n // 10) % 10) * 10, n % 10]
        else:
            # A Dificil la descomposicio per posicions era un simple "llegeix la xifra".
            # Ara la part coneguda no es canonica: 457 = 380 + ? obliga a restar.
            n = R(210, 980)
            base = _pick(lambda: R(3, (n - 20) // 10) * 10, lambda b: 20 <= n - b <= n - 20)
            return f"{n} = {base} + ?", n - base, None
        i = random.randrange(len(parts))
        shown = " + ".join("?" if j == i else str(pt) for j, pt in enumerate(parts))
        return f"{n} = {shown}", parts[i], None
    if kind == "Dobles":
        if diff == "Fàcil": n = R(2, 10)
        elif diff == "Normal": n = _pick(lambda: R(11, 50), lambda x: x % 10 != 0)
        else: n = _pick(lambda: R(55, 250), lambda x: x % 5 != 0)
        return f"DOBLE DE {n}", n * 2, None
    if kind == "Sèries":
        if diff == "Fàcil":
            step, s, down = R(2, 5), R(1, 20), False
        elif diff == "Normal":
            step, down = R(3, 10), random.random() < 0.4
            s = R(step * 4 + 1, step * 4 + 40) if down else R(5, 40)
        else:
            step, down = R(7, 25), random.random() < 0.4
            s = R(step * 4 + 1, step * 4 + 90) if down else R(20, 90)
        seq = [s - i * step for i in range(4)] if down else [s + i * step for i in range(4)]
        return ", ".join(str(x) for x in seq[:3]) + ", ?", seq[3], None
    if kind == "Meitats":
        n = _pick(lambda: R(1, 10) * 2, lambda x: x >= 4) if diff == "Fàcil" else (
            _pick(lambda: R(6, 50) * 2, lambda x: x % 10 != 0) if diff == "Normal" else
            _pick(lambda: R(51, 200) * 2, lambda x: x % 10 != 0))
        return f"MEITAT DE {n}", n // 2, None
    if kind == "Repartir":
        if diff == "Fàcil": d, q = R(2, 3), R(2, 5)
        elif diff == "Normal": d, q = R(2, 5), R(3, 10)
        else: d, q = R(3, 9), R(5, 20)
        return f"REPARTEIX {d * q} EN {d} GRUPS IGUALS", q, None
    if kind == "Desenes":
        if diff == "Fàcil": n = R(2, 9) * 10
        elif diff == "Normal": n = _pick(lambda: R(30, 300), lambda x: x % 10 != 0)
        else: n = _pick(lambda: R(300, 3000), lambda x: x % 10 != 0)
        return f"QUANTES DESENES HI HA A {n}?", n // 10, None
    if kind == "Inversa":
        if diff == "Fàcil": a, b = R(2, 5), R(2, 6)
        elif diff == "Normal": a, b = _pick(lambda: (R(3, 10), R(3, 10)), lambda c: max(c) >= 6)
        else: a, b = _pick(lambda: (R(6, 12), R(6, 20)), lambda c: c[0] * c[1] >= 80)
        return f"? x {a} = {a * b}", b, None
    if kind == "Suma3":
        if diff == "Fàcil": v = [R(1, 9) for _ in range(3)]
        elif diff == "Normal": v = [R(5, 30) for _ in range(3)]
        else: v = [R(20, 99) for _ in range(3)]
        return " + ".join(str(x) for x in v), sum(v), None
    if kind == "Problema":
        if diff == "Fàcil": lo, hi = 2, 10
        elif diff == "Normal": lo, hi = 5, 40
        else: lo, hi = 20, 150
        t = random.choice(["resta", "suma", "grups", "queden"])
        if t == "resta":
            a = R(lo + 2, hi); b = R(lo, max(lo + 1, a - lo))   # res de "menys 1"
            return f"HI HA {a} CROMOS I EN DONES {b}. QUANTS EN QUEDEN?", a - b, None
        if t == "suma":
            a, b = R(lo, hi), R(lo, hi)
            return f"TENS {a} CANIQUES I EN GUANYES {b}. QUANTES TENS?", a + b, None
        if t == "grups":
            c = R(2, 5) if diff == "Fàcil" else R(3, 9)
            n = R(2, 6) if diff == "Fàcil" else R(4, 12)
            return f"{c} CAIXES AMB {n} LLAPIS CADA UNA. QUANTS LLAPIS HI HA?", c * n, None
        a = R(lo + 5, hi); b = R(max(2, lo), max(lo + 2, a // 2))
        return f"UN AUTOBÚS PORTA {a} PERSONES I EN BAIXEN {b}. QUANTES QUEDEN?", a - b, None
    rng = (1, 9) if diff == "Fàcil" else ((3, 20) if diff == "Normal" else (15, 60))
    n = 2 if diff == "Fàcil" else 3
    bottom = [R(*rng) for _ in range(n)]
    return "PIRÀMIDE", _pyramid_top(bottom), _pyramid_html(bottom)

RECENT_MAX = 20  # quants exercicis recordem per no repetir-los

def _sopa_ocurrencies(grid, word):
    """Quantes vegades surt la paraula a la graella, en qualsevol de les 8 direccions."""
    n, L, count = len(grid), len(word), 0
    for r in range(n):
        for c in range(n):
            for dr, dc in DIRS8:
                if not (0 <= r + dr * (L - 1) < n and 0 <= c + dc * (L - 1) < n):
                    continue
                if all(grid[r + dr * i][c + dc * i] == word[i] for i in range(L)):
                    count += 1
    return count


def _sopa_tria_paraules(diff):
    """k paraules del nivell, que capiguen i que cap no sigui dins d'una altra."""
    cfg = SOPA_CFG[diff]
    pool = [w for w in SOPA_WORDS[diff] if len(w) <= cfg["n"]]
    random.shuffle(pool)
    out = []
    for w in pool:
        if any(w in o or w[::-1] in o or o in w or o[::-1] in w for o in out):
            continue
        out.append(w)
        if len(out) == cfg["k"]:
            break
    return out


def genera_sopa(diff):
    """Sopa de lletres del nivell: graella n x n amb k paraules amagades, cada una
    exactament un cop (es comprova a posteriori, perque el farciment aleatori
    podria formar-ne una altra copia i el nen trobaria 'la que no toca')."""
    cfg = SOPA_CFG[diff]
    n = cfg["n"]
    for _ in range(300):
        words = _sopa_tria_paraules(diff)
        grid = [[None] * n for _ in range(n)]
        ok = True
        for w in sorted(words, key=len, reverse=True):
            L = len(w)
            for _ in range(300):
                dr, dc = random.choice(cfg["dirs"])
                r, c = random.randrange(n), random.randrange(n)
                if not (0 <= r + dr * (L - 1) < n and 0 <= c + dc * (L - 1) < n):
                    continue
                cells = [(r + dr * i, c + dc * i) for i in range(L)]
                if all(grid[x][y] in (None, w[i]) for i, (x, y) in enumerate(cells)):
                    for i, (x, y) in enumerate(cells):
                        grid[x][y] = w[i]
                    break
            else:
                ok = False
                break
        if not ok:
            continue
        for row in grid:
            for j, ch in enumerate(row):
                if ch is None:
                    row[j] = random.choice(SOPA_FARCIT)
        if all(_sopa_ocurrencies(grid, w) == 1 for w in words):
            return {"n": n, "grid": ["".join(row) for row in grid],
                    "words": sorted(words), "level": diff}
    raise RuntimeError("No s'ha pogut generar la sopa de lletres")


def genera_memory(diff):
    """Parelles barrejades d'un mateix tema (animals, menjar o coses)."""
    n = MEMORY_CFG[diff]["n"]
    tema = random.choice(list(MEMORY_SETS))
    cards = random.sample(MEMORY_SETS[tema], n) * 2
    random.shuffle(cards)
    return {"cards": cards, "level": diff, "tema": tema}


def _remember(text):
    r = st.session_state.recent
    r.append(text)
    del r[:-RECENT_MAX]

def new_problem():
    """Genera l'exercici seguent, evitant repetir els ultims RECENT_MAX."""
    ss = st.session_state
    ss.attempts = 0
    ss.problem_html = None
    block, diff = ss.current_block, ss.diff

    if block == "Lletres":
        ss.problem_text = "caligrafia"     # marca perque la guarda d'inici no torni a entrar
        return
    if block == "Sopa":
        ss.problem_text = "sopa"
        ss.sopa = genera_sopa(diff)
        ss.sopa_n += 1                     # canvia la clau del component: graella nova de zero
        return
    if block == "Memory":
        ss.problem_text = "memory"
        ss.memory = genera_memory(diff)
        ss.memory_n += 1
        return
    if block == "Colors":
        ss.problem_text = "colors"
        return
    if block == "Lectura":
        if not ss.words_pool:
            pool = LECTURA_WORDS[diff].copy(); random.shuffle(pool); ss.words_pool = pool
        ss.reading_word = ss.words_pool.pop()
        ss.problem_text = ss.reading_word   # cal, si no la guarda d'inici el regenera cada rerun
        ss.word_start_time = time.time()
        return
    if block == "Mates":
        for _ in range(40):
            text, ans = make_math(diff, ss.mode)
            if text not in ss.recent: break
        ss.problem_text, ss.correct_answer = text, ans
        _remember(text)
        return
    if block == "Innovamat":
        for _ in range(40):
            text, ans, html = make_inno(diff, ss.inno_kind)
            key = html or text          # la piramide sempre te el mateix text
            if key not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.problem_html = text, ans, html
        _remember(html or text)
        return
    # Repte: barreja mates + innovamat, sempre al nivell que ha triat el nen
    d = ss.diff
    if random.random() < 0.5:
        for _ in range(40):
            text, ans = make_math(d, random.choice([m for _, m, _ in OPS]))
            if text not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.kind_label = text, ans, "Càlcul"
        _remember(text)
    else:
        k = random.choice(INNO_ALL)
        for _ in range(40):
            text, ans, html = make_inno(d, k)
            if (html or text) not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.problem_html, ss.kind_label = text, ans, html, k
        _remember(html or text)

# ------------------------------------------------------------------ STATE
DEFAULTS = {
    'current_block': "Home", 'nom': "", 'diff': "Fàcil", 'mode': "Sumes", 'inno_kind': "Tots",
    'reading_pos': 0, 'rival_pos': 0, 'reading_word': "", 'word_start_time': time.time(),
    'words_pool': [], 'problem_text': "", 'problem_html': None, 'correct_answer': 0,
    'input_key': 0, 'last_status': None, 'reveal': None, 'attempts': 0, 'ratxa': 0,
    'kind_label': "", 'lectura_avis': False,
    'punts': 0, 'encerts': 0, 'errors': 0, 'millor_ratxa': 0, 'partides': 0, 'db_error': '',
    'repte': None, 'repte_report': None, 'recent': [], 'last_gif': '', 'last_msg': '',
    'base': None, 'nom_actiu': '', 'lletra_idx': 0, 'lletra_set': 'Lletres',
    'sopa': None, 'sopa_n': 0, 'memory': None, 'memory_n': 0, 'dibuix_idx': 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

def new_repte():
    st.session_state.repte = {"i": 0, "ok": 0, "ko": 0, "level": st.session_state.diff,
                              "t0": time.time(), "log": []}
    st.session_state.repte_report = None

def start_block(block):
    ss = st.session_state
    ss.current_block = block
    ss.words_pool = []; ss.reading_pos = ss.rival_pos = 0; ss.lectura_avis = False
    if block == "Repte": new_repte()
    if block == "Lletres": ss.lletra_idx = 0
    new_problem()

def de_o_d(paraula):
    """En catala 'de' es contreu davant de vocal o h: d'avio, d'hotel, d'illa.
    Excepcio: la i i la u semiconsonants no es contreuen (de iogurt)."""
    if paraula.upper().startswith(("IO", "IU", "HI", "UA", "UE", "UI")):
        return f"de {paraula.lower()}"
    if paraula[0].upper() in "AEIOUÀÈÉÍÒÓÚH":
        return f"d'{paraula.lower()}"
    return f"de {paraula.lower()}"


def lletres_actual():
    taula = ABECEDARI if st.session_state.lletra_set == "Lletres" else NUMEROS
    i = st.session_state.lletra_idx % len(taula)
    return taula[i], i, len(taula)


def lletres_mou(delta):
    taula = ABECEDARI if st.session_state.lletra_set == "Lletres" else NUMEROS
    st.session_state.lletra_idx = (st.session_state.lletra_idx + delta) % len(taula)


def set_lletra_set(quin):
    st.session_state.lletra_set = quin
    st.session_state.lletra_idx = 0


def sopa_completada():
    """Totes les paraules trobades: punts segons el nivell, GIF i sopa nova."""
    ss = st.session_state
    if ss.current_block != "Sopa" or ss.sopa is None:
        return
    ss.punts += SOPA_CFG[ss.sopa["level"]]["bonus"]
    register(True)                         # +1 punt, encert, ratxa i classificacio
    ss.last_status = "correct"
    new_problem()


def memory_completat():
    """Totes les parelles trobades: punts segons el nivell, GIF i partida nova."""
    ss = st.session_state
    if ss.current_block != "Memory" or ss.memory is None:
        return
    ss.punts += MEMORY_CFG[ss.memory["level"]]["bonus"]
    register(True)
    ss.last_status = "correct"
    new_problem()


def dibuix_mou(delta):
    ss = st.session_state
    if delta is None:
        ss.dibuix_idx = random.randrange(len(DIBUIXOS))
    else:
        ss.dibuix_idx = (ss.dibuix_idx + delta) % len(DIBUIXOS)


def set_mode(m):
    st.session_state.mode = m; new_problem()

def set_diff(d):
    st.session_state.diff = d
    st.session_state.words_pool = []
    if st.session_state.current_block == "Repte":
        new_repte()          # canviar de nivell comenca un repte net d'aquell nivell
    new_problem()

def reset_lectura():
    """Torna els dos cotxes a la sortida i comenca una carrera nova."""
    ss = st.session_state
    ss.reading_pos = ss.rival_pos = 0
    ss.lectura_avis = False
    ss.words_pool = []          # barreja de nou tot el vocabulari del nivell
    new_problem()

def set_inno_kind(k):
    st.session_state.inno_kind = k; new_problem()

def sync_ranking():
    """Puja el total (el que ja tenia + el d'aquesta sessio) a la classificacio."""
    ss = st.session_state
    nom = ss.nom.strip()
    if not nom or ss.base is None:
        return
    try:
        b = ss.base
        db_save(nom, b["punts"] + ss.punts, b["encerts"] + ss.encerts,
                b["errors"] + ss.errors, max(b["millor_ratxa"], ss.millor_ratxa),
                b["partides"] + ss.partides)
    except Exception as e:
        ss.db_error = str(e)


def on_nom_change():
    """Streamlit esborra l'estat dels widgets que deixen de dibuixar-se, i el nom
    nomes es dibuixa a la Home: si el guardavem a la clau del widget, es perdia
    en entrar a un bloc i no es desava res. Per aixo el copiem a 'nom', que es
    una clau normal i sobreviu."""
    st.session_state.nom = normalitza_nom(st.session_state.nom_input)
    carrega_base()


def carrega_base():
    """Quan el nen escriu el seu nom, recupera el que ja tenia."""
    ss = st.session_state
    nom = ss.nom.strip()
    if nom == ss.nom_actiu:
        return
    ss.nom_actiu = nom
    if not nom:
        ss.base = None
        return
    try:
        ss.base = db_load(nom)
        ss.db_error = ""
    except Exception as e:
        ss.base = None
        ss.db_error = str(e)


def register(correct):
    ss = st.session_state
    if correct:
        ss.punts += 1; ss.encerts += 1; ss.ratxa += 1
        ss.millor_ratxa = max(ss.millor_ratxa, ss.ratxa)
    else:
        ss.errors += 1; ss.ratxa = 0
    sync_ranking()

def advance_repte(correct):
    """Compta l'exercici. El nivell el mana el nen, no puja ni baixa sol."""
    r = st.session_state.repte
    r["i"] += 1
    r["log"].append({"kind": st.session_state.kind_label, "ok": correct, "level": st.session_state.diff})
    if correct: r["ok"] += 1
    else: r["ko"] += 1
    if r["i"] >= REPTE_LEN:
        r["secs"] = time.time() - r["t0"]
        r["level"] = st.session_state.diff
        st.session_state.partides += 1
        st.session_state.repte_report = r
        sync_ranking()

def check_answer(value):
    ss = st.session_state
    ss.input_key += 1
    correct = value == ss.correct_answer
    if ss.current_block == "Repte":
        register(correct)
        advance_repte(correct)
        ss.last_status = "correct" if correct else "reveal"
        if not correct: ss.reveal = str(ss.correct_answer)
        if ss.repte_report is None: new_problem()
        return
    if correct:
        register(True); ss.last_status = "correct"; new_problem()
    else:
        register(False); ss.attempts += 1
        if ss.attempts >= 2:
            ss.last_status = "reveal"; ss.reveal = str(ss.correct_answer); new_problem()
        else:
            ss.last_status = "incorrect"

if not st.session_state.problem_text and st.session_state.current_block not in ("Home", "Ranking"):
    new_problem()

# ----------------------------------------------------------------- RENDER
def render_header():
    c1, c2 = st.columns([0.15, 0.85])
    with c1: st.markdown("<div style='font-size:2.4rem;text-align:center;'>🧮</div>", unsafe_allow_html=True)
    with c2: st.markdown("<h2 style='font-family:Bungee; color:#FF6B6B; margin:0;'>AVENTURA MATEMÀTICA</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

render_header()

if st.session_state.current_block == "Home":
    hola = f"Hola <b>{st.session_state.nom}</b>! " if st.session_state.nom.strip() else ""
    st.markdown(f"<p style='font-size:1.1rem;'>{hola}Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    # La descripcio va DINS de la columna del seu boto: aixi queda alineada
    # sempre. Abans anaven totes en una fila a part i es descolocaven en
    # arribar al final de linia. Vuit blocs: dues files de quatre.
    with st.container(key="homeblocks"):
        for fila in (BLOCKS[:4], BLOCKS[4:]):
            cols = st.columns(4)
            for col, (icon, label, block, desc) in zip(cols, fila):
                col.button(f"{icon} {label}", key=f"home_{block}", use_container_width=True,
                           on_click=start_block, args=(block,))
                col.markdown(f"<div class='desc'>{desc}</div>", unsafe_allow_html=True)
    s = st.session_state
    total = s.encerts + s.errors
    if total:
        st.markdown(
            f"<div class='scoreboard' style='margin-top:18px;'><div class='chip'>⭐ PUNTS: {s.punts}</div>"
            f"<div class='chip'>✅ ENCERTS: {round(100 * s.encerts / total)}%</div>"
            f"<div class='chip'>🔥 MILLOR RATXA: {s.millor_ratxa}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🏆 CLASSIFICACIÓ DE LA CLASSE", key="home_rank", use_container_width=True,
              on_click=lambda: st.session_state.update(current_block="Ranking"))
    st.markdown("<br>", unsafe_allow_html=True)
    if "nom_input" not in st.session_state:
        st.session_state.nom_input = st.session_state.nom
    st.text_input("Nom i cognom (per sortir a la classificació)", key="nom_input", max_chars=40,
                  placeholder="Ex: Jan Donoso", on_change=on_nom_change)
    st.session_state.nom = normalitza_nom(st.session_state.nom_input)
    carrega_base()
    if st.session_state.nom.strip() and st.session_state.base:
        b = st.session_state.base
        st.caption(f"Benvingut/da de nou! Tens {b['punts']} punts acumulats. "
                   "A la classificació surts com a **" + nom_public(st.session_state.nom.strip()) + "**.")
    elif not st.session_state.nom.strip():
        st.caption("Sense nom pots jugar igual, però no sortiràs a la classificació.")
    if st.session_state.db_error:
        st.warning("No s'ha pogut desar la puntuació: " + st.session_state.db_error)

elif st.session_state.current_block == "Ranking":
    # ---- Classificacio de la classe ----
    ss = st.session_state
    with st.container(key="maincard"):
        st.markdown("<h2 style='font-family:Bungee; color:#FF6B6B;'>🏆 CLASSIFICACIÓ</h2>", unsafe_allow_html=True)
        try:
            files = db_top(20)
            _, sense_db = get_engine()
        except Exception as e:
            files, sense_db = [], False
            st.error("No s'ha pogut llegir la classificació: " + str(e))
        jo = ss.nom.strip()
        if not files:
            st.markdown("<p>Encara no hi ha ningú. Sigues el primer! 🚀</p>", unsafe_allow_html=True)
        else:
            medalles = {1: "🥇", 2: "🥈", 3: "🥉"}
            html = ["<div style='display:flex; flex-direction:column; gap:6px;'>"]
            for i, (nom, punts, enc, err, ratxa) in enumerate(files, 1):
                tot = enc + err
                pct = round(100 * enc / tot) if tot else 0
                meu = (nom == jo)
                fons = "#FFF4CC" if meu else "white"
                vora = "3px solid #F7B731" if meu else "1px solid #EEE"
                html.append(
                    f"<div class='rank-row' style='display:flex; align-items:center; gap:12px; background:{fons};"
                    f" border:{vora}; border-radius:14px; padding:8px 14px;'>"
                    f"<div style=\"font-family:Bungee; width:46px;\">{medalles.get(i, str(i) + '.')}</div>"
                    f"<div style='flex:1; font-weight:700;'>{nom_public(nom)}</div>"
                    f"<div style='font-family:Bungee; color:#EE5253;'>⭐ {punts}</div>"
                    f"<div class='rank-pct' style='width:70px; text-align:right;'>✅ {pct}%</div>"
                    f"<div style='width:60px; text-align:right;'>🔥 {ratxa}</div></div>")
            html.append("</div>")
            st.markdown("".join(html), unsafe_allow_html=True)
            if jo and not any(n == jo for n, *_ in files):
                st.markdown(f"<p style='margin-top:10px;'>Encara no ets al top 20, "
                            f"<b>{nom_public(jo)}</b>. A jugar! 💪</p>", unsafe_allow_html=True)
        if sense_db:
            st.caption("⚠️ Sense base de dades configurada: la classificació es guarda en local i "
                       "es perdrà en cada redesplegament. Cal el secret `db_url`.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🏠 INICI", key="rank_home", use_container_width=True,
                  on_click=lambda: st.session_state.update(current_block="Home"))

elif st.session_state.repte_report is not None:
    # ---- Informe final del REPTE (l'idea de bmath: sessio curta + informe) ----
    r = st.session_state.repte_report
    pct = round(100 * r["ok"] / REPTE_LEN)
    mins, secs = divmod(int(r["secs"]), 60)
    nota = "EXCEL·LENT! 🏆" if pct >= 90 else ("MOLT BÉ! 🎉" if pct >= 70 else ("BON TREBALL! 💪" if pct >= 50 else "SEGUIM PRACTICANT! 🔄"))
    with st.container(key="maincard"):
        st.markdown(f"<h2 style='font-family:Bungee; color:#FF6B6B;'>{nota}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='scoreboard'><div class='chip'>✅ {r['ok']} / {REPTE_LEN}</div>"
            f"<div class='chip'>🎯 {pct}%</div>"
            f"<div class='chip'>⏱️ {mins}m {secs}s</div>"
            f"<div class='chip'>📈 NIVELL: {r['level'].upper()}</div></div>", unsafe_allow_html=True)
        fallats = {}
        for e in r["log"]:
            if not e["ok"]: fallats[e["kind"]] = fallats.get(e["kind"], 0) + 1
        st.markdown("<br>", unsafe_allow_html=True)
        if fallats:
            detall = " · ".join(f"{k}: {v}" for k, v in sorted(fallats.items(), key=lambda x: -x[1]))
            st.markdown(f"<p style='text-align:center;'>A repassar → <b>{detall}</b></p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center;'>Cap error. Impecable! ✨</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("🔁 UN ALTRE REPTE", key="rep_again", use_container_width=True,
                  on_click=start_block, args=("Repte",))
        c2.button("🏠 INICI", key="rep_home", use_container_width=True,
                  on_click=lambda: st.session_state.update(current_block="Home", repte_report=None))

else:
    ss = st.session_state
    lvl_slug = dict(DIFFS)[ss.diff]
    active = [f"ctl_lvl_{lvl_slug}", f"sb_lvl_{lvl_slug}"]
    if ss.current_block == "Mates":
        op_slug = {m: s for _, m, s in OPS}[ss.mode]
        active += [f"ctl_op_{op_slug}", f"sb_op_{op_slug}"]
    if ss.current_block == "Innovamat":
        active.append("sb_kind_" + slugify(ss.inno_kind))
    if ss.current_block == "Lletres":
        active = ["ctl_set_lletres"] if ss.lletra_set == "Lletres" else ["ctl_set_numeros"]
    if ss.current_block == "Colors":
        active = []
    st.markdown("<style>" + "".join(
        f".st-key-{k} button {{ background: linear-gradient(180deg,#20BF6B 0%,#0FA45B 100%) !important;"
        f" box-shadow: 0 5px 0px #0B7A45 !important; }}" for k in active) + "</style>", unsafe_allow_html=True)

    # Barra sempre visible (si la sidebar es col.lapsa, els botons segueixen aqui)
    with st.container(key="controlbar"):
        if ss.current_block == "Lletres":
            # Nomes nivell basic: aqui es tria abecedari o numeros, no dificultat
            cols = st.columns([1, 2, 2])
            cols[0].button("🏠", key="ctl_home", use_container_width=True,
                           on_click=lambda: st.session_state.update(current_block="Home"))
            cols[1].button("🔤 LLETRES", key="ctl_set_lletres", use_container_width=True,
                           on_click=set_lletra_set, args=("Lletres",))
            cols[2].button("🔢 NÚMEROS", key="ctl_set_numeros", use_container_width=True,
                           on_click=set_lletra_set, args=("Números",))
        elif ss.current_block == "Colors":
            # Nomes icones: al mobil "ANTERIOR" i "SEGÜENT" es partien en dues linies.
            # Sense help=: el tooltip embolcalla el boto i perd l'estil vermell de l'app.
            cols = st.columns([1, 1, 3, 1])
            cols[0].button("🏠", key="ctl_home", use_container_width=True,
                           on_click=lambda: st.session_state.update(current_block="Home"))
            cols[1].button("⬅️", key="ctl_dib_prev", use_container_width=True,
                           on_click=dibuix_mou, args=(-1,))
            cols[2].button("🎲 SORPRESA", key="ctl_dib_rand", use_container_width=True,
                           on_click=dibuix_mou, args=(None,))
            cols[3].button("➡️", key="ctl_dib_next", use_container_width=True,
                           on_click=dibuix_mou, args=(1,))
        else:
            cols = st.columns(4)
            cols[0].button("🏠", key="ctl_home", use_container_width=True,
                           on_click=lambda: st.session_state.update(current_block="Home"))
            for col, (label, slug) in zip(cols[1:], DIFFS):
                col.button(label.upper(), key=f"ctl_lvl_{slug}", use_container_width=True,
                           on_click=set_diff, args=(label,))
        if ss.current_block == "Mates":
            ocols = st.columns(3)
            for col, (label, mode, slug) in zip(ocols, OPS):
                col.button(label, key=f"ctl_op_{slug}", use_container_width=True,
                           on_click=set_mode, args=(mode,))

    with st.sidebar:
        st.markdown("<h2 style='font-family:Bungee;'>MENU</h2>", unsafe_allow_html=True)
        who = ss.nom.strip() or "Jugador/a"
        st.markdown(f"<div class='chip'>👦 {who} · ⭐ {ss.punts} · 🔥 {ss.ratxa}</div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🏠 INICI", key="sb_home", use_container_width=True):
            ss.current_block = "Home"; safe_rerun()
        st.markdown("---")
        if ss.current_block == "Mates":
            for label, mode, slug in OPS:
                if st.button(label, key=f"sb_op_{slug}", use_container_width=True):
                    set_mode(mode); safe_rerun()
            st.markdown("---")
        if ss.current_block == "Innovamat":
            for label, kind in INNO_KINDS:
                key = "sb_kind_" + slugify(kind)
                if st.button(label, key=key, use_container_width=True):
                    set_inno_kind(kind); safe_rerun()
            st.markdown("---")
        if ss.current_block not in SENSE_NIVELL:
            for label, slug in DIFFS:
                if st.button(label.upper(), key=f"sb_lvl_{slug}", use_container_width=True):
                    set_diff(label); safe_rerun()

    with st.container(key="maincard"):
        if ss.current_block == "Repte":
            r = ss.repte
            st.markdown(f"<h3>REPTE • {r['i'] + 1} de {REPTE_LEN} • NIVELL {ss.diff.upper()}</h3>", unsafe_allow_html=True)
            st.progress(r["i"] / REPTE_LEN)
        elif ss.current_block == "Lletres":
            (glif, paraula, dib, veu), i, total = lletres_actual()
            st.markdown(f"<h3>LLETRES I NÚMEROS • {i + 1} de {total}</h3>", unsafe_allow_html=True)
        elif ss.current_block == "Sopa":
            st.markdown(f"<h3>SOPA DE LLETRES • {ss.diff.upper()} • TROBA {len(ss.sopa['words'])} PARAULES</h3>",
                        unsafe_allow_html=True)
        elif ss.current_block == "Memory":
            st.markdown(f"<h3>MEMORY • {ss.diff.upper()} • {ss.memory['tema'].upper()} • "
                        f"{len(ss.memory['cards']) // 2} PARELLES</h3>", unsafe_allow_html=True)
        elif ss.current_block == "Colors":
            emoji, nom = DIBUIXOS[ss.dibuix_idx]
            st.markdown(f"<h3>COLOREJA • DIBUIX {ss.dibuix_idx + 1} DE {len(DIBUIXOS)} • {nom}</h3>",
                        unsafe_allow_html=True)
        else:
            extra = f" • {ss.inno_kind.upper()}" if ss.current_block == "Innovamat" else ""
            st.markdown(f"<h3>{ss.current_block.upper()} • {ss.diff.upper()}{extra}</h3>", unsafe_allow_html=True)

        if ss.current_block == "Lectura":
            st.markdown(f"<div class='race-track'><div class='car' style='left:{ss.reading_pos}%;'>🏎️</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='race-track' style='background:#444;'><div class='car' style='left:{ss.rival_pos}%; filter:hue-rotate(90deg);'>🏎️</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='problem-box' style='border-color:#4BCffa;'>{ss.reading_word}</div>", unsafe_allow_html=True)
            bcol, rcol = st.columns([3, 1])
            rcol.button("🔄 REINICIAR", key="lec_reset", use_container_width=True,
                        help="Torna els cotxes a la sortida", on_click=reset_lectura)
            if bcol.button("LLEGIT! ✅", use_container_width=True):
                elapsed = time.time() - ss.word_start_time
                # Sense cartells ni bloquejos: sempre avances. Pero si claques
                # sense haver llegit, el rival avanca mes que tu i acabes perdent.
                minim = max(0.7, 0.16 * len(ss.reading_word))
                spd = {"Fàcil": 1.5, "Normal": 4.5, "Difícil": 4.5}[ss.diff]
                ss.reading_pos += 10
                ss.rival_pos += 12 if elapsed < minim else 5 + (elapsed - minim) * spd
                if ss.reading_pos >= 90:
                    ss.last_status = "correct"; ss.reading_pos = ss.rival_pos = 0
                    ss.punts += 5
                elif ss.rival_pos >= 90:
                    ss.last_status = "incorrect"; ss.reading_pos = ss.rival_pos = 0
                new_problem()
                safe_rerun()
        elif ss.current_block == "Lletres":
            (glif, paraula, dib, veu), i, total = lletres_actual()
            if ss.lletra_set == "Lletres":
                rotul = f"{glif} {glif.lower()}"
                peu = f"<b>{glif}</b> de <b>{paraula}</b> {dib}"
            else:
                rotul = glif
                peu = f"<b>{glif}</b> · {paraula} <span style='font-size:1.4rem;'>{dib}</span>"
            st.markdown(
                f"<div style='text-align:center; font-family:Bungee; font-size:2.6rem;"
                f" color:#EE5253; line-height:1;'>{rotul}</div>"
                f"<p style='text-align:center; font-size:1.25rem; margin:6px 0 2px 0;'>{peu}</p>",
                unsafe_allow_html=True)
            if ss.lletra_set == "Lletres":
                frase = f"Lletra {veu}, {de_o_d(paraula)}."
            elif glif == "0":
                frase = "Número zero. Cap poma."
            else:
                quantitat = "una poma" if glif == "1" else f"{veu} pomes"
                frase = f"Número {veu}. {quantitat.capitalize()}."
            canvas_caligrafia(glif, f"{ss.lletra_set}-{i}", frase)
            nav = st.columns(2)
            nav[0].button("⬅️ ANTERIOR", key="lle_prev", use_container_width=True,
                          on_click=lletres_mou, args=(-1,))
            nav[1].button("SEGÜENT ➡️", key="lle_next", use_container_width=True,
                          on_click=lletres_mou, args=(1,))
        elif ss.current_block == "Sopa":
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Arrossega el dit o el ratolí "
                        "per sobre de les lletres, en línia recta, per marcar cada paraula.</p>",
                        unsafe_allow_html=True)
            sopa_component(ss.sopa, f"{ss.diff}-{ss.sopa_n}")
            # El clica sol el component quan s'han trobat totes (CSS: invisible)
            st.button("fet", key="sopa_done", on_click=sopa_completada)
            st.button("🔁 NOVA SOPA", key="sopa_nova", use_container_width=True, on_click=new_problem)
        elif ss.current_block == "Memory":
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Toca dues cartes. "
                        "Si són iguals, es queden girades. Troba totes les parelles!</p>",
                        unsafe_allow_html=True)
            memory_component(ss.memory, f"{ss.diff}-{ss.memory_n}")
            st.button("fet", key="memory_done", on_click=memory_completat)
            st.button("🔁 NOVA PARTIDA", key="memory_nova", use_container_width=True, on_click=new_problem)
        elif ss.current_block == "Colors":
            emoji, nom = DIBUIXOS[ss.dibuix_idx]
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Tria un color de la paleta. "
                        "Amb 🪣 OMPLE toques una zona i s'omple; amb 🖌️ PINTA pintes lliurement.</p>",
                        unsafe_allow_html=True)
            coloreja_component(emoji, nom, f"dib-{ss.dibuix_idx}")
        else:
            body = ss.problem_html or ss.problem_text
            mida = "" if ss.problem_html or len(ss.problem_text) <= 22 else (
                "font-size:1.5rem; line-height:1.25;" if len(ss.problem_text) <= 48 else
                "font-size:1.15rem; line-height:1.3;")
            st.markdown(f"<div class='problem-box' style='{mida}'>{body}</div>", unsafe_allow_html=True)
            if ss.attempts == 1:
                st.markdown("<p style='font-family:Bungee; color:#EE5253; text-align:center;'>GAIREBÉ! TENS UN ALTRE INTENT 💪</p>", unsafe_allow_html=True)
            with st.form(key=f"form_{ss.input_key}", clear_on_submit=True, border=False):
                val = st.number_input("Resultat?", step=1, value=None, label_visibility="collapsed")
                submitted = st.form_submit_button("COMPROVAR! 🚀", use_container_width=True)
            autofocus_answer(f"{ss.input_key}|{ss.problem_text}|{ss.attempts}")
            if submitted:
                if val is None:
                    st.warning("Escriu un número abans de comprovar 😉")
                else:
                    check_answer(int(val)); safe_rerun()
        if ss.current_block not in SENSE_NIVELL:
            st.markdown(f"<div class='scoreboard'><div class='chip'>⭐ {ss.punts}</div><div class='chip'>🔥 RATXA: {ss.ratxa}</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- OVERLAY
if st.session_state.last_status:
    status = st.session_state.last_status
    st.session_state.last_status = None
    if status == "correct":
        gif = random.choice([g for g in CELEBRATION_GIFS if g != st.session_state.last_gif])
        msg = random.choice([m for m in CELEBRATION_MESSAGES if m != st.session_state.last_msg])
        st.session_state.last_gif, st.session_state.last_msg = gif, msg
        st.markdown(f"<div class='gif-overlay'><img src='{gif}'><h1 style='font-family:Bungee; color:#FF6B6B; font-size:3rem; margin-top:20px;'>{msg} 🎉</h1></div>", unsafe_allow_html=True)
        time.sleep(2)
    elif status == "reveal":
        st.markdown(f"<div class='gif-overlay' style='background:rgba(255,159,67,0.95);'><h1 style='font-family:Bungee; color:white; font-size:2.2rem;'>LA RESPOSTA ERA:</h1><h1 style='font-family:Bungee; color:white; font-size:4rem;'>{st.session_state.reveal}</h1><p style='font-family:Bungee; color:white;'>SEGUIM! 💪</p></div>", unsafe_allow_html=True)
        time.sleep(3)
    else:
        st.markdown("<div class='gif-overlay' style='background:rgba(244,67,54,0.9);'><h1 style='font-family:Bungee; color:white; font-size:3rem;'>PROVA DE NOU! 🔄</h1></div>", unsafe_allow_html=True)
        time.sleep(1.5)
    safe_rerun()
