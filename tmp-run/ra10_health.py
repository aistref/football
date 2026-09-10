"""Run A, 9 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-10"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 10 sep 2026 — 2 van de 21 competities hadden wedstrijden, samen 7 duels: Champions "
    "League 6, Primeira Liga 1. Cap 40 (donderdag), 0 afgekapt. Zes duels door de "
    "datadekkingspoort (1 FULL, 5 LIGHT), 96 selecties over alle zes de markten, 0 bets. Vijf "
    "van de zes UCL-duels op LIGHT via interleague.convert_team; Bayern München valt op NONE "
    "omdat zijn omgerekende aanval (2.742) boven de gemeten bovengrens 2.432 uitkomt. Geen "
    "enkele selectie binnen de koersband had een positieve herijkte edge — hoogste -0.80 pp.")}

TOEVOEGING = {
 "fotmob": (" Run A 10 sep 2026: daglijst gaf 2 Run A-competities met wedstrijden, 7 duels. "
   "Team-xG aanwezig voor de enige nationale basiscompetitie die nodig was (Primeira Liga), zowel "
   "voor 2025/2026 als voor het lopende seizoen (5 speeldagen), dus blend_seasons kon daar "
   "draaien. Voor de zes Champions League-duels leverde Fotmob via interleague.team_country de "
   "binnenlandse competitie en de stand van 2025/2026 van beide ploegen; dat werkte voor alle "
   "twaalf ploegen zonder uitval — de enige afwijzing (Bayern) komt van de bereikpoort en niet "
   "van een ontbrekende meting. Context opgehaald voor alle 7 duels, alle 7 bruikbaar voor "
   "ctxlog.py; het contextlogboek staat daarmee op 343. Opstellingstype: predicted voor alle "
   "zeven duels — geen enkele bevestigde opstelling op het moment van de run (04:0x), wat voor "
   "avondwedstrijden normaal is."),
 "betexplorer": (" Run A 10 sep 2026: fixtures-rijen voor beide competities met wedstrijden. "
   "Champions League 6 rijen, alle 6 van vandaag, met 18 tot 19 boeken per rij; Primeira Liga 10 "
   "rijen waarvan 1 van vandaag, met 11 tot 12 boeken. Dekking dus 7 van 7. Net als op 9 sep gaf "
   "de Champions League-pagina gewoon rijen — de lege tabel van 8 sep blijft daarmee een "
   "incident."),
 "the_odds_api": (" Run A 10 sep 2026: 19.520 credits over, 480 gebruikt deze maand "
   "(api_check.py), 47 actieve voetbalcompetities. Twee sportkeys werkten met de bulk-aanroep "
   "(h2h+spreads+totals): soccer_portugal_primeira_liga (10 events) en soccer_uefa_champs_league "
   "(6 events). BTTS kostte voor de vierde run op rij 1 credit per wedstrijd in plaats van de 2 "
   "die §1a aanhoudt: 2 bulk-aanroepen à 3 = 6, plus 6 BTTS-aanroepen = 6, samen precies de 12 "
   "die guard meldt over 8 aanroepen. Dat verschil met de regel is inmiddels structureel genoeg "
   "om te noteren, niet om §1a op te wijzigen — het maakt BTTS goedkoper dan begroot, nooit "
   "duurder. Beste prijs lag over de zes doorgerekende duels gemiddeld +8.27% boven het "
   "BetExplorer-marktgemiddelde (mediaan +6.38%); de uitschieter is Manchester United – Sabah FK "
   "met +21.04%, waar de spreiding tussen boeken op een zware favoriet groot is."),
 "api_football": (" 10 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput."),
 "understat": (" Run A 10 sep 2026: niet aangeroepen. Understat dekt PL, La Liga, Bundesliga, "
   "Serie A en Ligue 1; geen van die vijf speelde vandaag. De Primeira Liga en de Champions "
   "League vallen buiten de dekking van deze bron. Geen storing."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
# Understat is deze run niet geprobeerd; status blijft staan op wat er laatst gemeten is.

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
