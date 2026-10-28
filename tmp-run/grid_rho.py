"""De enige kandidaat die een vooraf vastgelegde hypothese heeft: rho.

De gepaarde toets gaf `rho = -0.025` de hoogste t van alle kandidaten (+1,89) en `rho = -0.10`
duidelijk slechter (t = -2,67). Dat is één richting en ze volgt uit de enige histogramcel die op
de homogene populatie de twee standaardfouten haalt: `totaal = 0` staat te dik (z = -2,67), en dat
is precies de cel die Dixon-Coles met rho regelt.

Maar de GEFITTE rho sprong tussen de twee splitsingen van +0.10 naar -0.01, en dat is geen
meting. Daarom hier de strengere en eerlijkere toets: **vaste, vooraf gekozen waarden**, los
geëvalueerd op vier onafhankelijke deelsteekproeven. Er wordt nergens gefit, dus er is niets om
aan te passen; de vraag is alleen of het teken op alle vier dezelfde kant op wijst.

Haalt een waarde dat niet, dan is ook deze kandidaat ruis en blijft het grid zoals het is.
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
CAND = (-0.05, -0.025, 0.0)


def ll_list(rows, rho):
    out = []
    for r in rows:
        g = model.score_grid(r["lam"][0], r["lam"][1], rho=rho)
        v = [0.0] * (TMAX + 1)
        for i, row in enumerate(g):
            for j, p in enumerate(row):
                v[i + j] += p
        t = r["hg"] + r["ag"]
        out.append(-math.log(max(v[t] if t <= TMAX else 1e-12, 1e-12)))
    return out


def ll_exact_list(rows, rho):
    out = []
    for r in rows:
        g = model.score_grid(r["lam"][0], r["lam"][1], rho=rho)
        p = g[r["hg"]][r["ag"]] if (r["hg"] <= MAXG and r["ag"] <= MAXG) else 1e-12
        out.append(-math.log(max(p, 1e-12)))
    return out


def paired(base, cand):
    d = [b - c for b, c in zip(base, cand)]
    n = len(d)
    m = sum(d) / n
    var = sum((x - m) ** 2 for x in d) / (n - 1)
    se = math.sqrt(var / n)
    return m, (m / se if se else 0.0)


def p00(rows, rho):
    pr = ac = 0.0
    for r in rows:
        g = model.score_grid(r["lam"][0], r["lam"][1], rho=rho)
        pr += g[0][0]
        ac += 1.0 if (r["hg"] == 0 and r["ag"] == 0) else 0.0
    return 100 * pr / len(rows), 100 * ac / len(rows)


def main():
    subs = {
        "homogeen, eerste helft op tijd": POST[:len(POST) // 2],
        "homogeen, tweede helft op tijd": POST[len(POST) // 2:],
        "homogeen, even duels": POST[0::2],
        "homogeen, oneven duels": POST[1::2],
        "de 803 duels van VOOR de overstap": [r for r in ROWS if r["date"] < "2026-09-20"],
    }
    print("VASTE rho-WAARDEN, nergens gefit, op vijf deelsteekproeven.")
    print("Winst = log loss(rho = -0.05) - log loss(kandidaat); positief = kandidaat beter.\n")
    print(f"{'deelsteekproef':36s} {'n':>5}  {'rho=-0.025':>22s}  {'rho=0.00':>22s}")
    print("-" * 92)
    tekens = {c: [] for c in CAND[1:]}
    for naam, rows in subs.items():
        base = ll_list(rows, -0.05)
        cel = f"{naam:36s} {len(rows):5d}"
        for c in CAND[1:]:
            m, t = paired(base, ll_list(rows, c))
            tekens[c].append(m)
            cel += f"   {m:+.5f} (t={t:+5.2f})"
        print(cel)

    print("\nTEKENCONTROLE — hoort op alle vijf dezelfde kant op te wijzen:")
    for c in CAND[1:]:
        pos = sum(1 for m in tekens[c] if m > 0)
        print(f"  rho = {c:+.3f}: positief op {pos} van de {len(tekens[c])} deelsteekproeven")

    print("\n" + "=" * 92)
    print("WAT rho MET DE 0-0-CEL DOET — de enige cel die de twee standaardfouten haalde")
    print("=" * 92)
    for c in CAND:
        pr, ac = p00(POST, c)
        print(f"  rho = {c:+.3f}: P(0-0) voorspeld {pr:5.2f}%   werkelijk {ac:5.2f}%   "
              f"{ac-pr:+.2f} pp")
    print("""
  Lees dat goed: zelfs met rho = 0 (dus ZONDER Dixon-Coles) blijft 0-0 te dik voorspeld. De
  scheefstand op die cel komt dus niet van de rho-correctie maar van de Poisson-aanname zelf, en
  rho verschuift hem maar voor een deel. Wie de 0-0-cel echt wil repareren, moet aan de
  marginalen en niet aan rho — en daar is op deze steekproef geen variant voor die het haalt.""")

    print("\n" + "=" * 92)
    print("EN OP DE EXACTE UITSLAG (raakt elke markt, niet alleen de totalen)")
    print("=" * 92)
    base_e = ll_exact_list(POST, -0.05)
    for c in CAND[1:]:
        m, t = paired(base_e, ll_exact_list(POST, c))
        print(f"  rho = {c:+.3f}: winst {m:+.5f}  t = {t:+5.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
