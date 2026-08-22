# Gedeelde analyseregels — Run A & Run B

Deze regels gelden voor **elke** run. Wijzig ze hier in de repo, niet in de scheduler.
De scheduler-prompt is met opzet kort en verwijst naar dit bestand, zodat je regels kunt
aanpassen zonder de geplande taak aan te raken.

---

## 0. Vaste parameters

| Parameter | Waarde | Waarom |
|---|---|---|
| `MAX_DEEP_ANALYSES` | **30** | Harde cap. Zonder cap loopt een run met 40+ wedstrijden altijd zijn tijdslimiet in en levert een halve lijst. Verhoogd van 12 naar 30 op 8 aug 2026 nadat `scripts/fotmob.py`, `scripts/model.py`, `scripts/betexplorer.py` en `scripts/oddsapi.py` de ophaal- en rekenlogica herbruikbaar maakten — zie de toelichting eronder. |
| `MAX_SHORTLIST` | **3** (ma–do) / **5** (vr–zo) | Onveranderd t.o.v. de oude opdracht. |
| `EDGE_THRESHOLD_FULL` | **3.0 procentpunt** | Onder deze grens is de schatting niet te onderscheiden van modelruis. |
| `EDGE_THRESHOLD_LIGHT` | **6.0 procentpunt** | Zwakkere data eist een grotere marge. |
| `MAX_LIGHT_IN_SHORTLIST` | **2** | Voorkomt dat de topselectie volloopt met zwak onderbouwde bets. |
| `MIN_ODDS` / `MAX_ODDS` | **1.30** / **6.00** | Buiten deze band is de kansschatting te onnauwkeurig om edge zinvol te noemen. |
| `SETTLE_AFTER_HOURS` | **12** | Openstaande picks ouder dan dit worden afgewikkeld. |

---

## 1. Selectie: **0 of 1** bet per wedstrijd

> Dit vervangt de oude regel "exact één beste valuebet per wedstrijd".

Per geanalyseerde wedstrijd geldt precies één van twee uitkomsten:

- **BET** — er is één markt/selectie die alle poorten hieronder passeert.
- **GEEN BET** — met een reden in één regel. Dit is een volwaardige, correcte uitkomst.

**Draai altijd beide methodes** en middel ze tot één schatting:

```python
p_xg    = analyze_match(...)              # op xG, genormaliseerd op de competitie
p_split = analyze_match_from_splits(...)  # op wat de ploegen thuis en uit werkelijk scoorden
my_prob = (p_xg + p_split) / 2            # dit is de kans die in de pick komt
edge_pp = (my_prob - 1 / odds) * 100
```

Een bet mag alleen gepubliceerd worden als **alle** voorwaarden gelden:

1. `edge_pp ≥ EDGE_THRESHOLD_FULL` bij `data_tier = FULL`, of `≥ EDGE_THRESHOLD_LIGHT` bij `LIGHT`
   — gemeten op de **gemiddelde** `my_prob` hierboven, niet op één van de twee afzonderlijk;
2. `MIN_ODDS ≤ odds ≤ MAX_ODDS`;
3. de anti-circulariteitsregel (§2) is voldaan;
4. `data_tier ≠ NONE`;
5. **de twee methodes spreken elkaar niet tegen.** Beide moeten de markt dezelfde kant op
   verslaan: `p_xg > 1/odds` **én** `p_split > 1/odds`. Zakt één van de twee onder de
   marktkans, dan wijzen ze tegengesteld en gaat de bet eruit met reden "data conflicterend";
6. **de edge draait niet om bij een andere parameterkeuze:**
   `robustness_check(...).min_edge > 0` over het hele (shrink, rho)-grid.

### Waarom poort 5 en 6 zo staan (herzien 11 aug 2026)

Van 9 t/m 11 aug luidde poort 5 "**beide** methodes moeten boven de drempel uitkomen" en poort 6
"`min_edge ≥ drempel`". Dat is drie keer dezelfde volle drempel op drie ruizige statistieken, en
dat bleek in de praktijk een filter dat vrijwel alles wegvangt: **acht kandidaten met een echte
edge, nul bets** over vier runs (10–11 aug, beide runs).

De constructie was ook statistisch te streng. `min(A, B) ≥ drempel` eisen van twee schatters van
dezelfde grootheid ligt veel hoger dan `gemiddelde(A, B) ≥ drempel`: het middelen van twee
schattingen verkleint juist de ruis, terwijl de min-regel de ruis maximaal laat meetellen. Wat je
wilt uitsluiten is niet "de tweede methode is wat lager", maar "de twee methodes wijzen
tegengesteld" — en dát is precies wat poort 5 nu toetst.

Op de acht kandidaten tot nu toe geeft de herziene regel 5 bets in plaats van 0, en houdt hij de
twee gevallen tegen waar de methodes werkelijk tegenover elkaar stonden (Sirius – Brommapojkarna
+3.4 / **−8.4** en Västerås – Djurgården +4.6 / **−4.3**). De aanleiding voor de oude poort,
Gil Vicente – Rio Ave op 9 aug (+10.3 / +2.7), zou onder de nieuwe regel wél doorgaan — met
`my_prob` op het gemiddelde, dus met een navenant lagere geclaimde edge.

**Dit is een verruiming zonder bewijs, en daarom loopt er vanaf nu een schaduwlogboek mee.** Er is
namelijk nooit gemeten of de oude poort iets opleverde: alle acht picks in `picks.jsonl` dateren
van vóór 9 aug, dus er is geen enkele afgerekende bet onder het oude regime. Zolang dat zo blijft
is "strenger is beter" een aanname, geen bevinding. §6d legt vast hoe elke afgewezen kandidaat
alsnog wordt afgerekend, zodat over enkele weken met cijfers te zeggen is of deze poorten geld
besparen of alleen bets.

**Een run met nul bets is geen mislukte run.** Nul bets rapporteren met een heldere reden is
correct gedrag; bets forceren om het format te vullen is dat niet.

Ga alle markten langs — 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS —
en publiceer alleen de sterkste. Geen "gevoel", geen reputatie-argumenten.

**Dit is tot 14 aug 2026 niet gebeurd, en het lag aan de code.** `MatchProbabilities` had velden
voor 1X2, Over/Under **2.5** en BTTS en verder niets; Asian Handicap en Draw No Bet waren niet uit
te rekenen, andere O/U-lijnen evenmin. Aan de oddskant was er wél een `fetch_totals` maar geen
`fetch_spreads`, en `fetch_event_markets` (voor BTTS en Double Chance) is nooit aangeroepen. Het
resultaat is te tellen in `data/picks.jsonl`: van de eerste 15 picks waren er **11 een 1X2, 3 een
Over/Under 2.5 en 1 een Double Chance** — nul Asian Handicap, nul BTTS, nul Draw No Bet. In
`data/shadow.jsonl` was 19 van de 20 een 1X2. De routine koos dus niet de sterkste markt maar de
sterkste van de twee die toevallig geïmplementeerd waren.

Sinds 14 aug 2026 kan het wel, en het kost niets extra aan modelwerk — alle markten komen uit
hetzelfde scoregrid dat `analyze_match` toch al berekent:

```python
p = analyze_match(...)                              # p.grid is nu beschikbaar
asian_prob(p.grid, -0.75, "home", odds)             # Asian Handicap, incl. kwart- en hele lijnen
dnb_prob(p.grid, "away", odds)                      # Draw No Bet (= de handicap op 0.0)
totals_prob(p.grid, 3.0, "over", odds)              # elke O/U-lijn, niet alleen 2.5
p.dc_1x, p.dc_x2, p.dc_12                           # Double Chance
p.btts                                              # BTTS
```

