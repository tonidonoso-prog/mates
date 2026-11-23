"""Temes del CONCURS (23 nov 2026): 69 temes en 12 categories, per a nens de 6 a 8 anys.

Cada tema dona preguntes {text, emoji, opcions (4), correcta}. N'hi ha de tres menes:
- generades (mates, calendari, lletres): mai s'acaben i sempre es poden comprovar;
- bancs de preguntes escrites a ma, amb la bona i les enganyoses;
- taules (clau -> valor), on les enganyoses son els altres valors de la mateixa taula.

Nivells: una linia que comenca amb * nomes surt a Normal i Dificil; amb ** nomes a Dificil.
Si un nivell es queda amb poques preguntes, s'hi afegeixen les dels altres.

Els temes que fan servir dades de app.py (sumes, restes, taules, calcul, animals, lletra) es
generen alla; aqui nomes hi ha el seu nom i la seva categoria.
"""
import random

# ------------------------------------------------------------------ categories
CATEGORIES = [
    ("mates", "🔢 MATES"), ("llengua", "🔤 LLENGUA"), ("angles", "💬 ANGLÈS"),
    ("natura", "🐾 NATURA"), ("ciencia", "🔬 COS I ESPAI"), ("mon", "🌍 EL MÓN"),
    ("catalunya", "🌹 CATALUNYA"), ("historia", "📜 HISTÒRIA"), ("cultura", "🎨 ART, MÚSICA I ESPORT"),
    ("vida", "🏙️ VIDA DIÀRIA"), ("temps", "📅 CALENDARI I TEMPS"), ("logica", "🧩 LÒGICA"),
]
NOM_CATEGORIA = dict(CATEGORIES)

# (id, etiqueta, categoria) en l'ordre que surten
TEMES = []
_GEN = {}           # id -> funcio(diff) que torna una pregunta
NIVELLS = {"Fàcil": 0, "Normal": 1, "Difícil": 2}


def _tema(tid, label, cat):
    TEMES.append((tid, label, cat))


def _q(text, bona, falses, emoji=""):
    """Pregunta amb la bona i 3 enganyoses (diferents entre elles i de la bona)."""
    vistes, ops = {bona.upper()}, [bona]
    for f in falses:
        if f.upper() not in vistes:
            vistes.add(f.upper())
            ops.append(f)
        if len(ops) == 4:
            break
    if len(ops) < 4:
        return None
    ops = [o.upper() for o in ops]
    random.shuffle(ops)
    return {"text": text.upper(), "emoji": emoji, "opcions": ops, "correcta": ops.index(bona.upper())}


def el_num(n):
    """'el 7', pero 'l'1' i 'l'11' (en catala l'u i l'onze s'apostrofen)."""
    return f"l'{n}" if n in (1, 11) else f"el {n}"


def del_num(n):
    return f"de l'{n}" if n in (1, 11) else f"del {n}"


def de(paraula):
    return f"d'{paraula}" if paraula[0].lower() in "aeiouàèéíòóúh" else f"de {paraula}"


def de_num(n):
    """'el doble de 7', pero 'el doble d'1' i 'd'11'."""
    return f"d'{n}" if n in (1, 11) else f"de {n}"


def _enganyoses_num(ans, salts=(1, 2, 3, 10), minim=0):
    pool = {ans + s for s in salts} | {ans - s for s in salts}
    pool = [v for v in pool if v >= minim and v != ans]
    random.shuffle(pool)
    return pool


def _linies(txt):
    """Linies 'camp | camp | ...' amb el nivell (0, 1 o 2 estrelles al davant)."""
    out = []
    for l in txt.strip().splitlines():
        l = l.strip()
        if not l or l.startswith("#"):
            continue
        n = 0
        while l.startswith("*"):
            n, l = n + 1, l[1:]
        out.append((n, [p.strip() for p in l.split("|")]))
    return out


def _del_nivell(items, diff, minim=12):
    nv = NIVELLS.get(diff, 0)
    tria = [it for it in items if it[0] <= nv]
    return tria if len(tria) >= minim else items


def banc(tid, label, cat, txt):
    """Linia: emoji | pregunta | bona | enganyosa | enganyosa | enganyosa [| mes enganyoses]"""
    items = _linies(txt)
    for n, p in items:
        assert len(p) >= 6, (tid, p)
    _tema(tid, label, cat)

    def gen(diff):
        _, (emoji, preg, bona, *falses) = random.choice(_del_nivell(items, diff))
        return _q(preg, bona, random.sample(falses, len(falses)), emoji)
    _GEN[tid] = gen
    return items


def taula(tid, label, cat, plantilla, txt, amb_de=False):
    """Linia: emoji | clau | valor. Pregunta = plantilla amb {clau}; enganyoses = altres valors.
    amb_de: la clau va precedida de 'de' apostrofat ('el contrari d'alt', 'el femeni d'avi')."""
    items = _linies(txt)
    for n, p in items:
        assert len(p) == 3, (tid, p)
    valors = sorted({p[2] for _, p in items})
    _tema(tid, label, cat)

    def gen(diff):
        _, (emoji, clau, bona) = random.choice(_del_nivell(items, diff))
        falses = random.sample([v for v in valors if v != bona], min(8, len(valors) - 1))
        return _q(plantilla.format(clau=de(clau) if amb_de else clau), bona, falses, emoji)
    _GEN[tid] = gen
    return items


def grups(tid, label, cat, plantilles, dades):
    """'Quin d'aquests es un X?': la bona del grup X i tres de grups diferents."""
    g = {k: [x.strip() for x in v.split(",") if x.strip()] for k, v in dades.items()}
    _tema(tid, label, cat)

    def gen(diff):
        grup = random.choice([k for k in g if k in plantilles])
        bona = random.choice(g[grup])
        altres = [x for k, xs in g.items() if k != grup for x in xs]
        return _q(plantilles[grup], bona, random.sample(altres, 6))
    _GEN[tid] = gen
    return g


def generat(tid, label, cat):
    """Decorador per als temes que es generen amb codi."""
    _tema(tid, label, cat)

    def dec(f):
        _GEN[tid] = f
        return f
    return dec


# ======================================================================== MATES
# Els que fan servir dades de app.py (es generen alla)
for _tid, _label in (("sumes", "➕ SUMES"), ("restes", "➖ RESTES"), ("taules", "✖️ TAULES"),
                     ("calcul", "💡 CÀLCUL MENTAL")):
    _tema(_tid, _label, "mates")


@generat("dobles", "👯 DOBLES I MEITATS", "mates")
def _dobles(diff):
    hi = {"Fàcil": 10, "Normal": 25, "Difícil": 50}[diff]
    if random.random() < 0.5:
        n = random.randint(1, hi)
        bona, text = 2 * n, f"Quin és el doble {de_num(n)}?"
    else:
        n = 2 * random.randint(1, hi)
        bona, text = n // 2, f"Quina és la meitat {de_num(n)}?"
    return _q(text, str(bona), [str(v) for v in _enganyoses_num(bona, (1, 2, 10), 0)] + [str(n)])


_COSES = "🍎 ⭐ 🐞 🎈 🐟 🌸 🚗 🍓 🐥 ⚽".split()


@generat("comptar", "🍎 COMPTAR", "mates")
def _comptar(diff):
    lo, hi = {"Fàcil": (2, 10), "Normal": (6, 15), "Difícil": (11, 20)}[diff]
    n = random.randint(lo, hi)
    e = random.choice(_COSES)
    files = [e * min(5, n - i) for i in range(0, n, 5)]       # de cinc en cinc: es compta millor
    return _q("Quants n'hi ha?", str(n), [str(v) for v in _enganyoses_num(n, (1, 2), 1)],
              "<br>".join(files))


@generat("mesgran", "🔝 EL MÉS GRAN I EL MÉS PETIT", "mates")
def _mesgran(diff):
    hi = {"Fàcil": 20, "Normal": 100, "Difícil": 1000}[diff]
    nums = random.sample(range(0, hi + 1), 4)
    if random.random() < 0.5:
        return _q("Quin és el número més gran?", str(max(nums)), [str(v) for v in nums if v != max(nums)])
    return _q("Quin és el número més petit?", str(min(nums)), [str(v) for v in nums if v != min(nums)])


@generat("abansdespres", "↔️ ABANS I DESPRÉS", "mates")
def _abans(diff):
    hi = {"Fàcil": 20, "Normal": 100, "Difícil": 1000}[diff]
    pas = 10 if diff == "Difícil" and random.random() < 0.4 else 1
    n = random.randint(pas, hi - pas)
    if diff == "Difícil" and pas == 1:
        n = random.choice([v for v in range(10, hi - 1) if v % 10 in (0, 9)])   # els que costen: 199, 300...
    if random.random() < 0.5:
        bona, text = n + pas, (f"Quin número va just després {del_num(n)}?" if pas == 1
                               else f"Quant fa {n} + 10?")
    else:
        bona, text = n - pas, (f"Quin número va just abans {del_num(n)}?" if pas == 1
                               else f"Quant fa {n} − 10?")
    return _q(text, str(bona), [str(v) for v in _enganyoses_num(bona, (1, 2, 10, 11), 0) if v != n])


@generat("desenes", "🔟 DESENES I UNITATS", "mates")
def _desenes(diff):
    if diff == "Difícil" and random.random() < 0.5:
        n = random.randint(101, 999)
        c, d, u = n // 100, n // 10 % 10, n % 10
        quina, bona = random.choice([("centenes", c), ("desenes", d), ("unitats", u)])
        falses = [c, d, u, (bona + 1) % 10, (bona - 1) % 10, (bona + 5) % 10, (bona + 3) % 10]
    else:
        n = random.randint(11 if diff == "Fàcil" else 21, 49 if diff == "Fàcil" else 99)
        d, u = n // 10, n % 10
        quina, bona = random.choice([("desenes", d), ("unitats", u)])
        falses = [d, u, (bona + 1) % 10, (bona - 1) % 10, (bona + 5) % 10, (bona + 3) % 10]
    return _q(f"Quina xifra hi ha a les {quina} {del_num(n)}?", str(bona), [str(v) for v in falses if v != bona])


_MONEDES = {"Fàcil": [100, 200], "Normal": [10, 20, 50], "Difícil": [10, 20, 50, 100, 200]}


def _euros(c):
    if c % 100 == 0:
        return f"{c // 100} €"
    if c < 100:
        return f"{c} cèntims"
    return f"{c // 100},{c % 100:02d} €"


@generat("monedes", "🪙 MONEDES I EUROS", "mates")
def _monedes(diff):
    m = [random.choice(_MONEDES[diff]) for _ in range(random.randint(2, 4 if diff != "Fàcil" else 3))]
    total = sum(m)
    text = "Quants diners són?  " + " + ".join(_euros(x) for x in m)
    pas = 100 if diff == "Fàcil" else 10
    falses = [total + pas, total - pas, total + 2 * pas, total - 2 * pas, total + 5 * pas]
    return _q(text, _euros(total), [_euros(v) for v in falses if v > 0])


banc("formes", "🔺 FORMES", "mates", """
🔺 | Quants costats té un triangle? | 3 | 4 | 5 | 2
🟥 | Quants costats té un quadrat? | 4 | 3 | 5 | 6
⬜ | Quina forma té tots quatre costats iguals? | Quadrat | Triangle | Cercle | Rectangle
⚪ | Quina forma és rodona i no té cantonades? | Cercle | Quadrat | Triangle | Rectangle
🔺 | Quina forma té tres costats? | Triangle | Quadrat | Cercle | Hexàgon
| Quants costats té un rectangle? | 4 | 3 | 5 | 6
| Quantes puntes (vèrtexs) té un triangle? | 3 | 4 | 2 | 5
🎲 | Quina forma té un dau? | Cub | Esfera | Piràmide | Cilindre
⚽ | Quina forma té una pilota? | Esfera | Cub | Piràmide | Cilindre
🥫 | Quina forma té una llauna? | Cilindre | Cub | Esfera | Piràmide
*| Quants costats té un pentàgon? | 5 | 6 | 4 | 8
*| Quants costats té un hexàgon? | 6 | 5 | 8 | 4
*🛑 | Quants costats té un octàgon (com el senyal de STOP)? | 8 | 6 | 10 | 5
*🎲 | Quantes cares té un cub? | 6 | 4 | 8 | 12
*| Quina figura té 5 costats? | Pentàgon | Hexàgon | Quadrat | Octàgon
**| Quantes arestes té un cub? | 12 | 6 | 8 | 10
**| Quants vèrtexs té un cub? | 8 | 6 | 12 | 4
**🐝 | Quina forma tenen les cel·les d'una bresca d'abelles? | Hexàgon | Quadrat | Cercle | Triangle
""")


