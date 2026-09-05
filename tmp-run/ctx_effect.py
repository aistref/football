"""Meet of ontbrekende spelers de fout van het model voorspellen — op uitslagen, niet op de markt.

De vraag (gebruiker, 5 sep 2026): poort 7 houdt sinds 23 aug bets tegen op grond van blessures en
schorsingen, maar stelt `my_prob` niet bij. §1c zegt daar met zoveel woorden bij waarom: "er is geen
enkele meting die zegt hoeveel procentpunt een geblesseerde middenvelder waard is, en zo'n getal
verzinnen is precies wat §2 en §4 verbieden." Inmiddels liggen er wél waarnemingen. Dit script
maakt er een meting van.

Opzet:
  - Elke wedstrijd in `data/run-state/` met zowel een `context`- als een `calibration`-blok.
  - Onafhankelijke variabele: het **beschikbaarheidsverschil**, het aandeel van de selectiewaarde
    dat de thuisploeg mist minus dat van de uitploeg. Positief = de thuisploeg mist meer.
  - Afhankelijke variabele: de **fout van het model** op de thuiswinstkans, `uitkomst - p_model`.
  - Uitslag van Fotmob, één verzoek per kalenderdag.

Als ontbrekende spelers informatie bevatten die het model niet heeft, hoort een groter
beschikbaarheidsverschil samen te gaan met een negatievere fout: het model verwacht dan te veel van
de thuisploeg. Zo niet, dan is er niets te corrigeren en blijft poort 7 wat hij is.

Er komt geen bookmakerprijs aan te pas bij het fitten (§2). De marktkans wordt alleen als
referentie meegeprint.
"""
import json
import glob
import re
import statistics as S
import sys
from datetime import date

sys.path.insert(0, ".")
from scripts.settling import DayIndex, norm

rows = []
index = DayIndex()
gemist = {"geen uitslag": 0, "niet afgelopen": 0, "geen waarde": 0}

for path in sorted(glob.glob("data/run-state/*.json")):
    dag = date.fromisoformat(path.split("/")[-1][:10])
    state = json.load(open(path))
    for comp, blk in (state.get("competitions") or {}).items():
        if not isinstance(blk, dict):
            continue
        for m in blk.get("matches", []):
            if not isinstance(m, dict):
                continue
            ctx, cal = m.get("context") or {}, m.get("calibration")
            if not ctx.get("home") or not cal:
                continue
            ho, aw = ctx["home"], ctx["away"]
            # Twee vormen in de data: sommige runs schreven het contextblok als dict, andere als
            # leesbare zin ("2 afwezig (13% van de selectiewaarde) - vorm LWWWL"). Allebei
            # bruikbaar; de zin bevat hetzelfde percentage, dus die wordt uitgelezen in plaats van
            # weggegooid.
            def aandeel(v):
                # LET OP de noemer. `squad_value` is de waarde van de vermoedelijke BASISELF, en
                # de uitvallers zitten daar niet in. Het aandeel is dus out/(basis+out), precies
                # zoals `context.TeamContext.out_share` het rekent — niet out/basis. Met die
                # verkeerde noemer kwam Lommel - Club Brugge op 247% uit, wat onmogelijk is, en
                # liep deze meting op twee verschillende definities door elkaar (de tekstvorm
                # hieronder gebruikte namelijk wél de goede).
                if isinstance(v, dict):
                    sv = v.get("squad_value") or 0
                    ov = v.get("out_value") or 0
                    return (ov / (sv + ov)) if sv > 0 else None
                m = re.search(r"\((\d+(?:[.,]\d+)?)\s*% van de selectiewaarde\)", str(v))
                return float(m.group(1).replace(",", ".")) / 100 if m else None

            uit_h, uit_a = aandeel(ho), aandeel(aw)
            if uit_h is None or uit_a is None:
                gemist["geen waarde"] += 1
                continue

            naam = m.get("match", "")
            thuis, uitp = [x.strip() for x in naam.split("–")] if "–" in naam else (None, None)
            if not thuis:
                gemist["geen uitslag"] += 1
                continue
            hit = index.lookup(thuis, uitp, dag) if hasattr(index, "lookup") else None
            if hit is None:
                hit = index._day(dag).get((norm(thuis), norm(uitp)))
            if not hit or not hit.get("finished") or not hit.get("score"):
                gemist["niet afgelopen"] += 1
                continue
            try:
                gh, ga = (int(x) for x in str(hit["score"]).replace("-", " ").split())
            except ValueError:
                gemist["geen uitslag"] += 1
                continue

            rows.append({
                "datum": dag.isoformat(), "match": naam, "comp": comp,
                "gap": uit_h - uit_a,              # positief = thuisploeg mist meer
                "uit_h": uit_h, "uit_a": uit_a,
                "p_model_home": cal["p_xg"][0] if cal.get("p_xg") else None,
                "p_mean_home": ((cal["p_xg"][0] + cal["p_split"][0]) / 2
                                if cal.get("p_xg") and cal.get("p_split") else None),
                "p_markt_home": cal["market"][0] if cal.get("market") else None,
                "thuis_win": 1.0 if gh > ga else 0.0,
                "gelijk": 1.0 if gh == ga else 0.0,
                "doelpunten": gh + ga,
            })

