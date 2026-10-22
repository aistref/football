## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
| Premier League (ENG) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Serie A (ITA) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| La Liga (ESP) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Bundesliga (GER) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Ligue 1 (FRA) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Championship (ENG) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Eredivisie (NED) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Primeira Liga (POR) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Belgian Pro League (BEL) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Super Lig (TUR) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Scottish Premiership (SCO) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Danish Superliga (DEN) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Ekstraklasa (POL) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Champions League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Europa League | GEANALYSEERD | 18 duels (14× `LIGHT`, 4× `NONE`), 1 gepubliceerde regel(s) |
| UEFA Conference League | GEANALYSEERD | 18 duels (9× `LIGHT`, 9× `NONE`), 1 gepubliceerde regel(s) |
| FA Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 07.11. 16:00 (UK-tijd), buiten het venster; 40 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| League Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 20:45 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| Coppa Italia (ITA) | GEEN WEDSTRIJD | eerstvolgende ronde 01.12. 21:00 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| KNVB Beker (NED) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:45 (UK-tijd), buiten het venster; 26 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| DFB Pokal (GER) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:00 (UK-tijd), buiten het venster; 16 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 40 (donderdag, ma-do). 36 duels in het venster, waarvan 23 doorgerekend en 13 op `NONE`. Dat is de krapste marge die Run A tot nu toe heeft gehad: vier duels onder de cap. Alle 36 duels zijn kruis-grens, dus alle 36 lopen langs `scripts/interleague.py`; de dertien op `NONE` vallen in twee groepen — elf waarvoor het LAND geen gemeten Europese competitiefactor heeft (Armenië, Slovenië, Kazachstan, Litouwen, Georgië, Andorra, Letland, Albanië, Bosnië, Finland, Gibraltar), en drie waar de omgerekende sterkte BUITEN het gemeten bereik valt (OFI Crete, CSKA Sofia, Mjällby). Eén geval staat los: Torreense speelt in Liga Portugal 2 en niet in de hoogste divisie waarop de factor is gemeten. Datarijkdom liep van 4.33 tot 6.17 over de doorgerekende duels; er viel niets af door de cap, dus er is geen 'laagste die het haalde' en geen 'hoogste die afviel'.

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Bet | Koers | Kans | Edge | Score | Tier | Risico | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Braga – Gent — Over/Under: Over 2.5 | 2.2152 | 68.3% | +23.19 pp | 7.923 | `LIGHT` | High | BET — en haalt ook de lat van 16.0 pp |
| 2 | Omonia Nicosia – Benfica — Over/Under: Under 3 | 1.9300 | 72.2% | +20.34 pp | 7.338 | `LIGHT` | High | BET — en haalt ook de lat van 16.0 pp |

**Beide gepubliceerde regels halen hun eigen lat van 16,0 pp, en beide ook op de ruwe schaal** (`bet_beide` = TRUE): Braga – Gent, Over 2.5, +23,19 pp (ruw +22,72), en Omonia Nicosia – Benfica, Under 3, +20,34 pp (ruw +19,85). Bij beide staan alle negen poorten open. **De lijst is twee regels lang en niet drie, en dat is niet de drempel maar `MAX_LIGHT_IN_SHORTLIST` = 2** (§0): er is vandaag geen enkel `FULL`-duel, want alle 36 wedstrijden zijn kruis-grens en een omgerekende ploeg is nooit `FULL`. Die grens is vandaag DUUR. **Vijf** selecties haalden alle negen poorten én stonden boven hun eigen lat, en er passen er twee. De drie die afvallen staan hieronder per wedstrijd en gaan als `failed_gate = lijstlengte` het schaduwlogboek in (§5b, 26 sep 2026): Union St.Gilloise – Hapoel Beer Sheva (Under 3.5 @1.67, +16,61 pp, rang 3), Sturm Graz – Marseille (Marseille wint @2.0584, +17,30 pp, rang 4) en Celtic – Celta Vigo (Celta Vigo wint @2.5876, +16,74 pp, rang 5). Let op de volgorde: de rangorde loopt op `selection_score` (edge × kans × datafactor) en niet op edge, dus Sturm Graz staat met een HOGERE edge lager dan Union SG met een hogere kans. Lees de lijst niet als een gevonden voordeel: §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Bet | Koers | Kans | Ruwe edge | Score | Viel af op |
|---|---|---|---|---|---|---|
| 1 | Braga – Gent — Over/Under: Over 2.5 | 2.2152 | 67.9% | +22.72 pp | 7.709 | BET |
| 2 | Omonia Nicosia – Benfica — Over/Under: Under 3 | 1.9300 | 71.7% | +19.85 pp | 7.112 | BET |
| 3 | Beşiktaş – Crystal Palace — Asian Handicap: Crystal Palace +0.25 | 1.9996 | 68.9% | +18.88 pp | 6.503 | underdog-kant onder de ondergrens (poort 8) |

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 2 van 2 (allemaal beste prijs uit de bulk; beide spelende competities hebben een sportkey) | 64 | 0 |
| Asian Handicap | 2 van 2 (bulk `spreads`) | 82 | 0 |
| Draw No Bet | 2 van 2 (de 0.0-lijn uit diezelfde `spreads`, gratis) | 22 | 0 |
| Double Chance | 2 van 2 (de ±0.5-lijn uit diezelfde `spreads`, gratis) | 10 | 0 |
| Over/Under | 2 van 2 (bulk `totals`) | 110 | 2 |
| BTTS | 19 van de 20 duels met een kandidaat-edge (2 credits per duel); FK Crvena Zvezda – FC København stond niet in de spreads-respons en kon niet op event-id worden opgevraagd | 38 | 0 |
| **totaal** | | **326** | **2** |

