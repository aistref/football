## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
| Premier League (ENG) | GEANALYSEERD | 1 duels (1× `LIGHT`), 1 gepubliceerde regel(s) |
| Serie A (ITA) | GEANALYSEERD | 1 duels (1× `LIGHT`), 0 gepubliceerde regel(s) |
| La Liga (ESP) | GEANALYSEERD | 1 duels (1× `LIGHT`), 1 gepubliceerde regel(s) |
| Bundesliga (GER) | GEANALYSEERD | 1 duels (1× `FULL`), 0 gepubliceerde regel(s) |
| Ligue 1 (FRA) | GEANALYSEERD | 1 duels (1× `FULL`), 1 gepubliceerde regel(s) |
| Championship (ENG) | GEANALYSEERD | 1 duels (1× `LIGHT`), 0 gepubliceerde regel(s) |
| Eredivisie (NED) | GEANALYSEERD | 1 duels (1× `FULL`), 0 gepubliceerde regel(s) |
| Primeira Liga (POR) | GEANALYSEERD | 1 duels (1× `LIGHT`), 0 gepubliceerde regel(s) |
| Belgian Pro League (BEL) | GEANALYSEERD | 1 duels (1× `LIGHT`), 0 gepubliceerde regel(s) |
| Super Lig (TUR) | GEANALYSEERD | 1 duels (1× `FULL`), 0 gepubliceerde regel(s) |
| Scottish Premiership (SCO) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Danish Superliga (DEN) | GEANALYSEERD | 1 duels (1× `FULL`), 1 gepubliceerde regel(s) |
| Ekstraklasa (POL) | GEANALYSEERD | 2 duels (2× `FULL`), 0 gepubliceerde regel(s) |
| UEFA Champions League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Europa League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Conference League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| FA Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 06.11. 20:45 (UK-tijd), buiten het venster; 40 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| League Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 20:45 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| Coppa Italia (ITA) | GEEN WEDSTRIJD | eerstvolgende ronde 01.12. 21:00 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| KNVB Beker (NED) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:45 (UK-tijd), buiten het venster; 26 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| DFB Pokal (GER) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:00 (UK-tijd), buiten het venster; 16 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 55 (vrijdag, vr-zo). 13 duels in het venster en alle dertien doorgerekend: er is vandaag geen enkel duel op `NONE`, en dat is voor Run A in weken niet voorgekomen. De marge op de cap is dus 42 duels — de ruimste in weken, waar het gisteren nog vier duels scheelde. Zeven duels zijn `FULL`; de zes andere hebben een ploeg die niet in de stand van 2025/2026 staat en zijn via `scripts/promotion.py` omgerekend, wat per definitie `LIGHT` geeft (Ipswich Town, Monza, Málaga, Bolton Wanderers, Marítimo en Kortrijk — alle zes binnen `conversion_in_range`, dus geen van de zes strandt op de Coventry-val). Geen enkel duel is kruis-grens, dus `scripts/interleague.py` komt deze run niet aan de orde. Datarijkdom liep van 4.50 (Kortrijk – KV Mechelen, geen opstelling en geen selectiewaarde bij Fotmob) tot 7.50 (VfB Stuttgart – Borussia Mönchengladbach); er viel niets af door de cap, dus er is geen 'laagste die het haalde' en geen 'hoogste die afviel'.

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Bet | Koers | Kans | Edge | Score | Tier | Risico | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Randers FC – Brøndby IF — Over/Under: Under 3 | 1.8800 | 68.8% | +15.58 pp | 10.714 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 2 | Brest – Nice — 1X2: 1 (Brest wint) | 2.3100 | 59.6% | +16.29 pp | 9.706 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 3 | Deportivo Alavés – Málaga — Over/Under: Over 2.5 | 2.1400 | 56.8% | +10.07 pp | 2.860 | `LIGHT` | High | BET op rangorde — onder de lat van 16.0 pp (§5b) |
| 4 | Ipswich Town – Nottingham Forest — Over/Under: Over 2.5 | 1.8300 | 63.1% | +8.41 pp | 2.652 | `LIGHT` | High | BET op rangorde — onder de lat van 16.0 pp (§5b) |