Aan de oddskant: `fetch_spreads(sport_key)` kost **1 credit**, precies zoveel als `fetch_totals`, en
levert de handicaplijnen van alle wedstrijden in een competitie. BTTS en Double Chance gaan via
`fetch_event_markets(sport_key, event_id, ["btts", "double_chance"])` en kosten 2 credits **per
wedstrijd** — vraag die dus pas op voor wedstrijden die al een kandidaat-edge tonen, niet voor de
hele kalender. `best_by_line(event, markt)` geeft de beste prijs per (uitkomst, lijn); vergelijk
nooit prijzen over verschillende lijnen heen, want een andere lijn is een andere bet.

Een handicap of totaal met push is geen gewone kans — bij een push komt de inzet terug — dus
`asian_prob` geeft de kans terug die bij díe koers dezelfde verwachtingswaarde oplevert, zodat
`edge_pp` en alle zes poorten er ongewijzigd op werken. Gebruik voor markten met push dus altijd
`asian_prob` / `dnb_prob` / `totals_prob` en nooit de kale winkans, anders staan de markten niet op
dezelfde schaal en is de rangschikking hieronder betekenisloos.

### 1a. Waar de prijzen vandaan komen — creditbudget (vastgesteld 15 aug 2026)

The Odds API is de gratis Starter met **500 credits per maand**. Op 15 aug verbruikten Run A en
Run B samen **132 credits op één dag** — een kwart van de maand — doordat alle zes markten voor het
eerst echt werden doorgerekend. Op dat tempo is het budget in twee dagen op, en een run zonder
prijzen levert per definitie nul bets. Daarom ligt vanaf nu vast wélke bron welke markt levert:

| Markt | Bron | Kosten |
|---|---|---|
| **1X2** | `betexplorer.fetch_league_fixtures(url)` | **gratis** |
| Asian Handicap, Over/Under | `oddsapi.fetch_bulk(key, ["spreads","totals"])` | 2 credits per competitie |
| Double Chance, BTTS | `oddsapi.fetch_event_markets(...)` | 2 credits per wedstrijd |
| Draw No Bet | de 0.0-lijn uit `spreads` — dezelfde bet | gratis, zit al in de bulk |

Gebruik **`fetch_league_fixtures`**, niet `fetch_league_odds`: die tweede leest de "Next matches"-
tabel en die toont er maar vijf. Op 15 aug had de Championship acht duels; drie zouden zonder 1X2
zijn gebleven. De fixtures-pagina geeft ze alle acht — gemeten op alle acht competities van die dag,
32 van de 32 wedstrijden gedekt, nul credits.

**Bepaal aan het begin van de run je plafond en houd je eraan:**

```python
from scripts.oddsapi import CreditGuard, suggest_cap
cap = suggest_cap(remaining_uit_api_check, dagen_tot_de_maandwissel)   # 2 runs per dag
guard = CreditGuard(cap=cap)
```

Geef de credits uit in deze volgorde, en stop zodra `guard.can_afford(...)` False geeft:

1. `spreads,totals` (2 per competitie), voor de competities die **vandaag aan de beurt zijn**:

   ```python
   from scripts.oddsapi import rotate_for_day
   vandaag_aan_de_beurt = rotate_for_day(comps_op_datakwaliteit, date.today(), take=cap // 2)
   ```

   Roteren en niet altijd de beste vier: bij een plafond van 8 credits passen er maar vier, en
   steeds dezelfde vier nemen betekent dat de andere vier structureel nooit een handicap of totaal
   krijgen. Dat is precies de stille blinde vlek die §6b-5b moest wegnemen. Met roulatie is elke
   competitie om de dag aan de beurt, en 1X2 heeft elke competitie sowieso elke dag (gratis).
2. `double_chance,btts` **alleen als er daarna nog credits over zijn** — in de praktijk dus meestal
   niet. Dit is geen bezuiniging op gevoel maar op een meting van 15 aug 2026, de dag waarop deze
   markten voor het eerst werden opgevraagd:

   | Creditgroep | Kosten in Run A | Bets eruit | Per bet |
   |---|---|---|---|
   | `spreads,totals` (bulk) | 16 | 12 van de 15 | **1,3 credits** |
   | `h2h` (bulk, nu gratis via BetExplorer) | 8 | 2 van de 15 | 4 credits |
   | `double_chance,btts` (per wedstrijd, 15x) | **30** | **1 van de 15** | **30 credits** |

   Dertig credits voor één bet, tegen 1,3 voor de bulkmarkten: een factor 23. Zolang het budget
   krap is, is dit de eerste die eraf gaat. **Let op dat dit één dag meten is** (§6d), dus het is
   een budgetkeuze en geen bevinding over de markten zelf: komt er ooit meer ruimte, zet ze dan
   terug en meet opnieuw voordat je concludeert dat DC en BTTS weinig opleveren.

Een markt die je door het plafond niet hebt opgevraagd is **bekeken met een reden**, niet een gat:
noteer hem in `markets_checked` als `"DC": "niet opgevraagd — creditplafond van de run bereikt"`.
Zo blijft `progress.py verify` groen zonder dat de administratie liegt. Neem `guard.report()` op in
het runrapport onder "Bronstatus deze run".

**Wat dit kost aan kwaliteit, en waarom het toch klopt.** BetExplorer geeft het **marktgemiddelde**
over de getoonde boeken, niet de beste prijs, en de bookmaker is niet herleidbaar. Een 1X2-edge is
daardoor systematisch **lager** dan tegen de beste prijs — conservatief, dus geen risico op te veel
bets, maar het maakt de vergelijking tussen markten scheef: een 1X2 op een gemiddelde prijs verliest
het in `selection_score` van een handicap op een beste prijs, ook als de 1X2 in werkelijkheid beter
was. Daarom:

- noteer bij een 1X2-pick altijd `odds_source` als marktgemiddelde met het aantal boeken erbij, en
  vermeld dat de bookmaker niet herleidbaar is (dat deed de routine op 13 aug al zo);
- **wint een 1X2 de `selection_score` binnen een wedstrijd, dan is die uitkomst betrouwbaar** — hij
  won immers met de zwakkere prijs. Verliest hij nipt van een handicap, meld dat dan in het
  runrapport als "mogelijk artefact van de prijsbron", en stel op grond daarvan geen regel bij.

Ga niet alsnog een `h2h`-bulkcall doen om dat recht te trekken: dat kost precies de 8 credits per run
die deze paragraaf bespaart.

### 1b. De reservebron: OddsPapi — uit, tenzij een mens hem aanzet

Er is een tweede oddsbron beschikbaar, met **250 verzoeken per maand**. Dat is ongeveer vier per run
en dus geen tweede leverancier maar een noodvoorraad. Hij is er voor precies één geval: The Odds API
is door zijn maandbudget heen en de runs zouden anders zonder prijzen komen te staan — en een run
zonder prijzen levert per definitie nul bets.

**De run zet hem nooit zelf aan.** Er zijn twee sloten en ze moeten allebei open:

1. `data/odds-fallback.json` staat op `"armed": true`. Dit veld is **van de gebruiker**. Een run die
   het zelf zou mogen omzetten, kan zichzelf toestemming geven en de hele voorraad in één ochtend
   opmaken. Kom je een run tegen waarin dat nodig lijkt: doe het niet, meld het in het runrapport en
   in de notificatie, en laat de gebruiker beslissen.
2. The Odds API zit op of onder `threshold` credits (standaard 20).

In code:

```python
from scripts.oddspapi import should_use
inzetbaar, reden = should_use(odds_api_remaining)   # remaining komt uit api_check.py
```

Neem `reden` **elke run** letterlijk over in het runrapport onder "Bronstatus deze run", ook — juist —
als hij niet is ingezet. Zo is achteraf te zien dat de reserve er was en waarom hij bleef staan.

Twee dingen om te weten voordat je hem gebruikt:

