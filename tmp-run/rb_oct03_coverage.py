"""coverage.json bijwerken met wat deze run per competitie heeft nagetrokken (§3 Stage 3)."""
import json

PAD = "data/coverage.json"
d = json.load(open(PAD))
C = d["competitions"]
DAG = "2026-10-03"

TOEVOEGING = {
 "Segunda División (ESP)": (
    "Run B 3 okt 2026: fotmob_id 140 opnieuw bevestigd (idcheck.py; 22 ploegen in 2025/2026 met "
    "xG, 42 speeldagen, avg_xg 1.360; lopend 2026/2027 op 8 speeldagen met xG, avg_xg 1.338). "
    "league_level koos route `vorig+uplift`: thuis 1.507 / uit 1.224 / basis 1.349. Vier duels, "
    "drie doorgerekend op FULL. HET GAT VAN 2 OKTOBER IS BEVESTIGD EN HET IS STRUCTUREEL: "
    "Sabadell – FC Andorra kwam op NONE uit omdat Sabadell uit de Primera Federación komt en "
    "promotion.TIER2 geen Spaans paar LaLiga2/Primera Federación kent. Dat is nu twee runs op "
    "rij in deze competitie, met een andere promovendus."),
 "Keuken Kampioen Divisie (NED)": (
    "Run B 3 okt 2026: fotmob_id 111 bevestigd (20 ploegen 2025/2026, GEEN xG — doelpunten als "
    "sterktemaat, dus LIGHT met drempel 16.0; lopend 2026/2027 op 9 speeldagen, ook zonder xG). "
    "Zes duels, alle zes doorgerekend; de drie degradanten (NAC Breda, FC Volendam) en "
    "promovendi zijn via de gemeten NED-factor omgerekend en bleven binnen het bereik. Geen "
    "sportkey bij The Odds API, dus alleen het gratis BetExplorer-marktgemiddelde over 3 boeken: "
    "elk duel kreeg precies drie selecties (1X2) en AH, DNB, DC, OU en BTTS staan als 'niet "
    "opgevraagd — geen sportkey' in markets_checked. Dat is het hele verschil met de Engelse "
    "divisies van vandaag, die er dertien per duel hadden. RKC Waalwijk – FC Emmen leverde op "
    "rangorde een regel op (+10.94 pp op een LIGHT-drempel van 16.0)."),
 "English League One (ENG)": (
    "Run B 3 okt 2026: fotmob_id 108 bevestigd (24 ploegen 2025/2026 met xG, 46 speeldagen, "
    "avg_xg 1.302; lopend 2026/2027 op 8 speeldagen, avg_xg 1.434). league_level koos route "
    "`vorig+uplift`: thuis 1.534 / uit 1.195 / basis 1.368. LET OP VOOR EEN VOLGENDE RUN: van de "
    "negen duels op de daglijst waren er ZES afgelast (AFC Wimbledon – Stevenage, Barnsley – MK "
    "Dons, Bromley – Wycombe, Luton – Doncaster, Peterborough – Notts County, Wigan – "
    "Mansfield). runwindow.matches_for_run filtert op status.cancelled, dus er kwamen drie duels "
    "in het venster; zonder die aantekening leest de dekkingstabel als een magere speelronde."),
 "English League Two (ENG)": (
    "Run B 3 okt 2026: fotmob_id 109 bevestigd (24 ploegen 2025/2026 met xG, 46 speeldagen, "
    "avg_xg 1.302; lopend 2026/2027 op 8 speeldagen, avg_xg 1.386). league_level koos route "
    "`vorig+uplift`: thuis 1.425 / uit 1.250 / basis 1.344. Acht van de elf duels in het "
    "venster, drie afgelast. Deze competitie leverde drie van de vijf gepubliceerde regels op, "
    "waaronder de enige die de drempel haalde (Accrington Stanley wint @2.54 Betfair). HETZELFDE "
    "STRUCTURELE GAT ALS BIJ DE SEGUNDA, en dat is hier nieuw vastgesteld: Rochdale – Swindon "
    "Town kwam op NONE uit omdat Rochdale uit de National League promoveerde en promotion.TIER2 "
    "geen paar League Two/National League kent. Exeter City en Rotherham United zijn wél om te "
    "rekenen (degradanten uit League One, TIER1-route met de gemeten E2/E3-factor) en kwamen "
    "daarmee op LIGHT uit — hun duel staat tweede in de dagranglijst."),
 "Série A (BRA)": (
    "Run B 3 okt 2026: fotmob_id 268 bevestigd, xG in beide kalenderjaren (2025: 20 ploegen, 38 "
    "speeldagen, avg_xg 1.267; 2026: 28 speeldagen, avg_xg 1.309). league_level koos opnieuw "
    "route `lopend` — 28 van 38 speeldagen ligt boven SEASON_MATURE_SHARE — dus thuis 1.518 / "
    "uit 1.151 / basis 1.300 en de competitie blijft uit de gepoolde vroeg-seizoenscorrectie. "
    "Eén duel, Atlético-MG – RB Bragantino, FULL, geen regel in de lijst. NAAMKOPPELING, EN DIT "
    "IS EEN ANDERE DAN HET BRIEFJE VAN 2 OKTOBER: niet de accenten (die haalt norm() weg) maar "
    "een ander deel van de naam. The Odds API schrijft 'Atletico Mineiro' en 'Bragantino-SP', "
    "Fotmob 'Atlético-MG' en 'RB Bragantino', BetExplorer 'Atletico-MG' en 'Bragantino'. Alleen "
    "BetExplorer koppelde vanzelf; bij The Odds API gaf side_of voor beide ploegen None en "
    "vielen de 1- en 2-kant van de 1X2 plus alle handicaplijnen stil weg (3 selecties in plaats "
    "van 13). Vier aliassen toegevoegd. Reken op meer hiervan: de Braziliaanse clubnamen dragen "
    "bij elke bron een andere staats- of sponsoraanduiding."),
}

for comp, tekst in TOEVOEGING.items():
    e = C[comp]
    e["notes"] = (str(e.get("notes", "")).rstrip() + " " + tekst).strip()
    e["fotmob_id_verified"] = f"{DAG} (Run B): fetch_league_stats gaf een bruikbare stand"
d["updated"] = DAG
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt voor:", ", ".join(TOEVOEGING))
