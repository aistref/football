"""Run A, 19 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-19"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 19 sep 2026 — de drukste dag tot nu toe: 13 van de 21 competities hadden een "
    "wedstrijd, samen 57 duels van 13:30 tot 21:30. De acht lege zijn de drie Europese "
    "toernooien plus alle vijf de bekers (FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB "
    "Pokal). Cap 55 (vr-zo) tegen 57 duels, dus voor het eerst sinds de verhoging van 5 sep "
    "knelt hij: 2 afgekapt (St. Johnstone - Falkirk en Lommel - KV Mechelen, allebei op een "
    "datarijkdom van 5.0 — gelijk aan het laagste duel dat het wél haalde). Van de 57 "
    "duels 40 FULL, 16 LIGHT en 1 NONE (Newcastle United - Hull City, "
    "omrekening buiten het gemeten bereik). 773 selecties over alle zes de markten, 0 bets — "
    "hoogste herijkte edge binnen de koersband +5.41 pp (FULL, drempel 8.0), hoogste LIGHT "
    "+3.77 pp (drempel 16.0). Alle dertien competities hebben een sportkey en kregen de volle "
    "bulk-aanroep; 54 van 793 credits, waarvan 15 aan BTTS voor de vijftien duels met een "
    "kandidaat-edge. Veertien selecties haalden alle acht poorten op de ruwe schaal maar niet "
    "na de herijking (acht zonder_herijking-rijen) en zes werden op de ruwe schaal door poort 8 "
    "tegengehouden (drie underdog_ruw-rijen).")}

TOEVOEGING = {
 "fotmob": (" Run A 19 sep 2026: daglijst gaf 13 Run A-competities met wedstrijden (PL 47 met 5, "
   "Serie A 55 met 4, La Liga 87 met 4, Bundesliga 54 met 5, Ligue 1 53 met 5, Championship 48 "
   "met 9, Eredivisie 57 met 4, Liga Portugal 61 met 4, Pro League 40 met 4, Süper Lig 71 met "
   "4, Premiership SCO 64 met 5, Superligaen 46 met 1 en Ekstraklasa 196 met 3) — samen 57 "
   "duels, de drukste daglijst tot nu toe. Alle dertien hebben xG in zowel het vorige als het "
   "lopende seizoen (4 tot 9 speeldagen ver). Context voor alle 57 duels opgehaald zonder één "
   "fout: 32 met een voorspelde opstelling, 25 met de laatste basiself. check_venue meldde geen "
   "enkele verplaatsing. Tweede divisies opgehaald voor de zeventien promovendi- en "
   "degradantenomrekeningen: Championship 48, League One 108, Serie B 86, LaLiga2 140, Ligue 2 "
   "110, Eerste Divisie 111, Liga Portugal 2 185, First Division B 264, 1. Lig 165 en "
   "Championship SCO 123."),
 "betexplorer": (" Run A 19 sep 2026: dertien slugs opgehaald, alle dertien raak — "
   "england/premier-league, italy/serie-a, spain/laliga, germany/bundesliga, france/ligue-1, "
   "england/championship, netherlands/eredivisie, portugal/liga-portugal, "
   "belgium/jupiler-pro-league, turkey/super-lig, scotland/premiership, denmark/superliga en "
   "poland/ekstraklasa, samen 167 rijen waarvan 57 vandaag. Alleen gebruikt voor het "
   "kalibratieblok (§6e) en poort 8; de gespeelde prijs komt van The Odds API."),
 "the_odds_api": (" Run A 19 sep 2026: 19.066 credits over, 934 gebruikt deze maand "
   "(api_check.py, 43 actieve voetbalcompetities). Plafond suggest_cap(19066, 12) = 793, "
   "split_budget(793, 13) = 13 spreads / 13 totals; uitgegeven 39 in 13 bulk-aanroepen "
   "(h2h+spreads+totals à 3 credits) plus 15 in de tweede ronde van §1a stap 2 — BTTS voor de "
   "vijftien duels met een kandidaat-edge. Totaal 54 van 793, 19.012 over. `soccer_spl` "
   "(Schotse Premiership) stond niet in de sportkey-lijst van api_check.py maar leverde wél 6 "
   "events op — de lijst is dus krapper dan wat de bulk-aanroep accepteert. Dekking binnen de "
   "spreads-respons: 22 van de 54 doorgerekende duels hadden géén 0.0-lijn (dus geen Draw No "
   "Bet) en 17 géén ±0.5-lijn (dus geen Double Chance) — bekeken met een reden, geen gat, maar "
   "het verklaart waarom die twee markten met 63 en 37 selecties dunner meededen dan Asian "
   "Handicap en Over/Under (elk 242) en 1X2 (159). Beste prijs lag over 51 duels met een "
   "mediaan van +4.96% boven het BetExplorer-marktgemiddelde (gemiddeld +5.68%, hoogste "
   "+16.37% bij Sporting CP - Arouca)."),
 "api_football": (" 19 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. De kansinput kwam van Fotmob en Understat; dat 16 van "
   "de 57 duels LIGHT zijn komt door de promovendi- en degradantenomrekeningen "
   "(§4), niet door deze sleutel."),
 "understat": (" Run A 19 sep 2026: aangeroepen voor alle vijf gedekte competities (EPL, "
   "Serie_A, La_liga, Bundesliga, Ligue_1 — 20/20/20/18/18 ploegen, competitiegemiddelden "
   "1.529, 1.395, 1.501, 1.702 en 1.515 xG per ploeg per duel). Gebruikt als tweede xG-model in "
   "het kalibratieblok (§6e); de overige acht competities dekt Understat niet."),
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