### Net niet

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
| Dinamo Zagreb – NEC Nijmegen | Over/Under — Over 3.5 @ 2.4896 | +11.16 pp | +16.80 pp | +5.19 pp | edge |
| AFC Bournemouth – Milan | Over/Under — Under 2.5 @ 2.2500 | +5.57 pp | +15.71 pp | +1.50 pp | edge |
| Beşiktaş – Crystal Palace | Over/Under — Under 3.5 @ 1.6700 | +7.40 pp | +2.98 pp | +7.40 pp | edge |
| Hoffenheim – Lyon | Over/Under — Under 3.25 @ 1.8600 | +8.60 pp | +9.70 pp | +7.51 pp | edge |
| Olympiacos – Sparta Prague | Over/Under — Under 2.5 @ 2.1368 | +4.89 pp | +17.27 pp | +3.49 pp | edge |
| FK Crvena Zvezda – FC København | 1X2 — 1 (FK Crvena Zvezda wint) @ 2.2400 | +6.69 pp | +18.46 pp | +5.09 pp | edge |
| Getafe – Lugano | BTTS — Beide ploegen scoren — nee @ 1.9100 | +11.78 pp | +17.51 pp | +5.33 pp | edge |
| Jablonec – Brighton & Hove Albion | Over/Under — Under 3.5 @ 1.6600 | +8.22 pp | +14.27 pp | +8.22 pp | edge |
| Ajax – Atalanta | Over/Under — Under 3 @ 1.9500 | +12.38 pp | +11.73 pp | +10.13 pp | edge |
| FC Midtjylland – St.Truiden | Asian Handicap — FC Midtjylland -1 @ 2.1500 | +6.24 pp | +4.68 pp | +1.01 pp | context |
| Monaco – Freiburg | 1X2 — 1 (AS Monaco wint) @ 2.2800 | +3.96 pp | +25.41 pp | +3.45 pp | edge |

11 regels. Van de 10 duels hebben 25 geen `near_miss`. Bij Inter – Shakhtar Donetsk en Real Betis – Feyenoord bleef de sterkste kandidaat onder de NEAR-ondergrens van 6,0 pp op `LIGHT` en is er dus niets om te melden. Bij Bayern München – Arsenal is er geen kandidaat omdat het duel op `NONE` staat en geen enkele markt is doorgerekend. En bij Real Madrid – RB Leipzig en Aston Villa – Viking is de sterkste selectie juist de gepubliceerde bet: een andere selectie van een duel waarop is gepubliceerd is dezelfde mening en geen afgewezen kandidaat (§1a, §6d). De drie poort-8-rijen (Aston Villa – Viking, Club Brugge – Lens en Real Madrid – RB Leipzig) staan niet in deze tabel maar als eigen categorie `underdog` in het schaduwlogboek; voor Club Brugge staat hier wel de Under-kandidaat die daarnaast afviel op edge.

## Wedstrijden

De 10 duels in het inzetvenster, op aftraptijd. De twee gepubliceerde regels staan in het volledige format van §5; bij de andere acht staat de reden in één regel, met de cijfers per poort in de tabel "Net niet" hierboven.

