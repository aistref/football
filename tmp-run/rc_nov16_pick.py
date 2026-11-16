import json
from datetime import date
from scripts import preview
P = "data/run-state/2026-11-16-run-c.json"
s = json.load(open(P))
DAY = date(2026, 11, 16)
EXTRA = {
 "Greece – Serbia": ("UEFA Nations League A (id 9806)", "Over/Under", "Under 2.75", "under-2-75",
   "The Odds API — beste prijs Pinnacle 1.99 (geen beurs, geen commissie)",
   "Poort 7: Greece mist 0,6% selectiewaarde (Michailidis, Pelkas), Serbia 0,6% (Terzić) — Under heeft geen kant; rust niet meetbaar. Poort 8: geen kant. "
   "Poort 9: LIGHT, raakt niet. Pinnacle 1X2 1.46/4.85/7.00, O/U 2.75 1.90/1.99. LET OP: het model ligt ver van de markt op 1X2 "
   "(Greece 42,8% tegen 66,3%, Serbia 29,0% tegen 13,8%); een markt die Serbia op 7.00 zet, prijst iets in wat de landenrating niet ziet "
   "(rotatie of een ploeg zonder belang). Gaat Greece ruim winnen, dan breekt deze Under. Half verlies bij precies 3 doelpunten."),
 "Gibraltar – Malta": ("UEFA Nations League D (id 9809)", "BTTS", "BTTS Ja", "btts-ja",
   "The Odds API — beste prijs Pinnacle 2.70 (geen beurs, geen commissie)",
   "Poort 7: BTTS heeft geen kant; rust niet meetbaar. Poort 8: geen kant. Poort 9: geen Under. Pinnacle 1X2 7.17/3.80/1.52, BTTS 2.70/1.46. "
   "LET OP: het model geeft Gibraltar veel meer dan de markt (22,2% tegen 12,8% op winst) en de BTTS-kans leunt op diezelfde afwijking: "
   "Gibraltar moet scoren."),
 "Switzerland – Scotland": ("UEFA Nations League B (id 9807)", "Over/Under", "Over 2.5", "over-2-5",
   "The Odds API — beste prijs LeoVegas (SE) 2.23 (geen beurs, geen commissie)",
   "Poort 7: Switzerland mist 7,3% selectiewaarde (Rodríguez, Monteiro, Boteli), Scotland 0,8% — Over heeft geen kant; rust niet meetbaar. "
   "Poort 8: geen kant. Poort 9: Over-kant, raakt niet. Pinnacle O/U 2.25 1.85/2.03, 1X2 1.79/3.69/4.80. De landenrating draagt "
   "het grootste deel (+11,74 pp tegen +2,84 pp selectiewaarde); verwacht totaal 2,95 doelpunten."),
}
n = 0
for comp in s["competitions"].values():
    for m in comp["matches"]:
        if not m.get("bet"): continue
        c = m.pop("_bet"); cid, mk, sel, slug, osrc, extra = EXTRA[m["match"]]; n += 1
        notes = (f"Gepubliceerd op rangorde (§5b): plek {n} van 6 selecties die alle poorten halen, over 17 doorgerekende duels (LIGHT); "
                 "MAX_SHORTLIST = 3 (maandag). BET op rangorde — onder de lat van 16.0 pp. "
                 f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f}). Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde "
                 f"{c['edge_split']:+.2f} pp — beide boven de marktkans, poort 5 gemeten en open. Ruwe kans {c['my_raw']:.4f}, ruwe edge "
                 f"{c['edge_raw']:+.2f} pp; zwakste stand (shrink, rho)-grid {c['edge_robust_min']:+.2f} pp. " + extra +
                 " Afrekenen op de stand na 90 minuten (§6d).")
        h, a = m["home"], m["away"]
        pick = {"id": f"2026-11-16-{cid.split(' (')[0].lower().replace(' ', '-')}-{h.lower().replace(' ', '-')}-{a.lower().replace(' ', '-')}-{slug}",
                "run": "C", "run_date": "2026-11-16", "kickoff": m["kickoff_utc"], "competition": cid, "home": h, "away": a,
                "market": mk, "selection": sel, "odds": c["odds"], "odds_source": osrc,
                "odds_captured_at": "2026-11-16T05:30:00+01:00", "implied_prob": round(c["implied"], 4),
                "my_prob": round(c["my_prob"], 4), "edge_pp": round(c["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
                "prob_sources": m["prob_sources"], "shortlisted": True, "result": "pending", "settled_at": None,
                "settled_score": None, "notes": notes}
        m["pick_id"] = pick["id"]
        m["voorbeschouwing"] = preview.match_block(m["match_id"], DAY, h, a, home_id=m["home_id"], away_id=m["away_id"])
        with open("data/picks.jsonl", "a") as f: f.write(json.dumps(pick, ensure_ascii=False) + "\n")
        print(pick["id"]); print(json.dumps(m["voorbeschouwing"], ensure_ascii=False)[:3000])
json.dump(s, open(P, "w"), indent=1, ensure_ascii=False)
