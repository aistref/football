"""De beslissende toets: is er iets te repareren dat niet ruis is?

Twee splitsingen van dezelfde 914 duels gaven tegengestelde antwoorden op élke kandidaat. Dat is
geen reden om de gunstigste te kiezen — het is precies de valkuil die §6e beschrijft ("een sterk
ogend verband dat alleen bestaat doordat je de verkeerde populatie neemt") en die §0 bij
`EDGE_THRESHOLD_FULL` zelf als bezwaar opschrijft. Daarom hier drie dingen die geen enkele
splitsing nodig hebben:

1. **Een GEPAARDE toets per wedstrijd** op het verschil in log loss. Dat is de juiste toets voor
   "is kandidaat X beter dan het huidige grid": elke wedstrijd levert één verschil, en de vraag is
   of het gemiddelde daarvan van nul te onderscheiden is. Geen fit, geen splitsing.
2. **Vooraf vastgelegde rho-waarden**, niet gefit. De enige cel die op de homogene populatie de
   twee standaardfouten haalt is `totaal = 0` (z = −2,67, model te dik), en dat is precies de cel
   die Dixon-Coles met rho regelt. Dat maakt "rho minder negatief" een hypothese die vóór het
   kijken vaststaat, en dan is de hele populatie een geldige toets.
3. **De significantie van de §6g-claims zelf**, op beide populaties, zodat zichtbaar is wat er
   werkelijk is gemeten en wat er is overgenomen.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import model

MAXG, TMAX = model.MAX_GOALS, 2 * model.MAX_GOALS
ROWS = sorted(json.loads(Path("tmp-run/grid_data.json").read_text()),
              key=lambda r: (r["date"], r["match"]))
POST = [r for r in ROWS if r["date"] >= "2026-09-20"]


def tv_of(lh, la, rho=model.DEFAULT_RHO, scale=1.0):
    g = model.score_grid(lh * scale, la * scale, rho=rho)
    v = [0.0] * (TMAX + 1)
    for i, row in enumerate(g):
        for j, p in enumerate(row):
            v[i + j] += p
    return v


def tilt(v, mu, a, b):
    out = [0.0] * len(v)
    z = 0.0
    for t in range(len(v)):
        if v[t] <= 0:
            continue
        d = t - mu
        x = v[t] * math.exp(a * d + b * d * d)
        out[t] = x
        z += x
    return [x / z for x in out]


def per_match_ll(rows, rho=model.DEFAULT_RHO, scale=1.0, a=0.0, b=0.0):
    out = []
    for r in rows:
        lh, la = r["lam"]
        v = tv_of(lh, la, rho=rho, scale=scale)
        if a or b:
            v = tilt(v, (lh + la) * scale, a, b)
        t = r["hg"] + r["ag"]
        out.append(-math.log(max(v[t] if t <= TMAX else 1e-12, 1e-12)))
    return out


def paired(base, cand, label):
    d = [b - c for b, c in zip(base, cand)]      # positief = kandidaat beter
    n = len(d)
    m = sum(d) / n
    var = sum((x - m) ** 2 for x in d) / (n - 1)
    se = math.sqrt(var / n)
    t = m / se if se else 0.0
    win = sum(1 for x in d if x > 0)
    print(f"  {label:34s} winst {m:+.5f}  t = {t:+5.2f}  beter in {win}/{n} "
          f"({100*win/n:.1f}%)")
    return m, t


def main():
    print(f"POPULATIE: {len(POST)} duels met lambdas van ná de shrink-overstap\n")

    print("=" * 84)
    print("1. WAT §6g CLAIMT, EN HOE HARD DAT IS")
    print("=" * 84)
    for naam, rows in (("alle duels (twee shrink-instellingen door elkaar)", ROWS),
                       ("alleen lambdas van ná 2026-09-20 (homogeen)", POST)):
        n = len(rows)
        pm = sum(sum(r["lam"]) for r in rows) / n
        am = sum(r["hg"] + r["ag"] for r in rows) / n
        sd = math.sqrt(sum((r["hg"] + r["ag"] - am) ** 2 for r in rows) / (n - 1))
        zt = (am - pm) / (sd / math.sqrt(n))
        print(f"\n  {naam}  (n = {n})")
        print(f"    gemiddeld totaal : voorspeld {pm:.3f}  werkelijk {am:.3f}  "
              f"{am-pm:+.3f}  z = {zt:+.2f}")
        for line in (2.5, 3.5):
            pr = ac = 0.0
            for r in rows:
                v = tv_of(*r["lam"])
                pr += sum(v[k] for k in range(len(v)) if k < line)
                ac += 1.0 if (r["hg"] + r["ag"]) < line else 0.0
            pr, ac = pr / n, ac / n
            se = math.sqrt(ac * (1 - ac) / n)
            print(f"    P(Under {line})     : voorspeld {100*pr:5.2f}%  werkelijk {100*ac:5.2f}%  "
                  f"{100*(ac-pr):+.2f} pp  z = {(ac-pr)/se:+.2f}")

    print("\n" + "=" * 84)
    print("2. GEPAARDE TOETS PER WEDSTRIJD op de homogene populatie (geen fit, geen splitsing)")
    print("=" * 84)
    base = per_match_ll(POST)
    print(f"  huidig grid: gemiddelde log loss {sum(base)/len(base):.5f}\n")
    print("  vooraf vastgelegde rho-waarden (hypothese: 0-0 staat te dik, dus rho minder negatief):")
    for rr in (-0.10, -0.025, 0.0, 0.025, 0.05):
        paired(base, per_match_ll(POST, rho=rr), f"rho = {rr:+.3f}")
    print("\n  overige kandidaten, op hun IN-STEEKPROEF beste waarde (dus optimistisch):")
    paired(base, per_match_ll(POST, scale=1.032), "scale = 1.032 (meer doelpunten)")
    paired(base, per_match_ll(POST, a=0.0320), "shift a = +0.032")
    paired(base, per_match_ll(POST, b=0.0050), "narrow b = +0.005")
    paired(base, per_match_ll(POST, a=0.0320, b=0.0005), "both a=+0.032 b=+0.0005")
    print("\n  en de variant die de vormfout van §6g LETTERLIJK implementeert")
    print("  (massa van de staarten naar het midden = b < 0):")
    for bb in (-0.005, -0.010, -0.015):
        paired(base, per_match_ll(POST, b=bb), f"narrow b = {bb:+.3f}")

    print("\n" + "=" * 84)
    print("3. DE TWEE SPLITSINGEN NAAST ELKAAR — elke kandidaat draait van teken")
    print("=" * 84)
    print("""
  kandidaat   gefit op tijd -> toets    gefit om en om -> toets
  rho              -0.00201 (slechter)        +0.00294 (beter)
  scale            +0.00183 (beter)           -0.00193 (slechter)
  shift            +0.00199 (beter)           -0.00430 (slechter)
  narrow           -0.00026 (niets)           +0.00027 (niets)
  both             +0.00100 (beter)           -0.00182 (slechter)

  En de gefitte waarden zelf lopen even hard uiteen:
  rho   +0.10 tegen -0.01   |   scale 1.024 tegen 1.040   |   shift +0.026 tegen +0.058

  Twee splitsingen van DEZELFDE 914 duels. Een parameter die op de ene helft +0.002 oplevert en
  op de andere -0.004 kost, met een gefitte waarde die een factor twee verschilt, meet de ruis
  van de steekproef en niet een eigenschap van het model.""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
