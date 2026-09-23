"""Run A, 23 sep 2026 — data/source-health.json bijwerken (§3, slot).

Geen wedstrijd in de runlijst, dus er is niets ingekocht. Wat er wél is gemeten en dus hier
hoort: de sleutelcontrole, de Fotmob-daglijst en achttien BetExplorer-fixturepagina's.
"""
import json
from datetime import date

DAY = "2026-09-23"
p = "data/source-health.json"
d = json.load(open(p))

NOTE = (
 "Run A 2026-09-23 — woensdag, interlandperiode. Geen van de 21 competities uit de runlijst "
 "speelt vandaag; met twee onafhankelijke bronnen nagetrokken voordat het als leeg is genoteerd. "
 "Methode 1: de Fotmob-daglijst van 23 sep — 28 competities, 83 wedstrijden, en daarin geen "
 "enkele hoogste divisie. Wat er wél speelt is interland- en lager voetbal (vriendschappelijke "
 "interlands, CONCACAF Nations League C, Asian Games, Gulf Cup, NPFL 10 duels, UEFA Women's "
 "Europa Cup 15, Women's Champions League 4, nationale bekers). Methode 2: achttien "
 "BetExplorer-fixturepagina's, los opgehaald — PL 20 komende duels, Serie A 20, La Liga 20, "
 "Bundesliga 18, Ligue 1 18, Eredivisie 18, Championship 12, Scottish Premiership 12, Primeira "
 "Liga 9, Pro League 9, Süper Lig 9, Danish Superliga 6, UCL/UEL/UECL elk 18, League Cup 8; nul "
 "rijen op vandaag. Ekstraklasa en Coppa Italia gaven HTTP 200 met een lege fixturetabel, dus "
 "daar bevestigt alleen Fotmob de dag. Nieuw ten opzichte van gisteren is de kalender die uit "
 "die tweede bron valt af te lezen: de eerstvolgende speelronde ligt voor de héle runlijst op "
 "9–13 oktober (9 okt La Liga, Championship, Eredivisie, Primeira Liga, Pro League, Süper Lig, "
 "Danish Superliga, Bundesliga en Ligue 1; 10 okt PL, Serie A en Scottish Premiership; 13 okt "
 "UCL; 15 okt UEL en UECL; 27 okt League Cup). De stilte is dus geen losse dag maar een "
 "aaneengesloten onderbreking van ruim twee weken. 0 wedstrijden doorgerekend, 0 bets, cap 40 "
 "bond nergens. 0 credits uitgegeven; The Odds API staat op 18.763 van 20.000 over (1.237 "
 "gebruikt deze maand). De marktbalans-controle van §1a is niet van toepassing: er is niets "
 "ingekocht omdat er niets te analyseren viel, niet omdat het plafond knelde. API_FOOTBALL_KEY "
 "ontbreekt nog steeds — bekend sinds 8 aug 2026, geen nieuwe storing. Stage 0 had niets "
 "openstaan: ledger.py open en shadow.py open gaven beide nul en er staat geen enkele pending "
 "regel in picks.jsonl (294) of shadow.jsonl (632)."
)

d["last_run"] = [e for e in d["last_run"] if not (e["run"] == "A" and e["date"] == DAY)]
d["last_run"].append({"run": "A", "date": DAY, "note": NOTE})
d["last_run"] = d["last_run"][-3:]

S = d["sources"]
S["fotmob"]["last_checked"] = DAY
S["fotmob"]["status"] = "ok"
S["fotmob"]["detail"] += (
 " Run A 23 sep 2026: daglijst opgehaald (28 competities, 83 wedstrijden), per competitie uit de "
 "runlijst getoetst met find_league op naam, ccode en aliassen — 21 van de 21 leeg. Geen fout, "
 "geen time-out; de leegte zit in de kalender en niet in de bron.")
S["betexplorer"]["last_checked"] = DAY
S["betexplorer"]["status"] = "ok"
S["betexplorer"]["detail"] += (
 " Run A 23 sep 2026: achttien fixturepagina's opgehaald als tweede bron bij een lege dag. "
 "Zestien gaven een gevulde tabel (6 tot 20 komende duels), nul rijen op vandaag; Ekstraklasa en "
 "Coppa Italia gaven HTTP 200 met een lege tabel. Niet gebruikt voor prijzen — er viel niets door "
 "te rekenen — maar wel voor de kalender: eerstvolgende speelronde 9–13 oktober.")
S["the_odds_api"]["last_checked"] = DAY
S["the_odds_api"]["status"] = "ok"
S["the_odds_api"]["detail"] += (
 " Run A 23 sep 2026: api_check.py gaf 43 actieve voetbalcompetities en 18.763 credits over van "
 "20.000 (1.237 gebruikt deze maand). Geen enkele aanroep gedaan: zonder wedstrijd in de "
 "runlijst is er geen competitie om prijzen voor te kopen.")
S["api_football"]["last_checked"] = DAY
S["api_football"]["status"] = "key_missing"
S["api_football"]["detail"] += (
 " Run A 23 sep 2026: API_FOOTBALL_KEY nog steeds niet gezet — api_check.py slaat de bron over. "
 "Onveranderd sinds 8 aug 2026, dus geen nieuwe blokkade; zie README, 'Sleutels toevoegen'.")

d["updated"] = DAY
json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", DAY, "| last_run:", [(e["run"], e["date"]) for e in d["last_run"]])
