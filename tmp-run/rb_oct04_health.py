"""§6b-3 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft.

Schrijfwijze volgens `_doc`: één doorlopende tekst per bron, chronologisch, oudste feit eerst.
Geen runverslagen achter elkaar plakken.
"""
import json

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
DAG = "2026-10-04"


def bij(key, status, tekst, **extra):
    v = S.setdefault(key, {})
    v["status"] = status
    v["last_checked"] = DAG
    v["detail"] = (str(v.get("detail", "")).rstrip() + f"  [Run B] {tekst}").strip()
    v.update(extra)


bij("fotmob", "ok",
    "Run B 4 okt: twee daglijsten (4 okt: 88 competities/273 duels; 5 okt: 30/53), 34 "
    "standenverzoeken voor scripts/idcheck.py (17 competities, alle 17 OK, afsluitcode 0), vier "
    "standen voor de twee spelende competities (vorig en lopend seizoen) en de wedstrijdcontext "
    "van alle zes duels in het inzetvenster. Alles HTTP 200, geen storing; Fotmob was opnieuw de "
    "enige kansbron. Geen enkel duel uit de runlijst droeg status.cancelled. NIEUW GEMETEN, en "
    "het is een bevestiging dat de statusregel van §0 doet wat ze moet doen: de "
    "vriendschappelijke interland USA – Mexico stond gepland op 02:00Z en is werkelijk om "
    "04:10Z begonnen (firstHalfStarted), dus bij het afwikkelen van 05:07 stond hij op HT met "
    "1-0 en finished=False. `settling.settleable` wachtte correct — met de oude klokregel van "
    "twee uur na de geplánde aftrap was deze pick op de ruststand afgerekend.")

bij("the_odds_api", "ok",
    "Run B 4 okt: api_check.py geeft 49 actieve voetbalcompetities en 19.914 van de 20.000 "
    "credits over (86 deze maand). Sleutel niet afgewezen. 6 credits uitgegeven: één "
    "bulk-aanroep (h2h + spreads + totals, 3 credits) voor soccer_spain_segunda_division — de "
    "enige spelende competitie met een sportkey — plus drie per-duel BTTS-verzoeken (1 credit "
    "elk) voor de drie duels met een kandidaat-edge; quota daarna 19.908. Geen naamkoppelfouten "
    "deze run: alle vijf de Segunda-duels koppelden vanzelf aan de h2h- en spreads-respons en "
    "side_of gaf voor beide kanten een antwoord, dus er zijn geen stil weggevallen selecties. "
    "Wat opvalt in het aanbod: bij géén van de vijf duels zat er een +0.5-lijn in de "
    "spreads-respons, dus Double Chance was deze run nergens te koop — dat staat per duel met "
    "die reden in markets_checked en is geen gat in de administratie.")

bij("oddsapi", "ok",
    "Sleutel geaccepteerd (api_check.py 4 okt 2026). Gebruikt voor Segunda División (ESP): 6 "
    "credits.")

bij("betexplorer", "ok",
    "Run B 4 okt: twee fixturepagina's opgehaald (spain/laliga2 9 rijen waarvan 5 vandaag, "
    "netherlands/eerste-divisie 9 rijen waarvan 1 vandaag), beide HTTP 200. Voor de Keuken "
    "Kampioen Divisie opnieuw de ENIGE 1X2-bron — die competitie heeft geen sportkey bij The "
    "Odds API — en het marktgemiddelde komt daar over 3 boeken; dat is de reden dat VVV-Venlo – "
    "Roda JC Kerkrade drie doorgerekende selecties kreeg in plaats van dertien.")

bij("understat", "ok",
    "Run B 4 okt: niet aangeroepen — geen van de twee spelende competities (Segunda División, "
    "Keuken Kampioen Divisie) zit in de vijf die Understat dekt (§4). Status ongewijzigd "
    "overgenomen. Geen storing, maar wél de reden dat deze run geen tweede xG-model had.")

bij("api_football", "missing_key",
    "Met opzet afwezig sinds het besluit van de gebruiker op 27 sep 2026 (§3). Geen gat, geen "
    "actiepunt, niet in de notificatie. api_check.py meldt het onveranderd als feit en dringt "
    "niet aan.")

d["last_run"] = f"{DAG} run-b"
d["updated"] = DAG
d["last_run_bevinding"] = (
    "Run B 4 okt 2026 — interlandvenster: vijftien van de zeventien competities hadden geen "
    "wedstrijd, zes duels in het venster, drie regels op rangorde (§5b) waarvan één boven de "
    "lat. Drie dingen die een volgende run moet weten. "
    "(1) DE MEETLAT VAN §1e IS VANDAAG GEHAALD, EN HIJ WIJST NAAR BUITEN. De `underdog`-reeks "
    "in het schaduwlogboek staat op **31 afgewikkelde kandidaten met +12,6% rendement** (17/31 "
    "= 54,8% trefkans). §1e noemt zelf precies deze uitweg: de poort 'gaat eruit zodra het "
    "schaduwlogboek laat zien dat hij structureel winnaars tegenhoudt (positieve ROI over >= 30 "
    "afgewikkelde kandidaten)'. Op 30 september stond die reeks op 20 en was dat argument niet "
    "beschikbaar; nu wel. Wat er eerlijk bij hoort: de tegenhanger `underdog_ruw` staat op "
    "-8,8% over 17 gevallen en die twee mogen nooit worden opgeteld (twee populaties), en de "
    "kalibratiefout die de poort afdekt staat nog: +1,95 pp te veel kans op longshots en -3,82 "
    "pp te weinig op favorieten over 3792 uitkomsten. Dit is daarom GEEN wijziging die deze run "
    "zelf doorvoert — §1e legt de keuze expliciet bij de gebruiker (risicobereidheid, niet "
    "data) — maar het is het eerste moment waarop de vraag met het door §1e geëiste aantal te "
    "beantwoorden is. Staat als besluit in het dagrapport. "
    "(2) HET STRUCTURELE TIER2-GAT IN DE SEGUNDA IS GEEN TOEVAL MEER. Derde run op rij een duel "
    "op NONE omdat een promovendus uit de Primera Federación komt en promotion.TIER2 geen "
    "Spaans paar LaLiga2/Primera Federación kent — 2 en 3 oktober Sabadell, vandaag Celta "
    "Fortuna. De foutmelding noemt alleen de TIER1-tak ('staat niet in de stand van La Liga'), "
    "waardoor de oorzaak verkeerd leest. Niet opgelost deze run: het vraagt een gemeten factor "
    "voor dat divisiepaar, en die verzinnen is wat §2 en §4 verbieden. "
    "(3) HET KALIBRATIELOGBOEK HOUDT EEN STAART VAN 129 ONAFGEWIKKELDE WAARNEMINGEN. Dat zijn 43 "
    "duels uit augustus en september (Championship 10, Premier League 8, Bundesliga 8, English "
    "League One 7, en acht losse) die ook na de reparatie van 3 oktober op `won = None` blijven "
    "staan. Oorzaak is bevinding 2 van 3 oktober: `settling.DayIndex.lookup` kent de aliastabel "
    "van tmp-run/ra_names.py niet en koppelt korte weergavenamen niet aan de volledige naam in "
    "de daglijst. De vijftien rijen van 3 oktober die nog open staan zijn iets anders en geen "
    "fout: vier FA Cup-duels van Run A en USA – Mexico, dat op dit moment nog wordt gespeeld.")
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", d["last_run"])
