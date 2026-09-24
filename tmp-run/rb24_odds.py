"""Run B 24 sep 2026 — prijzen voor het enige duel van de runlijst.

Het duel (Seattle Sounders FC - Real Salt Lake, MLS) trapte af om 01:30Z / 03:30 NL en was bij
het draaien van deze run al ~1u50m onderweg. De vraag die deze meting beantwoordt: geeft The Odds
API voor een al begonnen wedstrijd nog pre-match prijzen, of live prijzen, of niets?
"""
import json
from scripts import oddsapi

r = oddsapi.fetch_bulk("soccer_usa_mls", ["h2h", "spreads", "totals"], regions="eu")
print("credits over:", r.requests_remaining, "gebruikt:", r.requests_used, "kosten:", r.cost)
ev = [e for e in r.data if "Seattle" in e.get("home_team","")]
print("events in respons:", len(r.data), "| Seattle-event:", len(ev))
out = {"remaining": r.requests_remaining, "used": r.requests_used, "cost": r.cost, "n_events": len(r.data), "event": ev[0] if ev else None}
if ev:
    e = ev[0]
    print("commence:", e.get("commence_time"), e.get("home_team"), "-", e.get("away_team"))
    print("bookmakers:", len(e.get("bookmakers", [])))
    for mk in ("h2h", "spreads", "totals"):
        best = oddsapi.best_by_line(e, mk)
        print(f"  {mk}: {len(best)} (uitkomst,lijn)-combinaties")
        for k, v in sorted(best.items(), key=lambda x: str(x[0]))[:12]:
            print("     ", k, v)
json.dump(out, open("tmp-run/rb24_odds.json", "w"), ensure_ascii=False, indent=1)