- **Controleer de reserve in Stage 3, niet pas als je hem nodig hebt.** Basis-URL
  (`https://v5.oddspapi.io/{taal}/…`) en de `apiKey`-queryparameter zijn nagetrokken; de precieze
  fixture- en odds-paden niet, omdat OddsPapi de sleutel vóór de routering controleert en zonder
  sleutel élk pad 401 geeft — een verzonnen pad net zo goed als een echt pad. Roep daarom in Stage 3,
  direct na `api_check.py`, één keer aan:

  ```python
  from scripts.oddspapi import ensure_discovered
  gedraaid, melding = ensure_discovered()   # no-op zodra de paden bekend zijn
  ```

  Dit staat **los van `armed`** en is geen inzet van de reserve: het is de controle of hij wérkt.
  Een noodaggregaat test je niet voor het eerst tijdens de stroomstoring — en een verkeerd
  overgetypte sleutel wil je weten op een dag dat het niet uitmaakt, niet op de dag dat The Odds API
  op is. Kosten: een handvol van de 250, eenmalig. Meld `melding` in het runrapport en werk
  `data/source-health.json` bij (`oddspapi` → `status`). Komt er `invalid_api_key` uit, meld dat dan
  ook in de notificatie: dat is een blokkade die anders weken onopgemerkt blijft.
- **Tel zelf mee.** OddsPapi geeft `X-RateLimit-*` per seconde en per minuut, maar geen teller voor
  het maandquotum. `scripts/oddspapi.py` houdt `used_this_month` daarom zelf bij in
  `data/odds-fallback.json`; zet die bij een nieuwe periode met de hand op 0.

### Welke markt je publiceert: `selection_score`, hoogste wint

Dezelfde onderliggende inschatting levert vaak op vier tot zeven markten tegelijk een edge op.
Gemeten op Viborg – AGF (14 aug 2026): 1X2 +17.6 · AH +0.5 +15.5 · DNB +15.2 · Double Chance +12.2 ·
AH +1.0 +8.8 · Over 2.5 +5.1 · BTTS ja +3.0. Dat zijn geen zeven bevindingen maar **één, zeven keer
uitgedrukt**. De 0-of-1-bet-regel blijft dus onverkort gelden: "de sterkste" betekent één selectie
per wedstrijd, niet één per markt.

Welke van die uitdrukkingen je publiceert, is **vastgesteld op 14 aug 2026 op verzoek van de
gebruiker** en niet langer aan de run:

```python
from scripts.model import selection_score
selection_score(edge_pp, my_prob, data_tier)      # = edge_pp × my_prob × (FULL 1.0 | LIGHT 0.5)
```

Van alle selecties die **alle zes de poorten** halen, publiceer je die met de hoogste score. Dit is
dezelfde formule als bij de topselectie in §5 — één weegregel voor beide, zodat de bet die je kiest
en de plek die hij in de shortlist krijgt niet uit elkaar kunnen lopen.

Waarom deze en niet een andere. Er waren vier redelijke lezingen van "Edge × Probability ×
Data-betrouwbaarheid", en op de wedstrijden van 14 aug wezen ze niet dezelfde kant op:

| Lezing | Viborg – AGF | Cercle – St.Truiden | Telstar – Sparta |
|---|---|---|---|
| hoogste edge in procentpunten | 1X2 | 1X2 | 1X2 |
| **Edge × kans, letterlijk (gekozen)** | **AH +0.5** | **AH +0.25** | **1X2** |
| hoogste rendement per euro | 1X2 | 1X2 | 1X2 |
| grootste Kelly-inzet | AH +0.5 | AH +0.25 | 1X2 |

Tot die datum deed de routine feitelijk de eerste, zonder dat ooit te hebben opgeschreven. De
gekozen regel geeft de voorkeur aan een hogere trefkans boven een paar procentpunt extra edge. Dat
is een keuze over risicobereidheid — die hoort bij de gebruiker en niet bij de data — maar er is
één inhoudelijk argument dat dezelfde kant op wijst: de bekende zwakte van dit model (het kent geen
competitiesterkte) verschuift kansmassa tussen *winst* en *gelijkspel*. Een 1X2 is daar maximaal
gevoelig voor, want een gelijkspel is dan puur verlies; een handicap +0.5 of een Draw No Bet is er
ongevoelig voor, want daar wordt een gelijkspel gewonnen of teruggegeven. Zolang die fout er is,
kiest deze regel dus ook de minst blootgestelde uitdrukking van dezelfde mening.

**Het gewicht 0.5 voor LIGHT is afgeleid, niet gekozen:** het is `EDGE_THRESHOLD_FULL /
EDGE_THRESHOLD_LIGHT` = 3.0 / 6.0. Zwakke data moet al twee keer zoveel edge opleveren om mee te
mogen doen; diezelfde verhouding bij het rangschikken houdt de twee met elkaar in de pas.

Noteer in het runrapport bij elke gepubliceerde bet **welke selectie tweede werd en met welke
score**. Zonder dat is niet na te gaan of deze weegregel iets doet, en dan staan we over een maand
weer waar we op 14 aug stonden.

---

## 2. Anti-circulariteitsregel (hard, niet optioneel)

`my_prob` mag **nooit** afgeleid zijn van de odds waartegen je hem afzet. Doe je dat, dan meet
`edge = my_prob − implied_prob` alleen je eigen afwijking van de markt, zonder onafhankelijk
anker — een getal dat overtuigend lijkt en niets betekent.

Daarom: elke bet heeft **minstens één onafhankelijke kansinput** in `prob_sources`, en die mag
géén bookmaker of odds-aggregator zijn. Geldig zijn o.a. xG/xGA, rolling-xG, shot- en
big-chance-data, gepubliceerde modelkansen, goal averages, BTTS%/O-U-percentages,
home/away-splits, blessures/schorsingen van sleutelspelers.

Is er voor een wedstrijd géén enkele onafhankelijke input? → `data_tier = NONE` → **GEEN BET**.
Niet "LIGHT met lage confidence" — geen bet. Vermeld bij elk cijfer de bron. Niet gevonden =
schrijf "niet gevonden", nooit gokken.

**Een "gepubliceerde modelkans"-site is niet automatisch schoon.** De expliciete bookmaker/
aggregator-uitsluiting (Oddschecker, BetExplorer, The Odds API e.d.) vangt niet alles: sommige
voorspellingssites nemen odds of marktbeweging zelf al op als invoer voor hun "modelkans" — hun
getal is dan een verkapte afgeleide van de markt, ook al staat het niet op een bookmakerpagina.
Controleer de methodetekst van een nieuwe bron voordat je hem als onafhankelijk aanmerkt.
Concreet voorbeeld, ontdekt op 8 aug 2026: prognosist.com noemt zelf "team form, xG, odds and
market movement" als invoer voor zijn "Model probability" — daarom staat die bron in
`coverage.json` met `"blends_market_data": true` en telt hij niet als schone onafhankelijke input
op zichzelf. Twijfel je over een bron? Zoek de "methodology"/"how it works"-pagina op en lees hem,
net zo goed als je bij een cijfer de bron leest.

---

## 3. Pipeline — filter vóór de analyse, niet erna

### Stage -2 — Eén werkbranch (vóór alles, ook vóór het lezen van deze regels)

Elke sessie krijgt een eigen branchnaam, en de twee geplande taken lopen los van elkaar. Zonder
maatregel schrijven Run A en Run B naar twee takken die elkaars werk niet zien. Dat is geen
theoretisch risico:

- **9 aug 2026** — de scheduler wees naar een branch die zeven commits achterliep.
- **10 aug 2026** — Run A en Run B schreven allebei naar een eigen tak, allebei met echt werk erop.
  Run A startte op de tak van Run B en miste daardoor poort 5 (§1.5) en de vroeg-seizoenscorrectie
  (Stage 5), regels die Run A zelf de dag ervoor had toegevoegd. Er is een bet gepubliceerd en
  verstuurd die onder de volledige regelset niet had gemogen, en twee picks van de dag ervoor bleven
  onafgewikkeld omdat hun tak nooit is aangeraakt.

Daarom, als allereerste handeling van elke run:

