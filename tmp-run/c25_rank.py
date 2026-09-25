import json, sys
sys.path.insert(0, '.')

results = json.load(open("tmp-run/c25_pass2.json"))

MAX_SHORTLIST = 5  # vrijdag
MAX_DEEP = 55

rows_for_ranking = []  # per wedstrijd sterkste kwalificerende kandidaat (voor herijkte lijst)
match_summaries = []

for comp, mlist in results.items():
    for r in mlist:
        if r["tier"] not in ("LIGHT",):
            match_summaries.append({"comp": comp, "match": r["match"], "tier": r["tier"],
                                     "kickoff_nl": r["kickoff_nl"], "bet": False,
                                     "reason": r.get("reden", "")})
            continue
        cands = r["all_candidates"]
        # sterkste op ruwe score, voor de rapportagekolom
        strongest_ruw = max(cands, key=lambda c: c["score_ruw"])
        qualifying = [c for c in cands if c["failed_gate"] is None]
        chosen = max(qualifying, key=lambda c: c["score"]) if qualifying else None
        r["bet"] = chosen is not None
        if chosen:
            chosen["gepubliceerd_kandidaat"] = True
            r["bet_selection"] = chosen["selection"]
            r["bet_market"] = chosen["market"]
            rows_for_ranking.append({"comp": comp, "match": r["match"], "cand": chosen, "rec": r})
        match_summaries.append({
            "comp": comp, "match": r["match"], "tier": r["tier"], "kickoff_nl": r["kickoff_nl"],
            "bet": r["bet"],
            "sterkste_ruw": f"{strongest_ruw['market']} {strongest_ruw['selection']} @ {strongest_ruw['odds']:.2f}, edge {strongest_ruw['edge_raw']:+.2f} pp (score_ruw {strongest_ruw['score_ruw']:.3f})",
            "reason": "BET" if r["bet"] else (chosen["failed_gate"] if False else strongest_ruw["failed_gate"] or "?"),
        })

# rangschik over de hele runlijst op herijkte score
rows_for_ranking.sort(key=lambda x: -x["cand"]["score"])
for i, row in enumerate(rows_for_ranking, 1):
    row["rank"] = i

print(f"Aantal duels met een kwalificerende kandidaat (alle 8 poorten open): {len(rows_for_ranking)}")
for row in rows_for_ranking:
    c = row["cand"]
    print(f"  #{row['rank']:2d} {row['match']:35s} {c['market']:15s} {c['selection']:40s} @ {c['odds']:.2f}  edge {c['edge_pp']:+.2f}pp  score {c['score']:.3f}")

with open("tmp-run/c25_ranking.json", "w") as f:
    json.dump({"rows": [{"comp": r["comp"], "match": r["match"], "rank": r["rank"],
                         "cand": r["cand"]} for r in rows_for_ranking],
              "summaries": match_summaries}, f, indent=1, ensure_ascii=False)

with open("tmp-run/c25_pass3.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
