"""Run B, 14 sep 2026 — data/coverage.json bijwerken met wat deze run gemeten heeft (§3, Stage 3)."""
import json

P = "data/coverage.json"
d = json.load(open(P))
C = d["competitions"]

TOEVOEGING = {
 "Eliteserien (NOR)": (" Run B 14 sep 2026: opnieuw bevestigd, has_xg=true voor 2025 (16 ploegen, "
   "avg 1.5425) én voor het lopende 2026 (20 speeldagen, avg 1.6657). FULL."),
 "Allsvenskan (SWE)": (" Run B 14 sep 2026: opnieuw bevestigd, has_xg=true voor 2025 (16 ploegen, "
   "avg 1.4400) én voor het lopende 2026 (21 speeldagen, avg 1.4909). FULL."),
 "Croatian HNL (CRO)": (" Run B 14 sep 2026: has_xg=false bevestigd voor 2025/2026 én 2026/2027 "
   "(7 speeldagen). LIGHT op doelpunten, ongewijzigd."),
 "Romanian SuperLiga (ROU)": (" Run B 14 sep 2026: has_xg=false bevestigd voor 2025/2026 én "
   "2026/2027 (9 speeldagen). LIGHT op doelpunten, ongewijzigd."),
 "Segunda División (ESP)": (" Run B 14 sep 2026: has_xg is nu OOK true voor het lopende 2026/2027 "
   "(5 speeldagen, avg 1.2963) — dat stond hierboven nog als false genoteerd en is dus veranderd; "
   "vorig seizoen 2025/2026 blijft true (22 ploegen na b_merge, avg 1.3600). LET OP voor de "
   "promovendi-omrekening: promotion.TIER2 kent voor 'LaLiga2 (ESP)' GEEN divisie eronder, en dat "
   "is niet zomaar een ontbrekende regel. De Primera Federacion draait bij Fotmob onder EEN "
   "primaryId (8968) voor TWEE parallelle groepen ('Primera Federacion - Group 1' en '- Group 2', "
   "beide gezien in de daglijsten van 8-14 sep 2026), dus een enkele fetch_league_stats levert "
   "geen eenduidige competitiebasis. Gevolg vandaag: Celta Fortuna - Eibar op NONE."),
 "Keuken Kampioen Divisie (NED)": (" Run B 14 sep 2026: has_xg=false bevestigd voor 2025/2026 én "
   "2026/2027 (7 speeldagen). LIGHT op doelpunten, ongewijzigd. De twee duels van vandaag waren "
   "allebei tussen beloftenelftallen (Jong FC Utrecht - Jong Ajax, Jong PSV - Jong AZ); die staan "
   "gewoon in de stand van vorig seizoen en hoeven dus niet omgerekend te worden."),
}

for k, extra in TOEVOEGING.items():
    C[k]["notes"] = (C[k].get("notes") or "").rstrip() + extra

d["updated"] = "2026-09-14"
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt")
