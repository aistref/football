"""Bouwt runs/2026-09-18-run-b.md uit de vaste tekst plus de blokken die uit de repo komen.

De dekkingstabel en de wedstrijdsecties komen uit `tmp-run/rb18_md.py` (dat leest
`data/run-state/`), de statistiekblokken uit de `*.txt`-uitvoer die deze run is weggeschreven.
Overtypen is precies de fout die §5 en §6c benoemen.
"""
import json

P = json.load(open("tmp-run/rb18_parts.json"))
TXT = lambda p: open(p).read().rstrip()

DOC = f"""# Run B — 2026-09-18

**Gestart:** 05:08 CEST · **Bets gepubliceerd:** 0 · **Wedstrijden diep geanalyseerd:** 15 van 18 · **Afgekapt:** 0

Branch: de sessie startte op `claude/zealous-edison-pm4uw8`, maar alle commits van deze run staan
op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.

**Leesbaar dagrapport:** ARTIFACT_LINK

## Samenvatting in één alinea

De drukste Run B-dag sinds weken, en nul bets. Negen van de zeventien competities uit
`prompts/run-b.md` speelden, samen **achttien duels**, waaronder een volledige ronde van acht in de
Keuken Kampioen Divisie. Vijftien daarvan kwamen door de datadekkingspoort (4 `FULL`, 11 `LIGHT`);
drie kwamen op `NONE` uit — Rudeš – Slaven, Puskás – Kispest Honvéd en UTA Arad – Sepsi OSK — en
alle drie om dezelfde reden, die géén datareden is: er staat een ploeg in die vorig seizoen niet in
deze divisie speelde, en voor Kroatië, Hongarije en Roemenië kent `promotion.TIER2` geen gemeten
divisiepaar. De cap stond op 55 (vr–zo) tegen achttien duels, dus er is niets afgekapt. Uit de
vijftien doorgerekende duels kwamen **98 selecties over alle zes de markten** en nul bets. De
hoogste herijkte edge van de dag, +17,86 pp op Almere City FC, staat op de underdog-kant en is door
poort 8 tegengehouden; de hoogste die geen enkele poort raakte is Asian Handicap WSG Tirol +1,5 op
**+7,54 pp tegen een drempel van 8,0** — een half procentpunt tekort.

## Stage -2 — Branches

De branchcontrole is als allereerste handeling uitgevoerd, vóór het lezen van deze regels.
`git fetch origin` bracht **32 takken** naast `main` in beeld.

De eerste telling, op de ondiepe kloon waarmee de container start
(`git rev-parse --is-shallow-repository` → `true`), gaf **26 takken met 4 tot 184 "eigen"
commits**. Dat is het valse alarm waar Stage -2 expliciet voor waarschuwt: bij een ondiepe kloon
ligt het punt waarop de takken uiteenliepen vóór de knip, dus telt élke commit van vóór die knip
mee als "nog niet hier".

Na `git fetch --unshallow origin` (320 commits geschiedenis) staat de teller op **0 van de 32** —
geen enkele tak bevat een commit die `main` niet heeft.

Dat is óók op inhoud nagetrokken, want daar gaan de conflictregels van Stage -2 over. Over **alle**
32 takken is per tak `data/picks.jsonl` uitgelezen en op `id` vergeleken met die van `main`:
**nul pick-ids die alleen op een tak staan**. Hetzelfde voor de bronnen in
`data/source-health.json` en de competities in `data/coverage.json`: het enige dat op takken staat
en niet op `main` is de bron `oddspapi` plus `scripts/oddspapi.py` en `data/odds-fallback.json`, en
die zijn op 31 aug 2026 bewust verwijderd ("OddsPapi-reserve verwijderd na overstap naar
20K-plan"). `main` is dus een strikte superverzameling en er viel niets te verenigen.

Er staan ook geen openstaande picks van een run die op een andere tak nooit is afgewikkeld:
`ledger.py open` gaf "Geen picks klaar om af te wikkelen" en `shadow.py open` alleen de vier
schaduwpicks van Run A van vanochtend, van wedstrijden die vandaag nog gespeeld moeten worden.

De sessie kreeg `claude/zealous-edison-pm4uw8` toegewezen; die tak stond exact gelijk aan `main`.
Er is lokaal naar `main` overgeschakeld en alles is met `git push origin HEAD:main` gepusht.

## Bronstatus deze run

Uitvoer van `python3 scripts/api_check.py`, letterlijk (§3, Stage 3):

```
{P['api']}
```

**Wat daaruit volgt.** `API_FOOTBALL_KEY` is **niet gezet** — ontbrekend, niet afgewezen:
`api_check.py` slaat de bron over zonder HTTP-verzoek. Dat is onveranderd sinds de eerste run en
geen nieuwe blokkade. Gevolg voor deze run: **geen enkel duel is hierdoor op `NONE` uitgekomen.**
De kansinput kwam van Fotmob, en de drie `NONE`-duels zijn een ontbrekend divisiepaar en geen
ontbrekende sleutel. The Odds API is in orde met 19.081 credits over.

| Bron | Status | Detail deze run |
|---|---|---|
| Fotmob | `ok` | daglijst (9 competities met wedstrijden), standen vorig + lopend seizoen voor alle negen, context voor alle 18 duels, stadioncontrole — alles zonder fout |
| BetExplorer | `ok` | negen slugs opgehaald, **acht raak**; `albania/abissnet-superiore` gaf 0 rijen |
| The Odds API | `ok` | 19.081 over; 15 credits uitgegeven (4× bulk à 3 + 3× BTTS à 1 halve ronde van 2) |
| API-Football | `key_missing` | sleutel niet in de omgeving van de geplande taak (README → "Sleutels toevoegen") |
| Understat | niet aangeroepen | dekt alleen de vijf grote competities; geen daarvan staat op de runlijst van Run B |

**Eén verandering ten opzichte van de vorige run, en het is er een om in de gaten te houden.** De
BetExplorer-slug `albania/abissnet-superiore` gaf sinds 23 aug 2026 gewoon rijen; vandaag geeft hij
er **nul** — geen HTTP-fout, gewoon een lege tabel. Gevolg: Vllaznia – Teuta Durrës kwam wél door de
kansenkant (`LIGHT` op doelpunten uit de stand van 2025/2026) maar bleef helemaal zonder koers, en
is dus niet doorgerekend. Met één waarneming is niet te zeggen of de pagina verhuisd is of dat de
competitie er tijdelijk niet op staat; het staat genoteerd in `data/coverage.json` met de opdracht
er volgende ronde opnieuw naar te kijken.

Uitvoer van `CreditGuard.report()` (§1a), beide rondes:

```
12 van 733 credits gebruikt in 4 aanroep(en), nog 19069 over
3 van 721 credits gebruikt in 3 aanroep(en), nog 19066 over
```

## Dekkingsrapportage

{P['cov']}

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 wedstrijden. De cap staat op 55 (vr–zo) tegen achttien
duels. Datarijkdom liep van **4,5** (FC Den Bosch – Helmond Sport en Vllaznia – Teuta Durrës) tot
**8,0** (beide Roemeense duels). "Laagste die het haalde" en "hoogste die afviel" zijn allebei leeg
— er viel niets af.

## Drie duels op `NONE`, en waarom dat geen datagat is

Rudeš (Croatian HNL), Kispest Honvéd (Hungarian NB I) en Sepsi OSK (Romanian SuperLiga) staan geen
van drieën in de stand van 2025/2026 van hun eigen competitie. §4 schrijft voor zo'n ploeg **eerst
de omrekening uit de divisie eronder** voor en pas daarna `NONE`. Die omrekening kon hier niet:
`promotion.TIER2` kent dertien divisieparen en Kroatië, Hongarije en Roemenië zitten daar geen van
drieën bij, dus `promotion.convert` gooit meteen *"geen divisie boven of onder … bekend"*.

**Dat is de regel die werkt zoals hij bedoeld is, en het is nadrukkelijk geen reden om een factor te
verzinnen.** `promotion.MEASURED_TIER2_GAP` is op 31 aug 2026 gemeten voor NED, DEN, POR, BEL, TUR
en POL over de seizoenen 2016/2017 t/m 2024/2025. Buiten die landen is er geen meting en dus geen
onafhankelijke kansinput op het niveau waarop gespeeld wordt — precies de Coventry-val waar
`conversion_in_range` voor is gemaakt: een geraden of gepoolde factor levert schijnedge op die alle
andere poorten haalt.

**Wat het kost, en wat het zou kosten om het op te lossen.** Vandaag drie van de achttien duels. Dit
is geen eenmalig geval: alle drie die competities staan vast op `LIGHT` (geen Fotmob-xG) en hebben
elk promovendi, dus elke speelronde valt hier wel een duel af. De oplossing is een meting in de
geest van 31 aug — de tweede divisie van die drie landen bij Fotmob ophalen over meerdere seizoenen
en het gat meten met `promotion.measure_gap` — en dat is werk voor een aparte sessie, niet voor een
dagelijkse run. Het hoort pas in `TIER2` als het gemeten is. Zie "Openstaand" onderaan.

## De omrekeningen die wél konden (§4)

Drie degradanten, alle drie binnen het gemeten bereik en dus doorgerekend — op `LIGHT`, want een
omgerekende ploeg is nooit `FULL`:

| Ploeg | Uit | Relatief (aanval / verdediging) | Factor | Na omrekening | Bereik |
|---|---|---|---|---|---|
| Wolfsburg | Bundesliga → 2. Bundesliga | 0.818 / 1.255 over 34 duels | D1/D2 **gemeten**, ×1.777 / ×0.743 | 1.454 / 0.932 | binnen (n=23) |
| Heracles | Eredivisie → KKD | 0.648 / 1.574 over 34 duels | **gepoold**, ×1.654 / ×0.647 | 1.072 / 1.018 | binnen (n=240) |
| FC Volendam | Eredivisie → KKD | 0.648 / 1.019 over 34 duels | **gepoold**, ×1.654 / ×0.647 | 1.072 / 0.659 | binnen (n=240) |

De twee Nederlandse leunen op de **gepoolde** factor: Eredivisie/KKD staat niet apart in
`promotion.MEASURED_TIER2_GAP`. Dat is toegestaan — `conversion_in_range` staat open — maar het is
de zwakste variant, en beide duels kwamen vandaag hoe dan ook niet in de buurt van een bet.

## Stadioncontrole

`context.check_venue` sloeg één keer aan: **Jong AZ Alkmaar – FC Volendam** wordt gespeeld op het
AFAS Trainingscomplex in Wijdewormer en niet in het AFAS Stadion, dat Fotmob als eigen stadion van
AZ noteert. Dat is geen verplaatsing maar de normale gang van zaken voor een beloftenelftal — de
controle vergelijkt het speelstadion met dat van de hoofdmacht. Poort 7 stond er hoe dan ook open
voor (de drie selecties in dat duel zijn 1X2 zonder kant of met een kant die niets mist) en er was
geen bet. Het staat hier omdat §1c vraagt de stadioncontrole ook te melden als de poort opengaat.

## Wedstrijden

{P['secs']}

## De drie duels die ertoe deden

### Rapid Wien – WSG Tirol · 19:30 · Austrian Bundesliga (AUT) — `FULL`, 13 selecties

| Markt — selectie | Koers | Herijkte kans | Herijkte edge | Ruwe kans | Ruwe edge | xG-model | 2e methode | Valt af op |
|---|---|---|---|---|---|---|---|---|
| 1X2 — 2 (WSG Tirol wint) | 8.06 | 21.3% | +8.85 pp | 26.6% | +14.18 pp | +13.74 | +15.90 | `odds` |
| Asian Handicap — WSG Tirol +1.5 | 1.97 | 58.3% | **+7.54 pp** | 72.5% | +21.71 pp | +20.41 | +26.92 | `edge` |
| 1X2 — X (gelijkspel) | 5.80 | 19.6% | +2.32 pp | 24.2% | +6.94 pp | +6.21 | +9.84 | `edge` |
| Over/Under — Under 2.5 | 2.88 | 31.4% | −3.30 pp | 40.7% | +5.94 pp | +3.22 | +16.84 | `edge` |
| Over/Under — Under 3.5 | 1.86 | 49.2% | −4.57 pp | 62.8% | +9.07 pp | +6.44 | +19.60 | `herijking` |
| Over/Under — Under 3.25 | 1.99 | 44.5% | −5.80 pp | 57.3% | +7.07 pp | +4.41 | +17.69 | `edge` |
| BTTS — ja | 1.70 | 47.3% | −11.55 pp | 60.6% | +1.81 pp | +3.74 | −5.90 | `edge` |
| BTTS — nee | 2.32 | 30.5% | −12.64 pp | 39.4% | −3.74 pp | −5.67 | +3.98 | `edge` |
| 1X2 — 1 (Rapid Wien wint) | 1.36 | 37.9% | −35.46 pp | 49.2% | −24.15 pp | −22.99 | −28.78 | `edge` |

*(vier Over/Under- en handicaplijnen met een nog lagere edge weggelaten; ze staan volledig in
`data/run-state/2026-09-18-run-b.json`.)*

**Dit is het duel van de dag, en het laat alle drie de meetreeksen tegelijk zien.** De handicap
WSG Tirol +1,5 haalt élke poort behalve de edge-poort en komt **een half procentpunt tekort**
(+7,54 tegen 8,0). De uitwinst zelf zou meer edge hebben (+8,85 pp) maar staat op 8,06 en valt dus
buiten de koersband van 1,30–6,00 — poort 2 sluit dat af, en dat is geen toeval: dat is precies het
gebied waar de kansschatting te onnauwkeurig wordt om edge zinvol te noemen.

Op de **ruwe** schaal, zonder de herijking van §1g, ziet dezelfde selectie er heel anders uit:
+21,71 pp, en dan bindt poort 8 er wél op, want de markt geeft WSG Tirol 12,7% tegen 70,2% voor
Rapid. Die twee lezingen staan daarom als twee aparte rijen in het schaduwlogboek — een `near_miss`
op de herijkte schaal en een `underdog_ruw`-rij op de ruwe — en `shadow.py collect` slaat de
dubbeltelling zelf over. Daarnaast levert dit duel een `zonder_herijking`-rij: Under 3.5 @ 1.86,
ruw +9,07 pp en herijkt −4,57 pp.

### Almere City FC – Heracles · 20:00 · Keuken Kampioen Divisie (NED) — `LIGHT`, 3 selecties

| Markt — selectie | Koers | Herijkte kans | Herijkte edge | Ruwe kans | Ruwe edge | xG-model | 2e methode | Valt af op |
|---|---|---|---|---|---|---|---|---|
| 1X2 — 1 (Almere City FC wint) | 3.10 | 50.1% | **+17.86 pp** | 63.9% | +31.60 pp | +30.41 | +36.38 | `underdog` |
| 1X2 — X (gelijkspel) | 3.92 | 15.2% | −10.34 pp | 18.1% | −7.46 pp | −7.02 | −9.25 | `edge` |
| 1X2 — 2 (Heracles wint) | 1.96 | 15.2% | −35.82 pp | 18.1% | −32.93 pp | −32.18 | −35.92 | `edge` |

**De hoogste edge van de dag, en de enige selectie die poort 8 deze run heeft tegengehouden.** De
markt geeft Almere 29,7% tegen 46,9% voor Heracles; dat is onder `sides.UNDERDOG_FLOOR` = 0.35, dus
de poort gaat dicht. De drie getallen die §5 eist staan er allemaal en wijzen dezelfde kant op —
xG-model +30,41, splitsmethode +36,38, zwakste stand van het (shrink, rho)-grid **+28,28** — dus dit
is niet één poort tegen een wankele schatting maar een selectie die op elk ander punt overeind blijft.

Dat maakt hem juist een goede meting voor 25 september, wanneer §1e poort 8 wil herzien. Let wel op
de bron van het verschil: Heracles is een **omgerekende** degradant op de gepoolde
Eredivisie/KKD-factor, en dat is de zwakste invoer die deze run gebruikt heeft. Een edge van dertig
procentpunt op de zwakkere kant bij een omgerekende tegenstander is exact het patroon waar §1g voor
waarschuwt: de grootste geclaimde edge is meestal de grootste modelfout.

### Albacete – Córdoba · 20:30 · Segunda División (ESP) — `FULL`, 13 selecties

De doelpuntenmarkt geeft hier twee selecties die op de ruwe schaal ruim boven de drempel uitkomen en
na de herijking negatief staan: Over 2.75 @ 1.90 (ruw +8,30, herijkt −5,11) en Over 2.5 @ 1.73
(ruw +8,29, herijkt −5,66). Alleen de hoogste van de twee gaat als `zonder_herijking`-rij het
schaduwlogboek in — §5a regel 2, één rij per wedstrijd — met `edge_robust_min` +5,94.

## Topselectie

**Geen.** Er is nul bets gepubliceerd, dus er valt niets te rangschikken. §5: *"Zijn er minder
gekwalificeerde bets dan `MAX_SHORTLIST`? Lever er minder. Vul niet aan."*

De twee ranglijsten van §5a (`scripts/toplist.py --run b --date 2026-09-18`):

```
{TXT('tmp-run/rb18_top.txt')}
```

**Lees de tweede lijst zoals §5a hem bedoelt: als meting, niet als tip.** De bovenste twee daar zijn
allebei door poort 8 tegengehouden en de derde alleen door de herijking. Wat de lijst laat zien is
wat de routine vóór 5 september zou hebben gespeeld — en §1g heeft op 552 afgerekende gevallen
gemeten dat juist de hoogste geclaimde edge het slechtste rendement geeft.

### Net niet

| Wedstrijd | Markt — selectie | Koers | xG-model | 2e methode | Zwakste stand | Herijkt | Valt af op |
|---|---|---|---|---|---|---|---|
| Rapid Wien – WSG Tirol | Asian Handicap — WSG Tirol +1.5 | 1.97 | +20,41 | +26,92 | +18,00 | +7,54 pp | `edge` |
| Almere City FC – Heracles | 1X2 — 1 (Almere City wint) | 3.10 | +30,41 | +36,38 | +28,28 | +17,86 pp | `underdog` |
| Albacete – Córdoba | Over/Under — Over 2.5 | 1.73 | +7,07 | +13,17 | +5,94 | −5,66 pp | `herijking` |
| Rapid Wien – WSG Tirol | Over/Under — Under 3.5 | 1.86 | +6,44 | +19,60 | +4,71 | −4,57 pp | `herijking` |

Alle vier de rijen staan in `data/shadow.jsonl` en worden daar net zo afgerekend als een echte pick
(§6d). Bij geen van de vier was het tekort breed: de zwakste stand van het (shrink, rho)-grid is
overal positief, dus poort 6 speelde nergens een rol.

De verdeling van de 98 selecties over de poorten, op beide schalen:

| Poort | Herijkte schaal | Ruwe schaal |
|---|---|---|
| 1 — edge onder de drempel | 92 | 90 |
| 2 — koers buiten 1.30–6.00 | 2 | 2 |
| 5 — tweede methode | 0 | 1 |
| 6 — robuustheid | 0 | 0 |
| 7 — context | 0 | 0 |
| 8 — underdog | 1 | 2 |
| alleen de herijking | 3 | — |
| **haalt alle acht** | **0** | **3** |

## Marktbalans (§1a — controle op de inkoop, niet op de uitkomst)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 (beste prijs waar mogelijk, anders marktgemiddelde) | 6 van 9 | 41 | 0 |
| Asian Handicap | 4 van 9 | 14 | 0 |
| Draw No Bet (0.0-lijn) | 2 van 9 | 4 | 0 |
| Double Chance (±0.5-lijn) | 1 van 9 | 1 | 0 |
| Over/Under | 4 van 9 | 32 | 0 |
| BTTS | 3 van 9 — tweede ronde, kandidaat-edge | 6 | 0 |

**De controle slaagt ruim en toch is dit de eerlijkste regel van het hele rapport: de dekking is
scheef, en niet door de portemonnee.** §1a eist minstens één competitie met een doelpuntenmarkt én
minstens één met een uitkomstmarkt; er zijn er vier van allebei. Maar vier van de negen spelende
competities hebben een sportkey bij The Odds API en vijf niet (Kroatië, Hongarije, Roemenië, Keuken
Kampioen Divisie, Kategoria Superiore). Voor die vijf is het BetExplorer-marktgemiddelde de enige
1X2-bron, en dat betekent **drie selecties per duel in plaats van elf tot negentien**. Tien van de
vijftien doorgerekende duels staan daardoor op een marktgemiddelde zonder handicap-, doelpunten- of
BTTS-markt. Dat is geen creditprobleem — er is 718 van de 733 credits ongebruikt gebleven — maar een
dekkingsprobleem aan de bronkant, en het staat als zodanig in `markets_checked` bij elk van die
duels.

De beste prijs leverde op de vier duels waar beide bronnen een koers gaven gemiddeld **+5,50%** op
ten opzichte van het BetExplorer-marktgemiddelde: +9,30% (Sarpsborg – KFUM), +5,41% (Rapid Wien),
+5,12% (Albacete), +3,88% (Greuther Fürth) en +3,81% (Wolfsburg). In lijn met de +7,78% van de
meting op 5 sep. Een deel van die beste prijzen stond bij een **beurs** (Betfair, Matchbook) en is
door `oddsapi.net_price` gehaald — bij Rapid Wien – WSG Tirol stonden alle drie de 1X2-uitkomsten
bij een beurs.

BTTS is in de tweede ronde gekocht voor drie van de vier duels met een kandidaat-edge (Albacete,
Greuther Fürth, Rapid Wien). Het vierde, Almere City – Heracles, kon niet: de Keuken Kampioen
Divisie heeft geen sportkey. Dat staat zo in `markets_checked`, met de reden erbij en niet als gat.

`python3 scripts/progress.py verify --run b --date 2026-09-18` is groen: *"Alle 15 geanalyseerde
wedstrijd(en) hebben alle zes markten gehad."*

## Vroeg-seizoenscorrectie

`early_season_uplift` komt uit op **×1.1027** (gepoold 1.1143 over **71 speeldagen in 9
competities**) — de ruimste steekproef die deze routine tot nu toe heeft gehad. Dat komt doordat ook
de vijf competities zónder Fotmob-xG meetellen, daar op **doelpunten** gemeten: dat is de eenheid
waarin die duels sowieso rekenen, dus teller en noemer staan gelijk en er komt geen bookmakerprijs
aan te pas.

**De controle tegen de markt valt deze keer ongunstig uit, en dat hoort hier te staan.**

| | gemiddelde afwijking | gem. absolute fout |
|---|---|---|
| zonder correctie | −3,59 pp | 5,35 pp |
| met correctie ×1.1027 | +2,81 pp | 7,03 pp |

De correctie schiet dus door: hij haalt de onderschatting weg en zet er een overschatting voor in de
plaats, en de absolute fout loopt op. **Maar dit is gemeten over vier wedstrijden** — alleen de
duels waar beide kanten van de 2.5-lijn een prijs hebben, en dat zijn precies de vier ingekochte
competities — en bij vier waarnemingen is dit ruis, geen bevinding. Het staat hier zodat een
volgende run kan zien of het patroon terugkomt; het is nadrukkelijk **geen** reden om aan
`prior_matchdays` te draaien, want dat zou de correctie op de markt afregelen en dat verbiedt §2.

## Schaduwlogboek (§6d)

Vier nieuwe rijen deze run (1 `underdog`, 1 `underdog_ruw`, 2 `herijking`); het logboek staat op
488. Uitvoer van `python3 scripts/shadow.py stats`:

```
{TXT('tmp-run/rb18_shadow_head.txt')}
```

```
{TXT('tmp-run/rb18_shadow.txt')}
```

**Twee dingen om hier te lezen, en allebei met de waarschuwing van §6d ernaast.**

1. **De poort-8-reeks groeit, maar haalt 25 september niet.** `underdog` staat op 9 kandidaten
   (8 afgewikkeld, ROI **+12,9%**) en `underdog_ruw` op 11 (9 afgewikkeld, ROI **−34,0%**). Beide
   liggen ver onder de ≥ 30 afgewikkelde gevallen die §1e zelf eist, en ze wijzen bovendien
   tegengesteld — wat precies illustreert waarom die twee reeksen niet bij elkaar opgeteld mogen
   worden. Met nog een week te gaan en ongeveer één rij per dag komt de herziening van 25 september
   met een reeks van rond de vijftien aan. Dat is een voorspelling, geen verwijt: de regel is op
   15 september al een keer aangepast om deze reeks sneller te laten groeien.
2. **De edge-poort staat op +0,3% over 207 afgewikkelde kandidaten.** Dat is de enige poort met een
   positieve ROI en dus de enige die geld zou kúnnen kosten in plaats van besparen. Bij +0,66u over
   207 is dat statistisch niets, maar het is de reeks om over enkele weken opnieuw naar te kijken.

## Contextlogboek (§1c)

Uitvoer van `python3 scripts/ctxlog.py stats`:

```
{TXT('tmp-run/rb18_ctxstats.txt')}
```

Twaalf nieuwe wedstrijden toegevoegd; het logboek staat op 616. **Er is hier voor het eerst iets te
zien, en het is niet wat je zou willen.** Zowel het model als de markt staat nu op t ≈ −2,2 tegen het
beschikbaarheidsverschil — de grens die §1c zelf als drempel noemt — maar de hellingen zijn vrijwel
identiek (−26,3 pp voor het model tegen −25,7 pp voor de markt). Dat betekent: het effect bestaat
misschien, maar de markt prijst het even goed in als het model het mist. Er valt dus niets te
winnen met een bijstelling, en poort 7 blijft een rem. Zie §1c: *"Een getal verzinnen omdat het
plausibel klinkt is exact wat §2 en §4 verbieden."*

## Kalibratielogboek (§6e)

Uitvoer van `python3 scripts/calibration.py stats`:

```
{TXT('tmp-run/rb18_calib_head.txt')}
```

Achtentwintig waarnemingen erbij vandaag, op **−0,21 pp** in de longshotbak — de eerste dag sinds
8 september die daar niet positief uitkomt, en met 28 waarnemingen is dat ruis. De hoofdregel
verschuift niet: over 727 longshot-waarnemingen staat `my_prob` op **+2,03 pp** boven de markt en op
favorieten op **−3,94 pp**, en de splitsmethode blijft de scheefste van de twee.

## Afwikkeling vorige picks

**Geen.** `ledger.py open` gaf "Geen picks klaar om af te wikkelen" — er stond niets open. `shadow.py
open` gaf alleen de vier schaduwpicks die Run A vanochtend heeft aangemaakt, van wedstrijden die
vandaag nog gespeeld moeten worden ("bron meldt nog niet afgelopen"). Run A van vanochtend had de
picks en schaduwpicks van 17 september al afgewikkeld.

## Stand van het logboek

Uitvoer van `python3 scripts/ledger.py stats`:

```
{TXT('tmp-run/rb18_ledger_head.txt')}
```

Uitvoer van `python3 scripts/recalibrate.py show` (§1g) — de fit waarmee vandaag is gerekend:

```
{TXT('tmp-run/rb18_recal.txt')}
```

De fit staat nu op **a=0.829, b=−0.467 over 680 afgerekende gevallen**: het model zegt gemiddeld
52,0% en het gebeurt 40,7% van de tijd. Op een kans van 60% haalt de correctie 13,3 procentpunt
weg. Dat is de reden dat er vandaag drie selecties zijn die ruw alle acht poorten halen en herijkt
niet.

## Openstaand

1. **Geen divisiepaar voor Kroatië, Hongarije en Roemenië** (nieuw vandaag, kostte drie duels). De
   oplossing is een meting zoals die van 31 aug 2026: de tweede divisie van die drie landen bij
   Fotmob ophalen over meerdere seizoenen en het gat meten met `promotion.measure_gap`, daarna in
   `MEASURED_TIER2_GAP`. Werk voor een aparte sessie; niet raden, meten.
2. **BetExplorer Albanië staat weer op nul rijen.** Volgende speelronde opnieuw proberen. Blijft hij
   leeg, dan is de doorbraak van 23 aug teruggedraaid en is Kategoria Superiore terug bij "kansen
   wel, prijzen niet".
3. **Vijf van de negen spelende competities zijn niet in te kopen bij The Odds API.** Dat is geen
   creditprobleem (718 van 733 ongebruikt) maar een dekkingsprobleem, en het maakt tien van de
   vijftien doorgerekende duels structureel armer: 1X2 op een marktgemiddelde, geen handicap, geen
   doelpuntenmarkt, geen BTTS. Voor de Keuken Kampioen Divisie — acht duels vandaag — is dat het
   meest zichtbaar.
4. **De poort-8-reeks haalt 25 september niet.** Zie hierboven: `underdog` staat op 8 afgewikkelde
   gevallen tegen de ≥ 30 die §1e eist. De herziening zal dus moeten kiezen tussen uitstellen en
   beslissen op te weinig waarnemingen; uitstellen is verdedigbaar, beslissen op vijftien gevallen
   niet.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-09-18-run-b.md", "w").write(DOC)
print("runs/2026-09-18-run-b.md geschreven:", len(DOC), "tekens")
