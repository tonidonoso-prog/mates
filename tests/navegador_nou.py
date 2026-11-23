"""Cara nova (?nou=1): ordre dels jocs, Càlcul mental amb piràmide i un Repte sencer fins a l'informe.

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8599 --server.headless true
    python3 tests/navegador_nou.py [url] [carpeta_captures]
"""
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599/?nou=1"
CAP = sys.argv[2] if len(sys.argv) > 2 else "/tmp"


def piramide(f):
    base = [int(x) for x in f.locator(".piramide .pyr-row").last.inner_text().split()]
    while len(base) > 1:
        base = [base[i] + base[i + 1] for i in range(len(base) - 1)]
    return base[0]


with sync_playwright() as p:
    b = p.webkit.launch()
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); time.sleep(8)
    f = pg.frame_locator("iframe[title='app.aventura']")
    noms = f.locator(".gominola .nom").all_inner_texts()
    print("ordre:", noms[:4])
    assert noms[0] == "KAHOOT", noms
    # CÀLCUL MENTAL: piràmide i amics
    f.locator("button[data-arg='Calcul']").click(); f.locator(".mates-pregunta").wait_for(timeout=15000); time.sleep(1)
    f.locator("button[data-fa='op'][data-arg='Piràmide']").click(); f.locator(".piramide").wait_for(timeout=15000)
    pg.screenshot(path=f"{CAP}/calcul_pir_mob.png")
    for d in str(piramide(f)):
        f.locator(f".tecla[data-arg='{d}']").click()
    f.locator(".tecla.ok").click(); time.sleep(0.5)
    print("piràmide:", f.locator("#avis").inner_text())
    assert "Torna-ho" not in f.locator("#avis").inner_text()
    f.locator("button[data-fa='op'][data-arg='Amics']").click(); time.sleep(3)
    print("amics:", f.locator(".operacio").inner_text().replace("\n", " "))
    f.locator("button[data-fa='mates_inici']").click(); time.sleep(1.5)
    # REPTE sencer, sempre malament (2 intents), fins a l'informe
    f.locator("button[data-arg='Repte']").click(); f.locator(".mates-pregunta").wait_for(timeout=15000); time.sleep(1.5)
    for k in range(10):
        for _ in range(2):
            f.locator(".tecla[data-arg='0']").click(); f.locator(".tecla.ok").click(); time.sleep(0.4)
        time.sleep(2.2)
    f.locator(".final").wait_for(timeout=10000); time.sleep(1.2)
    pg.screenshot(path=f"{CAP}/repte_informe_mob.png")
    inf = f.locator(".final").inner_text().replace("\n", " | ")
    print("informe:", inf[:200])
    assert "de 10" in inf and "A repassar" in inf
    f.locator("button[data-fa='inici']").click(); time.sleep(2)
    print("errors JS:", errs)
    assert not errs
    b.close()
print("NAVEGADOR NOU OK")
