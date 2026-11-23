"""Scroll AMB EL DIT a la cara nova (el que falla al mobil si Streamlit posa scrolling="no" a l'iframe).
Chromium amb emulacio de mobil (Android i iPhone) i gest tactil real (CDP). Entra per la pagina de fora si
l'adreca no porta /~/+/.

    python3 tests/navegador_scroll.py [url]
"""
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599/"
SEL = "iframe[title='app.aventura']"


def obre(p, disp):
    ctx = p.chromium.launch().new_context(**p.devices[disp])
    pg = ctx.new_page(); pg.goto(URL)
    if "streamlit.app" in URL and "/~/+/" not in URL:
        fora = pg.wait_for_selector("iframe[src*='/~/+/']", timeout=120000).content_frame()
        el = fora.wait_for_selector(SEL, timeout=120000)
    else:
        el = pg.wait_for_selector(SEL, timeout=120000)
    time.sleep(6)
    return ctx, pg, el.content_frame()


with sync_playwright() as p:
    for disp in ("Pixel 7", "iPhone 13"):
        ctx, pg, f = obre(p, disp)
        cdp = ctx.new_cdp_session(pg); vp = pg.viewport_size

        def dit(dy):
            cdp.send("Input.synthesizeScrollGesture", {"x": vp["width"] // 2, "y": int(vp["height"] * (0.8 if dy < 0 else 0.3)),
                                                         "yDistance": dy, "gestureSourceType": "touch", "speed": 1000})
            time.sleep(1.2)

        def prova(nom):
            alt, vist = f.evaluate("() => { const r = document.getElementById('rodet'); return [r.scrollHeight, r.clientHeight]; }")
            dit(-500)
            baixat = f.evaluate("() => document.getElementById('rodet').scrollTop")
            print(disp, nom, "contingut", alt, "pantalla", vist, "-> baixa", baixat)
            if alt > vist + 120:
                assert baixat > 100, (disp, nom, baixat)
            dit(900)
            assert f.evaluate("() => document.getElementById('rodet').scrollTop") < 5

        prova("portada")
        # un joc obert amb la portada baixada ha de començar a dalt
        dit(-500)
        f.locator("button[data-arg='Calcul']").evaluate("b => b.click()"); f.locator(".teclat").wait_for(timeout=15000); time.sleep(1)
        assert f.evaluate("() => document.getElementById('rodet').scrollTop") < 5, "Càlcul no comença a dalt"
        f.locator("button[data-fa='mates_inici']").click(); time.sleep(2)
        dit(-500)
        f.locator("button[data-arg='Recta']").evaluate("b => b.click()"); f.locator(".recta-svg").wait_for(timeout=15000); time.sleep(1)
        assert f.evaluate("() => document.getElementById('rodet').scrollTop") < 5, "Recta no comença a dalt"
        f.locator("button[data-fa='recta_inici']").click(); time.sleep(2)
        f.locator("button[data-arg='Concurs']").click(); time.sleep(2.5); prova("kahoot")
        f.locator("button.nav.inici").first.click(); time.sleep(2)
        f.locator("button[data-arg='Recta']").click(); f.locator(".recta-svg").wait_for(timeout=15000); time.sleep(1); prova("recta")
        f.locator("button[data-fa='recta_inici']").click(); time.sleep(2)
        f.locator("button[data-arg='Mates']").click(); f.locator(".teclat").wait_for(timeout=15000); time.sleep(1); prova("mates")
        ctx.browser.close()
print("NAVEGADOR SCROLL OK")
