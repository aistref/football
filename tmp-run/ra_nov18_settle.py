"""Stage 0 - Run A 18 nov 2026: schaduwrijen van 17 nov afwikkelen.
De drie echte picks van 17 nov zijn al via ledger.py settle afgewikkeld (1 won, 2 lost).
Alle duels van 17 nov zijn interlands (Nations League-groepsfase, WK/AC-kwalificatie) zonder
verlenging, dus de Fotmob-eindstand is de stand na 90'. Logica overgenomen uit rc_nov17_settle.py.
"""
import json, re, sys, subprocess
from datetime import date

src = open("tmp-run/rb_nov09_settle.py").read().split("def run(cmd):")[0]
src = src.replace('for f in glob.glob("data/run-state/2026-11-0*.json")', 'for f in []')
src = src.replace("DAYS = [date(2026, 11, 7), date(2026, 11, 9)]", "DAYS = [date(2026, 11, 17), date(2026, 11, 18)]")
g = {}
exec(compile(src, "lib", "exec"), g)
find, evaluate, net_units, norm = g["find"], g["evaluate"], g["net_units"], g["norm"]

sel = {}
for D in ("2026-11-17",):
    st = json.load(open(f"data/run-state/{D}-run-c.json"))
    for c in st["competitions"].values():
        for m in c["matches"]:
            if m.get("near_miss"):
                sel[(D, norm(m["match"]), "nm")] = (m["near_miss"]["market"], m["near_miss"]["selection"])
            if m.get("poort8_geblokkeerd"):
                sel[(D, norm(m["match"]), "p8")] = (m["poort8_geblokkeerd"][0]["market"], m["poort8_geblokkeerd"][0]["selection"])

def ev(market, h, a, gh, ga):
    mm = re.search(r"Double Chance (1X|X2|12)", market)
    if mm:
        k = mm.group(1)
        ok = {"1X": gh >= ga, "X2": ga >= gh, "12": gh != ga}[k]
        return ("won" if ok else "lost"), None
    return evaluate(market, h, a, gh, ga)

apply_now = "--apply" in sys.argv
rep = {"shadow": [], "mis": []}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print("FOUT", r.stdout, r.stderr)

for r in [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]:
    if r["result"] != "pending":
        continue
    h, a = [x.strip() for x in r["match"].split("–")]
    hit = find(h, a)
    if not hit or not hit.get("finished"):
        rep["mis"].append(r["id"]); print("MIS", r["id"]); continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    key = (r["id"][7:17], norm(r["match"]), "p8" if "-p8-" in r["id"] else "nm")
    if key not in sel:
        rep["mis"].append(r["id"]); print("GEEN SELECTIE", r["id"]); continue
    mk, s = sel[key]
    assert mk == r["market"], (mk, r)
    market = f"{mk} — {s}"
    res, u = ev(market, hit["home"], hit["away"], gh, ga)
    units = net_units(u, r["odds"])
    rep["shadow"].append({"id": r["id"], "match": r["match"], "market": market,
                          "gate": r["failed_gate"], "odds": r["odds"],
                          "score": f"{gh}-{ga}", "result": res, "units": units})
    print(f"SHAD {r['match'][:28]:28s} {gh}-{ga} {market[:46]:46s} {r['failed_gate']:14s} {res} {units if units is not None else ''}")
    if apply_now:
        cmd = ["python3", "scripts/shadow.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"]
        if units is not None:
            cmd += ["--units", str(units)]
        run(cmd)

json.dump(rep, open("tmp-run/ra_nov18_settle.json", "w"), ensure_ascii=False, indent=1)
print("shadow", {x: sum(1 for y in rep["shadow"] if y["result"] == x) for x in ("won", "lost", "void")})
print("mis", rep["mis"])
