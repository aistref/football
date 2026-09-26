"""Run A, 26 sep 2026 — data/source-health.json bijwerken (§3, slot).

Geen wedstrijd in de runlijst, dus er is niets ingekocht. Wat er wél is gemeten en dus hier hoort:
de sleutelcontrole, zestien Fotmob-daglijsten (twee voor het inzetvenster, veertien voor de lengte
van de onderbreking) en eenentwintig BetExplorer-fixturepagina's.

De `detail`-velden worden elke run aangevuld en staan inmiddels op 12 tot 13 duizend tekens per
bron; deze run houdt haar toevoeging daarom kort en noteert de groei als openstaand punt in het
runrapport.
"""
import json

DAY = "2026-09-26"
p = "data/source-health.json"
d = json.load(open(p))

NOTE = (
 "Run A 2026-09-26 — zaterdag, zesde lege dag op rij. Geen van de 21 competities uit de runlijst "
 "speelt vandaag; met twee onafhankelijke bronnen nagetrokken voordat het als leeg is genoteerd. "
 "De interlandperiode is voorbij en er is vandaag juist véél voetbal — de Fotmob-daglijst van 26 "
 "sep geeft 117 competities en 449 wedstrijden — maar geen enkele hoogste divisie: de drukste "
 "competities zijn de Schotse Challenge Cup (19), League Two (12), de Engelse National League met "
 "haar noord- en zuiddivisies (elk 12), J. League 2 en 3 (elk 10), League One (9), de Nederlandse "
 "Tweede Divisie (9) en Eerste Divisie (6), Ligue 3 (8) en MLS (5). Dat is het bewijs dat het "
 "geen naamkwestie is: bij een afwijkende naam zou de competitie er wél staan, en dan zouden niet "
 "juist de laagste divisies van dezelfde landen als enige overblijven. Wat vandaag speelt hoort "
 "bij Run B. Methode 2: 21 BetExplorer-fixturepagina's, los opgehaald — 19 gaven een gevulde "
 "tabel (5 tot 20 komende duels) met nul rijen op vandaag en de eerstvolgende op 9 of 10 oktober; "
 "Coppa Italia, FA Cup en KNVB Beker gaven HTTP 200 met een lege tabel, dus voor die drie "
 "bevestigt alleen Fotmob de dag (bronbeperking, geen bevestiging). De lengte van de onderbreking "
 "is opnieuw en onafhankelijk van gisteren uitgemeten: 16 Fotmob-daglijsten van 26 sep t/m 11 okt "
 "geven van 26 september t/m 8 oktober samen NUL wedstrijden uit de runlijst, en op 9 oktober "
 "staat er weer 12 in 10 competities, op 10 oktober 56 in 12 en op 11 oktober 41 in 13. Nog twaalf "
 "lege Run A-runs te gaan; dat is kalender en geen storing. include_carry_over staat weer uit — de "
 "vlag was eenmalig voor 25 september. Poort 8 is vandaag voor het eerst een volle dag vervallen "
 "(sides.LAPSES_ON = 2026-09-25) en er was opnieuw geen selectie om hem op toe te passen; de "
 "eerste run waarin dat iets doet is die van 9 oktober. 0 wedstrijden doorgerekend, 0 bets, cap 55 "
 "bond nergens, 0 credits uitgegeven; The Odds API staat op 18.707 van 20.000 over (1.293 gebruikt "
 "deze maand). De marktbalans-controle van §1a is niet van toepassing: er is niets ingekocht omdat "
 "er niets te analyseren viel, niet omdat het plafond knelde. API_FOOTBALL_KEY ontbreekt nog "
 "steeds — bekend sinds 8 aug 2026, geen nieuwe storing. Stage 0 wikkelde vier picks van Run C (25 "
 "sep) af: Turkiye - France 0-1 (AH +1.5 Turkiye) gewonnen, Montenegro - Cyprus 2-1 gewonnen, Togo "
 "- Burundi 1-0 verloren, Rwanda - Liberia 3-1 verloren — 2 uit 4, en beide verliezers waren "
 "selecties die poort 8 vóór 25 september had tegengehouden. Plus 22 schaduwpicks (7 gewonnen, 15 "
 "verloren). BEVINDING: twee schaduwpicks zijn NIET afgewikkeld terwijl `shadow.py open` ze op de "
 "lijst zette met 'geen bronstatus; terugval op de klok'. Honduras - Suriname en El Salvador - "
 "Martinique (CONCACAF) trappen af om 01:00 en 03:00 UTC op 26 september en staan dus niet op de "
 "daglijst van 25 september, waar DayIndex ze zocht; bij navraag op de juiste daglijst stond de "
 "eerste op 2-2 met finished=False en was de tweede nog niet begonnen. Ze zijn pending gelaten. "
 "Dit is de schaduw-variant van het tijdzoneprobleem dat §3 Stage 1 op 24 september voor fixtures "
 "heeft opgelost. De repo was opnieuw een ondiepe kloon; na `git fetch --unshallow origin` (392 "
 "commits) hebben 0 van de 37 takken eigen commits, en 0 pick-id's op een tak die main niet heeft."
)

