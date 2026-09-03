import json, sys
sys.path.insert(0,'.')
P="data/source-health.json"
d=json.load(open(P))
d["last_run"]={"run":"B","date":"2026-09-03",
  "note":"Run B 3 sep 2026 — 3 competities met wedstrijden, 4 duels, alle 4 doorgerekend, 1 bet."}
def app(key, status, text, checked="2026-09-03"):
    s=d["sources"][key]; s["status"]=status; s["last_checked"]=checked
    if text not in s["detail"]: s["detail"]=s["detail"].rstrip()+" "+text
app("the_odds_api","ok",
  "3 sep 2026 (Run B): sleutel OK, 47 actieve voetbalcompetities, 19.896 credits over en 104 gebruikt deze maand (20K-plan). "
  "Gekocht: spreads en totals voor Allsvenskan en Swiss Super League (4 credits) plus btts per wedstrijd voor de drie duels "
  "met een event (3 credits) — 7 in totaal. GEEN sportkey voor de Hungarian NB I: dat duel had daardoor alleen het gratis 1X2.")
app("api_football","key_missing",
  "3 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet — api_check.py meldt 'niet beschikbaar' bij statistieken. "
  "Fotmob vangt dat op; zie README, 'Sleutels toevoegen'.")
app("fotmob","ok",
  "3 sep 2026 (Run B): daglijst (44 competities), league-stats voor Allsvenskan 2025/2026 (16 ploegen, xG) en 2026 (18,8 speeldagen, xG), "
  "Hungarian NB I 2025/2026 en 2026/2027 (beide zonder xG, ongewijzigd sinds 9 aug) en Swiss Super League 2025/2026 en 2026/2027 (beide met xG), "
  "plus wedstrijdcontext en selectieverloop voor alle 4 de duels. Geen enkele fout.")
app("betexplorer","ok",
  "3 sep 2026 (Run B): fixturespagina's van Allsvenskan (9 rijen), Hungarian NB I (7) en Swiss Super League (8) alle drie HTTP 200 met odds; "
  "alle 4 de duels van vandaag hadden een 1X2-rij.")
app("understat","ok",
  "3 sep 2026 (Run B): niet aangeroepen — geen van de vijf gedekte competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) stond op de Run B-runlijst van vandaag.")
json.dump(d, open(P,"w"), ensure_ascii=False, indent=1)
print("bijgewerkt")
