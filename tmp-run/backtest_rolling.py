"""Is rollende xG beter dan het seizoensgemiddelde-tot-nu-toe? — gemeten op uitslagen.

De vraag (gebruiker, 5 sep 2026). §4 noemt "rolling xG-trend (laatste 5-8)" al vanaf het begin als
categorie-1-invoer, en `understat.rolling_xg` bestaat, maar niets gebruikt het: `blend_seasons`
mengt het vorige seizoen met het **vlakke gemiddelde** van alles wat er dit seizoen is gespeeld.
Een duel van speeldag 1 telt daarin even zwaar als dat van vorige week.

Deze test verandert precies één ding: hóe het tarief van het lopende seizoen wordt geschat. De
blend met het vorige seizoen blijft `n / (n + k)` met de gespeelde duels als n, en `k` staat op 8
(de waarde sinds 5 sep 2026).

    vlak      het gemiddelde over alle gespeelde duels          <- wat de routine nu doet
    laatste N alleen de laatste N duels
    exp h     exponentieel gewogen, halfwaardetijd h duels

Zelfde opzet als `backtest_blend.py`, en daarmee dezelfde waarborgen: chronologisch, elke wedstrijd
gescoord met alleen wat er vóór die wedstrijd bekend was, geen enkele bookmakerprijs (§2).
"""
import json
import math
import sys

sys.path.insert(0, ".")
from scripts import understat
from scripts.model import LeagueContext, TeamStats, analyze_match

LEAGUES = {"EPL": "Premier League", "La_liga": "La Liga", "Bundesliga": "Bundesliga",
           "Serie_A": "Serie A", "Ligue_1": "Ligue 1"}
SEIZOENEN = [("2024/2025", "2025/2026"), ("2023/2024", "2024/2025")]   # tweede = uit-steekproef
K = 8.0
SHRINK = 0.8

# (label, functie die uit een lijst [(xg, xga), ...] in speelvolgorde een (xg, xga)-tarief geeft)
def vlak(hist):
    n = len(hist)
    return sum(h[0] for h in hist) / n, sum(h[1] for h in hist) / n

def laatste(n_win):
    def f(hist):
        h = hist[-n_win:]
        return sum(x[0] for x in h) / len(h), sum(x[1] for x in h) / len(h)
    return f

def exponentieel(halfwaarde):
    def f(hist):
        lam = math.log(2) / halfwaarde
        gew = [math.exp(-lam * (len(hist) - 1 - i)) for i in range(len(hist))]
        tot = sum(gew)
        return (sum(g * h[0] for g, h in zip(gew, hist)) / tot,
                sum(g * h[1] for g, h in zip(gew, hist)) / tot)
    return f

METHODES = [("vlak (nu)", vlak), ("laatste 5", laatste(5)), ("laatste 8", laatste(8)),
            ("laatste 12", laatste(12)), ("exp h=4", exponentieel(4)),
            ("exp h=8", exponentieel(8)), ("exp h=12", exponentieel(12))]


def team_totals(data):
    out = {}
    for t in data["teams"].values():
        h = t["history"]
        out[t["title"]] = (sum(m["xG"] for m in h), sum(m["xGA"] for m in h), len(h))
    return out


def league_base(data):
    hg = ag = n = txg = tn = 0
    for t in data["teams"].values():
        for m in t["history"]:
            txg += m["xG"]; tn += 1
            if m["h_a"] == "h":
                hg += m["scored"]; ag += m["missed"]; n += 1
    return LeagueContext(home_goals_per_match=hg / n, away_goals_per_match=ag / n,
                         avg_xg_per_match=txg / tn)


