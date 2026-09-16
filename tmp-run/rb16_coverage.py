"""Run B, 16 sep 2026 — data/coverage.json bijwerken met wat deze run gemeten heeft (§3, Stage 3)."""
import json

P = "data/coverage.json"
d = json.load(open(P))
C = d["competitions"]

TOEVOEGING = {
 "Allsvenskan (SWE)": (" Run B 16 sep 2026: opnieuw bevestigd. Fotmob (primaryId 67) geeft "
   "has_xg=true voor het volle seizoen 2025 (16 ploegen, avg 1.4400 xG per ploeg per duel) én "
   "voor het lopende 2026 (21 speeldagen, avg 1.4910). AIK - Mjällby kwam daarmee op FULL uit, "
   "met blend_seasons op gewicht 0.714 voor het lopende seizoen (20 duels per ploeg) — de "
   "hoogste blendweging die deze routine tot nu toe heeft gedraaid. De sportkey "
   "soccer_sweden_allsvenskan leverde 9 events op de volle bulk-aanroep, met een 0.0-lijn (Draw "
   "No Bet) én een ±0.5-lijn (Double Chance) in de spreads-respons. Merk op dat de "
   "vroeg-seizoenscorrectie hier vrijwel is uitgedoofd: de eigen waarneming staat op 1.0354, en "
   "dat hoort zo bij 21 van de 30 speeldagen."),
 "Swiss Super League (SUI)": (" Run B 16 sep 2026: opnieuw bevestigd, nu op twee duels. Fotmob "
   "(primaryId 69) geeft has_xg=true voor 2025/2026 (12 ploegen, avg 1.6035 xG per ploeg per "
   "duel) én voor het lopende 2026/2027 (8 speeldagen, avg 1.7337). Lugano - St. Gallen en Thun "
   "- Servette kwamen allebei op FULL uit, met blend_seasons op gewicht 0.467 voor het lopende "
   "seizoen (7 duels per ploeg). Anders dan op 15 sep bevatte de spreads-respons dit keer wél "
   "een 0.0-lijn, dus Draw No Bet was gewoon af te leiden; de ±0.5-lijn (Double Chance) lag er "
   "ook. BTTS is niet gekocht — geen van beide duels toonde een kandidaat-edge (§1a stap 2), dus "
   "dat is het criterium en niet het plafond."),
}

for k, extra in TOEVOEGING.items():
    C[k]["notes"] = (C[k].get("notes") or "").rstrip() + extra

d["updated"] = "2026-09-16"
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt")
