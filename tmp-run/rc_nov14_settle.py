"""Stage 0 — Run C 14 nov 2026: picks en schaduwpicks van 13 nov afwikkelen.
Alle duels van 13 nov zijn groepsfase / oefen / kwalificatie zonder verlenging: Fotmob-eindstand = stand na 90'.
Evaluatielogica overgenomen uit rb_nov09_settle.py; selectie per schaduwrij uit run-state
(near_miss, of poort8_geblokkeerd voor -p8-rijen)."""
import json, re, sys, runpy
from datetime import date
from scripts import fotmob
src = open("tmp-run/rb_nov09_settle.py").read().split("def run(cmd):")[0]
src = src.replace('for f in glob.glob("data/run-state/2026-11-0*.json")', 'for f in []')
src = src.replace("DAYS = [date(2026, 11, 7), date(2026, 11, 9)]", "DAYS = [date(2026, 11, 13), date(2026, 11, 14)]")
g = {}; exec(compile(src, "lib", "exec"), g)
find, evaluate, net_units, norm = g["find"], g["evaluate"], g["net_units"], g["norm"]
import subprocess
st = json.load(open("data/run-state/2026-11-13-run-c.json"))
sel = {}
for c in st["competitions"].values():
    for m in c["matches"]:
        if m.get("near_miss"): sel[(norm(m["match"]), "nm")] = (m["near_miss"]["market"], m["near_miss"]["selection"])
        if m.get("poort8_geblokkeerd"): sel[(norm(m["match"]), "p8")] = (m["poort8_geblokkeerd"][0]["market"], m["poort8_geblokkeerd"][0]["selection"])
def ev(market, h, a, gh, ga):
    mm = re.search(r"Double Chance (1X|X2|12)", market)
    if mm:
        k = mm.group(1); ok = {"1X": gh >= ga, "X2": ga >= gh, "12": gh != ga}[k]
        return ("won" if ok else "lost"), None
    return evaluate(market, h, a, gh, ga)
apply_now = "--apply" in sys.argv
rep = {"picks": [], "shadow": [], "mis": []}
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("FOUT", r.stdout, r.stderr)
for r in [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]:
    if r.get("result") not in (None, "pending"): continue
    hit = find(r["home"], r["away"])
    if not hit or not hit.get("finished"): rep["mis"].append(r["id"]); print("MIS", r["id"]); continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    res, u = ev(f'{r["market"]} — {r["selection"]}', hit["home"], hit["away"], gh, ga)
    rep["picks"].append({"id": r["id"], "score": f"{gh}-{ga}", "result": res}); print("PICK", r["id"], gh, ga, res)
    if apply_now: run(["python3", "scripts/ledger.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"])
for r in [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]:
    if r["result"] != "pending": continue
    h, a = [x.strip() for x in r["match"].split("–")]
    hit = find(h, a)
    if not hit or not hit.get("finished"): rep["mis"].append(r["id"]); print("MIS", r["id"]); continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    mk, s = sel[(norm(r["match"]), "p8" if "-p8-" in r["id"] else "nm")]
    assert mk == r["market"], (mk, r)
    market = f"{mk} — {s}"
    res, u = ev(market, hit["home"], hit["away"], gh, ga)
    units = net_units(u, r["odds"])
    rep["shadow"].append({"id": r["id"], "match": r["match"], "market": market, "gate": r["failed_gate"], "odds": r["odds"], "score": f"{gh}-{ga}", "result": res, "units": units})
    print(f"SHAD {r['match'][:30]:30s} {gh}-{ga} {market[:50]:50s} {r['failed_gate']:15s} {res} {units if units is not None else ''}")
    if apply_now:
        cmd = ["python3", "scripts/shadow.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"]
        if units is not None: cmd += ["--units", str(units)]
        run(cmd)
json.dump(rep, open("tmp-run/rc_nov14_settle.json", "w"), ensure_ascii=False, indent=1)
for k in ("picks", "shadow"):
    print(k, {x: sum(1 for y in rep[k] if y["result"] == x) for x in ("won", "lost", "void")})
print("mis", rep["mis"])
