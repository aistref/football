"""De `parameters`-tekst van Run B, 22 nov 2026 — apart gehouden zodat `rb_nov22_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vijf dingen die vandaag vooraan horen:

* **Vier regels op een zondaglijst van vier, en drie ervan halen hun eigen lat.** De vierde
  (Basel – Luzern, Under 3.5, +7,58 pp) staat er op rangorde en NIET op zijn lat.
* **Juist die vierde regel is door geen enkele rem op de doelpuntenkant getoetst.** Poort 9 bindt
  pas tussen 8,0 en 10,0 pp; met +7,58 pp ligt hij eronder en geeft `unders.check` zelf
  `passed = True` terug. Dat is de FULL-tegenhanger van Atalanta – Venezia (12 okt, LIGHT).
* **De Under-kant van de SELECTIE staat op z = +4,89 over 144 gespeelde Unders** — opnieuw de
  scherpste stand die `margins.py goalbias` ooit heeft gegeven.
* **Pinnacle is het met beide bovenste regels oneens, en met beide het hardst van de dag.**
* **Twee naamkoppelingen zijn gerepareerd** (`fk` ontbrak in `teamnames._DROP`, en BetExplorer
  schrijft Zbrojovka Brno kaal als "Brno"); samen kostten ze één duel al zijn prijzen.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,033, b=0,021 op "
            "8385 afgerekende gevallen, fitted_through 2026-11-21. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,5 pp op 50%, "
            "+1,0 pp op 70%) en verlaagt alleen onder ongeveer 35%. 'Herijkt haalt de lat, dus ruw "
            "ook' is daarmee NIET waar, en de vlag bet_beide is de controle en niet de redenering "
            "(§5a): vandaag staat ze op False bij DRIE van de vier regels. Wolfsberger (ruw +7,51 "
            "tegen herijkt +8,51), Debrecen (+15,90 tegen +16,71) en Basel (+6,80 tegen +7,58) "
            "halen hun lat alleen op de herijkte schaal, of in het geval van Basel op geen van "
            "beide. LEES DE FIT NIET ALS 'het model is goed gekalibreerd en dus goed': hij is "
            "gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de "
            "scheefstand die telt zit in de GESELECTEERDE groep. Daarom staat poort 8 nog aan en "
            "is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_VANDAAG_NIET_EN_DE_LIJSTLENGTE_OOK_NIET": (
            "VEERTIEN van de zeventien competities spelen, met 44 duels in het inzetvenster, op "
            "een ZONDAGcap van 55 (ranking.max_deep_analyses). Er is dus NIETS afgekapt en de "
            "dekkingstabel krijgt geen AFGEKAPT-regel. De drie die niets op de kalender hebben "
            "zijn Keuken Kampioen Divisie, English League One en English League Two — alle drie "
            "GEEN WEDSTRIJD en geen gat (§3 Stage 2): de Engelse divisies speelden gisteren en "
            "spelen dinsdag, de KKD vrijdag. MAX_SHORTLIST is op zondag 4 sinds de wijziging van "
            "18 nov 2026 (ranking.max_shortlist, bindt sinds 19 nov; de zondag splitst van de "
            "zaterdag, die op 5 staat). Er zijn precies VIER regels, dus de lijstlengte bindt "
            "NIET en er is geen enkele gekwalificeerd_niet_gepubliceerd-regel. De reeks "
            "`lijstlengte` blijft daarmee op 31 kandidaten staan, 30 afgewikkeld, +20,8% — de "
            "gebruiker kijkt er bij 100 gevallen opnieuw naar (§5b) en een run verzet "
            "MAX_SHORTLIST nooit op eigen initiatief."
        ),
        "DRIE_VAN_DE_VIER_REGELS_HALEN_HUN_LAT_EN_DE_VIERDE_STAAT_ER_OP_RANGORDE": (
            "Levadiakos +12,62 pp (FULL, lat 8,0), Wolfsberger AC Over 2.5 +8,51 pp (FULL, lat "
            "8,0) en Debrecen +16,71 pp (LIGHT, lat 16,0) staan boven hun eigen lat. Basel – "
            "Luzern Under 3.5 staat op +7,58 pp en haalt die 8,0 NIET; hij staat in de lijst "
            "omdat §5b de drempel sinds 20 sep 2026 aan het EIND laat snijden en er maar drie "
            "selecties boven hun lat stonden tegen vier plekken. `toplist._cut` zet daarom eerst "
            "alles boven de lat en vult daarna aan op selection_score. Dat is de regel en geen "
            "omissie, maar lees de lijst dan ook zoals §5b hem bedoelt: dit is een RANGSCHIKKING "
            "van wat het model vandaag het sterkst vindt en geen verzameling gevonden voordelen. "
            "MAX_LIGHT_IN_SHORTLIST (2) bindt niet: er is één LIGHT-regel."
        ),
        "DE_VIERDE_REGEL_IS_EEN_FULL_UNDER_DIE_DOOR_GEEN_ENKELE_REM_IS_GETOETST": (
            "DIT IS DE BELANGRIJKSTE WAARSCHUWING VAN DEZE RUN EN HET IS EEN GAT IN DE OPZET, GEEN "
            "FOUT IN DE RUN. Basel – Luzern Under 3.5 @1,95 is een Over/Under op de UNDER-kant met "
            "data_tier = FULL — precies de markt-en-kant waar §6g de schade meet. Poort 9 (§1h) is "
            "daarvoor gebouwd, maar hij bindt uitsluitend in de band tussen de gewone drempel (8,0) "
            "en de verzwaarde lat (10,0): met +7,58 pp valt deze selectie ERONDER en geeft "
            "unders.check letterlijk terug dat `edge` de bindende poort is en niet poort 9. Zolang "
            "de drempel een POORT was, hield die 8,0 hem tegen; sinds §5b (20 sep 2026) is de "
            "drempel een afkapping en kan een selectie onder de 8,0 op rangorde gepubliceerd worden "
            "— en dan is er niets meer dat de Under-kant toetst. Dat is exact dezelfde constructie "
            "als Atalanta – Venezia op 12 oktober (Under 3.5 op LIGHT, onder de LIGHT-lat, door "
            "geen rem getoetst omdat poort 9 LIGHT met opzet buiten laat), nu voor het eerst op "
            "FULL. Het robuustheidsgrid staat hier bovendien op zijn smalst van de vier regels "
            "(min_edge +2,47 pp) en de twee methodes lopen ver uiteen (xG 53,96% tegen splits "
            "74,59% voor Under 3.5). EEN RUN VERZET POORT 9 OF §5b NIET OP EIGEN INITIATIEF (§1h, "
            "stand 2 nov 2026; §5b): dit hoort als vraag in het dagrapport onder 'Wat er nog moet "
            "gebeuren' met owner = besluit, en niet als wijziging in deze run."
        ),
        "DE_UNDER_KANT_VAN_DE_SELECTIE_STAAT_OP_DE_SCHERPSTE_STAND_OOIT": (
            "margins.py goalbias splitst het MODEL van de SELECTIE en die twee mogen nooit worden "
            "opgeteld. Over alle 2368 doorgerekende duels staat het model op +0,020 doelpunt per "
            "duel (z = +0,56, dus de lambdas kloppen), maar over de 144 duels waar werkelijk een "
            "Under is gespeeld op +0,677 doelpunt per duel (z = +4,89). Dat is de SCHERPSTE stand "
            "die deze meting ooit heeft gegeven — gisteren +4,74 over 139 — en ze zegt dat de "
            "routine juist daar Under speelt waar haar eigen doelverwachting te laag staat. De "
            "spiegel staat er ook: over de 78 gespeelde Overs vielen er 0,318 doelpunt per duel "
            "MINDER dan verwacht (z = -1,53), dus ook de Over-regel van vandaag (Wolfsberger AC, "
            "Over 2.5) staat op een kant waar de selectie tot nu toe de verkeerde kant op uitvalt. "
            "De reeks `doelpunten_onder` staat op 52 kandidaten, 50 afgewikkeld, -33,3% rendement: "
            "de rem bespaart geld en heeft de ~30 van §6d gehaald. Vandaag hield poort 9 NUL "
            "selecties tegen. Eén dag is geen reeks (§6d) en dit getal hoort in het rapport en niet "
            "in een parameter."
        ),
        "PINNACLE_IS_HET_MET_BEIDE_BOVENSTE_REGELS_HET_HARDST_VAN_DE_DAG_ONEENS": (
            "De tweede toets van Stage 5 stap 2, en ze wijst dezelfde kant op als de meting "
            "hierboven. Op de 1X2 zijn er 27 toetsbare duels, met een gemiddelde absolute afstand "
            "van 3,91 pp tot het de-vigde Pinnacle-oordeel bij een gemiddelde Pinnacle-marge van "
            "3,82%. LEVADIAKOS IS DAARVAN DE TWEEDE GROOTSTE AFWIJKING: het eigen model geeft "
            "Levadiakos 49,2% waar Pinnacle 37,0% zegt, een gat van +12,16 pp bij een marge van "
            "3,6% (alleen Brommapojkarna – Halmstads BK staat verder, op +16,85 pp, en die "
            "sneuvelde op poort 5). Op de doelpuntenkant zijn er 27 (duel, lijn)-paren; daar is "
            "WOLFSBERGER AC – RIED DE GROOTSTE AFWIJKING VAN ALLE 27: op lijn 3,00 geeft het eigen "
            "model P(Under) 40,5% tegen 53,1% bij Pinnacle, oftewel 12,57 pp MEER kans op doelpunten "
            "dan de scherpste bookmaker van de markt, bij een Pinnacle-marge van 3,0%. Basel – "
            "Luzern staat op lijn 3,50 juist +3,84 pp boven Pinnacle op de Under-kant. Bij "
            "Nyíregyháza – Debrecen heeft Pinnacle niets, want de Hongaarse competitie heeft geen "
            "sportkey. DEZE GETALLEN GAAN NIET IN my_prob en veranderen geen enkele pick van vandaag "
            "(§2) — ze horen in de vergelijking, en daarom staan ze hier en bij de bets in het "
            "runrapport."
        ),
        "TWEE_NAAMKOPPELINGEN_GEREPAREERD_EN_SAMEN_KOSTTEN_ZE_EEN_HEEL_DUEL": (
            "Pardubice – FC Zbrojovka Brno kwam bij de eerste analyse met NUL doorgerekende markten "
            "door ('geen prijzen gevonden'), terwijl vijftien boeken een 1X2 noteerden. Twee "
            "oorzaken, beide in scripts/teamnames.py en beide gerepareerd. (1) `fk` stond NIET in "
            "_DROP, terwijl fc, afc, sc, ac en as er vanaf het begin in staan: BetExplorer schrijft "
            "'FK Pardubice' en Fotmob 'Pardubice', en zonder die regel is dat {pardubice} tegen "
            "{fk, pardubice} — geen gelijkheid, dus is_abbreviation wijst het af. (2) BetExplorer "
            "laat de clubnaam weg en houdt de stad over: 'Brno' voor FC Zbrojovka Brno, terwijl er "
            "dit seizoen TWEE Brno-clubs in de Chance Liga staan (Artis Brno is de andere). Alleen "
            "de kale stad kreeg een alias; Artis Brno koppelt op zijn eigen naam en wordt niet "
            "geraakt. In een competitie zonder sportkey is het BetExplorer-gemiddelde de ENIGE "
            "1X2-bron, dus dit kostte drie dingen tegelijk: geen enkele markt doorgerekend, een "
            "leeg kalibratieblok (§6e) en poort 8 die opengaat op 'geen marktoordeel over wie de "
            "mindere is' zonder te zijn getoetst. Na de reparatie heeft het duel drie "
            "1X2-selecties en een kalibratieblok. Beide wijzigingen zijn nagelopen op "
            "naambotsingen over alle 33 competities uit coverage.json: er zijn elf botsingen en "
            "GEEN ervan komt van `fk` — het zijn Manchester City tegen Manchester United en Dundee "
            "United tegen Dundee FC, die al botsten omdat 'city' en 'united' in _DROP staan. Die "
            "zijn onschadelijk omdat `resolve` alleen koppelt bij precies één treffer, en ze staan "
            "op runlijsten van Run A — niets om hier te veranderen, wel om op te schrijven."
        ),
        "VIER_VAN_DE_VIJF_COMPETITIES_ZONDER_xG_SPELEN_VANDAAG": (
            "Czech First League (122), Croatian HNL (252), Hungarian NB I (212) en Romanian "
            "SuperLiga (189) staan in coverage.json met has_xg=false en idcheck.py bevestigt dat "
            "per competitie; de vijfde (Keuken Kampioen Divisie, 111) speelt vandaag niet. Die "
            "vier draaien op doelpunten als sterktemaat en komen dus altijd op LIGHT uit, met een "
            "lat van 16,0 pp (prompts/run-b.md); ze hebben bovendien geen sportkey bij The Odds "
            "API, dus hun prijs is het gratis BetExplorer-marktgemiddelde waar de bookmaker niet "
            "herleidbaar is en de edge systematisch te laag uitvalt (§1a). Samen 10 van de 44 "
            "duels, op beide assen de zwakste van de dag — en uitgerekend daar staat de enige "
            "LIGHT-regel van vandaag: Nyíregyháza – Debrecen, op een marktgemiddelde over MAAR "
            "DRIE BOEKEN. Dat is de dunste prijsbasis van alle vier de regels en het hoort bij de "
            "bet te staan. Neem dekking nooit over van een andere competitie in hetzelfde land."
        ),
        "ACHT_VAN_DE_44_DUELS_KOMEN_OP_NONE_UIT_EN_DAT_IS_DE_PRIJS_VAN_EEN_PROMOVENDUSRIJKE_ZONDAG": (
            "Acht van de 44 duels komen op data_tier = NONE uit, allemaal langs de omrekening van "
            "§4, en omdat de cap vandaag niets afkapt blijven er 36 duels met kandidaten over. "
            "Twee vormen: VIER omdat er geen gemeten factor voor het divisiepaar is — Hongarije "
            "heeft bij Fotmob geen tweede divisie (Zalaegerszeg – Vasas Budapest, Kispest Honvéd – "
            "Paksi SE, §4 'Voor Hongarije is er geen factor'), en bij Série A (BRA) ligt Série B "
            "eronder zonder gemeten factor (Athletico Paranaense – Remo); en VIER omdat de "
            "omrekening buiten het gemeten bereik valt of de ploeg niet in de divisie erboven "
            "staat (Celta Fortuna – Real Valladolid, Girona – Eibar, Arezzo – Padova, Energie "
            "Cottbus – Hertha BSC, Karlsruher SC – VfL Osnabrück). Dat is geen defect: §4 schrijft "
            "NONE voor zodra er geen onafhankelijke kansbron op de juiste schaal is, en NONE "
            "betekent GEEN BET en niet 'LIGHT met lage confidence' (§2)."
        ),
        "EEN_POORT_VANGT_DRIEKWART_VAN_ALLES_WEG_EN_DAT_IS_POORT_5": (
            "Over de 36 duels met kandidaten zijn 390 selecties doorgerekend, verdeeld over alle "
            "zes de markten: 136 Over/Under, 92 1X2, 83 Asian Handicap, 42 BTTS, 23 Draw No Bet en "
            "14 Double Chance. Daarvan sneuvelden er 291 op poort 5 ('data conflicterend' — de twee "
            "methodes verslaan de markt niet dezelfde kant op), oftewel 75% van alles; daarna 56 op "
            "de edge-afkapping, 14 op poort 8 (underdog), 13 op de koersband, 6 op poort 7 "
            "(context) en 3 op poort 6 (robuustheid). Poort 9 hield NUL selecties tegen. ZEVEN "
            "selecties hielden alle poorten open, en die zeven zitten in drie wedstrijden — de "
            "0-of-1-bet-regel maakt daar drie regels van en de vierde komt op rangorde erbij. Twee "
            "duels sneuvelden op poort 7 (FC Zürich – St. Gallen, waar St. Gallen 41% van de "
            "selectiewaarde mist tegen 25% bij Zürich; Nashville SC – FC Cincinnati, 3 dagen rust "
            "tegen 15) en één op poort 6 (Vancouver Whitecaps – Real Salt Lake). De ruwe "
            "dagranglijst wordt aangevoerd door Brommapojkarna – Halmstads BK, dat op poort 5 "
            "sneuvelde en dus NIET in de lijst staat — lees die lijst als een meting en niet als "
            "een tip (§5a)."
        ),
        "CHICAGO_FIRE_SPEELT_NIET_IN_SOLDIER_FIELD_EN_DAT_HOORT_ER_OOK_BIJ_ALS_DE_POORT_OPENGAAT": (
            "context.check_venue sloeg vandaag bij één duel aan: Chicago Fire FC – Charlotte FC "
            "wordt gespeeld in SeatGeek Stadium (Bridgeview, Illinois) en niet in Soldier Field, "
            "het genoteerde eigen stadion. §1c eist dat een verplaatsing in het runrapport staat "
            "ÓÓK als de poort opengaat, want thuisvoordeel is de aanname waar het model het "
            "zwaarst op leunt. De poort gaat hier open omdat er geen materieel nadeel op de "
            "beschikbaarheid staat (0% tegen 0%), en het duel levert geen regel: +6,74 pp onder "
            "een lat van 8,0. Wat deze controle NIET vangt blijft staan zoals §1c het beschrijft: "
            "een fixture die van eigenaar is gewisseld is nieuws en geen data."
        ),
    }
