"""Recta numèrica (cara nova, ?nou=1): una suma i una resta resoltes salt a salt, amb un error.

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8599 --server.headless true
    python3 tests/navegador_recta.py [url] [carpeta_captures]
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599/?nou=1"
CAP = sys.argv[2] if len(sys.argv) > 2 else "/tmp"


def llegeix(f):
    m = re.match(r"(\d+)\s*([+−])\s*(\d+)", f.locator(".operacio").inner_text())
    a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
    salts = [int(x[1:]) for x in f.locator(".recta-svg .salt").all_text_contents()]
    assert sum(salts) == b, (salts, b)                       # els salts sumen el segon número
    assert all(x == 10 for x in salts[:-1]) and 0 < salts[-1] < 10, salts   # de 10 en 10 i al final les unitats
    pts = [a]
    for s in salts:
        pts.append(pts[-1] + (s if op == "+" else -s))
    return a, op, b, salts, pts


def escriu(f, n):
    for d in str(n):
        f.locator(f".tecla[data-arg='{d}']").click()
    f.locator(".tecla.ok").click(); time.sleep(0.35)


with sync_playwright() as p:
    for eng, vp, tag in (("webkit", (390, 844), "mob"), ("chromium", (1208, 830), "desk")):
        b = getattr(p, eng).launch()
        pg = b.new_page(viewport={"width": vp[0], "height": vp[1]})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); time.sleep(8)
        f = pg.frame_locator("iframe[title='app.aventura']")
        assert f.locator("button.nou[data-arg='Recta']").count() == 1
        f.locator("button[data-arg='Recta']").click(); f.locator(".recta-svg").wait_for(timeout=10000); time.sleep(0.6)
        a, op, b_, salts, pts = llegeix(f)
        print(tag, "suma:", a, op, b_, "salts", salts, "parades", pts)
        pg.screenshot(path=f"{CAP}/recta_{tag}.png")
        c = f.locator(".consigna").inner_text()
        assert c.startswith(f"Salt 1 de {len(salts)}:") and f"fes +{salts[0]}" in c, c
        escriu(f, pts[1] + 1)                                 # un error a la primera parada
        assert "Torna-ho" in f.locator("#avis").inner_text()
        for x in pts[1:]:
            escriu(f, x)
        print(tag, "avís:", f.locator("#avis").inner_text())
        pg.screenshot(path=f"{CAP}/recta_fet_{tag}.png")
        time.sleep(2.6)
        f.locator("button[data-fa='recta_op'][data-arg='resta']").click(); time.sleep(0.8)
        a, op, b_, salts, pts = llegeix(f)
        assert op == "−" and pts[-1] == a - b_
        print(tag, "resta:", a, op, b_, "salts", salts, "parades", pts)
        for x in pts[1:]:
            escriu(f, x)
        print(tag, "avís:", f.locator("#avis").inner_text(), "| punts:", f.locator(".xip").first.inner_text())
        pg.screenshot(path=f"{CAP}/recta_resta_{tag}.png")
        # Difícil: 3 xifres, tot de 10 en 10; les caselles no es trepitgen
        time.sleep(2.6)
        f.locator("button[data-fa='recta_op'][data-arg='suma']").click(); time.sleep(0.6)
        f.locator("button[data-fa='nivell'][data-arg='Difícil']").click(); time.sleep(1.5)
        a, op, b_, salts, pts = llegeix(f)
        print(tag, "difícil:", a, op, b_, "parades", pts)
        assert a >= 100 and len(salts) <= 5
        caixes = f.locator(".recta-svg .caixa rect").evaluate_all("rs => rs.map(r => { const b = r.getBoundingClientRect(); return [b.left, b.right]; })")
        caixes.sort()
        assert all(caixes[i][1] <= caixes[i + 1][0] + 0.5 for i in range(len(caixes) - 1)), caixes
        for x in pts[1:-1]:
            escriu(f, x)
        assert "Aquesta casella és el resultat" in f.locator(".consigna").inner_text()
        pg.screenshot(path=f"{CAP}/recta_dificil_{tag}.png")
        # es pot baixar fins al teclat en una pantalla baixa
        pg.set_viewport_size({"width": vp[0], "height": 600}); time.sleep(1)
        fr = pg.locator("iframe[title='app.aventura']").element_handle().content_frame()
        pg.mouse.move(vp[0] / 2, 300); pg.mouse.wheel(0, 800); time.sleep(1)
        baixat = fr.evaluate("() => scrollY")
        print(tag, "scroll:", baixat)
        assert baixat > 100, baixat
        print(tag, "errors JS:", errs)
        assert not errs
        b.close()
print("NAVEGADOR RECTA OK")
