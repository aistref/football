"""Run A, 5 sep 2026 — Stage 1/2/3: fixtures, competitiepoort, bronprobe + datadekking."""
import json
from datetime import date
from scripts import fotmob, understat

DAY = date(2026, 9, 5)

# runlijstnaam -> (fotmob daglijstnaam, ccode, aliassen, primaryId, seizoen vorig, huidig,
#                  betexplorer-url, sportkey, understat-code)
LEAGUES = {
 "Premier League (ENG)":   ("Premier League", "ENG", (), 47, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/england/premier-league/",
                            "soccer_epl", "EPL"),
 "Serie A (ITA)":          ("Serie A", "ITA", (), 55, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/italy/serie-a/",
                            "soccer_italy_serie_a", "Serie_A"),
 "La Liga (ESP)":          ("LaLiga", "ESP", ("La Liga",), 87, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/spain/laliga/",
                            "soccer_spain_la_liga", "La_liga"),
 "Bundesliga (GER)":       ("Bundesliga", "GER", (), 54, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/germany/bundesliga/",
                            "soccer_germany_bundesliga", "Bundesliga"),
 "Ligue 1 (FRA)":          ("Ligue 1", "FRA", (), 53, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/france/ligue-1/",
                            "soccer_france_ligue_one", "Ligue_1"),
 "Championship (ENG)":     ("Championship", "ENG", (), 48, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/england/championship/",
                            "soccer_efl_champ", None),
 "Eredivisie (NED)":       ("Eredivisie", "NED", (), 57, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/netherlands/eredivisie/",
                            "soccer_netherlands_eredivisie", None),
 "Primeira Liga (POR)":    ("Liga Portugal", "POR", ("Primeira Liga",), 61, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/portugal/liga-portugal/",
                            "soccer_portugal_primeira_liga", None),
 "Belgian Pro League (BEL)": ("Pro League", "BEL", ("Belgian Pro League", "Jupiler Pro League"), 40,
                            "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
                            "soccer_belgium_first_div", None),
 "Süper Lig (TUR)":        ("Super Lig", "TUR", ("Süper Lig",), 71, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/turkey/super-lig/",
                            "soccer_turkey_super_league", None),
 "Scottish Premiership (SCO)": ("Premiership", "SCO", (), 64, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/scotland/premiership/",
                            "soccer_spl", None),
 "Danish Superliga (DEN)":  ("Superligaen", "DEN", ("Superliga",), 46, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/denmark/superliga/",
                            "soccer_denmark_superliga", None),
 "Ekstraklasa (POL)":       ("Ekstraklasa", "POL", (), 196, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/poland/ekstraklasa/",
                            "soccer_poland_ekstraklasa", None),
 "UEFA Champions League":   ("Champions League", "INT", (), 42, None, None,
                            "https://www.betexplorer.com/football/europe/champions-league/",
                            "soccer_uefa_champs_league", None),
 "UEFA Europa League":      ("Europa League", "INT", (), 73, None, None,
                            "https://www.betexplorer.com/football/europe/europa-league/",
                            "soccer_uefa_europa_league", None),
 "UEFA Conference League":  ("Conference League", "INT", ("Europa Conference League",), 10216,
                            None, None,
                            "https://www.betexplorer.com/football/europe/conference-league/",
                            None, None),
 "FA Cup (ENG)":            ("FA Cup", "ENG", (), 132, None, None, None, None, None),
 "League Cup (ENG)":        ("EFL Cup", "ENG", ("League Cup", "Carabao Cup"), 133, None, None,
                            "https://www.betexplorer.com/football/england/efl-cup/", None, None),
 # Bekers: de ploegen komen uit meerdere divisies, dus 'primaryId' is de competitie waarvan de
 # basis (niveau + splits) wordt gebruikt; ploegen van buiten die divisie worden omgerekend.
 "Coppa Italia (ITA)":      ("Coppa Italia", "ITA", (), 55, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/italy/coppa-italia/",
                            "soccer_italy_coppa_italia", None),
 "KNVB Beker (NED)":        ("KNVB Beker", "NED", (), 57, "2025/2026", "2026/2027", None, None, None),
 "DFB Pokal (GER)":         ("DFB Pokal", "GER", (), 54, "2025/2026", "2026/2027", None,
                            "soccer_germany_dfb_pokal", None),
}

fx = fotmob.fetch_fixtures(DAY)
out = {}
for name, (fm, cc, al, pid, s_prev, s_cur, bx, key, us) in LEAGUES.items():
    lg = fotmob.find_league(fx, fm, cc, al)
    if lg is None or not lg.get("matches"):
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        print(f"{name:30s} GEEN WEDSTRIJD")
        continue
    ms = [{"match_id": m.get("id"), "home": m["home"]["name"], "away": m["away"]["name"],
           "home_id": m["home"].get("id"), "away_id": m["away"].get("id"),
           "kickoff_utc": m.get("status", {}).get("utcTime")}
          for m in lg["matches"]]
    out[name] = {"status": "?", "primaryId": pid, "betexplorer": bx, "sportkey": key,
                 "understat": us, "s_prev": s_prev, "s_cur": s_cur, "matches": ms}
    print(f"{name:30s} {len(ms)} wedstrijd(en)")

stats = {}
for name, v in out.items():
    if v["status"] != "?":
        continue
    prev = fotmob.fetch_league_stats(v["primaryId"], v["s_prev"])
    cur = fotmob.fetch_league_stats(v["primaryId"], v["s_cur"])
    has_xg = any("xg" in t for t in prev["teams"].values())
    played = max((t.get("played") or 0) for t in cur["teams"].values())
    cur_xg = any("xg" in t for t in cur["teams"].values())
    stats[name] = {
        "prev": {"teams": len(prev["teams"]), "has_xg": has_xg,
                 "avg_xg": prev.get("avg_xg_per_match"),
                 "home_gpm": prev.get("home_goals_per_match"), "away_gpm": prev.get("away_goals_per_match")},
        "cur": {"played": played, "has_xg": cur_xg, "avg_xg": cur.get("avg_xg_per_match")},
    }
    print(f"  {name:28s} vorig: {len(prev['teams'])} ploegen, xG={has_xg}, avg_xg={prev.get('avg_xg_per_match')}"
          f" | huidig: {played} speeldagen, xG={cur_xg}, avg_xg={cur.get('avg_xg_per_match')}")

us_data = {}
for name, v in out.items():
    if v["status"] != "?" or not v.get("understat"):
        continue
    try:
        code = v["understat"]
        d_prev = understat.fetch_league(code, understat.season_code(v["s_prev"]))
        t_prev = understat.team_stats(d_prev)
        ctx_prev = understat.league_context(t_prev)
        us_data[name] = {"ok": True, "code": code, "teams": len(t_prev), "context": ctx_prev}
        print(f"  understat {name:24s} {len(t_prev)} ploegen, avg_xg {ctx_prev.get('avg_xg_per_match')}")
    except Exception as e:
        us_data[name] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        print(f"  understat {name:24s} FAIL {type(e).__name__}: {e}")

json.dump({"fixtures": out, "stats": stats, "understat": us_data},
          open("tmp-run/ra5_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden:", sum(len(v["matches"]) for v in out.values()))
