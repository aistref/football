"""Bouwt data/run-state/2026-09-26-run-c.json in het juiste schema, en tel af naar picks."""
import json
from datetime import datetime, timezone

pass2 = json.load(open("tmp-run/rc26_pass2.json"))
allrows = json.load(open("tmp-run/rc26_allrows.json"))

COMP_ID = {
    "Vriendschappelijke interlands": "Vriendschappelijke interlands (id 114)",
    "UEFA Nations League A": "UEFA Nations League A (id 9806)",
    "UEFA Nations League B": "UEFA Nations League B (id 9807)",
    "UEFA Nations League C": "UEFA Nations League C (id 9808)",
    "UEFA Nations League D": "UEFA Nations League D (id 9809)",
    "CONCACAF Nations League": "CONCACAF Nations League (id 9821)",
    "CAF Afrika Cup-kwalificatie": "CAF Afrika Cup-kwalificatie (id 10608)",
    "Arabian Gulf Cup": "Arabian Gulf Cup (id 329)",
    "FIFA ASEAN Cup": "FIFA ASEAN Cup (id 13287)",
}

MARKET_LABELS = ["1X2", "DC", "DNB", "AH", "OU", "BTTS"]
KIND_TO_LABEL = {"1x2": "1X2", "dc": "DC", "dnb": "DNB", "ah": "AH", "ou": "OU", "btts": "BTTS"}

# rank across all qualifying selections to know shortlist rank + count
ranked = sorted([r for r in allrows if r.get("bet") is not None], key=lambda r: -r["bet"]["score"])
n_qualifying = len(ranked)
MAX_SHORTLIST = 5  # zaterdag
EDGE_THRESHOLD_LIGHT = 16.0

picks_out = []
shadow_would_settle_note = None

