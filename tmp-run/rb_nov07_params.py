"""De `parameters`-tekst van Run B, 7 nov 2026 — apart gehouden zodat `rb_nov07_publiceer.py`
alleen de rekenlogica van 6 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **VIER VAN DE VIJF GEPUBLICEERDE REGELS STAAN OP DE UNDER-KANT**, en `margins.py goalbias`
  meet die kant vandaag harder scheef dan ooit: +0,626 doelpunt per duel boven de eigen lambda
  over 127 gespeelde Unders, z = +4,25. Dat is het belangrijkste voorbehoud van deze run.
* **Drie van de vijf regels halen hun eigen lat niet** en staan er op rangorde (§5b). Twee wél:
  Austin FC – Portland Timbers (+14,23 pp) en Cesena – Catanzaro (+10,08 pp).
* **Poort 5 hield voor de vierde dag op rij de grootste groep tegen** — 395 van 510 selecties,
  77,5%.
* **De volste Run B-dag van deze reeks, en de cap bond met drie duels marge**: 52 duels op een
  zaterdagcap van 55.
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
            "groep. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DIE_KANT_STAAT_SCHEEF": (
            "LEES DIT EERST, WANT HET IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG en §6g eist dat "
            "het bij elke gepubliceerde Under staat. Vier van de vijf regels zijn een Under 3,5 "
            "(Austin FC - Portland Timbers, CF Montreal - Vancouver Whitecaps, Philadelphia Union - "
            "Toronto FC en San Diego FC - Sporting Kansas City) en de vijfde is een Over 2,5 "
            "(Cesena - Catanzaro). De Under-kant is de ENIGE markt-en-kant waarvan op UITKOMSTEN is "
            "gemeten dat de routine er structureel naast zit, en de meting is vandaag harder dan "
            "ooit: `margins.py goalbias` geeft over 127 gespeelde Unders +0,626 doelpunt per duel "
            "MEER dan de eigen lambda zei, z = +4,25 (bij de invoering van poort 9 op 11 okt 2026 "
            "was dat +0,68 over 49 duels bij z = +2,91, gisteren +0,614 over 126 bij z = +4,16). Op "
            "de Over-kant gebeurt dat niet: 67 duels, -0,267, z = -1,20. Daarbovenop staat de "
            "vormfout: P(Under 3.5) staat over 2060 duels 1,6 pp te hoog (voorspeld 64,1%, "
            "werkelijk 62,6%). Van de geclaimde edge van elke Under gaat dus ruwweg anderhalf "
            "procentpunt al op aan een gemeten fout die niets met deze ploegen te maken heeft. DAT "
            "MAAKT DE REGELS NIET ONGELDIG - drie van de vier staan er op rangorde en niet op een "
            "belofte - maar het hoort erbij te staan en het staat in de `why`-tekst van het "
            "dagrapport. VIER OP EEN DAG IS WEL EEN PATROON OM TE NOEMEN: Run A publiceerde "
            "vandaag vijf regels waarvan vier Over en een Under, dus over beide runs samen staat "
            "het op vijf Under tegen vijf Over. Een dag is geen reeks (§6d) en er wordt op grond "
            "hiervan geen enkele lat verzet."
        ),
        "DRIE_VAN_DE_VIJF_REGELS_HALEN_HUN_EIGEN_LAT_NIET": (
            "Twee regels halen de lat van 8,0 pp wel: Austin FC - Portland Timbers (Under 3,5 "
            "@1,89, FULL, +14,23 pp herijkt en +13,34 ruw) en Cesena - Catanzaro (Over 2,5 @1,7938 "
            "na commissie, FULL, +10,08 pp herijkt en +9,21 ruw). DRIE NIET: CF Montreal (+7,41), "
            "San Diego FC (+7,31) en Philadelphia Union (+7,17). Die drie staan er op RANGORDE "
            "(§5b, 20 sep 2026): de drempel snijdt sinds die datum aan het eind van de dag en "
            "alleen wanneer er MEER selecties boven de lat staan dan er regels in de lijst passen. "
            "Vandaag staan er TWEE boven de lat en passen er VIJF regels in een zaterdaglijst, dus "
            "bepaalt de rangorde de lijst en gaat de drempel als LABEL mee. Alle drie halen ze wel "
            "alle ANDERE poorten - koersband, anti-circulariteit, datatier, tweede methode, "
            "robuustheid, context, underdog en poort 9 - en die blijven onverkort poorten. Lees de "
            "onderste drie dus als 'het beste van vandaag' en niet als 'een gevonden voordeel'; dat "
            "onderscheid is de hele reden dat §5b mag, want §1g heeft op 552 afgerekende gevallen "
            "gemeten dat er GEEN drempel op de herijkte edge bestaat die geld oplevert. "
            "MAX_LIGHT_IN_SHORTLIST (2) bindt niet: alle vijf de regels staan op FULL. De "
            "afkapping op LIJSTLENGTE bindt ook niet - er zijn vijf plekken en vijf regels - dus de "
            "reeks `lijstlengte` groeit vandaag niet."
        ),
        "VIER_VAN_DE_VIJF_REGELS_KOMEN_UIT_MLS_EN_DAT_IS_EEN_SPEELRONDE_EN_GEEN_VOORKEUR": (
            "MLS levert vandaag 15 van de 52 duels - de laatste reguliere speelronde, waarin alle "
            "dertig ploegen tegelijk spelen - en vier van de vijf gepubliceerde regels. Dat is bijna "
            "dertig procent van de duels en tachtig procent van de lijst, dus het hoort genoemd te "
            "worden in plaats van weggelaten. Twee dingen die het verklaren zonder het weg te "
            "poetsen: (1) MLS is een van de weinige competities van deze runlijst met xG EN een "
            "sportkey, dus alle zes markten dingen er mee en de duels komen op FULL uit - de vijf "
            "competities zonder xG (Czech First League, Croatian HNL, Hungarian NB I, Romanian "
            "SuperLiga, Keuken Kampioen Divisie) staan op LIGHT met een lat van 16,0 pp en kwamen "
            "geen van de veertien in de buurt; (2) `model.league_level` kiest voor MLS de route "
            "`lopend` (33 van 34 speeldagen gespeeld), dus het niveau komt uit het lopende seizoen "
            "zelf en niet uit een opgeschaald vorig seizoen. WAT HET NIET IS: een voorkeur van de "
            "rangorde voor MLS. Van de 15 MLS-duels halen er vier de lijst en elf niet, waarvan "
            "drie op poort 5, drie op robuustheid, een op context en vier op edge."
        ),
        "ALLE VIJF DE REGELS ZIJN OVER/UNDER - EN DAT IS DE ANALYSE EN NIET DE INKOOP": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data, en vandaag komt hij uit de data. De inkoop was zo breed als hij kon zijn: ALLE "
            "NEGEN inkoopbare competities kregen de bulk-aanroep met h2h + spreads + totals, dus "
            "alle negen hadden zowel een uitkomstmarkt (1X2 op de beste prijs, Asian Handicap, en "
            "waar de lijn er is DNB en Double Chance) als een doelpuntenmarkt (O/U), en BTTS is in "
            "de tweede ronde gekocht voor 24 van de 27 duels met een kandidaat-edge. Alle ZES "
            "markten hebben werkelijk meegedongen: van de 510 doorgerekende selecties waren er 158 "
            "Over/Under, 135 Asian Handicap, 123 1X2, 48 BTTS, 31 Draw No Bet en 15 Double Chance. "
            "Dat de vijf overgebleven regels alle vijf uit een markt komen is dus de uitkomst van "
            "`selection_score` over zes concurrerende markten, en geen quotum en geen artefact van "
            "de prijsbron. Bets forceren om een verdeling te halen is precies wat §1 verbiedt."
        ),
        "POORT_5_VANGT_VOOR_DE_VIERDE_DAG_OP_RIJ_HET_MEESTE_WEG": (
            "Van de 510 doorgerekende selecties sneuvelen er 395 op POORT 5, de bevestiging door "
            "een tweede methode (§1, voorwaarde 5) - 77,5% van alles. De rest: 38 op `edge`, 30 op "
            "poort 8 (underdog), 17 op de koersband, 14 op context, 11 op robuustheid, en 5 "
            "selecties over 2 wedstrijden haalden alle negen poorten. DAT IS DE POORT DIE GELD "
            "BESPAART: `shadow.py stats` meet `tweede_methode` vandaag op -1,0% over 256 "
            "afgewikkelde kandidaten, dus de afgewezen groep verliest en de poort doet zijn werk. "
            "Het is ook de poort waarvan §5 waarschuwt dat hij structureel alles kan wegvangen; "
            "77,5% op een dag is geen reeks (§6d eist ~30), maar het is de VIERDE dag op rij dat "
            "deze poort de grootste groep wegvangt (82% gisteren, 74,6% bij Run A vanochtend) en "
            "dat is het vermelden waard. Er wordt niets verzet."
        ),
        "POORT_9_HEEFT_VANDAAG_NUL_SELECTIES_GEBLOKKEERD_EN_DAT_IS_ZIJN_ONTWERP": (
            "De vraag dringt zich op: waarom laat poort 9 vier Unders door, waarvan drie met een "
            "edge onder de gewone drempel? OMDAT DIE POORT MET OPZET ALLEEN IN DE BAND TUSSEN DE "
            "TWEE LATTEN BINDT, 8,0 tot 10,0 pp op FULL. Austin FC staat met +14,23 pp BOVEN de "
            "verzwaarde lat van 10,0 en passeert dus op eigen kracht; de andere drie (+7,41, +7,31, "
            "+7,17) staan ONDER de gewone drempel van 8,0, dus daar is `edge` de bindende poort en "
            "niet poort 9 - en `edge` is sinds §5b een label en geen veto. Zou poort 9 ook de "
            "kandidaten claimen die de gewone drempel al niet halen, dan loopt de reeks "
            "`doelpunten_onder` vol met rijen die nooit een bet konden worden en meet ze niets meer: "
            "exact de 'twee populaties'-fout die §1e bij `underdog_ruw` en §5b bij `lijstlengte` "
            "benoemt. WAT HIER WEL BIJ HOORT: onder §5b kunnen zo drie Unders op de rangorde worden "
            "gepubliceerd die poort 9 zou hebben geblokkeerd als ze tussen 8 en 10 pp hadden "
            "gestaan. Dat is een bekende grens van de constructie (dezelfde als bij de LIGHT-Under "
            "van Run A op 12 oktober en bij Hammarby gisteren) en geen nieuwe bevinding; de run "
            "verzet die poort niet op eigen initiatief (§1h, §6g). De reeks `doelpunten_onder` "
            "staat op 35 afgewikkelde kandidaten met -30,4% rendement: duidelijk negatief, dus de "
            "poort houdt verliezers tegen en er is geen aanleiding om hem te verlagen of de vraag "
            "aan de gebruiker voor te leggen."
        ),
        "PINNACLE_ZET_DE_BESTE_BET_7_8_PP_LAGER_DAN_HET_MODEL": (
            "Stage 5 stap 2 (§3) zet de de-vigde prijs van de scherpste bookmaker naast de eigen "
            "kans, LOS van de beste prijs waarop gespeeld wordt. Op de bovenste regel is dat het "
            "op een na grootste verschil van de dag op de Under-kant: Pinnacle zet P(Under 3,5) "
            "voor Austin FC - Portland Timbers op 52,1% en het eigen model op 59,8%, een verschil "
            "van +7,76 pp bij een Pinnacle-marge van 3,8%. Het is een ZUIVERE halve lijn, dus geen "
            "push. Ook de andere drie Unders staan boven Pinnacle: CF Montreal +7,26 pp (op "
            "Pinnacle's lijn 3,25), San Diego FC +4,59 pp (lijn 3,75) en Philadelphia Union "
            "+3,15 pp (lijn 3,5). Over alle 33 toetsbare (duel, lijn)-paren staat het model "
            "gemiddeld -0,20 pp ONDER Pinnacle op de Under-kant, met 16 van de 33 erboven - de "
            "populatie als geheel is dus in evenwicht en het zijn juist de vier gepubliceerde "
            "regels die eruit steken. Uitgesplitst naar lijnsoort: 15 zuivere halve lijnen op "
            "-0,51 pp en 18 lijnen MET push op +0,05 pp. Op 1X2 staat het model gemiddeld 4,02 pp "
            "van het Pinnacle-oordeel af over 33 duels (marge 4,10%), met het grootste gat bij "
            "Ried - LASK (+17,5 pp meer thuiszege dan Pinnacle) - en dat is precies het duel dat "
            "poort 7 heeft tegengehouden. HARDE GRENS (§2/§4): geen van deze getallen gaat in "
            "my_prob of in prob_sources; het is andermans lezing en het is marktafgeleid."
        ),
        "DE_CAP_BINDT_NIET_MAAR_MET_DE_KRAPSTE_MARGE_VAN_DEZE_REEKS": (
            "52 duels in veertien van de zeventien competities op een ZATERDAGcap van 55 "
            "(`ranking.max_deep_analyses`), dus er is NIETS afgekapt en de dekkingstabel krijgt "
            "geen AFGEKAPT-regel. Drie duels marge is de krapste sinds de verhoging naar 40/55 op "
            "5 september; Run A zat vanochtend met 86 duels ruim erover en kapte er 31 af. De "
            "datarijkdom liep van 4,75 tot 8,0; omdat er niet is afgekapt zijn 'laagste die het "
            "haalde' en 'hoogste die afviel' per definitie leeg. Alle 52 duels staan op "
            "`playable = True`. ZEVEN MLS-DUELS KOMEN VAN DE DAGLIJST VAN MORGEN (aftrap 01:00 NL "
            "op 8 november) en horen evengoed bij deze run, want het inzetvenster is [08:00 NL, "
            "08:00 NL + 1 dag) - bijna de helft van de MLS-ronde, en precies het geval waarvoor "
            "`scripts/runwindow.py` bestaat en waaraan de run van 24 september een hele MLS-ronde "
            "verloor."
        ),
        "DRIE_COMPETITIES_OP_GEEN_WEDSTRIJD_EN_DE_TWEE_ENGELSE_ZIJN_HET_GEVAL_OM_NA_TE_TREKKEN": (
            "English League One, English League Two en Serie A (BRA) hebben niets op de kalender. "
            "Dat is GEEN WEDSTRIJD en geen gat (§3 Stage 2), maar bij de twee Engelse divisies is "
            "het de uitkomst die `prompts/run-b.md` uitdrukkelijk als STILLE FAALSTAND beschrijft: "
            "op een gewone zaterdag in november spelen die juist wel, en een fout fotmob_id geeft "
            "geen foutmelding maar nul wedstrijden - en nul wedstrijden leest als GEEN WEDSTRIJD. "
            "Daarom is het op drie manieren nagetrokken en is de nul echt. (1) `scripts/idcheck.py` "
            "bevindt alle 33 id's groen, id 108 met 24 ploegen en id 109 met 24 ploegen in "
            "2025/2026 - dat is de controle die juist op de competities draait die vandaag stil "
            "zijn. (2) De tweede bron is het eens: BetExplorer geeft voor beide divisies nul duels "
            "in het inzetvenster en als eerstvolgende speelronde 14 november "
            "(`rb_nov07_bevestiging.py`, 17 van 17 competities eens, 52 tegen 52 duels). (3) De "
            "REDEN staat in de daglijst van Run A: de EERSTE RONDE VAN DE FA CUP speelt vandaag met "
            "33 duels, en daarin zijn precies de clubs uit League One en League Two ingestroomd. "
            "Dat toernooi hoort bij de runlijst van Run A en niet bij deze - Run A heeft het "
            "vanochtend doorgerekend en er een gekwalificeerde selectie uit gehaald (Newport County "
            "- Walsall, op lijstlengte buiten de lijst gevallen). Serie A (BRA) speelt niet: de "
            "daglijst heeft onder ccode BRA alleen Serie B (8814) en de Copa do Brasil (9067), en "
            "BetExplorer geeft 14 november als eerstvolgende."
        ),
        "ZES_DUELS_OP_NONE_EN_ALLE_ZES_OM_EEN_VOORGESCHREVEN_REDEN": (
            "Zes van de 52 duels komen op data_tier = NONE uit en worden dus niet geanalyseerd "
            "(§2). ALLE ZES om een reden die in de regels staat en geen van de zes is een storing. "
            "DRIE DEGRADANTEN ZONDER DIVISIEPAAR ERONDER: Juve Stabia - Arezzo en Benevento - "
            "Avellino (Serie B; Arezzo en Benevento komen uit de Serie C en dat divisiepaar staat "
            "niet in TIER2) en VfL Osnabruck - Kaiserslautern (2. Bundesliga; Osnabruck komt uit de "
            "3. Liga, zelfde geval). TWEE BUITEN HET GEMETEN BEREIK: Burgos CF - Celta Fortuna "
            "(Segunda Division) en Austria Lustenau - Grazer AK (Austrian Bundesliga) - daar "
            "weigert `promotion.conversion_in_range`, en dat is de Coventry-val waarvoor die poort "
            "bestaat en geen lacune. Celta Fortuna is hetzelfde geval als op 5 oktober (een "
            "beloftenelftal met een verdediging zwakker dan alles wat ooit is gemeten) en Austria "
            "Lustenau hetzelfde als op 11 oktober (relatieve aanval onder de gemeten ondergrens). "
            "EEN ZONDER MEETBAAR DIVISIEPAAR: MTK Budapest - Kispest Honved (Hungarian NB I) - "
            "Fotmob HEEFT de NB II (id 9117) maar dat id negeert de seizoensparameter, dus "
            "`measure_gap` weigert luidruchtig sinds 11 okt 2026. §4 noemt dat 'niet nog niet "
            "gemeten maar niet meetbaar op deze bron' en een gepoolde factor erop zetten is "
            "verboden. Van alle zes is de context wel opgehaald en gelogd (§1c eist dat ook bij "
            "tier NONE). WAT DAT MET DE DEKKINGSTABEL DOET, per competitie en niet per duel: alle "
            "vier de betrokken competities hebben OOK duels die wel zijn doorgerekend (Serie B 3 "
            "van 6, 2. Bundesliga 3 van 4, Segunda Division 3 van 4, Austrian Bundesliga 1 van 2, "
            "Hungarian NB I 2 van 3), dus alle vier staan op GEANALYSEERD. Geen enkele competitie "
            "krijgt vandaag BUITEN DATADEKKING of AFGEKAPT."
        ),
        "VIJF_VAN_DE_VEERTIEN_COMPETITIES_HEBBEN_GEEN_XG_EN_GEEN_BESTE_PRIJS": (
            "Vijf van de veertien spelende competities hebben GEEN xG bij Fotmob - Czech First "
            "League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) en "
            "Keuken Kampioen Divisie (111) - en draaien op doelpunten als sterktemaat; ze komen dus "
            "altijd op LIGHT uit, met een lat van 16,0 pp (`prompts/run-b.md`). Dat zijn vandaag 14 "
            "van de 52 duels. DEZELFDE VIJF hebben ook geen sportkey bij The Odds API en draaien op "
            "het gratis BetExplorer-marktgemiddelde (4 tot 17 boeken), waar de bookmaker niet "
            "herleidbaar is en de edge systematisch te laag uitvalt (§1a) - conservatief, dus geen "
            "risico op te veel bets, maar niet vergelijkbaar met een duel waar de beste prijs wel "
            "bekend is. Die veertien duels zijn op beide assen de zwakste van de dag, en er is geen "
            "enkele markt buiten 1X2 voor te koop: AH, DNB, DC, OU en BTTS staan daar alle vijf als "
            "'niet opgevraagd - geen sportkey' in `markets_checked`, met de reden erbij en niet als "
            "gat (§6b-5b). De hoogste edge van die groep was Rosenborg - Start met +10,45 pp, ruim "
            "onder de LIGHT-lat van 16,0. Neem dekking nooit over van een andere competitie in "
            "hetzelfde land: Duitsland heeft xG in de 2. Bundesliga en Nederland niet in de Keuken "
            "Kampioen Divisie, terwijl beide landen het in hun hoogste divisie wel hebben. EEN "
            "DUEL KREEG HELEMAAL GEEN PRIJZEN: FC Zbrojovka Brno - Banik Ostrava (Czech First "
            "League) staat niet op de BetExplorer-fixturepagina met een koers, dus daar zijn nul "
            "selecties doorgerekend."
        ),
        "DE_NIVEAUCORRECTIE_IS_VIER_DAGEN_OUD_EN_NOG_NIET_TE_LEZEN": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. `gridfit.py measure` zegt vandaag zelf dat de reeks nog "
            "niet te lezen is: 84 van de 1257 homogene duels dragen de correctie al in zich, dus de "
            "regel `scale = 1.032` toetst op die duels een DUBBELE correctie en de gemengde reeks "
            "beantwoordt de vraag niet. De diagnose die eronder ligt staat vandaag op +0,089 "
            "doelpunt per duel (z = +1,78) over 1257 duels, tegen +0,091 (z = +1,80) over 1230 "
            "gisteren en +0,100 (z = +1,93) over 1147 op 2 november - meegegroeid noch weggezakt. "
            "ER IS DUS NIETS TE BESLISSEN en de vraag hoort niet gesteld (§1h, §6g); reken op "
            "enkele maanden voordat de reeks van na 3 november groot genoeg is. En let op de "
            "VOLGORDE: deze correctie wijst de voorzichtige kant op (meer verwachte doelpunten, dus "
            "een LAGERE P(Under)), terwijl er vandaag vier Unders op de lijst staan - zonder de "
            "correctie waren die vier edges ongeveer twee procentpunt hoger geweest."
        ),
        "DE_AFWIKKELING_WAS_VANOCHTEND_AL_GEDAAN_DOOR_RUN_A": (
            "Stage 0 vond NIETS open om af te wikkelen en dat is de normale gang van zaken, geen "
            "storing: Run A draaide vanochtend om 02:45 en heeft de vier picks van 6 november "
            "afgewikkeld (3 gewonnen, 1 verloren) plus acht schaduwrijen. De vijf picks die nu nog "
            "op `pending` staan zijn alle vijf van Run A van VANDAAG en hebben nog niet afgetrapt "
            "(`ledger.py open` meldt ze met een negatieve tijd sinds de aftrap). `shadow.py open` "
            "zegt hetzelfde over de schaduwrijen. De reflectie op de uitslagen van gisteren (§3 "
            "Stage 0, 12 okt 2026) staat daarom in het runrapport onder Afwikkeling en in gewone "
            "taal in `settled_note` van het dagrapport, met de EEN verliezer die van Run B zelf was: "
            "Hammarby - Elfsborg, Under 3, uitslag 4-1 op een verwachting van 2,90 doelpunten. Die "
            "ene past precies in de reeks van 127 Unders die §6g meet en is de reden dat het "
            "voorbehoud van vandaag zo zwaar hoort te wegen."
        ),
    }
