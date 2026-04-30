# ⚠️ LLISTA DE "CAGADES" A EVITAR (MISTAKES LOG)

Aquest document serveix per recordar els errors comesos i la seva SOLUCIÓ definitiva per no entrar en bucle.

## 🐍 SINTAXI PYTHON (CRÍTIC)
- **❌ Error**: Posar un bloc `elif` després d'un bloc `else`.
  - *Per què ha passat?*: Per una mala identació en tancar els blocs de condició.
  - **✅ Solució**: Estructurar les condicions de manera plana (`if` -> `elif` -> `elif`) sense obrir un `else` innecessari que bloquegi la resta.
  - **🔄 Status**: CORREGIT (30 Abr 2026). REVISAR SEMPRE la identació abans de fer el commit.

- **❌ Error**: Usar `; if` a la mateixa línia.
  - **✅ Solució**: L' `if` sempre en línia nova.
  - **🔄 Status**: MONITORITZAT.

## 🏎️ CARRERA DE COTXES (LECTURA)
- **❌ Error**: El cotxe vermell (rival) semblava que no avançava. El jugador es confonia de cotxe.
- **✅ Solució**: S'ha canviat el cotxe del jugador a **VERMELL** (el color per defecte 🏎️) i el rival a blau/verd. S'ha assegurat que el rival tingui un moviment mínim per evitar que sembli congelat.
- **🔄 Status**: CORREGIT.

## 🚀 STREAMLIT STATE
- **❌ Error**: `AttributeError` per variables no inicialitzades.
- **✅ Solució**: Inicialitzar totes les variables a l'inici amb `if 'var' not in st.session_state`.
- **🔄 Status**: CORREGIT. Afegit `problem_text` i `correct_answer`.

---
*Si veus un error nou, apunta'l aquí i posa la solució abans de seguir.*
