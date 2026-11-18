"""Stage 1+2 - Run A 18 nov 2026: welke duels van de runlijst vallen in het inzetvenster?

Venster: [08:00 NL 18 nov, 08:00 NL 19 nov). Twee daglijsten (days_needed), plus BetExplorer
als tweede bron voor de vijf bekers - "niet in de daglijst" mag nooit als GEEN WEDSTRIJD worden
opgeschreven zonder tweede bron (het gat van 6 okt 2026).
"""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 11, 18)

RUNLIST = {
    "Premier League (ENG)": 47, "Serie A (ITA)": 55, "La Liga (ESP)": 87,
    "Bundesliga (GER)": 54, "Ligue 1 (FRA)": 53, "Championship (ENG)": 48,
    "Eredivisie (NED)": 57, "Primeira Liga (POR)": 61, "Belgian Pro League (BEL)": 40,
    "Super Lig (TUR)": 71, "Scottish Premiership (SCO)": 64, "Danish Superliga (DEN)": 46,
    "Ekstraklasa (POL)": 196,
    "UEFA Champions League": 42, "UEFA Europa League": 73, "UEFA Conference League": 10216,
    "FA Cup (ENG)": 132, "League Cup (ENG)": 133, "Coppa Italia (ITA)": 141,
    "KNVB Beker (NED)": 235, "DFB Pokal (GER)": 209,
}

fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
print("daglijsten:", [str(d) for d in fixtures])
per_comp = matches_for_run(DAY, fixtures, RUNLIST)

out = {}
for naam, _id in RUNLIST.items():
    ms = per_comp.get(naam, [])
    out[naam] = [{"match_id": m.match_id, "home": m.home, "away": m.away,
                  "home_id": m.home_id, "away_id": m.away_id,
                  "kickoff_utc": m.kickoff_utc.isoformat(),
                  "kickoff_nl": m.kickoff_nl.strftime("%Y-%m-%d %H:%M"),
                  "source_day": str(m.source_day), "playable": m.playable} for m in ms]
    print(f"{naam:30s} {len(ms)}")

# wat stond er WEL in de twee daglijsten, zodat een id-wijziging niet stil wegvalt
alle = {}
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []):
        alle.setdefault(f'{lg.get("name")} [{lg.get("primaryId") or lg.get("id")}]', 0)
        alle[f'{lg.get("name")} [{lg.get("primaryId") or lg.get("id")}]'] += len(lg.get("matches", []))
json.dump({"runlijst": out, "daglijst_alle_competities": alle},
          open("tmp-run/ra_nov18_runlist.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal duels in venster:", sum(len(v) for v in out.values()))
