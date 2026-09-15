"""Run B, 15 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-15"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 15 sep 2026 — dinsdag in de Europese speelweek, en dat is te zien: 1 van de 17 "
    "competities had een wedstrijd. Grasshopper - Sion in de Swiss Super League, 19:00 NL. Cap 40 "
    "(ma-do) tegen 1 duel, 0 afgekapt. Het duel kwam op FULL door de datadekkingspoort, alle zes "
    "markten deden mee, 17 selecties, 0 bets — hoogste herijkte edge +2.03 pp tegen een drempel "
    "van 8.0. De Swiss Super League heeft een sportkey en kreeg de volle bulk-aanroep; 4 van 598 "
    "credits. Geen enkele selectie haalde alle acht poorten op de ruwe kans (de splitsmethode "
    "wees op de sterkste kandidaat tegengesteld), dus ook geen schaduwrij op de herijking en geen "
    "near_miss.")}

TOEVOEGING = {
 "fotmob": (" Run B 15 sep 2026: daglijst gaf 1 Run B-competitie met een wedstrijd (Swiss Super "
   "League, id 69). WEL xG, zowel in 2025/2026 als in het lopende 2026/2027 (8 speeldagen) — de "
   "competitie stond t/m 14 sep als 'nog niet getest' in prompts/run-b.md en is daarmee nu "
   "bevestigd als FULL-waardig; dat is in coverage.json vastgelegd. De overige zestien "
   "competities speelden vandaag niet en zijn dus niet opnieuw nagetrokken. Context opgehaald "
   "zonder fout; opstellingstype lastStarting11. check_venue meldde geen verplaatsing "
   "(Letzigrund is Grasshoppers eigen stadion). Het `totalStarterMarketValue = 0`-gat raakte dit "
   "duel niet: ctxlog kon het vastleggen."),
 "betexplorer": (" Run B 15 sep 2026: één slug opgehaald (switzerland/super-league), raak — 9 "
   "rijen, waarvan 1 vandaag. Alleen gebruikt voor het kalibratieblok (§6e) en poort 8; de "
   "gespeelde prijs komt van The Odds API."),
 "the_odds_api": (" Run B 15 sep 2026: 19.167 credits over, 833 gebruikt deze maand "
   "(api_check.py, 46 actieve voetbalcompetities). Plafond suggest_cap(19167, 16) = 598; "
   "uitgegeven 4 in 2 aanroepen (1 bulk-aanroep h2h+spreads+totals à 3 credits, plus 1 "
   "BTTS-aanroep à 1 credit in de tweede ronde van §1a stap 2). soccer_switzerland_superleague "
   "leverde 9 events. De spreads-respons bevatte geen 0.0-lijn, dus Draw No Bet was niet af te "
   "leiden; de ±0.5-lijn lag er wel (Double Chance). Beste prijs lag +4.62% boven het "
   "BetExplorer-marktgemiddelde — minder dan de +7.78% van de meting op 5 sep, en dat past bij "
   "een duel waarin de beste 1X2-prijs twee van de drie keer bij een beurs lag (Betfair) en dus "
   "met commissie is doorgerekend."),
 "api_football": (" 15 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. Het enige duel had al Fotmob-xG en kwam op FULL uit."),
 "understat": (" Run B 15 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
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
S["understat"]["last_checked"] = "2026-09-15"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
