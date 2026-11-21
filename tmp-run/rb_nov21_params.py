"""De `parameters`-tekst van Run B, 21 nov 2026 — apart gehouden zodat `rb_nov21_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vijf dingen die vandaag vooraan horen:

* **De volle zaterdag is terug: alle zeventien competities spelen, 71 duels in het venster, en de
  cap bindt voor het eerst sinds 24 oktober** — 55 doorgerekend, 16 afgekapt.
* **Vijf regels, en alle vijf halen hun eigen lat.** Dat is sinds 8 november niet gebeurd.
* **Vier van de vijf staan op de kant 'er vallen weinig doelpunten'** (drie Unders en een BTTS
  'nee'), en dat is precies de kant waarvan §6g op uitkomsten meet dat de SELECTIE scheef staat.
  `margins.py goalbias` geeft vandaag **z = +4,74 over 139 gespeelde Unders**, de scherpste stand
  die die meting ooit heeft gegeven.
* **Pinnacle is het met alle vier die regels oneens, en met drie ervan het hardst van de dag.**
* **Een parserfout in `betexplorer.fetch_league_fixtures` is gerepareerd**; hij kostte de
  bevestigingspoort van §1 een spookduel. Zie bevinding 1.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0443, b=0,0286 op "
            "8082 afgerekende gevallen, fitted_through 2026-11-20. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,7 pp op 50%, "
            "+1,4 pp op 70%) en verlaagt alleen onder ongeveer 35%: het ruwe model zei gemiddeld "
            "33,3% en het gebeurde 33,3%. 'Herijkt haalt de lat, dus ruw ook' is daarmee NIET waar, "
            "en de vlag bet_beide is de controle en niet de redenering (§5a). Vandaag staat ze op "
            "False bij twee van de vijf regels — Modena en Tromsø halen de lat alleen herijkt. "
            "LEES DE FIT NIET ALS 'het model is goed gekalibreerd en dus goed': hij is gekalibreerd "
            "op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit "
            "in de GESELECTEERDE groep. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_VANDAAG_WEL_EN_DAT_IS_SINDS_24_OKTOBER_NIET_GEBEURD": (
            "71 duels in ALLE ZEVENTIEN competities van de runlijst, op een ZATERDAGcap van 55 "
            "(ranking.max_deep_analyses), dus er zijn 16 duels AFGEKAPT en de dekkingstabel krijgt "
            "AFGEKAPT-regels. Dat is geen storing maar de eerste volle zaterdag van deze runlijst "
            "na het interlandvenster. De afkapping kost naar rato en niet proportioneel-slechter "
            "(§3 Stage 4, meting van 5 sep: de betkans is vlak over de rangorde), dus lees de "
            "zestien niet als 'de zwakste zestien'. De datarijkdom liep van 4,5 tot 8,0; de "
            "laagste die het haalde is Sampdoria – Benevento (5,0) en de hoogste die afviel "
            "Kalamata – AEK Athens (5,0) — dezelfde score, dus de grens is op het aantal markten "
            "en de aftrap gevallen en niet op de informatie. Twee competities zijn in hun GEHEEL "
            "afgekapt — Croatian HNL (2 van 2) en Greek Super League (1 van 1) — en die krijgen "
            "AFGEKAPT en niet GEANALYSEERD, want dat laatste is precies de stille truncatie die "
            "Stage 4 verbiedt. De Czech First League verliest er drie van de vijf en houdt er twee "
            "over, dus die blijft GEANALYSEERD met een afkappingsregel in de toelichting."
        ),
        "VIJF_REGELS_EN_ALLE_VIJF_HALEN_HUN_EIGEN_LAT": (
            "Dit is sinds 8 november niet gebeurd en het is de vermelding waard, maar lees het "
            "zoals §5b het bedoelt. Alle vijf de gepubliceerde selecties staan boven "
            "EDGE_THRESHOLD_FULL (8,0 pp) en alle vijf zijn FULL: Modena +11,35 · Tromsø +11,08 · "
            "Palmeiras +11,85 · Carrarese +9,94 · HamKam +8,97. Het aantal gekwalificeerde "
            "selecties is daarmee EXACT MAX_SHORTLIST (5 op zaterdag, ranking.max_shortlist), dus "
            "de lijstlengte bindt NIET en er is geen enkele gekwalificeerd_niet_gepubliceerd-regel. "
            "Dat betekent NIET dat dit vijf gevonden voordelen zijn: §1g heeft op 552 afgerekende "
            "gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert, en "
            "dat het rendement het SLECHTST is bij de hoogste geclaimde edge. Het logboek staat "
            "vandaag op -5,8% over 508 bets en de markt schat op Brier nog steeds scherper "
            "(0,2429 tegen 0,2616 eigen)."
        ),
        "VIER_VAN_DE_VIJF_STAAN_OP_DE_KANT_WAAR_DE_SELECTIE_MEETBAAR_SCHEEF_STAAT": (
            "DIT IS DE BELANGRIJKSTE WAARSCHUWING VAN DEZE RUN. Drie Unders (Modena Under 3, "
            "Tromsø Under 3.5, Palmeiras Under 2.5) en een BTTS 'nee' (Carrarese): vier van de vijf "
            "regels zeggen dat er weinig doelpunten vallen. margins.py goalbias splitst het MODEL "
            "van de SELECTIE en die twee mogen nooit worden opgeteld: over alle 2266 doorgerekende "
            "duels staat het model op +0,026 doelpunt per duel (z = +0,71, dus de lambdas kloppen), "
            "maar over de 139 duels waar werkelijk een Under is gespeeld op +0,668 doelpunt per duel "
            "(z = +4,74). Dat is de SCHERPSTE stand die deze meting ooit heeft gegeven — gisteren "
            "stond ze op z = +4,63 over 138 — en ze zegt dat de routine juist daar Under speelt waar "
            "haar eigen doelverwachting te laag staat. Poort 9 bindt en alle drie de Unders halen de "
            "verzwaarde lat van 10,0 pp ruim (11,35 / 11,08 / 11,85). BTTS 'nee' valt met opzet "
            "BUITEN die poort (§1h punt 2: 15 afgewikkelde BTTS-picks is geen meting), dus de "
            "Carrarese-regel is door geen enkele rem op deze kant getoetst. EEN RUN VERZET POORT 9 "
            "NIET OP EIGEN INITIATIEF (§1h, stand 2 nov 2026) en één dag is geen reeks (§6d); dit "
            "getal hoort in het rapport en niet in een parameter."
        ),
        "PINNACLE_IS_HET_MET_ALLE_VIER_DIE_REGELS_ONEENS_EN_MET_DRIE_HET_HARDST_VAN_DE_DAG": (
            "De tweede toets van Stage 5 stap 2, en ze wijst dezelfde kant op als de meting "
            "hierboven. Over 38 toetsbare (duel, lijn)-paren ligt de eigen Under-kant gemiddeld "
            "+1,60 pp boven het de-vigde Pinnacle-oordeel, met 23 van de 38 erboven; uitgesplitst "
            "+1,35 pp op de negen zuivere halve lijnen en +1,68 pp op de 29 met push. De vier "
            "doelpuntenregels van vandaag staan alle vier BOVEN Pinnacle en ze staan op de plekken "
            "1, 3 en 4 van de hele dag: Modena – Juve Stabia +14,25 pp op lijn 2,75 (de grootste van "
            "de 38, bij een Pinnacle-marge van 3,1%), Tromsø – Viking +12,37 pp op lijn 3,25, "
            "Palmeiras – Flamengo +11,49 pp op lijn 2,50 en Carrarese – Virtus Entella +7,05 pp op "
            "lijn 2,25. Palmeiras – Flamengo is bovendien de grootste 1X2-afwijking van de dag: het "
            "eigen model geeft Flamengo 33,2% waar Pinnacle 49,5% zegt, een gat van 16,3 pp bij een "
            "marge van 3,7%. Bij HamKam – Fredrikstad heeft Pinnacle geen 1X2, dus die regel is langs "
            "deze weg niet te toetsen. DEZE GETALLEN GAAN NIET IN my_prob en veranderen geen enkele "
            "pick van vandaag (§2) — ze horen in de vergelijking, en daarom staan ze hier en bij de "
            "bets in het runrapport."
        ),
        "DE_TWEEDE_BRON_IS_NA_EEN_REPARATIE_OVER_DE_HELE_LIJN_EENS": (
            "De bevestigingspoort van §1 gaf bij de eerste meting 16 van de 17 competities 'eens' en "
            "wees bij de Keuken Kampioen Divisie naar een duel dat Fotmob niet heeft: NAC Breda – "
            "Den Bosch, zogenaamd vandaag 16:30 UK. Dat duel bestaat vandaag niet — de JSON-LD van "
            "diezelfde BetExplorer-pagina zet hem op 27 nov 20:00, en beide ploegen speelden gisteren "
            "nog (Almere City – NAC 1-4, Den Bosch – VVV 1-0). De oorzaak is een parserfout in "
            "scripts/betexplorer.fetch_league_fixtures en ze is gerepareerd; zie bevinding 1. Na de "
            "reparatie: 17 van de 17 competities eens, 71 duels bij Fotmob tegen 71 bij BetExplorer, "
            "per competitie gelijk. idcheck.py geeft daarnaast afsluitcode 0 op alle 33 id's uit "
            "coverage.json, met Serie B op het echte id 86 en twintig ploegen."
        ),
        "VIJF_VAN_DE_ZEVENTIEN_COMPETITIES_HEBBEN_GEEN_xG_EN_DAT_IS_DE_VASTGELEGDE_STAND": (
            "Czech First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga "
            "(189) en Keuken Kampioen Divisie (111) staan in coverage.json met has_xg=false en "
            "idcheck.py bevestigt dat per competitie. Die vijf draaien op doelpunten als sterktemaat "
            "en komen dus altijd op LIGHT uit, met een lat van 16,0 pp (prompts/run-b.md); ze hebben "
            "bovendien geen sportkey bij The Odds API, dus hun prijs is het gratis "
            "BetExplorer-marktgemiddelde waar de bookmaker niet herleidbaar is en de edge "
            "systematisch te laag uitvalt (§1a). Samen 14 van de 71 duels, op beide assen de zwakste "
            "van de dag, en geen van hen levert vandaag een regel. Neem dekking nooit over van een "
            "andere competitie in hetzelfde land: Duitsland heeft xG in de 2. Bundesliga en Nederland "
            "niet in de Keuken Kampioen Divisie, terwijl beide landen het in hun hoogste divisie wel "
            "hebben."
        ),
        "ACHT_VAN_DE_55_DUELS_KOMEN_OP_NONE_UIT_EN_DAT_IS_DE_PRIJS_VAN_EEN_VOLLE_ZATERDAG": (
            "Veertien van de 71 duels komen op data_tier = NONE uit; zes daarvan zijn ook afgekapt, "
            "dus van de 55 doorgerekende duels blijven er 47 met kandidaten over en vallen er ACHT "
            "op NONE. Alle veertien gaan langs de omrekening van §4: acht omdat de omrekening buiten "
            "het gemeten bereik valt (conversion_in_range) en zes omdat er geen historie in de "
            "divisie is — vier degradanten die niet in de stand van de divisie erboven staan "
            "(Ascoli, Benevento, Rochdale, York City) en twee competities waar Fotmob geen divisie "
            "eronder kent (Croatian HNL voor Rudeš, Série A BRA voor Coritiba en Chapecoense). Dat "
            "is geen defect: §4 schrijft NONE voor zodra er geen onafhankelijke kansbron op de "
            "juiste schaal is, en NONE betekent GEEN BET en niet 'LIGHT met lage confidence' (§2). "
            "Het is wel de reden dat een zaterdag met 71 duels geen 71 doorgerekende wedstrijden "
            "oplevert. MLS kent géén promotie en degradatie, dus een ploeg die niet in de stand van "
            "vorig seizoen staat is daar een uitbreidingsploeg en geen promovendus (prompts/run-b.md); "
            "bij Série A (BRA) bestaat er geen gemeten factor voor het divisiepaar met Série B."
        ),
        "EEN_POORT_VANGT_DRIEKWART_VAN_ALLES_WEG_EN_DAT_IS_POORT_5": (
            "Over de 47 duels met kandidaten zijn 582 selecties doorgerekend, verdeeld over alle zes "
            "de markten: 182 Over/Under, 160 Asian Handicap, 135 1X2, 58 BTTS, 36 Draw No Bet en 11 "
            "Double Chance. Daarvan sneuvelden er 444 op poort 5 ('data conflicterend' — de twee "
            "methodes verslaan de markt niet dezelfde kant op), oftewel 76% van alles; daarna 55 op "
            "de edge-afkapping, 25 op poort 8 (underdog), 19 op poort 7 (context), 18 op de "
            "koersband, 7 op poort 6 (robuustheid) en 5 op poort 9 (Under-kant). NEGEN selecties "
            "hielden alle poorten open, en die negen zitten in vijf wedstrijden — de 0-of-1-bet-regel "
            "maakt daar vijf regels van, en de vier niet-gekozen selecties staan als "
            "binnen_wedstrijd_niet_gekozen in de run-state en niet in het schaduwlogboek (§1a: "
            "dezelfde mening in een andere markt is één bevinding). Twee duels sneuvelden op poort 7 "
            "(AIK – Degerfors, waar AIK 27% van de selectiewaarde mist tegen 12% bij Degerfors; "
            "Plymouth – Peterborough, 19% tegen 0%) en één op poort 6 (Sion – Servette). De ruwe "
            "dagranglijst wordt aangevoerd door vijf kandidaten die alle vijf op poort 7 of poort 8 "
            "sneuvelden en die dus NIET in de lijst staan — lees die lijst als een meting en niet "
            "als een tip (§5a)."
        ),
    }
