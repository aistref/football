"""De inter-competitiemeting: fit + uit-steekproefcontrole.

MODEL. Voor een Europees duel tussen thuisploeg i (competitie A) en uitploeg j (competitie B):

    lambda_thuis = H * (att_i * A_A) * (dfn_j * D_B)
    lambda_uit   = W * (att_j * A_B) * (dfn_i * D_A)

`att_i` en `dfn_i` zijn de aanval- en verdedigingsverhouding van de ploeg t.o.v. het gemiddelde
van zijn EIGEN competitie in het vorige afgeronde seizoen — exact wat `model.team_strength`
uitrekent, inclusief dezelfde `shrink`. `A_L` en `D_L` zijn de twee onbekenden per competitie:
hoeveel een "gemiddelde ploeg uit competitie L" waard is op de Europese schaal. `H` en `W` zijn
het Europese thuis- en uitdoelpuntenniveau.

Dit is precies dezelfde vorm als `model.match_lambdas`, met per ploeg één extra factor. Daardoor
kan de uitkomst als een OMREKENING worden toegepast (zoals promotion.convert dat doet) en hoeft
er aan het model zelf niets te veranderen.

IDENTIFICEERBAARHEID. Twee vrijheidsgraden: A -> cA met D -> D/c laat beide lambda's ongemoeid,
en A -> cA met H,W -> H/c,W/c ook. Daarom wordt na elke iteratie het waarnemingsgewogen
meetkundig gemiddelde van A en van D op 1 gezet.

REGULARISATIE. Kleine competities hebben weinig Europese duels. De update krijgt daarom een
pseudo-waarneming die naar 1 trekt: A = (telller + PRIOR) / (noemer + PRIOR). PRIOR is in
"pseudo-doelpunten" en wordt UIT-STEEKPROEF gekozen, niet naar smaak.
"""
import json, math, sys
from collections import defaultdict
sys.path.insert(0, ".")
from scripts.model import score_grid, DEFAULT_RHO

SHRINK = 0.80          # zelfde waarde als model.DEFAULT_SHRINK — de productieketen gebruikt die
MAX_ITER = 400
TOL = 1e-10
FLOOR = 1e-4        # ondergrens op A en D, zodat log() bij prior=0 niet ontploft


def build_rows(ds: dict, shrink: float = SHRINK) -> list[dict]:
    """Eén rij per Europees duel waarvan BEIDE ploegen een binnenlandse stand hebben."""
    tables, team_league = ds["tables"], ds["team_league"]
    available = ds["available"]

    def domestic_season(cc: str, euro_season: str) -> str | None:
        start = int(euro_season[:4])
        av = available.get(cc) or []
        for cand in (f"{start - 1}/{start}", str(start - 1)):
            if cand in av:
                return cand
        return None

    season_pool: dict[str, list[str]] = {}
    for m in ds["matches"]:
        es = m["euro_season"]
        if es not in season_pool:
            season_pool[es] = sorted({s for s in (domestic_season(cc, es) for cc in ds["leagues"]) if s})

    def find(team_id: str, es: str):
        for s in season_pool[es]:
            cc = team_league.get(f"{team_id}|{s}")
            if cc:
                return cc, s
        return None, None

    rows, dropped = [], 0
    for m in ds["matches"]:
        es = m["euro_season"]
        cc_h, s_h = find(m["home_id"], es)
        cc_a, s_a = find(m["away_id"], es)
        if not cc_h or not cc_a:
            dropped += 1
            continue
        th = tables[f"{cc_h}|{s_h}"]
        ta = tables[f"{cc_a}|{s_a}"]
        rh = th["teams"][m["home_id"]]
        ra = ta["teams"][m["away_id"]]
        if not rh.get("played") or not ra.get("played"):
            dropped += 1
            continue
        gh, ga_ = th["goals_per_team_per_match"], ta["goals_per_team_per_match"]

        def strength(row, avg):
            att = 1 + shrink * ((row["gf"] / row["played"]) / avg - 1)
            dfn = 1 + shrink * ((row["ga"] / row["played"]) / avg - 1)
            return max(att, 0.05), max(dfn, 0.05)

        att_h, dfn_h = strength(rh, gh)
        att_a, dfn_a = strength(ra, ga_)
        rows.append({"season": es, "competition": m["competition"], "round": m.get("round"),
                     "reason": m.get("reason") or "?",
                     "cc_home": cc_h, "cc_away": cc_a,
                     "home": m["home"], "away": m["away"],
                     "att_home": att_h, "dfn_home": dfn_h,
                     "att_away": att_a, "dfn_away": dfn_a,
                     "hg": m["hg"], "ag": m["ag"],
                     "same_country": cc_h == cc_a})
    return rows, dropped


