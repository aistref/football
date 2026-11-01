## Afwikkeling vorige picks

Stage 0 heeft **tien picks** en **vierenzeventig schaduwrijen** van 31 oktober afgewikkeld — de grootste afwikkeling tot nu toe, en een gevolg van de volle zaterdag ervoor en niet van een stapel die was blijven liggen: er stond geen rij van vóór 31 oktober open. Alle 84 rijen zijn **competitiewedstrijden**, dus er is geen verlenging of strafschoppenreeks en de eindstand ís de stand na 90 minuten (§6d). Dat is nagetrokken en niet aangenomen: de negen MLS-duels van 31 oktober zijn de laatste reguliere speelronde en geen play-offduel.

**Eén rij blijft correct open:** Colorado Rapids – Chicago Fire FC trapte om 01:30 UTC vanochtend af en de bron meldt hem na 2,1 uur nog niet afgelopen. Die gaat naar de volgende run.

| Pick | Uitslag | Resultaat | Verwacht (λ) | Werkelijk | Klopte de redenering? |
|---|---|---|---|---|---|
| Bradford City – Huddersfield Town · BTTS nee @2,22 | 0-3 | **gewonnen** | 2.19 | 3 | ja — Bradford kreeg er 1,0 toegeschreven en maakte 0 |
| Modena – Mantova · BTTS nee @2,2936 | 1-1 | **verloren** | 2.66 | 2 | nee — Mantova kreeg 0,8 en maakte 1; totaal wél goed |
| Bayer Leverkusen – VfB Stuttgart · Over 3.5 @1,87 | 2-4 | **gewonnen** | 4.36 | 6 | half — goede kant, model 1,6 doelpunt te laag |
| Middlesbrough – Charlton Athletic · Under 3.5 @1,87 | 3-0 | **gewonnen** | 3.03 | 3 | **ja, exact** — 3,0 verwacht, 3 gevallen |
| AFC Bournemouth – Leeds United · Over 2.5 @1,94 | 2-0 | **verloren** | 3.21 | 2 | nee — model 1,2 doelpunt te hoog |
| Moreirense – Estrela da Amadora · Over 2.5 @2,1368 | 2-1 | **gewonnen** | 2.99 | 3 | **ja, exact** — 3,0 verwacht, 3 gevallen |
| Kifisia FC – Olympiacos · Under 2.5 @1,93 | 2-3 | **verloren** | 2.23 | 5 | nee — model 2,8 doelpunt te laag, de grootste misser van de dag |
| Columbus Crew – DC United · Under 3.5 @1,87 | 3-0 | **gewonnen** | 2.83 | 3 | **ja** — 2,8 verwacht, 3 gevallen |
| Anderlecht – Westerlo · Under 3.5 @1,7742 | 4-1 | **verloren** | 2.96 | 5 | nee — model 2,0 doelpunt te laag |
| San Jose Earthquakes – Real Salt Lake · 1X2 thuis @2,3916 | 2-1 | **gewonnen** | 3.38 | 3 | ja — 3,4 verwacht, 3 gevallen, juiste winnaar |
| **totaal over 10 duels** | | **6 gewonnen, 4 verloren** | **29.83** | **35** | **+0.52 doelpunt per duel** |

**De reflectie van §3 Stage 0, vier vragen:**

1. **Klopte de redenering, of alleen de uitkomst?** Bij vier van de zes winnaars klopte ze tot op de halve goal: Middlesbrough – Charlton 3–0 bij 3,03 verwacht, Moreirense – Estrela 2–1 bij 2,99, Columbus – DC United 3–0 bij 2,84 en San Jose – Real Salt Lake 2–1 bij 3,38. Dat zijn winsten op de juiste redenering. Bij Leverkusen – Stuttgart (2–4 bij 4,36 verwacht) was de kant goed en de hoogte niet. Omgekeerd was Modena – Mantova een verlies waarbij het totaal klopte (2 tegen 2,66) en alleen de nul niet kwam — verloren, maar niet verkeerd ingeschat.
2. **Deden de poorten hun werk, in dít geval?** Op zaterdag niet. De vierenzeventig afgewezen kandidaten stonden samen op **+12,97u over 70 beslechte rijen = +18,5%**, met `tweede_methode` op +61,6% (13 van 18 goed) en `edge` op +35,4% (14 van 24). Alleen `robuustheid` (0 van 2), `doelpunten_onder` (1 van 4) en `underdog` (8 van 19) deden wat ze moeten doen. Dat is één dag en achttien gevallen; over de hele looptijd bespaart `tweede_methode` nog steeds geld (−3,0% over 237).
3. **Zat er een patroon in?** Ja, en het is het bekende. Over de tien duels vielen er **35 doelpunten tegen 29.8 verwachte** — een halve goal per wedstrijd te veel. Drie van de vier verliezers waren doelpuntenmarkten die aan de verkeerde kant uitliepen, en **twee daarvan waren Unders die overschoten** (Kifisia 5 tegen 2,2 verwacht; Anderlecht 5 tegen 3,0). Dat is precies de richting die §6g meet.
4. **En wat betekent dit niet?** Eén dag is geen reeks. De Under-reeks waar dit in past staat nu op **+0,668 doelpunt per duel over 115 gevallen (z = +4,32)** — dát is de meting, en de twee van gisteren zijn er twee van de 115. Er is op grond van deze dag geen drempel, gewicht of poort verzet, en poort 9 staat onveranderd op `UNDER_EXTRA` = 2,0 pp.

