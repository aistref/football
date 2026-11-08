"""Run A, 8 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Vijf dingen die hier vastgelegd moeten worden en die een volgende run anders opnieuw moet
uitzoeken:

1. **Understat ligt er de zevende dag uit**, en vandaag raakt het 24 duels: alle vijf zijn
   competities hadden een volle zondagronde. Duurste dag van de reeks.
2. **De pick van 7 nov op Nacional – Academico Viseu is een dag opgeschoven**, en de klokterugval
   van `settling.py` bood hem aan als afwikkelbaar terwijl de wedstrijd nog niet gespeeld was.
3. **De cap kwam exact op nul marge uit**: 55 duels op een zondagcap van 55.
4. **De twee gepubliceerde Unders staan ver boven het Pinnacle-oordeel** (+18,45 en +15,13 pp),
   terwijl het model over alle 47 (duel, lijn)-paren gemiddeld 0,81 pp eronder zit.
5. **`prosecheck.py` las `rho` in "voorhoede" en "achterhoede"** en is gerepareerd op hele woorden.
"""
import json

H = "data/source-health.json"
h = json.load(open(H))
S = h["sources"]


def hist(key, detail, status=None, role=None):
    """Oude detailtekst bewaren in detail_history voordat hij wordt overschreven."""
    S.setdefault(key, {})
    oud = S[key].get("detail")
    if oud:
        S[key].setdefault("detail_history", []).insert(
            0, {"date": S[key].get("last_checked"), "detail": oud})
        S[key]["detail_history"] = S[key]["detail_history"][:8]
    S[key]["detail"] = detail
    S[key]["last_checked"] = "2026-11-08"
    if status:
        S[key]["status"] = status
    if role:
        S[key]["role"] = role


hist("understat",
     "8 nov (run A): ZEVENDE dag op rij onbruikbaar, en de DUURSTE van de reeks. Alle vijf de "
     "competities geven exact dezelfde fout: `UnderstatError: geen JSON terug van "
     "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)` — vijf verzoeken, vijf keer "
     "EXACT 26.719 bytes. Vijf dagen op rij hetzelfde antwoord in dezelfde grootte wijst op een "
     "blokkadepagina of een permanent gewijzigde route, niet op een storing die voorbijgaat. De "
     "reeks: 1 nov HTTP 502 op de CONNECT van de netwerkgateway, 3 nov `Connection reset by "
     "peer`, 4/5/6/7/8 nov 26.719 bytes zonder JSON. WAT HET VANDAAG KOST: alle vijf de "
     "Understat-competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) hadden een volle "
     "zondagronde — 5 + 5 + 5 + 3 + 6 = 24 van de 55 duels in het venster missen hun "
     "`p_xg_understat`-arm in het kalibratieblok van §6e. Gisteren waren dat 18 van 52, de dag "
     "ervoor 5 van 15. Vier van de vijf gepubliceerde bets staan in die vijf competities (Napoli "
     "– Lazio, Fiorentina – Juventus, Sunderland – Chelsea, Villarreal – Getafe). WAT HET NIET "
     "KOST: geen enkel duel wordt hierdoor `NONE`. Fotmob levert en is voor vrijwel elke "
     "competitie de xG-bron, dus §2 blijft gedekt. §3 (27 sep 2026) schrijft voor dat de kanskant "
     "pas vooraan in de notificatie hoort zodra FOTMOB wegvalt; dat is niet het geval — Fotmob "
     "leverde vandaag twee daglijsten en 55 wedstrijdcontexten zonder een enkele fout. Wat weg "
     "is, is de REDUNDANTIE waarvoor Understat op 31 augustus is toegevoegd: zeven dagen, en als "
     "Fotmob ook omvalt is er niets meer. NIET OMZEILD (§3, 'Niet doen').")

