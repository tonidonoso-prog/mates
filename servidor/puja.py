#!/usr/bin/env python3
"""Puja el servidor de progres (calendari i medalles) a osuhosting.com/panel/<carpeta>/ (mateix patro que el
webhook de Fanvue: carpeta propia amb .htaccess que obre nomes aquesta ruta).

  python3 servidor/puja.py            # puja classificacio.php + .htaccess + cfg.php
  python3 servidor/puja.py --prova    # a mes, fa una crida real i comprova que respon

La clau de l'API es genera sola el primer cop i es guarda a
~/.claude/secrets/mates_api.json (MAI a Dropbox ni a git).
"""
import argparse
import io
import json
import os
import secrets
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MOTOR = os.path.expanduser("~/Library/CloudStorage/Dropbox/ANTIGRAVITY/TONI/TD/MOTOR")
sys.path.insert(0, f"{MOTOR}/directorios/pipeline")
import ftp_util  # noqa: E402

CARPETA = "/mates-8f2c1d64b0a7"
URL = "https://osuhosting.com/panel" + CARPETA + "/classificacio.php"
SEC = os.path.expanduser("~/.claude/secrets/mates_api.json")
# /panel te Basic auth; aquesta carpeta s'obre nomes per a l'app, i qualsevol JSON
# de dades (progres.json) i el cfg.php queden tancats: no es poden baixar.
# El .php es diu classificacio.php per no canviar la URL dels Secrets de Streamlit.
HTACCESS = (
    "Satisfy Any\nAllow from all\n"
    "<IfModule mod_authz_core.c>\n  Require all granted\n</IfModule>\n"
    '<FilesMatch "\\.json$">\n  Require all denied\n  Deny from all\n</FilesMatch>\n'
    '<Files "cfg.php">\n  Require all denied\n  Deny from all\n</Files>\n'
    "Options -Indexes\n"
)


def clau():
    if os.path.exists(SEC):
        return json.load(open(SEC))["api_key"]
    k = secrets.token_urlsafe(32)
    os.makedirs(os.path.dirname(SEC), exist_ok=True)
    json.dump({"api_url": URL, "api_key": k}, open(SEC, "w"))
    os.chmod(SEC, 0o600)
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prova", action="store_true")
    a = ap.parse_args()
    k = clau()
    c = json.load(open(f"{MOTOR}/directorios/credenciales/panel-ftp.json"))
    ftp = ftp_util.conectar({"host": c["host"], "user": c["user"], "password": c["password"]})
    try:
        ftp.mkd(CARPETA)
    except Exception:
        pass
    cfg = "<?php return ['clau' => " + json.dumps(k) + "];\n"
    fitxers = (("classificacio.php", open(f"{HERE}/classificacio.php", "rb").read()),
               (".htaccess", HTACCESS.encode()),
               ("cfg.php", cfg.encode()))
    for nom, dades in fitxers:
        ftp.storbinary(f"STOR {CARPETA}/{nom}", io.BytesIO(dades))
    ftp.quit()
    print("pujat ->", URL)
    print("\nsecrets per a Streamlit Cloud (Settings -> Secrets):")
    print(f'api_url = "{URL}"\napi_key = "{k}"')
    if a.prova:
        def crida(cos):
            req = urllib.request.Request(URL, data=json.dumps(cos).encode(), headers={
                "Content-Type": "application/json", "X-Mates-Key": k})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        # una clau que no pot ser de cap nen (els resums reals son de 16 caracters)
        print("prova:", crida({"accio": "jugador", "clau": "00000000"}))


if __name__ == "__main__":
    main()
