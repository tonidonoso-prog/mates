# ⚠️ LLISTA DE "CAGADES" A EVITAR (MISTAKES LOG)

Aquest document serveix per recordar els errors comesos durant el desenvolupament de **Aventura Matemàtica** i no tornar-los a repetir.

## 🐍 SINTAXI PYTHON
- **❌ Cagada**: Posar un `if` a la mateixa línia que una altra sentència usant `;`.
  - *Exemple dolent*: `n = 10; if x: n = 5`
  - **✅ Solució**: L' `if` sempre ha d'anar en una línia nova. Python no permet sentències compostes després d'un punt i coma.

## 🚀 STREAMLIT STATE
- **❌ Cagada**: Oblidar inicialitzar variables a `st.session_state` (com `problem_text` o `correct_answer`).
  - **✅ Solució**: Totes les variables d'estat han d'estar al bloc inicial d' `if 'var' not in st.session_state`.
- **❌ Cagada**: Inicialitzar `problem_text = ""` i no generar el primer problema.
  - **✅ Solució**: Cridar a `get_new_problem()` immediatament després de la inicialització perquè l'usuari no vegi un quadre en blanc al principi.

## 🎨 UI & CSS
- **❌ Cagada**: Usar selectors CSS massa agressius (com `:has` en contenidors pare) que acaben amagant tota la pàgina al PC.
  - **✅ Solució**: Usar classes molt específiques com `.mobile-only-section` i amagar-les només en `min-width: 768px`.
- **❌ Cagada**: Intentar detectar el mòbil des de Python.
  - **✅ Solució**: Streamlit no ho fa bé. La millor manera és fer-ho via CSS Media Queries (`max-width: 767px`).

## 🎮 LÒGICA DE JOC
- **❌ Cagada**: Repetir paraules en el nivell de Lectura.
  - **✅ Solució**: Usar una "bossa" (pool) de paraules barrejades i anar-les treient (`pop`) fins que s'acabin.
- **❌ Cagada**: Velocitat del rival massa alta en Difícil.
  - **✅ Solució**: Mantenir una velocitat equilibrada (màxim 4.5) per no frustrar el nen.

---
*Aquest document s'ha d'actualitzar amb cada error nou per aprendre de la lliçó.*
