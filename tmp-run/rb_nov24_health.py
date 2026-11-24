"""Run B, 24 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **Een dinsdag met 14 duels in VIJF van de zeventien competities**; de cap van 40 bindt niet.
2. **Vier van de 133 selecties halen alle poorten én hun eigen lat, en alle vier staan in
   DEZELFDE wedstrijd.** Regel 1 haalt zijn lat wél (+11,65 pp tegen 10,0), anders dan op 22 en
   23 november; regel 2 komt volledig op rangorde (§5b).
3. **Poort 9 heeft de gepubliceerde Under WEL getoetst** — de twee gaten van 12 okt (LIGHT) en
   22 nov (onder de band) spelen vandaag niet.
4. **Pinnacle is het met regel 1 het meest oneens van alle negen toetsbare (duel, lijn)-paren**
   (+12,66 pp), en met regel 2 het meest op de 1X2 van alle negen duels (+15,21 pp).
5. **De Under-kant van de SELECTIE staat op z = +4,95** over 148 gespeelde Unders; het MODEL op
   z = +0,68 over 2453 duels.
6. **ALLE VIJF de spelende competities hebben xG én een sportkey** — ongewoon voor deze runlijst —
   en maar 3 van de 14 duels vallen uit het contextlogboek, tegen 62% op 23 nov. Dat gat is
   COMPETITIE-afhankelijk en niet dagafhankelijk.
"""

import json, datetime

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:34} {status:38} {detail[:70]}")


note("fotmob", "ok",
     "24 nov (run B): daglijsten 24 en 25 nov opgehaald (153 en 145 wedstrijden); idcheck.py gaf "
     "voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, AFSLUITCODE 0 - Serie B "
     "staat op het echte id 86 met 20 ploegen. Standen van alle VIJF spelende competities "
     "geleverd, beide seizoenen, en ALLE VIJF HEBBEN xG - dat is ongewoon voor deze runlijst en "
     "het is de as waarop ze normaal het zwakst staat. De vijf competities ZONDER xG (Czech "
     "First League 122, Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga 189, Keuken "
     "Kampioen Divisie 111) spelen vandaag ALLE VIJF niet, dus er is geen enkel duel dat op "
     "doelpunten-als-sterktemaat moet draaien. Context voor alle 14 duels in een keer opgehaald, "
     "NUL fouten; datarijkdom tussen 4,5 en 6,5. context.check_venue sloeg bij GEEN van de 14 "
     "duels aan en poort 7 hield nul selecties tegen. lineupType stond op geen enkel duel op "
     "'confirmed' - 13 op lastStarting11 en 1 op unavailable; de run draait om 04:00 NL en dan is "
     "er nergens een opstelling bevestigd. MLS speelt de play-offs: Fotmob zet die onder 'Major "
     "League Soccer Playoff' (id 957981) met parentLeagueId 130, dus runwindow.py vindt ze op het "
     "id uit coverage.json en het is dezelfde competitie.")

note("the_odds_api", "ok",
     "24 nov (run B): api_check.py meldt 45 actieve voetbalcompetities en 19005 credits over, 995 "
     "verbruikt deze maand. 33 van de 34 sportkeys van de repo actief; NIET ACTIEF is alleen "
     "Ligue 2 (soccer_france_ligue_two). VIER actieve sportkeys die de repo niet kent: "
     "soccer_brazil_serie_b, soccer_england_efl_trophy, soccer_germany_liga3 en "
     "soccer_uefa_nations_league. suggest_cap(19005, 7) gaf plafond 1356; ALLE VIJF de spelende "
     "competities zijn inkoopbaar en kregen de bulkroute (h2h+spreads+totals, 3 credits elk = "
     "15), en zes duels met kandidaat-edge kregen in ronde twee BTTS (1 elk = 6). TOTAAL 21 van "
     "1356, 18984 over en 1016 verbruikt deze maand. MARKTBALANS GEHAALD: 5 van de 5 inkoopbare "
     "competities kregen zowel een uitkomstmarkt als een doelpuntenmarkt, en over de hele run 56 "
     "selecties op een doelpuntenmarkt (44 O/U + 12 BTTS) tegen 77 op een uitkomstmarkt (34 AH + "
     "26 1X2 + 13 DNB + 4 DC). ANDERS DAN DE MEESTE RUN B-DAGEN is er vandaag GEEN competitie "
     "die op het gratis BetExplorer-marktgemiddelde moet draaien.")

