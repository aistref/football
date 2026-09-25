"""Run A, 25 sep 2026 — data/source-health.json bijwerken (§3, slot).

Geen wedstrijd in de runlijst, dus er is niets ingekocht. Wat er wél is gemeten en dus hier
hoort: de sleutelcontrole, twee Fotmob-daglijsten voor het inzetvenster, eenentwintig
Fotmob-daglijsten voor de lengte van de onderbreking, en achttien BetExplorer-fixturepagina's.
"""
import json

DAY = "2026-09-25"
p = "data/source-health.json"
d = json.load(open(p))

NOTE = (
 "Run A 2026-09-25 — vrijdag, interlandperiode, vijfde lege dag op rij. Geen van de 21 "
 "competities uit de runlijst speelt vandaag; met twee onafhankelijke bronnen nagetrokken "
 "voordat het als leeg is genoteerd. NIEUW VANDAAG, en dit is de eigenlijke bevinding: de "
 "lengte van de onderbreking is uitgemeten in plaats van alleen de dag van vandaag. Eenentwintig "
 "Fotmob-daglijsten van 26 september t/m 16 oktober, elk getoetst op alle 21 competities, geven "
 "van 26 september t/m 8 oktober samen NUL wedstrijden uit de runlijst. De eerstvolgende is "
 "vrijdag 9 oktober (12 duels: La Liga, Bundesliga, Ligue 1, Championship, Eredivisie, Primeira "
 "Liga 2, Pro League, Süper Lig, Danish Superliga, Ekstraklasa 2), de eerste volle speelronde is "
 "zaterdag 10 oktober (56 duels, inclusief Premier League, Serie A en Scottish Premiership), 11 "
 "okt 41 en 12 okt 9; UCL 13-14 oktober, UEL en UECL 15 oktober. Er staan dus nog dertien lege "
 "Run A-runs voor de boeg, en dat is kalender en geen storing. Methode 1: Fotmob-daglijsten van "
 "25 sep (61 competities, 104 wedstrijden) en 26 sep (118 competities), per competitie getoetst "
 "met find_league op naam, ccode en aliassen — 21 van de 21 leeg op beide dagen. Wat er wél "
 "speelt is interlandvoetbal (UEFA Nations League A/B/C, AFCON-kwalificatie in acht groepen, "
 "CONCACAF Nations League A/B, EURO U21-kwalificatie in vijf groepen, Asian Games, FIFA ASEAN "
 "Cup, twee vriendschappelijke interlands) plus lagere en buitenlandse competities (Scottish "
 "Championship 4, Ierse First Division 4, vijf Duitse Regionalliga's 13, Deense 2. en 3. "
 "Division, LaLiga2 1, Eerste Divisie 1, Braziliaanse Série B 2, USL Championship 2, NWSL 1). "
 "Methode 2: achttien BetExplorer-fixturepagina's, los opgehaald — PL 20 komende duels, Serie A "
 "20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie 18, Championship 11, Scottish "
 "Premiership 12, Primeira Liga 9, Pro League 9, Süper Lig 9, Danish Superliga 6, Ekstraklasa 2, "
 "UCL/UEL/UECL elk 18, League Cup 8; nul rijen op vandaag, en de eerstvolgende data komen exact "
 "overeen met Fotmob (9-10 oktober voor de competities, 13-15 oktober voor Europa, 27 oktober "
 "voor de League Cup). Alleen Coppa Italia gaf HTTP 200 met een lege tabel — daar bevestigt "
 "alleen Fotmob de dag. STAGE 1 IS VANDAAG VOOR HET EERST IN RUN A VIA scripts/runwindow.py "
 "gelopen: het inzetvenster [08:00 NL 25 sep, 08:00 NL 26 sep) in plaats van de UTC-dag, met "
 "include_carry_over=True omdat dit de eerste Run A met die module is. De carry-over band "
 "[00:00, 08:00) NL van 25 september leverde nul duels op — te verwachten bij een volledig "
 "Europese runlijst, maar nu gemeten in plaats van aangenomen. POORT 8 VERVALT VANDAAG "
 "(sides.LAPSES_ON = 2026-09-25); er was geen selectie om hem op toe te passen, dus de eerste "
 "run waarin dat iets doet is die van 9 oktober. 0 wedstrijden doorgerekend, 0 bets, cap 55 bond "
 "nergens. 0 credits uitgegeven; The Odds API staat op 18.719 van 20.000 over (1.281 gebruikt "
 "deze maand). De marktbalans-controle van §1a is niet van toepassing: er is niets ingekocht "
 "omdat er niets te analyseren viel, niet omdat het plafond knelde. API_FOOTBALL_KEY ontbreekt "
 "nog steeds — bekend sinds 8 aug 2026, geen nieuwe storing. Stage 0 wikkelde drie picks van Run "
 "C (24 sep) af: Namibia - Congo 1-0 gewonnen, Serbia - Greece 1-2 verloren, Liechtenstein - "
 "Lithuania 0-2 gewonnen (Under 2.5). Plus vier schaduwpicks van Run C, alle vier verloren "
 "(Norway - Denmark 3-2 half verlies op de kwartlijn, Portugal - Wales 1-0, South Korea - "
 "Ecuador 3-0, Puerto Rico - Guyana 0-1). De repo was opnieuw een ondiepe kloon; na "
 "`git fetch --unshallow origin` (386 commits) hebben 0 van de 37 takken eigen commits."
)

