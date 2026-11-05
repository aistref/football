"""De `parameters`-tekst van Run B, 5 nov 2026 — apart gehouden zodat `rb_nov05_publiceer.py`
alleen de rekenlogica van 4 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **NUL bets, en de reden is niet de drempel maar POORT 5.** Alle zeventien doorgerekende
  selecties van het enige analyseerbare duel sneuvelen op de bevestigingspoort: de xG-methode en
  de splitsmethode verslaan de markt nooit dezelfde kant op. Dat is iets anders dan "te weinig
  voordeel" en het hoort niet als zo'n dag te worden opgeschreven.
* **Eén van de zeventien competities speelt.** Série A (BRA) heeft twee duels in het
  inzetvenster; de overige zestien hebben niets op de kalender, en dat is bij BetExplorer als
  tweede bron nagetrokken (17 van 17 eens).
* **Palmeiras – Remo komt op NONE uit en dat is de voorgeschreven uitkomst.** Remo is
  promovendus uit de Série B en voor dat divisiepaar is er GEEN gemeten factor; `prompts/run-b.md`
  zegt dat met zoveel woorden.
* **De §5b-rangorde is vandaag leeg, niet afgekapt.** De NEAR-ondergrens van 3,0 pp op FULL is de
  bodem die `toplist._pool` en `ledger.py validate` samen bewaken, en de beste selectie van de dag
  staat op +1,62 pp. Wat te zwak is om te loggen, is te zwak om te spelen.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0287, b=0,0186 op "
            "7032 afgerekende gevallen, fitted_through 2026-11-04. DAT IS DE VORIGE RUNDAG, dus "
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
        "NUL_BETS_EN_POORT_5_IS_DE_REDEN_NIET_DE_DREMPEL": (
            "LEES DIT EERST, WANT 'nul bets' WORDT STANDAARD ALS 'te weinig voordeel' GELEZEN EN "
            "DAT IS HET VANDAAG NIET. Er is precies EEN analyseerbaar duel - Cruzeiro - Bahia, "
            "FULL - en daarin zijn ZEVENTIEN selecties over vier markten doorgerekend. ALLE "
            "ZEVENTIEN sneuvelen op POORT 5, de bevestiging door een tweede methode (§1, "
            "voorwaarde 5): de xG-methode en de splitsmethode verslaan de markt nooit dezelfde "
            "kant op. De oorzaak is te zien in de twee lambdaparen. De xG-methode komt op "
            "1,891 / 1,272 uit (3,16 doelpunten totaal) en de splitsmethode op 2,244 / 0,647 "
            "(2,89 totaal): de splitsmethode zet Cruzeiro veel sterker EN de wedstrijd lager. "
            "Daardoor staan de twee methodes op elke as tegenover elkaar. Op de Bahia-kant (1X2 "
            "2, AH Bahia +0,75/+1/+1,5, Double Chance) verslaat de xG-methode de markt met +2,91 "
            "tot +4,52 pp en de splitsmethode NIET, met -12,40 tot -20,09 pp. Op de "
            "Cruzeiro-kant (1X2 1, AH -0,5 t/m -1,5) is het precies omgekeerd: splits +14,19 tot "
            "+15,23 pp, xG -5,06 tot -7,79 pp. En op de doelpuntenmarkten splijt het net zo - "
            "Under 3,5 staat op splits +5,72 pp en xG -0,37 pp, Over 2,5 op xG -4,14 en splits "
            "-10,17. Er is dus geen enkele selectie waar beide methodes aan dezelfde kant van de "
            "markt staan. DAT IS DE POORT DIE GELD BESPAART: `shadow.py stats` meet "
            "`tweede_methode` vandaag op -2,5% over 251 afgewikkelde kandidaten. Het is ook de "
            "poort waarvan §5 waarschuwt dat hij structureel alles kan wegvangen; dat is hier "
            "EEN dag op EEN duel en dus geen reeks (§6d eist ~30)."
        ),
        "DE_RANGORDE_VAN_5B_IS_LEEG_EN_DAT_IS_DE_BODEM_VAN_3_0_PP": (
            "§5b trekt de drempel naar het eind en publiceert op RANGORDE, dus 'edge onder de lat' "
            "is sinds 20 sep 2026 geen reden meer voor nul bets. Vandaag is de rangorde tóch leeg, "
            "en dat komt door een ANDERE grens: de NEAR-ondergrens van 3,0 pp op FULL (6,0 op "
            "LIGHT), die `toplist._pool` en `ledger.py validate` samen bewaken. De beste selectie "
            "van de dag - Cruzeiro - Bahia, Under 3,5 @1,6272 (Matchbook, beurs: 1,64 bruto) - "
            "staat op +1,62 pp herijkt en +0,85 pp ruw, en zou dus zelfs zonder poort 5 onder die "
            "bodem zijn gebleven. De regel erachter staat in de docstring van `_pool`: wat te zwak "
            "is om als schaduwrij te loggen, is te zwak om te spelen. De lijst heeft vandaag drie "
            "plekken (MAX_SHORTLIST = 3 op do) en nul regels; MAX_LIGHT_IN_SHORTLIST (2) en de "
            "afkapping op LIJSTLENGTE binden dus geen van beide, en de reeks `lijstlengte` groeit "
            "vandaag niet."
        ),
        "POORT_7_STAAT_OP_DE_CRUZEIRO_KANT_OOK_DICHT": (
            "Een tweede poort die vandaag bindt, en op dezelfde wedstrijd. Cruzeiro mist 22,4% van "
            "de selectiewaarde tegen 0,3% bij Bahia - Matheus Pereira (schorsing), William "
            "(schorsing), João Marcelo (uit voor het seizoen), Felipe Morais, Luis Sinisterra "
            "(tot eind december) en Gabriel Pec (half november), zes namen samen 37,8 van 130,8 "
            "miljoen - en dat is ruim boven de 10 procentpunt waar poort 7 dichtgaat (§1c). Elke "
            "selectie op de THUISkant is daarmee langs twee dichte poorten gegaan en niet langs "
            "een. Op de Bahia-kant en op de doelpuntenmarkten staat poort 7 open (geen kant om te "
            "benadelen, respectievelijk geen materieel nadeel), dus daar is poort 5 de enige die "
            "tegenhoudt. Poort 8 en poort 9 hebben vandaag NIETS geblokkeerd: geen enkele selectie "
            "kwam zo ver, want poort 5 staat in de volgorde ervoor."
        ),
        "GEEN_NEAR_MISS_RIJEN_EN_DUS_GEEN_NET_NIET_TABEL": (
            "§5 eist een 'Net niet'-regel voor elke afgewezen kandidaat die een ECHTE edge liet "
            "zien, en vandaag is die tabel leeg - niet overgeslagen. De NEAR-drempel staat op 3,0 "
            "pp (FULL) en de hoogste edge van de dag is +1,62 pp, dus er is geen kandidaat die "
            "boven die ondergrens uitkomt. `data/shadow.jsonl` groeit vandaag dus met NUL rijen, "
            "en dat is het verschil tussen 'drie kandidaten die op een haar afvielen' en 'er was "
            "niets' dat §5 juist zichtbaar wil maken. Het is vandaag het tweede."
        ),
        "PALMEIRAS_REMO_KOMT_OP_NONE_UIT_EN_DAT_IS_VOORGESCHREVEN": (
            "Remo staat niet in de Série A-stand van 2025 en is dus promovendus uit de Série B. "
            "`prompts/run-b.md` zegt expliciet: bij Série A (BRA) ligt Série B eronder, maar er is "
            "GEEN gemeten factor voor dat divisiepaar, dus een Braziliaanse promovendus komt op "
            "NONE uit. De omrekening meldt dat ook zo: 'geen divisie boven of onder Série A (BRA) "
            "bekend'. Er is daarmee geen onafhankelijke kansinput op het niveau waarop gespeeld "
            "wordt, dus data_tier = NONE en GEEN BET (§2) - en er valt geen enkele markt door te "
            "rekenen, ook al lagen de prijzen klaar. Dezelfde regel als bij Kroatië en Hongarije. "
            "De competitie staat daarom NIET op GEEN WEDSTRIJD maar op GEANALYSEERD: het andere "
            "duel van Série A is wél doorgerekend. De context is wel opgehaald en gelogd (§1c), "
            "ook bij tier NONE: Remo mist daar 30,1% van de selectiewaarde tegen 15,8% bij "
            "Palmeiras."
        ),
        "PINNACLE_STAAT_VANDAAG_VRIJWEL_GELIJK_AAN_HET_MODEL": (
            "De scherpste bookmaker van de markt (§3 Stage 5, stap 2) is vandaag op ÉÉN duel "
            "toetsbaar en het verschil is klein. Op de totalen: de enige toetsbare lijn is "
            "Cruzeiro - Bahia Under 3,0, een HELE lijn met een push van 0,223 bij drie "
            "doelpunten; Pinnacle zet P(Under) op 48,8% en het eigen model op 49,9%, een verschil "
            "van +1,06 pp, bij een Pinnacle-marge van 3,4%. Op 1X2 staat het model gemiddeld 3,86 "
            "pp van het Pinnacle-oordeel af (marge 4,1%): Pinnacle 57,2 / 22,1 / 20,7 tegen eigen "
            "51,4 / 23,4 / 25,2 - het model geeft Cruzeiro 5,79 pp minder thuiszege en Bahia 4,47 "
            "pp meer. LEES DE +1,06 PP NIET ALS 'de scheefstand van §6g is weg'. Dit is de derde "
            "dag waarop LEVEL_SCALE = 1.032 bindt, het is ÉÉN (duel, lijn)-paar, en op 4 november "
            "stond hetzelfde getal nog op +4,47 pp over vier paren. Eén waarneming is geen meting, "
            "en §6g schrijft voor dit met `gridfit.py measure` te doen op de duels van ná "
            "3 november - niet met een vergelijking van twee ochtenden."
        ),
        "DE_CAP_BINDT_VANDAAG_NIET": (
            "2 duels in één van de zeventien competities op een DONDERDAGcap van 40 "
            "(ranking.max_deep_analyses), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. Zestien competities hebben niets op de kalender: dat is GEEN WEDSTRIJD "
            "en geen gat (§3 Stage 2), en het is bij een tweede bron nagetrokken (zie hieronder). "
            "De datarijkdom stond op 6,5 bij beide duels; omdat er niet is afgekapt zijn 'laagste "
            "die het haalde' en 'hoogste die afviel' per definitie leeg. Dat vandaag alleen Brazilië "
            "speelt is de normale vorm van een Europese bekeravond: de competities van Run B liggen "
            "stil omdat hun clubs in de toernooien van Run A spelen of omdat het midweeks is - de "
            "eerstvolgende ronde van veertien van de zestien staat op 7 november."
        ),
        "DE_TWEEDE_BRON_IS_HET_OVER_ALLE_ZEVENTIEN_COMPETITIES_EENS": (
            "§1 eist bevestiging door een tweede methode op de vraag WELKE wedstrijden er zijn, en "
            "vandaag is er geen enkele afwijking: BetExplorer geeft voor alle zeventien competities "
            "exact hetzelfde aantal duels in het inzetvenster als de Fotmob-daglijst, 2 tegen 2, "
            "met de eerstvolgende ronde van de zestien stille competities erbij (7 t/m 14 "
            "november). 'Niet in de daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven "
            "zonder tweede bron - dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte. "
            "Juist op een dag waarop zestien van de zeventien competities stil zijn, is dit de "
            "controle die telt: `idcheck.py` draaide daarnaast groen op alle 33 Fotmob-id's uit "
            "coverage.json, inclusief die van de competities die vandaag niet spelen - de "
            "controle die het Serie B-id in september vier dagen te laat vond."
        ),
        "MARKTBALANS_OP_DE_INKOOP_GEHAALD_MAAR_OP_EEN_COMPETITIE": (
            "§1a eist dat geen enkele run voor de hele runlijst maar één soort markt koopt, en de "
            "controle slaagt - maar het is vandaag één competitie en niet twaalf. Série A (BRA) "
            "heeft een sportkey bij The Odds API en kreeg de bulk-aanroep met h2h + spreads + "
            "totals: zowel uitkomstmarkten (1X2 met 3 selecties, Asian Handicap met 7 "
            "handicaplijnen, Double Chance met 1) als een doelpuntenmarkt (O/U met 6 lijnen). Dat "
            "is 1 van 1 inkoopbaar. DNB kon niet: er zit geen 0,0-lijn in de spreads-respons, en "
            "dat is een grens van de bron en geen gat in de administratie (§6b-5b: noteer hem met "
            "de reden erbij). BTTS is NIET gekocht omdat geen van de twee duels een "
            "kandidaat-edge liet zien, wat §1a stap 2 als voorwaarde stelt; dat scheelde 2 credits "
            "per duel. Totaal 3 credits van een plafond van 379, bij 19751 credits over en 26 "
            "dagen tot de maandwissel. Het gratis BetExplorer-marktgemiddelde (12 boeken) is "
            "daarnaast opgehaald voor poort 8 en §6e."
        ),
    }
