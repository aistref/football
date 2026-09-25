"""Run B, 25 sep 2026 — `data/source-health.json` en `data/coverage.json` bijwerken (§3, §6b-3)."""
import json
from datetime import date

DAG = "2026-09-25"
NOTE = {
    "oddsapi": ("25 sep 2026 (Run B): OK. 43 actieve voetbalcompetities, quota 18.719 over / "
                "1.281 gebruikt deze maand. Eén bulk-aanroep (h2h + spreads + totals) voor "
                "soccer_spain_segunda_division, 3 credits; 11 events terug. De Keuken Kampioen "
                "Divisie heeft geen sportkey en is dus niet inkoopbaar."),
    "api_football": ("25 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet — ongewijzigd "
                     "sinds de eerste run. De statistiekenbron die telt ontbreekt; Fotmob vangt "
                     "dat op, zie README 'Sleutels toevoegen'."),
    "fotmob": ("25 sep 2026 (Run B): OK op alle aanroepen. Twee daglijsten (25 en 26 sep) voor "
               "runwindow, competitiestanden voor Segunda División (140) en Eerste Divisie (111) "
               "in beide seizoenen, wedstrijdcontext voor beide duels, plus La Liga 2025/2026 "
               "(87) voor de degradantenomrekening van Girona."),
    "betexplorer": ("25 sep 2026 (Run B): OK voor beide competities. spain/laliga2 gaf 11 rijen "
                    "(1 vandaag), netherlands/eerste-divisie 8 rijen (1 vandaag, 3 boeken). Voor "
                    "de Keuken Kampioen Divisie is dit de enige 1X2-bron."),
}

h = json.load(open("data/source-health.json"))
for key, note in NOTE.items():
    src = h["sources"].setdefault(key, {"status": "unknown", "role": "?", "detail": ""})
    src["last_checked"] = DAG
    if key == "api_football":
        src["status"] = "missing_key"
    else:
        src["status"] = "ok"
    src["detail"] = (src.get("detail", "") + " | " + note).strip(" |")
h["last_run"] = f"{DAG} run-b"
h["updated"] = DAG
json.dump(h, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt voor:", ", ".join(NOTE))

c = json.load(open("data/coverage.json"))
comp = c["competitions"]
comp["Segunda División (ESP)"]["notes"] += (
    " Run B 25 sep 2026: **het lopende seizoen 2026/2027 heeft nu wél xG** (has_xg=true, 22 "
    "ploegen, 6 speeldagen, avg_xg 1.299) — dat stond hierboven nog op false uit de meting van "
    "speeldag 1. Vorig seizoen blijft de basis (42 speeldagen, avg_xg 1.360) en het lopende "
    "seizoen weegt via blend_seasons mee; league_level koos route `vorig+uplift`, want 6 van 42 "
    "speeldagen is ruim onder de helft. Let op de degradanten: Girona stond niet in de "
    "Segunda-stand van 2025/2026 en kwam via promotion.convert_relegated (TIER1 -> La Liga, "
    "Fotmob 87) op een relatieve verdediging van 1.074, nét onder het gemeten bereik van "
    "SP1/SP2 omlaag (1.078-1.809, n=33). Dat is `conversion_in_range` als poort, geen bronfout: "
    "data_tier NONE, geen bet.")
comp["Keuken Kampioen Divisie (NED)"]["notes"] += (
    " Run B 25 sep 2026: has_xg=false opnieuw bevestigd voor **beide** seizoenen (2025/2026 en "
    "2026/2027), dus doelpunten als sterktemaat en LIGHT met een drempel van 16.0. De competitie "
    "wordt daardoor ook uit de gepoolde vroeg-seizoenscorrectie gelaten "
    "(model.uplift_observations: 'geen xG in vorig of lopend seizoen'). FC Dordrecht en Almere "
    "City FC staan allebei gewoon in de stand van 2025/2026, dus geen omrekening nodig. "
    "BetExplorer gaf 3 boeken voor het duel van vandaag.")
c["updated"] = DAG
json.dump(c, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage bijgewerkt voor: Segunda División (ESP), Keuken Kampioen Divisie (NED)")
