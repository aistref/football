import json
state = json.load(open("data/run-state/2026-09-25-run-c.json"))

order = ["UEFA Nations League A (id 9806)","UEFA Nations League B (id 9807)","UEFA Nations League C (id 9808)",
         "UEFA Nations League D (id 9809)","CAF Afrika Cup-kwalificatie (id 10608)",
         "CONCACAF Nations League (id 9821)","Vriendschappelijke interlands (id 114)",
         "FIFA ASEAN Cup (id 13287)","Arabian Gulf Cup (id 329)"]

print("| Wedstrijd | Competitie | Aftrap NL | Poort5 gemeten? | Sterkste selectie (ruwe score) | Uitkomst |")
print("|---|---|---|---|---|---|")
for comp in order:
    block = state["competitions"].get(comp, {"matches": []})
    for r in block["matches"]:
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

print("\n\n=== NET NIET (near_miss per duel zonder bet) ===")
for comp in order:
    block = state["competitions"].get(comp, {"matches": []})
    for r in block["matches"]:
        nm = r.get("near_miss")
        if nm:
            es = f"{nm['edge_split']:+.2f}" if isinstance(nm.get('edge_split'), (int,float)) else "niet gemeten"
            print(f"| {r['match']} | {nm['market']} — {nm['selection']} | {nm['odds']:.2f} | {nm['edge_xg']:+.2f} | {es} | {nm['edge_robust_min']:+.2f} | {nm['failed_gate']} |")
