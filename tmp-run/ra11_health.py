"""Run A, 11 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-11"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 11 sep 2026 — 10 van de 21 competities hadden wedstrijden, samen 11 duels (de eerste "
    "speelronde na de interlandbreak). Cap 55 (vrijdag), 0 afgekapt. Negen duels door de "
    "datadekkingspoort (4 FULL, 5 LIGHT), 161 selecties over alle zes de markten, 0 bets. Twee "
    "duels op NONE doordat de promovendus buiten het gemeten conversiebereik viel (Erzurumspor "
    "FK, AC Horsens). Alle tien competities kregen de bulk-aanroep, dus marktbalans 10 op 10. "
    "Hoogste herijkte edge binnen de koersband +1.02 pp tegen drempels van 8.0 en 16.0.")}

TOEVOEGING = {
 "fotmob": (" Run A 11 sep 2026: daglijst gaf 10 Run A-competities met wedstrijden, 11 duels. "
   "Team-xG aanwezig voor alle tien basiscompetities, zowel voor 2025/2026 als voor het lopende "
   "seizoen (2 tot 7 speeldagen), dus blend_seasons en de vroeg-seizoenscorrectie konden overal "
   "draaien — de pooling stond deze run op 47 speeldagen over tien competities, de ruimste "
   "steekproef sinds de correctie bestaat. Voor de zeven binnenlandse omrekeningen leverde "
   "Fotmob de stand van de divisie eronder (Serie B, 2. Bundesliga, Eerste Divisie, 1. Lig, "
   "1. Division, I Liga) en die erboven (Premier League) zonder uitval; de twee afwijzingen "
   "komen van de bereikpoort en niet van een ontbrekende meting. Context opgehaald voor alle 11 "
   "duels, 9 daarvan bruikbaar voor ctxlog.py; het contextlogboek staat daarmee op 354. "
   "Opstellingstype: 5 predicted, 4 lastStarting11, 2 zonder opstellingsblok — geen enkele "
   "bevestigde opstelling op het moment van de run (04:1x), wat voor avondwedstrijden normaal "
   "is."),
 "betexplorer": (" Run A 11 sep 2026: fixtures-rijen voor alle tien competities met wedstrijden, "
   "samen 143 rijen waarvan 11 van vandaag — dekking 11 van 11, nul uitval. Het aantal boeken "
   "per rij loopt sterk uiteen: 19 in Serie A, La Liga, Bundesliga en de Süper Lig, 18 in "
   "België, 11 in de Championship en de Deense Superliga, maar 5 in de Ekstraklasa, 4 in "
   "Ligue 1 en 3 in de Eredivisie. Dat raakt alleen het consensusgemiddelde van §6e en poort 8, "
   "niet de prijs waarop gespeeld wordt; noteer wel dat het marktoordeel bij die laatste drie op "
   "een dunne basis staat."),
 "the_odds_api": (" Run A 11 sep 2026: 19.500 credits over, 500 gebruikt deze maand "
   "(api_check.py), 48 actieve voetbalcompetities. Alle tien sportkeys werkten met de "
   "bulk-aanroep (h2h+spreads+totals), samen 143 events. BTTS kostte voor de vijfde run op rij "
   "1 credit per wedstrijd in plaats van de 2 die §1a aanhoudt: 10 bulk-aanroepen à 3 = 30, plus "
   "11 BTTS-aanroepen = 11, samen precies de 41 die guard meldt over 21 aanroepen. Dat verschil "
   "met de regel is structureel genoeg om te noteren, niet om §1a op te wijzigen — het maakt "
   "BTTS goedkoper dan begroot, nooit duurder. Beste prijs lag over de negen doorgerekende duels "
   "gemiddeld +6.83% boven het BetExplorer-marktgemiddelde (mediaan +5.20%); de uitschieter is "
   "AZ Alkmaar – Willem II met +19.23%, waar de boeken het ver oneens zijn over het gat tussen "
   "Eredivisie en Eerste Divisie."),
 "api_football": (" 11 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput."),
 "understat": (" Run A 11 sep 2026: aangeroepen voor de vier gedekte competities die vandaag "
   "speelden (Serie A, La Liga, Bundesliga, Ligue 1), alle vier zonder fout, 18 tot 20 ploegen "
   "per competitie. Als tweede onafhankelijk xG-model daadwerkelijk meegenomen bij Sevilla – "
   "Valencia en Rennes – Marseille; bij Venezia – Fiorentina en Union Berlin – Schalke 04 niet, "
   "omdat de promovendus daar niet in de Understat-reeks van vorig seizoen staat."),
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
