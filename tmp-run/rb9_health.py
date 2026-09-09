"""Run B, 9 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-09"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 9 sep 2026 — 1 van de 17 competities had wedstrijden (Czech First League, 2 duels); "
    "beide doorgerekend (cap 40, woensdag), 0 afgekapt, allebei tier LIGHT, 6 selecties, "
    "0 bets. Interlandperiode: de andere zestien competities lagen stil. De Czech First League "
    "heeft geen sportkey bij The Odds API, dus er is deze run geen enkele credit uitgegeven en "
    "was alleen 1X2 te koop — de marktbalans-controle van §1a faalt daardoor, en niet door het "
    "creditplafond.")}

TOEVOEGING = {
 "fotmob": (" Run B 9 sep 2026: daglijst gaf 1 Run B-competitie met wedstrijden (1. Liga, "
   "primaryId 122, 2 duels). OPNIEUW BEVESTIGD has_xg=FALSE voor de Czech First League, zowel "
   "voor 2025/2026 (16 ploegen, 30 speeldagen) als voor het lopende 2026/2027 (7 speeldagen) — "
   "dezelfde uitkomst als op 22 aug en 2 sep, dus die competitie staat terecht in "
   "no_xg_confirmed en blijft LIGHT op doelpunten. Wel bruikbaar daar: doelpunten voor/tegen, "
   "thuis/uit-splits (1.379 thuis / 1.217 uit per duel in 2025/2026) en de stand van het "
   "lopende seizoen (6 duels per ploeg, blend-gewicht 0.429). Context voor beide duels "
   "opgehaald zonder fout, lineupType lastStarting11 voor allebei, squad_value gevuld voor alle "
   "vier de ploegen en niemand als afwezig gemeld."),
 "betexplorer": (" Run B 9 sep 2026: slug czech-republic/chance-liga gaf 10 fixtures-rijen, "
   "waarvan 2 van vandaag — beide duels gedekt met een 1X2-rij over 3 boeken. Dit was deze run "
   "de ENIGE prijsbron: de Czech First League heeft geen sportkey bij The Odds API, dus geen "
   "beste prijs, geen handicaps en geen doelpuntenmarkt. Marktgemiddelde, bookmaker niet "
   "herleidbaar, en met 3 boeken een dunne consensus."),
 "the_odds_api": (" Run B 9 sep 2026: 19.520 credits over, 480 gebruikt deze maand "
   "(api_check.py, 48 actieve voetbalcompetities). NUL aanroepen deze run en dus nul credits "
   "gebruikt van een plafond van 443 — niet uit zuinigheid maar omdat de enige competitie met "
   "wedstrijden geen sportkey heeft. Dat is sinds 9 aug 2026 zo voor Tsjechie en is vandaag "
   "opnieuw bevestigd: soccer_czech_* komt niet voor in de /v4/sports-lijst."),
 "api_football": (" 9 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen extra gevolgen bovenop wat Fotmob al niet heeft; de "
   "Czech First League zou met een werkende statistiekenbron mogelijk wel xG hebben gehad en "
   "dan FULL zijn geweest in plaats van LIGHT."),
 "understat": (" Run B 9 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
   "Bundesliga, Serie A en Ligue 1, en geen daarvan staat op de Run B-runlijst. Normale "
   "uitkomst voor Run B, geen storing."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
# Understat is deze run niet geprobeerd; status blijft staan op wat er laatst gemeten is.
S["understat"]["last_checked"] = "2026-09-09"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
