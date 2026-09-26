"""Run B, 26 sep 2026 — `data/source-health.json` en `data/coverage.json` bijwerken (§3, §6b-3)."""
import json

DAG = "2026-09-26"
NOTE = {
    "oddsapi": ("26 sep 2026 (Run B): OK. 43 actieve voetbalcompetities, quota 18.707 over / "
                "1.293 gebruikt deze maand. Vier bulk-aanroepen (h2h + spreads + totals, 3 "
                "credits elk) voor soccer_spain_segunda_division (11 events), "
                "soccer_england_league1 (4), soccer_england_league2 (10) en soccer_usa_mls (32), "
                "plus 20 losse btts-aanroepen voor de duels met een kandidaat-edge (1 credit "
                "elk). Totaal 32 credits van een plafond van 1868. De Keuken Kampioen Divisie "
                "heeft geen sportkey en is dus niet inkoopbaar."),
    "api_football": ("26 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet — ongewijzigd "
                     "sinds de eerste run. De statistiekenbron die telt ontbreekt; Fotmob vangt "
                     "dat op, zie README 'Sleutels toevoegen'."),
    "fotmob": ("26 sep 2026 (Run B): OK op alle aanroepen. Twee daglijsten (26 en 27 sep) voor "
               "runwindow, competitiestanden voor Segunda División (140), Eerste Divisie (111), "
               "League One (108), League Two (109) en MLS (130) in beide seizoenen, "
               "wedstrijdcontext voor alle 38 duels zonder één fout, plus La Liga (87), "
               "Championship (48), League One (108) en Eredivisie (57) voor de "
               "degradantenomrekening. Ook de Stage 0-controle liep hierlangs: de daglijst van "
               "26 sep gaf Honduras – Suriname als afgelopen (2-3) en El Salvador – Martinique "
               "als nog niet afgelopen."),
    "betexplorer": ("26 sep 2026 (Run B): OK voor alle vijf de competities. spain/laliga2 11 "
                    "rijen (4 vandaag), netherlands/eerste-divisie 7 (6), england/league-one 4 "
                    "(4), england/league-two 10 (10), usa/mls 32 rijen maar 0 als 'vandaag' "
                    "gemarkeerd — de MLS-duels van deze rundag trappen in UTC pas morgen af, dus "
                    "de is_today-vlag van BetExplorer valt niet samen met het inzetvenster van "
                    "§3 Stage 1. De koppeling op namen vond ze wel, dus het kalibratieblok en "
                    "het marktoordeel voor MLS staan er compleet in."),
}

h = json.load(open("data/source-health.json"))
for key, note in NOTE.items():
    src = h["sources"].setdefault(key, {"status": "unknown", "role": "?", "detail": ""})
    src["last_checked"] = DAG
    src["status"] = "missing_key" if key == "api_football" else "ok"
    src["detail"] = (src.get("detail", "") + " | " + note).strip(" |")
h["last_run"] = f"{DAG} run-b"
h["updated"] = DAG
json.dump(h, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt voor:", ", ".join(NOTE))

c = json.load(open("data/coverage.json"))
comp = c["competitions"]
comp["English League One (ENG)"]["notes"] += (
    " Run B 26 sep 2026: xG bevestigd in **beide** seizoenen (vorig 24 ploegen / 46 speeldagen / "
    "avg_xg 1.302; lopend 7 speeldagen / avg_xg 1.426), dus FULL. `league_level` koos route "
    "`vorig+uplift`. Naamverschil vastgelegd: de runlijst noemt deze competitie \"English League "
    "One (ENG)\" en `promotion.TIER1/TIER2` kennen haar als \"League One (ENG)\" — zelfde "
    "Fotmob-id 108. Zonder die koppeling gaat elke promovendus of degradant hier ten onrechte op "
    "NONE. Cambridge United kwam na omrekening uit League Two alsnog op NONE via "
    "`conversion_in_range`: dat is de poort en geen bronfout.")
comp["English League Two (ENG)"]["notes"] += (
    " Run B 26 sep 2026: xG bevestigd in beide seizoenen (vorig 24 ploegen / 46 speeldagen / "
    "avg_xg 1.302; lopend 7 speeldagen / avg_xg 1.389), dus FULL, route `vorig+uplift`. Zelfde "
    "naamkoppeling als League One (\"League Two (ENG)\", Fotmob 109). Er is géén TIER2 onder "
    "League Two, dus een promovendus uit de National League (vandaag Rochdale en York City) komt "
    "terecht op NONE — er is geen gemeten factor voor dat divisiepaar. Exeter City en Rotherham "
    "United zijn degradanten uit League One en kwamen net buiten het gemeten bereik.")
comp["MLS (USA)"]["notes"] += (
    " Run B 26 sep 2026: xG bevestigd in beide kalenderjaren (2025: 30 ploegen, 34 speeldagen, "
    "avg_xg 1.492; 2026: 27 speeldagen, avg_xg 1.537). `league_level` koos route **`lopend`** — "
    "27 van 34 speeldagen ligt boven `SEASON_MATURE_SHARE`, dus het niveau komt uit het lopende "
    "seizoen zelf (thuis 1.820 / uit 1.389 / basis 1.527) en MLS blijft uit de gepoolde "
    "vroeg-seizoenscorrectie. Alle 30 ploegen stonden in de stand van 2025, dus geen "
    "uitbreidingsploeg zonder historie vandaag. Veertien duels, allemaal via het inzetvenster "
    "van §3 Stage 1 — vijf op de daglijst van 26 sep en negen op die van 27 sep.")
comp["Segunda División (ESP)"]["notes"] += (
    " Run B 26 sep 2026: xG in beide seizoenen bevestigd (lopend 7 speeldagen, avg_xg 1.312), "
    "route `vorig+uplift`. Celta Fortuna, Sabadell en Tenerife stonden niet in de stand van "
    "2025/2026 en zijn promovendi uit de Primera Federación; er is géén TIER2 onder LaLiga2, dus "
    "die drie komen op NONE. Dat kostte vandaag twee van de vier Spaanse duels.")
comp["Keuken Kampioen Divisie (NED)"]["notes"] += (
    " Run B 26 sep 2026: has_xg=false opnieuw bevestigd voor beide seizoenen, dus doelpunten als "
    "sterktemaat, LIGHT en een drempel van 16.0; de competitie blijft uit de gepoolde "
    "vroeg-seizoenscorrectie. Heracles, FC Volendam en NAC Breda zijn degradanten uit de "
    "Eredivisie en zijn met de gemeten NED-factor omgerekend (TIER1 -> Eredivisie, Fotmob 57), "
    "alle drie binnen bereik. Zes duels, alle zes op het gratis BetExplorer-marktgemiddelde: "
    "AH, DNB, DC, OU en BTTS zijn hier niet te koop.")
c["updated"] = DAG
json.dump(c, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage bijgewerkt voor:", ", ".join(["English League One (ENG)", "English League Two (ENG)",
      "MLS (USA)", "Segunda División (ESP)", "Keuken Kampioen Divisie (NED)"]))
