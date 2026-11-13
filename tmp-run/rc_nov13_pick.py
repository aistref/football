import json
from datetime import date
from scripts import preview
P = "data/run-state/2026-11-13-run-c.json"
s = json.load(open(P))
DAY = date(2026, 11, 13)
EXTRA = {
 "Scotland – North Macedonia": ("UEFA Nations League B (id 9807)", "BTTS", "BTTS Ja", "btts-ja",
   "The Odds API — beste prijs Pinnacle 2.85 (geen beurs, geen commissie)",
   "Poort 7: North Macedonia en Scotland, zie context (BTTS heeft geen kant; rust niet meetbaar). Poort 8: geen kant. Poort 9: geen Under. "
   "Pinnacle BTTS 2.85/1.44 → de-vig Ja 33,6% (§3 stap 2, alleen ter vergelijking): de markt ziet North Macedonia veel minder vaak scoren dan het model. "
   "Let op: het model ligt bij grote favorieten structureel onder de markt (Scotland 60,9% tegen 79,5%), en deze BTTS leunt op die zelfde afwijking."),
 "Moldova – Kazakhstan": ("UEFA Nations League C (id 9808)", "Over/Under", "Over 2.5", "over-2-5",
   "The Odds API — beste prijs 1xBet 2.58 (geen beurs, geen commissie)",
   "Poort 7: Kazakhstan mist 42,7% selectiewaarde (Satpaev), Moldova 0% — Over heeft geen kant. Poort 8: geen kant. Poort 9: Over-kant, raakt niet. "
   "Pinnacle Over/Under 2 1.80/2.07 (de-vig Over 2 ≈ 53,5%, push bij precies 2), alleen ter vergelijking. "
   "Selectiewaarde-methode slechts +0,71 pp boven de marktkans: poort 5 open, maar krap."),
}
n = 0
for comp in s["competitions"].values():
    for m in comp["matches"]:
        if not m.get("bet"): continue
        c = m.pop("_bet"); cid, mk, sel, slug, osrc, extra = EXTRA[m["match"]]; n += 1
        notes = (f"Gepubliceerd op rangorde (§5b): plek {n} van 2 selecties die alle poorten halen, over 27 doorgerekende duels (LIGHT); "
                 "MAX_SHORTLIST = 5 (vrijdag). BET op rangorde — onder de lat van 16.0 pp. "
                 f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f}). Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde "
                 f"{c['edge_split']:+.2f} pp — beide boven de marktkans, poort 5 gemeten en open. Ruwe kans {c['my_raw']:.4f}, ruwe edge "
                 f"{c['edge_raw']:+.2f} pp; zwakste stand (shrink, rho)-grid {c['edge_robust_min']:+.2f} pp. " + extra +
                 " Afrekenen op de stand na 90 minuten (§6d).")
        h, a = m["home"], m["away"]
        pick = {"id": f"2026-11-13-{cid.split(' (')[0].lower().replace(' ', '-')}-{h.lower().replace(' ', '-')}-{a.lower().replace(' ', '-')}-{slug}",
                "run": "C", "run_date": "2026-11-13", "kickoff": m["kickoff_utc"], "competition": cid, "home": h, "away": a,
                "market": mk, "selection": sel, "odds": c["odds"], "odds_source": osrc,
                "odds_captured_at": "2026-11-13T04:22:00+01:00", "implied_prob": round(c["implied"], 4),
                "my_prob": round(c["my_prob"], 4), "edge_pp": round(c["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
                "prob_sources": m["prob_sources"], "shortlisted": True, "result": "pending", "settled_at": None,
                "settled_score": None, "notes": notes}
        m["pick_id"] = pick["id"]
        m["voorbeschouwing"] = preview.match_block(m["match_id"], DAY, h, a, home_id=m["home_id"], away_id=m["away_id"])
        with open("data/picks.jsonl", "a") as f: f.write(json.dumps(pick, ensure_ascii=False) + "\n")
        print(pick["id"]); print(json.dumps(m["voorbeschouwing"], ensure_ascii=False)[:3000])
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
