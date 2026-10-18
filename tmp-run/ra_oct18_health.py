"""Run A, 18 okt 2026 — bronprobe voor source-health.json.

35 duels in het inzetvenster over tien competities: de zondag van hetzelfde weekend, kleiner dan
de zaterdag ervoor maar met alle drie de bronkanten werkelijk in gebruik. Fotmob voor de
daglijsten, de 33 standen, de context van alle 35 duels, de divisies eronder voor vier
omrekeningen, de voorbeschouwingsblokken van de vijf bets en de marktvormtelling van alle 35
duels. The Odds API voor de bulk (negen competities) en BTTS (29 duels). BetExplorer voor het
gratis 1X2-marktgemiddelde van alle tien competities, als tweede bron op de vraag wélke
wedstrijden er zijn, én als enige bron voor de vijf bekers. De statusregels komen dus uit echte
aanroepen en niet uit een probe.

Anders dan gisteren: GEEN ENKELE bronstoring. De TimeoutError op de Ekstraklasa van 17 oktober is
niet teruggekomen, en `store["errors"]` is over de hele run leeg gebleven.
"""
import json, datetime
from scripts import betexplorer

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
    print(f"{key:18} {status:8} {detail[:110]}")


note("fotmob", "ok",
     "18 okt (run A): daglijsten 18 en 19 okt opgehaald (174 resp. 64 competities, 580 resp. 110 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle tien spelende competities geleverd, alle tien met xG in zowel 2025/2026 als "
     "het lopende seizoen. Context opgehaald voor alle 35 duels, zonder één fout, en relocated is "
     "overal False. Daarnaast de standen van drie divisies eronder voor de vier omrekeningen van "
     "§4: LaLiga2 (140, voor Racing Santander en Málaga), Eerste Divisie (111, Cambuur) en de "
     "Deense 1. Division (Lyngby). Ook het voorbeschouwingsblok van de vijf gepubliceerde duels "
     "(preview.match_block: h2h, insights, weer, weekoverzicht) en de marktvormtelling van alle 35 "
     "duels (marketform.match_block) komen hiervandaan — 35 van 35, nul fouten.")

note("the_odds_api", "ok",
     "18 okt (run A): api_check.py OK, 49 actieve voetbalcompetities, quota 19237 over / 763 "
     "gebruikt deze maand. 56 credits uitgegeven: 9 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "per competitie) en 29 BTTS-aanroepen à 1 credit. Negen van de tien spelende competities "
     "hebben een sportkey; de Scottish Premiership heeft er geen en viel dus buiten de betaalde "
     "inkoop (daar is BetExplorer de enige 1X2-bron, marktgemiddelde over 17 boeken).")

note("oddsapi", "ok",
     "18 okt (run A): fetch_bulk gaf voor alle negen sportkeys events met h2h, spreads en totals "
     "(25, 16, 16, 11, 14, 14, 8, 6 en 10 events); fetch_event_markets gaf btts voor 29 van de 29 "
     "duels met een kandidaat-edge. store['errors'] is LEEG — nul fouten over de hele run. "
     "Pinnacle in de respons voor 31 van de 35 duels (Stage 5 stap 2, gemiddelde marge 3,75%, "
     "gemiddelde afstand tot het eigen model 4,33 pp); Betfair en Matchbook ook, en net_price is "
     "toegepast op de Matchbook-koers van de hoogst-rangschikkende regel Juventus – Lazio (1.97 "
     "bruto / 1.9506 netto). De winst van de beste prijs boven het BetExplorer-marktgemiddelde "
     "liep van +4,38% (Serie A) tot +7,81% (Eredivisie) over 34 duels.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "Eredivisie (NED)": "https://www.betexplorer.com/football/netherlands/eredivisie/",
    "Ekstraklasa (POL)": "https://www.betexplorer.com/football/poland/ekstraklasa/",
    "FA Cup (ENG)": "https://www.betexplorer.com/football/england/fa-cup/",
}
ok, det = True, []
for naam, url in probes.items():
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        det.append(f"{naam}: {len(rows)} fixtures met 1X2-gemiddelde")
    except Exception as e:
        ok = False
        det.append(f"{naam}: FAIL {type(e).__name__}: {e}")
note("betexplorer", "ok" if ok else "partial_failure",
     "18 okt (run A): " + "; ".join(det) + ". Deze run in drie rollen gebruikt: (1) het gratis "
     "1X2-marktgemiddelde voor alle tien competities, voor het kalibratieblok van §6e en poort 8, "
     "en voor de Scottish Premiership als ENIGE 1X2-bron; (2) als TWEEDE BRON op de vraag wélke "
     "wedstrijden er zijn — zestien van de zestien competities met een fotmob_id eens, 35 duels "
     "tegen 35, nul afwijkingen; (3) als ENIGE bron voor de vijf bekers zonder fotmob_id, die alle "
     "vijf teamparen op de fixturepagina leveren (11, 8, 8, 26, 16) en geen ronde in het venster "
     "hebben. GEEN HAPERING deze run: de TimeoutError die de Ekstraklasa op 17 oktober gaf is niet "
     "teruggekomen, en geen enkele slug viel in de homepage-redirect-faalmodus.")

