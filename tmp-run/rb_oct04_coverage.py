"""coverage.json bijwerken met wat deze run per competitie heeft nagetrokken (§3 Stage 3)."""
import json

PAD = "data/coverage.json"
d = json.load(open(PAD))
C = d["competitions"]
DAG = "2026-10-04"

TOEVOEGING = {
 "Segunda División (ESP)": (
    "Run B 4 okt 2026: fotmob_id 140 opnieuw bevestigd (idcheck.py; 22 ploegen in 2025/2026 met "
    "xG, 42 speeldagen, avg_xg 1.360; lopend 2026/2027 op 8 speeldagen met xG, avg_xg 1.349). "
    "league_level koos route `vorig+uplift`: thuis 1.446 / uit 1.175 / basis 1.354. Vijf duels, "
    "vier doorgerekend op FULL of LIGHT. TWEE DINGEN OM TE ONTHOUDEN. (1) De "
    "vroeg-seizoenscorrectie kwam hier voor het eerst ONDER 1 uit — 0.9959, gepoold 0.9918 over "
    "8 speeldagen — omdat deze competitie dit seizoen juist iets mínder scoort dan vorig jaar "
    "(1.349 tegen 1.360). Dat is correct gedrag (de factor is een gemeten verhouding, geen "
    "aanname in één richting), maar de pool bestond vandaag uit PRECIES DEZE ENE competitie: de "
    "Keuken Kampioen Divisie valt eruit wegens ontbrekende xG. Lees die 0.9959 dus als 'de "
    "Segunda zelf'. (2) HET STRUCTURELE GAT IS NU DRIE RUNS OP RIJ EN DRAAIT NIET OM ÉÉN PLOEG: "
    "Sporting Gijón – Celta Fortuna kwam op NONE uit omdat Celta Fortuna uit de Primera "
    "Federación promoveerde en promotion.TIER2 geen Spaans paar LaLiga2/Primera Federación "
    "kent. Op 2 en 3 oktober was het Sabadell, vandaag een ander elftal. De foutmelding noemt "
    "alleen de TIER1-tak ('staat niet in de stand van La Liga'), wat de oorzaak makkelijk "
    "verkeerd laat lezen — de echte oorzaak is dat er onder LaLiga2 geen gemeten divisiepaar "
    "bestaat. Alle drie de gepubliceerde regels van deze run staan in deze competitie en alle "
    "drie zijn Under 2.5; dat is één mening, drie keer uitgedrukt, en het komt uit de analyse "
    "en niet uit de inkoop (alle zes markten dongen mee, 53 selecties over zes duels)."),
 "Keuken Kampioen Divisie (NED)": (
    "Run B 4 okt 2026: fotmob_id 111 bevestigd (20 ploegen 2025/2026, GEEN xG — doelpunten als "
    "sterktemaat, dus LIGHT met drempel 16.0; lopend 2026/2027 op 9 speeldagen, ook zonder xG). "
    "Eén duel, VVV-Venlo – Roda JC Kerkrade, doorgerekend op LIGHT. Geen sportkey bij The Odds "
    "API, dus alleen het gratis BetExplorer-marktgemiddelde over 3 boeken: precies drie "
    "selecties (1X2) en AH, DNB, DC, OU en BTTS staan als 'niet opgevraagd — geen sportkey' in "
    "markets_checked. Beide methodes wezen hier tegengesteld (poort 5), dus geen regel in de "
    "lijst. LET OP VOOR DE MARKTBALANS: met deze competitie als enige andere speler slaagt de "
    "controle van §1a met de kleinst mogelijke marge — één van de twee spelende competities had "
    "zowel een uitkomst- als een doelpuntenmarkt. Dat is geen te krap plafond (355 beschikbaar, "
    "6 uitgegeven) maar een competitie die bij The Odds API niet te koop is; op een dag waarop "
    "alleen deze competitie speelt, faalt die controle."),
}

for comp, tekst in TOEVOEGING.items():
    e = C[comp]
    e["notes"] = (str(e.get("notes", "")).rstrip() + " " + tekst).strip()
    e["fotmob_id_verified"] = f"{DAG} (Run B): fetch_league_stats gaf een bruikbare stand"

# De vijftien stille competities zijn vandaag niet op een stand nagetrokken via de runpipeline,
# maar wél door scripts/idcheck.py — en dat is juist de controle die voor hen bedoeld is (§run-b:
# "ook die van vandaag stil zijn"). Leg dat per competitie vast, anders is over een week niet te
# zien of GEEN WEDSTRIJD op een gecontroleerd id stond.
STIL = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
        "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
        "Romanian SuperLiga (ROU)", "Serie B (ITA)", "2. Bundesliga (GER)",
        "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)", "English League One (ENG)",
        "English League Two (ENG)", "MLS (USA)", "Série A (BRA)"]
for comp in STIL:
    C[comp]["fotmob_id_verified"] = (
        f"{DAG} (Run B): geen wedstrijd in het inzetvenster (interlandvenster), id wel "
        f"gecontroleerd door scripts/idcheck.py — bruikbare stand, afsluitcode 0")

d["updated"] = DAG
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt: notities voor", ", ".join(TOEVOEGING),
      f"+ id-bevestiging voor {len(STIL)} stille competities")
