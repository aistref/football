"""End-to-end controle: de productiemodule op de zes Champions League-duels van 8 sep 2026.

Loopt via `interleague.convert` -> `model.analyze_match` (dus door `team_strength` heen, inclusief
de terugrekening van `_deshrink`) en legt het resultaat naast de de-vigde marktkans. Dat laatste is
CONTROLEREN, geen fitten: er is geen marktprijs in de meting gegaan (§2).
"""
import json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from il_fetch import LEAGUES, league_table, domestic_season as _ds
from scripts import calibration, interleague, oddsapi
from scripts.model import analyze_match, analyze_match_from_splits, combine_probs, robustness_check

DS = json.load(open("tmp-run/il_dataset.json"))
available = DS["available"]
LIVE = {}
for cc, (lid, _n) in LEAGUES.items():
    season = _ds(cc, "2026/2027", available.get(cc) or [])
    if season and (tbl := league_table(lid, season)):
        LIVE[cc] = (season, tbl)

UCL = [m for m in json.load(open("tmp-run/ra8_cands.json"))
       if m["competition"] == "UEFA Champions League"]
odds_raw = json.load(open("tmp-run/ra8_odds.json"))["raw"]["h2h"].get("UEFA Champions League") or []


def domestic(team_id):
    for cc, (season, tbl) in LIVE.items():
        if team_id in tbl["teams"]:
            return cc, season, tbl
    return None, None, None


def market(home, away):
    for ev in odds_raw:
        h_ok = home.split()[0].lower() in ev["home_team"].lower() or ev["home_team"].split()[0].lower() in home.lower()
        a_ok = away.split()[0].lower() in ev["away_team"].lower() or ev["away_team"].split()[0].lower() in away.lower()
        if h_ok and a_ok:
            best, got = oddsapi.best_by_line(ev, "h2h"), {}
            for (outcome, _), (price, _book) in best.items():
                if outcome.lower() in ("draw", "gelijkspel"):
                    got["X"] = price
                elif outcome.lower() in ev["home_team"].lower():
                    got["1"] = price
                else:
                    got["2"] = price
            if len(got) == 3:
                return calibration.devig([got["1"], got["X"], got["2"]])
    return None


lg = interleague.reference_league()
print(f"referentie: thuis {lg.home_goals_per_match:.3f} / uit {lg.away_goals_per_match:.3f}\n")
print(f"{'wedstrijd':34s} {'comp':9s} {'tier':6s} | {'xG-methode 1/X/2':24s} | {'splits 1/X/2':24s} | {'markt':24s}")
print("-" * 132)
for m in UCL:
    cc_h, s_h, th = domestic(str(m["home_id"]))
    cc_a, s_a, ta = domestic(str(m["away_id"]))
    name = f"{m['home']} – {m['away']}"
    if not cc_h or not cc_a:
        print(f"{name:34s} geen binnenlandse stand"); continue
    if not (interleague.covered(cc_h) and interleague.covered(cc_a)):
        print(f"{name:34s} {cc_h}/{cc_a:5s} NONE   | geen gemeten factor voor "
              f"{cc_h if not interleague.covered(cc_h) else cc_a}")
        continue
    rh, ra = th["teams"][str(m["home_id"])], ta["teams"][str(m["away_id"])]
    ch = interleague.convert(cc_h, rh["gf"], rh["ga"], rh["played"],
                             th["goals_per_team_per_match"],
                             home=rh.get("home"), away=rh.get("away"))
    ca = interleague.convert(cc_a, ra["gf"], ra["ga"], ra["played"],
                             ta["goals_per_team_per_match"],
                             home=ra.get("home"), away=ra.get("away"))
    tier = "LIGHT" if (ch.in_range and ca.in_range) else "NONE"
    p = analyze_match(ch.stats, ca.stats, lg)
    ps = (analyze_match_from_splits(ch.splits, ca.splits, league=lg)
          if ch.splits and ca.splits else None)
    mk = market(m["home"], m["away"])
    f = lambda t: "  ".join(f"{x:5.1%}" for x in t)
    print(f"{name:34s} {cc_h}/{cc_a:5s} {tier:6s} | {f((p.home, p.draw, p.away)):24s} | "
          f"{f((ps.home, ps.draw, ps.away)) if ps else 'geen splits':24s} | {f(mk) if mk else '-':24s}")
    if not ch.in_range:
        print(f"     thuis buiten bereik: {ch.note}")
    if not ca.in_range:
        print(f"     uit buiten bereik:   {ca.note}")

print("\nvoorbeeldnotitie zoals hij in data/run-state/ komt:")
rh = LIVE["ESP"][1]["teams"][str(UCL[-1]["home_id"])]
print("  " + interleague.convert("ESP", rh["gf"], rh["ga"], rh["played"],
                                 LIVE["ESP"][1]["goals_per_team_per_match"]).note)