def fit(rows: list[dict], prior: float = 20.0, halflife: float | None = None) -> dict:
    """Poisson-MLE met multiplicatieve updates. Geeft {A, D, H, W, n_per_league}.

    `halflife` in seizoenen: elk seizoen ouder dan het nieuwste in `rows` telt met gewicht
    0.5 ** (leeftijd / halflife). `None` = alle seizoenen even zwaar. Bedoeld om te toetsen
    of de drift in de stabiliteitscontrole (NED zakt, FRA stijgt over 2021-2026) echte
    beweging is die je wilt volgen, of ruis die je juist wilt uitmiddelen.
    """
    newest = max(r["season"] for r in rows)
    def w_of(r):
        if halflife is None:
            return 1.0
        age = int(newest[:4]) - int(r["season"][:4])
        return 0.5 ** (age / halflife)
    for r in rows:
        r["_w"] = w_of(r)
    ccs = sorted({r["cc_home"] for r in rows} | {r["cc_away"] for r in rows})
    A = {c: 1.0 for c in ccs}
    D = {c: 1.0 for c in ccs}
    H = sum(r["hg"] for r in rows) / max(len(rows), 1)
    W = sum(r["ag"] for r in rows) / max(len(rows), 1)

    n_per = defaultdict(int)
    for r in rows:
        n_per[r["cc_home"]] += 1
        n_per[r["cc_away"]] += 1

    it = 0
    for it in range(1, MAX_ITER + 1):
        prev = (dict(A), dict(D), H, W)

        # H en W: totaal aantal doelpunten gedeeld door de som van de rest van het product
        den_h = sum(r["_w"] * r["att_home"] * A[r["cc_home"]] * r["dfn_away"] * D[r["cc_away"]] for r in rows)
        den_w = sum(r["_w"] * r["att_away"] * A[r["cc_away"]] * r["dfn_home"] * D[r["cc_home"]] for r in rows)
        H = sum(r["_w"] * r["hg"] for r in rows) / den_h if den_h else H
        W = sum(r["_w"] * r["ag"] for r in rows) / den_w if den_w else W

        # A_L: doelpunten GEMAAKT door ploegen uit L, tegen de rest van het product
        num_a, den_a = defaultdict(float), defaultdict(float)
        for r in rows:
            num_a[r["cc_home"]] += r["_w"] * r["hg"]
            den_a[r["cc_home"]] += r["_w"] * H * r["att_home"] * r["dfn_away"] * D[r["cc_away"]]
            num_a[r["cc_away"]] += r["_w"] * r["ag"]
            den_a[r["cc_away"]] += r["_w"] * W * r["att_away"] * r["dfn_home"] * D[r["cc_home"]]
        for c in ccs:
            # Ondergrens: zonder regularisatie kan een competitie waarvan de ploegen in Europa
            # nul keer scoorden op precies 0 uitkomen, en dan klapt het log-gemiddelde eruit.
            A[c] = max(FLOOR, (num_a[c] + prior) / (den_a[c] + prior)) if (den_a[c] + prior) else 1.0

        # D_L: doelpunten TEGEN ploegen uit L
        num_d, den_d = defaultdict(float), defaultdict(float)
        for r in rows:
            num_d[r["cc_away"]] += r["_w"] * r["hg"]
            den_d[r["cc_away"]] += r["_w"] * H * r["att_home"] * A[r["cc_home"]] * r["dfn_away"]
            num_d[r["cc_home"]] += r["_w"] * r["ag"]
            den_d[r["cc_home"]] += r["_w"] * W * r["att_away"] * A[r["cc_away"]] * r["dfn_home"]
        for c in ccs:
            D[c] = max(FLOOR, (num_d[c] + prior) / (den_d[c] + prior)) if (den_d[c] + prior) else 1.0

        # normaliseren: waarnemingsgewogen meetkundig gemiddelde van A en D op 1
        tot = sum(n_per[c] for c in ccs) or 1
        for M in (A, D):
            g = math.exp(sum(n_per[c] * math.log(M[c]) for c in ccs) / tot)
            for c in ccs:
                M[c] /= g

        delta = max(max(abs(A[c] - prev[0][c]) for c in ccs),
                    max(abs(D[c] - prev[1][c]) for c in ccs),
                    abs(H - prev[2]), abs(W - prev[3]))
        if delta < TOL:
            break
    return {"A": A, "D": D, "H": H, "W": W, "n_per_league": dict(n_per), "prior": prior,
            "halflife": halflife, "iterations": it}