```bash
git rev-parse --is-shallow-repository        # ZIE HIERONDER — doe dit eerst
git fetch --unshallow origin || git fetch origin
git branch -r
for b in $(git branch -r | grep -v HEAD); do
  echo "$b: $(git rev-list --count HEAD..$b) commits die hier nog niet zijn"
done
```

**Haal eerst de volledige geschiedenis op, anders meet je iets anders dan je denkt.** De container
krijgt de repo als **ondiepe kloon** aangeleverd (`--is-shallow-repository` → `true`, en dat was op
20 aug 2026 opnieuw zo, in een verse container). Bij een ondiepe kloon ontbreekt alles van vóór de
knip, en dus ook het punt waar twee takken uit elkaar zijn gegaan: `git merge-base main <tak>` geeft
**niets** terug en `rev-list --count HEAD..<tak>` telt élke commit van vóór de knip als "nog niet
hier". Het resultaat is een vals alarm dat er precies uitziet als het echte geval van 10 aug —
takken met tientallen "eigen" commits die er in werkelijkheid allemaal al in zitten.

Zo zag dat er op 20 aug 2026 uit, dezelfde repo, vóór en na één commando:

| | ondiep (60 commits lokaal) | na `--unshallow` (109 commits) |
|---|---|---|
| takken met "eigen" commits | 7 van de 15 (3 t/m 39 stuks) | **0 van de 15** |
| `merge-base` met `main` | leeg | gewoon een commit |

Kost dit één extra opdracht per run, dan is dat het waard: zonder die stap doet elke run opnieuw
het handwerk van 19 en 20 aug (per tak de picks, de runrapporten en de scripts vergelijken) om
uiteindelijk vast te stellen dat er niets te mergen viel. Blijkt ná het unshallowen dat er tóch
takken met eigen commits zijn, dan is dat het echte geval en geldt alles hieronder onverkort.

Elke branch met méér dan 0 eigen commits wordt **gemerged**, niet weggegooid en niet vervangen.
"Pak gewoon de nieuwste" is expliciet fout: op 10 aug bevatten beide takken werk dat de ander niet
had, dus kiezen betekende hoe dan ook iets verliezen.

Bij conflicten:

| Bestand | Regel |
|---|---|
| `data/picks.jsonl` | **Vereniging.** Een pick die op één tak staat is een echte, gepubliceerde pick. Staat dezelfde id op beide takken, neem dan de versie die het meest weet — een afgewikkelde regel wint van `pending`. |
| `data/source-health.json`, `data/coverage.json` | **Vereniging.** Beide runs hebben echt gemeten; bewaar beide waarnemingen naast elkaar in `detail` in plaats van er een te laten winnen. |
| `prompts/_shared-rules.md`, `scripts/*` | De **nieuwste** versie wint. Regels en rekencode zijn geen metingen. |

Lees deze regels pas ná de merge opnieuw: vóór de merge kun je een oudere versie van dit bestand in
handen hebben dan er in de repo bestaat. Kom je uit op een andere branch dan de scheduler noemt, meld
dat dan bovenaan het runrapport én in de notificatie — anders blijft het elke run handwerk.

Controleer na de merge of `picks.jsonl` openstaande picks bevat van een run die op de andere tak
nooit is afgewikkeld. Die horen bij Stage 0.

Deze stap ruimt op wat al uiteen is gelopen. Dat er niets nieuws bij komt, regelt §6a: je pusht
aan het eind naar `main`, niet naar de tak die deze sessie toevallig kreeg toegewezen. De twee
horen bij elkaar — Stage -2 alleen betekent dat je elke run opnieuw hetzelfde opruimwerk doet.

### Stage -1 — Onderbreking en hervatting (Claude-limiet)

Een sessie kan halverwege stoppen doordat de gebruiker zijn Claude-gebruikslimiet raakt. Zonder
maatregel begint de volgende poging weer bij wedstrijd 1 — met `MAX_DEEP_ANALYSES = 30` is dat
zonde van precies het werk dat al gedaan was. Daarom, **vóór Stage 0**:

```python
from datetime import date
from scripts.progress import load_or_start, is_completed, is_done, mark, save, mark_completed

state = load_or_start(RUN_ID, date.today())
```

- `is_completed(state)` is waar → deze run is vandaag al helemaal afgerond (rapport geschreven,
  picks gecommit). Stop meteen, doe niets — anders analyseer je dezelfde dag twee keer.
- `state["resumed_count"] > 0` → dit is een hervatting. Meld dat bovenaan het runrapport in één
  zin ("hervat om HH:MM na onderbreking, N competities al gedaan"). Geen drama, geen aparte
  sectie — gewoon vermelden.
- Loop je vervolgens door de runlijst (Stage 4/5): sla een competitie over met `is_done(state,
  naam)` als hij al in het voortgangsbestand staat, en verwerk alleen wat nog ontbreekt.
- **Commit en push het voortgangsbestand na elke afgeronde competitie** (`mark(...)` gevolgd door
  `save(...)`), niet pas aan het eind. Dit is de kern van hervatten: zonder tussentijdse commit
  overleeft niets een afgebroken sessie, want de container wordt weggegooid zodra hij stopt.
- Aan het eind van Stage 6, ná de normale vastlegging (rapport, picks, source-health, push): roep
  `mark_completed(state)` en `save(state)` aan. Dat is het signaal voor een eventuele latere
  aanroep diezelfde dag dat er niets meer te doen is.

`data/run-state/` staat **niet** in `.gitignore` (in tegenstelling tot `data/cache/`) — dit
bestand moet juist wél overleven tussen sessies, dat is zijn hele functie.

### Stage 0 — Afwikkelen (vorige runs)
Lees `data/picks.jsonl`. Zoek de uitslagen op van picks met `result = null` en een aftrap ouder
dan `SETTLE_AFTER_HOURS`. Werk ze bij via `scripts/ledger.py settle`. Zonder deze stap is de
kwaliteit van de routine niet meetbaar.

### Stage 1 — Fixtures van vandaag
Bepaal zelf de actuele datum. Haal fixtures op; probeer meerdere bronnen (zie
`data/source-health.json` voor wat laatst werkte). Werk uitsluitend met wedstrijden van **vandaag**.

### Stage 2 — Competitiepoort
Competities uit je runlijst **zonder** wedstrijden vandaag: overslaan, één regel in de
dekkingstabel, geen verdere aandacht. Rapporteer ze niet als "gat" — buiten het seizoen is geen
storing.

### Stage 3 — Bronprobe + datadekkingspoort

Begin met de sleutelcontrole — dit is de eerste opdracht van elke run na het afwikkelen:

```bash
python3 scripts/api_check.py
```

Neem de uitvoer letterlijk over in het runrapport onder "Bronstatus deze run". Wat je eruit haalt:

- **Beide sleutels ontbreken** → er is geen API-bron. Ga verder met de scrape-bronnen uit
  `coverage.json`; verwacht dat vrijwel alles `BUITEN DATADEKKING` wordt. Meld in het rapport dat
  de sleutels ontbreken, met verwijzing naar `README.md` → "Sleutels toevoegen".
- **`API_FOOTBALL_KEY` werkt** → er is een onafhankelijke kansbron. Deze competities kunnen nu de
  datadekkingspoort passeren. Trek per competitie na of er daadwerkelijk xG in de respons zit:
  zo ja `FULL`, zo nee `LIGHT` op basis van teamstatistieken, doelgemiddelden en home/away-splits.
- **Een sleutel wordt afgewezen** → meld de exacte foutmelding in het rapport en stuur een
  notificatie (§7, "nieuwe blokkade"). Een stilzwijgend afgewezen sleutel is het soort storing dat
  maanden onopgemerkt blijft.
- **Quota bijna op** → verlaag het aantal opvragingen deze run en meld het. Bij The Odds API kost
  een verzoek `markten × regio's`; houd het op één regio en maximaal twee markten.