note("betexplorer", "ok",
     "24 nov (run B): fixturepagina's van alle 17 competities van de runlijst opgehaald, nul "
     "fouten en geen enkele lege lijst (de stille faalmodus van een verkeerde slug deed zich niet "
     "voor). De bevestigingscontrole van §1 (Fotmob-daglijst naast de BetExplorer-fixturepagina, "
     "per competitie) staat op 17 VAN DE 17 EENS, 14 duels tegen 14, inclusief de TWAALF "
     "competities die vandaag GEEN WEDSTRIJD hebben (0 tegen 0, met voor elk de eerstvolgende "
     "ronde erbij). Dat is de controle die juist op de stille competities moet draaien, want een "
     "fout id geeft geen foutmelding maar nul wedstrijden (prompts/run-b.md).")

note("teamnames", "ok",
     "24 nov (run B): geen nieuwe naamkoppeling nodig. Juve Stabia - Catanzaro koppelde bij de "
     "Pinnacle-totalen pas op de TWEEDE poging (genormaliseerde naam) en dat is de bestaande "
     "terugval die werkt, geen defect. BetExplorer schrijft vier namen anders dan Fotmob (Entella "
     "/ Virtus Entella, Verona / Hellas Verona, Sudtirol / Sudtirol, L.R. Vicenza / Vicenza, "
     "Sheffield Wed / Sheffield Wednesday) en de bestaande koppeling ving ze alle vier.")

note("understat", "niet_bevraagd",
     "24 nov (run B): niet opgevraagd. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue "
     "1 - geen enkele competitie van de Run B-runlijst. Dat is geen storing maar de afbakening "
     "van §4.")

note("api_football", "niet_gezet",
     "24 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker (27 sep "
     "2026) en geen storing, geen gat en geen actiepunt (§3). De onafhankelijke kansinput komt "
     "van Fotmob, dat vandaag alles leverde voor alle vijf de spelende competities; de "
     "uitzondering van §3 punt 3 - melden zodra Fotmob niet meer levert - is niet aan de orde.")

note("settling", "een_rij_blijft_terecht_open",
     "24 nov (run B): ledger.py open en shadow.py open gaven NUL afwikkelbare regels. "
     "shadow-2026-11-23-b-st--louis-city---los-angeles-fc staat 3,1 uur na de aftrap nog op "
     "pending, en dat is hier ook FEITELIJK juist: Fotmob vindt het duel (MLS Playoff) met "
     "finished=false en ongoing, en de tweede helft was om 03:27:57 NL begonnen terwijl deze run "
     "om ~04:05 NL begon - het duel LIEP werkelijk nog. §0 zegt dan letterlijk wachten; de "
     "terugval op de klok (SETTLE_FALLBACK_HOURS = 2,0) geldt UITSLUITEND wanneer er geen "
     "bronstatus te krijgen was, en die is er hier wel. De volgende run wikkelt hem af. De twee "
     "openstaande picks in picks.jsonl (Bodo/Glimt - LASK, RB Leipzig - Lens) zijn van Run A van "
     "VANDAAG en moeten nog beginnen.")

