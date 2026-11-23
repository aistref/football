"""Run B, 23 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **Een maandag met 13 duels in acht van de zeventien competities**; de cap van 40 bindt niet.
2. **Nul van de 142 selecties haalt zijn eigen lat.** Beide gepubliceerde regels staan er
   uitsluitend op rangorde (§5b).
3. **Beide regels zijn Unders uit DEZELFDE competitie (Allsvenskan) op DEZELFDE aftraptijd**, en
   geen van beide is door enige rem op de doelpuntenkant getoetst: de ene valt ONDER de band
   waarin poort 9 bindt (8-10 pp op FULL), de andere staat op LIGHT, dat poort 9 met opzet
   buiten laat. De twee gaten van 12 okt (LIGHT) en 22 nov (FULL) staan vandaag voor het eerst
   SAMEN, en ze vullen de hele lijst.
4. **Pinnacle is het met beide regels oneens en het zijn de twee GROOTSTE Under-afwijkingen van
   de acht toetsbare (duel, lijn)-paren** (+6,79 en +6,35 pp).
5. **De Under-kant van de SELECTIE staat op z = +4,82** over 146 gespeelde Unders; het MODEL op
   z = +0,60 over 2436 duels.
6. **8 van de 13 duels vallen uit het contextlogboek** (`squad_value = 0` aan minstens één kant),
   5 geboekt. Dezelfde bevinding als 22 nov, geen bronfout maar een meting die niet bestaat.
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
     "23 nov (run B): daglijsten 23 en 24 nov opgehaald (91 en 154 wedstrijden); idcheck.py gaf "
     "voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, afsluitcode 0 - Serie B "
     "staat op het echte id 86 met 20 ploegen. Standen van alle ACHT spelende competities "
     "geleverd, beide seizoenen. DRIE VAN DE VIJF COMPETITIES ZONDER xG SPELEN VANDAAG en dat is "
     "de bekende, vastgelegde stand, geen storing: Croatian HNL (252), Romanian SuperLiga (189) "
     "en Keuken Kampioen Divisie (111) staan in coverage.json met xG=False; de andere twee "
     "(Czech First League 122, Hungarian NB I 212) spelen niet. Die drie leveren 5 van de 13 "
     "duels, komen altijd op LIGHT uit (lat 16,0 pp) en hebben GEEN sportkey, dus elk maar DRIE "
     "doorgerekende selecties tegen 12 tot 19 bij de rest. Context voor alle 13 duels in een "
     "keer opgehaald, nul fouten. context.check_venue SLOEG EEN KEER AAN: Santos - Gremio wordt "
     "gespeeld in MorumBIS (Sao Paulo) en niet in Estadio Urbano Caldeira, het eigen stadion van "
     "Santos; de poort gaat open en het duel levert geen regel, maar Sec. 1c eist de melding ook "
     "dan. ACHT VAN DE 13 DUELS HEBBEN AAN MINSTENS EEN KANT squad_value = 0 en vallen daardoor "
     "uit het contextlogboek: 5 van de 13 geboekt, 62% valt weg. Zelfde bevinding als 22 nov "
     "(68%); geen bronfout maar een meting die niet bestaat. lineupType stond op GEEN ENKEL duel "
     "op 'confirmed' - 7 op lastStarting11, 3 op standard, 3 op unavailable; de run draait om "
     "04:00 NL en dan is er nergens een opstelling bevestigd.")

note("the_odds_api", "ok",
     "23 nov (run B): api_check.py meldt 46 actieve voetbalcompetities en 19048 credits over, 952 "
     "verbruikt deze maand. 33 van de 34 sportkeys van de repo actief; NIET ACTIEF is alleen "
     "Coppa Italia (soccer_italy_coppa_italia). Vijf actieve sportkeys die de repo niet kent, "
     "onveranderd sinds 22 nov: soccer_brazil_serie_b, soccer_england_efl_trophy, "
     "soccer_germany_bundesliga_women, soccer_germany_liga3 en soccer_uefa_nations_league. "
     "suggest_cap(19048, 8) gaf plafond 1189; VIJF inkoopbare competities kregen de bulkroute "
     "(h2h+spreads+totals, 3 credits elk = 15) en zes duels met kandidaat-edge kregen BTTS (1 "
     "elk = 6). TOTAAL 21 van 1189, 19027 over. MARKTBALANS GEHAALD: alle 5 van de 5 inkoopbare "
     "competities kregen zowel een uitkomstmarkt als een doelpuntenmarkt. De drie competities "
     "zonder sportkey (Croatian HNL, Romanian SuperLiga, Keuken Kampioen Divisie) hebben alleen "
     "het gratis BetExplorer-1X2 en dus geen doelpuntenmarkt - de grens van de gratis bron, niet "
     "van het plafond.")

note("betexplorer", "ok",
     "23 nov (run B): fixturepagina's van alle 17 competities van de runlijst opgehaald, nul "
     "fouten. De bevestigingscontrole van Sec. 1 (Fotmob-daglijst naast de "
     "BetExplorer-fixturepagina, per competitie) staat op 17 VAN DE 17 EENS, 13 duels tegen 13, "
     "inclusief de negen competities die vandaag GEEN WEDSTRIJD hebben (0 tegen 0). De "
     "parserreparatie van 21 november en de twee naamkoppelingen van 22 november houden stand.")

note("teamnames", "ok",
     "23 nov (run B): geen nieuwe naamkoppeling nodig. De reparaties van 22 november ('fk' in "
     "_DROP en de kale stadsnaam 'Brno') zijn niet opnieuw aangeraakt. Orgryte - Kalmar FF "
     "koppelde bij de Pinnacle-totalen pas op de TWEEDE poging (genormaliseerde naam) en dat is "
     "de bestaande terugval die werkt, geen defect.")

note("understat", "niet_bevraagd",
     "23 nov (run B): niet opgevraagd. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue "
     "1 - geen enkele competitie van de Run B-runlijst. Dat is geen storing maar de afbakening "
     "van Sec. 4.")

note("api_football", "niet_gezet",
     "23 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker (27 sep "
     "2026) en geen storing, geen gat en geen actiepunt (Sec. 3). De onafhankelijke kansinput "
     "komt van Fotmob, dat vandaag alles leverde; de uitzondering van Sec. 3 punt 3 - melden "
     "zodra Fotmob niet meer levert - is niet aan de orde.")

note("settling", "een_rij_blijft_terecht_open",
     "23 nov (run B): ledger.py open en shadow.py open gaven NUL afwikkelbare regels. "
     "shadow-2026-11-22-b-vancouver-whitecaps---real-salt-lake staat 3,1 uur na de aftrap nog op "
     "pending: Fotmob VINDT het duel (MLS Playoff, stand 2 - 0) maar zet finished nog niet op "
     "true, en Sec. 0 zegt dan letterlijk wachten. De terugval op de klok "
     "(SETTLE_FALLBACK_HOURS = 2,0) geldt UITSLUITEND wanneer er geen bronstatus te krijgen was, "
     "en die is er hier wel. Dit is de regel die werkt, geen vastloper; de volgende run wikkelt "
     "hem af. De twee openstaande picks in picks.jsonl zijn van Run A van VANDAAG en moeten nog "
     "beginnen.")

note("poort_9_doelpunten_onder", "reeks_54_rem_werkt_en_ving_vandaag_twee",
     "23 nov (run B): poort 9 hield vandaag TWEE selecties tegen (failed_gate = "
     "doelpunten_onder), beide FULL-Unders in de band 8-10 pp waarvoor de rem is gebouwd - onder "
     "meer Hammarby - IFK Goteborg Under 3.5 @1,784 (+9,17 pp). De reeks staat daarmee op 54 "
     "kandidaten, 51 afgewikkeld, 35,3% trefkans, -17,65u = -34,6% rendement: de rem bespaart "
     "geld en heeft de ~30 van Sec. 6d ruim gehaald. TEGELIJK IS VANDAAG HET DUIDELIJKSTE "
     "VOORBEELD VAN ZIJN TWEE GATEN: beide GEPUBLICEERDE regels zijn Unders en geen van beide is "
     "door de rem getoetst. Hammarby Under 3 staat op +6,08 pp, ONDER de band waarin de rem "
     "bindt (unders.check geeft zelf terug dat edge de bindende poort is); Orgryte Under 2.5 "
     "staat op LIGHT, dat punt 1 van Sec. 1h met opzet buiten de poort houdt (gevraagd en "
     "beantwoord 12 okt 2026). EEN RUN VERZET POORT 9 NIET OP EIGEN INITIATIEF - dit hoort als "
     "vraag aan de gebruiker en niet als wijziging.")

note("pinnacle_vergelijking", "let_op",
     "23 nov (run B): Stage 5 stap 2. Op de 1X2 acht toetsbare duels, gemiddelde absolute "
     "afstand 3,24 pp bij een gemiddelde Pinnacle-marge van 4,05%; de grootste afwijking is "
     "Hammarby - IFK Goteborg, waar het eigen model de thuisploeg 65,5% geeft tegen 78,4% bij "
     "Pinnacle (-12,92 pp). Op de doelpuntenkant acht (duel, lijn)-paren, en DE TWEE GROOTSTE "
     "AFWIJKINGEN ZIJN PRECIES DE TWEE GEPUBLICEERDE DUELS: Hammarby op lijn 3,25 eigen P(Under) "
     "55,7% tegen 49,0% bij Pinnacle (+6,79 pp, marge 4,2%) en Orgryte - Kalmar FF op lijn 2,75 "
     "eigen 58,2% tegen 51,8% (+6,35 pp, marge 4,3%). Over alle acht gemiddeld +1,77 pp op de "
     "Under-kant met 5 van 8 erboven; uitgesplitst +0,69 pp op de twee zuivere halve lijnen en "
     "+2,12 pp op de zes met push. DEZE GETALLEN GAAN NIET IN my_prob (Sec. 2).")

note("goalbias_selectie", "onveranderd_scherp",
     "23 nov (run B): margins.py goalbias staat op 2436 doorgerekende duels van 25 aug t/m 22 "
     "nov. Het MODEL staat op +0,021 doelpunt per duel (z = +0,60): de lambdas kloppen. De "
     "SELECTIE niet - over de 146 duels waar werkelijk een Under is gespeeld vielen er 0,663 "
     "doelpunt per duel MEER dan verwacht (z = +4,82; 22 nov: +4,89 over 144). De spiegel staat "
     "er ook: over de 81 gespeelde Overs vielen er 0,356 doelpunt per duel MINDER dan verwacht "
     "(z = -1,74). BEIDE gepubliceerde regels van vandaag staan op de Under-kant, dus op precies "
     "de kant waar de selectie tot nu toe de verkeerde kant op uitvalt. De VORM geeft daar "
     "nauwelijks steun aan: P(Under 2.5) staat voorspeld 42,2% tegen werkelijk 40,8% over 2436 "
     "duels (1,4 pp te hoog) - het probleem zit in de SELECTIE en niet in het grid, zoals "
     "gridfit.py measure op 28 okt al vaststelde. Deze twee regels mogen NOOIT bij elkaar worden "
     "opgeteld en geen van beide is een reden om op een enkele dag een lat te verzetten "
     "(Sec. 6d).")

note("contextlogboek_dekking", "structureel_gat_bevestigd",
     "23 nov (run B): 5 van de 13 duels komen in ctxlog, 8 vallen weg omdat squad_value aan "
     "minstens een kant 0 is. Dat is 62% weg, tegen 68% op 22 nov - dezelfde bevinding op een "
     "andere runlijst, dus het is structureel en niet dagafhankelijk. Het treft vooral de "
     "kleinere competities: Allsvenskan, Greek Super League, Croatian HNL, Romanian SuperLiga en "
     "MLS gaven aan BEIDE kanten squad_value = 0, de drie Braziliaanse duels en de Spaanse en "
     "Nederlandse duels wel marktwaarden. Gevolg: de twee GEPUBLICEERDE duels van vandaag staan "
     "allebei NIET in het contextlogboek, en poort 7 kon er dus ook niets over zeggen - hij gaat "
     "daar open op 'ontbrekende data laat de poort open' (Sec. 1c) en niet op een meting. Geen "
     "bronfout; Fotmob noteert voor deze competities geen marktwaarden.")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print(f"\n{len(S)} bronnen in data/source-health.json")