Werk daarna `data/source-health.json` bij met wat je gemeten hebt: de statusregels van
`api_check.py` én de scrape-bronnen die je deze run hebt geprobeerd (inclusief HTTP-status bij
falen). Zet de sleutelbronnen op `ok` of op de foutmelding, niet meer op `untested`.

Bepaal dan per resterende competitie of er een werkende, onafhankelijke kansbron is. Competities
zonder dekking gaan naar **"buiten datadekking"** en worden niet geanalyseerd.

**Niet doen:** de Cloudflare-challenge op fbref, Forebet, FootyStats of PredictZ omzeilen. Die
sites sluiten bots bewust af (zie `README.md` → "Waarom de bronnen dicht zitten"). Blijft hun
status `cloudflare_challenge`, dan is dat de uitkomst — probeer geen headless browser, geen
challenge-solver en geen proxy om er langs te komen.

Deze stap maakt de routine zelfherstellend: zodra een bron terugkomt of er een API-key
beschikbaar is, stroomt het werk automatisch weer door — zonder de prompt te wijzigen.

### Stage 4 — Rangschikken en afkappen
Rangschik de overgebleven wedstrijden op verwachte datakwaliteit (FULL boven LIGHT, meer
onafhankelijke inputs boven minder). Neem de top `MAX_DEEP_ANALYSES` mee naar de diepe analyse.
Noteer expliciet hoeveel wedstrijden hierdoor zijn afgekapt — **stille truncatie is verboden**;
een afgekapte lijst leest anders als volledige dekking.

**Gebruik `scripts/fotmob.py`, `scripts/betexplorer.py`, `scripts/oddsapi.py`, `scripts/xgscore.py`
en `scripts/model.py` voor Stage 3-5** in plaats van de ophaal- en rekenlogica opnieuw te schrijven.
Dat is precies wat de vorige aanpak duur maakte: niet het aantal wedstrijden, maar het aantal
**nieuwe, nog niet opgehaalde competities** — voor elke competitie moet één keer een team-xG-
dossier worden opgebouwd (`fotmob.fetch_league_stats`, met caching per dag), maar zodra dat er
is, kost een extra wedstrijd binnen diezelfde competitie bijna niets: alleen nog
`model.analyze_match` en `model.robustness_check` aanroepen. Reken dus niet met wedstrijden als
eenheid van "hoeveel kan ik aan vandaag", maar met **hoeveel competities voor het eerst worden
opgehaald**. Een dag met 30 wedstrijden in 3 al-bekende competities is goedkoop; een dag met
10 wedstrijden in 10 nieuwe competities is duur — ook al is het aantal wedstrijden lager. Val bij
twijfel terug op de volgorde uit deze paragraaf (FULL boven LIGHT), en meld in het runrapport
welke competities deze run voor het eerst zijn opgehaald (en dus in `data/cache/fotmob/` zijn
gecached voor de volgende run).

### Stage 5 — Analyse en output
Analyseer de geselecteerde wedstrijden volgens §4 en §5.

**Zet eerst het doelpuntenniveau goed.** Haal per competitie de teamstatistieken van zowel het
vorige als het lopende seizoen op, en corrigeer de competitiebasis voordat je één wedstrijd
doorrekent:

```python
from scripts.model import early_season_uplift, scale_level
obs = [(vorig["avg_xg_per_match"], huidig["avg_xg_per_match"], speeldagen) for elke competitie]
factor, pooled, total_md = early_season_uplift(obs)
league = scale_level(league_uit_vorig_seizoen, factor)
```

Waarom dit moet: met teamsterktes uit vorig seizoen komt het niveau óók uit vorig seizoen, en
begin seizoen wordt er meer gescoord dan over een heel jaar gemiddeld. Op 9 aug 2026 lag het
model daardoor over 17 wedstrijden gemiddeld 3.0 pp onder de markt op P(Over 2.5) — tien van de
zeventien keer dezelfde kant op — waardoor zeven Under-kandidaten dezelfde scheefstand zeven keer
telden. Na de correctie: +0.9 pp, gemiddelde absolute fout van 4.5 naar 3.9 pp. De correctie dooft
vanzelf uit naarmate het seizoen vordert.

**Regel de correctie nooit af op de markt.** Hij komt volledig uit xG-waarnemingen; zou je
`prior_matchdays` bijstellen tot de afwijking tegenover de bookmakers nul is, dan is `my_prob`
alsnog van de odds afgeleid en meet de edge niets meer (§2). Meten tegen de markt om te zien of
de correctie werkt mag wel — dat is controleren, niet fitten. Meld de gemeten afwijking vóór en
na in het runrapport, zodat een volgende run ziet of de correctie nog klopt.

### Stage 6 — Vastleggen
Volg §6. Zonder commit is de run niet gebeurd.

---

## 4. Datahiërarchie en labels

1. **Hard data** (indien beschikbaar): team xG/xGA (seizoen); rolling xG-trend (laatste 5–8);
   match-level predicted xG (home/away); shots, SOT, big chances; fitheid, blessures/schorsingen
   key-players.
2. **Bij ontbrekende xG**: gepubliceerde modelkansen (Forebet, FootyStats, xGscore, Prognosist
   e.d.); goal averages, BTTS%, over/under-lijnen; home/away-splits; recente vorm (5–6).

**Consistentie-check:** benoem waar data onzeker of conflicterend is.

| Label | Voorwaarde |
|---|---|
| `FULL` | ≥ 2 onafhankelijke inputs, waarvan ≥ 1 uit categorie 1 |
| `LIGHT` | ≥ 1 onafhankelijke input, maar niet genoeg voor FULL |
| `NONE` | geen onafhankelijke input → geen bet |

**Vroeg seizoen (speeldag 1–5):** "rolling xG laatste 5–8" bestaat dan niet. Eis het niet en
verzin het niet. Gebruik xG van vorig seizoen en markeer expliciet transfers en
selectiewisselingen als onzekerheid. Bij promovendi/nieuwkomers zonder vergelijkbare historie:
`LIGHT` of `NONE`.

---

## 5. Outputformat

### Dekkingsrapportage (bovenaan, verplicht)

Een tabel met elke competitie uit je runlijst en precies één status:

| Status | Betekenis |
|---|---|
| `GEANALYSEERD` | wedstrijden vandaag + datadekking |
| `GEEN WEDSTRIJD` | niets op de kalender vandaag |
| `BUITEN DATADEKKING` | wedstrijden vandaag, maar geen werkende onafhankelijke kansbron (noem welke bron faalde + status) |
| `AFGEKAPT` | wel dekking, maar buiten `MAX_DEEP_ANALYSES` gevallen (noem het aantal) |

Doe niet alsof de dekking volledig is als dat niet zo is.

### Per wedstrijd

Bij een **bet**:

```
[Thuis] – [Uit] · [aftrap lokale tijd NL] · [competitie]
Data: FULL | LIGHT
Bet: [markt + selectie] — Odds: best [x.xx] ([bron]) of target ≥ [x.xx]
Implied prob: xx.x%  •  My prob: xx.x%
Edge: +x.x pp  •  Confidence: High | Medium | Low
Inputs: [de sturende onafhankelijke inputs, met bron per cijfer]
Onderbouwing: [max 5 zinnen, data-gedreven]
```

Bij **geen bet**:

```
[Thuis] – [Uit] · [aftrap] · [competitie]
Data: FULL | LIGHT | NONE
GEEN BET — [reden in één regel: edge onder drempel / geen onafhankelijke input /
             odds buiten band / data conflicterend]
```

### Topselectie

Rangschik alle gepubliceerde bets op **Edge × Probability × Data-betrouwbaarheid**, met dezelfde
formule waarmee je in §1 de markt binnen een wedstrijd hebt gekozen:

```python
from scripts.model import selection_score
selection_score(edge_pp, my_prob, data_tier)      # = edge_pp × my_prob × (FULL 1.0 | LIGHT 0.5)
```