note("poort_9_doelpunten_onder", "reeks_53_rem_werkt_en_toetste_vandaag_de_bet",
     "24 nov (run B): poort 9 hield vandaag NUL selecties tegen, maar hij HEEFT de gepubliceerde "
     "regel wel getoetst en dat is het verschil met 22 en 23 november. Bradford City - Barnsley "
     "Under 3 is een Over/Under op de Under-kant met data_tier = FULL en valt daarmee precies in "
     "het bereik waar de rem bindt (§1h): unders.check geeft lat 10,0 terug met de melding 'Under "
     "met +11,65 pp, boven de verzwaarde lat van 10,0 pp (poort 9)'. De rem heeft dus gemeten en "
     "DOORGELATEN in plaats van buiten het bereik te vallen - op 22 nov viel de regel ONDER de "
     "band (8-10 pp) en op 23 nov vielen beide regels erbuiten (een onder de band, een op "
     "LIGHT). De reeks blijft op 53 kandidaten, 52 afgewikkeld, 34,6% trefkans, -18,65u = -35,9% "
     "rendement: de rem bespaart geld en heeft de ~30 van §6d ruim gehaald. EEN RUN VERZET POORT "
     "9 NIET OP EIGEN INITIATIEF.")

note("pinnacle_vergelijking", "let_op",
     "24 nov (run B): Stage 5 stap 2, en BEIDE gepubliceerde regels staan op het duel waar "
     "Pinnacle het meest van het eigen model afwijkt. Op de doelpuntenkant negen toetsbare (duel, "
     "lijn)-paren, en DE GROOTSTE AFWIJKING VAN ALLE NEGEN IS PRECIES REGEL 1: Bradford City - "
     "Barnsley op lijn 2,75, eigen P(Under) 59,7% tegen 47,0% bij Pinnacle (+12,66 pp, "
     "Pinnacle-marge 3,7%). Over alle negen gemiddeld +1,42 pp op de Under-kant met 5 van 9 "
     "erboven; uitgesplitst +4,82 pp op de ene zuivere halve lijn en +0,99 pp op de acht met "
     "push. Op de 1X2 negen toetsbare duels, gemiddelde absolute afstand 3,64 pp bij een "
     "gemiddelde Pinnacle-marge van 4,45%, en DE GROOTSTE AFWIJKING IS REGEL 2: San Jose "
     "Earthquakes - Houston Dynamo FC, waar het eigen model de thuisploeg 59,4% geeft tegen 44,2% "
     "bij Pinnacle (+15,21 pp) - bijna het dubbele van de tweede grootste. DEZE GETALLEN GAAN "
     "NIET IN my_prob (§2); ze horen in de vergelijking.")

note("goalbias_selectie", "onveranderd_scherp",
     "24 nov (run B): margins.py goalbias staat op 2453 doorgerekende duels. Het MODEL staat op "
     "+0,024 doelpunt per duel (z = +0,68): de lambdas kloppen. De SELECTIE niet - over de 148 "
     "duels waar werkelijk een Under is gespeeld vielen er 0,676 doelpunt per duel MEER dan "
     "verwacht (z = +4,95; 23 nov: +4,95 over 148, 22 nov: +4,89 over 144). De spiegel staat er "
     "ook: over de 83 gespeelde Overs vielen er 0,374 doelpunt per duel MINDER dan verwacht "
     "(z = -1,85). Regel 1 van vandaag staat op de Under-kant, dus op precies de kant waar de "
     "selectie tot nu toe de verkeerde kant op uitvalt - nu wel door poort 9 getoetst, wat de "
     "waarschuwing verzacht en niet wegneemt. Regel 2 staat op de OVER-kant, de kant waar de "
     "selectie juist te laag uitvalt. De VORM geeft op de 3,0-lijn nauwelijks steun aan een "
     "Under-overschatting: P(Under 3.0) voorspeld 63,8% tegen werkelijk 63,0% (0,9 pp te hoog), "
     "tegen 1,4 pp op de 2,5-lijn. Deze twee regels mogen NOOIT bij elkaar worden opgeteld en "
     "geen van beide is een reden om op een enkele dag een lat te verzetten (§6d).")