## Stand van het logboek

`recalibrate.load_fit().fitted_through` = **2026-10-31**, de vorige rundag — zoals §6b-5c eist. De 285 waarnemingen die nog open stonden zijn vóór het lezen van de fit afgewikkeld (`calibration.py settle`), en `ctxlog.py settle` wikkelde 109 wedstrijden af. Fit: `a=0,9943`, `b=-0,0037` op **6606** afgerekende gevallen; het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. De correctie is daarmee vrijwel de identiteit — ze verlaagt een kans van 50% met 0,1 pp en een van 80% met 0,2 pp.

Uitvoer van `python3 scripts/recalibrate.py show`:

```
herijking op 6606 afgerekende gevallen t/m 2026-10-31: a=0.994, b=-0.004 — het model zei gemiddeld 33.3%, werkelijk 33.3% (+0.0 pp)

Wat de correctie met een kans doet:
       ruw   herijkt   verschil
     30.0%     30.0%      +0.0 pp
     40.0%     40.0%      -0.0 pp
     50.0%     49.9%      -0.1 pp
     55.0%     54.9%      -0.1 pp
     60.0%     59.9%      -0.1 pp
     70.0%     69.8%      -0.2 pp
     80.0%     79.8%      -0.2 pp
```

Uitvoer van `python3 scripts/ledger.py stats`:

```

ALLE PICKS
  picks            500  (0 open, 500 afgewikkeld, 61 void)
  hit rate         199/439 = 45.3%
  ROI (1u flat)    -34.99u over 439 bets = -8.0%
  waarvan 10 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.18   gem. geclaimde edge +10.1 pp
  Brier eigen      0.2598
  Brier markt      0.2398   -> markt beter (verschil -0.0199)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 260.1 winnaars, werkelijk 199 (-61.1)

data_tier = FULL
  picks            390  (0 open, 390 afgewikkeld, 54 void)
  hit rate         157/336 = 46.7%
  ROI (1u flat)    -20.73u over 336 bets = -6.2%
  waarvan 9 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.13   gem. geclaimde edge +9.3 pp
  Brier eigen      0.2547
  Brier markt      0.2397   -> markt beter (verschil -0.0151)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 198.4 winnaars, werkelijk 157 (-41.4)

data_tier = LIGHT
  picks            110  (0 open, 110 afgewikkeld, 7 void)
  hit rate         42/103 = 40.8%
  ROI (1u flat)    -14.26u over 103 bets = -13.8%
  waarvan 1 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.35   gem. geclaimde edge +12.7 pp
  Brier eigen      0.2761
  Brier markt      0.2404   -> markt beter (verschil -0.0358)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 61.6 winnaars, werkelijk 42 (-19.6)

confidence = High
  picks            87  (0 open, 87 afgewikkeld, 17 void)
  hit rate         34/70 = 48.6%
  ROI (1u flat)    -3.97u over 70 bets = -5.7%
  waarvan 1 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.22   gem. geclaimde edge +11.1 pp
  Brier eigen      0.2437
  Brier markt      0.2271   -> markt beter (verschil -0.0167)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 42.0 winnaars, werkelijk 34 (-8.0)

confidence = Medium
  picks            260  (0 open, 260 afgewikkeld, 22 void)
  hit rate         112/238 = 47.1%
  ROI (1u flat)    -12.98u over 238 bets = -5.5%
  waarvan 7 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.06   gem. geclaimde edge +9.4 pp
  Brier eigen      0.2612
  Brier markt      0.2438   -> markt beter (verschil -0.0174)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 143.0 winnaars, werkelijk 112 (-31.0)

confidence = Low
  picks            153  (0 open, 153 afgewikkeld, 22 void)
  hit rate         53/131 = 40.5%
  ROI (1u flat)    -18.04u over 131 bets = -13.8%
  waarvan 2 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.38   gem. geclaimde edge +10.8 pp
  Brier eigen      0.2657
  Brier markt      0.2394   -> markt beter (verschil -0.0263)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 75.0 winnaars, werkelijk 53 (-22.0)

alleen topselectie
  picks            368  (0 open, 368 afgewikkeld, 27 void)
  hit rate         158/341 = 46.3%
  ROI (1u flat)    -28.84u over 341 bets = -8.5%
  waarvan 8 halve uitkomst(en) op een kwartlijn, geboekt op hun werkelijke inzetdeel
  gem. odds        2.10   gem. geclaimde edge +10.9 pp
  Brier eigen      0.2627
  Brier markt      0.2407   -> markt beter (verschil -0.0220)
  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:
  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.
  kalibratie       verwacht 208.9 winnaars, werkelijk 158 (-50.9)
```

