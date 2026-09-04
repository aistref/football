"""Run B van 4 sep 2026 opnieuw beoordeeld met poort 8 (§1e).

Run B legt in `tmp-run/b_analysis.json` per wedstrijd de **volledige** kandidatenlijst vast, met
per selectie de kant, de score en de uitslag van elke poort. Poort 8 kan alleen tegenhouden en
nooit iets extra's doorlaten, dus die lijst is genoeg om de run opnieuw te beoordelen zonder hem
opnieuw te draaien: per wedstrijd valt de winnaar af als hij op de underdog-kant staat, en dan
wint de hoogste score die overblijft — of er komt geen bet.
"""
import json
import sys

sys.path.insert(0, ".")
from scripts import sides

data = json.load(open("tmp-run/b_analysis.json"))

changes, blocked = [], []
for name, m in data.items():
    cands = m.get("candidates") or []
    if not cands:
        continue
    o1x2 = m.get("odds_1x2")
    qualified = []
    for c in cands:
        g = c.get("gates") or {}
        if not all(g.get(k, True) for k in ("edge", "odds", "tier", "tweede_methode",
                                            "robuustheid", "context")):
            continue
        chk = sides.check(c.get("side"), o1x2)
        c["gate_underdog"] = {"passed": chk.passed, "reason": chk.reason}
        if chk.passed:
            qualified.append(c)
        else:
            blocked.append((name, c))
    old = m.get("winner")
    new = max(qualified, key=lambda c: c["score"]) if qualified else None
    if (old or {}).get("selection") != (new or {}).get("selection"):
        changes.append((name, old, new, m))
    m["winner_na_poort8"] = new

print(f"{len(data)} wedstrijden, {len(blocked)} selectie(s) tegengehouden door poort 8\n")
for name, c in blocked:
    print(f"  GEBLOKKEERD  {name[:38]:38s} {c['market']} — {c['selection']} @ {c['odds']} "
          f"(edge {c['edge_pp']:+.2f}, score {c['score']})")
print()
for name, old, new, m in changes:
    o = f"{old['market']} — {old['selection']} @ {old['odds']} (score {old['score']})" if old else "geen bet"
    n = f"{new['market']} — {new['selection']} @ {new['odds']} (score {new['score']})" if new else "GEEN BET"
    print(f"  WIJZIGING    {name}\n      was : {o}\n      nu  : {n}")
    if new:
        print(f"      kant: {new.get('side')}, poort 8: "
              f"{sides.check(new.get('side'), m.get('odds_1x2')).reason}")

json.dump(data, open("tmp-run/b_analysis_gate8.json", "w"), ensure_ascii=False, indent=1)
print("\nweggeschreven naar tmp-run/b_analysis_gate8.json")