**Vier regels, en de lijst is niet door een grens afgekapt maar door een gebrek aan kandidaten.** `MAX_SHORTLIST` = 5 (vrijdag) en er zijn precies vier publiceerbare selecties — vier duels waarbij alle acht de andere poorten openstonden. `MAX_LIGHT_IN_SHORTLIST` = 2 raakt zijn bovengrens exact (twee `LIGHT`-regels van maximaal twee) maar heeft niets uitgesloten, want er was geen derde `LIGHT`-kandidaat; de reeks `lijstlengte` groeit vandaag dus niet. **Twee van de vier halen hun eigen lat**, en bij die twee staat `bet_beide` op TRUE: Randers FC – Brøndby IF, Under 3, +15,58 pp op `FULL` (ruw +15,56; lat 8,0, met poort 9 erbij 10,0) en Brest – Nice, Brest wint, +16,29 pp op `FULL` (ruw +16,27). **De andere twee staan onder hun lat van 16,0 pp en zijn op rangorde gepubliceerd** (§5b): Deportivo Alavés – Málaga, Over 2.5, +10,07 pp op `LIGHT`, en Ipswich Town – Nottingham Forest, Over 2.5, +8,41 pp op `LIGHT`. Dat hun lat op 16,0 staat en niet op 8,0 is geen willekeur maar de prijs van de omrekening: beide duels hebben een promovendus. Lees die twee dus als 'het beste van vandaag' en niet als een gevonden voordeel — §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de hóógste geclaimde edge. **En dat laatste is vandaag geen abstractie:** de twee regels die hun lat wél halen zijn precies de twee duels waar het model het verst van het Pinnacle-oordeel af staat (Brest +17,5 pp op de thuiszege, Randers +17,4 pp op P(Under 3)) — zie de bevindingen.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Bet | Koers | Kans | Ruwe edge | Score | Viel af op |
|---|---|---|---|---|---|---|
| 1 | Randers FC – Brøndby IF — Over/Under: Under 3 | 1.8800 | 68.8% | +15.56 pp | 10.697 | BET |
| 2 | Brest – Nice — 1X2: 1 (Brest wint) | 2.3100 | 59.6% | +16.27 pp | 9.690 | BET |
| 3 | VfB Stuttgart – Borussia Mönchengladbach — Asian Handicap: Borussia Monchengladbach +1.5 | 1.9408 | 59.1% | +7.57 pp | 4.474 | context spreekt de bet tegen (poort 7) |
| 4 | Alanyaspor – Kocaelispor — Double Chance: Double Chance — Kocaelispor of gelijk (AH +0.5 @ 1.86) | 1.8600 | 59.6% | +5.83 pp | 3.474 | de twee methodes wijzen tegengesteld |
| 5 | Go Ahead Eagles – Telstar — Over/Under: Over 3.25 | 1.9000 | 57.9% | +5.24 pp | 3.032 | de twee methodes wijzen tegengesteld |

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 12 van 12 (allemaal beste prijs uit de bulk-`h2h`; alle twaalf spelende competities hebben een sportkey bij The Odds API) | 39 | 1 |
| Asian Handicap | 12 van 12 (bulk `spreads`) | 53 | 0 |
| Draw No Bet | 12 van 12 (de 0.0-lijn uit diezelfde `spreads`, gratis) | 16 | 0 |
| Double Chance | 12 van 12 (de ±0.5-lijn uit diezelfde `spreads`, gratis) | 9 | 0 |
| Over/Under | 12 van 12 (bulk `totals`) | 54 | 3 |
| BTTS | 10 van de 13 duels, namelijk alle duels met een kandidaat-edge (2 credits per duel); de drie zonder — Vitória de Guimarães – Marítimo, Kortrijk – KV Mechelen en Motor Lublin – Zagłębie Lubin — staan als ‘niet opgevraagd, geen kandidaat-edge’ in markets_checked en niet als gat | 20 | 0 |
| **totaal** | | **191** | **4** |

