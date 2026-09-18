"""Run A, 18 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-18"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 18 sep 2026 — vrijdagavond, en voor het eerst sinds weken speelt bijna de hele "
    "binnenlandse runlijst tegelijk: 11 van de 21 competities hadden een wedstrijd, samen 12 "
    "duels. De tien lege zijn Primeira Liga, Schotse Premiership, de drie Europese toernooien "
    "(de speelweek was woensdag en donderdag afgelopen), FA Cup, League Cup, Coppa Italia, KNVB "
    "Beker en DFB Pokal. Cap 55 (vr-zo) tegen 12 duels, 0 afgekapt. Alle twaalf door de "
    "datadekkingspoort: 8 FULL en 4 LIGHT, geen enkele NONE. 171 selecties over alle zes de "
    "markten, 0 bets — hoogste herijkte edge +4.50 pp (LIGHT, drempel 16.0), hoogste op een "
    "FULL-duel +3.71 pp (drempel 8.0). Alle elf competities hebben een sportkey en kregen de "
    "volle bulk-aanroep; 38 van 734 credits, waarvan 5 aan BTTS voor de vijf duels met een "
    "kandidaat-edge. Vijf selecties haalden alle acht poorten op de ruwe schaal maar niet na de "
    "herijking (drie zonder_herijking-rijen) en drie werden op de ruwe schaal door poort 8 "
    "tegengehouden (één underdog_ruw-rij, Monaco - Lens).")}

TOEVOEGING = {
 "fotmob": (" Run A 18 sep 2026: daglijst gaf 11 Run A-competities met wedstrijden (PL 47, Serie A "
   "55, La Liga 87, Bundesliga 54, Ligue 1 53, Championship 48, Eredivisie 57, Pro League 40, "
   "Süper Lig 71, Superligaen 46, Ekstraklasa 196 met twee duels). Alle elf hebben xG in zowel "
   "het vorige als het lopende seizoen (3 tot 8 speeldagen ver). De I Liga (POL, id 197) heeft "
   "die niet — dat kwam vandaag boven water doordat Wisła Kraków en Śląsk Wrocław allebei uit "
   "die divisie zijn gepromoveerd; zie de toelichting in het runrapport. Context voor alle 12 "
   "duels opgehaald zonder fout: zeven met een voorspelde opstelling, vijf met de laatste "
   "basiself. check_venue meldde geen enkele verplaatsing."),
 "betexplorer": (" Run A 18 sep 2026: elf slugs opgehaald, alle elf raak — england/premier-league, "
   "italy/serie-a, spain/laliga, germany/bundesliga, france/ligue-1, england/championship, "
   "netherlands/eredivisie, belgium/jupiler-pro-league, turkey/super-lig, denmark/superliga en "
   "poland/ekstraklasa, samen 158 rijen waarvan 12 vandaag. Alleen gebruikt voor het "
   "kalibratieblok (§6e) en poort 8; de gespeelde prijs komt van The Odds API."),
 "the_odds_api": (" Run A 18 sep 2026: 19.119 credits over, 881 gebruikt deze maand "
   "(api_check.py, 45 actieve voetbalcompetities). Plafond suggest_cap(19119, 13) = 734, "
   "split_budget(734, 11) = 11 spreads / 11 totals; uitgegeven 33 in 11 bulk-aanroepen "
   "(h2h+spreads+totals à 3 credits) plus 5 in de tweede ronde van §1a stap 2 — BTTS voor "
   "Brentford - Chelsea, Bayern München - Union Berlin, Monaco - Lens, Widzew Łódź - Wieczysta "
   "Kraków en Wisła Kraków - Śląsk Wrocław, de vijf duels met een kandidaat-edge. Totaal 38 van "
   "734, 19.081 over. Dekking binnen de spreads-respons: vier van de twaalf duels hadden géén "
   "0.0-lijn (dus geen Draw No Bet) en vier géén ±0.5-lijn (dus geen Double Chance) — bekeken "
   "met een reden, geen gat, maar het verklaart waarom die twee markten met 15 en 9 selecties "
   "dunner meededen dan Asian Handicap (45) en Over/Under (58). Beste prijs lag over de twaalf "
   "duels met een mediaan van +5.80% boven het BetExplorer-marktgemiddelde; het gemiddelde van "
   "+9.86% wordt vandaag gedragen door één uitschieter (Union Berlin bij Bayern, +53.34% op een "
   "koers van 39.22 die sowieso buiten de koersband valt)."),
 "api_football": (" 18 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen. De kansinput kwam van Fotmob en Understat; dat vier "
   "van de twaalf duels LIGHT zijn komt door de promovendi-omrekeningen (§4), niet door deze "
   "sleutel."),
 "understat": (" Run A 18 sep 2026: aangeroepen voor alle vijf gedekte competities (EPL, Serie_A, "
   "La_liga, Bundesliga, Ligue_1 — 20/20/20/18/18 ploegen, competitiegemiddelden 1.529, 1.395, "
   "1.501, 1.702 en 1.515 xG per ploeg per duel). Gebruikt als tweede xG-model in het "
   "kalibratieblok (§6e); de overige zes competities dekt Understat niet."),
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
