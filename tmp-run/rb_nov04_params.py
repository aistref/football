"""De `parameters`-tekst van Run B, 4 nov 2026 — apart gehouden zodat `rb_nov04_publiceer.py`
alleen de rekenlogica van 3 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **TWEE gepubliceerde regels en geen van beide haalt zijn eigen lat.** Botafogo – Atlético-MG
  Under 3 @1,83 (+6,34 pp op een FULL-lat van 8,0) en Oxford United – Reading DNB @1,9702
  (+7,49 pp op een LIGHT-lat van 16,0). Ze staan er dus op RANGORDE (§5b) en niet op gevonden
  voordeel.
* **De bovenste regel is een FULL-Under ónder de 8,0 pp, en poort 9 heeft hem daarom nooit
  getoetst.** Dat is de constructie van `unders.check` en geen vergeetachtigheid — maar het
  betekent dat de lijst niet-monotoon is: bij +8,50 pp zou deze bet zijn geblokkeerd en bij
  +6,34 pp staat hij bovenaan. Dezelfde waarneming als 31 okt en 3 nov; de vraag is op
  31 oktober aan de gebruiker voorgelegd en hoort niet elke dag opnieuw gesteld (§1h).
* **Pinnacle staat op de Under-kant 4 van 4 onder het eigen model, gemiddeld +4,47 pp**, en op de
  enige zuivere halve lijn +6,76 pp — ruim boven de +2,84 pp van gisteren. Dat is de tweede dag
  waarop `LEVEL_SCALE` bindt en er is dus géén aanwijzing dat de knop deze scheefstand al
  wegneemt; het zijn twee losse waarnemingen en geen meting (§6d eist ~30).
* **Drie van de vier Braziliaanse duels sneuvelen op een echte poort**, niet op de drempel: twee
  op poort 5 (de methodes wijzen tegengesteld) en São Paulo – Corinthians op poort 7, dat 49% van
  de selectiewaarde mist tegen 19% bij de tegenstander.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0299, b=0,0193 op "
            "6987 afgerekende gevallen, fitted_through 2026-11-03. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit staat vrijwel op de identiteit en VERHOOGT een kans licht over de hele "
            "speelbare band: het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET "
            "ALS 'het model is goed gekalibreerd en dus goed': het is gekalibreerd op de "
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
        "TWEE_REGELS_OP_RANGORDE_EN_GEEN_VAN_BEIDE_HAALT_ZIJN_LAT": (
            "LEES DIT VOORDAT ER IETS WORDT INGEZET. De dagranglijst van §5b bestaat vandaag uit "
            "TWEE regels van de drie plekken die MAX_SHORTLIST (3 op ma-do) biedt. (1) Botafogo - "
            "Atletico-MG, Under 3 @1,83 (Pinnacle via The Odds API), +6,34 pp op FULL-data, "
            "selection_score 3,867, aftrap 01:30 NL op 5 november. (2) Oxford United - Reading, "
            "Draw No Bet op Oxford United @1,9702 (Matchbook, beurs: 1,99 bruto), +7,49 pp op "
            "LIGHT-data, selection_score 2,181, aftrap 20:45 NL. De latten zijn 8,0 (FULL) en 16,0 "
            "(LIGHT) en geen van beide wordt gehaald, dus beide staan er op RANGORDE en de drempel "
            "gaat als label mee (§5b). Dit is het beste van zes doorgerekende duels, geen gevonden "
            "voordeel - en §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de "
            "herijkte edge bestaat die geld oplevert."
        ),
        "POORT_9_HEEFT_DE_BOVENSTE_REGEL_NOOIT_GETOETST_EN_DAT_IS_DE_CONSTRUCTIE": (
            "DIT IS DE BEVINDING VAN DEZE RUN. De bovenste regel is een Over/Under op de "
            "UNDER-kant met data_tier = FULL - precies de markt-en-kant waarvoor poort 9 op "
            "11 okt 2026 is ingevoerd omdat §6g daar -16,5% over 76 picks meet (en -28,2% over de "
            "66 FULL-Unders). Toch heeft die poort hem niet getoetst, en `unders.check` zegt zelf "
            "waarom: hij bindt UITSLUITEND in de band tussen de twee latten, 8,0 tot 10,0 pp. "
            "Onder 8,0 is `edge` de bindende poort - zo is het geschreven - maar sinds §5b op "
            "20 sep 2026 de edge-drempel uit de poorten heeft gehaald, is `edge` daar GEEN poort "
            "meer maar een afkapping, en kan een FULL-Under van +6,34 pp dus gepubliceerd worden "
            "terwijl dezelfde bet bij +8,50 pp door poort 9 zou zijn geblokkeerd. De lijst is op "
            "deze as dus niet-monotoon: meer voordeel claimen maakt de bet in de band 8-10 pp "
            "MINDER publiceerbaar. Dat is geen fout in de code - beide regels doen exact wat er "
            "staat - maar een gat tussen twee regels die op verschillende dagen zijn geschreven. "
            "DE RUN VERZET POORT 9 NIET OP EIGEN INITIATIEF (§1h, §6g): het is een keuze over "
            "risicobereidheid en die hoort bij de gebruiker. De vraag is op 31 oktober (Run A) en "
            "op 30/31 oktober (Run B) al voorgelegd en §1h zegt expliciet hem niet elke dag "
            "opnieuw te stellen; hij staat daarom vandaag als feit in het runrapport en onder "
            "'Stand van het logboek', niet als nieuw besluit. De reeks die hem moet beantwoorden "
            "is `doelpunten_onder` en die is op 12 oktober op nul begonnen."
        ),
        "PINNACLE_STAAT_OP_DE_UNDER_KANT_4_VAN_4_ONDER_HET_MODEL": (
            "De scherpste bookmaker van de markt (§3 Stage 5, stap 2) zet de Under-kant bij ALLE "
            "VIER de toetsbare (duel, lijn)-paren LAGER dan het eigen model, gemiddeld +4,47 pp, "
            "bij een gemiddelde Pinnacle-marge van 3,65%. Op de enige ZUIVERE halve lijn - "
            "Flamengo - Gremio, Under 3,5 - is het +6,76 pp (51,8% Pinnacle tegen 58,6% eigen), en "
            "bij de gepubliceerde regel Botafogo - Atletico-MG Under 3 is het +9,84 pp (53,0% tegen "
            "62,8% in de ruwe xG-methode; op een HELE lijn, dus met een push van 0,221 bij 3 "
            "doelpunten). Dat is dezelfde richting als de scheefstand die §6g op UITKOMSTEN meet. "
            "EN HET IS GROTER DAN GISTEREN, NIET KLEINER: op 3 november stond het op +2,84 pp over "
            "een zuivere halve lijn en +0,38 pp over alle vier de paren. Vandaag is de tweede dag "
            "waarop LEVEL_SCALE = 1.032 bindt, en er is dus GEEN aanwijzing dat de knop deze "
            "scheefstand wegneemt - maar twee dagen zijn twee waarnemingen en geen meting (§6d "
            "eist ~30, en §6g schrijft voor dat met `gridfit.py measure` te doen op de duels van "
            "na 3 november, niet met een redenering). Op 1X2 staat het model gemiddeld 5,41 pp van "
            "het Pinnacle-oordeel af over vier duels, met uitgerekend de gepubliceerde wedstrijd "
            "als uitschieter: Pinnacle geeft Botafogo 59,3% thuiszege en het model 43,0%, een "
            "verschil van 16,28 pp. De gepubliceerde Under komt dus uit het duel waarover het "
            "model het meest met de scherpste bookmaker van mening verschilt."
        ),
        "DRIE_BRAZILIAANSE_DUELS_SNEUVELEN_OP_EEN_ECHTE_POORT": (
            "Niet op de drempel maar op een poort die tegenhoudt omdat de selectie zelf niet "
            "deugt (§5b: de zeven andere poorten blijven poorten). Flamengo - Gremio (AH Gremio "
            "+2,25, +3,86 pp ruw) en Botafogo - Atletico-MG (AH Atletico Mineiro +1, +10,14 pp "
            "ruw) sneuvelen beide op POORT 5: de xG-methode verslaat de markt wel en de "
            "splitsmethode niet (+6,79 tegen -7,88 en +14,14 tegen -5,88). Bij Botafogo is dat de "
            "sterkste selectie van de dag op de ruwe schaal, score 6,56, en de reden dat de "
            "gepubliceerde regel van dat duel een Under is en geen handicap. Sao Paulo - "
            "Corinthians sneuvelt op POORT 7: Sao Paulo mist 49% van de selectiewaarde tegen 19% "
            "bij Corinthians - Sabino (uit voor het seizoen), Marcos Antonio (1-2 weken) en Artur "
            "(twijfelgeval) - en dat is ruim boven de 10 procentpunt waar poort 7 dichtgaat. Alle "
            "drie gaan als schaduwrij het logboek in en worden daar afgerekend (§6d)."
        ),
        "TWEE_DUELS_OP_NONE_EN_BEIDE_KEREN_OM_EEN_GEMETEN_REDEN": (
            "Artis Brno - Bohemians 1905 (Czech First League) en Athletico Paranaense - Vasco da "
            "Gama (Serie A BRA) komen op data_tier = NONE uit en dus op GEEN BET, en in beide "
            "gevallen is dat de JUISTE uitkomst en geen gat in de administratie. Artis Brno is "
            "promovendus uit de FNL en Tsjechie HEEFT sinds 9 okt 2026 een eigen gemeten factor "
            "(x0,608 aanval / x1,835 verdediging, n=12), maar `conversion_in_range` weigert: de "
            "relatieve verdediging van Artis Brno is 0,921 tegen een gemeten bereik van "
            "0,370-0,894. Dat is de Coventry-val waarvoor die poort bestaat - buiten het gemeten "
            "bereik is er geen meting, dus geen onafhankelijke kansinput op het niveau waarop "
            "gespeeld wordt (§4). Athletico Paranaense is promovendus uit de Serie B en daar is "
            "GEEN gemeten factor voor dat divisiepaar; `prompts/run-b.md` zegt dat expliciet, en "
            "een gepoolde factor erop zetten is precies wat §2 en §4 verbieden (dezelfde regel als "
            "bij Kroatie en Hongarije). Beide duels staan daarom als BUITEN DATADEKKING in de "
            "dekkingstabel en er valt geen markt voor door te rekenen."
        ),
        "DE_OMREKENING_VAN_OXFORD_UNITED_IS_GEMETEN_EN_BINNEN_BEREIK": (
            "De gepubliceerde LIGHT-regel staat op een OMGEREKENDE ploeg, en §4 eist dat de tekst "
            "van `GapResult.direction` wordt overgenomen in plaats van een samenvattende zin. Die "
            "tekst: Oxford United komt uit Championship (ENG) 2025/2026 (Fotmob 48), relatieve "
            "aanval 0,751 / verdediging 0,985 over 46 duels, omgerekend met gap_for(E1,E2,down) "
            "x1,559 / x0,638 [down] naar 1,171 / 0,628; conversion_in_range: E1/E2 down (n=33) - "
            "aanval 0,751 binnen 0,473-0,939 en verdediging 0,985 binnen 0,918-1,632. Dit is dus "
            "de NEERWAARTSE richting en ze loopt over een gemeten football-data-paar en NIET over "
            "`POOLED_GAP` - anders dan de Nederlandse tak (Keuken Kampioen Divisie <- Eredivisie), "
            "die daar nog wel op terugvalt (§4, besluit bij de gebruiker). EN EEN OMGEREKENDE "
            "PLOEG IS NOOIT FULL: `RESIDUAL_SPREAD` houdt na correctie ~0,16 relatieve sterkte "
            "over, dus dit duel is LIGHT en de lat staat er op 16,0 pp. Het lopende seizoen weegt "
            "voor 0,60 mee over 12 duels (§4 blend_seasons)."
        ),
        "GEEN_GEKWALIFICEERDE_SELECTIE_BUITEN_DE_LIJST": (
            "De afkapping op LIJSTLENGTE bindt vandaag niet: de lijst heeft drie plekken "
            "(MAX_SHORTLIST = 3 op ma-do) en er zijn twee regels. Er is geen enkele selectie die "
            "alle poorten EN zijn drempel haalt, dus er valt ook niemand buiten de lijst om die "
            "reden. De reeks `lijstlengte` groeit vandaag niet. MAX_LIGHT_IN_SHORTLIST (2) bindt "
            "evenmin: een van de twee regels staat op LIGHT."
        ),
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "6 duels in drie van de zeventien competities op een WOENSDAGcap van 40 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. Veertien competities hebben niets op de kalender: dat is GEEN "
            "WEDSTRIJD en geen gat (§3 Stage 2), en het is bij een tweede bron nagetrokken (zie "
            "hieronder). De datarijkdom liep van 5,5 tot 7,0 over de hele run; omdat er niet is "
            "afgekapt zijn 'laagste die het haalde' en 'hoogste die afviel' per definitie leeg."
        ),
        "DE_TWEEDE_BRON_IS_HET_OVER_ALLE_ZEVENTIEN_COMPETITIES_EENS": (
            "§1 eist bevestiging door een tweede methode op de vraag WELKE wedstrijden er zijn, en "
            "vandaag is er geen enkele afwijking: BetExplorer geeft voor alle zeventien "
            "competities exact hetzelfde aantal duels in het inzetvenster als de Fotmob-daglijst, "
            "6 tegen 6, met de eerstvolgende ronde van de veertien stille competities erbij (6 t/m "
            "14 november). 'Niet in de daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven "
            "zonder tweede bron - dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte."
        ),
        "MARKTBALANS_OP_DE_INKOOP_GEHAALD_MAAR_OP_TWEE_VAN_DRIE": (
            "§1a eist dat geen enkele run voor de hele runlijst maar een soort markt koopt, en de "
            "controle slaagt - maar krapper dan het getal suggereert. TWEE van de drie spelende "
            "competities hebben een sportkey bij The Odds API (English League One en Serie A BRA) "
            "en kregen allebei de bulk-aanroep met h2h + spreads + totals: per competitie zowel "
            "een uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U). Dat is 2 van 2 "
            "inkoopbaar en dus 100%, maar in absolute zin twee competities en niet twaalf. De "
            "DERDE - Czech First League - heeft GEEN sportkey en draait op het gratis "
            "BetExplorer-marktgemiddelde: daar is de bookmaker niet herleidbaar en valt de edge "
            "systematisch te laag uit (§1a), en het is uitgerekend ook de enige competitie van "
            "vandaag zonder xG. Dat duel is op beide assen de zwakste van de dag en komt op NONE "
            "uit, dus het heeft vandaag geen gevolg. Daarna is BTTS in een tweede ronde gekocht "
            "voor de vier duels met een kandidaat-edge (2 credits per duel). Totaal 6 + 4 = 10 "
            "credits van een plafond van 366, bij 19786 credits over en 27 dagen tot de "
            "maandwissel."
        ),
    }