### Kairat Almaty – Panathinaikos · 16:30 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: KAZ: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Ararat Armenia – AZ Alkmaar · 18:45 NL · UEFA Europa League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: ARM: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Dinamo Zagreb – NEC Nijmegen · 18:45 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 5.17
- **GEEN BET** — edge onder drempel (+12.57 pp, nodig 16.0)

### FK Crvena Zvezda – FC København · 18:45 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 5.33
- **GEEN BET** — edge onder drempel (+9.35 pp, nodig 16.0)

### FK Kauno Žalgiris – Brann · 18:45 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: LTU: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Ferencváros – Torreense · 18:45 NL · UEFA Europa League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — uit: POR: ploeg speelt in 'Liga Portugal 2' (id 185), niet in de hoogste divisie (id 61) waarop de factor is gemeten

### Getafe – Lugano · 18:45 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 5.33
- **GEEN BET** — edge onder drempel (+13.37 pp, nodig 16.0)

### Iberia 1999 – Mjällby · 18:45 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: GEO: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen); uit: SWE: binnenlandse verhouding aanval 0.796 / verdediging 1.137 over 24 duels, omgerekend met de gemeten Europese competitiefactor x0.657/1.323 (n=65 Europese duels) naar 0.550/1.468; aanval 0.550 buiten 0.585-2.432, verdediging 1.468 buiten 0.388-1.446

### Inter Club d'Escaldes – Universitatea Craiova · 18:45 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: AND: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Jablonec – Brighton & Hove Albion · 18:45 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.83
- **GEEN BET** — edge onder drempel (+9.91 pp, nodig 16.0)

### Juventus – Rennes · 18:45 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEEN BET** — edge onder drempel

### Lech Poznań – Sunderland · 18:45 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 5.67
- **GEEN BET** — edge onder drempel

### Nordsjælland – CSKA Sofia · 18:45 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — uit: BUL: binnenlandse verhouding aanval 1.235 / verdediging 0.661 over 30 duels, omgerekend met de gemeten Europese competitiefactor x0.489/1.487 (n=45 Europese duels) naar 0.581/1.083; aanval 0.581 buiten 0.585-2.432

### OFI Crete – Bayer Leverkusen · 18:45 NL · UEFA Europa League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: GRE: binnenlandse verhouding aanval 1.028 / verdediging 1.361 over 26 duels, omgerekend met de gemeten Europese competitiefactor x0.795/1.308 (n=128 Europese duels) naar 0.813/1.685; verdediging 1.685 buiten 0.388-1.446

### Pafos FC – Riga FC · 18:45 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — uit: LVA: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Sturm Graz – Marseille · 18:45 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEKWALIFICEERD, NIET GEPUBLICEERD** — 1X2 — 2 (Marseille wint) @ 2.0584, edge +17.32 pp, selection_score 5.706, rang 4 op de dagranglijst. alle negen poorten open en +17.32 pp boven de drempel, maar rang 4 en niet in de lijst van 2 regels; laagste gepubliceerde selection_score 7.338
- **Doelverwachting:** xG-methode 0.887 / 2.215 · splitsmethode 0.748 / 1.669

### Trabzonspor – Heart of Midlothian · 18:45 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.33
- **GEEN BET** — edge onder drempel

### Union St.Gilloise – Hapoel Beer Sheva · 18:45 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEKWALIFICEERD, NIET GEPUBLICEERD** — Over/Under — Under 3.5 @ 1.6700, edge +16.57 pp, selection_score 6.334, rang 3 op de dagranglijst. alle negen poorten open en +16.57 pp boven de drempel, maar rang 3 en niet in de lijst van 2 regels; laagste gepubliceerde selection_score 7.338
- **Doelverwachting:** xG-methode 1.781 / 0.603 · splitsmethode 2.476 / 0.426

### AFC Bournemouth – Milan · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 5.67
- **GEEN BET** — edge onder drempel (+7.87 pp, nodig 16.0)

### AGF – Egnatia · 21:00 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — uit: ALB: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Ajax – Atalanta · 21:00 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.83
- **GEEN BET** — edge onder drempel (+12.67 pp, nodig 16.0)

### Beşiktaş – Crystal Palace · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEEN BET** — edge onder drempel (+6.97 pp, nodig 16.0)

