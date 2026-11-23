"""Concurs en grup en navegadors reals: la pantalla gran (ordinador, 1280) i tres mobils (390) que
entren per l'adreca del QR (?sala=<PIN>), responen, veuen el resultat, el podi i tornen a jugar.

Cal tenir l'app engegada:  python3 -m streamlit run app.py --server.port 8502 --server.headless true
    python3 tests/navegador_grup.py [url] [carpeta_captures]
"""
import re
import sys
import time

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8502"
CAP = sys.argv[2] if len(sys.argv) > 2 else "/tmp"
HOST = URL.split("://", 1)[1].split("/")[0]


def espera(page, sel, segons=25, text=None):
    t0 = time.time()
    while time.time() - t0 < segons:
        loc = page.locator(sel)
        if loc.count() and (text is None or text in loc.first.inner_text()):
            return time.time() - t0
        time.sleep(0.2)
    raise TimeoutError(f"{sel} {text or ''}")


def txt(page, sel):
    return page.locator(sel).first.inner_text().replace("\n", " ")


def sense_scroll_lateral(page):
    return page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")


def bona(mestre, jugador):
    """Index del boto bo al mobil, calculat de l'enunciat de la pantalla gran (sumes)."""
    expr = txt(mestre, ".cg-preg").replace("= ?", "").strip()
    valor = str(eval(expr))
    for i in range(4):
        if jugador.locator(f".st-key-cg_op_{i} button").first.inner_text().split()[-1] == valor:
            return i
    raise AssertionError(expr)


