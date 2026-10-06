"""coverage.json bijwerken met wat deze run per competitie heeft nagetrokken (§3 Stage 3)."""
import json

PAD = "data/coverage.json"
d = json.load(open(PAD))
C = d["competitions"]
DAG = "2026-10-06"

TOEVOEGING = {
 "MLS (USA)": (
    "Run B 6 okt 2026: fotmob_id 130 opnieuw bevestigd (idcheck.py; 30 ploegen in 2025 met xG, "
    "34 speeldagen, avg_xg 1.492; lopend 2026 op 28 speeldagen met xG, avg_xg 1.542). ENIGE "
    "spelende competitie van de hele runlijst, met één duel in het inzetvenster: Chicago Fire "
    "FC – Vancouver Whitecaps, aftrap 2026-10-07T00:30Z = 02:30 NL, dus van de DAGLIJST VAN "
    "MORGEN en toch van de run van vandaag (runwindow, §3 Stage 1). league_level koos route "
    "`lopend` — 28 van 34 speeldagen is ruim over de helft, dus het niveau komt rechtstreeks "
    "uit het lopende seizoen (thuis 1.832 / uit 1.391 / basis 1.531) en niet uit vorig seizoen "
    "× uplift. Dat is wat prompts/run-b.md voor de vier kalenderjaarcompetities voorschrijft "
    "sinds 24 sep, en het betekent óók dat MLS uit de gepoolde vroeg-seizoenscorrectie valt "
    "(uplift_observations); omdat MLS vandaag de enige spelende competitie was, kwam die pool "
    "op NUL waarnemingen uit en staat de factor op 1.0000. Geen defect, maar wel de reden dat "
    "het factorveld in het runrapport leeg is. Datadekking: FULL — xG in beide seizoenen, "
    "thuis/uit-splits, en de volledige wedstrijdcontext (datarijkdom 6,5 van 10; de 1,5 die "
    "ontbreekt is de opstelling, die op `lastStarting11` stond en dus voorspeld was en niet "
    "bevestigd). Geen Understat-dekking, dus één xG-model in plaats van twee."),
}

for comp, tekst in TOEVOEGING.items():
    e = C[comp]
    e["notes"] = (str(e.get("notes", "")).rstrip() + " " + tekst).strip()
    e["fotmob_id_verified"] = f"{DAG} (Run B): fetch_league_stats gaf een bruikbare stand"

STIL = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
        "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
        "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
        "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
        "Keuken Kampioen Divisie (NED)", "English League One (ENG)",
        "English League Two (ENG)", "Série A (BRA)"]
for comp in STIL:
    C[comp]["fotmob_id_verified"] = (
        f"{DAG} (Run B): geen wedstrijd in het inzetvenster (interlandvenster), id wel "
        f"gecontroleerd door scripts/idcheck.py — bruikbare stand, afsluitcode 0")

d["updated"] = DAG
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt: notitie voor", ", ".join(TOEVOEGING),
      f"+ id-bevestiging voor {len(STIL)} stille competities")
