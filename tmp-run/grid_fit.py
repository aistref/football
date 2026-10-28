"""Kandidaat-reparaties voor de vormfout in `score_grid`, gemeten op uitkomsten.

§6g meet dat het scoregrid de VORM van de totaalverdeling fout heeft terwijl het GEMIDDELDE
klopt: te weinig massa op 3, 4 en 5 doelpunten en te veel op 0, 2 en in de staart, waardoor
`P(Under 2.5)` ~2,2 pp en `P(Under 3/3.5)` ~1,7 pp te hoog staat. Dit script toetst kandidaten
tegen diezelfde uitslagen.

LET OP DE MAATSTAF, want de diagnose van §6g is een AGGREGAAT en dat is niet waarop je mag fitten.
Een gemiddelde voorspelde histogram kan afwijken terwijl elke wedstrijd apart goed gekalibreerd
is, en omgekeerd. De keuze valt daarom op **log loss per wedstrijd** over het werkelijke totaal
(en over de werkelijke exacte uitslag), met de aggregaathistogram ernaast als diagnose. Dat is
dezelfde discipline als §1f voor de 80/20-weging: kiezen op een score per waarneming, niet op een
plaatje.

UIT-STEEKPROEF is verplicht (§0 klaagt daar terecht over bij EDGE_THRESHOLD_FULL): de parameters
worden gefit op de eerste helft van de periode en getoetst op de tweede.

SNELHEID. De tilt werkt per ANTI-DIAGONAAL en hangt dus alleen van `i + j` af. Daarom is per
wedstrijd één keer de basis-totaalvector nodig (en de basiskans van de werkelijke uitslag); elke
kandidaatwaarde is daarna een herweging van die vector. Zonder die voorberekening bouwt het script
honderden keren 1717 grids en duurt het tientallen minuten.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import model

MAXG = model.MAX_GOALS
TMAX = 2 * MAXG


def totals_vec(grid):
    v = [0.0] * (TMAX + 1)
    for i, row in enumerate(grid):
        for j, p in enumerate(row):
            v[i + j] += p
    return v


def prep(rows, rho=model.DEFAULT_RHO):
    """Per wedstrijd: mu, basis-totaalvector, werkelijk totaal, basiskans van de exacte uitslag."""
    out = []
    for r in rows:
        lh, la = r["lam"]
        g = model.score_grid(lh, la, rho=rho)
        out.append({
            "mu": lh + la,
            "tv": totals_vec(g),
            "t": r["hg"] + r["ag"],
            "pe": g[r["hg"]][r["ag"]] if (r["hg"] <= MAXG and r["ag"] <= MAXG) else 1e-12,
            "date": r["date"],
        })
    return out


def tilt_vec(p, a, b):
    """De getilte totaalvector van één wedstrijd, plus de normalisatieconstante Z."""
    mu, tv = p["mu"], p["tv"]
    out = [0.0] * (TMAX + 1)
    z = 0.0
    for t in range(TMAX + 1):
        if tv[t] <= 0.0:
            continue
        d = t - mu
        w = math.exp(a * d + b * d * d)
        v = tv[t] * w
        out[t] = v
        z += v
    return [v / z for v in out], z


def evaluate(prepped, a=0.0, b=0.0):
    """log loss op het totaal en op de exacte uitslag, plus de aggregaathistogram."""
    ll_t = ll_e = 0.0
    n = len(prepped)
    pred = [0.0] * 16
    act = [0] * 16
    for p in prepped:
        tv, z = tilt_vec(p, a, b)
        ll_t -= math.log(max(tv[p["t"]] if p["t"] <= TMAX else 1e-12, 1e-12))
        d = p["t"] - p["mu"]
        w = math.exp(a * d + b * d * d)
        ll_e -= math.log(max(p["pe"] * w / z, 1e-12))
        for k in range(16):
            pred[k] += tv[k]
        act[min(p["t"], 15)] += 1
    return {"n": n, "ll_tot": ll_t / n, "ll_exact": ll_e / n,
            "pred": [100 * x / n for x in pred], "act": [100 * x / n for x in act]}


def under(prepped, line, a=0.0, b=0.0):
    pred = act = 0.0
    for p in prepped:
        tv, _ = tilt_vec(p, a, b)
        pred += sum(tv[k] for k in range(TMAX + 1) if k < line)
        act += 1.0 if p["t"] < line else 0.0
    return 100 * pred / len(prepped), 100 * act / len(prepped)


def fmt_hist(res):
    out = ["  totaal   voorspeld   werkelijk   verschil"]
    for k in range(0, 10):
        out.append(f"  {k:>6}    {res['pred'][k]:7.2f}%    {res['act'][k]:7.2f}%   "
                   f"{res['act'][k]-res['pred'][k]:+6.2f} pp")
    return "\n".join(out)


def fit(prepped, b_only=False):
    best = (1e9, 0.0, 0.0)
    arange = [0.0] if b_only else [x / 500 for x in range(-30, 31)]
    brange = [x / 10000 for x in range(-500, 201, 5)]
    for a in arange:
        for b in brange:
            ll = evaluate(prepped, a, b)["ll_tot"]
            if ll < best[0]:
                best = (ll, a, b)
    _, a0, b0 = best
    for a in ([0.0] if b_only else [a0 + x / 5000 for x in range(-6, 7)]):
        for b in [b0 + x / 100000 for x in range(-10, 11)]:
            ll = evaluate(prepped, a, b)["ll_tot"]
            if ll < best[0]:
                best = (ll, a, b)
    return best


def main():
    rows = sorted(json.loads(Path("tmp-run/grid_data.json").read_text()),
                  key=lambda r: (r["date"], r["match"]))
    print(f"{len(rows)} wedstrijden met lambdapaar en uitslag, "
          f"{rows[0]['date']} t/m {rows[-1]['date']}")
    print("voorbereiden (één grid per wedstrijd)...", flush=True)
    P = prep(rows)

    print("\n" + "=" * 78)
    print(f"BASISLIJN — het huidige grid (rho = {model.DEFAULT_RHO})")
    print("=" * 78)
    base = evaluate(P)
    print(f"  log loss op het totaal : {base['ll_tot']:.5f}")
    print(f"  log loss exacte uitslag: {base['ll_exact']:.5f}")
    print(fmt_hist(base))
    for line in (2.5, 3.0, 3.5):
        p, a = under(P, line)
        print(f"  P(Under {line}) voorspeld {p:5.2f}%  werkelijk {a:5.2f}%  {a-p:+.2f} pp")

    print("\n" + "=" * 78)
    print("KANDIDAAT 1 — rho opnieuw fitten (raakt alleen 0-0, 0-1, 1-0, 1-1)")
    print("=" * 78)
    best_rho = (1e9, None)
    for rr in [x / 100 for x in range(-20, 21, 1)]:
        ll = evaluate(prep(rows, rho=rr))["ll_tot"]
        if ll < best_rho[0]:
            best_rho = (ll, rr)
        if rr in (-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15):
            print(f"  rho = {rr:+.2f}  log loss totaal {ll:.5f}  "
                  f"({base['ll_tot']-ll:+.5f})")
    print(f"  -> beste rho {best_rho[1]:+.2f} met {best_rho[0]:.5f}, "
          f"winst {base['ll_tot']-best_rho[0]:+.5f}")

    print("\n" + "=" * 78)
    print("KANDIDAAT 2 — exponentiële tilt op de anti-diagonalen (= op het totaal)")
    print("=" * 78)
    ll, a, b = fit(P)
    print(f"  vrij (a, b)        : a = {a:+.4f}  b = {b:+.5f}  log loss {ll:.5f} "
          f"({base['ll_tot']-ll:+.5f})")
    llb, _, bb = fit(P, b_only=True)
    print(f"  a vastgezet op 0   : b = {bb:+.5f}  log loss {llb:.5f} "
          f"({base['ll_tot']-llb:+.5f})")
    print(f"  a draagt dus {ll-llb:+.5f} bij — §6g meet dat het GEMIDDELDE klopt, dus a hoort")
    print(f"  dicht bij 0 te liggen. Dat is hier een CONTROLE op de fit, geen aanname.")

    print("\n" + "=" * 78)
    print("UIT-STEEKPROEF — fit op de eerste helft, toets op de tweede")
    print("=" * 78)
    half = len(rows) // 2
    tr_rows, te_rows = rows[:half], rows[half:]
    TR, TE = P[:half], P[half:]
    print(f"  fit  : {len(TR)} duels, {tr_rows[0]['date']} t/m {tr_rows[-1]['date']}")
    print(f"  toets: {len(TE)} duels, {te_rows[0]['date']} t/m {te_rows[-1]['date']}")
    _, a_tr, b_tr = fit(TR)
    _, _, bb_tr = fit(TR, b_only=True)
    rho_tr = min(((evaluate(prep(tr_rows, rho=rr))["ll_tot"], rr)
                  for rr in [x / 100 for x in range(-20, 21)]), key=lambda t: t[0])[1]
    print(f"  gefit op de eerste helft: tilt a={a_tr:+.4f} b={b_tr:+.5f} | "
          f"tilt(a=0) b={bb_tr:+.5f} | rho={rho_tr:+.2f}")

    te_base = evaluate(TE)
    te_tilt = evaluate(TE, a_tr, b_tr)
    te_tiltb = evaluate(TE, 0.0, bb_tr)
    te_rho = evaluate(prep(te_rows, rho=rho_tr))
    print("\n  op de TOETSHELFT (log loss totaal, lager is beter):")
    print(f"    huidig grid         {te_base['ll_tot']:.5f}")
    print(f"    rho hergefit        {te_rho['ll_tot']:.5f}  "
          f"({te_base['ll_tot']-te_rho['ll_tot']:+.5f})")
    print(f"    tilt (a, b)         {te_tilt['ll_tot']:.5f}  "
          f"({te_base['ll_tot']-te_tilt['ll_tot']:+.5f})")
    print(f"    tilt (a = 0)        {te_tiltb['ll_tot']:.5f}  "
          f"({te_base['ll_tot']-te_tiltb['ll_tot']:+.5f})")
    print("\n  idem op de EXACTE UITSLAG (raakt elke markt, niet alleen de totalen):")
    print(f"    huidig grid         {te_base['ll_exact']:.5f}")
    print(f"    tilt (a = 0)        {te_tiltb['ll_exact']:.5f}  "
          f"({te_base['ll_exact']-te_tiltb['ll_exact']:+.5f})")

    print(f"\n  vormfout op de toetshelft, HUIDIG grid:")
    print(fmt_hist(te_base))
    print(f"\n  vormfout op de toetshelft, TILT (a = 0, b = {bb_tr:+.5f}):")
    print(fmt_hist(te_tiltb))
    print()
    for line in (2.5, 3.0, 3.5):
        p0, a0 = under(TE, line)
        p1, _ = under(TE, line, 0.0, bb_tr)
        print(f"  P(Under {line}) op de toetshelft: huidig {p0:5.2f}% -> tilt {p1:5.2f}%  "
              f"(werkelijk {a0:5.2f}%)")

    json.dump({"b_all": bb, "b_train": bb_tr, "a_free": a, "b_free": b,
               "rho_best": best_rho[1], "ll_base_all": base["ll_tot"]},
              open("tmp-run/grid_fit_result.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