@generat("series", "🔢 SÈRIES DE NÚMEROS", "mates")
def _series(diff):
    pas = random.choice({"Fàcil": (1, 2, 10), "Normal": (2, 5, 10, 3), "Difícil": (3, 4, 5, 25, 50)}[diff])
    hi = {"Fàcil": 20, "Normal": 100, "Difícil": 500}[diff]
    baixa = diff != "Fàcil" and random.random() < 0.3
    ini = random.randint(5 * pas, hi) if baixa else random.randint(0, max(1, hi - 5 * pas))
    s = [ini - i * pas for i in range(5)] if baixa else [ini + i * pas for i in range(5)]
    if min(s) < 0:
        return _series(diff)
    bona = s[4]
    return _q("Quin número ve després?  " + ", ".join(str(v) for v in s[:4]) + ", ...", str(bona),
              [str(v) for v in _enganyoses_num(bona, (1, pas + 1, 2 * pas, 10), 0) if v != s[3]])


_PROBLEMES = [
    ("Un esquirol té {a} avellanes i en troba {b} més. Quantes en té ara?", "+", "🐿️"),
    ("En un arbre hi ha {a} ocells i se'n van {b}. Quants en queden?", "-", "🐦"),
    ("Hi ha {a} pomes a la cistella i ens en mengem {b}. Quantes en queden?", "-", "🍎"),
    ("Una gallina pon {a} ous i una altra en pon {b}. Quants ous hi ha en total?", "+", "🥚"),
    ("Un tren té {a} vagons i n'hi enganxen {b} més. Quants vagons té ara?", "+", "🚂"),
    ("Tenim {a} globus i se n'escapen {b}. Quants globus ens queden?", "-", "🎈"),
    ("A la bassa hi ha {a} granotes i n'hi salten {b} més. Quantes granotes hi ha?", "+", "🐸"),
    ("Una abella visita {a} flors al matí i {b} a la tarda. Quantes flors ha visitat?", "+", "🐝"),
]
_PROBLEMES_X = [
    ("Hi ha {a} cotxes i cada cotxe té 4 rodes. Quantes rodes hi ha?", 4, "🚗"),
    ("Tenim {a} bosses amb 5 caramels cadascuna. Quants caramels hi ha?", 5, "🍬"),
    ("Hi ha {a} gats i cada gat té 4 potes. Quantes potes hi ha?", 4, "🐱"),
    ("{a} amics porten 2 mitjons cadascun. Quants mitjons hi ha?", 2, "🧦"),
    ("Hi ha {a} capses amb 10 llapis cadascuna. Quants llapis hi ha?", 10, "✏️"),
]


@generat("problemes", "🐿️ PROBLEMES", "mates")
def _problemes(diff):
    if diff == "Difícil" and random.random() < 0.5:
        t, f, e = random.choice(_PROBLEMES_X)
        a = random.randint(2, 9)
        bona, text = a * f, t.format(a=a)
    else:
        t, op, e = random.choice(_PROBLEMES)
        hi = {"Fàcil": 10, "Normal": 20, "Difícil": 50}[diff]
        a = random.randint(3, hi)
        b = random.randint(2, a - 1) if op == "-" else random.randint(2, hi)   # amb 1, el verb aniria en singular
        bona, text = (a + b if op == "+" else a - b), t.format(a=a, b=b)
    return _q(text, str(bona), [str(v) for v in _enganyoses_num(bona, (1, 2, 10), 0)], e)


@generat("parells", "⚖️ PARELLS I SENARS", "mates")
def _parells(diff):
    hi = {"Fàcil": 20, "Normal": 100, "Difícil": 1000}[diff]
    vol = random.choice(["parell", "senar"])
    bons = [v for v in range(1, hi + 1) if (v % 2 == 0) == (vol == "parell")]
    dolents = [v for v in range(1, hi + 1) if (v % 2 == 0) != (vol == "parell")]
    return _q(f"Quin d'aquests números és {vol}?", str(random.choice(bons)),
              [str(v) for v in random.sample(dolents, 5)])


# ===================================================================== LLENGUA
_tema("lletra", "🔤 LLETRA QUE FALTA", "llengua")

taula("contraris", "🔄 CONTRARIS", "llengua", "Quin és el contrari {clau}?", """
| alt | baix
| baix | alt
| gran | petit
| petit | gran
| calent | fred
| fred | calent
| ple | buit
| ràpid | lent
| dia | nit
| obert | tancat
| net | brut
| llarg | curt
| content | trist
| dins | fora
| amunt | avall
| davant | darrere
| entrar | sortir
| pujar | baixar
| riure | plorar
| guanyar | perdre
| encendre | apagar
| sec | mullat
*| dur | tou
*| fort | feble
*| clar | fosc
*| nou | vell
*| gruixut | prim
*| començar | acabar
*| primer | últim
**| a prop | lluny
**| molt | poc
**| sempre | mai
**| algú | ningú
""", amb_de=True)

banc("sillabes", "👏 SÍL·LABES", "llengua", """
☀️ | Quantes síl·labes té SOL? | 1 | 2 | 3 | 4
🐱 | Quantes síl·labes té GAT? | 1 | 2 | 3 | 4
🍞 | Quantes síl·labes té PA? | 1 | 2 | 3 | 4
🚆 | Quantes síl·labes té TREN? | 1 | 2 | 3 | 4
🌸 | Quantes síl·labes té FLOR? | 1 | 2 | 3 | 4
🏠 | Quantes síl·labes té CA-SA? | 2 | 1 | 3 | 4
🍎 | Quantes síl·labes té PO-MA? | 2 | 1 | 3 | 4
🌙 | Quantes síl·labes té LLU-NA? | 2 | 1 | 3 | 4
📖 | Quantes síl·labes té LLI-BRE? | 2 | 1 | 3 | 4
🚗 | Quantes síl·labes té CO-TXE? | 2 | 1 | 3 | 4
⚽ | Quantes síl·labes té PI-LO-TA? | 3 | 2 | 4 | 1
👟 | Quantes síl·labes té SA-BA-TA? | 3 | 2 | 4 | 1
🐌 | Quantes síl·labes té CA-RA-GOL? | 3 | 2 | 4 | 1
🐜 | Quantes síl·labes té FOR-MI-GA? | 3 | 2 | 4 | 1
🦒 | Quantes síl·labes té GI-RA-FA? | 3 | 2 | 4 | 1
🦋 | Quantes síl·labes té PA-PA-LLO-NA? | 4 | 3 | 5 | 2
🍫 | Quantes síl·labes té XO-CO-LA-TA? | 4 | 3 | 5 | 2
🚲 | Quantes síl·labes té BI-CI-CLE-TA? | 4 | 3 | 5 | 2
*🐶 | Quantes síl·labes té GOS? | 1 | 2 | 3 | 4
*🐘 | Quantes síl·labes té ELEFANT? | 3 | 2 | 4 | 5
*🐝 | Quantes síl·labes té ABELLA? | 3 | 2 | 4 | 1
*🦘 | Quantes síl·labes té CANGUR? | 2 | 1 | 3 | 4
*🐬 | Quantes síl·labes té DOFÍ? | 2 | 1 | 3 | 4
*🐊 | Quantes síl·labes té COCODRIL? | 3 | 2 | 4 | 5
*🍅 | Quantes síl·labes té TOMÀQUET? | 3 | 2 | 4 | 5
**🦕 | Quantes síl·labes té DINOSAURE? | 4 | 3 | 5 | 6
**💻 | Quantes síl·labes té ORDINADOR? | 4 | 3 | 5 | 6
**🚁 | Quantes síl·labes té HELICÒPTER? | 4 | 3 | 5 | 6
**🦛 | Quantes síl·labes té HIPOPÒTAM? | 4 | 3 | 5 | 6
**➗ | Quantes síl·labes té MATEMÀTIQUES? | 5 | 4 | 6 | 3
""")

banc("rimes", "🎵 RIMES", "llengua", """
🐱 | Quina paraula rima amb GAT? | plat | gos | casa | lluna | flor
🍎 | Quina paraula rima amb POMA? | goma | pera | sol | tren | gat
⚽ | Quina paraula rima amb PILOTA? | gota | pilot | casa | nen | mar
🌸 | Quina paraula rima amb FLOR? | cor | fulla | gat | taula | peix
📋 | Quina paraula rima amb TAULA? | paraula | cadira | llit | sol | pa
🦶 | Quina paraula rima amb PEU? | neu | mà | cap | nas | gat
🐋 | Quina paraula rima amb BALENA? | arena | peix | mar | sol | dofí
🍪 | Quina paraula rima amb GALETA? | maleta | pastís | llet | pa | sucre
🚚 | Quina paraula rima amb CAMIÓ? | lleó | cotxe | tren | moto | casa
🐜 | Quina paraula rima amb FORMIGA? | amiga | abella | mosca | cuc | flor
🏰 | Quina paraula rima amb CASTELL? | ocell | rei | torre | porta | mur
🥔 | Quina paraula rima amb PATATA? | sabata | pastanaga | col | ou | pa
🐉 | Quina paraula rima amb DRAC? | sac | foc | cova | ala | rei
🛏️ | Quina paraula rima amb LLIT? | dit | coixí | son | llençol | manta
🌙 | Quina paraula rima amb LLUNA? | una | estrella | sol | cel | nit
*🐭 | Quina paraula rima amb RATOLÍ? | camí | formatge | gat | cua | forat
*🍫 | Quina paraula rima amb XOCOLATA? | rata | dolç | pastís | llet | sucre
*🎨 | Quina paraula rima amb PINZELL? | vermell | pintura | paper | color | dibuix
""")

banc("plurals", "👥 PLURALS", "llengua", """
🐱 | Quin és el plural de GAT? | gats | gates | gatos | gatons
🏠 | Quin és el plural de CASA? | cases | casas | casos | casens
🍎 | Quin és el plural de POMA? | pomes | pomas | pomos | pomens
📖 | Quin és el plural de LLIBRE? | llibres | llibros | llibrees | llibrens
🌳 | Quin és el plural d'ARBRE? | arbres | arbros | arbrees | arbrens
🌹 | Quin és el plural de ROSA? | roses | rosas | rosos | rosens
👦 | Quin és el plural de NOI? | nois | noies | noios | noiens
🐟 | Quin és el plural de PEIX? | peixos | peixs | peixes | peixens
🐶 | Quin és el plural de GOS? | gossos | goss | goses | gosens
✋ | Quin és el plural de MÀ? | mans | màs | mas | manes
🍞 | Quin és el plural de PA? | pans | pas | panes | paos
🦁 | Quin és el plural de LLEÓ? | lleons | lleós | lleones | lleo
*🐄 | Quin és el plural de VACA? | vaques | vacas | vaces | vacos
*🏖️ | Quin és el plural de PLATJA? | platges | platjas | platjes | platjos
*👭 | Quin és el plural d'AMIGA? | amigues | amigas | amiges | amigos
*🚚 | Quin és el plural de CAMIÓ? | camions | camiós | camiones | camió
*✏️ | Quin és el plural de LLAPIS? | llapis | llapissos | llapisos | llapises
**👃 | Quin és el plural de NAS? | nassos | nass | nases | nasos
**💪 | Quin és el plural de BRAÇ? | braços | braçs | braces | braçes
**⌚ | Quin és el plural de RELLOTGE? | rellotges | rellotjes | rellotgos | rellotgis
""")