hist("the_odds_api",
     "8 nov (run A): OK. `api_check.py`: 47 actieve voetbalcompetities, quota 19.561 over en 439 "
     "verbruikt deze maand, 31 van de 34 sportkeys van de repo actief (Coppa Italia, Ligue 2 en "
     "Conference League niet — alle drie spelen vandaag ook niet, en Ligue 2 staat niet in de "
     "Run A-runlijst). De bulk-aanroep (h2h + spreads + totals, 3 credits per competitie) is voor "
     "ALLE TWAALF inkoopbare competities gelukt: 36 credits, plus 38 voor de BTTS-tweede ronde op "
     "38 duels = 74 van een plafond van 424; 19.444 over. MARKTBALANS OP DE INKOOP: 12 van de 12 "
     "competities kregen zowel een uitkomst- als een doelpuntenmarkt. Dat is hier geen "
     "formaliteit: alle ZES gekwalificeerde selecties staan op een doelpuntenmarkt (vier "
     "Over/Under, twee BTTS) en geen enkele op een uitkomstmarkt, en zonder dit cijfer is van "
     "buitenaf niet te zien of die eenzijdigheid uit de analyse of uit de portemonnee komt (§1a, "
     "29 aug 2026). Ze komt uit de analyse — 720 doorgerekende selecties over 49 duels, verdeeld "
     "over O/U 242, AH 197, 1X2 133, BTTS 76, DNB 40 en DC 32; uitkomstmarkten zijn 402 van de "
     "720 (56%). BESTE PRIJS: +6,55% ten opzichte van het BetExplorer-marktgemiddelde over 47 "
     "duels. EEN BEURSKOERS in de lijst: Villarreal – Getafe via Matchbook, 1,90 bruto en 1,882 "
     "na 2% commissie (`oddsapi.net_price`). EEN DERDE GEVAL IN `markets_checked`: Heart of "
     "Midlothian – Falkirk had wel een kandidaat-edge maar stond niet in de spreads-respons, dus "
     "er was geen event-id om de btts-markt op op te vragen. Dat staat nu zo genoteerd in plaats "
     "van als 'geen kandidaat-edge'; `ra_nov08_analyze.py` heeft er een eigen regel voor.",
     status="ok")

hist("fotmob",
     "8 nov (run A): OK en de enige kansbron van de dag. Twee daglijsten (8 en 9 november), 55 "
     "wedstrijdcontexten via `matchDetails` zonder een enkele fout, en de standen van vorig en "
     "lopend seizoen voor twaalf competities plus de FA Cup-basis. `idcheck.py`: alle 33 id's uit "
     "`coverage.json` leveren een bruikbare stand. Het bekerid 132 (FA Cup, onder `notes` en niet "
     "onder `fotmob_id`) gaf vier duels in het venster; BetExplorer gaf dezelfde vier met dezelfde "
     "aftraptijden. STADIONCONTROLE: `context.check_venue` zette bij geen van de 51 duels met "
     "context `relocated`. OPSTELLINGEN: alle 51 op `predicted` — de run draait om 02:05 NL en "
     "bevestigde opstellingen komen een uur voor de aftrap. LET OP, EEN WAARSCHUWING VOOR DE "
     "VOLGENDE RUN: de daglijst van Fotmob kan een wedstrijd tussen twee runs van datum laten "
     "veranderen. Nacional – Academico Viseu (match_id 5887676) stond op 7 november in de "
     "daglijst van 7 november met aftrap 2026-11-07T15:30Z en staat vandaag in die van 8 november "
     "met 2026-11-08T15:30Z, exact 24 uur later. Dat is geen leesfout van gisteren — het staat zo "
     "in `tmp-run/ra_nov07_stage3.json` en `ra_nov07_cands.json`.",
     status="ok")