note("understat", "ok",
     "18 okt (run A): fetch_league voor alle VIJF de Understat-competities (Premier League, Serie "
     "A, La Liga, Bundesliga, Ligue 1, seizoen 2025) gaf een volledige stand — die vijf speelden "
     "alle vijf op deze zondag, samen 19 duels. Werkelijk BRUIKBAAR voor 16 van die 19. De drie "
     "die het niet hebben: Osasuna – Racing Santander en Málaga – Real Sociedad (promovendus, "
     "staat terecht niet in de stand van 2025/2026) en Borussia Mönchengladbach – Hoffenheim "
     "(naamkoppeling). Dat laatste is het enige duel van vandaag waar understat_pair None gaf "
     "zonder promotiereden; het duel leverde geen regel (+3,24 pp, onder de drempel), dus het "
     "heeft niets gekost — maar het hoort hier te staan in plaats van stil weg te vallen.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "A", "date": "2026-10-18",
                 "matches_in_window": 35, "bets": 5,
                 "note": "35 duels in het inzetvenster [08:00 NL 18 okt, 08:00 NL 19 okt) over "
                         "tien competities: Ligue 1 5, Eredivisie 5, Premier League 4, Serie A 4, "
                         "La Liga 4, Danish Superliga 4, Super Lig 3, Ekstraklasa 3, Bundesliga 2 "
                         "en Scottish Premiership 1. Geen enkel duel op tier NONE — 31 FULL en 4 "
                         "LIGHT (de vier omgerekende promovendi) — en geen kruis-grensduel, want "
                         "de drie Europese toernooien spelen niet. Vijf gepubliceerde regels, de "
                         "volle MAX_SHORTLIST van een zondag, waarvan VIER boven hun eigen lat en "
                         "alle vier ook op de ruwe schaal."}
H["last_run_bevinding"] = (
    "Drie dingen. (1) VIER VAN DE VIJF REGELS HALEN HUN EIGEN LAT, EN ALLE VIER OOK RUW "
    "(bet_beide = TRUE): Juventus – Lazio BTTS nee +11,88 pp (FULL, lat 8,0), FC Twente – FC "
    "Utrecht Under 3,5 +11,03 pp (FULL, en als Under de verzwaarde lat van 10,0 uit poort 9), "
    "Osasuna – Racing Santander Over 2,5 +17,40 pp (LIGHT, lat 16,0) en Paris FC – Rennes Over "
    "2,5 +9,80 pp (FULL, lat 8,0). Dat is weken niet gebeurd — gisteren waren het twee van vijf. "
    "De drempel is daarmee vandaag GEEN afkapping (§5b stap 5) en er valt geen gekwalificeerde "
    "selectie op lijstlengte. Lees het niet als een belofte: §1g heeft op 552 gevallen gemeten "
    "dat er geen drempel op de herijkte edge bestaat die geld oplevert. (2) HET CONTEXTLOGBOEK "
    "KOMT VOOR HET EERST BOVEN DE AANTOONBAARHEIDSGRENS UIT. Op 1249 afgewikkelde wedstrijden "
    "staat de fout van het model tegen het beschikbaarheidsverschil op r = -0,066, t = -2,20, "
    "helling -19,1 pp per eenheid, tegen een aantoonbaarheidsgrens van ~16 pp bij dit aantal. De "
    "markt heeft bijna dezelfde fout (-17,6 pp, t = -2,07). Het teken wijst de verwachte kant op, "
    "maar t = 2,20 bij een drempel van 2,0 is een grensgeval en het effect is 1,5 pp over het "
    "hele bereik: POORT 7 BLIJFT EEN REM EN GEEN BIJSTELLING (§1c), en deze run verandert niets. "
    "(3) DE MARGEFOUT VAN §6f IS OP DE NIEUWE SHRINK-INSTELLING OMGESLAGEN EN DE TELLER STAAT OP "
    "147 VAN DE 150. Op `margins.py stats --since 2026-09-20` (n=147 duels met een duidelijke "
    "favoriet) staat 'favoriet wint met 2 of meer' op -5,8 pp en 'met 3 of meer' op -5,4 pp, waar "
    "september nog +9,0 resp. +9,0 pp gaf. Het grid voorspelt dus nu te VEEL scheefheid in plaats "
    "van te weinig. §6f zegt de vraag opnieuw te stellen bij ~150 duels; dat moment is binnen "
    "dagen. Met n=147 is dit geen bevinding en deze run raakt niets aan.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")
