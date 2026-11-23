/* Aventura Matemàtica · nova cara (23 nov 2026). Component de Streamlit fet a mà, sense dependències.
   Python dona les dades (jocs, categories, preguntes) i desa el progrés; aquí hi ha tota la partida,
   el compte enrere i les animacions, sense recarregar la pàgina a cada segon. */
(function () {
  "use strict";
  const $app = document.getElementById("app");
  const $capa = document.getElementById("capa");
  const COLORS = ["#F2544A", "#2F8FEA", "#12A982", "#7A5AF0", "#EC5C9F", "#E8701F"];
  const RESP = [["★", "#7A5AF0"], ["●", "#E8701F"], ["▲", "#12A982"], ["■", "#EC5C9F"]];
  const PAUSA = 2500;

  let A = null;              // el que envia Python
  let vista = "inici";
  let cat = null;            // categoria triada
  let pendent = null;        // id de la partida que hem demanat
  let P = null;              // partida en curs
  let avisosVistos = 0;
  let primerCop = true;

  // ---------------------------------------------------------------- protocol de Streamlit
  function envia(tipus, dades) {
    window.parent.postMessage(Object.assign({ isStreamlitMessage: true, apiVersion: 1, type: tipus }, dades || {}), "*");
  }
  function demana(accio, extra) {
    envia("streamlit:setComponentValue", { value: Object.assign({ n: Date.now() + Math.random(), accio: accio }, extra || {}), dataType: "json" });
  }
  window.addEventListener("message", function (e) {
    if (!e.data || e.data.type !== "streamlit:render") return;
    A = e.data.args || {};
    if (A.partida && pendent && A.partida.id === pendent) {
      pendent = null;
      comencaPartida(A.partida);
    } else if (vista !== "partida" && vista !== "carregant") {
      pinta();
    }
    mostraAvisos();
  });
  envia("streamlit:componentReady");
  function alcada() { envia("streamlit:setFrameHeight", { height: Math.max(window.innerHeight, 600) }); }
  window.addEventListener("resize", alcada);

  // ---------------------------------------------------------------- utilitats
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const punts = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  const img = (nom) => "img/" + nom + ".png";

  let ac = null;
  function so(tipus) {
    try {
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      const notes = { toc: [[620, .045]], si: [[523, .09], [659, .09], [784, .18]], no: [[233, .22]],
        festa: [[523, .1], [659, .1], [784, .1], [1046, .3]] }[tipus];
      let t = ac.currentTime;
      for (const [f, d] of notes) {
        const o = ac.createOscillator(), g = ac.createGain();
        o.type = "triangle"; o.frequency.value = f;
        g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.16, t + .012); g.gain.exponentialRampToValueAtTime(.0001, t + d);
        o.connect(g).connect(ac.destination); o.start(t); o.stop(t + d + .03); t += d * .85;
      }
    } catch (e) { /* sense so, no passa res */ }
  }
  function parla(text) {
    const s = window.speechSynthesis; if (!s) return;
    s.cancel();
    const u = new SpeechSynthesisUtterance(text); u.lang = "ca-ES"; u.rate = .9;
    const v = s.getVoices().filter((x) => /^ca/i.test(x.lang))[0]; if (v) u.voice = v;
    s.speak(u);
  }
  function textVeu(q) {
    let t = q.text.toLowerCase().replace(/×/g, " per ").replace(/\+/g, " més ").replace(/−/g, " menys ").replace(/= \?/g, ", quant fa?");
    const ops = q.opcions.map((o) => o.toLowerCase().replace(/[^\p{L}\p{N}\s,.'€·:-]/gu, "").trim()).filter(Boolean);
    return t + ". " + ops.join(". ") + ".";
  }

  // aixafar i estirar a cada toc; l'acció arriba quan el bloc ja ha rebotat una mica
  document.addEventListener("pointerdown", (e) => { const b = e.target.closest("button"); if (b) b.classList.add("premut"); });
  ["pointerup", "pointercancel", "pointerleave"].forEach((ev) => document.addEventListener(ev, (e) => {
    const b = e.target.closest && e.target.closest("button"); if (!b) return;
    b.classList.remove("premut"); b.classList.remove("boing"); void b.offsetWidth; b.classList.add("boing");
  }, true));
  document.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-fa]"); if (!b) return;
    so("toc");
    const fa = b.dataset.fa, arg = b.dataset.arg;
    setTimeout(() => accio(fa, arg), b.classList.contains("resposta") ? 0 : 170);
  });

  // ---------------------------------------------------------------- accions
  function accio(fa, arg) {
    if (fa === "bloc") {
      if (arg === "Concurs") { vista = "categories"; pinta(); } else demana("bloc", { bloc: arg });
    } else if (fa === "nivell") { A.nivell = arg; demana("nivell", { nivell: arg }); pinta(); }
    else if (fa === "inici") { vista = "inici"; pinta(); }
    else if (fa === "categories") { vista = "categories"; pinta(); }
    else if (fa === "cat") { cat = arg; vista = "temes"; pinta(); }
    else if (fa === "tema") demanaPartida(arg);
    else if (fa === "resposta") respon(+arg);
    else if (fa === "escolta") parla(textVeu(P.preguntes[P.idx]));
    else if (fa === "sortir") { atura(); vista = cat ? "temes" : "categories"; pinta(); }
    else if (fa === "antic") demana("antic");
    else if (fa === "grup") demana("bloc", { bloc: "Concurs" });
  }

  function demanaPartida(tema) {
    pendent = "p" + Date.now();
    vista = "carregant"; pinta();
    demana("comenca", { tema: tema, nivell: A.nivell, id: pendent });
  }

  // ---------------------------------------------------------------- pantalles
  function pinta() {
    if (!A) return;
    if (vista === "inici") pintaInici();
    else if (vista === "categories") pintaCategories();
    else if (vista === "temes") pintaTemes();
    else if (vista === "carregant") $app.innerHTML = "<p class='carregant'>Preparant les preguntes…</p>";
    else if (vista === "final") pintaFinal();
    window.scrollTo(0, 0);
    alcada();
  }

  function nivells() {
    return "<div class='nivells' role='group' aria-label='Nivell'>" + A.nivells.map((n) =>
      `<button data-fa="nivell" data-arg="${esc(n)}" aria-pressed="${n === A.nivell}">${esc(n)}</button>`).join("") + "</div>";
  }

  function pintaInici() {
    const blocs = A.blocs.map((b, i) =>
      `<button class="gominola${b.nou ? " nou" : ""}" style="--c:${COLORS[i % COLORS.length]}" data-fa="bloc" data-arg="${esc(b.id)}">
        <img src="${img(b.img)}" alt=""><span class="nom">${esc(b.nom)}</span><span class="desc">${esc(b.desc)}</span></button>`).join("");
    $app.innerHTML = `
      <header class="cap">
        <img class="mascota${primerCop ? " arriba" : ""}" src="img/mascota.png" alt="El robot de l'Aventura Matemàtica">
        <p class="bafarada"><b>Hola!</b>A què juguem avui?</p>
        <div class="medalles" title="Medalles del dia"><img src="${img("estrella")}" alt="">${A.medalles}</div>
      </header>
      ${nivells()}
      <section class="graella" aria-label="Jocs">${blocs}
        <button class="gominola llarga" style="--c:#2F8FEA" data-fa="bloc" data-arg="Calendari">
          <img src="${img("calendari")}" alt=""><span class="nom">El meu calendari i medalles</span></button>
      </section>`;
    primerCop = false;
  }

  function pintaCategories() {
    const cats = A.categories.map((c, i) =>
      `<button class="gominola" style="--c:${COLORS[(i + 2) % COLORS.length]}" data-fa="cat" data-arg="${esc(c.id)}">
        <img src="${img(c.img)}" alt=""><span class="nom">${esc(c.nom)}</span><span class="desc">${c.temes.length} temes</span></button>`).join("");
    $app.innerHTML = `
      <div class="barra"><button class="tornar" data-fa="inici" aria-label="Tornar a l'inici">‹</button>
        <img class="mini" src="${img("concurs")}" alt=""><h1>Kahoot</h1></div>
      <p class="ajuda">Tria de què vols les preguntes. ${A.n_preguntes} preguntes, com més ràpid, més punts!</p>
      ${nivells()}
      <section class="categories">
        <button class="gominola" style="--c:#E8701F" data-fa="tema" data-arg="barreja">
          <img src="${img("barreja")}" alt=""><span class="nom">Barreja de tot</span><span class="desc">Una mica de cada</span></button>
        ${cats}
        <button class="gominola llarga" style="--c:#7A5AF0" data-fa="grup">
          <img src="${img("festa")}" alt=""><span class="nom">Jugar en grup amb una pantalla gran</span></button>
      </section>`;
  }

  function pintaTemes() {
    const c = A.categories.find((x) => x.id === cat);
    const rec = (t) => { const r = A.records[t + "|" + A.nivell]; return r ? `<span class="rec">🏆 ${punts(r)}</span>` : ""; };
    const temes = [`<button class="tema barreja" data-fa="tema" data-arg="barreja_${esc(c.id)}">🎲 Barreja${rec("barreja_" + c.id)}</button>`]
      .concat(c.temes.map((t) => `<button class="tema" data-fa="tema" data-arg="${esc(t.id)}">${esc(t.nom)}${rec(t.id)}</button>`)).join("");
    $app.innerHTML = `
      <div class="barra"><button class="tornar" data-fa="categories" aria-label="Tornar a les categories">‹</button>
        <img class="mini" src="${img(c.img)}" alt=""><h1>${esc(c.nom)}</h1></div>
      ${nivells()}
      <section class="temes">${temes}</section>`;
  }

  // ---------------------------------------------------------------- partida
  let rellotge = null;
  function atura() { if (rellotge) clearInterval(rellotge); rellotge = null; if (window.speechSynthesis) speechSynthesis.cancel(); }

  function comencaPartida(p) {
    P = { tema: p.tema, nivell: p.nivell, segons: p.segons, preguntes: p.preguntes, idx: 0, punts: 0, encerts: 0, respostes: [],
          record: p.record || 0 };
    vista = "partida";
    mostraPregunta();
  }

  function mostraPregunta() {
    const q = P.preguntes[P.idx];
    P.t0 = performance.now(); P.respost = false;
    const llarg = q.emoji.replace(/<[^>]+>|\s|️/g, "").length > 4;
    const C = 2 * Math.PI * 34;
    $app.innerHTML = `
      <section class="partida">
        <div class="marcador"><span>${P.idx + 1} de ${P.preguntes.length}</span>
          <div class="rellotge" role="timer" aria-label="Segons que queden">
            <svg width="78" height="78" viewBox="0 0 78 78"><circle cx="39" cy="39" r="34" fill="#fff" stroke="rgba(59,42,92,.12)" stroke-width="8"/>
            <circle id="arc" cx="39" cy="39" r="34" fill="none" stroke="#12A982" stroke-width="8" stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="0"/></svg>
            <span class="num" id="num">${P.segons}</span></div>
          <span class="punts">⭐ ${punts(P.punts)}</span></div>
        <div class="pregunta">
          ${q.emoji ? `<div class="dibuix${llarg ? " llarg" : ""}">${q.emoji}</div>` : ""}
          <p class="enunciat">${esc(q.text)}</p>
          <button class="escolta" data-fa="escolta"><img src="${img("altaveu")}" alt="">Escolta</button>
        </div>
        <p class="avis" id="avis"></p>
        <div class="respostes">${q.opcions.map((o, i) =>
          `<button class="resposta" style="--c:${RESP[i][1]}" data-fa="resposta" data-arg="${i}"><span class="forma" aria-hidden="true">${RESP[i][0]}</span>${esc(o)}</button>`).join("")}</div>
        <button class="sortir" data-fa="sortir">Sortir de la partida</button>
      </section>`;
    window.scrollTo(0, 0);
    atura();
    rellotge = setInterval(() => {
      const passat = (performance.now() - P.t0) / 1000, queda = Math.max(0, P.segons - passat);
      const num = document.getElementById("num"), arc = document.getElementById("arc");
      if (!num) return;
      num.textContent = Math.ceil(queda);
      arc.setAttribute("stroke-dashoffset", String(C * (1 - queda / P.segons)));
      arc.setAttribute("stroke", queda <= 5 ? "#F2544A" : "#12A982");
      num.parentElement.classList.toggle("poc", queda <= 5);
      if (queda <= 0) respon(null);
    }, 100);
  }

  function respon(i) {
    if (!P || P.respost) return;
    P.respost = true; atura();
    const q = P.preguntes[P.idx];
    const t = (performance.now() - P.t0) / 1000;
    const be = i === q.correcta;
    const guanya = be ? Math.round(1000 * (1 - Math.min(t, P.segons) / (2 * P.segons))) : 0;
    P.punts += guanya; P.encerts += be ? 1 : 0;
    if (i !== null) P.respostes.push(be);             // el temps esgotat no resta
    document.querySelectorAll(".resposta").forEach((b, k) => {
      b.disabled = true;
      if (k === q.correcta) b.classList.add("bona");
      else if (k === i) b.classList.add("malament");
      else b.classList.add("apagada");
    });
    const avis = document.getElementById("avis");
    if (be) { avis.className = "avis si"; avis.textContent = `Correcte! +${guanya}`; so("si"); confeti(14); }
    else if (i === null) { avis.className = "avis no"; avis.textContent = "S'ha acabat el temps!"; so("no"); }
    else { avis.className = "avis no"; avis.textContent = "Gairebé! Era aquesta"; so("no"); }
    document.querySelector(".punts").textContent = "⭐ " + punts(P.punts);
    setTimeout(() => {
      if (vista !== "partida") return;
      P.idx += 1;
      if (P.idx < P.preguntes.length) mostraPregunta();
      else acaba();
    }, PAUSA);
  }

  function acaba() {
    vista = "final";
    const clau = P.tema + "|" + P.nivell;
    P.nouRecord = P.punts > (A.records[clau] || 0) && (A.records[clau] || 0) > 0;
    P.primer = !(A.records[clau] > 0);
    demana("final", { tema: P.tema, nivell: P.nivell, punts: P.punts, encerts: P.encerts, respostes: P.respostes });
    pinta(); so("festa"); confeti(40);
  }

  function pintaFinal() {
    const rec = P.nouRecord ? `<p class="rec nou">🏆 Nou rècord!</p>`
      : P.primer ? `<p class="rec">Aquest és el teu primer rècord en aquest tema.</p>`
      : `<p class="rec">El teu rècord: ⭐ ${punts(A.records[P.tema + "|" + P.nivell] || 0)}</p>`;
    $app.innerHTML = `
      <section class="final">
        <img class="mascota arriba" src="img/mascota.png" alt="">
        <h1>${P.encerts >= P.preguntes.length * .7 ? "Molt bé!" : "Bona feina!"}</h1>
        <p>Has encertat ${P.encerts} de ${P.preguntes.length}</p>
        <div class="xifra">⭐ ${punts(P.punts)}</div>
        ${rec}
        <div class="botons">
          <button class="boto" style="--c:#12A982" data-fa="tema" data-arg="${esc(P.tema)}">Tornar a jugar</button>
          <button class="boto" style="--c:#7A5AF0" data-fa="${cat ? "cat" : "categories"}" data-arg="${esc(cat || "")}">Un altre tema</button>
          <button class="boto" style="--c:#2F8FEA" data-fa="inici">Inici</button>
        </div>
      </section>`;
  }

  // ---------------------------------------------------------------- celebracions
  function confeti(n) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    for (let k = 0; k < n; k++) {
      const c = document.createElement("i");
      c.className = "confeti";
      c.style.left = Math.random() * 100 + "vw";
      c.style.background = COLORS[k % COLORS.length];
      c.style.animationDelay = Math.random() * 300 + "ms";
      c.style.animationDuration = 1000 + Math.random() * 900 + "ms";
      document.body.appendChild(c);
      setTimeout(() => c.remove(), 2400);
    }
  }

  // medalles: a pantalla completa, de una en una, i se'n van soles (mai una X petita)
  function mostraAvisos() {
    if (!A || !A.avisos || A.avisos.n <= avisosVistos) return;
    avisosVistos = A.avisos.n;
    const cua = A.avisos.llista.slice();
    const seguent = () => {
      const a = cua.shift();
      if (!a) { $capa.hidden = true; return; }
      $capa.innerHTML = `<div><img src="${img("medalla")}" alt=""><h2>${esc(a[1])}</h2><p>${esc(a[0])} ${esc(a[2])}</p></div>`;
      $capa.hidden = false; so("festa"); confeti(30);
      setTimeout(seguent, 2600);
    };
    setTimeout(seguent, vista === "final" ? 1200 : 0);
  }
})();
