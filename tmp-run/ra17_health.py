"""Run A, 17 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-17"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 17 sep 2026 — donderdag in de Europese speelweek: 3 van de 21 competities hadden "
    "wedstrijden, samen 12. La Liga 2 (restanten van de midweekse ronde), Europa League 9 "
    "(eerste volle speelronde van de competitiefase) en League Cup 1. Cap 40 (ma-do) tegen 12 "
    "duels, 0 afgekapt. Tien duels door de datadekkingspoort (1 FULL, 9 LIGHT), 2 op NONE "
    "(OFI Crete - Hoffenheim en Lillestrøm - Torreense, allebei op de in_range-poort van "
    "interleague.py). 141 selecties over alle zes de markten, 0 bets — hoogste herijkte edge "
    "+12.99 pp tegen een LIGHT-drempel van 16.0. Alle drie de competities hebben een sportkey "
    "en kregen de volle bulk-aanroep; 12 van 682 credits, waarvan 3 aan BTTS voor de drie duels "
    "met een kandidaat-edge. Geen enkele selectie haalde alle acht poorten op de ruwe kans, dus "
    "geen schaduwrij op de herijking; wel tien selecties die op de ruwe schaal door poort 8 "
    "werden tegengehouden, samengevat in drie underdog_ruw-rijen.")}

TOEVOEGING = {
 "fotmob": (" Run A 17 sep 2026: daglijst gaf 3 Run A-competities met wedstrijden (La Liga id 87, "
   "Europa League, League Cup id 47 als basisdivisie). La Liga en de Premier League-basis van de "
   "League Cup hebben xG in zowel het vorige als het lopende seizoen (6 respectievelijk 4 "
   "speeldagen). Context voor alle 12 duels opgehaald zonder fout; twee duels hadden een "
   "voorspelde opstelling, negen de laatste basiself en één (Lillestrøm - Torreense) geen "
   "opstellingsblok — dat laatste is een ontbrekende meting en geen storing. check_venue meldde twee "
   "verplaatsingen: Real Betis - Getafe staat in Estadio Benito Villamarín terwijl Fotmob La "
   "Cartuja als thuisbasis van Betis noteert, en Levski Sofia - Salzburg staat in het nationale "
   "Stadion Vasil Levski in plaats van Georgi Asparuhov. In beide gevallen speelt de thuisploeg "
   "in de eigen stad en gaat poort 7 gewoon open; het staat hier omdat thuisvoordeel de aanname "
   "is waar het model het zwaarst op leunt."),
 "betexplorer": (" Run A 17 sep 2026: drie slugs opgehaald (spain/laliga, europe/europa-league en "
   "england/efl-cup), alle drie raak — 12, 9 en 1 rijen, waarvan 2, 9 en 1 vandaag. Alleen "
   "gebruikt voor het kalibratieblok (§6e) en poort 8; de gespeelde prijs komt van The Odds API."),
 "the_odds_api": (" Run A 17 sep 2026: 19.134 credits over, 866 gebruikt deze maand "
   "(api_check.py, 46 actieve voetbalcompetities). Plafond suggest_cap(19134, 14) = 682, "
   "split_budget(682, 3) = 3 spreads / 3 totals; uitgegeven 9 in 3 bulk-aanroepen "
   "(h2h+spreads+totals à 3 credits) plus 3 in de tweede ronde van §1a stap 2 — BTTS voor Levski "
   "Sofia - Salzburg, Beşiktaş - Marseille en Celtic - Ferencváros, de drie duels met een "
   "kandidaat-edge. Totaal 12 van 682, 19.122 over. soccer_spain_la_liga leverde 12 events, "
   "soccer_uefa_europa_league 9 en soccer_england_efl_cup 1. Let op de dekking binnen de "
   "spreads-respons: zes van de tien doorgerekende duels hadden géén 0.0-lijn (dus geen Draw No "
   "Bet) en zes géén ±0.5-lijn (dus geen Double Chance) — dat is bekeken met een reden en geen "
   "gat, maar het verklaart waarom die twee markten vandaag met 7 en 4 selecties veel dunner "
   "meededen dan Asian Handicap (41) en Over/Under (54). Beste prijs lag over de negen duels met "
   "beide prijzen gemiddeld +6.68% boven het BetExplorer-marktgemiddelde (bereik +2.57% tot "
   "+15.88%), in lijn met de +7.78% van de meting op 5 sep."),
 "api_football": (" 17 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. De kansinput kwam van Fotmob en Understat; dat negen "
   "van de tien duels LIGHT zijn komt door de omrekeningen (§4), niet door deze sleutel."),
 "understat": (" Run A 17 sep 2026: aangeroepen voor La Liga (code La_liga, 20 ploegen, "
   "competitiegemiddelde 1.501 xG per ploeg per duel). Gebruikt als tweede xG-model in het "
   "kalibratieblok (§6e). De Europa League en de League Cup dekt Understat niet, dus daar is hij "
   "niet aangeroepen."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
S["understat"]["status"] = "ok"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")
