"""Entra a l'app com un visitant perque Streamlit Cloud no l'adormi (la fa servir la tasca
.github/workflows/desperta.yml cada hora). No fa cap exercici: no escriu res enlloc."""
import time

from playwright.sync_api import sync_playwright

APP = "https://aventura-matematica.streamlit.app"
with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page()
    pg.goto(APP, timeout=90000)
    time.sleep(8)
    boto = pg.get_by_role("button", name="get this app back up")
    if boto.count():
        print("Dormia: la desperto")
        boto.first.click()
        time.sleep(90)
    pg.goto(APP + "/~/+/", timeout=90000)
    # portada per defecte = cara nova (component a pantalla completa); amb ?antic=1 seria .st-key-home_Mates
    pg.wait_for_selector("iframe[title='app.aventura']", timeout=180000)
    pg.frame_locator("iframe[title='app.aventura']").locator(".gominola").first.wait_for(timeout=60000)
    print("App desperta i portada carregada")
    nav.close()