Uitvoer van `python3 scripts/shadow.py stats`:

```

ALLE AFGEWEZEN KANDIDATEN
  kandidaten       1517  (1 nog niet afgewikkeld)
  hit rate         644/1458 = 44.2%
  ROI (1u flat)    -80.86u over 1458 = -5.5%
  gem. odds        2.57   gem. geclaimde edge +7.2 pp
  kalibratie       verwacht 763.3 winnaars, werkelijk 644 (-119.3)
  >> Deze afwijzingen bespaarden 80.86u. De poort doet dan zijn werk.

viel af op: context
  kandidaten       107  (0 nog niet afgewikkeld)
  hit rate         36/106 = 34.0%
  ROI (1u flat)    -26.01u over 106 = -24.5%
  gem. odds        2.51   gem. geclaimde edge +9.5 pp
  kalibratie       verwacht 56.0 winnaars, werkelijk 36 (-20.0)
  >> Deze afwijzingen bespaarden 26.01u. De poort doet dan zijn werk.

viel af op: data
  kandidaten       57  (0 nog niet afgewikkeld)
  hit rate         22/55 = 40.0%
  ROI (1u flat)    -4.65u over 55 = -8.5%
  gem. odds        3.17   gem. geclaimde edge +15.5 pp
  kalibratie       verwacht 29.2 winnaars, werkelijk 22 (-7.2)
  >> Deze afwijzingen bespaarden 4.65u. De poort doet dan zijn werk.

viel af op: doelpunten_onder
  kandidaten       29  (0 nog niet afgewikkeld)
  hit rate         12/29 = 41.4%
  ROI (1u flat)    -6.38u over 29 = -22.0%
  gem. odds        1.98   gem. geclaimde edge +8.8 pp
  kalibratie       verwacht 17.6 winnaars, werkelijk 12 (-5.6)
  >> Deze afwijzingen bespaarden 6.38u. De poort doet dan zijn werk.

viel af op: edge
  kandidaten       588  (0 nog niet afgewikkeld)
  hit rate         259/564 = 45.9%
  ROI (1u flat)    +10.52u over 564 = +1.9%
  gem. odds        2.45   gem. geclaimde edge +5.3 pp
  kalibratie       verwacht 284.6 winnaars, werkelijk 259 (-25.6)
  >> Deze afwijzingen kostten +10.52u. Waren het er veel en blijft dit staan,
     dan is de poort te streng afgesteld.

viel af op: herijking
  kandidaten       68  (0 nog niet afgewikkeld)
  hit rate         30/59 = 50.8%
  ROI (1u flat)    -1.96u over 59 = -3.3%
  gem. odds        1.93   gem. geclaimde edge +10.4 pp
  kalibratie       verwacht 37.1 winnaars, werkelijk 30 (-7.1)
  >> Deze afwijzingen bespaarden 1.96u. De poort doet dan zijn werk.

viel af op: herijking_omgekeerd
  kandidaten       3  (0 nog niet afgewikkeld)
  hit rate         0/3 = 0.0%
  ROI (1u flat)    -3.00u over 3 = -100.0%
  gem. odds        2.18   gem. geclaimde edge +10.8 pp
  kalibratie       verwacht 1.7 winnaars, werkelijk 0 (-1.7)
  >> Deze afwijzingen bespaarden 3.00u. De poort doet dan zijn werk.

viel af op: lijstlengte
  kandidaten       20  (0 nog niet afgewikkeld)
  hit rate         10/20 = 50.0%
  ROI (1u flat)    +4.83u over 20 = +24.2%
  gem. odds        2.48   gem. geclaimde edge +12.7 pp
  kalibratie       verwacht 11.2 winnaars, werkelijk 10 (-1.2)
  >> Deze afwijzingen kostten +4.83u. Waren het er veel en blijft dit staan,
     dan is de poort te streng afgesteld.

viel af op: odds
  kandidaten       38  (0 nog niet afgewikkeld)
  hit rate         3/38 = 7.9%
  ROI (1u flat)    -21.98u over 38 = -57.8%
  gem. odds        9.45   gem. geclaimde edge +5.7 pp
  kalibratie       verwacht 7.3 winnaars, werkelijk 3 (-4.3)
  >> Deze afwijzingen bespaarden 21.98u. De poort doet dan zijn werk.

viel af op: robuustheid
  kandidaten       60  (0 nog niet afgewikkeld)
  hit rate         23/59 = 39.0%
  ROI (1u flat)    -10.44u over 59 = -17.7%
  gem. odds        2.22   gem. geclaimde edge +6.5 pp
  kalibratie       verwacht 31.9 winnaars, werkelijk 23 (-8.9)
  >> Deze afwijzingen bespaarden 10.44u. De poort doet dan zijn werk.

viel af op: tweede_methode
  kandidaten       246  (0 nog niet afgewikkeld)
  hit rate         108/237 = 45.6%
  ROI (1u flat)    -7.22u over 237 = -3.0%
  gem. odds        2.35   gem. geclaimde edge +5.9 pp
  kalibratie       verwacht 122.4 winnaars, werkelijk 108 (-14.4)
  >> Deze afwijzingen bespaarden 7.22u. De poort doet dan zijn werk.

viel af op: underdog
  kandidaten       284  (1 nog niet afgewikkeld)
  hit rate         134/271 = 49.4%
  ROI (1u flat)    -13.06u over 271 = -4.8%
  gem. odds        2.27   gem. geclaimde edge +8.4 pp
  kalibratie       verwacht 153.5 winnaars, werkelijk 134 (-19.5)
  >> Deze afwijzingen bespaarden 13.06u. De poort doet dan zijn werk.

viel af op: underdog_ruw
  kandidaten       17  (0 nog niet afgewikkeld)
  hit rate         7/17 = 41.2%
  ROI (1u flat)    -1.50u over 17 = -8.8%
  gem. odds        2.25   gem. geclaimde edge +15.0 pp
  kalibratie       verwacht 10.7 winnaars, werkelijk 7 (-3.7)
  >> Deze afwijzingen bespaarden 1.50u. De poort doet dan zijn werk.

APART GEHOUDEN: kandidaten met maar één methode (`--include-single`)
  kandidaten       73  (0 nog niet afgewikkeld)
  hit rate         13/73 = 17.8%
  ROI (1u flat)    -36.28u over 73 = -49.7%
  gem. odds        6.96   gem. geclaimde edge +5.3 pp
  kalibratie       verwacht 22.2 winnaars, werkelijk 13 (-9.2)
  >> Deze afwijzingen bespaarden 36.28u. De poort doet dan zijn werk.
  Deze staan buiten de cijfers hierboven: hun my_prob komt uit één schatter in
  plaats van het gemiddelde van twee, dus ze zijn niet op dezelfde schaal.

Lees dit naast `python3 scripts/ledger.py stats`: dat is wat er wél doorheen kwam,
dit is wat er is tegengehouden. Het verschil tussen die twee is wat de poorten doen.
```

