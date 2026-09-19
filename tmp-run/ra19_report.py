"""Bouwt runs/2026-09-19-run-a.md: handgeschreven tekst + de blokken die uit de scripts komen.

Overtypen is de fout die §5 en §6c allebei benoemen, dus de dekkingstabel, de wedstrijdsecties en
alle stats-uitvoer worden hier ingelezen in plaats van herhaald.
"""
import os

S = os.environ["SCRATCH"]
cov = open("tmp-run/ra19_coverage.md").read()
secs = open("tmp-run/ra19_matches.md").read()
cap = lambda p: open(p).read().rstrip("\n")

api = cap(f"{S}/api_check.txt")
toplist = cap(f"{S}/toplist.txt")
ledger = cap(f"{S}/ledger.txt")
shadow = cap(f"{S}/shadow.txt")
recal = cap(f"{S}/recal.txt")
calib = cap(f"{S}/calib.txt")
ctx = cap(f"{S}/ctx.txt")
ART = os.environ.get("ARTIFACT_URL", "(nog niet gepubliceerd)")
DUUR = os.environ.get("DUUR", "?")
EIND = os.environ.get("EIND", "?")

MD = f"""# Run A — 2026-09-19

**Gestart:** 04:09 CEST · **Afgerond:** {EIND} CEST · **Looptijd:** {DUUR} minuten · **Bets gepubliceerd:** 0 · **Wedstrijden diep geanalyseerd:** 54 van 57 · **Afgekapt:** 2

De run is niet onderbroken (`resumed_count` = 0). Dit is de drukste dag die deze routine tot nu toe
heeft gedraaid — 57 duels in dertien competities tegen twaalf duels in elf competities gisteren —
en de looptijd is ruim binnen de grens van 06:30 gebleven die §0 als de échte betekenis van
`MAX_DEEP_ANALYSES` aanwijst. De cap van 55 knelde vandaag voor het eerst sinds de verhoging van
5 september.

Branch: de sessie startte op `claude/stoic-davinci-lwr9lk`, maar alle commits van deze run staan
op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.

**Leesbaar dagrapport:** {ART}

## Samenvatting in één alinea

Zaterdag 19 september, en alle dertien binnenlandse competities van de runlijst speelden tegelijk:
**57 wedstrijden** van 13:30 tot 21:30, tegen twaalf gisteren. De acht overige stonden niet op de
kalender — de drie Europese toernooien beginnen hun competitiefase pas volgende week en alle vijf
de bekers lagen stil — en dat is `GEEN WEDSTRIJD`, geen storing. **De cap van 55 knelde voor het
eerst:** twee duels zijn `AFGEKAPT` (St. Johnstone – Falkirk en Lommel – KV Mechelen), allebei op
precies dezelfde datarijkdom van 5,0 als het laagste duel dat het wél haalde. Van de 57 duels
zijn er **40 `FULL`, 16 `LIGHT` en 1 `NONE`**; binnen de cap blijven 40 `FULL`, 14 `LIGHT`
en 1 `NONE` over, en zijn er **54 werkelijk doorgerekend** (Newcastle United – Hull City,
omrekening buiten het gemeten bereik), samen **773 selecties over alle zes de markten en nul
bets**. Zeventien duels hebben een omgerekende ploeg — achttien ploegen, de grootste
omrekenoperatie tot nu toe, met voor het eerst twee **degradanten** (West Ham United en Burnley)
naast de promovendi. De inkoop kan de uitkomst niet hebben veroorzaakt: alle dertien competities
hebben een sportkey, alle dertien kregen de volle bulk-aanroep, en de vijftien duels met een
kandidaat-edge kregen daarbovenop BTTS — **54 van 793 credits**, marktbalans 13 op 13. Binnen de
koersband staat de hoogste herijkte edge op **+5,41 pp** tegen een `FULL`-drempel van 8,0; dezelfde
selectie stond ruw op **+19,11 pp**. Onder **Bevindingen** staan drie dingen: het contextlogboek
meet voor het eerst een significant effect (en de markt maakt precies dezelfde fout), de
herijkingsreeks bevestigt op 43 afgewikkelde gevallen dat de correctie geld bespaart, en de
vroeg-seizoenscorrectie valt vandaag op 40 duels iets gunstiger uit dan gisteren op acht.

## Stage -2 — Branches

De branchcontrole is als eerste handeling uitgevoerd, vóórdat `_shared-rules.md` is gelezen.
`git fetch origin` bracht **31 takken** naast `main` in beeld, en op de eerste telling hadden er
**26** tussen de 4 en 184 commits die `HEAD` niet had.

Dat was opnieuw het **valse ondiep-kloonalarm** waar §3 Stage -2 voor waarschuwt: de container
leverde de repo als ondiepe kloon aan (`git rev-parse --is-shallow-repository` → `true`, 62
commits lokaal). Na `git fetch --unshallow origin` staat `main` op **326** commits en is het beeld
compleet anders:

| | ondiep (62 commits lokaal) | na `--unshallow` (326) |
|---|---|---|
| takken met "eigen" commits | 26 van de 31 (4 t/m 184 stuks) | **0 van de 31** |

Er viel dus **niets te mergen** en geen enkele conflictregel hoefde te worden toegepast. Dat was
vóór het unshallowen al op **inhoud** nagegaan, en die controle wees dezelfde kant op:

| Controle over alle takken met "eigen" commits | Uitkomst |
|---|---|
| picks met een id dat niet in `main` staat | **0** — `main` telt 274 regels en is de vereniging van alle takken; de takken met tekstueel afwijkende regels wijken af doordat `main` diezelfde picks intussen heeft afgewikkeld |
| takken die inhoudelijk vóórliggen op `main` | **0** — elke tak met een afwijkend bestand is een snapshot van een oudere `main`; `scripts/oddspapi.py` op `zealous-edison-m3dxn5` is het enige bestand dat `main` niet heeft, en dat is op 31 aug bewust verwijderd (commit `f342894`) |
| openstaande picks van een run die op een andere tak nooit is afgewikkeld | **0** — `ledger.py open` gaf niets, `picks.jsonl` telt 0 open regels op 274 |

De run draait op `main` en alle commits gaan erheen.

## Stage 0 — Afwikkelen

`ledger.py open` gaf **niets**: alle 274 picks in het logboek zijn afgewikkeld. `shadow.py open`
gaf **acht** schaduwpicks van 18 september (vijf uit Run A, drie uit Run B), alle acht afwikkelbaar
volgens de statusregel van §0 (`finished` van de bron, niet de klok). Alle acht zijn
competitieduels zonder verlenging of strafschoppen: de eindstand ís de stand na 90 minuten.

| Schaduwpick | Uitslag | Resultaat |
|---|---|---|
| Bayern München – Union Berlin · BTTS ja @ 1.87 (`herijking`) | 7–0 | **verloren** |
| Monaco – Lens · 1X2 Lens @ 3.60 (`underdog_ruw`) | 2–1 | **verloren** |
| Monaco – Lens · Over 2.5 @ 1.56 (`herijking`) | 2–1 | **gewonnen** |
| Wisła Kraków – Śląsk Wrocław · Over 3 @ 1.99 (`herijking`) | 2–1 | **void** (precies 3 doelpunten op een hele lijn) |
| Albacete – Córdoba · Over 2.5 @ 1.73 (`herijking`) | 1–2 | **gewonnen** |
| Rapid Wien – WSG Tirol · AH WSG Tirol +1.5 @ 1.97 (`underdog_ruw`) | 3–0 | **verloren** |
| Rapid Wien – WSG Tirol · Under 3.5 @ 1.86 (`herijking`) | 3–0 | **gewonnen** |
| Almere City FC – Heracles · 1X2 Almere @ 3.10 (`underdog`) | 1–0 | **gewonnen** |

Vier gewonnen, drie verloren, één void. `ctxlog.py settle` wikkelde dezelfde ochtend 24
contextwedstrijden af; het contextlogboek staat nu op 610 afgewikkelde duels — zie Bevinding 1.

## Bronstatus deze run

Letterlijke uitvoer van `python3 scripts/api_check.py`:

```
{api}
```

**`API_FOOTBALL_KEY` ontbreekt nog steeds** — niet afgewezen, maar niet gezet in de omgeving van de
geplande taak. `api_check.py` slaat de bron over zonder HTTP-verzoek. Gevolg voor deze run: geen.
De kansinput kwam van Fotmob en Understat, en dat zestien duels `LIGHT` zijn komt door de
omrekeningen (§4) en niet door deze sleutel. Zie `README.md` → "Sleutels toevoegen".

| Bron | Status | Detail deze run |
|---|---|---|
| Fotmob | `ok` | daglijst 13 Run A-competities met 57 duels, alle dertien met xG in vorig én lopend seizoen; context voor alle 57 duels zonder fout (32× voorspelde opstelling, 25× laatste basiself); `check_venue` meldde géén verplaatsing; tien tweede divisies opgehaald voor de omrekeningen |
| The Odds API | `ok` | 19.066 credits over, 934 gebruikt deze maand, 43 actieve voetbalcompetities |
| BetExplorer | `ok` | dertien slugs, alle dertien raak — 167 rijen waarvan 57 vandaag |
| Understat | `ok` | vijf competities (EPL, Serie_A, La_liga, Bundesliga, Ligue_1), alleen voor het kalibratieblok |
| API-Football | `key_missing` | sleutel niet gezet; ongewijzigd sinds 8 aug 2026 |

Wijzigingen t.o.v. vorige run: **geen.** Eén kleine waarneming die het noteren waard is:
`soccer_spl` (Schotse Premiership) stond **niet** in de sportkey-lijst die `api_check.py` afdrukt,
maar leverde in de bulk-aanroep wél zes events op. Die lijst is dus krapper dan wat de API
accepteert — geen storing, maar wie hem als dekkingsbron leest, onderschat wat er te koop is.

## Dekkingsrapportage

{cov}

**Afgekapt door `MAX_DEEP_ANALYSES`:** 2 wedstrijden van de 57. De cap staat op 55 (zaterdag).
Dit is de eerste dag sinds de verhoging van 5 september waarop hij knelt, en de twee getallen die
§3 Stage 4 verplicht stelt liggen precies op elkaar:

| | Wedstrijd | Datarijkdom | Markten |
|---|---|---|---|
| laagste die het nog haalde | Lincoln City – Swansea City | 5,0 | 5 |
| hoogste die afviel | St. Johnstone – Falkirk | 5,0 | 5 |

De datarijkdom liep over de hele run van 5,0 tot 8,0. De afkapping is dus **niet** beslist op
datarijkdom maar op de derde en vierde sleutel (aantal markten, daarna aftrap) — en dat is precies
wat de meting van 5 september voorspelt: de sortering scheidt niet, dus afkappen kost naar rato en
niet de slechtste groep. Beide afgekapte duels zijn `LIGHT` met een omgerekende ploeg. Hun context
is wél opgehaald en staat in `data/run-state/` en in `ctxlog.py`, zoals §1c sinds 5 september eist.

## Omrekeningen

**Zeventien duels, achttien ploegen** — de grootste omrekenoperatie tot nu toe. Geen enkele
kruis-grens (de Europese toernooien speelden niet). Alle omgerekende duels zijn `LIGHT`: een
omgerekende ploeg is nooit `FULL`, want de omrekening haalt de systematische fout eruit en niet de
onzekerheid.

| Richting | Ploegen | Divisiepaar | Factor |
|---|---|---|---|
| omhoog | Ipswich Town, Hull City, Coventry City | E0/E1 (gemeten) | ×0.541 / 1.783 |
| **omlaag** | **West Ham United, Burnley** | **E0/E1 (gemeten)** | **×1.830 / 0.634** |
| omhoog | Cardiff City, Lincoln City | E1/E2 (gemeten) | ×0.673 / 1.638 |
| omhoog | Venezia | I1/I2 (gemeten) | ×0.601 / 1.528 |
| omhoog | Racing Santander | SP1/SP2 (gemeten) | ×0.661 / 1.498 |
| omhoog | Troyes, Le Mans | F1/F2 (gemeten) | ×0.609 / 1.424 |
| omhoog | St. Johnstone | SC0/SC1 (gemeten) | ×0.591 / 1.689 |
| omhoog | ADO Den Haag, Cambuur, Willem II | NED (eigen meting 31 aug) | ×0.614 / 1.564 |
| omhoog | Marítimo | POR (eigen meting 31 aug) | ×0.615 / 1.504 |
| omhoog | Lommel | BEL (eigen meting 31 aug) | ×0.696 / 1.604 |
| omhoog | Çorum FK | TUR (eigen meting 31 aug) | ×0.708 / 1.497 |

Twee dingen die opvallen. Ten eerste: de **degradantentak** raakt vandaag voor het eerst twee duels
tegelijk (Millwall – West Ham United en Burnley – Derby County). Die tak gebruikt een eigen factor
in de andere richting, en het is dezelfde meting — E0/E1, n=33 — dus hij staat op dezelfde grond
als de promotiekant.

Ten tweede, en dat is de enige weigering van vandaag: **Hull City** komt met een relatieve
verdediging van 1.102 boven de bovengrens 1.022 van het gemeten bereik uit. `conversion_in_range`
is een poort en geen aantekening (§4), dus Newcastle United – Hull City is `NONE` geworden en is
niet doorgerekend. Dat is de Coventry-val waar die paragraaf voor waarschuwt, en de poort deed
precies wat hij moet doen: buiten het gemeten bereik is er geen onafhankelijke kansinput op het
niveau waarop gespeeld wordt.

## Creditbudget en marktbalans

`suggest_cap(19066, 12)` = **793** — 19.066 credits over volgens `api_check.py`, 12 dagen tot de
maandwissel, 2 runs per dag. `split_budget(793, 13)` gaf **13 spreads / 13 totals**: alle dertien
inkoopbare competities kregen allebei. Het plafond laat 3 credits per competitie ruimschoots toe,
dus de bulk-aanroep (`h2h` + `spreads` + `totals`) is voor alle dertien gedaan — vijf van de zes
markten in één keer, en 1X2 op de **beste prijs** in plaats van op het BetExplorer-marktgemiddelde.

| | |
|---|---|
| bulk (13 × 3 credits) | 39 |
| BTTS, tweede ronde (15 duels met een kandidaat-edge, §1a stap 2) | 15 |
| **totaal** | **54 van 793** — 19.012 over |

**Marktbalans — de controle op de inkoop (§1a).** Dertien van de dertien competities kregen zowel
een uitkomst- als een doelpuntenmarkt. Ruimer kan hij niet slagen.

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 (beste prijs, `h2h`-bulk) | 13 van 13 | 159 | 0 |
| Asian Handicap | 13 van 13 | 242 | 0 |
| Draw No Bet (0.0-lijn) | 32 van 54 duels | 63 | 0 |
| Double Chance (±0.5-lijn) | 37 van 54 duels | 37 | 0 |
| Over/Under | 13 van 13 | 242 | 0 |
| BTTS | 15 duels met kandidaat-edge | 30 | 0 |

Draw No Bet en Double Chance zijn dunner omdat respectievelijk 22 en 17 duels géén 0.0- of
±0.5-lijn in de `spreads`-respons hadden. Dat is **bekeken met een reden** en geen gat; het staat
zo in `markets_checked`, en `progress.py verify` is groen over alle 54 doorgerekende wedstrijden.

**Beste prijs tegenover het marktgemiddelde:** mediaan **+4,96%** over 51 duels, gemiddeld
**+5,68%**, hoogste +16,37% (Sporting CP – Arouca). Dat ligt in lijn met de +7,78% van de meting
op 5 september en is vandaag, anders dan gisteren, niet door één uitschieter vertekend.

## Vroeg-seizoenscorrectie

`early_season_uplift` gaf **×1,0861** (gepoold 1,0944 over 84 speeldagen in 13 competities). De
competities staan tussen 4 (Bundesliga) en 9 speeldagen (Deense Superliga, Ekstraklasa) ver.

De controle die §3 Stage 5 voorschrijft — P(Over 2.5) tegen de de-vigde marktkans, over de **40**
duels met een 2.5-lijn aan beide kanten:

| | gemiddelde afwijking | gemiddelde absolute fout |
|---|---|---|
| zonder correctie | −2,71 pp | 4,42 pp |
| met correctie ×1,0861 | +2,66 pp | **4,21 pp** |

**Anders dan gisteren maakt de correctie de schatting vandaag iets béter** — de absolute fout zakt
van 4,42 naar 4,21 pp. Wat in beide metingen hetzelfde is: het teken klapt van onder de markt naar
boven de markt, dus de correctie schiet door. Met 40 duels in plaats van acht is dit de
betrouwbaardere van de twee. Dit blijft een meting tegen de markt en dus uitsluitend een diagnose
(§1d, §6e) — de correctie mag hier niet op worden afgeregeld.

## Wedstrijden

{secs}

## Topselectie

**Nul gepubliceerde bets**, dus geen topselectie. §5 zegt het met zoveel woorden: zijn er minder
gekwalificeerde bets dan `MAX_SHORTLIST`, lever er dan minder — en vul niet aan.

### De dagelijkse top-5, twee keer gerekend (§5a)

Letterlijke uitvoer van `python3 scripts/toplist.py --run a --date 2026-09-19`:

```
{toplist}
```

### Net niet

Zes wedstrijden leverden een `near_miss` op — de overige 48 hadden geen enkele selectie boven de
`NEAR`-drempel (3,0 pp bij `FULL`, 6,0 bij `LIGHT`) op de herijkte schaal.

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Herijkt | Valt af op |
|---|---|---|---|---|---|---|
| Sevilla – Barcelona | AH Sevilla +2.5 @ 1.71 | +20,09 pp | +15,22 pp | +13,92 pp | **+5,41 pp** | `edge` |
| Athletic Club – Deportivo Alavés | 1X2 Alavés @ 5.80 | +10,20 pp | +12,65 pp | +9,59 pp | **+4,98 pp** | `edge` |
| Osasuna – Rayo Vallecano | AH Osasuna −1 @ 4.55 | +12,33 pp | +11,47 pp | +11,97 pp | **+4,70 pp** | `edge` |
| Queens Park Rangers – Preston North End | 1X2 Preston @ 5.10 | +8,71 pp | +15,45 pp | +7,78 pp | **+3,85 pp** | `herijking` |
| Ajax – Excelsior | AH Excelsior +2 @ 2.06 | +17,00 pp | +19,03 pp | +13,23 pp | **+3,62 pp** | `edge` |
| Brighton & Hove Albion – Arsenal | 1X2 Brighton @ 5.21 | +10,80 pp | +4,41 pp | +6,04 pp | **+3,59 pp** | `edge` |

Lees de eerste regel als het verhaal van vandaag in het klein. Sevilla +2.5 tegen Barcelona haalt
op de ruwe schaal **alles**: beide methodes ver boven de drempel, en de zwakste stand van het hele
`(shrink, rho)`-grid nog op +13,92 pp. Na de herijking blijft er +5,41 pp over tegen een drempel
van 8,0. Dat verschil van bijna veertien procentpunt op één en dezelfde bet is wat §1g beschrijft,
en het is vandaag de hele verklaring voor nul bets.

**Eén selectie haalde de drempel wél, maar niet de koersband:** Sevilla wint van Barcelona op
@14.23, herijkte edge **+8,48 pp**. `MAX_ODDS` staat op 6.00 omdat de kansschatting daarboven te
onnauwkeurig is om edge zinvol te noemen. Het schaduwlogboek geeft die poort vandaag gelijk met een
hardheid die verder geen enkele poort haalt: **15 van de 15** afgewikkelde kandidaten die op `odds`
sneuvelden, verloren — een ROI van −100% en 15 eenheden bespaard.

### Waar de 773 selecties op afvielen

| Poort | Herijkte schaal | Ruwe schaal |
|---|---|---|
| 1 — edge onder de drempel | 735 | 711 |
| 2 — koers buiten 1.30–6.00 | 24 | 24 |
| 5 — tweede methode tegengesteld | 0 | 0 |
| 7 — context | 0 | 18 |
| 8 — underdog onder 0.35 | 0 | 6 |
| alle acht gehaald | 0 (14 vielen alleen op de herijking) | 14 |

Lees die twee kolommen naast elkaar. Op de herijkte schaal komt de edge-poort altijd als eerste,
dus alles wat daar sneuvelt bereikt de latere poorten nooit — precies het verschijnsel waar §1e op
15 september de tweede boekingsschaal voor invoerde. Op de ruwe schaal bindt poort 7 achttien keer
en poort 8 zes keer, verdeeld over drie duels (Tottenham – Aston Villa, Ajax – Excelsior en
OH Leuven – RAAL La Louvière), die als `underdog_ruw` het schaduwlogboek ingaan. Op de herijkte
schaal hield poort 8 **niets** tegen. Die poort vervalt over zes dagen, op 25 september, volgens
het besluit van de gebruiker van 18 september; vanaf dan houdt `sides.check()` alleen nog
`would_block` bij.

## Afwikkeling vorige picks

Geen openstaande echte picks. Acht schaduwpicks van 18 september afgewikkeld — zie Stage 0
hierboven: vier gewonnen, drie verloren, één void.

## Stand van het logboek

### `ledger.py stats` — wat er wél doorheen kwam

```
{ledger}
```

### `recalibrate.py show` — de stand van de herijking

```
{recal}
```

De fit van vandaag is `a=0.833, b=-0.464` op **687** afgerekende gevallen t/m 18 september. Het
model zei gemiddeld 52,1% en het gebeurde 40,9% van de tijd. Op de kansen die vandaag in de buurt
kwamen haalt de correctie 11 tot 14 procentpunt weg, en dat is exact het verschil tussen 304
positieve ruwe edges en nul bets.

### `shadow.py stats` — wat de poorten hebben tegengehouden

```
{shadow}
```

### `calibration.py stats` — staat het model scheef tegenover de markt?

```
{calib}
```

### `ctxlog.py stats` — doet context er iets toe?

```
{ctx}
```

## Bevindingen

### 1. Het contextlogboek meet voor het eerst een significant effect — en de markt maakt precies dezelfde fout

Dit is de meting waar §1c sinds 5 september op wacht. Toen stond ze op 147 wedstrijden met
`r = −0,007` en `t = −0,08`: niets. Vandaag, met **548 bruikbare wedstrijden** van de 610
afgewikkelde, staat er iets anders:

| | r | t | helling |
|---|---|---|---|
| fout van het **model** tegen het beschikbaarheidsverschil | −0,105 | **−2,48** | **−29,4 pp per eenheid** |
| fout van de **markt** tegen hetzelfde verschil | −0,105 | **−2,46** | **−28,7 pp per eenheid** |

De tabel in §1c zegt dat er bij ~475 wedstrijden een effect van 30 pp per eenheid aantoonbaar zou
zijn. Dat is precies waar we nu staan, en precies wat er gemeten wordt. Het teken klopt ook met wat
een mens zou zeggen: mist de thuisploeg meer selectiewaarde dan de tegenstander, dan wint hij
minder vaak dan zowel het model als de markt dacht.

**Maar lees de tweede regel net zo aandachtig als de eerste, want die bepaalt wat dit waard is.**
De markt maakt dezelfde fout, met een helling die binnen een procentpunt gelijk is (−28,7 tegen
−29,4) en een `t` die niet te onderscheiden is. Twee lezingen, en er is vandaag geen meting die
tussen de twee kiest:

1. **Het is een echte, onbeprijsde factor.** Dan zou het model corrigeren wél een voordeel op de
   markt opleveren, want de bookmaker doet het niet. Dit is de enige kandidaat in dit hele bestand
   waarvan dat zou kunnen gelden, en dat is opmerkelijk genoeg om vast te leggen.
2. **Beide meten hetzelfde artefact.** `out_share` komt uit het opstellingsblok van Fotmob, en dat
   blok is bij 32 van de 57 duels een *voorspelling*. Een voorspelde opstelling is deels afgeleid
   van dezelfde informatie waarmee de markt beweegt; dan meet de correlatie geen voorsprong maar
   een gedeelde bron.

**Er verandert vandaag niets.** §1c zegt het zonder omhaal: *"Tot die meting er is blijft poort 7
een rem en geen bijstelling"*, en één dag waarop `t` de twee passeert is geen meting maar een
eerste waarneming (§6d: kijk naar de richting over weken). Wat hier wél uit volgt, staat onder
Openstaand — en het is de eerste keer sinds de invoering van `ctxlog.py` dat die vraag een
concrete vervolgstap heeft in plaats van "meer data verzamelen".

### 2. De herijkingsreeks staat op 43 afgewikkelde gevallen en bevestigt dat de correctie geld bespaart

§5a voerde op 6 september de categorie `failed_gate = "herijking"` in met de instructie *"niet
lezen vóór ~30 afgewikkelde gevallen"*. Gisteren passeerde die reeks die grens op 39; vandaag staat
ze op **43 afgewikkelde van 60 kandidaten**, en het beeld is stabiel:

| | n afgewikkeld | trefkans | ROI | gem. geclaimde edge |
|---|---|---|---|---|
| viel af op `herijking` (gisteren) | 39 | 38,5% | −25,7% | +10,9 pp |
| **viel af op `herijking` (vandaag)** | **43** | **41,9%** | **−20,7%** | **+10,7 pp** |

Dat is de uitkomst die §5a als "blijft staan" definieert. Deze 43 selecties haalden alle acht
poorten op de ruwe kans — het zijn dus precies de bets die de routine vóór 5 september zou hebben
gespeeld — en ze verloren een vijfde van de inzet. De herijking heeft in die periode **8,9
eenheden** bespaard.

Twee dingen die erbij horen. Ten eerste dempt de reeks: −25,7% werd −20,7% met vier gevallen erbij,
wat laat zien hoe ruizig een getal op deze aantallen nog is. De richting is wat telt. Ten tweede,
en belangrijker: dit zegt iets over de **correctie**, niet over het model. Dat de routine geld
bespaart door haar eigen oude selecties niet meer te spelen, betekent dat die selecties slecht
waren — niet dat de nieuwe goed zijn. `ledger.py stats` staat nog altijd op −7,8% over 223
afgewikkelde bets en de markt schat nog altijd scherper (Brier 0,2362 tegen 0,2552).

### 3. De edge-poort staat na 207 afgewikkelde gevallen op +0,3% — en dat is de enige poort die niets bespaart

Het schaduwlogboek splitst per poort uit, en één regel wijkt af van alle andere:

| Poort | n afgewikkeld | ROI | oordeel van `shadow.py` |
|---|---|---|---|
| `odds` | 15 | −100,0% | bespaart 15,00u |
| `robuustheid` | 22 | −44,8% | bespaart 9,86u |
| `underdog_ruw` | 11 | −46,0% | bespaart 5,06u |
| `context` | 17 | −25,2% | bespaart 4,29u |
| `herijking` | 43 | −20,7% | bespaart 8,88u |
| `data` | 55 | −8,5% | bespaart 4,65u |
| `tweede_methode` | 74 | −1,6% | bespaart 1,16u |
| **`edge`** | **207** | **+0,3%** | **kostte 0,66u** |
| `underdog` | 9 | +34,8% | kostte 3,13u |

`edge` is met afstand de grootste reeks — 207 afgewikkelde gevallen, ruim boven de dertig die §6d
eist — en het is de enige grote reeks die op break-even staat in plaats van op verlies. Dat betekent
**niet** dat de drempel omlaag moet: §1g heeft dat op alle 552 afgerekende gevallen nagerekend en er
is geen drempel op de herijkte edge die geld oplevert. Wat het wél zegt, is dat de groep die net
onder de drempel valt niet meetbaar slechter is dan gemiddeld — dezelfde bevinding als de vlakke
rangorde bij `MAX_DEEP_ANALYSES`. De poort is dus geen filter dat kaf van koren scheidt maar een
rem op het aantal bets, en dat is precies hoe §1g hem ook verantwoordt: *"er is alleen een keuze
tussen weinig verlies en veel verlies"*.

De regel `underdog` (+34,8% over 9 gevallen) blijft te klein om te lezen, en dat verandert niet meer
vóór 25 september — zie Openstaand 2.

## Openstaand

1. **De contextmeting van Bevinding 1 verdient nu een gerichte vervolgvraag in plaats van meer
   data.** Concreet: splits het logboek op `lineupType`. Is de helling bij de duels met een
   **bevestigde** opstelling even groot als bij de voorspelde, dan pleit dat voor lezing 1 (een
   echte, onbeprijsde factor); is hij alleen zichtbaar bij de voorspelde, dan is het lezing 2 (een
   gedeelde bron). Dat is met de huidige 610 wedstrijden te doen en het kost geen enkele nieuwe
   waarneming. Pas daarna is de vraag "mag poort 7 een bijstelling worden" te beantwoorden, en dan
   nog op **uitkomsten**, niet tegen de markt.
2. **Poort 8 vervalt op 25 september** (§1e, besluit van de gebruiker van 18 september) en staat
   vandaag op **9** afgewikkelde `underdog`-rijen (+34,8%) en **11** `underdog_ruw`-rijen (−46,0%).
   Geen van beide haalt de dertig die §1e zelf eist, en dat gaat over zes dagen niet meer lukken.
   Vanaf 25 september neemt `poort8_vervallen` het over: leg per selectie `would_block` vast en
   noteer bij een gepubliceerde bet `"poort8_zou_hebben_geblokkeerd": true`.
3. **De uitdoofcurve van `early_season_uplift` tegen de blend van §4.** Gisteren viel de correctie
   op acht duels slechter uit, vandaag op veertig duels iets beter. Het teken klapt in beide
   gevallen door naar de andere kant. Meet dit op **uitkomsten** in plaats van tegen de markt, en
   meet de twee stappen samen in plaats van los — het vermoeden blijft dubbeltelling.
4. **De afkapping is voor het eerst bindend geweest en beide grensgevallen stonden op dezelfde
   score.** Bij 57 duels beslist de tie-break (aantal markten, dan aftrap) en niet de datarijkdom.
   Dat is geen defect — §3 Stage 4 zegt zelf dat de score niet scheidt — maar als de weekenden
   structureel boven de 55 uitkomen, is de vraag of de cap omhoog moet een tijdsvraag: deze run
   paste ruim vóór 06:30, dus daar is nog ruimte. Noteer de looptijd van elke run in
   `data/run-state/` onder `duur` en beslis het met die cijfers, niet met een schatting.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-09-19-run-a.md", "w").write(MD)
print("runs/2026-09-19-run-a.md geschreven:", len(MD), "tekens")
