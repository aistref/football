"""De `parameters`-tekst van Run B, 23 nov 2026 — apart gehouden zodat `rb_nov23_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vijf dingen die vandaag vooraan horen:

* **Twee regels, en GEEN van beide haalt zijn eigen lat.** Allebei op rangorde (§5b).
* **Allebei Unders, allebei in dezelfde competitie, allebei om 19:00.** De hele lijst komt uit
  één hoek — §5b noemt dat zelf een signaal over het model en niet over de regel.
* **Geen van beide is door enige rem op de doelpuntenkant getoetst.** De ene valt ONDER de band
  waarin poort 9 bindt, de andere staat op LIGHT, dat poort 9 met opzet buiten laat.
* **Pinnacle is het met allebei oneens, en het zijn de twee GROOTSTE Under-afwijkingen van de dag.**
* **Poort 9 hield vandaag wél twee andere selecties tegen**, en de reeks `doelpunten_onder` staat
  op -34,6% over 51 afgewikkelde gevallen.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,037, b=0,024 op "
            "8589 afgerekende gevallen, fitted_through 2026-11-22. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,6 pp op 50%, "
            "+1,2 pp op 70%) en verlaagt alleen onder ongeveer 35%. 'Herijkt haalt de lat, dus ruw "
            "ook' is daarmee NIET waar, en de vlag bet_beide is de controle en niet de redenering "
            "(§5a): vandaag staat ze op False bij BEIDE regels, maar dat zegt hier weinig, want "
            "geen van beide haalt zijn lat op welke schaal dan ook. Örgryte komt ruw op +10,10 pp "
            "en herijkt op +10,95 pp (lat 16,0); Hammarby ruw op +5,15 pp en herijkt op +6,08 pp "
            "(lat 8,0). LEES DE FIT NIET ALS 'het model is goed gekalibreerd en dus goed': hij is "
            "gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de "
            "scheefstand die telt zit in de GESELECTEERDE groep — vandaag staat die op z = +4,82 "
            "over 146 gespeelde Unders. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_NIET_EN_DE_LIJSTLENGTE_OOK_NIET": (
            "ACHT van de zeventien competities spelen, met 13 duels in het inzetvenster, op een "
            "MAANDAGcap van 40 (ranking.max_deep_analyses). Er is dus NIETS afgekapt en de "
            "dekkingstabel krijgt geen AFGEKAPT-regel. De negen die niets op de kalender hebben "
            "zijn Czech First League, Eliteserien, Serie B, 2. Bundesliga, Swiss Super League, "
            "Austrian Bundesliga, English League One, English League Two en Hungarian NB I — alle "
            "negen GEEN WEDSTRIJD en geen gat (§3 Stage 2); idcheck.py bevestigt per competitie "
            "dat hun id een bruikbare stand geeft, juist omdat een fout id óók nul wedstrijden "
            "zou geven (prompts/run-b.md). MAX_SHORTLIST is op maandag 2 sinds de wijziging van "
            "18 nov 2026 (ranking.max_shortlist, bindt sinds 19 nov). Er staan precies NUL "
            "selecties boven hun eigen lat, dus de lijstlengte bindt NIET en er is geen enkele "
            "gekwalificeerd_niet_gepubliceerd-regel. De reeks `lijstlengte` blijft daarmee op 31 "
            "kandidaten staan, 31 afgewikkeld, +24,5% — de gebruiker kijkt er bij 100 gevallen "
            "opnieuw naar (§5b) en een run verzet MAX_SHORTLIST nooit op eigen initiatief."
        ),
        "GEEN_VAN_BEIDE_REGELS_HAALT_ZIJN_EIGEN_LAT_EN_DAT_IS_DE_KOP_VAN_DE_DAG": (
            "Hammarby – IFK Göteborg Under 3 @2,12 staat op +6,08 pp bij een FULL-lat van 8,0, en "
            "Örgryte – Kalmar FF Under 2.5 @2,1172 op +10,95 pp bij een LIGHT-lat van 16,0. NUL "
            "van de 142 doorgerekende selecties haalde vandaag zijn drempel; beide regels staan "
            "er uitsluitend omdat §5b de drempel sinds 20 sep 2026 aan het EIND laat snijden en "
            "`toplist._cut` de lijst dan aanvult op selection_score. Dat is de regel en geen "
            "omissie, maar lees de lijst dan ook zoals §5b hem bedoelt: dit is een RANGSCHIKKING "
            "van wat het model vandaag het sterkst vindt en GEEN verzameling gevonden voordelen. "
            "MAX_LIGHT_IN_SHORTLIST (2) bindt niet: er is één LIGHT-regel."
        ),
        "BEIDE_REGELS_ZIJN_UNDERS_UIT_DEZELFDE_COMPETITIE_EN_HET_ZELFDE_TIJDSTIP": (
            "Allsvenskan, allebei 19:00 NL: Hammarby – IFK Göteborg en Örgryte – Kalmar FF. Dat "
            "is de enige competitie op de runlijst van vandaag die twee duels in het venster "
            "heeft, en ze vult daarmee de HELE lijst — twee van de twee regels, op dezelfde markt "
            "en dezelfde kant. §5b zegt daar zelf iets over: 'Blijft de lijst dagen achtereen uit "
            "één hoek komen, dan is dat een signaal over het model en niet over deze regel.' Eén "
            "dag is geen reeks (§6d) en deze run verzet daar niets op. Wat er wel bij hoort: de "
            "lijst van vandaag is GEEN gespreide weddenschap maar twee keer dezelfde mening over "
            "hetzelfde — er wordt weinig gescoord in Zweden — in twee wedstrijden die tegelijk "
            "beginnen. Allsvenskan loopt op kalenderjaar en zit op 29 van 30 speeldagen, dus "
            "league_level nam daar route `lopend` (§3 Stage 5) en NIET de gepoolde "
            "vroeg-seizoenscorrectie; de competitie staat ook in de overgeslagen lijst van "
            "uplift_observations, precies zoals prompts/run-b.md dat voor de vier "
            "kalenderjaarcompetities voorschrijft."
        ),
        "GEEN_VAN_BEIDE_UNDERS_IS_DOOR_ENIGE_REM_GETOETST_EN_DAT_IS_HET_GAT_IN_DE_OPZET": (
            "DIT IS DE BELANGRIJKSTE WAARSCHUWING VAN DEZE RUN EN HET IS EEN GAT IN DE OPZET, "
            "GEEN FOUT IN DE RUN. Poort 9 (§1h) bestaat precies voor de Under-kant, maar hij "
            "bindt uitsluitend op data_tier = FULL én uitsluitend in de band tussen de gewone "
            "drempel (8,0) en de verzwaarde lat (10,0). Regel 1 (Hammarby, FULL, +6,08 pp) valt "
            "ERONDER: unders.check geeft terug dat `edge` de bindende poort is en niet poort 9 — "
            "dezelfde constructie als Basel – Luzern op 22 november. Regel 2 (Örgryte, LIGHT, "
            "+10,95 pp) valt erbuiten omdat punt 1 van §1h LIGHT met opzet buiten de poort houdt, "
            "gevraagd en beantwoord op 12 oktober — dezelfde constructie als Atalanta – Venezia. "
            "Vandaag staan die twee gaten voor het eerst SAMEN, en ze vullen de hele lijst. EEN "
            "RUN VERZET POORT 9 OF §5b NIET OP EIGEN INITIATIEF (§1h, stand 2 nov 2026; §5b): dit "
            "hoort als vraag in het dagrapport onder 'Wat er nog moet gebeuren' met owner = "
            "besluit, en niet als wijziging in deze run."
        ),
        "POORT_9_HIELD_VANDAAG_WEL_TWEE_ANDERE_SELECTIES_TEGEN": (
            "Twee van de 142 selecties sneuvelden op failed_gate = doelpunten_onder — FULL-Unders "
            "in de band 8–10 pp, precies waarvoor de rem is gebouwd. De reeks staat daarmee op 54 "
            "kandidaten, 51 afgewikkeld, 35,3% trefkans, -17,65u = -34,6% rendement: de rem "
            "bespaart geld en heeft de ~30 van §6d ruim gehaald. Dat is het argument om hem te "
            "laten staan, en tegelijk het argument waarom zijn twee gaten hierboven ertoe doen: "
            "de kant die de rem tegenhoudt kost -34,6%, en de twee regels van vandaag staan op "
            "diezelfde kant zonder door de rem te zijn gegaan."
        ),
        "DE_UNDER_KANT_VAN_DE_SELECTIE_STAAT_OP_Z_IS_PLUS_4_82": (
            "margins.py goalbias splitst het MODEL van de SELECTIE en die twee mogen nooit worden "
            "opgeteld. Over alle 2436 doorgerekende duels staat het model op +0,021 doelpunt per "
            "duel (z = +0,60, dus de lambdas kloppen), maar over de 146 duels waar werkelijk een "
            "Under is gespeeld op +0,663 doelpunt per duel (z = +4,82). De routine speelt Under "
            "dus juist daar waar haar eigen doelverwachting te laag staat, en dat is exact de "
            "kant waarop BEIDE regels van vandaag staan. De vormtabel geeft bovendien géén "
            "steun aan een Under-overschatting door de vórm: P(Under 2.5) staat voorspeld 42,2% "
            "tegen werkelijk 40,8% over 2436 duels — 1,4 pp te hoog, de kant die §6g beschrijft, "
            "maar klein. Het probleem zit in de SELECTIE en niet in het grid. Eén dag is geen "
            "reeks (§6d) en dit getal hoort in het rapport en niet in een parameter."
        ),
        "PINNACLE_IS_HET_MET_BEIDE_REGELS_ONEENS_EN_HET_ZIJN_DE_TWEE_GROOTSTE_AFWIJKINGEN": (
            "De tweede toets van Stage 5 stap 2, en ze wijst dezelfde kant op als de meting "
            "hierboven. Op de doelpuntenkant zijn er acht toetsbare (duel, lijn)-paren; de twee "
            "GROOTSTE afwijkingen van alle acht zijn precies de twee gepubliceerde duels. "
            "HAMMARBY – IFK GÖTEBORG: op lijn 3,25 geeft het eigen model P(Under) 55,7% tegen "
            "49,0% bij Pinnacle, +6,79 pp, bij een Pinnacle-marge van 4,2%. ÖRGRYTE – KALMAR FF: "
            "op lijn 2,75 eigen 58,2% tegen 51,8%, +6,35 pp, marge 4,3%. Gemiddeld over alle acht "
            "staat het model +1,77 pp boven Pinnacle op de Under-kant, bij 5 van 8 erboven — de "
            "twee bets zijn dus niet alleen aan de verkeerde kant van de scheefstand, ze zijn er "
            "de uiterste gevallen van. Op de 1X2 zijn er acht toetsbare duels met een gemiddelde "
            "absolute afstand van 3,24 pp bij een gemiddelde Pinnacle-marge van 4,05%; de "
            "grootste staat eveneens bij Hammarby, waar het eigen model de thuisploeg 65,5% geeft "
            "tegen 78,4% bij Pinnacle (-12,92 pp). DEZE GETALLEN GAAN NIET IN my_prob en "
            "veranderen geen enkele pick van vandaag (§2) — ze horen in de vergelijking, en "
            "daarom staan ze hier en bij de bets in het runrapport."
        ),
        "POORT_5_VANGT_VIER_VAN_DE_VIJF_SELECTIES_WEG": (
            "Over de 13 duels zijn 142 selecties doorgerekend, verdeeld over alle zes de markten: "
            "40 Over/Under, 38 1X2, 38 Asian Handicap, 12 BTTS, 9 Draw No Bet en 5 Double Chance. "
            "Daarvan sneuvelden er 112 op poort 5 ('data conflicterend' — de twee methodes "
            "verslaan de markt niet dezelfde kant op), oftewel 79% van alles; daarna 10 op de "
            "edge-afkapping, 8 op poort 7 (context), 6 op poort 8 (underdog), 4 op de koersband "
            "en 2 op poort 9. Poort 6 (robuustheid) hield NUL selecties tegen. NUL selecties "
            "hielden alle poorten open én haalden hun drempel; de twee regels komen dus volledig "
            "op rangorde. Twee duels sneuvelden op poort 7 (AD Ceuta FC – Almería, waar Ceuta 22% "
            "van de selectiewaarde mist tegen 8% bij Almería; Internacional – Vitória, 40% tegen "
            "25% met Alan Patrick geschorst en Bernabéi en Matheus Cunha geblesseerd) en één op "
            "poort 5 als wedstrijduitkomst (St. Louis City – Los Angeles FC). De RUWE dagranglijst "
            "wordt aangevoerd door IFK Göteborg +2 @1,8526 (+15,95 pp, score 11,154), dat op poort "
            "8 sneuvelde en dus NIET in de lijst staat — lees die lijst als een meting en niet als "
            "een tip (§5a)."
        ),
        "DRIE_VAN_DE_VIJF_COMPETITIES_ZONDER_xG_SPELEN_VANDAAG": (
            "Croatian HNL (252), Romanian SuperLiga (189) en Keuken Kampioen Divisie (111) staan "
            "in coverage.json met has_xg=false en idcheck.py bevestigt dat per competitie; de "
            "andere twee zonder xG (Czech First League 122, Hungarian NB I 212) spelen vandaag "
            "niet. Die drie draaien op doelpunten als sterktemaat en komen dus altijd op LIGHT "
            "uit, met een lat van 16,0 pp (prompts/run-b.md); ze hebben bovendien geen sportkey "
            "bij The Odds API, dus hun prijs is het gratis BetExplorer-marktgemiddelde waar de "
            "bookmaker niet herleidbaar is en de edge systematisch te laag uitvalt (§1a). Samen 5 "
            "van de 13 duels, op beide assen de zwakste van de dag — en ze leveren elk maar DRIE "
            "doorgerekende selecties op (alleen de 1X2), tegen 12 tot 19 bij de competities met "
            "een sportkey. Geen van die vijf komt in de buurt van de lijst. Neem dekking nooit "
            "over van een andere competitie in hetzelfde land: Nederland heeft xG in de "
            "Eredivisie en niet in de Keuken Kampioen Divisie."
        ),
        "TWEE_PROMOVENDI_ZIJN_OMGEREKEND_EN_GEEN_VAN_BEIDE_KWAM_OP_NONE_UIT": (
            "Örgryte en Kalmar FF staan niet in de Allsvenskan-stand van 2025 en Sepsi OSK niet "
            "in de Romanian SuperLiga van 2025/2026; alle drie zijn langs promotion.convert "
            "gegaan (§4, 'Promovendi: eerst omrekenen, dan pas NONE'). Beide duels zijn daardoor "
            "op LIGHT uitgekomen in plaats van op NONE, en Örgryte – Kalmar FF levert de tweede "
            "regel van de dag. NUL van de 13 duels komt vandaag op data_tier = NONE uit — dat is "
            "ongewoon en het is een gevolg van de omrekening, niet van soepeler regels."
        ),
        "SANTOS_SPEELT_NIET_IN_VILA_BELMIRO_EN_DAT_HOORT_ER_OOK_BIJ_ALS_DE_POORT_OPENGAAT": (
            "context.check_venue sloeg vandaag bij één duel aan: Santos – Grêmio wordt gespeeld "
            "in MorumBIS (São Paulo) en niet in Estádio Urbano Caldeira, het genoteerde eigen "
            "stadion van Santos. §1c eist dat een verplaatsing in het runrapport staat ÓÓK als de "
            "poort opengaat, want thuisvoordeel is de aanname waar het model het zwaarst op "
            "leunt. De poort gaat hier open omdat er geen materieel nadeel op de beschikbaarheid "
            "staat, en het duel levert geen regel. Wat deze controle NIET vangt blijft staan zoals "
            "§1c het beschrijft: een fixture die van eigenaar is gewisseld is nieuws en geen data."
        ),
        "EEN_SCHADUWRIJ_VAN_GISTEREN_STAAT_NOG_OPEN_EN_DAT_IS_DE_REGEL_EN_GEEN_FOUT": (
            "shadow-2026-11-22-b-vancouver-whitecaps---real-salt-lake staat 3,1 uur na de aftrap "
            "nog op pending. Fotmob vindt het duel (MLS Playoff, stand 2 - 0) maar zet "
            "`finished` nog niet op true, en §0 zegt dan letterlijk: wachten. De terugval op de "
            "klok (SETTLE_FALLBACK_HOURS = 2,0) geldt UITSLUITEND wanneer er géén bronstatus te "
            "krijgen was, en die is er hier wel. De volgende run wikkelt hem af. Verder stonden "
            "er vanochtend geen afwikkelbare picks of schaduwrijen: de twee openstaande picks "
            "(Wieczysta Kraków – Motor Lublin, Levante – Elche) zijn van Run A van VANDAAG en "
            "moeten nog beginnen."
        ),
    }
