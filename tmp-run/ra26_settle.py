"""Stage 0 — Run A 26 sep 2026: openstaande picks en schaduwpicks van 25 sep afwikkelen.

Rekent af op de stand na 90 minuten (§6d). De openstaande rijen komen uit interlandvoetbal
(Nations League, CAF/CONCACAF/AFC-kwalificatie) en de KKD — geen knock-out, dus `status.scoreStr`
van Fotmob *is* de stand na 90 minuten. De marktlogica is die van `ra21_settle.py`; nieuw is dat
de selectie van een schaduwrij uit `data/run-state/` wordt gehaald, omdat `shadow.jsonl` voor de
Run C-rijen alleen de markt bewaart en niet de kant.
"""
import json, re, subprocess, sys, unicodedata, glob
from datetime import date
from scripts import fotmob

DAYS = [date(2026, 9, 25), date(2026, 9, 26)]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


index = {}
for d in DAYS:
    fx = fotmob.fetch_fixtures(d)
    for lg in fx.get("leagues", []):
        for m in lg.get("matches", []):
            st = m.get("status", {}) or {}
            key = (norm(m["home"]["name"]), norm(m["away"]["name"]))
            if key in index and index[key].get("finished"):
                continue
            index[key] = {"league": lg.get("name"), "score": st.get("scoreStr"),
                          "finished": st.get("finished"), "home": m["home"]["name"],
                          "away": m["away"]["name"]}
print("fixtures geindexeerd:", len(index))

# selectie per wedstrijd uit run-state (near_miss), zodat een schaduwrij zonder kant afrekenbaar is
sel_by_match = {}
for f in glob.glob("data/run-state/2026-09-2*.json"):
    d = json.load(open(f))
    for c in d.get("competitions", {}).values():
        for m in c.get("matches", []) if isinstance(c, dict) else []:
            nm = m.get("near_miss")
            if nm and nm.get("selection"):
                sel_by_match[norm(m["match"])] = f'{nm["market"]} — {nm["selection"]}'


def find(home, away):
    hit = index.get((norm(home), norm(away)))
    if hit:
        return hit
    cand = [v for k, v in index.items()
            if k[0].startswith(norm(home)[:6]) and k[1].startswith(norm(away)[:6])]
    if len(cand) == 1:
        return cand[0]
    cand = [v for k, v in index.items()
            if (norm(home)[:6] in k[0] or k[0][:6] in norm(home))
            and (norm(away)[:6] in k[1] or k[1][:6] in norm(away))]
    return cand[0] if len(cand) == 1 else None


def side_of(text, home, away):
    t = norm(text)
    for side, name in (("home", home), ("away", away)):
        n = norm(name)
        if n and (n in t or t.startswith(n[:6]) or n[:6] in t):
            return side
    return None


def ah_units(line, side, gh, ga):
    margin = (gh - ga) if side == "home" else (ga - gh)
    if abs(line * 4) % 2 == 1:
        return (ah_units(line - 0.25, side, gh, ga) + ah_units(line + 0.25, side, gh, ga)) / 2
    d = margin + line
    return 1.0 if d > 0 else (-1.0 if d < 0 else 0.0)


def totals_units(line, over, gh, ga):
    tot = gh + ga
    if abs(line * 4) % 2 == 1:
        return (totals_units(line - 0.25, over, gh, ga) + totals_units(line + 0.25, over, gh, ga)) / 2
    d = (tot - line) if over else (line - tot)
    return 1.0 if d > 0 else (-1.0 if d < 0 else 0.0)


