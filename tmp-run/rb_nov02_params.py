"""De `parameters`-tekst van Run B, 2 nov 2026 — apart gehouden zodat `rb_nov02_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **EEN REKENFOUT IN HET RUN B-SCRIPT IS GEVONDEN EN GEREPAREERD, EN HIJ BOND VANDAAG OP DE
  BOVENSTE REGEL.** `promotion.match_tier` is op 31 okt 2026 toegevoegd nadat bleek dat elk
  runscript de `data_tier` van een DUEL met een kale toewijzing berekende, twee keer achter
  elkaar (thuis, dan uit), waardoor de tweede de eerste overschreef. Die fix is diezelfde dag in
  het RUN A-script doorgevoerd en **niet** in het Run B-script. Vandaag stond Kalamata – Iraklis
  met +21,59 pp bovenaan de dagranglijst terwijl de omrekening van Kalamata BUITEN het gemeten
  bereik valt (relatieve aanval 2.105 tegen een gemeten 1.248–1.951, n=13). Het duel hoort op
  `data_tier = NONE` en is daarmee GEEN BET. Dat is exact de Coventry-val waarvoor
  `conversion_in_range` bestaat, en exact de orde van grootte die §4 ervoor noemt (+21 pp
  schijnedge die alle andere poorten haalt).
* **Alle drie de gepubliceerde regels staan op de UNDER-kant, en geen van de drie haalt zijn
  eigen lat.** Real Oviedo – Las Palmas +15,24 pp op een LIGHT-lat van 16,0; Mjällby – Kalmar FF
  +10,91 pp op diezelfde 16,0; Atromitos – NFC Volos +4,83 pp op een FULL-lat van 8,0 (en op de
  verzwaarde lat van poort 9 van 10,0). Ze staan er dus alle drie op RANGORDE (§5b) en niet op
  gevonden voordeel. Dat is de slechtst mogelijke samenstelling gegeven §6g, waar de Under-kant
  op −16,5% over 76 picks staat.
* **De tweede bron is het eens met de eerste op de Under-richting, en dat is slecht nieuws.**
  Over de 3 zuivere halve lijnen die tegen Pinnacle te leggen zijn, staat de eigen P(Under)
  gemiddeld +7,46 pp hoger en op 3 van de 3 erboven — Real Oviedo +9,81 pp, Mallorca +7,05 pp en
  Mjällby +5,51 pp. Over alle 7 toetsbare (duel, lijn)-paren is het +3,69 pp op 5 van de 7.
* **De marktvormtelling spreekt twee van de drie regels tegen** (§4, "Hoe vaak ging deze markt
  eerder op?"). Real Oviedo kwam in zijn laatste vijf duels één keer onder 2,5 (gemiddeld 3,60)
  en Las Palmas ook één keer (3,40; uit zelfs 3,80); Atromitos staat dit seizoen op 43% onder 2,5,
  thuis op 33%, en in zijn laatste vijf duels scoorden BEIDE ploegen vijf van de vijf keer.
  Alleen Mjällby – Kalmar FF wordt door de telling gesteund (54–62% onder 2,5).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0199, b=0,0129 op "
            "6840 afgerekende gevallen, fitted_through 2026-11-01. DAT IS DE VORIGE RUNDAG, dus "
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
        "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
        "REPARATIE_MATCH_TIER_EN_WAT_ZE_VANDAAG_HEEFT_TEGENGEHOUDEN": (
            "DIT IS DE BEVINDING VAN DEZE RUN. promotion.match_tier bestaat sinds 31 okt 2026 en "
            "zegt dat de data_tier van een DUEL de ZWAKSTE van zijn twee kanten is, omdat beide "
            "sterktes in dezelfde lambda gaan. De fix is op 31 oktober in het RUN A-script "
            "doorgevoerd en NIET in het Run B-script; Run B heeft daarom op 31 okt en 1 nov nog met "
            "de kale toewijzing gedraaid. Op die twee dagen bond het niet (geen enkel duel had de "
            "buitenbereik-ploeg thuis), vandaag wel: Kalamata – Iraklis. Kalamata komt uit Super "
            "League 2 groep B met een relatieve aanval van 2.105, en het gemeten invoerbereik van "
            "het Griekse divisiepaar is 1.248–1.951 (n=13) — dus BUITEN bereik, dus geen meting op "
            "het niveau waarop gespeeld wordt, dus NONE (Sec. 4, conversion_in_range is een POORT en "
            "geen aantekening). Zonder de reparatie stond dit duel vandaag met +21,59 pp en "
            "selection_score 6,83 BOVENAAN de dagranglijst en was het de bet van de dag geweest, "
            "ruim boven zijn eigen LIGHT-lat van 16,0 pp. Een scan over data/run-state/*-run-b.json "
            "vindt drie eerdere Run B-duels waar de buitenbereik-ploeg thuis stond: Exeter City – "
            "Rotherham United (3 okt, bet), Girona – Mallorca (4 okt, bet) en Celta Fortuna – "
            "Tenerife (19 okt, geen bet). De eerste twee zijn dezelfde twee die het commitbericht "
            "van 31 oktober al noemt; beide zijn gewonnen, dus er is geen geld mee verloren. Die "
            "rijen zijn NIET herschreven — ze zijn historie."
        ),
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "15 duels in zes van de zeventien competities op een MAANDAGcap van 40 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. Czech First League, Eliteserien, Croatian HNL, Hungarian NB I, Serie B, "
            "2. Bundesliga, Swiss Super League, Austrian Bundesliga, English League One, English "
            "League Two en MLS hebben niets op de kalender: dat is GEEN WEDSTRIJD en geen gat "
            "(Sec. 3 Stage 2), en het is bij een tweede bron nagetrokken (zie hieronder). De "
            "datarijkdom liep van 4,5 tot 8,0 over de hele run; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg."
        ),
        "ALLE_DRIE_DE_REGELS_STAAN_OP_DE_UNDER_KANT_EN_GEEN_VAN_DE_DRIE_HAALT_ZIJN_LAT": (
            "LEES DIT VOORDAT ER IETS WORDT INGEZET. De dagranglijst van Sec. 5b bestaat vandaag uit "
            "drie keer Under 2,5: Real Oviedo – Las Palmas @1,9604 (+15,24 pp, LIGHT, lat 16,0), "
            "Mjällby – Kalmar FF @1,9506 (+10,91 pp, LIGHT, lat 16,0) en Atromitos – NFC Volos "
            "@1,85 (+4,83 pp, FULL, lat 8,0 en met poort 9 erbij 10,0). GEEN VAN DE DRIE HAALT ZIJN "
            "EIGEN LAT; ze staan er op rangorde en de drempel gaat als label mee (Sec. 5b). Poort 9 "
            "houdt er geen van tegen, en dat is bij alle drie om een andere reden: bij de twee "
            "LIGHT-regels omdat de poort met opzet alleen op FULL geldt (besluit van de gebruiker, "
            "12 okt 2026), en bij Atromitos omdat hij alleen in de band 8–10 pp bindt — onder 8,0 is "
            "`edge` de bindende poort en niet poort 9 (unders.check, zie de code). Sec. 6g meet voor "
            "deze kant Under 76 picks op -16,5% tegen Over 62 picks op +10,6%, en P(Under 2.5) staat "
            "bij ELK duel ongeveer 2,4 pp te hoog door de vormfout in score_grid. Die fout is op "
            "28 okt 2026 onderzocht en NIET gerepareerd, omdat elke kandidaat-reparatie het symptoom "
            "verergerde (zie gridfit.py). De oorzaak is er dus nog, en vandaag staat de hele lijst "
            "op de kant waar ze het hardst doorwerkt."
        ),
        "PINNACLE_IS_HET_EENS_MET_DE_RICHTING_EN_DAT_IS_GEEN_STEUN_MAAR_EEN_WAARSCHUWING": (
            "De scherpste bookmaker van de markt (Sec. 3 Stage 5, stap 2) zet de Under-kant vandaag "
            "LAGER dan het eigen model, en precies op de lijnen die geen push kennen. Over de drie "
            "zuivere halve lijnen: Real Oviedo 60,5% eigen tegen 50,6% Pinnacle (+9,81 pp), Mallorca "
            "57,4% tegen 50,4% (+7,05 pp) en Mjällby 55,5% tegen 50,0% (+5,51 pp) — 3 van 3 erboven, "
            "gemiddeld +7,46 pp, bij een Pinnacle-marge van 3,4 tot 4,2%. Over alle zeven toetsbare "
            "(duel, lijn)-paren +3,69 pp op 5 van de 7. Dat is dezelfde richting als de scheefstand "
            "die Sec. 6g op UITKOMSTEN heeft gemeten, nu zichtbaar in een onafhankelijke bron, en "
            "het is dus een tweede reden om deze drie regels als 'het beste van een zwakke dag' te "
            "lezen in plaats van als gevonden voordeel. Bij Atromitos – NFC Volos is deze controle "
            "NIET te doen: Pinnacle prijst dat duel niet, noch op 1X2 noch op totalen."
        ),
        "DE_MARKTVORMTELLING_SPREEKT_TWEE_VAN_DE_DRIE_REGELS_TEGEN": (
            "Sec. 4 eist dat de telling wordt genoemd ook (juist) als ze de bet tegenspreekt, en "
            "vandaag doet ze dat bij twee van de drie. Real Oviedo kwam in zijn laatste vijf duels "
            "EEN keer onder 2,5 (gemiddeld 3,60 doelpunt) en Las Palmas ook een keer (3,40; in "
            "uitduels 3,80 over vijf); alleen Real Oviedo's vijf thuisduels steunen de bet (vier "
            "keer onder, gemiddeld 1,40). Atromitos staat dit seizoen op 3 van 7 onder 2,5 en thuis "
            "op 1 van 3, en in zijn laatste vijf duels scoorden BEIDE ploegen vijf van de vijf keer. "
            "Alleen Mjällby – Kalmar FF wordt gesteund: Mjällby thuis 8 van 13 onder 2,5 (gemiddeld "
            "2,54) en Kalmar uit 8 van 13 (2,31)."
        ),
        "GEEN_GEKWALIFICEERDE_SELECTIE_BUITEN_DE_LIJST": (
            "De afkapping op LIJSTLENGTE bindt vandaag niet: er is geen enkele selectie die alle "
            "poorten EN zijn drempel haalt, dus er valt niemand buiten de lijst van drie. De reeks "
            "`lijstlengte` groeit vandaag niet."
        ),
        "DE_TWEEDE_BRON_IS_HET_OVER_ALLE_ZEVENTIEN_COMPETITIES_EENS": (
            "Sec. 1 eist bevestiging door een tweede methode op de vraag WELKE wedstrijden er zijn, "
            "en vandaag is er geen enkele afwijking: BetExplorer geeft voor alle zeventien "
            "competities exact hetzelfde aantal duels in het inzetvenster als de Fotmob-daglijst, "
            "15 tegen 15, met de eerstvolgende ronde van de elf stille competities erbij (4 t/m "
            "14 november). 'Niet in de daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven "
            "zonder tweede bron — dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte."
        ),
        "EEN_FIXTURE_IS_EEN_DAG_OPGESCHOVEN_EN_DAT_RAAKT_EEN_SCHADUWRIJ_VAN_GISTEREN": (
            "Tenerife – FC Andorra stond op de Fotmob-daglijst van 1 november op "
            "2026-11-01T20:00Z en staat vandaag op 2026-11-02T13:00Z. Run B van 1 november heeft het "
            "duel daarom in zijn venster meegenomen en er een schaduwrij voor weggeschreven "
            "(failed_gate = context, datum 2026-11-01), en die rij staat nog op `pending` omdat de "
            "wedstrijd pas vanmiddag wordt gespeeld. Vandaag staat hetzelfde duel opnieuw in het "
            "venster en is het opnieuw op `context` gesneuveld (FC Andorra mist 32% van de "
            "selectiewaarde). Er wordt vandaag GEEN tweede schaduwrij voor weggeschreven: "
            "shadow.py collect boekt per (datum, wedstrijd) en de rij van 1 november beschrijft "
            "dezelfde wedstrijd en dezelfde poort. Wie de reeks `context` naleest moet weten dat "
            "deze ene wedstrijd met de datum van GISTEREN in het logboek staat."
        ),
    }
