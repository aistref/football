"""Twee controles op de blend-meting: significantie, en of hij standhoudt op een ánder seizoen.

De keuze van k=16 is op 2025/2026 gemaakt. Precies dezelfde fout als bij EDGE_THRESHOLD_FULL
(§0: "dit is in-sample gekozen en dat is een echt bezwaar"). Daarom hier:

  1. Gepaarde toets op 2025/2026: per wedstrijd het verschil in Brier tussen "alleen vorig
     seizoen" en k=16, met standaardfout. Gepaard, want beide voorspellen dezelfde wedstrijden.
  2. Uit-steekproef: dezelfde k=16 op testseizoen 2024/2025 met prior 2023/2024 — een seizoen
     dat bij het kiezen van k geen enkele rol speelde.
"""
import json
import math
import sys

sys.path.insert(0, ".")
from scripts import understat
from scripts.model import LeagueContext, TeamStats, analyze_match

LEAGUES = ["EPL", "La_liga", "Bundesliga", "Serie_A", "Ligue_1"]
K = 16
SHRINK = 0.8


def team_totals(data):
    return {t["title"]: (sum(m["xG"] for m in t["history"]),
                         sum(m["xGA"] for m in t["history"]), len(t["history"]))
            for t in data["teams"].values()}


def league_base(data):
    hg = ag = n = txg = tn = 0
    for t in data["teams"].values():
        for m in t["history"]:
            txg += m["xG"]; tn += 1
            if m["h_a"] == "h":
                hg += m["scored"]; ag += m["missed"]; n += 1
    return LeagueContext(hg / n, ag / n, txg / tn)


def blend(cur_xg, cur_xga, n_cur, pr_xg, pr_xga, k):
    if k is None or n_cur == 0:
        return pr_xg, pr_xga
    w = n_cur / (n_cur + k)
    return w * (cur_xg / n_cur) + (1 - w) * pr_xg, w * (cur_xga / n_cur) + (1 - w) * pr_xga


def run(prior_season, test_season, label):
    diffs, br_prior, br_blend = [], [], []
    buckets = {}
    for code in LEAGUES:
        prior = understat.fetch_league(code, understat.season_code(prior_season))
        test = understat.fetch_league(code, understat.season_code(test_season))
        pt, base = team_totals(prior), league_base(prior)
        hist = {t["title"]: sorted(t["history"], key=lambda m: m["date"])
                for t in test["teams"].values()}
        fixtures = []
        for title, ms in hist.items():
            for m in ms:
                if m["h_a"] != "h":
                    continue
                opp = next((o for o, oms in hist.items() if o != title
                            and any(x["date"] == m["date"] and x["h_a"] == "a" for x in oms)), None)
                if opp:
                    fixtures.append((m["date"], title, opp, m["scored"], m["missed"]))
        fixtures.sort()
        state = {t: [0.0, 0.0, 0] for t in hist}
        for datum, home, away, gh, ga in fixtures:
            if home in pt and away in pt:
                ph, pa = pt[home], pt[away]
                uit = 0 if gh > ga else (1 if gh == ga else 2)
                scores = []
                for k in (None, K):
                    hx, hxa = blend(*state[home][:2], state[home][2], ph[0] / ph[2], ph[1] / ph[2], k)
                    ax, axa = blend(*state[away][:2], state[away][2], pa[0] / pa[2], pa[1] / pa[2], k)
                    p = analyze_match(TeamStats(hx, hxa, 1), TeamStats(ax, axa, 1), base, shrink=SHRINK)
                    pr = [p.home, p.draw, p.away]
                    scores.append(sum((pr[i] - (1 if i == uit else 0)) ** 2 for i in range(3)))
                br_prior.append(scores[0]); br_blend.append(scores[1])
                diffs.append(scores[0] - scores[1])          # positief = blend beter
                md = min(state[home][2], state[away][2])
                bk = "1-5" if md < 5 else ("6-12" if md < 12 else ("13-24" if md < 24 else "25+"))
                b = buckets.setdefault(bk, {"p": 0.0, "b": 0.0, "n": 0})
                b["p"] += scores[0]; b["b"] += scores[1]; b["n"] += 1
            hm = next(m for m in hist[home] if m["date"] == datum and m["h_a"] == "h")
            am = next(m for m in hist[away] if m["date"] == datum and m["h_a"] == "a")
            state[home][0] += hm["xG"]; state[home][1] += hm["xGA"]; state[home][2] += 1
            state[away][0] += am["xG"]; state[away][1] += am["xGA"]; state[away][2] += 1

    n = len(diffs)
    mean = sum(diffs) / n
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(var / n)
    t = mean / se if se else 0.0
    beter = sum(1 for d in diffs if d > 0)
    print(f"\n=== {label}: prior {prior_season} -> test {test_season} ===")
    print(f"  wedstrijden            {n}")
    print(f"  Brier alleen vorig     {sum(br_prior)/n:.5f}")
    print(f"  Brier met blend k={K}   {sum(br_blend)/n:.5f}")
    print(f"  gemiddeld verschil     {mean:+.5f}  (positief = blend beter)")
    print(f"  standaardfout          {se:.5f}   t = {t:+.2f}")
    print(f"  blend beter in         {beter}/{n} = {100*beter/n:.1f}% van de wedstrijden")
    print(f"  {'speeldagen':>12} {'alleen vorig':>13} {'blend':>9} {'winst':>9} {'n':>6}")
    for bk in ("1-5", "6-12", "13-24", "25+"):
        v = buckets.get(bk)
        if v:
            print(f"  {bk:>12} {v['p']/v['n']:>13.5f} {v['b']/v['n']:>9.5f} "
                  f"{(v['p']-v['b'])/v['n']:>+9.5f} {v['n']:>6}")
    return {"label": label, "prior": prior_season, "test": test_season, "n": n,
            "brier_prior": sum(br_prior)/n, "brier_blend": sum(br_blend)/n,
            "mean_diff": mean, "se": se, "t": t, "beter_pct": 100*beter/n}


out = [run("2024/2025", "2025/2026", "IN-STEEKPROEF (waar k op gekozen is)"),
       run("2023/2024", "2024/2025", "UIT-STEEKPROEF (speelde geen rol bij de keuze)")]
json.dump(out, open("tmp-run/backtest_verify.json", "w"), indent=1)
