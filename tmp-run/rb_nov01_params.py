"""De `parameters`-tekst van Run B, 1 nov 2026 — apart gehouden zodat `rb_nov01_publiceer.py`
alleen de rekenlogica van 31 oktober hoeft te zijn.

Vijf dingen die vandaag vooraan horen:

* **Drie van de vijf gepubliceerde regels staan op de UNDER-kant**, en dat zijn precies de drie
  duels waar de eigen kans het verst van Pinnacle af ligt: Atlanta United - Toronto FC +15,56 pp,
  Portland Timbers - Houston Dynamo FC +11,35 pp en Los Angeles FC - Minnesota United +4,39 pp.
* **De scheefstand van Sec. 6g is vandaag ook in een ONAFHANKELIJKE bron te zien.** Over alle 36
  toetsbare (duel, lijn)-paren ligt de eigen P(Under) gemiddeld +3,29 pp boven Pinnacle en staat
  27 van de 36 erboven. Uitgesplitst: op de 31 lijnen MET push +3,77 pp (24 van 31), op de 5
  zuivere halve lijnen +0,30 pp (3 van 5).
* **De bovenste 1X2 wijkt het hardst van Pinnacle af van alle 34 toetsbare duels.** Op
  Hannover 96 - Dynamo Dresden zegt het model 62,0% thuiswinst en Pinnacle 44,3%: +17,73 pp, bij
  een Pinnacle-marge van 3,1%.
* **Burgos CF - Castellón haalt zijn lat en valt tóch af op LIJSTLENGTE.** BTTS-"nee" @2,568 op
  +8,88 pp, alle poorten open, maar `selection_score` 4,24 is rang 6 bij MAX_SHORTLIST = 5. Twee
  regels die hem voorbijgaan staan ONDER de lat (+7,44 en +7,22 pp) en halen de lijst op rangorde;
  dat is Sec. 5b zoals ze is geschreven - score rangschikt, de drempel is een label - en de rij
  gaat als `failed_gate = "lijstlengte"` het schaduwlogboek in.
* **De tweede bron meldde ÉÉN afwijking en die is met een derde bron beslecht.** BetExplorer zette
  Vaduz - Sion op "Today 16:30"; Fotmob en The Odds API zetten het duel allebei op
  2026-11-07T17:00Z (speelronde 13). De 51 duels van Fotmob zijn dus juist en BetExplorer labelt
  een fixture van volgende week als vandaag.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0,994, b=-0,004 op "
            "6606 afgerekende gevallen, fitted_through 2026-10-31. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (Sec. 6b-5c eist die controle aan dit ene "
            "getal). De fit staat vrijwel op de identiteit: het ruwe model zei gemiddeld 33,3% en het "
            "gebeurde 33,3%, en de correctie haalt binnen de speelbare koersband nergens meer dan "
            "0,2 procentpunt van een kans af. LEES DAT NIET ALS 'het model is goed gekalibreerd en "
            "dus goed': het is gekalibreerd op de ONGESELECTEERDE ijksteekproef (Sec. 1g, 20 sep "
            "2026), en de scheefstand die telt zit in de GESELECTEERDE groep. Daarom staat poort 8 "
            "nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "51 duels in vijftien van de zeventien competities op een ZONDAGcap van 55 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. English League Two en Serie A (BRA) hebben niets op de kalender: dat is "
            "GEEN WEDSTRIJD en geen gat (Sec. 3 Stage 2). De datarijkdom liep van 4,5 tot 8,0 over de "
            "hele run; omdat er niet is afgekapt zijn 'laagste die het haalde' en 'hoogste die "
            "afviel' per definitie leeg."
        ),
        "DRIE_VAN_DE_VIJF_REGELS_STAAN_OP_DE_UNDER_KANT_EN_PINNACLE_IS_HET_ONEENS": (
            "DIT IS DE BEVINDING VAN DEZE RUN EN ZE IS MET VIER GETALLEN NA TE REKENEN. Atlanta "
            "United - Toronto FC (Under 3,5 @1,83), Portland Timbers - Houston Dynamo FC (Under 3,5 "
            "@1,65) en Los Angeles FC - Minnesota United (Under 3,5 @1,7154) zijn alle drie een "
            "FULL-Under, en op de Pinnacle-lijn van hetzelfde duel staat de eigen P(Under) "
            "respectievelijk +15,56, +11,35 en +4,39 procentpunt boven het de-vigde "
            "Pinnacle-oordeel. De eerste twee zijn de nummers 1 en 3 van alle 36 toetsbare (duel, "
            "lijn)-paren van vandaag. OVER DE HELE RUN ligt de eigen Under-kant +3,29 pp boven "
            "Pinnacle met 27 van de 36 erboven - en dat is precies de richting die Sec. 6g op "
            "uitkomsten meet (Under 76 picks, -16,5% tegen Over 62 picks, +10,6%). Poort 9 bindt "
            "en alle drie halen de verzwaarde lat van 10,0 pp WEL... op de edge tegen de "
            "AANBIEDER. Tegen Pinnacle gemeten is het verschil groter, niet kleiner, en dat is "
            "geen bevestiging maar een waarschuwing: Pinnacle heeft hier een marge van 3,6 tot "
            "3,9% tegen 6 tot 10% bij de rest. Dit getal gaat NIET in my_prob en verandert geen "
            "enkele pick van vandaag (Sec. 2) - het hoort in de vergelijking, en daarom staat het "
            "hier en bij de bets in het runrapport."
        ),
        "DE_BOVENSTE_1X2_IS_DE_GROOTSTE_AFWIJKING_VAN_PINNACLE_VAN_DE_DAG": (
            "Hannover 96 - Dynamo Dresden, 1X2 thuiswinst @2,2152: het model zegt 62,0% en Pinnacle "
            "44,3%, een verschil van +17,73 procentpunt en daarmee de grootste van alle 34 duels "
            "waar beide een 1X2 hebben (gemiddelde absolute afstand over die 34: 3,89 pp). De "
            "Pinnacle-marge is 3,1%, dus het is geen slappe prijs. Noteer het als de risicokant van "
            "de hoogst geplaatste uitkomstbet van vandaag en niet als extra onderbouwing."
        ),
        "GEKWALIFICEERD_MAAR_BUITEN_DE_LIJST": (
            "Burgos CF - Castellón, BTTS 'beide ploegen scoren - nee' @2,568 op +8,88 pp met alle "
            "negen poorten open. selection_score 4,24 is rang 6 bij MAX_SHORTLIST = 5, dus hij valt "
            "af op LIJSTLENGTE en niet op een poort. Vier selecties halen vandaag de lat van 8,0 pp "
            "- dat is MINDER dan MAX_SHORTLIST - en dan bepaalt volgens Sec. 5b de RANGORDE de lijst "
            "en is de drempel een label. Daardoor staan Portland (+7,44 pp, score 5,06) en Los "
            "Angeles (+7,22 pp, score 4,73) wél in de lijst en Burgos niet. Dat is de regel zoals "
            "ze is geschreven en geen omissie; de rij gaat als failed_gate = 'lijstlengte' het "
            "schaduwlogboek in, dezelfde naam als op 24 en 26 september (Sec. 5b, 26 sep 2026)."
        ),
        "DE_TWEEDE_BRON_MELDDE_EEN_AFWIJKING_EN_FOTMOB_HAD_GELIJK": (
            "De bevestigingspoort van Sec. 1 gaf 16 van de 17 competities 'eens'. De uitzondering is "
            "Swiss Super League: Fotmob 3 duels, BetExplorer 4. Het extra duel is Vaduz - Sion, dat "
            "BetExplorer op zijn fixturepagina als 'Today 16:30' labelt. Nagetrokken met een DERDE "
            "bron: Fotmob zet het op 2026-11-07T17:00Z in speelronde 13 en The Odds API geeft "
            "commence_time 2026-11-07T17:00:00Z - twee onafhankelijke bronnen tegen één. FC Vaduz "
            "staat wél in de stand van 2026/2027 (promovendus, twaalf ploegen) en speelde op "
            "31 oktober bij Grasshopper in ronde 12, dus hij is niet aan het verkeerde seizoen "
            "gekoppeld. De 51 duels van Fotmob zijn juist. LET OP DE FAALVORM: het 'Today'-label "
            "van BetExplorer is relatief aan zijn eigen pagina en niet aan de rundag, en een vals "
            "POSITIEF van de tweede bron ziet er precies zo uit als het echte geval van het "
            "Serie B-id (een competitie die stil een duel mist). Alleen een derde bron scheidt die "
            "twee."
        ),
    }
