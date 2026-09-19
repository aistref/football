"""Run B, 19 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-19"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 19 sep 2026 — zaterdag, en de drukste Run B-dag tot nu toe: 15 van de 17 competities "
    "uit de runlijst hadden wedstrijden, samen 57 duels, met voor het eerst een volledige "
    "zaterdagronde in zowel English League One (11) als English League Two (12). Leeg: Serie B "
    "(speelt dit weekend niet) en de Kosovo Superleague (komt nog altijd niet op de "
    "Fotmob-daglijst voor, ongewijzigd sinds 13 aug 2026). Cap 55 (vr-zo) tegen 57 duels, dus 2 "
    "afgekapt — Debrecen – Vasas Budapest en FC Dinamo City – Laçi, allebei al op NONE, dus geen "
    "analyse verloren. 42 van de 57 door de datadekkingspoort: 24 FULL en 18 LIGHT. De 15 op "
    "NONE vallen in drie groepen van precies vijf: 5x geen divisiepaar voor dat land "
    "(Griekenland, Hongarije, Oostenrijk, 2x Albanië), 5x een divisie onder de onderkant van de "
    "TIER2-ketting (Tenerife, Eldense, Rochdale, York City, VfL Osnabrück) en 5x "
    "conversion_in_range (Girona, Cambridge United, Port Vale, Exeter City, Leicester City) — "
    "die laatste vijf alle vijf binnen 0,03 van het gemeten bereik, zie het runrapport. 460 "
    "selecties over alle zes de markten, 0 bets: 438 vielen af op de edge-poort, 17 op de "
    "koersband en 5 op de herijking; poort 5, 6, 7 en 8 hielden op de herijkte schaal niets "
    "tegen. Hoogste herijkte edge die geen poort raakte +5.99 pp (AH Kristiansund BK +1.25, "
    "drempel 8.0). Zes schaduwrijen: 3 underdog_ruw en 3 zonder_herijking. 9 van de 15 spelende "
    "competities hebben een sportkey en kregen alle negen de volle bulk; 35 van 791 credits, "
    "waarvan 8 aan BTTS voor alle acht duels met een kandidaat-edge.")}

TOEVOEGING = {
 "fotmob": (" Run B 19 sep 2026: daglijst gaf 15 Run B-competities met wedstrijden (Czech First "
   "League 4, Greek Super League 2, Eliteserien 2, Allsvenskan 3, Croatian HNL 2, Hungarian NB I "
   "2, Romanian SuperLiga 2, Segunda División 5, 2. Bundesliga 4, Swiss Super League 3, Austrian "
   "Bundesliga 2, Keuken Kampioen Divisie 1, English League One 11, English League Two 12, "
   "Kategoria Superiore 2). xG-dekking ongewijzigd: Greek Super League (id 135), Eliteserien "
   "(59), Allsvenskan (67), Segunda División (140), 2. Bundesliga (146), Swiss Super League "
   "(69), Austrian Bundesliga (38), English League One (108) en English League Two (109) hebben "
   "xG in vorig én lopend seizoen; Czech First League (122), Croatian HNL (252), Hungarian NB I "
   "(212), Romanian SuperLiga (189), Keuken Kampioen Divisie (111) en Kategoria Superiore (260) "
   "in geen van beide — daar komen zowel het competitieniveau als de teamsterktes uit doelpunten. "
   "Context opgehaald voor alle 57 duels zonder één fout, de beste dekking tot nu toe. "
   "check_venue meldde drie verplaatsingen (Kisvárda – Paksi SE, Real Sociedad B – Mallorca, FC "
   "Andorra – Sporting Gijón), alle drie vals-positief: het veld home_ground komt uit het "
   "clubdossier en niet uit de wedstrijd, dus een diakrietenverschil, een beloftenelftal op het "
   "eigen terrein en een club met één stadion onder twee namen. Alle drie at_away_ground=false."),
 "betexplorer": (" Run B 19 sep 2026: vijftien slugs opgehaald, VIJFTIEN raak, samen 122 rijen — "
   "Czech First League 8, Greek Super League 14, Eliteserien 7, Allsvenskan 8, Croatian HNL 4, "
   "Hungarian NB I 5, Romanian SuperLiga 14, Segunda División 11, 2. Bundesliga 7, Swiss Super "
   "League 6, Austrian Bundesliga 11, Keuken Kampioen Divisie 3, English League One 11, English "
   "League Two 12, Kategoria Superiore 1. LET OP, en dit is goed nieuws: "
   "albania/abissnet-superiore gaf op 18 sep 0 rijen en vandaag weer wél een rij. Dat was dus "
   "geen verhuisde pagina maar een lege kalender; het openstaande punt van 18 sep kan dicht."),
 "the_odds_api": (" Run B 19 sep 2026: 19.012 credits over, 988 gebruikt deze maand "
   "(api_check.py, 43 actieve voetbalcompetities). Plafond suggest_cap(19012, 12) = 791, "
   "split_budget(791, 9) = 9 spreads / 9 totals. Alle negen competities met een sportkey kregen "
   "de bulk-aanroep (h2h+spreads+totals, 3 credits): soccer_greece_super_league 14 events, "
   "soccer_norway_eliteserien 7, soccer_sweden_allsvenskan 8, soccer_spain_segunda_division 11, "
   "soccer_germany_bundesliga2 7, soccer_switzerland_superleague 6, soccer_austria_bundesliga "
   "10, soccer_england_league1 11, soccer_england_league2 12. Daarna 8 credits aan BTTS voor "
   "alle acht duels met een kandidaat-edge. Totaal 35 van 791, 18.977 over. Dekking binnen de "
   "spreads-respons blijft wisselend: 9 van de 14 doorgerekende competities hadden een "
   "handicaplijn, 7 een 0.0-lijn (Draw No Bet) en 7 een ±0.5-lijn (Double Chance) — bekeken met "
   "een reden, geen gat. De beste 1X2-prijs lag gemiddeld +6,74% boven het "
   "BetExplorer-marktgemiddelde (mediaan +6,41%) over 32 duels waar beide bronnen een prijs "
   "gaven — de ruimste steekproef die deze meting heeft gehad, in lijn met de +7,78% van 5 sep. "
   "Waar de beste prijs bij een beurs stond is hij door net_price gehaald."),
 "api_football": (" 19 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen enkel duel is hierdoor op NONE uitgekomen; alle vijftien "
   "NONE-duels gaan over een omrekening die niet kon (promotion.py), niet over een sleutel."),
 "understat": (" 19 sep 2026 (Run B): niet aangeroepen — Understat dekt alleen de vijf grote "
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
