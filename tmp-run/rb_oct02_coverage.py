"""coverage.json bijwerken met wat deze run per competitie heeft nagetrokken (§3 Stage 3)."""
import json

PAD = "data/coverage.json"
d = json.load(open(PAD))
C = d["competitions"]
DAG = "2026-10-02"

TOEVOEGING = {
 "Segunda División (ESP)": (
    "Run B 2 okt 2026: fotmob_id 140 opnieuw bevestigd (idcheck.py, 22 ploegen in 2025/2026 met "
    "xG, 42 speeldagen, avg_xg 1.360; lopend 2026/2027 op 7 speeldagen met xG, avg_xg 1.328). "
    "league_level koos route `vorig+uplift` (7 van 42 speeldagen ligt onder SEASON_MATURE_SHARE): "
    "thuis 1.436 / uit 1.167 / basis 1.345. Eén duel, Eldense – Real Oviedo, en het kwam op "
    "data_tier NONE uit. Real Oviedo is wél om te rekenen (degradant uit La Liga, TIER1-route, "
    "gemeten ESP-factor uit football-data SP1/SP2), maar Eldense niet: die komt uit de Primera "
    "Federación en promotion.TIER2 heeft geen gemeten Spaans paar LaLiga2/Primera Federación. "
    "LET OP VOOR EEN VOLGENDE RUN: dit is een structureel gat in deze competitie, niet een "
    "incident. De Segunda telt elk seizoen drie promovendi uit de Primera Federación en die "
    "blijven NONE zolang dat paar niet is gemeten; de bulk-aanroep van 3 credits is dan al "
    "gedaan, want §1a koopt op datakwaliteit van de competitie en niet van het duel."),
 "Keuken Kampioen Divisie (NED)": (
    "Run B 2 okt 2026: fotmob_id 111 bevestigd (20 ploegen 2025/2026, GEEN xG — doelpunten als "
    "sterktemaat, dus LIGHT met drempel 16.0; lopend 2026/2027 op 9 speeldagen, ook zonder xG). "
    "Eén duel: Helmond Sport – Heracles. Heracles is degradant uit de Eredivisie en omgerekend "
    "langs TIER1 met de gepoolde down-factor (Eredivisie/KKD is niet apart gemeten), binnen het "
    "bereik. Geen sportkey bij The Odds API, dus alleen het gratis BetExplorer-marktgemiddelde en "
    "dat kwam over maar 3 boeken; AH, DNB, DC, OU en BTTS staan als 'niet opgevraagd — geen "
    "sportkey' in markets_checked. NIEUW GEMETEN EN VAST TE HOUDEN: Fotmob geeft voor Helmond "
    "Sport geen selectiewaarde (squad_value 0,0), waardoor dit duel stil buiten het "
    "contextlogboek valt (ctxlog.out_share eist een noemer). Dat raakt deze competitie "
    "structureel, niet alleen vandaag."),
 "Série A (BRA)": (
    "Run B 2 okt 2026: fotmob_id 268 bevestigd, xG in beide kalenderjaren (2025: 20 ploegen, 38 "
    "speeldagen, avg_xg 1.267; 2026: 28 speeldagen, avg_xg 1.309). league_level koos route "
    "`lopend` — 28 van 38 speeldagen ligt boven SEASON_MATURE_SHARE — dus het niveau komt uit het "
    "lopende seizoen zelf (thuis 1.520 / uit 1.148 / basis 1.300) en de competitie blijft uit de "
    "gepoolde vroeg-seizoenscorrectie, precies zoals bij MLS, Eliteserien en Allsvenskan. Eén "
    "duel, São Paulo – Santos, FULL, en het leverde de enige bet van de run op: Over 2.5 @2.15 "
    "bij Unibet (SE), op rangorde onder §5b (+3.68 pp op een drempel van 8.0). Alle zes markten "
    "werkelijk te koop via de bulk plus één BTTS-verzoek. Naamkoppeling: The Odds API en "
    "BetExplorer schrijven 'Sao Paulo' zonder accent, Fotmob 'São Paulo' — resolve() koppelt dat, "
    "maar houd het in het oog bij andere Braziliaanse namen met diakrieten."),
}

for comp, tekst in TOEVOEGING.items():
    e = C[comp]
    e["notes"] = (str(e.get("notes", "")).rstrip() + " " + tekst).strip()
    e["fotmob_id_verified"] = f"{DAG} (Run B): fetch_league_stats gaf een bruikbare stand"
d["updated"] = DAG
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt voor:", ", ".join(TOEVOEGING))
