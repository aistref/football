import json
from datetime import date
from scripts import preview
P = "data/run-state/2026-11-17-run-c.json"
s = json.load(open(P))
DAY = date(2026, 11, 17)
EXTRA = {
 "Wales – Portugal": ("UEFA Nations League A (id 9806)", "Over/Under", "Under 3.5", "under-3-5",
   "The Odds API — beste prijs Matchbook 1.66 bruto, 1.6468 netto na 2% commissie (beurs)",
   "Poort 7: Wales mist 0,0% selectiewaarde, Portugal 5,3% (Nuno Tavares 'Doubtful', Rafael Leão tot eind november) — Under heeft geen kant; rust niet meetbaar. "
   "Poort 8: geen kant. Poort 9: LIGHT, raakt niet. Pinnacle 1X2 6.88/5.20/1.43, O/U 3.0 1.86/2.04. Verwacht totaal landenrating 2,84 doelpunten. "
   "Robuustheid krap (zwakste stand +0,94 pp). Verliest bij 4 of meer doelpunten; een ruime Portugese zege is het risico."),
 "Libya – Tunisia": ("CAF Afrika Cup-kwalificatie (id 10608)", "1X2", "2 (Tunisia wint)", "2",
   "BetExplorer marktgemiddelde 2.13 (15 boeken; geen sportkey bij The Odds API) — edge systematisch te laag (§1a)",
   "Poort 5 NIET gemeten: selectiewaarde ontbreekt bij Libya; alleen de landenrating rekent. Poort 7 niet meetbaar (Libya geen selectie); rust niet meetbaar. "
   "Poort 8: Tunisia is de favoriet van de markt (42,9% de-vig), raakt niet. Poort 9: geen Under. BetExplorer-gemiddelde 1X2 3.53/2.92/2.13. "
   "LET OP: model 55,8% tegen markt 42,9% op Tunisia-winst; robuustheid krap (zwakste stand +0,97 pp)."),
 "Ukraine – Georgia": ("UEFA Nations League B (id 9807)", "1X2", "1 (Ukraine wint)", "1",
   "The Odds API — beste prijs Unibet (SE) 2.28 (geen beurs, geen commissie)",
   "Poort 7: geen van beide ploegen mist gemeten selectiewaarde (0,0% / 0,0%); rust niet meetbaar. Poort 8: Ukraine is de marktfavoriet (43,9% de-vig), raakt niet. "
   "Poort 9: geen Under. Pinnacle 1X2 2.15/3.37/3.65. Landenrating +7,58 pp, selectiewaarde +10,56 pp."),
}
n = 0
RANK = {"Wales – Portugal": 1, "Libya – Tunisia": 2, "Ukraine – Georgia": 3}
for comp in s["competitions"].values():
    for m in comp["matches"]:
        if not m.get("bet"): continue
        c = m.pop("_bet"); cid, mk, sel, slug, osrc, extra = EXTRA[m["match"]]; n += 1
        notes = (f"Gepubliceerd op rangorde (§5b): plek {RANK[m['match']]} van 7 selecties die alle poorten halen, over 43 doorgerekende duels (LIGHT); "
                 "MAX_SHORTLIST = 3 (dinsdag). BET op rangorde — onder de lat van 16.0 pp. "
                 f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f}). Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde "
                 + (f"{c['edge_split']:+.2f} pp — beide boven de marktkans, poort 5 gemeten en open." if c['edge_split'] is not None else "niet beschikbaar — poort 5 niet gemeten.") + f" Ruwe kans {c['my_raw']:.4f}, ruwe edge "
                 f"{c['edge_raw']:+.2f} pp; zwakste stand (shrink, rho)-grid {c['edge_robust_min']:+.2f} pp. " + extra +
                 " Afrekenen op de stand na 90 minuten (§6d).")
        h, a = m["home"], m["away"]
        pick = {"id": f"2026-11-17-{cid.split(' (')[0].lower().replace(' ', '-')}-{h.lower().replace(' ', '-')}-{a.lower().replace(' ', '-')}-{slug}",
                "run": "C", "run_date": "2026-11-17", "kickoff": m["kickoff_utc"], "competition": cid, "home": h, "away": a,
                "market": mk, "selection": sel, "odds": c["odds"], "odds_source": osrc,
                "odds_captured_at": "2026-11-17T04:40:00+01:00", "implied_prob": round(c["implied"], 4),
                "my_prob": round(c["my_prob"], 4), "edge_pp": round(c["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
                "prob_sources": m["prob_sources"], "shortlisted": True, "result": "pending", "settled_at": None,
                "settled_score": None, "notes": notes}
        m["pick_id"] = pick["id"]
        m["voorbeschouwing"] = preview.match_block(m["match_id"], DAY, h, a, home_id=m["home_id"], away_id=m["away_id"])
        with open("data/picks.jsonl", "a") as f: f.write(json.dumps(pick, ensure_ascii=False) + "\n")
        print(pick["id"]); print(json.dumps(m["voorbeschouwing"], ensure_ascii=False)[:3000])
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
