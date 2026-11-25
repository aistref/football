"""Run A, 25 nov 2026 — Stage 1/2/3: inzetvenster, competitiepoort, bronprobe.

Fotmob-id's komen uit data/coverage.json (niet overgetypt; idcheck.py controleert ze).
De zes bekers vallen vandaag BUITEN DE RUNLIJST (cups.filter_runlist met DAY).
"""
import json
from datetime import date
from scripts import fotmob, oddsapi, cups
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 11, 25)

META = {
 "Premier League (ENG)":       ("ENG", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/england/premier-league/"),
 "Serie A (ITA)":              ("ITA", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/italy/serie-a/"),
 "La Liga (ESP)":              ("ESP", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/spain/laliga/"),
 "Bundesliga (GER)":           ("GER", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/germany/bundesliga/"),
 "Ligue 1 (FRA)":              ("FRA", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/france/ligue-1/"),
 "Championship (ENG)":         ("ENG", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/england/championship/"),
 "Eredivisie (NED)":           ("NED", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/netherlands/eredivisie/"),
 "Primeira Liga (POR)":        ("POR", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/portugal/liga-portugal/"),
 "Belgian Pro League (BEL)":   ("BEL", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/belgium/jupiler-pro-league/"),
 "Super Lig (TUR)":            ("TUR", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/turkey/super-lig/"),
 "Scottish Premiership (SCO)": ("SCO", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/scotland/premiership/"),
 "Danish Superliga (DEN)":     ("DEN", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/denmark/superliga/"),
 "Ekstraklasa (POL)":          ("POL", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/poland/ekstraklasa/"),
 "UEFA Champions League":      ("EUR", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/europe/champions-league/"),
 "UEFA Europa League":         ("EUR", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/europe/europa-league/"),
 "UEFA Conference League":     ("EUR", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/europe/conference-league/"),
 "FA Cup (ENG)":               ("ENG", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/england/fa-cup/"),
 "League Cup (ENG)":           ("ENG", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/england/efl-cup/"),
 "Coppa Italia (ITA)":         ("ITA", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/italy/coppa-italia/"),
 "KNVB Beker (NED)":           ("NED", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/netherlands/knvb-beker/"),
 "DFB Pokal (GER)":            ("GER", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/germany/dfb-pokal/"),
 "Copa del Rey (ESP)":         ("ESP", "2025/2026", "2026/2027", "https://www.betexplorer.com/football/spain/copa-del-rey/"),
}

CROSSBORDER = {"UEFA Champions League", "UEFA Europa League", "UEFA Conference League"}

COV = json.load(open("data/coverage.json"))["competitions"]
IDS = {}
for name in META:
    c = COV.get(name) or {}
    IDS[name] = c.get("fotmob_id")
print("id's uit coverage.json:")
for n, i in IDS.items():
    print(f"  {n:30s} {i}")

# de zes bekers eruit (cups.py, met de rundag)
mee, buiten = cups.filter_runlist(IDS, DAY)
print("\nBUITEN DE RUNLIJST vandaag:", list(buiten))
RUNLIST_IDS = {k: v for k, v in mee.items() if v}
print("runlijst na de bekerfilter:", len(RUNLIST_IDS), "competities")

print("\nsportkey-controle:")
for name in RUNLIST_IDS:
    print(f"  {name:30s} {oddsapi.sport_key(name)}")

days = days_needed(DAY)
fixtures = {}
for d in days:
    fixtures[d] = fotmob.fetch_fixtures(d)
    n = sum(len(l.get("matches", []) or []) for l in fixtures[d].get("leagues", []) or [])
    print(f"daglijst {d}: {len(fixtures[d].get('leagues', []) or [])} competities, {n} wedstrijden")

per_comp = matches_for_run(DAY, fixtures, RUNLIST_IDS)

out = {}
for name in RUNLIST_IDS:
    cc, s_prev, s_cur, bx = META[name]
    ms = per_comp.get(name) or []
    if not ms:
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        print(f"{name:30s} GEEN WEDSTRIJD")
        continue
    out[name] = {"status": "?", "primaryId": RUNLIST_IDS[name], "betexplorer": bx,
                 "crossborder": name in CROSSBORDER,
                 "sportkey": oddsapi.sport_key(name), "s_prev": s_prev, "s_cur": s_cur,
                 "matches": [{"match_id": m.match_id, "home": m.home, "away": m.away,
                              "home_id": m.home_id, "away_id": m.away_id,
                              "kickoff_utc": m.kickoff_utc, "kickoff_nl": m.kickoff_nl,
                              "source_day": m.source_day.isoformat(), "playable": m.playable}
                             for m in ms]}
    for m in ms:
        print(f"{name:30s} {m.home} - {m.away}  {m.kickoff_nl} NL (lijst {m.source_day}, speelbaar={m.playable})")
for name in buiten:
    out[name] = {"status": "BUITEN DE RUNLIJST", "matches": [], "reden": cups.reason(name, DAY)}

stats = {}
for name, v in out.items():
    if v["status"] != "?":
        continue
    prev = fotmob.fetch_league_stats(v["primaryId"], v["s_prev"])
    cur = fotmob.fetch_league_stats(v["primaryId"], v["s_cur"])
    has_xg = any("xg" in t for t in prev["teams"].values())
    played = max((t.get("played") or 0) for t in cur["teams"].values()) if cur["teams"] else 0
    played_prev = max((t.get("played") or 0) for t in prev["teams"].values()) if prev["teams"] else 0
    cur_xg = any("xg" in t for t in cur["teams"].values())
    stats[name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg, "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"), "away_gpm": prev.get("away_goals_per_match"),
                 "played": played_prev},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match"),
                "home_gpm": cur.get("home_goals_per_match"), "away_gpm": cur.get("away_goals_per_match"),
                "teams": len(cur["teams"])},
    }
    print(f"  {name:28s} vorig: {len(prev['teams'])} ploegen xG={has_xg} avg_xg={prev.get('avg_xg_per_match')} "
          f"speeldagen={played_prev} | huidig: {played} speeldagen xG={cur_xg} avg_xg={cur.get('avg_xg_per_match')}")

audit = {d.isoformat(): sorted(
            [(l.get("primaryId") or l.get("id"), l.get("ccode"), l.get("name"),
              len(l.get("matches", []) or [])) for l in fx.get("leagues", []) or []],
            key=lambda r: (r[1] or "", r[2] or "")) for d, fx in fixtures.items()}

json.dump({"day": DAY.isoformat(), "fixtures": out, "stats": stats, "audit": audit},
          open("tmp-run/ra_nov25_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden in het inzetvenster:", sum(len(v["matches"]) for v in out.values()))