Uitvoer van `python3 scripts/calibration.py stats` (§6e):

```
KALIBRATIE — 2317 wedstrijden, 6951 uitkomsten, 70 dag(en) van 2026-08-22 t/m 2026-11-01
Afwijking van het model t.o.v. de de-vigde marktkans, in procentpunten.
Positief = het model geeft die uitkomst meer kans dan de markt.

ALLE WAARNEMINGEN
  methode                                 longshot    middenmoot      favoriet
  ----------------------------------------------------------------------------
  xG-methode (standaard shrink)             +1.77        -0.05        -3.49
  xG-methode (shrink 1.0)                   +0.90        -0.03        -1.76
  xG-methode (shrink 0.8, oude standaard)        +2.54        -0.00        -5.48
  splitsmethode                             +1.39        +0.03        -2.96
  xG-methode op Understat (2e xG-model)        +3.11        -0.11        -6.02
  gemiddelde van beide (= my_prob)          +1.57        -0.01        -3.22
  aantal waarnemingen                         2188          3701          1062

  Aandeel van `shrink=0.8` op longshots: +1.65 pp van de +2.55 pp die de xG-methode daar afwijkt (1904 waarnemingen).
  De rest is niet aan shrink toe te schrijven; vergelijk de regels hierboven.
  Sinds 2026-09-19 staat de standaard op 1.00 (§0) en is 0.8 de vergelijkingsarm, niet andersom.

PER DAG (gemiddelde van beide methodes, longshots <25%):
  2026-08-22    +4.19 pp   (21 waarnemingen)
  2026-08-23    +4.04 pp   (44 waarnemingen)
  2026-08-24    +2.13 pp   (14 waarnemingen)
  2026-08-25    -4.23 pp   (13 waarnemingen)
  2026-08-26    +5.79 pp   (8 waarnemingen)
  2026-08-27    -0.12 pp   (3 waarnemingen)
  2026-08-28    +1.92 pp   (21 waarnemingen)
  2026-08-29    +1.34 pp   (45 waarnemingen)
  2026-08-30    +1.88 pp   (59 waarnemingen)
  2026-08-31    +4.13 pp   (30 waarnemingen)
  2026-09-01    +4.82 pp   (16 waarnemingen)
  2026-09-02    +1.75 pp   (15 waarnemingen)
  2026-09-03    +2.84 pp   (13 waarnemingen)
  2026-09-04    +2.06 pp   (32 waarnemingen)
  2026-09-05    +1.23 pp   (39 waarnemingen)
  2026-09-06    +1.19 pp   (51 waarnemingen)
  2026-09-07    +2.49 pp   (12 waarnemingen)
  2026-09-08    -2.19 pp   (9 waarnemingen)
  2026-09-09    +1.13 pp   (19 waarnemingen)
  2026-09-10    -0.41 pp   (9 waarnemingen)
  2026-09-11    +2.44 pp   (26 waarnemingen)
  2026-09-12    +1.75 pp   (66 waarnemingen)
  2026-09-13    +2.90 pp   (64 waarnemingen)
  2026-09-14    +2.24 pp   (24 waarnemingen)
  2026-09-15    +1.66 pp   (21 waarnemingen)
  2026-09-16    +1.45 pp   (14 waarnemingen)
  2026-09-17    +3.80 pp   (11 waarnemingen)
  2026-09-18    -0.21 pp   (28 waarnemingen)
  2026-09-19    +1.31 pp   (72 waarnemingen)
  2026-09-20    +0.55 pp   (83 waarnemingen)
  2026-09-21    -6.15 pp   (1 waarnemingen)
  2026-09-23    -3.37 pp   (1 waarnemingen)
  2026-09-24    +2.62 pp   (17 waarnemingen)
  2026-09-25    +1.89 pp   (28 waarnemingen)
  2026-09-26    +2.68 pp   (39 waarnemingen)
  2026-09-27    +2.97 pp   (16 waarnemingen)
  2026-09-28    +0.88 pp   (5 waarnemingen)
  2026-09-29    +2.70 pp   (28 waarnemingen)
  2026-09-30    -2.27 pp   (3 waarnemingen)
  2026-10-01    +3.12 pp   (10 waarnemingen)
  2026-10-02    +4.72 pp   (14 waarnemingen)
  2026-10-03    +2.48 pp   (31 waarnemingen)
  2026-10-04    +1.74 pp   (13 waarnemingen)
  2026-10-05    +5.48 pp   (12 waarnemingen)
  2026-10-06    +2.28 pp   (22 waarnemingen)
  2026-10-07    +1.71 pp   (2 waarnemingen)
  2026-10-08    -0.55 pp   (3 waarnemingen)
  2026-10-09    +0.05 pp   (31 waarnemingen)
  2026-10-10    +0.75 pp   (93 waarnemingen)
  2026-10-11    +1.19 pp   (68 waarnemingen)
  2026-10-12    +1.93 pp   (12 waarnemingen)
  2026-10-13    +1.58 pp   (15 waarnemingen)
  2026-10-14    +0.22 pp   (26 waarnemingen)
  2026-10-15    +2.06 pp   (23 waarnemingen)
  2026-10-16    +1.71 pp   (20 waarnemingen)
  2026-10-17    +0.63 pp   (86 waarnemingen)
  2026-10-18    +0.02 pp   (70 waarnemingen)
  2026-10-19    +1.71 pp   (10 waarnemingen)
  2026-10-20    +0.92 pp   (25 waarnemingen)
  2026-10-21    -0.29 pp   (15 waarnemingen)
  2026-10-22    +1.63 pp   (26 waarnemingen)
  2026-10-23    -0.97 pp   (21 waarnemingen)
  2026-10-24    +2.28 pp   (102 waarnemingen)
  2026-10-25    +1.18 pp   (81 waarnemingen)
  2026-10-26    +3.17 pp   (15 waarnemingen)
  2026-10-27    -0.88 pp   (17 waarnemingen)
  2026-10-28    +1.35 pp   (46 waarnemingen)
  2026-10-30    +0.12 pp   (22 waarnemingen)
  2026-10-31    +1.52 pp   (94 waarnemingen)
  2026-11-01    +1.70 pp   (41 waarnemingen)

LEESWIJZER. 2188 waarnemingen in de longshotbak. Onder de ~150 (ruwweg vijf volle 
rundagen) is een verschil van een paar procentpunt nog ruis. Pas geen drempel en geen 
rekenstap aan op grond van één of twee dagen — zie §6d van _shared-rules.md.
De marge is proportioneel weggedeeld, wat longshotkansen van de markt overschat; een 
gemeten positieve afwijking op longshots is daarom eerder een ondergrens.
```

