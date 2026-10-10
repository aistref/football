"""Run B, 10 okt 2026 — Stage 1/2/3: inzetvenster, competitiepoort, bronprobe.

Verschil met `rb26_stage3.py`: de Fotmob-id's komen **uit `data/coverage.json`** in plaats van
hier te worden overgetypt. Dat is wat `prompts/run-b.md` sinds 29 sep 2026 eist, en het is de
reden dat `Serie B (ITA)` daar vier dagen op 56 stond in plaats van op 86 — een overgetypt id
geeft geen foutmelding maar nul wedstrijden, en nul wedstrijden leest als GEEN WEDSTRIJD.
`scripts/idcheck.py` controleert diezelfde id's, óók die van vandaag stil zijn.
"""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 10, 10)

# runlijstnaam -> (ccode, seizoen vorig, seizoen huidig, betexplorer-url, sportkey)
# Het id staat hier NIET: dat komt uit coverage.json (zie docstring).
META = {
 "Czech First League (CZE)":      ("CZE", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/czech-republic/chance-liga/", None),
 "Greek Super League (GRE)":      ("GRE", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/greece/super-league/",
                                   "soccer_greece_super_league"),
 "Eliteserien (NOR)":             ("NOR", "2025", "2026",
                                   "https://www.betexplorer.com/football/norway/eliteserien/",
                                   "soccer_norway_eliteserien"),
 "Allsvenskan (SWE)":             ("SWE", "2025", "2026",
                                   "https://www.betexplorer.com/football/sweden/allsvenskan/",
                                   "soccer_sweden_allsvenskan"),
 "Croatian HNL (CRO)":            ("CRO", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/croatia/hnl/", None),
 "Hungarian NB I (HUN)":          ("HUN", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/hungary/nb-i/", None),
 "Romanian SuperLiga (ROU)":      ("ROU", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/romania/superliga/", None),
 "Segunda División (ESP)":        ("ESP", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/spain/laliga2/",
                                   "soccer_spain_segunda_division"),
 "Serie B (ITA)":                 ("ITA", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/italy/serie-b/",
                                   "soccer_italy_serie_b"),
 "2. Bundesliga (GER)":           ("GER", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/germany/2-bundesliga/",
                                   "soccer_germany_bundesliga2"),
 "Swiss Super League (SUI)":      ("SUI", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/switzerland/super-league/",
                                   "soccer_switzerland_superleague"),
 "Austrian Bundesliga (AUT)":     ("AUT", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/austria/bundesliga/",
                                   "soccer_austria_bundesliga"),
 "Keuken Kampioen Divisie (NED)": ("NED", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/netherlands/eerste-divisie/", None),
 "English League One (ENG)":      ("ENG", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/england/league-one/",
                                   "soccer_england_league1"),
 "English League Two (ENG)":      ("ENG", "2025/2026", "2026/2027",
                                   "https://www.betexplorer.com/football/england/league-two/",
                                   "soccer_england_league2"),
 "MLS (USA)":                     ("USA", "2025", "2026",
                                   "https://www.betexplorer.com/football/usa/mls/",
                                   "soccer_usa_mls"),
 "Série A (BRA)":                 ("BRA", "2025", "2026",
                                   "https://www.betexplorer.com/football/brazil/serie-a-betano/",
                                   "soccer_brazil_campeonato"),
}

COV = json.load(open("data/coverage.json"))["competitions"]
LEAGUES = {name: (COV[name]["fotmob_id"], *meta) for name, meta in META.items()}
RUNLIST_IDS = {name: v[0] for name, v in LEAGUES.items()}
print("id's uit coverage.json:", RUNLIST_IDS)

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
                 "understat": None, "s_prev": s_prev, "s_cur": s_cur, "crossborder": False,
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
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg, "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"), "away_gpm": prev.get("away_goals_per_match"),
                 "played": played_prev},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match"),
                "home_gpm": cur.get("home_goals_per_match"), "away_gpm": cur.get("away_goals_per_match"),
                "teams": len(cur["teams"])},
    }
    print(f"  {name:30s} vorig: {len(prev['teams'])} ploegen, xG={has_xg}, "
          f"avg_xg={prev.get('avg_xg_per_match')}, speeldagen={played_prev} | "
          f"huidig: {played} speeldagen, xG={cur_xg}, avg_xg={cur.get('avg_xg_per_match')}")

# audit: alle competities op beide daglijsten, zodat een gemiste competitie na te lopen is
audit = {d.isoformat(): sorted(
            [(l.get("primaryId") or l.get("id"), l.get("ccode"), l.get("name"),
              len(l.get("matches", []) or [])) for l in fx.get("leagues", []) or []],
            key=lambda r: (r[1] or "", r[2] or "")) for d, fx in fixtures.items()}

json.dump({"day": DAY.isoformat(), "fixtures": out, "stats": stats, "understat": {}, "audit": audit},
          open("tmp-run/rb_oct10_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden in het inzetvenster:", sum(len(v["matches"]) for v in out.values()))
