"""Concurs en solitari: generador de preguntes i una partida sencera (AppTest).

    cd mates && python3 tests/test_concurs.py
"""
import os
import re
import sys
import time

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest  # noqa: E402

# ------------------------------------------------------------------ generador
src = open("app.py", encoding="utf-8").read()
ns = {"__file__": "app.py"}
exec(src.split("def local_css():")[0], ns)
exec(src[src.index("def _pyramid_html"):src.index("def _remember(text):")], ns)
preg = ns["concurs_pregunta"]
NOMS = dict((e, n) for e, n in ns["DIBUIXOS"])
conegudes = (ns["CONCURS_PARAULES_COMUNES"] | ns["CONCURS_PARAULES_LLETGES"]
             | {x for ws in ns["PENJAT_PARAULES"].values() for x in ws})
for tema in ("sumes", "restes", "taules", "calcul", "animals", "lletra", "barreja"):
    for diff in ("Fàcil", "Normal", "Difícil"):
        for _ in range(300):
            q = preg(tema, diff)
            o, bona = q["opcions"], q["opcions"][q["correcta"]]
            assert len(o) == 4 and len(set(o)) == 4, q
            if tema in ("sumes", "restes", "taules"):
                expr = q["text"].replace(" = ?", "").replace("×", "*")
                assert int(bona) == eval(expr), q
            elif tema == "animals":
                assert NOMS[q["emoji"]] == bona, q
            elif tema == "lletra":
                paraula = re.search(r"FALTA\?\s+(.+?)\s+\(", q["text"]).group(1).replace(" ", "")
                for i, x in enumerate(o):
                    w = paraula.replace("_", x)
                    assert (w in conegudes) == (i == q["correcta"]), (q, w)
print("generador OK")


# --------------------------------------------------------------------- partida
def run(at):
    at.run()
    assert not at.exception, at.exception
    return at


def html(at):
    return " ".join(m.value for m in at.markdown)


# la medalla del dia, a part: el primer exercici del dia la dona
m = run(AppTest.from_file("app.py", default_timeout=60))
m.button(key="home_Concurs").click(); run(m)
m.button(key="cq_tema_sumes").click(); run(m)
m.button(key="conc_op_0").click(); run(m)
assert len(m.session_state.dies) == 1
print("medalla del dia: OK")

at = run(AppTest.from_file("app.py", default_timeout=60))
# AppTest torna a executar l'app sencera a cada clic, i la pantalla de la medalla (2,5 s)
# es menjaria la del resultat. Al navegador no passa: el joc es refresca tot sol i la
# medalla surt al final. Per provar el joc, la medalla d'avui ja esta guanyada.
at.session_state.dies = [ns["avui"]().isoformat()]
home = [b for b in at.button if b.key == "home_Concurs"][0]
print("boto de la portada:", home.label)
assert "NOU" in home.label            # fins al 15 de desembre de 2026
at.button(key="home_Concurs").click(); run(at)
# sense codis ni mestres: directament els temes, i amb nivells
keys = [b.key for b in at.button]
assert "cq_tema_taules" in keys and "ctl_lvl_dificil" in keys
assert not any(k and ("cq_rol" in k or "cq_entra" in k or "cq_crea" in k) for k in keys)
assert [t.key for t in at.text_input] == ["dispositiu"], "no s'ha d'haver d'escriure cap codi"
at.button(key="ctl_lvl_normal").click(); run(at)
at.button(key="cq_tema_taules").click(); run(at)
g = at.session_state.cq
assert g["nivell"] == "Normal" and g["segons"] == 20 and len(g["preguntes"]) == 10
assert "PREGUNTA 1 DE 10" in html(at)
print("partida comencada:", g["preguntes"][0]["text"])

encerts = 0
for n in range(10):
    g = at.session_state.cq
    assert g["fase"] == "pregunta", g["fase"]
    q = g["preguntes"][g["idx"]]
    if n == 3:
        # aquesta la deixem passar: s'ha d'acabar el temps sola
        g["t0"] -= 100
        at.session_state.cq = g
        run(at)
        assert "S'HA ACABAT EL TEMPS" in html(at)
    else:
        op = q["correcta"] if n % 2 == 0 else (q["correcta"] + 1) % 4
        at.button(key=f"conc_op_{op}").click(); run(at)
        h = html(at)
        if op == q["correcta"]:
            encerts += 1
            assert "CORRECTE!" in h, h[:200]
        else:
            assert "GAIREBÉ! ERA AQUESTA" in h, h[:200]
    # passada la pausa, ve la seguent (o el final)
    g = at.session_state.cq
    g["resposta"]["t"] -= 10
    at.session_state.cq = g
    run(at)

g = at.session_state.cq
assert g["fase"] == "final" and g["encerts"] == encerts == 5, (g["fase"], g["encerts"], encerts)
h = html(at)
assert f"Has encertat {encerts} de 10" in h and "primer rècord" in h, h[:300]
assert at.session_state.encerts == 5 and at.session_state.errors == 4    # el temps esgotat no resta
assert len(at.session_state.dies) == 1                                   # medalla del dia
print(f"final: {encerts} de 10, {g['punts']} punts")

# tornar a jugar: si fa mes punts, nou record; el record surt al boto del tema
record = g["punts"]
at.button(key="cq_altre").click(); run(at)
assert at.session_state.cq["fase"] == "pregunta" and at.session_state.cq["tema"] == "taules"
for n in range(10):
    g = at.session_state.cq
    at.button(key=f"conc_op_{g['preguntes'][g['idx']]['correcta']}").click(); run(at)
    g = at.session_state.cq
    g["resposta"]["t"] -= 10
    at.session_state.cq = g
    run(at)
assert "NOU RÈCORD" in html(at) and at.session_state.cq["punts"] > record
at.button(key="cq_tema_nou").click(); run(at)
boto = [b for b in at.button if b.key == "cq_tema_taules"][0]
assert "🏆" in boto.label, boto.label
print("record:", boto.label)

# sortir a mitja partida i canviar de nivell tornen a la tria de tema
at.button(key="cq_tema_sumes").click(); run(at)
at.button(key="cq_surt").click(); run(at)
assert at.session_state.cq is None
at.button(key="cq_tema_animals").click(); run(at)
at.button(key="ctl_lvl_dificil").click(); run(at)
assert at.session_state.cq is None
print("TOT OK")