hist("settling_klokterugval",
     "8 nov (run A): DE KLOKTERUGVAL VAN §0 IS ONVEILIG BIJ EEN UITGESTELDE WEDSTRIJD, en dat is "
     "vanochtend bijna een verzonnen uitslag in het logboek geworden. De pick van Run A van 7 nov "
     "op Nacional – Academico Viseu (Over 2.25 @1,85) droeg `kickoff = 2026-11-07T15:30:00.000Z`. "
     "Fotmob geeft dat match_id (5887676) vandaag in de daglijst van 8 november, 24 uur later, "
     "`finished = False`. `settling.DayIndex` kon op de OUDE datum geen status vinden — de "
     "wedstrijd stond daar niet meer — en viel dus terug op `SETTLE_FALLBACK_HOURS` = 2 uur na de "
     "aftrap. `ledger.py open` bood de pick daarom aan als '10.6u — klaar om af te wikkelen' "
     "terwijl er geen uitslag bestond. WAT ER IS GEDAAN: `kickoff` bijgewerkt naar de werkelijke "
     "aftrap met de hele toedracht in `notes`, `run_date` ongewijzigd op 2026-11-07. Daarna meldt "
     "`ledger.py open` hem als 'bron meldt nog niet afgelopen (-13.4u na aftrap)' en wikkelt de "
     "run van morgen hem af op de bron. GEEN CODEWIJZIGING op een geval van één: een uitgestelde "
     "wedstrijd is geen fout in `settling.py` maar de werkelijkheid, en de krappe terugval is met "
     "opzet krap (§0). WAT EEN VOLGENDE RUN MOET DOEN: ziet hij een pick die op de klokterugval "
     "afwikkelbaar wordt (reden 'geen bronstatus'), dan eerst controleren of het duel vandaag of "
     "morgen in de daglijst staat voordat hij de klok volgt.",
     status="bekende_valkuil",
     role="afwikkeling Stage 0 (§0) — waarschuwing, geen storing")

hist("pinnacle_vergelijking",
     "8 nov (run A): DIT IS HET GROOTSTE VOORBEHOUD VAN DE RUN. Stap 2 van Stage 5 is ingevuld "
     "met de de-vigde Pinnacle-prijs naast de eigen kans (§3 Stage 5, 20 sep 2026). Over 46 duels "
     "met zowel een Pinnacle-1X2 als een eigen 1X2: gemiddelde absolute afstand 4,88 pp bij een "
     "gemiddelde Pinnacle-marge van 3,34%. Op de doelpuntenkant 47 (duel, lijn)-paren, gemiddeld "
     "verschil op de Under-kant -0,81 pp, en in 19 van de 47 staat het model erboven. DE TWEE "
     "GEPUBLICEERDE UNDERS ZIJN DE TWEE GROOTSTE UITSCHIETERS VAN DIE 47: Napoli – Lazio lijn 3,0 "
     "(Pinnacle 1,94/1,94, de-vigd en push-gecorrigeerd P(Under) = 0,500; eigen 0,6845, verschil "
     "+18,45 pp) en Fiorentina – Juventus lijn 2,5 (Pinnacle 1,88/2,00 -> 0,4845; eigen 0,6359, "
     "verschil +15,13 pp). HOE DAT GELEZEN HOORT TE WORDEN: §1g heeft op 552 afgerekende gevallen "
     "gemeten dat de bookmaker scherper schat (vandaag Brier markt 0,2412 tegen eigen 0,2605 over "
     "477 bets) en dat het rendement het SLECHTST is bij de hoogste geclaimde edge. Achttien "
     "procentpunt afstand tot het scherpste publieke oordeel is eerder een eigen fout dan een "
     "gevonden voordeel. Het grootste 1X2-verschil zit bij Union St.Gilloise – Genk (-14,27 pp op "
     "de thuiskant), de regel die op rang 6 buiten de lijst valt. HARDE GRENS §2: niets hiervan "
     "gaat in `my_prob` of `prob_sources`.",
     status="gemeten",
     role="stap 2 van Stage 5 (§3) — vergelijking, geen kansbron")

hist("max_deep_analyses",
     "8 nov (run A): BOND NIET, EN HAD NUL MARGE. 55 duels in het inzetvenster op een zondagcap "
     "van 55 (`ranking.max_deep_analyses`): nul afgekapt, nul over. Dat is de krapste stand van "
     "deze reeks — 7 nov had drie duels marge op 52 van 55. Dit staat hier omdat het spiegelbeeld "
     "van een stille truncatie een grens is die net niet bond en daarom nergens wordt genoemd "
     "(§3 Stage 4): één verschoven aftrap of één extra bekerduel en de dekkingstabel had een "
     "`AFGEKAPT`-regel gehad. Bereik van de datarijkdom in de run: 3,5 (de vier FA Cup-duels) tot "
     "8,0 (Brighton – Brentford, Vitoria de Guimaraes – FC Porto). Laagste die het haalde: "
     "Wimborne Town – Crawley Town (3,5 · 1 markt); hoogste die afviel: geen. GEEN AANLEIDING OM "
     "DE CAP TE VERHOGEN: het is een TIJDSgrens en geen creditgrens (§0). De looptijd van vandaag "
     "staat in `data/run-state/` onder `duur`.",
     status="nul_marge",
     role="afkapping Stage 4 (§3) — tijdsgrens, geen creditgrens")

