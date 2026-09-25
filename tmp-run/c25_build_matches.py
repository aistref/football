import json, re, sys
sys.path.insert(0, '.')

runlist = json.load(open("tmp-run/c25_runlist.json"))
odds_nl = json.load(open("tmp-run/c25_odds_nl.json"))
bx = json.load(open("tmp-run/c25_bx.json"))

ALIASES = {
    "turkiye": "turkey",
    "guinea bissau": "guinea bissau",
}

def norm(s):
    s = (s or "").lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = s.strip()
    s = ALIASES.get(s, s)
    return s

# Build NL odds lookup by normalized (home,away)
nl_by_pair = {}
for e in odds_nl:
    key = (norm(e["home_team"]), norm(e["away_team"]))
    nl_by_pair[key] = e

# Build BX odds lookup per competition-bucket, normalized pair -> MatchOdds dict
bx_by_bucket = {}
for bucket, rows in bx.items():
    if isinstance(rows, dict) and "error" in rows:
        bx_by_bucket[bucket] = {}
        continue
    d = {}
    for r in rows:
        key = (norm(r["home"]), norm(r["away"]))
        d[key] = r
    bx_by_bucket[bucket] = d

bucket_for_comp = {
    "CAF Afrika Cup-kwalificatie (id 10608)": "afcon",
    "CONCACAF Nations League (id 9821)": "concacaf_nl",
    "Vriendschappelijke interlands (id 114)": "friendlies",
    "FIFA ASEAN Cup (id 13287)": "asean",
}

report = []
matches_out = {}
for comp, matches in runlist.items():
    if not matches:
        continue
    matches_out[comp] = []
    for m in matches:
        key = (norm(m["home"]), norm(m["away"]))
        rec = dict(m)
        if comp in ("UEFA Nations League A (id 9806)", "UEFA Nations League B (id 9807)",
                     "UEFA Nations League C (id 9808)"):
            ev = nl_by_pair.get(key)
            if ev is None:
                report.append((comp, m["home"], m["away"], "GEEN MATCH in Odds API data"))
                rec["odds_event"] = None
            else:
                rec["odds_event"] = ev
        else:
            bucket = bucket_for_comp.get(comp)
            bxd = bx_by_bucket.get(bucket, {})
            row = bxd.get(key)
            if row is None:
                report.append((comp, m["home"], m["away"], f"GEEN MATCH in BetExplorer ({bucket})"))
                rec["bx_odds"] = None
            else:
                rec["bx_odds"] = row
        matches_out[comp].append(rec)

print("Onopgeloste koppelingen:")
for r in report:
    print(" ", r)

with open("tmp-run/c25_matches_with_odds.json", "w") as f:
    json.dump(matches_out, f, indent=1, ensure_ascii=False)

n_with_price = sum(1 for c in matches_out.values() for m in c if m.get("odds_event") or m.get("bx_odds"))
n_total = sum(len(v) for v in matches_out.values())
print(f"\n{n_with_price} van {n_total} duels hebben een prijs gevonden")
