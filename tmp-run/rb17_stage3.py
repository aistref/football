"""Run B, 17 sep 2026 — Stage 1/2/3: fixtures, competitiepoort, bronprobe + datadekking.

Zelfde vorm als tmp-run/ra17_stage3.py, met de runlijst van prompts/run-b.md (17 competities).
De Fotmob-ids komen uit tmp-run/b_matches.py (Run B 4 sep) en zijn daar op naam en land
geverifieerd; de BetExplorer-urls uit scripts/betexplorer.KNOWN_LEAGUE_URLS.
"""
import json
from datetime import date
from scripts import fotmob

DAY = date(2026, 9, 17)

# runlijstnaam -> (fotmob-id, ccode, seizoen vorig, huidig, betexplorer-url, sportkey)
LEAGUES = {
 "Czech First League (CZE)":      (122, "CZE", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/czech-republic/chance-liga/", None),
 "Greek Super League (GRE)":      (135, "GRE", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/greece/super-league/", "soccer_greece_super_league"),
 "Eliteserien (NOR)":             (59, "NOR", "2025", "2026",
    "https://www.betexplorer.com/football/norway/eliteserien/", "soccer_norway_eliteserien"),
 "Allsvenskan (SWE)":             (67, "SWE", "2025", "2026",
    "https://www.betexplorer.com/football/sweden/allsvenskan/", "soccer_sweden_allsvenskan"),
 "Croatian HNL (CRO)":            (252, "CRO", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/croatia/hnl/", None),
 "Hungarian NB I (HUN)":          (212, "HUN", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/hungary/nb-i/", None),
 "Romanian SuperLiga (ROU)":      (189, "ROU", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/romania/superliga/", None),
 "Segunda División (ESP)":        (140, "ESP", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/spain/laliga2/", "soccer_spain_segunda_division"),
 "Serie B (ITA)":                 (56, "ITA", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/italy/serie-b/", "soccer_italy_serie_b"),
 "2. Bundesliga (GER)":           (146, "GER", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/germany/2-bundesliga/", "soccer_germany_bundesliga2"),
 "Swiss Super League (SUI)":      (69, "SUI", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/switzerland/super-league/", "soccer_switzerland_superleague"),
 "Austrian Bundesliga (AUT)":     (38, "AUT", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/austria/bundesliga/", "soccer_austria_bundesliga"),
 "Keuken Kampioen Divisie (NED)": (111, "NED", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/netherlands/eerste-divisie/", None),
 "English League One (ENG)":      (108, "ENG", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/england/league-one/", "soccer_england_league1"),
 "English League Two (ENG)":      (109, "ENG", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/england/league-two/", "soccer_england_league2"),
 "Kategoria Superiore (ALB)":     (260, "ALB", "2025/2026", "2026/2027",
    "https://www.betexplorer.com/football/albania/abissnet-superiore/", None),
 # Kosovo staat niet op de Fotmob-daglijst (ongewijzigd sinds 13 aug 2026) en heeft geen
 # BetExplorer-slug in KNOWN_LEAGUE_URLS. Blijft daarom zonder id; zie coverage.json.
 "Kosovo Superleague (KOS)":      (None, "KOS", None, None, None, None),
}

fx = fotmob.fetch_fixtures(DAY)
BY_KEY = {}
for lg in fx.get("leagues", []):
    BY_KEY[(lg.get("primaryId") or lg.get("id"), lg.get("ccode"))] = lg

out = {}
for name, (pid, cc, s_prev, s_cur, bx, key) in LEAGUES.items():
    lg = BY_KEY.get((pid, cc)) if pid else None
    if lg is None or not lg.get("matches"):
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": [], "primaryId": pid}
        print(f"{name:32s} GEEN WEDSTRIJD")
        continue
    ms = []
    for m in lg["matches"]:
        st = m.get("status", {}) or {}
        ms.append({"match_id": m.get("id"), "home": m["home"]["name"], "away": m["away"]["name"],
                   "home_id": m["home"].get("id"), "away_id": m["away"].get("id"),
                   "kickoff_utc": st.get("utcTime"), "cancelled": st.get("cancelled")})
    out[name] = {"status": "?", "primaryId": pid, "betexplorer": bx, "sportkey": key,
                 "s_prev": s_prev, "s_cur": s_cur, "matches": ms}
    print(f"{name:32s} {len(ms)} wedstrijd(en)")
    for m in ms:
        print(f"    {m['kickoff_utc']}  {m['home']} - {m['away']}  id={m['match_id']}"
              + ("  AFGELAST" if m["cancelled"] else ""))

stats = {}
for name, v in out.items():
    if v["status"] != "?":
        continue
    prev = fotmob.fetch_league_stats(v["primaryId"], v["s_prev"])
    cur = fotmob.fetch_league_stats(v["primaryId"], v["s_cur"])
    has_xg = any("xg" in t for t in prev["teams"].values())
    played = max((t.get("played") or 0) for t in cur["teams"].values()) if cur["teams"] else 0
    cur_xg = any("xg" in t for t in cur["teams"].values())
    stats[name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg,
                 "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"),
                 "away_gpm": prev.get("away_goals_per_match")},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match"),
                "teams": len(cur["teams"]),
                "home_gpm": cur.get("home_goals_per_match"),
                "away_gpm": cur.get("away_goals_per_match")},
    }
    print(f"  {name:30s} vorig: {len(prev['teams'])} ploegen, xG={has_xg}, avg_xg={prev.get('avg_xg_per_match')}"
          f" | huidig: {played} speeldagen, xG={cur_xg}, avg_xg={cur.get('avg_xg_per_match')}")

json.dump({"fixtures": out, "stats": stats},
          open("tmp-run/rb17_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden:", sum(len(v["matches"]) for v in out.values()))
