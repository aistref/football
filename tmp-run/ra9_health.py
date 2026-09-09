"""Run A, 9 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-09"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 9 sep 2026 — 6 van de 21 competities hadden wedstrijden, samen 14 duels: Champions "
    "League 6, Championship 3, Scottish Premiership 2, Eredivisie 1, Primeira Liga 1, League Cup "
    "1. Cap 40 (woensdag), 0 afgekapt. Twaalf duels door de datadekkingspoort (6 FULL, 6 LIGHT), "
    "182 selecties over alle zes de markten, 0 bets. Eerste run waarin kruis-grensduels echt "
    "worden doorgerekend: vier van de zes UCL-duels op LIGHT via interleague.convert_team, twee "
    "op NONE (Slovan Bratislava — geen gemeten factor voor SVK; Arsenal — omgerekende verdediging "
    "0.373 onder de gemeten ondergrens 0.388).")}

TOEVOEGING = {
 "fotmob": (" Run A 9 sep 2026: daglijst gaf 6 Run A-competities met wedstrijden, 14 duels. "
   "Team-xG aanwezig voor alle vijf de nationale basiscompetities die nodig waren (Championship, "
   "Eredivisie, Primeira Liga, Scottish Premiership en de Premier League als basis voor de League "
   "Cup) én voor het lopende seizoen van alle vijf, dus blend_seasons kon overal draaien. "
   "Championship (SCO) leverde de omrekenbasis voor St. Johnstone. Voor de zes Champions "
   "League-duels leverde Fotmob via interleague.team_country de binnenlandse competitie en de "
   "stand van 2025/2026 van beide ploegen; dat werkte voor alle twaalf ploegen zonder uitval. "
   "Context opgehaald voor alle 14 duels, waarvan 13 een bruikbare rij voor ctxlog.py opleverden; "
   "het contextlogboek staat daarmee op 334. Opstellingstype: lastStarting11 voor de zes Engelse "
   "en Schotse duels, predicted voor de Eredivisie, de Primeira Liga en alle zes de Champions "
   "League-duels."),
 "betexplorer": (" Run A 9 sep 2026: fixtures-rijen voor alle zes de competities met wedstrijden, "
   "en anders dan op 8 sep gaf de Champions League-pagina deze keer WEL rijen: 12 in totaal, "
   "waarvan alle 6 van vandaag, elk met 19 boeken. De lege tabel van gisteren was dus tijdelijk "
   "en geen structurele blokkade. Dekking per competitie: Championship 3 van 3, Eredivisie 1 van "
   "1, Primeira Liga 1 van 1, Scottish Premiership 2 van 2, League Cup 1 van 1, Champions League "
   "6 van 6. Twee UCL-duels hebben in het runrapport toch geen marktgemiddelde staan (PSG – "
   "Slovan Bratislava en Napoli – Arsenal); dat is geen bronprobleem maar het gevolg van de "
   "volgorde in de analyse — die duels vallen op data_tier NONE af vóórdat er prijzen worden "
   "opgezocht."),
 "the_odds_api": (" Run A 9 sep 2026: 19.550 credits over, 450 gebruikt deze maand "
   "(api_check.py), 48 actieve voetbalcompetities. Zes sportkeys werkten met de bulk-aanroep "
   "(h2h+spreads+totals): soccer_efl_champ (17 events), soccer_netherlands_eredivisie (20), "
   "soccer_portugal_primeira_liga (11), soccer_spl (5), soccer_uefa_champs_league (12) en "
   "soccer_england_efl_cup (11). soccer_spl is deze run voor het eerst gebruikt en werkte meteen. "
   "BTTS kostte voor de derde run op rij 1 credit per wedstrijd in plaats van de 2 die §1a "
   "aanhoudt: 6 bulk-aanroepen à 3 = 18, plus 12 BTTS-aanroepen = 12, samen precies de 30 die "
   "guard meldt over 18 aanroepen. Beste prijs lag over de twaalf doorgerekende duels gemiddeld "
   "+10.03% boven het BetExplorer-marktgemiddelde (mediaan +7.25%); de uitschieter is Barcelona – "
   "Feyenoord met +25.4%, waar de beste prijs op de longshot-kant fors afwijkt van het "
   "consensusgemiddelde."),
 "api_football": (" 9 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving van "
   "de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput."),
 "understat": (" Run A 9 sep 2026: niet aangeroepen. Understat dekt PL, La Liga, Bundesliga, "
   "Serie A en Ligue 1; geen van die vijf speelde vandaag. De Championship, de Eredivisie, de "
   "Primeira Liga, de Scottish Premiership, de League Cup en de Champions League vallen buiten de "
   "dekking van deze bron. Geen storing."),
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