note("contextlogboek_dekking", "vandaag_veel_beter_en_dat_is_competitie_afhankelijk",
     "24 nov (run B): 11 van de 14 duels komen in ctxlog, 3 vallen weg omdat squad_value aan "
     "minstens een kant 0 is. Dat is 21% weg, tegen 62% op 23 nov en 68% op 22 nov - DUS HET GAT "
     "IS COMPETITIE-AFHANKELIJK EN NIET DAGAFHANKELIJK, en dat scherpt de bevinding van die twee "
     "dagen aan in plaats van haar tegen te spreken. Vandaag speelt de Italiaanse en Engelse kant "
     "van de runlijst, waar Fotmob wel marktwaarden noteert; de wegvallers zijn Crawley Town - "
     "Barnet (Barnet 0), San Jose Earthquakes - Houston Dynamo FC (BEIDE 0) en Chapecoense - "
     "Palmeiras (Chapecoense 0). LET OP HET GEVOLG VOOR REGEL 2: San Jose - Houston staat "
     "daardoor NIET in het contextlogboek, en poort 7 kon er dus ook niets over zeggen - hij gaat "
     "daar open op 'ontbrekende data laat de poort open' (§1c) en niet op een meting. Regel 1 "
     "(Bradford City - Barnsley) staat er wel in, met twee uitvallers aan de thuiskant (Stephen "
     "Humphrys, Josh Neufville) tegen nul bij Barnsley. Geen bronfout; Fotmob noteert voor MLS en "
     "de kleinere competities geen marktwaarden.")

note("divisiekaart_promovendi", "twee_structurele_gaten_kostten_vier_duels",
     "24 nov (run B): NEGEN van de 14 duels hebben een ploeg zonder stand in het vorige seizoen "
     "en gingen langs de omrekening van §4; VIJF kwamen op data_tier = NONE uit. TWEE STRUCTURELE "
     "GATEN, geen incidenten. (1) ONDER 'Serie B (ITA)' KENT promotion.TIER2 GEEN DIVISIE: de "
     "Serie C ligt eronder maar is niet gemeten, dus Benevento, Ascoli en Vicenza - alle drie "
     "promovendi uit de Serie C - zijn niet om te rekenen. Dat kostte DRIE van de zes Italiaanse "
     "duels. LET OP DE FOUTMELDING, die de oorzaak verkeerd laat lezen: hij zegt \"degradant: "
     "'Benevento' staat niet in de stand van Serie A (ITA) 2025/2026\" en noemt dus alleen de "
     "TIER1-tak, terwijl Benevento juist van ONDEREN komt. Exact dezelfde misleidende melding als "
     "bij de Spaanse Primera Federacion (notitie van 4 okt 2026). (2) 'Serie A (BRA)' STAAT IN "
     "GEEN VAN BEIDE KAARTEN - prompts/run-b.md zegt dat expliciet - dus Chapecoense komt op "
     "NONE. Het vijfde geval is anders en het is de poort die WERKT: Blackpool - Leicester City "
     "viel op conversion_in_range, dus Leicester City IS om te rekenen (degradant uit de "
     "Championship, TIER1-route) maar zijn omgerekende sterkte valt buiten het gemeten bereik. §4 "
     "verbiedt extrapoleren; de uitweg is de meting vergroten, niet de rand oprekken. Vier "
     "omrekeningen lukten wel en leverden drie LIGHT-duels plus Port Vale - Northampton Town.")

# --- het gedateerde snapshotblok van deze run (zie _merge_note: branchaudit vergelijkt hierop) ---
prev_b = H.get("last_run_run_b")
if prev_b and prev_b.get("date") != "2026-11-24":
    hist = prev_b.pop("history", [])
    H["last_run_run_b"] = {"history": ([prev_b] + list(hist))[:8]}
else:
    H["last_run_run_b"] = {"history": (H.get("last_run_run_b") or {}).get("history", [])}