d["last_run"] = [e for e in d["last_run"] if not (e["run"] == "A" and e["date"] == DAY)]
d["last_run"].append({"run": "A", "date": DAY, "note": NOTE})
d["last_run"] = d["last_run"][-3:]

S = d["sources"]
S["fotmob"]["last_checked"] = DAY
S["fotmob"]["status"] = "ok"
S["fotmob"]["detail"] += (
 " Run A 25 sep 2026: 21 daglijsten opgehaald (25 sep t/m 16 okt) — twee voor het inzetvenster "
 "van vandaag en negentien om de lengte van de onderbreking uit te meten. Geen fout, geen "
 "time-out, geen lege respons; 25 sep gaf 61 competities en 104 wedstrijden, 26 sep 118 "
 "competities. Per competitie uit de runlijst getoetst met find_league op naam, ccode en "
 "aliassen: 21 van de 21 leeg tot en met 8 oktober, en vanaf 9 oktober gewoon weer gevuld. Dat "
 "laatste is het bewijs dat de leegte in de kalender zit en niet in de bron — dezelfde aanroep "
 "op dezelfde manier geeft twee weken later wél 56 wedstrijden op één dag. Ook gebruikt voor "
 "Stage 0: drie picks en vier schaduwpicks van Run C zijn op de status van deze bron afgewikkeld.")
S["betexplorer"]["last_checked"] = DAY
S["betexplorer"]["status"] = "ok"
S["betexplorer"]["detail"] += (
 " Run A 25 sep 2026: achttien fixturepagina's opgehaald als tweede bron bij een lege dag. "
 "Zeventien gaven een gevulde tabel (2 tot 20 komende duels), nul rijen op vandaag; alleen Coppa "
 "Italia gaf HTTP 200 met een lege tabel. Ekstraklasa, dat op 23 en 24 september nog leeg was, "
 "geeft nu weer 2 komende duels — die pagina is dus hersteld. Niet gebruikt voor prijzen (er "
 "viel niets door te rekenen) maar wel voor de kalender, en die komt op de dag nauwkeurig "
 "overeen met Fotmob: 9-10 oktober voor de competities, 13-15 oktober voor de Europese "
 "toernooien, 27 oktober voor de League Cup.")
S["the_odds_api"]["last_checked"] = DAY
S["the_odds_api"]["status"] = "ok"
S["the_odds_api"]["detail"] += (
 " Run A 25 sep 2026: api_check.py gaf 43 actieve voetbalcompetities en 18.719 credits over van "
 "20.000 (1.281 gebruikt deze maand). Geen enkele aanroep gedaan: zonder wedstrijd in de "
 "runlijst is er geen competitie om prijzen voor te kopen. Met dertien lege dagen voor de boeg "
 "loopt het budget deze maand nergens tegenaan.")
S["api_football"]["last_checked"] = DAY
S["api_football"]["status"] = "key_missing"
S["api_football"]["detail"] += (
 " Run A 25 sep 2026: API_FOOTBALL_KEY nog steeds niet gezet — api_check.py slaat de bron over. "
 "Onveranderd sinds 8 aug 2026, dus geen nieuwe blokkade; zie README, 'Sleutels toevoegen'.")

d["updated"] = DAY
json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", DAY, "| last_run:", [(e["run"], e["date"]) for e in d["last_run"]])
