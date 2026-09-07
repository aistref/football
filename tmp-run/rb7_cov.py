"""Run B, 7 sep 2026 — data/coverage.json bijwerken met wat deze run per competitie heeft gemeten."""
import json

P = "data/coverage.json"
d = json.load(open(P))
C = d["competitions"]

EXTRA = {
 "Greek Super League (GRE)": (
   " Run B 7 sep 2026: 1 duel (Asteras Tripolis – Iraklis). Het LOPENDE seizoen 2026/2027 heeft nu "
   "wél has_xg=true (3 speeldagen, avg_xg 1.284) — dat stond t/m half augustus op false. De basis "
   "blijft 2025/2026 (14 ploegen, avg_xg 1.306). Het duel kwam toch op NONE: Iraklis staat niet in "
   "de stand van 2025/2026 en promotion.py kent voor Griekenland geen divisiepaar, dus er is geen "
   "gemeten gat om mee om te rekenen. Bulk-aanroep met soccer_greece_super_league werkte (9 events)."),
 "Allsvenskan (SWE)": (
   " Run B 7 sep 2026: 3 duels, de best gedekte competitie van de run. Seizoen 2026 op 20 speeldagen, "
   "has_xg=true; blend_seasons geeft het lopende seizoen daarmee gewicht 0.69–0.70, het hoogste van "
   "de hele runlijst. Kalmar FF stond niet in de Allsvenskan-stand van 2025 en is omgerekend uit de "
   "Superettan (gepoolde up-factor ×0.605/1.513, aanval 1.213 en verdediging 0.490 allebei binnen "
   "het gemeten bereik) → LIGHT. Malmö FF – AIK en Mjällby – IFK Göteborg op FULL. AIK mist 56% van "
   "de selectiewaarde tegen 23% bij Malmö — de zwaarste blokkade die poort 7 tot nu toe heeft "
   "gegeven. 54 selecties, 0 bets."),
 "Romanian SuperLiga (ROU)": (
   " Run B 7 sep 2026: 2 duels, has_xg=false opnieuw bevestigd voor 2025/2026 én 2026/2027 — het "
   "doelpuntenmodel blijft hier de enige route en levert LIGHT. FC Voluntari staat niet in de stand "
   "van 2025/2026 en er is geen divisiepaar bekend voor Roemenië → NONE. NAAMKOPPELING GEREPAREERD: "
   "BetExplorer schrijft 'Univ. Craiova' en 'U. Cluj' waar Fotmob de namen voluit geeft; "
   "best_pair kwam op 0.614 over het paar tegen een vloer van 0.62 en liet de enige prijsbron van "
   "dit duel vallen. Twee aliassen toegevoegd in tmp-run/ra_names.py, daarna 3 selecties."),
 "Segunda División (ESP)": (
   " Run B 7 sep 2026: 1 duel (Sabadell – Córdoba). Het lopende seizoen 2026/2027 heeft nu "
   "has_xg=true (4 speeldagen, avg_xg 1.243). Het duel kwam op NONE: Sabadell is gepromoveerd uit de "
   "DERDE divisie (Primera Federación) en promotion.TIER2 kent onder LaLiga2 geen divisie, dus de "
   "omweg viel terug op TIER1 (La Liga) waar Sabadell uiteraard niet in staat. Zelfde soort gat als "
   "LR Vicenza/Arezzo bij de Serie B op 6 sep."),
 "Serie B (ITA)": (
   " Run B 7 sep 2026: 1 duel (Palermo – Sampdoria), FULL. Het lopende seizoen 2026/2027 heeft nu "
   "has_xg=true (3 speeldagen), gewicht 0.20 in blend_seasons. 15 selecties over alle zes de "
   "markten, 0 bets; sterkste kandidaat BTTS-nee @1.98 op ruw +7.19 pp, herijkt −4.53 pp."),
 "Keuken Kampioen Divisie (NED)": (
   " Run B 7 sep 2026: 2 duels, allebei een beloftenelftal thuis (Jong FC Utrecht, Jong PSV). "
   "has_xg=false opnieuw bevestigd voor beide seizoenen; doelpuntenmodel op de stand van 2025/2026 "
   "geeft LIGHT voor alle vier de ploegen. Geen sportkey, dus alleen het BetExplorer-marktgemiddelde: "
   "3 selecties per duel. Fotmob geeft voor beide beloftenelftallen squad_value 0, waardoor deze "
   "duels buiten het contextlogboek vallen."),
 "English League One (ENG)": (
   " Run B 7 sep 2026: 1 duel (Bromley – Wimbledon). Het lopende seizoen 2026/2027 heeft nu "
   "has_xg=true (5 speeldagen, avg_xg 1.498) — t/m 15 aug stond dat op false en op played=0. De "
   "basis blijft 2025/2026. Bromley staat daar niet in en is omgerekend uit League Two met de "
   "GEMETEN E2/E3-factor ×0.782/1.375 (geen gepoolde), binnen bereik → LIGHT. 11 selecties, 0 bets."),
}

for k, extra in EXTRA.items():
    C[k]["notes"] = (C[k].get("notes") or "").rstrip() + extra

d["updated"] = "2026-09-07"
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt voor", len(EXTRA), "competities")
