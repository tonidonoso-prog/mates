"""Portada per defecte (sense parametres) = cara nova. Un joc encara no passat (Penjat) s'obre amb
la cara d'abans i el boto 🏠 torna a la cara nova. ?antic=1 deixa la d'abans i el seu boto torna a la nova.

    python3 tests/navegador_portada.py [url] [carpeta_captures]
"""
import sys
import time

from playwright.sync_api import sync_playwright

URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8599").rstrip("/")
CAP = sys.argv[2] if len(sys.argv) > 2 else "/tmp"
IFR = "iframe[title='app.aventura']"

with sync_playwright() as p:
    for motor, mida in (("webkit", (390, 844)), ("chromium", (1280, 860))):
        b = getattr(p, motor).launch()
        pg = b.new_page(viewport={"width": mida[0], "height": mida[1]})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL + "/"); pg.wait_for_selector(IFR, timeout=90000); time.sleep(6)
        f = pg.frame_locator(IFR)
        noms = f.locator(".gominola .nom").all_inner_texts()
        assert noms and noms[0] == "KAHOOT", noms
        pg.screenshot(path=f"{CAP}/portada_{motor}.png")
        # joc encara a la cara d'abans
        f.locator("button[data-arg='Penjat']").click()
        pg.wait_for_selector(".st-key-ctl_home button", timeout=60000); time.sleep(2)
        assert pg.locator(IFR).count() == 0
        pg.screenshot(path=f"{CAP}/penjat_{motor}.png")
        pg.locator(".st-key-ctl_home button").click()
        pg.wait_for_selector(IFR, timeout=60000); time.sleep(5)
        assert pg.frame_locator(IFR).locator(".gominola .nom").first.inner_text() == "KAHOOT"
        # sortida d'emergencia
        pg.goto(URL + "/?antic=1"); pg.wait_for_selector(".st-key-home_Concurs button", timeout=90000); time.sleep(2)
        assert pg.locator(IFR).count() == 0
        pg.locator(".st-key-torna_cara_nova button").click()
        pg.wait_for_selector(IFR, timeout=60000); time.sleep(3)
        print(motor, "ordre:", noms[:4], "| errors JS:", errs)
        assert not errs
        b.close()
print("NAVEGADOR PORTADA OK")
