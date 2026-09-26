import json, re, unicodedata

comps = json.load(open("tmp-run/rc26_competitions.json"))
DATE = "2026-09-26"
CAPTURED_AT = "2026-09-26T05:35:00+02:00"

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

picks = []
for comp_id, v in comps.items():
    comp_name = re.sub(r"\s*\(id \d+\)$", "", comp_id)
    for m in v["matches"]:
        if not m.get("bet"):
            continue
        c = m["_best_qual"]
        confidence = "Low"
        note_parts = [m["_note_rank"]]
        score_line = f"selection_score {c['score']:.3f} (ruw {c['score_ruw']:.3f})."
        note_parts.append(score_line)
        if not m["poort5_niet_gemeten"]:
            note_parts.append(
                f"Landenrating {c['edge_xg']:+.2f} pp, selectiewaarde {c['edge_split']:+.2f} pp — "
                f"beide boven de marktkans, dus poort 5 (tweede methode) is gemeten en open.")
        else:
            note_parts.append("Poort 5 (tweede methode) kon niet gemeten worden — selectie te dun bij "
                               "minstens één ploeg; gerekend met de landenrating alleen.")
        note_parts.append(f"Ruwe kans {c['my_raw']:.4f}, ruwe edge {c['edge_raw']:+.2f} pp; "
                           f"zwakste stand (shrink, rho)-grid (methode 1, landenrating) {c['edge_robust_min']:+.2f} pp.")
        note_parts.append(f"Poort 7 (context, via squadform.injuries): {c['context_reason']}")
        note_parts.append(f"Poort 8 (underdog): {c['underdog_reason']}")
        if c["would_block_underdog"]:
            note_parts.append(
                f"poort8_zou_hebben_geblokkeerd: JA — deze selectie stond op de underdog-kant onder "
                f"UNDERDOG_FLOOR (0.35) en zou vóór 25 sep 2026 zijn tegengehouden. De poort is op "
                f"25 sep 2026 vervallen (sides.LAPSES_ON), dus hij is toch gepubliceerd. Zie "
                f"run-c.md/§1e: dit is de meting die sinds 25 sep loopt.")
        note_parts.append("Afrekenen op de stand na 90 minuten (§6d), nooit op verlenging/strafschoppen.")
        notes = " ".join(note_parts)

        pid = f"{DATE}-{slug(comp_name)}-{slug(m['home'])}-{slug(m['away'])}-{slug(c['market'])}-{slug(c['selection'])}"
        pick = {
            "id": pid,
            "run": "C",
            "run_date": DATE,
            "kickoff": m["kickoff_utc"],
            "competition": comp_id,
            "home": m["home"],
            "away": m["away"],
            "market": c["market"],
            "selection": c["selection"],
            "odds": c["odds"],
            "odds_source": c["odds_source"],
            "odds_captured_at": CAPTURED_AT,
            "implied_prob": round(c["implied"], 4),
            "my_prob": round(c["my_prob"], 4),
            "edge_pp": round(c["edge_pp"], 2),
            "data_tier": "LIGHT",
            "confidence": confidence,
            "prob_sources": m["prob_sources"],
            "shortlisted": True,
            "result": "pending",
            "settled_at": None,
            "settled_score": None,
            "notes": notes,
        }
        picks.append(pick)

json.dump(picks, open("tmp-run/rc26_picks.json", "w"), indent=1, ensure_ascii=False)
for p in picks:
    print(p["id"], p["market"], p["selection"], p["odds"], p["edge_pp"])
