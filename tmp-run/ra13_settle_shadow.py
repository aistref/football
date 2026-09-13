"""Stage 0 (schaduw) — Run A 13 sep 2026: de 32 openstaande schaduwpicks van 12 sep afwikkelen.

Rekent af op de stand na 90 minuten (§6d). Alle 32 rijen komen uit nationale competities, dus er
is geen verlenging en `status.scoreStr` van Fotmob *is* de stand na 90 minuten; bij een bekerduel
zou dat niet gelden en moesten de doelpuntminuten erbij worden gezocht.

Nieuw ten opzichte van `settle_shadow.py` (1 sep): de uitkomst per markt wordt hier *uitgerekend*
in plaats van met de hand opgezocht. Dat is nodig omdat 32 rijen over zes markten lopen, en het
maakt bovendien de kwartlijn expliciet — een AH op een kwartlijn splitst in twee halve bets en kan
dus half winnen of half verliezen (`settled_units`), precies zoals `ledger.pick_units` rekent.
"""
import json, re, sys, unicodedata
from datetime import date
from scripts import fotmob

DAY = date(2026, 9, 12)


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


fx = fotmob.fetch_fixtures(DAY)
index = {}
for lg in fx.get("leagues", []):
    for m in lg.get("matches", []):
        st = m.get("status", {}) or {}
        index[(norm(m["home"]["name"]), norm(m["away"]["name"]))] = {
            "league": lg.get("name"), "score": st.get("scoreStr"),
            "finished": st.get("finished"), "home": m["home"]["name"], "away": m["away"]["name"]}
print("fixtures 12 sep:", len(index))


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
    """Welke kant de selectie speelt, op de genormaliseerde naam."""
    t = norm(text)
    for side, name in (("home", home), ("away", away)):
        n = norm(name)
        if n and (n in t or t.startswith(n[:6]) or n[:6] in t):
            return side
    return None


def ah_units(line, side, gh, ga):
    """Netto resultaat bij 1u inzet op een Aziatische handicap, incl. kwart- en pushlijnen."""
    margin = (gh - ga) if side == "home" else (ga - gh)
    # Een kwartlijn is twee halve bets op de twee hele/halve lijnen eromheen.
    if abs(line * 4) % 2 == 1:
        return (ah_units(line - 0.25, side, gh, ga) + ah_units(line + 0.25, side, gh, ga)) / 2
    d = margin + line
    if d > 0:
        return 1.0
    if d < 0:
        return -1.0
    return 0.0


def totals_units(line, over, gh, ga):
    tot = gh + ga
    if abs(line * 4) % 2 == 1:
        return (totals_units(line - 0.25, over, gh, ga) + totals_units(line + 0.25, over, gh, ga)) / 2
    d = (tot - line) if over else (line - tot)
    return 1.0 if d > 0 else (-1.0 if d < 0 else 0.0)


def evaluate(market, home, away, gh, ga):
    """(result, units) — units alleen bij een halve uitkomst, anders None."""
    m = market
    if m.startswith("1X2"):
        if "gelijkspel" in m or re.search(r"—\s*X\b", m):
            return ("won" if gh == ga else "lost"), None
        side = "home" if re.search(r"—\s*1\b", m) else ("away" if re.search(r"—\s*2\b", m) else
                                                        side_of(m.split("—")[-1], home, away))
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
        mm = re.search(r"([+-]?\d+(?:\.\d+)?)\s*$", tail.strip())
        if not mm:
            mm = re.search(r"([+-]\d+(?:\.\d+)?)", tail)
        line = float(mm.group(1))
        side = side_of(re.sub(r"AH|[+-]?\d+(\.\d+)?", " ", tail), home, away)
        u = ah_units(line, side, gh, ga)
        return ("won" if u > 0 else ("lost" if u < 0 else "void")), (u if abs(u) not in (0.0, 1.0) else None)
    if m.startswith("Over/Under"):
        mm = re.search(r"(Over|Under)\s+(\d+(?:\.\d+)?)", m, re.I)
        over = mm.group(1).lower() == "over"
        u = totals_units(float(mm.group(2)), over, gh, ga)
        return ("won" if u > 0 else ("lost" if u < 0 else "void")), (u if abs(u) not in (0.0, 1.0) else None)
    if m.startswith("BTTS"):
        ja = m.rstrip().endswith("ja")
        both = gh > 0 and ga > 0
        return ("won" if both == ja else "lost"), None
    raise ValueError(f"onbekende markt: {m}")


rows = [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]
todo = [r for r in rows if r["result"] == "pending"]
out = []
for r in todo:
    h, a = [x.strip() for x in r["match"].split("–")]
    hit = find(h, a)
    if not hit or not hit.get("finished") or not hit.get("score"):
        print(f"MIS {r['match']:42s} geen afgelopen wedstrijd gevonden")
        out.append({"id": r["id"], "found": False})
        continue
    gh, ga = [int(x) for x in re.split(r"\s*-\s*", hit["score"])]
    res, units = evaluate(r["market"], hit["home"], hit["away"], gh, ga)
    out.append({"id": r["id"], "found": True, "score": f"{gh}-{ga}", "result": res,
                "units": units, "match": r["match"], "market": r["market"],
                "failed_gate": r["failed_gate"], "odds": r["odds"]})
    print(f"OK  {r['match'][:36]:36s} {hit['score']:7s} {r['market'][:42]:42s} -> {res}"
          + (f" ({units:+.2f}u)" if units is not None else ""))

json.dump(out, open("tmp-run/ra13_shadow_results.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal", len(out), "gevonden", sum(o["found"] for o in out))
