"""Run B, 20 sep 2026 — Stage 1/2/3: fixtures, competitiepoort, bronprobe + datadekking.

Zelfde opzet als `ra20_stage3.py`, met de runlijst van `prompts/run-b.md`: zeventien competities,
geen toernooien, dus geen kruis-grenstak. Twee competities lopen op kalenderjaar (Eliteserien en
Allsvenskan): daar is het "vorige" seizoen 2025 en het lopende 2026.

Understat dekt geen enkele competitie uit deze runlijst (alleen PL, La Liga, Bundesliga, Serie A
en Ligue 1), dus het tweede xG-model van §4 is hier niet beschikbaar. Dat is geen storing maar de
bekende grens van die bron; het staat zo in het runrapport.
"""
import json
from datetime import date
from scripts import fotmob

DAY = date(2026, 9, 21)

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
 "MLS (USA)":                    (130, "USA", "2025", "2026",
                                   "https://www.betexplorer.com/football/usa/mls/",
                                   "soccer_usa_mls"),
 "Série A (BRA)":                 (268, "BRA", "2025", "2026",
                                   "https://www.betexplorer.com/football/brazil/serie-a-betano/",
                                   "soccer_brazil_campeonato"),
}

fx = fotmob.fetch_fixtures(DAY)

by_key = {}
for lg in fx.get("leagues", []):
    by_key[(lg.get("primaryId") or lg.get("id"), lg.get("ccode"))] = lg

out = {}
for name, (lid, cc, s_prev, s_cur, bx, key) in LEAGUES.items():
    lg = by_key.get((lid, cc))
    if lg is None or not lg.get("matches"):
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        print(f"{name:32s} GEEN WEDSTRIJD")
        continue
    ms = []
    for m in lg["matches"]:
        st = m.get("status", {}) or {}
        if st.get("cancelled"):
            continue
        ms.append({"match_id": m.get("id"), "home": m["home"]["name"], "away": m["away"]["name"],
                   "home_id": m["home"].get("id"), "away_id": m["away"].get("id"),
                   "kickoff_utc": st.get("utcTime")})
    if not ms:
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        print(f"{name:32s} GEEN WEDSTRIJD (alles afgelast)")
        continue
    out[name] = {"status": "?", "primaryId": lid, "betexplorer": bx, "sportkey": key,
                 "understat": None, "s_prev": s_prev, "s_cur": s_cur,
                 "crossborder": False, "matches": ms}
    print(f"{name:32s} {len(ms)} wedstrijd(en)")

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
    cur_xg = any("xg" in t for t in cur["teams"].values())
    stats[name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg,
                 "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"),
                 "away_gpm": prev.get("away_goals_per_match")},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match"),
                "teams": len(cur["teams"])},
    }
    print(f"  {name:30s} vorig: {len(prev['teams'])} ploegen, xG={has_xg}, "
          f"avg_xg={prev.get('avg_xg_per_match')} | huidig: {played} speeldagen, xG={cur_xg}, "
          f"avg_xg={cur.get('avg_xg_per_match')}")

json.dump({"fixtures": out, "stats": stats, "understat": {}},
          open("tmp-run/rb21_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden:", sum(len(v["matches"]) for v in out.values()))
