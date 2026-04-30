# ⚠️ LLISTA DE "CAGADES" A EVITAR (MISTAKES LOG)

Aquest document serveix per recordar els errors comesos i la seva SOLUCIÓ definitiva per no entrar en bucle.

## 🏎️ CARRERA DE COTXES (LECTURA)
- **❌ Error**: El cotxe vermell (rival) semblava que no avançava. El jugador es confonia de cotxe.
- **✅ Solució**: S'ha canviat el cotxe del jugador a **VERMELL** (el color per defecte 🏎️) i el rival a blau/verd. S'ha assegurat que el rival tingui un moviment mínim per evitar que sembli congelat.
- **🔄 Status**: CORREGIT (30 Abr 2026). No tornar a intercanviar els colors. El cotxe principal ha de ser el vermell.

## 🐍 SINTAXI PYTHON
- **❌ Error**: Usar `; if` a la mateixa línia.
- **✅ Solució**: L' `if` sempre en línia nova.
- **🔄 Status**: MONITORITZAT. No s'ha repetit en els últims 3 commits.

## 🚀 STREAMLIT STATE
- **❌ Error**: `AttributeError` per variables no inicialitzades.
- **✅ Solució**: Inicialitzar totes les variables a l'inici amb `if 'var' not in st.session_state`.
- **🔄 Status**: CORREGIT. Afegit `problem_text` i `correct_answer`.

## 🎨 UI & CSS
- **❌ Error**: La caixa de resposta sortia "aixafada" o més petita que la de la pregunta.
- **✅ Solució**: Forçar `height: 140px !important` a totes les capes del contenidor del `number_input`.
- **🔄 Status**: CORREGIT. Les dues caixes ara són idèntiques.

---
*Si veus un error nou, apunta'l aquí i posa la solució abans de seguir.*
