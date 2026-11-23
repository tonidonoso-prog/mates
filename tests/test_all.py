"""Recorre tots els blocs i nivells de l'app i comprova que cap peta.

    cd mates && python3 tests/test_all.py
"""
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest  # noqa: E402


def run(at):
    at.run()
    assert not at.exception, at.exception
    return at


at = run(AppTest.from_file("app.py", default_timeout=60))
keys = [b.key for b in at.button]
BLOCS = ("Mates", "Calcul", "Lectura", "Lletres", "Sopa", "Memory", "Penjat", "Colors",
         "Golut", "Concurs", "Repte")
SENSE_NIVELL = ("Lletres", "Colors")
for blk in BLOCS:
    assert f"home_{blk}" in keys, (blk, keys)
assert "home_cal" in keys and "home_rank" not in keys
labels = " ".join(b.label for b in at.button).upper()
# KAHOOT ja no hi es: el 23 nov 2026 el Toni va decidir dir-li Kahoot (app nomes per a la gent de l'escola)
for prohibit in ("INNOVAMAT", "CLASSIFICACI", "SUSHI"):
    assert prohibit not in labels, prohibit
for blk in BLOCS:
    at.button(key=f"home_{blk}").click()
    run(at)
    assert at.session_state.current_block == blk
    if blk not in SENSE_NIVELL:
        for lvl in ("normal", "dificil", "facil"):
            at.button(key=f"ctl_lvl_{lvl}").click()
            run(at)
    at.button(key="ctl_home").click()
    run(at)
at.button(key="home_cal").click()
run(at)
assert at.session_state.current_block == "Calendari"
at.button(key="cal_home").click()
run(at)

# privacitat (17-nov-2026, decisio del Toni): enlloc es demana el nom. Qui juga es un numero a
# l'atzar del dispositiu, i el que va al servidor nomes en porta aquest numero.
# l'unic camp es l'amagat on el JS escriu l'identificador del navegador
assert [t.key for t in at.text_input] == ["dispositiu"], [t.key for t in at.text_input]
pantalla = " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
assert "nom i cognom" not in pantalla.lower() and "escriu el teu nom" not in pantalla.lower()
at.text_input(key="dispositiu").input("no es valid").run()
assert at.session_state.jugador == ""
at.text_input(key="dispositiu").input("0123456789abcdef").run()
assert at.session_state.jugador == "0123456789abcdef"
assert "Donoso" not in open("app.py", encoding="utf-8").read()
gifs = [f for f in os.listdir("static/festa") if f.endswith(".webp")]
assert len(gifs) >= 40, len(gifs)
print("AppTest tot OK:", len(BLOCS), "blocs + calendari + sense noms + %d animacions" % len(gifs) + "")
