## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
| Premier League (ENG) | GEANALYSEERD | 4 duels (3× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| Serie A (ITA) | GEANALYSEERD | 4 duels (4× `FULL`), 2 gepubliceerde regel(s) |
| La Liga (ESP) | GEANALYSEERD | 4 duels (2× `FULL`, 2× `LIGHT`), 1 gepubliceerde regel(s) |
| Bundesliga (GER) | GEANALYSEERD | 6 duels (3× `FULL`, 3× `LIGHT`), 0 gepubliceerde regel(s) |
| Ligue 1 (FRA) | GEANALYSEERD | 1 duels (1× `FULL`), 0 gepubliceerde regel(s) |
| Championship (ENG) | GEANALYSEERD | 11 duels (7× `FULL`, 4× `LIGHT`), 1 gepubliceerde regel(s) |
| Eredivisie (NED) | GEANALYSEERD | 3 duels (1× `FULL`, 2× `LIGHT`), 0 gepubliceerde regel(s) |
| Primeira Liga (POR) | GEANALYSEERD | 3 duels (3× `FULL`), 1 gepubliceerde regel(s) |
| Belgian Pro League (BEL) | GEANALYSEERD | 4 duels (2× `FULL`, 2× `LIGHT`), 0 gepubliceerde regel(s) |
| Super Lig (TUR) | GEANALYSEERD | 3 duels (1× `FULL`, 1× `LIGHT`, 1× `NONE`), 0 gepubliceerde regel(s) |
| Scottish Premiership (SCO) | GEANALYSEERD | 4 duels (3× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| Danish Superliga (DEN) | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| Ekstraklasa (POL) | GEANALYSEERD | 4 duels (3× `FULL`, 1× `LIGHT`), 0 gepubliceerde regel(s) |
| UEFA Champions League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Europa League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| UEFA Conference League | GEEN WEDSTRIJD | niets op de kalender in het inzetvenster |
| FA Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 06.11. 20:45 (UK-tijd), buiten het venster; 40 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| League Cup (ENG) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 20:45 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| Coppa Italia (ITA) | GEEN WEDSTRIJD | eerstvolgende ronde 01.12. 21:00 (UK-tijd), buiten het venster; 8 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| KNVB Beker (NED) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:45 (UK-tijd), buiten het venster; 26 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |
| DFB Pokal (GER) | GEEN WEDSTRIJD | eerstvolgende ronde 27.10. 18:00 (UK-tijd), buiten het venster; 16 teamparen op de fixturepagina, dus de slug is goed en de bron heeft niet gefaald |

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 van 55 (zaterdag, vr-zo). 51 duels in het venster — de grootste Run A-lijst in weken — en 50 ervan doorgerekend. De marge op de cap is dus VIER duels, de krapste sinds de cap op 40/55 staat: een volle Championship-speelronde meer en hij had gebonden. 33 duels zijn `FULL`; 17 hebben een ploeg die niet in de stand van 2025/2026 staat en zijn via `scripts/promotion.py` omgerekend, wat per definitie `LIGHT` geeft. PRECIES ÉÉN duel komt op `NONE` uit: Gaziantep FK – Erzurumspor FK, waar Erzurumspor FK buiten `conversion_in_range` valt — de Coventry-val, en de juiste uitkomst, want buiten het gemeten bereik is doorrekenen raden. Geen enkel duel is kruis-grens, dus `scripts/interleague.py` komt deze run niet aan de orde. Datarijkdom liep van 4.50 (de vier Belgische duels) tot 8.00 (Valencia – Villarreal); er viel niets af door de cap, dus er is geen 'laagste die het haalde' en geen 'hoogste die afviel'. De context is voor alle 51 duels opgehaald zoals §1c eist, met nul fouten.

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Bet | Koers | Kans | Edge | Score | Tier | Risico | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Lazio – Parma — Over/Under: Under 2.5 | 2.0400 | 63.1% | +14.13 pp | 8.923 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 2 | Como – Sassuolo — Over/Under: Under 3.5 | 1.8232 | 66.4% | +11.58 pp | 7.693 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 3 | Alverca – Arouca — Over/Under: Over 2.5 | 1.9212 | 60.8% | +8.74 pp | 5.313 | `FULL` | Medium | BET — en haalt ook de lat van 8.0 pp |
| 4 | Racing Santander – Espanyol — Over/Under: Over 2.5 | 1.7300 | 70.6% | +12.84 pp | 4.535 | `LIGHT` | High | BET op rangorde — onder de lat van 16.0 pp (§5b) |
| 5 | Lincoln City – Burnley — Over/Under: Over 2.5 | 1.9212 | 64.9% | +12.82 pp | 4.158 | `LIGHT` | High | BET op rangorde — onder de lat van 16.0 pp (§5b) |

**Vijf regels, en voor het eerst in weken bindt de LIJSTLENGTE in plaats van het aantal kandidaten.** `MAX_SHORTLIST` = 5 (zaterdag) en er zijn VEERTIEN duels met een publiceerbare selectie — veertien duels waarbij alle acht de andere poorten openstonden en de edge boven de NEAR-ondergrens bleef. Er passen vijf regels in, dus negen vallen af op rangorde. `MAX_LIGHT_IN_SHORTLIST` = 2 raakt zijn bovengrens exact (twee `LIGHT`-regels van maximaal twee) maar heeft niets uitgesloten, want er is geen derde `LIGHT`-kandidaat binnen de eerste vijf plekken. **DRIE van de vijf halen hun eigen lat van 8,0 pp op `FULL`**, en bij alle vijf staat `bet_beide` op TRUE: Lazio – Parma Under 2.5 (+14,13 pp, ruw +14,53), Como – Sassuolo Under 3.5 (+11,58 pp, ruw +12,01) en Alverca – Arouca Over 2.5 (+8,74 pp, ruw +9,11). **De twee andere staan onder hun lat van 16,0 pp en zijn op rangorde gepubliceerd** (§5b): Racing Santander – Espanyol Over 2.5 (+12,84 pp op `LIGHT`) en Lincoln City – Burnley Over 2.5 (+12,82 pp op `LIGHT`). Dat hun lat op 16,0 staat en niet op 8,0 is geen willekeur maar de prijs van de omrekening: beide duels hebben een promovendus (Racing Santander, Lincoln City) en Lincoln – Burnley zelfs ook een degradant. Lees die twee dus als 'het beste van vandaag' en niet als een gevonden voordeel — §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de hóógste geclaimde edge. **En één gekwalificeerde selectie valt af op lijstlengte, wat op het eerste gezicht als een fout leest:** Chelsea – Tottenham Hotspur, BTTS 'nee' @2.6856, +8,38 pp op `FULL` — boven zijn lat — staat op rang 6 en haalt de lijst niet, terwijl de twee `LIGHT`-regels die hun lat NIET halen er wél in staan. Dat volgt uit §5b plus `selection_score`: de drempel bindt alleen als er MEER selecties boven hun lat staan dan er plekken zijn (dat zijn er vier op vijf, dus de rangorde beslist), en in `selection_score` verslaat +12,84 pp op `LIGHT` × 0,5 een +8,38 pp op `FULL`. Zie bevinding 1.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Bet | Koers | Kans | Ruwe edge | Score | Viel af op |
|---|---|---|---|---|---|---|
| 1 | Eyüpspor – Kasımpaşa — Asian Handicap: Eyüpspor +1.5 | 1.4800 | 80.8% | +13.19 pp | 10.651 | underdog-kant onder de ondergrens (poort 8) |
| 2 | Lazio – Parma — Asian Handicap: Parma +1.5 | 1.7400 | 71.3% | +13.85 pp | 9.878 | underdog-kant onder de ondergrens (poort 8) |
| 3 | Lens – Paris FC — Draw No Bet: DNB — RC Lens | 1.8700 | 66.4% | +12.93 pp | 8.587 | context spreekt de bet tegen (poort 7) |
| 4 | Como – Sassuolo — Over/Under: Under 3.5 | 1.8232 | 66.9% | +12.01 pp | 8.030 | BET |
| 5 | Gil Vicente – FC Porto — Asian Handicap: Gil Vicente +1.25 | 1.8500 | 64.6% | +10.55 pp | 6.816 | underdog-kant onder de ondergrens (poort 8) |

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 12 van 12 — 11 op de beste prijs uit de bulk-`h2h`, en de Scottish Premiership (4 duels) op het gratis BetExplorer-MARKTGEMIDDELDE, want die competitie heeft geen sportkey bij The Odds API; daar is de bookmaker niet herleidbaar en valt de edge systematisch te laag uit (§1a) | 147 | 0 |
| Asian Handicap | 11 van 12 (bulk `spreads`; geen spreads voor de Scottish Premiership) | 202 | 0 |
| Draw No Bet | 11 van 12 (de 0.0-lijn uit diezelfde `spreads`, gratis) | 55 | 0 |
| Double Chance | 11 van 12 (de ±0.5-lijn uit diezelfde `spreads`, gratis) | 29 | 0 |
| Over/Under | 11 van 12 (bulk `totals`; geen totals voor de Scottish Premiership) | 216 | 5 |
| BTTS | 28 van de 30 duels met een kandidaat-edge (2 credits per duel). De twee die afvielen zijn Dundee United – Aberdeen en Falkirk – Kilmarnock: geen sportkey, dus geen event-id om de markt op op te vragen. De 21 duels zonder kandidaat-edge staan als 'niet opgevraagd — geen kandidaat-edge in dit duel' in `markets_checked` en niet als gat | 56 | 0 |
| **totaal** | | **705** | **5** |

### Net niet

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
| Aston Villa – Manchester City | Asian Handicap — Aston Villa +1.5 @ 1.5900 | +6.24 pp | +11.52 pp | +6.24 pp | context |
| Cagliari – Bologna | 1X2 — 2 (Bologna wint) @ 2.7200 | +4.96 pp | +14.73 pp | +2.50 pp | context |
| Rayo Vallecano – Elche | 1X2 — 1 (Rayo Vallecano wint) @ 1.8200 | +6.38 pp | +5.68 pp | +2.73 pp | context |
| Augsburg – Union Berlin | Over/Under — Over 3.5 @ 2.2800 | +9.01 pp | -7.42 pp | +8.40 pp | tweede methode |
| 1. FC Köln – Schalke 04 | 1X2 — 1 (1. FC Köln wint) @ 2.1760 | +11.47 pp | +8.91 pp | +7.67 pp | edge |
| Paderborn – Hamburger SV | Over/Under — Under 2.5 @ 2.4700 | +9.60 pp | -7.33 pp | +2.25 pp | tweede methode |
| RB Leipzig – Elversberg | Asian Handicap — RB Leipzig -1.5 @ 2.1100 | +4.85 pp | +20.79 pp | -3.39 pp | context |
| Lens – Paris FC | 1X2 — 1 (RC Lens wint) @ 2.5484 | +12.48 pp | +25.60 pp | +11.09 pp | context |
| Portsmouth – Millwall | 1X2 — 2 (Millwall wint) @ 2.9600 | +3.05 pp | +9.70 pp | +1.88 pp | context |
| Sheffield United – Derby County | 1X2 — 2 (Derby County wint) @ 4.8220 | +4.70 pp | +23.25 pp | +4.10 pp | context |
| Blackburn Rovers – Wrexham | BTTS — Beide ploegen scoren — nee @ 2.0584 | +3.52 pp | +10.64 pp | -0.06 pp | robuustheid |
| Preston North End – West Bromwich Albion | 1X2 — 1 (Preston North End wint) @ 3.8420 | +8.28 pp | +17.98 pp | +7.66 pp | context |
| Stoke City – Bristol City | Draw No Bet — DNB — Bristol City @ 2.1500 | +10.10 pp | -1.10 pp | +6.37 pp | tweede methode |
| West Ham United – Southampton | Over/Under — Over 3.5 @ 2.2936 | +6.54 pp | +33.81 pp | +2.05 pp | edge |
| FC Utrecht – PEC Zwolle | 1X2 — 1 (FC Utrecht wint) @ 1.6860 | +0.13 pp | +24.46 pp | -3.13 pp | context |
| ADO Den Haag – SC Heerenveen | Over/Under — Under 3.5 @ 1.7350 | +11.33 pp | -7.60 pp | +6.89 pp | tweede methode |
| Estrela da Amadora – Casa Pia AC | Over/Under — Over 2.5 @ 1.9408 | +6.05 pp | -1.46 pp | +6.05 pp | tweede methode |
| Gil Vicente – FC Porto | 1X2 — X (gelijkspel) @ 4.7240 | +4.31 pp | +2.57 pp | +3.15 pp | edge |
| Eyüpspor – Kasımpaşa | 1X2 — X (gelijkspel) @ 4.0380 | +3.96 pp | +1.82 pp | +2.68 pp | edge |
| Dundee United – Aberdeen | 1X2 — 1 (Dundee United wint) @ 2.0700 | +4.32 pp | +7.45 pp | +2.84 pp | edge |
| Falkirk – Kilmarnock | 1X2 — 1 (Falkirk wint) @ 1.8600 | +3.89 pp | +13.80 pp | +1.48 pp | context |
| Piast Gliwice – Cracovia | Over/Under — Under 2.5 @ 2.3328 | +5.40 pp | +13.91 pp | +3.51 pp | edge |
| Pogoń Szczecin – Radomiak Radom | Over/Under — Over 3 @ 2.0500 | +3.69 pp | +17.81 pp | +1.99 pp | edge |
| Wisła Kraków – Raków Częstochowa | Over/Under — Over 3.5 @ 2.3524 | +9.71 pp | +19.66 pp | +4.70 pp | edge |

24 regels over 51 duels, en de rest telt als volgt op. VIJF duels hebben een `near_miss` die NIET in deze tabel staat omdat de sterkste afgewezen kandidaat daar de gepubliceerde bet zelf is geworden (de vijf duels van de topselectie; die staan in de run-state als `near_miss_gepubliceerd`, want een andere selectie van een duel waarop is gepubliceerd is dezelfde mening en geen afgewezen kandidaat — §1a, §6d). En 25 duels hebben er helemaal geen: daar bleef de sterkste kandidaat onder de NEAR-ondergrens (6,0 pp op `LIGHT`, 3,0 pp op `FULL`), op één na — Gaziantep FK – Erzurumspor FK staat op `NONE` en heeft niets doorgerekend om af te wijzen. De ELF poort-8-rijen en de TWEE poort-9-rijen staan niet in deze tabel maar als eigen categorie (`underdog`, `doelpunten_onder`) in het schaduwlogboek, en de ene `lijstlengte`-rij (Chelsea – Tottenham, BTTS nee) net zo — die drie categorieën zijn drie aparte populaties en mogen nooit bij `edge` worden opgeteld (§1e, §1h, §5b).

## Wedstrijden

De 51 duels in het inzetvenster, op aftraptijd. De vijf gepubliceerde regels staan in het volledige format van §5; bij de andere 46 staat de reden in één regel, met de cijfers per poort in de tabel "Net niet" hierboven.

### Piast Gliwice – Cracovia · 12:15 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel (+6.87 pp, nodig 8.0)

### Eyüpspor – Kasımpaşa · 12:30 NL · Super Lig (TUR)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel (+3.62 pp, nodig 8.0)

### Aston Villa – Manchester City · 13:30 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — context spreekt de bet tegen — blessures: Aston Villa mist 33% van de selectiewaarde tegen 20% bij Manchester City — Johan Manzambi (injury, terug Doubtful), Modou Kéba Cissé (injury, terug Back in training), Aaron Wan-Bissaka (injury, terug Mid November 2026)

### Charlton Athletic – Norwich City · 13:30 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Portsmouth – Millwall · 13:30 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Millwall mist 55% van de selectiewaarde tegen 28% bij Portsmouth — Filip Marschall (injury, terug Doubtful), Taïryk Arconte (injury, terug Doubtful), Lukas Bornhøft Jensen (injury, terug Doubtful)

### Sheffield United – Derby County · 13:30 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — context spreekt de bet tegen — blessures: Derby County mist 54% van de selectiewaarde tegen 4% bij Sheffield United — Lewis Travis (injury, terug Doubtful), Sondre Klingen Langås (injury, terug Early January 2027), Max Johnston (injury, terug Early November 2026)

### Rayo Vallecano – Elche · 14:00 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Rayo Vallecano mist 46% van de selectiewaarde tegen 10% bij Elche — Randy Nteka (injury, terug Early November 2026), Andrei Rațiu (injury, terug Doubtful), Augusto Batalla (injury, terug Early January 2027)

### Korona Kielce – GKS Katowice · 14:45 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel

### Cagliari – Bologna · 15:00 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Bologna mist 28% van de selectiewaarde tegen 11% bij Cagliari — Emil Holm (injury, terug Late February 2027), Riccardo Orsolini (injury, terug Early November 2026), Roberto Piccoli (injury, terug Early November 2026)

### Como – Sassuolo · 15:00 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.0
- **Bet:** Over/Under — Under 3.5 — Odds: best **1.8232** (The Odds API (Matchbook, beurs: 1.84 bruto / 1.8232 na 2% commissie))
- **Implied prob:** 54.9%  •  **My prob:** 66.4%  (ruw 66.9%)
- **Edge:** +11.58 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.823 / 1.092 · splitsmethode 2.021 / 0.841 · Understat 2.088 / 0.861
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.823 thuis / 1.092 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.021 / 0.841 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 2.088 / 0.861, rollende xG over 8 duels {'home': [1.77, 0.9, 8], 'away': [1.54, 1.53, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 2 van 5 over 51 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 7.693. Ruwe kans 0.6686, ruwe edge 12.01 pp; xG-methode 11.77 pp, splitsmethode 12.97 pp, zwakste stand van het (shrink, rho)-grid 11.77 pp. shrink staat sinds 19 sep op 1.00 (§6e). ONDER-KANT: §6g meet dat P(Under) bij élk duel ruim twee procentpunt te hoog staat door een vormfout in score_grid (gemeten vandaag over 1515 doorgerekende duels: P(Under 3.0) voorspeld 64,0% tegen werkelijk 61,8%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,590 doelpunt per duel over 90 gevallen (z = +3,39), terwijl de Over-kant op -0,243 staat (z = -0,97 over 53 gevallen). Poort 9 (§1h) BINDT hier wél, want dit duel staat op FULL, en deze selectie haalt de verzwaarde lat van 10,0 pp ruim. Dat is de rem die er is; de oorzaak — keuze (a) van 11 oktober, de vormfout zelf repareren — staat nog open. Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je haar leest. 

### Gaziantep FK – Erzurumspor FK · 15:00 NL · Super Lig (TUR)
- **Data:** `NONE`
- **GEEN BET** — omrekening buiten het gemeten bereik (conversion_in_range) — data_tier NONE

### 1. FC Köln – Schalke 04 · 15:30 NL · Bundesliga (GER)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel (+10.64 pp, nodig 16.0)

### Augsburg – Union Berlin · 15:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — data conflicterend

### Mainz 05 – Werder Bremen · 15:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel

### Paderborn – Hamburger SV · 15:30 NL · Bundesliga (GER)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### RB Leipzig – Elversberg · 15:30 NL · Bundesliga (GER)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — rust: RB Leipzig had 3 dagen tegen 7 bij Elversberg

### Arsenal – Everton · 16:00 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel

### Blackburn Rovers – Wrexham · 16:00 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — edge niet robuust over het (shrink, rho)-grid

### Cardiff City – Birmingham City · 16:00 NL · Championship (ENG)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Coventry City – Fulham · 16:00 NL · Premier League (ENG)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Dundee United – Aberdeen · 16:00 NL · Scottish Premiership (SCO)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel (+4.67 pp, nodig 8.0)

### Falkirk – Kilmarnock · 16:00 NL · Scottish Premiership (SCO)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Falkirk mist 27% van de selectiewaarde tegen 6% bij Kilmarnock — Aodhan Doherty (injury, terug Late October 2026), Joseph Gardner (injury, terug Early November 2026), Ethan Laidlaw (injury, terug Late October 2026)

### Lincoln City – Burnley · 16:00 NL · Championship (ENG)
- **Data:** `LIGHT` · datarijkdom 5.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.9212** (The Odds API (Matchbook, beurs: 1.94 bruto / 1.9212 na 2% commissie))
- **Implied prob:** 52.0%  •  **My prob:** 64.9%  (ruw 65.3%)
- **Edge:** +12.82 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 1.579 / 1.494 · splitsmethode 2.010 / 3.200
- **Inputs:** Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen (§4, k=8); doelverwachting 1.579 thuis / 1.494 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.010 / 3.200 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 5 van 5 over 51 doorgerekende wedstrijden. BET op rangorde — onder de lat van 16.0 pp (§5b). selection_score 4.158. Ruwe kans 0.6528, ruwe edge 13.23 pp; xG-methode 7.25 pp, splitsmethode 37.15 pp, zwakste stand van het (shrink, rho)-grid 6.03 pp. shrink staat sinds 19 sep op 1.00 (§6e). OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de systematische fout eruit en niet de onzekerheid. bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel (§5b). 

### Preston North End – West Bromwich Albion · 16:00 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — context spreekt de bet tegen — blessures: Preston North End mist 41% van de selectiewaarde tegen 25% bij West Bromwich Albion — Liam Lindsay (injury, terug Doubtful), Harry Clarke (injury, terug Late November 2026), Liam Gibbs (injury, terug Early November 2026)

### Queens Park Rangers – Swansea City · 16:00 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Rangers – St. Johnstone · 16:00 NL · Scottish Premiership (SCO)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Royal Antwerp – Sporting Charleroi · 16:00 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel

### St. Mirren – Dundee FC · 16:00 NL · Scottish Premiership (SCO)
- **Data:** `FULL` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Stoke City – Bristol City · 16:00 NL · Championship (ENG)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — data conflicterend

### West Ham United – Southampton · 16:00 NL · Championship (ENG)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel (+11.69 pp, nodig 16.0)

### Wolverhampton Wanderers – Watford · 16:00 NL · Championship (ENG)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### Racing Santander – Espanyol · 16:15 NL · La Liga (ESP)
- **Data:** `LIGHT` · datarijkdom 6.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.7300** (The Odds API (1xBet))
- **Implied prob:** 57.8%  •  **My prob:** 70.6%  (ruw 71.1%)
- **Edge:** +12.84 pp  •  **Confidence:** Low
- **Doelverwachting:** xG-methode 1.701 / 1.759 · splitsmethode 2.408 / 2.508
- **Inputs:** Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen (§4, k=8); doelverwachting 1.701 thuis / 1.759 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 2.408 / 2.508 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 4 van 5 over 51 doorgerekende wedstrijden. BET op rangorde — onder de lat van 16.0 pp (§5b). selection_score 4.535. Ruwe kans 0.7109, ruwe edge 13.29 pp; xG-methode 9.36 pp, splitsmethode 29.0 pp, zwakste stand van het (shrink, rho)-grid 7.09 pp. shrink staat sinds 19 sep op 1.00 (§6e). OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de systematische fout eruit en niet de onzekerheid. bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel (§5b). 

### Estrela da Amadora – Casa Pia AC · 16:30 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — data conflicterend

### FC Utrecht – PEC Zwolle · 16:30 NL · Eredivisie (NED)
- **Data:** `FULL` · datarijkdom 6.0
- **GEEN BET** — context spreekt de bet tegen — blessures: FC Utrecht mist 47% van de selectiewaarde tegen 25% bij PEC Zwolle — Artem Stepanov (injury, terug Mid November 2026), Alonzo Engwanda (injury, terug Day to day), Kevin Paredes (injury, terug Day to day)

### Pogoń Szczecin – Radomiak Radom · 17:30 NL · Ekstraklasa (POL)
- **Data:** `FULL` · datarijkdom 5.5
- **GEEN BET** — edge onder drempel (+6.21 pp, nodig 8.0)

### Napoli – Roma · 18:00 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Samsunspor – Amed Sportif · 18:00 NL · Super Lig (TUR)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel

### OH Leuven – Lommel · 18:15 NL · Belgian Pro League (BEL)
- **Data:** `LIGHT` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel

### Borussia Dortmund – Eintracht Frankfurt · 18:30 NL · Bundesliga (GER)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Chelsea – Tottenham Hotspur · 18:30 NL · Premier League (ENG)
- **Data:** `FULL` · datarijkdom 6.0
- **GEKWALIFICEERD, NIET GEPUBLICEERD** — BTTS — Beide ploegen scoren — nee @ 2.6856, edge +8.38 pp, selection_score 3.821, rang 4 op de dagranglijst. alle negen poorten open en +8.38 pp boven de drempel, maar rang 4 en niet in de lijst van 5 regels; laagste gepubliceerde selection_score 4.158
- **Doelverwachting:** xG-methode 1.765 / 0.992 · splitsmethode 1.360 / 1.631

### Valencia – Villarreal · 18:30 NL · La Liga (ESP)
- **Data:** `FULL` · datarijkdom 8.0
- **GEEN BET** — edge onder drempel

### Willem II – Cambuur · 18:45 NL · Eredivisie (NED)
- **Data:** `LIGHT` · datarijkdom 6.0
- **GEEN BET** — edge onder drempel

### Alverca – Arouca · 19:00 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 7.0
- **Bet:** Over/Under — Over 2.5 — Odds: best **1.9212** (The Odds API (Matchbook, beurs: 1.94 bruto / 1.9212 na 2% commissie))
- **Implied prob:** 52.0%  •  **My prob:** 60.8%  (ruw 61.2%)
- **Edge:** +8.74 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.968 / 1.219 · splitsmethode 1.568 / 1.487
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.968 thuis / 1.219 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 1.568 / 1.487 · Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 3 van 5 over 51 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 5.313. Ruwe kans 0.6116, ruwe edge 9.11 pp; xG-methode 9.68 pp, splitsmethode 6.86 pp, zwakste stand van het (shrink, rho)-grid 8.36 pp. shrink staat sinds 19 sep op 1.00 (§6e). 

### Wisła Kraków – Raków Częstochowa · 20:15 NL · Ekstraklasa (POL)
- **Data:** `LIGHT` · datarijkdom 5.0
- **GEEN BET** — edge onder drempel (+11.41 pp, nodig 16.0)

### Lazio – Parma · 20:45 NL · Serie A (ITA)
- **Data:** `FULL` · datarijkdom 6.0
- **Bet:** Over/Under — Under 2.5 — Odds: best **2.0400** (The Odds API (Unibet (SE)))
- **Implied prob:** 49.0%  •  **My prob:** 63.1%  (ruw 63.5%)
- **Edge:** +14.13 pp  •  **Confidence:** Medium
- **Doelverwachting:** xG-methode 1.488 / 0.662 · splitsmethode 1.364 / 0.801 · Understat 1.436 / 0.803
- **Inputs:** Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, k=8); doelverwachting 1.488 thuis / 0.662 uit · Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d multiplicatief en op het competitiegemiddelde genormaliseerd); doelverwachting 1.364 / 0.801 · Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): doelverwachting 1.436 / 0.803, rollende xG over 8 duels {'home': [1.22, 1.1, 8], 'away': [0.79, 1.67, 8]}
- **Onderbouwing:** Gepubliceerd op rangorde (§5b): plek 1 van 5 over 51 doorgerekende wedstrijden. BET — en haalt ook de lat van 8.0 pp. selection_score 8.923. Ruwe kans 0.6355, ruwe edge 14.53 pp; xG-methode 14.61 pp, splitsmethode 14.19 pp, zwakste stand van het (shrink, rho)-grid 10.51 pp. shrink staat sinds 19 sep op 1.00 (§6e). ONDER-KANT: §6g meet dat P(Under) bij élk duel ruim twee procentpunt te hoog staat door een vormfout in score_grid (gemeten vandaag over 1515 doorgerekende duels: P(Under 3.0) voorspeld 64,0% tegen werkelijk 61,8%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,590 doelpunt per duel over 90 gevallen (z = +3,39), terwijl de Over-kant op -0,243 staat (z = -0,97 over 53 gevallen). Poort 9 (§1h) BINDT hier wél, want dit duel staat op FULL, en deze selectie haalt de verzwaarde lat van 10,0 pp ruim. Dat is de rem die er is; de oorzaak — keuze (a) van 11 oktober, de vormfout zelf repareren — staat nog open. Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je haar leest. 

### Lens – Paris FC · 20:45 NL · Ligue 1 (FRA)
- **Data:** `FULL` · datarijkdom 6.5
- **GEEN BET** — context spreekt de bet tegen — rust: Lens had 3 dagen tegen 6 bij Paris FC

### RAAL La Louvière – Zulte Waregem · 20:45 NL · Belgian Pro League (BEL)
- **Data:** `FULL` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel

### Westerlo – SK Beveren · 20:45 NL · Belgian Pro League (BEL)
- **Data:** `LIGHT` · datarijkdom 4.5
- **GEEN BET** — edge onder drempel

### ADO Den Haag – SC Heerenveen · 21:00 NL · Eredivisie (NED)
- **Data:** `LIGHT` · datarijkdom 7.0
- **GEEN BET** — data conflicterend

### Atlético Madrid – Deportivo A Coruña · 21:00 NL · La Liga (ESP)
- **Data:** `LIGHT` · datarijkdom 6.5
- **GEEN BET** — edge onder drempel

### Gil Vicente – FC Porto · 21:30 NL · Primeira Liga (POR)
- **Data:** `FULL` · datarijkdom 7.0
- **GEEN BET** — edge onder drempel (+4.08 pp, nodig 8.0)
