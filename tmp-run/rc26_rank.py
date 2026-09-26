import json

results = json.load(open("tmp-run/rc26_pass2.json"))

all_rows = []   # per match: best qualifying candidate (or None) + near_miss info
for comp, ms in results.items():
    for r in ms:
        if r.get("tier") == "NONE":
            all_rows.append({"comp": comp, "match": r["match"], "tier": "NONE", "bet": None,
                              "reason": "data", "detail": r.get("data_reason")})
            continue
        if r.get("buiten_datadekking"):
            all_rows.append({"comp": comp, "match": r["match"], "tier": r.get("tier"), "bet": None,
                              "reason": "buiten_datadekking", "detail": None})
            continue
        cands = r["all_candidates"]
        qualifying = [c for c in cands if c["failed_gate"] is None]
        best_qual = max(qualifying, key=lambda c: c["score"]) if qualifying else None
        # sterkste kandidaat ongeacht poorten (voor "Net niet"), op ruwe score
        best_any = max(cands, key=lambda c: c["score_ruw"]) if cands else None
        all_rows.append({
            "comp": comp, "match": r["match"], "tier": r["tier"],
            "bet": best_qual, "best_any": best_any, "n_candidates": len(cands),
            "poort5_niet_gemeten": r.get("poort5_niet_gemeten"),
        })

# rangorde over alle wedstrijden op selection_score van de beste kwalificerende selectie
ranked = [row for row in all_rows if row.get("bet") is not None]
ranked.sort(key=lambda row: -row["bet"]["score"])

print(f"Aantal wedstrijden totaal: {len(all_rows)}")
print(f"Aantal met een kwalificerende selectie (alle 8 poorten): {len(ranked)}")
for row in ranked:
    b = row["bet"]
    print(f"  {row['comp']:30s} {row['match']:40s} {b['market']:15s} {b['selection_label']:35s} "
          f"odds={b['odds']:.2f} edge={b['edge_pp']:.2f}pp score={b['score']:.3f}")

json.dump(all_rows, open("tmp-run/rc26_allrows.json", "w"), indent=1, ensure_ascii=False)