### Net niet

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
| Torino – Monza | 1X2 — 2 (Monza wint) @ 3.6460 | +10.73 pp | +2.34 pp | +9.22 pp | context |
| VfB Stuttgart – Borussia Mönchengladbach | Asian Handicap — Borussia Monchengladbach +1.5 @ 1.9408 | +6.88 pp | +10.32 pp | +6.88 pp | context |
| Bolton Wanderers – Middlesbrough | Asian Handicap — Middlesbrough -1 @ 2.0192 | +5.18 pp | +10.13 pp | -4.94 pp | context |
| Go Ahead Eagles – Telstar | Over/Under — Over 3.25 @ 1.9000 | +8.61 pp | -8.26 pp | +6.01 pp | tweede methode |
| Alanyaspor – Kocaelispor | Draw No Bet — DNB — Kocaelispor @ 3.2300 | +12.43 pp | -8.90 pp | +11.43 pp | tweede methode |
| Widzew Łódź – Górnik Zabrze | Over/Under — Under 2.5 @ 1.9300 | +3.02 pp | +14.15 pp | -0.83 pp | robuustheid |

6 regels over 13 duels, en de rest telt als volgt op. TWEE duels hebben een `near_miss` die NIET in deze tabel staat omdat de sterkste afgewezen kandidaat daar de gepubliceerde bet zelf is geworden (Deportivo Alavés – Málaga en Ipswich Town – Nottingham Forest; die staan in de run-state als `near_miss_gepubliceerd`, want een andere selectie van een duel waarop is gepubliceerd is dezelfde mening en geen afgewezen kandidaat — §1a, §6d). En 5 duels hebben er helemaal geen: bij Vitória de Guimarães – Marítimo, Kortrijk – KV Mechelen en Motor Lublin – Zagłębie Lubin bleef de sterkste kandidaat onder de NEAR-ondergrens (6,0 pp op `LIGHT`, 3,0 pp op `FULL`) — precies de drie duels die ook geen BTTS kregen, want geen kandidaat-edge — en bij Randers FC – Brøndby IF en Brest – Nice stonden alle negen poorten open, dus daar is niets afgewezen om te melden. De ene poort-8-rij (Go Ahead Eagles – Telstar, Telstar wint @5.508, marktkans 18,3%) staat niet in deze tabel maar als eigen categorie `underdog` in het schaduwlogboek; de Over 3.25 van datzelfde duel, die op de tweede methode afviel, staat hier wel. Er is vandaag geen enkel duel op `NONE`, dus er is ook geen regel die ontbreekt omdat er niets is doorgerekend.

## Wedstrijden

De 13 duels in het inzetvenster, op aftraptijd. De vier gepubliceerde regels staan in het volledige format van §5; bij de andere negen staat de reden in één regel, met de cijfers per poort in de tabel "Net niet" hierboven.

### Motor Lublin – Zagłębie Lubin · 18:00 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel

### Alanyaspor – Kocaelispor · 19:00 NL · Super Lig (TUR)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — data conflicterend

