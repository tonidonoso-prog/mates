"""Concurs en grup (pantalla gran + mobils): sales, punts, top 5, podi, tornar a jugar,
que no surt cap nom, que no es desa res i que el joc en solitari segueix igual.

    cd mates && python3 tests/test_grup.py
"""
import os
import re
import sys
import time

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest  # noqa: E402

# ------------------------------------------------------ 1) les sales, sense navegador
src = open("app.py", encoding="utf-8").read()
ns = {"__file__": "app.py"}
exec(src.split("def local_css():")[0], ns)
exec(src[src.index("def _pyramid_html"):src.index("def _remember(text):")], ns)
S = ns["_sales"]()
crea, entra, respon, avanca, estat = (ns["sala_crea"], ns["sala_entra"], ns["sala_respon"],
                                      ns["sala_avanca"], ns["sala_estat"])

pin = crea("sumes", "Fàcil", 5, 20)
assert re.fullmatch(r"\d{4}", pin) and len(estat(pin)["preguntes"]) == 5
for k in range(40):
    assert entra(pin, f"{k:012x}") == "ok"
assert entra(pin, "f" * 12) == "plena"                       # 40 jugadors per sala
sa = estat(pin)
avs = [(j["emoji"], j["color"]) for j in sa["jugadors"].values()]
assert len(set(avs)) == 40 and len({e for e, _ in avs}) == 20   # cap avatar repetit; tots els animals
assert set(sa["jugadors"]["0" * 12]) == {"emoji", "color", "punts", "ratxa", "respostes", "vist", "entrat"}
# un doble clic al boto de la pantalla gran no se salta res
avanca(pin, "espera", 0); avanca(pin, "espera", 0)
assert estat(pin)["fase"] == "pregunta" and estat(pin)["idx"] == 0
q = S["sales"][pin]["preguntes"][0]
r1 = respon(pin, "0" * 12, q["correcta"])
assert 990 <= r1["punts"] <= 1000 and r1["bonus"] == 0, r1
assert respon(pin, "0" * 12, q["correcta"]) is None           # nomes una resposta per pregunta
S["sales"][pin]["t0"] -= 10                                   # a mitja pregunta: uns 750 punts
r2 = respon(pin, f"{1:012x}", q["correcta"])
assert 740 <= r2["punts"] <= 760, r2
r3 = respon(pin, f"{2:012x}", (q["correcta"] + 1) % 4)
assert r3["punts"] == 0 and not r3["encert"]
# ratxa: +100 a la segona seguida, +200 a la tercera... fins a +500
j = S["sales"][pin]["jugadors"]["0" * 12]
bonus = []
for n in range(2, 9):
    sa = S["sales"][pin]
    sa["fase"], sa["t0"], j["respostes"] = "pregunta", time.time(), {}
    bonus.append(respon(pin, "0" * 12, sa["preguntes"][sa["idx"]]["correcta"])["bonus"])
assert bonus == [100, 200, 300, 400, 500, 500, 500], bonus
# temps esgotat: 0 punts, no resta, i es perd la ratxa
punts = j["punts"]
sa = S["sales"][pin]
sa["fase"], sa["t0"], j["respostes"] = "pregunta", time.time() - 100, {}     # aquesta no la respon
assert estat(pin)["fase"] == "resultat"
assert j["punts"] == punts and j["ratxa"] == 0
# classificacio amb empat
cl = ns["sala_classificacio"](estat(pin))
assert cl[0][1] == "0" * 12 and cl[0][0] == 1
assert all(p == 3 for p, _, x in cl[2:] if x["punts"] == 0)
# 30 sales com a maxim, i les que fa 3 h que no es mouen desapareixen
pins = [crea("barreja", "Normal", 5, 20) for _ in range(40)]
assert pins.count(None) == 11 and len(S["sales"]) == 30
for p in list(S["sales"])[:5]:
    S["sales"][p]["mogut"] -= 3 * 3600 + 1
