"""De `parameters`-tekst van Run B, 20 nov 2026 — apart gehouden zodat `rb_nov20_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **De enige regel die zijn eigen lat haalt staat op de UNDER-kant, en Pinnacle is het daar het
  hardst oneens van alle zes toetsbare (duel, lijn)-paren van de dag** (+16,30 pp op de
  Under-kant bij Molde - Bodo/Glimt).
* **Twee van de drie gepubliceerde regels staan ONDER hun lat** en halen de lijst op rangorde
  (Sec. 5b): FC Volendam +15,10 pp op een LIGHT-lat van 16,0 en Arminia Bielefeld +3,41 pp op een
  FULL-lat van 8,0.
* **Een naamkoppeling is gerepareerd die TOP Oss - Roda JC Kerkrade al zijn prijzen kostte** —
  zie bevinding 1.
* **Elf van de zeventien duels staan in twee competities zonder xG EN zonder sportkey** (Keuken
  Kampioen Divisie en Romanian SuperLiga): op beide assen de zwakste van de dag.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, Sec. 6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0566, b=0,0365 op "
            "8001 afgerekende gevallen, fitted_through 2026-11-19. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (Sec. 6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band: het ruwe model zei "
            "gemiddeld 33,3% en het gebeurde 33,3%. Daardoor is 'herijkt haalt de lat, dus ruw ook' "
            "vandaag NIET waar - bij Molde staat de ruwe edge op +11,69 pp tegen +13,25 herijkt, en "
            "de vlag bet_beide is de controle en niet de redenering (Sec. 5a). LEES DE FIT NIET ALS "
            "'het model is goed gekalibreerd en dus goed': hij is gekalibreerd op de ONGESELECTEERDE "
            "ijksteekproef (Sec. 1g, 20 sep 2026), en de scheefstand die telt zit in de GESELECTEERDE "
            "groep. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "17 duels in zeven van de zeventien competities op een VRIJDAGcap van 55 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. De tien overige competities hebben niets op de kalender: dat is GEEN "
            "WEDSTRIJD en geen gat (Sec. 3 Stage 2), en het is langs drie wegen nagetrokken "
            "(idcheck.py afsluitcode 0, BetExplorer per competitie 17 van 17 eens, runwindow.py). "
            "De datarijkdom liep van 4,75 tot 8,0 over de hele run; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg."
        ),
        "MAX_SHORTLIST_IS_SINDS_19_NOV_DAGAFHANKELIJK": (
            "MAX_SHORTLIST komt uit ranking.max_shortlist(DAY) en staat op VRIJDAG op 3. De tabel is "
            "op 18 nov 2026 door de gebruiker gewijzigd naar 2 (ma-do) / 3 (vr) / 5 (za) / 4 (zo) en "
            "bindt vanaf 19 nov (ranking.SHORTLIST_BINDS_FROM); de oude tabel gaf op vrijdag 5. "
            "weekday() >= 4 is geen geldige lezing meer, want de zondag splitst van de zaterdag. "
            "MAX_DEEP_ANALYSES, de drempels en MAX_LIGHT_IN_SHORTLIST veranderen hier NIET door - "
            "alleen het aantal regels dat gepubliceerd wordt."
        ),
        "TWEE_VAN_DE_DRIE_REGELS_STAAN_ONDER_HUN_LAT_EN_DAT_IS_SEC_5B_ZOALS_ZE_IS_GESCHREVEN": (
            "Precies EEN selectie van de hele run haalt haar eigen lat: Molde - Bodo/Glimt, Under 4 "
            "@1,92 op FULL met +13,25 pp, ruim boven de 10,0 die poort 9 van een FULL-Under eist. "
            "Dat is MINDER dan MAX_SHORTLIST (3), en dan bepaalt volgens Sec. 5b de RANGORDE de "
            "lijst en is de drempel een LABEL per regel. Daarom staan FC Volendam - Jong Ajax "
            "(1X2 thuiswinst @1,70, LIGHT, +15,10 pp op een lat van 16,0; selection_score 5,581) en "
            "Arminia Bielefeld - Magdeburg (Draw No Bet @1,64, FULL, +3,41 pp op een lat van 8,0; "
            "score 2,195) wel in de lijst. LEES DIE TWEE DUS NIET ALS GEVONDEN VOORDEEL: het is de "
            "rangschikking van wat het model vandaag het sterkst vindt, en Sec. 1g heeft op 552 "
            "afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld "
            "oplevert. MAX_LIGHT_IN_SHORTLIST (2) bindt niet: er is een LIGHT-regel."
        ),
        "DE_BET_DIE_ZIJN_LAT_HAALT_IS_OOK_DE_GROOTSTE_AFWIJKING_VAN_PINNACLE_VAN_DE_DAG": (
            "DIT IS DE BELANGRIJKSTE WAARSCHUWING VAN DEZE RUN EN ZE IS MET EEN ONAFHANKELIJKE BRON "
            "NA TE REKENEN. Op de Pinnacle-lijn 4,0 van Molde - Bodo/Glimt zegt het eigen model "
            "P(Under) = 0,667 en het de-vigde Pinnacle-oordeel 0,504: +16,30 procentpunt, en dat is "
            "de grootste afwijking van alle zes toetsbare (duel, lijn)-paren van vandaag, bij een "
            "Pinnacle-marge van 3,4%. Over de hele run ligt de eigen Under-kant +2,04 pp boven "
            "Pinnacle met 4 van de 6 erboven; uitgesplitst +4,71 pp op de vijf lijnen MET push en "
            "-11,34 pp op de ene zuivere halve lijn. Dat is de richting die Sec. 6g op uitkomsten "
            "meet (Under 76 picks, -16,5% tegen Over 62 picks, +10,6%). Poort 9 bindt en deze regel "
            "haalt de verzwaarde lat van 10,0 pp WEL... op de edge tegen de AANBIEDER. Tegen Pinnacle "
            "gemeten is het verschil groter en niet kleiner. Dit getal gaat NIET in my_prob en "
            "verandert geen enkele pick van vandaag (Sec. 2) - het hoort in de vergelijking, en "
            "daarom staat het hier en bij de bet in het runrapport."
        ),
        "DE_ELF_ZWAKSTE_DUELS_VAN_DE_DAG_ZITTEN_IN_TWEE_COMPETITIES": (
            "Keuken Kampioen Divisie (9 duels) en Romanian SuperLiga (2) hebben GEEN xG bij Fotmob en "
            "GEEN sportkey bij The Odds API. Ze komen dus altijd op LIGHT uit met een lat van 16,0 pp "
            "(prompts/run-b.md) EN hun prijs is het gratis BetExplorer-marktgemiddelde, waar de "
            "bookmaker niet herleidbaar is en de edge systematisch te laag uitvalt (Sec. 1a). Elf van "
            "de zeventien duels zijn daarmee op beide assen de zwakste van de dag, en de enige "
            "LIGHT-regel in de lijst (FC Volendam) komt daar vandaan. Neem dekking nooit over van een "
            "andere competitie in hetzelfde land: Nederland heeft xG in de Eredivisie en niet in de "
            "Keuken Kampioen Divisie, Duitsland heeft het wel in de 2. Bundesliga."
        ),
        "EEN_NAAMKOPPELING_IS_GEREPAREERD_EN_ZE_KOSTTE_EEN_HEEL_DUEL": (
            "TOP Oss - Roda JC Kerkrade kwam bij de eerste doorrekening uit op 'geen prijzen gevonden "
            "voor deze wedstrijd': nul van de zes markten doorgerekend. De oorzaak zit in de namen en "
            "niet in de bron - BetExplorer heeft het duel gewoon, met 1X2 3,55/3,59/1,86, maar kort de "
            "clubnamen in tot de PLAATS: 'Oss' tegen Fotmobs 'TOP Oss' en 'Roda' tegen 'Roda JC "
            "Kerkrade'. is_abbreviation eist sinds 27 okt een voorvoegsel op woordniveau ('oss' is de "
            "staart van 'top oss', niet de kop) en best_pair haalt met 0,44 de vloer van 0,62 niet. "
            "Vier aliasregels in scripts/teamnames.py repareren het; na de reparatie heeft het duel "
            "drie selecties en een kalibratieblok. ZELFDE STILLE FAALSTAND als 'LA Galaxy' op 17 okt: "
            "de Keuken Kampioen Divisie heeft geen sportkey, dus het marktgemiddelde is daar de "
            "ENIGE prijsbron, en een duel zonder prijzen laat geen spoor na in het rapport."
        ),
        "DE_TWEEDE_BRON_IS_OVER_DE_HELE_LIJN_EENS": (
            "De bevestigingspoort van Sec. 1 gaf 17 van de 17 competities 'eens': 17 duels bij Fotmob "
            "en 17 bij BetExplorer, per competitie gelijk. Tien competities nul duels in het venster, "
            "Keuken Kampioen Divisie negen, 2. Bundesliga en Romanian SuperLiga elk twee, en "
            "Eliteserien, Segunda Division, Serie B en English League One elk een. Dat is de controle "
            "die prompts/run-b.md eist omdat een fout fotmob_id geen foutmelding geeft maar NUL "
            "wedstrijden, en nul wedstrijden leest als GEEN WEDSTRIJD. idcheck.py geeft daarnaast "
            "afsluitcode 0 op alle 33 id's uit coverage.json, ook die van de competities die vandaag "
            "stil zijn - dat is juist de controle die een stil verdwenen competitie kan vinden."
        ),
    }