Eén weegregel voor beide, zodat de selectie die je publiceert en de plek die hij in de shortlist
krijgt niet uit elkaar kunnen lopen. Zet de score in de tabel, zodat de volgorde na te rekenen is
in plaats van te geloven.

Geef de top `MAX_SHORTLIST`, met per bet: Probability • Edge • Score • Risicoklasse
(Low/Medium/High) • waarom deze wél en de eerstvolgende net niet. Maximaal
`MAX_LIGHT_IN_SHORTLIST` bets met `LIGHT`.

**Deze topselectie hoort óók op de HTML-pagina van §6c, niet alleen in het markdown-runrapport.**
Dat is toegevoegd op 22 aug 2026, op verzoek van de gebruiker, nadat hij hem in beide dagrapporten
miste. En terecht: `report.py` rendert de bets sinds zijn bestaan ongeordend onder elkaar en deed
niets met het `shortlisted`-veld dat wél in `picks.jsonl` staat — `grep -c shortlisted scripts/report.py`
gaf 0. Op een dag met dertien bets bleef daarmee precies de vraag onbeantwoord die de gebruiker
stelt: welke zou ik nou spelen. `render_shortlist()` doet dat nu, en `rank_picks()` zet ook de
bets zelf op scorevolgorde, zodat de twee rapporten van dezelfde run niet uiteen kunnen lopen.

Het opgeslagen `shortlisted`-veld is daarbij leidend, want dat is het besluit van de run zelf
(inclusief `MAX_LIGHT_IN_SHORTLIST`). **Zet dat veld dus goed** — staat het op elke pick `false`,
dan valt de pagina terug op de bovenste `MAX_SHORTLIST` op score en gaat `MAX_LIGHT_IN_SHORTLIST`
verloren. `report.py` leidt de dagsoort zelf af uit de datum (`max_shortlist()`: 3 op ma–do, 5 op
vr–zo), dus die hoeft nergens te worden meegegeven.

**Risicoklasse is iets anders dan score, en dat blijft zo.** De score rangschikt; de risicoklasse
waarschuwt. Een bet kan bovenaan staan én High risico zijn — dat was op 14 aug het geval bij AGF,
waar de markt 18 procentpunt afweek van het model. Vervang het een niet door het ander.

Zijn er minder gekwalificeerde bets dan `MAX_SHORTLIST`? Lever er minder. **Vul niet aan.**

### "Net niet" — verplicht, ook (juist) bij nul bets

Elke afgewezen kandidaat die een echte edge liet zien, krijgt een regel met **het cijfer per poort**.
Niet alleen de poort die hem afwees: alle drie de getallen, zodat zichtbaar is of het één poort was
of een breed tekort.

| Kolom | Wat erin staat |
|---|---|
| xG-model | `edge_pp` uit `analyze_match`, mét de vroeg-seizoenscorrectie |
| 2e methode | `edge_pp` uit `analyze_match_from_splits` |
| zwakste stand | `min_edge` uit `robustness_check` — het laagste punt van het (shrink, rho)-grid |
| valt af op | `edge` / `robuustheid` / `tweede_methode` / `odds` / `data` |

Leg die cijfers vast in `data/run-state/` onder de wedstrijd, als `near_miss`:

```json
{"match": "Silkeborg – OB Odense", "tier": "FULL", "bet": false,
 "near_miss": {"market": "1X2 — OB Odense wint", "odds": 2.58,
               "edge_xg": 7.29, "edge_split": 0.54, "edge_robust_min": 5.65,
               "failed_gate": "tweede_methode"}}
```

`scripts/report.py` rendert daar de sectie "Net niet" van het dagrapport uit. **Typ die tabel niet
over in het prosebestand** — dan lopen de twee rapporten van dezelfde run uiteen, en dat is precies
de fout die `report.py` moest wegnemen.

Waarom dit moet (verzoek van de gebruiker, 10 aug 2026): een run met nul bets leest anders als "er
was niets", terwijl het verschil tussen *geen enkele kandidaat* en *drie kandidaten die op een haar
afvielen* precies is wat je over meerdere dagen wilt kunnen zien. Het is ook de enige manier om te
merken dat één poort structureel alles wegvangt: valt er een week lang alles af op `tweede_methode`,
dan is de vraag of de twee methodes systematisch uiteenlopen — en dat is een bevinding, geen ruis.
Neem dezelfde tabel op in het markdown-runrapport onder de topselectie.

### Aftraptijden

Rapporteer in **NL-tijd**. Let op de tijdzone van de bron: Britse sites (Sporting Life, Oddschecker,
BBC) geven doorgaans UK-tijd, wat in de zomer NL −1 uur is. Labelt een bron de tijdzone niet
expliciet, dan reken je om, **zeg je dat je hebt omgerekend**, en controleer je één aftraptijd tegen
een tweede bron als sanity-check. Een aftraptijd die er een uur naast zit maakt de hele bet
onbruikbaar.

### Odds

Noteer het tijdstip van uitlezen — odds bewegen. Geef beste prijs + bookmaker als die te bepalen
is; anders "target minimum odds ≥ …". Een geaggregeerde beste prijs zonder herleidbare
bookmaker: noteer de aggregator als bron en zeg dat de bookmaker niet herleidbaar was.

### Onderaan, letterlijk

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.

---

## 6. Vastleggen in de repo

### 6a. Waar je naartoe pusht: `main`

Stage -2 ruimt aan het begin van de run op wat al uiteen is gelopen. Deze paragraaf zorgt dat er
niets nieuws bij komt: **je pusht naar `main`.** Niet naar de branch die de omgeving je deze sessie
heeft toegewezen — die naam is elke run anders, en dat is precies hoe de waaier aan takken ontstaat
die Stage -2 moet opruimen.

```bash
git push origin HEAD:main
```

Drie dingen om te weten:

- **Toestemming.** Een sessie weigert standaard naar een andere branch te pushen dan de toegewezen.
  Beide scheduler-teksten geven daarom expliciet toestemming om naar `main` te pushen. Ontbreekt die
  toestemming in de prompt waarmee je draait, push dan naar je eigen branch, **meld bovenaan het
  runrapport en in de notificatie dat de run niet op `main` staat**, en vraag om de scheduler-tekst
  bij te werken. Dan weet de volgende run dat er iets te mergen valt.
- **Botsing.** Wordt de push geweigerd omdat `main` intussen is opgeschoven (de andere run was je
  voor), fetch dan opnieuw, merge volgens de conflictregels van Stage -2, en push nog een keer.
  Forceer nooit: aan de andere kant hangt een echte run met echte picks. Dit is geen randgeval — het
  gebeurde op 10 aug 2026 al bij de eerste poging, omdat de twee runs elkaar overlapten.
- **Tussentijds.** Het voortgangsbestand na elke afgeronde competitie (Stage -1) push je ook naar
  `main`. Wacht daar niet mee tot het eind: de container wordt weggegooid zodra de sessie stopt.

### 6b. Wat je vastlegt

Elke run, ook een run met nul bets:

1. **Runrapport** → `runs/YYYY-MM-DD-run-<a|b>.md` (zie `runs/TEMPLATE.md`).
2. **Picks** → append één JSON-regel per gepubliceerde bet aan `data/picks.jsonl`
   (schema: `schema/pick.schema.json`; valideer met `scripts/ledger.py validate`).
3. **Bronstatus** → werk `data/source-health.json` bij met wat je deze run gemeten hebt.
4. **Afwikkeling** → uitkomsten van Stage 0 verwerkt in `data/picks.jsonl`.
5. **Schaduwlogboek** → `python3 scripts/shadow.py collect --date <datum> --run <a|b>`, en de
   schaduwpicks van vorige runs afwikkelen (zie 6d).
5c. **Kalibratielogboek** → een `calibration`-blok per doorgerekende wedstrijd in
   `data/run-state/`, en daarna `python3 scripts/calibration.py collect --run <a|b> --date <datum>`.
   Zie 6e; neem `calibration.py stats` op in het runrapport.
