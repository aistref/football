"""Run A, 14 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-14"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 14 sep 2026 — 7 van de 21 competities hadden wedstrijden, samen 11 duels. Cap 40 "
    "(maandag), 0 afgekapt. Alle elf duels kwamen door de datadekkingspoort: 10 FULL, 1 LIGHT, "
    "nul op NONE. 155 selecties over alle zes de markten, 0 bets. Alle zeven competities kregen "
    "de volle bulk-aanroep, dus marktbalans 7 op 7; BTTS in een tweede ronde voor de vier duels "
    "met een kandidaat-edge. 25 van 565 credits. Hoogste herijkte edge binnen de koersband "
    "+4.60 pp (Parma +1.5 @2.25) tegen een drempel van 8.0. Geen storing, geen afgewezen sleutel; "
    "API_FOOTBALL_KEY ontbreekt nog steeds.")}

TOEVOEGING = {
 "fotmob": (" Run A 14 sep 2026: daglijst gaf 7 Run A-competities met wedstrijden, 11 duels. "
   "Team-xG aanwezig voor alle zeven basiscompetities, zowel voor 2025/2026 als voor het lopende "
   "seizoen (4 tot 8 speeldagen), dus blend_seasons en de vroeg-seizoenscorrectie konden overal "
   "draaien; de pooling stond op 41 speeldagen over zeven competities. Voor de enige omrekening "
   "van vandaag (Marítimo) leverde Fotmob de stand van Liga Portugal 2 zonder uitval, binnen het "
   "gemeten bereik. Context opgehaald voor alle 11 duels, alle 11 bruikbaar. Opstellingstype: "
   "9 predicted, 2 lastStarting11 — geen bevestigde opstelling om 04:1x, wat voor avondduels "
   "normaal is. Poort 7 stond bij 7 van de 11 duels aan minstens één kant dicht en hield "
   "6 selecties tegen, waaronder de twee die zonder die poort een ruwe bet waren geweest "
   "(Villarreal – Real Betis en Radomiak Radom – Piast Gliwice)."),
 "betexplorer": (" Run A 14 sep 2026: fixtures-rijen voor alle zeven competities met wedstrijden, "
   "samen 95 rijen waarvan 11 van vandaag. Dekking 11 van 11, dus alle duels hebben een "
   "1X2-marktgemiddelde en een kalibratieblok (§6e). Het aantal boeken per rij loopt opnieuw "
   "sterk uiteen: 18 in de Premier League en Serie A, 12 in Portugal, maar 5 in Denemarken, "
   "4 in La Liga, 3 in de Ekstraklasa en 2 in de Süper Lig. Dat raakt alleen het "
   "consensusgemiddelde van §6e en poort 8, niet de prijs waarop gespeeld wordt."),
 "the_odds_api": (" Run A 14 sep 2026: 19.232 credits over, 768 gebruikt deze maand "
   "(api_check.py), 48 actieve voetbalcompetities. Alle zeven sportkeys werkten met de "
   "bulk-aanroep (h2h+spreads+totals), samen 95 events, 21 credits. BTTS in een tweede ronde ná "
   "de analyse, voor de vier duels met een kandidaat-edge: 4 credits (opnieuw 1 in plaats van de "
   "2 die §1a aanhoudt — voor de achtste run op rij). Samen 25 van 565. Beste prijs lag over de "
   "11 duels gemiddeld +6.79% boven het BetExplorer-marktgemiddelde (mediaan +5.90%, bereik "
   "+3.76% tot +13.12%); in 52 van de 155 doorgerekende selecties stond de beste prijs bij een "
   "beurs (Betfair, Matchbook) en is er met net_price gerekend."),
 "api_football": (" 14 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput voor alle 11 duels."),
 "understat": (" Run A 14 sep 2026: aangeroepen voor de drie gedekte competities die vandaag "
   "speelden (Premier League, Serie A, La Liga), alle drie zonder fout, 20 ploegen per "
   "competitie. Als tweede onafhankelijk xG-model meegenomen bij vijf duels (Leeds United – "
   "Newcastle United, Como – Parma, Torino – Roma, Inter – Udinese en Villarreal – Real Betis); "
   "bij Moreirense – Marítimo, Braga – Estoril en de overige duels dekt Understat de competitie "
   "niet."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["understat"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