taula("femeni", "👫 MASCULÍ I FEMENÍ", "llengua", "Quin és el femení {clau}?", """
👦 | nen | nena
🐱 | gat | gata
👦 | noi | noia
👴 | avi | àvia
👨 | pare | mare
👨 | home | dona
🤴 | rei | reina
🤴 | príncep | princesa
🐓 | gall | gallina
🦁 | lleó | lleona
🧑‍🏫 | mestre | mestra
🧒 | amic | amiga
🐰 | conill | conilla
👦 | germà | germana
👦 | fill | filla
*🐴 | cavall | euga
*🐂 | bou | vaca
*🎭 | actor | actriu
*🐯 | tigre | tigressa
*👨 | oncle | tia
**🐷 | porc | truja
**🦆 | ànec | ànega
**🗿 | gegant | geganta
""", amb_de=True)

_ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_PARAULES_ABC = ("ABELLA BALENA CASA DRAC ELEFANT FLOR GAT HIVERN ILLA JOC KIWI LLUNA MAR NEU OCELL PEIX "
                 "QUADRE RATOLÍ SOL TREN UNICORN VACA XOCOLATA ZEBRA").split()


@generat("abecedari", "🔠 ABECEDARI", "llengua")
def _abecedari(diff):
    if diff == "Difícil" and random.random() < 0.5:
        ws = random.sample(_PARAULES_ABC, 4)
        return _q("Quina paraula va primer en el diccionari?", min(ws), [w for w in ws if w != min(ws)])
    i = random.randint(1, 24)
    if random.random() < 0.5 or diff == "Fàcil":
        bona, text, mostra = _ABC[i + 1], "Quina lletra va després?", f"{_ABC[i]} → ?"
    else:
        bona, text, mostra = _ABC[i - 1], "Quina lletra va abans?", f"? → {_ABC[i]}"
    falses = [_ABC[j] for j in (i - 2, i + 2, i + 3, i - 3, i) if 0 <= j < 26 and _ABC[j] != bona]
    return _q(text, bona, falses, mostra)


# ====================================================================== ANGLÈS
taula("en_colors", "🎨 COLORS EN ANGLÈS", "angles", "Com es diu aquest color en anglès?", """
🔴 | | red
🔵 | | blue
🟢 | | green
🟡 | | yellow
🟠 | | orange
🟣 | | purple
⚫ | | black
⚪ | | white
🟤 | | brown
""")

taula("en_colors_b", "", "", "Com es diu «{clau}» en català?", """
| red | vermell
| blue | blau
| green | verd
| yellow | groc
| orange | taronja
| purple | lila
| black | negre
| white | blanc
| brown | marró
| pink | rosa
| grey | gris
""")
TEMES.pop()

taula("en_animals", "🐶 ANIMALS EN ANGLÈS", "angles", "Com es diu aquest animal en anglès?", """
🐶 | | dog
🐱 | | cat
🐭 | | mouse
🐰 | | rabbit
🐮 | | cow
🐷 | | pig
🐴 | | horse
🐑 | | sheep
🐔 | | chicken
🦆 | | duck
🐸 | | frog
🐘 | | elephant
🦁 | | lion
*🐯 | | tiger
*🐵 | | monkey
*🐻 | | bear
*🦒 | | giraffe
*🐍 | | snake
*🦋 | | butterfly
*🐝 | | bee
*🐧 | | penguin
**🦊 | | fox
**🐺 | | wolf
**🐙 | | octopus
**🦈 | | shark
**🐳 | | whale
**🐢 | | turtle
""")

_EN_NUM = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
           "fifteen sixteen seventeen eighteen nineteen twenty").split()
_EN_DESENES = {30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty",
               90: "ninety", 100: "one hundred"}


@generat("en_numeros", "🔢 NÚMEROS EN ANGLÈS", "angles")
def _en_numeros(diff):
    if diff == "Difícil" and random.random() < 0.5:
        n = random.choice(list(_EN_DESENES))
        opcions = {**_EN_DESENES, 13: "thirteen", 14: "fourteen", 15: "fifteen", 20: "twenty"}
    else:
        n = random.randint(0 if diff != "Fàcil" else 1, 10 if diff == "Fàcil" else 20)
        opcions = dict(enumerate(_EN_NUM))
    bona = opcions[n]
    prop = [k for k in sorted(opcions, key=lambda k: abs(k - n) + random.random() * 3) if k != n]
    if random.random() < 0.5:
        return _q("Com es diu aquest número en anglès?", bona, [opcions[k] for k in prop], str(n))
    return _q(f"Quin número és «{bona}»?", str(n), [str(k) for k in prop])


taula("en_menjar", "🍓 MENJAR EN ANGLÈS", "angles", "Com es diu en anglès?", """
🍎 | | apple
🍌 | | banana
🍊 | | orange
🍓 | | strawberry
🍇 | | grapes
🍐 | | pear
🍉 | | watermelon
🍋 | | lemon
🍞 | | bread
🧀 | | cheese
🥚 | | egg
🥛 | | milk
🍪 | | biscuit
🍰 | | cake
*🍕 | | pizza
*🍦 | | ice cream
*🥕 | | carrot
*🍅 | | tomato
*🥔 | | potato
*🍒 | | cherries
**🧈 | | butter
**🍯 | | honey
**🥒 | | cucumber
""")

taula("en_cos", "👃 EL COS EN ANGLÈS", "angles", "Com es diu en anglès?", """
👁️ | | eye
👂 | | ear
👃 | | nose
👄 | | mouth
✋ | | hand
🦶 | | foot
🦵 | | leg
💪 | | arm
🦷 | | tooth
👅 | | tongue
*🧠 | | brain
*🫀 | | heart
**🦴 | | bone
""")

# ====================================================================== NATURA
_tema("animals", "🐾 QUIN ANIMAL ÉS?", "natura")

taula("sons", "🔊 SONS DELS ANIMALS", "natura", "Què fa aquest animal?", """
🐶 | | borda
🐱 | | miola
🐮 | | mugeix
🐑 | | bela
🦁 | | rugeix
🐓 | | canta
🐸 | | rauca
*🐴 | | renilla
*🐝 | | brunzeix
*🐍 | | xiula
""")

banc("cases", "🏡 ON VIUEN ELS ANIMALS?", "natura", """
🐝 | On viuen les abelles? | al rusc | a la quadra | al cau | al galliner
🐦 | On fan la casa molts ocells? | al niu | al rusc | al formiguer | a la quadra
🐰 | On s'amaga el conill de bosc? | al cau | al galliner | al rusc | a la teranyina
🐜 | On viuen les formigues? | al formiguer | al rusc | al galliner | a la quadra
🐔 | On dormen les gallines de la granja? | al galliner | al rusc | al formiguer | al cau
🐴 | On dormen els cavalls de la granja? | a la quadra | al rusc | al formiguer | al niu
🕷️ | Què teixeix l'aranya per caçar insectes? | una teranyina | un niu | un rusc | un cau
🐌 | Què porta el cargol a l'esquena? | la closca | un niu | un rusc | una motxilla
🐬 | On viuen els dofins? | al mar | al desert | a la muntanya | a la bassa
🐫 | On viuen els camells? | al desert | al mar | al Pol Nord | a la bassa
🐸 | On viuen les granotes? | a la bassa | al desert | al mar | al rusc
🐒 | On viuen molts micos? | a la selva | al Pol Nord | al desert | al mar
🐟 | On viuen els peixos? | a l'aigua | a l'aire | als arbres | sota terra
*🦁 | On viuen els lleons? | a la sabana | al Pol Nord | al mar | a la bassa
*🐻‍❄️ | On viu l'ós polar? | al Pol Nord | al desert | a la selva | a la sabana
*🐿️ | On viuen els esquirols? | als arbres | al mar | al desert | a la bassa
**🦇 | On dormen els ratpenats durant el dia? | penjats a les coves | dins el rusc | al fons del mar | al galliner
**🐻 | On passa l'hivern l'ós bru? | dormint en una cova | a la platja | dins un rusc | al fons del mar
""")

grups("menjars", "🥕 QUÈ MENGEN?", "natura", {
    "herbivor": "Quin d'aquests animals només menja plantes?",
    "carnivor": "Quin d'aquests animals menja carn?",
}, {
    "herbivor": "🐄 vaca, 🐴 cavall, 🐰 conill, 🦒 girafa, 🐘 elefant, 🐑 ovella, 🦓 zebra, 🐐 cabra",
    "carnivor": "🦁 lleó, 🐯 tigre, 🐺 llop, 🦈 tauró, 🐊 cocodril, 🦅 àliga",
})
banc("menjars_b", "", "", """
| Com es diu un animal que només menja plantes? | herbívor | carnívor | omnívor | insectívor
| Com es diu un animal que només menja carn? | carnívor | herbívor | omnívor | vegetal
""")
TEMES.pop()        # 'menjars_b' no es un tema a part: es barreja dins 'menjars'

taula("cries", "🐣 LES CRIES", "natura", "Com es diu la cria d'aquest animal?", """
🐄 | | vedell
🐶 | | cadell
🐴 | | poltre
🐑 | | xai
🐔 | | pollet
🐷 | | garrí
🐸 | | capgròs
🦋 | | eruga
🐐 | | cabrit
🦆 | | aneguet
""")

grups("grups", "🧬 MAMÍFERS, OCELLS, PEIXOS...", "natura", {
    "mamifer": "Quin d'aquests animals és un mamífer?",
    "ocell": "Quin d'aquests animals és un ocell?",
    "peix": "Quin d'aquests animals és un peix?",
    "reptil": "Quin d'aquests animals és un rèptil?",
    "insecte": "Quin d'aquests animals és un insecte?",
}, {
    "mamifer": "🐳 balena, 🐬 dofí, 🦇 ratpenat, 🐶 gos, 🐄 vaca, 🐘 elefant, 🦁 lleó, 🐰 conill",
    "ocell": "🐧 pingüí, 🐔 gallina, 🦅 àliga, 🦉 mussol, 🦜 lloro, 🦆 ànec, 🕊️ colom",
    "peix": "🦈 tauró, 🐟 salmó, 🐠 peix pallasso, 🐡 peix globus",
    "reptil": "🐍 serp, 🐢 tortuga, 🐊 cocodril, 🦎 sargantana",
    "amfibi": "🐸 granota",
    "insecte": "🐝 abella, 🐜 formiga, 🦋 papallona, 🐞 marieta, 🦗 grill",
})

banc("potes", "🦵 QUANTES POTES?", "natura", """
🕷️ | Quantes potes té una aranya? | 8 | 6 | 4 | 10
🐜 | Quantes potes té una formiga? | 6 | 8 | 4 | 2
🐶 | Quantes potes té un gos? | 4 | 2 | 6 | 3
🐔 | Quantes potes té una gallina? | 2 | 4 | 3 | 6
🐍 | Quantes potes té una serp? | 0 | 2 | 4 | 8
🐴 | Quantes potes té un cavall? | 4 | 2 | 6 | 8
🦆 | Quantes potes té un ànec? | 2 | 4 | 3 | 6
🐝 | Quantes potes té una abella? | 6 | 4 | 8 | 2
🐞 | Quantes potes té una marieta? | 6 | 4 | 8 | 2
🐱 | Quantes potes té un gat? | 4 | 3 | 6 | 2
🐌 | Quantes potes té un cargol? | 0 | 2 | 4 | 6
🐙 | Quants braços té un pop? | 8 | 6 | 10 | 4
*⭐ | Quants braços té normalment una estrella de mar? | 5 | 4 | 6 | 8
*🦋 | Quantes potes té una papallona? | 6 | 4 | 8 | 2
**🦀 | Quantes potes té un cranc (comptant les pinces)? | 10 | 8 | 6 | 12
**| Quantes potes tenen tots els insectes? | 6 | 8 | 4 | 10
""")

