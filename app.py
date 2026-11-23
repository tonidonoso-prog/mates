import copy
import hashlib
import threading
import uuid
import urllib.parse
import urllib.request
import streamlit as st
import streamlit.components.v1 as components
import random
import time
import json
import re
import importlib
import concurs_temes as CT
import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Aventura Matemàtica", page_icon="🧮", layout="wide", initial_sidebar_state="expanded")

BLOCKS = [
    ("🧮", "MATES", "Mates", "Sumes, restes i taules"),
    ("💡", "CÀLCUL MENTAL", "Calcul", "Amics, dobles, sèries i piràmides"),
    ("📖", "LECTURA", "Lectura", "Carrera de lectura"),
    ("✏️", "LLETRES I NÚMEROS", "Lletres", "Resseguir lletres i números amb el dit"),
    ("🔍", "SOPA DE LLETRES", "Sopa", "Troba les paraules amagades"),
    ("🧠", "MEMORY", "Memory", "Gira les cartes i troba les parelles"),
    ("🔠", "PENJAT", "Penjat", "Endevina la paraula lletra a lletra"),
    ("🎨", "COLOREJA", "Colors", "Pinta més de 100 dibuixos amb la paleta"),
    ("👾", "MONSTRE GOLUT", "Golut", "Dona-li els plats que fan el seu número"),
    ("🎯", "KAHOOT", "Concurs", "Sol o en grup, amb una pantalla gran"),   # nom triat pel Toni (23 nov 2026)
    ("🏆", "REPTE", "Repte", "10 exercicis i informe final"),
]
SENSE_NIVELL = ("Lletres", "Colors")   # blocs sense Facil/Normal/Dificil
# nom que es veu a la capcalera (la clau interna es curta: Calcul, Sopa...)
NOM_BLOC = {block: label for _, label, block, _ in BLOCKS}

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
CALCUL_KINDS = [("TOTS", "Tots"), ("AMICS", "Amics"), ("DESCOMPON", "Descompon"),
              ("DOBLES", "Dobles"), ("MEITATS", "Meitats"), ("SÈRIES", "Sèries"),
              ("PIRÀMIDE", "Piràmide"), ("REPARTIR", "Repartir"), ("DESENES", "Desenes"),
              ("QUÈ FALTA", "Inversa"), ("SUMA DE 3", "Suma3"), ("PROBLEMES", "Problema")]
CALCUL_ALL = [k for _, k in CALCUL_KINDS if k != "Tots"]


def slugify(txt):
    """Clau CSS segura a partir d'un nom amb accents.

    Es diu slugify i no slug perque els bucles de DIFFS i OPS fan servir una
    variable 'slug', i abans tapaven la funcio -> TypeError al bloc de calcul."""
    return "".join(c if c.isalnum() else "_" for c in
                   txt.lower().replace("è", "e").replace("é", "e").replace("à", "a")
                      .replace("í", "i").replace("ó", "o").replace("ú", "u"))
REPTE_LEN = 10  # exercicis per sessio
BASE_DIR = Path(__file__).parent


def _signatura_temes():
    fs = [BASE_DIR / "concurs_temes.py", *sorted((BASE_DIR / "temes_extra").glob("*.py"))]
    return tuple((f.name, f.stat().st_mtime_ns) for f in fs if f.exists())


# Streamlit Cloud torna a llegir app.py a cada canvi pero NO els moduls que importa: si nomes
# canviaven les preguntes, l'app seguia amb les velles (23 nov 2026). Es recarrega si han canviat.
if getattr(CT, "_signatura", None) != _signatura_temes():
    CT = importlib.reload(CT)
    CT._signatura = _signatura_temes()

# Cap nom: hi juguen menors i son dades protegides (17 nov 2026, el Toni: "no podemos dar en ningun
# sitio que escriban el nombre, es confidencial"). Cada mobil o tauleta te un identificador a l'atzar
# (guardat al navegador, 'am_dispositiu'); a la base de dades nomes hi van aquest numero, els totals i els dies.


@st.cache_resource
def _secret(clau):
    try:
        return st.secrets.get(clau)
    except Exception:
        return None


def _api():
    """(url, clau) del servidor propi (osuhosting) si estan configurats."""
    url, key = _secret("api_url"), _secret("api_key")
    return (url, key) if url and key else None


def _api_crida(accio, dades=None):
    cfg = _api()
    cos = json.dumps({"accio": accio, **(dades or {})}).encode()
    req = urllib.request.Request(cfg[0], data=cos, headers={
        "Content-Type": "application/json", "X-Mates-Key": cfg[1]})
    with urllib.request.urlopen(req, timeout=10) as r:
        resposta = json.loads(r.read().decode())
    if not resposta.get("ok"):
        raise RuntimeError(resposta.get("error", "resposta invalida del servidor"))
    return resposta


def get_engine():
    """Postgres/MySQL si hi ha secret 'db_url', si no SQLite local.

    IMPORTANT: a Streamlit Cloud el disc s'esborra a cada redesplegament, o sigui
    que SQLite alla nomes serveix per provar. De debo es fa servir el servidor
    propi (secrets 'api_url' + 'api_key').
    """
    url = _secret("db_url")
    fallback = not url
    eng = create_engine(url or f"sqlite:///{BASE_DIR / 'progres.db'}", pool_pre_ping=True)
    with eng.begin() as c:
        c.execute(text("""
            CREATE TABLE IF NOT EXISTS progres (
                clau VARCHAR(32) PRIMARY KEY,
                punts INTEGER DEFAULT 0,
                encerts INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                millor_ratxa INTEGER DEFAULT 0,
                partides INTEGER DEFAULT 0,
                actualitzat VARCHAR(32)
            )"""))
        c.execute(text("""
            CREATE TABLE IF NOT EXISTS dies (
                clau VARCHAR(32),
                dia VARCHAR(10),
                PRIMARY KEY (clau, dia)
            )"""))
    return eng, fallback


BUIT = {"punts": 0, "encerts": 0, "errors": 0, "millor_ratxa": 0, "partides": 0, "dies": []}


def db_load(jugador):
    """Progres d'un nen: totals i els dies que ha jugat ('2026-09-25')."""
    clau = jugador if clau_ok(jugador) else ""
    if not clau:
        return dict(BUIT)
    if _api():
        return {**BUIT, **(_api_crida("jugador", {"clau": clau}).get("jugador") or {})}
    eng, _ = get_engine()
    with eng.begin() as c:
        r = c.execute(text("SELECT punts, encerts, errors, millor_ratxa, partides"
                           " FROM progres WHERE clau = :c"), {"c": clau}).fetchone()
        dies = [d for (d,) in c.execute(text("SELECT dia FROM dies WHERE clau = :c ORDER BY dia"),
                                        {"c": clau}).fetchall()]
    fila = dict(BUIT) if not r else {"punts": r[0], "encerts": r[1], "errors": r[2],
                                     "millor_ratxa": r[3], "partides": r[4]}
    fila["dies"] = dies
    return fila


def db_save(jugador, punts, encerts, errors, millor_ratxa, partides):
    """Escriu el TOTAL (base d'abans + el d'aquesta sessio). Idempotent.

    No hi viatja cap nom: nomes l'identificador del dispositiu."""
    clau = jugador if clau_ok(jugador) else ""
    if not clau:
        return
    dades = {"clau": clau, "punts": punts, "encerts": encerts,
             "errors": errors, "millor_ratxa": millor_ratxa, "partides": partides}
    if _api():
        _api_crida("desa", dades)
        return
    eng, _ = get_engine()
    fila = {"c": clau, "p": punts, "e": encerts, "x": errors, "r": millor_ratxa,
            "g": partides, "t": datetime.datetime.now().isoformat(timespec="seconds")}
    with eng.begin() as c:
        fet = c.execute(text("""
            UPDATE progres SET punts = :p, encerts = :e, errors = :x,
                   millor_ratxa = :r, partides = :g, actualitzat = :t
             WHERE clau = :c"""), fila)
        if not fet.rowcount:      # sense ON CONFLICT: funciona igual a SQLite, Postgres i MySQL
            c.execute(text("""
                INSERT INTO progres (clau, punts, encerts, errors, millor_ratxa, partides, actualitzat)
                VALUES (:c, :p, :e, :x, :r, :g, :t)"""), fila)


def db_marca_dia(jugador, dia):
    """Apunta que en aquest dispositiu s'han fet exercicis el dia 'dia' (text 'AAAA-MM-DD')."""
    clau = jugador if clau_ok(jugador) else ""
    if not clau:
        return
    if _api():
        _api_crida("dia", {"clau": clau, "dia": dia})
        return
    eng, _ = get_engine()
    with eng.begin() as c:
        ja = c.execute(text("SELECT 1 FROM dies WHERE clau = :c AND dia = :d"),
                       {"c": clau, "d": dia}).fetchone()
        if not ja:
            c.execute(text("INSERT INTO dies (clau, dia) VALUES (:c, :d)"), {"c": clau, "d": dia})


# ------------------------------------------------------------- calendari i medalles
# Sense competicio (25 set 2026, el Toni): cada nen nomes veu les SEVES medalles.
# Un dia sense jugar no resta res ni surt en vermell: nomes se sumen dies bons.
ZONA = ZoneInfo("Europe/Madrid")
MESOS = ["GENER", "FEBRER", "MARÇ", "ABRIL", "MAIG", "JUNY", "JULIOL", "AGOST",
         "SETEMBRE", "OCTUBRE", "NOVEMBRE", "DESEMBRE"]
DIES_SETMANA = ["DL", "DT", "DC", "DJ", "DV", "DS", "DG"]


def avui():
    return datetime.datetime.now(ZONA).date()


def _dates(dies):
    out = set()
    for d in dies:
        try:
            out.add(datetime.date.fromisoformat(d))
        except (TypeError, ValueError):
            pass
    return out


def _per_setmana(dates):
    setmanes = {}
    for d in dates:
        setmanes.setdefault(d.isocalendar()[:2], set()).add(d.weekday())
    return setmanes


def _per_mes(dates):
    mesos = {}
    for d in dates:
        mesos[(d.year, d.month)] = mesos.get((d.year, d.month), 0) + 1
    return mesos


# (id, emoji, nom, com s'aconsegueix, condicio sobre el conjunt de dates jugades)
MEDALLES = [
    ("primer", "🌱", "PRIMER DIA", "Fes el primer exercici", lambda ds: len(ds) >= 1),
    ("tres", "🔥", "3 DIES EN UNA SETMANA", "Juga 3 dies de la mateixa setmana",
     lambda ds: any(len(v) >= 3 for v in _per_setmana(ds).values())),
    ("setmana", "🏅", "SETMANA COMPLETA", "Juga de dilluns a divendres",
     lambda ds: any({0, 1, 2, 3, 4} <= v for v in _per_setmana(ds).values())),
    ("d5", "🥉", "5 DIES", "Juga 5 dies diferents", lambda ds: len(ds) >= 5),
    ("d10", "🥈", "10 DIES", "Juga 10 dies diferents", lambda ds: len(ds) >= 10),
    ("mes", "🌟", "12 DIES EN UN MES", "Juga 12 dies del mateix mes",
     lambda ds: any(v >= 12 for v in _per_mes(ds).values())),
    ("d20", "🥇", "20 DIES", "Juga 20 dies diferents", lambda ds: len(ds) >= 20),
    ("d30", "🏆", "30 DIES", "Juga 30 dies diferents", lambda ds: len(ds) >= 30),
    ("d50", "💎", "50 DIES", "Juga 50 dies diferents", lambda ds: len(ds) >= 50),
    ("d100", "👑", "100 DIES", "Juga 100 dies diferents", lambda ds: len(ds) >= 100),
]


def medalles_guanyades(dies):
    ds = _dates(dies)
    return [m for m in MEDALLES if m[4](ds)]


def marca_avui():
    """Es crida a cada exercici fet (encertat o no: compta l'esforc). El primer
    del dia dona la medalla del dia i, si toca, alguna medalla especial."""
    ss = st.session_state
    dia = avui().isoformat()
    if dia in ss.dies:
        return
    abans = {m[0] for m in medalles_guanyades(ss.dies)}
    ss.dies = sorted(set(ss.dies) | {dia})
    n = len(ss.dies)
    if n == 1:      # el primer dia, un sol missatge (abans sortien dos que deien el mateix)
        ss.avisos.append(("⭐ 🌱", "LA TEVA PRIMERA MEDALLA!", "CADA DIA QUE JUGUIS EN GUANYES UNA"))
    else:
        ss.avisos.append(("⭐", "MEDALLA DEL DIA!", f"JA EN TENS {n}"))
    for m in medalles_guanyades(ss.dies):
        if m[0] not in abans and m[0] != "primer":
            ss.avisos.append((m[1], "NOVA MEDALLA!", m[2]))
    if ss.jugador and ss.base is not None:
        try:
            db_marca_dia(ss.jugador, dia)
        except Exception as e:
            ss.db_error = str(e)


DISPOSITIU = "am_dispositiu"


def clau_ok(c):
    return isinstance(c, str) and len(c) == 16 and all(x in "0123456789abcdef" for x in c)


def on_dispositiu():
    """El JS de dispositiu_html() ha escrit l'identificador d'aquest mobil o tauleta al camp amagat."""
    c = st.session_state.get("dispositiu", "")
    if clau_ok(c) and c != st.session_state.jugador:
        st.session_state.jugador = c
        carrega_base()


def dispositiu_html():
    # Un numero a l'atzar guardat al navegador (localStorage), que no diu res de qui hi juga.
    # Abans era una galeta, pero Streamlit Cloud no la fa arribar a l'app (17 nov 2026).
    return """<script>
(function(){
  var d = window.parent.document, w = window.parent, K = '""" + DISPOSITIU + """', id = '';
  try { id = w.localStorage.getItem(K) || ''; } catch(e) {}
  if (!/^[0-9a-f]{16}$/.test(id)) {
    var a = new Uint8Array(8); w.crypto.getRandomValues(a);
    id = Array.prototype.map.call(a, function(x){ return ('0' + x.toString(16)).slice(-2); }).join('');
    try { w.localStorage.setItem(K, id); } catch(e) {}
  }
  var n = 0, t = setInterval(function(){
    var el = d.querySelector('.st-key-dispositiu input');
    if (++n > 100) { clearInterval(t); return; }
    if (!el) return;
    clearInterval(t);
    if (el.value === id) return;
    var set = Object.getOwnPropertyDescriptor(w.HTMLInputElement.prototype, 'value').set;
    set.call(el, id);
    el.dispatchEvent(new w.Event('input', {bubbles: true}));
    ['keydown', 'keypress'].forEach(function(tipus){
      el.dispatchEvent(new w.KeyboardEvent(tipus, {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, charCode: 13, bubbles: true}));
    });
  }, 100);
})();
</script>"""


# Animacions per felicitar: emojis animats de Google (Noto Emoji Animation, CC BY 4.0), servits
# des de la propia app (static/festa/, .streamlit/config.toml). Abans eren GIFs de Giphy: alguns
# sortien en negre o amb interrogants i cada GIF enviava la IP del nen a un tercer (17 nov 2026).
# Revisats un a un mirant-ne els fotogrames: fora els de fons fosc (focs artificials) i els que
# no feien festa. Per afegir-ne: deixar el .webp a static/festa/.
CELEBRATION_GIFS = sorted(f"app/static/festa/{f.name}" for f in (BASE_DIR / "static" / "festa").glob("*.webp"))
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
    # afegits el 9 set 2026: mes animals, dinosaures i personatges (el Toni volia Disney,
    # Patrulla Canina i Sonic: no es pot per drets d'autor; per a dibuixos propis hi ha
    # la carpeta dibuixos/ de sota)
    ("🦕", "DINOSAURE DE COLL LLARG"), ("🦩", "FLAMENC"), ("🦭", "FOCA"), ("🦥", "PERESÓS"),
    ("🦦", "LLÚDRIA"), ("🦙", "LLAMA"), ("🐫", "CAMELL"), ("🦌", "CÉRVOL"), ("🐆", "LLEOPARD"),
    ("🐺", "LLOP"), ("🦅", "ÀGUILA"), ("🦢", "CIGNE"), ("🦂", "ESCORPÍ"),
    ("🥷", "NINJA"), ("🧞", "GENI"), ("👸", "PRINCESA"), ("🤴", "PRÍNCEP"), ("🧛", "VAMPIR"),
    ("🎅", "PARE NOEL"), ("🏎️", "COTXE DE CURSES"), ("🚓", "COTXE DE POLICIA"),
    ("🚑", "AMBULÀNCIA"), ("🚢", "VAIXELL"), ("🛵", "MOTO"), ("🎡", "NÒRIA"),
    ("🎢", "MUNTANYA RUSSA"), ("🎮", "VIDEOJOC"),
]
assert len(set(e for e, _ in DIBUIXOS)) == len(DIBUIXOS), "dibuix repetit"
# Dibuixos propis: fitxers PNG/JPG a mates/dibuixos/ (contorn negre sobre blanc). El nom del
# fitxer es el titol (rei_lleo.png -> REI LLEO). Es carreguen com a capa de linies.
def _dibuixos_propis():
    out = []
    carpeta = BASE_DIR / "dibuixos"
    if not carpeta.is_dir():
        return out
    import base64
    for f in sorted(carpeta.iterdir()):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg") and f.stat().st_size < 1_500_000:
            mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
            data = base64.b64encode(f.read_bytes()).decode()
            out.append((f"data:{mime};base64,{data}", f.stem.replace("_", " ").replace("-", " ").upper()))
    return out
DIBUIXOS = _dibuixos_propis() + DIBUIXOS


