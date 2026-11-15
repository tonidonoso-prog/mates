"""Partida real al navegador: mestre (ordinador) + dos nens (mobil).

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8599 --server.headless true
    python3 tests/navegador_concurs.py [carpeta_captures]
"""
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = "http://localhost:8599"
CAP = sys.argv[1] if len(sys.argv) > 1 else "/tmp"


def espera(page, sel, segons=20):
    t0 = time.time()
    while time.time() - t0 < segons:
        if page.locator(sel).count():
            return True
        time.sleep(0.2)
    raise TimeoutError(sel)


def text(page, sel):
    return page.locator(sel).first.inner_text().replace("\n", " ")


with sync_playwright() as p:
    errs = []
    nav_m = p.chromium.launch()
    m = nav_m.new_context(viewport={"width": 1280, "height": 900}).new_page()
    m.on("pageerror", lambda e: errs.append("mestre: " + str(e)))
    m.goto(URL); espera(m, ".st-key-home_Concurs button"); time.sleep(1)
    m.locator(".st-key-home_Concurs button").first.click(); espera(m, ".st-key-cq_rol_m button")
    m.locator(".st-key-cq_rol_m button").first.click(); espera(m, ".st-key-cq_crea button")
    # tema animals, 5 preguntes, 10 segons
    m.locator("[data-testid='stSelectbox']").first.click(); time.sleep(0.5)
    m.get_by_role("option", name="🐾 ANIMALS").click(); time.sleep(1)
    for s in m.get_by_role("slider").all():
        s.focus()
        for _ in range(6):
            s.press("ArrowLeft"); time.sleep(0.25)
        time.sleep(0.6)
    valors = [s.get_attribute("aria-valuetext") or s.get_attribute("aria-valuenow") for s in m.get_by_role("slider").all()]
    print("preguntes i segons:", valors)
    m.locator(".st-key-cq_crea button").first.click(); espera(m, ".cq-pin")
    pin = text(m, ".cq-pin").strip()
    print("codi:", pin)

    nens = []
    for k, eng in enumerate(("webkit", "chromium")):
        nav = getattr(p, eng).launch()
        j = nav.new_context(viewport={"width": 390, "height": 844}, has_touch=(eng == "webkit")).new_page()
        j.on("pageerror", lambda e, k=k: errs.append(f"nen{k}: " + str(e)))
        j.goto(URL); espera(j, ".st-key-home_Concurs button"); time.sleep(1)
        j.locator(".st-key-home_Concurs button").first.click(); espera(j, ".st-key-cq_rol_j button")
        j.locator(".st-key-cq_rol_j button").first.click(); espera(j, ".st-key-cq_entra button")
        j.locator("input[aria-label*='Codi']").first.fill(pin); j.keyboard.press("Enter")
        espera(j, ".cq-jo")      # amb Intro ja entra, sense haver de premer ENTRAR
        print(f"nen {k} ({eng}):", text(j, ".cq-jo"))
        nens.append((nav, j))
    t0 = time.time()
    while "2 jugadors" not in text(m, "body") and time.time() - t0 < 10:
        time.sleep(0.3)
    print("mestre veu:", re.search(r"\d+ jugadors? connectats?", text(m, "body")).group(0))
    m.screenshot(path=f"{CAP}/cq_lobby.png")

    m.locator(".st-key-cq_m_start button").first.click(); espera(m, ".cq-temps")
    a = int(text(m, ".cq-temps")); time.sleep(2.2); b = int(text(m, ".cq-temps"))
    print(f"compte enrere sol: {a} -> {b}")
    assert b < a
    m.screenshot(path=f"{CAP}/cq_pregunta_mestre.png")

    # pregunta 1: tots dos responen -> es tanca de seguida
    for k, (_, j) in enumerate(nens):
        espera(j, ".st-key-conc_op_0 button")
        if k == 0:
            j.screenshot(path=f"{CAP}/cq_pregunta_nen.png")
        j.locator(f".st-key-conc_op_{k} button").first.click(); time.sleep(0.5)
    espera(m, ".cq-op.bona", 6)
    print("P1 (tots responen):", text(m, ".cq-gran"))
    time.sleep(1.5)
    for k, (_, j) in enumerate(nens):
        print(f"   nen {k}:", text(j, ".cq-feedback"))
    nens[0][1].screenshot(path=f"{CAP}/cq_feedback_nen.png")
    m.screenshot(path=f"{CAP}/cq_resultat_mestre.png")

    # pregunta 2: nomes respon el nen 0 -> s'ha de tancar sola en acabar el temps
    m.locator(".st-key-cq_m_seg button").first.click(); espera(m, ".cq-temps")
    espera(nens[0][1], ".st-key-conc_op_0 button")
    nens[0][1].locator(".st-key-conc_op_2 button").first.click()
    t0 = time.time()
    espera(m, ".cq-op.bona", 15)
    print(f"P2 (un no respon): tancada sola als {time.time() - t0:.0f}s ·", text(m, ".cq-gran"))
    time.sleep(1.5)
    print("   nen 1 (no ha respost):", text(nens[1][1], ".cq-feedback"))

    # preguntes 3 a 5 amb el boto de tancar del mestre
    for q in range(3, 6):
        m.locator(".st-key-cq_m_seg button").first.click(); espera(m, ".st-key-cq_m_tanca button")
        time.sleep(1)
        m.locator(".st-key-cq_m_tanca button").first.click(); espera(m, ".cq-op.bona")
    m.locator(".st-key-cq_m_seg button").first.click(); espera(m, ".st-key-cq_m_nova button")
    time.sleep(1)
    print("final mestre:", text(m, ".cq-gran"), "·", text(m, ".cq-info"))
    m.screenshot(path=f"{CAP}/cq_final_mestre.png")
    time.sleep(1.5)
    for k, (_, j) in enumerate(nens):
        print(f"   final nen {k}:", text(j, ".cq-feedback"))
    nens[1][1].screenshot(path=f"{CAP}/cq_final_nen.png")
    print("errors JS:", errs)
    assert not errs
    for nav, _ in nens:
        nav.close()
    nav_m.close()
print("NAVEGADOR OK")
