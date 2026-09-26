"""Run A, 26 sep 2026 — run-state wegschrijven.

Zesde dag op rij zonder wedstrijd in de runlijst. Twee dingen zijn vandaag anders dan op 25 sep:

1. **`include_carry_over` staat weer uit.** De vlag was eenmalig voor de overstapdag; hem laten
   staan zou de band [00:00, 08:00) NL van 26 sep in twee runrapporten zetten (§3, Stage 1).
2. **Poort 8 is vanaf vandaag voor het eerst een volle dag vervallen** in plaats van op de
   vervaldatum zelf te staan. Er was opnieuw geen selectie om hem op toe te passen.

En één ding dat níet over deze rundag gaat maar wel in het bestand hoort: de terugval van twee uur
in `settling.py` stond op het punt twee schaduwpicks op een verkeerde stand af te wikkelen. Zie
`afwikkeling.bevinding`.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 26)
STAGE3 = json.load(open("tmp-run/ra26_stage3.json"))
BEV = json.load(open("tmp-run/ra26_bevestiging.json"))
GAP = json.load(open("tmp-run/ra26_gap.json"))
SETTLE = json.load(open("tmp-run/ra26_settle.json"))

state = load_or_start("a", DAY)

# eerstvolgende speeldag per competitie uit de Fotmob-scan
eerste_fotmob = {}
for d, hits in sorted(GAP["scan"].items()):
    for naam in hits:
        eerste_fotmob.setdefault(naam, d)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    tweede = (BEV.get(naam) or GAP["cups"].get(naam) or {})
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 26 sep, 08:00 NL 27 sep) — "
                 "nul op beide Fotmob-daglijsten (26 en 27 sep), bevestigd met BetExplorer",
        "eerstvolgende_betexplorer": tweede.get("eerste"),
        "eerstvolgende_fotmob": eerste_fotmob.get(naam, "geen binnen 16 dagen"),
    })

state["parameters"] = {
    "MAX_DEEP_ANALYSES": ranking.max_deep_analyses(DAY),
    "MAX_SHORTLIST": ranking.max_shortlist(DAY),
    "EDGE_THRESHOLD_FULL": 8.0,
    "EDGE_THRESHOLD_LIGHT": 16.0,
    "MAX_LIGHT_IN_SHORTLIST": 2,
    "MIN_ODDS": 1.30,
    "MAX_ODDS": 6.00,
    "SHRINK": 1.00,
    "XG_WEIGHT": 0.80,
    "CREDIBILITY_K": 8,
    "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
    "afgekapt": 0,
    "afkapping": {"cap": ranking.max_deep_analyses(DAY), "afgekapt": 0,
                  "laagste_die_het_haalde": None, "hoogste_die_afviel": None, "lijst": [],
                  "reden": "0 wedstrijden in de runlijst, dus de cap bond nergens"},
    "HERIJKING": "niet toegepast — er is geen wedstrijd doorgerekend. De fit zelf is wel gelezen "
                 "en staat in het runrapport onder 'Stand van het logboek'.",
    "POORT8": {
        "lapses_on": str(sides.LAPSES_ON),
        "actief_vandaag": sides.LAPSES_ON > DAY,
        "toelichting":
            "Eerste volle dag ná de vervaldatum van §1e: sides.check() laat elke kant door en zet "
            "alleen nog would_block. Deze run heeft daar niets van gemerkt — er was geen selectie "
            "om te toetsen. De eerste Run A waarin het vervallen van poort 8 werkelijk iets kan "
            "doen is die van 9 oktober; leg daar poort8_vervallen per selectie vast en zet "
            "poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een gepubliceerde bet "
            "wordt.",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 26 sep 2026, 08:00 27 sep 2026)",
    "include_carry_over": False,
    "reden_carry_over":
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap. Run A van 25 september heeft "
        "de band [00:00, 08:00) NL van die dag ingehaald; hem vandaag opnieuw meenemen zou "
        "dezelfde wedstrijd in twee runrapporten zetten.",
    "daglijsten": {"2026-09-26": 117, "2026-09-27": 83},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.707 van de 20.000 over (api_check.py).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1":
        "Fotmob-daglijsten van 26 en 27 sep 2026 (117 respectievelijk 83 competities; 449 "
        "wedstrijden op 26 sep), per competitie uit de runlijst getoetst met find_league op naam, "
        "ccode en aliassen — 21 van de 21 leeg, op beide dagen. Er is dus véél voetbal vandaag, "
        "alleen geen hoogste divisie: de drukste competities op de daglijst zijn de Schotse "
        "Challenge Cup (19), League Two (12), de Engelse National League en haar noord- en "
        "zuiddivisies (elk 12), J. League 2 en 3 (elk 10), League One (9), de Nederlandse Tweede "
        "Divisie (9) en Eerste Divisie (6), Ligue 3 (8) en MLS (5). Dat is het bewijs dat het "
        "geen naamkwestie is: bij een afwijkende naam zou de competitie er wél staan en zouden "
        "de laagste divisies van dezelfde landen niet als enige overblijven.",
    "methode_2":
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 komende "
        "duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie 18, Championship 12, "
        "Scottish Premiership 12, Primeira Liga 9, Pro League 9, Süper Lig 9, Danish Superliga 6, "
        "Ekstraklasa 5, UCL/UEL/UECL elk 18, League Cup 8 — nul daarvan op vandaag, en de "
        "eerstvolgende staat overal op 9 of 10 oktober. Coppa Italia gaf HTTP 200 met een lege "
        "tabel. Plus de drie bekers die gisteren buiten de tweede bron vielen: DFB Pokal 16 "
        "komende duels met de eerste op 27 oktober; FA Cup en KNVB Beker geven bij BetExplorer "
        "een lege tabel, dus voor die twee blijft Fotmob de enige bron — dat is een "
        "bronbeperking en geen bevestiging, en het hoort zo opgeschreven te staan.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil tot 9 oktober. "
                 "GEEN WEDSTRIJD is de uitkomst, geen storing (Stage 2).",
    "context":
        "Zesde dag op rij. De interlandperiode is voorbij — het interlandvoetbal dat op 25 "
        "september de daglijst vulde is vandaag weg — maar de clubcompetities uit déze runlijst "
        "beginnen pas op 9 oktober weer. Wat vandaag wél speelt zijn de lagere divisies, en die "
        "horen bij Run B. Meld hun ontbreken hier dus niet als gat (run-a.md).",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "lege_runs_nog_te_gaan": 12,
        "gemeten_met": "tmp-run/ra26_gap.py — 16 Fotmob-daglijsten van 26 sep t/m 11 okt, per dag "
                       "getoetst op alle 21 competities uit de runlijst. Onafhankelijk van de "
                       "scan van 25 september, en met dezelfde uitkomst.",
    },
    "eerstvolgende_speelronde": eerste_fotmob,
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst in 12 competities; 9 okt is "
                        "de vrijdagavond met 12 duels in 10 competities, 11 okt 41 in 13)",
    "bekers": "FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal staan in de hele "
              "gemeten periode t/m 11 oktober niet op een Fotmob-daglijst. BetExplorer zet de "
              "League Cup op 27 oktober en de DFB Pokal ook. Dat is kalender, geen gat.",
}

state["afwikkeling"] = {
    "picks_afgewikkeld": len(SETTLE["picks"]),
    "schaduw_afgewikkeld": len(SETTLE["shadow"]),
    "niet_afgewikkeld": SETTLE["mis"],
    "bevinding":
        "De terugval van twee uur uit §0 (settling.FALLBACK_HOURS) stond op het punt twee "
        "schaduwpicks op een verkeerde stand af te wikkelen. `shadow.py open` zette "
        "Honduras – Suriname en El Salvador – Martinique (CONCACAF Nations League, run C van 25 "
        "sep) op de lijst met de reden 'geen bronstatus; terugval op de klok (2.3u >= 2u)'. Die "
        "twee duels staan echter niet op de Fotmob-daglijst van 25 september maar op die van 26 "
        "september: ze trappen af om 01:00 en 03:00 UTC. Een schaduwrij bewaart geen aftraptijd, "
        "alleen de rundatum, dus DayIndex zocht in de verkeerde daglijst, vond niets en viel terug "
        "op de klok. Bij navraag op de daglijst van 26 sep stond Honduras – Suriname op 2-2 met "
        "finished=False (nog aan het spelen) en was El Salvador – Martinique nog niet begonnen. "
        "Beide zijn daarom pending gelaten, zoals de docstring van settling.py zelf eist: de "
        "terugval bepaalt alleen wat er op de lijst komt, niet dat er een uitslag genoteerd mag "
        "worden. Dit is de structurele versie van de fout die §3 Stage 1 op 24 september voor "
        "fixtures heeft opgelost — een run die in UTC-dagen denkt terwijl de wedstrijd in een "
        "Amerikaanse tijdzone staat. Openstaand punt: geef een schaduwrij (en een pick) het "
        "kickoff-veld mee, of laat DayIndex net als runwindow.days_needed twee daglijsten lezen.",
}

state["duur"] = {
    "gestart": state.get("duur", {}).get("gestart") or "2026-09-26T02:17:44+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})
print("eerstvolgende per competitie:", eerste_fotmob)
