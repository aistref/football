"""Stage 1+2 — Run A 22 nov 2026: welke duels van de runlijst vallen in het inzetvenster?

Venster: [08:00 NL 22 nov, 08:00 NL 23 nov). Twee daglijsten (days_needed). De zes bekers
staan van 1 juli t/m 31 december niet op de runlijst (cups.filter_runlist, run-a.md).
"""
import json
from datetime import date
from scripts import fotmob, cups
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 11, 22)

RUNLIST = {
    "Premier League (ENG)": 47, "Serie A (ITA)": 55, "La Liga (ESP)": 87,
    "Bundesliga (GER)": 54, "Ligue 1 (FRA)": 53, "Championship (ENG)": 48,
    "Eredivisie (NED)": 57, "Primeira Liga (POR)": 61, "Belgian Pro League (BEL)": 40,
    "Super Lig (TUR)": 71, "Scottish Premiership (SCO)": 64, "Danish Superliga (DEN)": 46,
    "Ekstraklasa (POL)": 196,
    "UEFA Champions League": 42, "UEFA Europa League": 73, "UEFA Conference League": 10216,
    "FA Cup (ENG)": 132, "League Cup (ENG)": 133, "Coppa Italia (ITA)": 141,
    "KNVB Beker (NED)": 235, "DFB Pokal (GER)": 209, "Copa del Rey (ESP)": 138,
}

mee, buiten = cups.filter_runlist(RUNLIST, DAY)
print("op de runlijst vandaag:", len(mee))
for b in buiten:
    print("  BUITEN DE RUNLIST:", b, "—", cups.reason(b, DAY))

fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
print("daglijsten:", [str(d) for d in fixtures])
per_comp = matches_for_run(DAY, fixtures, mee)

out = {}
for naam in mee:
    ms = per_comp.get(naam, [])
    out[naam] = [{"match_id": m.match_id, "home": m.home, "away": m.away,
                  "home_id": m.home_id, "away_id": m.away_id,
                  "kickoff_utc": m.kickoff_utc, "kickoff_nl": m.kickoff_nl,
                  "source_day": str(m.source_day), "playable": m.playable} for m in ms]
    print(f"{naam:30s} {len(ms)}")

# controle: wat stond er WEL in de daglijsten, ook voor de zes bekers buiten de lijst
alle = {}
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []):
        k = f'{lg.get("name")} [{lg.get("primaryId") or lg.get("id")}]'
        alle[k] = alle.get(k, 0) + len(lg.get("matches", []))

buiten_gespeeld = {}
for naam in buiten:
    lid = RUNLIST[naam]
    n = 0
    for d, fx in fixtures.items():
        for lg in fx.get("leagues", []):
            if (lg.get("primaryId") or lg.get("id")) == lid:
                n += len(lg.get("matches", []))
    buiten_gespeeld[naam] = n
print("\nbekers buiten de lijst, duels in de daglijsten:", buiten_gespeeld)

json.dump({"runlijst": out, "buiten_de_runlijst": {n: cups.reason(n, DAY) for n in buiten},
           "buiten_gespeeld": buiten_gespeeld,
           "daglijst_alle_competities": alle},
          open("tmp-run/ra_nov22_runlist.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal duels in venster:", sum(len(v) for v in out.values()))