banc("plantes", "🌱 LES PLANTES", "natura", """
🌱 | Quina part de la planta és sota terra? | l'arrel | la flor | la fulla | el fruit
🌱 | Què necessita una planta per viure? | aigua i llum | xocolata | fum | sal
🌰 | Què surt d'una llavor si la plantem? | una planta | un ou | una pedra | un cuc
🍃 | De quin color són normalment les fulles? | verd | blau | negre | rosa
🍎 | Com es diu l'arbre que fa pomes? | pomera | taronger | olivera | pi
🍊 | Com es diu l'arbre que fa taronges? | taronger | pomera | olivera | castanyer
🫒 | Com es diu l'arbre que fa olives? | olivera | pomera | taronger | pi
🌰 | Com es diu l'arbre que fa castanyes? | castanyer | olivera | pomera | taronger
🌲 | Quin arbre fa pinyes? | el pi | la pomera | el taronger | l'olivera
🐝 | Quin insecte porta el pol·len d'una flor a una altra? | l'abella | la formiga | el mosquit | la puça
🌻 | Cap a on es gira el gira-sol? | cap al sol | cap a la lluna | cap a terra | cap al mar
*🌱 | Per on puja l'aigua des de l'arrel fins a les fulles? | per la tija | per la flor | pel fruit | per l'aire
*🍂 | Què fan molts arbres a la tardor? | perden les fulles | fan flors | creixen molt | es moren
*🌳 | Com es diu l'arbre que fa glans? | alzina | pomera | taronger | pi
**🍃 | Com es diu el procés en què les plantes fan el seu aliment amb la llum? | fotosíntesi | digestió | respiració | evaporació
**🌵 | Quina planta guarda aigua i té punxes? | el cactus | la rosa | el pi | la margarida
""")

banc("dinosaures", "🦖 DINOSAURES", "natura", """
🦖 | Què menjava el tiranosaure (T-Rex)? | carn | plantes | fruita | fulles
🦕 | Quin dinosaure tenia el coll molt llarg? | diplodoc | tiranosaure | triceratops | velociraptor
🦕 | Què menjava el diplodoc? | plantes | carn | peixos | insectes
🦖 | Com tenia els braços el T-Rex? | molt curts | molt llargs | amb ales | amb ventoses
🦴 | Com sabem que hi va haver dinosaures? | pels fòssils | per les fotos | pels vídeos | pels llibres de l'època
⏳ | Quan van viure els dinosaures? | fa milions d'anys | fa 100 anys | fa 1.000 anys | l'any passat
🥚 | Com neixien les cries dels dinosaures? | d'un ou | d'una llavor | d'una flor | d'una pedra
👨 | Les persones van viure al mateix temps que els dinosaures? | no | sí | només els nens | només a Catalunya
| Quin dinosaure tenia tres banyes al cap? | triceratops | diplodoc | tiranosaure | estegosaure
*| Quin dinosaure tenia plaques a l'esquena? | estegosaure | triceratops | diplodoc | tiranosaure
*☄️ | Què creuen els científics que va fer desaparèixer els dinosaures? | un meteorit | un gat gegant | la pluja | el fred d'un hivern
*🐦 | Quins animals d'avui són parents dels dinosaures? | els ocells | els gats | els peixos | els cucs
**👩‍🔬 | Com es diu qui estudia els fòssils? | paleontòleg o paleontòloga | astronauta | dentista | arquitecte o arquitecta
**| Quin dinosaure tenia una bola a la cua per defensar-se? | anquilosaure | diplodoc | velociraptor | triceratops
""")

# =========================================================== COS, SALUT I ESPAI
banc("cos", "🫀 EL COS HUMÀ", "ciencia", """
👁️ | Amb què veiem? | amb els ulls | amb el nas | amb les orelles | amb la llengua
👂 | Amb què sentim els sons? | amb les orelles | amb els ulls | amb el nas | amb les mans
👃 | Amb què olorem? | amb el nas | amb les orelles | amb els ulls | amb la llengua
👅 | Amb què notem el gust del menjar? | amb la llengua | amb el nas | amb els ulls | amb les orelles
🖐️ | Quants dits té una mà? | 5 | 4 | 6 | 10
🖐️ | Quants dits tenim en total a les dues mans? | 10 | 5 | 8 | 20
🫀 | Quin òrgan bombeja la sang? | el cor | l'estómac | el pulmó | el cervell
🫁 | Amb què respirem? | amb els pulmons | amb el cor | amb l'estómac | amb els ossos
🧠 | Amb què pensem? | amb el cervell | amb el cor | amb l'estómac | amb els peus
🍽️ | On va el menjar quan l'empassem? | a l'estómac | al cervell | al cor | als pulmons
🦵 | Com es diu l'articulació del mig de la cama? | el genoll | el colze | el canell | el turmell
💪 | Com es diu l'articulació del mig del braç? | el colze | el genoll | el turmell | el coll
*✋ | Amb quina part del cos sentim si una cosa és suau o rasposa? | amb la pell | amb les orelles | amb el nas | amb els cabells
*| Quants sentits tenim? | 5 | 3 | 4 | 7
*🦴 | Com es diu el conjunt de tots els ossos? | esquelet | múscul | pell | sang
**🦷 | Quantes dents de llet té un infant? | 20 | 32 | 10 | 28
**🧠 | Quin os protegeix el cervell? | el crani | la costella | el fèmur | la columna
**🦴 | Quin és l'os més llarg del cos? | el fèmur | el crani | la costella | el colze
""")

banc("salut", "🍏 SALUT I HÀBITS", "ciencia", """
🪥 | Quan ens hem de rentar les dents? | després de menjar | un cop a la setmana | mai | només per Nadal
🧼 | Què hem de fer abans de menjar? | rentar-nos les mans | córrer | cridar | dormir
💧 | Què és millor beure quan tenim set? | aigua | refresc | cafè | suc de caramel
😴 | Quantes hores ha de dormir un infant de la teva edat? | unes 10 hores | 3 hores | 20 hores | 1 hora
🧴 | Què ens protegeix del sol a la platja? | la crema solar | la sorra | el gelat | l'aigua del mar
🤧 | Quan esternudem, amb què ens hem de tapar? | amb el colze | amb la mà de l'amic | amb res | amb el plat
🍎 | Quin d'aquests aliments és més sa per berenar? | una fruita | uns caramels | unes patates fregides | un refresc
🥛 | Quin aliment ens ajuda a tenir els ossos forts? | la llet | els caramels | les llaminadures | el refresc
🏃 | Què és bo fer cada dia? | moure'ns i jugar | estar quiet tot el dia | menjar dolços | dormir 2 hores
🥦 | Quin d'aquests aliments és una verdura? | bròquil | poma | pa | formatge
*🩺 | Qui ens cura quan estem malalts? | el metge o la metgessa | el carter | el bomber | el forner
*| Quants gots d'aigua és bo beure cada dia (més o menys)? | uns 6 | cap | 1 | 30
*🍬 | Què fa mal a les dents si en mengem molt? | el sucre | l'aigua | la poma | la pastanaga
**🦠 | Com es diuen els éssers molt petits que ens poden posar malalts? | microbis | dinosaures | planetes | vitamines
""")

banc("espai", "🚀 L'ESPAI", "ciencia", """
🌍 | Com es diu el planeta on vivim? | la Terra | Mart | la Lluna | el Sol
☀️ | Què és el Sol? | una estrella | un planeta | una lluna | un núvol
🪐 | Quin planeta té uns anells molt famosos? | Saturn | Mart | la Terra | Mercuri
🔴 | Quin planeta és de color vermell? | Mart | Júpiter | Saturn | la Terra
🌙 | Què gira al voltant de la Terra? | la Lluna | el Sol | Mart | Júpiter
👩‍🚀 | Com es diu qui viatja a l'espai? | astronauta | submarinista | bomber | pilot de carreres
🌗 | Per què hi ha dia i nit? | perquè la Terra gira | perquè el Sol s'apaga | perquè plou | perquè la Lluna tapa el Sol
⭐ | Què veiem al cel de nit que brilla molt lluny? | estrelles | núvols | ocells | arcs de Sant Martí
🔭 | Amb què podem mirar les estrelles de més a prop? | amb un telescopi | amb un microscopi | amb unes ulleres de sol | amb una lupa
*🪐 | Quin és el planeta més gran? | Júpiter | la Terra | Mart | Mercuri
*☀️ | Quin planeta és el més proper al Sol? | Mercuri | Neptú | la Terra | Júpiter
*| Quants planetes té el sistema solar? | 8 | 9 | 5 | 12
*🌍 | Quant triga la Terra a fer una volta sencera al Sol? | un any | un dia | una setmana | una hora
*🧑‍🚀 | Qui va ser la primera persona que va trepitjar la Lluna? | Neil Armstrong | Cristòfor Colom | Albert Einstein | Isaac Newton
**🚀 | En quin any es va arribar per primer cop a la Lluna? | 1969 | 1492 | 2000 | 1900
**| Quin és el planeta més llunyà del Sol? | Neptú | Mart | Saturn | Venus
**🔥 | Quin és el planeta més calent? | Venus | Mercuri | Mart | Júpiter
**🌌 | Com es diu la galàxia on vivim? | la Via Làctia | Andròmeda | el Gran Carro | la Lluna
""")

# ====================================================================== EL MÓN
taula("banderes", "🏳️ BANDERES", "mon", "De quin país és aquesta bandera?", """
🇪🇸 | | Espanya
🇫🇷 | | França
🇮🇹 | | Itàlia
🇵🇹 | | Portugal
🇩🇪 | | Alemanya
🇬🇧 | | Regne Unit
🇺🇸 | | Estats Units
🇯🇵 | | Japó
🇧🇷 | | Brasil
🇨🇳 | | Xina
🇦🇩 | | Andorra
🇲🇽 | | Mèxic
*🇦🇷 | | Argentina
*🇨🇦 | | Canadà
*🇬🇷 | | Grècia
*🇨🇭 | | Suïssa
*🇮🇪 | | Irlanda
*🇲🇦 | | Marroc
*🇦🇺 | | Austràlia
*🇸🇪 | | Suècia
**🇳🇴 | | Noruega
**🇳🇱 | | Països Baixos
**🇧🇪 | | Bèlgica
**🇮🇳 | | Índia
**🇪🇬 | | Egipte
**🇰🇷 | | Corea del Sud
**🇺🇦 | | Ucraïna
**🇨🇴 | | Colòmbia
**🇯🇲 | | Jamaica
""")

taula("capitals", "🏙️ CAPITALS", "mon", "Quina és la capital {clau}?", """
🇪🇸 | d'Espanya | Madrid
🇫🇷 | de França | París
🇮🇹 | d'Itàlia | Roma
🇵🇹 | de Portugal | Lisboa
🇩🇪 | d'Alemanya | Berlín
🇬🇧 | del Regne Unit | Londres
🇬🇷 | de Grècia | Atenes
🇯🇵 | del Japó | Tòquio
🇦🇩 | d'Andorra | Andorra la Vella
🇮🇪 | d'Irlanda | Dublín
🇦🇹 | d'Àustria | Viena
🇪🇬 | d'Egipte | el Caire
*🇨🇳 | de la Xina | Pequín
*🇷🇺 | de Rússia | Moscou
*🇦🇷 | de l'Argentina | Buenos Aires
*🇲🇽 | de Mèxic | Ciutat de Mèxic
*🇳🇱 | dels Països Baixos | Amsterdam
*🇧🇪 | de Bèlgica | Brussel·les
*🇸🇪 | de Suècia | Estocolm
*🇳🇴 | de Noruega | Oslo
*🇩🇰 | de Dinamarca | Copenhaguen
*🇵🇱 | de Polònia | Varsòvia
*🇭🇺 | d'Hongria | Budapest
*🇵🇪 | del Perú | Lima
**🇺🇸 | dels Estats Units | Washington
**🇨🇦 | del Canadà | Ottawa
**🇧🇷 | del Brasil | Brasília
**🇦🇺 | d'Austràlia | Canberra
**🇨🇭 | de Suïssa | Berna
**🇲🇦 | del Marroc | Rabat
**🇹🇷 | de Turquia | Ankara
**🇨🇴 | de Colòmbia | Bogotà
""")

taula("continents", "🗺️ CONTINENTS", "mon", "En quin continent és {clau}?", """
🇫🇷 | França | Europa
🇮🇹 | Itàlia | Europa
🇩🇪 | Alemanya | Europa
🇪🇸 | Espanya | Europa
🇯🇵 | el Japó | Àsia
🇨🇳 | la Xina | Àsia
🇮🇳 | l'Índia | Àsia
🇰🇷 | Corea del Sud | Àsia
🇪🇬 | Egipte | Àfrica
🇲🇦 | el Marroc | Àfrica
🇰🇪 | Kenya | Àfrica
🇿🇦 | Sud-àfrica | Àfrica
🇺🇸 | els Estats Units | Amèrica
🇧🇷 | el Brasil | Amèrica
🇲🇽 | Mèxic | Amèrica
🇦🇷 | l'Argentina | Amèrica
🇦🇺 | Austràlia | Oceania
🇳🇿 | Nova Zelanda | Oceania
""")

