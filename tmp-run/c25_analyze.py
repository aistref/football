import json, math, sys
from datetime import date
sys.path.insert(0, '.')
from scripts import national, squadform, model, sides, oddsapi, recalibrate

DAY = date(2026, 9, 25)
NEAR_LIGHT = 6.0
EDGE_THRESHOLD_LIGHT_RAW = 16.0

nf = national.load_fit()
sf = squadform.load_fit()
squads = squadform.load_squads()
recal = recalibrate.load_fit()
print("Recalibratie:", recal.describe() if recal.n else "geen herijking (te weinig waarnemingen)")

matches = json.load(open("tmp-run/c25_matches_with_odds.json"))

def nat_team_id(fotmob_id):
    tid = str(fotmob_id)
    if tid in nf["teams"]:
        return tid
    return None

def best_price_nl(event, market_key, outcome_name, point=None):
    """Beste netto prijs uit een Odds-API event voor een outcome (optioneel met lijn)."""
    best = None
    for bm in event.get("bookmakers", []):
        title = bm.get("title")
        for mk in bm.get("markets", []):
            if mk["key"] != market_key:
                continue
            for oc in mk["outcomes"]:
                if oc["name"] != outcome_name:
                    continue
                if point is not None and oc.get("point") != point:
                    continue
                if point is None and market_key in ("spreads","totals") and oc.get("point") is None:
                    continue
                price = oc["price"]
                net = oddsapi.net_price(price, title)
                if best is None or net > best[0]:
                    best = (net, price, title, oddsapi.is_exchange(title))
    return best

def all_lines_nl(event, market_key):
    lines = set()
    for bm in event.get("bookmakers", []):
        for mk in bm.get("markets", []):
            if mk["key"] != market_key:
                continue
            for oc in mk["outcomes"]:
                if oc.get("point") is not None:
                    lines.add(oc["point"])
    return sorted(lines)

results = {}
n_price = n_noprice = 0
for comp, mlist in matches.items():
    results[comp] = []
    for m in mlist:
        rec = dict(m)
        home_id = nat_team_id(m["home_id"])
        away_id = nat_team_id(m["away_id"])
        ok_h = ok_a = False
        reason_h = reason_a = ""
        if home_id:
            ok_h, reason_h = national.in_range(home_id, nf)
        else:
            reason_h = f"geen interlandrating voor Fotmob-id {m['home_id']} ({m['home']})"
        if away_id:
            ok_a, reason_a = national.in_range(away_id, nf)
        else:
            reason_a = f"geen interlandrating voor Fotmob-id {m['away_id']} ({m['away']})"
        rec["national_gate"] = {"home": reason_h, "away": reason_a, "ok": ok_h and ok_a}
        if not (m.get("odds_event") or m.get("bx_odds")):
            rec["tier"] = "BUITEN_DATADEKKING_GEEN_PRIJS"
            n_noprice += 1
        else:
            n_price += 1
        results[comp].append(rec)

with open("tmp-run/c25_gate_check.json","w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)

print(f"\nprijs gevonden: {n_price}, geen prijs: {n_noprice}")
for comp, mlist in results.items():
    for m in mlist:
        g = m["national_gate"]
        status = "OK" if g["ok"] else "DICHT"
        pricetag = "prijs" if (m.get("odds_event") or m.get("bx_odds")) else "GEEN PRIJS"
        print(f"[{status:5s}] [{pricetag:9s}] {comp[:35]:35s} {m['home']:22s}-{m['away']:22s} h:{g['home'][:50]:50s} a:{g['away'][:50]}")