def dibuix_font(emoji):
    """Que es passa al component: el SVG de linia d'OpenMoji (dibuixos_svg/<hex>.svg,
    nitid a qualsevol mida) com a data URI; si no hi es, l'emoji (contorn calculat)."""
    if emoji.startswith("data:image"):
        return emoji
    hexcode = "-".join(f"{ord(c):04X}" for c in emoji if ord(c) != 0xFE0F)
    f = BASE_DIR / "dibuixos_svg" / f"{hexcode}.svg"
    if f.is_file():
        import base64
        return "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()
    return emoji
# lletres de farciment amb la frequencia aproximada del catala
SOPA_FARCIT = "AAAAAEEEEEIIIOOOOUURRRSSSTTTLLLNNNMMCCDDPPBGVFXJZH"


# ---- Penjat: paraules en catala amb la seva pista. El nivell el marca la llargada
# (Facil 3-5 lletres, Normal 6-8, Dificil 9 o mes). Els accents no compten: la A
# del teclat destapa A i A amb accent; la C-trencada te tecla propia.
PENJAT_PARAULES = {
    "ANIMAL": ["GAT", "GOS", "LLOP", "PORC", "VACA", "RATA", "MICO", "ÀNEC", "LLEÓ", "DOFÍ",
               "PEIX", "GALL", "ZEBRA", "TIGRE", "OVELLA", "CAVALL", "CONILL", "GIRAFA",
               "BALENA", "POLLET", "CARGOL", "ABELLA", "GRANOTA", "TORTUGA", "FORMIGA",
               "ELEFANT", "ESQUIROL", "PINGÜÍ", "CANGUR", "COCODRIL", "PAPALLONA",
               "HIPOPÒTAM", "RINOCERONT", "DINOSAURE", "CAMALEÓ", "ESCARABAT", "RATPENAT",
               "GUINEU", "MARIETA",
               "SARGANTANA", "ORANGUTAN", "ROSSINYOL", "TARÀNTULA", "ORNITORRINC", "LLANGARDAIX"],
    "MENJAR": ["POMA", "PERA", "MEL", "LLET", "SOPA", "PASTÍS", "GALETA", "TARONJA", "MADUIXA",
               "PLÀTAN", "LLIMONA", "CIRERA", "XOCOLATA", "ESPAGUETIS", "MACARRONS",
               "CROQUETA", "ENTREPÀ", "MANDARINA", "SÍNDRIA", "MELÓ", "FORMATGE", "IOGURT",
               "PIZZA", "TRUITA", "CARBASSA", "PASTANAGA", "ENSALADA", "MAGDALENA", "GELAT",
               "MACEDÒNIA", "HAMBURGUESA", "MANDONGUILLES", "PANELLETS", "MELMELADA", "NECTARINA"],
    "COSA DE CASA": ["TAULA", "CADIRA", "LLIT", "PORTA", "SOFÀ", "CUINA", "FINESTRA", "NEVERA",
                     "DUTXA", "ARMARI", "LÀMPADA", "TOVALLOLA", "RENTADORA", "ESCALA", "COIXÍ",
                     "MIRALL", "TELEVISIÓ", "ESCOMBRA", "RELLOTGE", "CULLERA", "FORQUILLA",
                     "DESPERTADOR", "RENTAPLATS", "ASPIRADORA", "PRESTATGERIA", "CALAIXERA", "MICROONES"],
    "TRANSPORT": ["TREN", "COTXE", "MOTO", "AVIÓ", "VAIXELL", "CAMIÓ", "BICICLETA", "HELICÒPTER",
                  "AUTOBÚS", "SUBMARÍ", "AMBULÀNCIA", "TRACTOR", "PATINET", "COET", "FURGONETA",
                  "GLOBUS", "CARAVANA",
                  "MOTOCICLETA", "FORMIGONERA", "EXCAVADORA", "TELEFÈRIC", "PARACAIGUDES"],
    "NATURA": ["SOL", "MAR", "RIU", "LLUNA", "ARBRE", "FLOR", "NEU", "PLUJA", "NÚVOL", "ESTRELLA",
               "MUNTANYA", "PLATJA", "BOSC", "VOLCÀ", "TEMPESTA", "CASCADA", "PLANETA", "GIRASOL",
               "FULLA", "SORRA", "ROCA", "LLAMP",
               "TERRATRÈMOL", "MARGARIDA", "PRIMAVERA"],
    "ESCOLA": ["LLIBRE", "LLAPIS", "GOMA", "ESTOIG", "MOTXILLA", "PISSARRA", "PAPERERA", "TISORES",
               "CALCULADORA", "ORDINADOR", "PUPITRE", "PATI", "LLIBRETA", "REGLE", "RETOLADOR",
               "BIBLIOTECA", "COMPANYS",
               "ENCICLOPÈDIA", "DICCIONARI", "MATEMÀTIQUES", "MAQUINETA", "GRAPADORA", "ESBORRADOR"],
    "COS": ["NAS", "ULL", "DIT", "BOCA", "CAP", "ORELLA", "GENOLL", "ESQUENA", "CABELL", "DENTS",
            "COLZE", "MELIC", "PANXA", "TURMELL", "ESPATLLA", "CELLES",
            "PESTANYES", "COSTELLES", "CERVELL", "ESQUELET"],
}
# errors = vides; pista = es mostra la categoria; destapa = lletres que es veuen d'entrada
PENJAT_CFG = {
    "Fàcil":   {"llarg": (3, 5),  "errors": 8, "pista": True,  "destapa": "primera", "bonus": 2},
    "Normal":  {"llarg": (6, 8),  "errors": 7, "pista": True,  "destapa": "",        "bonus": 3},
    "Difícil": {"llarg": (9, 20), "errors": 6, "pista": False, "destapa": "",        "bonus": 5},
}
PENJAT_ACCENTS = str.maketrans("ÀÈÉÍÏÒÓÚÜ", "AEEIIOOUU")


def penjat_base(ch):
    """Lletra del teclat que destapa aquest caracter (À -> A, Ç -> Ç)."""
    return ch.translate(PENJAT_ACCENTS)


def genera_penjat(diff, evita=()):
    cfg = PENJAT_CFG[diff]
    lo, hi = cfg["llarg"]
    pool = sorted({(w, cat) for cat, ws in PENJAT_PARAULES.items() for w in ws
                   if lo <= len(w) <= hi and w not in evita})
    if not pool:          # tot vist: tornem a comencar
        return genera_penjat(diff)
    w, cat = random.choice(pool)
    visibles = sorted({penjat_base(w[0])}) if cfg["destapa"] == "primera" else []
    return {"paraula": w, "cat": cat, "level": diff, "errors": cfg["errors"],
            "pista": cfg["pista"], "visibles": visibles}


# ---- Monstre golut: el monstre demana un numero i cal donar-li els plats que,
# junts, el fan (sumant o multiplicant). k = plats que cal triar.
GOLUT_OPS = [("➕ SUMA", "suma"), ("✖️ MULTIPLICACIÓ", "mult")]
GOLUT_CFG = {
    "suma": {
        "Fàcil":   {"k": 2, "plats": 6, "nums": (1, 10), "objectiu": (5, 10)},
        "Normal":  {"k": 2, "plats": 8, "nums": (1, 15), "objectiu": (11, 20)},
        "Difícil": {"k": 3, "plats": 8, "nums": (1, 12), "objectiu": (12, 25)},
    },
    "mult": {
        "Fàcil":   {"k": 2, "plats": 6, "nums": (1, 10), "taules": (2, 5, 10)},
        "Normal":  {"k": 2, "plats": 8, "nums": (1, 10), "taules": (2, 3, 4, 5, 6, 7, 8, 9)},
        # amb 3 plats nomes sortien 9 objectius diferents: millor les taules dificils
        "Difícil": {"k": 2, "plats": 8, "nums": (1, 10), "taules": (6, 7, 8, 9)},
    },
}


def golut_valor(nums, op):
    total = 0 if op == "suma" else 1
    for n in nums:
        total = total + n if op == "suma" else total * n
    return total


def genera_golut(diff, op, evita=()):
    """Un monstre: objectiu, plats (tots diferents) i una solucio garantida."""
    cfg = GOLUT_CFG[op][diff]
    k, (lo, hi) = cfg["k"], cfg["nums"]
    for _ in range(500):
        if op == "suma":
            sol = random.sample(range(lo, hi + 1), k)
            objectiu = sum(sol)
            if not cfg["objectiu"][0] <= objectiu <= cfg["objectiu"][1]:
                continue
        else:
            if k == 2:
                a = random.choice(cfg["taules"])
                b = random.randint(2, 10)
                sol = [a, b]
            else:
                sol = random.sample(cfg["taules"], 3)
            if len(set(sol)) < k:      # 5 x 5 necessitaria dos plats iguals
                continue
            objectiu = golut_valor(sol, op)
        if objectiu in evita:
            continue
        resta = [n for n in range(lo, hi + 1) if n not in sol]
        plats = sol + random.sample(resta, cfg["plats"] - k)
        random.shuffle(plats)
        return {"objectiu": objectiu, "plats": plats, "solucio": sorted(sol),
                "k": k, "op": op, "level": diff}
    raise RuntimeError("No s'ha pogut generar el monstre")


# ======================================================================= CONCURS
# Joc de preguntes contra rellotge, a l'estil dels concursos de la tele (15 nov 2026).
# Cada nen juga SOL a la seva tauleta: tria tema, 10 preguntes amb compte enrere, quatre
# respostes de colors i mes punts com mes rapid. Al final, el seu propi record.
# Primera versio: un mestre creava la partida i els nens hi entraven amb un codi. El Toni
# no vol codis ni dependre d'un adult ("no hagas password"; "¿no pueden jugar solos?").
# Sense classificacio ni comparacio amb ningu (decisio del 25 set 2026).
# 23 nov 2026: 70 temes en 12 categories (concurs_temes.py). Es tria primer la categoria.
CONCURS_TEMES = ([("🎲 BARREJA DE TOT", "barreja")]
                 + [(f"🎲 BARREJA · {nom.split(' ', 1)[1]}", f"barreja_{cat}") for cat, nom in CT.CATEGORIES]
                 + [(label, tid) for tid, label, _ in CT.TEMES])
CONCURS_DE_APP = ("sumes", "restes", "taules", "calcul", "animals", "lletra")   # es generen aqui
# formes i colors propis (no els de cap joc comercial)
CONCURS_FORMES = [("★", "#8854D0", "#5F3A99"), ("●", "#FA8231", "#B85A1C"),
                  ("▲", "#0FB9B1", "#0A817B"), ("■", "#EB3B8F", "#A82563")]
# "Quina lletra falta?": cap opcio falsa pot formar una altra paraula (S_L: SAL tambe
# valdria) ni una paraula lletja. Paraules curtes molt comunes + les de les altres llistes.
CONCURS_PARAULES_COMUNES = set("""
SAL SOL SUL MAR MOR MUR PAL PEL PIL POL GOL GEL GAL BOL COL CEL MEL VOL FIL FAL FEL VEL
NAS NOS NUS PAS PES POS PUS GAT GOT GIT MAT MOT MIT RAT ROT PAT POT PIT BOT BAT BIT
DIT DAT FET FAT FIT FOT LLIT LLET LLAT CAP COP CUP SAP SOP MAL MEL MIL MOL CAR COR CUR
PAN PEN PIN PON PUN PAU PEU POU BOU NOU NAU SOU SEU CEU MEU TEU TOU VEU VAU RIU REU
CASA COSA CUSA MASA MESA MOSA ROSA RASA BASE BOSC BASC RODA RADA RIDA PILA PALA POLA PULA
BOLA BALA BELA GOMA GAMA COMA CAMA FAMA FUMA LLUNA LLANA TAULA TEULA PORTA PARTA POMA
PEIX PIXA GALL GOLL TREN TRON NENA NANA NONA VACA VECA RATA ROTA MICO MACO MOCO MOTO
""".split())
CONCURS_PARAULES_LLETGES = set("MORO PUTA PUTO CACA POLLA PITO CULO MEAR MERDA TONTO TONTA".split())
CONCURS_N = 10                                            # preguntes per partida
CONCURS_SEGONS = {"Fàcil": 25, "Normal": 20, "Difícil": 15}
CONCURS_PAUSA = 2.5           # segons que es veu si l'ha encertada abans de la seguent
# blocs nous: a la portada surten daurats i amb "NOU!" fins a aquesta data
NOU_FINS = {"Concurs": datetime.date(2026, 12, 15)}


def _opcions_numeriques(ans):
    """La bona i tres d'enganyoses a prop (mai negatives ni repetides)."""
    pool = [ans + d for d in (-10, -5, -2, -1, 1, 2, 5, 10) if ans + d >= 0]
    random.shuffle(pool)
    falses = []
    for v in sorted(pool, key=lambda v: abs(v - ans) + random.random() * 4):
        if v != ans and v not in falses:
            falses.append(v)
        if len(falses) == 3:
            break
    return [str(ans)] + [str(v) for v in falses]


