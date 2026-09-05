import json
p = "data/source-health.json"; h = json.load(open(p))
h["last_run"] = {"run": "A", "date": "2026-09-05",
    "note": ("Run A 5 sep 2026 — 13 competities met wedstrijden, 55 duels, 35 doorgerekend "
             "(cap 35, zaterdag), 20 afgekapt, 2 op tier NONE, 6 bets.")}
h["updated"] = "2026-09-05"
ADD = {
 "fotmob": (" 5 sep 2026, Run A: alle dertien competities van de runlijst has_xg=true voor "
   "2025/2026 én 2026/2027 (PL 1.398/1.571, Serie A 1.260/1.410, La Liga 1.354/1.442, "
   "Bundesliga 1.572/1.985, Ligue 1 1.434/1.721, Championship 1.302/1.411, Eredivisie "
   "1.579/1.772, Liga Portugal 1.316/1.291, Belgische Pro League 1.460/1.589, Super Lig "
   "1.328/1.357, Schotse Premiership 1.394/1.612, Deense Superliga 1.535/1.473, Ekstraklasa "
   "1.406/1.611). Context, opstellingen en transfers voor alle 55 duels opgehaald zonder fout. "
   "BRONDEFECT GEVONDEN EN GEREPAREERD: de xG-lijsten (`ParticipantName`) schrijven clubnamen "
   "zonder accenten en de stand (`row['name']`) mét, waardoor fetch_league_stats één club in "
   "twee halve tabelrijen zette — de ene met xg/xga/mp en zonder stand, de andere met de stand "
   "en zonder xG. De run koppelt op de naam uit de daglijst en die heeft accenten, dus hij pakte "
   "structureel de helft zonder xG. Zes ploegen in drie competities van deze runlijst: Atletico "
   "Madrid en Deportivo Alaves (La Liga), Famalicao en Vitoria de Guimaraes (Liga Portugal), "
   "Standard Liege en RAAL La Louviere (Belgie). Drie duels van vandaag klapten eruit op een "
   "KeyError. Opgelost met _merge_accent_duplicates() in scripts/fotmob.py: La Liga van 22 naar "
   "20 tabelsleutels, Liga Portugal van 20 naar 18, Belgie van 18 naar 16, en geen ploeg meer "
   "zonder xG. De samenvoeging draait ook op de dagcache, zodat een bestand dat eerder op "
   "dezelfde dag is weggeschreven niet de oude vorm teruggeeft."),
 "the_odds_api": (" 5 sep 2026, Run A: quota 19844 over bij 156 gebruikt deze maand (plan is nog "
   "steeds 20.000, niet de 500 waar §1a van uitgaat). suggest_cap(19844, 26) gaf een plafond van "
   "381; split_budget(381, 13) gaf 13 spreads / 13 totals, dus alle dertien inkoopbare "
   "competities kregen beide markten. Uitgegeven: 61 credits in 61 aanroepen — 13x spreads, 13x "
   "totals, 35x btts, telkens 1 credit. Dat btts 1 en niet 2 credits kost is nu de derde "
   "bevestiging (na 1 en 2 sep); §1a rekent nog met 2, wat conservatief maar onjuist is. "
   "Sportkey soccer_spl (Schotse Premiership) werkt wél, ook al staat hij niet in de "
   "'relevante sportkeys'-lijst van api_check.py — 6 events, spreads en totals allebei. Geen "
   "enkele fout deze run."),
 "betexplorer": (" 5 sep 2026, Run A: 1X2 opgehaald voor alle dertien competities uit bestaande "
   "slugs, samen 190 fixtures-rijen waarvan 55 van vandaag. Geen nieuwe slug nodig, geen "
   "naamval die een wedstrijd zonder prijs liet. 1X2 dekte 10 van de 13 competities in de "
   "doorgerekende set (96 selecties)."),
 "api_football": (" 5 sep 2026, Run A: API_FOOTBALL_KEY ontbreekt nog steeds in de omgeving van "
   "de geplande taak. Ongewijzigd sinds 10 aug 2026. Geen afgewezen sleutel, een ontbrekende — "
   "zie README.md 'Sleutels toevoegen'. The Odds API werkt wel."),
 "understat": (" 5 sep 2026, Run A: alle vijf de gedekte competities opgehaald zonder fout (PL 20 "
   "ploegen 1.529 xG, Serie A 20 / 1.395, La Liga 20 / 1.501, Bundesliga 18 / 1.702, Ligue 1 18 "
   "/ 1.515). Gebruikt als tweede xG-model in het kalibratieblok van de 22 duels in die vijf "
   "competities die de cap haalden; niet in my_prob (§4)."),
}
for k, extra in ADD.items():
    h["sources"][k]["detail"] = h["sources"][k].get("detail", "").rstrip() + extra
    h["sources"][k]["last_checked"] = "2026-09-05"
json.dump(h, open(p, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", list(ADD))
