"""Run A, 9 okt 2026 — Stage 1/2/3: inzetvenster, competitiepoort, bronprobe.

Overgenomen van `rb_oct08_stage3.py` (de meest recente run met wedstrijden), met de runlijst van
`prompts/run-a.md` erin. De Fotmob-id's komen **uit `data/coverage.json`** en worden hier niet
overgetypt; `scripts/idcheck.py` heeft ze deze run alle 33 groen bevonden.

**De vijf bekers van deze runlijst hebben geen `fotmob_id`.** Dat is geen fout maar een
eigenschap van de bron, en het is precies het gat dat Run A op 6 oktober geld kostte: de
FA Cup-kwalificatie stond toen níet in de Fotmob-daglijst en wél bij BetExplorer, en zonder die
tweede bron was er `GEEN WEDSTRIJD` opgeschreven bij vijf duels die er gewoon waren. Daarom gaan
de bekers deze run langs BetExplorer in plaats van langs de daglijst — zie
`ra_oct09_cups.json`, apart gemeten omdat het een andere bron met een ander datumlabel is.
"""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 10, 9)

# runlijstnaam -> (ccode, seizoen vorig, seizoen huidig, betexplorer-url, sportkey)
# Het id staat hier NIET: dat komt uit coverage.json (zie docstring).
META = {
 "Premier League (ENG)":      ("ENG", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/england/premier-league/",
                               "soccer_epl"),
 "Serie A (ITA)":             ("ITA", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/italy/serie-a/",
                               "soccer_italy_serie_a"),
 "La Liga (ESP)":             ("ESP", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/spain/laliga/",
                               "soccer_spain_la_liga"),
 "Bundesliga (GER)":          ("GER", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/germany/bundesliga/",
                               "soccer_germany_bundesliga"),
 "Ligue 1 (FRA)":             ("FRA", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/france/ligue-1/",
                               "soccer_france_ligue_one"),
 "Championship (ENG)":        ("ENG", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/england/championship/",
                               "soccer_efl_champ"),
 "Eredivisie (NED)":          ("NED", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/netherlands/eredivisie/",
                               "soccer_netherlands_eredivisie"),
 # coverage.json en run-a.md noemen hem "Primeira Liga (POR)"; BetExplorer "Liga Portugal".
 "Primeira Liga (POR)":       ("POR", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/portugal/liga-portugal/",
                               "soccer_portugal_primeira_liga"),
 "Belgian Pro League (BEL)":  ("BEL", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
                               "soccer_belgium_first_div"),
 # run-a.md schrijft "Süper Lig (TUR)", coverage.json "Super Lig (TUR)" (id 71). Zelfde
 # competitie; de sleutel hieronder is de coverage-naam, zodat het id gevonden wordt.
 "Super Lig (TUR)":           ("TUR", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/turkey/super-lig/",
                               "soccer_turkey_super_league"),
 "Scottish Premiership (SCO)":("SCO", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/scotland/premiership/",
                               None),
 "Danish Superliga (DEN)":    ("DEN", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/denmark/superliga/",
                               "soccer_denmark_superliga"),
 "Ekstraklasa (POL)":         ("POL", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/poland/ekstraklasa/",
                               "soccer_poland_ekstraklasa"),
 "UEFA Champions League":     ("INT", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/europe/champions-league/",
                               "soccer_uefa_champs_league"),
 "UEFA Europa League":        ("INT", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/europe/europa-league/",
                               "soccer_uefa_europa_league"),
 "UEFA Conference League":    ("INT", "2025/2026", "2026/2027",
                               "https://www.betexplorer.com/football/europe/conference-league/",
                               "soccer_uefa_europa_conference_league"),
}

# De vijf bekers: geen fotmob_id, dus niet via de daglijst te filteren. Ze gaan langs
# BetExplorer in `ra_oct09_cups.py`; hier staan ze alleen zodat de dekkingstabel volledig is.
CUPS = ["FA Cup (ENG)", "League Cup (ENG)", "Coppa Italia (ITA)", "KNVB Beker (NED)",
        "DFB Pokal (GER)"]

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
                              "kickoff_utc": m.kickoff_utc, "kickoff_nl": str(m.kickoff_nl),
                              "source_day": m.source_day.isoformat(), "playable": m.playable}
                             for m in ms]}
    for m in ms:
        print(f"{name:32s} {m.home} - {m.away}  {m.kickoff_nl} NL "
              f"(lijst {m.source_day}, speelbaar={m.playable})")

# Understat dekt vijf competities (§4); drie ervan spelen vandaag.
from scripts import understat as us_mod
for name in out:
    if out[name]["status"] == "?" and name in us_mod.LEAGUES:
        out[name]["understat"] = us_mod.LEAGUES[name]

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

audit = {d.isoformat(): sorted(
            [(l.get("primaryId") or l.get("id"), l.get("ccode"), l.get("name"),
              len(l.get("matches", []) or [])) for l in fx.get("leagues", []) or []],
            key=lambda r: (r[1] or "", r[2] or "")) for d, fx in fixtures.items()}

json.dump({"day": DAY.isoformat(), "fixtures": out, "stats": stats, "cups": CUPS,
           "understat": {k: v["understat"] for k, v in out.items() if v.get("understat")},
           "audit": audit},
          open("tmp-run/ra_oct09_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal wedstrijden in het inzetvenster:", sum(len(v["matches"]) for v in out.values()))
