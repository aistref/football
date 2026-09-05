#!/usr/bin/env python3
"""Herijk `my_prob` op **uitslagen** — de enige maatstaf waar geen bookmaker in zit (§33/§2).

Waarom dit bestaat (5 sep 2026, na de analyse in `runs/2026-09-05-run-a.md`). Over 392 afgerekende
gevallen — 155 gespeelde picks plus 237 kandidaten die een poort tegenhield — zegt het model
gemiddeld 52.5% en gebeurt het 42.6% van de tijd. Dat is een scheefstand van bijna tien
procentpunt, en altijd dezelfde kant op. De gemiddelde geclaimde edge is +9.7 pp; het model zit er
+12.3 pp naast. **Het "voordeel" dat de routine meet, is grotendeels haar eigen fout.** Wie dan
selecteert op de grootste gemeten edge, selecteert op de grootste modelfout — en dat is precies
waarom een hógere drempel op de underdog-kant het resultaat dáár slechter maakte in plaats van
beter (§1e, punt 3).

**Waarom dit mag en de correctie van 31 aug niet mocht.** Die oude, ingetrokken instructie mat de
afwijking tegen de **de-vigde marktkans** en trok die van `my_prob` af; dan hangt je kansschatting
per definitie af van de koers waartegen je hem afzet, en meet `edge_pp` niets meer (§2). Deze
functie meet tegen de **werkelijke uitslag**. Een uitslag weet niet wat de prijs was, dus deze
correctie kan geen verkapte kopie van de bookmaker zijn. Dat is het hele onderscheid.

    from scripts.recalibrate import load_fit, apply
    fit = load_fit()                 # leest picks.jsonl + shadow.jsonl
    p = apply(my_prob_ruw, fit)

Vorm van de correctie: Platt-schaling op de logit,

    p' = sigmoid(a * logit(p) + b)

`a` regelt hoe scherp de schatting is (a < 1 vlakt af, a > 1 maakt scherper), `b` verschuift het
niveau. Twee parameters op honderden waarnemingen — met opzet het simpelste dat de scheefstand kan
wegnemen zonder de vorm van de verdeling te verzinnen.

**Uit-steekproef gecontroleerd**, want een correctie die alleen op zijn eigen data werkt is geen
correctie. Gefit op de eerste helft van de periode (196 gevallen t/m 28 aug) en getest op de tweede
helft (196 gevallen vanaf 28 aug), die bij het fitten geen rol speelden. Brier tegen de uitslag,
lager is beter:

| | ruw | herijkt |
|---|---|---|
| ongewogen gemiddelde (oud) | .25624 | .24771 |
| 0.8/0.2-weging (nu) | .25343 | **.24741** |
| **de markt** | | **.23950** |

De herijking werkt dus echt, en ze houdt stand op gevallen waarop niets is afgesteld. **En ze is
niet genoeg.** Ook herijkt en met de betere weging schat de bookmaker scherper dan het model, en
dat is nog een gunstige vergelijking ook: in zijn getal zit zijn eigen marge, die zijn score juist
slechter maakt. Haal die eruit en het verschil wordt groter.

Wat daaruit volgt en wat je hier niet moet weglezen: zolang die onderste regel staat, is elk
gemeten voordeel eerder modelfout dan marktfout, en is "vandaag niets" op de meeste dagen het
juiste antwoord — geen defect. De herijking maakt de routine eerlijker over wat ze weet; ze maakt
haar niet winstgevend. Zie `runs/2026-09-05-run-a.md`.

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PICKS = ROOT / "data" / "picks.jsonl"
SHADOW = ROOT / "data" / "shadow.jsonl"

MIN_OBSERVATIONS = 150
"""Onder dit aantal afgerekende gevallen wordt er niet herijkt.

