"""Run B, 16 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-16"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 16 sep 2026 — woensdag in de Europese speelweek, en dat is te zien: 2 van de 17 "
    "competities hadden een wedstrijd. AIK - Mjällby (Allsvenskan) en Lugano - St. Gallen en "
    "Thun - Servette (Swiss Super League), alle drie 19:00 NL. Cap 40 (ma-do) tegen 3 duels, "
    "0 afgekapt. Alle drie kwamen op FULL door de datadekkingspoort, vijf van de zes markten "
    "deden mee (BTTS niet gekocht: geen kandidaat-edge), 51 selecties, 0 bets — hoogste herijkte "
    "edge -3.60 pp en hoogste ruwe edge +5.96 pp, tegen een drempel van 8.0. Beide competities "
    "hebben een sportkey en kregen de volle bulk-aanroep; 6 van 637 credits. Geen enkele selectie "
    "haalde alle acht poorten op de ruwe kans, dus geen schaduwrij op de herijking, geen "
    "poort-8-rij en geen near_miss.")}

TOEVOEGING = {
 "fotmob": (" Run B 16 sep 2026: daglijst gaf 2 Run B-competities met wedstrijden (Allsvenskan "
   "id 67, Swiss Super League id 69). Allebei WEL xG, zowel in het vorige seizoen als in het "
   "lopende (Allsvenskan 21 speeldagen, Swiss Super League 8). Allebei staan ze in "
   "prompts/run-b.md nog op de lijst 'nog niet getest', maar dat is een verouderde regel: "
   "coverage.json heeft de Allsvenskan sinds 9 aug en de Swiss Super League sinds 23 aug 2026 "
   "bevestigd, en vandaag opnieuw. De overige vijftien competities speelden vandaag niet en zijn dus "
   "niet opnieuw nagetrokken. Context voor alle drie de duels opgehaald zonder fout; "
   "check_venue meldde geen enkele verplaatsing (Strawberry Arena, AIL Arena en VISANA STADION "
   "zijn alle drie het eigen stadion van de genoteerde thuisploeg). Eén waarneming om te "
   "onthouden: bij AIK gaf Fotmob dertien uitvallers met samen meer marktwaarde dan de "
   "vermoedelijke basiself zelf (out_value 8,73 mln tegen squad_value 8,71 mln), oftewel een "
   "ontbrekend aandeel van 50% — hoog, maar rekenkundig geldig, en poort 7 sloot de thuiskant."),
 "betexplorer": (" Run B 16 sep 2026: twee slugs opgehaald (sweden/allsvenskan en "
   "switzerland/super-league), allebei raak — 9 respectievelijk 8 rijen, waarvan 1 en 2 vandaag. "
   "Alleen gebruikt voor het kalibratieblok (§6e) en poort 8; de gespeelde prijs komt van The "
   "Odds API. Beide gemiddelden liepen over 3 boeken."),
 "the_odds_api": (" Run B 16 sep 2026: 19.140 credits over, 860 gebruikt deze maand "
   "(api_check.py, 46 actieve voetbalcompetities). Plafond suggest_cap(19140, 15) = 637; "
   "uitgegeven 6 in 2 aanroepen (twee bulk-aanroepen h2h+spreads+totals à 3 credits). De tweede "
   "ronde van §1a stap 2 kocht géén BTTS: geen van de drie duels toonde een kandidaat-edge op de "
   "ruwe of de herijkte schaal, dus er was niets te kopen. soccer_sweden_allsvenskan leverde 9 "
   "events, soccer_switzerland_superleague 8. Beide spreads-responsen bevatten wél een 0.0-lijn, "
   "dus Draw No Bet was overal af te leiden, net als Double Chance uit de ±0.5-lijn. Beste prijs "
   "lag gemiddeld +5.1% boven het BetExplorer-marktgemiddelde (6.06% / 4.49% / 4.77% per duel) — "
   "iets onder de +7.78% van de meting op 5 sep, en dat past bij drie duels waarin de beste "
   "1X2-prijs meestal bij een beurs lag (Betfair, Matchbook) en dus met 2% commissie is "
   "doorgerekend."),
 "api_football": (" 16 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. Alle drie de duels hadden Fotmob-xG en kwamen op FULL "
   "uit."),
 "understat": (" Run B 16 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
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
S["understat"]["last_checked"] = DAY

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