assert crea("barreja", "Normal", 5, 20) is not None and len(S["sales"]) == 26
S["sales"].clear()
# un mobil que s'ha tancat (fa mes de 8 s que no dona senyals) no fa esperar la resta
p2 = crea("sumes", "Fàcil", 5, 20)
entra(p2, "a" * 12); entra(p2, "b" * 12)
avanca(p2, "espera", 0)
S["sales"][p2]["jugadors"]["b" * 12]["vist"] -= 60
respon(p2, "a" * 12, S["sales"][p2]["preguntes"][0]["correcta"])
assert estat(p2)["fase"] == "resultat"
S["sales"].clear()
print("sales OK: 40 jugadors, 30 sales, punts per rapidesa, ratxa fins a +500, temps esgotat no resta")


# ------------------------------------------------- 2) pantalla gran + 3 mobils (AppTest)
def run(at):
    at.run()
    assert not at.exception, at.exception
    return at


def html(at):
    return " ".join(m.value for m in at.markdown)


def boto(at, key):
    return [b for b in at.button if b.key == key]


mestre = run(AppTest.from_file("app.py", default_timeout=60))
mestre.button(key="home_Concurs").click(); run(mestre)
mestre.button(key="cq_grup").click(); run(mestre)
assert "pantalla gran" in html(mestre)
# 23 nov 2026: primer la categoria; el tema surt de la llista d'aquella categoria
mestre.radio(key="cg_cat").set_value("mates"); run(mestre)
assert "sumes" in mestre.radio(key="cg_tema").options or "➕ SUMES" in mestre.radio(key="cg_tema").options
mestre.radio(key="cg_tema").set_value("sumes"); run(mestre)
mestre.session_state.cg_nivell = "Fàcil"
mestre.session_state.cg_n = 5
mestre.session_state.cg_seg = 10
mestre.button(key="cg_crea").click(); run(mestre)
pin = mestre.session_state.cg_pin
h = html(mestre)
assert re.fullmatch(r"\d{4}", pin), pin
assert "data:image/svg+xml" in h, "hi ha d'haver el QR (generat en local)"
assert f"?sala={pin}" in h and "0 A LA SALA" in h.replace("👥 ", "")
assert boto(mestre, "cg_m_start")[0].disabled                  # sense ningu no es pot comencar
assert not any(k in h for k in ("api.qrserver", "chart.googleapis", "quickchart"))
print("sala creada:", pin)

jugadors = []
for k in range(3):
    p = AppTest.from_file("app.py", default_timeout=60)
    p.query_params["sala"] = pin                                # el QR porta aqui: entra sol
    run(p)
    assert p.session_state.cg_rol == "jugador" and p.session_state.current_block == "Concurs"
    assert "JA HI ETS" in html(p), html(p)[:300]
    jugadors.append(p)
pids = [p.session_state.cg_pid for p in jugadors]
assert len(set(pids)) == 3
jos = [p.query_params.get("jo") for p in jugadors]               # (l'AppTest hi posa llistes)
assert [x[0] if isinstance(x, list) else x for x in jos] == pids, jos   # recarregar = mateix animal
run(mestre)
h = html(mestre)
avs_html = h[h.find("class='cg-avatars'"):h.find("class='cg-resum'")]
assert "3 A LA SALA" in h and avs_html.count("<span class='cg-av") == 3, avs_html
assert not boto(mestre, "cg_m_start")[0].disabled
# recarregar la pagina al mobil (adreca amb ?jo=): el mateix animal, no un de nou
re_ = AppTest.from_file("app.py", default_timeout=60)
re_.query_params["sala"] = pin
re_.query_params["jo"] = pids[0]
run(re_)
run(mestre)
assert "3 A LA SALA" in html(mestre)
print("3 jugadors dins per ?sala=, sense escriure res; recarregar no en fa un de nou")

# cap nom: cap camp per escriure (nomes l'amagat del dispositiu) ni cap nom d'animal escrit
ANIMALS_TXT = ("PANDA", "GIRAFA", "GRANOTA", "GUINEU", "TIGRE", "LLEÓ", "PINGÜÍ", "LILA", "TURQUESA")
for at in [mestre] + jugadors:
    assert [t.key for t in at.text_input] == ["dispositiu"], [t.key for t in at.text_input]
    assert not any(a in html(at) for a in ANIMALS_TXT)


