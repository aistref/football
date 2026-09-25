"""Run A, 25 sep 2026 — Stage 1/2/3: fixtures via het inzetvenster, competitiepoort, bronprobe.

Nieuw ten opzichte van 24 sep: Stage 1 loopt nu via `scripts/runwindow.py` (§3 Stage 1, gewijzigd
24 sep 2026). Dit is de **eerste Run A** die die module gebruikt — Run B en Run C hebben hem op
24 sep ingevoerd — dus gaat `include_carry_over=True` eenmalig mee, zodat de band
[00:00, 08:00) NL van 25 sep niet door niemand bekeken wordt. Duels daaruit zijn al afgetrapt en
komen als GEEN BET in het rapport, nooit als bet.
"""
import json
from datetime import date
from scripts import fotmob, understat
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 9, 25)
CARRY = True

# runlijstnaam -> (fotmob daglijstnaam, ccode, aliassen, primaryId (basisdivisie voor het model),
#                  seizoen vorig, huidig, betexplorer-url, sportkey, understat-code)
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
 "UEFA Champions League":   ("Champions League", "INT", (), None, None, None,
                            "https://www.betexplorer.com/football/europe/champions-league/",
                            "soccer_uefa_champs_league", None),
 "UEFA Europa League":      ("Europa League", "INT", (), None, None, None,
                            "https://www.betexplorer.com/football/europe/europa-league/",
                            "soccer_uefa_europa_league", None),
 "UEFA Conference League":  ("Conference League", "INT", ("Europa Conference League",), None,
                            None, None,
                            "https://www.betexplorer.com/football/europe/conference-league/",
                            "soccer_uefa_europa_conference_league", None),
 "FA Cup (ENG)":            ("FA Cup", "ENG", (), 47, "2025/2026", "2026/2027", None, None, None),
 "League Cup (ENG)":        ("EFL Cup", "ENG", ("League Cup", "Carabao Cup"), 47,
                            "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/england/efl-cup/",
                            "soccer_england_efl_cup", None),
 "Coppa Italia (ITA)":      ("Coppa Italia", "ITA", (), 55, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/italy/coppa-italia/",
                            "soccer_italy_coppa_italia", None),
 "KNVB Beker (NED)":        ("KNVB Beker", "NED", (), 57, "2025/2026", "2026/2027", None, None, None),
 "DFB Pokal (GER)":         ("DFB Pokal", "GER", (), 54, "2025/2026", "2026/2027", None,
                            "soccer_germany_dfb_pokal", None),
}

CROSSBORDER = {"UEFA Champions League", "UEFA Europa League", "UEFA Conference League"}

# 1. daglijsten ophalen (twee, zoals days_needed voorschrijft)
fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY, include_carry_over=CARRY)}
for d, fx in fixtures.items():
    print(f"daglijst {d}: {len(fx.get('leagues', []) or [])} competities")

# 2. Fotmob-id per runlijstcompetitie opzoeken op naam, in beide daglijsten
ids, id_source = {}, {}
for name, (fm, cc, al, *_rest) in LEAGUES.items():
    for d, fx in fixtures.items():
        lg = fotmob.find_league(fx, fm, cc, al)
        if lg is not None:
            lid = lg.get("primaryId") or lg.get("id")
            if lid is not None:
                ids[name] = int(lid)
                id_source[name] = f"{d} ({lg.get('name')})"
                break
print("\nid's gevonden voor", len(ids), "van", len(LEAGUES), "competities")
for k, v in ids.items():
    print(f"   {k:30s} id={v:6d}  via {id_source[k]}")

# 3. het inzetvenster toepassen
per_comp = matches_for_run(DAY, fixtures, ids, include_carry_over=CARRY)

out = {}
for name, (fm, cc, al, pid, s_prev, s_cur, bx, key, us) in LEAGUES.items():
    ms = [m.as_dict() for m in per_comp.get(name, [])]
    if not ms:
        out[name] = {"status": "GEEN WEDSTRIJD", "matches": [], "fotmob_id": ids.get(name)}
        continue
    out[name] = {"status": "?", "primaryId": pid, "fotmob_id": ids.get(name), "betexplorer": bx,
                 "sportkey": key, "understat": us, "s_prev": s_prev, "s_cur": s_cur,
                 "crossborder": name in CROSSBORDER, "matches": ms}
    flags = []
    if name in CROSSBORDER:
        flags.append("kruis-grens")
    if any(m["source_day"] != DAY.isoformat() for m in ms):
        flags.append("deels van de daglijst van morgen")
    if any(not m["playable"] for m in ms):
        flags.append("deels onspeelbaar (carry-over)")
    print(f"{name:30s} {len(ms)} wedstrijd(en)" + ("  [" + ", ".join(flags) + "]" if flags else ""))

print("\n--- alle wedstrijden in het venster ---")
for name, v in out.items():
    for m in v["matches"]:
        print(f"  {m['kickoff_nl']} NL  {name:28s} {m['home']} - {m['away']}"
              f"  (daglijst {m['source_day']}, speelbaar={m['playable']})")

# 4. competitiestatistieken voor de actieve competities
stats = {}
for name, v in out.items():
    if v["status"] != "?" or not v.get("primaryId"):
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
                "home_gpm": cur.get("home_goals_per_match"),
                "away_gpm": cur.get("away_goals_per_match")},
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

json.dump({"day": DAY.isoformat(), "carry_over": CARRY, "ids": ids, "id_source": id_source,
           "fixtures": out, "stats": stats, "understat": us_data},
          open("tmp-run/ra25_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden:", sum(len(v["matches"]) for v in out.values()))
