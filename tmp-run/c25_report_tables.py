import json, sys
sys.path.insert(0, '.')
results = json.load(open("tmp-run/c25_pass3.json"))

order = ["UEFA Nations League A (id 9806)","UEFA Nations League B (id 9807)","UEFA Nations League C (id 9808)",
         "UEFA Nations League D (id 9809)","CAF Afrika Cup-kwalificatie (id 10608)",
         "CONCACAF Nations League (id 9821)","Vriendschappelijke interlands (id 114)",
         "FIFA ASEAN Cup (id 13287)","Arabian Gulf Cup (id 329)"]

print("| Wedstrijd | Competitie | Aftrap NL | Poort5 | Sterkste selectie (ruwe score) | Uitkomst |")
print("|---|---|---|---|---|---|")
near_misses = []
for comp in order:
    for r in results.get(comp, []):
        if r["tier"] == "BUITEN_DATADEKKING":
            print(f"| {r['match']} | {comp} | {r['kickoff_nl']} | — | — | BUITEN DATADEKKING — {r['reden']} |")
            continue
        if r["tier"] == "NONE":
            print(f"| {r['match']} | {comp} | {r['kickoff_nl']} | — | — | GEEN BET — NONE: {r['reden']} |")
            continue
        cands = r["all_candidates"]
        strongest = max(cands, key=lambda c: c["score_ruw"])
        p5 = "nee" if r["poort5_niet_gemeten"] else "ja"
        if r.get("bet"):
            outcome = f"**BET** — {r['bet_market']} {r['bet_selection']}"
        else:
            outcome = f"GEEN BET — {strongest['failed_gate']}"
        print(f"| {r['match']} | {comp} | {r['kickoff_nl']} | {p5} | {strongest['market']} {strongest['selection']} @ {strongest['odds']:.2f}, edge {strongest['edge_raw']:+.2f} pp | {outcome} |")

        # near miss: candidate with real positive edge (raw or herijkt) that failed a gate, strongest by score_ruw among failed
        failed = [c for c in cands if c["failed_gate"] is not None and c["failed_gate"] != "odds"]
        if failed:
            nm = max(failed, key=lambda c: c["score_ruw"])
            if nm["edge_raw"] > 0 or nm["edge_pp"] > 0:
                near_misses.append((comp, r["match"], nm))

print("\n\n=== NEAR MISS (voor 'Net niet' en shadow.jsonl) ===")
for comp, match, nm in near_misses:
    print(f"{match} | {nm['market']} {nm['selection']} | odds {nm['odds']:.2f} | edge_xg {nm['edge_xg']:+.2f} | edge_split {nm['edge_split']} | edge_robust_min {nm['edge_robust_min']:+.2f} | valt af op: {nm['failed_gate']}")
