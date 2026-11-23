"""Sense noms: el dispositiu es recorda amb un numero a l'atzar guardat al navegador, i la felicitacio es una
animacio servida per la propia app (cap tercer). Navegador real (ordinador i mobil).

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8599 --server.headless true
    python3 tests/navegador_privacitat.py [url] [carpeta_captures]
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599"
CAP = sys.argv[2] if len(sys.argv) > 2 else "/tmp"


def galeta(pg):
    """L'identificador del navegador (localStorage) i el que ha rebut l'app (camp amagat)."""
    for _ in range(50):
        ls = pg.evaluate("() => localStorage.getItem('am_dispositiu')")
        camp = pg.locator(".st-key-dispositiu input").first.input_value() if pg.locator(".st-key-dispositiu input").count() else ""
        if ls and ls == camp:
            return ls
        time.sleep(0.2)
    raise AssertionError(("no arriba a l'app", ls, camp))


with sync_playwright() as p:
    for eng, vp, tag in (("chromium", {"width": 1280, "height": 900}, "desk"),
                         ("webkit", {"width": 390, "height": 844}, "mob")):
        errs, terc = [], set()
        nav = getattr(p, eng).launch()
        ctx = nav.new_context(viewport=vp, has_touch=(eng == "webkit"))
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("request", lambda r: terc.add(r.url.split("/")[2]) if "giphy" in r.url else None)
        pg.goto(URL.rstrip("/") + "/?antic=1"); pg.wait_for_selector(".st-key-home_Mates button", timeout=90000); time.sleep(3)
        assert pg.locator("input[type=text]:visible").count() == 0, "cap camp per escriure el nom"
        assert "nom i cognom" not in pg.content().lower()
        g1 = galeta(pg)
        print(eng, "galeta:", g1)
        assert g1 and re.fullmatch(r"[0-9a-f]{16}", g1)
        # un exercici bo -> felicitacio amb animacio local
        pg.locator(".st-key-home_Mates button").first.click()
        pg.wait_for_selector(".problem-box", timeout=20000); time.sleep(1)
        txt = pg.locator(".problem-box").first.inner_text()
        expr = txt.split("=")[0].replace("×", "*").replace("x", "*").strip()
        pg.locator("[data-testid=stNumberInput] input").first.fill(str(eval(expr))); pg.keyboard.press("Enter")
        pg.wait_for_selector(".gif-overlay img", timeout=15000)
        img = pg.locator(".gif-overlay img").first
        for _ in range(30):
            w = img.evaluate("i => i.complete ? i.naturalWidth : 0")
            if w:
                break
            time.sleep(0.2)
        src = img.get_attribute("src")
        print(eng, txt, "->", src, "amplada", w)
        pg.screenshot(path=f"{CAP}/festa_{tag}.png")
        assert w == 512 and "static/festa/" in src
        time.sleep(6)
        # tornar a entrar (ara per la portada per defecte, la cara nova): el mateix dispositiu, sense cap camp
        pg.goto(URL.rstrip("/") + "/"); pg.wait_for_selector("iframe[title='app.aventura']", timeout=90000); time.sleep(4)
        g2 = galeta(pg)
        print(eng, "en tornar:", g2)
        assert g2 == g1, (g1, g2)
        f = pg.frame_locator("iframe[title='app.aventura']")
        assert f.locator("input").count() == 0, "la cara nova no te cap camp per escriure"
        assert "nom" not in " ".join(f.locator("label, input").all_inner_texts()).lower()
        print(eng, "giphy:", terc or "cap", "| errors JS:", errs)
        assert not terc and not errs
        pg.screenshot(path=f"{CAP}/portada_{tag}.png", full_page=True)
        nav.close()
print("NAVEGADOR OK")
