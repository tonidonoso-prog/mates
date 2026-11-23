"""Concurs en solitari, en un navegador real (ordinador i mobil).

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8599 --server.headless true
    python3 tests/navegador_concurs.py [carpeta_captures]
"""
import sys
import time

from playwright.sync_api import sync_playwright

URL = "http://localhost:8599"
CAP = sys.argv[1] if len(sys.argv) > 1 else "/tmp"


def espera(page, sel, segons=25):
    t0 = time.time()
    while time.time() - t0 < segons:
        if page.locator(sel).count():
            return time.time() - t0
        time.sleep(0.2)
    raise TimeoutError(sel)


def text(page, sel):
    return page.locator(sel).first.inner_text().replace("\n", " ")


with sync_playwright() as p:
    for eng, vp, tag in (("chromium", {"width": 1280, "height": 900}, "desk"),
                         ("webkit", {"width": 390, "height": 844}, "mob")):
        errs = []
        nav = getattr(p, eng).launch()
        pg = nav.new_context(viewport=vp, has_touch=(eng == "webkit")).new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); espera(pg, ".st-key-home_Concurs button"); time.sleep(1)
        boto = pg.locator(".st-key-home_Concurs button").first
        fons = boto.evaluate("b => getComputedStyle(b).backgroundImage")
        print(eng, "portada:", boto.inner_text(), "· daurat:", "247, 183, 49" in fons or "255, 209, 92" in fons)
        pg.screenshot(path=f"{CAP}/cq_home_{tag}.png", full_page=True)
        boto.click(); espera(pg, ".st-key-cq_sol button")
        # 18 nov 2026: primer es tria jugar sol o en grup
        pg.locator(".st-key-cq_sol button").first.click(); espera(pg, ".st-key-cq_cat_natura button")
        pg.locator(".st-key-cq_cat_natura button").first.click(); espera(pg, ".st-key-cq_tema_animals button")
        assert pg.locator("input:visible").count() == 0, "no hi ha d'haver cap camp per escriure codis"
        pg.locator(".st-key-ctl_lvl_dificil button").first.click(); time.sleep(3)
        pg.screenshot(path=f"{CAP}/cq_temes_{tag}.png", full_page=True)
        pg.locator(".st-key-cq_tema_animals button").first.click(); espera(pg, ".cq-temps")
        a = int(text(pg, ".cq-temps")); time.sleep(2.2); b = int(text(pg, ".cq-temps"))
        print(eng, f"compte enrere: {a} -> {b}")
        assert b < a
        pg.screenshot(path=f"{CAP}/cq_pregunta_{tag}.png")
        # 1) respon
        pg.locator(".st-key-conc_op_0 button").first.click(); espera(pg, ".cq-feedback")
        print(eng, "P1:", text(pg, ".cq-feedback"))
        pg.screenshot(path=f"{CAP}/cq_feedback_{tag}.png")
        t = espera(pg, ".st-key-conc_op_0 button", 8)
        print(eng, f"la seguent arriba sola en {t:.1f}s")
        if tag == "mob":
            nav.close()
            continue
        # 2) no respon: s'ha d'acabar el temps sol
        t = espera(pg, ".cq-feedback", 20)
        print(eng, f"P2 sense respondre, als {t:.0f}s:", text(pg, ".cq-feedback"))
        # 3-10) respon rapid fins al final
        for _ in range(8):
            espera(pg, ".st-key-conc_op_0 button", 10)
            pg.locator(".st-key-conc_op_0 button").first.click()
            espera(pg, ".cq-feedback", 6)
        espera(pg, ".st-key-cq_altre button", 25)
        time.sleep(1)
        print(eng, "final:", text(pg, ".cq-feedback"))
        pg.screenshot(path=f"{CAP}/cq_final_{tag}.png")
        print(eng, "errors JS:", errs)
        assert not errs
        nav.close()
print("NAVEGADOR OK")