competitions = {}
for comp, ms in pass2.items():
    comp_id = COMP_ID[comp]
    if not ms:
        competitions[comp_id] = {"status": "GEEN WEDSTRIJD", "matches": []}
        continue
    out_matches = []
    for r in ms:
        rec = {
            "competition": comp_id, "match": r["match"], "match_id": r["match_id"],
            "home": r["home"], "away": r["away"], "home_id": int(r["home_id"]), "away_id": int(r["away_id"]),
            "kickoff_utc": r["kickoff_utc"], "kickoff_nl": r["kickoff_nl"], "source_day": r["source_day"],
        }
        if r.get("tier") == "NONE":
            rec["tier"] = "NONE"
            rec["bet"] = False
            rec["reden"] = f"data_tier NONE — {r.get('data_reason')}"
            rec["markets_checked"] = {m: "niet doorgerekend — data_tier NONE (geen onafhankelijke kansinput)"
                                       for m in MARKET_LABELS}
            out_matches.append(rec)
            continue
        if r.get("buiten_datadekking"):
            rec["tier"] = "BUITEN_DATADEKKING"
            rec["bet"] = False
            rec["reden"] = "geen prijsbron (geen sportkey bij The Odds API, geen BetExplorer-pagina/koersen)"
            rec["markets_checked"] = {m: f"BUITEN DATADEKKING — {rec['reden']}" for m in MARKET_LABELS}
            out_matches.append(rec)
            continue

        rec["tier"] = "LIGHT"
        rec["poort5_niet_gemeten"] = r["poort5_niet_gemeten"]
        rec["calibration"] = r["calibration"]
        rec["context"] = r["context"]
        rec["landenrating"] = r["landenrating"]
        if "selectiewaarde" in r:
            rec["selectiewaarde"] = r["selectiewaarde"]
        prob_sources = ["scripts/national.py — landenrating (6784 interlands, gefit 20 sep 2026)"]
        if not r["poort5_niet_gemeten"]:
            prob_sources.append("scripts/squadform.py — selectiewaarde (tweede methode, 0.30)")
        ctx = r["context"]
        if ctx.get("poort7_meetbaar"):
            hs, aw = ctx["home"], ctx["away"]
            prob_sources.append(
                f"scripts/squadform.injuries — poort 7: {hs['team']} mist {hs['out_share']*100:.1f}% "
                f"selectiewaarde, {aw['team']} mist {aw['out_share']*100:.1f}%")
        rec["prob_sources"] = prob_sources
        rec["odds_source"] = ("The Odds API (beste prijs, netto)" if r["odds_source"] == "oddsapi"
                               else r["all_candidates"][0]["book"])

        cands_out = []
        for c in r["all_candidates"]:
            cands_out.append({
                "market": c["market"], "selection": c["selection_label"], "sel_key": c["sel_key"],
                "odds": c["odds"], "odds_raw": c["odds_gross"],
                "odds_source": (f"The Odds API (beste prijs, netto); {c['book']}" if r["odds_source"] == "oddsapi"
                                 else c["book"]),
                "side": c["side"] if c["side"] in ("home", "away") else None,
                "my_prob": c["my_prob"], "my_raw": c["my_raw"], "implied": c["implied"],
                "p_xg": c["p_xg"], "p_split": c["p_split"], "edge_pp": c["edge_pp"], "edge_raw": c["edge_raw"],
                "edge_xg": c["edge_xg"], "edge_split": c["edge_split"],
                "edge_robust_min": c["edge_robust_min"], "edge_robust_max": c["edge_robust_max"],
                "poorten": c["poorten"], "context_reason": c["context_reason"],
                "underdog_reason": c["underdog_reason"], "would_block_underdog": c["would_block_underdog"],
                "failed_gate": c["failed_gate"], "score": c["score"], "score_ruw": c["score_ruw"],
            })
        rec["all_candidates"] = cands_out

        # markets_checked
        present_kinds = set(c["kind"] for c in r["all_candidates"])
        mc = {}
        for kind_label in MARKET_LABELS:
            kind = {"1X2": "1x2", "DC": "dc", "DNB": "dnb", "AH": "ah", "OU": "ou", "BTTS": "btts"}[kind_label]
            if kind in present_kinds:
                src = "The Odds API (beste prijs, netto)" if r["odds_source"] == "oddsapi" else "BetExplorer marktgemiddelde"
                extra = " per-wedstrijd-markt btts (2 credits, kandidaat-edge)" if kind == "btts" and r["odds_source"] == "oddsapi" else ""
                mc[kind_label] = f"doorgerekend — {src}{(' ' + extra) if extra else ''}"
            else:
                if r["odds_source"] == "oddsapi":
                    if kind == "btts":
                        mc[kind_label] = "niet opgevraagd — geen kandidaat-edge in dit duel" if not r.get("kandidaat_edge_voor_btts") else "niet gevonden — geen BTTS-prijs bij The Odds API voor dit duel"
                    elif kind == "dnb":
                        mc[kind_label] = "niet beschikbaar — geen 0.0-lijn in de spreads-respons voor dit duel"
                    elif kind == "dc":
                        mc[kind_label] = "niet beschikbaar — geen 0.5-lijn in de spreads-respons voor dit duel"
                    else:
                        mc[kind_label] = "niet beschikbaar — geen prijs bij The Odds API voor dit duel"
                else:
                    mc[kind_label] = "niet opgevraagd — geen sportkey bij The Odds API voor deze competitie (alleen BetExplorer 1X2)"
        rec["markets_checked"] = mc

        qualifying = [c for c in cands_out if c["failed_gate"] is None]
        best_qual = max(qualifying, key=lambda c: c["score"]) if qualifying else None
        rec["bet"] = best_qual is not None

        wb = [c for c in cands_out if c["would_block_underdog"]]
        if wb:
            rec["poort8_vervallen"] = [{"market": c["market"], "selection": c["selection"],
                                          "odds": c["odds"], "underdog_reason": c["underdog_reason"]} for c in wb]

        if best_qual is None:
            best_any = max(cands_out, key=lambda c: c["score_ruw"])
            rec["near_miss"] = {
                "market": best_any["market"], "selection": best_any["selection"],
                "odds": best_any["odds"], "edge_xg": best_any["edge_xg"], "edge_split": best_any["edge_split"],
                "edge_robust_min": best_any["edge_robust_min"], "failed_gate": best_any["failed_gate"],
                "my_prob": best_any["my_prob"],
            }
        else:
            rec["near_miss"] = None
            rank_idx = next(i for i, row in enumerate(ranked) if row["match"] == r["match"] and row["comp"] == comp) + 1
            n_doorgerekend = 18
            note_rank = (f"Gepubliceerd op rangorde (§5b): plek {rank_idx} van {n_qualifying} kwalificerende "
                         f"selecties over {n_doorgerekend} doorgerekende duels (LIGHT), "
                         f"MAX_SHORTLIST={MAX_SHORTLIST} (zaterdag) "
                         f"{'niet bereikt' if n_qualifying <= MAX_SHORTLIST else 'bereikt — drempel snijdt'} — "
                         f"de drempel van {EDGE_THRESHOLD_LIGHT:.1f} pp werkt hier dus als "
                         f"{'label, niet als veto' if n_qualifying <= MAX_SHORTLIST else 'echte grens'}.")
            rec["_note_rank"] = note_rank
            rec["_best_qual"] = best_qual

        out_matches.append(rec)
    status = "GEANALYSEERD"
    competitions[comp_id] = {"status": status, "matches": out_matches}

json.dump(competitions, open("tmp-run/rc26_competitions.json", "w"), indent=1, ensure_ascii=False)
print("klaar, competities:", list(competitions.keys()))
