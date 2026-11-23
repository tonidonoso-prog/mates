"""Preguntes extra del CONCURS (23 nov 2026): temes de llengua i de lògica.

EXTRA: línies noves per als temes que ja hi ha a concurs_temes.py (mateix format).
GRUPS["intrus"]: grups complets per a L'INTRÚS (inclouen els elements que ja hi havia a _INTRUS).
"""

EXTRA = {
    # taula: | clau | valor   (plantilla «Quin és el contrari {de clau}?»)
    "contraris": """
| lent | ràpid
| nit | dia
| tancat | obert
| brut | net
| curt | llarg
| trist | content
| fora | dins
| avall | amunt
| darrere | davant
| sortir | entrar
| baixar | pujar
| plorar | riure
| perdre | guanyar
| apagar | encendre
| mullat | sec
| buit | ple
| vell | nou
| bo | dolent
| dolent | bo
| bonic | lleig
| lleig | bonic
| ric | pobre
| pobre | ric
| comprar | vendre
| vendre | comprar
| anar | venir
| venir | anar
| estiu | hivern
| hivern | estiu
| dreta | esquerra
| esquerra | dreta
| abans | després
| després | abans
| sí | no
| no | sí
| despert | adormit
| adormit | despert
| parlar | callar
| callar | parlar
| fàcil | difícil
| omplir | buidar
| buidar | omplir
| ahir | demà
| demà | ahir
| barat | car
| car | barat
| cru | cuit
| cuit | cru
| igual | diferent
| diferent | igual
*| feble | fort
*| fosc | clar
*| prim | gruixut
*| acabar | començar
*| últim | primer
*| lluny | a prop
*| poc | molt
*| mai | sempre
*| ningú | algú
*| soroll | silenci
*| silenci | soroll
*| valent | poruc
*| poruc | valent
*| recordar | oblidar
*| oblidar | recordar
*| veritat | mentida
*| mentida | veritat
*| tot | res
*| res | tot
*| dolç | salat
*| salat | dolç
*| pregunta | resposta
*| resposta | pregunta
*| entrada | sortida
*| sortida | entrada
*| nord | sud
*| sud | nord
*| sumar | restar
*| estret | ample
**| est | oest
**| oest | est
**| aparèixer | desaparèixer
**| desaparèixer | aparèixer
**| lligar | deslligar
**| deslligar | lligar
**| preguntar | respondre
**| respondre | preguntar
**| empènyer | estirar
**| alegria | tristesa
**| tristesa | alegria
**| asseure's | aixecar-se
**| apropar-se | allunyar-se
**| allunyar-se | apropar-se
**| agradable | desagradable
**| possible | impossible
**| ordenat | desordenat
**| mascle | femella
**| femella | mascle
**| pujada | baixada
**| baixada | pujada
**| mullar | eixugar
**| eixugar | mullar
""",

    # taula: | clau | valor   (plantilla «Quin és el femení {de clau}?»)
    "femeni": """
| gos | gossa
| llop | lloba
| cosí | cosina
| senyor | senyora
| veí | veïna
| company | companya
| pintor | pintora
| director | directora
| cuiner | cuinera
| forner | fornera
| bomber | bombera
| infermer | infermera
| cambrer | cambrera
| jugador | jugadora
| alumne | alumna
| professor | professora
| ballarí | ballarina
| campió | campiona
| pastisser | pastissera
| perruquer | perruquera
| pescador | pescadora
| escriptor | escriptora
| conductor | conductora
*| metge | metgessa
*| alcalde | alcaldessa
*| poeta | poetessa
*| emperador | emperadriu
*| nebot | neboda
*| nuvi | núvia
*| besavi | besàvia
*| pagès | pagesa
*| toro | vaca
*| colom | coloma
*| mul | mula
*| cunyat | cunyada
*| sogre | sogra
**| jutge | jutgessa
**| sastre | sastressa
**| comte | comtessa
**| gendre | nora
**| ase | somera
**| boc | cabra
**🐻 | os | ossa
**| fillol | fillola
""",

    "plurals": """
🚗 | Quin és el plural de COTXE? | cotxes | cotxos | cotxis | cotxens
📋 | Quin és el plural de TAULA? | taules | taulas | taulos | taulens
🪑 | Quin és el plural de CADIRA? | cadires | cadiras | cadiros | cadirens
🌸 | Quin és el plural de FLOR? | flors | flores | florsos | flos
🌙 | Quin és el plural de LLUNA? | llunes | llunas | llunos | llunens
🐦 | Quin és el plural d'OCELL? | ocells | ocelles | ocellos | ocellsos
🚪 | Quin és el plural de PORTA? | portes | portas | portos | portens
👟 | Quin és el plural de SABATA? | sabates | sabatas | sabatos | sabatens
🍪 | Quin és el plural de GALETA? | galetes | galetas | galetos | galetens
⭐ | Quin és el plural d'ESTRELLA? | estrelles | estrellas | estrellos | estrellens
🐝 | Quin és el plural d'ABELLA? | abelles | abellas | abellos | abellens
👀 | Quin és el plural d'ULL? | ulls | ulles | ullos | ullsos
🦶 | Quin és el plural de PEU? | peus | peues | peuses | peuns
🦷 | Quin és el plural de DENT? | dents | dentes | dentos | dentsos
👂 | Quin és el plural d'ORELLA? | orelles | orellas | orellos | orellens
🥚 | Quin és el plural d'OU? | ous | ouns | ouses | oues
🐓 | Quin és el plural de GALL? | galls | galles | gallos | gallsos
🐺 | Quin és el plural de LLOP? | llops | llopes | llopos | llopsos
🦓 | Quin és el plural de ZEBRA? | zebres | zebras | zebros | zebrens
🦒 | Quin és el plural de GIRAFA? | girafes | girafas | girafos | girafens
🐍 | Quin és el plural de SERP? | serps | serpes | serpos | serpsos
🍐 | Quin és el plural de PERA? | peres | peras | peros | perens
🍓 | Quin és el plural de MADUIXA? | maduixes | maduixas | maduixos | maduixens
🍉 | Quin és el plural de SÍNDRIA? | síndries | síndrias | síndrios | síndriens
👦 | Quin és el plural de NEN? | nens | nenos | nensos | nenses
👩 | Quin és el plural de DONA? | dones | donas | donos | donens
☁️ | Quin és el plural de NÚVOL? | núvols | núvoles | núvolos | núvolsos
💡 | Quin és el plural de LLUM? | llums | llumes | llumos | llumsos
🚂 | Quin és el plural de TREN? | trens | trenes | trenos | trensos
🚢 | Quin és el plural de VAIXELL? | vaixells | vaixelles | vaixellos | vaixellsos
🚲 | Quin és el plural de BICICLETA? | bicicletes | bicicletas | bicicletos | bicicletens
🎒 | Quin és el plural de MOTXILLA? | motxilles | motxillas | motxillos | motxillens
🧸 | Quin és el plural de JOGUINA? | joguines | joguinas | joguinos | joguinens
🖌️ | Quin és el plural de PINZELL? | pinzells | pinzelles | pinzellos | pinzellsos
🍽️ | Quin és el plural de PLAT? | plats | plates | platos | platsos
🎹 | Quin és el plural de PIANO? | pianos | pianes | pianons | pianoes
🛵 | Quin és el plural de MOTO? | motos | motes | motons | motoes
🐬 | Quin és el plural de DOFÍ? | dofins | dofís | dofines | dofí
✈️ | Quin és el plural d'AVIÓ? | avions | aviós | aviones | avió
🍈 | Quin és el plural de MELÓ? | melons | melós | melones | meló
🐭 | Quin és el plural de RATOLÍ? | ratolins | ratolís | ratolines | ratolí
🌲 | Quin és el plural de PI? | pins | pis | pies | pinos
🔥 | Quin és el plural de FOC? | focs | focos | foques | focsos
*🪰 | Quin és el plural de MOSCA? | mosques | moscas | mosces | moscos
*🛍️ | Quin és el plural de BOTIGA? | botigues | botigas | botiges | botigos
*👄 | Quin és el plural de BOCA? | boques | bocas | boces | bocos
*⛲ | Quin és el plural de PLAÇA? | places | plaçes | plaças | plaços
*🐢 | Quin és el plural de TORTUGA? | tortugues | tortugas | tortuges | tortugos
*🦭 | Quin és el plural de FOCA? | foques | focas | foces | focos
*🌧️ | Quin és el plural de PLUJA? | pluges | plujes | plujas | plujos
*🎂 | Quin és el plural de PASTÍS? | pastissos | pastís | pastisos | pastisses
*🦟 | Quin és el plural de MOSQUIT? | mosquits | mosquites | mosquitos | mosquitsos
*🧒 | Quin és el plural d'AMIC? | amics | amigos | amiques | amicos
*📅 | Quin és el plural de DIA? | dies | dias | dios | diens
*| Quin és el plural de PIJAMA? | pijames | pijamas | pijamos | pijamens
*🧦 | Quin és el plural de MITJÓ? | mitjons | mitjós | mitjones | mitjonos
*🎵 | Quin és el plural de CANÇÓ? | cançons | cançós | cançones | cancions
*🛏️ | Quin és el plural de COIXÍ? | coixins | coixís | coixines | coixí
*🐧 | Quin és el plural de PINGÜÍ? | pingüins | pingüís | pingüines | pingüí
*👦 | Quin és el plural de GERMÀ? | germans | germàs | germanos | germàns
*🏢 | Quin és el plural de PIS? | pisos | piss | pises | pissos
*| Quin és el plural de VAS? | vasos | vass | vases | vasons
**🍊 | Quin és el plural de TARONJA? | taronges | taronjes | taronjas | taronjos
**👅 | Quin és el plural de LLENGUA? | llengües | llenguas | llengues | llenguos
**💧 | Quin és el plural d'AIGUA? | aigües | aiguas | aigues | aiguos
**🚌 | Quin és el plural d'AUTOBÚS? | autobusos | autobussos | autobuses | autobús
**🌍 | Quin és el plural de PAÍS? | països | païssos | paísos | paíssos
**👨‍🌾 | Quin és el plural de PAGÈS? | pagesos | pagèsos | pagessos | pagèss
**🛋️ | Quin és el plural de SOFÀ? | sofàs | sofans | sofaes | sofases
**☕ | Quin és el plural de CAFÈ? | cafès | cafens | cafeses | cafeus
**⛷️ | Quin és el plural d'ESQUÍ? | esquís | esquins | esquíes | esquisos
**🎈 | Quin és el plural de GLOBUS? | globus | globussos | globusos | globes
**📆 | Quin és el plural de DILLUNS? | dilluns | dillunsos | dillunses | dillunys
**🎀 | Quin és el plural de LLAÇ? | llaços | llaçs | llaces | llassos
**🏠 | Quin és el plural de VEÍ? | veïns | veís | veins | veïnos
""",

    "rimes": """
☀️ | Quina paraula rima amb SOL? | col | gat | pa | llit | mar
🌊 | Quina paraula rima amb MAR? | bar | sol | peix | llum | dit
👃 | Quina paraula rima amb NAS? | gas | peu | llit | sol | ou
✋ | Quina paraula rima amb MÀ? | pa | peu | sol | llit | cor
☝️ | Quina paraula rima amb DIT? | pit | gat | sol | peu | mar
💡 | Quina paraula rima amb LLUM? | fum | gat | sol | peu | mar
🔥 | Quina paraula rima amb FOC? | lloc | gat | llum | pa | dit
🏞️ | Quina paraula rima amb RIU? | niu | gat | sol | mar | llum
🥚 | Quina paraula rima amb OU? | bou | gat | llum | dit | mar
🧢 | Quina paraula rima amb CAP? | nap | sol | peu | llit | fum
📅 | Quina paraula rima amb DIA? | tia | sol | gat | peu | llum
*🏠 | Quina paraula rima amb CASA? | brasa | llit | sol | peu | gos
🦵 | Quina paraula rima amb CAMA? | rama | peu | sol | llit | ou
🙂 | Quina paraula rima amb CARA? | clara | gos | llit | peu | sol
*🐀 | Quina paraula rima amb RATA? | corbata | gos | peu | sol | llum
*🐢 | Quina paraula rima amb TORTUGA? | eruga | gat | sol | peix | flor
🐛 | Quina paraula rima amb CUC? | ruc | gat | sol | peu | llit
🐬 | Quina paraula rima amb DOFÍ? | jardí | gos | sol | llum | peu
✈️ | Quina paraula rima amb AVIÓ? | cançó | gat | sol | peu | llit
🐝 | Quina paraula rima amb ABELLA? | ovella | gat | sol | llum | dit
🧼 | Quina paraula rima amb SABÓ? | racó | gat | llum | peu | mar
| Quina paraula rima amb MANTA? | planta | gos | llit | peu | sol
🐔 | Quina paraula rima amb GALLINA? | farina | gat | sol | peu | llum
🏊 | Quina paraula rima amb PISCINA? | cortina | gat | sol | peu | llum
⛰️ | Quina paraula rima amb MUNTANYA? | aranya | gos | llit | peu | sol
🛵 | Quina paraula rima amb MOTO? | foto | gat | llit | peu | mar
**🌳 | Quina paraula rima amb ARBRE? | marbre | gos | sol | peu | llit
🐴 | Quina paraula rima amb CAVALL? | gall | gos | sol | peu | llit
**🐰 | Quina paraula rima amb CONILL? | grill | gat | sol | peu | mar
🐮 | Quina paraula rima amb VACA? | butaca | gos | llit | peu | sol
*🍦 | Quina paraula rima amb GELAT? | mercat | gos | peu | sol | llit
🎂 | Quina paraula rima amb PASTÍS? | gris | gat | sol | peu | mar
🍯 | Quina paraula rima amb MEL? | cel | gat | sol | dit | llum
🧵 | Quina paraula rima amb FIL? | mil | gat | sol | peu | mar
🌹 | Quina paraula rima amb ROSA? | cosa | gat | llit | peu | mar
🔵 | Quina paraula rima amb BLAU? | clau | gos | llit | sol | peu
**| Quina paraula rima amb PRUNA? | duna | gat | peu | sol | llit
🍍 | Quina paraula rima amb PINYA? | vinya | gat | sol | peu | mar
🍃 | Quina paraula rima amb FULLA? | agulla | gat | sol | peu | llit
🌈 | Quina paraula rima amb ARC? | parc | gos | peu | llit | sol
*🌾 | Quina paraula rima amb PRAT? | blat | gos | peu | sol | llit
*👁️ | Quina paraula rima amb ULL? | full | gat | sol | peu | mar
*🐧 | Quina paraula rima amb PINGÜÍ? | camí | gat | sol | peu | llum
*🛏️ | Quina paraula rima amb COIXÍ? | cosí | gat | sol | peu | llum
*🏫 | Quina paraula rima amb ESCOLA? | cassola | gat | llit | peu | mar
*🧀 | Quina paraula rima amb FORMATGE? | viatge | gos | sol | llit | peu
*👦 | Quina paraula rima amb GERMÀ? | demà | gos | peu | sol | llit
*🪞 | Quina paraula rima amb MIRALL? | treball | gos | sol | peu | llit
*🔘 | Quina paraula rima amb BOTÓ? | turó | gat | llum | peu | mar
*🐑 | Quina paraula rima amb XAI? | mai | gos | peu | sol | llit
*🧤 | Quina paraula rima amb GUANT? | gegant | gos | peu | sol | llit
*| Quina paraula rima amb FIGA? | espiga | gat | sol | peu | mar
*☕ | Quina paraula rima amb TASSA? | carbassa | gos | llit | peu | sol
**🧶 | Quina paraula rima amb LLANA? | campana | gos | llit | peu | sol
**🎸 | Quina paraula rima amb GUITARRA? | cigarra | gos | llit | peu | sol
**🦀 | Quina paraula rima amb CRANC? | blanc | gos | peu | sol | llit
**🧂 | Quina paraula rima amb SAL? | animal | gos | peu | sol | llit
**🎄 | Quina paraula rima amb NADAL? | davantal | gos | peu | sol | llit
**💪 | Quina paraula rima amb BRAÇ? | llaç | gos | peu | sol | llit
**8️⃣ | Quina paraula rima amb VUIT? | fruit | gat | sol | peu | mar
**| Quina paraula rima amb PALA? | sala | gos | llit | peu | sol
""",

    "sillabes": """
🦶 | Quantes síl·labes té PEU? | 1 | 2 | 3 | 4
👃 | Quantes síl·labes té NAS? | 1 | 2 | 3 | 4
🌊 | Quantes síl·labes té MAR? | 1 | 2 | 3 | 4
🛏️ | Quantes síl·labes té LLIT? | 1 | 2 | 3 | 4
❄️ | Quantes síl·labes té NEU? | 1 | 2 | 3 | 4
🥚 | Quantes síl·labes té OU? | 1 | 2 | 3 | 4
🐟 | Quantes síl·labes té PEIX? | 1 | 2 | 3 | 4
💡 | Quantes síl·labes té LLUM? | 1 | 2 | 3 | 4
🐛 | Quantes síl·labes té CUC? | 1 | 2 | 3 | 4
🔥 | Quantes síl·labes té FOC? | 1 | 2 | 3 | 4
📋 | Quantes síl·labes té TAU-LA? | 2 | 1 | 3 | 4
👧 | Quantes síl·labes té NE-NA? | 2 | 1 | 3 | 4
🛵 | Quantes síl·labes té MO-TO? | 2 | 1 | 3 | 4
🍐 | Quantes síl·labes té PE-RA? | 2 | 1 | 3 | 4
🍍 | Quantes síl·labes té PI-NYA? | 2 | 1 | 3 | 4
🐴 | Quantes síl·labes té CA-VALL? | 2 | 1 | 3 | 4
🐰 | Quantes síl·labes té CO-NILL? | 2 | 1 | 3 | 4
🦓 | Quantes síl·labes té ZE-BRA? | 2 | 1 | 3 | 4
🐯 | Quantes síl·labes té TI-GRE? | 2 | 1 | 3 | 4
🐦 | Quantes síl·labes té O-CELL? | 2 | 1 | 3 | 4
🌳 | Quantes síl·labes té AR-BRE? | 2 | 1 | 3 | 4
🚪 | Quantes síl·labes té POR-TA? | 2 | 1 | 3 | 4
☁️ | Quantes síl·labes té NÚ-VOL? | 2 | 1 | 3 | 4
🍄 | Quantes síl·labes té BO-LET? | 2 | 1 | 3 | 4
🧳 | Quantes síl·labes té MA-LE-TA? | 3 | 2 | 4 | 1
🪑 | Quantes síl·labes té CA-DI-RA? | 3 | 2 | 4 | 1
🐔 | Quantes síl·labes té GA-LLI-NA? | 3 | 2 | 4 | 1
🐸 | Quantes síl·labes té GRA-NO-TA? | 3 | 2 | 4 | 1
🐢 | Quantes síl·labes té TOR-TU-GA? | 3 | 2 | 4 | 1
🏫 | Quantes síl·labes té ES-CO-LA? | 3 | 2 | 4 | 1
⭐ | Quantes síl·labes té ES-TRE-LLA? | 3 | 2 | 4 | 1
🎺 | Quantes síl·labes té TROM-PE-TA? | 3 | 2 | 4 | 1
🍊 | Quantes síl·labes té TA-RON-JA? | 3 | 2 | 4 | 1
🥕 | Quantes síl·labes té PAS-TA-NA-GA? | 4 | 3 | 5 | 2
🌷 | Quantes síl·labes té PRI-MA-VE-RA? | 4 | 3 | 5 | 2
🍊 | Quantes síl·labes té MAN-DA-RI-NA? | 4 | 3 | 5 | 2
*🐑 | Quantes síl·labes té OVELLA? | 3 | 2 | 4 | 1
*👂 | Quantes síl·labes té ORELLA? | 3 | 2 | 4 | 1
*🪟 | Quantes síl·labes té FINESTRA? | 3 | 2 | 4 | 1
*⛰️ | Quantes síl·labes té MUNTANYA? | 3 | 2 | 4 | 1
*🕷️ | Quantes síl·labes té ARANYA? | 3 | 2 | 4 | 1
*🏊 | Quantes síl·labes té PISCINA? | 3 | 2 | 4 | 1
*🧀 | Quantes síl·labes té FORMATGE? | 3 | 2 | 4 | 1
*🐿️ | Quantes síl·labes té ESQUIROL? | 3 | 2 | 4 | 1
*🎸 | Quantes síl·labes té GUITARRA? | 3 | 2 | 4 | 1
*🎹 | Quantes síl·labes té PIANO? | 3 | 2 | 4 | 1
*🚚 | Quantes síl·labes té CAMIÓ? | 3 | 2 | 4 | 1
*✈️ | Quantes síl·labes té AVIÓ? | 3 | 2 | 4 | 1
*🦁 | Quantes síl·labes té LLEÓ? | 2 | 1 | 3 | 4
*🍳 | Quantes síl·labes té CUINA? | 2 | 1 | 3 | 4
*🛏️ | Quantes síl·labes té COIXÍ? | 2 | 1 | 3 | 4
*🚢 | Quantes síl·labes té VAIXELL? | 2 | 1 | 3 | 4
*😂 | Quantes síl·labes té RIURE? | 2 | 1 | 3 | 4
*📅 | Quantes síl·labes té CALENDARI? | 4 | 3 | 5 | 2
*🛹 | Quantes síl·labes té MONOPATÍ? | 4 | 3 | 5 | 2
*🐞 | Quantes síl·labes té MARIETA? | 4 | 3 | 5 | 2
*🦏 | Quantes síl·labes té RINOCERONT? | 4 | 3 | 5 | 6
**💧 | Quantes síl·labes té AIGUA? | 2 | 1 | 3 | 4
**🐧 | Quantes síl·labes té PINGÜÍ? | 2 | 1 | 3 | 4
**🍇 | Quantes síl·labes té RAÏM? | 2 | 1 | 3 | 4
**🌍 | Quantes síl·labes té PAÍS? | 2 | 1 | 3 | 4
**🌂 | Quantes síl·labes té PARAIGUA? | 3 | 2 | 4 | 5
**🏠 | Quantes síl·labes té VEÏNA? | 3 | 2 | 4 | 1
**🦎 | Quantes síl·labes té CAMALEÓ? | 4 | 3 | 5 | 2
**🧊 | Quantes síl·labes té FRIGORÍFIC? | 4 | 3 | 5 | 6
**💊 | Quantes síl·labes té FARMÀCIA? | 4 | 3 | 5 | 2
**📺 | Quantes síl·labes té TELEVISIÓ? | 5 | 4 | 6 | 3
**🎂 | Quantes síl·labes té ANIVERSARI? | 5 | 4 | 6 | 3
**📚 | Quantes síl·labes té BIBLIOTECA? | 5 | 4 | 6 | 3
**🔤 | Quantes síl·labes té ABECEDARI? | 5 | 4 | 6 | 3
""",

    "formes": """
⭐ | Quantes puntes té aquesta estrella? | 5 | 4 | 6 | 3
| Quina forma té una roda? | Cercle | Quadrat | Triangle | Rectangle
🪙 | Quina forma té una moneda? | Cercle | Quadrat | Triangle | Hexàgon
🚪 | Quina forma té normalment una porta? | Rectangle | Cercle | Triangle | Hexàgon
📄 | Quina forma té un full de paper? | Rectangle | Cercle | Triangle | Pentàgon
| Quantes cantonades té un rectangle? | 4 | 3 | 5 | 2
| Quants vèrtexs té un quadrat? | 4 | 3 | 5 | 8
| Quantes cantonades té un cercle? | 0 | 1 | 2 | 4
⬛ | Quina forma és aquesta? | Quadrat | Cercle | Triangle | Hexàgon
🍦 | Quina forma té el cucurutxo d'un gelat? | Con | Cub | Esfera | Cilindre
🥳 | Quina forma té un barret de festa d'aniversari? | Con | Cub | Esfera | Cilindre
| Quina forma té una bombolla de sabó? | Esfera | Cub | Con | Piràmide
🍊 | Quina forma té una taronja? | Esfera | Cub | Con | Piràmide
*✏️ | Quina forma té la punta d'un llapis? | Con | Cub | Esfera | Cilindre
*🧻 | Quina forma té un rotllo de paper de vàter? | Cilindre | Cub | Esfera | Con
*| Quina figura té 6 costats? | Hexàgon | Pentàgon | Octàgon | Triangle
*| Quina figura té 8 costats? | Octàgon | Hexàgon | Pentàgon | Quadrat
*🔷 | Quina forma és aquesta? | Rombe | Cercle | Triangle | Hexàgon
*| Quants costats té un rombe? | 4 | 3 | 5 | 6
*| Quants costats tenen en total dos triangles? | 6 | 3 | 5 | 8
*| Quants costats tenen en total dos quadrats? | 8 | 4 | 6 | 10
*♟️ | Quina forma tenen les caselles d'un tauler d'escacs? | Quadrat | Triangle | Cercle | Hexàgon
**| Quantes cares té una piràmide de base quadrada? | 5 | 4 | 6 | 8
**| Quantes cares té una piràmide de base triangular? | 4 | 3 | 5 | 6
**| Si talles un quadrat per la diagonal, què et queda? | Dos triangles | Dos quadrats | Dos cercles | Dos rectangles
**| Si poses dos quadrats iguals l'un al costat de l'altre, quina forma fan? | Rectangle | Triangle | Cercle | Hexàgon
**| Quin cos geomètric té totes les cares quadrades? | Cub | Esfera | Cilindre | Con
""",

    "endevinalles": """
| Tinc bigotis, faig «miau» i caço ratolins. Qui soc? | el gat | el gos | el conill | la vaca
| Bordo, moc la cua quan estic content i vigilo la casa. Qui soc? | el gos | el gat | el cavall | el porc
| Faig «muu», menjo herba i dono llet. Qui soc? | la vaca | l'ovella | el cavall | el porc
| Tinc llana i faig «bee». Qui soc? | l'ovella | la vaca | el gos | el gat
| Faig «oinc» i m'encanta rebolcar-me pel fang. Qui soc? | el porc | la vaca | l'ovella | el conill
| Tinc les orelles llargues, salto i m'agraden les pastanagues. Qui soc? | el conill | el gat | la granota | el ratolí
| Visc a l'aigua, nedo amb aletes i tinc escates. Qui soc? | el peix | la granota | l'ànec | el cargol
| Tinc una closca dura, camino molt a poc a poc i hi puc amagar el cap. Qui soc? | la tortuga | el conill | la granota | l'ànec
| Tinc una gran cabellera al voltant del cap i rugeixo molt fort. Qui soc? | el lleó | la girafa | la zebra | l'elefant
| Tinc vuit braços i visc al mar. Qui soc? | el pop | el peix | el dofí | la balena
| Faig «quac, quac» i nedo a l'estany. Qui soc? | l'ànec | la granota | la gallina | el peix
| Faig «quiquiriquic» quan surt el sol. Qui soc? | el gall | la gallina | l'ànec | el gat
| Soc petita, vermella amb punts negres i volo. Qui soc? | la marieta | la formiga | l'abella | la mosca
| Tinc ales de colors i abans era una eruga. Qui soc? | la papallona | l'abella | la mosca | l'ocell
| Tinc una cua llarga, m'enfilo als arbres i m'agraden els plàtans. Qui soc? | el mico | el lleó | la girafa | l'elefant
| Tinc tecles blanques i negres i faig música. Què soc? | el piano | la guitarra | el tambor | la flauta
| Per dins soc freda i guardo el menjar fresc. Què soc? | la nevera | el forn | la rentadora | l'armari
| Si em mires, hi veus la teva cara. Què soc? | el mirall | la finestra | la porta | la pissarra
| Faig escuma i et deixo les mans netes. Què soc? | el sabó | la tovallola | la pinta | el pinzell
| Esborro el que has escrit amb el llapis. Què soc? | la goma | les tisores | el regle | el pinzell
| Vaig per les vies i porto molts vagons. Què soc? | el tren | l'autobús | el cotxe | el vaixell
| Navego pel mar i porto gent d'un port a un altre. Què soc? | el vaixell | el tren | l'avió | la bicicleta
| Caic del cel en forma de gotes. Què soc? | la pluja | la neu | el sol | el vent
| No em veus, però faig moure les fulles dels arbres. Què soc? | el vent | la pluja | el sol | la neu
| De nit brillem al cel i som moltes, moltes. Què som? | les estrelles | la lluna | el sol | el núvol
| Tinc sorra i a l'estiu la gent s'hi banya. Què soc? | la platja | la muntanya | el bosc | el desert
| Soc groc, llarg i corbat, i m'has de pelar. Què soc? | el plàtan | la poma | la pera | la maduixa
| Soc taronja i llarga, creixo sota terra i als conills els agrado molt. Què soc? | la pastanaga | la taronja | el plàtan | la poma
| Tinc pètals de colors i les abelles em venen a visitar. Què soc? | la flor | el bolet | la fulla | la pedra
| Tinc llengüeta i cordons, i em poses al peu. Què soc? | la sabata | el guant | el barret | el mitjó
| Et protegeixo el cap quan vas amb bicicleta. Què soc? | el casc | la bufanda | els guants | les sabates
*| Soc un ocell que no vola, nedo molt bé i visc on fa molt de fred. Qui soc? | el pingüí | la gallina | l'àguila | el colom
*| Porto la cria en una bossa a la panxa i faig grans salts. Qui soc? | el cangur | la granota | el conill | el lleó
**| Soc l'animal més gran del mar i respiro per un forat que tinc a dalt del cap. Qui soc? | la balena | el dofí | el peix | el pop
**| Volo de nit, tinc uns ulls molt grossos i puc girar molt el cap. Qui soc? | l'òliba | el ratpenat | el gat | la gallina
**| Tinc punxes a l'esquena i, si tinc por, em faig una bola. Qui soc? | l'eriçó | el conill | la tortuga | el cargol
*| Soc un gat molt gran amb ratlles taronges i negres. Qui soc? | el tigre | la zebra | el lleó | la girafa
*| Si em piques amb les baquetes, faig «pom, pom». Què soc? | el tambor | el piano | la flauta | el violí
*| Tinc sis cordes i em toquen amb els dits. Què soc? | la guitarra | el piano | el tambor | la trompeta
*| Per dins soc molt calent i hi couen els pastissos. Què soc? | el forn | la nevera | la rentadora | la dutxa
*| Dono voltes i voltes i deixo la roba neta. Què soc? | la rentadora | la nevera | el forn | l'aspiradora
*| Tenim dos vidres i t'ajudem a veure-hi millor. Què som? | les ulleres | el mirall | la finestra | el rellotge
*| Tinc un mànec i molts pèls, i et netejo les dents. Què soc? | el raspall de dents | la pinta | la forquilla | el sabó
*| Tenim dues fulles que tallen i dos forats per posar-hi els dits. Què som? | les tisores | la goma | el llapis | el regle
**| Soc llarg i recte, tinc números i t'ajudo a fer ratlles rectes. Què soc? | el regle | la goma | les tisores | el pinzell
*| Soc vermell, porto una escala i una mànega i apago focs. Què soc? | el camió de bombers | l'ambulància | el taxi | l'autobús
*| Porto les persones malaltes a l'hospital amb la sirena posada. Què soc? | l'ambulància | el camió de bombers | el tren | l'autobús
*| Tinc set colors i surto al cel quan plou i fa sol alhora. Què soc? | l'arc de Sant Martí | el núvol | la lluna | l'estrella
**| Soc el soroll molt fort que se sent quan hi ha tempesta. Què soc? | el tro | el llamp | l'arc de Sant Martí | la neu
*| Soc molt gran, d'aigua salada, i tinc onades. Què soc? | el mar | el riu | el llac | la piscina
*| Soc molt alta i a l'hivern tinc neu a dalt de tot. Què soc? | la muntanya | el riu | la platja | el mar
*| Tinc cap i mànec, i clavo claus. Què soc? | el martell | la serra | les tisores | la cullera
**| Soc vermella i petita, i porto les llavors per fora. Què soc? | la maduixa | la cirera | la poma | el tomàquet
*| Soc verda per fora, vermella per dins i tinc llavors negres. Què soc? | la síndria | el meló | la poma | el kiwi
*| Tinc tronc, branques i fulles, i els ocells hi fan niu. Què soc? | l'arbre | la flor | l'herba | el bolet
**| Tinc moltes capes i, quan em tallen, faig plorar. Què soc? | la ceba | la pastanaga | l'enciam | el tomàquet
**| Tinc molts grans grocs i amb mi es fan crispetes. Què soc? | el blat de moro | l'arròs | el pèsol | la poma
**| Cent dames en un camí, no fan pols ni remolí. Què són? | les formigues | les vaques | les gallines | les ovelles
**| Blanca com la neu, negra com el carbó; parla i no té boca, camina i no té peus. Què és? | la carta | la neu | el llapis | la sabata
**| Si dius el meu nom, em trenques. Què soc? | el silenci | el got | el mirall | la pilota
**| Puc omplir tota l'habitació, però no ocupo gens de lloc. Què soc? | la llum | l'aigua | la sorra | la roba
""",
}

