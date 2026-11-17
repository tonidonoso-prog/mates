# CHECKS · Aventura Matemàtica

Línies «si toques X → comprova Y · origen». Abans de donar per bo un canvi, fes només les que toquen.
Mètode general: `~/.claude/VERIFICACION.md`.

- **Si toques qualsevol text que mostri el nom del nen** (portada, barra lateral, calendari, informes) → només `nom_public()` (nom + inicial) i sempre `html.escape` si va dins `unsafe_allow_html`. `python3 tests/test_all.py` ho prova. · _17-nov-2026, el verificador va veure «Hola Jan Test!» a la portada i HTML injectat pel camp del nom_
- **Si escrius exemples, placeholders, docstrings o tests** → cap nom real de nen ni de la família (el repo de GitHub és PÚBLIC). Exemple neutre: «Anna Pons». · _17-nov-2026, «Ex: Jan Donoso» al camp del nom, visible per a tots els pares_
- **Si mostres un error a la pantalla** → missatge amable i genèric; el detall (`str(e)`) només al log amb `print`. · _17-nov-2026, «No s'ha pogut desar el progrés: HTTP Error 403» als pares_
- **Si toques `servidor/classificacio.php`** → `php -l`, pujar amb `python3 servidor/puja.py`, i des de fora: sense clau 403, `progres.json` i `cfg.php` no es veuen, cap ruta del servidor als errors. Màxim ~10 peticions amb 2 s de pausa (Imunify360 banneja). · _17-nov-2026, revisió del verificador_
- **Si puges la versió de Streamlit** → canviar-la a `requirements.txt` (està fixada) i passar els 3 tests + `tests/navegador_concurs.py`. · _17-nov-2026, sense versió fixada un Streamlit nou podia trencar l'app en un redesplegament_