Uitvoer van `python3 scripts/ctxlog.py stats` (§1c):

```
CONTEXTLOGBOEK — 1871 afgewikkelde wedstrijden, 39 nog open
  thuiswinst werkelijk 44.8%
  beschikbaarheidsverschil: gemiddelde +0.002, spreiding 0.164

  fout van het MODEL tegen het beschikbaarheidsverschil (n=1628):
     r = -0.048   t = -1.93   helling -13.7 pp per eenheid
  fout van de MARKT tegen het beschikbaarheidsverschil (n=1616):
     r = -0.041   t = -1.66   helling -11.5 pp per eenheid

  Met 1871 wedstrijden is alleen een effect vanaf ~13 pp per eenheid aantoonbaar (t=2).
  Lees dit als §6d: kijk naar de richting over weken, niet naar het getal van vandaag,
  en stel op grond hiervan pas iets bij als het teken consistent is én groot genoeg.
```

Uitvoer van `python3 scripts/margins.py stats` (§6f):

```
(68 wedstrijd(en) zonder bruikbare eindstand overgeslagen)

MARGEKALIBRATIE — 1870 wedstrijden, 61 dag(en) van 2026-08-25 t/m 2026-10-31
Voorspeld = het scoregrid van `model.score_grid` op de opgeslagen lambdas.
`<--` betekent: meer dan twee standaardfouten van de voorspelling af.

DOELSALDO (beide kanten samengenomen)
  wint met 3 of meer                 voorspeld  17.7%   werkelijk  19.1%    +1.4 pp
  wint met 4 of meer                 voorspeld   6.9%   werkelijk   7.9%    +1.0 pp
  wint met 5 of meer                 voorspeld   2.4%   werkelijk   2.7%    +0.3 pp
  gelijkspel                         voorspeld  23.8%   werkelijk  22.7%    -1.1 pp

TOTAAL AANTAL DOELPUNTEN (de controle: hier hoort het wél te kloppen)
  0 of 1 doelpunt                    voorspeld  20.0%   werkelijk  18.9%    -1.1 pp
  4 of meer                          voorspeld  36.0%   werkelijk  37.6%    +1.6 pp
  6 of meer                          voorspeld   9.5%   werkelijk   8.6%    -0.9 pp

DUELS MET EEN DUIDELIJKE FAVORIET (lambda-ratio >= 1.8, n=478)
  favoriet wint                      voorspeld  65.9%   werkelijk  66.7%    +0.8 pp
  favoriet wint met 2 of meer        voorspeld  43.6%   werkelijk  43.1%    -0.5 pp
  favoriet wint met 3 of meer        voorspeld  24.3%   werkelijk  24.3%    -0.0 pp
  favoriet wint met 4 of meer        voorspeld  11.7%   werkelijk  14.2%    +2.5 pp
  underdog wint of speelt gelijk     voorspeld  34.1%   werkelijk  33.3%    -0.8 pp

LEESWIJZER. Staat hier een positief verschil bij 'favoriet wint met 3 of meer', dan
onderschat het scoregrid hoe scheef een duel met een duidelijke favoriet afloopt, en
ziet de routine daardoor waarde in een handicap op de underdog die er niet is. Lambdas
van vóór 2026-09-19 komen van `shrink = 0.80`; draai `--since 2026-09-20` voor een
meting op de nieuwe instelling, en lees die pas vanaf ~150 duels met een favoriet.
```

