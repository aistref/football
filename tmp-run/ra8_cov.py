"""Run A, 8 sep 2026 — data/coverage.json bijwerken met wat deze run per competitie heeft gemeten."""
import json

P = "data/coverage.json"
d = json.load(open(P))
C = d["competitions"]

EXTRA = {
 "Championship (ENG)": (
   " Run A 8 sep 2026: 6 duels, de best gedekte competitie van de run. Basis 2025/2026 (24 "
   "ploegen, has_xg=true, avg_xg 1.302); lopend seizoen 2026/2027 op 5 speeldagen met "
   "has_xg=true en avg_xg 1.429, dus blend_seasons geeft het lopende seizoen gewicht rond 0.38. "
   "Drie duels op FULL (Blackburn – Sheff Utd, Southampton – Swansea, Watford – Preston) en "
   "drie op LIGHT door een omrekening: Cardiff City omhoog uit League One (×0.673/1.638, binnen "
   "bereik), Burnley en West Ham United omlaag uit de Premier League (×1.830/0.634, binnen "
   "bereik), Bolton Wanderers omhoog uit League One. Alle zes de markten doorgerekend, 0 bets; "
   "hoogste herijkte edge +5.88 pp (Wrexham – Burnley, 1X2 Burnley @ 3.695, LIGHT — 16.0 nodig)."),
 "Eredivisie (NED)": (
   " Run A 8 sep 2026: 2 duels, allebei FULL. Basis 2025/2026 (18 ploegen, avg_xg 1.579); "
   "lopend seizoen op 5 speeldagen met has_xg=true en avg_xg 1.714 — het hoogste "
   "competitieniveau van de run. Beide duels hebben een voorspelde opstelling (predicted) in "
   "plaats van een bevestigde. FC Utrecht – Go Ahead Eagles stond NIET in de "
   "BetExplorer-fixturelijst en heeft daardoor geen marktgemiddelde: geen kalibratieblok, en "
   "poort 8 staat er open omdat er geen marktoordeel over de zwakkere ploeg is. De beste "
   "1X2-prijzen kwamen wel gewoon uit de bulk-aanroep (2 en X; geen thuiswinstprijs). "
   "22 selecties, 0 bets."),
 "League Cup (ENG)": (
   " Run A 8 sep 2026: 5 duels, ronde 3 — en dit is de eerste run waarin soccer_england_efl_cup "
   "bij The Odds API is gebruikt: de bulk-aanroep gaf 16 events, alle vijf de duels gedekt op "
   "h2h, spreads én totals. De basis (niveau + splits) is de Premier League 2025/2026, zoals "
   "PROMO_COMP voorschrijft. Dat werkt voor Championship-ploegen — Middlesbrough en Millwall "
   "zijn omgerekend met de gemeten E0/E1-up-factor ×0.541/1.783 en vielen binnen bereik → "
   "LIGHT — maar het legt ook twee grenzen bloot. (1) Hull City komt op verdediging 1.102 uit, "
   "buiten de bovengrens 1.022 van conversion_in_range → NONE, geen bet (Sunderland – Hull). "
   "(2) Lincoln City, Leyton Orient en Bradford City spelen in League One, TWEE divisies onder "
   "de basis, en er is geen gemeten factor over twee divisies → NONE (Bournemouth – Lincoln, "
   "Leyton Orient – Bradford). Van de vijf duels bleven er dus twee over om door te rekenen: "
   "32 selecties, 0 bets."),
 "UEFA Champions League": (
   " Run A 8 sep 2026: 6 duels (AEK Athens – LASK, Club Brugge – Aston Villa, Dortmund – "
   "Villarreal, FC Porto – Man City, Lille – Real Betis, Real Madrid – Inter), alle zes op "
   "BUITEN DATADEKKING wegens kruis-grens. De reden is niet dat de cijfers ontbreken — Fotmob "
   "heeft team-xG voor elk van de twaalf ploegen — maar dat ze op onvergelijkbare schalen "
   "staan: elke sterkte is genormaliseerd op het eigen competitiegemiddelde, en het "
   "krachtsverschil TUSSEN twee nationale competities kent het model niet. "
   "promotion.MEASURED_TIER2_GAP meet divisies binnen één land; tussen landen bestaat zo'n "
   "gemeten factor niet. Prijzen waren er wel: de bulk-aanroep met soccer_uefa_champs_league "
   "gaf 18 events op h2h, spreads en totals (3 credits). De BETEXPLORER-fixturepagina voor de "
   "Champions League gaf daarentegen NUL rijen — geen HTTP-fout, een lege tabel — dus er was "
   "ook geen marktgemiddelde. De beperking zit dus aan de kansinput, niet aan de markt. "
   "Context is voor alle zes de duels wél opgehaald en gelogd (§1c)."),
}

for k, extra in EXTRA.items():
    C[k]["notes"] = (C[k].get("notes") or "").rstrip() + extra
    C[k]["last_checked"] = "2026-09-08"

d["updated"] = "2026-09-08"
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt voor:", ", ".join(EXTRA))
