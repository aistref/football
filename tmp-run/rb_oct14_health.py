"""Run B, 14 okt 2026 — bronprobe voor source-health.json.

Zestien duels in het inzetvenster over twee competities: een volle MLS-speelronde (15) en één
Tsjechisch duel. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob voor de standen,
de context en de daglijsten, The Odds API voor de bulk en BTTS, BetExplorer voor het gratis
1X2-marktgemiddelde van de competitie zonder sportkey — dus de statusregels komen hier uit
echte aanroepen en niet uit een probe.
"""
import json, datetime
from scripts import betexplorer, fotmob

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
    print(f"{key:18} {status:8} {detail}")

# 1. Fotmob — daglijsten, 33 standen via idcheck.py, context van alle 16 duels
note("fotmob", "ok",
     "14 okt (run B): daglijsten 14 en 15 okt opgehaald (49 resp. 28 competities, 143 resp. 93 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand "
     "(afsluitcode 0). Standen van beide spelende competities geleverd (MLS id 130 met xG, Czech "
     "First League id 122 zonder xG) en context opgehaald voor alle 16 duels in het inzetvenster.")

# 2. The Odds API — via api_check.py, en deze run werkelijk gebruikt
note("the_odds_api", "ok",
     "14 okt (run B): api_check.py OK, 46 actieve voetbalcompetities, quota 19469 over / 531 "
     "gebruikt deze maand. 17 credits uitgegeven: 1 bulk-aanroep (h2h+spreads+totals, 3 credits, "
     "30 events voor soccer_usa_mls) en 14 BTTS-aanroepen à 1 credit.")
note("oddsapi", "ok",
     "14 okt (run B): fetch_bulk voor soccer_usa_mls gaf 30 events met h2h, spreads en totals; "
     "fetch_event_markets gaf btts voor 14 duels. Pinnacle, Betfair en Matchbook zaten alle drie "
     "in de respons; net_price toegepast op de Matchbook-koers van de gepubliceerde regel.")

# 3. API-Football — ontbrekende sleutel, besluit van 27 sep 2026, geen storing
note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

# 4. BetExplorer — werkelijk gebruikt: enige 1X2-bron voor de competitie zonder sportkey
probes = {
    "Chance Liga (CZE)": "https://www.betexplorer.com/football/czech-republic/chance-liga/",
    "MLS (USA)": "https://www.betexplorer.com/football/usa/mls/",
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
     "14 okt (run B): " + "; ".join(det) + ". Voor Czech First League is dit de ENIGE 1X2-bron "
     "(geen sportkey bij The Odds API): marktgemiddelde over 3 boeken, bookmaker niet herleidbaar. "
     "Voor MLS alleen gebruikt voor het kalibratieblok (§6e) en poort 8, niet voor de bet zelf.")

# 5. Understat — Run B heeft geen enkele competitie die Understat dekt
note("understat", "n/a",
     "14 okt (run B): geen aanroep. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 — "
     "geen daarvan staat op de runlijst van Run B.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "B", "date": "2026-10-14",
                 "matches_in_window": 16, "bets": 3,
                 "note": "Zestien duels in het inzetvenster [08:00 NL 14 okt, 08:00 NL 15 okt): een "
                         "volle MLS-speelronde van vijftien plus Bohemians 1905 - Mlada Boleslav. "
                         "Vijftien van de zeventien competities hadden geen wedstrijd (woensdag in "
                         "een Europese bekerweek). Drie gepubliceerde regels, alle drie een Under "
                         "3,5 op FULL in de MLS."}
H["last_run_bevinding"] = (
    "Twee dingen gebeurden vandaag voor het eerst. (1) POORT 9 NEEMT WERKELIJK IETS WEG: CF "
    "Montreal - Atlanta United (Under 3,5 @1,65, +8,66 pp) is de eerste rij ooit in de reeks "
    "doelpunten_onder, en zijn selection_score (5,999) is hoger dan die van twee van de drie "
    "regels die wel zijn gepubliceerd - de poort kost dus plek 2. Hij laat juist de twee Unders "
    "MET MINDER edge door (+7,70 en +7,69), omdat unders.check elke Under onder de gewone drempel "
    "van 8,0 doorlaat op de aanname dat `edge` daar de bindende poort is; sinds 5b (20 sep) is "
    "`edge` geen poort meer maar een afkapping. Dat is een niet-monotone uitkomst en ze staat als "
    "besluit bij de gebruiker (1h en 6g verbieden een run deze poort zelf te verzetten). (2) "
    "runwindow.py VANGT EEN HELE SPEELRONDE: negen van de vijftien MLS-duels kwamen van de "
    "daglijst van 15 oktober en waren onder de oude UTC-dagregel aan de run van morgen "
    "toegewezen, die na hun aftrap begint; een van de drie gepubliceerde regels staat in die "
    "groep. Dat is precies de voorspelling van 24 september, nu op volle schaal.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")
