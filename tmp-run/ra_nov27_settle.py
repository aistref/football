"""Stage 0 - Run A 27 nov 2026: de openstaande picks en schaduwpicks van 26 nov afwikkelen.

Alle openstaande rijen komen uit de league phase van de Europa League en de Conference League
en uit twee binnenlandse competities; geen knock-out, dus `status.scoreStr` van Fotmob is de
stand na 90 minuten (6d). Reken- en evaluatielogica ongewijzigd overgenomen uit
`tmp-run/rb_nov09_settle.py`; de schaduwrijen dragen zelf de volle markt-en-selectie, dus de
run-state hoeft er niet bij.
"""
import json, re, subprocess, sys
from datetime import date

MARKER = "def " + "run(cmd):"
src = open("tmp-run/rb_nov09_settle.py").read().split(MARKER)[0]
src = src.replace("DAYS = [date(2026, 11, 7), date(2026, 11, 9)]",
                  "DAYS = [date(2026, 11, 26), date(2026, 11, 27)]")
src = src.replace('for f in glob.glob("data/run-state/2026-11-0*.json")', 'for f in []')
g = {}
exec(compile(src, "settle-lib", "exec"), g)
find, evaluate, net_units, norm = g["find"], g["evaluate"], g["net_units"], g["norm"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  FOUT:", r.stdout.strip(), r.stderr.strip())
    return r.returncode == 0


apply_now = "--apply" in sys.argv
rep = {"picks": [], "shadow": [], "mis": []}

for r in [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]:
    if r.get("result") not in (None, "pending"):
        continue
    hit = find(r["home"], r["away"])
    if not hit or not hit.get("finished") or not hit.get("score"):
        rep["mis"].append(r["id"]); print("MIS pick", r["id"]); continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    market = f'{r["market"]} - {r["selection"]}'.replace(" - ", " — ", 1)
    res, u = evaluate(market, hit["home"], hit["away"], gh, ga)
    units = net_units(u, r["odds"])
    rep["picks"].append({"id": r["id"], "match": f'{r["home"]} - {r["away"]}', "market": market,
                         "odds": r["odds"], "score": f"{gh}-{ga}", "result": res, "units": units,
                         "my_prob": r.get("my_prob")})
    print(f'PICK {r["home"][:20]:20s}-{r["away"][:20]:20s} {gh}-{ga} {market[:40]:40s} -> {res}'
          + (f" ({units:+.2f}u)" if units is not None else ""))
    if apply_now:
        cmd = ["python3", "scripts/ledger.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"]
        if units is not None:
            cmd += ["--units", str(units)]
        run(cmd)

for r in [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]:
    if r["result"] != "pending":
        continue
    h, a = [x.strip() for x in r["match"].split("–")]
    hit = find(h, a)
    if not hit or not hit.get("finished") or not hit.get("score"):
        rep["mis"].append(r["id"]); print("MIS shadow", r["id"]); continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    market = r["market"]
    if market.startswith("AH \u2014"):      # shadow.jsonl schrijft AH, evaluate kent Asian Handicap
        market = "Asian Handicap " + market[3:]
    if market.startswith("DNB \u2014"):
        market = "Draw No Bet " + market[4:]
    res, u = evaluate(market, hit["home"], hit["away"], gh, ga)
    units = net_units(u, r["odds"])
    rep["shadow"].append({"id": r["id"], "match": r["match"], "market": market,
                          "gate": r["failed_gate"], "odds": r["odds"], "score": f"{gh}-{ga}",
                          "result": res, "units": units})
    print(f'SHAD {r["match"][:32]:32s} {gh}-{ga} {market[:44]:44s} {r["failed_gate"]:18s} {res}'
          + (f" ({units:+.2f}u)" if units is not None else ""))
    if apply_now:
        cmd = ["python3", "scripts/shadow.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"]
        if units is not None:
            cmd += ["--units", str(units)]
        run(cmd)

json.dump(rep, open("tmp-run/ra_nov27_settle.json", "w"), ensure_ascii=False, indent=1)
for k in ("picks", "shadow"):
    print(k, {x: sum(1 for y in rep[k] if y["result"] == x) for x in ("won", "lost", "void")})
print("mis:", rep["mis"])
