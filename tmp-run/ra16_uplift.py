"""Controle die §3 Stage 5 voorschrijft: de gemeten afwijking vóór en ná de vroeg-seizoenscorrectie.

Meet P(Over 2.5) tegen de **de-vigde marktkans** over de duels waar beide kanten van de 2.5-lijn
een prijs hebben. Dat is een vergelijking mét de markt en dus uitsluitend een **diagnose** (§1d,
§6e): de correctie mag hier niet op worden afgeregeld.

Twee verschillen met de versie van 12 sep, allebei om hem met de analyse van vandaag te laten
kloppen in plaats van met die van augustus: de kans komt uit `combine_probs` (0.80/0.20, §1f) in
plaats van uit het ongewogen gemiddelde, en de teamsterktes komen uit `blend_seasons` — precies de
stap die volgens Bevinding 1 van 12 sep de dubbeltelling veroorzaakt.
"""
import json, statistics as S, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob, oddsapi
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           splits_from_fotmob, scale_level, blend_seasons, combine_probs,
                           early_season_uplift)
from ra_names import resolve, best_pair

s3 = json.load(open("tmp-run/ra16_stage3.json"))
odds = json.load(open("tmp-run/ra16_odds.json"))
cands = json.load(open("tmp-run/ra16_ctx.json"))
stats_meta = s3["stats"]

obs = []
for comp, s in stats_meta.items():
    p, c = s["prev"], s["cur"]
    if p.get("has_xg") and c.get("has_xg") and p.get("avg_xg") and c.get("avg_xg") and c.get("played"):
        obs.append((p["avg_xg"], c["avg_xg"], c["played"]))
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)

cache = {}
def ctx_for(comp, pid, s_prev, s_cur):
    if comp not in cache:
        st = fotmob.fetch_league_stats(pid, s_prev)
        base = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                             away_goals_per_match=st["away_goals_per_match"],
                             avg_xg_per_match=st["avg_xg_per_match"])
        cur = {}
        try:
            cur = fotmob.fetch_league_stats(pid, s_cur)["teams"]
        except Exception:
            pass
        cache[comp] = (base, scale_level(base, FACTOR), st["teams"], cur)
    return cache[comp]


def find_event(comp, kind, home, away):
    evs = (odds["raw"].get(kind) or {}).get(comp) or []
    for e in evs:
        if resolve(home, {e["home_team"]: 1}) and resolve(away, {e["away_team"]: 1}):
            return e
    return best_pair(home, away, evs, lambda e: e["home_team"], lambda e: e["away_team"])


pre, post = [], []
used = 0
for c in cands:
    if not (c["table_home"] and c["table_away"]):
        continue                       # omgerekende ploegen: geen stand, andere invoerweg
    ev = find_event(c["competition"], "totals", c["home"], c["away"])
    if not ev:
        continue
    pair = {}
    for (outcome, line), (o, _book) in oddsapi.best_by_line(ev, "totals").items():
        if line is not None and abs(float(line) - 2.5) < 1e-9:
            pair[outcome.lower()[:1]] = o
    if "o" not in pair or "u" not in pair:
        continue
    mkt = (1 / pair["o"]) / ((1 / pair["o"]) + (1 / pair["u"]))
    base, scaled, teams, cur = ctx_for(c["competition"], c["primaryId"], c["season"], c["season_cur"])

    def side(name, key):
        r = teams[key]
        prior = TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"])
        ck = resolve(name, cur) if cur else None
        now = None
        if ck:
            cr = cur[ck]
            if cr.get("mp") and "xg" in cr:
                now = TeamStats(xg=cr["xg"], xga=cr["xga"], matches_played=cr["mp"])
        return blend_seasons(prior, now), splits_from_fotmob(r)

    hs, sp_h = side(c["home"], c["table_home"])
    as_, sp_a = side(c["away"], c["table_away"])
    used += 1
    for lg, acc in ((base, pre), (scaled, post)):
        px = analyze_match(hs, as_, lg)
        ps = analyze_match_from_splits(sp_h, sp_a, league=lg)
        acc.append((combine_probs(px.over_2_5, ps.over_2_5) - mkt) * 100)

print(f"vroeg-seizoenscorrectie x{FACTOR:.4f} (gepoold {POOLED:.4f} over {TOTAL_MD} speeldagen, "
      f"{len(obs)} competities)")
print(f"P(Over 2.5) t.o.v. de de-vigde marktkans, {used} wedstrijden met een 2.5-lijn aan beide kanten")
print(f"  zonder correctie      : gemiddelde afwijking {S.mean(pre):+.2f} pp, "
      f"gem. absolute fout {S.mean(map(abs, pre)):.2f} pp")
print(f"  met correctie x{FACTOR:.4f}: gemiddelde afwijking {S.mean(post):+.2f} pp, "
      f"gem. absolute fout {S.mean(map(abs, post)):.2f} pp")
json.dump({"factor": FACTOR, "gepoold": POOLED, "speeldagen": TOTAL_MD, "n": used,
           "zonder": {"afwijking": S.mean(pre), "abs": S.mean(map(abs, pre))},
           "met": {"afwijking": S.mean(post), "abs": S.mean(map(abs, post))}},
          open("tmp-run/ra16_uplift.json", "w"), ensure_ascii=False, indent=1)
