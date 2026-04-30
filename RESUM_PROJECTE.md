# 📝 RESUM DE L'AVENTURA MATEMÀTICA (ABRIL 2026)

Aquest document resumeix les millores i l'estat actual de l'aplicació.

## 🏁 MÒDUL DE LECTURA (CARRERA DE COTXES)
- **Mecànica**: Carrera contra un rival controlat per l'ordinador.
- **Velocitat**: Ajustada a **4.5** per als nivells Normal i Difícil per mantenir el repte sense ser impossible.
- **Vocabulari**: Pool de paraules sense repeticions. No es repeteix cap paraula fins que s'ha llegit tot el diccionari del nivell.
- **Visual**: Requadres de paraules centrats i grans per facilitar la lectura.

## 💡 INNOVAMAT I MATES
- **Disseny**: Requadre de pregunta i resposta **idèntics** (140px d'alçada, font Bungee 3.5rem).
- **Contingut**: Eliminades les divisions i conceptes de "meitats" del nivell Fàcil per simplificar la pedagogia.
- **Responsive**: Controls de mòbil gegants (Inici i Nivells) amagats automàticament al PC per deixar la interfície neta.

## 🛠️ MILLORES TÈCNIQUES
- **CSS Quirúrgic**: Ús de Media Queries per separar l'experiència de PC i Mòbil.
- **Session State**: Inicialització robusta de totes les variables per evitar errors de càrrega.
- **Non-Repeating Pool**: Lògica de `pop()` i `shuffle()` per a la varietat de paraules.

## ⚠️ MEMÒRIA DE CONFLICTES
Tots els errors de sintaxi i UI detectats s'han registrat al fitxer:
👉 [ERRORES_A_EVITAR.md](file:///Users/osu/Library/CloudStorage/Dropbox/ANTIGRAVITY/JAN-MAX/mates/ERRORES_A_EVITAR.md)

---
*Estat: Estable i optimitzat per a nens.*
