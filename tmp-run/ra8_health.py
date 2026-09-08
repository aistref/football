"""Run A, 8 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-08"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 8 sep 2026 — 4 van de 21 competities hadden wedstrijden, samen 19 duels: "
    "Championship 6, Eredivisie 2, League Cup 5, Champions League 6. Cap 40 (maandag), 0 "
    "afgekapt. Tien duels door de datadekkingspoort (5 FULL, 5 LIGHT), 141 selecties over alle "
    "zes de markten, 0 bets. Negen op tier NONE: de zes Champions League-duels op kruis-grens "
    "(geen gemeten factor tussen twee nationale competities) en drie League Cup-duels waar een "
    "ploeg twee divisies lager speelt of de omrekening buiten bereik viel.")}

TOEVOEGING = {
 "fotmob": (" Run A 8 sep 2026: daglijst gaf 4 Run A-competities met wedstrijden, 19 duels. "
   "Team-xG aanwezig voor alle drie de nationale basiscompetities die vandaag nodig waren "
   "(Championship, Eredivisie, Premier League — die laatste als basis voor de League Cup). "
   "League One (Fotmob 108) leverde de omrekenbasis voor Cardiff City en Bolton Wanderers. "
   "Context opgehaald voor alle 19 duels, inclusief de negen met tier NONE: dat is nieuw deze "
   "run en het is bewust — §1c wil de contextsteekproef zo groot mogelijk, de duels zijn gratis "
   "en 16 van de 19 leverden een bruikbare rij voor ctxlog.py (de drie League Cup-duels zonder "
   "opstellingsblok vielen af). Het contextlogboek staat daarmee op 321. Opstellingstype: "
   "lastStarting11 voor de zes Engelse competitieduels, predicted voor de Eredivisie en alle "
   "zes de Champions League-duels."),
 "betexplorer": (" Run A 8 sep 2026: fixtures-rijen voor drie van de vier competities met "
   "wedstrijden. De Championship gaf 6 van 6 en de League Cup 5 van 5, maar de Eredivisie gaf "
   "maar 1 van 2 (FC Utrecht – Go Ahead Eagles ontbrak) en de CHAMPIONS LEAGUE-pagina gaf NUL "
   "rijen. Dat is geen HTTP-fout — de pagina laadde — maar een lege fixturetabel. Gevolg: geen "
   "marktgemiddelde voor die zeven duels, dus geen kalibratieblok (§6e) en poort 8 staat er "
   "open. Voor de Champions League maakte dat niets uit (die duels zijn NONE); voor FC Utrecht "
   "– Go Ahead Eagles is het één ontbrekend kalibratiepunt."),
 "the_odds_api": (" Run A 8 sep 2026: 19.575 credits over, 425 gebruikt deze maand "
   "(api_check.py), 47 actieve voetbalcompetities. Vier sportkeys werkten met de bulk-aanroep "
   "(h2h+spreads+totals): soccer_efl_champ, soccer_netherlands_eredivisie, "
   "soccer_uefa_champs_league en soccer_england_efl_cup. Die laatste is deze run voor het eerst "
   "gebruikt en werkte meteen: 16 events. BTTS kostte opnieuw 1 credit per wedstrijd in plaats "
   "van de 2 die §1a aanhoudt (13 duels, 13 credits; 4 bulk-aanroepen à 3 = 12, samen 25). "
   "Opnieuw bevestigd, en het staat er nog steeds op 2 in de regels. Run A "
   "gebruikte 25 van 425 credits in 17 aanroepen. Beste prijs lag over de negen duels met beide "
   "bronnen gemiddeld +5.38% boven het BetExplorer-marktgemiddelde."),
 "api_football": (" 8 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput."),
 "understat": (" Run A 8 sep 2026: niet aangeroepen. Understat dekt PL, La Liga, Bundesliga, "
   "Serie A en Ligue 1; geen van die vijf speelde vandaag. De Championship, de Eredivisie en de "
   "League Cup vallen buiten de dekking van deze bron. Geen storing."),
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