for PRIOR, TEST in SEIZOENEN:
    print(f"\n=== testseizoen {TEST} (prior {PRIOR}) ===", flush=True)
    res = {lbl: {"brier": 0.0, "logloss": 0.0, "n": 0} for lbl, _ in METHODES}
    bucket = {lbl: {} for lbl, _ in METHODES}
    paren = {lbl: [] for lbl, _ in METHODES}      # per wedstrijd: Brier(vlak) - Brier(methode)

    for code, naam in LEAGUES.items():
        try:
            prior = understat.fetch_league(code, understat.season_code(PRIOR))
            test = understat.fetch_league(code, understat.season_code(TEST))
        except Exception as e:
            print(f"  {naam}: overgeslagen ({type(e).__name__})")
            continue
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

        gespeeld = {t: [] for t in hist}          # [(xg, xga), ...] in speelvolgorde
        for datum, home, away, gh, ga in fixtures:
            if home in pt and away in pt:
                uit = 0 if gh > ga else (1 if gh == ga else 2)
                ph_xg, ph_xga, ph_n = pt[home]
                pa_xg, pa_xga, pa_n = pt[away]
                briers = {}
                for lbl, fn in METHODES:
                    def tarief(team, prior_xg, prior_xga, prior_n):
                        h = gespeeld[team]
                        if not h:
                            return prior_xg / prior_n, prior_xga / prior_n
                        cx, ca = fn(h)
                        w = len(h) / (len(h) + K)
                        return (w * cx + (1 - w) * prior_xg / prior_n,
                                w * ca + (1 - w) * prior_xga / prior_n)
                    hx, hxa = tarief(home, ph_xg, ph_xga, ph_n)
                    ax, axa = tarief(away, pa_xg, pa_xga, pa_n)
                    p = analyze_match(TeamStats(xg=hx, xga=hxa, matches_played=1),
                                      TeamStats(xg=ax, xga=axa, matches_played=1),
                                      base, shrink=SHRINK)
                    probs = [p.home, p.draw, p.away]
                    b = sum((probs[i] - (1 if i == uit else 0)) ** 2 for i in range(3))
                    res[lbl]["brier"] += b
                    res[lbl]["logloss"] += -math.log(max(probs[uit], 1e-9))
                    res[lbl]["n"] += 1
                    md = min(len(gespeeld[home]), len(gespeeld[away]))
                    bak = "1-5" if md < 5 else ("6-12" if md < 12 else ("13-24" if md < 24 else "25+"))
                    d = bucket[lbl].setdefault(bak, {"brier": 0.0, "n": 0})
                    d["brier"] += b; d["n"] += 1
                    briers[lbl] = b
                for lbl, _ in METHODES:
                    paren[lbl].append(briers["vlak (nu)"] - briers[lbl])
            # pas ná het scoren bijwerken
            hm = next(m for m in hist[home] if m["date"] == datum and m["h_a"] == "h")
            am = next(m for m in hist[away] if m["date"] == datum and m["h_a"] == "a")
            gespeeld[home].append((hm["xG"], hm["xGA"]))
            gespeeld[away].append((am["xG"], am["xGA"]))
        print(f"  {naam:16s} klaar", flush=True)

    basis = res["vlak (nu)"]["brier"] / res["vlak (nu)"]["n"]
    print(f"\n{'methode':14s} {'n':>6s} {'Brier':>9s} {'verschil':>10s} {'log loss':>9s}")
    print("-" * 52)
    for lbl, _ in METHODES:
        r = res[lbl]
        if not r["n"]:
            continue
        br = r["brier"] / r["n"]
        merk = "  <-- huidig" if lbl == "vlak (nu)" else ""
        print(f"{lbl:14s} {r['n']:6d} {br:9.5f} {basis - br:+10.5f} "
              f"{r['logloss'] / r['n']:9.5f}{merk}")
    print("\n(positief verschil = beter dan wat de routine nu doet)")
    import statistics as ST
    print(f"\ngepaarde t-toets per wedstrijd tegen 'vlak' (positief = beter):")
    for lbl, _ in METHODES:
        v = paren[lbl]
        if lbl == "vlak (nu)" or len(v) < 5:
            continue
        sd = ST.stdev(v)
        t = ST.mean(v) / (sd / len(v) ** 0.5) if sd else float("nan")
        print(f"   {lbl:14s} gemiddeld {ST.mean(v):+.5f}   t = {t:+5.2f}")
    print(f"\nper speeldagbak, verschil met 'vlak':")
    kop = [b for b in ("1-5", "6-12", "13-24", "25+") if b in bucket["vlak (nu)"]]
    print("  " + "methode".ljust(14) + "".join(f"{b:>12s}" for b in kop))
    for lbl, _ in METHODES:
        if lbl == "vlak (nu)":
            continue
        rij = []
        for b in kop:
            v, w = bucket[lbl].get(b), bucket["vlak (nu)"].get(b)
            rij.append(f"{(w['brier']/w['n'] - v['brier']/v['n']):+12.5f}" if v and w else f"{'-':>12s}")
        print("  " + lbl.ljust(14) + "".join(rij))
    json.dump({"test": TEST, "rows": {l: res[l] for l, _ in METHODES}},
              open(f"tmp-run/backtest_rolling_{TEST.replace('/', '-')}.json", "w"), indent=1)
