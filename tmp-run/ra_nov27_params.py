"""De `parameters`-tekst van Run A, 27 nov 2026 — apart gehouden zodat `ra_nov27_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `ra_nov25_params.py`).

Vijf dingen die vandaag vooraan horen:

* **ALLE DRIE DE GEPUBLICEERDE REGELS ZIJN EEN OVER**, en dat is voor het eerst sinds weken de
  andere kant van §6g. De Over-kant is de kant die aan de vormfout juist verdíent — maar
  `margins.py goalbias` meet daar vandaag voor het eerst een selectie-effect van enige omvang in
  de ándere richting: −0,374 doelpunt per duel over 83 gevallen, z = −1,85.
* **DE NIVEAUCORRECTIE IS VOOR HET EERST APART TE METEN EN HAAR TEKEN IS OMGESLAGEN.** Op de 519
  duels van ná 3 november staat het gemiddelde totaal op −0,116 (z = −1,43) waar het op de 1173
  duels ervóór op +0,099 (z = +1,92) stond, en de fout op `P(Under 2.5)` ging van −2,38 naar
  +2,22 pp. **De fout is niet kleiner geworden maar gespiegeld.** Een run verzet die knop niet op
  eigen initiatief en de vraag hoort pas voorgelegd bij ruim boven de ~900 duels (de lat die Run A
  op 21 nov zelf heeft gezet) — dus vandaag niet.
* **DE DERDE REGEL STAAT ER OP RANGORDE ÉN HAALT ZIJN LAT ALLEEN HERIJKT.** Levante – Racing
  Santander staat op `LIGHT` met +16,84 pp herijkt tegen +15,71 pp ruw, bij een lat van 16,0:
  `bet_beide` is **onwaar** en de regel wordt dus door de herijking gedragen. Dat is precies het
  geval waarvoor §5a die vlag heeft gebouwd, en de tegenhanger `herijking_omgekeerd` staat op
  −70,9% over zeven gevallen.
* **DE LIJSTLENGTE BINDT NIET**: twee selecties boven hun lat, drie plekken in de vrijdaglijst,
  dus de rangorde vult de derde plek aan (§5b stap 5) en er valt niets buiten de lijst.
* **UNDERSTAT LIGT ER VOOR DE NEGENDE RUNDAG UIT EN KOST VANDAAG WÉL IETS**: alle vijf de
  competities die hij dekt spelen, dus het kalibratieblok van §6e mist bij vijf duels de
  `p_xg_understat`-arm en er is vandaag geen tweede, onafhankelijk xG-model.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,041, b=0,027 op "
            "8847 afgerekende gevallen, fitted_through 2026-11-26. §6b-5c eist dat dat getal op de "
            "vorige rundag staat of daarna, en de vorige rundag IS 26 november, dus de fit is bij "
            "het rekenen van vandaag actueel. Dat komt doordat `calibration.py settle` vandaag in "
            "Stage 0 is gedraaid vóórdat `load_fit()` aan de analyse begon (72 waarnemingen "
            "afgewikkeld, 9246 van 9276 compleet). DE FIT VERHOOGT EEN KANS OVER VRIJWEL DE HELE "
            "SPEELBARE BAND: -0,2 pp op 30%, +0,2 pp op 40%, +0,7 pp op 50%, +1,0 pp op 60%, "
            "+1,3 pp op 70%, +1,3 pp op 80%. Bij alle drie de gepubliceerde regels tilt hij de kans "
            "dus OP, en bij de derde is dat beslissend: Levante – Racing Santander gaat van 63,33% "
            "ruw naar 64,46% herijkt en daarmee van +15,71 pp naar +16,84 pp, langs een lat van "
            "16,0. `bet_beide` is bij die regel ONWAAR en bij de eerste twee waar. Het ruwe model "
            "zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET ALS 'het model is goed': het "
            "is gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de "
            "scheefstand die telt zit in de GESELECTEERDE groep — `ledger.py stats` verwachtte over "
            "537 afgewikkelde bets 322,2 winnaars en er werden er 249 (-73,2), met een Brier van "
            "0,2630 tegen 0,2433 voor de markt. De markt schat nog steeds scherper, en dat is de "
            "regel die telt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",

        "ALLE_DRIE_DE_REGELS_ZIJN_EEN_OVER_EN_DAT_IS_DE_ANDERE_KANT_VAN_6G": (
            "LEES DIT EERST. Nottingham Forest – Chelsea Over 2.5, Alanyaspor – Konyaspor Over 2.5 "
            "en Levante – Racing Santander Over 3.5: drie doelpuntenmarkten, alle drie op de "
            "OVER-kant. §6g meet dat de Over-kant de kant is die aan de vormfout van `score_grid` "
            "juist VERDIENT — te weinig massa op 4 en 5 doelpunten maakt elke Over goedkoper dan "
            "hij is — en over het hele logboek staat Over op +4,4% over 110 bets tegen Under op "
            "-15,2% over 192. Dat is nog steeds het beste beeld van de twee. MAAR: de Over-reeks "
            "is sinds §6g werd geschreven gezakt van +10,6% (n=62) naar +4,4% (n=110), en "
            "`margins.py goalbias` meet op de Over-kant voor het eerst een selectie-effect van "
            "enige omvang: -0,374 doelpunt per duel over 83 gevallen bij z = -1,85, waar §6g nog "
            "n=38 en z=-0,54 noteerde. Dat wijst dezelfde kant op als de Under-fout, in spiegel: "
            "de routine speelt Over juist daar waar haar lambda te HOOG staat. Het haalt de lat "
            "van deze repo niet (|z| < 2) en er wordt vandaag dus niets aan verzet, maar het hoort "
            "bij elke Over-regel van vandaag genoemd te worden en het is het eerste cijfer dat de "
            "'Over betaalt mee aan dezelfde fout'-lezing van §6g onder druk zet. Ter vergelijking "
            "de Under-kant vandaag: +0,661 doelpunt per duel over 153 gevallen, z = +4,92."
        ),

        "DE_NIVEAUCORRECTIE_IS_VOOR_HET_EERST_APART_TE_METEN_EN_HAAR_TEKEN_IS_OMGESLAGEN": (
            "§6g schrijft voor hoe te zien of `model.LEVEL_SCALE` = 1.032 heeft geholpen: 'op de "
            "duels van ná 3 november hoort de regel gemiddeld totaal van gridfit.py measure naar "
            "nul te zakken en de fout op P(Under 2.5) klein te blijven'. Die reeks staat vandaag op "
            "519 duels en is voor het eerst apart gemeten (`tmp-run/ra_nov27_gridfit_na_niveau.txt`, "
            "`gridfit.measure` op de twee deelpopulaties). De uitkomst:\n"
            "  20 sep t/m 2 nov (1173 duels, ZONDER correctie): gemiddeld totaal +0,099 (z = +1,92), "
            "P(Under 2.5) -2,38 pp, P(Under 3.5) -0,96 pp.\n"
            "  3 nov t/m 26 nov (519 duels, MET correctie):      gemiddeld totaal -0,116 (z = -1,43), "
            "P(Under 2.5) +2,22 pp, P(Under 3.5) +2,46 pp.\n"
            "DE FOUT IS NIET KLEINER GEWORDEN MAAR GESPIEGELD. Het teken is op alle drie de regels "
            "omgeslagen en de absolute omvang is vrijwel gelijk (2,38 -> 2,22 pp op Under 2.5). Dat "
            "is een derde geval dat §6g niet heeft voorzien: de regel daar beschrijft 'blijft die op "
            "+0,1 staan, dan heeft de correctie niet gedaan wat ze moest doen', en wat er gebeurd is, "
            "is dat ze dóórgeschoten is. Een tweede bevestiging uit dezelfde meting: op die 519 duels "
            "geeft `scale = 1.032` nóg een keer toepassen t = -2,12 — de enige variant in die tabel "
            "die de lat van deze repo haalt, en dan in de ONGUNSTIGE richting. "
            "ER WORDT VANDAAG NIETS VERZET EN DE VRAAG WORDT NIET VOORGELEGD. Run A heeft op 21 nov "
            "zelf de lat gezet op 'ruim boven de ~900 duels' en het zijn er 519; z = -1,43 haalt de "
            "lat van |t| = 2 niet, en §6g eist uitdrukkelijk dat zo'n knop niet op eigen initiatief "
            "wordt verzet en de vraag niet te vroeg wordt gesteld (§9 rem 3). Wat vandaag verandert "
            "is alleen dat de reeks voor het eerst leesbaar is en dat haar richting bekend is."
        ),

        "DE_DERDE_REGEL_WORDT_DOOR_DE_HERIJKING_GEDRAGEN_EN_DAT_STAAT_ER_MET_OPZET_BIJ": (
            "Levante – Racing Santander, Over 3.5 @2.10 op `LIGHT`, is de derde regel van vandaag en "
            "de enige waarbij `bet_beide` ONWAAR is: +16,84 pp herijkt tegen +15,71 pp ruw, bij een "
            "LIGHT-lat van 16,0. Hij haalt zijn lat dus alléén nadat de fit van vandaag zijn kans "
            "met 1,13 pp heeft OPGETILD. §5a heeft dit geval voorzien ('vertrouw de redenering niet "
            "meer, vertrouw de vlag') en de code boekt zo'n kandidaat normaal als "
            "`failed_gate = herijking_omgekeerd`; vandaag wordt hij een gepubliceerde bet, omdat §1 "
            "en §5a de HERIJKTE kans als publicatieschaal aanwijzen en alle overige poorten open "
            "staan. Lees hem met de reeks ernaast: `herijking_omgekeerd` staat op -70,9% over zeven "
            "afgewikkelde gevallen (1 winnaar op 7). Dat zijn er veel te weinig om iets te zeggen "
            "(§6d eist ~30) en het wijst niet de kant op die de publicatie steunt. "
            "MAX_LIGHT_IN_SHORTLIST = 2 en dit is de enige LIGHT-regel, dus die grens bindt niet. "
            "De omrekening zelf: Racing Santander komt uit LaLiga2 (ESP) 2025/2026, relatieve aanval "
            "1.628 en verdediging 1.104 over 42 duels, omgerekend met de gemeten SP1/SP2-factor "
            "x0.661 / x1.498 naar 1.076 / 1.653, en `conversion_in_range` laat beide binnen het "
            "gemeten bereik door. Een omgerekende ploeg is nooit FULL (§4), vandaar de LIGHT-lat."
        ),

        "DE_LIJSTLENGTE_BINDT_NIET_EN_DE_DERDE_PLEK_IS_OP_RANGORDE_GEVULD": (
            "MAX_SHORTLIST is 3 op vrijdag (`ranking.max_shortlist`, §0, bindend sinds 19 nov 2026). "
            "Twee selecties stonden boven hun eigen lat (Nottingham Forest – Chelsea +9,78 pp op een "
            "FULL-lat van 8,0 en Alanyaspor – Konyaspor +11,11 pp op dezelfde lat), dus §5b stap 5 "
            "zegt dat de RANGORDE de lijst bepaalt en de drempel alleen als label meegaat. De derde "
            "plek is daarmee aangevuld met Levante – Racing Santander. Er valt NIETS buiten de lijst: "
            "geen `lijstlengte`-rij en geen groene regel bovenaan de dekkingsrapportage vandaag. "
            "De stand van die reeks noemen we evengoed, zoals §5b voorschrijft: 34 afgewikkelde "
            "gevallen, +4,60u = +13,5%, waar de gebruiker bij 100 opnieuw kijkt. Op 20 november "
            "stond ze op 30 gevallen en +20,8%; ze is dus gegroeid en in rendement gezakt. Niets te "
            "beslissen — de lat is 100, niet 30."
        ),

        "UNDERSTAT_LIGT_ER_VOOR_DE_NEGENDE_RUNDAG_UIT_EN_KOST_VANDAAG_WEL_IETS": (
            "Understat is vandaag opnieuw bevraagd voor alle vijf zijn competities (EPL, La_liga, "
            "Bundesliga, Serie_A, Ligue_1, seizoen 2026) en geeft vijf keer hetzelfde beeld: HTTP 200 "
            "met 26.719 bytes en geen JSON — `UnderstatError: geen JSON terug`. Dat is exact hetzelfde "
            "foutbeeld en dezelfde bytelengte als op 26 november, dus er is niets veranderd; het is de "
            "negende rundag op rij. ANDERS DAN DE AFGELOPEN RUNDAGEN KOST HET VANDAAG WÉL IETS: alle "
            "vijf de competities die hij dekt spelen in het inzetvenster (Nottingham Forest – Chelsea, "
            "Venezia – Bologna, Levante – Racing Santander, Werder Bremen – Borussia Mönchengladbach, "
            "Brest – Paris FC). Twee gevolgen, en geen van beide raakt een gepubliceerde bet: het "
            "kalibratieblok van §6e mist bij die vijf duels de arm `p_xg_understat`, dus de "
            "vergelijking tussen twee xG-modellen staat vandaag stil, en `prob_sources` heeft geen "
            "tweede, onafhankelijk xG-model. §2 blijft gedekt: Fotmob levert team-xG, thuis/uit-splits "
            "en de wedstrijdcontext, en dat zijn de inputs waarop de drie regels van vandaag staan. "
            "Dit is NIET het geval waarvoor §3 punt 3 een notificatie vooraan eist — dat gaat over "
            "FOTMOB, en Fotmob leverde vandaag alles (twee daglijsten, 24 competitiestanden, context "
            "voor 14 van 14 duels, voorbeschouwingsdata en de afwikkeling van Stage 0)."
        ),

        "POORT_5_VANGT_DRIEKWART_WEG_EN_POORT_7_KOSTTE_TWEE_DUELS": (
            "Over 202 doorgerekende selecties is `tweede_methode` (poort 5) de eerste dichte poort bij "
            "149 — driekwart. Dat is dezelfde stand als op 26 november (veertien van de vijftien "
            "selecties) en het is nu een reeks van dagen. Lees het met de volgorde erbij: "
            "`failed_gate` geeft alleen de EERSTE dichte poort in ORDER, en `tweede_methode` staat "
            "daar vooraan, dus dit getal is een bovengrens voor wat poort 5 alléén tegenhoudt. Wat "
            "de reeks zegt: 347 afgewikkelde kandidaten, -2,3% — de poort bespaart geld, maar "
            "nauwelijks. De rest van de dag: context 18, edge 16, underdog 6, odds 3, "
            "doelpunten_onder 2, robuustheid 1, en 7 selecties met alle poorten open. "
            "POORT 7 KOSTTE VANDAAG TWEE HELE DUELS, en bij beide ging het om een forse "
            "uitvallerslijst: Werder Bremen – Borussia Mönchengladbach (Gladbach mist 38% van de "
            "selectiewaarde tegen 28% bij Werder — Hashioka, Leszczyński, Ullrich) en Brest – Paris "
            "FC (Brest mist 49% tegen 10% — Doumbia, Lala, Le Guen). Die reeks is de scherpste die "
            "het schaduwlogboek heeft: 153 afgewikkelde gevallen op -23,8%."
        ),

        "TWAALF_VAN_DE_ZESTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_TWEE_BRONNEN_NAGETROKKEN": (
            "Veertien duels in het inzetvenster [27 nov 08:00 NL, 28 nov 08:00 NL), verdeeld over "
            "twaalf competities: elf met één duel, de Super Lig en de Ekstraklasa met twee. Vier "
            "competities van de runlijst hebben niets: de Scottish Premiership en de drie Europese "
            "toernooien, die hun league phase op 26 november hebben afgesloten. ALLE VEERTIEN DUELS "
            "KOMEN VAN DE DAGLIJST VAN DE RUNDAG ZELF (`source_day = 2026-11-27`) en alle veertien "
            "zijn speelbaar — geen enkel duel trapte af vóór 08:00 NL, dus de `playable`-regel van "
            "§3 Stage 1 bindt vandaag niet. Op twee bronnen nagetrokken (`ra_nov27_bevestiging.py`): "
            "Fotmob 14 duels, BetExplorer 14 duels, 22 van 22 competities eens — inclusief de vier "
            "zonder duel en de zes bekers. Dat is de poort 'bevestiging door een tweede methode' op "
            "de RUNLIJST zelf, en hij is vandaag voor het eerst sinds 20 november op alle 22 "
            "competities gesloten: de twee ontbrekende BetExplorer-adressen die Run A op 26 november "
            "als gat meldde (Primeira Liga en Super Lig) blijken er wél te staan en leverden beide "
            "een fixturepagina."
        ),

        "DE_ZES_BEKERS_STAAN_BUITEN_DE_RUNLIJST_EN_GEEN_VAN_ZES_SPEELT_VANDAAG": (
            "FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB Pokal en Copa del Rey vallen van "
            "1 juli t/m 31 december buiten de runlijst (`cups.filter_runlist` met de rundag, "
            "besluit van de gebruiker van 18 en 19 nov 2026). Ze krijgen de status "
            "`BUITEN DE RUNLIJST` en niet `GEEN WEDSTRIJD` — §5 verbiedt dat laatste met zoveel "
            "woorden. Vandaag maakt het feitelijk niets uit: geen van de zes heeft een duel in "
            "beide daglijsten (0, 0, 0, 0, 0, 0). De eerstvolgende ronde van de Coppa Italia staat "
            "op 1 december en van de DFB Pokal ook, dus geen van beide valt in de tweede "
            "seizoenshelft waarin ze weer meedoen; ze doen voor het eerst mee op 1 januari 2027."
        ),

        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "Veertien duels op een VRIJDAGcap van 55 (`ranking.max_deep_analyses(2026-11-27)`), dus "
            "`afgekapt = 0` en de dekkingstabel krijgt geen `AFGEKAPT`-regel. De datarijkdom van de "
            "run loopt van 5,0 tot 6,5 punten (laagste: Southampton – Middlesbrough en OH Leuven – "
            "Kortrijk, hoogste: Nottingham Forest – Chelsea, Werder Bremen – Gladbach, Brest – Paris "
            "FC en FC Groningen – Willem II). Omdat er niets is afgekapt zijn de twee getallen die "
            "Stage 4 eist ('laagste die het haalde' en 'hoogste die afviel') leeg, en dat is de "
            "juiste lege stand: er is geen onderkant als niemand afvalt. Context is voor 14 van 14 "
            "duels opgehaald, vóór de afkapping zoals §1c eist, dus het contextlogboek krijgt "
            "vandaag veertien rijen."
        ),

        "HET_NIVEAU_KOMT_BIJ_ELF_COMPETITIES_UIT_VORIG_SEIZOEN_EN_DENEMARKEN_UIT_HET_LOPENDE": (
            "`league_level` nam voor elf van de twaalf competities de route `vorig+uplift` en voor "
            "de Danish Superliga de route `lopend`: die staat op 15 van 22 speeldagen en is dus over "
            "de helft (`SEASON_MATURE_SHARE`). Dat is ook de reden dat Denemarken uit de gepoolde "
            "vroeg-seizoenscorrectie is WEGGELATEN — `uplift_observations` noemt dat zelf, en §3 "
            "Stage 5 eist dat een weggelaten waarneming in het runrapport staat in plaats van stil "
            "te verdwijnen. De gepoolde factor komt daarmee op 1.1059 over 137 speeldagen in elf "
            "competities (ongepoold 1.1121). Dat is een hoge factor en hij hoort zo: elf van de "
            "twaalf competities zitten op 10 tot 17 speeldagen van een seizoen van 30 tot 46, dus "
            "de correctie dooft nog niet uit. De twaalf niveaublokken staan per competitie in "
            "`data/run-state/` onder `niveau`, met de route erbij."
        ),

        "VIJF_DUELS_GINGEN_LANGS_DE_PROMOVENDI_OMREKENING_EN_ALLE_VIJF_KWAMEN_DOOR": (
            "Venezia (Serie A), Racing Santander (La Liga), Willem II (Eredivisie), Marítimo "
            "(Primeira Liga) en Kortrijk (Belgian Pro League) staan niet in de stand van 2025/2026 "
            "van hun huidige competitie en zijn omgerekend uit de divisie eronder (§4). ALLE VIJF "
            "KWAMEN DOOR `conversion_in_range` — er is vandaag geen enkel duel op `NONE` uitgekomen, "
            "en dat is bij vijf omrekeningen op veertien duels geen vanzelfsprekendheid: de "
            "Coventry-val heeft deze maand al meerdere duels gekost. De vijf duels zijn daarmee "
            "`LIGHT` en staan op de lat van 16,0 pp, want een omgerekende ploeg is nooit `FULL` "
            "(`RESIDUAL_SPREAD` laat na correctie nog ~0,16 relatieve sterkte staan). Twee van de "
            "drie gepubliceerde regels staan op een FULL-duel; de derde is een van deze vijf. De "
            "omrekeningsnoten staan per duel in `data/run-state/` onder `promovendi`."
        ),

        "DE_INKOOP_IS_VOLLEDIG_EN_DE_MARKTBALANS_SLAAGT_ZO_RUIM_ALS_HIJ_KAN": (
            "`suggest_cap(18884, 4)` gaf een plafond van 2358 credits en `split_budget(2358, 12)` "
            "gaf 12 spreads / 12 totals, dus alle twaalf inkoopbare competities kregen de volledige "
            "bulk-aanroep (h2h + spreads + totals, 3 credits elk = 36). Daarna 10 credits aan BTTS "
            "voor de tien duels met een kandidaat-edge (§1a stap 2, de vereniging van beide schalen) "
            "— samen 46 van 2358, en 18.838 credits over bij vier dagen tot de maandwissel. "
            "DE MARKTBALANS-CONTROLE VAN §1a SLAAGT ZO RUIM ALS HIJ KAN: twaalf van de twaalf "
            "competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt, niet één op twaalf. "
            "Wat eruit kwam over 202 selecties: Over/Under 76 (12 competities), Asian Handicap 50 "
            "(11), 1X2 35 (12), BTTS 20 (9), Draw No Bet 13 (8), Double Chance 8 (8). Alle drie de "
            "gepubliceerde regels komen uit Over/Under, en dat is vandaag dus GEEN uitkomst van de "
            "inkoop maar van de analyse — precies het onderscheid waarvoor §1a deze tabel eist. "
            "De 1X2-prijzen komen bij alle twaalf competities van The Odds API (beste prijs, na "
            "commissie via `net_price`); het BetExplorer-marktgemiddelde is alleen gebruikt waar §1a "
            "het voorschrijft: het kalibratieblok van §6e en poort 8."
        ),

        "STAGE_0_WIKKELDE_TWEE_PICKS_EN_VIERENDERTIG_SCHADUWRIJEN_AF": (
            "Alle openstaande rijen kwamen uit de league phase van de Europa League en de Conference "
            "League van 26 november, dus zonder verlenging: de eindstand van Fotmob IS de stand na "
            "90 minuten (§6d). TWEE PICKS: Lyon – Lillestrøm Under 3.5 @1.89 GEWONNEN op 0-0, en "
            "Union St.Gilloise – Lech Poznań Under 3.5 @1.76 VERLOREN op 2-2. Netto +0,89 - 1,00 = "
            "-0,11u. VIERENDERTIG SCHADUWRIJEN: 22 gewonnen, 11 verloren, 1 push (Ajax – Thun, "
            "Under 4 bij exact vier doelpunten). Dat de schaduwlijst zo goed liep en de bets niet, is "
            "één dag en geen reeks (§6d). Niets stond MIS en er is geen rij overgebleven: "
            "`ledger.py open` en `shadow.py open` geven na de afwikkeling beide 'geen'. "
            "De reflectie staat in het runrapport onder Afwikkeling en in gewone taal in het "
            "dagrapport."
        ),

        "STAGE_MIN_2_HONDERD_TAKKEN_NAGELOPEN_EN_ZESTIEN_MELDINGEN_DIE_GEEN_VERLIES_ZIJN": (
            "De repo kwam opnieuw als ONDIEPE KLOON aan (`--is-shallow-repository` -> true) en is "
            "unshallowed; daarna zijn 100 takken per record op de INHOUD vergeleken "
            "(`scripts/branchaudit.py`, §3 Stage -2 punt 2: '0 eigen commits is een uitspraak over "
            "de graaf, alleen een vergelijking per regel is een uitspraak over de metingen'). "
            "UITKOMST: `picks.jsonl` (603), `context-log.jsonl` (2605), `calibration.jsonl` (9259) en "
            "`coverage.json` (339) zijn VOLLEDIG op origin/main. Zestien records staan op een tak en "
            "niet op main, en alle zestien zijn bekend en géén verlies: vier `shadow.jsonl`-rijen van "
            "3 oktober die op 7 november MET OPZET zijn verwijderd omdat ze dubbel stonden (§3 Stage "
            "-2 noemt die vier bij naam en verbiedt ze aan te vullen), en twaalf bladpaden in "
            "`source-health.json` die per-run momentopnames zijn van oudere Run B/C-takken en door "
            "latere runs zijn overschreven. ER IS DUS NIETS GEMERGED EN ER VIEL NIETS TE MERGEN. "
            "Daarnaast: géén openstaande pick van een run die op een andere tak nooit is afgewikkeld "
            "— de enige twee openstaande picks waren die van Run A van 26 november zelf, en die zijn "
            "in Stage 0 afgewikkeld. DE RUN STAAT OP `main`: de scheduler geeft daar expliciet "
            "toestemming voor (§6a)."
        ),

        "DE_MARGEKALIBRATIE_HEEFT_EEN_CEL_BOVEN_TWEE_STANDAARDFOUTEN_EN_DAT_IS_HET_GELIJKSPEL": (
            "`margins.py stats --since 2026-09-20` (1692 duels met lambdas van ná de shrink-overstap) "
            "heeft één cel die meer dan twee standaardfouten van de voorspelling af staat: GELIJKSPEL "
            "voorspeld 23,6% tegen werkelijk 20,6%, -3,0 pp. Dat is dezelfde cel die Run A op "
            "26 november ook meldde, en ze staat nu een dag langer. Op de volle reeks (2495 duels, "
            "beide shrink-instellingen door elkaar) is het -1,6 pp en haalt ze de grens niet. Wat het "
            "betekent voor vandaag: niets, want geen van de drie gepubliceerde regels is een 1X2 of "
            "een markt waarin het gelijkspel verlies is — alle drie zijn doelpuntenmarkten zonder "
            "kant. Wat het voor de rangorde betekent is wél iets: §1a kiest `selection_score` deels "
            "omdat push-beschermde markten minder blootstaan aan juist deze fout, en een gelijkspel "
            "dat drie procentpunt te hoog staat raakt elke Draw No Bet en elke handicap op 0.0. "
            "De kant waar de margefout van §6f over ging staat recht: 'favoriet wint met 3 of meer' "
            "op -0,7 pp over 476 duels met een duidelijke favoriet."
        ),

        "WAT_PINNACLE_ERVAN_VINDT_EN_HET_WIJST_DEZELFDE_KANT_OP_ALS_DE_BETS": (
            "Stap 2 van Stage 5 (§3, 20 sep 2026) — het beste publieke expertoordeel dat bereikbaar "
            "is, LOS van de beste prijs waarop gespeeld wordt. Pinnacle is er voor 12 van de 14 "
            "duels (Levante – Racing Santander en Rizespor – Kasımpaşa niet), met een marge van 3,0 "
            "tot 4,8% tegen 6 tot 10% bij de rest. OP 1X2 staat het model gemiddeld 4,20 pp van zijn "
            "oordeel af — dicht, en de twee grootste afwijkingen zitten precies bij de twee duels "
            "die poort 7 heeft tegengehouden (Brest +15,78 pp op de thuiszege, Sønderjyske -9,19 pp "
            "op de uitzege). OP DE DOELPUNTENKANT IS HET BEELD SYSTEMATISCH EN HET STEUNT DE DRIE "
            "REGELS VAN VANDAAG: over 12 (duel, lijn)-paren staat het model gemiddeld 4,96 pp ONDER "
            "Pinnacle op `P(Under)`, oftewel het verwacht structureel MEER doelpunten dan de "
            "scherpste bookmaker. Bij Nottingham Forest – Chelsea is dat -11,44 pp op lijn 2,75 en "
            "bij Alanyaspor – Konyaspor -9,16 pp op lijn 2,25. LEES DAT TWEE KANTEN OP, want dat is "
            "de eerlijke lezing: het is de reden dat er vandaag drie Overs staan, en het is "
            "tegelijk precies de scheefstand die de `scale`-meting hierboven op de 519 duels van ná "
            "3 november terugvindt (het model verwacht daar 0,116 doelpunt per duel te VEEL). Niets "
            "hiervan gaat in `my_prob` of in `prob_sources` (§2, §5 stap 2); het staat ernaast."
        ),
    }
