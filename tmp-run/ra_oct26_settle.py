"""Stage 0 — Run A 26 okt 2026: de 11 afwikkelbare picks van 24/25 okt.

Alle elf zijn competitiewedstrijden (MLS, 2.Bundesliga, Swiss Super League, Eredivisie,
Premier League, Serie A, La Liga, Eliteserien) — geen knock-out, dus `status.scoreStr`
van Fotmob *is* de stand na 90 minuten (§6d).
"""
import json, re, subprocess, unicodedata
from datetime import date
from scripts import fotmob

DAYS = [date(2026, 10, 24), date(2026, 10, 25)]

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
                          "finished": st.get("finished"),
                          "home": m["home"]["name"], "away": m["away"]["name"]}
print("fixtures geindexeerd:", len(index))

def find(home, away):
    hit = index.get((norm(home), norm(away)))
    if hit:
        return hit
    cand = [v for k, v in index.items()
            if k[0].startswith(norm(home)[:6]) and k[1].startswith(norm(away)[:6])]
    return cand[0] if len(cand) == 1 else None

def settle_ou(sel, hg, ag):
    tot = hg + ag
    m = re.search(r"(Over|Under)\s+([\d.]+)", sel, re.I)
    side, line = m.group(1).lower(), float(m.group(2))
    if abs(tot - line) < 1e-9:
        return "void", None
    if side == "over":
        return ("won" if tot > line else "lost"), None
    return ("won" if tot < line else "lost"), None

def settle_btts(sel, hg, ag):
    both = hg > 0 and ag > 0
    nee = "nee" in sel.lower()
    hit = (not both) if nee else both
    return ("won" if hit else "lost"), None

rows = []
for l in open("data/picks.jsonl"):
    d = json.loads(l)
    if d.get("result") != "pending":
        continue
    rows.append(d)

out = []
for d in rows:
    home, away = d["home"], d["away"]
    f = find(home, away)
    if not f or not f.get("finished"):
        out.append({"id": d["id"], "actie": "wacht", "reden": "niet afgelopen of niet gevonden"})
        continue
    hg, ag = (int(x) for x in f["score"].replace("–", "-").split("-"))
    mk = d["market"]
    if mk == "Over/Under":
        res, units = settle_ou(d["selection"], hg, ag)
    elif mk == "BTTS":
        res, units = settle_btts(d["selection"], hg, ag)
    else:
        out.append({"id": d["id"], "actie": "HANDMATIG", "markt": mk, "score": f["score"]})
        continue
    out.append({"id": d["id"], "wedstrijd": f'{home} - {away}', "comp": f["league"],
                "markt": mk, "selectie": d["selection"], "odds": d["odds"],
                "score": f"{hg}-{ag}", "totaal": hg + ag, "result": res})

json.dump(out, open("tmp-run/ra_oct26_settle.json", "w"), ensure_ascii=False, indent=1)
for o in out:
    print(o.get("result", o.get("actie")), "|", o.get("wedstrijd", o["id"]), "|",
          o.get("selectie", ""), "|", o.get("score", ""))