def lambdas(r: dict, f: dict | None) -> tuple[float, float]:
    """Met `f=None`: het huidige model — geen competitiefactor, dus A=D=1 (de nulhypothese)."""
    A = (f or {}).get("A", {})
    D = (f or {}).get("D", {})
    a_h, d_h = A.get(r["cc_home"], 1.0), D.get(r["cc_home"], 1.0)
    a_a, d_a = A.get(r["cc_away"], 1.0), D.get(r["cc_away"], 1.0)
    H = (f or {}).get("H", 1.0)
    W = (f or {}).get("W", 1.0)
    return (H * r["att_home"] * a_h * r["dfn_away"] * d_a,
            W * r["att_away"] * a_a * r["dfn_home"] * d_h)


def evaluate(rows: list[dict], f: dict | None, baseline_hw: tuple[float, float] | None = None) -> dict:
    """Poisson-loglikelihood per doelpuntwaarneming én 1X2-Brier op de uitslag."""
    if f is None:
        H, W = baseline_hw
        f0 = {"A": {}, "D": {}, "H": H, "W": W}
    else:
        f0 = f
    ll, brier, n = 0.0, 0.0, 0
    for r in rows:
        lh, la = lambdas(r, f0)
        lh, la = max(lh, 1e-6), max(la, 1e-6)
        for goals, lam in ((r["hg"], lh), (r["ag"], la)):
            ll += goals * math.log(lam) - lam - math.lgamma(goals + 1)
        grid = score_grid(lh, la, DEFAULT_RHO)
        n_max = len(grid)
        p_home = sum(grid[i][j] for i in range(n_max) for j in range(n_max) if i > j)
        p_draw = sum(grid[i][i] for i in range(n_max))
        p_away = max(0.0, 1 - p_home - p_draw)
        actual = (1, 0, 0) if r["hg"] > r["ag"] else ((0, 1, 0) if r["hg"] == r["ag"] else (0, 0, 1))
        brier += sum((p - a) ** 2 for p, a in zip((p_home, p_draw, p_away), actual))
        n += 1
    return {"n": n, "loglik_per_goal_obs": ll / (2 * n), "brier": brier / n}


PRIORS = (0.0, 5.0, 10.0, 20.0, 40.0, 80.0, 160.0, 320.0)


def fold(cross: list[dict], test_season: str, priors=PRIORS) -> dict:
    """Fit op alles vóór `test_season`, evalueer op `test_season`. Geeft alle priors terug."""
    train = [r for r in cross if r["season"] < test_season]
    test = [r for r in cross if r["season"] == test_season]
    if not train or not test:
        return {}
    base = (sum(r["hg"] for r in train) / len(train), sum(r["ag"] for r in train) / len(train))
    out = {"n_train": len(train), "n_test": len(test),
           "baseline": evaluate(test, None, base), "per_prior": {}}
    for prior in priors:
        f = fit(train, prior=prior)
        out["per_prior"][prior] = {"eval": evaluate(test, f), "fit": f}
    return out