# Grups complets per a L'INTRÚS. Cada element és només d'un grup (sense tomàquet,
# sense taronja als colors, sense patinet ni pilota a les joguines, sense insectes a part).
GRUPS = {
    "intrus": {
        "fruites": "🍎 poma, 🍐 pera, 🍌 plàtan, 🍓 maduixa, 🍊 taronja, 🍇 raïm, 🍒 cireres, 🍉 síndria, "
                   "🍋 llimona, 🍑 préssec, 🍍 pinya, 🥝 kiwi, 🥭 mango, 🍈 meló",
        "animals": "🐶 gos, 🐱 gat, 🐮 vaca, 🐷 porc, 🐴 cavall, 🐰 conill, 🦁 lleó, 🐸 granota, "
                   "🐘 elefant, 🦒 girafa, 🐒 mico, 🐔 gallina, 🐑 ovella, 🐭 ratolí, 🐢 tortuga, 🐟 peix, 🦆 ànec",
        "transports": "🚗 cotxe, 🚌 autobús, 🚂 tren, ✈️ avió, 🚲 bicicleta, 🚢 vaixell, "
                      "🚁 helicòpter, 🛵 moto, 🚕 taxi, 🚜 tractor, 🚚 camió, 🚑 ambulància, 🚋 tramvia",
        "roba": "👕 samarreta, 👖 pantalons, 🧦 mitjons, 👟 sabates, 🧥 jaqueta, 🧢 gorra, 🧣 bufanda, "
                "👗 vestit, 🧤 guants, 👒 barret, 👔 camisa, 🥾 botes, 🩱 banyador",
        "instruments": "🎸 guitarra, 🎹 piano, 🥁 tambor, 🎺 trompeta, 🎻 violí, 🎷 saxòfon, 🪕 banjo, 🪗 acordió",
        "cos": "👁️ ull, 👂 orella, 👃 nas, ✋ mà, 🦶 peu, 👄 boca, 🦷 dent, 👅 llengua, 💪 braç, 🦵 cama, 🧠 cervell",
        "verdures": "🥕 pastanaga, 🥦 bròquil, 🥬 enciam, 🧅 ceba, 🥒 cogombre, 🧄 all, 🥔 patata",
        "esports": "⚽ futbol, 🏀 bàsquet, 🎾 tennis, 🏊 natació, ⛷️ esquí, 🏐 voleibol, 🏉 rugbi, "
                   "🤸 gimnàstica, 🏒 hoquei, ⛳ golf, 🏸 bàdminton",
        "mobles": "🪑 cadira, 🛏️ llit, 🛋️ sofà, 🗄️ arxivador",
        "eines": "🔨 martell, 🪚 serra, 🔧 clau anglesa, 🪛 tornavís, ⛏️ pic",
        "colors": "🔴 vermell, 🔵 blau, 🟡 groc, 🟢 verd, ⚫ negre, ⚪ blanc, 🟤 marró, 🟣 lila",
        "escola": "✏️ llapis, 🖍️ ceres, 📒 llibreta, 🎒 motxilla, 🖊️ bolígraf",
        "joguines": "🧸 osset de peluix, 🪀 io-io, 🪁 estel, 🎈 globus, 🧩 trencaclosques",
        "oratge": "☀️ sol, 🌧️ pluja, ❄️ neu, ⛅ núvols, 🌈 arc de Sant Martí, ⚡ llamp, 🌬️ vent",
    }
}
