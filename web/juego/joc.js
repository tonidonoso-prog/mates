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
  let M = null;              // partida de mates: {op, cua, actual, escrit, intents, punts, ratxa, pendents}
  let lotDemanat = null;
  let primerCop = true;

  // ---------------------------------------------------------------- protocol de Streamlit
  function envia(tipus, dades) {
    window.parent.postMessage(Object.assign({ isStreamlitMessage: true, apiVersion: 1, type: tipus }, dades || {}), "*");
  }
  // Cada accio porta un id i es torna a enviar fins que Python diu que l'ha feta (A.ack): si se n'envien
  // dues seguides, Streamlit nomes veu l'ultim valor i la primera es perdia (24 nov 2026).
  let perEnviar = [], programat = false, ultimEnviament = 0;
  function demana(accio, extra) {
    perEnviar.push(Object.assign({ id: "a" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7), accio: accio }, extra || {}));
    programa();
  }
  function programa() {
    if (programat) return;
    programat = true;
    setTimeout(() => {
      programat = false;
      if (!perEnviar.length) return;
      ultimEnviament = Date.now();
      envia("streamlit:setComponentValue", { value: { n: Date.now() + Math.random(), accions: perEnviar.slice() }, dataType: "json" });
    }, 40);
  }
  setInterval(() => { if (perEnviar.length && Date.now() - ultimEnviament > 2500) programa(); }, 1000);
  window.addEventListener("message", function (e) {
    if (!e.data || e.data.type !== "streamlit:render") return;
    A = e.data.args || {};
    if (A.ack) perEnviar = perEnviar.filter((a) => A.ack.indexOf(a.id) < 0);
    if (A.lot && lotDemanat && A.lot.id === lotDemanat) {
      lotDemanat = null;
      if (M && A.lot.joc === M.joc && A.lot.op === M.op && A.lot.nivell === A.nivell) {
        M.cua = M.cua.concat(A.lot.problemes);
        if (!M.actual) { seguentMates(); return; }
      }
    }
    if (A.partida && pendent && A.partida.id === pendent) {
      pendent = null;
      comencaPartida(A.partida);
    } else if (["partida", "carregant", "mates", "informe", "recta"].indexOf(vista) < 0) {
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
  document.addEventListener("keydown", (e) => {
    const t = /^[0-9]$/.test(e.key) ? e.key : e.key === "Backspace" ? "esborra" : e.key === "Enter" ? "ok" : null;
    if (!t) return;
    if (vista === "mates") tecla(t); else if (vista === "recta") teclaRecta(t);
  });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-fa]"); if (!b) return;
    so("toc");
    const fa = b.dataset.fa, arg = b.dataset.arg;
    setTimeout(() => accio(fa, arg), b.classList.contains("resposta") ? 0 : 170);
  });

  // ---------------------------------------------------------------- accions
  function accio(fa, arg) {
    if (fa === "bloc") {
      if (arg === "Concurs") { demana("obre", { bloc: arg }); vista = "categories"; pinta(); }
      else if (JOCS[arg]) { demana("obre", { bloc: arg }); comencaExercicis(arg); }
      else if (arg === "Recta") { demana("obre", { bloc: arg }); comencaRecta(RT ? RT.op : "suma"); }
      else demana("bloc", { bloc: arg });
    } else if (fa === "nivell") {
      A.nivell = arg; demana("nivell", { nivell: arg });
      if (vista === "mates") comencaExercicis(M.joc, M.op);
      else if (vista === "recta") comencaRecta(RT.op);
      else pinta();
    }
    else if (fa === "op") comencaExercicis(M.joc, arg);
    else if (fa === "repte_altre") comencaExercicis("Repte");
    else if (fa === "tecla") { if (vista === "recta") teclaRecta(arg); else tecla(arg); }
    else if (fa === "recta_op") comencaRecta(arg);
    else if (fa === "recta_inici") { enviaRecta(); vista = "inici"; pinta(); }
    else if (fa === "mates_inici") { enviaResultats(); vista = "inici"; pinta(); }
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

  // Botons de navegació amb text: la fletxa sola no s'entenia (24 nov 2026, el Toni)
  const botoInici = (fa) => `<button class="nav inici" data-fa="${fa || "inici"}"><img src="${img("casa")}" alt="">Inici</button>`;
  const botoEnrere = (fa, text) => `<button class="nav" data-fa="${fa}"><span aria-hidden="true">‹</span> ${text}</button>`;

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
      </header>
      ${nivells()}
      <section class="graella" aria-label="Jocs">${blocs}</section>`;
    primerCop = false;
  }

  function pintaCategories() {
    const cats = A.categories.map((c, i) =>
      `<button class="gominola" style="--c:${COLORS[(i + 2) % COLORS.length]}" data-fa="cat" data-arg="${esc(c.id)}">
        <img src="${img(c.img)}" alt=""><span class="nom">${esc(c.nom)}</span><span class="desc">${c.temes.length} temes</span></button>`).join("");
    $app.innerHTML = `
      <nav class="navegacio">${botoInici()}</nav>
      <div class="barra"><img class="mini" src="${img("concurs")}" alt=""><h1>Kahoot</h1></div>
      <p class="ajuda">Tria de què vols les preguntes. ${A.n_preguntes} preguntes, com més ràpid, més punts!</p>
      ${nivells()}
      <section class="categories">
        <button class="gominola" style="--c:#E8701F" data-fa="tema" data-arg="barreja">
          <img src="${img("barreja")}" alt=""><span class="nom">Barreja de tot</span><span class="desc">Una mica de cada</span></button>
        ${cats}
      </section>
      <h2 class="seccio">Tota la classe alhora</h2>
      <button class="targeta-grup" data-fa="grup">
        <img src="${img("festa")}" alt="">
        <span><b>Kahoot en grup</b>Una pantalla gran per a tothom i cada nen o nena respon amb el seu mòbil o tauleta.</span>
        <span class="fletxa" aria-hidden="true">›</span></button>`;
  }

  function pintaTemes() {
    const c = A.categories.find((x) => x.id === cat);
    const rec = (t) => { const r = A.records[t + "|" + A.nivell]; return r ? `<span class="rec">🏆 ${punts(r)}</span>` : ""; };
    const temes = [`<button class="tema barreja" data-fa="tema" data-arg="barreja_${esc(c.id)}">🎲 Barreja${rec("barreja_" + c.id)}</button>`]
      .concat(c.temes.map((t) => `<button class="tema" data-fa="tema" data-arg="${esc(t.id)}">${esc(t.nom)}${rec(t.id)}</button>`)).join("");
    $app.innerHTML = `
      <nav class="navegacio">${botoEnrere("categories", "Categories")}${botoInici()}</nav>
      <div class="barra"><img class="mini" src="${img(c.img)}" alt=""><h1>${esc(c.nom)}</h1></div>
      ${nivells()}
      <section class="temes">${temes}</section>`;
  }

  // ---------------------------------------------------------------- EXERCICIS AMB TECLAT
  // Un sol motor per a MATES (operacions), CÀLCUL MENTAL (12 tipus) i REPTE (10 barrejats + informe).
  const JOCS = {
    Mates: { titol: "Mates", img: "mates", ops: [["Sumes", "➕ Sumes"], ["Restes", "➖ Restes"], ["Multiplicació", "✖️ Multiplicacions"]] },
    Calcul: { titol: "Càlcul mental", img: "calcul", ops: null },
    Repte: { titol: "Repte", img: "repte", ops: null },
  };
  const REPTE_LEN = 10;

  function comencaExercicis(joc, op) {
    enviaResultats();
    const ops = joc === "Calcul" ? A.calcul_tipus : JOCS[joc].ops;
    op = op || (M && M.joc === joc ? M.op : (ops ? ops[0][0] : ""));
    M = { joc: joc, op: op, cua: [], actual: null, escrit: "", intents: 0,
          punts: M ? M.punts : 0, ratxa: M ? M.ratxa : 0, pendents: [],
          repte: joc === "Repte" ? { i: 0, ok: 0, log: [], t0: performance.now() } : null };
    lotDemanat = null;
    vista = "mates";
    pintaMates();
    demanaLot();
  }
  function demanaLot() {
    if (lotDemanat) return;
    lotDemanat = "l" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    demana("lot", { joc: M.joc, op: M.op, nivell: A.nivell, id: lotDemanat });
  }
  function enviaResultats() {
    if (M && M.pendents.length) { demana("resultats", { respostes: M.pendents, repte: !!(M.repte && M.repte.i >= REPTE_LEN) }); M.pendents = []; }
  }
  function seguentMates() {
    if (M.repte && M.repte.i >= REPTE_LEN) return informeRepte();
    M.actual = M.cua.shift() || null; M.escrit = ""; M.intents = 0;
    if (!M.repte && M.cua.length < 4) demanaLot();
    pintaMates();
  }

  function caixaEscrit() {
    return `<span class="escrit${M.escrit ? "" : " buit"}" id="escrit">${M.escrit ? esc(M.escrit) : "?"}</span>`;
  }
  function enunciatHtml(p) {
    // si l'enunciat ja porta "?" (7 + ? = 10), la casella va al seu lloc; si no, va al final
    let t = esc(p[0]).replace(/ x /g, " × ").replace(/ - /g, " − ");
    // piràmide: la resposta s'escriu a la pedra de dalt (abans hi havia un segon "?" a sota que confonia)
    if (p[2]) return `<div class="piramide">${p[2].replace("<div class='brick ask'>?</div>", "<div class='brick ask'>" + caixaEscrit() + "</div>")}</div>`;
    const llarg = p[0].length > 16;
    t = t.indexOf("?") >= 0 ? t.replace("?", caixaEscrit()) : t + " = " + caixaEscrit();
    return `<p class="operacio${llarg ? " llarga" : ""}">${t}</p>`;
  }

  function pintaMates() {
    const J = JOCS[M.joc];
    const ops = M.joc === "Calcul" ? A.calcul_tipus : J.ops;
    const triaOps = ops ? `<div class="ops${M.joc === "Calcul" ? " moltes" : ""}" role="group" aria-label="Tipus">${ops.map(([op, nom]) =>
      `<button class="op-tria" aria-pressed="${M.op === op}" data-fa="op" data-arg="${esc(op)}">${esc(nom)}</button>`).join("")}</div>` : "";
    const p = M.actual;
    const comptador = M.repte ? `<p class="ajuda">Exercici ${Math.min(M.repte.i + 1, REPTE_LEN)} de ${REPTE_LEN}</p>` : "";
    const tecles = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "esborra", "0", "ok"].map((t) =>
      `<button class="tecla${t === "ok" ? " ok" : t === "esborra" ? " esborra" : ""}" data-fa="tecla" data-arg="${t}"
        aria-label="${t === "ok" ? "Comprovar" : t === "esborra" ? "Esborrar" : t}">${t === "ok" ? "✓" : t === "esborra" ? "⌫" : t}</button>`).join("");
    $app.innerHTML = `
      <nav class="navegacio">${botoInici("mates_inici")}</nav>
      <div class="barra"><img class="mini" src="${img(J.img)}" alt=""><h1>${J.titol}</h1>
        <span class="xips"><span class="xip">⭐ ${M.punts}</span><span class="xip">🔥 ${M.ratxa}</span></span></div>
      ${nivells()}
      ${triaOps}${comptador}
      <section class="exercici">
        <div class="pregunta mates-pregunta">${p && p[4] ? `<p class="consigna">${esc(p[4])}</p>` : ""}${p ? enunciatHtml(p) : "<p class='carregant'>Preparant…</p>"}</div>
        <p class="avis" id="avis"></p>
        <div class="teclat">${tecles}</div>
      </section>`;
    const fila = document.querySelector(".ops.moltes"), sel = fila && fila.querySelector('[aria-pressed="true"]');
    if (sel) fila.scrollLeft = sel.offsetLeft - fila.clientWidth / 2 + sel.clientWidth / 2;   // el tipus triat, a la vista
    alcada();
  }

  function tecla(t) {
    if (!M || !M.actual || M.bloquejat) return;
    if (t === "esborra") M.escrit = M.escrit.slice(0, -1);
    else if (t === "ok") return comprova();
    else if (M.escrit.length < 5) M.escrit += t;
    const e = document.getElementById("escrit");
    e.textContent = M.escrit || "?"; e.classList.toggle("buit", !M.escrit);
  }

  function apunta(be) {
    M.pendents.push(be);
    if (M.repte) {
      M.repte.i += 1; M.repte.ok += be ? 1 : 0;
      M.repte.log.push({ tipus: M.actual[3] || "", be: be });
    }
  }

  function comprova() {
    if (!M.escrit) return;
    const bona = +M.escrit === M.actual[1];
    const avis = document.getElementById("avis");
    if (bona) {
      M.punts += 1; M.ratxa += 1; apunta(true);
      avis.className = "avis si"; avis.textContent = ["Molt bé!", "Ho has clavat!", "Genial!", "Correcte!"][Math.floor(Math.random() * 4)];
      so("si"); confeti(18);
      document.querySelector(".mates-pregunta").classList.add("encert");
      M.bloquejat = true;
      setTimeout(() => { M.bloquejat = false; seguentMates(); }, 1300);
    } else if (M.intents === 0) {
      M.intents = 1; so("no");
      avis.className = "avis no"; avis.textContent = "Gairebé! Torna-ho a provar";
      const c = document.querySelector(".mates-pregunta"); c.classList.remove("malament"); void c.offsetWidth; c.classList.add("malament");
      M.escrit = ""; const e = document.getElementById("escrit"); e.textContent = "?"; e.classList.add("buit");
    } else {
      M.ratxa = 0; apunta(false); so("no");
      avis.className = "avis no"; avis.textContent = "Era " + M.actual[1] + ". Seguim!";
      const e = document.getElementById("escrit"); e.textContent = M.actual[1]; e.classList.add("solucio");
      M.bloquejat = true;
      setTimeout(() => { M.bloquejat = false; seguentMates(); }, 2000);
    }
    if (M.pendents.length >= 5 || (M.repte && M.repte.i >= REPTE_LEN)) enviaResultats();   // de cinc en cinc
  }

  function informeRepte() {
    const r = M.repte;
    const pct = Math.round(100 * r.ok / REPTE_LEN);
    const s = Math.round((performance.now() - r.t0) / 1000);
    const nota = pct >= 90 ? "Excel·lent!" : pct >= 70 ? "Molt bé!" : pct >= 50 ? "Bon treball!" : "Seguim practicant!";
    const fallats = {};
    r.log.forEach((e) => { if (!e.be) fallats[e.tipus || "Càlcul"] = (fallats[e.tipus || "Càlcul"] || 0) + 1; });
    const repassar = Object.keys(fallats).sort((a, b) => fallats[b] - fallats[a]).map((k) => `${esc(k)}: ${fallats[k]}`).join(" · ");
    vista = "informe";
    so("festa"); confeti(40);
    $app.innerHTML = `
      <section class="final">
        <img class="mascota arriba" src="img/mascota.png" alt="">
        <h1>${nota}</h1>
        <div class="xifra">${r.ok} de ${REPTE_LEN}</div>
        <div class="xips centrat"><span class="xip">🎯 ${pct}%</span><span class="xip">⏱️ ${Math.floor(s / 60)}m ${s % 60}s</span><span class="xip">📈 ${esc(A.nivell)}</span></div>
        <p class="rec">${repassar ? "A repassar: <b>" + repassar + "</b>" : "Cap error. Impecable! ✨"}</p>
        <div class="botons">
          <button class="boto" style="--c:#12A982" data-fa="repte_altre">Un altre repte</button>
          <button class="boto" style="--c:#2F8FEA" data-fa="inici">Inici</button>
        </div>
      </section>`;
    window.scrollTo(0, 0);
  }

  // ---------------------------------------------------------------- RECTA NUMÈRICA
  // 24 + 17: salt de +10 fins al 34 i salt de +7 fins al 41; cada parada és una casella per omplir.
  // Les sumes van cap a la dreta i les restes cap a l'esquerra, com a l'escola (24 nov 2026, el Toni).
  let RT = null;
  const rnd = (a, b) => a + Math.floor(Math.random() * (b - a + 1));

  function genRecta(nivell, op) {
    let a, b;
    if (nivell === "Fàcil") { b = rnd(11, 29); a = op === "suma" ? rnd(11, 60) : rnd(b + 5, 90); }
    else if (nivell === "Normal") { b = rnd(21, 39); a = op === "suma" ? rnd(15, 59) : rnd(b + 10, 99); }
    else { b = rnd(21, 49); a = op === "suma" ? rnd(101, 499) : rnd(b + 40, 599); }
    if (b % 10 === 0) b += rnd(1, 9);
    // Com a classe (Innovamat, linia numerica buida): primer les desenes, de 10 en 10 i una a una,
    // i al final les unitats. 210 + 43 -> 220, 230, 240, 250, 253.
    const salts = Array(Math.floor(b / 10)).fill(10);
    salts.push(b % 10);
    const punts = [a];
    salts.forEach((sx) => punts.push(punts[punts.length - 1] + (op === "suma" ? sx : -sx)));
    return { a: a, b: b, op: op, salts: salts, punts: punts };
  }

  function comencaRecta(op) {
    enviaRecta();
    RT = { op: op, punts: RT ? RT.punts : 0, ratxa: RT ? RT.ratxa : 0, pendents: [] };
    vista = "recta";
    novaRecta();
  }
  function enviaRecta() {
    if (RT && RT.pendents.length) { demana("resultats", { respostes: RT.pendents }); RT.pendents = []; }
  }
  function novaRecta() {
    RT.p = genRecta(A.nivell, RT.op);
    RT.actiu = 1; RT.escrit = ""; RT.intents = 0; RT.errors = 0;
    RT.fets = [String(RT.p.a)];              // el que hi ha escrit a cada casella
    RT.estat = ["donat"];                     // donat | be | ajuda
    pintaRecta();
  }

  function rectaSvg() {
    const p = RT.p, n = p.salts.length, W = 360, H = 170, Y = 92, M = 34;
    const amples = p.salts.map((sx) => sx >= 10 ? 1 : .85);   // no cal que siguin proporcionals; així les caselles no es trepitgen
    const total = amples.reduce((x, y) => x + y, 0);
    const xs = [0];
    amples.forEach((w) => xs.push(xs[xs.length - 1] + (W - 2 * M) * w / total));
    const X = (i) => p.op === "suma" ? M + xs[i] : W - M - xs[i];
    const CW = Math.min(54, Math.min(...xs.slice(1).map((x, i) => x - xs[i])) - 4);   // amplada de casella
    let svg = `<svg class="recta-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="Recta numèrica">`;
    svg += `<line x1="8" y1="${Y}" x2="${W - 8}" y2="${Y}" stroke="#3B2A5C" stroke-width="4" stroke-linecap="round"/>`;
    svg += p.op === "suma" ? `<path d="M${W - 18} ${Y - 8} L${W - 6} ${Y} L${W - 18} ${Y + 8}" fill="none" stroke="#3B2A5C" stroke-width="4" stroke-linecap="round"/>`
                           : `<path d="M18 ${Y - 8} L6 ${Y} L18 ${Y + 8}" fill="none" stroke="#3B2A5C" stroke-width="4" stroke-linecap="round"/>`;
    for (let i = 0; i < n; i++) {
      const x1 = X(i), x2 = X(i + 1), h = Math.min(30, 14 + Math.abs(x2 - x1) * .16), mig = (x1 + x2) / 2;   // l'etiqueta mai surt per dalt
      const fet = i < RT.actiu - 0 && RT.estat[i + 1];
      svg += `<path d="M${x1} ${Y - 6} Q${mig} ${Y - 6 - 2 * h} ${x2} ${Y - 6}" fill="none" stroke="${fet ? "#12A982" : "#7A5AF0"}" stroke-width="4" stroke-dasharray="${fet ? "0" : "7 6"}" stroke-linecap="round"/>`;
      svg += `<path d="M${x2 - (p.op === "suma" ? 9 : -9)} ${Y - 14} L${x2} ${Y - 5} L${x2 - (p.op === "suma" ? 1 : -1)} ${Y - 17}" fill="none" stroke="${fet ? "#12A982" : "#7A5AF0"}" stroke-width="4" stroke-linecap="round"/>`;
      svg += `<text x="${mig}" y="${Y - 12 - h}" text-anchor="middle" class="salt">${p.op === "suma" ? "+" : "−"}${p.salts[i]}</text>`;
    }
    for (let i = 0; i <= n; i++) {
      const x = X(i), est = RT.estat[i], actiu = i === RT.actiu;
      const val = i === RT.actiu ? (RT.escrit || "?") : (RT.fets[i] || "");
      const cls = est === "donat" ? "donat" : est === "be" ? "be" : est === "ajuda" ? "ajuda" : actiu ? "actiu" : "buida";
      svg += `<line x1="${x}" y1="${Y - 9}" x2="${x}" y2="${Y + 9}" stroke="#3B2A5C" stroke-width="4" stroke-linecap="round"/>`;
      svg += `<g class="caixa ${cls}"><rect x="${x - CW / 2}" y="${Y + 18}" width="${CW}" height="40" rx="12"/>
              <text x="${x}" y="${Y + 46}" text-anchor="middle">${esc(val)}</text></g>`;
    }
    return svg + "</svg>";
  }

  function consignaRecta() {
    const p = RT.p, i = RT.actiu, n = p.salts.length;
    if (i > n) return "Fet!";
    const salt = (p.op === "suma" ? "+" : "−") + p.salts[i - 1];
    const v = +RT.fets[i - 1], des = (v === 1 || v === 11) ? `des de l'${v}` : `des del ${v}`;   // l'u i l'onze s'apostrofen
    return i < n ? `Salt ${i} de ${n}: ${des}, fes ${salt}. On arribes?`
                 : `Últim salt: ${des}, fes ${salt}. Aquesta casella és el resultat!`;
  }

  function pintaRecta() {
    const p = RT.p, signe = p.op === "suma" ? "+" : "−";
    const ultim = RT.estat[p.punts.length - 1];
    const tecles = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "esborra", "0", "ok"].map((t) =>
      `<button class="tecla${t === "ok" ? " ok" : t === "esborra" ? " esborra" : ""}" data-fa="tecla" data-arg="${t}"
        aria-label="${t === "ok" ? "Comprovar" : t === "esborra" ? "Esborrar" : t}">${t === "ok" ? "✓" : t === "esborra" ? "⌫" : t}</button>`).join("");
    $app.innerHTML = `
      <nav class="navegacio">${botoInici("recta_inici")}</nav>
      <div class="barra"><img class="mini" src="${img("recta")}" alt=""><h1>Recta numèrica</h1>
        <span class="xips"><span class="xip">⭐ ${RT.punts}</span><span class="xip">🔥 ${RT.ratxa}</span></span></div>
      ${nivells()}
      <div class="ops" role="group" aria-label="Operació">
        <button class="op-tria" aria-pressed="${RT.op === "suma"}" data-fa="recta_op" data-arg="suma">➕ Sumes ➡️</button>
        <button class="op-tria" aria-pressed="${RT.op === "resta"}" data-fa="recta_op" data-arg="resta">⬅️ Restes ➖</button></div>
      <section class="exercici">
        <div class="pregunta mates-pregunta recta">
          <p class="consigna">${consignaRecta()}</p>
          <p class="operacio llarga">${p.a} ${signe} ${p.b} = <span class="escrit${ultim ? " solucio" : " buit"}">${ultim ? RT.fets[p.punts.length - 1] : "?"}</span></p>
          ${rectaSvg()}
        </div>
        <p class="avis" id="avis"></p>
        <div class="teclat">${tecles}</div>
      </section>`;
    alcada();
  }

  function teclaRecta(t) {
    if (!RT || RT.bloquejat) return;
    if (t === "esborra") RT.escrit = RT.escrit.slice(0, -1);
    else if (t === "ok") return comprovaRecta();
    else if (RT.escrit.length < 4) RT.escrit += t;
    const caixa = document.querySelectorAll(".recta-svg .caixa")[RT.actiu];
    if (caixa) caixa.querySelector("text").textContent = RT.escrit || "?";
  }

  function comprovaRecta() {
    if (!RT.escrit) return;
    const p = RT.p, i = RT.actiu, bona = +RT.escrit === p.punts[i];
    const ultima = i === p.punts.length - 1;
    const avisa = (cls, text) => { const a = document.getElementById("avis"); a.className = "avis " + cls; a.textContent = text; };
    if (bona || RT.intents >= 1) {
      if (!bona) RT.errors += 1;
      RT.fets[i] = String(p.punts[i]); RT.estat[i] = bona ? "be" : "ajuda";
      RT.actiu = i + 1; RT.escrit = ""; RT.intents = 0;
      pintaRecta();
      if (!ultima) {
        if (bona) { so("toc"); avisa("si", "Molt bé! Ara el salt següent"); }
        else { so("no"); avisa("no", "Era " + p.punts[i] + ". Seguim saltant!"); }
        return;
      }
      const be = RT.errors === 0;
      RT.pendents.push(be);
      if (be) { RT.punts += 1; RT.ratxa += 1; so("si"); confeti(22); avisa("si", `Molt bé! ${p.a} ${p.op === "suma" ? "+" : "−"} ${p.b} = ${p.punts[i]}`); }
      else { RT.ratxa = 0; so("no"); avisa("no", `${p.a} ${p.op === "suma" ? "+" : "−"} ${p.b} = ${p.punts[i]}. La pròxima, segur!`); }
      document.querySelectorAll(".xip")[0].textContent = "⭐ " + RT.punts;
      document.querySelectorAll(".xip")[1].textContent = "🔥 " + RT.ratxa;
      if (RT.pendents.length >= 5) enviaRecta();
      RT.bloquejat = true;
      setTimeout(() => { RT.bloquejat = false; novaRecta(); }, 2300);
    } else {
      RT.intents = 1; so("no"); avisa("no", "Gairebé! Torna-ho a provar");
      RT.escrit = "";
      const caixa = document.querySelectorAll(".recta-svg .caixa")[i];
      caixa.querySelector("text").textContent = "?";
      caixa.classList.remove("tremola"); void caixa.getBoundingClientRect(); caixa.classList.add("tremola");
    }
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
        <div class="sortida"><button class="boto-sortir" data-fa="sortir">🚪 Sortir de la partida</button></div>
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
