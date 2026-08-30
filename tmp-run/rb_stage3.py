"""Run B, 30 aug 2026 — Stage 1/2/3: fixtures, competitiepoort, bronprobe."""
import json, sys
from datetime import date, datetime
from scripts import fotmob

DAY = date(2026, 8, 30)

# naam in de runlijst -> (fotmob daglijst-naam, ccode, primaryId voor stats, seizoen vorig, seizoen huidig, betexplorer slug, sportkey)
LEAGUES = {
 "Czech First League (CZE)":      ("1. Liga", "CZE", 122, "2025/2026", "2026/2027", "czech-republic/chance-liga", None),
 "Greek Super League (GRE)":      ("Super League", "GRE", 135, "2025/2026", "2026/2027", "greece/super-league", "soccer_greece_super_league"),
 "Eliteserien (NOR)":             ("Eliteserien", "NOR", 59, "2025", "2026", "norway/eliteserien", "soccer_norway_eliteserien"),
 "Allsvenskan (SWE)":             ("Allsvenskan", "SWE", 67, "2025", "2026", "sweden/allsvenskan", "soccer_sweden_allsvenskan"),
 "Croatian HNL (CRO)":            ("HNL", "CRO", 252, "2025/2026", "2026/2027", "croatia/hnl", None),
 "Hungarian NB I (HUN)":          ("NB I", "HUN", 212, "2025/2026", "2026/2027", "hungary/nb-i", None),
 "Romanian SuperLiga (ROU)":      ("Superliga", "ROU", 189, "2025/2026", "2026/2027", "romania/superliga", None),
 "Segunda División (ESP)":        ("LaLiga2", "ESP", 140, "2025/2026", "2026/2027", "spain/laliga2", "soccer_spain_segunda_division"),
 "Serie B (ITA)":                 ("Serie B", "ITA", 86, "2025/2026", "2026/2027", "italy/serie-b", "soccer_italy_serie_b"),
 "2. Bundesliga (GER)":           ("2. Bundesliga", "GER", 146, "2025/2026", "2026/2027", "germany/2-bundesliga", "soccer_germany_bundesliga2"),
 "Swiss Super League (SUI)":      ("Super League", "SUI", 69, "2025/2026", "2026/2027", "switzerland/super-league", "soccer_switzerland_superleague"),
 "Austrian Bundesliga (AUT)":     ("Bundesliga", "AUT", 38, "2025/2026", "2026/2027", "austria/bundesliga", "soccer_austria_bundesliga"),
 "Keuken Kampioen Divisie (NED)": ("Eerste Divisie", "NED", 111, "2025/2026", "2026/2027", "netherlands/eerste-divisie", None),
 "English League One (ENG)":      ("League One", "ENG", 108, "2025/2026", "2026/2027", "england/league-one", "soccer_england_league1"),
 "English League Two (ENG)":      ("League Two", "ENG", 109, "2025/2026", "2026/2027", "england/league-two", "soccer_england_league2"),
 "Kategoria Superiore (ALB)":     ("Kategoria Superiore", "ALB", 260, "2025/2026", "2026/2027", "albania/kategoria-superiore", None),
 "Kosovo Superleague (KOS)":      ("Superliga", "KOS", None, None, None, None, None),
}

fx = fotmob.fetch_fixtures(DAY)
out = {}
for name, (fm_name, ccode, pid, s_prev, s_cur, slug, key) in LEAGUES.items():
    lg = fotmob.find_league(fx, fm_name, ccode)
    if lg is None:
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": []}
        continue
    ms = []
    for m in lg.get("matches", []):
        ms.append({"match_id": m.get("id"),
                   "home": m["home"]["name"], "away": m["away"]["name"],
                   "home_id": m["home"].get("id"), "away_id": m["away"].get("id"),
                   "kickoff_utc": m.get("status", {}).get("utcTime"),
                   "started": m.get("status", {}).get("started")})
    out[name] = {"status": "?", "fotmob_day_id": lg.get("id"), "primaryId": pid,
                 "slug": slug, "sportkey": key, "s_prev": s_prev, "s_cur": s_cur,
                 "matches": ms}
json.dump(out, open("tmp-run/rb_fixtures.json", "w"), ensure_ascii=False, indent=1)
tot = sum(len(v["matches"]) for v in out.values())
for k, v in out.items():
    print(f"{k:32s} {len(v['matches'])}")
print("TOTAAL", tot)
