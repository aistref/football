import json
p = "data/source-health.json"
d = json.load(open(p))
S = d["sources"]
add = {
 "fotmob": " Run B 30 aug 2026: alle vijftien spelende competities van de Run B-lijst opgehaald, geen enkele fout. xG bevestigd voor GRE (135), NOR (59, seizoen 2026), SWE (67, 2026), ESP2 (140), ITA-B (86), GER2 (146), SUI (69), AUT (38) én — NIEUW — English League One (108) ook voor het lopende 2026/2027 (has_xg=true na 3 speeldagen; de dekkingsnotitie zei nog 'alleen 2025/2026'). has_xg=false opnieuw bevestigd voor CZE (122), CRO (252), HUN (212), ROU (189), KKD (111) en ALB (260). Context (blessures, vorm, rust, stadion) en transfers opgehaald voor alle 38 duels met een tier, nul fouten.",
 "betexplorer": " Run B 30 aug 2026: veertien van de vijftien slugs leverden rijen (chance-liga 11, greece/super-league 11, norway/eliteserien 13, sweden/allsvenskan 8, croatia/hnl 3, hungary/nb-i 5, romania/superliga 11, spain/laliga2 6, italy/serie-b 4, germany/2-bundesliga 12, switzerland/super-league 5, austria/bundesliga 6, netherlands/eerste-divisie 4, england/league-one 26). albania/kategoria-superiore gaf opnieuw 0 rijen — dat gat staat nu ruim twee weken open. Naamkoppeling: 'Gyor' (BetExplorer) tegen 'Györi ETO' (Fotmob) kwam er alleen doorheen met een gelijkenismatch op het hele ploegenpaar; zonder die stap was de enige prijs van dat duel weggevallen.",
 "the_odds_api": " Run B 30 aug 2026: 56 credits over bij aanvang, plafond 9 (suggest_cap(56, 2)), alle 9 uitgegeven — 8x spreads (2. Bundesliga, Allsvenskan, Austrian Bundesliga, Eliteserien, Greek Super League, Segunda División, Serie B, Swiss Super League) en 1x totals (English League One, uit de rotatie). 47 over na de run. Alle negen sportkeys van de Run B-lijst actief. Geen enkele 4xx.",
 "api_football": " Run B 30 aug 2026: API_FOOTBALL_KEY nog steeds niet gezet (twintigste dag op rij). Blijft de enige structurele blokkade: zonder deze sleutel hangt de hele kansinput aan Fotmob alleen.",
 "oddspapi": " Run B 30 aug 2026: sleutel opnieuw niet in de omgeving. should_use(56) -> (False, 'ODDSPAPI_KEY niet gezet'); ensure_discovered() -> (False, 'ODDSPAPI_KEY niet gezet — niets te ontdekken'). De reserve is dus nog steeds niet getest en zou bij een leeg Odds API-budget niet inzetbaar zijn.",
}
for k, v in add.items():
    S[k]["detail"] = S[k]["detail"].rstrip() + v
    S[k]["last_checked"] = "2026-08-30"
for k in S:
    S[k]["last_checked"] = "2026-08-30"
d["last_run"] = {"date": "2026-08-30", "run": "B",
  "samenvatting": ("Run B 30 aug: 45 wedstrijden op de daglijst in 15 van de 17 competities, 7 op data_tier "
                   "NONE (kruis-divisie), 35 doorgerekend (cap), 3 afgekapt, 10 bets. The Odds API 56 over bij "
                   "aanvang, 9 uitgegeven (8x spreads + 1x totals), 47 na de run. API_FOOTBALL_KEY ontbreekt "
                   "(twintigste dag), OddsPapi-sleutel niet in de omgeving. Alle takken in de repo waren al in "
                   "main opgenomen; run staat op main.")}
d["updated"] = "2026-08-30"
json.dump(d, open(p, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt")
