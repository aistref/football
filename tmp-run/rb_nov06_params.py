"""De `parameters`-tekst van Run B, 6 nov 2026 — apart gehouden zodat `rb_nov06_publiceer.py`
alleen de rekenlogica van 5 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **EEN gepubliceerde regel, en hij staat op de UNDER-kant** — precies de kant waarvan §6g een
  gemeten scheefstand kent. `margins.py goalbias` meet die scheefstand vandaag harder dan ooit:
  +0,614 doelpunt per duel boven de eigen lambda over 126 gespeelde Unders, z = +4,16.
* **Poort 9 houdt hem NIET tegen, en dat is de regel en geen omissie.** `unders.check` bindt
  alleen in de band tussen 8,0 en 10,0 pp; met +5,47 pp is `edge` de bindende poort, en die is
  sinds §5b een label en geen veto.
* **Pinnacle zet deze Under 7,07 pp lager dan het eigen model.** Dat is het grootste verschil
  van de vier toetsbare duels en het hoort bij de bet genoemd.
* **De bevestigingscontrole van §1 is gerepareerd en vond meteen iets.** Het inzetvenster in
  `rb_nov06_bevestiging.py` wordt nu uit `DAY` afgeleid in plaats van hardgecodeerd; in de versie
  van 5 november stonden nog de datums van 4 november.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0253, b=0,0164 op "
            "7107 afgerekende gevallen, fitted_through 2026-11-05. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal; deze run heeft er zelf 3 waarnemingen mee afgewikkeld). De fit staat vrijwel op "
            "de identiteit en VERHOOGT een kans licht over de hele speelbare band: +0,4 pp op 50%, "
            "+0,8 pp op 70%. Het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT "
            "NIET ALS 'het model is goed gekalibreerd en dus goed': het is gekalibreerd op de "
            "ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in de "
            "GESELECTEERDE groep. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "EEN_REGEL_OP_RANGORDE_EN_HIJ_HAALT_ZIJN_EIGEN_LAT_NIET": (
            "LEES DIT EERST. De enige gepubliceerde regel is Hammarby - Elfsborg, Under 3 @1,93 "
            "(Coolbet, The Odds API), FULL, modelkans 57,28% tegen een marktkans van 51,81%, dus "
            "+5,47 pp herijkt en +4,90 pp ruw. DAT IS ONDER DE LAT VAN 8,0 pp. Hij staat er op "
            "RANGORDE (§5b, 20 sep 2026): de drempel snijdt sinds die datum aan het eind van de "
            "dag en alleen wanneer er MEER selecties boven de lat staan dan er regels in de lijst "
            "passen. Vandaag staat er geen enkele selectie boven de lat, dus bepaalt de rangorde "
            "de lijst en gaat de drempel als LABEL mee. Lees deze regel dus als 'het beste van "
            "vandaag' en niet als 'een gevonden voordeel' - dat onderscheid is de hele reden dat "
            "§5b mag, want §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op "
            "de herijkte edge bestaat die geld oplevert. De lijst heeft vandaag VIJF plekken "
            "(MAX_SHORTLIST = 5 op vrijdag) en EEN regel; MAX_LIGHT_IN_SHORTLIST (2) en de "
            "afkapping op LIJSTLENGTE binden dus geen van beide, en de reeks `lijstlengte` groeit "
            "vandaag niet."
        ),
        "DE_GEPUBLICEERDE_REGEL_STAAT_OP_DE_UNDER_KANT_EN_DIE_KANT_STAAT_SCHEEF": (
            "DIT IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG en §6g eist dat het bij de bet staat. "
            "De Under-kant is de enige markt-en-kant waarvan op UITKOMSTEN is gemeten dat de "
            "routine er structureel naast zit, en de meting is vandaag harder dan bij de invoering "
            "van poort 9: `margins.py goalbias` geeft over 126 gespeelde Unders +0,614 doelpunt per "
            "duel MEER dan de eigen lambda zei, z = +4,16 (op 11 okt 2026 was dat +0,68 over 49 "
            "duels bij z = +2,91). Op de Over-kant gebeurt dat niet (66 duels, -0,268, z = -1,19). "
            "Daarbovenop staat de vormfout: P(Under 3.0) staat over 2033 duels 1,6 pp te hoog "
            "(voorspeld 64,1%, werkelijk 62,6%). Van de +5,47 pp geclaimde edge gaat dus ruwweg "
            "anderhalf procentpunt al op aan een gemeten fout die niets met Hammarby of Elfsborg "
            "te maken heeft. DAT MAAKT DE BET NIET ONGELDIG - hij staat op rangorde en niet op een "
            "belofte - maar het hoort erbij te staan en het staat in de `why`-tekst van het "
            "dagrapport."
        ),
        "POORT_9_HOUDT_HEM_NIET_TEGEN_EN_DAT_IS_DE_REGEL": (
            "De vraag dringt zich op: waarom laat poort 9 een Under op FULL met +5,47 pp door, als "
            "de verzwaarde lat 10,0 pp is? OMDAT DIE POORT MET OPZET ALLEEN IN DE BAND TUSSEN DE "
            "TWEE LATTEN BINDT. `unders.check` geeft letterlijk terug: 'Under met +5.47 pp - onder "
            "de gewone drempel van 8.0 pp, dus `edge` is de bindende poort en niet poort 9'. De "
            "reden staat in de code met de meting erbij: zou poort 9 ook de kandidaten claimen die "
            "de gewone drempel al niet halen, dan loopt de reeks `doelpunten_onder` vol met rijen "
            "die nooit een bet konden worden en meet ze niets meer - exact de 'twee "
            "populaties'-fout die §1e bij `underdog_ruw` en §5b bij `lijstlengte` benoemt. Op 11 "
            "okt 2026 ging het om 44 gemarkeerde selecties zonder die regel en om 4 met. Poort 9 "
            "heeft vandaag dus NUL selecties geblokkeerd, en dat is geen stilstand maar zijn "
            "ontwerp. Wat hier wél bij hoort: onder §5b kan een Under op de rangorde worden "
            "gepubliceerd die poort 9 zou hebben geblokkeerd als hij tussen 8 en 10 pp had "
            "gestaan. Dat is een bekende grens van de constructie (dezelfde als bij de LIGHT-Under "
            "van Run A op 12 oktober) en geen nieuwe bevinding; de run verzet die poort niet op "
            "eigen initiatief (§1h, §6g)."
        ),
        "PINNACLE_ZET_DEZE_UNDER_7_PP_LAGER_DAN_HET_MODEL": (
            "Stage 5 stap 2 (§3) zet de de-vigde prijs van de scherpste bookmaker naast de eigen "
            "kans, LOS van de beste prijs waarop gespeeld wordt. Op de gepubliceerde regel is dat "
            "het grootste verschil van de dag: Pinnacle zet P(Under 3,0) voor "
            "Hammarby - Elfsborg op 50,3% en het eigen model op 57,3%, een verschil van +7,07 pp "
            "bij een Pinnacle-marge van 4,2%. Het is een HELE lijn, dus met een push van 0,224 bij "
            "exact drie doelpunten - bij 3-0, 2-1, 1-2 of 0-3 komt de inzet terug. Over de vier "
            "toetsbare (duel, lijn)-paren staat het model gemiddeld +1,56 pp boven Pinnacle op de "
            "Under-kant, en 3 van de 4 erboven; uitgesplitst naar lijnsoort: twee ZUIVERE halve "
            "lijnen op -1,77 pp en twee lijnen MET push op +4,90 pp. Op 1X2 staat het model "
            "gemiddeld 3,85 pp van het Pinnacle-oordeel af over vier duels (marge 4,18%), met het "
            "grootste gat bij Rapid Wien - Wolfsberger AC (+7,60 pp meer thuiszege dan Pinnacle). "
            "HARDE GRENS (§2/§4): geen van deze getallen gaat in my_prob of in prob_sources; het is "
            "andermans lezing en het is marktafgeleid."
        ),
        "POORT_5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
            "Van de 83 doorgerekende selecties sneuvelen er 68 op POORT 5, de bevestiging door een "
            "tweede methode (§1, voorwaarde 5) - 82% van alles. De rest: 6 op `edge`, 6 op de "
            "koersband, 2 op robuustheid en 1 op poort 8. Het duidelijkste geval is Helmond Sport - "
            "FC Volendam, dat met +8,86 pp herijkt de hoogste edge van de dag had op de "
            "LIGHT-populatie: de xG-methode verslaat de markt daar met +12,17 pp en de "
            "splitsmethode met -6,56 pp, dus ze wijzen tegengesteld en de bet gaat eruit. DAT IS DE "
            "POORT DIE GELD BESPAART: `shadow.py stats` meet `tweede_methode` vandaag op -2,0% over "
            "254 afgewikkelde kandidaten. Het is ook de poort waarvan §5 waarschuwt dat hij "
            "structureel alles kan wegvangen; 82% op EEN dag is geen reeks (§6d eist ~30), maar het "
            "is het vermelden waard dat het de derde dag op rij is dat deze poort de grootste groep "
            "wegvangt."
        ),
        "DRIE_NEAR_MISS_RIJEN_EN_EEN_POORT_8_RIJ": (
            "§5 eist een 'Net niet'-regel voor elke afgewezen kandidaat met een echte edge, en "
            "vandaag zijn het er drie: Hammarby - Elfsborg (Under 3, nu een gepubliceerde bet en "
            "daarom hernoemd naar `near_miss_gepubliceerd`), Helmond Sport - FC Volendam (1X2 "
            "Volendam @2,33, +8,86 pp, valt af op `tweede_methode`) en Vitoria - Fluminense (BTTS "
            "nee @2,08, +4,50 pp, valt af op `robuustheid` met een zwakste grid-stand van "
            "-0,35 pp). Daarnaast gaat er EEN rij als `underdog` het schaduwlogboek in: UTA Arad - "
            "Petrolul Ploiesti, 1X2 Petrolul @4,15, +10,17 pp herijkt op een marktkans van 24,1% - "
            "ruim onder UNDERDOG_FLOOR = 0,35, dus poort 8 gaat dicht. Dat is de hoogste edge van "
            "de hele dag en hij staat op precies de kant waar het model aantoonbaar te optimistisch "
            "is. De reeks `underdog` staat nu op 307 afgewikkelde gevallen met -3,8%: negatief, dus "
            "de poort doet zijn werk, en er is geen grond om de vraag van 5 oktober opnieuw te "
            "stellen (§1e: niet elke dag opnieuw vragen)."
        ),
        "DE_BEVESTIGINGSCONTROLE_IS_GEREPAREERD_EN_VOND_METEEN_IETS": (
            "§1 eist bevestiging door een tweede methode op de vraag WELKE wedstrijden er zijn, en "
            "die controle stond stil groen op het verkeerde etmaal. `rb_nov06_bevestiging.py` "
            "leidde het inzetvenster af uit twee HARDGECODEERDE datumparen, en in de versie van "
            "5 november stonden daar nog die van 4 november: het venster toetste "
            "[4.11 07:00, 5.11 07:00) UK terwijl de rundag 5 november was. Zestien van de zeventien "
            "competities kwamen daardoor op `fotmob=0 bx=0` uit en de controle meldde 'eens: 17 van "
            "17' - groen, over de verkeerde dag. Dezelfde stille faalstand als het Serie B-id "
            "(`run-b.md`), `calibration.py settle` (§6b-5c) en de `\\s+`-regex in datzelfde script: "
            "een controle die niet klaagt omdat hij de verkeerde grootheid meet. Het venster komt "
            "sinds vandaag uit `DAY` en kan niet meer achterlopen. EN HIJ VOND METEEN EEN "
            "AFWIJKING: 16 van 17 eens, met Segunda Division (ESP) op fotmob=0 tegen bx=1 - zie de "
            "volgende sleutel."
        ),
        "CASTELLON_EIBAR_IS_UITGESTELD_EN_DAAROM_STAAT_SEGUNDA_OP_GEEN_WEDSTRIJD": (
            "De enige afwijking tussen de twee bronnen is nagetrokken en Fotmob heeft het goed. "
            "BetExplorer noteert Castellon - Eibar vandaag om 20:30 UK, en de Fotmob-daglijst heeft "
            "dat duel OOK (id 5868528, aftrap 2026-11-06T19:30Z = 20:30 NL) - maar met "
            "`status.cancelled = true` en `reason.long = 'Postponed'`. `runwindow.matches_for_run` "
            "laat een afgelast of uitgesteld duel eruit vallen, zoals zijn docstring voorschrijft, "
            "dus Segunda Division komt op nul duels in het inzetvenster uit. De BetExplorer-"
            "fixturepagina heeft het uitstel nog niet verwerkt. De status is daarmee GEEN WEDSTRIJD "
            "en niet BUITEN DATADEKKING: er is geen kansbron weggevallen, er is geen wedstrijd. "
            "DIT IS DE EERSTE KEER DAT DEZE CONTROLE IETS HEEFT GEVONDEN sinds hij bestaat, en hij "
            "vond het op de ochtend dat hij werd gerepareerd - zonder de reparatie had hier "
            "'fotmob=0 bx=0, eens' gestaan en was het uitstel onzichtbaar gebleven."
        ),
        "DRIE_DUELS_OP_NONE_EN_ALLE_DRIE_OM_EEN_VOORGESCHREVEN_REDEN": (
            "Drie van de zestien duels komen op data_tier = NONE uit en worden dus niet "
            "geanalyseerd (§2). ALLE DRIE om een reden die in de regels staat en geen van de drie "
            "is een storing: (1) NK Lokomotiva - Rudes, Croatian HNL - Rudes is promovendus en "
            "Fotmob HEEFT de Kroatische tweede divisie niet; §4 noemt dat 'niet nog niet gemeten "
            "maar niet meetbaar op deze bron' en een gepoolde factor erop zetten is verboden. "
            "(2) Ascoli - Palermo, Serie B - Ascoli staat niet in de Serie A-stand van 2025/2026 en "
            "moet dus uit de divisie ERONDER komen; die tak bestaat niet in TIER2 voor Serie B. "
            "(3) Eintracht Braunschweig - Energie Cottbus, 2. Bundesliga - zelfde geval, Cottbus "
            "komt uit de 3. Liga en dat divisiepaar is niet gemeten. Van alle drie is de context "
            "wel opgehaald en gelogd (§1c eist dat ook bij tier NONE). WAT DAT MET DE DEKKINGSTABEL "
            "DOET, per competitie en niet per duel: 2. Bundesliga heeft een TWEEDE duel dat wel is "
            "doorgerekend (Dynamo Dresden - Greuther Furth) en staat dus op GEANALYSEERD, maar "
            "Croatian HNL en Serie B hebben vandaag maar EEN duel en dat staat op NONE - die twee "
            "krijgen daarom BUITEN DATADEKKING, met de bron en de reden erbij. Dat is de juiste "
            "status en niet AFGEKAPT: de cap heeft niets aangeraakt (zie hieronder), er is geen "
            "werkende onafhankelijke kansbron op het niveau waarop gespeeld wordt. Die regel is op "
            "25 okt 2026 expliciet zo vastgelegd nadat Croatian HNL om precies deze reden ten "
            "onrechte AFGEKAPT kreeg."
        ),
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "16 duels in acht van de zeventien competities op een VRIJDAGcap van 55 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. De datarijkdom liep van 5,0 tot 8,0; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg. Negen "
            "competities hebben niets op de kalender: dat is GEEN WEDSTRIJD en geen gat (§3 Stage "
            "2), en het is bij BetExplorer als tweede bron nagetrokken. Alle zestien duels staan "
            "op `playable = True` en komen van de daglijst van de rundag zelf; er is vandaag geen "
            "enkel duel dat via de daglijst van morgen binnenkwam, ook niet bij Serie A (BRA) - "
            "Vitoria - Fluminense trapt om 00:00 NL af en staat op de lijst van 6 november."
        ),
        "VIJF_VAN_DE_ACHT_COMPETITIES_HEBBEN_GEEN_XG_OF_GEEN_BESTE_PRIJS": (
            "Drie van de acht spelende competities hebben GEEN xG bij Fotmob - Croatian HNL (252), "
            "Romanian SuperLiga (189) en Keuken Kampioen Divisie (111) - en draaien op doelpunten "
            "als sterktemaat; ze komen dus altijd op LIGHT uit, met een lat van 16,0 pp "
            "(`prompts/run-b.md`). Dat zijn vandaag 9 van de 16 duels. DEZELFDE DRIE hebben ook "
            "geen sportkey bij The Odds API en draaien op het gratis BetExplorer-marktgemiddelde "
            "(17 boeken), waar de bookmaker niet herleidbaar is en de edge systematisch te laag "
            "uitvalt (§1a) - conservatief, dus geen risico op te veel bets, maar niet "
            "vergelijkbaar met een duel waar de beste prijs wel bekend is. Die negen duels zijn op "
            "beide assen de zwakste van de dag, en er is geen enkele markt buiten 1X2 voor te "
            "koop: AH, DNB, DC, OU en BTTS staan daar alle vijf als 'niet opgevraagd - geen "
            "sportkey' in `markets_checked`, met de reden erbij en niet als gat (§6b-5b). Neem "
            "dekking nooit over van een andere competitie in hetzelfde land: Duitsland heeft xG in "
            "de 2. Bundesliga en Nederland niet in de Keuken Kampioen Divisie."
        ),
        "MARKTBALANS_OP_DE_INKOOP_GEHAALD_MET_MARGE": (
            "§1a eist dat geen enkele run voor de hele runlijst maar een soort markt koopt, en de "
            "controle slaagt met de ruimste marge die hij kan hebben: VIJF van de vijf inkoopbare "
            "competities kregen de bulk-aanroep met h2h + spreads + totals, dus alle vijf hebben "
            "zowel een uitkomstmarkt (1X2 op de beste prijs, Asian Handicap, en waar de lijn er is "
            "DNB en Double Chance) als een doelpuntenmarkt (O/U). `split_budget(393, 5)` gaf 5 "
            "spreads / 5 totals en de bulk paste ruim: 15 van 393 credits. BTTS is in de tweede "
            "ronde gekocht voor de duels die een kandidaat-edge lieten zien (§1a stap 2) - vier "
            "duels kwamen daarvoor in aanmerking, twee kregen hem (Hammarby - Elfsborg en "
            "Vitoria - Fluminense, 2 credits), en bij UTA Arad en Helmond Sport kon het niet omdat "
            "die competities geen sportkey hebben. Totaal 17 van 393 credits, bij 19704 over en 25 "
            "dagen tot de maandwissel. Twee competities missen DNB en DC omdat er geen 0,0- en "
            "geen +0,5-lijn in hun spreads-respons zit; dat is een grens van de bron en staat met "
            "de reden erbij in `markets_checked`."
        ),
        "DE_NIVEAUCORRECTIE_IS_DRIE_DAGEN_OUD_EN_NOG_NIET_TE_LEZEN": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. `gridfit.py measure` zegt vandaag zelf dat de reeks nog "
            "niet te lezen is: 57 van de 1230 homogene duels dragen de correctie al in zich, dus "
            "de regel `scale = 1.032` toetst op die duels een DUBBELE correctie en de gemengde "
            "reeks beantwoordt de vraag niet. De diagnose die eronder ligt staat vandaag op +0,091 "
            "doelpunt per duel (z = +1,80) over 1230 duels, tegen +0,100 (z = +1,93) over 1147 op "
            "2 november - meegegroeid noch weggezakt. ER IS DUS NIETS TE BESLISSEN en de vraag "
            "hoort niet gesteld (§1h, §6g); reken op enkele maanden voordat de reeks van na "
            "3 november groot genoeg is."
        ),
        "POORT_9_HEEFT_ZIJN_MEETLAT_GEHAALD_EN_DE_REEKS_IS_NEGATIEF": (
            "Een reeks die vandaag voor het eerst leesbaar is en die daarom in het runrapport hoort: "
            "`doelpunten_onder` staat op 35 afgewikkelde kandidaten met -30,4% rendement (13 "
            "winnaars op 35, gem. koers 1,95). §1h schreef dat die reeks de vraag moest "
            "beantwoorden of de poort geld bespaart of alleen bets, en eiste er ~30 voor (§6d). Dat "
            "aantal is nu gehaald en het antwoord is DUIDELIJK NEGATIEF: de poort houdt verliezers "
            "tegen en doet zijn werk. Daarmee is er geen aanleiding om hem te verlagen of te "
            "schrappen, en ook geen vraag om aan de gebruiker voor te leggen - §1h noemt als "
            "aanleiding alleen 'de reeks draait van teken' of 'de vormfout is gerepareerd', en geen "
            "van beide is het geval (die vormfout bleek op 28 oktober niet te bestaan). Noem de "
            "stand gewoon, zoals elke andere reeks."
        ),
    }