hist("poort_5_bevestiging",
     "8 nov (run A): VIERDE DAG OP RIJ DE POORT DIE DE DAG BEPAALT, op de grootste steekproef tot "
     "nu toe. 554 van de 720 doorgerekende selecties sneuvelen op poort 5 (76,9%). De reeks: 5 nov "
     "alle 17 selecties van het enige analyseerbare duel, 6 nov 149 van 186 (80,1%), 7 nov 395 van "
     "510 (77,5%), vandaag 554 van 720 (76,9%). Daarna: `edge` 53 (7,4%), `underdog` 38 (5,3%), "
     "`context` 35 (4,9%), `odds` 22 (3,1%), `robuustheid` 6 (0,8%), `doelpunten_onder` 2 (0,3%); "
     "10 selecties (1,4%) halen alle poorten, verdeeld over zes wedstrijden. "
     "DE SCHADUWREEKS ZEGT DAT DE POORT ROND NUL STAAT en dat is de maat die §6d voorschrijft, "
     "niet het aandeel van vandaag: `tweede_methode` staat op 281 kandidaten, 271 afgewikkeld, "
     "trefkans 46,5%, rendement +0,1% (+0,34u). Hij bespaart dus geen geld en kost het ook niet. "
     "§1f: als KANSBRON voegt de splitsmethode vrijwel niets toe (Brier .23674 tegen .23625), als "
     "VETO is ze vandaag ruim driekwart van de run. NEGEN VAN DE VIJFTIEN `near_miss`-rijen met de "
     "hoogste xG-edge sneuvelen hierop, en in zeven daarvan staat de tweede methode NEGATIEF — de "
     "twee kansbronnen zijn het oneens over de RICHTING en niet over de grootte. "
     "ER IS VANDAAG NIETS VERZET. Vier dagen is geen reeks (§6d, §1g).",
     status="vierde_dag")

hist("poort_9_doelpunten_onder",
     "8 nov (run A): DE POORT HIELD VOOR HET EERST TWEE SELECTIES TEGEN — Inter – Como (Under 3.5 "
     "@1,69, +8,13 pp) en Besiktas – Genclerbirligi (Under 3.5 @2,0192, +8,51 pp), beide in de "
     "band 8-10 pp op `FULL` waar `unders.UNDER_EXTRA` = 2,0 pp voor is gebouwd. De reeks "
     "`doelpunten_onder` staat op 36 kandidaten, alle 36 afgewikkeld, trefkans 36,1%, rendement "
     "-32,3% (-11,63u): boven de ~30 van §6d en duidelijk negatief, dus de rem houdt verliezers "
     "tegen. De twee van vandaag maken het er 38 zodra ze zijn afgewikkeld. "
     "DE ONDERLIGGENDE SCHEEFSTAND IS OPNIEUW GEGROEID: `margins.py goalbias` meet over 130 "
     "gespeelde Unders +0,612 doelpunt per duel boven de eigen lambda (z = +4,20), tegen 127 / "
     "+0,626 / z = +4,25 gisteren — zelfde orde, en het is nu de langste reeks die deze meting "
     "heeft gehad. Modelkant staat recht: 2150 duels, +0,032 doelpunt, z = +0,86. Over-kant rustig: "
     "71 gevallen, -0,359, z = -1,65. In het logboek: `Over/Under — Under` 164 picks / -12,5%, "
     "`Over/Under — Over` 94 picks / +5,0%. "
     "TWEE VAN DE VIJF BETS VAN VANDAAG STAAN OP DEZE KANT en beide halen de verzwaarde lat ruim "
     "(Napoli – Lazio +20,26 pp, Fiorentina – Juventus +15,79 pp). Juist daarom staat het "
     "Pinnacle-voorbehoud bij beide vooraan in de `why`-tekst (§4 punt 2): +18,45 en +15,13 pp "
     "boven het scherpste publieke oordeel. "
     "ER IS NIETS VERZET: `gridfit.py measure` zegt dat 174 van de 1347 homogene duels lambdas van "
     "ná 3 nov dragen (gisteren 84), dus `LEVEL_SCALE` = 1.032 is nog niet te beoordelen (§6g, "
     "§1h).",
     status="meting_loopt")