banc("planeta", "🌊 MARS, MUNTANYES I DESERTS", "mon", """
🌊 | Quin mar banya Catalunya? | el Mediterrani | el Cantàbric | el mar Roig | el mar Negre
🌍 | En quin continent vivim? | Europa | Àfrica | Àsia | Oceania
🏔️ | Quina és la muntanya més alta del món? | l'Everest | el Montseny | el Tibidabo | el Teide
🐫 | Com es diu el desert gran del nord d'Àfrica? | el Sàhara | l'Antàrtida | l'Amazones | els Alps
🧊 | Quin continent és ple de gel, al Pol Sud? | l'Antàrtida | Àfrica | Europa | Amèrica
🌊 | Quin és l'oceà més gran? | el Pacífic | l'Atlàntic | l'Índic | el Mediterrani
💧 | L'aigua del mar és... | salada | dolça | ensucrada | de colors
🌋 | Com es diu la muntanya que treu lava? | volcà | turó | penya-segat | cova
🏝️ | Com es diu un tros de terra envoltat d'aigua per tots costats? | illa | península | muntanya | desert
*🌳 | Quina és la selva més gran del món? | l'Amazònia | el Sàhara | el Montseny | els Pirineus
*🏔️ | Quines muntanyes separen Espanya de França? | els Pirineus | els Alps | els Andes | l'Himàlaia
*🌊 | Quin oceà hi ha entre Europa i Amèrica? | l'Atlàntic | el Pacífic | l'Índic | l'Àrtic
**🌋 | Com es diu el volcà més alt d'Espanya, a Tenerife? | el Teide | l'Etna | el Vesuvi | el Montseny
**🏞️ | Com es diu un tros de terra envoltat d'aigua per tots els costats menys un? | península | illa | golf | cap
""")

banc("monuments", "🗽 MONUMENTS DEL MÓN", "mon", """
| En quina ciutat hi ha la Torre Eiffel? | París | Roma | Londres | Madrid
🗽 | En quina ciutat hi ha l'Estàtua de la Llibertat? | Nova York | París | Londres | Roma
| En quina ciutat hi ha el Coliseu? | Roma | Atenes | París | Barcelona
| En quin país hi ha les grans piràmides de Gizeh? | Egipte | Mèxic | Itàlia | França
| En quina ciutat hi ha el Big Ben? | Londres | París | Berlín | Roma
| En quin país hi ha la Gran Muralla? | la Xina | el Japó | l'Índia | Egipte
| En quina ciutat hi ha la Sagrada Família? | Barcelona | Madrid | París | Girona
| En quin país hi ha la torre inclinada de Pisa? | Itàlia | França | Grècia | Portugal
🗻 | En quin país hi ha el mont Fuji? | el Japó | la Xina | Itàlia | Suïssa
*| En quin país hi ha el Taj Mahal? | l'Índia | Egipte | la Xina | el Marroc
*| En quina ciutat hi ha l'Alhambra? | Granada | Sevilla | Barcelona | Lisboa
*| En quina ciutat hi ha l'Acròpoli? | Atenes | Roma | Istanbul | París
**| En quin país hi ha Machu Picchu? | el Perú | Mèxic | el Brasil | Egipte
**| En quin país hi ha l'Òpera de Sydney? | Austràlia | els Estats Units | el Canadà | Anglaterra
""")

banc("animals_mon", "🦘 ANIMALS DEL MÓN", "mon", """
🦘 | On viuen els cangurs en llibertat? | a Austràlia | a Catalunya | al Pol Nord | al Japó
🐼 | De quin país és l'ós panda? | de la Xina | d'Austràlia | del Brasil | d'Egipte
🐻‍❄️ | On viu l'ós polar? | a l'Àrtic | al desert | a la selva | a Austràlia
🦁 | En quin continent viuen els lleons en llibertat? | Àfrica | Europa | Oceania | l'Antàrtida
🦒 | En quin continent viuen les girafes? | Àfrica | Europa | Amèrica | Oceania
🐧 | On viu el pingüí emperador? | a l'Antàrtida | al Sàhara | a la selva | al Pol Nord
🐫 | On viuen els camells? | al desert | al Pol Nord | al fons del mar | a la selva
🐨 | On viuen els coales? | a Austràlia | a la Xina | a l'Àfrica | a Europa
*🐯 | En quin continent viuen els tigres en llibertat? | Àsia | Àfrica | Europa | Oceania
*🦙 | On viuen les llames? | a les muntanyes d'Amèrica del Sud | al Pol Nord | a Austràlia | al Sàhara
*🦓 | En quin continent viuen les zebres? | Àfrica | Àsia | Europa | Oceania
**🐘 | Quins elefants tenen les orelles més grans? | els africans | els asiàtics | els europeus | tots igual
""")

# ================================================================== CATALUNYA
banc("catalunya", "🌹 CATALUNYA", "catalunya", """
🏙️ | Quina és la capital de Catalunya? | Barcelona | Girona | Lleida | Tarragona
🗺️ | Quantes províncies té Catalunya? | 4 | 2 | 5 | 10
🌊 | Quin mar banya Catalunya? | el Mediterrani | l'Atlàntic | el Cantàbric | el Pacífic
⛰️ | Quina muntanya té un monestir molt famós i forma de serra? | Montserrat | el Tibidabo | el Turó de l'Home | l'Everest
🏔️ | Quines muntanyes hi ha al nord de Catalunya? | els Pirineus | els Alps | els Andes | l'Himàlaia
💬 | Quina és la llengua pròpia de Catalunya? | el català | el francès | l'anglès | l'italià
🌹 | Quina flor es regala per Sant Jordi? | la rosa | la margarida | el gira-sol | la tulipa
🟨 | De quins colors és la senyera? | groc i vermell | blau i blanc | verd i blanc | negre i groc
🇫🇷 | Amb quin país fa frontera Catalunya pel nord? | França | Portugal | Itàlia | Alemanya
🇦🇩 | Quin país petit hi ha als Pirineus, entre Catalunya i França? | Andorra | Mònaco | Suïssa | Portugal
*🟥 | Quantes barres vermelles té la senyera? | 4 | 3 | 5 | 2
*🏔️ | Quina és la muntanya més alta de Catalunya? | la Pica d'Estats | Montserrat | el Tibidabo | el Montseny
*🏛️ | Quina d'aquestes ciutats és capital de província? | Girona | Sabadell | Reus | Figueres
**🌊 | Quin riu acaba en un gran delta al sud de Catalunya? | l'Ebre | el Llobregat | el Ter | el Besòs
**🏞️ | Quin riu passa per Lleida? | el Segre | el Besòs | el Llobregat | el Ter
""")

banc("tradicions", "🎉 FESTES I TRADICIONS", "catalunya", """
🌹 | Quin dia és Sant Jordi? | el 23 d'abril | el 25 de desembre | l'11 de setembre | el 6 de gener
📚 | Què es regala per Sant Jordi? | llibres i roses | ous de xocolata | castanyes | torrons
🌰 | Què mengem per la Castanyada? | castanyes i panellets | mona | coca de Sant Joan | torrons
👑 | Qui porta regals el 6 de gener? | els Reis d'Orient | el Tió | Sant Jordi | el drac
🪵 | Què fem amb el Tió per Nadal? | el fem cagar | el pintem de blau | el llencem al mar | el fem volar
🧒 | Com es diu el nen o la nena que puja a dalt de tot del castell? | l'enxaneta | el gegant | el capgròs | el drac
💃 | Quina dansa es balla en rotllana agafats de les mans? | la sardana | el flamenc | el tango | la jota
🔥 | Què es fa la nit de Sant Joan? | revetlla amb fogueres i coca | regalar roses | menjar castanyes | caçar ous
🎭 | Què fem per Carnestoltes? | ens disfressem | mengem castanyes | regalem roses | fem cagar el Tió
🥚 | Què regala el padrí o la padrina per Pasqua? | la mona | el tió | una rosa | panellets
🐉 | Segons la llegenda, què va matar Sant Jordi? | un drac | un lleó | un llop | un gegant
🌹 | Segons la llegenda, què va néixer de la sang del drac? | una rosa | un arbre | un riu | una estrella
*📅 | Quin dia és la Diada de Catalunya? | l'11 de setembre | el 23 d'abril | el 24 de juny | el 6 de gener
*🗿 | Com es diuen les figures molt altes que ballen a les festes? | gegants | enxanetes | castellers | diables
*😈 | Com es diu la festa amb diables, foc i petards? | correfoc | sardana | castanyada | mona
*🎄 | Quina figura fa caca al pessebre català? | el caganer | el pastor | l'àngel | el bou
**🎶 | Com es diu el grup de músics que toca sardanes? | la cobla | l'orquestra | la banda | el cor
**🏰 | Com es diuen els que fan castells humans? | castellers | geganters | diables | caganers
""")

banc("gaudi", "🦎 BARCELONA I GAUDÍ", "catalunya", """
⛪ | Qui va fer la Sagrada Família? | Antoni Gaudí | Joan Miró | Pablo Picasso | Salvador Dalí
🦎 | Quin animal de trencadís de colors hi ha a l'escala del Park Güell? | un drac | un lleó | un cavall | un elefant
🎡 | Quina muntanya de Barcelona té un parc d'atraccions? | el Tibidabo | Montjuïc | Montserrat | el Montseny
🚶 | Quin passeig famós va de la plaça de Catalunya fins al port? | la Rambla | la Diagonal | la Gran Via | el Paral·lel
🏖️ | Com es diu la platja més coneguda de Barcelona? | la Barceloneta | Sitges | Salou | la Concha
🗿 | Quina estàtua hi ha al final de la Rambla, mirant al mar? | Colom | Sant Jordi | Gaudí | Picasso
🏞️ | Quin parc de Gaudí té bancs de trencadís? | el Park Güell | la Ciutadella | Montjuïc | el Retiro
*🧩 | Com es diu el mosaic fet amb trossets de rajola trencada? | trencadís | puzle | fresc | vitrall
*🐉 | Quina casa de Gaudí té una teulada que sembla l'esquena d'un drac? | la Casa Batlló | la Pedrera | la Casa Amatller | el Palau Güell
*🏛️ | Com es diu també la Casa Milà, de Gaudí? | la Pedrera | la Casa Batlló | la Sagrada Família | el Park Güell
*🏟️ | On es van fer els Jocs Olímpics de 1992? | a Barcelona | a Madrid | a París | a Roma
**🏗️ | Quin ofici tenia Gaudí? | arquitecte | pintor | músic | metge
""")

# ================================================================== HISTÒRIA
banc("prehistoria", "🦣 PREHISTÒRIA", "historia", """
🕳️ | On vivien sovint les persones de la prehistòria? | a les coves | en pisos | en castells | en vaixells
🔥 | Quin descobriment els va ajudar a cuinar i escalfar-se? | el foc | l'electricitat | la televisió | el gas
🪨 | Amb què feien les primeres eines? | amb pedra | amb plàstic | amb ferro | amb vidre
🦣 | Quin animal gran i pelut caçaven? | el mamut | el dinosaure | el drac | el cangur
🎨 | Com es diuen les pintures a les parets de les coves? | pintures rupestres | grafits | murals de colors | vitralls
🐺 | Quin va ser el primer animal que van domesticar? | el gos | el gat | el cavall | la gallina
🍖 | Com aconseguien menjar al principi? | caçant i recollint fruits | anant al súper | per encàrrec | amb restaurants
*🚶 | Com es diuen les persones que no viuen sempre al mateix lloc? | nòmades | pagesos | reis | soldats
*🌾 | Què van començar a fer quan es van quedar a viure en un lloc? | conrear la terra | fer cotxes | escriure llibres | anar a l'escola
*🗿 | Com es diuen les grans pedres posades dretes de la prehistòria? | menhirs | piràmides | castells | gratacels
**🦴 | Com es diu l'època en què les eines eren de pedra? | Edat de Pedra | Edat Mitjana | Edat Moderna | Edat del Ferro
""")