def resposta(p, opcio):
    p.button(key=f"cg_op_{opcio}").click(); run(p)


mestre.button(key="cg_m_start").click(); run(mestre)
for p in jugadors:
    run(p)
    assert len(boto(p, "cg_op_0")) == 1 and "PREGUNTA 1 DE 5" in html(p)
assert "PREGUNTA 1 DE 5" in html(mestre) and "0 DE 3" in html(mestre)


def bona_de(p):
    """Calcula la resposta bona des de l'enunciat que hi ha a la pantalla gran (sumes)."""
    run(mestre)
    txt = re.search(r"class='cg-preg'>(.*?) = \?</div>", html(mestre)).group(1)
    valor = str(eval(txt))
    etiquetes = {b.key: b.label for b in p.button if b.key and b.key.startswith("cg_op_")}
    for k, lab in etiquetes.items():
        if lab.split()[-1] == valor:
            return int(k[-1])
    raise AssertionError((txt, etiquetes))


# P1: el primer encerta de seguida, el segon falla, el tercer encerta mes tard
b = bona_de(jugadors[0])
resposta(jugadors[0], b)
assert "RESPOSTA ENVIADA" in html(jugadors[0])
resposta(jugadors[1], (b + 1) % 4)
time.sleep(2)
resposta(jugadors[2], b)
run(mestre)                                     # tothom ha respost: passa sola al resultat
h = html(mestre)
assert "cg-barres" in h and "2 DE 3 L'HAN ENCERTADA" in h, h[:400]
assert "TOP 5" in h and h.count("class='cg-fila'") == 3
for p in jugadors:
    run(p)
assert "CORRECTE!" in html(jugadors[0]) and "POSICIÓ 1 DE 3" in html(jugadors[0])
assert "INCORRECTE" in html(jugadors[1]) and "POSICIÓ 3 DE 3" in html(jugadors[1])
assert "CORRECTE!" in html(jugadors[2]) and "POSICIÓ 2 DE 3" in html(jugadors[2])
punts1 = [int(re.search(r"\+(\d+) punts", html(p)).group(1)) for p in (jugadors[0], jugadors[2])]
assert punts1[0] > punts1[1] >= 850, punts1             # mes rapid, mes punts (fins a 1000)
print("P1: rapid", punts1[0], "· lent", punts1[1], "· error 0 · barres i top 5 a la pantalla gran")

# P2: el primer torna a encertar (ratxa +100), el segon no respon i es tanca amb el boto
mestre.button(key="cg_m_seg").click(); run(mestre)
for p in jugadors:
    run(p)
b = bona_de(jugadors[0])
resposta(jugadors[0], b)
resposta(jugadors[2], b)
run(mestre)
assert "2 DE 3" in html(mestre) and boto(mestre, "cg_m_tanca")      # n'espera un encara
mestre.button(key="cg_m_tanca").click(); run(mestre)
for p in jugadors:
    run(p)
assert re.search(r"2 seguides: \+100", html(jugadors[0])), html(jugadors[0])
assert "S'HA ACABAT EL TEMPS" in html(jugadors[1])
print("P2: ratxa +100 · qui no respon: 0 i no resta")

# P3: ningu respon i s'acaba el temps sol (10 s)
mestre.button(key="cg_m_seg").click(); run(mestre)
for p in jugadors:
    run(p)
abans = re.search(r"⭐ ([\d.]+)", html(jugadors[1])).group(1)
time.sleep(10.5)
run(mestre)
assert "AQUESTA COSTAVA" in html(mestre), html(mestre)[:300]
for p in jugadors:
    run(p)
assert "S'HA ACABAT EL TEMPS" in html(jugadors[1]) and f"⭐ {abans}" in html(jugadors[1])
print("P3: temps esgotat sol, sense restar")

# P4 i P5: tothom encerta
for n in (4, 5):
    mestre.button(key="cg_m_seg").click(); run(mestre)
    for p in jugadors:
        run(p)
    b = bona_de(jugadors[0])
    for p in jugadors:
        resposta(p, b)
    run(mestre)
    assert "TOTHOM L'HA ENCERTADA" in html(mestre)