### Randers FC – Brøndby IF · 19:00 NL · Danish Superliga (DEN)
- **Data:** `FULL` · datarijkdom 6.5
- **Bet:** Over/Under — Under 3 — Odds: best **1.8800** (The Odds API (Pinnacle))
- **Implied prob:** 53.2%  •  **My prob:** 68.8%  (ruw 68.8%)
- **Edge:** +15.58 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.217 / 1.390 · splitsmethode 0.414 / 0.902
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.217 thuis / 1.390 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 0.414 / 0.902 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 1 van 4 over 13 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 10.714. Ruwe kans 0.6875, ruwe edge 15.56 pp; xG-methode 10.06 pp, splitsmethode 37.56 pp, zwakste stand van het (shrink, rho)-grid 7.33 pp. shrink staat sinds 19 sep op 1.00 (§6e). ONDER-KANT: §6g meet dat P(Under) bij élk duel ruim twee procentpunt te hoog staat door een vormfout in score_grid (gemeten vandaag over 1486 doorgerekende duels: P(Under 3.0) voorspeld 64,0% tegen werkelijk 61,9%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,616 doelpunt per duel over 88 gevallen (z = +3,49 — gegroeid van +0,592 en z = +3,34 gisteren), terwijl de Over-kant op -0,221 staat (z = -0,85). Poort 9 (§1h) BINDT hier wél, want dit duel staat op FULL, en deze selectie haalt de verzwaarde lat van 10,0 pp ruim. Dat is de rem die er is; de oorzaak — keuze (a) van 11 oktober, de vormfout zelf repareren — staat nog open. Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je haar leest. 

### Go Ahead Eagles – Telstar · 20:00 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### VfB Stuttgart – Borussia Mönchengladbach · 20:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 7.5
- **GEEN BET** — context spreekt de bet tegen — blessures: Borussia Mönchengladbach mist 50% van de selectiewaarde tegen 14% bij VfB Stuttgart — Jan Leszczyński (injury, terug Early December 2026), Ko Itakura (injury, terug Doubtful), Enzo Leopold (injury, terug Late May 2027)

### Widzew Łódź – Górnik Zabrze · 20:30 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge niet robuust over het (shrink, rho)-grid

### Brest – Nice · 20:45 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.5
- **Bet:** 1X2 — 1 (Brest wint) — Odds: best **2.3100** (The Odds API — beste prijs 1xBet)
- **Implied prob:** 43.3%  •  **My prob:** 59.6%  (ruw 59.6%)
- **Edge:** +16.29 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 2.003 / 1.013 · splitsmethode 2.229 / 1.276 · Understat 1.853 / 1.355
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 2.003 thuis / 1.013 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.229 / 1.276 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 1.853 / 1.355, rollende xG over 8 duels {'home': [1.2, 2.04, 8], 'away': [1.11, 1.92, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 2 van 4 over 13 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 9.706. Ruwe kans 0.5956, ruwe edge 16.27 pp; xG-methode 16.53 pp, splitsmethode 15.26 pp, zwakste stand van het (shrink, rho)-grid 12.4 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Kortrijk – KV Mechelen · 20:45 NL · Belgian Pro League (BEL)
- **Data:** `LIGHT` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel

### Torino – Monza · 20:45 NL · Serie A (ITA)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Monza mist 41% van de selectiewaarde tegen 20% bij Torino — Cyril Ngonge (injury, terug Doubtful), Yvan Kouadio Maye (injury, terug Doubtful), Jan Ziólkowski (injury, terug Early November 2026)

### Bolton Wanderers – Middlesbrough · 21:00 NL · Championship (ENG)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Middlesbrough mist 20% van de selectiewaarde tegen 2% bij Bolton Wanderers — David Strelec (injury, terug Early November 2026), Rokas Pukštas (injury, terug Early November 2026), Alfie Jones (injury, terug Early November 2026)

### Deportivo Alavés – Málaga · 21:00 NL · La Liga (ESP)
- **Data:** `LIGHT` · datarijkdom 6.5
- **Bet:** Over/Under — Over 2.5 — Odds: best **2.1400** (The Odds API (1xBet))
- **Implied prob:** 46.7%  •  **My prob:** 56.8%  (ruw 56.8%)
- **Edge:** +10.07 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 1.989 / 0.830 · splitsmethode 2.196 / 1.418
- **Inputs:** Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen (§4, k=8); doelverwachting 1.989 thuis / 0.830 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.196 / 1.418 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 3 van 4 over 13 doorgerekende wedstrijden. BET op rangorde — onder de lat van 16.0 pp (§5b). selection_score 2.86. Ruwe kans 0.5679, ruwe edge 10.06 pp; xG-methode 6.77 pp, splitsmethode 23.23 pp, zwakste stand van het (shrink, rho)-grid 6.77 pp. shrink staat sinds 19 sep op 1.00 (§6e). OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de systematische fout eruit en niet de onzekerheid. bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel (§5b). 

### Ipswich Town – Nottingham Forest · 21:00 NL · Premier League (ENG)
- **Data:** `LIGHT` · datarijkdom 6.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.8300** (The Odds API (1xBet))
- **Implied prob:** 54.6%  •  **My prob:** 63.1%  (ruw 63.0%)
- **Edge:** +8.41 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 1.401 / 1.847 · splitsmethode 1.296 / 1.963
- **Inputs:** Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen (§4, k=8); doelverwachting 1.401 thuis / 1.847 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 1.296 / 1.963 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 4 van 4 over 13 doorgerekende wedstrijden. BET op rangorde — onder de lat van 16.0 pp (§5b). selection_score 2.652. Ruwe kans 0.6304, ruwe edge 8.4 pp; xG-methode 8.35 pp, splitsmethode 8.6 pp, zwakste stand van het (shrink, rho)-grid 7.01 pp. shrink staat sinds 19 sep op 1.00 (§6e). OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de systematische fout eruit en niet de onzekerheid. bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel (§5b). 

### Vitória de Guimarães – Marítimo · 21:45 NL · Primeira Liga (POR)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel
