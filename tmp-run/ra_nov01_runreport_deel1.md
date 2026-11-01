# Run A — 2026-11-01

**Gestart:** 03:05 CET · **Bets gepubliceerd:** 5 · **Wedstrijden diep geanalyseerd:** 37 van 37 in het inzetvenster (1 op `data_tier = NONE`)

**Branch:** deze run is op `claude/stoic-davinci-dnxlwo` gestart en **naar `main` gepusht** (§6a); de scheduler-prompt geeft daar expliciet toestemming voor. Er is dus niets te mergen voor een volgende run.

**Dit rapport is voor de repo.** Het leesbare dagrapport staat op
[de HTML-pagina](https://claude.ai/artifact/PVvXeSfUmXxW4dy9THkpxy) en, als tweede route (§6c, 14 okt), in
[`runs/2026-11-01-run-a.dagrapport.md`](https://github.com/aistref/football/blob/main/runs/2026-11-01-run-a.dagrapport.md).

---

## Stage -2 — takken

`git rev-parse --is-shallow-repository` gaf **true**: de container kreeg de repo opnieuw als ondiepe kloon. Vóór het unshallowen leken **70 van de 82 takken** eigen commits te hebben (3 tot 604 stuks); ná `git fetch --unshallow origin` (668 commits lokaal) zijn dat **nul van de 82**. Dat is exact het valse alarm dat §3 Stage -2 beschrijft, en het is de reden dat die stap vóór alles komt.

De commitgraaf is echter niet het antwoord (§3 Stage -2, 27 sep). `scripts/branchaudit.py --ref HEAD` vergelijkt alle vijf de logboeken **per record op de inhoud**:

```
STAGE -2 — alle takken vergeleken met HEAD, per record op de inhoud
  82 tak(ken) nagelopen · ondiepe kloon: false

  data/picks.jsonl                   500 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/shadow.jsonl                 1590 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/context-log.jsonl            1874 op HEAD  (sleutel: id)  -> VOLLEDIG
  data/calibration.jsonl            6830 op HEAD  (sleutel: date.run.match.market.method)  -> VOLLEDIG
  data/source-health.json            146 op HEAD  (sleutel: bladpaden)  -> VOLLEDIG
       sources.oddspapi (+5 bladpad(en)) — bekend besluit, geen vondst
         OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het 20K-creditplan (commit f342894, README). Besluit, geen verlies.
  data/coverage.json                 324 op HEAD  (sleutel: bladpaden)  -> VOLLEDIG

Niets te verenigen: elk record dat op een tak staat, staat ook op HEAD.

LET OP wat dit NIET zegt. Dit is een uitspraak over de metingen, niet over de
commitgraaf — en dat is met opzet de enige uitspraak die telt (§3 Stage -2). Een
tak met 0 eigen commits kan metingen dragen die hier ontbreken, en in een ondiepe
kloon lijken tientallen takken eigen commits te hebben die er al in zitten.
```

`HEAD` was bij de start bit-voor-bit gelijk aan `origin/main` (0 commits voor, 0 achter). Er viel niets te verenigen. **Wat er wél openstond zijn picks en niet takken:** `picks.jsonl` had tien openstaande picks van 31 oktober en `shadow.jsonl` vijfenzeventig schaduwrijen; die horen bij Stage 0 en staan daar.

Eén bekend verschil blijft staan en is géén vondst: `sources.oddspapi` staat op vijf oude takken en niet op `HEAD`. OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het 20K-creditplan (commit `f342894`). Besluit, geen verlies — `branchaudit.py` merkt dat zelf aan.

## Stage -1 — hervatting

Geen voortgangsbestand voor 1 november bij de start, dus dit is een verse run. `resumed_count` = 0 en `sessies` bevat één id — géén hervatting, en dat is sinds 16 oktober een afgeleid getal in plaats van een teller (§3 Stage -1).

## Dekkingsrapportage

| Competitie | Status | n | bets | datalabels / eerstvolgende ronde |
|---|---|---|---|---|
| Serie A (ITA) | `GEANALYSEERD` | 5 | 1 | 3 FULL, 2 LIGHT |
| La Liga (ESP) | `GEANALYSEERD` | 4 | 1 | 3 FULL, 1 LIGHT |
| Ligue 1 (FRA) | `GEANALYSEERD` | 4 | 1 | 4 FULL |
| Super Lig (TUR) | `GEANALYSEERD` | 4 | 1 | 3 FULL, 1 LIGHT |
| Belgian Pro League (BEL) | `GEANALYSEERD` | 4 | 0 | 3 FULL, 1 LIGHT |
| Danish Superliga (DEN) | `GEANALYSEERD` | 4 | 0 | 3 FULL, 1 NONE |
| Eredivisie (NED) | `GEANALYSEERD` | 4 | 0 | 3 FULL, 1 LIGHT |
| Primeira Liga (POR) | `GEANALYSEERD` | 4 | 0 | 2 FULL, 2 LIGHT |
| Bundesliga (GER) | `GEANALYSEERD` | 2 | 0 | 2 FULL |
| Premier League (ENG) | `GEANALYSEERD` | 1 | 1 | 1 FULL |
| Scottish Premiership (SCO) | `GEANALYSEERD` | 1 | 0 | 1 FULL |
| Championship (ENG) | `GEEN WEDSTRIJD` | 0 | 0 | — |
| Coppa Italia (ITA) | `GEEN WEDSTRIJD` | 0 | 0 | 01.12. 21:00 |
| DFB Pokal (GER) | `GEEN WEDSTRIJD` | 0 | 0 | — |
| Ekstraklasa (POL) | `GEEN WEDSTRIJD` | 0 | 0 | — |
| FA Cup (ENG) | `GEEN WEDSTRIJD` | 0 | 0 | 06.11. 20:30 |
| KNVB Beker (NED) | `GEEN WEDSTRIJD` | 0 | 0 | 01.12. 17:00 |
| League Cup (ENG) | `GEEN WEDSTRIJD` | 0 | 0 | 15.12. 20:45 |
| UEFA Champions League | `GEEN WEDSTRIJD` | 0 | 0 | — |
| UEFA Conference League | `GEEN WEDSTRIJD` | 0 | 0 | — |
| UEFA Europa League | `GEEN WEDSTRIJD` | 0 | 0 | — |

**Niets afgekapt.** 37 duels tegen een zondagcap van 55 (`MAX_DEEP_ANALYSES`). De datarijkdom-score liep van **4,75** (laagste in de run) tot **8,5** (hoogste); §3 Stage 4 eist die twee getallen zodra de cap knelt, en ze staan er ook als hij dat niet doet — anders is achteraf niet na te gaan of de afkapping ergens op sloeg.

Alle 37 duels stonden op de daglijst van de rundag zelf; geen enkel duel komt van de lijst van 2 november en geen enkel duel was bij het eerste verzoek al afgetrapt (`RunMatch.playable = True` voor alle 37).

## Bronstatus deze run

Uitvoer van `python3 scripts/api_check.py`, letterlijk:

```
Controle van de databronnen die een sleutel nodig hebben.

=== The Odds API (odds per bookmaker) ===
  OK — 47 actieve voetbalcompetities beschikbaar.
  Quota: 20000 over, 0 gebruikt deze maand.
  Sportkeys van de repo: 32 van 34 actief vandaag.
    NIET ACTIEF  Coppa Italia (ITA)             soccer_italy_coppa_italia
    NIET ACTIEF  DFB Pokal (GER)                soccer_germany_dfb_pokal
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

  Er is geen statistieken-API. Dat is sinds 27 sep 2026 de bewuste opzet en geen
  gat: de onafhankelijke kansinput komt van Fotmob (alle competities) en Understat
  (vijf). Zolang die twee leveren, is §2 gedekt en is er niets te doen.
  WEL melden, vooraan in de notificatie: als Fotmob niet meer levert. Dan is er voor
  vrijwel elke wedstrijd geen kansbron meer, wordt alles data_tier = NONE en levert
  elke run gegarandeerd nul bets. Pas dán is een betaald plan een reële vraag.
```

Wat daaruit volgt voor deze run:

- **The Odds API: 20000 credits over, 0 verbruikt.** De maandwissel heeft het quotum gereset. November heeft 30 dagen, dus `suggest_cap` zet het dagplafond op **333**. Gebruikt: **33** voor de bulk (h2h + spreads + totals, 3 per competitie × 11) plus **23** voor de BTTS-ronde = **56 van 20000**.
- **`API_FOOTBALL_KEY` ontbreekt.** Dat is een besluit van de gebruiker van 27 september 2026 en geen gat, geen actiepunt en geen notificatieonderwerp (§3). De kanskant komt van Fotmob (alle elf competities) en Understat (vijf, vandaag alle vijf spelend). Fotmob leverde voor alle 37 duels, dus de uitzondering van §3 punt 3 is niet aan de orde.
- **Geen sleutel is afgewezen** en geen bron gaf een fout. `store["errors"]` is over de hele run leeg gebleven.
- Twee bekende sportkeys staan vandaag op NIET ACTIEF (Coppa Italia, DFB Pokal) en dat klopt met BetExplorer. Vier actieve sportkeys kent de repo niet: `soccer_brazil_serie_b`, `soccer_germany_liga3`, `soccer_sweden_superettan` en `soccer_uefa_nations_league`. Geen van de vier staat op de runlijst van Run A — de eerste drie zijn Run B-gebied, de Nations League is Run C.

### Bevestiging door een tweede methode (§1)

De bevestigingspoort is op de **runlijst zelf** gedraaid en niet alleen op de analyse: de Fotmob-daglijst naast de BetExplorer-fixturepagina per competitie, twee losse bronnen.

| Competitie | Fotmob | BetExplorer | eens |
|---|---|---|---|
| Belgian Pro League (BEL) | 4 | 4 | ja |
| Bundesliga (GER) | 2 | 2 | ja |
| Championship (ENG) | 0 | 0 | ja |
| Danish Superliga (DEN) | 4 | 4 | ja |
| Ekstraklasa (POL) | 0 | 0 | ja |
| Eredivisie (NED) | 4 | 4 | ja |
| La Liga (ESP) | 4 | 4 | ja |
| Ligue 1 (FRA) | 4 | 4 | ja |
| Premier League (ENG) | 1 | 1 | ja |
| Primeira Liga (POR) | 4 | 4 | ja |
| Scottish Premiership (SCO) | 1 | 1 | ja |
| Serie A (ITA) | 5 | 5 | ja |
| Super Lig (TUR) | 4 | 4 | ja |
| UEFA Champions League | 0 | 0 | ja |
| UEFA Conference League | 0 | 0 | ja |
| UEFA Europa League | 0 | 0 | ja |
| **totaal** | **37** | **37** | **16 van 16** |

**Eens over alles.** Dat is de eerste run in weken zonder enig verschil tussen de twee bronnen; op 31 oktober stond er nog één duel verschil (Cambuur – Go Ahead Eagles).

De vijf bekers zijn apart langs twee bronnen gegaan, want ze hebben geen `fotmob_id` in `coverage.json`:

| Beker | Fotmob-daglijst | BetExplorer |
|---|---|---|
| League Cup (ENG) | id 133: 0 duels | 4 teamparen, eerstvolgende ronde 15.12. 20:45 |
| DFB Pokal (GER) | id 209: 0 duels | 0 teamparen, eerstvolgende ronde **geen** |
| KNVB Beker (NED) | id 235: 0 duels | 16 teamparen, eerstvolgende ronde 01.12. 17:00 |
| FA Cup (ENG) | geen id | 40 teamparen, eerstvolgende ronde 06.11. 20:30 |
| Coppa Italia (ITA) | geen id | 8 teamparen, eerstvolgende ronde 01.12. 21:00 |

**De DFB Pokal-fixturepagina van BetExplorer is vandaag leeg** (0 teamparen op een respons van 200). Daar is Fotmob dus de enige bron die iets zegt, en dat is genoteerd als *niet bevestigd* en niet als bevestiging. Dat onderscheid is precies wat 6 oktober 2026 vijf FA Cup-duels kostte, met de rollen omgedraaid.

