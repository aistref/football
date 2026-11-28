"""De `parameters`-tekst van Run A, 28 nov 2026 — apart gehouden zodat `ra_nov28_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `ra_nov27_params.py`).

Vijf dingen die vandaag vooraan horen:

* **VIER VAN DE VIJF REGELS ZIJN EEN DOELPUNTENMARKT, EN DAAR MEET §6g NU OP BEIDE KANTEN EEN
  SIGNIFICANT SELECTIE-EFFECT.** `margins.py goalbias`: Under gespeeld +0,661 doelpunt per duel
  over 153 gevallen bij **z = +4,92**, Over gespeeld −0,368 over 87 bij z = −1,87. Het model zelf
  staat goed (+0,019 over 2521, z = +0,56). Drie Overs en één Under op de lijst van vandaag staan
  dus allemaal op een as waar de selectie — niet het model — aantoonbaar de verkeerde kant kiest.
* **DE VOLSTE RUN A-DAG VAN DEZE REEKS EN DE CAP KOMT VOOR HET EERST IN ZICHT.** 51 duels op een
  zaterdagcap van 55: niets afgekapt, maar het scheelt vier duels waar het de afgelopen weken
  tientallen waren.
* **TWINTIG VAN DE 51 DUELS GINGEN LANGS DE PROMOVENDI-/DEGRADANTENOMREKENING**, het grootste
  aantal van deze reeks, verdeeld over ALLE TWAALF spelende competities, en geen enkele kwam op
  `NONE` uit. Twee duels hebben een omgerekende ploeg aan BEIDE kanten (Paderborn – Schalke 04,
  Lincoln City – Wolverhampton Wanderers).
* **DE NIVEAUCORRECTIE HOUDT HAAR GESPIEGELDE TEKEN, NU OP 545 DUELS.** Op de duels mét de
  correctie staat het gemiddelde totaal op −0,097 (z = −1,22) tegen +0,099 (z = +1,92) op de 1173
  ervóór; de fout op `P(Under 2.5)` ging van −2,38 naar +1,94 pp. Niets verzet, de vraag niet
  voorgelegd: de lat die Run A op 21 nov zelf zette is "ruim boven de ~900 duels".
* **POORT 7 KOMT VOOR HET EERST AAN DE MEETGRENS.** `ctxlog.py stats` geeft de fout van het model
  tegen het beschikbaarheidsverschil op t = −1,99 bij een helling van −11,8 pp per eenheid over
  2297 wedstrijden, en de aantoonbaarheidsgrens ligt bij ~11 pp. Het teken wijst de verwachte kant
  op. Nog steeds een rem en geen bijstelling (§1c).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,037, b=0,024 op "
            "8922 afgerekende gevallen, fitted_through 2026-11-27. §6b-5c eist dat dat getal op de "
            "vorige rundag staat of daarna, en de vorige rundag IS 27 november, dus de fit is bij "
            "het rekenen van vandaag actueel. Dat komt doordat `calibration.py settle` vandaag in "
            "Stage 0 is gedraaid vóórdat `load_fit()` aan de analyse begon (75 waarnemingen "
            "afgewikkeld, 9321 van 9369 compleet). DE FIT VERHOOGT EEN KANS OVER VRIJWEL DE HELE "
            "SPEELBARE BAND: -0,2 pp op 30%, +0,2 pp op 40%, +0,6 pp op 50%, +0,9 pp op 60%, "
            "+1,1 pp op 70%, +1,2 pp op 80%. Bij alle vijf de gepubliceerde regels tilt hij de kans "
            "dus OP, met ongeveer één procentpunt edge erbij — en bij geen van de vijf is dat "
            "beslissend: `bet_beide` is bij ALLE VIJF waar, dus elke regel haalt zijn lat ook op de "
            "ruwe schaal. Dat is de gunstige stand van §5a en hij komt niet elke dag voor. Het ruwe "
            "model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET ALS 'het model is "
            "goed': het is gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en "
            "de scheefstand die telt zit in de GESELECTEERDE groep — `ledger.py stats` verwachtte "
            "over 542 afgewikkelde bets 325,1 winnaars en er werden er 253 (-72,1), met een Brier "
            "van 0,2627 tegen 0,2438 voor de markt. De markt schat nog steeds scherper, en dat is "
            "de regel die telt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",

        "VIER_VAN_DE_VIJF_REGELS_ZIJN_EEN_DOELPUNTENMARKT_EN_DAAR_STAAT_DE_SELECTIE_SCHEEF": (
            "LEES DIT EERST. Manchester United – Brentford Over 2.5, Hamburger SV – Bayern München "
            "Over 3.5, Vitória de Guimarães – Estrela da Amadora Over 2.5 en Torino – Lazio Under "
            "2.5: vier van de vijf regels zijn een Over/Under, drie op de Over-kant en één op de "
            "Under-kant. `margins.py goalbias` van vandaag meet op BEIDE kanten een selectie-effect "
            "en op één ervan is het nu hard: UNDER GESPEELD +0,661 DOELPUNT PER DUEL OVER 153 "
            "GEVALLEN BIJ z = +4,92, OVER GESPEELD -0,368 OVER 87 BIJ z = -1,87. Het MODEL staat "
            "daarentegen goed: +0,019 doelpunt per duel over 2521 doorgerekende duels, z = +0,56. "
            "Die twee regels mogen nooit worden opgeteld (§6g) — de bovenste meet het model, de "
            "onderste de selectie — maar ze wijzen hetzelfde aan: de routine kiest aan BEIDE "
            "uiteinden van de doelpuntenas juist de duels waar haar eigen lambda de verkeerde kant "
            "op staat. Dat is géén gerichte fout meer zoals §6g op 11 oktober beschreef ('op de "
            "Over-kant gebeurt dat niet', n = 38, z = -0,54) maar een algemene winner's curse op "
            "die as. Het rendement beweegt mee: Over/Under op de Under-kant staat op -15,2% over "
            "192 picks, de Over-kant op +6,4% over 114 — op 11 oktober was dat nog +10,6% over 62, dus de "
            "Over-kant levert nog steeds geld op maar minder dan toen. Voor de vijfde regel, de "
            "Draw No Bet, staat de reeks op +22,6% over 19 afgewikkelde picks: ruim positief en ruim "
            "ONDER de ~30 die §6d eist, dus niet te lezen. "
            "NIETS VERZET. Poort 9 blijft onveranderd (§1h, §6g: een run verzet die knop nooit op "
            "eigen initiatief), de Over-kant krijgt geen eigen lat, en |z| = 1,87 op de Over-kant "
            "haalt de lat van deze repo niet. Het hoort wél bij elke doelpuntenregel van vandaag "
            "genoemd te worden, en dat zijn er vier van de vijf."
        ),

        "DE_ENE_UNDER_STAAT_ELF_PROCENTPUNT_BOVEN_PINNACLE_EN_DAT_IS_DE_SCHEVE_KANT": (
            "Torino – Lazio, Under 2.5 @2.00, is de enige Under op de lijst en hij staat op de kant "
            "waar §6g de schade meet. Twee cijfers die daarbij horen en die elkaar versterken. (1) "
            "Poort 9 bindt en hij haalt zijn verzwaarde lat met marge: +12,59 pp tegen de 10,0 die "
            "een Under op FULL-data moet halen (`unders.UNDER_EXTRA` = 2,0 bovenop de 8,0 van §0). "
            "(2) MAAR PINNACLE IS HET ER NIET MEE EENS: zijn de-vigde P(Under 2.5) staat op 49,4% "
            "tegen 60,6% van het model, een verschil van +11,20 pp op de scheefste kant die deze "
            "routine heeft. Pinnacle noteert dat duel met een marge van 2,8% — de scherpste prijs "
            "van de dag — en over alle 49 (duel, lijn)-paren van vandaag ligt het model gemiddeld "
            "2,98 pp ONDER Pinnacle op de Under-kant. Deze ene regel wijst dus precies de andere "
            "kant op dan de dagreeks waar hij in staat. Dat is geen reden om hem weg te laten — §5b "
            "rangschikt en de poorten staan open — maar het is de eerlijke lezing: de twee "
            "lambdas zijn 1,004 thuis en 1,260 uit, samen 2,26 doelpunt, en dat is een laag totaal "
            "voor een Serie A-duel tussen twee ploegen die beide boven het competitiegemiddelde "
            "scoren. Gaat dit duel over 2,5, dan is het de verwachte uitkomst van een gemeten fout "
            "en niet een verrassing."
        ),

        "DE_LIJSTLENGTE_BINDT_NIET_EN_ALLE_VIJF_HALEN_HUN_EIGEN_LAT": (
            "Vijf selecties boven hun eigen lat, vijf plekken in de zaterdaglijst (`MAX_SHORTLIST` "
            "= 5 sinds 19 nov 2026, §0). De rangorde en de drempel wijzen dus exact dezelfde lijst "
            "aan, er valt NIETS buiten de lijst en er is vandaag geen enkele "
            "`lijstlengte`-schaduwrij. Dat is in deze reeks ongewoon: sinds §5b op 20 september de "
            "drempel naar achteren trok, staan de meeste dagen er regels op rangorde die hun eigen "
            "lat niet halen. Vandaag niet. Voor de volledigheid de stand van de reeks die hieraan "
            "hangt, zoals §5b voorschrijft onder 'Stand van het logboek': `lijstlengte` staat op 34 "
            "AFGEWIKKELDE gevallen met +4,60u = +13,5% (16 winnaars op 34). De gebruiker heeft op "
            "18 november gezegd dat hij bij 100 gevallen opnieuw kijkt — dat is de lat, en het zijn "
            "er 34, dus de vraag hoort vandaag NIET voorgelegd en `MAX_SHORTLIST` wordt niet "
            "aangeraakt (§5b: een run verandert die nooit op eigen initiatief)."
        ),

        "DE_CAP_KOMT_VOOR_HET_EERST_IN_ZICHT_MAAR_BINDT_NIET": (
            "51 duels in het inzetvenster op een ZATERDAGcap van 55 "
            "(`ranking.max_deep_analyses(2026-11-28)`): nul afgekapt, dus geen `AFGEKAPT`-regel in "
            "de dekkingstabel en geen stille truncatie. Het scheelt vier duels, en dat is het "
            "krapst van deze reeks — de Run A-dagen van de afgelopen twee weken zaten op 6, 14 en "
            "19 duels. De Championship levert er alleen al tien, de Bundesliga, Ligue 1 en de "
            "Scottish Premiership elk vijf. Zou de cap wél hebben gebonden, dan was dat op "
            "datakwaliteit en datarijkdom gegaan (§3 Stage 4) en niet op aftraptijd; de laagste "
            "datarijkdom in de run is 5,0 en de hoogste 8,0. Beide getallen staan in "
            "`afkapping` in de run-state, met een lege afkappingslijst ernaast."
        ),

        "TWINTIG_OMREKENINGEN_OVER_TWAALF_COMPETITIES_EN_GEEN_ENKELE_OP_NONE": (
            "TWINTIG van de 51 duels hebben minstens één ploeg die niet in de stand van 2025/2026 "
            "staat en gingen dus langs `promotion.convert` / `convert_relegated` (§4). Dat is "
            "veruit het grootste aantal van deze reeks, en het bijzondere is dat het NIET uit één "
            "competitie komt: alle TWAALF spelende competities hebben er minstens één, van vier op "
            "tien in de Championship tot twee op drie in de Premier League en de Ekstraklasa. TWEE "
            "duels hebben een omgerekende ploeg aan BEIDE kanten: Paderborn – Schalke 04 (twee "
            "promovendi uit de 2. Bundesliga) en Lincoln City – Wolverhampton Wanderers (een "
            "promovendus uit League One tegen een degradant uit de Premier League, dus de "
            "opwaartse én de neerwaartse tak in één duel). GEEN ENKELE van de twintig kwam op "
            "`NONE` uit — `conversion_in_range` heeft vandaag niets geweigerd, en dat is bij deze "
            "aantallen het vermelden waard, want die poort is er juist om te weigeren (de "
            "Coventry-val, §4). En geen enkele is `FULL` geworden, want een omgerekende ploeg is "
            "dat nooit (§4): de tierverdeling is 31 FULL en 20 LIGHT, met nul op `NONE`. Alle "
            "twintig staan dus op de LIGHT-lat van 16,0 pp en geen van de vijf gepubliceerde "
            "regels komt eruit — alle vijf de bets zijn FULL. Lees dat als de prijs van die lat en "
            "niet als een gebrek: de hoogste LIGHT-edge van vandaag is +14,97 pp (Frosinone – "
            "Parma, Under 3.5 @1.92, enige dichte poort `edge`) en die mist de 16,0 met ruim een "
            "procentpunt. Daarna +14,71 (Académico Viseu – Alverca) en +14,49 (West Ham United – "
            "Stoke City): drie LIGHT-regels binnen anderhalve procentpunt van hun lat, en alle "
            "drie gaan ze als `near_miss` het schaduwlogboek in."
        ),

        "DE_NIVEAUCORRECTIE_HOUDT_HAAR_GESPIEGELDE_TEKEN_NU_OP_545_DUELS": (
            "`model.LEVEL_SCALE` = 1.032 bindt sinds 3 november en §6g punt 4 eist dat de vraag "
            "'werkt de correctie' op ALLEEN de duels met die correctie wordt gelezen. Dat is "
            "vandaag gedaan (`tmp-run/ra_nov28_gridfit_na_niveau.txt`), en de bevinding van "
            "27 november houdt stand: op de 545 duels van 3 t/m 27 november staat het gemiddelde "
            "totaal op -0,097 (z = -1,22) en de fout op `P(Under 2.5)` op +1,94 pp, waar het op de "
            "1173 duels van 20 sep t/m 2 nov -- ZONDER de correctie -- +0,099 (z = +1,92) en "
            "-2,38 pp was. HET TEKEN IS OP ALLE DRIE DE DIAGNOSEREGELS OMGESLAGEN EN DE OMVANG IS "
            "VERGELIJKBAAR GEBLEVEN: de correctie heeft de fout niet verkleind maar gespiegeld. "
            "Tweede aanwijzing dezelfde kant op: `scale = 1.032` nog een keer toepassen geeft op "
            "die 545 duels t = -1,91, tegen t = +0,92 op de 1173 ervóór. Op de gemengde reeks van "
            "1718 duels die `gridfit.py measure` standaard laat zien lijkt alles juist goed "
            "(+0,037, z = +0,84) — dat is precies de populatiemenging waarvoor `gridfit.py` in zijn "
            "eigen kop waarschuwt, en de reden dat deze knip er is. NIETS VERZET EN DE VRAAG NIET "
            "VOORGELEGD: Run A heeft op 21 november zelf de lat op 'ruim boven de ~900 duels' "
            "gezet, het zijn er 545, en z = -1,22 haalt de lat niet. Verwacht in januari. Poort 9 "
            "hangt aan hetzelfde besluit en blijft onveranderd staan."
        ),

        "POORT_7_KOMT_VOOR_HET_EERST_AAN_DE_MEETGRENS": (
            "`ctxlog.py stats` geeft vandaag voor het eerst een bijna-significant verband: de fout "
            "van het MODEL tegen het beschikbaarheidsverschil staat op r = -0,042, t = -1,99, "
            "helling -11,8 pp per eenheid over 2297 wedstrijden, en de aantoonbaarheidsgrens ligt "
            "bij ~11 pp per eenheid. De fout van de MARKT staat op t = -1,60 (-9,3 pp per eenheid) "
            "— het model is dus iets gevoeliger voor ontbrekende spelers dan de markt, en in de "
            "verwachte richting: een ploeg die meer van zijn selectiewaarde mist, doet het slechter "
            "dan het model zegt. Zet dit naast de meting van 5 september 2026 (§1c), waar over 147 "
            "wedstrijden r = -0,007 en t = -0,08 stond en de tabel 4270 wedstrijden becijferde voor "
            "een effect van 10 pp: met 2629 afgewikkelde contextwedstrijden is het verband nu "
            "zichtbaar en het is ongeveer zo groot als de steekproef kan aantonen. NIETS VERZET: "
            "poort 7 blijft een REM en geen BIJSTELLING (§1c, en dat is geen voorlopigheid maar de "
            "regel: een getal verzinnen omdat het plausibel klinkt is wat §2 en §4 verbieden). "
            "|t| = 1,99 haalt de lat van |t| = 2 bovendien net niet, en de lat die deze repo elders "
            "aanhoudt is hoger (`CREDIBILITY_K` op t = +2,11 / +1,71). Het hoort als openstaand "
            "punt in het runrapport en het is de eerste keer dat deze reeks iets zegt."
        ),

        "POORT_7_KOSTTE_VANDAAG_EEN_DUEL_EN_POORT_5_VANGT_DRIEKWART_WEG": (
            "Van de 51 doorgerekende wedstrijden hield poort 7 er ÉÉN tegen, en het is een "
            "duidelijk geval: Widzew Łódź – Zagłębie Lubin, waar Zagłębie Lubin 62% van zijn "
            "selectiewaarde mist tegen 21% bij Widzew Łódź — Marcel Reguła (terug begin januari "
            "2027), Michał Nalepa en Pawel Kosmalski (beiden twijfelachtig). De poort is "
            "asymmetrisch en grof en houdt alleen tegen (§1c); de reeks `context` staat op 157 "
            "afgewikkelde kandidaten met -22,0%, de meest overtuigende van alle negen poorten. "
            "POORT 5 (de bevestiging door een tweede methode) is net als de afgelopen dagen de "
            "grootste zeef: hij is de eerste dichte poort bij 564 van de 740 doorgerekende "
            "selecties, oftewel 76%. Lees dat met de volgorde erbij — `failed_gate` geeft alleen de "
            "EERSTE dichte poort in `ORDER` en `tweede_methode` staat vooraan, dus 564 is een "
            "BOVENGRENS voor wat de poort alléén tegenhoudt. Scherper gemeten: bij 11 van de 46 "
            "duels zonder bet is `tweede_methode` de enige poort die bij álle kandidaten binnen de "
            "koersband dichtstaat, en dat is de ondergrens. De reeks staat op 338 afgewikkelde "
            "kandidaten en -2,9%: hij bespaart geld, maar nauwelijks. De overige poorten vangen "
            "veel minder: `edge` 74 selecties, `underdog` 53, `odds` 27, en `robuustheid` en "
            "`context` elk 6."
        ),

        "TWAALF_VAN_DE_ZESTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_TWEE_BRONNEN_NAGETROKKEN": (
            "Twaalf van de zestien competities op de runlijst hebben duels in het inzetvenster "
            "[08:00 NL 28 nov, 08:00 NL 29 nov). Vier niet: de Danish Superliga (die speelt morgen "
            "weer, eerste duel 30 nov 19:00) en de Champions League, Europa League en Conference "
            "League, die alle drie pas in december terugkomen (8 en 10 december). BEVESTIGD DOOR "
            "EEN TWEEDE, ONAFHANKELIJKE BRON, zoals §1 eist: Fotmob levert de daglijst en "
            "BetExplorer de fixturepagina per competitie, en ze zijn het over ALLE 22 competities "
            "eens — 51 duels tegen 51, nul afwijkingen, inclusief de tien competities die vandaag "
            "nul duels hebben. Dat is de controle die op 14 oktober stil één competitie liet "
            "wegvallen door een `\\s+` in de regex en op 5 november een heel etmaal verkeerd "
            "toetste; beide zijn gerepareerd en het venster wordt sindsdien uit `DAY` afgeleid."
        ),

        "DE_ZES_BEKERS_STAAN_BUITEN_DE_RUNLIJST_EN_GEEN_VAN_ZES_SPEELT_VANDAAG": (
            "FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB Pokal en Copa del Rey staan van "
            "1 juli t/m 31 december NIET op de runlijst (`cups.filter_runlist` met de rundag, "
            "besluit van de gebruiker van 18 en 19 nov 2026). Ze krijgen daarom de status `BUITEN "
            "DE RUNLIJST` en NIET `GEEN WEDSTRIJD` — §5 verbiedt dat laatste met zoveel woorden, "
            "want er wórdt in die toernooien gespeeld, het staat alleen niet op onze lijst. Vandaag "
            "valt dat onderscheid toevallig samen: nul duels in beide daglijsten voor alle zes. De "
            "eerstvolgende rondes staan op 1 december (Coppa Italia, DFB Pokal), 4 december (FA "
            "Cup) en 15 december (League Cup), en die vallen alle vier nog buiten de lijst. Alle "
            "zes doen weer mee op 1 januari 2027."
        ),

        "HET_NIVEAU_KOMT_BIJ_ALLE_TWAALF_UIT_VORIG_SEIZOEN_PLUS_UPLIFT": (
            "`model.league_level` koos bij ALLE TWAALF spelende competities de route "
            "`vorig+uplift`: geen enkel lopend seizoen is over de helft van zijn speeldagen heen "
            "(`SEASON_MATURE_SHARE`), met de Championship als verste op 18 van 46 en de Bundesliga "
            "als vroegste op 11 van 34. De gepoolde vroeg-seizoenscorrectie staat op factor 1,1129 "
            "(gepoold 1,1185 over 162 speeldagen, twaalf competities) en `uplift_observations` "
            "heeft NUL competities overgeslagen — alle twaalf hebben xG in beide seizoenen en alle "
            "twaalf zitten in de pool. Dat is een factor van ruim elf procent en dus groot; hij "
            "dooft vanzelf uit naarmate het seizoen vordert en hij staat los van "
            "`model.LEVEL_SCALE`, dat niet uitdooft (§6g). De twee mogen nooit tot één factor "
            "worden samengevoegd."
        ),

        "DE_INKOOP_IS_VOLLEDIG_EN_DE_MARKTBALANS_SLAAGT_ZO_RUIM_ALS_HIJ_KAN": (
            "Plafond `suggest_cap(18809, 3)` = 3131 credits, `split_budget(3131, 12)` = (12, 12), "
            "dus de volledige bulk paste voor alle twaalf inkoopbare competities: 36 credits aan "
            "h2h + spreads + totals (3 per competitie) en 39 aan BTTS voor de 39 duels met een "
            "kandidaat-edge, samen 75 van 3131. MARKTBALANS-CONTROLE GEHAALD, EN ZO RUIM ALS HIJ "
            "KAN: alle twaalf competities kregen uit dezelfde bulk zowel een uitkomstmarkt (1X2, "
            "AH, DNB, DC) als een doelpuntenmarkt (OU) — twaalf op twaalf, niet één op twaalf zoals "
            "op 30 augustus. §1a eist dat dat getal erbij staat, want twee bets uit één markt op "
            "een dag dat alleen die markt te koop was is iets anders dan op een dag dat alle zes "
            "meededen. Vandaag deden alle zes mee bij alle twaalf, en er komen vier "
            "doelpuntenmarkten en één uitkomstmarkt uit. Die scheefheid komt dus uit de analyse en "
            "niet uit de portemonnee, en dat is precies het onderscheid dat deze controle moet "
            "kunnen maken. BTTS is in de tweede ronde gekocht op de VERENIGING van beide schalen "
            "(§1a, 13 sep 2026) en werd nergens de sterkste selectie: de analyse is daarna opnieuw "
            "gedraaid en gaf exact dezelfde vijf bets."
        ),

        "STAGE_0_WIKKELDE_VIJF_PICKS_EN_ZEVENTIEN_SCHADUWRIJEN_AF": (
            "Vijf picks van 27 november afgewikkeld: VIER GEWONNEN EN ÉÉN VERLOREN. Gewonnen: "
            "Alanyaspor – Konyaspor Over 2.5 (1-2, drie doelpunten), Nottingham Forest – Chelsea "
            "Over 2.5 (3-2, vijf), Levante – Racing Santander Over 3.5 (1-3, vier) en Fluminense – "
            "Cruzeiro BTTS nee (0-1). Verloren: Leganés – Sabadell Over 2.0 (0-0, nul doelpunten). "
            "Alle vijf zijn competitieduels, dus de eindstand IS de stand na 90 minuten en de "
            "verlengingsregel van §6d komt niet aan de orde. REFLECTIE (§3 Stage 0, 12 okt 2026): "
            "vier van de vijf waren een doelpuntenmarkt en drie van die vier een Over, en alle "
            "drie die Overs wonnen — maar lees dat naast de meting van vandaag, want de Over-kant "
            "staat over 110 picks op +4,4% en op z = -1,87 in de goalbias. Eén dag is geen reeks "
            "(§6d). Het leerzaamste geval is de verliezer: bij Leganés – Sabadell verwachtte het "
            "model 2,6 doelpunt en er vielen er nul, en diezelfde wedstrijd hield óók een "
            "schaduwrij op de underdog-kant tegen (Sabadell wint @3.40) die op 0-0 eveneens "
            "verloor. Daar deed de poort dus zijn werk op een duel dat de analyse verkeerd had "
            "ingeschat. Zeventien schaduwrijen afgewikkeld: negen gewonnen, zeven verloren, één "
            "void (Jong AZ Alkmaar – TOP Oss, door de bron als afgelast gemeld). Sønderjyske – "
            "Brøndby IF (1-1) leverde er drie, en alle drie gewonnen: de Under 2.5 die op de "
            "herijking sneuvelde, de Asian Handicap +0.75 die poort 8 tegenhield en de Under 3 die "
            "poort 9 tegenhield. Drie poorten die op dat ene duel samen drie winnaars hebben "
            "tegengehouden — vermeld, niet gelezen als bevinding."
        ),

        "STAGE_MIN_2_HONDERD_TAKKEN_NAGELOPEN_OP_DE_INHOUD_EN_NIET_OP_DE_GRAAF": (
            "De container kreeg de repo als ONDIEPE KLOON (`--is-shallow-repository` -> true), en "
            "vóór het unshallowen meldden 90 van de 103 takken 'eigen commits', tot 730 stuks. Dat "
            "was het valse alarm waar §3 Stage -2 voor waarschuwt: zonder de volledige "
            "geschiedenis bestaat het punt waar twee takken uit elkaar gingen niet en telt "
            "`rev-list HEAD..<tak>` élke commit van vóór de knip mee. Na "
            "`git fetch --unshallow origin` (main van 57 naar 806 commits) houden NUL van de 103 "
            "takken eigen commits over. DAARNA IS OP DE INHOUD VERGELEKEN EN NIET OP DE GRAAF, "
            "zoals §3 Stage -2 sinds 27 september eist: per unieke blobversie van alle vijf de "
            "logboeken zijn de record-id's tegen main gelegd — picks.jsonl (609 records, 77 "
            "blobvarianten), shadow.jsonl (2269, 94), context-log.jsonl (2637, 91), "
            "calibration.jsonl (9369, 94) en coverage.json (50 competities, 49 varianten). MAIN IS "
            "OP ALLE VIJF EEN SUPERSET: nul records die main mist. In source-health.json stond één "
            "sleutel die main niet heeft, `oddspapi`, en dat is GEEN verloren meting maar een "
            "bewuste verwijdering — commit f342894, 'OddsPapi-reserve verwijderd na overstap naar "
            "20K-plan' — net als de vier dubbele schaduwrijen van 7 november die §3 Stage -2 "
            "uitdrukkelijk NIET wil laten terugkomen. Er is dus niets gemerged en er viel niets te "
            "mergen. De run staat op `main` (`git push origin HEAD:main`, §6a), met expliciete "
            "toestemming in de scheduler-tekst."
        ),

        "DE_MARGEKALIBRATIE_HEEFT_EEN_CEL_BOVEN_TWEE_STANDAARDFOUTEN_EN_DAT_IS_HET_GELIJKSPEL": (
            "`margins.py stats --since 2026-09-20` over 1718 homogene duels heeft precies ÉÉN cel "
            "boven twee standaardfouten, en dat is het gelijkspel: voorspeld 23,6% tegen werkelijk "
            "20,8%, -2,8 pp. Derde dag op rij dezelfde cel. Op de volle reeks (2521 duels, beide "
            "`shrink`-instellingen door elkaar) is het -1,5 pp en haalt ze de grens niet. DIT RAAKT "
            "ÉÉN BET VAN VANDAAG: Motherwell – Hibernian is een DRAW NO BET, en dat is de markt "
            "waar het gelijkspel uit de berekening wordt gedeeld. Een grid dat te veel "
            "gelijkspelmassa legt, verdeelt die massa bij een DNB over beide ploegen naar rato, dus "
            "het effect op de DNB-kans is tweede-orde en niet eenduidig van teken — maar het is "
            "niet nul, en bij een handicap op 0.0 geldt hetzelfde. De kant waar §6f oorspronkelijk "
            "over ging staat recht: 'favoriet wint met 3 of meer' op -0,9 pp over 483 duels met een "
            "duidelijke favoriet, en 'wint met 4 of meer' op +0,3 pp. Dat gat is dicht sinds de "
            "shrink-overstap en dat blijft zo."
        ),

        "WAT_PINNACLE_ERVAN_VINDT_EN_HIJ_IS_HET_BIJ_VIER_VAN_DE_VIJF_ONEENS": (
            "Stage 5 stap 2 (§3, 20 sep 2026): geschreven voorspellingen zijn niet te halen "
            "(Forebet 403, Pinnacle-artikelen 404, Matchbook 530), dus de enige publieke "
            "expertlezing is DE PRIJS VAN PINNACLE APART. Over 48 duels met een Pinnacle-1X2 wijkt "
            "het model gemiddeld 3,93 pp af bij een gemiddelde Pinnacle-marge van 3,61% — tegen 6 "
            "tot 10% bij de rest, dus dit is de strengste toets die er is. PER GEPUBLICEERDE REGEL, "
            "EN HET IS GEEN GUNSTIG BEELD: Manchester United – Brentford staat 14,54 pp MEER "
            "doelpunten dan Pinnacle (eigen P(Under 3.0) 34,8% tegen 49,4%); Hamburger SV – Bayern "
            "München 11,50 pp meer (eigen P(Under 3.5) 38,4% tegen 49,9%); Torino – Lazio 11,20 pp "
            "meer UNDER (60,6% tegen 49,4%); Motherwell – Hibernian geeft Motherwell 44,1% waar "
            "Pinnacle 35,9% geeft, +8,18 pp. Bij Vitória de Guimarães – Estrela da Amadora noteert "
            "Pinnacle geen 1X2 en geen totaal, dus daar is geen vergelijking. VIER VAN DE VIER "
            "VERGELIJKBARE REGELS LIGGEN DUS MEER DAN ACHT PROCENTPUNT VAN DE SCHERPSTE BOOKMAKER "
            "AF, en §1g heeft op 552 gevallen gemeten dat de grootste geclaimde edge het SLECHTSTE "
            "rendement geeft. Dit getal gaat niet in `my_prob` en niet in `prob_sources` (§2, §4) — "
            "het is marktafgeleid en het hoort in de vergelijking. Maar het hoort er wél te staan: "
            "een lijst van vijf is een rangschikking van wat het model het sterkst vindt, niet een "
            "gevonden voordeel (§5b)."
        ),

        "DE_DRIE_BRONNEN_DIE_ER_UIT_LIGGEN_EN_WAT_DAT_VANDAAG_KOST": (
            "UNDERSTAT LIGT ER VOOR DE TIENDE RUNDAG UIT, en vandaag kost dat iets: alle vijf de "
            "competities die hij dekt (PL, Serie A, La Liga, Bundesliga, Ligue 1) spelen, met "
            "samen twintig duels, dus het kalibratieblok van §6e mist bij die twintig de "
            "`p_xg_understat`-arm en er is vandaag geen tweede, onafhankelijk xG-model. Drie van de "
            "vijf gepubliceerde regels staan in die vijf competities. Wat het NIET raakt: `my_prob` "
            "komt uit Fotmob-xG en Fotmob-splits en verandert hier niet door (§4, 31 aug 2026 — "
            "Understat is redundantie en meting, geen invoer), en §2 blijft gedekt omdat Fotmob "
            "levert. Zou Fotmob ook omvallen, dan is er geen onafhankelijke kansinput meer en wordt "
            "élk duel `NONE`; dát is het geval dat §3 vooraan in de notificatie wil hebben, en het "
            "is vandaag niet aan de orde. `API_FOOTBALL_KEY` ontbreekt met opzet (besluit van de "
            "gebruiker, 27 sep 2026) en is geen gat en geen actiepunt. The Odds API staat op 18809 "
            "credits over van 20000; 33 van de 34 sportkeys van de repo zijn vandaag actief, en de "
            "enige inactieve is `soccer_uefa_europa_conference_league` — een competitie die vandaag "
            "toch geen duels heeft, dus het kost niets. Vijf actieve sportkeys kent de repo niet "
            "(Brazil Série B, Coupe de France, 3. Liga, Superettan, Nations League) en geen van de "
            "vijf staat op de runlijst van Run A."
        ),
    }
