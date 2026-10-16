"""Run B, 16 okt 2026 — BetExplorer-slug van Série A (BRA) is verhuisd.

`data/coverage.json` schrijft sinds 20 sep 2026 `brazil/serie-a-betano` voor, met de
uitdrukkelijke notitie dat `brazil/serie-a` toen de stille faalmodus gaf (HTTP 200, 0 rijen).
Vandaag is het precies omgekeerd gemeten:

    brazil/serie-a-betano   -> 200, 0 rijen
    brazil/serie-a          -> 200, 20 rijen, met Mirassol - Internacional erbij

Dat is dezelfde stille faalstand als het Serie B-id (`idcheck.py`): geen foutmelding, alleen
nul rijen, en nul rijen leest als "geen marktgemiddelde voor dit duel". Zonder deze correctie
mist Mirassol - Internacional zijn de-vigde marktoordeel, en dat raakt twee dingen die niet over
de bet zelf gaan (§1a): het kalibratieblok van §6e en poort 8.

Dit script repareert alleen de BetExplorer-kant en koopt niets bij: de bulk van The Odds API is
al betaald (18 credits) en wordt hier ongemoeid gelaten.
"""
import json
from scripts import betexplorer

GOED = "https://www.betexplorer.com/football/brazil/serie-a/"
FOUT = "https://www.betexplorer.com/football/brazil/serie-a-betano/"
COMP = "Série A (BRA)"

rows = betexplorer.fetch_league_fixtures(GOED)
print(f"{GOED} -> {len(rows)} rijen, {sum(r.is_today for r in rows)} met vandaag-label")

# 1. stage3.json en de kandidatenbestanden: de url die erin staat
for pad in ("tmp-run/rb_oct16_stage3.json", "tmp-run/rb_oct16_cands.json",
            "tmp-run/rb_oct16_ctx.json"):
    d = json.load(open(pad))
    n = 0
    if isinstance(d, dict) and "fixtures" in d:
        if d["fixtures"].get(COMP, {}).get("betexplorer") == FOUT:
            d["fixtures"][COMP]["betexplorer"] = GOED
            n += 1
    else:
        for c in d:
            if c.get("betexplorer") == FOUT:
                c["betexplorer"] = GOED
                n += 1
    json.dump(d, open(pad, "w"), ensure_ascii=False, indent=1, default=str)
    print(f"  {pad}: {n} verwijzing(en) bijgewerkt")

# 2. de odds-store: de rijen zelf, zodat find_1x2 ze vindt
o = json.load(open("tmp-run/rb_oct16_odds.json"))
o["fixtures"][COMP] = [{"home": r.home, "away": r.away, "odds": list(r.odds),
                        "books": r.bookmakers, "is_today": r.is_today} for r in rows]
o["errors"].pop(f"1x2 {COMP}", None)
o["bx_slug_correctie"] = {
    "competitie": COMP, "oud": FOUT, "nieuw": GOED,
    "oud_rijen": 0, "nieuw_rijen": len(rows),
    "reden": "coverage.json noemde serie-a-betano (geverifieerd 20 sep 2026); die slug geeft "
             "vandaag 200 met 0 rijen en brazil/serie-a geeft 20 rijen. Stille faalmodus."}
json.dump(o, open("tmp-run/rb_oct16_odds.json", "w"), ensure_ascii=False, indent=1)
hit = [r for r in rows if "Mirassol" in r.home]
print("  odds.json bijgewerkt; Mirassol-rij:", [(r.home, r.away, r.odds, r.bookmakers) for r in hit])
