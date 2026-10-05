"""coverage.json bijwerken met wat deze run per competitie heeft nagetrokken (§3 Stage 3)."""
import json

PAD = "data/coverage.json"
d = json.load(open(PAD))
C = d["competitions"]
DAG = "2026-10-05"

TOEVOEGING = {
 "Segunda División (ESP)": (
    "Run B 5 okt 2026: fotmob_id 140 opnieuw bevestigd (idcheck.py; 22 ploegen in 2025/2026 met "
    "xG, 42 speeldagen, avg_xg 1.360; lopend 2026/2027 op 8 speeldagen met xG, avg_xg 1.359). "
    "league_level koos route `vorig+uplift`: thuis 1.452 / uit 1.179 / basis 1.359, met een "
    "vroeg-seizoensfactor van 0.9995 op een pool van PRECIES DEZE ENE competitie — lees die "
    "factor dus als 'de Segunda zelf' en niet als een gepoolde correctie. Eén duel in het "
    "inzetvenster, Córdoba – Tenerife (20:30 NL), en het kwam op NONE uit: VIERDE RUN OP RIJ "
    "HETZELFDE GAT, en vandaag kostte het de enige wedstrijd van de hele run. Tenerife staat "
    "niet in de Segunda-stand van 2025/2026 en ook niet in die van La Liga — het promoveerde uit "
    "de Primera Federación — en promotion.TIER2 kent geen Spaans paar LaLiga2/Primera "
    "Federación, dus er is geen tak om langs om te rekenen. De foutmelding noemt alleen de "
    "TIER1-tak ('staat niet in de stand van La Liga'), wat de oorzaak verkeerd laat lezen; op 2 "
    "en 3 okt was het Sabadell, op 4 okt Celta Fortuna, vandaag Tenerife. NIEUW GEMETEN VANDAAG "
    "en het scherpt de vraag aan: Tenerife heeft 7 duels LaLiga2 MÉT xG in het LOPENDE seizoen "
    "(6.2 xG / 8.2 xGA, 11 punten) — de data op het niveau waarop gespeeld wordt bestaat dus "
    "wél, wat ontbreekt is een prior uit vorig seizoen voor blend_seasons. De dekkingstabel "
    "zet deze competitie daarom op BUITEN DATADEKKING: van de vier statussen die §5 toestaat is "
    "dat de enige die klopt, maar de bron faalde niet — Fotmob leverde stand, xG en de volledige "
    "wedstrijdcontext (datarijkdom 5.0). Beide rapporten noemen dat verschil expliciet."),
}

for comp, tekst in TOEVOEGING.items():
    e = C[comp]
    e["notes"] = (str(e.get("notes", "")).rstrip() + " " + tekst).strip()
    e["fotmob_id_verified"] = f"{DAG} (Run B): fetch_league_stats gaf een bruikbare stand"

STIL = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
        "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
        "Romanian SuperLiga (ROU)", "Serie B (ITA)", "2. Bundesliga (GER)",
        "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
        "Keuken Kampioen Divisie (NED)", "English League One (ENG)",
        "English League Two (ENG)", "MLS (USA)", "Série A (BRA)"]
for comp in STIL:
    C[comp]["fotmob_id_verified"] = (
        f"{DAG} (Run B): geen wedstrijd in het inzetvenster (interlandvenster), id wel "
        f"gecontroleerd door scripts/idcheck.py — bruikbare stand, afsluitcode 0")

d["updated"] = DAG
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt: notitie voor", ", ".join(TOEVOEGING),
      f"+ id-bevestiging voor {len(STIL)} stille competities")