def main() -> int:
    ds = json.load(open("tmp-run/il_dataset.json"))
    rows, dropped = build_rows(ds)
    reasons = defaultdict(int)
    for m in ds["matches"]:
        reasons[m.get("reason") or "?"] += 1
    print(f"Europese wedstrijden met uitslag   : {len(ds['matches'])}")
    print(f"  reden-codes                      : {dict(sorted(reasons.items(), key=lambda kv: -kv[1]))}")
    print(f"  bruikbaar (beide ploegen bekend) : {len(rows)}  ({dropped} laten vallen)")

    # §6d: afrekenen op 90 minuten. `scoreStr` is de EINDstand, dus knock-outduels die in
    # verlenging of op strafschoppen zijn beslist geven een te hoge doelpuntenscore. Die gaan eruit.
    ft = [r for r in rows if r["reason"] == "FT"]
    print(f"  daarvan op FT (geen verlenging)  : {len(ft)}  ({len(rows) - len(ft)} met verlenging/strafschoppen)")
    cross = [r for r in ft if not r["same_country"]]
    print(f"  daarvan kruis-grens              : {len(cross)}")
    per_season = defaultdict(int)
    for r in cross:
        per_season[r["season"]] += 1
    print("  per seizoen                      :", dict(sorted(per_season.items())))
    json.dump(cross, open("tmp-run/il_rows.json", "w"))

    seasons = sorted({r["season"] for r in cross})
    final_season = seasons[-1]
    tune_seasons = [s for s in seasons[1:] if s != final_season]

    # 1. regularisatiesterkte kiezen op de EERDERE seizoenen, niet op het eindcijfer
    print(f"\n=== 1. prior kiezen op {tune_seasons} (rollende oorsprong) ===")
    agg = {p: 0.0 for p in PRIORS}
    n_tot = 0
    for ts in tune_seasons:
        fo = fold(cross, ts)
        if not fo:
            continue
        n_tot += fo["n_test"]
        line = f"  test {ts} (n={fo['n_test']:4d})  basis Brier {fo['baseline']['brier']:.5f} |"
        for p in PRIORS:
            d = fo["per_prior"][p]["eval"]["brier"] - fo["baseline"]["brier"]
            agg[p] += fo["per_prior"][p]["eval"]["brier"] * fo["n_test"]
            line += f"  {p:g}:{d:+.5f}"
        print(line)
    best_prior = min(agg, key=lambda p: agg[p])
    print(f"  -> gekozen prior: {best_prior:g}")

    # 2. eerlijk eindcijfer op het laatst gehouden seizoen, met die vaste prior
    print(f"\n=== 2. eindcijfer, uit-steekproef op {final_season} met prior {best_prior:g} ===")
    fo = fold(cross, final_season, priors=(best_prior,))
    b, m = fo["baseline"], fo["per_prior"][best_prior]["eval"]
    print(f"  fit op {fo['n_train']} duels, getest op {fo['n_test']}")
    print(f"    ZONDER competitiefactor : loglik {b['loglik_per_goal_obs']:+.5f}   Brier {b['brier']:.5f}")
    print(f"    MET  competitiefactor   : loglik {m['loglik_per_goal_obs']:+.5f}   Brier {m['brier']:.5f}")
    print(f"    verschil                : loglik {m['loglik_per_goal_obs'] - b['loglik_per_goal_obs']:+.5f}   "
          f"Brier {m['brier'] - b['brier']:+.5f}  ({'BETER' if m['brier'] < b['brier'] else 'SLECHTER'})")

    # 3. de fit op ALLE seizoenen — dat is wat de routine zou gebruiken
    print(f"\n=== 3. fit op alle {len(cross)} kruis-grensduels, prior {best_prior:g} ===")
    full = fit(cross, prior=best_prior)
    n_per = full["n_per_league"]
    print(f"  H (thuis) {full['H']:.3f}   W (uit) {full['W']:.3f}   iteraties {full['iterations']}")
    print(f"  {'cc':4s} {'A (aanval)':>11s} {'D (verdediging)':>16s} {'sterkte':>9s} {'duels':>6s}")
    order = sorted(full["A"], key=lambda c: -(full["A"][c] / full["D"][c]))
    for c in order:
        s_idx = full["A"][c] / full["D"][c]
        print(f"  {c:4s} {full['A'][c]:11.3f} {full['D'][c]:16.3f} {s_idx:9.3f} {n_per.get(c, 0):6d}")
    json.dump({"best_prior": best_prior, "full": full,
               "final": {"baseline": b, "model": m, "n_test": fo["n_test"], "season": final_season}},
              open("tmp-run/il_fitresult.json", "w"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