5b. **Marktdekking aantonen** → noteer bij elke geanalyseerde wedstrijd in `data/run-state/` een
   `markets_checked` met de markten die je werkelijk hebt doorgerekend, en draai daarna:

   ```bash
   python3 scripts/progress.py verify --run <a|b> --date YYYY-MM-DD
   ```

   Dit moet groen zijn vóór de commit. Namen: `1X2`, `DC`, `DNB`, `AH`, `OU`, `BTTS`. Een markt
   waarvoor geen odds te vinden waren telt óók als bekeken — noteer hem dan met de reden erbij
   (`"AH": "geen spreads bij The Odds API voor deze competitie"`), niet als gat. Wedstrijden met
   `tier = NONE` worden overgeslagen; daar valt geen markt door te rekenen.

   Waarom dit een aparte stap is: §1 schreef "ga alle markten langs" al vanaf het begin voor, en
   een week lang gebeurde het niet — 11 van de eerste 15 picks waren een 1X2, nul een handicap.
   Dat bleef onopgemerkt omdat er nergens werd vastgelegd wát er per wedstrijd was bekeken, alleen
   wát eruit kwam. Een regel die niemand kan nalopen is een voornemen, geen regel. Dit is met opzet
   een controle op de administratie en niet op de uitkomst: nul bets is een geldige uitkomst, een
   wedstrijd waarbij vier markten niet eens zijn opgezocht niet.
6. **Commit en push** naar `main` (zie 6a: `git push origin HEAD:main`). Zonder push is de run
   verdwenen zodra de container wordt opgeruimd.
7. **Voortgangsbestand afsluiten** — `scripts/progress.py`: `mark_completed(state)` + `save(state)`,
   en nog een keer committen/pushen (zie Stage -1). Zonder deze stap denkt een latere aanroep
   diezelfde dag dat de run nog loopt.

### 6d. Het schaduwlogboek — wat de poorten hebben tegengehouden

`picks.jsonl` bevat alleen wat er wél doorheen kwam. Daaruit is per definitie niet af te lezen of
een poort je geld bespaart of alleen bets: de afgewezen kandidaten verdwenen tot 11 aug 2026
spoorloos. `data/shadow.jsonl` sluit dat gat — elke `near_miss` uit `data/run-state/` wordt daar
een schaduwpick en wordt daarna net zo afgerekend als een echte.

Twee handelingen per run, allebei verplicht:

```bash
# 1. de kandidaten van vandaag erin (leest data/run-state/, doet niets bij nul kandidaten)
python3 scripts/shadow.py collect --date YYYY-MM-DD --run <a|b>

# 2. de schaduwpicks van eerdere runs afwikkelen, net als Stage 0 voor echte picks
python3 scripts/shadow.py open
python3 scripts/shadow.py settle <id> won|lost|void --score 2-1
```

**Reken 1X2, Double Chance, Draw No Bet, O/U en BTTS af op de stand na 90 minuten** (reguliere tijd
plus blessuretijd), nooit op de eindstand na verlenging of strafschoppen. Bij bekerduels en
Europese voorrondes zijn dat verschillende getallen, en `status.scoreStr` van Fotmob geeft de
**eind**stand — dus inclusief verlenging. Zoek bij een knock-outduel de doelpuntminuten op en tel
zelf tot 90'. Dit is geen theoretisch punt: op 12 aug 2026 wikkelde Run B Bodø/Glimt – Union
St.Gilloise af op 3–2 en zette de gelijkspelpick op `lost`, terwijl het na 90 minuten 2–2 stond en
die pick dus **gewonnen** was. Die ene regel verschoof de ROI van poort `tweede_methode` met 81
procentpunt (−33.8% → +47.0% over zes gevallen) en keerde de conclusie eronder om. Bij de kleine
aantallen waar 6d over gaat, weegt één verkeerd afgerekende regel zwaarder dan alles wat de poort
werkelijk doet.

Neem `python3 scripts/shadow.py stats` op in het runrapport, náást `ledger.py stats`. De
uitsplitsing per `failed_gate` is het punt: staat één poort structureel op een positieve ROI, dan
houdt die poort winnende bets tegen en hoort hij ruimer; is de ROI structureel negatief, dan doet
hij zijn werk en blijft hij zoals hij is.

**Lees dit niet te vroeg.** Bij minder dan ~30 afgewikkelde schaduwpicks per poort is elk verschil
ruis — de eerste meting op 11 aug 2026 stond op 5 afgewikkelde kandidaten en zei dus niets. Kijk
naar de richting over weken, niet naar het getal van vandaag, en pas geen enkele drempel aan op
basis van één dag. Dat laatste zou dezelfde fout zijn als waarmee de oude poort 5 werd ingevoerd:
één anekdote tot regel verheffen.

Draai daarna `python3 scripts/ledger.py stats` en neem hit rate, ROI en Brier score op in het
runrapport. Dit is de enige manier waarop "gaat het goed of niet" een antwoord met een getal krijgt.

### 6e. Het kalibratielogboek — zit het model systematisch scheef?

`ledger.py` meet of de bets winnen en `shadow.py` of de poorten iets tegenhouden. Geen van beide
beantwoordt de vraag daaronder: **staat `my_prob` als schatter systematisch scheef, en waar?**

Op 22 aug 2026 bleek dat te kunnen. Run A publiceerde die dag dertien bets, en nameten liet zien dat
het niet dertien vondsten waren maar grotendeels één afwijking: over de dertig doorgerekende duels lag
het model **+4.19 pp boven** de de-vigde marktkans op uitkomsten die de markt onder de 25% zet, en
**−6.67 pp eronder** bij favorieten. Tien van de dertien bets lagen daardoor in dezelfde hoek.

De uitsplitsing wees bovendien een andere oorzaak aan dan verwacht. Niet `shrink`:

| | longshots (<25%) | favorieten (>50%) |
|---|---|---|
| `analyze_match` bij `shrink = 1.0` | **+0.47 pp** | **+0.55 pp** |
| `analyze_match_from_splits` | **+5.75 pp** | **−9.87 pp** |

De xG-methode is vlak; de afwijking komt vrijwel volledig uit de splitsmethode. En dat is
rekenkundig: `analyze_match` **vermenigvuldigt** sterkteverhoudingen, terwijl
`analyze_match_from_splits` twee doelpuntgemiddelden **optelt en door twee deelt**. Middelen trekt
naar het midden — gemeten gebruikte de splitsmethode 62% van de spreiding in verwacht doelsaldo van
de xG-methode. Dat slijt dus niet naarmate het seizoen vordert; het is geen vroeg-seizoenseffect.

Omdat `my_prob` het **ongewogen gemiddelde** van die twee is, komt de helft van elke gepubliceerde
kans uit een structureel samengedrukte schatter. Dat is een reden om te meten, nog niet om te
verbouwen — één dag is geen bevinding (§6d). Daarom, **elke run**:

```bash
python3 scripts/calibration.py collect --run <a|b> --date YYYY-MM-DD
python3 scripts/calibration.py stats
```

Leg daarvoor per doorgerekende wedstrijd een `calibration`-blok in `data/run-state/` vast, met de
**de-vigde** marktkans en de modelkansen voor de drie 1X2-uitkomsten:

```json
"calibration": {
  "market":        [0.45, 0.27, 0.28],
  "p_xg":          [0.41, 0.28, 0.31],
  "p_xg_noshrink": [0.43, 0.28, 0.29],
  "p_split":       [0.38, 0.29, 0.33]
}
```

`scripts/calibration.devig(odds)` doet het wegdelen. 1X2 is met opzet de meetmarkt: die is via
BetExplorer elke run gratis en voor vrijwel elke wedstrijd beschikbaar, en de drie uitkomsten
sommeren tot 1. `p_xg_noshrink` is één extra `analyze_match(..., shrink=1.0)` per wedstrijd en kost
dus vrijwel niets — zonder dat veld is het aandeel van `shrink` niet te scheiden van dat van de
splitsmethode. Neem de uitvoer van `stats` op in het runrapport, naast `ledger.py stats` en
`shadow.py stats`.