banc("egipte", "🐫 L'ANTIC EGIPTE", "historia", """
🔺 | On són les piràmides més famoses? | a Egipte | a França | a Catalunya | al Japó
👑 | Com es deien els reis de l'antic Egipte? | faraons | emperadors | cavallers | presidents
🌊 | Quin riu travessa Egipte? | el Nil | l'Ebre | el Sena | el Tàmesi
🧻 | Com es diu un cos embolicat amb benes per conservar-lo? | mòmia | fòssil | estàtua | esquelet
| Com es diu l'escriptura egípcia feta amb dibuixos? | jeroglífics | números romans | lletres llatines | emojis
🦁 | Quin monument té cos de lleó i cap de persona? | l'esfinx | la Torre Eiffel | el Coliseu | la Sagrada Família
🔺 | Per a què servien les piràmides? | eren les tombes dels faraons | eren escoles | eren mercats | eren estacions de tren
*🐱 | Quin animal era sagrat per als egipcis? | el gat | el porc | el cangur | el ratolí
*📜 | Sobre què escrivien els egipcis? | papir | plàstic | tauletes digitals | cartró
**👦 | Quin faraó, que va ser rei de molt jove, és molt famós? | Tutankamon | Juli Cèsar | Napoleó | Carlemany
""")

banc("roma", "🏛️ ELS ROMANS", "historia", """
🗣️ | Quina llengua parlaven els romans? | el llatí | el català | l'anglès | l'àrab
🏛️ | Quina ciutat era la capital de l'Imperi Romà? | Roma | Barcelona | Atenes | París
⚔️ | On lluitaven els gladiadors? | a l'amfiteatre | a l'església | a la platja | a l'escola
💧 | Què construïen els romans per portar aigua a les ciutats? | aqüeductes | gratacels | ponts penjants | piscines
🛡️ | Com es deien els soldats romans? | legionaris | cavallers | mosqueters | samurais
🏟️ | On anaven a veure curses de carros? | al circ | al cinema | a la piscina | al teatre de titelles
🔢 | Com es diuen els números que feien servir els romans? | números romans | números àrabs | números xinesos | números egipcis
*🏙️ | Com es deia Tarragona en temps dels romans? | Tàrraco | Barcino | Roma | Empúries
*🏙️ | Com es deia Barcelona en temps dels romans? | Barcino | Tàrraco | Gerunda | Ilerda
*👑 | Qui manava a l'Imperi Romà? | l'emperador | el faraó | el president | l'alcalde
*💬 | Quina d'aquestes llengües ve del llatí? | el català | l'anglès | l'alemany | el xinès
**🔟 | Quin número és X en números romans? | 10 | 5 | 1 | 100
**🖐️ | Quin número és V en números romans? | 5 | 10 | 50 | 1
""")

banc("edatmitjana", "🏰 CASTELLS I CAVALLERS", "historia", """
🏰 | On vivien els reis i els senyors a l'edat mitjana? | en castells | en coves | en pisos | en tendes
🧱 | Què envoltava i protegia les ciutats i els castells? | les muralles | les tanques de fusta | els rius de llet | els jardins
🌉 | Com es diu el pont del castell que es puja i es baixa? | pont llevadís | pont penjant | pont romà | pont de ferro
🛡️ | Què duia un cavaller per protegir-se? | armadura | banyador | pijama | disfressa de pallasso
🐴 | Quin animal muntaven els cavallers? | el cavall | el camell | l'elefant | el ruc
📜 | Qui copiava els llibres a mà als monestirs? | els monjos | els cavallers | els pirates | els reis
🌊 | Com es diu el clot ple d'aigua al voltant d'un castell? | fossat | piscina | font | pou
*⚔️ | Com es diu la competició de cavallers a cavall? | torneig | partit | cursa de carros | olimpíada
*🌾 | Qui treballava la terra per al senyor? | els pagesos | els cavallers | els monjos | els reis
*🐉 | Quin cavaller de la llegenda va matar un drac? | Sant Jordi | el rei Artur | Robin Hood | Guifré el Pilós
**🟨 | Segons la llegenda, què explica la història de Guifré el Pilós? | l'origen de les quatre barres | com es va fer la Sagrada Família | com es va descobrir Amèrica | qui va inventar la roda
""")

banc("invents", "💡 INVENTS", "historia", """
| Quin invent molt antic serveix per moure els carros? | la roda | el telèfon | l'ordinador | la bombeta
📞 | Quin invent ens permet parlar amb algú que és lluny? | el telèfon | la roda | el rellotge | la cullera
💡 | Quin invent ens dona llum a casa amb electricitat? | la bombeta | l'espelma | el foc | el mirall
🔬 | Amb quin aparell veiem coses molt i molt petites? | el microscopi | el telescopi | la ràdio | la tele
✈️ | Quin invent ens permet volar? | l'avió | el submarí | el tren | la bicicleta
🧭 | Quin aparell indica sempre el nord? | la brúixola | el rellotge | el termòmetre | la calculadora
*🖨️ | Qui va inventar la impremta per fer llibres més de pressa? | Gutenberg | Edison | Einstein | Gaudí
*✈️ | Qui van fer volar el primer avió amb motor? | els germans Wright | els germans Grimm | els germans Marx | els germans Lumière
*🌊 | Quin invent va fer el català Narcís Monturiol? | un submarí | un avió | un telèfon | una bicicleta
*💡 | Qui va fer famosa la bombeta elèctrica? | Thomas Edison | Leonardo da Vinci | Isaac Newton | Cristòfor Colom
**📞 | Qui va patentar el telèfon? | Graham Bell | Thomas Edison | Marie Curie | Albert Einstein
**💊 | Qui va descobrir la penicil·lina, un medicament contra els microbis? | Alexander Fleming | Albert Einstein | Isaac Newton | Charles Darwin
""")

banc("personatges", "⭐ PERSONATGES DE LA HISTÒRIA", "historia", """
⛵ | Qui va arribar a Amèrica amb tres vaixells l'any 1492? | Cristòfor Colom | Neil Armstrong | Marco Polo | Napoleó
🧑‍🚀 | Qui va ser el primer a trepitjar la Lluna? | Neil Armstrong | Cristòfor Colom | Albert Einstein | Galileu
🖼️ | Qui va pintar la Gioconda? | Leonardo da Vinci | Picasso | Dalí | Miró
🎼 | Quin músic va començar a compondre quan era un nen molt petit? | Mozart | Picasso | Colom | Einstein
🍎 | Segons la història, a qui li va caure una poma al cap i va pensar en la gravetat? | Isaac Newton | Albert Einstein | Thomas Edison | Leonardo da Vinci
*👩‍🔬 | Quina científica va guanyar dos premis Nobel? | Marie Curie | Frida Kahlo | Amelia Earhart | Florence Nightingale
*🧠 | Quin científic té una foto molt famosa traient la llengua? | Albert Einstein | Isaac Newton | Charles Darwin | Galileu
*🎻 | Quin instrument tocava el català Pau Casals? | el violoncel | el piano | la guitarra | la trompeta
*🐢 | Quin científic va estudiar com canvien els animals amb el temps, a les illes Galápagos? | Charles Darwin | Isaac Newton | Thomas Edison | Graham Bell
**✈️ | Quina aviadora va creuar sola l'oceà Atlàntic? | Amelia Earhart | Marie Curie | Frida Kahlo | Rosalía de Castro
**📖 | Qui va escriure el Quixot? | Miguel de Cervantes | William Shakespeare | Jacint Verdaguer | Mercè Rodoreda
**🔭 | Quin científic italià va mirar el cel amb un telescopi fa més de 400 anys? | Galileu | Colom | Leonardo da Vinci | Mozart
""")

# ============================================================== ART, MÚSICA, ESPORT
banc("art", "🖼️ ART I PINTORS", "cultura", """
🖼️ | Qui va pintar la Gioconda? | Leonardo da Vinci | Joan Miró | Salvador Dalí | Pablo Picasso
🌻 | Quin pintor va pintar uns gira-sols molt famosos? | Van Gogh | Picasso | Miró | Velázquez
👨‍🎨 | Quin pintor català tenia un bigoti llarg i retorçat? | Salvador Dalí | Joan Miró | Antoni Gaudí | Pablo Picasso
⭐ | Quin pintor català pintava estrelles, llunes i colors vius? | Joan Miró | Salvador Dalí | Van Gogh | Velázquez
🎨 | On barregem els colors per pintar? | a la paleta | a la cullera | al raspall de dents | a la sabata
*🐴 | Qui va pintar el Guernica? | Pablo Picasso | Joan Miró | Salvador Dalí | Van Gogh
*🌌 | Quin pintor va pintar «La nit estelada»? | Van Gogh | Picasso | Dalí | Miró
*🕰️ | Quin pintor va pintar rellotges tous que es fonen? | Salvador Dalí | Joan Miró | Van Gogh | Leonardo da Vinci
*👸 | Qui va pintar «Les Menines»? | Velázquez | Picasso | Dalí | Miró
**| Quin pintor va pintar moltes vegades els nenúfars del seu jardí? | Claude Monet | Pablo Picasso | Salvador Dalí | Velázquez
**🗿 | Com es diu l'art de fer figures amb pedra, fang o metall? | escultura | pintura | música | dansa
""")

taula("instruments", "🎸 INSTRUMENTS", "cultura", "Quin instrument és?", """
🎸 | | guitarra
🎹 | | piano
🥁 | | tambor
🎺 | | trompeta
🎻 | | violí
🎷 | | saxòfon
🪗 | | acordió
🪕 | | banjo
""")
banc("instruments_b", "", "", """
🎻 | Quin instrument es toca amb un arc? | violí | trompeta | tambor | piano
🥁 | Quin instrument es toca picant amb baquetes? | tambor | violí | flauta | guitarra
🎸 | Quantes cordes té una guitarra normal? | 6 | 4 | 10 | 2
🎺 | Quin d'aquests instruments es toca bufant? | trompeta | piano | violí | tambor
*🎹 | Quin instrument té tecles blanques i negres? | piano | guitarra | trompeta | arpa
**🎹 | Quantes tecles té un piano normal? | 88 | 20 | 50 | 120
""")
TEMES.pop()

banc("esports", "⚽ ESPORTS", "cultura", """
⚽ | Quants jugadors té un equip de futbol de grans al camp? | 11 | 9 | 15 | 20
🏀 | Quants jugadors té un equip de bàsquet de grans a la pista? | 5 | 11 | 8 | 2
🏑 | Amb què es juga a l'hoquei sobre herba? | amb un estic i una bola | amb una raqueta | amb les mans | amb un bat
🎾 | Quin esport es juga amb raqueta i una pilota groga? | tennis | futbol | natació | rugbi
🏊 | Quin esport es fa a la piscina? | natació | ciclisme | esquí | golf
⛷️ | Quin esport es fa a la neu? | esquí | surf | tennis | natació
🚴 | Quin esport es fa en bicicleta? | ciclisme | atletisme | natació | judo
🏉 | Quin esport es juga amb una pilota amb forma d'ou? | rugbi | futbol | bàsquet | handbol
*🥇 | Cada quants anys es fan els Jocs Olímpics d'estiu? | 4 | 1 | 2 | 10
*⭕ | Quants anells té el símbol dels Jocs Olímpics? | 5 | 3 | 4 | 6
*🏟️ | On es van fer els Jocs Olímpics de 1992? | a Barcelona | a Madrid | a Londres | a París
**🏐 | Quants jugadors té un equip de voleibol de grans a la pista? | 6 | 3 | 11 | 9
**⛳ | En quin esport s'intenta fer el «forat en un cop»? | golf | tennis | bàsquet | hoquei
""")

