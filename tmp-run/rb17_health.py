"""Run B, 17 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-17"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 17 sep 2026 — donderdag in de Europese speelweek: 1 van de 17 competities uit de "
    "runlijst had een wedstrijd, AFC Wimbledon - Milton Keynes Dons in English League One "
    "(21:00 NL). De andere zestien stonden leeg; de Kosovo Superleague komt nog altijd niet op "
    "de Fotmob-daglijst voor (ongewijzigd sinds 13 aug 2026). Cap 40 (ma-do) tegen 1 duel, "
    "0 afgekapt. Het duel is op LIGHT doorgerekend — MK Dons is met promotion.convert omgerekend "
    "uit League Two (E2/E3, binnen bereik) en een omgerekende ploeg is nooit FULL. 11 selecties "
    "over vijf markten, 0 bets: geen enkele selectie kwam zelfs maar boven de marktkans uit, de "
    "hoogste herijkte edge staat op -6.09 pp. Geen near_miss, geen poort-8-rij en geen rij op de "
    "herijking. 3 van 682 credits (één bulk-aanroep); BTTS niet gekocht, geen kandidaat-edge.")}

TOEVOEGING = {
 "fotmob": (" Run B 17 sep 2026: daglijst gaf 1 Run B-competitie met wedstrijden (English League "
   "One, id 108, 1 duel); de overige zestien uit de runlijst stonden er niet op. League One heeft "
   "xG in zowel 2025/2026 (24 ploegen, gemiddeld 1.302 xG per ploeg per duel) als 2026/2027 "
   "(6 speeldagen, 1.447). Context voor het duel opgehaald zonder fout: lineupType "
   "lastStarting11, nul uitvallers aan beide kanten, vorm en rustdagen bekend voor beide ploegen "
   "(allebei 5,2 dagen). check_venue meldde géén verplaatsing — The Cherry Red Records Stadium is "
   "het eigen stadion van AFC Wimbledon."),
 "betexplorer": (" Run B 17 sep 2026: één slug opgehaald (england/league-one), raak — 12 rijen, "
   "waarvan 1 vandaag, met het marktgemiddelde over 3 boeken (2.93 / 3.35 / 2.27). Alleen "
   "gebruikt voor het kalibratieblok (§6e) en poort 8; de gespeelde prijs komt van The Odds API."),
 "the_odds_api": (" Run B 17 sep 2026: 19.122 credits over, 878 gebruikt deze maand "
   "(api_check.py, 46 actieve voetbalcompetities). Plafond suggest_cap(19122, 14) = 682, "
   "split_budget(682, 1) = 1 spreads / 1 totals; uitgegeven 3 in één bulk-aanroep "
   "(h2h+spreads+totals) voor soccer_england_league1, dat 12 events leverde. BTTS is niet "
   "gekocht: het enige duel toonde geen kandidaat-edge op geen van beide schalen (§1a stap 2). "
   "Totaal 3 van 682, 19.119 over. Let op de dekking binnen de spreads-respons: er zat wél een "
   "0.0-lijn in (Draw No Bet, 2 selecties) maar géén ±0.5-lijn, dus Double Chance kon deze run "
   "niet meedoen — bekeken met een reden, geen gat. De beste 1X2-prijs stond bij alle drie de "
   "uitkomsten bij Betfair (beurs) en lag +5.99% boven het BetExplorer-marktgemiddelde, in lijn "
   "met de +7.78% van de meting op 5 sep."),
 "api_football": (" 17 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. De kansinput kwam van Fotmob; dat het duel LIGHT is "
   "komt door de promovendi-omrekening (§4), niet door deze sleutel."),
 "understat": (" 17 sep 2026 (Run B): niet aangeroepen — Understat dekt alleen de vijf grote "
   "competities en geen daarvan staat op de runlijst van Run B."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
S["understat"]["status"] = S["understat"].get("status", "ok")   # niet aangeroepen deze run

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