def concurs_pregunta(tema, diff):
    """{text, emoji, opcions (4), correcta (index)}. Tot generat: mai s'acaben."""
    if tema == "barreja":
        tema = random.choice([t for t, _, _ in CT.TEMES])
    elif tema.startswith("barreja_"):
        tema = random.choice([t for t, _ in CT.temes_de(tema[len("barreja_"):])])
    if tema not in CONCURS_DE_APP:
        return CT.pregunta(tema, diff)
    emoji = ""
    if tema in ("sumes", "restes"):
        text, ans = make_math(diff, "Sumes" if tema == "sumes" else "Restes")
        text, ops = f"{text} = ?", _opcions_numeriques(ans)
    elif tema == "taules":
        taules = {"Fàcil": (2, 5, 10), "Normal": (2, 3, 4, 5, 6, 7, 8, 9), "Difícil": (6, 7, 8, 9)}[diff]
        a, b = random.choice(taules), random.randint(2, 10)
        a, b = (a, b) if random.random() < 0.5 else (b, a)
        text = f"{a} × {b} = ?"
        # enganyoses de la mateixa taula: el veí de dalt i el de baix
        ans, ops = a * b, [str(a * b)]
        for v in random.sample([a * (b - 1), a * (b + 1), (a - 1) * b, (a + 1) * b, a * b + 1, a * b - 2], 6):
            if v > 0 and str(v) not in ops:
                ops.append(str(v))
            if len(ops) == 4:
                break
    elif tema == "calcul":
        kind = random.choice([k for k in CALCUL_ALL if k != "Piràmide"])
        text, ans, _ = make_calcul(diff, kind)
        text, ops = text.replace(" x ", " × "), _opcions_numeriques(ans)
    elif tema == "animals":
        animals = [(e, n) for e, n in DIBUIXOS if not e.startswith("data:")][:40]
        tria = random.sample(animals, 4)
        emoji, text = tria[0][0], "QUIN ANIMAL ÉS?"
        ops = [n for _, n in tria]
    else:   # lletra que falta
        lo, hi = PENJAT_CFG[diff]["llarg"]
        paraules = [(w, c) for c, ws in PENJAT_PARAULES.items() for w in ws if lo <= len(w) <= hi]
        while True:
            w, cat = random.choice(paraules)
            llocs = [i for i in range(1, len(w)) if w[i] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
            if llocs:
                break
        conegudes = (CONCURS_PARAULES_COMUNES | CONCURS_PARAULES_LLETGES
                     | {x for ws in PENJAT_PARAULES.values() for x in ws}
                     | {x for ws in SOPA_WORDS.values() for x in ws})
        random.shuffle(llocs)
        for i in llocs:
            lletra = w[i]
            grup = "AEIOU" if lletra in "AEIOU" else "BCDFGLMNPRSTV"
            falses = [x for x in grup if x != lletra and w[:i] + x + w[i + 1:] not in conegudes]
            if len(falses) >= 3:
                break
        else:
            return concurs_pregunta("lletra", diff)     # aquesta paraula no dona joc: una altra
        ops = [lletra] + random.sample(falses, 3)
        text = "QUINA LLETRA FALTA?  " + " ".join(w[:i] + "_" + w[i + 1:]) + f"  ({cat})"
    correcta = ops[0]
    random.shuffle(ops)
    return {"text": text, "emoji": emoji, "opcions": ops, "correcta": ops.index(correcta)}


def cq_clau(q):
    """Identifica una pregunta ("el mes gran" es repeteix amb altres numeros: hi va la resposta)."""
    return q["text"] + q["emoji"] + q["opcions"][q["correcta"]]


def concurs_preguntes(tema, diff, n, evita=()):
    """n preguntes diferents. Primer les que no son a 'evita' (les ja vistes); si el tema no en
    te prou de noves, s'omple amb vistes (i qui crida torna a comencar la llista)."""
    out, repes, vistes = [], [], set()
    for _ in range(n * 40):
        q = concurs_pregunta(tema, diff)
        clau = cq_clau(q)
        if clau in vistes or len(set(q["opcions"])) < 4:
            continue
        vistes.add(clau)
        if clau in evita:
            repes.append(q)
            continue
        out.append(q)
        if len(out) == n:
            break
    return out + repes[:n - len(out)]


@st.cache_resource
def _cq_memoria():
    """Preguntes ja vistes per (dispositiu, tema, nivell), perque no surtin les mateixes cada dia
    (23 nov 2026, el Toni: "que no se vayan repitiendo"). A la memoria del servidor: sense noms,
    nomes el numero a l'atzar del dispositiu. Es perd si Streamlit reinicia l'app (no passa res)."""
    return {}


# ============================================================ CONCURS EN GRUP (pantalla gran)
# 18 nov 2026: el Toni torna a voler el joc de tota la classe, pero amb les seves regles:
# - Cap nom ni alies: cada jugador rep un animal i un color a l'atzar, sense escriure res.
# - Sense codis per teclejar: la pantalla gran ensenya un QR que porta a ?sala=<PIN> i l'app
#   hi entra sola. El numero de sala surt petit, nomes com a alternativa.
# - No es desa res: les sales viuen a la memoria del proces (st.cache_resource, compartit per
#   totes les sessions) i desapareixen soles al cap de 3 h sense moviment.
# - El joc en solitari es queda igual.
# La primera versio de grup (15 nov, commit 32c5fd6) demanava escriure un codi: per aixo es va treure.
CG_ANIMALS = "🐼 🦒 🐸 🦊 🐨 🐯 🦁 🐧 🐬 🦉 🐢 🐙 🦄 🐝 🦋 🐰 🐻 🐳 🐞 🦓".split()
CG_COLORS = ["#EB3B5A", "#FA8231", "#F7B731", "#20BF6B", "#0FB9B1", "#4B7BEC", "#8854D0", "#F368E0"]
CG_MAX_SALES = 30
CG_MAX_JUGADORS = 40
CG_VIDA = 3 * 3600          # una sala sense moviment desapareix al cap de 3 h
CG_ACTIU = 8                # segons sense senyals d'un mobil per deixar d'esperar-ne la resposta
CG_N = (5, 10, 15)          # preguntes per partida
CG_SEGONS = (10, 15, 20, 30, 45)
CG_RATXA_BONUS, CG_RATXA_MAX = 100, 500     # +100 per encert seguit (des del 2n), fins a +500
APP_URL = "https://aventura-matematica.streamlit.app"


@st.cache_resource
def _sales():
    """Totes les sales en joc, compartides per TOTES les sessions del mateix proces."""
    return {"lock": threading.Lock(), "sales": {}}


def _sala_neteja(sales, ara):
    for pin in [p for p, sa in sales.items() if ara - sa["mogut"] > CG_VIDA]:
        del sales[pin]


def _sala_nova_ronda(sa):
    """Preguntes noves i tothom a zero, pero els jugadors es queden a la sala (no cal tornar a escanejar)."""
    sa.update(fase="espera", idx=0, t0=0.0,
              preguntes=concurs_preguntes(sa["tema"], sa["nivell"], sa["n"]))
    for j in sa["jugadors"].values():
        j.update(punts=0, ratxa=0, respostes={})


def sala_crea(tema, nivell, n, segons):
    """Crea una sala i en torna el numero (o None si ja n'hi ha massa)."""
    c = _sales()
    with c["lock"]:
        ara = time.time()
        _sala_neteja(c["sales"], ara)
        if len(c["sales"]) >= CG_MAX_SALES:
            return None
        pin = random.choice([p for p in map(str, range(1000, 10000)) if p not in c["sales"]])
        sa = {"pin": pin, "tema": tema, "nivell": nivell, "n": n, "segons": segons,
              "jugadors": {}, "mogut": ara, "ronda": 1}
        _sala_nova_ronda(sa)
        c["sales"][pin] = sa
        return pin


def _sala_tanca_pregunta(sa):
    """Fi de la pregunta: qui no ha respost perd la ratxa, pero no perd punts."""
    sa["fase"] = "resultat"
    for j in sa["jugadors"].values():
        if sa["idx"] not in j["respostes"]:
            j["ratxa"] = 0


def _sala_actualitza(sa, ara):
    """La pregunta es tanca sola si s'acaba el temps o ja ha respost tothom qui hi es."""
    if sa["fase"] != "pregunta":
        return
    actius = [j for j in sa["jugadors"].values()
              if ara - j["vist"] <= CG_ACTIU or sa["idx"] in j["respostes"]]
    tots = bool(actius) and all(sa["idx"] in j["respostes"] for j in actius)
    if tots or ara - sa["t0"] >= sa["segons"]:
        _sala_tanca_pregunta(sa)


def sala_estat(pin, pid=None):
    """Copia de la sala per pintar-la. Si qui pregunta es un jugador, consta que encara hi es."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if not sa:
            return None
        ara = time.time()
        if pid in sa["jugadors"]:
            sa["jugadors"][pid]["vist"] = ara
        _sala_actualitza(sa, ara)
        return copy.deepcopy(sa)


def sala_entra(pin, pid):
    """Un mobil entra a la sala i li toca un avatar lliure. Torna 'ok', 'no' (no hi es) o 'plena'."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if not sa:
            return "no"
        ara = time.time()
        if pid in sa["jugadors"]:
            sa["jugadors"][pid]["vist"] = ara
            return "ok"
        if len(sa["jugadors"]) >= CG_MAX_JUGADORS:
            return "plena"
        agafats = {(j["emoji"], j["color"]) for j in sa["jugadors"].values()}
        usos = {e: 0 for e in CG_ANIMALS}
        for j in sa["jugadors"].values():
            usos[j["emoji"]] += 1
        lliures = [(e, col) for e in CG_ANIMALS for col in CG_COLORS if (e, col) not in agafats]
        minim = min(usos[e] for e, _ in lliures)       # primer, animals que encara no hi son
        emoji, color = random.choice([(e, col) for e, col in lliures if usos[e] == minim])
        sa["jugadors"][pid] = {"emoji": emoji, "color": color, "punts": 0, "ratxa": 0,
                               "respostes": {}, "vist": ara, "entrat": ara}
        sa["mogut"] = ara
        return "ok"


def sala_respon(pin, pid, opcio):
    """Torna la resposta apuntada ({punts, bonus, encert...}) o None si ja no es pot respondre."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if not sa:
            return None
        ara = time.time()
        _sala_actualitza(sa, ara)
        j = sa["jugadors"].get(pid)
        if sa["fase"] != "pregunta" or not j or sa["idx"] in j["respostes"]:
            return None
        t = ara - sa["t0"]
        encert = opcio == sa["preguntes"][sa["idx"]]["correcta"]
        if encert:
            j["ratxa"] += 1
            # mes rapid, mes punts: de 1000 (a l'instant) a 500 (just al final)
            base = round(1000 * (1 - min(t, sa["segons"]) / (2 * sa["segons"])))
            bonus = min(CG_RATXA_BONUS * (j["ratxa"] - 1), CG_RATXA_MAX)
        else:
            j["ratxa"], base, bonus = 0, 0, 0
        r = {"opcio": opcio, "t": round(t, 1), "punts": base + bonus, "bonus": bonus,
             "encert": encert, "ratxa": j["ratxa"]}
        j["respostes"][sa["idx"]] = r
        j["punts"] += base + bonus
        j["vist"] = sa["mogut"] = ara
        _sala_actualitza(sa, ara)
        return r


def sala_avanca(pin, fase, idx):
    """Boto de la pantalla gran: comencar, tancar la pregunta o passar a la seguent.
    Nomes actua si la sala encara es a la fase i pregunta on s'ha clicat (un doble clic no salta res)."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if not sa or sa["fase"] != fase or sa["idx"] != idx:
            return
        ara = time.time()
        if fase == "pregunta":
            _sala_tanca_pregunta(sa)
        elif fase in ("espera", "resultat"):
            if fase == "resultat":
                sa["idx"] += 1
            if sa["idx"] >= len(sa["preguntes"]):
                sa["fase"] = "final"
            else:
                sa["fase"], sa["t0"] = "pregunta", ara
        sa["mogut"] = ara


def sala_torna(pin):
    """Tornar a jugar amb la mateixa sala i la mateixa gent (preguntes noves, punts a zero)."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if sa:
            _sala_nova_ronda(sa)
            sa["ronda"] += 1
            sa["mogut"] = time.time()


def sala_config(pin, tema, nivell, n, segons):
    """Canviar tema, nivell, preguntes o segons d'una sala que espera (la gent es queda)."""
    c = _sales()
    with c["lock"]:
        sa = c["sales"].get(pin)
        if sa and sa["fase"] in ("espera", "final"):
            sa.update(tema=tema, nivell=nivell, n=n, segons=segons)
            _sala_nova_ronda(sa)
            sa["mogut"] = time.time()


def sala_tanca(pin):
    c = _sales()
    with c["lock"]:
        c["sales"].pop(pin, None)


def sala_classificacio(sa):
    """[(posicio, pid, jugador)] de mes a menys punts. Empat = mateixa posicio."""
    ordre = sorted(sa["jugadors"].items(), key=lambda kv: (-kv[1]["punts"], kv[1]["entrat"]))
    return [(1 + sum(1 for x in sa["jugadors"].values() if x["punts"] > j["punts"]), pid, j)
            for pid, j in ordre]


def sala_vots(sa, idx):
    """Quanta gent ha triat cada opcio a la pregunta idx."""
    vots = [0, 0, 0, 0]
    for j in sa["jugadors"].values():
        r = j["respostes"].get(idx)
        if r:
            vots[r["opcio"]] += 1
    return vots


# Carrera de lectura: (segons de base, segons per lletra) que es consideren "bon ritme"
LECTURA_RITME = {"Fàcil": (1.5, 0.50), "Normal": (1.5, 0.52), "Difícil": (1.5, 0.47)}


def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&family=Bungee&family=Noto+Color+Emoji&display=swap');
    .bandera { font-family: 'Noto Color Emoji', sans-serif; }
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
      .st-key-homeblocks div[data-testid="stColumn"] { flex: 1 1 calc(33% - 6px) !important; min-width: calc(33% - 6px) !important; }
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
    }
    /* mòbils molt estrets: un botó per línia als blocs de la home */
    @media (max-width: 430px) {
      .st-key-homeblocks div[data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 100% !important; }
      .problem-box { font-size: 1.55rem !important; }
    }
    .race-track { background: #333; height: 60px; width: 100%; border-radius: 15px; position: relative; margin: 10px 0; border: 3px dashed white; overflow: hidden; }
    .car { font-size: 2rem; position: absolute; transition: left 0.5s ease; top: 50%; transform: translateY(-50%); }
    .medal-overlay { background: radial-gradient(circle, rgba(255,244,204,0.97) 0%, rgba(255,214,102,0.95) 100%) !important; }
    .medal-icones { font-size: 7rem; line-height: 1.1; animation: medalpop 0.7s ease-out; }
    .medal-overlay h1 { font-family: 'Bungee', cursive; color: #EE5253; font-size: 3rem; margin: 14px 0 0 0; text-align: center; }
    .medal-overlay h2 { font-family: 'Bungee', cursive; color: #2D3436; font-size: 1.6rem; margin: 6px 0 0 0; text-align: center; padding: 0 14px; }
    @keyframes medalpop { 0% { transform: scale(0.2) rotate(-25deg); opacity: 0; }
                          65% { transform: scale(1.18) rotate(6deg); opacity: 1; }
                          100% { transform: scale(1) rotate(0); } }
    @media (max-width: 767px) {
      .medal-icones { font-size: 4.6rem; }
      .medal-overlay h1 { font-size: 1.9rem !important; }
      .medal-overlay h2 { font-size: 1.1rem; }
    }
    .gif-overlay img { width: min(300px, 70vw); height: auto; }
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
    /* boto 🔊 ESCOLTA del concurs: nomes l'alcada del boto */
    .st-key-escolta iframe[data-testid="stIFrame"] { height: 58px !important; min-height: 0 !important; }
    /* boto invisible que la sopa de lletres clica sola quan s'han trobat totes les paraules */
    .st-key-sopa_done { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-sopa_done button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    .st-key-golut_ok, .st-key-golut_ko { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-golut_ok button, .st-key-golut_ko button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    .st-key-penjat_guanya, .st-key-penjat_perd { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-penjat_guanya button, .st-key-penjat_perd button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    .st-key-memory_done { height: 0 !important; min-height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    .st-key-memory_done button { height: 1px !important; min-height: 0 !important; padding: 0 !important; opacity: 0 !important; }
    /* ---- calendari i medalles ---- */
    .cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; max-width: 560px; margin: 6px auto 0 auto; }
    .cal-cap { text-align: center; font-family: 'Bungee', cursive; font-size: 0.8rem; color: #636E72; }
    .cal-dia { aspect-ratio: 1; background: white; border: 2px solid #EEE; border-radius: 12px; display: flex;
               flex-direction: column; align-items: center; justify-content: center; font-weight: 700; color: #2D3436; }
    .cal-dia.buit { background: transparent; border: none; }
    .cal-dia.fet { background: #FFF4CC; border-color: #F7B731; }
    .cal-dia.avui { border: 3px solid #4B7BEC; }
    .cal-dia.futur { opacity: 0.45; }
    .cal-dia .num { font-size: 0.95rem; line-height: 1; }
    .cal-dia .est { font-size: 1.35rem; line-height: 1.15; }
    .cal-mes { text-align: center; font-family: 'Bungee', cursive; font-size: 1.3rem; color: #EE5253; margin-top: 8px; }
    .med-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(135px, 1fr)); gap: 8px; margin-top: 8px; }
    .med { background: white; border: 3px solid #F7B731; border-radius: 16px; padding: 8px 6px; text-align: center; }
    .med .ico { font-size: 2.1rem; line-height: 1.2; }
    .med .nom { font-family: 'Bungee', cursive; font-size: 0.72rem; color: #2D3436; line-height: 1.2; }
    .med .com { font-size: 0.74rem; color: #636E72; line-height: 1.2; margin-top: 2px; }
    .med.no { filter: grayscale(1); opacity: 0.45; border-color: #DDD; }
    .st-key-calnav div[data-testid="stColumn"] { flex: 1 1 0 !important; min-width: 0 !important; }
    div.stButton > button:disabled { opacity: 0.35 !important; box-shadow: none !important; cursor: default !important; }
    @media (max-width: 767px) {
      .cal { gap: 3px; }
      .cal-dia { border-radius: 8px; border-width: 1px; }
      .cal-dia.avui { border-width: 2px; }
      .cal-dia .num { font-size: 0.72rem; }
      .cal-dia .est { font-size: 1rem; }
      .cal-cap { font-size: 0.62rem; }
      .med-grid { grid-template-columns: repeat(2, 1fr); }
    }
    /* ---- concurs ---- */
    .st-key-conc_op_0 div.stButton > button { background: #8854D0 !important; box-shadow: 0 7px 0 #5F3A99 !important; min-height: 118px !important; font-size: 1.7rem !important; }
    .st-key-conc_op_1 div.stButton > button { background: #FA8231 !important; box-shadow: 0 7px 0 #B85A1C !important; min-height: 118px !important; font-size: 1.7rem !important; }
    .st-key-conc_op_2 div.stButton > button { background: #0FB9B1 !important; box-shadow: 0 7px 0 #0A817B !important; min-height: 118px !important; font-size: 1.7rem !important; }
    .st-key-conc_op_3 div.stButton > button { background: #EB3B8F !important; box-shadow: 0 7px 0 #A82563 !important; min-height: 118px !important; font-size: 1.7rem !important; }
    .cq-cap { display: flex; justify-content: space-between; align-items: center; font-family: 'Bungee', cursive;
              color: #636E72; font-size: 1rem; }
    .cq-temps { font-family: 'Bungee', cursive; font-size: 2.4rem; color: white; background: #8854D0; border-radius: 50%;
                width: 84px; height: 84px; display: flex; align-items: center; justify-content: center; }
    .cq-temps.poc { background: #EB3B5A; }
    .cq-preg { font-family: 'Bungee', cursive; font-size: 2.6rem; color: #2D3436; text-align: center; margin: 10px 0;
               line-height: 1.2; }
    .cq-emoji { font-size: 6rem; text-align: center; line-height: 1.1; }
    .cq-ops { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .cq-op { border-radius: 16px; color: white; font-family: 'Bungee', cursive; font-size: 1.9rem; padding: 18px 16px;
             display: flex; align-items: center; gap: 14px; min-height: 86px; transition: opacity .3s; }
    .cq-op .forma { font-size: 2.2rem; }
    .cq-op.apagada { opacity: .28; }
    .cq-op.bona { outline: 6px solid #20BF6B; }
    .cq-op.triada { opacity: .55; text-decoration: line-through; }
    .cq-info { text-align: center; font-size: 1.15rem; color: #2D3436; margin: 6px 0; }
    .cq-gran { font-family: 'Bungee', cursive; font-size: 2.2rem; text-align: center; margin: 14px 0 4px 0; }
    .cq-feedback { text-align: center; font-family: 'Bungee', cursive; font-size: 2.6rem; padding: 24px 10px;
                   border-radius: 24px; color: white; margin: 10px 0; }
    .cq-feedback.si { background: #20BF6B; } .cq-feedback.no { background: #EB3B5A; }
    .cq-feedback.espera { background: #8854D0; font-size: 1.7rem; }
    .st-key-cq_sol div.stButton > button, .st-key-cq_grup div.stButton > button { min-height: 110px !important; font-size: 1.5rem !important; }
    .st-key-cq_grup div.stButton > button { background: linear-gradient(180deg,#4B7BEC 0%,#3867D6 100%) !important; box-shadow: 0 5px 0 #2a4fa8 !important; }
    /* ---- concurs en grup ---- */
    .cg-av { display: inline-flex; align-items: center; justify-content: center; width: 58px; height: 58px;
             border-radius: 50%; font-size: 2.1rem; line-height: 1; border: 3px solid white;
             box-shadow: 0 3px 0 rgba(0,0,0,.15); flex: 0 0 auto; }
    .cg-av.mig { width: 84px; height: 84px; font-size: 3.1rem; }
    .cg-av.gran { width: 130px; height: 130px; font-size: 5rem; border-width: 6px; }
    .cg-av.petit { width: 42px; height: 42px; font-size: 1.5rem; border-width: 2px; }
    .cg-avatars .cg-av { animation: medalpop .6s ease-out; }
    .cg-avatars { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 10px 0; min-height: 64px; }
    .cg-qr-caixa { background: white; border-radius: 24px; padding: 14px; text-align: center;
                   box-shadow: 0 6px 18px rgba(0,0,0,.08); max-width: 420px; margin: 0 auto 18px auto; }
    .cg-ops { margin-bottom: 16px; }
    .cg-qr { width: 100%; max-width: 380px; height: auto; display: block; margin: 0 auto; }
    .cg-qr-peu { font-family: 'Bungee', cursive; font-size: 1.25rem; color: #2D3436; margin-top: 4px; }
    .cg-url { font-size: 0.85rem; color: #636E72; word-break: break-all; margin-top: 2px; }
    .cg-titol { font-family: 'Bungee', cursive; font-size: 2rem; color: #2D3436; text-align: center; margin: 4px 0 12px 0; }
    .cg-resum { text-align: center; color: #636E72; font-size: 1.05rem; margin: 4px 0 10px 0; }
    .cg-cap { display: flex; justify-content: space-between; align-items: center; font-family: 'Bungee', cursive;
              color: #636E72; font-size: 1.15rem; gap: 8px; }
    .cg-preg { font-family: 'Bungee', cursive; font-size: 3.3rem; color: #2D3436; text-align: center; margin: 14px 0;
               line-height: 1.2; }
    .cg-preg.petita { font-size: 1.9rem; margin: 6px 0 12px 0; }
    .cg-barres { display: flex; gap: 14px; align-items: stretch; height: 250px; }
    .cg-barra { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; min-width: 0; }
    .cg-barra .n { text-align: center; font-family: 'Bungee', cursive; font-size: 1.7rem; color: #2D3436; }
    .cg-barra .col { border-radius: 12px 12px 0 0; min-height: 6px; }
    .cg-barra .peu { border-radius: 0 0 12px 12px; color: white; font-family: 'Bungee', cursive; text-align: center;
                     padding: 6px 4px; font-size: 1.15rem; overflow-wrap: anywhere; line-height: 1.15; }
    .cg-barra.no { opacity: .35; }
    .cg-barra.bona .peu { outline: 5px solid #20BF6B; outline-offset: 2px; }
    .cg-top { display: flex; flex-direction: column; gap: 8px; }
    .cg-top-tit { font-family: 'Bungee', cursive; color: #636E72; text-align: center; font-size: 1.1rem; }
    .cg-fila { display: flex; align-items: center; gap: 12px; background: white; border-radius: 16px; padding: 5px 14px;
               font-family: 'Bungee', cursive; font-size: 1.35rem; color: #2D3436; box-shadow: 0 3px 0 rgba(0,0,0,.06); }
    .cg-fila .pos { width: 30px; color: #636E72; }
    .cg-fila .pts { margin-left: auto; }
    .cg-fila .foc { font-size: 0.95rem; color: #FA8231; }
    .cg-frase { font-family: 'Bungee', cursive; font-size: 1.6rem; color: #20BF6B; text-align: center; margin: 4px 0 10px 0; }
    .cg-podi { display: flex; align-items: flex-end; justify-content: center; gap: 18px; margin: 6px 0; }
    .cg-esgrao { display: flex; flex-direction: column; align-items: center; width: 210px; }
    .cg-esgrao .pts { font-family: 'Bungee', cursive; font-size: 1.35rem; color: #2D3436; margin: 6px 0; }
    .cg-bloc { width: 100%; border-radius: 18px 18px 0 0; display: flex; justify-content: center; align-items: flex-start;
               font-family: 'Bungee', cursive; font-size: 3rem; color: white; padding-top: 6px; }
    .cg-esgrao.p1 .cg-bloc { height: 150px; background: linear-gradient(180deg,#FFD15C,#F7B731); }
    .cg-esgrao.p2 .cg-bloc { height: 110px; background: linear-gradient(180deg,#DFE6E9,#A4B0BE); }
    .cg-esgrao.p3 .cg-bloc { height: 78px; background: linear-gradient(180deg,#F8A47B,#E17055); }
    .cg-trofeu { width: 100px; height: 100px; }
    .cg-festa { width: 74px; height: 74px; }
    .cg-podi-cap { display: flex; justify-content: center; align-items: center; gap: 16px; }
    .cg-jo { display: flex; align-items: center; justify-content: space-between; gap: 10px; font-family: 'Bungee', cursive;
             font-size: 1.5rem; color: #2D3436; margin-bottom: 6px; }
    .cg-jo-centre { display: flex; flex-direction: column; align-items: center; gap: 10px; margin: 10px 0; }
    .cg-mini { text-align: center; color: #636E72; font-size: 1rem; margin: 6px 0; }
    .st-key-cg_botons div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; column-gap: 12px !important; }
    .st-key-cg_botons div[data-testid="stColumn"] { flex: 1 1 0 !important; min-width: 0 !important; }
    .st-key-cg_op_0 div.stButton > button { background: #8854D0 !important; box-shadow: 0 7px 0 #5F3A99 !important; }
    .st-key-cg_op_1 div.stButton > button { background: #FA8231 !important; box-shadow: 0 7px 0 #B85A1C !important; }
    .st-key-cg_op_2 div.stButton > button { background: #0FB9B1 !important; box-shadow: 0 7px 0 #0A817B !important; }
    .st-key-cg_op_3 div.stButton > button { background: #EB3B8F !important; box-shadow: 0 7px 0 #A82563 !important; }
    .st-key-cg_botons div.stButton > button { min-height: 150px !important; }
    .st-key-cg_botons div.stButton > button p { font-size: 2.4rem !important; line-height: 1.1 !important; }
    .st-key-maincard div[role="radiogroup"] { gap: 6px 18px; }
    .st-key-maincard div[role="radiogroup"] label p { font-size: 1.15rem !important; font-weight: 700; }
    .st-key-maincard div[data-testid="stWidgetLabel"] p { font-family: 'Bungee', cursive; font-size: 1.05rem !important; color: #636E72; }
    .st-key-cg_m_start div.stButton > button { background: linear-gradient(180deg,#20BF6B 0%,#0FA45B 100%) !important;
                                               box-shadow: 0 5px 0 #0B7A45 !important; min-height: 76px !important; font-size: 1.8rem !important; }

    @media (max-width: 767px) {
      .cg-preg { font-size: 1.6rem; }
      .cg-preg.petita { font-size: 1.1rem; }
      .cg-av.gran { width: 104px; height: 104px; font-size: 4rem; }
      .cg-av.mig { width: 64px; height: 64px; font-size: 2.3rem; }
      .cg-jo { font-size: 1.15rem; }
      .cg-barres { height: 170px; gap: 6px; }
      .cg-barra .peu { font-size: 0.75rem; }
      .cg-barra .n { font-size: 1.1rem; }
      .cg-fila { font-size: 1rem; }
      .cg-podi { gap: 6px; }
      .cg-esgrao .pts { font-size: 0.9rem; }
      .cg-bloc { font-size: 1.8rem; }
      .cg-esgrao.p1 .cg-bloc { height: 120px; } .cg-esgrao.p2 .cg-bloc { height: 90px; } .cg-esgrao.p3 .cg-bloc { height: 64px; }
      .cg-trofeu { width: 76px; height: 76px; } .cg-festa { width: 56px; height: 56px; }
      .cg-titol { font-size: 1.4rem; }
      .st-key-cg_botons div[data-testid="stHorizontalBlock"] { row-gap: 12px !important; }
      .st-key-cg_botons div.stButton > button { min-height: max(140px, 25vh) !important; }
      .st-key-cg_botons div.stButton > button p { font-size: 1.9rem !important; }
      .st-key-cq_sol div.stButton > button, .st-key-cq_grup div.stButton > button { min-height: 84px !important; font-size: 1.05rem !important; }
    }

    @media (max-width: 767px) {
      .cq-preg { font-size: 1.5rem; }
      .cq-emoji { font-size: 4rem; }
      .cq-op { font-size: 1.1rem; padding: 10px; min-height: 60px; gap: 8px; }
      .cq-op .forma { font-size: 1.4rem; }
      .cq-temps { width: 58px; height: 58px; font-size: 1.6rem; }
      .cq-feedback { font-size: 1.7rem; }
      .st-key-conc_op_0 div.stButton > button { min-height: 96px !important; font-size: 1.25rem !important; }
      .st-key-conc_op_1 div.stButton > button { min-height: 96px !important; font-size: 1.25rem !important; }
      .st-key-conc_op_2 div.stButton > button { min-height: 96px !important; font-size: 1.25rem !important; }
      .st-key-conc_op_3 div.stButton > button { min-height: 96px !important; font-size: 1.25rem !important; }
    }
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


def golut_component(g, nonce):
    """El monstre i la cinta de plats. Tot el joc passa al navegador:
    - encert: el monstre se'ls menja i es clica el boto invisible 'golut_ok';
    - primer error: els plats tornen a la cinta i pot tornar-ho a provar;
    - segon error: ensenya la solucio en verd i clica 'golut_ko' (sense cartell)."""
    simbol = "+" if g["op"] == "suma" else "×"
    verb = "sumin" if g["op"] == "suma" else "multiplicats facin"
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Andika:wght@700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent;
         user-select:none; -webkit-user-select:none; }
  #wrap { display:flex; flex-direction:column; align-items:center; gap:8px; max-width:720px; margin:0 auto; }
  #dalt { display:flex; align-items:center; justify-content:center; gap:18px; }
  .monstre { width:140px; height:124px; position:relative; flex:none;
             background:radial-gradient(circle at 35% 30%, #C9A7FF, #7C4DFF);
             border-radius:50% 50% 44% 44%; box-shadow:0 6px 0 #5E35B1; }
  .monstre::before, .monstre::after { content:''; position:absolute; top:-14px; width:0; height:0;
             border-left:12px solid transparent; border-right:12px solid transparent;
             border-bottom:22px solid #7C4DFF; }
  .monstre::before { left:24px; transform:rotate(-15deg); }
  .monstre::after { right:24px; transform:rotate(15deg); }
  .ull { position:absolute; top:26px; width:34px; height:34px; background:#fff; border-radius:50%; }
  .ull.e { left:28px; } .ull.d { right:28px; }
  .pupil { position:absolute; top:11px; left:11px; width:13px; height:13px; background:#2D3436;
           border-radius:50%; transition:transform .2s; }
  .boca { position:absolute; bottom:20px; left:50%; transform:translateX(-50%); width:58px; height:20px;
          background:#B71C1C; border-radius:0 0 40px 40px; transition:height .2s, width .2s; overflow:hidden; }
  .boca::after { content:''; position:absolute; top:0; left:12px; width:10px; height:8px; background:#fff;
                 border-radius:0 0 4px 4px; box-shadow:24px 0 0 #fff; }
  .monstre.menja { animation:nyam .55s ease-in-out 2; }
  .monstre.menja .boca { height:44px; width:66px; }
  .monstre.trist .boca { height:10px; border-radius:40px 40px 0 0; bottom:26px; }
  @keyframes nyam { 0%,100% { transform:scale(1); } 50% { transform:scale(1.12) rotate(-4deg); } }
  .cartell { text-align:center; }
  .num { font-family:'Bungee',cursive; font-size:3rem; color:#EE5253; line-height:1;
         background:#FFF4CC; border:4px solid #F7B731; border-radius:18px; padding:6px 20px; display:inline-block; }
  .peticio { font-size:1rem; color:#2D3436; margin-top:6px; }
  #safata { min-height:50px; font-family:'Bungee',cursive; font-size:1.7rem; color:#2D3436;
            display:flex; align-items:center; justify-content:center; gap:8px; }
  #cinta { display:flex; flex-wrap:wrap; gap:12px; justify-content:center; padding:14px 10px; width:100%;
           border-radius:20px; background:repeating-linear-gradient(90deg,#DFE6E9 0 22px,#CFD8DC 22px 44px);
           background-size:44px 100%; animation:cinta 2.5s linear infinite; }
  @keyframes cinta { from { background-position:0 0; } to { background-position:44px 0; } }
  .plat { width:76px; height:76px; border-radius:50%; background:#fff; border:7px solid var(--c);
          box-shadow:0 5px 0 rgba(0,0,0,.18); font-family:'Bungee',cursive; font-size:1.9rem; color:#2D3436;
          display:flex; align-items:center; justify-content:center; cursor:pointer;
          transition:transform .15s, opacity .3s; }
  .plat.triat { transform:translateY(-10px) scale(1.08); background:#FFF4CC; }
  .plat.menjat { opacity:0; transform:scale(.3); }
  .plat.solucio { background:#20BF6B; color:#fff; border-color:#0B7A45; }
  .plat.tremola { animation:tremola .4s; }
  @keyframes tremola { 25% { transform:translateX(-6px); } 75% { transform:translateX(6px); } }
  #msg { font-weight:700; color:#EE5253; text-align:center; min-height:26px; font-size:1.15rem; }
  @media (max-width:520px) {
    .monstre { width:110px; height:98px; } .ull { width:28px; height:28px; top:20px; }
    .ull.e { left:20px; } .ull.d { right:20px; } .pupil { top:8px; left:8px; width:12px; height:12px; }
    .num { font-size:2.2rem; padding:4px 14px; } .peticio { font-size:.85rem; }
    .plat { width:60px; height:60px; font-size:1.45rem; border-width:6px; }
    #cinta { gap:9px; } #safata { font-size:1.35rem; }
  }
</style>
<div id="wrap">
  <div id="dalt">
    <div class="monstre" id="monstre">
      <div class="ull e"><div class="pupil"></div></div>
      <div class="ull d"><div class="pupil"></div></div>
      <div class="boca"></div>
    </div>
    <div class="cartell">
      <div class="num">__OBJ__</div>
      <div class="peticio">Dona'm <b>__K__ plats</b> que __VERB__ <b>__OBJ__</b></div>
    </div>
  </div>
  <div id="safata"></div>
  <div id="cinta"></div>
  <div id="msg"></div>
</div>
<script>
  const OBJ = __OBJ__, K = __K__, OP = "__OP__", SIMB = "__SIMB__", PLATS = __PLATS__,
        SOL = __SOL__, NONCE = "__NONCE__";
  const COLORS = ['#FF6B6B','#4B7BEC','#20BF6B','#F7B731','#A55EEA','#FD9644','#2BCBBA','#EB3B5A'];
  const cinta = document.getElementById('cinta'), safata = document.getElementById('safata'),
        msg = document.getElementById('msg'), monstre = document.getElementById('monstre');
  let triats = [], intents = 0, bloquejat = false;
  const plats = PLATS.map((n, i) => {
    const d = document.createElement('div'); d.className = 'plat'; d.textContent = n;
    d.style.setProperty('--c', COLORS[i % COLORS.length]);
    d.onclick = () => toca(i); cinta.appendChild(d); return d;
  });
  function valor(ns) { return ns.reduce((a, n) => OP === 'suma' ? a + n : a * n, OP === 'suma' ? 0 : 1); }
  function pinta() {
    const ns = triats.map(i => PLATS[i]);
    const falten = Array(K - ns.length).fill('?');
    safata.textContent = ns.concat(falten).join(' ' + SIMB + ' ') + ' = ' +
      (ns.length === K ? valor(ns) : '?');
    plats.forEach((p, i) => p.classList.toggle('triat', triats.includes(i)));
    ajusta();
  }
  function ajusta() {
    try {
      const fr = window.frameElement;
      if (!fr) return;
      const h = (document.getElementById('wrap').scrollHeight + 14) + 'px';
      fr.style.height = h;
      // Streamlit fixa l'alcada inicial al contenidor amb 'flex: 0 0 500px': cal
      // canviar l'alcada i tambe el flex, si no queda un forat en blanc a sota
      const cont = fr.closest('[data-testid="stElementContainer"]');
      if (cont) {
        cont.style.setProperty('height', h, 'important');
        cont.style.setProperty('flex', '0 0 ' + h, 'important');
      }
    } catch (e) {}
  }
  window.addEventListener('resize', ajusta);
  function mira(dx) { document.querySelectorAll('.pupil').forEach(p => p.style.transform = 'translateX(' + dx + 'px)'); }
  function avisa(clau, espera) {
    setTimeout(() => {
      try {
        const b = window.parent.document.querySelector('.st-key-' + clau + ' button');
        if (b) { b.click(); return; }
      } catch (e) {}
      msg.textContent = "Prem UN ALTRE MONSTRE per continuar";
    }, espera);
  }
  function toca(i) {
    if (bloquejat) return;
    const j = triats.indexOf(i);
    if (j >= 0) triats.splice(j, 1);           // tornar-lo a tocar el treu
    else if (triats.length < K) triats.push(i);
    msg.textContent = ''; mira(i < PLATS.length / 2 ? -5 : 5); pinta();
    if (triats.length === K) comprova();
  }
  function comprova() {
    const ns = triats.map(i => PLATS[i]);
    if (valor(ns) === OBJ) {
      bloquejat = true; msg.style.color = '#20BF6B'; msg.textContent = 'NYAM NYAM! 😋';
      monstre.classList.add('menja');
      triats.forEach(i => plats[i].classList.add('menjat'));
      avisa('golut_ok', 1300);
      return;
    }
    intents++;
    monstre.classList.add('trist');
    triats.forEach(i => plats[i].classList.add('tremola'));
    if (intents < 2) {
      msg.textContent = (ns.join(' ' + SIMB + ' ') + ' fa ' + valor(ns) + '. Torna-ho a provar! 💪');
      bloquejat = true;
      setTimeout(() => {
        triats.forEach(i => plats[i].classList.remove('tremola'));
        monstre.classList.remove('trist'); triats = []; bloquejat = false; pinta();
      }, 1100);
      return;
    }
    // segon error: ensenyem una solucio i passem al seguent, sense cartell
    bloquejat = true;
    setTimeout(() => {
      triats = []; pinta();
      const usats = new Set();
      SOL.forEach(n => {
        const i = PLATS.findIndex((v, k) => v === n && !usats.has(k)); usats.add(i);
        plats[i].classList.add('solucio');
      });
      safata.textContent = SOL.join(' ' + SIMB + ' ') + ' = ' + OBJ;
      msg.textContent = 'Era aquesta! El proper segur que sí 💪';
      ajusta();
      avisa('golut_ko', 2600);
    }, 900);
  }
  pinta();
</script>
"""
        .replace("__OBJ__", str(g["objectiu"]))
        .replace("__K__", str(g["k"]))
        .replace("__VERB__", verb)
        .replace("__OP__", g["op"])
        .replace("__SIMB__", simbol)
        .replace("__PLATS__", json.dumps(g["plats"]))
        .replace("__SOL__", json.dumps(g["solucio"]))
        .replace("__NONCE__", nonce))
    components.html(html, height=500)


def penjat_component(pj, nonce):
    """Joc del penjat: teclat en pantalla (i el del PC), dibuix que es completa amb
    cada error. En guanyar o perdre, clica el boto invisible corresponent."""
    html = ("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Andika:wght@700&display=swap');
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Andika','Trebuchet MS',sans-serif; background:transparent;
         user-select:none; -webkit-user-select:none; }
  #wrap { display:flex; flex-direction:column; align-items:center; gap:8px; max-width:720px; margin:0 auto; }
  #dalt { display:flex; align-items:center; justify-content:center; gap:14px; width:100%; }
  #dibuix { width:150px; height:150px; flex:none; }
  #dibuix .part { stroke:#2D3436; stroke-width:6; stroke-linecap:round; fill:none; opacity:0;
                  transition:opacity .3s; }
  #dibuix .part.on { opacity:1; }
  #dibuix .cap.on { stroke:#EE5253; }
  #info { display:flex; flex-direction:column; gap:6px; align-items:flex-start; }
  #pista { background:#FFF4CC; border:2px solid #F7B731; border-radius:12px; padding:3px 10px;
           font-size:1rem; color:#2D3436; }
  #vides { font-size:1.3rem; letter-spacing:2px; }
  #paraula { display:flex; flex-wrap:wrap; gap:6px; justify-content:center; margin:4px 0; }
  .ll { width:36px; height:46px; border-bottom:5px solid #4B7BEC; display:flex; align-items:flex-end;
        justify-content:center; font-size:2rem; color:#2D3436; line-height:1; padding-bottom:2px; }
  .ll.perdut { color:#EE5253; }
  #teclat { display:grid; grid-template-columns:repeat(9, 1fr); gap:6px; width:100%; }
  .t { height:46px; border:none; border-radius:12px; font-family:inherit; font-size:1.25rem;
       color:#fff; background:#4B7BEC; box-shadow:0 4px 0 #2D5BC7; cursor:pointer; padding:0; }
  .t:active { transform:translateY(3px); box-shadow:none; }
  .t.be { background:#20BF6B; box-shadow:0 4px 0 #0B7A45; }
  .t.mal { background:#B2BEC3; box-shadow:none; color:#fff; }
  .t:disabled { cursor:default; }
  #msg { font-weight:700; color:#EE5253; text-align:center; min-height:24px; font-size:1.15rem; }
  @media (max-width:520px) {
    #dibuix { width:110px; height:110px; }
    .ll { width:26px; height:36px; font-size:1.45rem; border-bottom-width:4px; }
    #teclat { gap:4px; }
    .t { height:40px; font-size:1.05rem; border-radius:9px; }
    #pista { font-size:0.85rem; }
  }
</style>
<div id="wrap">
  <div id="dalt">
    <svg id="dibuix" viewBox="0 0 150 150">
      <line class="part" x1="15" y1="140" x2="95" y2="140"/>
      <line class="part" x1="35" y1="140" x2="35" y2="12"/>
      <line class="part" x1="35" y1="12" x2="105" y2="12"/>
      <line class="part" x1="105" y1="12" x2="105" y2="32"/>
      <circle class="part cap" cx="105" cy="46" r="14"/>
      <line class="part" x1="105" y1="60" x2="105" y2="98"/>
      <polyline class="part" points="85,78 105,68 125,78"/>
      <polyline class="part" points="90,126 105,98 120,126"/>
    </svg>
    <div id="info"><div id="pista"></div><div id="vides"></div></div>
  </div>
  <div id="paraula"></div>
  <div id="msg"></div>
  <div id="teclat"></div>
</div>
<script>
  const PARAULA = "__PARAULA__", CAT = "__CAT__", PISTA = __PISTA__, MAXERR = __MAXERR__,
        INICIALS = __VISIBLES__, NONCE = "__NONCE__";
  const LLETRES = "ABCÇDEFGHIJKLMNOPQRSTUVWXYZ".split("");
  const BASE = {"À":"A","È":"E","É":"E","Í":"I","Ï":"I","Ò":"O","Ó":"O","Ú":"U","Ü":"U"};
  const base = ch => BASE[ch] || ch;
  const parts = Array.from(document.querySelectorAll('#dibuix .part'));
  // amb menys vides, part del dibuix ja surt fet d'entrada
  const JAFET = parts.length - MAXERR;
  const provades = new Set(INICIALS); let errors = 0, fi = false;
  const tecles = {};

  document.getElementById('pista').textContent = PISTA ? ("PISTA: " + CAT) : ("SENSE PISTA · " + PARAULA.length + " LLETRES");
  LLETRES.forEach(l => {
    const b = document.createElement('button'); b.className = 't'; b.textContent = l;
    b.onclick = () => prova(l); document.getElementById('teclat').appendChild(b); tecles[l] = b;
  });
  INICIALS.forEach(l => { if (tecles[l]) { tecles[l].disabled = true; tecles[l].classList.add('be'); } });

  function pinta(perdut) {
    const cont = document.getElementById('paraula'); cont.innerHTML = '';
    for (const ch of PARAULA) {
      const d = document.createElement('div'); d.className = 'll';
      if (provades.has(base(ch))) d.textContent = ch;
      else if (perdut) { d.textContent = ch; d.classList.add('perdut'); }
      cont.appendChild(d);
    }
    parts.forEach((p, i) => p.classList.toggle('on', i < JAFET + errors));
    const queden = MAXERR - errors;
    document.getElementById('vides').textContent = "❤️".repeat(queden) + "🤍".repeat(errors);
  }
  function avisa(clau, text) {
    fi = true; document.getElementById('msg').textContent = text;
    Object.values(tecles).forEach(b => b.disabled = true);
    setTimeout(() => {
      try {
        const b = window.parent.document.querySelector('.st-key-' + clau + ' button');
        if (b) { b.click(); return; }
      } catch (e) {}
      document.getElementById('msg').textContent = text + " Prem NOVA PARAULA";
    }, clau === 'penjat_guanya' ? 1100 : 1800);
  }
  function prova(l) {
    if (fi || provades.has(l)) return;
    provades.add(l);
    const hi_es = [...PARAULA].some(ch => base(ch) === l);
    tecles[l].disabled = true; tecles[l].classList.add(hi_es ? 'be' : 'mal');
    if (!hi_es) errors++;
    const guanyat = [...PARAULA].every(ch => provades.has(base(ch)));
    const perdut = !guanyat && errors >= MAXERR;
    pinta(perdut);
    if (guanyat) avisa('penjat_guanya', "L'HAS ENDEVINADA! 🎉");
    else if (perdut) avisa('penjat_perd', "ERA " + PARAULA + ". LA PROPERA SEGUR! 💪");
  }
  document.addEventListener('keydown', e => {
    const l = (e.key || "").toUpperCase();
    if (LLETRES.includes(l)) prova(l);
  });
  pinta(false);
</script>
"""
        .replace("__PARAULA__", pj["paraula"])
        .replace("__CAT__", pj["cat"])
        .replace("__PISTA__", "true" if pj["pista"] else "false")
        .replace("__MAXERR__", str(pj["errors"]))
        .replace("__VISIBLES__", json.dumps(pj["visibles"], ensure_ascii=False))
        .replace("__NONCE__", nonce))
    components.html(html, height=500)


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
    i el nen pinta amb el dit o el ratoli. Paleta a la dreta. NOMES pinzell: el Toni
    va demanar treure el cubell d'omplir zones (9 set 2026).
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
      <button class="eina" id="gruix">✏️ GRUIX</button>
      <button class="eina" id="desfes">↩️ DESFÉS</button>
      <button class="eina vermell" id="neteja">🧽 NETEJA</button>
    </div>
  </div>
</div>
<script>
  const EMOJI = "__EMOJI__", NONCE = "__NONCE__", S = 640;
  const COLORS = ['#EE5253','#FF9F43','#FECA57','#F9E79F','#20BF6B','#7BED9F','#1E90FF','#48DBFB',
                  '#5F27CD','#A55EEA','#FF6B81','#FFC0CB','#8B4513','#D2B48C','#2D3436','#95A5A6','#FFFFFF','#00CEC9'];
  const zona = document.getElementById('zona'), pintura = document.getElementById('pintura'),
        linies = document.getElementById('linies'), paleta = document.getElementById('paleta'),
        eines = document.getElementById('eines'), avis = document.getElementById('avis');
  const pctx = pintura.getContext('2d', {willReadFrequently: true}), lctx = linies.getContext('2d');
  pintura.width = pintura.height = linies.width = linies.height = S;
  const GRUIXOS = [S / 24, S / 12, S / 48]; let ig = 0;
  let color = COLORS[0], historial = [], pintant = false, teLinies = false;

  COLORS.forEach((c, i) => {
    const d = document.createElement('div'); d.className = 'color' + (i === 0 ? ' actiu' : '');
    d.style.background = c;
    d.onclick = () => { color = c; paleta.querySelectorAll('.color').forEach(x => x.classList.remove('actiu')); d.classList.add('actiu'); };
    paleta.insertBefore(d, eines);
  });
  document.getElementById('gruix').onclick = () => { ig = (ig + 1) % GRUIXOS.length; };
  document.getElementById('desfes').onclick = () => { if (historial.length) pctx.putImageData(historial.pop(), 0, 0); };
  document.getElementById('neteja').onclick = () => { guarda(); pctx.fillStyle = '#fff'; pctx.fillRect(0, 0, S, S); };
  function guarda() { historial.push(pctx.getImageData(0, 0, S, S)); if (historial.length > 15) historial.shift(); }

  // ---- de l'emoji al dibuix de linia ----
  // Gradient de Sobel sobre color + silueta: capta tambe les vores suaus
  // (antialiasing) que una simple comparacio de veins es deixava, i aixi el
  // dibuix quedi net. Despres s'engruixeix 1px i s'esborren
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
    const T = 45, linia = new Uint8Array(S * S);
    for (let y = 1; y < S - 1; y++) for (let x = 1; x < S - 1; x++) {
      const i = y * S + x; let mag = 0;
      for (let c = 0; c < 4; c++) { const v = ch[c];
        const gx = -v[i-S-1] + v[i-S+1] - 2*v[i-1] + 2*v[i+1] - v[i+S-1] + v[i+S+1];
        const gy = -v[i-S-1] - 2*v[i-S] - v[i-S+1] + v[i+S-1] + 2*v[i+S] + v[i+S+1];
        mag += Math.sqrt(gx*gx + gy*gy) * (c === 3 ? 2 : 1); }
      if (mag > T * 4) linia[i] = 1;
    }
    const mask = new Uint8Array(S * S);
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
  function pos(e) {
    const r = pintura.getBoundingClientRect();
    return {x: Math.floor((e.clientX - r.left) * S / r.width), y: Math.floor((e.clientY - r.top) * S / r.height)};
  }
  let ultim = null;
  zona.addEventListener('pointerdown', e => {
    e.preventDefault(); const p = pos(e);
    if (p.x < 0 || p.y < 0 || p.x >= S || p.y >= S) return;
    guarda(); pintant = true; zona.setPointerCapture(e.pointerId); ultim = p;
    pctx.strokeStyle = color; pctx.lineWidth = GRUIXOS[ig]; pctx.lineCap = 'round'; pctx.lineJoin = 'round';
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
  function dibuixaImatge() {
    // dibuix propi (PNG de linia): el que sigui fosc es linia, la resta transparent
    const im = new Image();
    im.onload = () => {
      const esc = Math.min((S - 40) / im.width, (S - 40) / im.height);
      lctx.imageSmoothingEnabled = true; lctx.imageSmoothingQuality = 'high';
      const w = im.width * esc, h = im.height * esc;
      lctx.clearRect(0, 0, S, S);
      lctx.drawImage(im, (S - w) / 2, (S - h) / 2, w, h);
      const img = lctx.getImageData(0, 0, S, S), p = img.data;
      for (let i = 0; i < p.length; i += 4) {
        const fosc = p[i+3] > 80 && (p[i] + p[i+1] + p[i+2]) < 360;
        p[i] = p[i+1] = p[i+2] = 34; p[i+3] = fosc ? 255 : 0;
      }
      lctx.putImageData(img, 0, 0); teLinies = true;
    };
    im.onerror = () => { avis.textContent = "No s'ha pogut carregar el dibuix: pinta lliurement! 🖌️"; };
    im.src = EMOJI;
  }
  function inicia() {
    if (EMOJI.startsWith('data:image')) { dibuixaImatge(); return; }
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

def make_calcul(diff, kind="Tots"):
    """Retorna (text, resposta, html_opcional)."""
    R = random.randint
    if kind == "Tots":
        kind = random.choice(CALCUL_ALL)
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
    if block == "Concurs":
        ss.problem_text = "concurs"
        ss.cq = None                      # en entrar o canviar de nivell: tornar a triar tema
        return
    if block == "Golut":
        ss.problem_text = "golut"
        abans = ss.golut["objectiu"] if ss.golut else None
        ss.golut = genera_golut(diff, ss.golut_op, evita=(abans,))
        ss.golut_n += 1
        return
    if block == "Penjat":
        ss.problem_text = "penjat"
        ss.penjat = genera_penjat(diff, evita=ss.penjat_vistes)
        ss.penjat_vistes = (ss.penjat_vistes + [ss.penjat["paraula"]])[-30:]
        ss.penjat_n += 1
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
    if block == "Calcul":
        for _ in range(40):
            text, ans, html = make_calcul(diff, ss.calcul_kind)
            key = html or text          # la piramide sempre te el mateix text
            if key not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.problem_html = text, ans, html
        _remember(html or text)
        return
    # Repte: barreja mates + calcul mental, sempre al nivell que ha triat el nen
    d = ss.diff
    if random.random() < 0.5:
        for _ in range(40):
            text, ans = make_math(d, random.choice([m for _, m, _ in OPS]))
            if text not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.kind_label = text, ans, "Càlcul"
        _remember(text)
    else:
        k = random.choice(CALCUL_ALL)
        for _ in range(40):
            text, ans, html = make_calcul(d, k)
            if (html or text) not in ss.recent: break
        ss.problem_text, ss.correct_answer, ss.problem_html, ss.kind_label = text, ans, html, k
        _remember(html or text)

# ------------------------------------------------------------------ STATE
DEFAULTS = {
    'current_block': "Home", 'jugador': "", 'diff': "Fàcil", 'mode': "Sumes", 'calcul_kind': "Tots",
    'reading_pos': 0, 'rival_pos': 0, 'reading_word': "", 'word_start_time': time.time(),
    'words_pool': [], 'problem_text': "", 'problem_html': None, 'correct_answer': 0,
    'input_key': 0, 'last_status': None, 'reveal': None, 'attempts': 0, 'ratxa': 0,
    'kind_label': "", 'lectura_avis': False,
    'punts': 0, 'encerts': 0, 'errors': 0, 'millor_ratxa': 0, 'partides': 0, 'db_error': '',
    'repte': None, 'repte_report': None, 'recent': [], 'last_gif': '', 'last_msg': '',
    'base': None, 'jugador_actiu': '', 'dies': [], 'avisos': [], 'cal_mes': None, 'lletra_idx': 0, 'lletra_set': 'Lletres',
    'sopa': None, 'sopa_n': 0, 'cq': None, 'cq_records': {}, 'golut': None, 'golut_n': 0, 'golut_op': 'suma', 'penjat': None, 'penjat_n': 0, 'penjat_vistes': [], 'memory': None, 'memory_n': 0, 'dibuix_idx': 0,
    # concurs: 'sol' o 'grup'; en grup, la pantalla gran es 'mestre' i cada mobil 'jugador'
    'cq_mode': None, 'cq_cat': None, 'cg_cat': 'tot', 'cg_rol': None, 'cg_pin': '', 'cg_pid': '', 'cg_edita': False, 'cg_avis': '',
    'cg_tema': 'barreja', 'cg_nivell': 'Fàcil', 'cg_n': 10, 'cg_seg': 20,
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
    if block == "Concurs": ss.cq_mode = None     # primer: jugar sol o en grup
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
    marca_avui()
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
    register(True)                         # +1 punt, encert, ratxa i medalla del dia
    ss.last_status = "correct"
    new_problem()


def golut_encert():
    ss = st.session_state
    if ss.current_block != "Golut" or ss.golut is None:
        return
    register(True)
    ss.last_status = "correct"
    new_problem()


def golut_error():
    """El component ja ha ensenyat la solucio: nomes comptem l'error i passem
    al seguent monstre, sense cartell."""
    ss = st.session_state
    if ss.current_block != "Golut" or ss.golut is None:
        return
    register(False)
    new_problem()


def set_golut_op(op):
    st.session_state.golut_op = op
    new_problem()


def penjat_guanyat():
    ss = st.session_state
    if ss.current_block != "Penjat" or ss.penjat is None:
        return
    ss.punts += PENJAT_CFG[ss.penjat["level"]]["bonus"]
    register(True)
    ss.last_status = "correct"
    new_problem()


def penjat_perdut():
    """El component ja ha ensenyat la paraula en vermell: nomes comptem l'error
    i passem a la seguent, sense cartell (el Toni no en vol durant el joc)."""
    ss = st.session_state
    if ss.current_block != "Penjat" or ss.penjat is None:
        return
    register(False)
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

def set_calcul_kind(k):
    st.session_state.calcul_kind = k; new_problem()

def sync_progres():
    """Desa el total del nen (el que ja tenia + el d'aquesta sessio)."""
    ss = st.session_state
    if not ss.jugador or ss.base is None:
        return
    try:
        b = ss.base
        db_save(ss.jugador, b["punts"] + ss.punts, b["encerts"] + ss.encerts,
                b["errors"] + ss.errors, max(b["millor_ratxa"], ss.millor_ratxa),
                b["partides"] + ss.partides)
    except Exception as e:
        ss.db_error = str(e)


def carrega_base():
    """En obrir l'app, recupera el que ja s'havia fet en aquest dispositiu."""
    ss = st.session_state
    nom = ss.jugador
    if nom == ss.jugador_actiu:
        return
    ss.jugador_actiu = nom
    dia = avui().isoformat()
    jugat_avui = dia in ss.dies
    if not nom:
        ss.base = None
        ss.dies = [dia] if jugat_avui else []
        return
    try:
        ss.base = db_load(nom)
        ss.dies = sorted(set(ss.base.get("dies") or []))
        ss.db_error = ""
        if jugat_avui and dia not in ss.dies:
            ss.dies = sorted(set(ss.dies) | {dia})
            db_marca_dia(nom, dia)
    except Exception as e:
        ss.base = None
        ss.dies = [dia] if jugat_avui else []
        ss.db_error = str(e)


def register(correct):
    ss = st.session_state
    if correct:
        ss.punts += 1; ss.encerts += 1; ss.ratxa += 1
        ss.millor_ratxa = max(ss.millor_ratxa, ss.ratxa)
    else:
        ss.errors += 1; ss.ratxa = 0
    marca_avui()
    sync_progres()

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
        sync_progres()

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

if not st.session_state.problem_text and st.session_state.current_block not in ("Home", "Calendari"):
    new_problem()

# -------------------------------------------------------------- CONCURS: PANTALLES
def _cq_ops_html(q, triada=None):
    """Les quatre respostes, marcant la bona (i la triada, si era dolenta)."""
    caixes = []
    for i, (forma, color, _) in enumerate(CONCURS_FORMES):
        cls = "cq-op " + ("bona" if i == q["correcta"] else "apagada")
        if i == triada and i != q["correcta"]:
            cls += " triada"
        caixes.append(f"<div class='{cls}' style='background:{color};'><span class='forma'>{forma}</span>"
                      f"<span>{q['opcions'][i]}</span></div>")
    return f"<div class='cq-ops'>{''.join(caixes)}</div>"


def _cq_emoji_html(q, mida=""):
    """El dibuix de la pregunta. Si n'hi ha molts (comptar, series), mes petit perque hi capiguen."""
    if not q["emoji"]:
        return ""
    llarg = len(re.sub(r"<[^>]+>|\s|\ufe0f", "", q["emoji"])) > 4
    estil = "font-size:clamp(1.8rem, 8vw, 3.2rem);" if llarg else mida
    return f"<div class='cq-emoji' style='{estil}'>{q['emoji']}</div>"


def _cq_pregunta_html(q):
    emoji = _cq_emoji_html(q)
    return f"{emoji}<div class='cq-preg'>{q['text']}</div>"


def _text_veu(q):
    """El que llegeix el boto 🔊: la pregunta i les quatre respostes, sense emojis ni simbols."""
    t = q["text"].lower()
    for a, b in (("×", " per "), ("+", " més "), ("−", " menys "), ("= ?", ", quant fa?"), ("→", " ")):
        t = t.replace(a, b)
    ops = [re.sub(r"[^\w\s,.'€·:-]", "", o).strip().lower() for o in q["opcions"]]
    return t + ". " + ". ".join(o for o in ops if o) + "."


def boto_escolta(q):
    """🔊 Llegeix la pregunta en veu alta (veu del navegador, en catala si n'hi ha). Per als que encara
    llegeixen a poc a poc: al benchmark de concursos, la lectura en veu alta es de pagament."""
    with st.container(key="escolta"):
        _boto_escolta_html(q)


def _boto_escolta_html(q):
    components.html(
        "<div style='text-align:center;margin:0'><button id='b' style='font-family:sans-serif;font-weight:700;font-size:20px;border:0;border-radius:30px;"
        "padding:10px 22px;background:#2D3436;color:white;cursor:pointer;'>🔊 ESCOLTA</button></div><script>"
        "var t=" + json.dumps(_text_veu(q)) + ";document.getElementById('b').onclick=function(){"
        "var s=window.speechSynthesis;if(!s)return;s.cancel();var u=new SpeechSynthesisUtterance(t);"
        "u.lang='ca-ES';var v=s.getVoices().filter(function(x){return /^ca/i.test(x.lang);})[0];"
        "if(v)u.voice=v;u.rate=0.9;s.speak(u);};</script>", height=60)


def _cq_punts(n):
    return f"{n:,}".replace(",", ".")


def _cq_comenca(tema):
    ss = st.session_state
    # vistes d'aquest dispositiu (o d'aquesta sessio, si encara no sabem quin dispositiu es)
    mem = _cq_memoria() if ss.jugador else ss.setdefault("cq_vistes_sessio", {})
    vistes = mem.setdefault((ss.jugador, tema, ss.diff), {})
    preguntes = concurs_preguntes(tema, ss.diff, CONCURS_N, vistes)
    claus = [cq_clau(q) for q in preguntes]
    if any(c in vistes for c in claus):
        vistes.clear()                 # ja les ha vistes totes: es torna a comencar
    vistes.update(dict.fromkeys(claus))
    ss.cq = {"tema": tema, "nivell": ss.diff, "segons": CONCURS_SEGONS[ss.diff],
             "preguntes": preguntes, "idx": 0,
             "t0": time.time(), "resposta": None, "punts": 0, "encerts": 0, "fase": "pregunta"}


def _cq_respon(opcio):
    ss = st.session_state
    g = ss.cq
    if not g or g["fase"] != "pregunta":
        return
    t = time.time() - g["t0"]
    q = g["preguntes"][g["idx"]]
    encert = opcio == q["correcta"]
    # mes rapid, mes punts: de 1000 (a l'instant) a 500 (just al final)
    punts = round(1000 * (1 - min(t, g["segons"]) / (2 * g["segons"]))) if encert else 0
    g["resposta"] = {"opcio": opcio, "punts": punts, "t": time.time()}
    g["punts"] += punts
    g["encerts"] += int(encert)
    g["fase"] = "resultat"
    register(encert)


def _cq_seguent(g):
    """Passa a la seguent pregunta, o al final (i apunta el record d'aquest tema i nivell)."""
    ss = st.session_state
    g["idx"] += 1
    if g["idx"] < len(g["preguntes"]):
        g["fase"], g["t0"], g["resposta"] = "pregunta", time.time(), None
        return False
    clau = f"{g['tema']}|{g['nivell']}"
    g["record_abans"] = ss.cq_records.get(clau, 0)
    ss.cq_records[clau] = max(g["record_abans"], g["punts"])
    g["fase"] = "final"
    return True


@st.fragment(run_every=1)
def concurs_partida():
    """La partida en curs. Es refresca sola cada segon pel compte enrere."""
    ss = st.session_state
    g = ss.cq
    if not g:
        return
    ara = time.time()
    if g["fase"] == "pregunta" and ara - g["t0"] >= g["segons"]:
        # s'ha acabat el temps: no resta res, nomes ensenya la bona
        g["fase"], g["resposta"] = "resultat", {"opcio": None, "punts": 0, "t": ara}
    if g["fase"] == "resultat" and ara - g["resposta"]["t"] >= CONCURS_PAUSA:
        if _cq_seguent(g):
            st.rerun(scope="app")      # pantalla final (i, si toca, la medalla del dia)
    if g["fase"] == "final":
        return
    q = g["preguntes"][g["idx"]]
    if g["fase"] == "pregunta":
        queda = max(0, int(round(g["segons"] - (ara - g["t0"]))))
        st.markdown(f"<div class='cq-cap'><span>PREGUNTA {g['idx'] + 1} DE {len(g['preguntes'])}</span>"
                    f"<span class='cq-temps{' poc' if queda <= 5 else ''}'>{queda}</span>"
                    f"<span>⭐ {_cq_punts(g['punts'])}</span></div>" + _cq_pregunta_html(q),
                    unsafe_allow_html=True)
        boto_escolta(q)
        for fila in ((0, 1), (2, 3)):
            cols = st.columns(2)
            for col, i in zip(cols, fila):
                col.button(f"{CONCURS_FORMES[i][0]}  {q['opcions'][i]}", key=f"conc_op_{i}",
                           use_container_width=True, on_click=_cq_respon, args=(i,))
        return
    r = g["resposta"]
    if r["punts"] > 0:
        cap = f"<div class='cq-feedback si'>CORRECTE! 🎉 +{r['punts']}</div>"
    elif r["opcio"] is None:
        cap = "<div class='cq-feedback no'>S'HA ACABAT EL TEMPS! ⏰</div>"
    else:
        cap = "<div class='cq-feedback no'>GAIREBÉ! ERA AQUESTA 💪</div>"
    st.markdown(f"<div class='cq-cap'><span>PREGUNTA {g['idx'] + 1} DE {len(g['preguntes'])}</span>"
                f"<span>⭐ {_cq_punts(g['punts'])}</span></div>"
                + cap + _cq_pregunta_html(q) + _cq_ops_html(q, r["opcio"]), unsafe_allow_html=True)


def concurs_solo():
    """Triar tema, jugar i veure el resultat. Sense codis ni adults."""
    ss = st.session_state
    g = ss.cq
    if g and g["fase"] == "final":
        n = len(g["preguntes"])
        if g["punts"] > g["record_abans"] and g["record_abans"] > 0:
            rec = "<div class='cq-gran' style='color:#F7B731;'>🏆 NOU RÈCORD! 🏆</div>"
        elif g["record_abans"] > 0:
            rec = f"<div class='cq-info'>El teu rècord en aquest tema: ⭐ {_cq_punts(g['record_abans'])}</div>"
        else:
            rec = "<div class='cq-info'>Aquest és el teu primer rècord en aquest tema!</div>"
        st.markdown(f"<div class='cq-feedback si'>FI DEL KAHOOT!<br>Has encertat {g['encerts']} de {n}<br>"
                    f"⭐ {_cq_punts(g['punts'])} punts</div>" + rec, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("🔁 TORNAR A JUGAR", key="cq_altre", use_container_width=True,
                  on_click=_cq_comenca, args=(g["tema"],))
        c2.button("🎲 UN ALTRE TEMA", key="cq_tema_nou", use_container_width=True,
                  on_click=lambda: ss.update(cq=None))
        return
    if g:
        concurs_partida()
        st.button("⏹️ SORTIR", key="cq_surt", on_click=lambda: ss.update(cq=None))
        return
    def boto_tema(col, label, tema):
        rec = ss.cq_records.get(f"{tema}|{ss.diff}")
        col.button(label + (f" · 🏆 {_cq_punts(rec)}" if rec else ""), key=f"cq_tema_{tema}",
                   use_container_width=True, on_click=_cq_comenca, args=(tema,))

    if not ss.cq_cat:
        st.markdown(f"<div class='cq-info'>Tria una categoria i després un tema: {CONCURS_N} preguntes, "
                    f"{CONCURS_SEGONS[ss.diff]} segons cadascuna. Com més ràpid, més punts!</div>",
                    unsafe_allow_html=True)
        boto_tema(st, "🎲 BARREJA DE TOT", "barreja")
        for i in range(0, len(CT.CATEGORIES), 2):
            cols = st.columns(2)
            for col, (cat, nom) in zip(cols, CT.CATEGORIES[i:i + 2]):
                col.button(f"{nom} · {len(CT.temes_de(cat))}", key=f"cq_cat_{cat}", use_container_width=True,
                           on_click=lambda c=cat: ss.update(cq_cat=c))
        st.button("🔙 TORNAR", key="cq_sol_torna", on_click=lambda: ss.update(cq_mode=None, cq=None))
        return
    cat = ss.cq_cat
    st.markdown(f"<div class='cq-info'><b>{CT.NOM_CATEGORIA[cat]}</b> · tria un tema</div>", unsafe_allow_html=True)
    temes = [(f"🎲 BARREJA", f"barreja_{cat}")] + [(l, t) for t, l in CT.temes_de(cat)]
    for i in range(0, len(temes), 2):
        cols = st.columns(2)
        for col, (label, tema) in zip(cols, temes[i:i + 2]):
            boto_tema(col, label, tema)
    st.button("🔙 CATEGORIES", key="cq_cat_torna", on_click=lambda: ss.update(cq_cat=None))


# ------------------------------------------------------ CONCURS EN GRUP: PANTALLES
def cg_url(pin):
    """L'adreca del QR. A Streamlit Cloud, la publica; en local, la mateixa per on s'ha obert l'app
    (aixi es pot provar a casa amb el mobil a la mateixa wifi)."""
    base = APP_URL
    try:
        u = urllib.parse.urlsplit(st.context.url or "")
        if u.hostname and not u.hostname.endswith("streamlit.app"):
            base = f"{u.scheme}://{u.netloc}"
    except Exception:
        pass
    return f"{base}/?sala={pin}"


@st.cache_data(max_entries=64, show_spinner=False)
def qr_data_uri(url):
    """QR generat aqui mateix (segno, Python pur): cap servei de tercers veu l'adreca."""
    try:
        import segno
        return segno.make_qr(url, error="m").svg_data_uri(scale=10, border=2, dark="#2D3436")
    except Exception as e:
        print("qr:", e, flush=True)
        return ""


def cg_av(j, mida=""):
    """L'avatar d'un jugador: el seu animal dins un cercle del seu color. Cap nom."""
    return f"<span class='cg-av {mida}' style='background:{j['color']};'>{j['emoji']}</span>"


def cg_resum(sa):
    tema = {t: l for l, t in CONCURS_TEMES}.get(sa["tema"], sa["tema"])
    return f"{tema} · {sa['nivell'].upper()} · {sa['n']} PREGUNTES · {sa['segons']} SEGONS"


def cg_ops_html(q):
    """Pantalla gran: les quatre respostes amb el seu color i forma."""
    caixes = "".join(f"<div class='cq-op' style='background:{color};'><span class='forma'>{forma}</span>"
                     f"<span>{q['opcions'][i]}</span></div>" for i, (forma, color, _) in enumerate(CONCURS_FORMES))
    return f"<div class='cq-ops cg-ops'>{caixes}</div>"


def cg_barres_html(q, vots):
    """Grafic de barres: quanta gent ha triat cada resposta. La bona, destacada."""
    maxim = max(vots) or 1
    barres = []
    for i, (forma, color, _) in enumerate(CONCURS_FORMES):
        bona = i == q["correcta"]
        barres.append(f"<div class='cg-barra {'bona' if bona else 'no'}'><div class='n'>{vots[i]}</div>"
                      f"<div class='col' style='height:{round(150 * vots[i] / maxim)}px;background:{color};'></div>"
                      f"<div class='peu' style='background:{color};'>{forma} {q['opcions'][i]}{' ✓' if bona else ''}"
                      f"</div></div>")
    return f"<div class='cg-barres'>{''.join(barres)}</div>"


def cg_top_html(sa, n=5):
    files = []
    for pos, _, j in sala_classificacio(sa)[:n]:
        foc = f"<span class='foc'>🔥 {j['ratxa']}</span>" if j["ratxa"] >= 2 else ""
        files.append(f"<div class='cg-fila'><span class='pos'>{pos}</span>{cg_av(j, 'petit')}{foc}"
                     f"<span class='pts'>{_cq_punts(j['punts'])}</span></div>")
    return f"<div class='cg-top'><div class='cg-top-tit'>🏅 TOP {n}</div>{''.join(files)}</div>"


def cg_podi_html(sa):
    """Podi amb els tres primers (segon, primer, tercer) i l'animacio de festa (static/festa)."""
    cl = sala_classificacio(sa)[:3]
    esgraons = []
    for k in (1, 0, 2):
        if k < len(cl):
            pos, _, j = cl[k]
            esgraons.append(f"<div class='cg-esgrao p{k + 1}'>{cg_av(j, 'gran' if k == 0 else 'mig')}"
                            f"<div class='pts'>⭐ {_cq_punts(j['punts'])}</div><div class='cg-bloc'>{pos}</div></div>")
    festa = ("<div class='cg-podi-cap'><img class='cg-festa' src='app/static/festa/1f389.webp' alt=''>"
             "<img class='cg-trofeu' src='app/static/festa/1f3c6.webp' alt='Trofeu'>"
             "<img class='cg-festa' src='app/static/festa/1f38a.webp' alt=''></div>")
    return festa + f"<div class='cg-podi'>{''.join(esgraons)}</div>"


def cg_prepara_edicio(sa):
    """Omple el formulari amb la configuracio de la sala per canviar-la (la gent es queda)."""
    ss = st.session_state
    ss.cg_tema = sa["tema"]
    ss.cg_cat = CT.categoria_de(sa["tema"]) or "tot"
    ss.cg_nivell, ss.cg_n, ss.cg_seg, ss.cg_edita = sa["nivell"], sa["n"], sa["segons"], True


def cg_deixa_sala():
    """La pantalla gran tanca la sala: es tornen a veure les opcions per crear-ne una."""
    ss = st.session_state
    if ss.cg_pin:
        sala_tanca(ss.cg_pin)
    ss.update(cg_rol=None, cg_pin="", cg_edita=False, cg_avis="")


def cg_surt():
    """Un jugador surt: fora la sala de l'adreca, perque no hi torni a entrar sol."""
    ss = st.session_state
    for k in ("sala", "jo"):
        if k in st.query_params:
            del st.query_params[k]
    ss.update(cg_rol=None, cg_pin="", cg_avis="", cq_mode=None, current_block="Home")


@st.fragment(run_every=1)
def cg_mestre():
    """La pantalla gran (projector o pissarra digital). Es refresca sola cada segon."""
    ss = st.session_state
    pin = ss.cg_pin
    sa = sala_estat(pin)
    if sa is None:
        st.markdown("<div class='cq-feedback espera'>Aquesta sala ja no hi és<br>(ha passat molta estona "
                    "sense jugar o l'app s'ha reiniciat)</div>", unsafe_allow_html=True)
        if st.button("✨ CREAR-NE UNA DE NOVA", key="cg_m_nova", use_container_width=True):
            ss.update(cg_rol=None, cg_pin="", cg_edita=False)
            st.rerun(scope="app")
        return
    jug, fase, idx = sa["jugadors"], sa["fase"], sa["idx"]
    n_q = len(sa["preguntes"])

    if fase == "espera":
        url = cg_url(pin)
        c1, c2 = st.columns([5, 7], gap="large")
        qr = qr_data_uri(url)
        img = f"<img class='cg-qr' src='{qr}' alt='Codi QR per entrar a la sala'>" if qr else ""
        c1.markdown(f"<div class='cg-qr-caixa'>{img}<div class='cg-qr-peu'>📷 ESCANEJA'L PER JUGAR</div>"
                    f"<div class='cg-url' data-url='{url}' data-pin='{pin}'>{url.split('://', 1)[-1]}</div></div>",
                    unsafe_allow_html=True)
        avatars = "".join(cg_av(j) for j in sorted(jug.values(), key=lambda j: j["entrat"]))
        with c2:
            st.markdown(f"<div class='cg-titol'>👥 {len(jug)} A LA SALA</div>"
                        + (f"<div class='cg-avatars'>{avatars}</div>" if jug else
                           "<div class='cg-mini'>Esperant que entri algú... A cadascú li tocarà un animal.</div>")
                        + f"<div class='cg-resum'>{cg_resum(sa)}</div>", unsafe_allow_html=True)
            st.button("▶️ COMENÇAR", key="cg_m_start", use_container_width=True, disabled=not jug,
                      on_click=sala_avanca, args=(pin, "espera", 0))
            b1, b2 = st.columns(2)
            if b1.button("⚙️ CANVIAR TEMA", key="cg_m_config", use_container_width=True):
                cg_prepara_edicio(sa)
                st.rerun(scope="app")
            if b2.button("🚪 TANCAR LA SALA", key="cg_m_tanca_sala", use_container_width=True):
                cg_deixa_sala()
                st.rerun(scope="app")
        return

    if fase == "final":
        resp = [r for j in jug.values() for r in j["respostes"].values()]
        pct = round(100 * sum(r["encert"] for r in resp) / len(resp)) if resp else 0
        st.markdown("<div class='cg-titol'>🎉 FI DEL KAHOOT! 🎉</div>" + cg_podi_html(sa)
                    + f"<div class='cg-resum'>Entre tots i totes heu encertat el <b>{pct}%</b> de les respostes. "
                    "Molt bona feina, equip! 💪</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.button("🔁 TORNAR A JUGAR", key="cg_m_torna", use_container_width=True,
                  on_click=sala_torna, args=(pin,))
        if c2.button("⚙️ CANVIAR TEMA", key="cg_m_config2", use_container_width=True):
            sala_torna(pin)
            cg_prepara_edicio(sa)
            st.rerun(scope="app")
        if c3.button("🚪 TANCAR LA SALA", key="cg_m_tanca_sala2", use_container_width=True):
            cg_deixa_sala()
            st.rerun(scope="app")
        return

    q = sa["preguntes"][idx]
    emoji = _cq_emoji_html(q)
    if fase == "pregunta":
        queda = max(0, int(round(sa["segons"] - (time.time() - sa["t0"]))))
        respostes = sum(1 for j in jug.values() if idx in j["respostes"])
        st.markdown(f"<div class='cg-cap'><span>PREGUNTA {idx + 1} DE {n_q}</span>"
                    f"<span class='cq-temps{' poc' if queda <= 5 else ''}'>{queda}</span>"
                    f"<span class='cg-rebudes'>📥 {respostes} DE {len(jug)}</span></div>"
                    + emoji + f"<div class='cg-preg'>{q['text']}</div>" + cg_ops_html(q), unsafe_allow_html=True)
        boto_escolta(q)
        st.button("⏭️ JA N'HI HA PROU", key="cg_m_tanca", use_container_width=True,
                  on_click=sala_avanca, args=(pin, "pregunta", idx))
        return

    # resultat de la pregunta: la bona, quanta gent ha triat cada opcio i el top 5
    vots = sala_vots(sa, idx)
    bons, n = vots[q["correcta"]], len(jug)
    frase = ("TOTHOM L'HA ENCERTADA! 🎉" if n and bons == n else
             f"{bons} DE {n} L'HAN ENCERTADA!" if bons else "AQUESTA COSTAVA! 💪")
    emoji = _cq_emoji_html(q, "font-size:3.2rem;")
    st.markdown(f"<div class='cg-cap'><span>PREGUNTA {idx + 1} DE {n_q}</span></div>"
                + emoji + f"<div class='cg-preg petita'>{q['text']}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2], gap="large")
    c1.markdown(cg_barres_html(q, vots) + f"<div class='cg-frase'>{frase}</div>", unsafe_allow_html=True)
    c2.markdown(cg_top_html(sa), unsafe_allow_html=True)
    ultima = idx + 1 >= n_q
    st.button("🏆 VEURE EL PODI" if ultima else "▶️ SEGÜENT PREGUNTA", key="cg_m_seg",
              use_container_width=True, on_click=sala_avanca, args=(pin, "resultat", idx))


def cg_respon(opcio):
    ss = st.session_state
    sala_respon(ss.cg_pin, ss.cg_pid, opcio)    # res es desa: ni punts ni medalla


@st.fragment(run_every=1)
def cg_jugador():
    """El mobil de cada jugador: el seu animal, quatre botons grans i com li ha anat."""
    ss = st.session_state
    sa = sala_estat(ss.cg_pin, ss.cg_pid)
    jo = sa["jugadors"].get(ss.cg_pid) if sa else None
    if jo is None:
        msg = ("Aquesta sala ja és plena.<br>Podeu crear-ne una altra o jugar sols." if ss.cg_avis == "plena" else
               "Aquesta partida ja no hi és.<br>Quan la pantalla gran en tingui una de nova, escaneja'n el QR.")
        st.markdown(f"<div class='cq-feedback espera'>{msg}</div>", unsafe_allow_html=True)
        if st.button("🏠 INICI", key="cg_j_inici", use_container_width=True):
            cg_surt()
            st.rerun(scope="app")
        return
    fase, idx, n_q = sa["fase"], sa["idx"], len(sa["preguntes"])
    pos = {pid: p for p, pid, _ in sala_classificacio(sa)}[ss.cg_pid]
    n = len(sa["jugadors"])

    if fase == "espera":
        st.markdown(f"<div class='cg-jo-centre'>{cg_av(jo, 'gran')}</div>"
                    "<div class='cq-feedback espera'>JA HI ETS! 🎉<br>Aquest és el teu animal.<br>"
                    "Mira la pantalla gran: començarem de seguida</div>", unsafe_allow_html=True)
        st.button("🚪 SORTIR", key="cg_j_surt", on_click=cg_surt)
        return
    st.markdown(f"<div class='cg-jo'>{cg_av(jo, 'mig')}<span>⭐ {_cq_punts(jo['punts'])}</span></div>",
                unsafe_allow_html=True)
    if fase == "final":
        medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, "🏁")
        encerts = sum(r["encert"] for r in jo["respostes"].values())
        st.markdown(f"<div class='cq-feedback si'>{medalla} POSICIÓ {pos} DE {n}<br>⭐ {_cq_punts(jo['punts'])} punts"
                    f"<br>Has encertat {encerts} de {n_q}</div>"
                    "<div class='cg-mini'>Mira el podi a la pantalla gran! Si es torna a jugar, la partida "
                    "nova sortirà aquí sola.</div>", unsafe_allow_html=True)
        st.button("🚪 SORTIR", key="cg_j_surt", on_click=cg_surt)
        return
    q = sa["preguntes"][idx]
    meva = jo["respostes"].get(idx)
    if fase == "pregunta" and meva is None:
        queda = max(0, int(round(sa["segons"] - (time.time() - sa["t0"]))))
        st.markdown(f"<div class='cg-cap'><span>PREGUNTA {idx + 1} DE {n_q}</span>"
                    f"<span class='cq-temps{' poc' if queda <= 5 else ''}'>{queda}</span></div>",
                    unsafe_allow_html=True)
        with st.container(key="cg_botons"):
            for fila in ((0, 1), (2, 3)):
                cols = st.columns(2)
                for col, i in zip(cols, fila):
                    col.button(f"{CONCURS_FORMES[i][0]}  {q['opcions'][i]}", key=f"cg_op_{i}",
                               use_container_width=True, on_click=cg_respon, args=(i,))
        return
    if fase == "pregunta":
        st.markdown("<div class='cq-feedback espera'>RESPOSTA ENVIADA! ✅<br>Esperem la resta...</div>",
                    unsafe_allow_html=True)
        return
    # resultat
    bona = f"{CONCURS_FORMES[q['correcta']][0]} {q['opcions'][q['correcta']]}"
    if meva and meva["encert"]:
        ratxa = f"<br>🔥 {meva['ratxa']} seguides: +{meva['bonus']}" if meva["bonus"] else ""
        st.markdown(f"<div class='cq-feedback si'>CORRECTE! 🎉<br>+{_cq_punts(meva['punts'])} punts{ratxa}</div>",
                    unsafe_allow_html=True)
    elif meva:
        st.markdown(f"<div class='cq-feedback no'>INCORRECTE 💪<br>Era {bona}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='cq-feedback no'>S'HA ACABAT EL TEMPS ⏰<br>Era {bona}</div>",
                    unsafe_allow_html=True)
    st.markdown(f"<div class='cg-titol'>POSICIÓ {pos} DE {n}</div>", unsafe_allow_html=True)


def cg_crea():
    ss = st.session_state
    tema = ss.cg_tema if ss.cg_tema in {t for _, t in CONCURS_TEMES} else "barreja"
    nivell, n, seg = ss.cg_nivell or "Fàcil", ss.cg_n or 10, ss.cg_seg or 20
    if ss.cg_pin and ss.cg_edita:
        sala_config(ss.cg_pin, tema, nivell, n, seg)
        ss.cg_edita = False
        return
    pin = sala_crea(tema, nivell, n, seg)
    if pin:
        ss.update(cg_pin=pin, cg_rol="mestre", cg_edita=False, cg_avis="")
    else:
        ss.cg_avis = "Ara mateix hi ha massa partides obertes. Torna-ho a provar d'aquí a una estona."


def cg_tria():
    """La pantalla gran tria tema, nivell, preguntes i segons, i crea la sala."""
    ss = st.session_state
    editant = bool(ss.cg_pin) and ss.cg_edita
    if not editant:
        st.markdown("<div class='cq-info'>Aquesta serà la <b>pantalla gran</b> (projector, pissarra digital o "
                    "ordinador). Cadascú hi entra escanejant el QR amb el mòbil o la tauleta: no cal escriure "
                    "res i a cadascú li toca un animal.</div>", unsafe_allow_html=True)
    # st.radio i no st.pills/segmented_control: l'AppTest de Streamlit 1.50 no sap llegir-los (18 nov 2026)
    noms = {t: l for l, t in CONCURS_TEMES}
    cats = {"tot": "🎲 TOT BARREJAT", **CT.NOM_CATEGORIA}
    st.radio("Categoria", list(cats), key="cg_cat", format_func=cats.get, horizontal=True)
    opcions = (["barreja"] if ss.cg_cat == "tot" else
               [f"barreja_{ss.cg_cat}"] + [t for t, _ in CT.temes_de(ss.cg_cat)])
    if ss.cg_tema not in opcions:
        ss.cg_tema = opcions[0]
    st.radio("Tema", opcions, key="cg_tema", format_func=noms.get, horizontal=True)
    st.radio("Nivell", [d for d, _ in DIFFS], key="cg_nivell", horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        st.radio("Preguntes", list(CG_N), key="cg_n", horizontal=True)
    with c2:
        st.radio("Segons per pregunta", list(CG_SEGONS), key="cg_seg", horizontal=True)
    st.button("✅ FET" if editant else "✨ CREAR LA SALA", key="cg_crea", use_container_width=True, on_click=cg_crea)
    if ss.cg_avis:
        st.markdown(f"<div class='cq-info'>{ss.cg_avis}</div>", unsafe_allow_html=True)
    st.button("🔙 TORNAR", key="cg_tria_torna",
              on_click=lambda: ss.update(cg_edita=False) if editant else ss.update(cq_mode=None, cg_avis=""))


def cg_entra_num():
    """Alternativa al QR: el numero de sala que surt petit a la pantalla gran."""
    ss = st.session_state
    pin = "".join(ch for ch in (ss.cg_num or "") if ch.isdigit())
    ss.cg_num = ""
    if len(pin) == 4:
        st.query_params["sala"] = pin       # i cg_entra_per_url() hi entra, com amb el QR


def cg_portada():
    """CONCURS: jugar sol (com sempre) o en grup amb una pantalla gran."""
    ss = st.session_state
    c1, c2 = st.columns(2)
    with c1:
        st.button("👤 JUGAR SOL", key="cq_sol", use_container_width=True,
                  on_click=lambda: ss.update(cq_mode="sol", cq=None))
        st.markdown("<div class='desc'>Tria tema i nivell, i bat el teu rècord</div>", unsafe_allow_html=True)
    with c2:
        st.button("📺 JUGAR EN GRUP (PANTALLA GRAN)", key="cq_grup", use_container_width=True,
                  on_click=lambda: ss.update(cq_mode="grup", cg_edita=False,
                                             cg_rol="mestre" if ss.cg_rol == "mestre" else None))
        st.markdown("<div class='desc'>Una pantalla gran fa les preguntes i cadascú respon des del seu mòbil "
                    "o tauleta</div>", unsafe_allow_html=True)
    st.markdown("<div class='cq-info' style='margin-top:16px;'>📷 Per entrar a una partida en grup, escaneja "
                "amb la càmera el QR de la pantalla gran.</div>", unsafe_allow_html=True)
    with st.expander("No pots fer servir la càmera?"):
        st.text_input("Número de sala (el petit que surt sota el QR)", key="cg_num", max_chars=4,
                      on_change=cg_entra_num)
        st.button("ENTRAR", key="cg_entra", on_click=cg_entra_num)


def concurs():
    ss = st.session_state
    if ss.cq_mode == "sol":
        concurs_solo()
    elif ss.cq_mode == "grup" and ss.cg_rol == "jugador":
        cg_jugador()
    elif ss.cq_mode == "grup" and ss.cg_rol == "mestre" and ss.cg_pin and not ss.cg_edita:
        cg_mestre()
    elif ss.cq_mode == "grup":
        cg_tria()
    else:
        cg_portada()


def cg_entra_per_url():
    """S'ha obert l'app amb ?sala=<PIN> (el QR): entra sola a la sala, sense escriure res.
    Despres de la primera vegada, l'adreca porta tambe ?jo=<id a l'atzar> i, si es recarrega la
    pagina, es torna a ser el mateix animal (no un de nou)."""
    ss = st.session_state
    pin = st.query_params.get("sala", "")
    if not pin or (ss.cg_rol == "jugador" and ss.cg_pin == pin):
        return
    if not (len(pin) == 4 and pin.isdigit()):
        del st.query_params["sala"]
        return
    pid = st.query_params.get("jo", "")
    if not (len(pid) == 12 and all(c in "0123456789abcdef" for c in pid)):
        pid = ss.cg_pid if len(ss.cg_pid) == 12 else uuid.uuid4().hex[:12]
    ss.cg_pid = pid
    res = sala_entra(pin, pid)
    ss.update(current_block="Concurs", cq_mode="grup", cg_rol="jugador", cg_pin=pin, cg_edita=False,
              cg_avis="" if res == "ok" else res)
    if res == "ok":
        st.query_params["jo"] = pid


# ----------------------------------------------------------------- RENDER
def render_header():
    c1, c2 = st.columns([0.15, 0.85])
    with c1: st.markdown("<div style='font-size:2.4rem;text-align:center;'>🧮</div>", unsafe_allow_html=True)
    with c2: st.markdown("<h2 style='font-family:Bungee; color:#FF6B6B; margin:0;'>AVENTURA MATEMÀTICA</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

# Qui juga: un numero a l'atzar d'aquest dispositiu (cap nom). El JS el llegeix del navegador
# i l'escriu al camp amagat 'dispositiu'; el callback carrega el que ja s'hi havia fet.
carrega_base()
with st.container(key="amagat_dispositiu"):
    st.markdown("<style>.st-key-amagat_dispositiu{display:none !important;}</style>", unsafe_allow_html=True)
    st.text_input("dispositiu", key="dispositiu", on_change=on_dispositiu, label_visibility="collapsed")
    components.html(dispositiu_html(), height=0)
cg_entra_per_url()          # si s'ha obert amb el QR d'una sala (?sala=<PIN>), hi entra sola
render_header()

if st.session_state.current_block == "Home":
    st.markdown(f"<p style='font-size:1.1rem;'>Hola! Tria la teva aventura d'avui!</p>", unsafe_allow_html=True)
    # La descripcio va DINS de la columna del seu boto: aixi queda alineada
    # sempre. Abans anaven totes en una fila a part i es descolocaven en
    # arribar al final de linia. Files de tres; si a l'ultima en queda un, va al mig.
    nous = [b for b, fins in NOU_FINS.items() if avui() <= fins]
    if nous:
        st.markdown("<style>" + "".join(
            f".st-key-home_{b} div.stButton > button {{ background: linear-gradient(180deg,#FFD15C 0%,#F7B731 100%)"
            f" !important; box-shadow: 0 5px 0 #C8900E !important; color: #5A3E00 !important; }}"
            for b in nous) + "</style>", unsafe_allow_html=True)
    with st.container(key="homeblocks"):
        for i in range(0, len(BLOCKS), 3):
            fila = BLOCKS[i:i + 3]
            cols = st.columns(3)
            if len(fila) == 1:
                cols = cols[1:2]
            for col, (icon, label, block, desc) in zip(cols, fila):
                nou = block in NOU_FINS and avui() <= NOU_FINS[block]
                col.button(f"{icon} {label}" + (" · NOU!" if nou else ""), key=f"home_{block}",
                           use_container_width=True, on_click=start_block, args=(block,))
                col.markdown(f"<div class='desc'>{desc}</div>", unsafe_allow_html=True)
    s = st.session_state
    total = s.encerts + s.errors
    if total:
        st.markdown(
            f"<div class='scoreboard' style='margin-top:18px;'><div class='chip'>⭐ PUNTS: {s.punts}</div>"
            f"<div class='chip'>✅ ENCERTS: {round(100 * s.encerts / total)}%</div>"
            f"<div class='chip'>🔥 MILLOR RATXA: {s.millor_ratxa}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    medalles_txt = f" · ⭐ {len(s.dies)}" if s.dies else ""
    st.button(f"📅 EL MEU CALENDARI I MEDALLES{medalles_txt}", key="home_cal", use_container_width=True,
              on_click=lambda: st.session_state.update(current_block="Calendari", cal_mes=None))
    st.markdown("<br>", unsafe_allow_html=True)
    n = len(st.session_state.dies)
    hola = (f"Portes {n} medalla del dia. " if n == 1 else f"Portes {n} medalles del dia. " if n else "")
    st.caption(hola + "Cada dia que facis exercicis en guanyes una. El calendari es guarda en aquest "
               "mòbil o tauleta, sense cap nom ni cap dada personal.")
    st.markdown("<p style='font-size:0.7rem; opacity:0.6; margin-top:14px;'>Animacions: Noto Emoji "
                "(Google, CC BY 4.0) · Dibuixos: OpenMoji (CC BY-SA 4.0)</p>", unsafe_allow_html=True)
    if st.session_state.db_error:
        # El detall tecnic nomes al log: els pares no l'han de veure
        print("db_error:", st.session_state.db_error, flush=True)
        st.warning("Ara mateix no s'ha pogut desar el calendari. Pots jugar igual.")

elif st.session_state.current_block == "Calendari":
    # ---- El meu calendari: nomes les medalles d'aquest nen, sense comparar amb ningu ----
    ss = st.session_state
    hui = avui()
    if ss.cal_mes is None:
        ss.cal_mes = (hui.year, hui.month)
    any_, mes = ss.cal_mes
    jugats = _dates(ss.dies)
    guanyades = {m[0] for m in medalles_guanyades(ss.dies)}
    setmana = sum(1 for d in jugats if d.isocalendar()[:2] == hui.isocalendar()[:2])
    with st.container(key="maincard"):
        st.markdown("<h2 style='font-family:Bungee; color:#FF6B6B;'>📅 EL MEU CALENDARI</h2>",
                    unsafe_allow_html=True)
        st.markdown(
            f"<div class='scoreboard'><div class='chip'>⭐ {len(jugats)} "
            f"{'MEDALLA' if len(jugats) == 1 else 'MEDALLES'} DEL DIA</div>"
            f"<div class='chip'>📆 {setmana} {'DIA' if setmana == 1 else 'DIES'} AQUESTA SETMANA</div>"
            f"<div class='chip'>🏅 {len(guanyades)} DE {len(MEDALLES)} ESPECIALS</div></div>",
            unsafe_allow_html=True)
        import calendar as _calendar
        cel = [f"<div class='cal-cap'>{x}</div>" for x in DIES_SETMANA]
        for d in _calendar.Calendar(firstweekday=0).itermonthdates(any_, mes):
            if d.month != mes:
                cel.append("<div class='cal-dia buit'></div>")
                continue
            cls = "cal-dia" + (" fet" if d in jugats else "") + (" avui" if d == hui else "") \
                + (" futur" if d > hui else "")
            est = "<span class='est'>⭐</span>" if d in jugats else ""
            cel.append(f"<div class='{cls}'><span class='num'>{d.day}</span>{est}</div>")
        st.markdown(f"<div class='cal-mes'>{MESOS[mes - 1]} {any_}</div>"
                    f"<div class='cal'>{''.join(cel)}</div>", unsafe_allow_html=True)

        def _mou_mes(delta):
            a, m = st.session_state.cal_mes
            m += delta
            a, m = (a - 1, 12) if m < 1 else ((a + 1, 1) if m > 12 else (a, m))
            st.session_state.cal_mes = (a, m)

        with st.container(key="calnav"):
            nav = st.columns(2)
            nav[0].button("⬅️ MES ANTERIOR", key="cal_prev", use_container_width=True,
                          on_click=_mou_mes, args=(-1,))
            nav[1].button("MES SEGÜENT ➡️", key="cal_next", use_container_width=True,
                          on_click=_mou_mes, args=(1,), disabled=(any_, mes) >= (hui.year, hui.month))

        st.markdown("<h3 style='margin-top:18px;'>🏅 LES MEVES MEDALLES</h3>", unsafe_allow_html=True)
        targetes = []
        for mid, ico, nom, com, _ in MEDALLES:
            classe = "med" if mid in guanyades else "med no"
            targetes.append(f"<div class='{classe}'><div class='ico'>{ico}</div>"
                            f"<div class='nom'>{nom}</div><div class='com'>{com}</div></div>")
        st.markdown(f"<div class='med-grid'>{''.join(targetes)}</div>", unsafe_allow_html=True)
        if not _api() and get_engine()[1] and ss.jugador:
            st.caption("⚠️ Sense servidor configurat: el calendari només es guarda en aquest aparell "
                       "i es pot perdre. Calen els secrets `api_url` i `api_key`.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🏠 INICI", key="cal_home", use_container_width=True,
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
    if ss.current_block == "Calcul":
        active.append("sb_kind_" + slugify(ss.calcul_kind))
    if ss.current_block == "Golut":
        active += [f"ctl_gop_{ss.golut_op}", f"sb_gop_{ss.golut_op}"]
    if ss.current_block == "Lletres":
        active = ["ctl_set_lletres"] if ss.lletra_set == "Lletres" else ["ctl_set_numeros"]
    if ss.current_block == "Colors":
        active = []
    st.markdown("<style>" + "".join(
        f".st-key-{k} div.stButton > button {{ background: linear-gradient(180deg,#20BF6B 0%,#0FA45B 100%) !important;"
        f" box-shadow: 0 5px 0px #0B7A45 !important; }}" for k in active) + "</style>", unsafe_allow_html=True)

    # Concurs en grup: sense nivells ni menu lateral (el nivell es tria en crear la sala)
    cq_grup = ss.current_block == "Concurs" and ss.cq_mode == "grup"
    if cq_grup:
        st.markdown("<style>div[data-testid='stMainBlockContainer'] { padding-top: 1.2rem !important; }</style>",
                    unsafe_allow_html=True)
    # Barra sempre visible (si la sidebar es col.lapsa, els botons segueixen aqui)
    with st.container(key="controlbar"):
        if cq_grup:
            if ss.cg_rol != "jugador":      # el mobil del jugador surt amb el seu boto SORTIR
                cols = st.columns([1, 5])
                cols[0].button("🏠", key="ctl_home", use_container_width=True,
                               on_click=lambda: st.session_state.update(current_block="Home"))
        elif ss.current_block == "Lletres":
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
        if ss.current_block == "Golut":
            ocols = st.columns(2)
            for col, (label, op) in zip(ocols, GOLUT_OPS):
                col.button(label, key=f"ctl_gop_{op}", use_container_width=True,
                           on_click=set_golut_op, args=(op,))

    if not cq_grup:
        with st.sidebar:
            st.markdown("<h2 style='font-family:Bungee;'>MENU</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='chip'>⭐ {ss.punts} · 🔥 {ss.ratxa}</div>", unsafe_allow_html=True)
            st.markdown("---")
            if st.button("🏠 INICI", key="sb_home", use_container_width=True):
                ss.current_block = "Home"; safe_rerun()
            st.markdown("---")
            if ss.current_block == "Mates":
                for label, mode, slug in OPS:
                    if st.button(label, key=f"sb_op_{slug}", use_container_width=True):
                        set_mode(mode); safe_rerun()
                st.markdown("---")
            if ss.current_block == "Golut":
                for label, op in GOLUT_OPS:
                    if st.button(label, key=f"sb_gop_{op}", use_container_width=True):
                        set_golut_op(op); safe_rerun()
                st.markdown("---")
            if ss.current_block == "Calcul":
                for label, kind in CALCUL_KINDS:
                    key = "sb_kind_" + slugify(kind)
                    if st.button(label, key=key, use_container_width=True):
                        set_calcul_kind(kind); safe_rerun()
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
        elif ss.current_block == "Concurs":
            if ss.cq_mode == "sol":
                st.markdown(f"<h3>🎯 KAHOOT • {ss.diff.upper()}</h3>", unsafe_allow_html=True)
            elif not cq_grup:
                st.markdown("<h3>🎯 KAHOOT</h3>", unsafe_allow_html=True)
            elif ss.cg_rol != "jugador" and not (ss.cg_pin and not ss.cg_edita):   # en joc, tot el lloc per al joc
                st.markdown("<h3>🎯 KAHOOT EN GRUP</h3>", unsafe_allow_html=True)
        elif ss.current_block == "Golut":
            nom_op = dict((o, l.split(" ", 1)[1]) for l, o in GOLUT_OPS)[ss.golut_op]
            st.markdown(f"<h3>MONSTRE GOLUT • {ss.diff.upper()} • {nom_op}</h3>", unsafe_allow_html=True)
        elif ss.current_block == "Penjat":
            st.markdown(f"<h3>PENJAT • {ss.diff.upper()} • {ss.penjat['errors']} VIDES</h3>",
                        unsafe_allow_html=True)
        elif ss.current_block == "Memory":
            st.markdown(f"<h3>MEMORY • {ss.diff.upper()} • {ss.memory['tema'].upper()} • "
                        f"{len(ss.memory['cards']) // 2} PARELLES</h3>", unsafe_allow_html=True)
        elif ss.current_block == "Colors":
            emoji, nom = DIBUIXOS[ss.dibuix_idx]
            st.markdown(f"<h3>COLOREJA • DIBUIX {ss.dibuix_idx + 1} DE {len(DIBUIXOS)} • {nom}</h3>",
                        unsafe_allow_html=True)
        else:
            extra = f" • {ss.calcul_kind.upper()}" if ss.current_block == "Calcul" else ""
            nom = NOM_BLOC.get(ss.current_block, ss.current_block).upper()
            st.markdown(f"<h3>{nom} • {ss.diff.upper()}{extra}</h3>", unsafe_allow_html=True)

        if ss.current_block == "Lectura":
            st.markdown(f"<div class='race-track'><div class='car' style='left:{ss.reading_pos}%;'>🏎️</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='race-track' style='background:#444;'><div class='car' style='left:{ss.rival_pos}%; filter:hue-rotate(90deg);'>🏎️</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='problem-box' style='border-color:#4BCffa;'>{ss.reading_word}</div>", unsafe_allow_html=True)
            bcol, rcol = st.columns([3, 1])
            rcol.button("🔄 REINICIAR", key="lec_reset", use_container_width=True,
                        help="Torna els cotxes a la sortida", on_click=reset_lectura)
            if bcol.button("LLEGIT! ✅", use_container_width=True):
                marca_avui()
                elapsed = time.time() - ss.word_start_time
                # Sense cartells ni bloquejos: sempre avances. Pero si claques
                # sense haver llegit, el rival avanca mes que tu i acabes perdent.
                minim = max(0.7, 0.16 * len(ss.reading_word))
                # Ritme del rival (9 set 2026, abans era impossible guanyar a Normal i
                # Dificil): temps objectiu = base + segons per lletra. Llegint just a
                # aquest ritme s'empata (i guanya el nen, que arriba primer); mes rapid,
                # el rival queda enrere; mes lent, s'escapa. La base absorbeix la
                # latencia del rerun de Streamlit, que abans es menjava tot el marge.
                base, per_lletra = LECTURA_RITME[ss.diff]
                objectiu = base + per_lletra * len(ss.reading_word)
                ss.reading_pos += 10
                if elapsed < minim:
                    ss.rival_pos += 12               # clic sense llegir: el rival s'escapa
                else:
                    ss.rival_pos += min(16, max(3, 10 * elapsed / objectiu))
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
        elif ss.current_block == "Concurs":
            concurs()
        elif ss.current_block == "Golut":
            golut_component(ss.golut, f"{ss.diff}-{ss.golut_op}-{ss.golut_n}")
            st.button("🔁 UN ALTRE MONSTRE", key="golut_nou", use_container_width=True, on_click=new_problem)
            # botons invisibles que clica el joc (encert / dos errors)
            st.button("ok", key="golut_ok", on_click=golut_encert)
            st.button("ko", key="golut_ko", on_click=golut_error)
        elif ss.current_block == "Penjat":
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Toca les lletres per endevinar "
                        "la paraula abans que es completi el dibuix.</p>", unsafe_allow_html=True)
            penjat_component(ss.penjat, f"{ss.diff}-{ss.penjat_n}")
            st.button("guanya", key="penjat_guanya", on_click=penjat_guanyat)
            st.button("perd", key="penjat_perd", on_click=penjat_perdut)
            st.button("🔁 NOVA PARAULA", key="penjat_nova", use_container_width=True, on_click=new_problem)
        elif ss.current_block == "Memory":
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Toca dues cartes. "
                        "Si són iguals, es queden girades. Troba totes les parelles!</p>",
                        unsafe_allow_html=True)
            memory_component(ss.memory, f"{ss.diff}-{ss.memory_n}")
            st.button("fet", key="memory_done", on_click=memory_completat)
            st.button("🔁 NOVA PARTIDA", key="memory_nova", use_container_width=True, on_click=new_problem)
        elif ss.current_block == "Colors":
            emoji, nom = DIBUIXOS[ss.dibuix_idx]
            st.markdown("<p style='text-align:center; margin:0 0 6px 0;'>Tria un color de la paleta i "
                        "pinta amb el dit o el ratolí. Amb ✏️ GRUIX canvies la mida del pinzell.</p>",
                        unsafe_allow_html=True)
            coloreja_component(dibuix_font(emoji), nom, f"dib-{ss.dibuix_idx}")
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
        if ss.current_block not in SENSE_NIVELL and not cq_grup:
            st.markdown(f"<div class='scoreboard'><div class='chip'>⭐ {ss.punts}</div><div class='chip'>🔥 RATXA: {ss.ratxa}</div></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- OVERLAY
if st.session_state.last_status:
    status = st.session_state.last_status
    st.session_state.last_status = None
    if status == "correct":
        gif = random.choice([g for g in CELEBRATION_GIFS if g != st.session_state.last_gif] or [""])
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

# ------------------------------------------------------------ AVISOS DE MEDALLA
# Pantalla de celebracio com la de les felicitacions: ocupa tota la pantalla i marxa
# sola, SENSE recuadre ni X per tancar (28 set 2026: la X del toast era massa petita i
# molestava els nens). Nomes arriba aqui quan no hi ha GIF (aquell bloc acaba amb
# rerun), aixi que si toquen totes dues surt primer el GIF i despres la medalla.
if st.session_state.avisos:
    avisos = st.session_state.avisos
    st.session_state.avisos = []
    icones = " ".join(a[0] for a in avisos)
    textos = "".join(f"<h1>{titol}</h1><h2>{sub}</h2>" for _, titol, sub in avisos)
    st.markdown(f"<div class='gif-overlay medal-overlay'><div class='medal-icones'>{icones}</div>"
                f"{textos}</div>", unsafe_allow_html=True)
    time.sleep(2.5 if len(avisos) == 1 else 3.5)
    safe_rerun()