# ================================================================ VIDA DIÀRIA
banc("oficis", "👩‍🚒 OFICIS", "vida", """
🚒 | Qui apaga els focs? | bomber o bombera | metge o metgessa | cuiner o cuinera | pilot
🩺 | Qui ens cura quan estem malalts? | metge o metgessa | bomber o bombera | fuster o fustera | carter o cartera
🐶 | Qui cura els animals malalts? | veterinari o veterinària | dentista | forner o fornera | pilot
🧑‍🏫 | Qui ens ensenya a l'escola? | mestre o mestra | cuiner o cuinera | policia | carter o cartera
👩‍🍳 | Qui cuina en un restaurant? | cuiner o cuinera | mestre o mestra | dentista | bomber o bombera
💇 | Qui ens talla els cabells? | perruquer o perruquera | dentista | forner o fornera | pagès o pagesa
🦷 | Qui ens cuida les dents? | dentista | perruquer o perruquera | carter o cartera | mestre o mestra
✉️ | Qui porta les cartes a casa? | carter o cartera | pilot | metge o metgessa | cuiner o cuinera
✈️ | Qui condueix un avió? | pilot | astronauta | fuster o fustera | mestre o mestra
🥖 | Qui fa el pa? | forner o fornera | fuster o fustera | pagès o pagesa | dentista
🌾 | Qui cultiva la terra? | pagès o pagesa | pilot | perruquer o perruquera | carter o cartera
🪚 | Qui fa mobles de fusta? | fuster o fustera | forner o fornera | dentista | pilot
*🚀 | Qui viatja a l'espai? | astronauta | submarinista | pilot | bomber o bombera
*🏗️ | Qui dibuixa els plànols de les cases? | arquitecte o arquitecta | pagès o pagesa | forner o fornera | carter o cartera
""")

taula("transports", "🚗 TRANSPORTS", "vida", "Quin transport és?", """
🚗 | | cotxe
🚌 | | autobús
🚂 | | tren
🚲 | | bicicleta
✈️ | | avió
🚁 | | helicòpter
🚢 | | vaixell
🚀 | | coet
🚜 | | tractor
🛴 | | patinet
🏍️ | | moto
🚑 | | ambulància
*🚠 | | telefèric
*🛶 | | canoa
""")
grups("transports_g", "", "", {
    "aire": "Quin d'aquests transports va per l'aire?",
    "aigua": "Quin d'aquests transports va per l'aigua?",
}, {
    "aire": "✈️ avió, 🚁 helicòpter, 🚀 coet",
    "aigua": "🚢 vaixell, ⛵ veler, 🛶 canoa, 🚤 llanxa",
    "terra": "🚗 cotxe, 🚌 autobús, 🚂 tren, 🚲 bicicleta, 🚜 tractor, 🏍️ moto",
})
TEMES.pop()

banc("reciclatge", "♻️ RECICLATGE", "vida", """
🧴 | On llencem una ampolla de plàstic? | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd | 🟤 contenidor marró
🥫 | On llencem una llauna? | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd | 🟤 contenidor marró
🧃 | On llencem un bric de suc? | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd | 🟤 contenidor marró
📦 | On llencem una capsa de cartró? | 🔵 contenidor blau | 🟡 contenidor groc | 🟢 contenidor verd | 🟤 contenidor marró
📰 | On llencem un diari vell? | 🔵 contenidor blau | 🟡 contenidor groc | 🟢 contenidor verd | 🟤 contenidor marró
🍾 | On llencem una ampolla de vidre? | 🟢 contenidor verd | 🟡 contenidor groc | 🔵 contenidor blau | 🟤 contenidor marró
| On llencem un pot de vidre buit? | 🟢 contenidor verd | 🟡 contenidor groc | 🔵 contenidor blau | 🟤 contenidor marró
🍌 | On llencem la pell d'un plàtan? | 🟤 contenidor marró | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd
🥚 | On llencem les closques d'ou? | 🟤 contenidor marró | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd
🍎 | On llencem el cor d'una poma? | 🟤 contenidor marró | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd
♻️ | Què vol dir reciclar? | fer coses noves amb les velles | llençar-ho tot junt | cremar les escombraries | comprar més coses
*🔋 | On portem les piles gastades? | a un punt de recollida de piles | al contenidor groc | al contenidor marró | al vàter
*🛍️ | On llencem una bossa de patates xips buida? | 🟡 contenidor groc | 🔵 contenidor blau | 🟢 contenidor verd | 🟤 contenidor marró
**♻️ | Quines són les tres erres? | reduir, reutilitzar i reciclar | riure, ruixar i rodar | rentar, recollir i respirar | córrer, saltar i nedar
""")

banc("viaria", "🚦 SEGURETAT AL CARRER", "vida", """
🚦 | Si el semàfor dels vianants és vermell, què fem? | ens esperem | correm | passem saltant | ens asseiem al mig
🚦 | Si el semàfor dels vianants és verd, què fem? | passem mirant bé | ens esperem sempre | tornem a casa | ens estirem a terra
🦓 | Per on creuem el carrer? | pel pas de vianants | pel mig dels cotxes | per on vulguem | per sobre dels cotxes
🚗 | Què ens hem de cordar sempre al cotxe? | el cinturó | les sabates | la jaqueta | la motxilla
🚲 | Què ens hem de posar per anar en bici? | el casc | un barret de festa | unes ulleres de bussejar | un paraigua
🚶 | Per on caminem pel carrer? | per la vorera | pel mig de la carretera | per la via del tren | pel carril bici
👀 | Què fem abans de creuar el carrer? | mirar a banda i banda | tancar els ulls | córrer | mirar el mòbil
*🛑 | Què vol dir el senyal de STOP? | que cal parar del tot | que cal córrer | que es pot aparcar | que hi ha una escola
*🟠 | Què vol dir el llum taronja del semàfor? | atenció, aviat es posarà vermell | que podem córrer | que s'ha espatllat | que és de nit
*🚌 | Què fem quan baixem de l'autobús? | esperar que marxi abans de creuar | creuar per davant de seguida | córrer darrere | seure a la vorada
""")

banc("emocions", "😊 EMOCIONS", "vida", """
😀 | Quina emoció és? | alegria | tristesa | ràbia | por
😢 | Quina emoció és? | tristesa | alegria | ràbia | fàstic
😠 | Quina emoció és? | ràbia | alegria | tristesa | calma
😨 | Quina emoció és? | por | alegria | calma | fàstic
😲 | Quina emoció és? | sorpresa | tristesa | calma | fàstic
🤢 | Quina emoció és? | fàstic | alegria | calma | sorpresa
😌 | Quina emoció és? | calma | ràbia | por | fàstic
🎁 | Què sentim quan ens fan un regal que ens agrada? | alegria | tristesa | ràbia | fàstic
🧸 | Què sentim si perdem la nostra joguina preferida? | tristesa | alegria | calma | fàstic
🎨 | Què sentim si algú ens trenca el dibuix a propòsit? | ràbia | alegria | calma | fàstic
*😳 | Quina emoció és? | vergonya | ràbia | alegria | fàstic
*🤔 | Quina emoció és? | dubte | ràbia | alegria | fàstic
*🌬️ | Què ens pot ajudar quan estem molt enfadats? | respirar a poc a poc | pegar | cridar molt fort | trencar coses
""")

banc("colors", "🌈 COLORS", "vida", """
🍌 | De quin color és un plàtan madur? | groc | blau | lila | negre
❄️ | De quin color és la neu? | blanc | vermell | verd | marró
🌿 | De quin color és l'herba? | verd | groc | blau | rosa
🍓 | De quin color és una maduixa madura? | vermell | blau | verd | negre
🍫 | De quin color és la xocolata? | marró | groc | blau | verd
| De quin color és el cel en un dia de sol? | blau | verd | vermell | marró
🍊 | De quin color és una taronja? | taronja | blau | lila | gris
🎨 | Què surt si barregem blau i groc? | verd | taronja | lila | marró
🎨 | Què surt si barregem vermell i groc? | taronja | verd | lila | gris
🎨 | Què surt si barregem vermell i blau? | lila | verd | taronja | groc
*🎨 | Què surt si barregem blanc i negre? | gris | rosa | marró | blau
*🎨 | Què surt si barregem vermell i blanc? | rosa | gris | taronja | verd
*🌈 | Quants colors té l'arc de Sant Martí? | 7 | 3 | 5 | 10
**🎨 | Quins són els tres colors primaris en pintura? | vermell, groc i blau | verd, taronja i lila | blanc, negre i gris | rosa, marró i verd
""")

# ======================================================== CALENDARI I TEMPS
_DIES = "dilluns dimarts dimecres dijous divendres dissabte diumenge".split()
_MESOS = "gener febrer març abril maig juny juliol agost setembre octubre novembre desembre".split()


def _cicle(llista, diff, quin):
    n = len(llista)
    i = random.randrange(n)
    salt = random.choice([1, -1] if diff != "Difícil" else [1, -1, 2, -2])
    bona = llista[(i + salt) % n]
    if quin == "dia":
        text = {1: f"Si avui és {llista[i]}, quin dia serà demà?", -1: f"Si avui és {llista[i]}, quin dia era ahir?",
                2: f"Si avui és {llista[i]}, quin dia serà demà passat?",
                -2: f"Si avui és {llista[i]}, quin dia era abans-d'ahir?"}[salt]
    else:
        m = de(llista[i])
        text = {1: f"Quin mes va després {m}?", -1: f"Quin mes va abans {m}?",
                2: f"Quin mes és dos mesos després {m}?", -2: f"Quin mes és dos mesos abans {m}?"}[salt]
    falses = [llista[(i + s) % n] for s in (0, -salt, 2 * salt, 3, -3) if llista[(i + s) % n] != bona]
    return _q(text, bona, falses)


_DIES_B = banc("dies_b", "", "", """
📅 | Quants dies té una setmana? | 7 | 5 | 10 | 12
🎉 | Quins dies no hi ha escola normalment? | dissabte i diumenge | dilluns i dimarts | dimecres i dijous | dijous i divendres
📅 | Quin és el primer dia de la setmana a l'escola? | dilluns | diumenge | divendres | dimecres
""")
TEMES.pop()


@generat("dies", "📅 DIES DE LA SETMANA", "temps")
def _dies(diff):
    if random.random() < 0.2:
        return _GEN["dies_b"](diff)
    return _cicle(_DIES, diff, "dia")


banc("mesos_b", "", "", """
🎄 | En quin mes és Nadal? | desembre | gener | agost | abril
🌹 | En quin mes és Sant Jordi? | abril | maig | desembre | octubre
📅 | Quants mesos té un any? | 12 | 10 | 7 | 365
🎆 | Quin és el primer mes de l'any? | gener | desembre | setembre | març
🏖️ | En quin mes no hi ha escola i fa molta calor? | agost | gener | novembre | febrer
*📅 | Quants dies té un any (que no és de traspàs)? | 365 | 100 | 12 | 1.000
*⏰ | Quantes hores té un dia? | 24 | 12 | 60 | 7
*⏱️ | Quants minuts té una hora? | 60 | 100 | 24 | 30
**⏱️ | Quants segons té un minut? | 60 | 100 | 10 | 24
""")
TEMES.pop()


@generat("mesos", "🗓️ MESOS DE L'ANY", "temps")
def _mesos(diff):
    if random.random() < 0.3:
        return _GEN["mesos_b"](diff)
    return _cicle(_MESOS, diff, "mes")


# rellotges: 🕐..🕛 en punt i 🕜..🕧 i mitja
_EN_PUNT = "🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"
_I_MITJA = "🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧"


@generat("rellotge", "🕒 EL RELLOTGE", "temps")
def _rellotge(diff):
    h = random.randint(1, 12)
    mitja = diff != "Fàcil" and random.random() < 0.5
    emoji = (_I_MITJA if mitja else _EN_PUNT)[h - 1]
    bona = f"{h}:30" if mitja else f"{h}:00"
    altres = [f"{(h % 12) + 1}:00", f"{h}:30" if not mitja else f"{h}:00", f"{((h - 2) % 12) + 1}:30",
              f"{((h + 1) % 12) + 1}:00", f"{((h - 2) % 12) + 1}:00"]
    return _q("Quina hora marca el rellotge?", bona, [a for a in altres if a != bona], emoji)