rows = [r for r in rows if r["p_mean_home"] is not None]
print(f"bruikbare wedstrijden: {len(rows)}   (overgeslagen: {gemist})")
json.dump(rows, open("tmp-run/ctx_effect.json", "w"), ensure_ascii=False, indent=1)


def correlatie(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan"), float("nan")
    mx, my = S.mean(xs), S.mean(ys)
    sx, sy = S.pstdev(xs), S.pstdev(ys)
    if not sx or not sy:
        return float("nan"), float("nan")
    r = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)
    t = r * ((n - 2) / max(1e-9, 1 - r * r)) ** 0.5
    return r, t


gap = [r["gap"] for r in rows]
fout_model = [r["thuis_win"] - r["p_mean_home"] for r in rows]
fout_markt = [r["thuis_win"] - r["p_markt_home"] for r in rows]

print(f"\nbeschikbaarheidsverschil: gemiddelde {S.mean(gap):+.3f}, spreiding {S.pstdev(gap):.3f}")
print(f"thuiswinst werkelijk {S.mean(r['thuis_win'] for r in rows) * 100:.1f}%, "
      f"model {S.mean(r['p_mean_home'] for r in rows) * 100:.1f}%, "
      f"markt {S.mean(r['p_markt_home'] for r in rows) * 100:.1f}%")

for label, fout in (("fout van het MODEL", fout_model), ("fout van de MARKT", fout_markt)):
    r, t = correlatie(gap, fout)
    print(f"\n{label} tegen het beschikbaarheidsverschil:")
    print(f"   correlatie r = {r:+.3f}   t = {t:+.2f}   (n = {len(rows)})")
    # helling: hoeveel procentpunt per volle eenheid verschil
    mx, my = S.mean(gap), S.mean(fout)
    var = sum((x - mx) ** 2 for x in gap)
    if var:
        b = sum((x - mx) * (y - my) for x, y in zip(gap, fout)) / var
        print(f"   helling      = {b * 100:+.1f} pp per eenheid beschikbaarheidsverschil")
        print(f"   over het waargenomen bereik ({min(gap):+.2f} tot {max(gap):+.2f}) is dat "
              f"{b * (max(gap) - min(gap)) * 100:+.1f} pp van uiterste tot uiterste")

print("\nPer bak van het beschikbaarheidsverschil:")
print(f"{'bak':>18s} {'n':>4s} {'thuiswinst':>11s} {'model':>8s} {'fout':>8s}")
bakken = [(-9, -0.15), (-0.15, -0.05), (-0.05, 0.05), (0.05, 0.15), (0.15, 9)]
for lo, hi in bakken:
    v = [r for r in rows if lo <= r["gap"] < hi]
    if not v:
        continue
    lbl = f"{lo:+.2f} tot {hi:+.2f}" if abs(lo) < 9 else f"< {hi:+.2f}"
    if hi > 8:
        lbl = f">= {lo:+.2f}"
    w = S.mean(r["thuis_win"] for r in v)
    p = S.mean(r["p_mean_home"] for r in v)
    print(f"{lbl:>18s} {len(v):4d} {w * 100:10.1f}% {p * 100:7.1f}% {(w - p) * 100:+7.1f}")
