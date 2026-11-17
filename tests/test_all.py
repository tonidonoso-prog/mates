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
for prohibit in ("INNOVAMAT", "CLASSIFICACI", "SUSHI", "KAHOOT"):
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

# privacitat: a la pantalla nomes nom + inicial, i el nom escrit no pot injectar HTML
# (17-nov-2026, ho va trobar el verificador: la portada ensenyava el cognom sencer)
pantalla = lambda: " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
at.text_input(key="nom_input").input("anna pons").run()
assert "Anna P." in pantalla() and "Pons" not in pantalla(), pantalla()[:300]
assert at.text_input(key="nom_input").placeholder == "Ex: Anna Pons"
at.text_input(key="nom_input").input("<u>hack</u> <img src=x>").run()
assert "<u>" not in pantalla() and "<img src=x" not in pantalla(), pantalla()[:300]
assert "Donoso" not in open("app.py", encoding="utf-8").read()
print("AppTest tot OK:", len(BLOCS), "blocs + calendari + privacitat del nom")