banc("estacions", "🍂 LES ESTACIONS", "temps", """
🍂 | En quina estació cauen les fulles de molts arbres? | tardor | estiu | primavera | hivern
❄️ | En quina estació fa més fred? | hivern | estiu | primavera | tardor
🌸 | En quina estació surten més flors? | primavera | tardor | hivern | estiu
🏖️ | En quina estació fa més calor i anem a la platja? | estiu | hivern | tardor | primavera
🌸 | Quina estació va després de l'hivern? | primavera | estiu | tardor | hivern
🍂 | Quina estació va després de l'estiu? | tardor | primavera | hivern | estiu
❄️ | Quina estació va després de la tardor? | hivern | primavera | estiu | tardor
☀️ | Quina estació va després de la primavera? | estiu | tardor | hivern | primavera
| Quantes estacions té un any? | 4 | 2 | 6 | 12
🎄 | En quina estació és Nadal? | hivern | estiu | primavera | tardor
🌰 | En quina estació és la Castanyada? | tardor | estiu | primavera | hivern
🌹 | En quina estació és Sant Jordi? | primavera | hivern | tardor | estiu
*🔥 | En quina estació és la revetlla de Sant Joan? | estiu | hivern | tardor | primavera
""")

banc("oratge", "🌦️ QUIN TEMPS FA?", "temps", """
☀️ | Quin temps fa? | fa sol | neva | plou | hi ha boira
🌧️ | Quin temps fa? | plou | fa sol | neva | fa vent
❄️ | Quin temps fa? | neva | fa sol | fa calor | hi ha boira
⛈️ | Quin temps fa? | hi ha tempesta | fa sol | neva | hi ha boira
🌫️ | Quin temps fa? | hi ha boira | fa sol | neva | hi ha tempesta
💨 | Quin temps fa? | fa vent | neva | hi ha boira | fa calor
☁️ | Quin temps fa? | està ennuvolat | fa sol | neva | hi ha tempesta
☂️ | Què fem servir quan plou? | el paraigua | les ulleres de sol | el banyador | la crema solar
🌈 | Què pot sortir al cel quan plou i fa sol alhora? | l'arc de Sant Martí | la lluna plena | una estrella fugaç | la neu
🌡️ | Amb què mesurem si fa fred o calor? | amb el termòmetre | amb el rellotge | amb el metre | amb la balança
⚡ | Què sentim després de veure un llamp? | el tro | un ocell | la pluja de colors | el vent del sud
*💧 | En què es converteix l'aigua quan es glaça? | en gel | en vapor | en sorra | en llet
*☁️ | De què estan fets els núvols? | de gotetes d'aigua | de cotó | de fum de cotxe | de sucre
""")

# ===================================================================== LÒGICA
banc("endevinalles", "❓ ENDEVINALLES", "logica", """
| Té dents i no menja, té barba i no és home. Què és? | l'all | la pinta | el gat | la serra
| Blanc per dins, verd per fora; si no ho endevines, espera't una hora. Què és? | la pera | la síndria | la taronja | el tomàquet
| Com més en treus, més gran es fa. Què és? | un forat | un pastís | un globus | una pilota
| Té coll però no té cap. Què és? | l'ampolla | la girafa | el llapis | la sabata
| Té fulles però no és un arbre. Què és? | el llibre | la cadira | la sabata | el got
| Té agulles però no cus. Què és? | el rellotge | la cullera | la sabata | el got
| Corre i corre però no té cames. Què és? | el riu | el nen | l'atleta | la nena
| Té cap i peus però no té cos. Què és? | el llit | el got | la cadira | el sabó
| Té quatre potes però no camina. Què és? | la cadira | el gos | el cavall | la formiga
| Sempre puja i mai baixa. Què és? | l'edat | l'ascensor | el globus | l'avió
*| Com més s'asseca, més mullada està. Què és? | la tovallola | la roba | la pluja | el paraigua
*| És teu però els altres el fan servir més que tu. Què és? | el teu nom | el teu llapis | la teva bici | la teva casa
| Soc verda, salto molt i faig «rauc, rauc». Qui soc? | la granota | el gat | l'ocell | la serp
| Tinc ratlles blanques i negres i semblo un cavall. Qui soc? | la zebra | el tigre | el gos | la vaca
| Tinc una trompa molt llarga i les orelles molt grans. Qui soc? | l'elefant | la girafa | el ratolí | el lleó
| Porto la casa a l'esquena i vaig molt a poc a poc. Qui soc? | el cargol | el conill | el cavall | el gat
| Tinc el coll molt i molt llarg i menjo fulles dels arbres. Qui soc? | la girafa | l'elefant | el porc | la gallina
| Faig mel i pico si em molesten. Qui soc? | l'abella | la mosca | la formiga | la papallona
| Tinc vuit potes i faig teranyines. Qui soc? | l'aranya | la formiga | l'abella | el cargol
| De dia dormo penjat cap per avall i de nit volo. Qui soc? | el ratpenat | la gallina | el gat | el peix
| Quan plou m'obres i quan fa sol em tanques. Què soc? | el paraigua | la nevera | la sabata | el got
| Tinc dues rodes i pedals. Què soc? | la bicicleta | el cotxe | el patinet | l'autobús
| Escric però no sé llegir. Què soc? | el llapis | la goma | les tisores | el plat
| De dia escalfo i de nit no hi soc. Què soc? | el sol | la lluna | la neu | el núvol
| Surto de nit; a vegades soc rodona i a vegades em veus a mitges. Què soc? | la lluna | el sol | l'arc de Sant Martí | el núvol
| Soc blanca, caic del cel quan fa fred i amb mi fas ninots. Què soc? | la neu | la pluja | el sol | la sorra
| Tinc un barret i un sol peu, i visc al bosc. Què soc? | el bolet | el pi | la pedra | el ratolí
| Tinc llum vermella, taronja i verda, i estic al carrer. Què soc? | el semàfor | el fanal | l'arc de Sant Martí | la bombeta
| Petita com un ratolí, guardo la casa com un lleó. Què soc? | la clau | la porta | la finestra | la taula
| Sempre estic dins de casa però sempre miro al carrer. Què soc? | la finestra | el llit | la nevera | la banyera
| Quan fa sol et segueixo a tot arreu, i de nit desapareixo. Què soc? | l'ombra | el núvol | la lluna | la pluja
| Volo sense ales i ploro sense ulls. Què soc? | el núvol | l'ocell | l'avió | l'abella
| Tinc cua però no soc un animal, i volo lligat a un fil. Què soc? | l'estel | l'ocell | la pilota | el paraigua
| Tinc ble, faig llum i em fonc a poc a poc. Què soc? | l'espelma | la bombeta | la llanterna | el mirall
| Soc prima, tinc un sol ull i ajudo a cosir. Què soc? | l'agulla | les tisores | el fil | el botó
| Una caixeta blanca: tothom la sap obrir i ningú la sap tancar. Què és? | l'ou | la capsa de sabates | el llibre | la porta
| Entre dues parets blanques hi ha una flor groga. Què és? | l'ou | la casa | la poma | el plàtan
*| Tinc corona però no soc rei, tinc escates però no soc peix. Què soc? | la pinya tropical | el drac | el cocodril | la sargantana
*| Té ulls i no hi veu, té aigua i no la beu, té carn i no la menja. Què és? | el coco | el meló | la síndria | la poma
*| Pujo i baixo però no em moc de lloc. Què soc? | l'escala | l'ascensor | el globus | l'avió
*| Tinc coll i mànigues però no tinc cap ni braços. Què soc? | la camisa | la girafa | els pantalons | la sabata
*| Tinc llit però mai no dormo, i corro sense cames. Què soc? | el riu | el gat | la cadira | el llibre
*| Com més gran em faig, menys es veu. Què soc? | la foscor | la llum | el sol | el globus
*| M'has de trencar abans de fer-me servir. Què soc? | l'ou | el got | el llapis | la pilota
*| Si el comparteixes, ja no el tens. Què és? | un secret | un pastís | un llibre | una joguina
*| Tinc ulls de gat, orelles de gat i cua de gat, però no soc un gat. Què soc? | la gata | el gos | el conill | el ratolí
**| Què pesa més: un quilo de palla o un quilo de ferro? | pesen igual | el ferro | la palla | depèn del dia
**| Quants mesos de l'any tenen com a mínim 28 dies? | tots | 2 | 6 | 10
**| Tinc dents però no menjo, i tallo la fusta. Què soc? | la serra | el martell | les tisores | el clau
""")

_INTRUS = {
    "fruites": "🍎 poma, 🍐 pera, 🍌 plàtan, 🍓 maduixa, 🍊 taronja, 🍇 raïm, 🍒 cireres, 🍉 síndria",
    "animals": "🐶 gos, 🐱 gat, 🐮 vaca, 🐷 porc, 🐴 cavall, 🐰 conill, 🦁 lleó, 🐸 granota",
    "transports": "🚗 cotxe, 🚌 autobús, 🚂 tren, ✈️ avió, 🚲 bicicleta, 🚢 vaixell",
    "roba": "👕 samarreta, 👖 pantalons, 🧦 mitjons, 👟 sabates, 🧥 jaqueta, 🧢 gorra, 🧣 bufanda",
    "instruments": "🎸 guitarra, 🎹 piano, 🥁 tambor, 🎺 trompeta, 🎻 violí",
    "cos": "👁️ ull, 👂 orella, 👃 nas, ✋ mà, 🦶 peu",
    "verdures": "🥕 pastanaga, 🥦 bròquil, 🥬 enciam, 🧅 ceba, 🥒 cogombre",
    "esports": "⚽ futbol, 🏀 bàsquet, 🎾 tennis, 🏊 natació, ⛷️ esquí",
}
_INTRUS = {k: [x.strip() for x in v.split(",")] for k, v in _INTRUS.items()}
_tema("intrus", "🕵️ L'INTRÚS", "logica")


def _intrus(diff):
    a, b = random.sample(list(_INTRUS), 2)
    if {a, b} == {"fruites", "verdures"} and diff == "Fàcil":
        return _intrus(diff)            # fruita i verdura costen massa de separar a Facil
    tres = random.sample(_INTRUS[a], 3)
    bona = random.choice(_INTRUS[b])
    q = _q("Quin és l'intrús? (el que no és del mateix grup)", bona, tres)
    return q


_GEN["intrus"] = _intrus

_SERIES_DIB = ["🔴", "🔵", "🟡", "🟢", "⭐", "🌙", "🍎", "🐱", "🐶", "🌸", "⚽", "🚗"]


@generat("series_dib", "🔴🔵 SÈRIES DE DIBUIXOS", "logica")
def _series_dib(diff):
    pat = random.choice({"Fàcil": ["AB"], "Normal": ["AB", "ABB", "ABC"], "Difícil": ["ABB", "ABC", "AABB", "ABCB"]}[diff])
    simb = dict(zip("ABC", random.sample(_SERIES_DIB, 3)))
    llarg = len(pat) * 2 + random.randint(0, len(pat) - 1)
    seq = [simb[pat[i % len(pat)]] for i in range(llarg + 1)]
    bona = seq[-1]
    falses = [s for s in _SERIES_DIB if s != bona and s in simb.values()] + \
             [s for s in random.sample(_SERIES_DIB, 6) if s != bona]
    return _q("Quin dibuix ve després?", bona, falses, " ".join(seq[:-1]) + " ❓")


# ----------------------------------------------------- barreges dels temes de suport
def _amb_extra(tid, extra, prob):
    base = _GEN[tid]

    def gen(diff):
        return _GEN[extra](diff) if random.random() < prob else base(diff)
    _GEN[tid] = gen


_amb_extra("menjars", "menjars_b", 0.2)
_amb_extra("en_colors", "en_colors_b", 0.5)
_amb_extra("instruments", "instruments_b", 0.4)
_amb_extra("transports", "transports_g", 0.3)


# ---------------------------------------------------------------- API per a app.py
def pregunta(tid, diff):
    """Pregunta d'un tema d'aquest fitxer, o None si el tema es genera a app.py."""
    gen = _GEN.get(tid)
    if not gen:
        return None
    for _ in range(20):
        q = gen(diff)
        if q:
            # banderes: a Windows no hi ha emojis de bandera; la classe .bandera fa servir la font de Google
            if any("\U0001F1E6" <= ch <= "\U0001F1FF" for ch in q["emoji"]):
                q["emoji"] = f"<span class='bandera'>{q['emoji']}</span>"
            return q
    raise RuntimeError(f"El tema {tid} no dona preguntes")


def temes_de(cat):
    return [(tid, label) for tid, label, c in TEMES if c == cat]


def categoria_de(tid):
    if tid.startswith("barreja_"):
        return tid[len("barreja_"):]
    return next((c for t, _, c in TEMES if t == tid), None)