def evaluate(market, home, away, gh, ga):
    m = market
    if m.startswith("1X2"):
        tail = m.split("—")[-1]
        if "gelijkspel" in m.lower() or re.search(r"[—:]\s*X\b", m):
            return ("won" if gh == ga else "lost"), None
        side = "home" if re.search(r"[—:]\s*1\b", m) else ("away" if re.search(r"[—:]\s*2\b", m)
                                                           else side_of(tail, home, away))
        if side is None:
            raise ValueError(f"geen kant in: {m}")
        win = (gh > ga) if side == "home" else (ga > gh)
        return ("won" if win else "lost"), None
    if m.startswith("Draw No Bet"):
        side = side_of(m.split("—")[-1], home, away)
        if gh == ga:
            return "void", None
        win = (gh > ga) if side == "home" else (ga > gh)
        return ("won" if win else "lost"), None
    if m.startswith("Double Chance"):
        side = side_of(m.split("—")[-1].split("(")[0], home, away)
        ok = (gh >= ga) if side == "home" else (ga >= gh)
        return ("won" if ok else "lost"), None
    if m.startswith("Asian Handicap"):
        tail = m.split("—", 1)[1]
        mm = re.search(r"([+-]?\d+(?:\.\d+)?)", tail)
        line = float(mm.group(1))
        side = side_of(re.sub(r"AH|Asian Handicap|[+-]?\d+(\.\d+)?", " ", tail), home, away)
        u = ah_units(line, side, gh, ga)
        return ("won" if u > 0 else ("lost" if u < 0 else "void")), (u if abs(u) not in (0.0, 1.0) else None)
    if m.startswith("Over/Under") or re.match(r"^(Over|Under)\s", m):
        mm = re.search(r"(Over|Under)\s+(\d+(?:\.\d+)?)", m, re.I)
        over = mm.group(1).lower() == "over"
        u = totals_units(float(mm.group(2)), over, gh, ga)
        return ("won" if u > 0 else ("lost" if u < 0 else "void")), (u if abs(u) not in (0.0, 1.0) else None)
    if m.startswith("BTTS"):
        ja = "ja" in m.lower().split("—")[-1]
        both = gh > 0 and ga > 0
        return ("won" if both == ja else "lost"), None
    raise ValueError(f"onbekende markt: {m}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("  FOUT:", r.stdout.strip(), r.stderr.strip())
    return r.returncode == 0


apply_now = "--apply" in sys.argv
report = {"picks": [], "shadow": [], "mis": []}

for r in [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]:
    if r.get("result") not in (None, "pending"):
        continue
    h, a = r["home"], r["away"]
    hit = find(h, a)
    if not hit or not hit.get("finished") or not hit.get("score"):
        report["mis"].append(f"pick {h} - {a}")
        print(f"MIS pick {h} - {a}")
        continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    market = f'{r["market"]} — {r["selection"]}'
    res, units = evaluate(market, hit["home"], hit["away"], gh, ga)
    report["picks"].append({"id": r["id"], "match": f"{h} – {a}", "market": market,
                            "odds": r["odds"], "score": f"{gh}-{ga}", "result": res, "units": units})
    print(f"PICK {h[:18]:18s}-{a[:18]:18s} {gh}-{ga}  {market[:42]:42s} -> {res}"
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
        report["mis"].append(f"shadow {r['match']}")
        print(f"MIS shadow {r['match']}")
        continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    market = r["market"]
    if "—" not in market:
        market = sel_by_match.get(norm(r["match"]), market)
    res, units = evaluate(market, hit["home"], hit["away"], gh, ga)
    report["shadow"].append({"id": r["id"], "match": r["match"], "market": market,
                             "failed_gate": r["failed_gate"], "odds": r["odds"],
                             "score": f"{gh}-{ga}", "result": res, "units": units})
    print(f"SHAD {r['match'][:34]:34s} {gh}-{ga}  {market[:40]:40s} -> {res}")
    if apply_now:
        cmd = ["python3", "scripts/shadow.py", "settle", r["id"], res, "--score", f"{gh}-{ga}"]
        if units is not None:
            cmd += ["--units", str(units)]
        run(cmd)

json.dump(report, open("tmp-run/ra26_settle.json", "w"), ensure_ascii=False, indent=1)
print(f"\npicks {len(report['picks'])}  schaduw {len(report['shadow'])}  apply={apply_now}")
for k in ("picks", "shadow"):
    w = sum(1 for x in report[k] if x["result"] == "won")
    l = sum(1 for x in report[k] if x["result"] == "lost")
    v = sum(1 for x in report[k] if x["result"] == "void")
    print(f"  {k}: {w} gewonnen, {l} verloren, {v} void")