with sync_playwright() as p:
    errs, tercers = [], set()

    def vigila(pg, nom):
        pg.on("pageerror", lambda e: errs.append(f"{nom}: {e}"))
        pg.on("request", lambda r: tercers.add(r.url.split("/")[2])
              if r.url.startswith("http") and HOST not in r.url
              and not re.search(r"fonts\.(googleapis|gstatic)\.com", r.url) else None)

    chrome, webkit = p.chromium.launch(), p.webkit.launch()
    mestre = chrome.new_context(viewport={"width": 1280, "height": 900}).new_page()
    vigila(mestre, "pantalla gran")
    mestre.goto(URL); espera(mestre, ".st-key-home_Concurs button", 90); time.sleep(1)
    mestre.locator(".st-key-home_Concurs button").first.click(); espera(mestre, ".st-key-cq_grup button")
    mestre.screenshot(path=f"{CAP}/grup_0_triar_desk.png")
    mestre.locator(".st-key-cq_grup button").first.click(); espera(mestre, ".st-key-cg_crea button")
    mestre.locator(".st-key-cg_cat label").filter(has_text="MATES").first.click(); time.sleep(0.8)
    mestre.locator(".st-key-cg_tema label").filter(has_text="SUMES").first.click(); time.sleep(0.6)
    mestre.locator(".st-key-cg_n label").filter(has_text=re.compile(r"^5$")).first.click(); time.sleep(0.6)
    mestre.locator(".st-key-cg_seg label").filter(has_text=re.compile(r"^20$")).first.click(); time.sleep(0.6)
    mestre.screenshot(path=f"{CAP}/grup_1_config_desk.png", full_page=True)
    mestre.locator(".st-key-cg_crea button").first.click(); espera(mestre, "img.cg-qr", 15)
    qr = mestre.locator("img.cg-qr").first
    for _ in range(30):
        if qr.evaluate("i => i.complete && i.naturalWidth > 0"):
            break
        time.sleep(0.2)
    caixa = qr.bounding_box()
    sala = mestre.locator(".cg-url").first
    url_sala, pin = sala.get_attribute("data-url"), sala.get_attribute("data-pin")
    print("sala:", pin, url_sala, "| QR:", round(caixa["width"]), "px")
    assert url_sala == f"{URL}/?sala={pin}" and caixa["width"] >= 250
    assert qr.get_attribute("src").startswith("data:image/svg+xml")

    # tres mobils entren per l'adreca del QR, sense escriure res
    jugadors = []
    for k, (nav, eng) in enumerate(((webkit, "webkit"), (chrome, "chromium"), (webkit, "webkit"))):
        pg = nav.new_context(viewport={"width": 390, "height": 844}, has_touch=True,
                             is_mobile=(eng == "chromium")).new_page()
        vigila(pg, f"mobil {k + 1}")
        pg.goto(url_sala); espera(pg, ".cq-feedback", 90, "JA HI ETS")
        assert pg.locator("input[type=text]:visible").count() == 0, "no s'ha d'escriure res"
        assert sense_scroll_lateral(pg)
        jugadors.append(pg)
    time.sleep(1)
    jugadors[0].screenshot(path=f"{CAP}/grup_2_espera_mob.png")
    espera(mestre, ".cg-titol", 10, "3 A LA SALA"); time.sleep(1.2)
    assert mestre.locator(".cg-avatars .cg-av").count() == 3
    mestre.screenshot(path=f"{CAP}/grup_3_qr_avatars_desk.png")
    print("3 a la sala:", txt(mestre, ".cg-avatars"))
    # recarregar el mobil: torna a ser el mateix animal
    av0 = jugadors[0].locator(".cg-av").first.inner_text()
    print("adreca del mobil:", jugadors[0].url)
    assert "jo=" in jugadors[0].url
    jugadors[0].reload(); espera(jugadors[0], ".cq-feedback", 60, "JA HI ETS"); time.sleep(1.5)
    assert jugadors[0].locator(".cg-av").first.inner_text() == av0
    assert mestre.locator(".cg-avatars .cg-av").count() == 3

    mestre.locator(".st-key-cg_m_start button").first.click(); espera(mestre, ".cg-preg", 10)
    for pg in jugadors:
        espera(pg, ".st-key-cg_op_3 button", 10)
    a = int(txt(mestre, ".cq-temps")); time.sleep(2.2); b = int(txt(mestre, ".cq-temps"))
    print(f"compte enrere a la pantalla gran: {a} -> {b}")
    assert b < a
    mestre.screenshot(path=f"{CAP}/grup_4_pregunta_desk.png")
    jugadors[0].screenshot(path=f"{CAP}/grup_5_botons_mob.png")
    alt = jugadors[0].locator(".st-key-cg_op_0 button").first.bounding_box()
    ample = jugadors[0].locator(".st-key-cg_op_1 button").first.bounding_box()
    print("boto al mobil:", round(alt["width"]), "x", round(alt["height"]), "| 2 per fila:", ample["y"] == alt["y"])
    assert alt["height"] >= 120 and ample["y"] == alt["y"]
    assert all(sense_scroll_lateral(pg) for pg in jugadors)

    # P1: el 1r encerta, el 2n falla, el 3r encerta mes tard
    i = bona(mestre, jugadors[0])
    jugadors[0].locator(f".st-key-cg_op_{i} button").first.click()
    jugadors[1].locator(f".st-key-cg_op_{(i + 1) % 4} button").first.click()
    espera(mestre, ".cg-rebudes", 5, "2 DE 3")
    time.sleep(1.5)
    jugadors[2].locator(f".st-key-cg_op_{i} button").first.click()
    t = espera(mestre, ".cg-barres", 6)
    print(f"tothom ha respost: resultat a la pantalla gran en {t:.1f}s")
    time.sleep(1)
    mestre.screenshot(path=f"{CAP}/grup_6_resultat_desk.png")
    assert mestre.locator(".cg-fila").count() == 3 and "2 DE 3" in txt(mestre, ".cg-frase")
    for k, pg in enumerate(jugadors):
        espera(pg, ".cg-titol", 6, "POSICIÓ")
        print(f"mobil {k + 1}:", txt(pg, ".cq-feedback"), "|", txt(pg, ".cg-titol"))
    assert "CORRECTE" in txt(jugadors[0], ".cq-feedback") and "INCORRECTE" in txt(jugadors[1], ".cq-feedback")
    jugadors[0].screenshot(path=f"{CAP}/grup_7_correcte_mob.png")
    jugadors[1].screenshot(path=f"{CAP}/grup_7_incorrecte_mob.png")

    # P2..P5: tothom encerta
    for n in range(2, 6):
        mestre.locator(".st-key-cg_m_seg button").first.click()
        espera(mestre, ".cg-cap", 8, f"PREGUNTA {n} DE 5")
        for pg in jugadors:
            espera(pg, ".st-key-cg_op_3 button", 8)
        i = bona(mestre, jugadors[0])
        for pg in jugadors:
            pg.locator(f".st-key-cg_op_{i} button").first.click()
        espera(mestre, ".cg-barres", 8)
        if n == 3:
            jugadors[0].screenshot(path=f"{CAP}/grup_8_ratxa_mob.png")
    time.sleep(1)
    mestre.locator(".st-key-cg_m_seg button").first.click(); espera(mestre, ".cg-podi", 8)
    trofeu = mestre.locator("img.cg-trofeu").first
    for _ in range(30):
        if trofeu.evaluate("i => i.complete && i.naturalWidth > 0"):
            break
        time.sleep(0.2)
    print("podi:", txt(mestre, ".cg-podi"), "| trofeu:", trofeu.get_attribute("src"),
          trofeu.evaluate("i => i.naturalWidth"))
    assert trofeu.evaluate("i => i.naturalWidth") > 0 and mestre.locator(".cg-esgrao").count() == 3
    time.sleep(0.8)
    mestre.screenshot(path=f"{CAP}/grup_9_podi_desk.png")
    for k, pg in enumerate(jugadors):
        espera(pg, ".cq-feedback", 6, "POSICIÓ")
        print(f"mobil {k + 1} final:", txt(pg, ".cq-feedback"))
    jugadors[0].screenshot(path=f"{CAP}/grup_10_final_mob.png")
    assert "POSICIÓ 1 DE 3" in txt(jugadors[0], ".cq-feedback")

    # tornar a jugar: la mateixa sala, i els mobils hi son sense tornar a escanejar
    mestre.locator(".st-key-cg_m_torna button").first.click(); espera(mestre, ".cg-titol", 8, "3 A LA SALA")
    for pg in jugadors:
        espera(pg, ".cq-feedback", 8, "JA HI ETS")
    assert mestre.locator(".cg-url").first.get_attribute("data-pin") == pin
    print("tornar a jugar: mateixa sala", pin, "i els 3 mobils a dins sense fer res")

    # cap nom enlloc
    for pg in [mestre] + jugadors:
        cos = pg.locator("body").inner_text().upper()
        assert not any(x in cos for x in ("NOM I COGNOM", "ESCRIU EL TEU NOM", "PANDA", "GUINEU", "LILA"))
    print("errors JS:", errs or "cap", "| tercers:", tercers or "cap")
    assert not errs and not tercers
    chrome.close(); webkit.close()
print("NAVEGADOR GRUP OK")
