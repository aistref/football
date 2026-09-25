import json, re, sys
sys.path.insert(0, '.')

state = json.load(open("data/run-state/2026-09-25-run-c.json"))

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def slug_sel(sel):
    return re.sub(r"[^a-z0-9]+", "-", sel.lower()).strip("-")

CAPTURED_AT = "2026-09-25T05:30:00+02:00"

picks = []
for comp, block in state["competitions"].items():
    for m in block.get("matches", []):
        if not m.get("bet"):
            continue
        cand = next(c for c in m["all_candidates"] if c.get("gepubliceerd_kandidaat"))
        comp_slug = slug(comp.split(" (id")[0])
        pid = f"2026-09-25-{comp_slug}-{slug(m['home'])}-{slug(m['away'])}-{slug(cand['market'])}-{slug_sel(cand['selection'])}"[:160]

        notes_parts = []
        notes_parts.append(
            f"Gepubliceerd op rangorde (§5b): plek {m['bet_rank']} van 4 kwalificerende selecties "
            f"over 27 doorgerekende duels (LIGHT), MAX_SHORTLIST=5 (vrijdag) niet bereikt — de "
            f"drempel van 16.0 pp werkt hier dus als label, niet als veto. selection_score {cand['score']:.3f} "
            f"(ruw {cand['score_ruw']:.3f}).")
        if m["poort5_niet_gemeten"]:
            notes_parts.append("Poort 5 NIET gemeten: de selectiewaarde was voor minstens één ploeg "
                                "te dun (< 11 spelers met waarde of < €1 mln); my_prob draait alleen "
                                "op de landenrating.")
        else:
            notes_parts.append(f"Landenrating {cand['edge_xg']:+.2f} pp, selectiewaarde "
                                f"{cand['edge_split']:+.2f} pp — beide boven de marktkans, dus poort 5 "
                                f"(tweede methode) is gemeten en open.")
        notes_parts.append(f"Ruwe kans {cand['my_raw']:.4f}, ruwe edge {cand['edge_raw']:+.2f} pp; "
                            f"zwakste stand (shrink, rho)-grid (methode 1, landenrating) "
                            f"{cand['edge_robust_min']:+.2f} pp.")
        notes_parts.append(f"Poort 7 (context, via squadform.injuries): {cand['context_reason']}")
        notes_parts.append(f"Poort 8 (underdog): {cand['underdog_reason']}")
        if cand.get("would_block_underdog"):
            notes_parts.append("poort8_zou_hebben_geblokkeerd: JA — deze selectie stond op de "
                                "underdog-kant onder UNDERDOG_FLOOR (0.35) en zou vóór 25 sep 2026 "
                                "zijn tegengehouden. De poort is vandaag vervallen (sides.LAPSES_ON), "
                                "dus hij is toch gepubliceerd. Zie run-c.md/§1e: dit is precies de "
                                "meting die vanaf vandaag moet gaan lopen.")
        notes_parts.append("Afrekenen op de stand na 90 minuten (§6d), nooit op verlenging/strafschoppen.")

        prob_sources = list(m["prob_sources"])
        h = m["context"]["home"]; a = m["context"]["away"]
        prob_sources.append(
            f"scripts/squadform.injuries — poort 7: {h['name']} mist {(h['out_share'] or 0)*100:.1f}% "
            f"selectiewaarde, {a['name']} {(a['out_share'] or 0)*100:.1f}%")

        pick = {
            "id": pid, "run": "C", "run_date": "2026-09-25", "kickoff": m["kickoff_utc"],
            "competition": comp, "home": m["home"], "away": m["away"],
            "market": cand["market"], "selection": cand["selection"],
            "odds": cand["odds"], "odds_source": cand["odds_source"],
            "odds_captured_at": CAPTURED_AT,
            "implied_prob": round(cand["implied"], 4), "my_prob": round(cand["my_prob"], 4),
            "edge_pp": round(cand["edge_pp"], 2), "data_tier": "LIGHT", "confidence": "Low",
            "prob_sources": prob_sources, "shortlisted": True, "result": "pending",
            "notes": " ".join(notes_parts),
        }
        picks.append(pick)

with open("tmp-run/c25_new_picks.json", "w") as f:
    json.dump(picks, f, indent=1, ensure_ascii=False)
for p in picks:
    print(p["id"])
