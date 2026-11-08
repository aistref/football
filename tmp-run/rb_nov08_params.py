"""De `parameters`-tekst van Run B, 8 nov 2026 — apart gehouden zodat `rb_nov08_publiceer.py`
alleen de rekenlogica van 7 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **ALLE VIER DE OVER/UNDER-REGELS STAAN OP DE UNDER-KANT, en het zijn precies de vier duels waar
  het model het verst boven het Pinnacle-oordeel op die kant staat** (+12,07, +9,38, +12,76 en
  +14,69 pp). Dat is het patroon waar §1g voor waarschuwt.
* **De Under-kant staat vandaag over de HELE populatie boven Pinnacle**: +3,77 pp over 27
  (duel, lijn)-paren, 21 van de 27 erboven. Gisteren was die populatie nog in evenwicht (−0,20 pp).
* **`margins.py goalbias` meet de Under-kant harder scheef dan ooit**: +0,612 doelpunt per duel
  boven de eigen lambda over 130 gespeelde Unders, z = +4,20.
* **Poort 9 heeft vandaag voor het eerst in deze reeks werkelijk geblokkeerd** — vier selecties, en
  drie ervan gingen als `doelpunten_onder` het schaduwlogboek in.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0305, b=0,0197 op "
            "7188 afgerekende gevallen, fitted_through 2026-11-06. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit staat vrijwel op de identiteit en VERHOOGT een kans licht over de hele "
            "speelbare band: +0,2 pp op 40%, +0,5 pp op 50%, +0,8 pp op 60%, +0,9 pp op 70%. Het "
            "ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET ALS 'het model is "
            "goed gekalibreerd en dus goed': het is gekalibreerd op de ONGESELECTEERDE "
            "ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in de GESELECTEERDE "
            "groep — zie `ledger.py stats`, waar het model over 477 afgewikkelde bets 284,2 "
            "winnaars verwachtte en er 220 werden."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "ALLE_VIER_DE_DOELPUNTENREGELS_STAAN_OP_DE_UNDER_KANT_EN_PRECIES_DAAR_WAAR_PINNACLE_LAGER_ZIT": (
            "LEES DIT EERST, WANT HET IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG en §6g eist dat "
            "het bij elke gepubliceerde Under staat. Vier van de vijf regels zijn een Under "
            "(Tromso - Bodo/Glimt Under 3,5, Sandefjord - Molde Under 3,5, Viking - KFUM Under 3,75 "
            "en Virtus Entella - Modena Under 2,5) en de vijfde is een 1X2 (Carrarese - Sampdoria). "
            "DRIE METINGEN DIE ALLE DRIE DEZELFDE KANT OP WIJZEN. (1) `margins.py goalbias` geeft "
            "over 130 gespeelde Unders +0,612 doelpunt per duel MEER dan de eigen lambda zei, "
            "z = +4,20 - de hardste stand van deze reeks (bij de invoering van poort 9 op 11 okt "
            "2026 was dat +0,68 over 49 duels bij z = +2,91, gisteren +0,626 over 127 bij z = "
            "+4,25). Op de Over-kant gebeurt dat niet: 71 duels, -0,359, z = -1,65. (2) De vormfout "
            "staat er bovenop: P(Under 3.5) is over 2150 doorgerekende duels 1,1 pp te hoog "
            "(voorspeld 64,1%, werkelijk 62,9%) en P(Under 2.5) 1,8 pp (42,5% tegen 40,7%). (3) EN "
            "DIT IS NIEUW VANDAAG: op de Pinnacle-toets van Stage 5 stap 2 staat de Under-kant niet "
            "alleen bij de gepubliceerde regels maar over de HELE populatie boven de scherpste "
            "bookmaker: +3,77 pp over 27 (duel, lijn)-paren, met 21 van de 27 erboven. Gisteren was "
            "dat -0,20 pp over 33 paren met 16 van de 33 erboven, oftewel een populatie in "
            "evenwicht waarin alleen de gepubliceerde regels eruit staken. Vandaag is de hele kant "
            "scheef, en de vier gepubliceerde regels zijn precies de vier grootste gaten: Virtus "
            "Entella +14,69 pp, Viking +12,76, Tromso +12,07 en Sandefjord +9,38. DAT IS EXACT HET "
            "PATROON WAAR §1g VOOR WAARSCHUWT - wie selecteert op de grootste edge, selecteert op "
            "de grootste modelfout - en het hoort in het dagrapport bij elke regel te staan. Van de "
            "geclaimde edge van elke Under gaat ruwweg een tot twee procentpunt al op aan een "
            "gemeten fout die niets met deze ploegen te maken heeft. DAT MAAKT DE REGELS NIET "
            "ONGELDIG: alle vier halen ze hun eigen lat van 8,0 pp EN de verzwaarde lat van poort 9 "
            "(10,0 pp op FULL), en alle vier halen ze beide schalen (`bet_beide` = True). Maar het "
            "voorbehoud is vandaag zwaarder dan gisteren en er wordt op grond hiervan geen enkele "
            "lat verzet (§1h, §6d): een dag is geen reeks."
        ),
        "DE_VIJFDE_REGEL_HAALT_ZIJN_LAT_ALLEEN_HERIJKT_EN_NIET_RUW": (
            "Carrarese - Sampdoria (1X2, thuiszege @2,5288, FULL) staat op +8,36 pp HERIJKT en op "
            "+7,94 pp RUW, dus hij haalt de lat van 8,0 op de ene schaal en net niet op de andere: "
            "`bet_ruw` = False en `bet_beide` = False. DAT IS PRECIES HET GEVAL WAARVOOR DIE VLAG "
            "IS GEBOUWD. §5a schreef oorspronkelijk dat een selectie die de herijkte drempel haalt "
            "hem ook ruw haalt, omdat de herijking een kans binnen de koersband altijd VERLAAGDE; "
            "sinds 20 sep 2026 fit `recalibrate.observations()` op de ongeselecteerde ijksteekproef "
            "en VERHOOGT de fit een kans over vrijwel de hele band. Die redenering is dus niet meer "
            "waar, en §5a zegt met zoveel woorden: vertrouw de vlag en niet de redenering. WAT DAT "
            "HIER BETEKENT: de edge is sinds §5b (20 sep 2026) geen poort meer maar een AFKAPPING, "
            "en hij snijdt alleen wanneer er MEER selecties boven de lat staan dan er regels in de "
            "lijst passen. Vandaag staan er VIER boven de lat en passen er VIJF regels in een "
            "zondaglijst, dus bepaalt de rangorde de lijst en gaat de lat als LABEL mee. Carrarese "
            "haalt alle ZEVEN overgebleven poorten op de herijkte schaal - koersband, "
            "anti-circulariteit, datatier, tweede methode, robuustheid, context en underdog - en "
            "staat er op rang 5 van 5. Lees hem dus als 'het beste wat er na de vier Unders nog "
            "stond' en niet als een gevonden voordeel; zijn `selection_score` is 4,004 tegen 7,634 "
            "voor de regel erboven, het grootste gat in de lijst."
        ),
        "POORT_9_BINDT_VANDAAG_VOOR_HET_EERST_WERKELIJK": (
            "Poort 9 (§1h) heeft vandaag VIER selecties geblokkeerd, en dat is nieuw: gisteren "
            "blokkeerde hij er nul en op 12 oktober, zijn eerste bindende dag, ook. De poort bindt "
            "met opzet alleen in de band tussen de twee latten, 8,0 tot 10,0 pp op FULL, en vandaag "
            "zat daar voor het eerst een groepje in - onder meer St. Gallen - Lugano (Under 3,5 "
            "@1,67, +8,80 pp). Drie van die vier gingen als `failed_gate = doelpunten_onder` het "
            "schaduwlogboek in; de vierde was een selectie op een duel dat al een andere "
            "schaduwrij had (§1e punt 2 verbiedt dezelfde wedstrijd twee keer in dezelfde "
            "categorie). DE REEKS STAAT NU OP 36 AFGEWIKKELDE KANDIDATEN MET -32,3% RENDEMENT (13 "
            "winnaars, 36,1% trefkans). Dat is duidelijk negatief, dus de poort houdt verliezers "
            "tegen, doet zijn werk en er is geen aanleiding om hem te verlagen of de vraag aan de "
            "gebruiker voor te leggen (§1h punt 3: pas voorleggen als er iets wezenlijk verandert). "
            "WAT DE POORT VANDAAG NIET DOET: de vier gepubliceerde Unders tegenhouden. Alle vier "
            "staan BOVEN de verzwaarde lat van 10,0 pp (+14,48, +12,26, +12,10 en +11,87) en "
            "passeren dus op eigen kracht. Dat is de constructie en geen omissie."
        ),
        "POORT_5_VANGT_VOOR_DE_VIJFDE_DAG_OP_RIJ_HET_MEESTE_WEG": (
            "Van de 405 doorgerekende selecties sneuvelen er 297 op POORT 5, de bevestiging door "
            "een tweede methode (§1, voorwaarde 5) - 73,3% van alles. De rest: 37 op `edge`, 18 op "
            "context, 15 op poort 8 (underdog), 15 op de koersband, 9 op robuustheid, 4 op poort 9 "
            "(doelpunten_onder), en 10 selecties over 5 wedstrijden haalden alle negen poorten. DAT "
            "IS DE POORT DIE GELD BESPAART: `shadow.py stats` meet `tweede_methode` vandaag op "
            "+0,1% over 271 afgewikkelde kandidaten - vlak, dus de afgewezen groep verliest niet "
            "maar wint ook niet. Dat is zwakker dan de -1,0% van gisteren en het is het vermelden "
            "waard: deze poort vangt vijf dagen op rij de grootste groep weg (77,5% gisteren, 73,3% "
            "vandaag) en zijn eigen reeks staat op break-even. ER WORDT NIETS VERZET - §6d eist een "
            "richting over weken en niet een getal van een dag - maar als die reeks positief draait "
            "bij deze aantallen, is dat een vraag voor de gebruiker en niet voor een run."
        ),
        "VIER_COMPETITIES_OP_GEEN_WEDSTRIJD_EN_MLS_IS_HET_GEVAL_OM_NA_TE_TREKKEN": (
            "English League One, English League Two, MLS (USA) en Serie A (BRA) hebben niets op de "
            "kalender in het inzetvenster. Dat is GEEN WEDSTRIJD en geen gat (§3 Stage 2), maar het "
            "is wel de uitkomst die `prompts/run-b.md` uitdrukkelijk als STILLE FAALSTAND "
            "beschrijft: een fout fotmob_id geeft geen foutmelding maar nul wedstrijden, en nul "
            "wedstrijden leest als GEEN WEDSTRIJD. Daarom op drie manieren nagetrokken. (1) "
            "`scripts/idcheck.py` bevindt alle 33 id's groen, met 108 op 24 ploegen, 109 op 24 en "
            "268 op 20 in 2025/2026 - dat is de controle die juist op de competities draait die "
            "vandaag stil zijn. (2) De tweede bron is het eens: BetExplorer geeft voor alle vier "
            "nul duels in het venster en als eerstvolgende speelronde 13 of 14 november "
            "(`rb_nov08_bevestiging.py`, 17 van 17 competities eens, 44 tegen 44 duels). (3) MLS IS "
            "HET GEVAL WAARVOOR `scripts/runwindow.py` BESTAAT, EN VANDAAG STAAT HET ER OMGEKEERD "
            "IN: de daglijst van 8 november HEEFT zeven MLS-duels, maar ze trapten alle zeven om "
            "01:00 of 01:10 NL af en waren bij de eerste opvraging al afgelopen. Ze vallen dus "
            "buiten het venster [08:00 NL, 08:00 NL + 1 dag) en hoorden bij de run van 7 november, "
            "die ze ook werkelijk heeft doorgerekend en waaruit vier van de vijf regels van die dag "
            "kwamen. Zonder `runwindow.py` had deze run ze als duels van vandaag gezien en vier "
            "bets gepubliceerd op wedstrijden die al gespeeld waren. De reguliere MLS-competitie is "
            "daarmee afgelopen; `api_check.py` meldt de sportkey `soccer_usa_mls` vandaag als NIET "
            "ACTIEF, wat daarbij hoort en geen storing is. De twee Engelse divisies en Serie A (BRA) "
            "spelen weer op 13/14 november - bij de Engelse is de FA Cup-ronde van dit weekend de "
            "verklaring, en dat toernooi hoort bij de runlijst van Run A."
        ),
        "VIJF_DUELS_OP_NONE_EN_ALLE_VIJF_OM_EEN_VOORGESCHREVEN_REDEN": (
            "Vijf van de 44 duels komen op data_tier = NONE uit en worden dus niet geanalyseerd "
            "(§2). ALLE VIJF om een reden die in de regels staat en geen van de vijf is een "
            "storing. DRIE BUITEN HET GEMETEN BEREIK, waar `promotion.conversion_in_range` weigert "
            "- dat is de Coventry-val waarvoor die poort bestaat en geen lacune: Slavia Prague - "
            "Artis Brno (Czech First League), Asteras Tripolis - Kalamata (Greek Super League) en "
            "Girona - Almeria (Segunda Division). EEN ZONDER DIVISIEPAAR ERONDER: LR Vicenza - "
            "Cremonese (Serie B) - LR Vicenza komt uit de Serie C en dat divisiepaar staat niet in "
            "`TIER2`. EEN ZONDER MEETBAAR DIVISIEPAAR: Vasas Budapest - Ferencvaros (Hungarian "
            "NB I) - Fotmob HEEFT de NB II (id 9117) maar dat id negeert de seizoensparameter, dus "
            "`measure_gap` weigert luidruchtig sinds 11 okt 2026. §4 noemt dat 'niet nog niet "
            "gemeten maar niet meetbaar op deze bron' en een gepoolde factor erop zetten is "
            "verboden. Van alle vijf is de context wel opgehaald en gelogd (§1c eist dat ook bij "
            "tier NONE). WAT DAT MET DE DEKKINGSTABEL DOET, per competitie en niet per duel: alle "
            "vijf de betrokken competities hebben OOK duels die wel zijn doorgerekend (Czech First "
            "League 3 van 4, Greek Super League 4 van 5, Segunda Division 2 van 3, Serie B 2 van 3, "
            "Hungarian NB I 2 van 3), dus alle vijf staan op GEANALYSEERD. Geen enkele competitie "
            "krijgt vandaag BUITEN DATADEKKING of AFGEKAPT."
        ),
        "VIJF_VAN_DE_DERTIEN_COMPETITIES_HEBBEN_GEEN_XG_EN_GEEN_BESTE_PRIJS": (
            "Vijf van de dertien spelende competities hebben GEEN xG bij Fotmob - Czech First "
            "League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) en "
            "Keuken Kampioen Divisie (111) - en draaien op doelpunten als sterktemaat; ze komen dus "
            "altijd op LIGHT uit, met een lat van 16,0 pp (`prompts/run-b.md`). Dat zijn vandaag 13 "
            "van de 44 duels. DEZELFDE VIJF hebben ook geen sportkey bij The Odds API en draaien op "
            "het gratis BetExplorer-marktgemiddelde, waar de bookmaker niet herleidbaar is en de "
            "edge systematisch te laag uitvalt (§1a) - conservatief, dus geen risico op te veel "
            "bets, maar niet vergelijkbaar met een duel waar de beste prijs wel bekend is. Die "
            "dertien duels zijn op beide assen de zwakste van de dag, en er is geen enkele markt "
            "buiten 1X2 voor te koop: AH, DNB, DC, OU en BTTS staan daar alle vijf als 'niet "
            "opgevraagd - geen sportkey' in `markets_checked`, met de reden erbij en niet als gat "
            "(§6b-5b). De hoogste edge van die groep was Nyiregyhaza Spartacus - Gyori ETO met "
            "+31,09 pp op de RUWE schaal, en die werd door poort 8 tegengehouden (de markt geeft "
            "Gyori ETO minder dan de ondergrens van 35%); op de herijkte schaal haalde geen enkele "
            "LIGHT-selectie de lat van 16,0. Neem dekking nooit over van een andere competitie in "
            "hetzelfde land: Duitsland heeft xG in de 2. Bundesliga en Nederland niet in de Keuken "
            "Kampioen Divisie, terwijl beide landen het in hun hoogste divisie wel hebben."
        ),
        "ALLE_ZES_MARKTEN_HEBBEN_MEEGEDONGEN_EN_DE_LIJST_KOMT_UIT_DE_DATA": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data, en vandaag komt hij uit de data. De inkoop was zo breed als hij kon zijn: ALLE "
            "ACHT inkoopbare competities kregen de bulk-aanroep met h2h + spreads + totals, dus "
            "alle acht hadden zowel een uitkomstmarkt (1X2 op de beste prijs, Asian Handicap, en "
            "waar de lijn er is DNB en Double Chance) als een doelpuntenmarkt (O/U) - de "
            "marktbalans-controle slaagt dus met acht op acht en niet met de krappe marge waar §1a "
            "voor waarschuwt. BTTS is in de tweede ronde gekocht voor 19 van de 21 duels met een "
            "kandidaat-edge; de twee die het niet kregen (Jablonec - Mlada Boleslav en Nyiregyhaza "
            "Spartacus - Gyori ETO) hebben geen sportkey en staan met die reden in "
            "`markets_checked`. Alle ZES markten hebben werkelijk meegedongen: van de 405 "
            "doorgerekende selecties waren er 142 Over/Under, 103 1X2, 86 Asian Handicap, 38 BTTS, "
            "24 Draw No Bet en 12 Double Chance. Dat vier van de vijf regels uit een markt komen is "
            "dus de uitkomst van `selection_score` over zes concurrerende markten en geen quotum; "
            "bets forceren om een verdeling te halen is precies wat §1 verbiedt. Credits: 24 aan de "
            "bulk plus 19 aan BTTS = 43 van een plafond van 424, en er staan nog 19518 van de 20000 "
            "van deze maand."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "44 duels in dertien van de zeventien competities op een ZONDAGcap van 55 "
            "(`ranking.max_deep_analyses`), dus er is NIETS afgekapt en de dekkingstabel krijgt "
            "geen AFGEKAPT-regel. De datarijkdom liep van 5,0 tot 8,0; omdat er niet is afgekapt "
            "zijn 'laagste die het haalde' en 'hoogste die afviel' per definitie leeg. Alle 44 "
            "duels staan op `playable = True` en komen alle 44 van de daglijst van de rundag zelf - "
            "er is vandaag geen enkel duel van de daglijst van morgen, anders dan gisteren toen "
            "zeven MLS-duels daarvandaan kwamen. De context is voor alle 44 opgehaald (§1c), ook "
            "voor de vijf op tier NONE, en `ctxlog.py collect` heeft ze alle 44 gelogd."
        ),
        "DE_NIVEAUCORRECTIE_IS_VIJF_DAGEN_OUD_EN_HET_SIGNAAL_ERONDER_ZAKT": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. `gridfit.py measure` zegt vandaag zelf dat de reeks nog "
            "niet te lezen is: 174 van de 1347 homogene duels dragen de correctie al in zich, dus "
            "de regel `scale = 1.032` toetst op die duels een DUBBELE correctie en de gemengde "
            "reeks beantwoordt de vraag niet. De diagnose die eronder ligt staat vandaag op +0,062 "
            "doelpunt per duel (z = +1,28) over 1347 duels, tegen +0,089 (z = +1,78) over 1257 "
            "gisteren, +0,091 over 1230 op 6 november en +0,100 (z = +1,93) over 1147 op 2 "
            "november. HET SIGNAAL ZAKT DUS, en dat is precies wat je zou verwachten als de "
            "correctie doet wat ze moet doen - maar het is op deze gemengde reeks GEEN bewijs "
            "daarvan, want een duel dat de correctie al draagt verlaagt de gemeten fout per "
            "definitie. ER IS NIETS TE BESLISSEN en de vraag hoort niet gesteld (§1h, §6g); reken "
            "op enkele maanden voordat de reeks van na 3 november alleen groot genoeg is (§6d). En "
            "let op de VOLGORDE: deze correctie wijst de voorzichtige kant op (meer verwachte "
            "doelpunten, dus een LAGERE P(Under)), terwijl er vandaag vier Unders op de lijst "
            "staan - zonder de correctie waren die vier edges ongeveer twee procentpunt hoger "
            "geweest."
        ),
        "EEN_PICK_VAN_RUN_A_HAD_EEN_AFTRAP_VAN_EEN_DAG_TE_VROEG_EN_IS_GECORRIGEERD": (
            "STAGE 0 VOND EEN ECHTE FOUT EN HET IS DE SOORT DIE DEZE REPO AL DRIE KEER HEEFT "
            "GEKOST: een stille. De pick "
            "`2026-11-07-primeira-liga-por-nacional-academico-viseu-over-under-over-2-25` (Run A, "
            "7 nov, Nacional - Academico Viseu, Over 2,25 @1,85) had als `kickoff` "
            "2026-11-07T15:30:00.000Z staan, terwijl Fotmob voor dat duel (match 5887676) "
            "2026-11-08T15:30:00.000Z geeft - exact een dag te vroeg. GEVOLG: `ledger.py open` "
            "bood de rij vandaag aan als AFWIKKELBAAR, via de terugval op de klok ('geen "
            "bronstatus; terugval op de klok (11,6u >= 2u)'), terwijl het duel vandaag om 16:30 NL "
            "nog moet beginnen. De `DayIndex` van `scripts/settling.py` zoekt de wedstrijd op de "
            "kalenderdag van de opgeslagen aftrap, vindt hem daar niet, krijgt dus geen "
            "bronstatus, en valt dan terug op een klok die vanaf een verkeerd nulpunt loopt. Een "
            "run die de regel van §0 letterlijk op `ledger.py open` had gevolgd, had vandaag een "
            "uitslag geboekt op een wedstrijd die nog niet gespeeld was. WAT ER IS GEDAAN: het veld "
            "is gecorrigeerd naar de aftrap die de bron geeft en de rij staat weer op `pending` "
            "('bron meldt nog niet afgelopen (-12,4u na aftrap)'); de correctie staat in de pick "
            "zelf onder `kickoff_gecorrigeerd`. Er is NIETS afgewikkeld en geen enkele uitkomst "
            "aangeraakt. WAT ER NIET IS GEDAAN: de oorzaak repareren. Dat zit in het Run A-script "
            "van 7 november, dat een duel van de daglijst van morgen de aftrapdatum van de rundag "
            "gaf - dezelfde familie als de MLS-fout van 24 september, nu in de andere richting en "
            "in de administratie in plaats van in de selectie. Dat hoort bij Run A en het staat als "
            "actiepunt in het dagrapport."
        ),
        "DE_AFWIKKELING_VAN_GISTEREN_IS_DOOR_DEZE_RUN_GEDAAN_WANT_RUN_A_WAS_ER_NOG_NIET": (
            "Stage 0 vond NEGEN picks en 67 schaduwrijen klaar om af te wikkelen, en dat is "
            "ongebruikelijk: normaal doet Run A dat om 02:45 en vindt Run B niets meer open. "
            "Vandaag had Run A nog niet gedraaid (er is geen `runs/2026-11-08-run-a.*` en geen "
            "voortgangsbestand voor run a van vandaag), dus deze run was de eerste en heeft de hele "
            "afwikkeling van 7 november gedaan: 5 gewonnen en 4 verloren op de picks, 32 gewonnen, "
            "32 verloren en 3 void op de schaduwrijen. VAN DE VIJF PICKS VAN RUN B ZELF GINGEN ER "
            "DRIE GOED: Austin FC - Portland Timbers (Under 3,5, 0-2), CF Montreal - Vancouver "
            "Whitecaps (Under 3,5, 0-2) en San Diego FC - Sporting Kansas City (Under 3,5, 0-1) "
            "wonnen, Philadelphia Union - Toronto FC (Under 3,5, 4-1) en Cesena - Catanzaro (Over "
            "2,5, 1-0) verloren. De reflectie op die uitslagen (§3 Stage 0, 12 okt 2026) staat in "
            "het runrapport onder Afwikkeling en in gewone taal in `settled_note` van het "
            "dagrapport."
        ),
    }