**Lees dit net zo voorzichtig als 6d.** Onder ~150 waarnemingen in de longshotbak (ruwweg vijf volle
rundagen) is een paar procentpunt ruis. Twee dingen die pas daarna aan de orde zijn, en géén van
beide vandaag: de splitsmethode multiplicatief en op het competitiegemiddelde genormaliseerd maken
zodat §1 twee schatters van dezelfde grootheid middelt, of `shrink` laten aflopen naarmate het
seizoen vordert — die staat nu hard op 0.8 zonder afloopmechanisme, terwijl de docstring hem met
"vroeg seizoen" verantwoordt.

Let ten slotte op wat poort 6 hier **niet** doet: het `(shrink, rho)`-grid van `robustness_check`
varieert alleen `analyze_match` — precies de methode die vlak blijkt. "Deze bet overleeft het hele
grid" zegt dus niets over de methode die de afwijking veroorzaakt.

### 6c. Het leesbare dagrapport — verplicht, elke run

Het markdown-runrapport hierboven is voor de repo: methode, metingen, bronstatus. De gebruiker
leest dat niet, en had daar gelijk in — het opent met bronstatus, gebruikt `edge_pp`, "de-viggen"
en Brier zonder uitleg, en de bets staan als twee regels tussen alle andere wedstrijden. Daarom
levert elke run **ook** een HTML-pagina op:

1. Schrijf `runs/YYYY-MM-DD-run-<a|b>.prose.json` — alleen de tekst die een mens moet schrijven:
   `verdict`, `bets` (per pick-id een `why` in gewone taal + een risicozin), `coverage_notes`,
   `todo`, `finding` en `settled`. Zie `runs/2026-08-09-run-a.prose.json` als voorbeeld.
   Gebruik voor `risk_level` **`low` / `med` / `high`**; `report.py` normaliseert sinds 22 aug 2026
   ook `medium`, `laag`, `gemiddeld` en `hoog`, maar tot die datum leverde het verschil tussen
   Run A's `med` en Run B's `medium` stilzwijgend een chip zonder kleur op.
2. Draai `python3 scripts/report.py --run <a|b> --date YYYY-MM-DD`. Bets, dekkingstabel en de
   stand van het logboek komen automatisch uit `picks.jsonl` en `data/run-state/` — niet
   overtypen, want dan gaan de twee rapporten uiteenlopen.
3. Publiceer het bestand als Artifact en **zet die link in de notificatie** (§7).

Schrijf de prose voor iemand die de repo niet kent en het jargon niet spreekt. Geen `edge_pp`,
geen "de-viggen", geen ρ of shrink: die staan in de woordenlijst onderaan de pagina en horen niet
in de lopende tekst. Noem bedragen, tijden en bookmakers concreet.

Ook bij **nul bets** draait dit. De pagina zegt dan met zoveel woorden dat er niets gekwalificeerd
heeft, en de dekkingstabel laat zien dat er wél gekeken is. Dat is precies het geval waarin een
lege notificatie de gebruiker in het ongewisse laat — en sinds 17 aug 2026 gaat er bij nul bets dus
ook echt een notificatie uit, met deze pagina eraan (§7).

---

## 7. Wanneer een notificatie sturen

De run draait terwijl niemand meekijkt; wat alleen in het transcript staat, bereikt niemand.

**Elke run stuurt precies één notificatie. Altijd, ook bij nul bets, ook als er niets bijzonders
is gebeurd.** Geen uitzonderingen, geen afweging — de afweging gaat alleen over de *inhoud*, niet
over het wel of niet sturen. Dit is een wijziging van 17 aug 2026; de reden staat onderaan deze
paragraaf en is belangrijk genoeg om te lezen voordat je hem terugdraait.

Zet in **elke** notificatie de link naar de HTML-pagina uit §6c. Dat is de plek waar de gebruiker
het hele verhaal kan lezen, en zonder die link is de melding een dood bericht.

### Welke vorm

**Zijn er bets** — leid met de beste: markt en selectie, de koers, de bookmaker, de aftraptijd in
NL-tijd. Dan het aantal overige bets, dan de link. Geen methodediscussie; die staat op de pagina en
in het markdown-rapport.

> Beste bet vandaag: Sønderjyske +1.25 @ 1.94 (Pinnacle), aftrap 20:00. Nog 2 andere bets in de
> selectie. Hele verhaal: <link>

**Zijn er geen bets** — dan is dit een hartslag: kort, feitelijk, en het moet er ondubbelzinnig in
staan dat de run *gedraaid* heeft. Noem het aantal wedstrijden dat je bekeek, hoeveel er door de
datadekkingspoort kwamen, en in één halve zin waaróm er niets kwalificeerde.

> Run B gedraaid, 0 bets. 9 wedstrijden, 1 met datadekking; die viel af op robuustheid. Bronnen
> allemaal in orde. <link>

**Is er iets mis** — een afgewezen sleutel, een omgevallen bron, een geweigerde push, een run die
niet op `main` staat, een afwikkelingsreeks die opvalt (5+ verliezers) — dan gaat dat **vooraan**,
vóór de bets of de hartslag. Dit is het enige geval waarin de notificatie langer mag zijn dan drie
regels: noem wat er stuk is en wat de gebruiker eraan kan doen.

Meer dan één notificatie per run is niet de bedoeling. Heb je zowel bets als een blokkade, zet ze
in hetzelfde bericht — blokkade eerst.

### Waarom dit is veranderd (17 aug 2026, op verzoek van de gebruiker)

Tot vandaag stond hier het omgekeerde: géén notificatie bij "een routinematige, gezonde run zonder
gekwalificeerde bets". De bedoeling was de aandacht van de gebruiker te sparen, en op zichzelf is
dat een goed doel. Maar de regel had een gat dat niemand had gezien: **een gezonde run met nul bets
en een run die nooit is afgegaan, zien er van de telefoon af precies hetzelfde uit.** Beide zijn
stilte.

Dat is geen theoretisch bezwaar. Run B stuurde op 11, 12, 13 en 17 aug 2026 geen notificatie, elke
keer correct volgens de oude regel, elke keer met een gepubliceerd dagrapport dat de gebruiker niet
wist te bestaan. Op 17 aug was de eerste vraag van de gebruiker na die vier dagen: *"Why did run b
didn't run this morning?"* — terwijl hij die ochtend om 05:11 gedraaid had, negen wedstrijden had
bekeken, alle zes markten had doorgerekend en drie commits naar `main` had gepusht. De routine had
vier dagen lang niet te onderscheiden gezwegen van een kapotte scheduler.

De winst van de nieuwe regel zit niet in het bericht zelf maar in wat stilte nu betekent: zolang er
elke run één melding komt, is **een uitgebleven melding zelf het signaal** dat er iets stuk is.
Onder de oude regel was die informatie er niet, en kon de gebruiker een defect alleen ontdekken
door in de repo te gaan kijken.

De kosten zijn eerlijk te noemen: dit is één extra bericht per dag per run op dagen dat er niets te
melden valt. Dat is precies wat de oude regel wilde voorkomen. De afweging is bewust die kant op
gemaakt — een melding die de gebruiker één seconde kost weegt niet op tegen dagen waarin hij niet
weet of zijn routine nog leeft. Draai dit niet terug zonder de vier dagen hierboven mee te wegen.

---

## 8. Wat deze regels expliciet níet oplossen

De bronnen zijn nog steeds grotendeels dichtgezet (zie `data/source-health.json`). Zolang er geen
API-key beschikbaar is, zullen veel competities in `BUITEN DATADEKKING` blijven vallen en zullen
runs vaak nul bets opleveren. Dat is de eerlijke uitkomst van de huidige input, niet een defect
in deze regels. De structurele fix staat in `README.md` onder "Nog te doen".