hist("btts_reeks",
     "8 nov (run A): DE DREMPEL DIE §1h PUNT 2 VOOR ZICHZELF STELDE IS GEHAALD EN DE VRAAG IS "
     "EENMALIG VOORGELEGD. Die paragraaf houdt BTTS buiten poort 9 met als reden dat 15 "
     "afgewikkelde BTTS-picks in beide richtingen samen geen meting is, en schrijft erbij: 'dit is "
     "het eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30 haalt'. Vandaag staat hij "
     "op 31. UITGESPLITST, want poort 9 gaat over een KANT en niet over een markt: `BTTS — nee` 20 "
     "gevallen, 45,0% trefkans, -6,2% (-1,24u); `BTTS — ja` 11 gevallen, 63,6%, +37,9% (+4,17u); "
     "gepoold 31 gevallen, +9,5% (+2,93u). DE CIJFERS WIJZEN NIET EENDUIDIG: de gepoolde reeks "
     "haalt de 31 en staat POSITIEF, en de kant waar het vermoeden over gaat staat op 20 gevallen "
     "— onder de ~30 die §6d voor een losse reeks eist. Vergelijk met de Under-kant: -12,5% over "
     "164 gevallen PLUS een onafhankelijk gemeten doelpuntenafwijking van +0,612 per duel bij "
     "z = +4,20. Voor BTTS-nee bestaat die tweede meting niet, want `margins.py goalbias` splitst "
     "op Over/Under en niet op BTTS. DAAROM ALS VRAAG EN NIET ALS WIJZIGING: §1h en §1e verbieden "
     "een run een poort op eigen initiatief te verzetten. De vraag staat EEN keer in het "
     "dagrapport met `owner = \"besluit\"` en wordt daarna niet herhaald. Twee van de zes "
     "gekwalificeerde selecties van vandaag staan op deze markt, dus de vraag is niet theoretisch.",
     status="drempel_gehaald_vraag_gesteld",
     role="meting onder §1h punt 2 — besluit bij de gebruiker")

hist("prosecheck",
     "8 nov (run A): EERSTE BINDENDE DAG VAN §6c 'Geen tussenkopjes en minder AI-tells', en "
     "meteen een FOUT IN DE CONTROLE ZELF GEVONDEN EN GEREPAREERD. `prosecheck.py` telde zijn "
     "verboden rekenwoorden met `str.count()` op de kale letterreeks, en vond daardoor `rho` in "
     "VOORHOEDE en ACHTERHOEDE: twee volstrekt normale voetbalwoorden werden als rekenjargon "
     "gemeld, waardoor twee van de vijf voorbeschouwingen 'boven de norm' stonden. Gerepareerd "
     "door op hele woorden te zoeken (`\\b` + `re.escape`); dezelfde val lag klaar voor `edge` in "
     "een Engelse clubnaam en voor `lat van`. Zelftest ongewijzigd groen: 22 van 22. WAAROM DAT "
     "meer is dan cosmetica: het script is met opzet een hulpmiddel en geen poort (§6c), en een "
     "controle die bij gewoon taalgebruik alarm slaat leert je hem te negeren — waarna hij het "
     "echte geval ook niet meer vangt. "
     "DE UITKOMST VAN VANDAAG: 5 teksten, 2105 woorden, nul kopjes, nul label-openers, nul "
     "verboden formuleringen, nul herhaalde alinea-openers, em-dash gemiddeld 0,0 per tekst tegen "
     "de nulmeting van 5,2 op 7 november. Lengtes 383 tot 475 woorden (norm 300-600). Twee eerste "
     "versies openden een alinea met hun rubriek en drie sloten de cursieve slotregel met "
     "hetzelfde invulveld ('Deze staat...'); allebei herschreven vóór het renderen. DE TELLER "
     "BLIJFT EEN ONDERGRENS (§6c): hij kan geen sjabloon zien dat met andere woorden is "
     "geschreven.",
     status="gerepareerd",
     role="stijlcontrole §6b-5j — hulpmiddel, geen poort")

