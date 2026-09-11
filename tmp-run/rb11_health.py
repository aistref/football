"""Run B, 11 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-11"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 11 sep 2026 — 8 van de 17 competities hadden wedstrijden, samen 19 duels; de grootste "
    "Run B-dag van deze maand. Cap 55 (vrijdag), 0 afgekapt. Zestien duels door de "
    "datadekkingspoort (6 FULL, 10 LIGHT), 128 selecties, 0 bets. Drie duels op NONE wegens een "
    "ploeg zonder omrekenbare historie (Arezzo en Benevento uit de Serie C, Skënderbeu uit de "
    "Albanese tweede divisie). Vijf van de acht competities hadden een sportkey en kregen de volle "
    "bulk-aanroep; drie (Roemenië, Keuken Kampioen Divisie, Albanië) hebben er geen en kwamen niet "
    "verder dan het BetExplorer-marktgemiddelde. 23 van 485 credits.")}

TOEVOEGING = {
 "fotmob": (" Run B 11 sep 2026: daglijst gaf 8 Run B-competities met wedstrijden (19 duels). "
   "xG-dekking opnieuw per competitie nagetrokken: WEL xG bij Allsvenskan (67), Segunda División "
   "(140), Serie B (86), 2. Bundesliga (146) en Austrian Bundesliga (38), in beide seizoenen; GEEN "
   "xG bij Romanian SuperLiga (189), Keuken Kampioen Divisie (111) en Kategoria Superiore (260) — "
   "die drie rekenen op doelpunten voor/tegen en blijven LIGHT. Standen van het lopende seizoen "
   "gevuld voor alle acht (3 tot 20 speeldagen). Context opgehaald voor alle 19 duels zonder één "
   "fout; opstellingstype 17x lastStarting11 en 2x geen bruikbaar blok — geen enkele bevestigde "
   "opstelling om 03:3x, wat voor avondwedstrijden normaal is. Geen enkele verplaatsing gemeld "
   "door check_venue. Eindstanden van de Eredivisie 2025/2026 (57) gebruikt om Heracles en NAC "
   "Breda naar de Keuken Kampioen Divisie om te rekenen; beide ploegen stonden er gewoon in."),
 "betexplorer": (" Run B 11 sep 2026: zeven slugs opgehaald, alle zeven raak (Albanië heeft geen "
   "slug en is de enige competitie zonder 1X2-rij). Het aantal boeken per rij loopt opnieuw sterk "
   "uiteen: 19 in de 2. Bundesliga en de Eerste Divisie, 12 in de Allsvenskan, 5 in Roemenië en "
   "Oostenrijk, maar 3 in de Segunda División en de Serie B. Voor de drie competities zonder "
   "sportkey (Roemenië, Keuken Kampioen Divisie, Albanië) was dit de ENIGE 1X2-bron; daar is de "
   "bookmaker niet herleidbaar en valt de edge systematisch te laag uit."),
 "the_odds_api": (" Run B 11 sep 2026: 19.459 credits over, 541 gebruikt deze maand (api_check.py, "
   "48 actieve voetbalcompetities). Plafond suggest_cap(19459, 20) = 485; uitgegeven 23 in 13 "
   "aanroepen (5 bulk-aanroepen h2h+spreads+totals à 3 credits, plus 8 BTTS-aanroepen à 1 credit). "
   "Opnieuw bevestigd welke Run B-competities GEEN sportkey hebben: Roemenië, de Keuken Kampioen "
   "Divisie en Albanië komen geen van drieën voor in de /v4/sports-lijst; soccer_sweden_allsvenskan, "
   "soccer_spain_segunda_division, soccer_italy_serie_b, soccer_germany_bundesliga2 en "
   "soccer_austria_bundesliga wel, en alle vijf leverden events. Beste prijs lag over de zes duels "
   "waar hij bekend is gemiddeld +6.8% boven het BetExplorer-marktgemiddelde (mediaan +6.5%, "
   "uitschieter Häcken – Mjällby met +9.7%). BTTS kostte opnieuw 1 credit per wedstrijd in plaats "
   "van de 2 uit §1a."),
 "api_football": (" 11 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving van "
   "de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: de drie competities zonder Fotmob-xG (Roemenië, Keuken "
   "Kampioen Divisie, Albanië) hadden met een werkende statistiekenbron mogelijk FULL kunnen zijn "
   "in plaats van LIGHT; dat raakt negen van de zestien doorgerekende duels."),
 "understat": (" Run B 11 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
   "Bundesliga, Serie A en Ligue 1, en geen daarvan staat op de Run B-runlijst. Normale uitkomst "
   "voor Run B, geen storing."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
# Understat is deze run niet geprobeerd; status blijft staan op wat er laatst gemeten is.
S["understat"]["last_checked"] = "2026-09-11"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
