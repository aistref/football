import json
from datetime import date
from scripts import preview
P = "data/run-state/2026-11-14-run-c.json"
s = json.load(open(P))
DAY = date(2026, 11, 14)
EXTRA = {
 "Norway – Wales": ("UEFA Nations League A (id 9806)", "Over/Under", "Under 3.5", "under-3-5",
   "The Odds API — beste prijs Matchbook 1.88 (beurs, netto 1.8624 na 2% commissie)",
   "Poort 7: Norway mist 1,0% selectiewaarde (Langås), Wales 0% — Under heeft geen kant; rust niet meetbaar. Poort 8: geen kant. Poort 9: LIGHT, raakt niet. "
   "Pinnacle O/U 3.25 1.82/2.07, alleen ter vergelijking. Let op: het model ligt bij Norway ver onder de markt (53,9% tegen 78,2% op winst), "
   "en deze Under leunt deels op die zelfde afwijking; de selectiewaarde-methode draagt het grootste deel (+17,96 pp tegen +6,77 pp landenrating)."),
 "Georgia – Hungary": ("UEFA Nations League B (id 9807)", "Over/Under", "Over 2", "over-2",
   "The Odds API — beste prijs Pinnacle 1.87 (geen beurs, geen commissie)",
   "Poort 7: geen uitvallers bij beide ploegen — Over heeft geen kant; rust niet meetbaar. Poort 8: geen kant. Poort 9: Over-kant, raakt niet. "
   "Push bij precies 2 doelpunten. Model en markt liggen op 1X2 dicht bij elkaar (Georgia 33,5% tegen 30,5%)."),
}
n = 0
for comp in s["competitions"].values():
    for m in comp["matches"]:
        if not m.get("bet"): continue
        c = m.pop("_bet"); cid, mk, sel, slug, osrc, extra = EXTRA[m["match"]]; n += 1
        notes = (f"Gepubliceerd op rangorde (§5b): plek {n} van 2 selecties die alle poorten halen, over 16 doorgerekende duels (LIGHT); "
                 "MAX_SHORTLIST = 5 (zaterdag). BET op rangorde — onder de lat van 16.0 pp. "
                 f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f}). Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde "
                 f"{c['edge_split']:+.2f} pp — beide boven de marktkans, poort 5 gemeten en open. Ruwe kans {c['my_raw']:.4f}, ruwe edge "
                 f"{c['edge_raw']:+.2f} pp; zwakste stand (shrink, rho)-grid {c['edge_robust_min']:+.2f} pp. " + extra +
                 " Afrekenen op de stand na 90 minuten (§6d).")
        h, a = m["home"], m["away"]
        pick = {"id": f"2026-11-14-{cid.split(' (')[0].lower().replace(' ', '-')}-{h.lower().replace(' ', '-')}-{a.lower().replace(' ', '-')}-{slug}",
                "run": "C", "run_date": "2026-11-14", "kickoff": m["kickoff_utc"], "competition": cid, "home": h, "away": a,
                "market": mk, "selection": sel, "odds": c["odds"], "odds_source": osrc,
                "odds_captured_at": "2026-11-14T04:25:00+01:00", "implied_prob": round(c["implied"], 4),
                "my_prob": round(c["my_prob"], 4), "edge_pp": round(c["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
                "prob_sources": m["prob_sources"], "shortlisted": True, "result": "pending", "settled_at": None,
                "settled_score": None, "notes": notes}
        m["pick_id"] = pick["id"]
        m["voorbeschouwing"] = preview.match_block(m["match_id"], DAY, h, a, home_id=m["home_id"], away_id=m["away_id"])
        with open("data/picks.jsonl", "a") as f: f.write(json.dumps(pick, ensure_ascii=False) + "\n")
        print(pick["id"]); print(json.dumps(m["voorbeschouwing"], ensure_ascii=False)[:3500])
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