assert boto(mestre, "cg_m_seg")[0].label.startswith("🏆")
mestre.button(key="cg_m_seg").click(); run(mestre)
h = html(mestre)
podi = h[h.find("class='cg-podi'"):h.find("class='cg-resum'")]
assert "FI DEL KAHOOT" in h and podi.count("<div class='cg-esgrao p") == 3, podi
festa = h[h.find("class='cg-podi-cap'"):h.find("class='cg-podi'")]
srcs = re.findall(r"src='([^']+)'", festa)
assert srcs and all(x.startswith("app/static/festa/") for x in srcs), srcs     # mai URLs de tercers
for p in jugadors:
    run(p)
assert "🥇 POSICIÓ 1 DE 3" in html(jugadors[0]) and "POSICIÓ 3 DE 3" in html(jugadors[1])
print("final: podi a la pantalla gran i posicio a cada mobil")

# res es desa: ni punts de sessio, ni medalla del dia, ni base de dades
for p in jugadors:
    ss = p.session_state
    assert (ss.punts, ss.encerts, ss.errors, ss.dies) == (0, 0, 0, []), (ss.punts, ss.encerts, ss.dies)
assert (mestre.session_state.punts, mestre.session_state.dies) == (0, [])
print("res desat: ni punts ni medalla")

# tornar a jugar: la mateixa sala i la mateixa gent, sense tornar a escanejar
mestre.button(key="cg_m_torna").click(); run(mestre)
h = html(mestre)
assert mestre.session_state.cg_pin == pin and "3 A LA SALA" in h and f"?sala={pin}" in h
for p in jugadors:
    run(p)
    assert "JA HI ETS" in html(p) and p.session_state.cg_pin == pin
mestre.button(key="cg_m_start").click(); run(mestre)
for p in jugadors:
    run(p)
    assert "PREGUNTA 1 DE 5" in html(p) and "⭐ 0" in html(p)
print("tornar a jugar: mateixa sala, punts a zero, ningu ha hagut d'escanejar")

# la pantalla gran pot anar a l'inici i tornar a la seva sala
mestre.button(key="ctl_home").click(); run(mestre)
assert mestre.session_state.current_block == "Home"
mestre.button(key="home_Concurs").click(); run(mestre)
mestre.button(key="cq_grup").click(); run(mestre)          # torna a la seva sala
assert "PREGUNTA 1 DE 5" in html(mestre)

# una sala que ja no existeix: missatge amable i prou
p = AppTest.from_file("app.py", default_timeout=60)
p.query_params["sala"] = "0001"
run(p)
assert "ja no hi és" in html(p) and not p.exception
p.button(key="cg_j_inici").click(); run(p)
assert p.session_state.current_block == "Home" and "sala" not in p.query_params
print("sala inexistent: missatge amable, i INICI la treu de l'adreca")

# alternativa al QR: el numero petit de la pantalla gran (amagat dins "No pots fer servir la camera?")
p = run(AppTest.from_file("app.py", default_timeout=60))
p.button(key="home_Concurs").click(); run(p)
p.text_input(key="cg_num").input(pin); run(p)
assert p.session_state.cg_rol == "jugador" and p.session_state.cg_pin == pin
print("alternativa: amb el numero de sala tambe s'hi entra")

# ------------------------------------------------------- 3) el solitari segueix igual
s = run(AppTest.from_file("app.py", default_timeout=60))
s.session_state.dies = [ns["avui"]().isoformat()]
s.button(key="home_Concurs").click(); run(s)
s.button(key="cq_sol").click(); run(s)
s.button(key="cq_cat_mates").click(); run(s)
assert "cq_tema_sumes" in [b.key for b in s.button] and "ctl_lvl_dificil" in [b.key for b in s.button]
s.button(key="cq_tema_sumes").click(); run(s)
g = s.session_state.cq
s.button(key=f"conc_op_{g['preguntes'][0]['correcta']}").click(); run(s)
assert "CORRECTE!" in html(s) and s.session_state.encerts == 1
print("solitari: OK")
print("TOT OK")
