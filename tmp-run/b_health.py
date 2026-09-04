import json, sys
sys.path.insert(0,'.')
P="data/source-health.json"
d=json.load(open(P))
d["last_run"]={"run":"B","date":"2026-09-04",
  "note":"Run B 4 sep 2026 — 8 competities met wedstrijden, 16 duels, 10 doorgerekend, 3 bets."}
def app(key, status, text, checked="2026-09-04"):
    s=d["sources"][key]; s["status"]=status; s["last_checked"]=checked
    if text not in s["detail"]: s["detail"]=s["detail"].rstrip()+" "+text
app("the_odds_api","ok",
  "4 sep 2026 (Run B): sleutel OK, 47 actieve voetbalcompetities, 19.855 credits over en 145 gebruikt deze maand. "
  "suggest_cap(19855, 26) gaf een plafond van 381; split_budget(381, 3) gaf (3, 3), dus alle drie de inkoopbare "
  "competities kregen zowel spreads als totals (6 credits), plus 5 losse btts-aanroepen à 1 credit voor de wedstrijden "
  "met een kandidaat-edge — 11 in totaal, nog 19.844 over. GEEN sportkey voor vijf competities van de runlijst met "
  "wedstrijden vandaag (Keuken Kampioen Divisie, Croatian HNL, Kategoria Superiore, Hungarian NB I, Romanian SuperLiga): "
  "die tien duels hadden daardoor alleen het gratis 1X2 van BetExplorer.")
app("api_football","key_missing",
  "4 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet — api_check.py meldt 'niet beschikbaar' bij statistieken. "
  "Fotmob vangt dat op; zie README, 'Sleutels toevoegen'.")
app("fotmob","ok",
  "4 sep 2026 (Run B): daglijst (104 competities), league-stats voor de acht competities met wedstrijden in zowel vorig "
  "als lopend seizoen, plus wedstrijdcontext en selectieverloop voor alle 16 duels — geen enkele fout. xG bevestigd "
  "AANWEZIG voor 2. Bundesliga (146; 1.528 vorig, 1.756 lopend), Eliteserien (59; 1.543 in 2025, 1.674 in 2026) en "
  "Segunda División (140; 1.360 vorig, 1.229 lopend), en opnieuw bevestigd AFWEZIG voor Keuken Kampioen Divisie (111), "
  "Croatian HNL (252), Kategoria Superiore (260), Hungarian NB I (212) en Romanian SuperLiga (189), telkens voor beide "
  "seizoenen. NIEUW GEMETEN GEBREK: de tabel van LaLiga2 2025/2026 komt binnen als 30 rijen voor een competitie van 22 "
  "ploegen — acht ploegen (Almería, Cádiz, Castellón, Córdoba, CD Mirandés, Leganés, Málaga, Sporting Gijón) staan in "
  "twee halve rijen, de ene met xg/xga/mp onder de naam zonder accenten, de andere met de stand en de thuis/uit-splits "
  "onder de naam mét accenten. Wie ze niet samenvoegt krijgt xg=None of splits=None en zet de ploeg ten onrechte op NONE. "
  "Gemeten op alle zestien tabellen van deze run trad het alleen daar op.")
app("betexplorer","ok",
  "4 sep 2026 (Run B): fixturespagina's van 2. Bundesliga (9 rijen), Keuken Kampioen Divisie (10), Eliteserien (8), "
  "Croatian HNL (5), Segunda División (11), Hungarian NB I (6) en Romanian SuperLiga (16) alle zeven HTTP 200 met odds; "
  "15 van de 16 duels van vandaag hadden een 1X2-rij. De Albanese pagina (abissnet-superiore) kwam binnen zonder een "
  "enkele fixturerij, dus Egnatia – Skënderbeu had ook geen 1X2 — dat duel viel toch al op NONE.")
app("understat","ok",
  "4 sep 2026 (Run B): niet aangeroepen — geen van de vijf gedekte competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) "
  "stond op de Run B-runlijst van vandaag.")
json.dump(d, open(P,"w"), ensure_ascii=False, indent=1)
print("bijgewerkt")
