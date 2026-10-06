"""Run A, 6 okt 2026 — Stage 3 datadekkingspoort voor de vijf FA Cup-duels.

De duels komen van BetExplorer (Fotmob kent de FA Cup vandaag niet in zijn daglijst).
Vraag per duel: is er een onafhankelijke kansbron? Dat loopt via promotion.shared_lower_division
(§4, 'In een beker ligt de basis per WEDSTRIJD') — beide ploegen in dezelfde divisie onder de
basisdivisie van de beker, anders NONE.
"""
import json
from scripts import promotion, fotmob

DUELS = [("Atherton", "Trafford"), ("Halesowen", "Stafford"),
         ("Scarborough", "Macclesfield"), ("Spalding United", "Bury Town"),
         ("Wingate & Finchley", "Bedford")]
BASE = promotion.CUP_BASE["FA Cup (ENG)"]
SEASON = "2025/2026"

out = []
for home, away in DUELS:
    rec = {"home": home, "away": away, "base": BASE}
    try:
        sd = promotion.shared_lower_division(BASE, home, away, SEASON)
        rec["shared_lower_division"] = None if sd is None else {
            "competition": sd.competition, "fotmob_id": sd.fotmob_id}
    except Exception as e:
        rec["shared_lower_division_error"] = f"{type(e).__name__}: {e}"
    # tweede poging: staan ze überhaupt in de basisdivisie of een van de drie eronder?
    found = {}
    for comp, cid in (("Premier League (ENG)", 47), ("Championship (ENG)", 48),
                      ("League One (ENG)", 108), ("League Two (ENG)", 109)):
        try:
            tbl = promotion.lower_table(comp, SEASON) if comp != BASE else None
        except Exception:
            tbl = None
        found[comp] = None
    rec["in_tier1_4"] = found
    out.append(rec)
    print(json.dumps(rec, ensure_ascii=False))

json.dump(out, open("tmp-run/ra_oct06_cover.json", "w"), ensure_ascii=False, indent=1)
