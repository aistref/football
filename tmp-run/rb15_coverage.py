"""Run B, 15 sep 2026 — data/coverage.json bijwerken met wat deze run gemeten heeft (§3, Stage 3)."""
import json

P = "data/coverage.json"
d = json.load(open(P))
C = d["competitions"]

TOEVOEGING = {
 "Swiss Super League (SUI)": (" Run B 15 sep 2026: VOOR HET EERST WERKELIJK GEMETEN, en het "
   "antwoord is ja. prompts/run-b.md zette deze competitie t/m vandaag op de lijst 'nog niet "
   "getest'. Fotmob (primaryId 69) geeft has_xg=true voor 2025/2026 (12 ploegen, avg 1.6035 xG "
   "per ploeg per duel) én voor het lopende 2026/2027 (8 speeldagen, avg 1.7233). Grasshopper - "
   "Sion kwam daarmee op FULL uit, met blend_seasons op gewicht 0.467 voor het lopende seizoen "
   "(7 duels per ploeg). De competitie heeft bovendien een sportkey bij The Odds API "
   "(soccer_switzerland_superleague), dus alle zes markten waren in te kopen: h2h, spreads en "
   "totals in één bulk-aanroep, BTTS in de tweede ronde. De spreads-respons had geen 0.0-lijn, "
   "dus Draw No Bet was niet af te leiden; de ±0.5-lijn lag er wel."),
}

for k, extra in TOEVOEGING.items():
    C[k]["notes"] = (C[k].get("notes") or "").rstrip() + extra

d["updated"] = "2026-09-15"
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt")
