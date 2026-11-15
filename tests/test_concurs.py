"""Concurs: partida sencera amb una pantalla de mestre i dues tauletes (AppTest).

    cd mates && python3 tests/test_concurs.py
"""
import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest  # noqa: E402


def run(at):
    at.run()
    assert not at.exception, at.exception
    return at


def html(at):
    return " ".join(m.value for m in at.markdown)


def nou():
    at = run(AppTest.from_file("app.py", default_timeout=60))
    at.button(key="home_Concurs").click(); run(at)
    return at


# --- mestre: crea la partida
m = nou()
assert "home_Concurs" not in [b.key for b in m.button]
m.button(key="cq_rol_m").click(); run(m)
m.selectbox(key="cq_tema").set_value("✖️ TAULES"); run(m)
m.radio(key="cq_nivell").set_value("Normal"); run(m)
m.select_slider(key="cq_n").set_value(5); run(m)
m.button(key="cq_crea").click(); run(m)
pin = m.session_state.conc_pin
assert re.fullmatch(r"\d{4}", pin), pin
assert pin in html(m) and "0 jugadors connectats" in html(m)
assert [b for b in m.button if b.key == "cq_m_start"][0].disabled, "sense jugadors no es pot comencar"
print("mestre: partida creada amb el codi", pin)

# --- dos nens hi entren
nens = []
for _ in range(2):
    j = nou()
    j.button(key="cq_rol_j").click(); run(j)
    j.text_input(key="cq_codi").set_value(pin); run(j)    # amb Intro ja entra, sense el boto
    assert j.session_state.conc_pin == pin
    assert "cq_entra" not in [b.key for b in j.button]
    assert "JA HI ETS" in html(j)
    nens.append(j)
avatars = [re.search(r"cq-jo'>(.+?) ·", html(j)).group(1) for j in nens]
assert avatars[0] != avatars[1], avatars
print("dos nens dins:", avatars)

# un codi dolent
x = nou()
x.button(key="cq_rol_j").click(); run(x)
x.text_input(key="cq_codi").set_value("0000"); run(x)
x.button(key="cq_entra").click(); run(x)
# el text d'exemple no ha de semblar un codi
assert not any(ch.isdigit() for ch in x.text_input(key="cq_codi").placeholder)
assert x.session_state.conc_pin == "" and any("cap partida amb el codi 0000" in e.value for e in x.error)
print("codi dolent: rebutjat")

run(m)
assert "2 jugadors connectats" in html(m) and all(a in html(m) for a in avatars)
m.button(key="cq_m_start").click(); run(m)
assert "PREGUNTA 1 DE 5" in html(m)

encerts = [0, 0]
for n_preg in range(5):
    for j in nens:
        run(j)
    # el primer nen tria la A, el segon la D
    triat = []
    for k, j in enumerate(nens):
        op = 0 if k == 0 else 3
        triat.append([b.label for b in j.button if b.key == f"conc_op_{op}"][0])
        j.button(key=f"conc_op_{op}").click(); run(j)
    run(m)        # tothom ha respost: s'ha de tancar sola
    h = html(m)
    assert "L'HAN ENCERTADA" in h or "AQUESTA COSTAVA" in h, h[:300]
    for k, j in enumerate(nens):
        run(j)
        hj = html(j)
        if "CORRECTE!" in hj:
            encerts[k] += 1
        else:
            assert "ERA AQUESTA" in hj, hj[:300]
        # cap nen veu els punts d'un altre
        altre = avatars[1 - k]
        assert altre not in hj, (altre, hj[:200])
    if n_preg < 4:
        m.button(key="cq_m_seg").click(); run(m)
        assert f"PREGUNTA {n_preg + 2} DE 5" in html(m)
print("5 preguntes jugades · encerts:", encerts)

m.button(key="cq_m_seg").click(); run(m)
hm = html(m)
assert "FI DEL CONCURS" in hm and "ENTRE TOTS" in hm, hm[:300]
# a la pantalla gran no hi ha cap nen amb els seus punts (sense podi)
assert not any(a in hm for a in avatars), "la pantalla gran no ha d'ensenyar noms al final"
for k, j in enumerate(nens):
    run(j)
    hj = html(j)
    assert f"Has encertat {encerts[k]} de 5" in hj, hj[:300]
    assert j.session_state.encerts == encerts[k] and j.session_state.errors == 5 - encerts[k]
    assert len(j.session_state.dies) == 1      # medalla del dia
print("final: la pantalla gran nomes dona el total de la classe; cada nen veu el seu")

# entrar a una partida acabada
y = nou()
y.button(key="cq_rol_j").click(); run(y)
y.text_input(key="cq_codi").set_value(pin); run(y)
assert any("acabat" in e.value for e in y.error)
print("partida acabada: no s'hi pot entrar")
print("TOT OK")