Uitvoer van `python3 scripts/margins.py stats --since 2026-09-20` (§6f):

```
(65 wedstrijd(en) zonder bruikbare eindstand overgeslagen)

MARGEKALIBRATIE — 1067 wedstrijden, 35 dag(en) van 2026-09-20 t/m 2026-10-31
Voorspeld = het scoregrid van `model.score_grid` op de opgeslagen lambdas.
`<--` betekent: meer dan twee standaardfouten van de voorspelling af.

DOELSALDO (beide kanten samengenomen)
  wint met 3 of meer                 voorspeld  17.9%   werkelijk  19.4%    +1.5 pp
  wint met 4 of meer                 voorspeld   7.0%   werkelijk   7.2%    +0.2 pp
  wint met 5 of meer                 voorspeld   2.5%   werkelijk   2.5%    +0.0 pp
  gelijkspel                         voorspeld  23.7%   werkelijk  20.8%    -2.9 pp  <--

TOTAAL AANTAL DOELPUNTEN (de controle: hier hoort het wél te kloppen)
  0 of 1 doelpunt                    voorspeld  20.3%   werkelijk  18.3%    -2.0 pp
  4 of meer                          voorspeld  35.6%   werkelijk  36.5%    +0.9 pp
  6 of meer                          voorspeld   9.3%   werkelijk   9.4%    +0.1 pp

DUELS MET EEN DUIDELIJKE FAVORIET (lambda-ratio >= 1.8, n=296)
  favoriet wint                      voorspeld  66.3%   werkelijk  65.2%    -1.1 pp
  favoriet wint met 2 of meer        voorspeld  43.9%   werkelijk  39.9%    -4.0 pp
  favoriet wint met 3 of meer        voorspeld  24.5%   werkelijk  23.3%    -1.1 pp
  favoriet wint met 4 of meer        voorspeld  11.8%   werkelijk  13.2%    +1.4 pp
  underdog wint of speelt gelijk     voorspeld  33.7%   werkelijk  34.8%    +1.1 pp

LEESWIJZER. Staat hier een positief verschil bij 'favoriet wint met 3 of meer', dan
onderschat het scoregrid hoe scheef een duel met een duidelijke favoriet afloopt, en
ziet de routine daardoor waarde in een handicap op de underdog die er niet is. Lambdas
van vóór 2026-09-19 komen van `shrink = 0.80`; draai `--since 2026-09-20` voor een
meting op de nieuwe instelling, en lees die pas vanaf ~150 duels met een favoriet.
```

