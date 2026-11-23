"""Monstre golut: generador (sempre amb solucio) i el bloc dins l'app.

    cd mates && python3 tests/test_golut.py
"""
import itertools
import os
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest  # noqa: E402

# Aquests tests recorren la cara d'abans (la que fan servir els jocs encara no passats a la nova).
_from_file = AppTest.from_file


def _cara_antiga(*a, **k):
    t = _from_file(*a, **k)
    t.query_params["antic"] = "1"
    return t


AppTest.from_file = _cara_antiga

# --- generador
src = open("app.py", encoding="utf-8").read()
ns = {"__file__": "app.py"}
exec(src.split("def local_css():")[0], ns)
gen, val, CFG = ns["genera_golut"], ns["golut_valor"], ns["GOLUT_CFG"]
for op in ("suma", "mult"):
    for lvl in ("Fàcil", "Normal", "Difícil"):
        c, abans = CFG[op][lvl], None
        for _ in range(2000):
            g = gen(lvl, op, evita=(abans,))
            abans = g["objectiu"]
            p = g["plats"]
            assert len(p) == c["plats"] and len(set(p)) == len(p), g
            assert all(x in p for x in g["solucio"]) and val(g["solucio"], op) == g["objectiu"], g
            assert any(val(comb, op) == g["objectiu"] for comb in itertools.combinations(p, c["k"]))
print("generador OK")


def run(at):
    at.run()
    assert not at.exception, at.exception
    return at


at = run(AppTest.from_file("app.py", default_timeout=60))
at.button(key="home_Golut").click(); run(at)
g = at.session_state.golut
assert g["op"] == "suma" and g["level"] == "Fàcil"
at.button(key="ctl_lvl_dificil").click(); run(at)
assert at.session_state.golut["k"] == 3
at.button(key="ctl_gop_mult").click(); run(at)
assert at.session_state.golut["op"] == "mult"
n0, p0 = at.session_state.golut_n, at.session_state.punts
at.button(key="golut_ok").click(); run(at)
assert at.session_state.punts == p0 + 1 and at.session_state.golut_n == n0 + 1
at.button(key="golut_ko").click(); run(at)
assert at.session_state.errors == 1 and at.session_state.golut_n == n0 + 2
print("TOT OK")
