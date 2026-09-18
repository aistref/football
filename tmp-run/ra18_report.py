"""Bouwt runs/2026-09-18-run-a.md: handgeschreven tekst + de blokken die uit de scripts komen.

Overtypen is de fout die §5 en §6c allebei benoemen, dus de dekkingstabel, de wedstrijdsecties en
alle stats-uitvoer worden hier ingelezen in plaats van herhaald.
"""
import subprocess, os

S = os.environ["SCRATCH"]
cov = open("tmp-run/ra18_coverage.md").read()
secs = open("tmp-run/ra18_matches.md").read()


def cap(path, n=None):
    t = open(path).read().rstrip("\n")
    return t


api = cap(f"{S}/api_check.txt")
toplist = cap(f"{S}/toplist.txt")
ledger = cap(f"{S}/ledger.txt")
shadow = cap(f"{S}/shadow.txt")
recal = cap(f"{S}/recal.txt")
calib = cap(f"{S}/calib.txt")
ctx = cap(f"{S}/ctx.txt")

MD = f"""# Run A — 2026-09-18

**Gestart:** 04:09 CEST · **Afgerond:** 04:52 CEST · **Looptijd:** 43 minuten · **Bets gepubliceerd:** 0 · **Wedstrijden diep geanalyseerd:** 12 van 12 · **Afgekapt:** 0

De run is niet onderbroken (`resumed_count` = 0). Drieënveertig minuten voor twaalf duels in elf
competities — ruim binnen 06:30, maar wel bijna drie keer zo lang als gisteren, en de reden is de
inkoop: elf bulk-aanroepen en elf BetExplorer-slugs in plaats van drie.

Branch: de sessie startte op `claude/stoic-davinci-asab4o`, maar alle commits van deze run staan
op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.

**Leesbaar dagrapport:** https://claude.ai/artifact/23F8XjSmB6k3VoLPP8p3BA

## Samenvatting in één alinea

Vrijdag 18 september, en voor het eerst sinds weken speelt bijna de hele binnenlandse runlijst
tegelijk: **elf van de eenentwintig** competities hadden een duel, samen **twaalf** (de Ekstraklasa
twee, de rest één). De tien overige stonden niet op de kalender — de Europese speelweek was
woensdag en donderdag afgelopen — en dat is `GEEN WEDSTRIJD`, geen storing. De cap van 55
(vrijdag t/m zondag) kwam niet in de buurt: **nul afgekapt**. Alle twaalf duels kwamen door de
datadekkingspoort (**8 `FULL`, 4 `LIGHT`**, geen enkele `NONE`) en zijn over alle zes de markten
doorgerekend: **171 selecties, nul bets**. Vier ploegen zijn omgerekend uit de divisie eronder —
Monza, Lyngby, Wieczysta Kraków, en Wisła Kraków plus Śląsk Wrocław — en die vier bepalen welke
duels `LIGHT` zijn. De inkoop kan de uitkomst niet hebben veroorzaakt: alle elf competities hebben
een sportkey, alle elf kregen de volle bulk-aanroep, en de vijf duels met een kandidaat-edge kregen
daarbovenop BTTS — **38 van 734 credits**, marktbalans 11 op 11. De hoogste herijkte edge staat op
**+4,50 pp** tegen een `LIGHT`-drempel van 16,0; op een `FULL`-duel is de hoogste **+3,71 pp**
tegen 8,0. Ruw zijn er 79 positieve edges met +17,52 pp bovenaan. Onder **Bevindingen** staan drie
dingen: de bekerregel van 15 september is vandaag teruggebracht tot bekers omdat hij een
competitieduel in de verkeerde divisie doorrekende, de herijkingsreeks van §5a is voor het eerst
groot genoeg om te lezen, en de vroeg-seizoenscorrectie maakt de schatting vandaag aantoonbaar
slechter in plaats van beter.

## Stage -2 — Branches

De branchcontrole is als eerste handeling uitgevoerd, vóórdat `_shared-rules.md` is gelezen.
`git fetch origin` bracht **31 takken** naast `main` in beeld (vier nieuwe sinds gisteren), en op
de eerste telling hadden er **24** tussen de 4 en 184 commits die `HEAD` niet had.

Dat was het **valse ondiep-kloonalarm** waar §3 Stage -2 voor waarschuwt, en deze keer letterlijk:
de container leverde de repo opnieuw als ondiepe kloon aan (`git rev-parse
--is-shallow-repository` → `true`, 61 commits lokaal). Na `git fetch --unshallow origin` staat
`main` op **318** commits en is het beeld compleet anders:

| | ondiep (61 commits lokaal) | na `--unshallow` (318) |
|---|---|---|
| takken met "eigen" commits | 24 van de 31 (4 t/m 184 stuks) | **0 van de 31** |

Er viel dus **niets te mergen** en geen enkele conflictregel hoefde te worden toegepast. Dat was
vóór het unshallowen al op **inhoud** nagegaan, en die controle wees dezelfde kant op:

| Controle over alle takken met "eigen" commits | Uitkomst |
|---|---|
| picks met een id dat niet in `main` staat | **0** — `main` telt 274 regels en is de vereniging van alle takken; de takken met tekstueel afwijkende regels (`xw8dsg` 7, `38pm7k` 35) wijken af doordat `main` diezelfde picks intussen heeft afgewikkeld |
| takken die inhoudelijk vóórliggen op `main` | **0** — elke tak met een afwijkend bestand is een snapshot van een oudere `main` |
| openstaande picks van een run die op een andere tak nooit is afgewikkeld | **0** — `ledger.py open` gaf niets, `picks.jsonl` telt 0 open regels op 274 |

**Les voor de volgende run:** `--unshallow` staat in §3 Stage -2 als *eerste* commando en het is
vandaag pas ná de inhoudelijke controle gedraaid. Die volgorde kostte het handwerk dat die
paragraaf nu juist wil besparen — precies wat er op 19 en 20 augustus ook gebeurde. De run draait
op `main` en alle commits gaan erheen.

## Stage 0 — Afwikkelen

`ledger.py open` gaf **niets**: alle 274 picks in het logboek zijn afgewikkeld. `shadow.py open`
gaf **vijf** schaduwpicks van Run A van 17 september, alle vijf afwikkelbaar volgens de statusregel
van §0 (`finished` van de bron, niet de klok). Alle vijf zijn Europa League-duels in de
competitiefase, dus zonder verlenging of strafschoppen: de eindstand ís de stand na 90 minuten.

| Schaduwpick | Uitslag | Resultaat |
|---|---|---|
| Levski Sofia – Salzburg · AH Levski +0.25 @ 1.95 (`underdog_ruw`) | 0–1 | **verloren** |
| Beşiktaş – Marseille · 1X2 Marseille @ 4.33 (`edge`) | 4–1 | **verloren** |
| Beşiktaş – Marseille · AH Marseille +0.75 @ 1.90 (`underdog_ruw`) | 4–1 | **verloren** |
| Celtic – Ferencváros · 1X2 Ferencváros @ 4.63 (`edge`) | 1–3 | **gewonnen** |
| Celtic – Ferencváros · AH Ferencváros +1 @ 1.71 (`underdog_ruw`) | 1–3 | **gewonnen** |

Twee gewonnen, drie verloren. De `underdog_ruw`-reeks staat daarmee op 9 afgewikkelde gevallen
(−34,0%) en de reeks van poort 8 op de herijkte schaal nog altijd op 8 (+12,9%) — allebei ver onder
de dertig die §1e vraagt. `ctxlog.py settle` wikkelde dezelfde dag twaalf contextwedstrijden af.

## Bronstatus deze run

Letterlijke uitvoer van `python3 scripts/api_check.py`:

```
{api}
```

**`API_FOOTBALL_KEY` ontbreekt nog steeds** — niet afgewezen, maar niet gezet in de omgeving van de
geplande taak. `api_check.py` slaat de bron over zonder HTTP-verzoek. Gevolg voor deze run: geen.
De kansinput kwam van Fotmob en Understat, en dat vier duels `LIGHT` zijn komt door de
promovendi-omrekeningen (§4) en niet door deze sleutel. Zie `README.md` → "Sleutels toevoegen".

| Bron | Status | Detail deze run |
|---|---|---|
| Fotmob | `ok` | daglijst 11 Run A-competities, alle elf met xG in vorig én lopend seizoen; context voor alle 12 duels zonder fout (7× voorspelde opstelling, 5× laatste basiself); `check_venue` meldde géén verplaatsing |
| The Odds API | `ok` | 19.119 credits over, 881 gebruikt deze maand, 45 actieve voetbalcompetities |
| BetExplorer | `ok` | elf slugs, alle elf raak — 158 rijen waarvan 12 vandaag |
| Understat | `ok` | vijf competities (EPL, Serie_A, La_liga, Bundesliga, Ligue_1), alleen voor het kalibratieblok |
| API-Football | `key_missing` | sleutel niet gezet; ongewijzigd sinds 8 aug 2026 |

Wijzigingen t.o.v. vorige run: **geen.** Eén bron kwam er feitelijk bij in beeld zonder dat hij
faalde: de **I Liga (POL, Fotmob 197) heeft geen xG**. Dat is geen storing maar het is wel de reden
dat de correctie onder Bevinding 1 nodig was.

## Dekkingsrapportage

{cov}

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 wedstrijden. De cap staat op 55 (vrijdag) tegen 12
kandidaten. De datarijkdom liep van 5,0 (Kasımpaşa – Konyaspor) tot 7,0 (Brentford – Chelsea en
Bayern München – Union Berlin); omdat er niets is afgekapt zijn "laagste die het haalde" en
"hoogste die afviel" allebei leeg.

## Omrekeningen

Vier promovendi, geen enkele kruis-grens (de Europese toernooien speelden niet). Alle vier vielen
binnen het gemeten bereik van `conversion_in_range`, en alle vier leveren `LIGHT` op — een
omgerekende ploeg is nooit `FULL`, want de omrekening haalt de systematische fout eruit en niet de
onzekerheid.

| Ploeg | Uit | Relatief in die divisie | Factor | Na omrekening |
|---|---|---|---|---|
| Monza | Serie B (ITA), 38 duels | aanval 1.254 / verdediging 0.658 | ×0.601 / 1.528 (gemeten paar I1/I2) | 0.754 / 1.005 |
| Lyngby | 1. Division (DEN), 22 duels | 1.620 / 0.826 | ×0.624 / 1.807 (eigen meting 31 aug) | 1.011 / 1.493 |
| Wieczysta Kraków | I Liga (POL), 34 duels | 1.383 / 0.929 | ×0.680 / 1.743 (eigen meting 31 aug) | 0.941 / 1.619 |
| Wisła Kraków | I Liga (POL), 34 duels | 1.423 / 0.632 | ×0.680 / 1.743 | 0.967 / 1.102 |
| Śląsk Wrocław | I Liga (POL), 34 duels | 1.363 / 0.929 | ×0.680 / 1.743 | 0.927 / 1.619 |

Wieczysta Kraków en Śląsk Wrocław komen met een omgerekende verdediging van 0.929 **precies op de
bovengrens** van het gemeten bereik (0.505–0.929) uit. Dat is binnen bereik, maar het is de rand
ervan, en bij een ploeg die één punt verder had gelegen was het duel op `NONE` geëindigd.

## Creditbudget en marktbalans

`suggest_cap(19119, 13)` = **734** — 19.119 credits over volgens `api_check.py`, 13 dagen tot de
maandwissel, 2 runs per dag. `split_budget(734, 11)` gaf **11 spreads / 11 totals**: alle elf
inkoopbare competities kregen allebei. Het plafond laat 3 credits per competitie ruimschoots toe,
dus de bulk-aanroep (`h2h` + `spreads` + `totals`) is voor alle elf gedaan — vijf van de zes markten
in één keer, en 1X2 op de **beste prijs** in plaats van op het BetExplorer-marktgemiddelde.

| | |
|---|---|
| bulk (11 × 3 credits) | 33 |
| BTTS, tweede ronde (5 duels met een kandidaat-edge, §1a stap 2) | 5 |
| **totaal** | **38 van 734** — 19.081 over |

**Marktbalans — de controle op de inkoop (§1a).** Elf van de elf competities kregen zowel een
uitkomst- als een doelpuntenmarkt. Ruimer kan hij niet slagen; vergelijk 30 augustus, toen er
precies één competitie met een doelpuntenmarkt in de run zat.

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 (beste prijs, `h2h`-bulk) | 11 van 11 | 34 | 0 |
| Asian Handicap | 11 van 11 | 45 | 0 |
| Draw No Bet (0.0-lijn) | 8 van 12 duels | 15 | 0 |
| Double Chance (±0.5-lijn) | 8 van 12 duels | 9 | 0 |
| Over/Under | 11 van 11 | 58 | 0 |
| BTTS | 5 duels met kandidaat-edge | 10 | 0 |

Draw No Bet en Double Chance zijn dunner omdat vier duels géén 0.0- respectievelijk ±0.5-lijn in de
`spreads`-respons hadden (Bayern – Union Berlin, Groningen – PEC Zwolle, Wisła – Śląsk en bij DNB
ook Gent – Standard). Dat is **bekeken met een reden** en geen gat; het staat zo in
`markets_checked`.

**Beste prijs tegenover het marktgemiddelde:** mediaan **+5,80%** over de twaalf duels. Het
gemiddelde van +9,86% zegt vandaag niets — daar zit Union Berlin bij Bayern in met +53,34% op een
koers van 39.22, en die selectie valt sowieso buiten de koersband van §0. Zonder die ene uitschieter
is het gemiddelde +5,91%, in lijn met de +7,78% van de meting op 5 september.

## Vroeg-seizoenscorrectie

`early_season_uplift` gaf **×1,0834** (gepoold 1,0944 over 61 speeldagen in 11 competities). De
competities staan tussen 3 (Bundesliga) en 8 speeldagen (Deense Superliga, Ekstraklasa) ver.

De controle die §3 Stage 5 voorschrijft — P(Over 2.5) tegen de de-vigde marktkans, over de acht
duels met een 2.5-lijn aan beide kanten:

| | gemiddelde afwijking | gemiddelde absolute fout |
|---|---|---|
| zonder correctie | **−0,41 pp** | **3,47 pp** |
| met correctie ×1,0834 | +4,61 pp | 4,89 pp |

**De correctie maakt de schatting vandaag dus slechter, niet beter.** Dat is een meting tegen de
markt en daarmee uitsluitend een diagnose (§1d, §6e) — de correctie mag hier niet op worden
afgeregeld. Zie Bevinding 3.

## Wedstrijden

{secs}

## Topselectie

**Nul gepubliceerde bets**, dus geen topselectie. §5 zegt het met zoveel woorden: zijn er minder
gekwalificeerde bets dan `MAX_SHORTLIST`, lever er dan minder — en vul niet aan.

### De dagelijkse top-5, twee keer gerekend (§5a)

Letterlijke uitvoer van `python3 scripts/toplist.py --run a --date 2026-09-18`:

```
{toplist}
```

### Net niet

Eén wedstrijd leverde een `near_miss` op. De overige elf duels hadden geen enkele selectie boven de
`NEAR`-drempel (3,0 pp bij `FULL`, 6,0 bij `LIGHT`) op de herijkte schaal — dat is dus een dag
waarop er werkelijk niets in de buurt kwam, en geen dag waarop er drie op een haar afvielen.

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Herijkt | Valt af op |
|---|---|---|---|---|---|---|
| Monaco – Lens | 1X2 — Lens wint @ 3.60 | +11,22 pp | +20,01 pp | +10,13 pp | **+3,71 pp** | `edge` |

Die ene regel is het hele verhaal van vandaag in het klein: op de ruwe schaal haalt hij alles
(beide methodes ruim positief, de zwakste stand van het hele `(shrink, rho)`-grid nog boven de
tien), en na de herijking blijft er +3,71 pp over tegen een drempel van 8,0. Dezelfde selectie is
bovendien de enige die vandaag op de **ruwe** schaal door poort 8 is tegengehouden.

### Waar de 171 selecties op afvielen

| Poort | Herijkte schaal | Ruwe schaal |
|---|---|---|
| 1 — edge onder de drempel | 159 | 149 |
| 2 — koers buiten 1.30–6.00 | 7 | 7 |
| 5 — tweede methode tegengesteld | 0 | 3 |
| 7 — context | 0 | 4 |
| 8 — underdog onder 0.35 | 0 | 3 |
| alle acht gehaald | 0 (5 vielen alleen op de herijking) | 5 |

Lees die twee kolommen naast elkaar. Op de herijkte schaal komt de edge-poort altijd als eerste,
dus alles wat daar sneuvelt bereikt de latere poorten nooit — precies het verschijnsel waar §1e op
15 september de tweede boekingsschaal voor invoerde. Op de ruwe schaal bindt poort 7 vier keer
(drie selecties bij Brentford – Chelsea, waar Brentford drie dagen rust heeft tegen zes bij
Chelsea, en één bij Widzew Łódź – Wieczysta Kraków, waar Widzew 28% van zijn selectiewaarde mist
tegen 3% bij de tegenstander) en poort 5 drie keer (Bayern – Union Berlin, waar de twee methodes
op de handicap tegengesteld wijzen).

## Afwikkeling vorige picks

Geen openstaande echte picks. Vijf schaduwpicks van 17 september afgewikkeld — zie Stage 0
hierboven, twee gewonnen en drie verloren.

## Stand van het logboek

### `ledger.py stats` — wat er wél doorheen kwam

```
{ledger}
```

### `recalibrate.py show` — de stand van de herijking

```
{recal}
```

De fit van vandaag is `a=0.829, b=-0.467` op **680** afgerekende gevallen t/m 17 september. Het
model zei gemiddeld 52,0% en het gebeurde 40,7% van de tijd. Op de kansen die vandaag in de buurt
kwamen haalt de correctie 11 tot 13 procentpunt weg, en dat is exact het verschil tussen 79
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

### 1. De bekerregel van 15 september rekende een competitieduel in de verkeerde divisie door — teruggebracht tot bekers

§4 kreeg op 15 september de regel *"staan beide ploegen van een bekerduel in dezelfde divisie ónder
de basisdivisie, dan wordt het duel gewoon in díe divisie doorgerekend"*. De implementatie paste hem
op **elke** competitie toe (`promotion.CUP_BASE.get(name, name)` valt voor een competitie terug op
de competitie zelf). Vandaag sloeg dat aan op **Wisła Kraków – Śląsk Wrocław**: twee ploegen die
allebei uit de I Liga naar de Ekstraklasa zijn gepromoveerd en dus allebei niet in de
Ekstraklasa-stand van 2025/2026 staan. Twee dingen gingen daardoor mis:

1. **Het duel werd in de I Liga doorgerekend** — op het doelpuntenniveau en het competitiegemiddelde
   van de divisie eronder, terwijl deze twee ploegen vanavond in de Ekstraklasa spelen.
2. **En het liep vast.** De I Liga heeft geen xG bij Fotmob, dus `TeamStats(xg=r["xg"], …)` gooide
   een `KeyError` en de hele analyse stopte bij wedstrijd elf.

De regel is daarom teruggebracht tot waar §4 hem voor verantwoordt: **alleen bekers**. De
verantwoording staat er letterlijk — *"een beker heeft zelf geen stand en dus geen
competitiegemiddelde om ploegen op te normaliseren"* — en een competitie heeft dat wél. Twee
promovendi in een competitieduel gaan gewoon allebei door `promotion.convert` naar het niveau
waarop ze spelen. Na de correctie is het duel `LIGHT` met twee omgerekende ploegen, zoals elk ander
promovendusduel.

Wat dit **niet** verandert: voor bekers blijft de regel van 15 september onverkort staan, inclusief
de gevallen die hij toen redde (Peterborough United – Barnsley, Leyton Orient – Bradford). De
wijziging zit in `tmp-run/ra18_cand.py`; wie hem in een herbruikbaar script wil zetten, moet de
conditie `and name in promotion.CUP_BASE` meenemen.

### 2. De herijkingsreeks van §5a is voor het eerst groot genoeg om te lezen — en ze zegt dat de correctie geld bespaart

§5a voerde op 6 september de categorie `failed_gate = "herijking"` in met de instructie: *"niet
lezen vóór ~30 afgewikkelde gevallen"*. Met de drie rijen van vandaag staat die reeks op **50
kandidaten, waarvan 39 afgewikkeld** — en daarmee is de drempel gepasseerd.

| | n afgewikkeld | trefkans | ROI | gem. geclaimde edge |
|---|---|---|---|---|
| viel af op `herijking` | 39 | 38,5% | **−25,7%** | +10,9 pp |

Dat is de uitkomst die §5a als "blijft staan" definieert: *"is die structureel negatief, dan
bespaart de correctie geld en blijft ze staan"*. Deze 39 selecties haalden alle acht poorten op de
ruwe kans — het zijn dus precies de bets die de routine vóór 5 september zou hebben gespeeld — en
ze verloren een kwart van de inzet. De herijking heeft in die periode ongeveer **10 eenheden**
bespaard.

Twee dingen die erbij horen. Ten eerste: −25,7% over 39 gevallen is bij deze aantallen nog geen
scherp getal, en de richting is wat telt, niet de tweede decimaal. Ten tweede, en belangrijker: dit
zegt iets over de **correctie**, niet over het model. Dat de routine geld bespaart door haar eigen
oude selecties niet meer te spelen, betekent dat die selecties slecht waren — niet dat de nieuwe
goed zijn. `ledger.py stats` staat nog altijd op −7,8% over 223 afgewikkelde bets en de markt schat
nog altijd scherper (Brier 0,2362 tegen 0,2552).

### 3. De vroeg-seizoenscorrectie loopt achter op de kalender

`early_season_uplift` staat vandaag op **×1,0834** en maakt de schatting van P(Over 2.5) tegenover
de markt **slechter**: zonder correctie −0,41 pp gemiddelde afwijking (absolute fout 3,47), met
correctie +4,61 pp (absolute fout 4,89). Op 9 augustus, toen de correctie werd ingevoerd, was het
andersom — toen lag het model 3,0 pp **onder** de markt en trok de correctie dat recht.

Wat er sindsdien is veranderd: de competities zijn 3 tot 8 speeldagen ver, en de teamsterktes komen
sinds 3 september niet meer uitsluitend uit vorig seizoen maar via `blend_seasons` deels uit het
lopende seizoen (§4). Het lopende seizoen zit dus **twee keer** in de schatting — één keer als
teamsterkte, één keer als competitiebrede doelpuntenfactor — en dat is precies de dubbeltelling die
Run A op 12 september al als vermoeden noteerde.

**Dit is een meting tegen de markt en dus een diagnose, geen correctiefactor** (§1d, §6e). Er wordt
op grond hiervan vandaag niets veranderd. Wat het wél waard is: dit drie dagen achter elkaar
noteren met hetzelfde teken, en dan de vraag stellen op **uitkomsten** in plaats van tegen de markt
— bijvoorbeeld door `early_season_uplift` in de bestaande backtest van `blend_seasons` mee te laten
draaien en te kijken of de Brier-score erop vooruit- of achteruitgaat. Dat is dezelfde route
waarlangs `XG_WEIGHT` en `CREDIBILITY_K` zijn bepaald.

## Openstaand

1. **De uitdoofcurve van `early_season_uplift` tegen de blend van §4.** Zie Bevinding 3. Meet op
   uitkomsten, niet tegen de markt, en meet de twee stappen samen in plaats van los — het vermoeden
   is dubbeltelling en niet dat een van beide op zichzelf fout is.
2. **Poort 8 wordt uiterlijk 25 september herzien** (§1e) en staat vandaag op **8** afgewikkelde
   `underdog`-rijen (+12,9%) en **9** `underdog_ruw`-rijen (−34,0%). Beide reeksen groeien met
   ongeveer één rij per dag; op 25 september zal geen van beide de dertig halen die §1e zelf eist.
   Dat is geen reden om de poort ongezien te laten staan, maar de herziening zal het moeten doen
   met "te weinig om iets te zeggen" — noteer dat dan ook zo in plaats van het getal te lezen.
3. **De correctie van Bevinding 1 staat in `tmp-run/`, niet in `scripts/`.** De `cand`-stap van
   beide runs is per dag een kopie, dus Run B van vandaag heeft de oude conditie nog. Dit is een
   goede kandidaat om naar een herbruikbaar script te tillen — hetzelfde argument als bij
   `ra_names.py`.
4. **`conversion_in_range` op de rand.** Twee van de vier omrekeningen van vandaag komen precies op
   de bovengrens van het gemeten verdedigingsbereik uit (0.929 op 0.505–0.929). De poort is
   binair, maar een ploeg op de rand is niet even goed gemeten als een ploeg in het midden. Er is
   geen meting die zegt hoeveel dat scheelt; noteer het tot die er is.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-09-18-run-a.md", "w").write(MD)
print("runs/2026-09-18-run-a.md geschreven:", len(MD), "tekens")
