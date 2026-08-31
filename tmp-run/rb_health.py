import json
h=json.load(open('data/source-health.json'))
S=h['sources']
def app(k, txt, status=None, checked="2026-08-31"):
    S[k]['detail'] = S[k]['detail'].rstrip() + " " + txt
    S[k]['last_checked'] = checked
    if status: S[k]['status'] = status

app('betexplorer',
 "Run B 31 aug 2026: 1X2 voor alle zeven competities met wedstrijden, 13 van de 13 duels gedekt. "
 "Boeken: 19 (ROU), 11 (SWE), 9 en 8 (ALB), 5 (CRO, ESP, NED), 3 (GRE) — Griekenland had vandaag "
 "maar drie boeken achter het gemiddelde. BELANGRIJK: de slug albania/abissnet-superiore WERKT nu "
 "wel en gaf 2 rijen met odds (Vora – Egnatia 2.48/3.15/2.53 en Skenderbeu – Dinamo City "
 "2.56/3.06/2.59). Dat gat stond sinds 13 aug open en is hiermee dicht; de Kategoria Superiore is "
 "aan de oddskant niet langer het knelpunt.", status='ok')

app('fotmob',
 "Run B 31 aug 2026: daglijst (79 competities), standen vorig en lopend seizoen voor alle zeven "
 "runlijstcompetities met wedstrijden, plus context en transfers voor alle 13 duels — nul fouten. "
 "xG-status opnieuw gemeten: GRE (135) heeft nu has_xg=true voor 2026/2027 (2 speeldagen) naast "
 "2025/2026; SWE (67, seizoen '2026', 19 speelronden) en ESP LaLiga2 (140) hebben xG; CRO (252), "
 "ROU (189), NED KKD (111) en ALB (260) blijven has_xg=false voor beide seizoenen. LET OP GRE: "
 "xG over mp=36 duels tegen played=26 in de tabel — de splitsrondes tellen wel in de xG en niet "
 "in de stand, precies de val uit de docstring van fetch_league_stats.")

app('the_odds_api',
 "Run B 31 aug 2026: api_check.py gaf 19.908 credits over en 92 gebruikt deze maand. Slechts 3 van "
 "de 7 competities met wedstrijden hebben een sportkey (GRE, ESP LaLiga2, SWE Allsvenskan); CRO, "
 "ROU, NED KKD en ALB hebben er geen en kregen dus alleen het gratis 1X2. 11 credits verbruikt: "
 "3x spreads, 3x totals en 5x btts. BTTS koste opnieuw 1 credit per wedstrijd en niet 2. Het "
 "plafond (suggest_cap = 9944) was nergens bindend — de beperking is het aantal sportkeys, niet "
 "het budget.")

app('api_football',
 "Run B 31 aug 2026: API_FOOTBALL_KEY nog steeds niet gezet — eenentwintigste dag op rij. Vandaag "
 "kostte het gat twee wedstrijden: Skënderbeu (ALB) en Celta Fortuna (ESP) zijn promovendi zonder "
 "historie in hun huidige divisie, en voor Kategoria Superiore en LaLiga2 kent scripts/promotion.py "
 "geen gemeten divisiepaar, dus beide duels bleven op NONE steken.")

app('understat',
 "Run B 31 aug 2026: niet aangesproken. Understat dekt alleen PL, La Liga, Bundesliga, Serie A en "
 "Ligue 1; geen enkele competitie van de Run B-lijst valt daaronder. Dat is geen storing maar een "
 "dekkingsgrens.")

h['last_run'] = {"date":"2026-08-31","run":"B",
 "samenvatting":(
  "13 wedstrijden in 7 van de 17 runlijstcompetities (maandag eind augustus). 11 door de "
  "datadekkingspoort, 2 op NONE (promovendi Skënderbeu en Celta Fortuna, geen gemeten omrekenpaar "
  "voor hun divisie). Plafond suggest_cap(19908, 1) = 9944, split_budget -> 3 spreads / 3 totals; "
  "11 credits werkelijk gebruikt (3x spreads, 3x totals, 5x btts), 19.897 over. Alle zes markten "
  "voor de 11 doorgerekende duels, progress verify groen. 6 bets, 0 afgekapt. Marktbalans 3 bets "
  "uit doelpuntenmarkten tegen 3 uit uitkomstmarkten. Nieuw: de BetExplorer-slug voor de Kategoria "
  "Superiore (albania/abissnet-superiore) geeft voor het eerst odds.")}
json.dump(h, open('data/source-health.json','w'), ensure_ascii=False, indent=1)
print("source-health bijgewerkt")
