## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
| Premier League (ENG) | GEANALYSEERD | 5 duels (4× `FULL`, 1× `NONE`), 2 gepubliceerde regel(s) |
| Serie A (ITA) | GEANALYSEERD | 5 duels (3× `FULL`, 2× `LIGHT`), 1 gepubliceerde regel(s) |
| La Liga (ESP) | GEANALYSEERD | 4 duels (4× `FULL`), 1 gepubliceerde regel(s) |
| Bundesliga (GER) | GEANALYSEERD | 2 duels (2× `FULL`), 0 gepubliceerde regel(s) |
| Ligue 1 (FRA) | GEANALYSEERD | 6 duels (4× `FULL`, 2× `LIGHT`), 0 gepubliceerde regel(s) |
| Championship (ENG) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Eredivisie (NED) | GEANALYSEERD | 5 duels (5× `FULL`), 1 gepubliceerde regel(s) |
| Primeira Liga (POR) | GEANALYSEERD | 4 duels (3× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| Belgian Pro League (BEL) | GEANALYSEERD | 4 duels (4× `FULL`), 0 gepubliceerde regel(s) |
| Super Lig (TUR) | GEANALYSEERD | 2 duels (1× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| Scottish Premiership (SCO) | GEANALYSEERD | 2 duels (2× `FULL`), 0 gepubliceerde regel(s) |
| Danish Superliga (DEN) | GEANALYSEERD | 4 duels (2× `FULL`, 1× `LIGHT`, 1× `NONE`), 0 gepubliceerde regel(s) |
| Ekstraklasa (POL) | GEANALYSEERD | 3 duels (2× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| UEFA Champions League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Europa League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Conference League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| FA Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 06.11. 20:45 (UK-tijd), buiten het venster; 40 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| League Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 20:45 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| Coppa Italia (ITA) | GEEN WEDSTRIJD | eerstvolgende ronde 01.12. 21:00 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| KNVB Beker (NED) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:45 (UK-tijd), buiten het venster; 26 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| DFB Pokal (GER) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:00 (UK-tijd), buiten het venster; 16 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 55 (zondag, vr-zo). 46 duels in het venster en 44 ervan doorgerekend. De marge op de cap is dus NEGEN duels, ruimer dan gisteren (vier) maar krapper dan de weken ervoor. 36 duels zijn `FULL`; 10 hebben een ploeg die niet in de stand van 2025/2026 staat en zijn via `scripts/promotion.py` omgerekend, waarvan 8 op `LIGHT` uitkomen. TWEE duels komen op `NONE` uit: Hull City – Brentford en AC Horsens – Sønderjyske, beide omdat een ploeg buiten `conversion_in_range` valt — de Coventry-val, en de juiste uitkomst, want buiten het gemeten bereik is doorrekenen raden. Geen enkel duel is kruis-grens, dus `scripts/interleague.py` komt deze run niet aan de orde. Datarijkdom liep van 4.50 (Genk – Standard Liège en Union St.Gilloise – Cercle Brugge) tot 8.00 (Barcelona – Real Madrid en Manchester United – AFC Bournemouth); er viel niets af door de cap, dus er is geen 'laagste die het haalde' en geen 'hoogste die afviel'. De context is voor alle 46 duels opgehaald zoals §1c eist, met nul fouten.

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Bet | Koers | Kans | Edge | Score | Tier | Risico | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Sunderland – Leeds United — Over/Under: Over 2.5 | 2.2544 | 57.6% | +13.19 pp | 7.591 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 2 | Real Sociedad – Levante — Over/Under: Over 2.5 | 1.6400 | 70.3% | +9.37 pp | 6.591 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 3 | NEC Nijmegen – FC Groningen — Over/Under: Over 3.5 | 2.1500 | 57.7% | +11.14 pp | 6.423 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 4 | Manchester United – AFC Bournemouth — Over/Under: Over 2.5 | 1.7100 | 67.9% | +9.45 pp | 6.419 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 5 | Lecce – Juventus — BTTS: Beide ploegen scoren — nee | 1.8918 | 62.4% | +9.53 pp | 5.946 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |

**Vijf regels, en voor het eerst in weken halen ze ALLE VIJF hun eigen lat.** `MAX_SHORTLIST` = 5 (zondag) en er zijn ZES duels met een publiceerbare selectie — zes duels waarbij alle acht de andere poorten openstonden en de edge boven de NEAR-ondergrens bleef. Er passen vijf regels in, dus er valt er precies één af. Alle vijf gepubliceerde regels staan op `FULL` en halen de lat van 8,0 pp: Sunderland – Leeds United Over 2.5 (+13,19 pp, ruw +13,72), Real Sociedad – Levante Over 2.5 (+9,37 pp, ruw +10,09), NEC Nijmegen – FC Groningen Over 3.5 (+11,14 pp, ruw +11,68), Manchester United – AFC Bournemouth Over 2.5 (+9,45 pp, ruw +10,15) en Lecce – Juventus BTTS 'nee' (+9,53 pp). Bij alle vijf staat `bet_beide` op TRUE. Dat is het tegenovergestelde van gisteren, toen drie van de vijf hun lat haalden en twee `LIGHT`-regels op rangorde werden gepubliceerd. **`MAX_LIGHT_IN_SHORTLIST` = 2 bindt NIET en kan niets uitsluiten:** er staat geen enkele `LIGHT`-regel in de lijst, want de enige `LIGHT`-kandidaat van de dag viel af op lijstlengte. **En die ene afvaller is het spiegelbeeld van de uitkomst van gisteren:** Śląsk Wrocław – Wieczysta Kraków, Over 3.5 @2.4308, +17,12 pp op `LIGHT` — ruim boven zijn eigen lat van 16,0 pp — staat op rang 6 en haalt de lijst niet. Gisteren vielen juist twee `LIGHT`-regels ONDER hun lat de lijst in terwijl een `FULL` boven zijn lat eraf viel. Beide uitkomsten volgen uit §5b plus `selection_score`: er staan zes selecties boven hun eigen lat en er passen er vijf, dus de drempel bindt hier WEL als grens, maar hij snijdt alle zes door en dan beslist de rangorde alsnog — en in `selection_score` verslaat +9,53 pp op `FULL` (5,946) een +17,12 pp op `LIGHT` × 0,5 (4,987). Lees de lijst dus als 'het beste van vandaag' en niet als een gevonden voordeel: §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de hóógste geclaimde edge. Zie bevinding 2.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Bet | Koers | Kans | Ruwe edge | Score | Viel af op |
|---|---|---|---|---|---|---|
| 1 | Sparta Rotterdam – Ajax — Asian Handicap: Sparta Rotterdam +1.5 | 1.7500 | 69.6% | +12.42 pp | 8.639 | underdog-kant onder de ondergrens (poort 8) |
| 2 | Sunderland – Leeds United — Over/Under: Over 2.5 | 2.2544 | 58.1% | +13.72 pp | 7.969 | BET |
| 3 | Real Sociedad – Levante — Over/Under: Over 2.5 | 1.6400 | 71.1% | +10.09 pp | 7.171 | BET |
| 4 | Manchester United – AFC Bournemouth — Over/Under: Over 2.5 | 1.7100 | 68.6% | +10.15 pp | 6.966 | BET |
| 5 | NEC Nijmegen – FC Groningen — Over/Under: Over 3.5 | 2.1500 | 58.2% | +11.68 pp | 6.797 | BET |

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 12 van 12 — 11 op de beste prijs uit de bulk-`h2h`, en de Scottish Premiership (2 duels) op het gratis BetExplorer-MARKTGEMIDDELDE, want die competitie heeft geen sportkey bij The Odds API; daar is de bookmaker niet herleidbaar en valt de edge systematisch te laag uit (§1a) | 127 | 0 |
| Asian Handicap | 11 van 12 (bulk `spreads`; geen spreads voor de Scottish Premiership) | 175 | 0 |
| Draw No Bet | 11 van 12 (de 0.0-lijn uit diezelfde `spreads`, gratis) | 42 | 0 |
| Double Chance | 11 van 12 (de ±0.5-lijn uit diezelfde `spreads`, gratis) | 24 | 0 |
| Over/Under | 11 van 12 (bulk `totals`; geen totals voor de Scottish Premiership) | 208 | 4 |
| BTTS | 30 van de 32 duels met een kandidaat-edge (1 credit per duel). De twee die afvielen zijn Hibernian – Celtic en Motherwell – Heart of Midlothian: geen sportkey, dus geen event-id om de markt op op te vragen. De 12 duels zonder kandidaat-edge staan als 'niet opgevraagd — geen kandidaat-edge in dit duel' in `markets_checked` en niet als gat | 60 | 1 |
| **totaal** | | **636** | **5** |

### Net niet

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
| Crystal Palace – Newcastle United | 1X2 — 1 (Crystal Palace wint) @ 3.0090 | +11.25 pp | -0.35 pp | +10.76 pp | tweede methode |
| Atalanta – Frosinone | Over/Under — Under 3.5 @ 1.8820 | +5.57 pp | +19.68 pp | +5.57 pp | edge |
| Athletic Club – Getafe | Over/Under — Under 2.25 @ 1.8300 | +6.08 pp | +13.75 pp | -0.90 pp | robuustheid |
| Celta Vigo – Real Betis | Asian Handicap — Celta Vigo +0.25 @ 1.9800 | +13.71 pp | -0.34 pp | +13.42 pp | tweede methode |
| Barcelona – Real Madrid | BTTS — Beide ploegen scoren — nee @ 4.2340 | +2.54 pp | +24.76 pp | +2.25 pp | edge |
| Hoffenheim – Bayer Leverkusen | Over/Under — Under 3.5 @ 2.0200 | +6.38 pp | -1.32 pp | +4.98 pp | tweede methode |
| Freiburg – Bayern München | Over/Under — Under 4 @ 1.8800 | +9.45 pp | -5.60 pp | +7.67 pp | tweede methode |
| Monaco – Lille | 1X2 — 2 (Lille wint) @ 4.1360 | +9.65 pp | +22.50 pp | +8.38 pp | context |
| Rennes – Strasbourg | Over/Under — Over 3.5 @ 2.2000 | +6.67 pp | +0.86 pp | +2.58 pp | edge |
| Fortuna Sittard – Excelsior | Asian Handicap — Excelsior +0.25 @ 1.8134 | +5.61 pp | -2.42 pp | +1.26 pp | tweede methode |
| PSV Eindhoven – Feyenoord | Asian Handicap — Feyenoord +0.25 @ 2.0500 | +5.07 pp | -0.25 pp | +1.96 pp | tweede methode |
| Sparta Rotterdam – Ajax | BTTS — Beide ploegen scoren — ja @ 1.5586 | +8.55 pp | -4.95 pp | +7.75 pp | tweede methode |
| AZ Alkmaar – FC Twente | Over/Under — Under 3.25 @ 1.9900 | +12.72 pp | -14.51 pp | +6.72 pp | tweede methode |
| Estoril – Moreirense | Over/Under — Over 2.5 @ 1.9604 | +2.97 pp | +16.86 pp | +2.97 pp | edge |
| Nacional – Braga | BTTS — Beide ploegen scoren — ja @ 1.9702 | +7.60 pp | +7.88 pp | +7.09 pp | edge |
| Sporting CP – Académico Viseu | Over/Under — Over 3.5 @ 2.1300 | +8.14 pp | +40.14 pp | +0.99 pp | edge |
| Genk – Standard Liège | Over/Under — Under 3 @ 1.9400 | +3.40 pp | +18.50 pp | +3.40 pp | edge |
| Union St.Gilloise – Cercle Brugge | Over/Under — Under 3.5 @ 1.7200 | +4.90 pp | +23.58 pp | +4.90 pp | edge |
| Göztepe – Çorum FK | 1X2 — 1 (Goztepe wint) @ 2.2348 | +9.53 pp | +19.39 pp | +6.19 pp | edge |
| FC Midtjylland – Lyngby | Over/Under — Over 3.5 @ 2.2500 | -1.88 pp | +42.29 pp | -3.79 pp | tweede methode |
| Silkeborg – Nordsjælland | Over/Under — Under 3.25 @ 2.0300 | +0.27 pp | +18.02 pp | +0.27 pp | edge |
| AGF – Viborg | Over/Under — Under 3 @ 1.8800 | +3.40 pp | +14.20 pp | +2.33 pp | edge |
| Legia Warszawa – Lech Poznań | BTTS — Beide ploegen scoren — nee @ 2.3916 | +3.50 pp | +22.25 pp | +0.81 pp | edge |

23 regels over 46 duels, en de rest telt als volgt op. GEEN ENKEL duel heeft deze run een `near_miss_gepubliceerd`: bij de vijf duels van de topselectie was de sterkste kandidaat de bet zelf en bleef er geen tweede kandidaat boven de NEAR-ondergrens over. 22 duels hebben dus helemaal geen `near_miss`, en die splitsen in drie groepen: de VIJF gepubliceerde duels, de TWEE op `NONE` (Hull City – Brentford en AC Horsens – Sønderjyske, die niets doorgerekend hebben om af te wijzen) en VIJFTIEN waar de sterkste kandidaat onder de NEAR-ondergrens bleef (6,0 pp op `LIGHT`, 3,0 pp op `FULL`). De VEERTIEN poort-8-rijen en de DRIE poort-9-rijen staan niet in deze tabel maar als eigen categorie (`underdog`, `doelpunten_onder`) in het schaduwlogboek, en de ene `lijstlengte`-rij (Śląsk Wrocław – Wieczysta Kraków, Over 3.5) net zo — die drie categorieën zijn drie aparte populaties en mogen nooit bij `edge` worden opgeteld (§1e, §1h, §5b).

## Wedstrijden

De 46 duels in het inzetvenster, op aftraptijd. De vijf gepubliceerde regels staan in het volledige format van §5; bij de andere 41 staat de reden in één regel, met de cijfers per poort in de tabel "Net niet" hierboven.

### Fortuna Sittard – Excelsior · 12:15 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### Śląsk Wrocław – Wieczysta Kraków · 12:15 NL · Ekstraklasa (POL)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEKWALIFICEERD, NIET GEPUBLICEERD** — Over/Under — Over 3.5 @ 2.4308, edge +17.12 pp, selection_score 4.987, rang 6 op de dagranglijst. alle negen poorten open en +17.12 pp boven de drempel, maar rang 6 en niet in de lijst van 5 regels; laagste gepubliceerde selection_score 5.946
- **Doelverwachting:** xG-methode 2.074 / 1.922 · splitsmethode 2.562 / 2.056

### Inter – Fiorentina · 12:30 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Hibernian – Celtic · 13:00 NL · Scottish Premiership (SCO)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Genk – Standard Liège · 13:30 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel (+5.89 pp, nodig 8.0)

### Athletic Club – Getafe · 14:00 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge niet robuust over het (shrink, rho)-grid

### FC Midtjylland – Lyngby · 14:00 NL · Danish Superliga (DEN)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### Konyaspor – Gençlerbirliği · 14:00 NL · Super Lig (TUR)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Silkeborg – Nordsjælland · 14:00 NL · Danish Superliga (DEN)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel (+3.39 pp, nodig 8.0)

### NEC Nijmegen – FC Groningen · 14:30 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.5
- **Bet:** Over/Under — Over 3.5 — Odds: best **2.1500** (The Odds API (Unibet (NL)))
- **Implied prob:** 46.5%  •  **My prob:** 57.7%  (ruw 58.2%)
- **Edge:** +11.14 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 2.405 / 1.727 · splitsmethode 2.350 / 1.528
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 2.405 thuis / 1.727 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.350 / 1.528 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 3 van 5 over 46 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 6.423. Ruwe kans 0.5819, ruwe edge 11.68 pp; xG-methode 12.67 pp, splitsmethode 7.72 pp, zwakste stand van het (shrink, rho)-grid 8.96 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### PSV Eindhoven – Feyenoord · 14:30 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### Jagiellonia Białystok – Wisła Płock · 14:45 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Atalanta – Frosinone · 15:00 NL · Serie A (ITA)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel (+7.80 pp, nodig 16.0)

### Crystal Palace – Newcastle United · 15:00 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### Genoa – Venezia · 15:00 NL · Serie A (ITA)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Hull City – Brentford · 15:00 NL · Premier League (ENG)
- **Data:** `NONE`
- **GEEN BET** — omrekening buiten het gemeten bereik (conversion_in_range) — data_tier NONE

### Liverpool – Brighton & Hove Albion · 15:00 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Manchester United – AFC Bournemouth · 15:00 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 8.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.7100** (The Odds API (1xBet))
- **Implied prob:** 58.5%  •  **My prob:** 67.9%  (ruw 68.6%)
- **Edge:** +9.45 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.875 / 1.494 · splitsmethode 2.658 / 1.740 · Understat 2.045 / 1.345
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.875 thuis / 1.494 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.658 / 1.740 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 2.045 / 1.345, rollende xG over 8 duels {'home': [1.89, 1.51, 8], 'away': [1.85, 1.62, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 4 van 5 over 46 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 6.419. Ruwe kans 0.6863, ruwe edge 10.15 pp; xG-methode 6.94 pp, splitsmethode 22.99 pp, zwakste stand van het (shrink, rho)-grid 5.11 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Monaco – Lille · 15:00 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Lille mist 32% van de selectiewaarde tegen 8% bij Monaco — Osame Sahraoui (injury, terug Doubtful), Tiago Santos (injury, terug Late June 2027), Ayase Ueda (injury, terug A few weeks)

### Motherwell – Heart of Midlothian · 15:00 NL · Scottish Premiership (SCO)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Hoffenheim – Bayer Leverkusen · 15:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### AC Horsens – Sønderjyske · 16:00 NL · Danish Superliga (DEN)
- **Data:** `NONE`
- **GEEN BET** — omrekening buiten het gemeten bereik (conversion_in_range) — data_tier NONE

### Club Brugge – St.Truiden · 16:00 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Celta Vigo – Real Betis · 16:15 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### Estoril – Moreirense · 16:30 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 5.75
- **GEEN BET** — edge onder drempel (+5.24 pp, nodig 8.0)

### Sparta Rotterdam – Ajax · 16:45 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### Göztepe – Çorum FK · 17:00 NL · Super Lig (TUR)
- **Data:** `LIGHT` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel (+11.00 pp, nodig 16.0)

### Angers – Lorient · 17:15 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Auxerre – Le Mans · 17:15 NL · Ligue 1 (FRA)
- **Data:** `LIGHT` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel

### Marseille – Le Havre · 17:15 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Rennes – Strasbourg · 17:15 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel (+5.12 pp, nodig 8.0)

### Toulouse – Troyes · 17:15 NL · Ligue 1 (FRA)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Freiburg – Bayern München · 17:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — data conflicterend

### Legia Warszawa – Lech Poznań · 17:30 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel (+6.91 pp, nodig 8.0)

### Sunderland – Leeds United · 17:30 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 6.5
- **Bet:** Over/Under — Over 2.5 — Odds: best **2.2544** (The Odds API (Matchbook, beurs: 2.28 bruto / 2.2544 na 2% commissie))
- **Implied prob:** 44.4%  •  **My prob:** 57.6%  (ruw 58.1%)
- **Edge:** +13.19 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.476 / 1.611 · splitsmethode 1.754 / 1.000 · Understat 1.213 / 1.443
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.476 thuis / 1.611 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 1.754 / 1.000 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 1.213 / 1.443, rollende xG over 8 duels {'home': [1.55, 1.56, 8], 'away': [1.85, 1.38, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 1 van 5 over 46 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 7.591. Ruwe kans 0.5808, ruwe edge 13.72 pp; xG-methode 15.26 pp, splitsmethode 7.6 pp, zwakste stand van het (shrink, rho)-grid 14.94 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### AGF – Viborg · 18:00 NL · Danish Superliga (DEN)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel (+5.01 pp, nodig 8.0)

### Lecce – Juventus · 18:00 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.5
- **Bet:** BTTS — Beide ploegen scoren — nee — Odds: best **1.8918** (The Odds API (Matchbook, beurs: 1.91 bruto / 1.8918 na 2% commissie))
- **Implied prob:** 52.9%  •  **My prob:** 62.4%  (ruw 63.0%)
- **Edge:** +9.53 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 0.568 / 1.916 · splitsmethode 0.561 / 1.660 · Understat 0.674 / 2.171
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 0.568 thuis / 1.916 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 0.561 / 1.660 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 0.674 / 2.171, rollende xG over 8 duels {'home': [1.17, 1.85, 8], 'away': [1.87, 0.89, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 5 van 5 over 46 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 5.946. Ruwe kans 0.6301, ruwe edge 10.15 pp; xG-methode 9.72 pp, splitsmethode 11.86 pp, zwakste stand van het (shrink, rho)-grid 1.79 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Gent – Anderlecht · 18:30 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Real Sociedad – Levante · 18:30 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 7.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.6400** (The Odds API (1xBet))
- **Implied prob:** 61.0%  •  **My prob:** 70.3%  (ruw 71.1%)
- **Edge:** +9.37 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 2.200 / 1.374 · splitsmethode 2.374 / 1.777 · Understat 2.127 / 1.374
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 2.200 thuis / 1.374 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.374 / 1.777 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 2.127 / 1.374, rollende xG over 8 duels {'home': [1.44, 1.82, 8], 'away': [2.07, 1.1, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 2 van 5 over 46 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 6.591. Ruwe kans 0.7107, ruwe edge 10.09 pp; xG-methode 8.28 pp, splitsmethode 17.34 pp, zwakste stand van het (shrink, rho)-grid 4.97 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Nacional – Braga · 19:00 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel (+7.11 pp, nodig 8.0)

### Rio Ave – Famalicão · 19:00 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Union St.Gilloise – Cercle Brugge · 19:15 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel (+7.96 pp, nodig 8.0)

### AZ Alkmaar – FC Twente · 20:00 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### Udinese – Milan · 20:45 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Barcelona – Real Madrid · 21:00 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 8.0
- **GEEN BET** — edge onder drempel (+7.07 pp, nodig 8.0)

### Sporting CP – Académico Viseu · 21:30 NL · Primeira Liga (POR)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel (+13.95 pp, nodig 16.0)