H["last_run_run_b"].update({
    "run": "B", "date": "2026-11-24",
    "matches_in_window": 14, "analysed": 9, "truncated": 0, "bets": 2,
    "qualified_not_published": 0,
    "credits": "21 van een plafond van 1356 (15 bulk voor 5 competities + 6 BTTS); 18984 over, "
               "1016 gebruikt deze maand na deze run",
    "note": "VIJF van de zeventien competities spelen, met 14 duels in het inzetvenster: Serie B "
            "(6), English League One (4), English League Two (2), MLS (1) en Serie A (BRA) (1). De "
            "dinsdagcap van 40 bindt NIET, er is niets afgekapt. ALLE VIJF de spelende "
            "competities hebben xG bij Fotmob EN een sportkey bij The Odds API - ongewoon voor "
            "deze runlijst. Negen duels leverden kandidaten op; vijf kwamen op data_tier = NONE "
            "door twee structurele gaten in de divisiekaart (geen gemeten divisie onder Serie B, "
            "Serie A (BRA) in geen van beide kaarten) en een terechte conversion_in_range-"
            "weigering. 133 selecties doorgerekend over alle zes de markten; 106 (80%) sneuvelden "
            "op poort 5, 11 op de edge-afkapping, 9 op poort 8 en 3 op de koersband. Poort 6, 7 "
            "en 9 hielden NUL tegen. VIER selecties haalden alle poorten EN hun eigen lat en alle "
            "vier staan in DEZELFDE wedstrijd (Bradford City - Barnsley: drie Under-lijnen plus "
            "BTTS-nee) - een mening, vier keer uitgedrukt, waarvan de 0-of-1-regel er een "
            "publiceert. De controle langs drie wegen op de twaalf stille competities: idcheck.py "
            "33/33 met afsluitcode 0, BetExplorer 17 van 17 eens (14 tegen 14 duels), "
            "runwindow.py voor het venster.",
    "bevinding": "Regel 1 (Bradford City - Barnsley Under 3 @1,82, FULL, +11,65 pp) HAALT ZIJN "
                 "EIGEN LAT, en dat is de eerste keer sinds 22 november op deze runlijst: de lat "
                 "is door poort 9 verzwaard naar 10,0 en hij komt er op BEIDE schalen boven "
                 "(ruw +10,56). Poort 9 heeft hem dus gemeten en doorgelaten in plaats van buiten "
                 "zijn bereik te vallen. Regel 2 (San Jose Earthquakes - Houston Dynamo FC Over "
                 "2.5 @1,7252, FULL, +6,19 pp bij een lat van 8,0) komt volledig op rangorde "
                 "(§5b). DE TEGENHANGER STAAT ER OOK, en het is dezelfde als gisteren: de "
                 "Under-kant van de SELECTIE staat op z = +4,95 over 148 gespeelde Unders "
                 "terwijl het model zelf op z = +0,68 over 2453 duels staat, en Pinnacle is het "
                 "met regel 1 het meest oneens van alle negen toetsbare doelpuntenparen "
                 "(+12,66 pp). Regel 2 staat met +15,21 pp op de grootste 1X2-afwijking van de "
                 "dag en is op elke as de krapste van de twee: de xG-methode verslaat de markt "
                 "daar met slechts +1,05 pp en edge_robust_min staat op exact datzelfde getal.",
    "sources_deze_run": {
        "fotmob": "ok - daglijsten 24 en 25 nov, standen van 5 competities in beide seizoenen, "
                  "context voor 14 van 14 duels zonder fout, idcheck 33/33 afsluitcode 0",
        "the_odds_api": "ok - 45 actieve competities, 19005 over bij de start, 21 credits "
                        "verbruikt (15 bulk + 6 BTTS), 18984 over",
        "betexplorer": "ok - 17 van 17 fixturepagina's, geen lege lijst, 14 tegen 14 duels eens",
        "understat": "niet bevraagd - dekt geen enkele competitie van deze runlijst (§4)",
        "api_football": "niet gezet - besluit van de gebruiker van 27 sep 2026, geen gat",
        "pinnacle": "ok - 48 events met 1X2 en totalen; 9 toetsbare duels en 9 (duel, lijn)-paren",
    },
})

H["last_run"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")
