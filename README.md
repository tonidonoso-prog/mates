# 🧮 Aventura Matemàtica

Una aplicació web interactiva i divertida per practicar matemàtiques, dissenyada per a nens.

## 🚀 Característiques
- **Sumes, Restes i Multiplicacions**: Diferents modes de joc per practicar diverses operacions.
- **Disseny Premium**: Interfície d'usuari moderna, vibrant i fàcil d'utilitzar.
- **Feedback Interactiu**: Animacions i missatges positius per motivar l'aprenentatge.
- **Puntuació**: Seguiment de punts per gamificar l'experiència.

## 🛠️ Instal·lació local

1. Clonar el repositori:
   ```bash
   git clone https://github.com/tonidonoso-prog/mates.git
   cd mates
   ```

2. Instal·lar les dependències:
   ```bash
   pip install -r requirements.txt
   ```

3. Executar l'aplicació:
   ```bash
   streamlit run app.py
   ```

## 🌐 Desplegament
Aquesta aplicació està optimitzada per ser desplegada a **Streamlit Cloud**.

## 🙏 Crèdits
- Animacions de felicitar: [Noto Emoji Animation](https://googlefonts.github.io/noto-emoji-animation/) de Google, llicència CC BY 4.0.
- Dibuixos per pintar: [OpenMoji](https://openmoji.org/), llicència CC BY-SA 4.0.

## 🔒 Privacitat
L'app no demana cap nom. Cada mòbil o tauleta té un número a l'atzar (guardat al navegador, `am_dispositiu`) i al servidor només hi van aquest número, els punts i els dies jugats.

Al **concurs en grup** (pantalla gran) s'hi entra escanejant un QR, sense escriure res: a cadascú li toca un animal i un color a l'atzar. La partida viu només a la memòria de l'app i no es desa enlloc (ni punts ni classificació); una sala sense moviment desapareix sola al cap de 3 hores. El QR es genera a la mateixa app, sense serveis de tercers, i l'app no envia estadístiques d'ús a Streamlit.
