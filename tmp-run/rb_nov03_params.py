"""De `parameters`-tekst van Run B, 3 nov 2026 — apart gehouden zodat `rb_nov03_publiceer.py`
alleen de rekenlogica van 2 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **DE NIVEAUCORRECTIE `model.LEVEL_SCALE` BINDT VANDAAG VOOR HET EERST, EN HET RUN B-SCRIPT GAF
  `today` NIET MEE.** §6g punt 2 eist `analyze_match(..., today=DAY)` en
  `robustness_check(..., today=DAY)` bij élke aanroep; het Run A-script van vandaag doet dat op
  negen plekken en het Run B-script — overgenomen van 2 november, de dag waarop de knop nog niet
  bond — op nul. Dat is **exact dezelfde faalvorm als gisteren**, toen `promotion.match_tier`
  alleen in het Run A-script bleek te zitten: een reparatie die in één van de twee runscripts
  landt. De negen aanroepen zijn vóór de analyse gerepareerd; zonder die ingreep had deze run
  stil met de ongecorrigeerde lambdas van 2 november gerekend.
* **Er is één gepubliceerde regel en die haalt zijn lat niet.** Sirius – Halmstads BK, Under 3,5
  @1,99, +5,72 pp op een FULL-lat van 8,0. Hij staat er dus op RANGORDE (§5b) en niet op gevonden
  voordeel, en hij staat op de Under-kant — de enige kant waarvan §6g op uitkomsten heeft gemeten
  dat ze structureel verliest (FULL-Unders −28,2% over 66 picks, en de band 0–8 pp waarin deze
  regel valt staat op −34,1% over 26 gevallen).
* **De edge komt vrijwel volledig uit de splitsmethode, de scheefste van de twee.** xG-methode
  +0,77 pp, splitsmethode +22,72 pp, zwakste stand van het (shrink, rho)-grid +0,77 pp. Poort 6
  staat dus op een haar open, en §1f/§6e wijzen juist de splitsmethode aan als de samengedrukte
  schatter die maar voor 20% mag meewegen.
* **De tweede bron is het eens met de richting, en dat is geen steun maar een waarschuwing.**
  Pinnacle zet `P(Under 3.5)` op 48,2% waar de eigen xG-methode op 51,0% staat: +2,84 pp erboven,
  dezelfde kant als de gemeten scheefstand. Wel veel kleiner dan de +7,46 pp van gisteren, en dat
  is precies wat de niveaucorrectie hoort te doen.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0262, b=0,0169 op "
            "6927 afgerekende gevallen, fitted_through 2026-11-02. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (Sec. 6b-5c eist die controle aan dit ene "
            "getal). De fit staat vrijwel op de identiteit en VERHOOGT een kans licht over de hele "
            "speelbare band: het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET "
            "ALS 'het model is goed gekalibreerd en dus goed': het is gekalibreerd op de "
            "ONGESELECTEERDE ijksteekproef (Sec. 1g, 20 sep 2026), en de scheefstand die telt zit in "
            "de GESELECTEERDE groep. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_NIVEAUCORRECTIE_BINDT_VANDAAG_VOOR_HET_EERST_EN_DIT_SCRIPT_GAF_today_NIET_MEE": (
            "DIT IS DE BEVINDING VAN DEZE RUN EN ZE IS DEZELFDE ALS DIE VAN GISTEREN, IN EEN ANDERE "
            "GEDAANTE. model.LEVEL_SCALE = 1.032 is op 2 nov 2026 op besluit van de gebruiker "
            "ingevoerd en bindt vanaf 3 november (model.LEVEL_SCALE_BINDS_FROM), dus vandaag voor het "
            "eerst. Sec. 6g punt 2 schrijft erbij: geef `today` mee met de rundag bij ELKE aanroep van "
            "analyze_match en robustness_check, want zonder dat argument kijkt level_scale naar de "
            "systeemklok en krijgt een HERBEREKENING van een oudere dag stil de correctie van vandaag. "
            "Het Run A-script van vandaag doet dat op negen plekken. Dit Run B-script is overgenomen "
            "van 2 november — de dag waarop de knop nog NIET bond, dus de dag waarop het verschil "
            "nul was — en gaf `today` op geen enkele plek mee. Dat is exact de faalvorm van gisteren, "
            "toen promotion.match_tier alleen in het Run A-script bleek te zitten en in dit script "
            "niet: een reparatie die in een van de twee runscripts landt en in het andere niet, en "
            "die niet klaagt. De negen aanroepen (vier analyze_match, vijf robustness_check) zijn "
            "VOOR de analyse gerepareerd. Wat het verschil maakt, nagerekend op de enige "
            "gepubliceerde regel van vandaag: met de correctie staat Sirius – Halmstads BK Under 3,5 "
            "op P(U3.5) = 51,01% in de xG-methode en +5,72 pp edge; zonder de correctie op 53,41% en "
            "+7,67 pp. De correctie haalt er dus 1,95 procentpunt af en wijst daarmee de "
            "VOORZICHTIGE kant op, precies zoals Sec. 6g belooft (meer verwachte doelpunten = lagere "
            "P(Under) = minder Under-bets). De gepubliceerde lijst verandert er niet door: +7,67 pp "
            "haalt de lat van 8,0 ook niet en de rangorde heeft maar een kandidaat."
        ),
        "EEN_REGEL_OP_RANGORDE_EN_HIJ_STAAT_OP_DE_SLECHTST_GEMETEN_KANT": (
            "LEES DIT VOORDAT ER IETS WORDT INGEZET. De dagranglijst van Sec. 5b bestaat vandaag uit "
            "EEN regel: Sirius – Halmstads BK, Under 3,5 @1,99 (Pinnacle via The Odds API), +5,72 pp "
            "op FULL-data. De lat van Sec. 0 is 8,0 pp en die haalt hij niet, dus hij staat er op "
            "rangorde en de drempel gaat als label mee (Sec. 5b). Poort 9 houdt hem NIET tegen, en "
            "dat is geen vergeetachtigheid maar de constructie: die poort bindt uitsluitend in de "
            "band 8-10 pp, want onder 8,0 is `edge` de bindende poort en zou poort 9 anders de reeks "
            "`doelpunten_onder` vullen met kandidaten die nooit een bet konden worden (zie "
            "unders.check, en Sec. 1h over dezelfde twee-populaties-fout). Waar de regel WEL in valt is "
            "de band 0-8 pp van Sec. 6g, en die staat op -34,1% over 26 afgewikkelde FULL-Unders; de "
            "hele FULL-Under-reeks staat op -28,2% over 66. Dit is dus de best scorende selectie van "
            "een dag met zes duels, niet een gevonden voordeel — en ze staat op de enige kant waarvan "
            "op UITKOMSTEN is gemeten dat het model er structureel naast zit."
        ),
        "DE_EDGE_KOMT_VRIJWEL_VOLLEDIG_UIT_DE_SPLITSMETHODE": (
            "Sec. 5 eist alle drie de getallen per selectie, en bij deze regel vertellen ze een "
            "verhaal dat het ene getal `edge_pp` verbergt. xG-methode +0,77 pp, splitsmethode "
            "+22,72 pp, zwakste stand van het (shrink, rho)-grid +0,77 pp. De xG-methode verslaat de "
            "markt dus met nog geen procentpunt en poort 6 staat op een haar open; de +5,72 pp komt "
            "er doordat de splitsmethode 73,0% kans op Under 3,5 geeft tegen 51,0% voor de "
            "xG-methode, en voor 20% meeweegt (Sec. 1f). Dat is wrijvend met wat Sec. 1d en Sec. 6e over "
            "die methode hebben gemeten: ze is de samengedrukte schatter, ze staat op longshots te "
            "hoog en op favorieten te laag, en ze is daarom op 5 sep 2026 van 50% naar 20% gewicht "
            "gegaan. Haar rol is VETO (poort 5), niet aanjager. Een edge die alleen bestaat doordat "
            "de 20%-arm 22 procentpunt van de markt af staat, hoort met argwaan gelezen te worden. "
            "De splitslambdas (1,949 / 0,680, samen 2,63 doelpunt) liggen bovendien ruim onder die "
            "van de xG-methode (2,810 / 0,814, samen 3,62) — en de niveaucorrectie van vandaag raakt "
            "met opzet alleen die tweede (Sec. 6g punt 1), dus dit verschil is niet kleiner geworden."
        ),
        "PINNACLE_IS_HET_EENS_MET_DE_RICHTING_MAAR_MINDER_DAN_GISTEREN": (
            "De scherpste bookmaker van de markt (Sec. 3 Stage 5, stap 2) zet de Under-kant van de "
            "gepubliceerde regel LAGER dan het eigen model: P(Under 3,5) 48,2% tegen 51,0% voor de "
            "eigen xG-methode, +2,84 pp erboven, bij een Pinnacle-marge van 4,3% en op een ZUIVERE "
            "halve lijn (geen push). Dat is dezelfde richting als de scheefstand die Sec. 6g op "
            "uitkomsten meet. Twee dingen die erbij horen. Het is veel KLEINER dan gisteren "
            "(+7,46 pp over drie zuivere halve lijnen) en dat is precies wat de niveaucorrectie "
            "hoort te doen - een eerste, zwakke aanwijzing dat de knop werkt, op een enkele "
            "waarneming en dus geen meting (Sec. 6d eist ~30). En over alle vier de toetsbare (duel, "
            "lijn)-paren is het gemiddelde +0,38 pp op 2 van de 4, waar de pushlijnen juist ONDER "
            "Pinnacle staan (-0,43 pp op 3 paren). Op 1X2 staat het model gemiddeld 4,97 pp van het "
            "Pinnacle-oordeel af over vier duels, met Northampton - Oldham als uitschieter: Pinnacle "
            "maakt Northampton favoriet (41,4% tegen 29,1%) en het model Oldham (43,7% tegen 28,3%), "
            "een verschil van ruim 14 procentpunt op de uitwinst - en dat is uitgerekend het duel "
            "waarvan poort 8 alle drie de bovenste selecties heeft tegengehouden."
        ),
        "DE_MARKTVORMTELLING_STEUNT_EEN_KANT_EN_NIET_DE_ANDERE": (
            "Sec. 4 eist dat de telling wordt genoemd ook (juist) als ze de bet tegenspreekt, en "
            "vandaag doet ze beide tegelijk - per ploeg verschillend. Halmstads BK STEUNT de Under "
            "ruim: 22 van 26 duels dit seizoen onder 3,5 (85%, gemiddeld 2,58 doelpunt), in uitduels "
            "11 van 13 (85%, 2,77) en in de laatste vijf 4 van 5. Sirius SPREEKT HEM TEGEN: 15 van 26 "
            "onder 3,5 (58%, gemiddeld 3,46) en in eigen huis 7 van 13 (54%) met een gemiddelde van "
            "3,62 doelpunt per duel - vrijwel exact de lijn waarop gespeeld wordt. De laatste vijf "
            "duels van Sirius steunen hem wel (4 van 5, gemiddeld 2,60). Beide ploegen samen zitten "
            "dus rond de 3,1 doelpunt per duel waar het model op 3,62 uitkomt in de xG-methode; de "
            "telling is dus niet eensluidend en dat hoort in de voorbeschouwing te staan."
        ),
        "GEEN_GEKWALIFICEERDE_SELECTIE_BUITEN_DE_LIJST": (
            "De afkapping op LIJSTLENGTE bindt vandaag niet: er is geen enkele selectie die alle "
            "poorten EN zijn drempel haalt, dus er valt niemand buiten de lijst. De lijst heeft drie "
            "plekken (MAX_SHORTLIST = 3 op ma-do) en er is een kandidaat die de zeven overgebleven "
            "poorten haalt. De reeks `lijstlengte` groeit vandaag niet."
        ),
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "6 duels in vier van de zeventien competities op een DINSDAGcap van 40 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. Dertien competities hebben niets op de kalender: dat is GEEN WEDSTRIJD "
            "en geen gat (Sec. 3 Stage 2), en het is bij een tweede bron nagetrokken (zie hieronder). "
            "De datarijkdom liep van 5,25 tot 6,5 over de hele run; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg."
        ),
        "TWEE_BRAZILIAANSE_DUELS_OP_NONE_EN_DAT_IS_DE_JUISTE_UITKOMST": (
            "Chapecoense - Mirassol en Internacional - Coritiba komen beide op data_tier = NONE uit, "
            "en dus op GEEN BET. De reden is per duel een promovendus die niet in de stand van 2025 "
            "staat - Chapecoense en Coritiba promoveerden uit de Serie B - en `prompts/run-b.md` zegt "
            "daar expliciet over: bij Serie A (BRA) ligt Serie B eronder, maar er is GEEN GEMETEN "
            "FACTOR voor dat divisiepaar, dus een Braziliaanse promovendus komt op NONE uit. Dat is "
            "geen gat in de administratie en geen openstaand werk: een gepoolde factor erop zetten "
            "zou het gat wel dichten en is precies wat Sec. 2 en Sec. 4 verbieden (dezelfde regel als bij "
            "Kroatie en Hongarije). De twee duels staan daarom als BUITEN DATADEKKING in de "
            "dekkingstabel en er valt geen markt voor door te rekenen."
        ),
        "DE_TWEEDE_BRON_IS_HET_OVER_ALLE_ZEVENTIEN_COMPETITIES_EENS": (
            "Sec. 1 eist bevestiging door een tweede methode op de vraag WELKE wedstrijden er zijn, "
            "en vandaag is er geen enkele afwijking: BetExplorer geeft voor alle zeventien "
            "competities exact hetzelfde aantal duels in het inzetvenster als de Fotmob-daglijst, "
            "6 tegen 6, met de eerstvolgende ronde van de dertien stille competities erbij (5 t/m "
            "14 november). 'Niet in de daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven "
            "zonder tweede bron - dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte."
        ),
        "MARKTBALANS_OP_DE_INKOOP_GEHAALD": (
            "Sec. 1a eist dat geen enkele run voor de hele runlijst maar een soort markt koopt. Alle "
            "VIER de competities die vandaag spelen hebben een sportkey bij The Odds API "
            "(Allsvenskan, English League One, English League Two en Serie A BRA), dus alle vier "
            "kregen de bulk-aanroep met h2h + spreads + totals: per competitie zowel een "
            "uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U). Dat is 4 van 4 en niet "
            "1 van 12 zoals op 30 augustus - de controle slaagt dus ruim en niet op een haar. "
            "Daarna is BTTS in een tweede ronde gekocht voor de vier duels met een kandidaat-edge "
            "(2 credits per duel). Totaal 12 + 4 = 16 credits van een plafond van 353, bij 19824 "
            "credits over en 28 dagen tot de maandwissel."
        ),
    }
