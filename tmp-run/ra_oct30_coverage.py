"""Run A, 30 okt 2026 — de dekkingsprobe van deze run vastleggen in coverage.json.

`coverage.json` beschrijft wat een bron in PRINCIPE dekt; `source-health.json` wat er laatst
werkte. Deze notities horen dus hier: ze zeggen wat er per competitie te halen was en met welke
route het niveau is bepaald, zodat een volgende run dat niet opnieuw hoeft uit te zoeken.
"""
import json, datetime

C = json.load(open("data/coverage.json"))
COMP = C["competitions"]
DAG = "2026-10-30"

N = {
 "La Liga (ESP)": (
  "Run A 30 okt 2026: EEN duel in het venster (Villarreal - Espanyol, 21:00 NL), doorgerekend, "
  "GEEN bet. Basis 2025/2026 (20 ploegen, has_xg=true, avg_xg 1.354); lopend seizoen op 10 van 38 "
  "speeldagen, route vorig+uplift (thuis 1.720 / uit 1.225, basis 1.402). Understat dekt dit duel "
  "wel. Afgevallen op poort 7: Villarreal mist 28% van de selectiewaarde tegen 6% bij Espanyol - "
  "Nathan Saliba (blessure), Pape Gueye (schorsing) en Ilias Akhomach (blessure). Datarijkdom 8,0, "
  "de hoogste van de run."),
 "Bundesliga (GER)": (
  "Run A 30 okt 2026: EEN duel (Elversberg - Mainz 05, 20:30 NL), doorgerekend op LIGHT, GEEN bet. "
  "Basis 2025/2026 (18 ploegen, has_xg=true, avg_xg 1.572); lopend seizoen op 7 van 34 speeldagen, "
  "route vorig+uplift (thuis 1.943 / uit 1.593, basis 1.669). ELVERSBERG IS PROMOVENDUS en is "
  "omgerekend uit de 2. Bundesliga met de gemeten D1/D2-factor, binnen bereik - dus LIGHT en de lat "
  "op 16,0 pp, die geen enkele markt haalt. UNDERSTAT DEKT DIT DUEL NIET: Elversberg stond vorig "
  "seizoen niet in de Understat-tabel. Dat is bij een promovendus te verwachten en geen storing."),
 "Ligue 1 (FRA)": (
  "Run A 30 okt 2026: DRIE duels in het venster (Le Havre - PSG en Nice - Rennes om 19:00, "
  "Lille - Lens om 21:05) - een volledige vrijdagronde, en alle DRIE leveren een regel op. Basis "
  "2025/2026 (18 ploegen, has_xg=true, avg_xg 1.434); lopend seizoen op 8 van 34 speeldagen, route "
  "vorig+uplift (thuis 1.729 / uit 1.354, basis 1.520). Understat dekt alle drie. Gepubliceerd: "
  "Nice - Rennes Over 2.5 @1,67 (+8,74 pp, de enige die de lat haalt), Lille - Lens Over 2.5 @1,94 "
  "(+7,99915 pp - 0,00085 pp onder de lat, ruw +8,37 erboven) en Le Havre - PSG Under 2.5 @3,10 "
  "(+7,07 pp, op rangorde). POORT 8 HIELD BIJ LE HAVRE DE STERKSTE SELECTIE VAN DE HELE DAG TEGEN: "
  "Le Havre +1.5 @2,09 met +12,98 pp en score 8,184, hoger dan elke gepubliceerde regel - de markt "
  "geeft Le Havre 10,7% tegen 73,6% voor PSG. Poort 9 hield in datzelfde duel de Under 3.5 tegen "
  "(+9,01 pp onder de verzwaarde lat van 10,0) en liet de 2.5 met +7,07 pp door."),
 "Championship (ENG)": (
  "Run A 30 okt 2026: EEN duel (Sheffield United - Wrexham, 21:00 NL), doorgerekend, GEEN bet. "
  "Basis 2025/2026 (24 ploegen, has_xg=true, avg_xg 1.302); lopend seizoen op 12 van 46 speeldagen, "
  "route vorig+uplift (thuis 1.531 / uit 1.317, basis 1.393). Het enige duel van de run met "
  "lineupType = lastStarting11 bij beide ploegen naast de vier andere; de rest stond op predicted."),
 "Primeira Liga (POR)": (
  "Run A 30 okt 2026: EEN duel (Casa Pia AC - Sporting CP, 21:15 NL, de laatste aftrap van de "
  "run), doorgerekend, GEEN bet. Basis 2025/2026 (18 ploegen, has_xg=true, avg_xg 1.316); lopend "
  "seizoen op 9 van 34 speeldagen, route vorig+uplift (thuis 1.636 / uit 1.297, basis 1.333). "
  "LET OP VOOR EEN VOLGENDE RUN: Casa Pia speelt zijn thuiswedstrijden VAST in het Estadio "
  "Municipal de Rio Maior, ruim 70 km van Lissabon, omdat de eigen Pina Manique niet aan de "
  "competitie-eisen voldoet. Fotmob noteert dat als hun home_ground, dus context.check_venue zet "
  "terecht GEEN relocated - het is hun thuisveld. Verwar dat niet met een verplaatsing."),
 "Belgian Pro League (BEL)": (
  "Run A 30 okt 2026: EEN duel (Zulte Waregem - Club Brugge, 20:45 NL), doorgerekend, EEN regel. "
  "Basis 2025/2026 (16 ploegen, has_xg=true, avg_xg 1.460); lopend seizoen op 9 van 30 speeldagen, "
  "route vorig+uplift (thuis 1.517 / uit 1.343, basis 1.535). Gepubliceerd: Under 3.25 @2,01 met "
  "+3,29 pp - de vierde en laatste regel, ver onder de lat en op de kant waar Sec. 6g twee "
  "procentpunt te veel kans meet, dus daarna blijft er niets over. De handicap op de thuisploeg "
  "(Zulte-Waregem +1.25 @2,04, +6,65 pp) scoorde hoger maar is door poort 8 tegengehouden: de markt "
  "geeft Zulte Waregem 14,0% tegen 66,7% voor Club Brugge."),
 "Super Lig (TUR)": (
  "Run A 30 okt 2026: EEN duel (Konyaspor - Galatasaray, 18:00 NL, de vroegste aftrap van de run), "
  "doorgerekend, GEEN bet. Basis 2025/2026 (18 ploegen, has_xg=true, avg_xg 1.328); lopend seizoen "
  "op 9 van 34 speeldagen, route vorig+uplift (thuis 1.579 / uit 1.322, basis 1.392). Eigen "
  "schatting en Pinnacle liggen hier bijna op elkaar (grootste verschil 1,7 pp op de uitzege), en "
  "met 8 doorgerekende selecties is dit het dunste duel van de run."),
 "Danish Superliga (DEN)": (
  "Run A 30 okt 2026: EEN duel (Lyngby - Randers FC, 19:00 NL), doorgerekend op LIGHT, GEEN bet. "
  "DE ENIGE COMPETITIE VAN DEZE RUN DIE OP DE `lopend`-ROUTE DRAAIT: het seizoen staat op 12 van "
  "de 22 speeldagen en is daarmee over de helft, dus het niveau komt uit het lopende seizoen zelf "
  "(thuis 1.653 / uit 1.417, basis 1.523) en niet uit vorig seizoen x uplift. Daarom is deze "
  "competitie ook OVERGESLAGEN in de gepoolde vroeg-seizoenscorrectie (die staat op 1.0930 over de "
  "acht andere) - een rijp seizoen zou zijn eigen niveauverschil anders in de factor van alle "
  "andere drukken (Sec. 3 Stage 5, punt 2). LYNGBY IS PROMOVENDUS en is omgerekend uit de NordicBet "
  "Liga met de voor DEN gemeten factor (verdedigingsfactor 1.807, de correctie van 31 aug 2026), "
  "binnen bereik, dus LIGHT met de lat op 16,0 pp."),
 "Ekstraklasa (POL)": (
  "Run A 30 okt 2026: TWEE duels (Cracovia - Motor Lublin om 18:00 en Gornik Zabrze - Legia "
  "Warszawa om 20:30 NL), beide doorgerekend, GEEN bet. Basis 2025/2026 (18 ploegen, has_xg=true, "
  "avg_xg 1.407); lopend seizoen op 12 van 34 speeldagen, route vorig+uplift (thuis 1.722 / uit "
  "1.268, basis 1.545). GORNIK - LEGIA IS AFGEVALLEN OP POORT 7, EN OP RUST IN PLAATS VAN OP "
  "BLESSURES: Gornik had 3 dagen rust tegen 5 bij Legia, precies het criterium van Sec. 1c (ten "
  "hoogste 4 dagen EN minstens 2 dagen minder dan de tegenstander). Dat is een duur besluit - de "
  "thuiszege van Gornik @2,16 staat vijfde op de ruwe dagranglijst met +3,99 pp. Het is de eerste "
  "keer in deze run dat de rust-tak van poort 7 bindt in plaats van de blessure-tak."),
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
print("\ncoverage.json bijgewerkt — 9 competities.")
