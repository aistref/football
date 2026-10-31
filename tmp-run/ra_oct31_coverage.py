"""Run A, 31 okt 2026 — de dekkingsprobe van deze run vastleggen in coverage.json.

`coverage.json` beschrijft wat een bron in PRINCIPE dekt; `source-health.json` wat er laatst
werkte. Deze notities horen dus hier: ze zeggen wat er per competitie te halen was en met welke
route het niveau is bepaald, zodat een volgende run dat niet opnieuw hoeft uit te zoeken.

Gegenereerd uit data/run-state/2026-10-31-run-a.json in plaats van met de hand getypt: twaalf
competities met 53 duels is te veel om betrouwbaar over te typen, en overtypen is precies hoe
twee beschrijvingen van dezelfde run uiteen gaan lopen (zie §6c over het dagrapport).
"""
import json, datetime

C = json.load(open("data/coverage.json"))
COMP = C["competitions"]
DAG = "2026-10-31"

N = {
 'Premier League (ENG)': (
  'Run A 31 okt 2026: 8 duel(s) in het venster, 6 FULL/1 LIGHT/1 NONE. Basis 2025/2026 (20 ploegen, '
  'has_xg=true, avg_xg 1.398); lopend seizoen op 8 speeldagen, route vorig+uplift (thuis 1.689 / '
  'uit 1.354, basis 1.424). GEPUBLICEERD: AFC Bournemouth – Leeds United Over/Under Over 2.5 '
  '@1.9400 (+9.58 pp, tier FULL). Afgevallen: 3x edge onder drempel, 2x context spreekt de bet '
  'tegen, 1x omrekening buiten het gemeten bereik, 1x data conflicterend. 2 duel(s) met een '
  'omgerekende ploeg: Coventry City – Sunderland, Hull City – Ipswich Town. OP NONE door '
  'conversion_in_range (de reparatie van vandaag): Hull City – Ipswich Town. '
 ),
 'Serie A (ITA)': (
  'Run A 31 okt 2026: 3 duel(s) in het venster, 2 FULL/1 LIGHT. Basis 2025/2026 (20 ploegen, '
  'has_xg=true, avg_xg 1.260); lopend seizoen op 9 speeldagen, route vorig+uplift (thuis 1.413 / '
  'uit 1.273, basis 1.424). GEEN bet. Afgevallen: 3x edge onder drempel. 1 duel(s) met een '
  'omgerekende ploeg: Bologna – Monza. '
 ),
 'La Liga (ESP)': (
  'Run A 31 okt 2026: 4 duel(s) in het venster, 3 FULL/1 LIGHT. Basis 2025/2026 (20 ploegen, '
  'has_xg=true, avg_xg 1.354); lopend seizoen op 11 speeldagen, route vorig+uplift (thuis 1.742 / '
  'uit 1.241, basis 1.399). GEEN bet. Afgevallen: 2x edge onder drempel, 1x context spreekt de bet '
  'tegen, 1x data conflicterend. 1 duel(s) met een omgerekende ploeg: Real Betis – Málaga. '
 ),
 'Bundesliga (GER)': (
  'Run A 31 okt 2026: 6 duel(s) in het venster, 4 FULL/2 LIGHT. Basis 2025/2026 (18 ploegen, '
  'has_xg=true, avg_xg 1.572); lopend seizoen op 8 speeldagen, route vorig+uplift (thuis 1.968 / '
  'uit 1.613, basis 1.671). GEPUBLICEERD: Bayer Leverkusen – VfB Stuttgart Over/Under Over 3.5 '
  '@1.8700 (+10.74 pp, tier FULL). Afgevallen: 3x data conflicterend, 2x edge onder drempel. 2 '
  'duel(s) met een omgerekende ploeg: Borussia Mönchengladbach – Paderborn, Schalke 04 – RB '
  'Leipzig. '
 ),
 'Ligue 1 (FRA)': (
  'Run A 31 okt 2026: 1 duel(s) in het venster, 1 LIGHT. Basis 2025/2026 (18 ploegen, has_xg=true, '
  'avg_xg 1.434); lopend seizoen op 9 speeldagen, route vorig+uplift (thuis 1.751 / uit 1.371, '
  'basis 1.540). GEEN bet. Afgevallen: 1x edge onder drempel. 1 duel(s) met een omgerekende ploeg: '
  'Troyes – Le Mans. '
 ),
 'Championship (ENG)': (
  'Run A 31 okt 2026: 11 duel(s) in het venster, 6 FULL/5 LIGHT. Basis 2025/2026 (24 ploegen, '
  'has_xg=true, avg_xg 1.302); lopend seizoen op 13 speeldagen, route vorig+uplift (thuis 1.550 / '
  'uit 1.333, basis 1.393). GEPUBLICEERD: Middlesbrough – Charlton Athletic Over/Under Under 3.5 '
  '@1.8700 (+13.45 pp, tier FULL). Afgevallen: 9x edge onder drempel, 1x edge niet robuust over '
  'het. 5 duel(s) met een omgerekende ploeg: Lincoln City – Birmingham City, Bolton Wanderers – '
  'Bristol City, Burnley – Portsmouth, West Ham United – West Bromwich Albion, Wolverhampton '
  'Wanderers – Cardiff City. '
 ),
 'Eredivisie (NED)': (
  'Run A 31 okt 2026: 5 duel(s) in het venster, 3 FULL/2 LIGHT. Basis 2025/2026 (18 ploegen, '
  'has_xg=true, avg_xg 1.579); lopend seizoen op 10 speeldagen, route vorig+uplift (thuis 1.993 / '
  'uit 1.523, basis 1.657). GEEN bet. Afgevallen: 3x edge onder drempel, 1x data conflicterend, 1x '
  'context spreekt de bet tegen. 2 duel(s) met een omgerekende ploeg: PSV Eindhoven – Willem II, '
  'Cambuur – Go Ahead Eagles. '
 ),
 'Primeira Liga (POR)': (
  'Run A 31 okt 2026: 2 duel(s) in het venster, 2 FULL. Basis 2025/2026 (18 ploegen, has_xg=true, '
  'avg_xg 1.316); lopend seizoen op 10 speeldagen, route vorig+uplift (thuis 1.657 / uit 1.313, '
  'basis 1.335). GEPUBLICEERD: Moreirense – Estrela da Amadora Over/Under Over 2.5 @2.1368 (+9.41 '
  'pp, tier FULL). Afgevallen: 1x data conflicterend. '
 ),
 'Belgian Pro League (BEL)': (
  'Run A 31 okt 2026: 4 duel(s) in het venster, 2 FULL/2 LIGHT. Basis 2025/2026 (16 ploegen, '
  'has_xg=true, avg_xg 1.460); lopend seizoen op 10 speeldagen, route vorig+uplift (thuis 1.536 / '
  'uit 1.361, basis 1.538). GEPUBLICEERD: Anderlecht – Westerlo Over/Under Under 3.5 @1.7742 (+7.77 '
  'pp, tier FULL). Afgevallen: 3x edge onder drempel. 2 duel(s) met een omgerekende ploeg: Standard '
  'Liège – Kortrijk, SK Beveren – Union St.Gilloise. '
 ),
 'Super Lig (TUR)': (
  'Run A 31 okt 2026: 3 duel(s) in het venster, 2 FULL/1 NONE. Basis 2025/2026 (18 ploegen, '
  'has_xg=true, avg_xg 1.328); lopend seizoen op 10 speeldagen, route vorig+uplift (thuis 1.599 / '
  'uit 1.338, basis 1.399). GEEN bet. Afgevallen: 1x omrekening buiten het gemeten bereik, 1x edge '
  'onder drempel, 1x data conflicterend. 1 duel(s) met een omgerekende ploeg: Erzurumspor FK – '
  'Çorum FK. OP NONE door conversion_in_range (de reparatie van vandaag): Erzurumspor FK – Çorum '
  'FK. '
 ),
 'Scottish Premiership (SCO)': (
  'Run A 31 okt 2026: 2 duel(s) in het venster, 1 FULL/1 LIGHT. Basis 2025/2026 (12 ploegen, '
  'has_xg=true, avg_xg 1.394); lopend seizoen op 11 speeldagen, route vorig+uplift (thuis 1.750 / '
  'uit 1.280, basis 1.530). GEEN bet. Afgevallen: 2x edge onder drempel. 1 duel(s) met een '
  'omgerekende ploeg: Kilmarnock – St. Johnstone. '
 ),
 'Ekstraklasa (POL)': (
  'Run A 31 okt 2026: 4 duel(s) in het venster, 2 FULL/2 LIGHT. Basis 2025/2026 (18 ploegen, '
  'has_xg=true, avg_xg 1.407); lopend seizoen op 13 speeldagen, route vorig+uplift (thuis 1.743 / '
  'uit 1.284, basis 1.546). GEEN bet. Afgevallen: 2x edge onder drempel, 1x edge niet robuust over '
  'het, 1x data conflicterend. 2 duel(s) met een omgerekende ploeg: Wieczysta Kraków – Jagiellonia '
  'Białystok, Lech Poznań – Wisła Kraków. '
 ),
}

for comp, note in N.items():
    if comp not in COMP:
        print("ONBEKEND in coverage.json:", comp)
        continue
    COMP[comp]["notes"] = note
    COMP[comp]["last_checked"] = DAG
    print(f"{comp:30s} bijgewerkt ({len(note)} tekens)")

C["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(C, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("\ncoverage.json bijgewerkt — 12 competities.")