Uitvoer van `python3 scripts/margins.py goalbias` (§6g):

```
(68 wedstrijd(en) zonder bruikbare eindstand overgeslagen)

DOELPUNTENKALIBRATIE - 1870 wedstrijden, van 2026-08-25 t/m 2026-10-31
Verwacht = de som van het opgeslagen lambdapaar; z is de Poisson-toets op het totaal.

  groep                          n  verwacht/duel  werkelijk/duel  verschil       z
  ALLE DOORGEREKENDE DUELS    1870         3.034           3.075    +0.041   +1.01
  Under gespeeld               115         2.749           3.417    +0.668   +4.32
  Over gespeeld                 65         3.353           3.108    -0.245   -1.08

DE VORM VAN DE VERDELING, over alle doorgerekende duels
(het gemiddelde kan kloppen terwijl de verdeling dat niet doet - dat is hier zo)
  0 doelpunten                       voorspeld   5.9%   werkelijk   5.0%    -0.9 pp
  1 doelpunt                         voorspeld  14.1%   werkelijk  13.9%    -0.2 pp
  2 doelpunten                       voorspeld  22.4%   werkelijk  21.4%    -1.0 pp
  3 doelpunten                       voorspeld  21.6%   werkelijk  22.1%    +0.5 pp
  4 doelpunten                       voorspeld  16.4%   werkelijk  17.5%    +1.1 pp
  5 doelpunten                       voorspeld  10.2%   werkelijk  11.5%    +1.3 pp
  6 doelpunten                       voorspeld   5.4%   werkelijk   4.8%    -0.6 pp
  7 doelpunten                       voorspeld   2.5%   werkelijk   2.7%    +0.2 pp
  8 doelpunten                       voorspeld   1.0%   werkelijk   0.7%    -0.3 pp
  9 of meer                          voorspeld   0.6%   werkelijk   0.3%    -0.3 pp

WAT DAT MET DE GANGBARE UNDER-LIJNEN DOET
  P(Under 2.5)                       voorspeld  42.4%   werkelijk  40.3%    -2.1 pp
  P(Under 3.0)                       voorspeld  64.0%   werkelijk  62.4%    -1.6 pp
  P(Under 3.5)                       voorspeld  64.0%   werkelijk  62.4%    -1.6 pp

LEESWIJZER. De bovenste tabel scheidt twee fouten die je NIET mag optellen: de regel
'ALLE DOORGEREKENDE DUELS' meet het MODEL (een z rond nul betekent dat de lambdas
kloppen), de regels eronder meten de SELECTIE (een positieve z op 'Under gespeeld'
betekent dat de routine juist daar Under speelt waar haar lambda te laag staat). De
tweede tabel meet de VORM: schuift er massa van 2 naar 4-5 doelpunten, dan staat elke
Under structureel te hoog, ook zonder selectie. Lees geen van beide onder ~30 gevallen
per groep (6d), en verzet nooit een lat op een enkele dag.
```