Twee parameters fitten op minder dan ~150 waarnemingen is ruis vermenigvuldigen. Dezelfde
voorzichtigheid als §6d: onder ongeveer dertig gevallen per groep zegt een verschil niets, en een
correctie die op het hele bestand wordt toegepast verdient een ruimere drempel dan dat.
"""

_EDGES = re.compile(r"xG-methode ([+-][\d.]+) pp, splitsmethode ([+-][\d.]+) pp")


@dataclass(frozen=True)
class Fit:
    a: float
    b: float
    n: int
    hit_rate: float
    mean_claim: float
    fitted_through: str

    @property
    def bias_pp(self) -> float:
        """Hoeveel procentpunt het model gemiddeld te optimistisch was over deze periode."""
        return (self.mean_claim - self.hit_rate) * 100

    def describe(self) -> str:
        return (f"herijking op {self.n} afgerekende gevallen t/m {self.fitted_through}: "
                f"a={self.a:.3f}, b={self.b:.3f} — het model zei gemiddeld "
                f"{self.mean_claim * 100:.1f}%, werkelijk {self.hit_rate * 100:.1f}% "
                f"({self.bias_pp:+.1f} pp)")


IDENTITY = Fit(a=1.0, b=0.0, n=0, hit_rate=0.0, mean_claim=0.0, fitted_through="—")
"""Geen correctie. Wordt teruggegeven zolang er te weinig waarnemingen zijn."""


def _clip(p: float, eps: float = 0.005) -> float:
    return min(max(p, eps), 1 - eps)


def logit(p: float) -> float:
    p = _clip(p)
    return math.log(p / (1 - p))


def sigmoid(z: float) -> float:
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


def observations() -> list[tuple[float, float, str]]:
    """(my_prob, uitkomst 0/1, datum) van elk afgerekend geval — picks én schaduwkandidaten.

    Beide bestanden meedoen is geen slordigheid maar de bedoeling. `picks.jsonl` bevat alleen wat
    er dóórheen kwam en is daarmee de zwaarst geselecteerde groep die er is; `shadow.jsonl` bevat
    wat de poorten tegenhielden. Samen zijn ze de volledige verzameling waar de routine een mening
    over had, en dat is precies de populatie waarop de correctie later wordt toegepast.
    """
    rows: list[tuple[float, float, str]] = []
    for path, datefield in ((PICKS, "run_date"), (SHADOW, "date")):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("result") not in ("won", "lost"):
                continue
            prob = rec.get("my_prob")
            if prob is None:
                continue
            rows.append((float(prob), 1.0 if rec["result"] == "won" else 0.0,
                         rec.get(datefield) or rec.get("date") or ""))
    rows.sort(key=lambda r: r[2])
    return rows


def fit(rows: list[tuple[float, float, str]], *, steps: int = 4000, lr: float = 0.25) -> Fit:
    """Fit `a` en `b` met gradient descent op de log loss. Geen afhankelijkheden nodig."""
    if len(rows) < MIN_OBSERVATIONS:
        return IDENTITY
    xs = [logit(p) for p, _, _ in rows]
    ys = [y for _, y, _ in rows]
    a, b = 1.0, 0.0
    n = len(rows)
    for _ in range(steps):
        ga = gb = 0.0
        for x, y in zip(xs, ys):
            err = sigmoid(a * x + b) - y
            ga += err * x
            gb += err
        a -= lr * ga / n
        b -= lr * gb / n
    return Fit(a=a, b=b, n=n, hit_rate=sum(ys) / n,
               mean_claim=sum(p for p, _, _ in rows) / n, fitted_through=rows[-1][2])


def load_fit() -> Fit:
    """De herijking zoals hij nu uit het logboek volgt. Roep dit één keer per run aan."""
    return fit(observations())


def apply(prob: float, f: Fit) -> float:
    """Pas de herijking toe. Met `IDENTITY` verandert er niets."""
    if f.n == 0:
        return prob
    return sigmoid(f.a * logit(prob) + f.b)


def _cmd_show(_args: argparse.Namespace) -> int:
    f = load_fit()
    if f.n == 0:
        print(f"Nog geen herijking: minder dan {MIN_OBSERVATIONS} afgerekende gevallen "
              f"({len(observations())} gevonden). `my_prob` gaat ongewijzigd door.")
        return 0
    print(f.describe())
    print("\nWat de correctie met een kans doet:")
    print(f"  {'ruw':>8s}  {'herijkt':>8s}  {'verschil':>9s}")
    for p in (0.30, 0.40, 0.50, 0.55, 0.60, 0.70, 0.80):
        q = apply(p, f)
        print(f"  {p * 100:7.1f}%  {q * 100:7.1f}%  {(q - p) * 100:+8.1f} pp")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    show = sub.add_parser("show", help="toon de huidige herijking en wat hij doet")
    show.set_defaults(func=_cmd_show)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
