"""Tweede poging, nu op EEN homogene populatie — en dat verschil is de kern.

De eerste poging (`grid_fit.py`) splitste de 1717 duels 50/50 op datum. Die scheiding liep op
2026-09-20, en dat is bijna exact de dag waarop `DEFAULT_SHRINK` van 0.80 naar 1.00 ging (§6e).
De "fit-helft" bestond dus uit lambdas van het ENE model en de "toets-helft" uit lambdas van het
ANDERE. Een correctie fitten op de ene instelling en toetsen op de andere is geen
uit-steekproefcontrole maar een vergelijking van twee modellen; `scripts/margins.py` waarschuwt
in zijn eigen kop precies hiervoor.

Daarom hier alles op de **914 duels met lambdas van ná 2026-09-20**, en twee onafhankelijke
splitsingen:

* **op tijd** — eerste helft fitten, tweede helft toetsen. Dat is de eerlijke test (hij ziet geen
  enkele uitslag uit de toetshelft), maar hij is gevoelig voor kalendereffecten in een venster van
  vijf weken.
* **om en om** — even en oneven duels. Die heeft geen kalendereffect maar is iets optimistischer,
  omdat beide helften dezelfde dagen bevatten.

Een kandidaat die alleen op één van de twee wint, heeft niets bewezen.

KANDIDATEN. Alle vijf werken op het grid en laten de twee lambdas ongemoeid, op `scale` na:

| kandidaat | parameter | wat het doet |
|---|---|---|
| `rho`    | rho          | alleen 0-0, 0-1, 1-0, 1-1 (Dixon-Coles) |
| `scale`  | s            | beide lambdas x s — raakt het GEMIDDELDE |
| `shift`  | a            | tilt op de anti-diagonaal, alleen schuiven |
| `narrow` | b            | tilt op de anti-diagonaal, alleen knijpen |
| `both`   | a, b         | schuiven en knijpen |
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import model

MAXG = model.MAX_GOALS
TMAX = 2 * MAXG
ROWS = sorted(json.loads(Path("tmp-run/grid_data.json").read_text()),
              key=lambda r: (r["date"], r["match"]))
POST = [r for r in ROWS if r["date"] >= "2026-09-20"]


def totals_vec(grid):
    v = [0.0] * (TMAX + 1)
    for i, row in enumerate(grid):
        for j, p in enumerate(row):
            v[i + j] += p
    return v


def prep(rows, rho=model.DEFAULT_RHO, scale=1.0):
    out = []
    for r in rows:
        lh, la = r["lam"][0] * scale, r["lam"][1] * scale
        g = model.score_grid(lh, la, rho=rho)
        out.append({"mu": lh + la, "tv": totals_vec(g), "t": r["hg"] + r["ag"],
                    "pe": g[r["hg"]][r["ag"]] if (r["hg"] <= MAXG and r["ag"] <= MAXG) else 1e-12})
    return out


def tilt_vec(p, a, b):
    mu, tv = p["mu"], p["tv"]
    out = [0.0] * (TMAX + 1)
    z = 0.0
    for t in range(TMAX + 1):
        if tv[t] <= 0.0:
            continue
        d = t - mu
        v = tv[t] * math.exp(a * d + b * d * d)
        out[t] = v
        z += v
    return [v / z for v in out], z


def ll(prepped, a=0.0, b=0.0):
    s = 0.0
    for p in prepped:
        tv, _ = tilt_vec(p, a, b)
        s -= math.log(max(tv[p["t"]] if p["t"] <= TMAX else 1e-12, 1e-12))
    return s / len(prepped)


def under_cal(prepped, line, a=0.0, b=0.0):
    pred = act = 0.0
    for p in prepped:
        tv, _ = tilt_vec(p, a, b)
        pred += sum(tv[k] for k in range(TMAX + 1) if k < line)
        act += 1.0 if p["t"] < line else 0.0
    n = len(prepped)
    return 100 * pred / n, 100 * act / n


def hist(prepped, a=0.0, b=0.0):
    n = len(prepped)
    pred = [0.0] * 11
    act = [0] * 11
    for p in prepped:
        tv, _ = tilt_vec(p, a, b)
        for k in range(11):
            pred[k] += tv[k]
        act[min(p["t"], 10)] += 1
    return [100 * x / n for x in pred], [100 * x / n for x in act]


def show_hist(prepped, label, a=0.0, b=0.0):
    pred, act = hist(prepped, a, b)
    print(f"  {label}")
    print("    totaal  voorspeld  werkelijk  verschil      z")
    for k in range(10):
        n = len(prepped)
        p = pred[k] / 100
        se = math.sqrt(max(p * (1 - p), 1e-9) / n) * 100
        d = act[k] - pred[k]
        print(f"    {k:>6}   {pred[k]:7.2f}%  {act[k]:7.2f}%  {d:+7.2f} pp  {d/se:+5.2f}")


def fit1(prepped, kind, lo, hi, step):
    best = (1e9, None)
    x = lo
    while x <= hi + 1e-12:
        if kind == "shift":
            v = ll(prepped, a=x)
        elif kind == "narrow":
            v = ll(prepped, b=x)
        if v < best[0]:
            best = (v, x)
        x += step
    return best


def fit_both(prepped):
    best = (1e9, 0.0, 0.0)
    for ai in range(-40, 41, 2):
        for bi in range(-300, 101, 5):
            a, b = ai / 1000, bi / 10000
            v = ll(prepped, a, b)
            if v < best[0]:
                best = (v, a, b)
    return best


def main():
    print(f"POPULATIE: {len(POST)} duels met lambdas van ná de shrink-overstap "
          f"({POST[0]['date']} t/m {POST[-1]['date']})")
    print(f"(de 803 duels van vóór 2026-09-20 zijn weggelaten — andere modelinstelling)\n")

    P = prep(POST)
    base = ll(P)
    print("=" * 80)
    print("DE DIAGNOSE VAN §6g OP DEZE POPULATIE")
    print("=" * 80)
    show_hist(P, f"huidig grid (rho = {model.DEFAULT_RHO}), log loss totaal {base:.5f}")
    print()
    for line in (2.5, 3.5):
        p, a = under_cal(P, line)
        n = len(P)
        se = math.sqrt((a / 100) * (1 - a / 100) / n) * 100
        print(f"  P(Under {line}): voorspeld {p:5.2f}%  werkelijk {a:5.2f}%  "
              f"{a-p:+.2f} pp  (z = {(a-p)/se:+.2f})")
    mu = sum(p["mu"] for p in P) / len(P)
    mt = sum(p["t"] for p in P) / len(P)
    print(f"\n  gemiddeld totaal: voorspeld {mu:.3f}  werkelijk {mt:.3f}  "
          f"({mt-mu:+.3f} per duel)")

    print("\n" + "=" * 80)
    print("KANDIDATEN, IN-STEEKPROEF OP DE HELE POPULATIE (914)")
    print("=" * 80)
    rho_best = min(((ll(prep(POST, rho=r)), r) for r in [x / 100 for x in range(-20, 21)]),
                   key=lambda t: t[0])
    print(f"  rho      beste {rho_best[1]:+.2f}  log loss {rho_best[0]:.5f}  "
          f"winst {base-rho_best[0]:+.5f}")
    sc_best = min(((ll(prep(POST, scale=s)), s) for s in [1 + x / 1000 for x in range(-40, 41, 2)]),
                  key=lambda t: t[0])
    print(f"  scale    beste {sc_best[1]:.3f}  log loss {sc_best[0]:.5f}  "
          f"winst {base-sc_best[0]:+.5f}")
    sh = fit1(P, "shift", -0.08, 0.08, 0.002)
    print(f"  shift    beste a={sh[1]:+.4f}  log loss {sh[0]:.5f}  winst {base-sh[0]:+.5f}")
    na = fit1(P, "narrow", -0.04, 0.01, 0.0005)
    print(f"  narrow   beste b={na[1]:+.5f}  log loss {na[0]:.5f}  winst {base-na[0]:+.5f}")
    bo = fit_both(P)
    print(f"  both     beste a={bo[1]:+.4f} b={bo[2]:+.5f}  log loss {bo[0]:.5f}  "
          f"winst {base-bo[0]:+.5f}")

    for naam, idx in (("OP TIJD (eerste helft fitten, tweede toetsen)",
                       (list(range(len(POST) // 2)), list(range(len(POST) // 2, len(POST))))),
                      ("OM EN OM (even fitten, oneven toetsen)",
                       (list(range(0, len(POST), 2)), list(range(1, len(POST), 2))))):
        tr_i, te_i = idx
        tr_rows = [POST[i] for i in tr_i]
        te_rows = [POST[i] for i in te_i]
        TR, TE = prep(tr_rows), prep(te_rows)
        b0 = ll(TE)
        print("\n" + "=" * 80)
        print(f"UIT-STEEKPROEF — {naam}")
        print("=" * 80)
        print(f"  fit {len(TR)} duels, toets {len(TE)} duels")
        r_tr = min(((ll(prep(tr_rows, rho=r)), r) for r in [x / 100 for x in range(-20, 21)]),
                   key=lambda t: t[0])[1]
        s_tr = min(((ll(prep(tr_rows, scale=s)), s)
                    for s in [1 + x / 1000 for x in range(-40, 41, 2)]), key=lambda t: t[0])[1]
        a_tr = fit1(TR, "shift", -0.08, 0.08, 0.002)[1]
        b_tr = fit1(TR, "narrow", -0.04, 0.01, 0.0005)[1]
        _, ab_a, ab_b = fit_both(TR)
        print(f"  gefit: rho={r_tr:+.2f}  scale={s_tr:.3f}  shift a={a_tr:+.4f}  "
              f"narrow b={b_tr:+.5f}  both a={ab_a:+.4f} b={ab_b:+.5f}")
        print(f"\n  op de TOETSHELFT (log loss totaal, POSITIEF = beter dan het huidige grid):")
        print(f"    huidig grid   {b0:.5f}")
        for lab, v in (("rho", ll(prep(te_rows, rho=r_tr))),
                       ("scale", ll(prep(te_rows, scale=s_tr))),
                       ("shift", ll(TE, a=a_tr)),
                       ("narrow", ll(TE, b=b_tr)),
                       ("both", ll(TE, ab_a, ab_b))):
            print(f"    {lab:12s}  {v:.5f}   winst {b0-v:+.5f}")
        for line in (2.5, 3.5):
            p0, ac = under_cal(TE, line)
            p1, _ = under_cal(TE, line, ab_a, ab_b)
            p2, _ = under_cal(TE, line, 0.0, b_tr)
            print(f"    P(Under {line}) toets: huidig {p0:5.2f}%  both {p1:5.2f}%  "
                  f"narrow {p2:5.2f}%  werkelijk {ac:5.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
