"""Run A, 6 okt 2026 — Stage 1/2/3: fixtures via het inzetvenster, competitiepoort, bronprobe.

Gelijk aan `ra_oct02_stage3.py` met de rundag een dag later. Eén toevoeging die uit de bevinding
van 2 oktober volgt: de **FA Cup staat in geen enkele Fotmob-daglijst** terwijl BetExplorer er
39 duels met aftrap op 3 oktober voor gaf. Die competitie krijgt hier daarom BetExplorer als
fixturebron in plaats van Fotmob, zodat ze niet stil langs de competitiepoort (Stage 2) verdwijnt.
"""
import json
from datetime import date
from scripts import fotmob, understat, betexplorer
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 10, 7)
CARRY = False

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
 "FA Cup (ENG)":            ("FA Cup", "ENG", (), 47, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/england/fa-cup/", None, None),
 "League Cup (ENG)":        ("EFL Cup", "ENG", ("League Cup", "Carabao Cup"), 47,
                            "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/england/efl-cup/",
                            "soccer_england_efl_cup", None),
 "Coppa Italia (ITA)":      ("Coppa Italia", "ITA", (), 55, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/italy/coppa-italia/",
                            "soccer_italy_coppa_italia", None),
 "KNVB Beker (NED)":        ("KNVB Beker", "NED", (), 57, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/netherlands/knvb-beker/", None, None),
 "DFB Pokal (GER)":         ("DFB Pokal", "GER", (), 54, "2025/2026", "2026/2027",
                            "https://www.betexplorer.com/football/germany/dfb-pokal/",
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
    print(f"{name:30s} {len(ms)} wedstrijd(en)")

print("\n--- alle wedstrijden in het venster (Fotmob) ---")
n = 0
for name, v in out.items():
    for m in v["matches"]:
        n += 1
        print(f"  {m['kickoff_nl']} NL  {name:28s} {m['home']} - {m['away']}"
              f"  (daglijst {m['source_day']}, speelbaar={m['playable']})")
if not n:
    print("  (geen)")

# 4. TWEEDE FIXTUREBRON: BetExplorer per competitie — dit is de bron die op 2 oktober de
#    39 FA Cup-duels van vandaag vond die in geen Fotmob-daglijst staan.
print("\n--- BetExplorer, tweede fixturebron ---")
stamp = DAY.strftime("%d.%m.")
bx_out = {}
for name, (fm, cc, al, pid, s_prev, s_cur, bx, key, us) in LEAGUES.items():
    if not bx:
        bx_out[name] = {"url": None, "skipped": "geen URL"}
        continue
    try:
        fx = betexplorer.fetch_league_fixtures(bx)
        times = sorted({f.when for f in fx if f.when})
        today = [f for f in fx if f.is_today or (f.when or "").startswith(stamp)]
        bx_out[name] = {"n": len(fx), "vandaag": len(today), "eerste": times[:3],
                        "duels_vandaag": [{"home": f.home, "away": f.away, "when": f.when,
                                           "odds": getattr(f, "odds", None)} for f in today]}
        print(f"{name:28s} {len(fx):3d} fixtures, vandaag {len(today):3d}, eerstvolgende {times[:2]}")
    except Exception as e:
        bx_out[name] = {"error": f"{type(e).__name__}: {e}"}
        print(f"{name:28s} FOUT {type(e).__name__}: {e}")

json.dump({"day": DAY.isoformat(), "carry_over": CARRY, "ids": ids, "id_source": id_source,
           "fixtures": out, "betexplorer": bx_out},
          open("tmp-run/ra_oct07_stage3.json", "w"), ensure_ascii=False, indent=1)
print("\nactief volgens Fotmob:", [k for k, v in out.items() if v["status"] == "?"])
print("totaal Fotmob-wedstrijden in het venster:", sum(len(v["matches"]) for v in out.values()))
print("competities met BetExplorer-duels vandaag:",
      {k: v["vandaag"] for k, v in bx_out.items() if v.get("vandaag")})
