import json, sys
from datetime import datetime, timezone
sys.path.insert(0, '.')

results = json.load(open("tmp-run/c25_pass3.json"))
ranking = json.load(open("tmp-run/c25_ranking.json"))

MARKET_LABELS = {"1X2": "1X2", "Draw No Bet": "DNB", "Double Chance": "DC",
                  "Asian Handicap": "AH", "Over/Under": "OU", "BTTS": "BTTS"}

def markets_checked_for(r):
    out = {}
    present = {MARKET_LABELS.get(c["market"], c["market"]) for c in r["all_candidates"]}
    if r["_price_kind"] == "nl":
        for code in ("1X2", "DNB", "AH", "DC", "OU"):
            if code in present:
                out[code] = f"doorgerekend — {r['odds_source']}"
            else:
                reasons = {"DNB": "geen 0.0-lijn in de spreads-respons voor dit duel",
                           "AH": "geen andere lijn dan 0.0/0.5 in de spreads-respons voor dit duel",
                           "DC": "geen 0.5-lijn in de spreads-respons voor dit duel",
                           "OU": "geen totals-lijn in de respons voor dit duel"}
                out[code] = f"niet beschikbaar — {reasons.get(code, 'geen lijn')}"
        if "BTTS" in present:
            out["BTTS"] = "doorgerekend — per-wedstrijd-markt btts (2 credits, kandidaat-edge)"
        else:
            out["BTTS"] = "niet opgevraagd — geen kandidaat-edge in dit duel (unie van beide schalen)"
    else:
        out["1X2"] = f"doorgerekend — {r['odds_source']}"
        for code in ("DC", "DNB", "AH", "OU", "BTTS"):
            out[code] = "niet opgevraagd — geen sportkey bij The Odds API voor deze competitie"
    return out

bet_rank = {}
for row in ranking["rows"]:
    bet_rank[(row["comp"], row["match"])] = row["rank"]

poort8_lapsed_count = 0
for comp, mlist in results.items():
    for r in mlist:
        if r["tier"] != "LIGHT":
            continue
        r["markets_checked"] = markets_checked_for(r)
        # poort8_vervallen: alle kandidaten die de poort zou hebben tegengehouden
        p8 = [{"market": c["market"], "selection": c["selection"], "odds": c["odds"],
               "underdog_reason": c["underdog_reason"]}
              for c in r["all_candidates"] if c.get("would_block_underdog")]
        if p8:
            r["poort8_vervallen"] = p8
            poort8_lapsed_count += len(p8)
        if r.get("bet"):
            key = (comp, r["match"])
            r["bet_rank"] = bet_rank.get(key)
            for c in r["all_candidates"]:
                if c.get("gepubliceerd_kandidaat"):
                    c["poort8_zou_hebben_geblokkeerd"] = bool(c.get("would_block_underdog"))
        else:
            cands = r["all_candidates"]
            strongest = max(cands, key=lambda c: c["score_ruw"])
            r["near_miss"] = {
                "market": strongest["market"], "selection": strongest["selection"],
                "odds": strongest["odds"], "edge_xg": strongest["edge_xg"],
                "edge_split": strongest["edge_split"], "edge_robust_min": strongest["edge_robust_min"],
                "failed_gate": strongest["failed_gate"], "my_prob": strongest["my_prob"],
            }
        # opruimen interne velden
        r.pop("_price_kind", None)
        r.pop("_event_id", None)
        r.pop("kandidaat_edge_btts", None)

print("Aantal keer dat poort8_vervallen een kandidaat noteert:", poort8_lapsed_count)

with open("tmp-run/c25_final.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print("klaar")
