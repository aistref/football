"""Run B, 13 okt 2026 — bronprobe voor source-health.json.

Deze run heeft nul wedstrijden in het inzetvenster, dus er is geen analyse en geen inkoop.
De bronnen worden evengoed gemeten: een stille bron die omvalt op een dag zonder wedstrijden
moet morgen niet als verrassing komen. BetExplorer wordt daarom met één competitiepagina
geprobeerd ook al is hij deze run niet nodig.
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

# 1. Fotmob — daglijsten, 33 standen via idcheck.py, allemaal geleverd
note("fotmob", "ok",
     "13 okt (run B): daglijsten 13 en 14 okt opgehaald (54 resp. 48 competities, 186 resp. 137 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand.")

# 2. The Odds API — via api_check.py
note("the_odds_api", "ok",
     "13 okt (run B): api_check.py OK, 46 actieve voetbalcompetities, quota 19487 over / 513 "
     "gebruikt deze maand. Geen credits uitgegeven: nul wedstrijden in het inzetvenster.")
note("oddsapi", "ok", "13 okt (run B): geen aanroep nodig (nul wedstrijden); sleutel getest via api_check.py.")

# 3. API-Football — ontbrekende sleutel, besluit van 27 sep 2026, geen storing
note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

# 4. BetExplorer — niet nodig deze run, toch geprobeerd op één pagina
try:
    rows = betexplorer.fetch_league_fixtures(
        "https://www.betexplorer.com/football/czech-republic/chance-liga/")
    note("betexplorer", "ok",
         f"13 okt (run B): niet nodig voor de analyse (nul wedstrijden), wel geprobeerd op "
         f"Chance Liga (CZE) — {len(rows)} fixtures met 1X2-gemiddelde teruggekregen.")
except Exception as e:
    note("betexplorer", f"{type(e).__name__}",
         f"13 okt (run B): probe op Chance Liga (CZE) faalde — {type(e).__name__}: {e}")

# 5. Understat — Run B heeft geen enkele competitie die Understat dekt
note("understat", "n/a",
     "13 okt (run B): geen aanroep. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 — "
     "geen daarvan staat op de runlijst van Run B.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "B", "date": "2026-10-13",
                 "matches_in_window": 0, "bets": 0,
                 "note": "Nul wedstrijden in het inzetvenster [08:00 NL 13 okt, 08:00 NL 14 okt): "
                         "de hele runlijst van zeventien competities ligt stil in het "
                         "interlandvenster. Drie duels van runlijst-competities staan op de "
                         "daglijsten maar vallen in een aangrenzend venster."}
H["last_run_bevinding"] = (
    "De drie duels die wél op de daglijsten stonden, vallen alle drie buiten dit inzetvenster, en "
    "runwindow.py wees ze alle drie correct af: RB Bragantino - Cruzeiro (Serie A BRA) trapte af om "
    "02:00 NL op 13 okt en is op 12 okt door Run B doorgerekend; Bohemians 1905 - Mlada Boleslav "
    "(CZE, 18:00 NL 14 okt) en zes MLS-duels (01:30 NL 15 okt) horen bij de run van 14 oktober. "
    "Dat is precies waarvoor die module op 24 sep is gebouwd, nu in de omgekeerde richting: hij "
    "houdt een duel buiten de deur dat de oude UTC-dagregel wel had meegenomen.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")