**Drie dingen die uit deze blokken samen volgen en die niet in één getal passen.** Het logboek staat op **−8,0% over 439 bets** en de Brier-score van het model (0,2598) is nog steeds hoger dan die van de markt (0,2398): de analyse voegt over de hele reeks nog geen kansinformatie toe boven de markt. De `edge`-reeks in het schaduwlogboek staat op **+1,9% over 564 kandidaten** — de groep die net onder de drempel viel doet het dus iets béter dan de gespeelde bets, wat precies de meting is waarop §5b rust. En de `lijstlengte`-reeks staat op **+24,2% over 20 gevallen**; dat is boven de ~30 die §6d eist nog niet leesbaar, maar het is de reeks om in de gaten te houden, want ze zegt wat de lijstlengte kost op dagen dat er méér kwalificeert dan er past. Vandaag kostte ze niets: er paste alles.

## Dagrapport (§6c)

- HTML-pagina, als Artifact gepubliceerd: **https://claude.ai/artifact/PVvXeSfUmXxW4dy9THkpxy**
- Tweede route, door GitHub gerenderd: **https://github.com/aistref/football/blob/main/runs/2026-11-01-run-a.dagrapport.md**

De rendercontrole van §6c (15 okt) is **preventief** gedraaid met Chromium uit `/opt/pw-browsers`, in licht én donker:

```
{
 "light": {
  "scrollHeight": 21618,
  "textLen": 54299,
  "blocks": 56,
  "bg": "rgb(235, 238, 242)",
  "fg": "rgb(20, 26, 33)",
  "title": "Run A — zondag 1 november 2026",
  "tables": 6,
  "bets": 5,
  "errors": []
 },
 "dark": {
  "scrollHeight": 21618,
  "textLen": 54299,
  "blocks": 56,
  "bg": "rgb(12, 17, 23)",
  "fg": "rgb(230, 235, 241)",
  "title": "Run A — zondag 1 november 2026",
  "tables": 6,
  "bets": 5,
  "errors": []
 }
}
```

21.618 px hoog, 54.299 tekens zichtbare tekst, 56 blokken, 6 tabellen, 5 bets en **nul console- of pagefouten**, in beide thema's met de juiste achtergrond- en tekstkleur. Blijkt de Artifact voor de gebruiker onbereikbaar, dan is opnieuw publiceren dus zinloos en is de Markdown-route het antwoord (§6c, 14 en 15 okt).

Vijf voorbeschouwingen van 510 tot 578 woorden, één per gepubliceerde bet, binnen de norm van 300–600 van §6c. Bij Kasımpaşa – Beşiktaş en Getafe – Sevilla opent de tekst met wat de bet tegenspreekt, zoals §6c eist zodra de frequenties dat doen.

## Openstaande punten

1. **Welke van de twee rekenmethodes zit er stelselmatig naast?** `tweede_methode` vangt nu drie dagen op rij meer dan 70% van alle doorgerekende selecties weg (74% vandaag, 356 van 479). §5 noemt dat expliciet een bevinding en geen ruis. Wat ontbreekt is de meting wélke arm fout is: vandaag staat bij Marseille – Toulouse het xG-model op +11,52 pp en de splitsmethode op −3,68 pp, bij Elche – Valencia precies omgekeerd (+0,26 tegen +17,03), en bij de gepubliceerde Getafe – Sevilla op +9,38 tegen +0,03. Dat is na te rekenen over de duizenden afgerekende waarnemingen in `calibration.jsonl`, waar beide methodes apart in staan — §6e meet nu alleen hun afstand tot de markt per kansband en niet hun onderlinge tegenspraak tegen uitkomsten. **Van de gebruiker is hier niets nodig; dit is werk voor een volgende run.**
2. **Moeten de twee picks van 3 en 4 oktober uit het logboek?** Onveranderd sinds 31 oktober en nog niet beantwoord. Exeter City – Rotherham United en Girona – Mallorca zijn onder de `match_tier`-fout gepubliceerd en hadden onder de regels niet mogen bestaan; beide zijn gewonnen. Twee van 500 afgewikkelde picks verschuiven geen enkel cijfer in §6d. **Dit is een besluit van de gebruiker over zijn eigen administratie.**
3. **Markdown of Artifact als eerste route voor het dagrapport?** Onveranderd sinds 15 oktober. De Artifact heeft het sinds die datum goed gedaan en de rendercontrole hierboven staat schoon, dus er is geen aanleiding om te wisselen. **Dit is een besluit van de gebruiker over hoe hij zijn rapport wil lezen; een run verandert die volgorde niet op eigen initiatief, en de vraag wordt niet elke dag opnieuw gesteld.**
4. **De te soepele naamregel in `settling` is nooit over de hele looptijd geaudit.** Onveranderd: niet nagegaan of hij in het verleden al eens een verkeerde uitslag heeft weggeschreven. Dat is een audit over 68 rundagen en vandaag niet gedaan. **Werk voor een volgende run.**

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
