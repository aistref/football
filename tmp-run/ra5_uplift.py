"""Controle op de vroeg-seizoenscorrectie (§3, Stage 5): meten tegen de markt, niet fitten.

Vergelijkt P(Over 2.5) van `my_prob` (het gemiddelde van beide methodes) met de de-vigde
marktkans op de 2.5-lijn, één keer met en één keer zonder de correctie. Dat is controleren of
de correctie doet wat ze hoort te doen — de correctie zelf komt uitsluitend uit xG-waarnemingen.
"""
import json, statistics as S, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, oddsapi
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, early_season_uplift, blend_seasons)
from ra_names import resolve, best_pair

res = json.load(open("tmp-run/ra5_results.json"))
odds = json.load(open("tmp-run/ra5_odds.json"))
s3 = json.load(open("tmp-run/ra5_stage3.json"))
cands = {c["match_id"]: c for c in json.load(open("tmp-run/ra5_ctx.json"))}
FACTOR = res["vroeg_seizoen"]["factor"]

cache = {}
def league_ctx(comp, pid, season, season_cur):
    if comp not in cache:
        st = fotmob.fetch_league_stats(pid, season)
        base = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                             away_goals_per_match=st["away_goals_per_match"],
                             avg_xg_per_match=st["avg_xg_per_match"])
        try:
            cur = fotmob.fetch_league_stats(pid, season_cur)["teams"] if season_cur else {}
        except Exception:
            cur = {}
        cache[comp] = (base, scale_level(base, FACTOR), st["teams"], cur)
    return cache[comp]

pre, post = [], []
for m in res["matches"]:
    if not m.get("candidates_evaluated"):
        continue
    c = cands[m["match_id"]]
    if not c["table_home"] or not c["table_away"]:
        continue                      # omgerekende ploeg: geen tabelrij om mee te herrekenen
    ev = None
    evs = (odds["raw"].get("totals") or {}).get(c["competition"]) or []
    for e in evs:
        if resolve(c["home"], {e["home_team"]: 1}) and resolve(c["away"], {e["away_team"]: 1}):
            ev = e; break
    if ev is None:
        ev = best_pair(c["home"], c["away"], evs, lambda e: e["home_team"], lambda e: e["away_team"])
    if ev is None:
        continue
    pair = {}
    for (outcome, line), (o, _book) in oddsapi.best_by_line(ev, "totals").items():
        if line is not None and abs(float(line) - 2.5) < 1e-9:
            pair[outcome.lower()[:1]] = o
    if "o" not in pair or "u" not in pair:
        continue
    market = (1 / pair["o"]) / ((1 / pair["o"]) + (1 / pair["u"]))

    base, scaled, teams, cur_teams = league_ctx(c["competition"], c["primaryId"], c["season"],
                                                c.get("season_cur"))
    def side(name, key):
        r = teams[key]
        prior = TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"])
        ck = resolve(name, cur_teams) if cur_teams else None
        cur = None
        if ck and cur_teams[ck].get("mp") and "xg" in cur_teams[ck]:
            cr = cur_teams[ck]
            cur = TeamStats(xg=cr["xg"], xga=cr["xga"], matches_played=cr["mp"])
        return blend_seasons(prior, cur), splits_from_fotmob(r)
    hs, sph = side(c["home"], c["table_home"])
    as_, spa = side(c["away"], c["table_away"])
    for lg, acc in ((base, pre), (scaled, post)):
        px = analyze_match(hs, as_, lg)
        ps = analyze_match_from_splits(sph, spa, league=lg)
        acc.append(((px.over_2_5 + ps.over_2_5) / 2 - market) * 100)

print(f"P(Over 2.5) t.o.v. de de-vigde marktkans, {len(pre)} wedstrijden")
print(f"  zonder correctie      : gemiddelde afwijking {S.mean(pre):+.2f} pp, "
      f"gem. absolute fout {S.mean(map(abs, pre)):.2f} pp")
print(f"  met correctie x{FACTOR:.4f} : gemiddelde afwijking {S.mean(post):+.2f} pp, "
      f"gem. absolute fout {S.mean(map(abs, post)):.2f} pp")
json.dump({"n": len(pre), "factor": FACTOR,
           "zonder": {"bias": S.mean(pre), "mae": S.mean(map(abs, pre))},
           "met": {"bias": S.mean(post), "mae": S.mean(map(abs, post))}},
          open("tmp-run/ra5_uplift.json", "w"), indent=1)
