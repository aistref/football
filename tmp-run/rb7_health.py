"""Run B, 7 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-07"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 7 sep 2026 — 7 van de 17 competities hadden wedstrijden, samen 11 duels; alle 11 "
    "doorgerekend (cap 40, maandag), 0 afgekapt, 3 op tier NONE, 89 selecties over alle zes de "
    "markten, 0 bets. Maandag in de interlandperiode: tien competities lagen stil.")}

TOEVOEGING = {
 "fotmob": (" Run B 7 sep 2026: daglijst gaf 7 Run B-competities met wedstrijden, 11 duels. "
   "Team-xG voor vijf van die zeven; de twee zonder xG (Romanian SuperLiga, Eerste Divisie) "
   "leverden wel doelpunten en thuis/uit-splits, dus LIGHT in plaats van NONE. NIEUW SINDS "
   "15 AUG: het LOPENDE seizoen heeft nu ook xG voor de Greek Super League (3 speeldagen), "
   "Serie B (3), Segunda Division (4) en English League One (5) — tot medio augustus stond dat "
   "op has_xg=false. Dat verandert de basis niet (die blijft vorig seizoen) maar wel de "
   "blend_seasons-helft. Context voor alle 11 duels opgehaald zonder fout; squad_value is 0 "
   "voor zes van de elf thuisploegen (beloftenelftallen, Roemeense en Zweedse clubs), waardoor "
   "ctxlog.out_share daar None geeft en die duels buiten het contextlogboek blijven — "
   "ontbrekende marktwaardes, geen storing."),
 "betexplorer": (" Run B 7 sep 2026: fixtures-rijen voor alle zeven competities met wedstrijden, "
   "11 van de 11 duels gedekt met een 1X2-rij. Voor de Romanian SuperLiga en de Keuken Kampioen "
   "Divisie is dit de enige prijsbron (marktgemiddelde, bookmaker niet herleidbaar). "
   "Naamkoppeling: BetExplorer kort 'Universitatea Craiova' af tot 'Univ. Craiova' en "
   "'Universitatea Cluj' tot 'U. Cluj' — twee aliassen toegevoegd, zie tmp-run/ra_names.py. "
   "Zonder die twee kwam het enige doorrekenbare Roemeense duel op nul selecties uit."),
 "the_odds_api": (" Run B 7 sep 2026: 19.597 credits over, 403 gebruikt deze maand "
   "(api_check.py). Vijf sportkeys van de Run B-lijst werkten met de bulk-aanroep "
   "(h2h+spreads+totals): soccer_greece_super_league, soccer_sweden_allsvenskan, "
   "soccer_spain_segunda_division, soccer_italy_serie_b en soccer_england_league1. BTTS kostte "
   "opnieuw 1 credit per wedstrijd en niet 2 (7 duels, 7 credits) — zesde bevestiging. Run B "
   "gebruikte 22 van 407 credits in 12 aanroepen. Beste prijs lag over de vijf duels met beide "
   "bronnen gemiddeld +7.01% boven het BetExplorer-marktgemiddelde."),
 "api_football": (" 7 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput voor de vijf competities "
   "met xG."),
 "understat": (" Run B 7 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
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
S["understat"]["last_checked"] = "2026-09-06"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
