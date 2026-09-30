"""§6b-3 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft.

Schrijfwijze volgens `_doc`: één doorlopende tekst per bron, chronologisch, oudste feit eerst.
Geen runverslagen achter elkaar plakken.
"""
import json
from datetime import date

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
DAG = "2026-09-30"

def bij(key, status, tekst, **extra):
    v = S.setdefault(key, {})
    v["status"] = status
    v["last_checked"] = DAG
    v["detail"] = (str(v.get("detail", "")).rstrip() + f"  [Run B] {tekst}").strip()
    v.update(extra)

bij("fotmob", "ok",
    "Run B 30 sep: twee daglijsten (30 sep: 36 competities/84 duels; 1 okt: 31/60), 34 "
    "standenverzoeken voor scripts/idcheck.py (17 competities × max twee seizoensnotaties, alle "
    "17 OK), twee standen voor MLS (2025 en 2026, beide met xG), de wedstrijdcontext en het "
    "wedstrijddossier van Red Bull New York – St. Louis City. Alles HTTP 200, geen enkele "
    "storing. Fotmob was vandaag de ENIGE kansbron: Understat dekt MLS niet, dus de redundantie "
    "van 31 aug bestaat op deze runlijst niet. De uitzondering van §3 punt 3 is niet aan de orde.")

bij("the_odds_api", "ok",
    "Run B 30 sep: api_check.py geeft 46 actieve voetbalcompetities en 18.610 van de 20.000 "
    "credits over (1.390 deze maand). Sleutel niet afgewezen. 4 credits uitgegeven: één "
    "bulk-aanroep voor soccer_usa_mls (h2h + spreads + totals, 3 credits) en één per-duel "
    "BTTS-verzoek (1 credit); quota daarna 18.606. De h2h-respons gaf 22 boeken met een "
    "volledige 1X2 en marges van 1,01% (Betfair, Matchbook) tot 12,45% (Unibet FR). De "
    "spreads-respons had GEEN 0.0-lijn, dus Draw No Bet was niet te koop — genoteerd als reden, "
    "niet als gat.")

bij("oddsapi", "ok",
    "Sleutel geaccepteerd (api_check.py 30 sep 2026). Gebruikt voor MLS: 4 credits.")

bij("betexplorer", "ok",
    "Run B 30 sep: één fixturepagina opgehaald (usa/mls), 18 rijen, HTTP 200 — geen daarvan met "
    "is_today, want de aftrap valt op 1 oktober in NL-tijd. Het marktgemiddelde over 10 boeken "
    "(3.37 / 4.07 / 1.90) is gebruikt voor het kalibratieblok (§6e) en voor het marktoordeel over "
    "wie de mindere ploeg is, niet als prijs om op te spelen (§1a).")

bij("understat", "ok",
    "Run B 30 sep: niet aangeroepen — de enige spelende competitie is MLS en Understat dekt alleen "
    "PL, La Liga, Bundesliga, Serie A en Ligue 1 (§4). Status ongewijzigd overgenomen van de "
    "meting van Run A van vandaag. Dit is geen storing maar het is wél de reden dat deze run geen "
    "tweede xG-model had.")

bij("api_football", "missing_key",
    "Met opzet afwezig sinds het besluit van de gebruiker op 27 sep 2026 (§3). Geen gat, geen "
    "actiepunt, niet in de notificatie. api_check.py meldt het onveranderd als feit en dringt "
    "niet aan.")

d["last_run"] = f"{DAG} run-b"
d["updated"] = DAG
d["last_run_bevinding"] = (
    "Run B 30 sep 2026 — twee bevindingen, beide van de soort 'faalt zonder foutmelding'. "
    "(1) NAAMKOPPELING: Fotmob schrijft 'Red Bull New York', The Odds API 'New York Red Bulls'. "
    "Na token-normalisatie blijft {red,bull,new,york} tegen {new,york,red,bulls} over — geen "
    "deelverzameling, want 'bull' is niet 'bulls'. side_of gaf None en de analyse deed continue, "
    "dus de HELE THUISKANT viel stil uit de analyse: 11 selecties in plaats van 17, hoogste edge "
    "-0.30 pp in plaats van +10.40 pp, en de gerapporteerde reden voor nul bets zou 'edge onder "
    "drempel' zijn geweest in plaats van poort 7. Gerepareerd in tmp-run/ra_names.ALIASES (beide "
    "richtingen). Openstaand: er is nog geen controle die zegt dat er minder uitkomsten zijn "
    "gekoppeld dan de respons er had — dat is het echte antwoord en het is de vierde naamval in "
    "die lijst. "
    "(2) idcheck.py viel om op ModuleNotFoundError bij de aanroep die run-b.md voorschrijft "
    "(`python3 scripts/idcheck.py`): als script staat scripts/ op sys.path en niet de repowortel. "
    "Erger dan hinderlijk, want afsluitcode 1 betekent volgens run-b.md 'een competitie is stil "
    "uit de runlijst verdwenen' — een kapotte controle zag er dus precies uit als de vondst "
    "waarvoor hij op 29 sep is gebouwd. Gerepareerd met sys.path.insert(0, ROOT).")
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", d["last_run"])