### Borac Banja Luka – KuPS · 21:00 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: BIH: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen); uit: FIN: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Braga – Gent · 21:00 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.83
- **Bet:** Over/Under — Over 2.5 — Odds: best **2.2152** (The Odds API (Matchbook, beurs: 2.24 bruto / 2.2152 na 2% commissie))
- **Implied prob:** 45.1%  •  **My prob:** 68.3%  (ruw 67.9%)
- **Edge:** +23.19 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 2.338 / 1.074 · splitsmethode 2.918 / 0.958
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 2.338 thuis / 1.074 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.918 / 0.958 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 1 van 2 over 36 doorgerekende wedstrijden. BET — en haalt ook de lat van 16.0 pp. selection_score 7.923. Ruwe kans 0.6786, ruwe edge 22.72 pp; xG-methode 21.11 pp, splitsmethode 29.18 pp, zwakste stand van het (shrink, rho)-grid 17.06 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Celtic – Celta Vigo · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEKWALIFICEERD, NIET GEPUBLICEERD** — 1X2 — 2 (Celta Vigo wint) @ 2.5876, edge +16.66 pp, selection_score 4.607, rang 5 op de dagranglijst. alle negen poorten open en +16.66 pp boven de drempel, maar rang 5 en niet in de lijst van 2 regels; laagste gepubliceerde selection_score 7.338
- **Doelverwachting:** xG-methode 1.144 / 2.044 · splitsmethode 1.172 / 1.507

### FC Midtjylland – St.Truiden · 21:00 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 5.33
- **GEEN BET** — context spreekt de bet tegen — blessures: FC Midtjylland mist 28% van de selectiewaarde tegen 8% bij St.Truiden — Victor Bak (injury, terug About a week), Elías Ólafsson (injury, terug Day to day), Magnus Jensen (injury, terug Day to day)

### Hoffenheim – Lyon · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 5.17
- **GEEN BET** — edge onder drempel (+9.24 pp, nodig 16.0)

### Jagiellonia Białystok – Anderlecht · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEEN BET** — edge onder drempel

### Lillestrøm – Real Sociedad · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 5.67
- **GEEN BET** — edge onder drempel

### Lincoln Red Imps FC – FC Twente · 21:00 NL · UEFA Conference League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: GIB: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Monaco – Freiburg · 21:00 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.33
- **GEEN BET** — edge onder drempel (+8.53 pp, nodig 16.0)

### NK Celje – Salzburg · 21:00 NL · UEFA Europa League
- **Data:** `NONE`
- **GEEN BET** — kruis-grens, omrekening niet mogelijk — thuis: SVN: geen gemeten competitiefactor (minder dan 40 Europese duels in de meting, of niet in de meting opgenomen)

### Olympiacos – Sparta Prague · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **GEEN BET** — edge onder drempel (+7.67 pp, nodig 16.0)

### Omonia Nicosia – Benfica · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 4.67
- **Bet:** Over/Under — Under 3 — Odds: best **1.9300** (The Odds API (Pinnacle))
- **Implied prob:** 51.8%  •  **My prob:** 72.2%  (ruw 71.7%)
- **Edge:** +20.34 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 0.997 / 1.336 · splitsmethode 0.967 / 0.860
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 0.997 thuis / 1.336 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 0.967 / 0.860 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 2 van 2 over 36 doorgerekende wedstrijden. BET — en haalt ook de lat van 16.0 pp. selection_score 7.338. Ruwe kans 0.7166, ruwe edge 19.85 pp; xG-methode 17.56 pp, splitsmethode 29.0 pp, zwakste stand van het (shrink, rho)-grid 13.67 pp. shrink staat sinds 19 sep op 1.00 (§6e). ONDER-KANT: §6g meet dat P(Under) bij élk duel 1,6 tot 2,4 procentpunt te hoog staat door een vormfout in score_grid, en dat de gespeelde Under-kant daar bovenop een selectie-effect van +0,584 doelpunt per duel heeft (z = +3,24). Over het logboek: Under 112 picks op -14,3%, Over 72 picks op +8,8%. Poort 9 (§1h) bindt hier NIET — op LIGHT geldt hij per besluit van 12 okt 2026 niet, en op FULL bindt hij alleen in de band 8-10 pp. Lees deze regel dus met die scheefstand erbij. 

### Thun – Hajduk Split · 21:00 NL · UEFA Conference League
- **Data:** `LIGHT` · datarijkdom 4.33
- **GEEN BET** — edge onder drempel

### Viktoria Plzeň – Levski Sofia · 21:00 NL · UEFA Europa League
- **Data:** `LIGHT` · datarijkdom 6.17
- **GEEN BET** — edge onder drempel