h["updated"] = "2026-11-08"
h["last_run"] = {
    "run": "A",
    "date": "2026-11-08",
    "note": (
        "DE CAP KWAM EXACT OP NUL MARGE UIT: 55 duels in het inzetvenster uit twaalf competities "
        "van de runlijst plus vier FA Cup-duels, op een zondagcap van 55. Nul afgekapt, nul over — "
        "de krapste stand van deze reeks. ZES SELECTIES HAALDEN ALLE NEGEN POORTEN EN ER PASSEN "
        "VIJF REGELS IN DE LIJST; de zesde (Union St.Gilloise – Genk, BTTS nee @2,274, +8,85 pp) "
        "valt op `lijstlengte` (§5b). ALLE ZES STAAN OP EEN DOELPUNTENMARKT — vier Over/Under en "
        "twee BTTS — en geen enkele op een uitkomstmarkt. Dat is de ANALYSE en niet de inkoop: "
        "alle twaalf inkoopbare competities kregen de volle bulk, 12 van 12 met zowel een "
        "uitkomst- als een doelpuntenmarkt, BTTS voor 38 van de 39 duels met een kandidaat-edge, "
        "en 720 doorgerekende selecties waarvan 402 (56%) op een uitkomstmarkt. "
        "HET GROOTSTE VOORBEHOUD STAAT BIJ DE TWEE UNDERS: Napoli – Lazio (Under 3 @1,94) en "
        "Fiorentina – Juventus (Under 2.5 @2,10) staan +18,45 en +15,13 pp boven het de-vigde "
        "Pinnacle-oordeel op dezelfde lijn, de twee grootste uitschieters van de 47 "
        "(duel, lijn)-paren van vandaag, terwijl het model gemiddeld 0,81 pp ONDER Pinnacle zit. "
        "`margins.py goalbias` meet op die kant +0,612 doelpunt per duel over 130 gespeelde Unders "
        "bij z = +4,20, terwijl de modelkant recht staat (z = +0,86) — het is dus het "
        "selectie-effect van §6g. Poort 9 hield voor het eerst TWEE selecties tegen (Inter – Como, "
        "Besiktas – Genclerbirligi), beide in de band 8-10 pp. Poort 5 hield voor de vierde dag op "
        "rij ruim driekwart tegen (554 van 720, 76,9%). "
        "STAGE 0 VOND EEN STILLE FAALSTAND: de pick van 7 nov op Nacional – Academico Viseu werd "
        "door `ledger.py open` als afwikkelbaar aangeboden op de klokterugval van 2 uur, terwijl "
        "Fotmob datzelfde match_id vandaag 24 uur later in de daglijst zet en de wedstrijd nog "
        "niet gespeeld is. `kickoff` gecorrigeerd, pick blijft pending, geen tweede pick op "
        "hetzelfde duel. Afwikkeling van 7 nov: 9 picks, 5 gewonnen en 4 verloren, plus 64 "
        "schaduwrijen (29/32/3). DE BTTS-REEKS HAALT DE 31 die §1h punt 2 voor zichzelf stelde en "
        "de vraag is eenmalig aan de gebruiker voorgelegd. Understat zevende dag uit, raakt 24 van "
        "de 55 duels, kost geen enkel duel. Gerepareerd: `prosecheck.py` las `rho` in 'voorhoede' "
        "en 'achterhoede'."
    ),
    "matches_in_window": 55,
    "analysed": 49,
    "truncated": 0,
    "truncated_cost_real_analyses": 0,
    "bets": 5,
    "qualified_not_published": 1,
    "credits": "74 van een plafond van 424 (36 bulk voor 12 competities + 38 BTTS voor 38 duels); 19.444 over",
    "samenvatting": "5 bets uit 6 gekwalificeerde selecties, alle zes op een doelpuntenmarkt; cap op nul marge; twee Unders ver boven Pinnacle",
}
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt:", len(S), "bronnen")
