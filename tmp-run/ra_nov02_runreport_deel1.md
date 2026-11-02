# Run A — 2026-11-02

**Gestart:** 03:05 CET · **Bets gepubliceerd:** 3 · **Wedstrijden diep geanalyseerd:** 12 van 12 in het inzetvenster (0 op `data_tier = NONE`)

**Branch:** deze run is op `claude/stoic-davinci-flhpc4` gestart en **naar `main` gepusht** (§6a); de scheduler-prompt geeft daar expliciet toestemming voor. Er is dus niets te mergen voor een volgende run.

**Dit rapport is voor de repo.** Het leesbare dagrapport staat op
[de HTML-pagina](https://claude.ai/artifact/WrTKptPwewDDigqPnJuMf8) en, als tweede route (§6c, 14 okt), in
[`runs/2026-11-02-run-a.dagrapport.md`](https://github.com/aistref/football/blob/main/runs/2026-11-02-run-a.dagrapport.md).

---

## Stage -2 — takken

`git rev-parse --is-shallow-repository` gaf **true**: de container kreeg de repo opnieuw als ondiepe kloon. Vóór het unshallowen leken **73 van de 82 takken** eigen commits te hebben (3 tot 604 stuks); ná `git fetch --unshallow origin` (674 commits lokaal) zijn dat **nul van de 82**. Dat is exact het valse alarm dat §3 Stage -2 beschrijft, en het is de reden dat die stap vóór alles komt.

De commitgraaf is echter niet het antwoord (§3 Stage -2, 27 sep). `scripts/branchaudit.py --ref HEAD` vergelijkt alle vijf de logboeken **per record op de inhoud**:

```
STAGE -2 — alle takken vergeleken met HEAD, per record op de inhoud
  82 tak(ken) nagelopen · ondiepe kloon: false

  data/picks.jsonl                   510 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/shadow.jsonl                 1645 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/context-log.jsonl            1953 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/calibration.jsonl            7069 op HEAD  (sleutel: date.run.match.market.method)  -> VOLLEDIG
  data/source-health.json            147 op HEAD  (sleutel: bladpaden)  -> VOLLEDIG
       sources.oddspapi (+5 bladpad(en)) — bekend besluit, geen vondst
         OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het 20K-creditplan (commit f342894, README). Besluit, geen verlies.
  data/coverage.json                 324 op HEAD  (sleutel: bladpaden)  -> VOLLEDIG

Niets te verenigen: elk record dat op een tak staat, staat ook op HEAD.
```

`HEAD` was bij de start bit-voor-bit gelijk aan `origin/main` (0 commits voor, 0 achter). Er viel niets te verenigen. **Wat er wél openstond zijn picks en niet takken:** `picks.jsonl` had tien openstaande picks van 1 november en `shadow.jsonl` zesenvijftig schaduwrijen; die horen bij Stage 0 en staan daar.

Eén bekend verschil blijft staan en is géén vondst: `sources.oddspapi` staat op vijf oude takken en niet op `HEAD`. OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het 20K-creditplan (commit `f342894`). Besluit, geen verlies — `branchaudit.py` merkt dat zelf aan.

## Stage -1 — hervatting

Geen voortgangsbestand voor 2 november bij de start, dus dit is een verse run. `resumed_count` = 0 en `sessies` bevat één id — géén hervatting, en dat is sinds 16 oktober een afgeleid getal in plaats van een teller (§3 Stage -1).

## Dekkingsrapportage

| Competitie | Status | n | bets | datalabels / eerstvolgende ronde |
|---|---|---|---|---|
| Ekstraklasa (POL) | `GEANALYSEERD` | 3 | 2 | 2 FULL, 1 LIGHT |
| Serie A (ITA) | `GEANALYSEERD` | 2 | 1 | 2 FULL |
| Primeira Liga (POR) | `GEANALYSEERD` | 2 | 0 | 2 FULL |
| Premier League (ENG) | `GEANALYSEERD` | 1 | 0 | 1 FULL |
| La Liga (ESP) | `GEANALYSEERD` | 1 | 0 | 1 LIGHT (promovendus Deportivo) |
| Ligue 1 (FRA) | `GEANALYSEERD` | 1 | 0 | 1 FULL |
| Super Lig (TUR) | `GEANALYSEERD` | 1 | 0 | 1 FULL |
| Danish Superliga (DEN) | `GEANALYSEERD` | 1 | 0 | 1 FULL |
| Bundesliga (GER) | `GEEN WEDSTRIJD` | 0 | — | eerstvolgende ronde 6 nov |
| Championship (ENG) | `GEEN WEDSTRIJD` | 0 | — | eerstvolgende ronde 4 nov |
| Eredivisie (NED) | `GEEN WEDSTRIJD` | 0 | — | eerstvolgende ronde 6 nov |
| Belgian Pro League (BEL) | `GEEN WEDSTRIJD` | 0 | — | eerstvolgende ronde 4 nov |
| Scottish Premiership (SCO) | `GEEN WEDSTRIJD` | 0 | — | eerstvolgende ronde 7 nov |
| UEFA Champions League | `GEEN WEDSTRIJD` | 0 | — | 4 nov |
| UEFA Europa League | `GEEN WEDSTRIJD` | 0 | — | 4–5 nov |
| UEFA Conference League | `GEEN WEDSTRIJD` | 0 | — | 5 nov |
| FA Cup (ENG) | `GEEN WEDSTRIJD` | 0 | — | 6 nov (BetExplorer, 40 teamparen) |
| Coppa Italia (ITA) | `GEEN WEDSTRIJD` | 0 | — | 1 dec (BetExplorer, 8 teamparen) |
| KNVB Beker (NED) | `GEEN WEDSTRIJD` | 0 | — | 1 dec (BetExplorer, 16 teamparen) |
| DFB Pokal (GER) | `GEEN WEDSTRIJD` | 0 | — | 1 dec (BetExplorer, 8 teamparen) |
| League Cup (ENG) | `GEEN WEDSTRIJD` | 0 | — | 15 dec (BetExplorer, 4 teamparen) |

**Geen `AFGEKAPT`-regel en geen `BUITEN DATADEKKING`-regel.** Twaalf duels tegen een maandagcap van **40** (`ranking.max_deep_analyses`), dus er is nul afgekapt en alle twaalf zijn doorgerekend over alle zes de markten (`progress.py verify` groen). De datarijkdom liep van **4,5** (Raków Częstochowa – Pogoń Szczecin, opstellingsblok op `unavailable`) tot **7,0** (Lorient – Brest). Die twee getallen staan hier omdat §3 Stage 4 ze eist zodra de cap knelt; ze staan er ook als hij dat niet doet, want anders is achteraf niet na te gaan of de afkapping ergens op sloeg.

**De bekers zijn bij twee bronnen nagetrokken.** De Fotmob-daglijst geeft voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) nul duels in het venster; BetExplorer bevestigt dat voor alle vijf, met de eerstvolgende ronde erbij. Alle vijf fixturepagina's gaven teamparen, dus er is nergens een lege pagina die als bevestiging zou kunnen worden gelezen — anders dan op 1 november, toen de DFB Pokal-pagina leeg was. "Niet in de daglijst" mag nooit als `GEEN WEDSTRIJD` worden opgeschreven zonder tweede bron; dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte.

## Bronstatus deze run

`python3 scripts/api_check.py`, letterlijk:

```
Controle van de databronnen die een sleutel nodig hebben.

=== The Odds API (odds per bookmaker) ===
  OK — 48 actieve voetbalcompetities beschikbaar.
  Quota: 19893 over, 107 gebruikt deze maand.
  Sportkeys van de repo: 33 van 34 actief vandaag.
    NIET ACTIEF  Coppa Italia (ITA)             soccer_italy_coppa_italia
  Actieve sportkeys die de repo NIET kent (mogelijk een gat in SPORT_KEYS):
    soccer_brazil_serie_b  (Brazil Série B / Campeonato Brasileiro Série B)
    soccer_germany_liga3  (3. Liga - Germany / German Soccer)
    soccer_sweden_superettan  (Superettan - Sweden / Swedish Soccer)
    soccer_uefa_nations_league  (UEFA Nations League / UEFA Nations League)

=== API-Football (statistieken) ===
  API_FOOTBALL_KEY niet gezet — overgeslagen.
  Dat is een besluit van de gebruiker (27 sep 2026), geen storing: hij wil hier geen
  geld aan uitgeven. De kanskant komt van Fotmob en Understat. Zie
  _shared-rules.md §3, 'API_FOOTBALL_KEY komt er niet'. Niet als actiepunt melden.

=== Samenvatting ===
  odds (prijzen)        OK
  statistieken (kansen) niet beschikbaar
```

Wat daaruit volgt:

- **Geen sleutel is afgewezen.** The Odds API werkt, met 19893 credits over en 107 verbruikt deze maand.
- **`API_FOOTBALL_KEY` ontbreekt met opzet.** Besluit van de gebruiker van 27 september 2026; geen gat, geen actiepunt, en het staat hier als boekhouding zodat een volgende run ziet dat de stilte een keuze was (§3).
- **De enige inactieve sportkey is Coppa Italia**, en dat klopt met de tweede bron: BetExplorer zet de eerstvolgende ronde op 1 december. Vier actieve sportkeys kent de repo niet; geen van vier staat op een runlijst van Run A.

### Understat is onbereikbaar — nieuw vandaag

**Alle vier de door Understat gedekte competities die vandaag spelen gaven dezelfde fout** (Bundesliga speelt niet):

```
understat Premier League (ENG): UnderstatError: URLError op
  https://understat.com/getLeagueData/EPL/2025: <urlopen error Tunnel connection failed: 502 Bad Gateway>
understat Serie A (ITA):   idem op /Serie_A/2025
understat La Liga (ESP):   idem op /La_liga/2025
understat Ligue 1 (FRA):   idem op /Ligue_1/2025
```

**Het is niet het script en niet de site-beveiliging.** Een losse `curl` naar hetzelfde adres geeft `CONNECT tunnel failed, response 502`, en de proxystatus van de container noteert het als `connect_rejected — gateway answered 502 to CONNECT (policy denial or upstream failure)` voor `understat.com:443`. Dit is dus iets anders dan de Cloudflare-challenge van fbref, Forebet, FootyStats en PredictZ: daar antwoordt de site, hier komt de verbinding niet tot de site. De regel van §3 ("niet omzeilen") is hier niet eens van toepassing — er is niets om langs te gaan, en er is geen headless browser, challenge-solver of proxy ingezet.

Wat het **kost**: het kalibratieblok van §6e krijgt vandaag geen Understat-arm voor die vier competities, dus de vergelijking tussen de eigen xG-arm en de Understat-arm — die sinds 19 september structureel scheever staat (+3,11 pp op longshots tegen +0,90 voor de eigen arm) — kan over deze dag niet worden gemaakt.

Wat het **niet kost**: geen bet en geen kansschatting. Understat staat per ontwerp **naast** het eigen model in het kalibratieblok en gaat niet in `my_prob` of `prob_sources` (§2, §4). De kanskant van alle twaalf duels kwam van Fotmob, en Fotmob leverde zonder fout.

Wat er gebeurt **als het blijft**: dan is de redundantie waarvoor Understat sinds 31 augustus bestaat weg en wordt het kalibratielogboek voor die vijf competities eenarmig. Dat is verlies aan **controle**, niet aan kansinput. Een run repareert een netwerkpolicy niet zelf. **De uitzondering van §3 punt 3 is vandaag niet aan de orde** — die geldt zodra *Fotmob* omvalt, en dan is er voor vrijwel elke wedstrijd geen onafhankelijke kansbron meer.

### De overige bronnen

| Bron | Stand deze run |
|---|---|
| **Fotmob** | `ok`. Daglijsten 2 en 3 nov plus 1 en 2 nov voor de afwikkeling. `idcheck.py` gaf voor alle **33** `fotmob_id`'s uit `coverage.json` een bruikbare stand. Standen van de acht spelende competities plus de divisie eronder voor de twee omgerekende ploegen. Context voor **alle twaalf** duels zonder fout (acht voorspelde opstellingen, drie laatste basiselftallen, één op `unavailable`). Vandaag de **enige** xG-bron. |
| **The Odds API** | `ok`. Alle acht spelende competities hebben een sportkey en kregen de volledige bulk (h2h + spreads + totals, 3 credits per competitie, **24** in totaal), plus een tweede ronde BTTS van **10** credits voor de tien duels met een kandidaat-edge (§1a stap 2). **34 van een plafond van 342**, 19859 over. Geen duel hoefde op het gratis marktgemiddelde te leunen. |
| **BetExplorer** | `ok`. Marktgemiddelde 1X2 voor alle acht spelende competities (7 tot 22 fixturerijen), plus de fixturepagina's van de vijf bekers en de drie Europese toernooien. |
| **Pinnacle** | `ok`. In de bulk-respons van alle acht competities; 1X2-oordeel voor elf van de twaalf duels met een marge van 3,0 tot 4,2%, en een totalenoordeel voor alle twaalf. |

---

## Bevinding — de dagranglijst van §5b verdrong een gekwalificeerde bet

**Dit is een reparatie in `scripts/toplist.py` en ze raakte vandaag een gepubliceerde bet.** De dagranglijst koos vanmorgen Sassuolo – Fiorentina (Under 3.5 @1,64, +7,39 pp, score 5,052) **boven** Zagłębie Lubin – Korona Kielce (1 @2,63, +8,18 pp, score 3,780). De eerste haalt zijn lat van 8,0 pp **niet**, de tweede **wel**. §5 verbiedt zo'n ruil met zoveel woorden: *"zijn er minder gekwalificeerde bets dan `MAX_SHORTLIST`, lever er dan minder — vul niet aan"*.

Er zaten **twee** fouten op elkaar.

**(1) De grens in `_cut` stond een plek verkeerd.** De toets was `if len(boven) > n`, met `boven` de selecties boven hun eigen lat. Vandaag stonden er **drie** boven de lat en was `MAX_SHORTLIST` **drie**, dus `3 > 3` was onwaar en de lijst werd puur op `selection_score` gevuld. Maar de grens was niet het hele probleem: ook bij **minder** dan `n` boven de lat kon een gekwalificeerde selectie volledig uit de lijst vallen zodra er genoeg hoger scorende kandidaten ónder hun lat stonden — vijf sub-lat-kandidaten met een hoge score duwen twee gekwalificeerde selecties er dan samen uit. De reparatie is daarom geen `>` → `>=` maar een **ordening**: eerst alles boven de lat (op score onderling), daarna de rest om de lijst aan te vullen. Staan er méér dan `n` boven de lat, dan is het resultaat identiek aan de oude regel — de drempel is dan de grens, precies zoals §5b stap 5 zegt.

**(2) De keuze BINNEN een wedstrijd liep uiteen met de analyse zelf.** `build` koos per duel de hoogste `selection_score` onder *alle* publiceerbare selecties, dus ook onder de lat. Bij Zagłębie Lubin – Korona Kielce koos de analyse het 1X2 (+8,18 pp, score 3,780, lat gehaald) en koos `toplist` de **DNB** (+6,50 pp, score 3,968, lat **niet** gehaald): **twee rapporten van dezelfde run die een andere bet noemen**, wat §6c juist moet voorkomen. En die sub-lat-DNB ging daarna met score 3,968 de dagranglijst in, waar hij op fout (1) uit de lijst viel — zo verdween een gekwalificeerde bet stil. §1a kiest *"van alle selecties die alle poorten halen die met de hoogste score"*, en een selectie boven de lat haalt ook de drempel; een eronder niet. De lus vergelijkt nu op `(lat gehaald, score)` in plaats van op score alleen. Haalt geen enkele selectie van een duel haar lat, dan verandert er niets en blijft de hoogste score de vertegenwoordiger — dat is precies de rangorde-aanvulling die §5b wil.

**Wat het vandaag veranderde:** de derde regel van de lijst, van Sassuolo – Fiorentina Under 3.5 @1,64 naar Zagłębie Lubin – Korona Kielce 1 @2,63. Sassuolo gaat als `near_miss` met `failed_gate = "edge"` naar het schaduwlogboek, precies waar hij hoort.

**Waarom een run dit wél mag repareren.** Dit is geen parameter en geen poort, en er zit geen afweging over risicobereidheid in — dan zou het bij de gebruiker horen (§1a, §1e). Het is een grensgeval in de code dat twee regels uit hetzelfde bestand tegen elkaar in laat lopen, en het **faalt stil**: de lijst had precies de juiste lengte, elke regel droeg netjes zijn eigen label, en er was geen foutmelding. Dezelfde faalvorm als `calibration.py settle` (§6b-5c), het Serie B-id en `promotion.match_tier` van 31 oktober.

Het bewijs staat in **`tmp-run/ra_nov02_toplist_fix_test.py`**: vijf gevallen, geen netwerk en geen repo-state nodig. Drie over de grens (precies `n` boven de lat, minder dan `n` met hoger scorende kandidaten eronder, méér dan `n` — die laatste moet onveranderd blijven) en twee over de keuze binnen een duel.

## Bevinding — poort 9 heeft zijn meetlat gehaald

**Poort 9 (§1h) hield vandaag nul selecties tegen**: er was geen enkele FULL-Under in de band 8,0–10,0 pp waar hij met opzet bijt. Wat er wél is gebeurd, is dat de reeks waarmee die poort beoordeeld moet worden zijn eigen meetlat heeft gehaald.

| reeks | n afgewikkeld | trefkans | rendement | gem. geclaimde edge |
|---|---|---|---|---|
| `doelpunten_onder` | **35** | 37,1% (13/35) | **−30,4%** | +8,9 pp |

§6d eist ~30 gevallen voordat een reeks gelezen mag worden, en op 12 oktober stond in `_shared-rules.md` dat dat *"eerder een vraag voor december dan voor deze week"* zou zijn. Het is 2 november en het zijn er 35.

**Wat de reeks zegt:** de poort houdt verliezers tegen. −30,4% over 35 gevallen is op één categorie na de slechtste reeks van het hele schaduwlogboek (`odds` staat op −57,8%) en veel slechter dan het logboek van de gespeelde bets (−7,9%). Gisteren gingen er zes rijen in, waarvan vijf verloren. Er is dus geen grond om de rem te verlagen of te schrappen.

**Wat de reeks niet zegt:** dat `LIGHT` er ook bij hoort. Die vraag is op 12 oktober aan de gebruiker voorgelegd en beantwoord met *"eerst kijken wat deze rem doet"*. Die meting is er nu, maar ze is gedaan op `FULL` en zegt over `LIGHT` niets — daar staan tien afgewikkelde gevallen tegenover, met een rendement dat de andere kant op wijst. Een gemeten rem uitbreiden naar een populatie waar de meting hem niet steunt is wat §1c en §4 verbieden. **De poort blijft dus staan zoals hij staat en de vraag wordt niet opnieuw gesteld** (§1h, 12 okt).

De meting eronder is vandaag opnieuw bevestigd door `margins.py goalbias` — zie "Stand van het logboek".

---

## Topselectie

`MAX_SHORTLIST` = **3** (maandag). De lijst is exact vol, en de lijstlengte bindt niet: er zijn precies drie wedstrijden met een selectie die alle negen poorten haalt en er zijn drie plekken, dus `failed_gate = "lijstlengte"` krijgt vandaag geen enkele rij. *Dat klopt pas na de reparatie hierboven; ervóór viel de derde gekwalificeerde selectie wél uit de lijst.*

| # | Wedstrijd | Markt / selectie | Koers | Kans | Edge | Lat | Score | Risico |
|---|---|---|---|---|---|---|---|---|
| 1 | Atalanta – Parma · 20:45 · Serie A · `FULL` | Over/Under — Under 3.5 | 1,55 (Tipico) | 79,3% | **+14,80 pp** | 10,0 (poort 9) | **11,737** | Medium |
| 2 | Radomiak Radom – Śląsk Wrocław · 18:00 · Ekstraklasa · `LIGHT` | 1X2 — 1 (Radomiak Radom wint) | 2,2152 (Betfair, beurs; 2,24 bruto) | 63,4% | **+18,22 pp** | 16,0 (LIGHT) | **5,772** | High |
| 3 | Zagłębie Lubin – Korona Kielce · 18:00 · Ekstraklasa · `FULL` | 1X2 — 1 (Zagłębie Lubin wint) | 2,63 (Unibet SE) | 46,2% | **+8,18 pp** | 8,0 (FULL) | **3,782** | Medium |

**Alle drie halen hun eigen lat, en dat is sinds §5b van 20 september uitzondering en geen regel.** Bij alle drie is `bet_beide = true` — ze halen hun lat op de herijkte **en** op de ruwe schaal — en bij alle drie staat de zwakste stand van het (shrink, rho)-grid boven nul: **+10,69**, **+9,69** en **+6,52** pp. Dat die vlag bij een fit die vrijwel de identiteit is (`a=0,994, b=−0,004`) klopt, is te verwachten, maar hij is per selectie gecontroleerd en niet beredeneerd (§5a waarschuwt daar uitdrukkelijk voor).

**`MAX_LIGHT_IN_SHORTLIST` = 2 bindt niet**: er staat één `LIGHT`-regel in de lijst.

### Wat er tweede werd per gepubliceerde bet (§1a)

| Bet | Tweede selectie van hetzelfde duel | Score |
|---|---|---|
| Atalanta – Parma, Under 3.5 (11,737) | Over/Under — Under 3 | 11,286 |
| Radomiak Radom – Śląsk Wrocław, 1X2 1 (5,772) | Asian Handicap — Radomiak Radom −0.25 | 5,632 |
| Zagłębie Lubin – Korona Kielce, 1X2 1 (3,782) | *geen tweede selectie boven de lat* — de hoogst scorende open selectie van dit duel is de DNB op Zagłębie (+6,50 pp, score 3,968), en die haalt de lat van 8,0 niet. Dat is precies het geval uit de bevinding hierboven: hoger scorend én niet gekwalificeerd. | 3,968 (sub-lat) |

Bij Atalanta is het verschil tussen de vier Under-lijnen opvallend klein (11,035 / 11,077 / 11,286 / 11,737 voor 2.5, 2.75, 3.0 en 3.5) terwijl de edge juist afneemt van +18,58 naar +14,80 pp. Dat is `selection_score` die precies doet wat §1a van hem vraagt: een hogere trefkans weegt op tegen een paar procentpunt minder edge, en de hoogste lijn is de minst blootgestelde uitdrukking van dezelfde mening.

### De derde regel staat krap

Zagłębie Lubin haalt zijn lat met **0,18 procentpunt** over. Uitgesplitst: de xG-methode zegt **+7,14 pp** en haalt hem dus **niet**, de splitsmethode zegt **+12,72 pp**, en de gewogen 80/20-combinatie (§1f) komt op +8,18 pp uit. Poort 5 gaat open omdat beide methodes dezelfde kant van de markt kiezen — 45,2% en 50,8% tegen een marktkans van 38,0% — maar het verschil tussen de twee is vijf en een half procentpunt en de uitkomst hangt aan het gewicht. Dat gewicht is op uitslagen gemeten (§1f) en wordt vandaag niet aangeraakt; de krapte staat hier zodat ze niet uit het rapport verdwijnt.

**Lees de lijst als "dit is het beste van vandaag" en niet als "dit is een gevonden voordeel."** §1g heeft op 552 afgerekende gevallen gemeten dat er géén drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de hóógste geclaimde edge. Het logboek staat op −7,9% over 447 afgewikkelde bets, en §5b zegt zelf dat ongeveer −10% is wat je van deze lijst mag verwachten.

### Marktbalans (§1a, verplicht elke run)

| Markt | Competities met prijzen | Selecties doorgerekend | Alle poorten open | Bets |
|---|---|---|---|---|
| 1X2 | 8 van 8 (bulk h2h + gratis BetExplorer-gemiddelde) | 32 | 2 | **2** |
| Over/Under | 8 van 8 (bulk totals) | 60 | 5 | **1** |
| Asian Handicap | 8 van 8 (bulk spreads) | 41 | 2 | 0 |
| Draw No Bet | 8 van 8 (spreads, 0.0-lijn) | 15 | 0 | 0 |
| Double Chance | 8 van 8 (spreads, +0.5-lijn) | 5 | 0 | 0 |
| BTTS | 10 duels van 12 (tweede ronde, §1a stap 2) | 20 | 1 | 0 |
| **totaal** | | **173** | **10** | **3** |

De controle van §1a is **op de inkoop** gehaald en zo ruim als ze kan: alle acht spelende competities hebben een sportkey en kregen de volledige bulk, dus elke competitie had zowel een uitkomst- als een doelpuntenmarkt. De tien "alle poorten open"-selecties liggen op **drie** wedstrijden; de 0-of-1-bet-regel laat er per duel één door, en de overige zeven staan als `binnen_wedstrijd_niet_gekozen` in `data/run-state/`. Twee markten in de lijst (1X2 en Over/Under) na een 1 november met drie markten.

### "Net niet" — de afgewezen kandidaten met het cijfer per poort

Eén regel per wedstrijd, de sterkste afgewezen selectie, met **alle drie** de getallen zodat zichtbaar is of het één poort was of een breed tekort (§5).

| Wedstrijd | Selectie | Koers | xG-model | 2e methode | zwakste stand | valt af op |
|---|---|---|---|---|---|---|
| Gil Vicente – Vitória de Guimarães | 1X2 — Gil Vicente wint | 2,96 | +9,40 | +38,64 | +8,79 | **context** (poort 7) |
| Sassuolo – Fiorentina | Over/Under — Under 3.5 | 1,64 | +9,08 | +1,50 | +9,08 | **edge** |
| Sønderjyske – FC København | Over/Under — Under 3 | 2,06 | +6,05 | +8,17 | +5,62 | **edge** |
| Lorient – Brest | Over/Under — Over 2.5 | 2,20 | −1,08 | +23,01 | −1,08 | **tweede_methode** (poort 5) |
| Benfica – Alverca | BTTS — beide ploegen scoren, ja | 2,0584 | +4,27 | −0,11 | +4,01 | **tweede_methode** (poort 5) |
| Gençlerbirliği – Alanyaspor | Over/Under — Over 2.5 | 2,12 | +2,09 | +7,53 | +2,09 | **edge** |
| Newcastle United – Everton | — | — | — | — | — | geen kandidaat boven de `NEAR`-ondergrens van 3,0 pp |
| Raków Częstochowa – Pogoń Szczecin | — | — | — | — | — | geen kandidaat boven de `NEAR`-ondergrens van 3,0 pp |
| Deportivo A Coruña – Osasuna | Asian Handicap — Osasuna +0.25 | 2,0388 | +4,09 | +8,32 | +1,65 | **underdog** (poort 8) |

**Twee duels hebben géén "Net niet"-regel** en dat is iets anders dan "niets gevonden": bij Newcastle – Everton en Raków – Pogoń bleef élke kandidaat onder de `NEAR`-ondergrens van 3,0 pp, waaronder de routine een afgewezen kandidaat niet eens de moeite van het schaduwlogboek waard vindt. Bij Newcastle liggen mijn kansen en die van Pinnacle ook dicht bij elkaar (gemiddeld 2,2 pp verschil over de drie uitkomsten).

### Wat de poorten 7, 8 en 9 vandaag tegenhielden

| Poort | Selecties | Waar |
|---|---|---|
| 7 — context | **3** | alle drie Gil Vicente – Vitória de Guimarães: *rust, Gil Vicente had 4 dagen tegen 10 bij Vitória de Guimarães*. Dat was op de ruwe schaal de derde regel van de dag (DNB Gil Vicente, +12,43 pp, score 7,638). |
| 8 — underdog | **10** | Atalanta – Parma (3× een handicap op Parma, marktkans 16,1%), Deportivo A Coruña – Osasuna (5×, 26,9%), Sønderjyske – FC København (2×, 15,3%). Alle drie onder de ondergrens van 0,35. |
| 9 — doelpunten onder | **0** | geen FULL-Under in de band 8,0–10,0 pp. |

De grootste door poort 8 tegengehouden kandidaat is **Sønderjyske +1.25 @1,93 (+13,83 pp)**, en die stond op de ruwe schaal tweede van de dag met score 9,207. `sides.check` is met `today=DAY` aangeroepen, zodat het venster van 25 t/m 30 september uit `sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in plaats van geraden (§1e).

### De ruwe lijst (§5a) — een meting, geen tip

| # | Wedstrijd | Selectie | Koers | Ruwe kans | Ruwe edge | Score | Status |
|---|---|---|---|---|---|---|---|
| 1 | Atalanta – Parma | Under 3.5 | 1,55 | 79,5% | +14,98 | 11,909 | ook herijkt een bet |
| 2 | Sønderjyske – FC København | AH SonderjyskE +1.25 | 1,93 | 65,8% | +13,99 | 9,207 | underdog-kant onder de ondergrens (poort 8) |
| 3 | Gil Vicente – Vitória de Guimarães | DNB — Gil Vicente | 2,04 | 61,5% | +12,43 | 7,638 | context spreekt de bet tegen (poort 7) |

**Nul selecties sneuvelden alleen op de herijking** (`alleen_herijking` = 0), en dat is bij een fit van `a=0,994 / b=−0,004` te verwachten: die verandert een kans in de speelbare band met minder dan twee tienden van een procentpunt. De reeks `herijking` groeit vandaag dus niet en staat op 59 afgewikkelde gevallen (−3,3%).

## Wat anderen voorspellen (Stage 5 stap 2)

Geschreven voorspellingen zijn grotendeels niet te halen (§3 Stage 5, gemeten 20 sep: Forebet 403, Pinnacle-artikelen 404, Matchbook 530, voetbalwedden.net zonder de duels van de dag). Wat stap 2 in de praktijk invult is **de prijs van Pinnacle apart**, de-vigd, naast de eigen kans — en **los van** de beste prijs waarop gespeeld wordt.

| Wedstrijd | Pinnacle-marge | Pinnacle 1/X/2 | eigen xG 1/X/2 | verschil (pp) |
|---|---|---|---|---|
| Newcastle United – Everton | 3,3% | 0,419 / 0,270 / 0,311 | 0,452 / 0,256 / 0,293 | +3,25 / −1,40 / −1,86 |
| Sassuolo – Fiorentina | 3,1% | 0,334 / 0,255 / 0,411 | 0,325 / 0,266 / 0,410 | −0,99 / +1,10 / −0,11 |
| Atalanta – Parma | 3,4% | 0,636 / 0,207 / 0,157 | 0,558 / 0,259 / 0,184 | −7,87 / +5,18 / +2,69 |
| Deportivo A Coruña – Osasuna | 3,3% | 0,442 / 0,296 / 0,262 | 0,397 / 0,280 / 0,323 | −4,45 / −1,62 / +6,07 |
| Lorient – Brest | 3,0% | 0,387 / 0,295 / 0,318 | 0,355 / 0,286 / 0,358 | −3,13 / −0,89 / +4,03 |
| Gil Vicente – Vitória de Guimarães | 3,6% | 0,326 / 0,315 / 0,359 | 0,432 / 0,272 / 0,297 | **+10,59** / −4,37 / −6,21 |
| Gençlerbirliği – Alanyaspor | 3,5% | 0,355 / 0,288 / 0,356 | 0,338 / 0,273 / 0,389 | −1,75 / −1,51 / +3,25 |
| Sønderjyske – FC København | 4,2% | 0,148 / 0,190 / 0,662 | 0,204 / 0,234 / 0,562 | +5,60 / +4,35 / **−9,95** |
| Radomiak Radom – Śląsk Wrocław | 4,1% | 0,431 / 0,256 / 0,313 | 0,573 / 0,204 / 0,223 | **+14,26** / −5,25 / −9,01 |
| Zagłębie Lubin – Korona Kielce | 4,0% | 0,378 / 0,279 / 0,342 | 0,452 / 0,272 / 0,277 | +7,31 / −0,77 / −6,54 |
| Raków Częstochowa – Pogoń Szczecin | 4,0% | 0,416 / 0,249 / 0,335 | 0,423 / 0,235 / 0,342 | +0,70 / −1,39 / +0,69 |

Elf duels, gemiddelde absolute afstand tot het Pinnacle-oordeel **4,19 pp**, gemiddelde Pinnacle-marge 3,60%. Benfica – Alverca had geen Pinnacle-1X2.

**Twee dingen die hierbij horen en die de bets van vandaag tegenspreken.**

De eerste: bij **Radomiak Radom** zit het eigen model **14,26 pp** boven Pinnacle op de thuiszege. Dat is de grootste afwijking van de dag en het is precies de gepubliceerde bet. De tweede: op de **totalen** staat het eigen model bij **Atalanta – Parma** op P(Under 2.75) = 60,6% tegen 45,4% bij Pinnacle, een verschil van **+15,18 pp**. De bet staat op Under 3.5 en niet op 2,75, maar de richting is dezelfde en het is de scherpste bookmaker van de markt die hem tegenspreekt.

| Wedstrijd | lijn | Pinnacle under/over | P(Under) Pinnacle | P(Under) eigen | verschil |
|---|---|---|---|---|---|
| Atalanta – Parma | 2,75 | 2,14 / 1,78 | 0,454 | 0,606 | **+15,18 pp** |
| Radomiak Radom – Śląsk Wrocław | 3,00 | 1,92 / 1,93 | 0,501 | 0,390 | **−11,17 pp** |
| Sassuolo – Fiorentina | 3,00 | 1,99 / 1,90 | 0,488 | 0,590 | +10,18 pp |
| Sønderjyske – FC København | 3,00 | 2,06 / 1,82 | 0,469 | 0,546 | +7,68 pp |
| Gil Vicente – Vitória de Guimarães | 2,25 | 1,91 / 1,96 | 0,506 | 0,452 | −5,47 pp |
| Raków Częstochowa – Pogoń Szczecin | 3,00 | 1,90 / 1,95 | 0,506 | 0,456 | −5,09 pp |
| Benfica – Alverca | 3,50 | 1,85 / 1,85 | 0,500 | 0,461 | −3,91 pp |
| Deportivo A Coruña – Osasuna | 2,25 | 1,91 / 1,98 | 0,509 | 0,474 | −3,53 pp |
| Zagłębie Lubin – Korona Kielce | 2,50 | 1,92 / 1,93 | 0,501 | 0,522 | +2,12 pp |
| Gençlerbirliği – Alanyaspor | 2,50 | 1,85 / 2,03 | 0,523 | 0,507 | −1,58 pp |
| Newcastle United – Everton | 2,75 | 1,96 / 1,93 | 0,496 | 0,507 | +1,08 pp |
| Lorient – Brest | 2,50 | 1,78 / 2,15 | 0,547 | 0,556 | +0,91 pp |

Gemiddeld verschil op de Under-kant **+0,53 pp**, zes van twaalf boven Pinnacle. Dat is over de hele run dicht bij nul; de afwijking zit op twee duels en niet in het model. **De harde grens van §2 blijft onverkort:** niets hiervan gaat in `my_prob` of in `prob_sources`.

## Niveau per competitie (Stage 5)

`league_level` koos voor **zeven van de acht** competities de route `vorig+uplift` en voor de **Danish Superliga** de route `lopend`: die staat op 13 van 22 speeldagen en is daarmee over de helft, dus het niveau komt uit het lopende seizoen zelf en ongeschaald (`SEASON_MATURE_SHARE`).

| Competitie | route | thuis | uit | basis |
|---|---|---|---|---|
| Premier League (ENG) | `vorig+uplift` | 1,674 | 1,342 | 1,419 |
| Serie A (ITA) | `vorig+uplift` | 1,400 | 1,262 | 1,420 |
| La Liga (ESP) | `vorig+uplift` | 1,726 | 1,230 | 1,404 |
| Ligue 1 (FRA) | `vorig+uplift` | 1,735 | 1,359 | 1,531 |
| Primeira Liga (POR) | `vorig+uplift` | 1,642 | 1,301 | 1,323 |
| Super Lig (TUR) | `vorig+uplift` | 1,585 | 1,326 | 1,404 |
| Ekstraklasa (POL) | `vorig+uplift` | 1,728 | 1,273 | 1,556 |
| Danish Superliga (DEN) | **`lopend`** | 1,688 | 1,390 | 1,550 |

De gepoolde vroeg-seizoenscorrectie is gemeten over **72 speeldagen in zeven competities** en staat op factor **1,0970** (gepoold 1,1078). **De Danish Superliga is bij die pool overgeslagen** en dat staat met zoveel woorden in `vroeg_seizoen.overgeslagen`: *"halverwege het seizoen (13 van 22 speeldagen) — niveau komt uit het lopende seizoen, niet uit de gepoolde correctie"*. Een stil weggelaten waarneming is hetzelfde probleem als een stille truncatie in Stage 4 (§3 Stage 5).

## Promovendi

**Twee** van de twaalf duels hebben een omgerekende ploeg, en beide gaan langs `promotion.TIER1/TIER2` in plaats van rechtstreeks door de stand van vorig seizoen (§4):

| Duel | Omgerekende ploeg | Uit | Resultaat |
|---|---|---|---|
| Deportivo A Coruña – Osasuna | Deportivo A Coruña | Segunda División (ESP) | `LIGHT`, binnen het gemeten bereik |
| Radomiak Radom – Śląsk Wrocław | Śląsk Wrocław | Poolse I liga | `LIGHT`, binnen het gemeten bereik |

Daar geldt de lat van **16,0 pp**, en één van de twee haalt hem: Radomiak Radom met +18,22 pp. Dat is de eerste `LIGHT`-bet van Run A sinds 26 oktober. Sinds de reparatie van 31 oktober (`promotion.match_tier`, "de zwakste kant wint") kan de tier van een duel niet meer stil door de andere kant worden overschreven.

## Afwikkeling vorige picks (Stage 0)

Tien picks stonden open en acht waren afwikkelbaar; `settling.DayIndex` besliste dat op de **status van de bron** en niet op de klok (§0). Alle acht stonden op `reason = "Full-Time"`, dus er was geen verlenging of strafschoppenreeks om tot 90' terug te rekenen.

| Pick | Markt | Koers | Uitslag | Verwacht totaal | Resultaat |
|---|---|---|---|---|---|
| Juventus – Napoli | BTTS — nee | 2,156 | 2–0 | 2,02 | **gewonnen** |
| Lyon – Angers | Under 3.5 | 1,600 | 2–0 | 2,83 | **gewonnen** |
| Liverpool – Arsenal | DNB — Arsenal | 1,813 | 0–1 | 2,39 | **gewonnen** |
| Hannover 96 – Dynamo Dresden | 1X2 — Hannover wint | 2,215 | 2–1 | 3,32 | **gewonnen** |
| Kasımpaşa – Beşiktaş | BTTS — nee | 2,490 | 2–2 | 2,45 | verloren |
| Getafe – Sevilla | BTTS — nee | 1,784 | 3–1 | 1,75 | verloren |
| Atlanta United – Toronto FC | Under 3.5 | 1,830 | 3–1 | 2,78 | verloren |
| Panetolikos – OFI Crete | Over 2.25 | 1,880 | 0–1 | 2,73 | verloren |

**Vier gewonnen, vier verloren.** Twee bleven open omdat de bron ze als nog niet afgelopen meldde (Los Angeles FC – Minnesota United en Portland Timbers – Houston Dynamo, beide een half uur onderweg bij de eerste aanroep); die horen bij de Stage 0 van morgen. Dat is precies waarvoor de statusregel van §0 is gemaakt: een klok van twee uur na de aftrap had ze als afgelopen geboekt.

**Reflectie (§3 Stage 0, 12 okt) — vier vragen.**

1. **Klopte de redenering, of alleen de uitkomst?** Juventus – Napoli is de wedstrijd die liep zoals hij was voorgerekend: 2–0 bij een verwacht totaal van 2,02. Lyon – Angers (2–0 tegen 2,83) en Liverpool – Arsenal (0–1 tegen 2,39) zijn gewonnen **en** ongeveer goed ingeschat. Hannover 96 – Dynamo Dresden is gewonnen op een wedstrijd met één doelpunt minder dan voorgerekend. Aan de verliezende kant is het omgekeerde waar: Getafe – Sevilla werd 3–1 bij een verwacht totaal van **1,75** — dat is 2,25 doelpunt meer dan voorspeld en de bet (geen BTTS) was dan ook nergens — en Kasımpaşa – Beşiktaş werd 2–2 tegen 2,45 verwacht.
2. **Deed de poort die hem tegenhield zijn werk?** `doelpunten_onder` leverde zes rijen, waarvan **vijf verloren**. `underdog` leverde er zeventien: acht gewonnen, negen verloren — geen richting. `edge` leverde vijftien rijen (zes gewonnen, negen verloren), `tweede_methode` zes (vier gewonnen, twee verloren), `context` vijf (twee gewonnen, twee verloren, één void) en `robuustheid` drie (één gewonnen, twee verloren). `lijstlengte` kreeg één rij en die verloor.
3. **Zat er een patroon in de dag?** Ja, één: bij **vier van de acht** afgewikkelde picks vielen er méér doelpunten dan voorgerekend, en de twee duurste verliezen kwamen daar vandaan — beide waren een "beide ploegen scoren, nee" in een wedstrijd die op vier doelpunten uitkwam. Dat wijst dezelfde kant op als de reeks in §6g over de Under-kant.
4. **Wat betekent dit niet?** Met acht gevallen is dat patroon niets meer dan passen. §6d eist ~30 gevallen voordat een reeks gelezen mag worden, en de reeks die daar wél aan komt (`doelpunten_onder`, 35 gevallen) is hierboven apart behandeld. **Er is vandaag geen drempel, geen gewicht en geen poort verzet op grond van gisteren.**

Daarnaast zijn **53 schaduwrijen** afgewikkeld: 22 gewonnen, 30 verloren, 1 void. Eén schaduwrij bleef open (Tenerife – FC Andorra, bron meldt nog niet afgelopen).

