"""Run B, 25 sep 2026 — Stage 1/2/3: fixtures via het inzetvenster, competitiepoort, bronprobe.

Verschil met `rb21_stage3.py`: Stage 1 loopt nu via `scripts/runwindow.py` (§3 Stage 1, gewijzigd
24 sep 2026) in plaats van op de UTC-datum te filteren. `include_carry_over` staat op False — de
run van 24 september gebruikte de module al, dus de band [00:00, 08:00) NL van vandaag is door die
run bekeken en mag hier niet nog een keer mee.
"""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 9, 26)

# runlijstnaam -> (fotmob league id, ccode, seizoen vorig, seizoen huidig, betexplorer-url, sportkey)
LEAGUES = {
 "Czech First League (CZE)":      (122, "CZE", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/czech-republic/chance-liga/",
                                   None),
 "Greek Super League (GRE)":      (135, "GRE", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/greece/super-league/",
                                   "soccer_greece_super_league"),
 "Eliteserien (NOR)":             (59,  "NOR", "2025", "2026",
                                   "https://www.betexplorer.com/football/norway/eliteserien/",
                                   "soccer_norway_eliteserien"),
 "Allsvenskan (SWE)":             (67,  "SWE", "2025", "2026",
                                   "https://www.betexplorer.com/football/sweden/allsvenskan/",
                                   "soccer_sweden_allsvenskan"),
 "Croatian HNL (CRO)":            (252, "CRO", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/croatia/hnl/", None),
 "Hungarian NB I (HUN)":          (212, "HUN", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/hungary/nb-i/", None),
 "Romanian SuperLiga (ROU)":      (189, "ROU", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/romania/superliga/", None),
 "Segunda División (ESP)":        (140, "ESP", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/spain/laliga2/",
                                   "soccer_spain_segunda_division"),
 "Serie B (ITA)":                 (56,  "ITA", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/italy/serie-b/",
                                   "soccer_italy_serie_b"),
 "2. Bundesliga (GER)":           (146, "GER", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/germany/2-bundesliga/",
                                   "soccer_germany_bundesliga2"),
 "Swiss Super League (SUI)":      (69,  "SUI", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/switzerland/super-league/",
                                   "soccer_switzerland_superleague"),
 "Austrian Bundesliga (AUT)":     (38,  "AUT", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/austria/bundesliga/",
                                   "soccer_austria_bundesliga"),
 "Keuken Kampioen Divisie (NED)": (111, "NED", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/netherlands/eerste-divisie/",
                                   None),
 "English League One (ENG)":      (108, "ENG", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/england/league-one/",
                                   "soccer_england_league1"),
 "English League Two (ENG)":      (109, "ENG", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/england/league-two/",
                                   "soccer_england_league2"),
 "MLS (USA)":                     (130, "USA", "2025", "2026",
                                   "https://www.betexplorer.com/football/usa/mls/",
                                   "soccer_usa_mls"),
 "Série A (BRA)":                 (268, "BRA", "2025", "2026",
                                   "https://www.betexplorer.com/football/brazil/serie-a-betano/",
                                   "soccer_brazil_campeonato"),
}

RUNLIST_IDS = {name: v[0] for name, v in LEAGUES.items()}

days = days_needed(DAY)
fixtures = {}
for d in days:
    fixtures[d] = fotmob.fetch_fixtures(d)
    n = sum(len(l.get("matches", []) or []) for l in fixtures[d].get("leagues", []) or [])
    print(f"daglijst {d}: {len(fixtures[d].get('leagues', []) or [])} competities, {n} wedstrijden")

per_comp = matches_for_run(DAY, fixtures, RUNLIST_IDS)

out = {}
for name, (lid, cc, s_prev, s_cur, bx, key) in LEAGUES.items():
    ms = per_comp.get(name) or []
    if not ms:
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        print(f"{name:32s} GEEN WEDSTRIJD")
        continue
    out[name] = {"status": "?", "primaryId": lid, "betexplorer": bx, "sportkey": key,
                 "understat": None, "s_prev": s_prev, "s_cur": s_cur,
                 "crossborder": False,
                 "matches": [{"match_id": m.match_id, "home": m.home, "away": m.away,
                              "home_id": m.home_id, "away_id": m.away_id,
                              "kickoff_utc": m.kickoff_utc, "kickoff_nl": m.kickoff_nl,
                              "source_day": m.source_day.isoformat(), "playable": m.playable}
                             for m in ms]}
    for m in ms:
        print(f"{name:32s} {m.home} - {m.away}  {m.kickoff_nl} NL "
              f"(lijst {m.source_day}, speelbaar={m.playable})")

stats = {}
for name, v in out.items():
    if v["status"] != "?" or not v.get("primaryId"):
        continue
    try:
        prev = fotmob.fetch_league_stats(v["primaryId"], v["s_prev"])
        cur = fotmob.fetch_league_stats(v["primaryId"], v["s_cur"])
    except Exception as e:
        stats[name] = {"error": f"{type(e).__name__}: {e}"}
        print(f"  {name:30s} STAND FAIL {type(e).__name__}: {e}")
        continue
    has_xg = any("xg" in t for t in prev["teams"].values())
    played = max((t.get("played") or 0) for t in cur["teams"].values()) if cur["teams"] else 0
    played_prev = max((t.get("played") or 0) for t in prev["teams"].values()) if prev["teams"] else 0
    cur_xg = any("xg" in t for t in cur["teams"].values())
    stats[name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg,
                 "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"),
                 "away_gpm": prev.get("away_goals_per_match"),
                 "played": played_prev},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match"),
                "home_gpm": cur.get("home_goals_per_match"),
                "away_gpm": cur.get("away_goals_per_match"),
                "teams": len(cur["teams"])},
    }
    print(f"  {name:30s} vorig: {len(prev['teams'])} ploegen, xG={has_xg}, "
          f"avg_xg={prev.get('avg_xg_per_match')}, speeldagen={played_prev} | "
          f"huidig: {played} speeldagen, xG={cur_xg}, avg_xg={cur.get('avg_xg_per_match')}")

json.dump({"day": DAY.isoformat(), "fixtures": out, "stats": stats, "understat": {}},
          open("tmp-run/rb26_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden in het inzetvenster:", sum(len(v["matches"]) for v in out.values()))
