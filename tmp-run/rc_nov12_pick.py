import json
from datetime import date
from scripts import preview
P = "data/run-state/2026-11-12-run-c.json"
s = json.load(open(P))
m = [x for x in s["competitions"]["UEFA Nations League A (id 9806)"]["matches"] if x["home"] == "England"][0]
c = m.pop("_bet")
notes = ("Gepubliceerd op rangorde (§5b): plek 1 van 1 selectie die alle poorten haalt, over 20 doorgerekende duels "
         "(LIGHT); MAX_SHORTLIST = 3 (donderdag). BET op rangorde — onder de lat van 16.0 pp. "
         f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f}). Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde "
         f"{c['edge_split']:+.2f} pp — beide boven de marktkans, poort 5 gemeten en open. Ruwe kans {c['my_raw']:.4f}, ruwe edge "
         f"{c['edge_raw']:+.2f} pp; zwakste stand (shrink, rho)-grid {c['edge_robust_min']:+.2f} pp. Poort 7: Croatia mist 12,2% "
         "selectiewaarde, England 4,8% (BTTS heeft geen kant; rust niet meetbaar). Poort 8: geen kant. Poort 9: geen Under. "
         "Matchbook is een beurs: 2.04 bruto, 2.0192 na 2% commissie. Pinnacle BTTS 1.96/1.87 (de-vig Ja 48,8%). "
         "Afrekenen op de stand na 90 minuten (§6d).")
pick = {"id": "2026-11-12-uefa-nations-league-a-england-croatia-btts-btts-ja", "run": "C", "run_date": "2026-11-12",
        "kickoff": m["kickoff_utc"], "competition": "UEFA Nations League A (id 9806)", "home": "England", "away": "Croatia",
        "market": "BTTS", "selection": "BTTS Ja", "odds": c["odds"],
        "odds_source": "The Odds API — beste prijs Matchbook, beurs: 2.04 bruto / 2.0192 na 2% commissie",
        "odds_captured_at": "2026-11-12T04:30:00+01:00", "implied_prob": round(c["implied"], 4),
        "my_prob": round(c["my_prob"], 4), "edge_pp": round(c["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
        "prob_sources": m["prob_sources"], "shortlisted": True, "result": "pending", "settled_at": None,
        "settled_score": None, "notes": notes}
m["pick_id"] = pick["id"]
m["voorbeschouwing"] = preview.match_block(m["match_id"], date(2026, 11, 12), "England", "Croatia",
                                            home_id=m["home_id"], away_id=m["away_id"])
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
with open("data/picks.jsonl", "a") as f: f.write(json.dumps(pick, ensure_ascii=False) + "\n")
print(json.dumps(m["voorbeschouwing"], ensure_ascii=False, indent=1)[:5000])