d["last_run"] = [e for e in d["last_run"] if not (e["run"] == "A" and e["date"] == DAY)]
d["last_run"].append({"run": "A", "date": DAY, "note": NOTE})
d["last_run"] = d["last_run"][-6:]

S = d["sources"]
S["fotmob"]["last_checked"] = DAY
S["fotmob"]["status"] = "ok"
S["fotmob"]["detail"] += (
 " Run A 26 sep 2026: 16 daglijsten opgehaald (26 sep t/m 11 okt) — twee voor het inzetvenster van "
 "vandaag en veertien om de lengte van de onderbreking opnieuw uit te meten. Geen fout, geen "
 "time-out, geen lege respons; 26 sep gaf 117 competities en 449 wedstrijden, 27 sep 83 "
 "competities. Per competitie uit de runlijst getoetst met find_league: 21 van de 21 leeg t/m 8 "
 "oktober, en vanaf 9 oktober gewoon weer gevuld (12, 56 en 41 duels op 9, 10 en 11 oktober). "
 "Dezelfde aanroep op dezelfde manier, dus de leegte zit in de kalender en niet in de bron. Ook "
 "gebruikt voor Stage 0: vier picks en 22 schaduwpicks zijn op de status van deze bron afgewikkeld, "
 "en twee CONCACAF-schaduwpicks zijn er juist NIET op afgewikkeld omdat ze op de daglijst van 26 "
 "sep staan met finished=False.")
S["betexplorer"]["last_checked"] = DAY
S["betexplorer"]["status"] = "ok"
S["betexplorer"]["detail"] += (
 " Run A 26 sep 2026: 21 fixturepagina's opgehaald als tweede bron bij een lege dag. Negentien "
 "gaven een gevulde tabel (5 tot 20 komende duels) met nul rijen op vandaag; Coppa Italia, FA Cup "
 "en KNVB Beker gaven HTTP 200 met een lege tabel. Ekstraklasa staat weer op 5 komende duels (2 op "
 "25 sep, leeg op 23-24 sep) en Championship op 12 (11 op 25 sep) — beide pagina's zijn dus verder "
 "hersteld. Niet gebruikt voor prijzen; de kalender komt op de dag nauwkeurig overeen met Fotmob "
 "(9-10 oktober voor de competities, 13-15 oktober voor Europa, 27 oktober voor League Cup en DFB "
 "Pokal).")
S["the_odds_api"]["last_checked"] = DAY
S["the_odds_api"]["status"] = "ok"
S["the_odds_api"]["detail"] += (
 " Run A 26 sep 2026: api_check.py gaf 43 actieve voetbalcompetities en 18.707 credits over van "
 "20.000 (1.293 gebruikt deze maand, 12 meer dan bij Run A van 25 sep). Geen enkele aanroep "
 "gedaan: zonder wedstrijd in de runlijst is er geen competitie om prijzen voor te kopen.")
S["api_football"]["last_checked"] = DAY
S["api_football"]["status"] = "missing_key"
S["api_football"]["detail"] += (
 " Run A 26 sep 2026: API_FOOTBALL_KEY nog steeds niet gezet — api_check.py slaat de bron over. "
 "Onveranderd sinds 8 aug 2026, dus geen nieuwe blokkade; zie README, 'Sleutels toevoegen'.")

d["updated"] = DAY
json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", DAY, "| last_run:", [(e["run"], e["date"]) for e in d["last_run"]])
