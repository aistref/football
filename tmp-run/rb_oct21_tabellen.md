<!--DEK-->
| Competitie | Status | Toelichting |
|---|---|---|
| English League One (ENG) | `GEANALYSEERD` | 1 duel (Reading – Leyton Orient), 21:00 NL. xG bij Fotmob en beide ploegen in de stand van 2025/2026, dus `FULL` zonder omrekening. Nul regels: de twee methodes wijzen hier lijnrecht tegengesteld. (1 duels) |
| MLS (USA) | `GEANALYSEERD` | 1 duel (FC Cincinnati – DC United), 01:00 NL in de nacht naar 22 oktober — de nachtband waarvoor `runwindow.py` bestaat. xG bij Fotmob, `FULL`. Hier komt de enige regel van de run uit. (1 duels) |
| Czech First League (CZE) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Greek Super League (GRE) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Eliteserien (NOR) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Allsvenskan (SWE) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Croatian HNL (CRO) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Hungarian NB I (HUN) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Romanian SuperLiga (ROU) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Segunda División (ESP) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Serie B (ITA) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| 2. Bundesliga (GER) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Swiss Super League (SUI) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Austrian Bundesliga (AUT) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Keuken Kampioen Divisie (NED) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| English League Two (ENG) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
| Série A (BRA) | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |
<!--BEV-->
| Competitie | Fotmob | BetExplorer | Eens |
|---|---|---|---|
| 2. Bundesliga (GER) | 0 | 0 | ja |
| Allsvenskan (SWE) | 0 | 0 | ja |
| Austrian Bundesliga (AUT) | 0 | 0 | ja |
| Croatian HNL (CRO) | 0 | 0 | ja |
| Czech First League (CZE) | 0 | 0 | ja |
| Eliteserien (NOR) | 0 | 0 | ja |
| English League One (ENG) | 1 | 1 | ja |
| English League Two (ENG) | 0 | 0 | ja |
| Greek Super League (GRE) | 0 | 0 | ja |
| Hungarian NB I (HUN) | 0 | 0 | ja |
| Keuken Kampioen Divisie (NED) | 0 | 0 | ja |
| MLS (USA) | 1 | 1 | ja |
| Romanian SuperLiga (ROU) | 0 | 0 | ja |
| Segunda División (ESP) | 0 | 0 | ja |
| Serie B (ITA) | 0 | 0 | ja |
| Swiss Super League (SUI) | 0 | 0 | ja |
| Série A (BRA) | 0 | 0 | ja |
<!--TOP-->
| # | Bet | Prob | Edge | Score | Risico | Waarom deze |
|---|---|---|---|---|---|---|
| 1 | FC Cincinnati – DC United · **Over/Under — Under 3.5** @2.2348 (Matchbook, beurs: 2.26 bruto / 2.2348 na 2% commissie) · 01:00 NL · `FULL` | 57.8% | **+13.08 pp** (lat 8.0 — **gehaald**) | 7.564 | High | De enige van 29 doorgerekende selecties die alle negen poorten haalt, en hij haalt zowel de lat van 8,0 als de verzwaarde lat van 10,0 die poort 9 op een FULL-Under legt. `bet_beide` = TRUE (ruw +12,59 pp). Risicoklasse **High** en niet Medium, en dat is een eigen oordeel bovenop de score: de frequentietelling en Pinnacle spreken deze bet beide tegen (zie de twee paragrafen hieronder). De eerstvolgende selectie — Under 3,75 op hetzelfde duel, score 7,513 — is dezelfde mening in een naburige markt en geen tweede bevinding; de beste selectie van het ándere duel staat op +2,14 pp. |
<!--RUW-->
| # | Wedstrijd | Selectie | Kans | Edge (ruw) | Score | Viel af op |
|---|---|---|---|---|---|---|
| 1 | FC Cincinnati – DC United | Under 3.5 @2.23 | 57.3% | +12.59 pp | 7.218 | — |
| 2 | Reading – Leyton Orient | Reading -1 @1.94 | 53.3% | +1.73 pp | 0.922 | tweede_methode |
<!--NN-->
| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
<!--NIV-->
| Competitie | Route | Thuis | Uit | Basis | Reden |
|---|---|---|---|---|---|
| English League One (ENG) | `vorig+uplift` | 1.576 | 1.229 | 1.389 | lopend seizoen op 12 speeldagen van 46 (26%) — onder 50%, dus niveau uit vorig seizoen met de vroeg-seizoenscorrectie (1.0664) |
| MLS (USA) | `lopend` | 1.838 | 1.411 | 1.545 | lopend seizoen op 31 van 34 speeldagen (91%) — niveau rechtstreeks uit het lopende seizoen; de vroeg-seizoenscorrectie (1.0664) is NIET toegepast, want bij deze stand meet lopend/vorig (1.0446) een echt niveauverschil en geen tijdseffect |