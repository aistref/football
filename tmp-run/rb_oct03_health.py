"""§6b-3 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft.

Schrijfwijze volgens `_doc`: één doorlopende tekst per bron, chronologisch, oudste feit eerst.
Geen runverslagen achter elkaar plakken.
"""
import json

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
DAG = "2026-10-03"


def bij(key, status, tekst, **extra):
    v = S.setdefault(key, {})
    v["status"] = status
    v["last_checked"] = DAG
    v["detail"] = (str(v.get("detail", "")).rstrip() + f"  [Run B] {tekst}").strip()
    v.update(extra)


bij("fotmob", "ok",
    "Run B 3 okt: twee daglijsten (3 okt: 107 competities/434 duels; 4 okt: 88/273), 34 "
    "standenverzoeken voor scripts/idcheck.py (17 competities × twee seizoensnotaties, alle 17 "
    "OK, afsluitcode 0), tien standen voor de vijf spelende competities (vorig en lopend "
    "seizoen) en de wedstrijdcontext van alle 22 duels in het inzetvenster. Alles HTTP 200, geen "
    "storing; Fotmob was opnieuw de enige kansbron. NIEUW GEMETEN: negen van de 31 Engelse duels "
    "op de daglijst dragen status.cancelled (zes in League One, drie in League Two) en worden "
    "door runwindow.matches_for_run correct uitgefilterd — de velden kloppen dus, maar een run "
    "die ze niet noemt laat League One lezen als een competitie met drie zaterdagduels.")

bij("the_odds_api", "ok",
    "Run B 3 okt: api_check.py geeft 49 actieve voetbalcompetities en 19.949 van de 20.000 "
    "credits over (51 deze maand). Sleutel niet afgewezen. 20 credits uitgegeven: vier "
    "bulk-aanroepen (h2h + spreads + totals, 3 credits elk) voor soccer_spain_segunda_division, "
    "soccer_england_league1, soccer_england_league2 en soccer_brazil_campeonato, plus acht "
    "per-duel BTTS-verzoeken (1 credit elk); quota daarna 19.929. GEMETEN EN HERSTELD: de "
    "Braziliaanse namen in de h2h- en spreads-respons ('Atletico Mineiro', 'Bragantino-SP') "
    "koppelden niet aan de Fotmob-namen ('Atlético-MG', 'RB Bragantino'). find_event vond de "
    "wedstrijd nog wel, maar side_of gaf None, zodat de thuis- en uitkant van de 1X2 en álle "
    "handicaplijnen stil wegvielen — 3 doorgerekende selecties in plaats van 13. Vier aliassen "
    "toegevoegd in tmp-run/ra_names.py; na de herhaling van de analyse waren alle zes markten "
    "voor dat duel werkelijk te koop.")

bij("oddsapi", "ok",
    "Sleutel geaccepteerd (api_check.py 3 okt 2026). Gebruikt voor Segunda División, English "
    "League One, English League Two en Série A (BRA): 20 credits.")

bij("betexplorer", "ok",
    "Run B 3 okt: vijf fixturepagina's opgehaald (spain/laliga2 10 rijen, "
    "netherlands/eerste-divisie 7, england/league-one 15, england/league-two 8, "
    "brazil/serie-a-betano 11), alle HTTP 200. Voor de Keuken Kampioen Divisie opnieuw de ENIGE "
    "1X2-bron — die competitie heeft geen sportkey bij The Odds API — en het marktgemiddelde "
    "komt daar over 3 boeken; dat is de reden dat de zes Nederlandse duels elk maar drie "
    "selecties kregen in plaats van dertien.")

bij("understat", "ok",
    "Run B 3 okt: niet aangeroepen — geen van de vijf spelende competities (Segunda División, "
    "Keuken Kampioen Divisie, English League One, English League Two, Série A BRA) zit in de "
    "vijf die Understat dekt (§4). Status ongewijzigd overgenomen. Geen storing, maar wél de "
    "reden dat deze run geen tweede xG-model had.")

bij("api_football", "missing_key",
    "Met opzet afwezig sinds het besluit van de gebruiker op 27 sep 2026 (§3). Geen gat, geen "
    "actiepunt, niet in de notificatie. api_check.py meldt het onveranderd als feit en dringt "
    "niet aan.")

d["last_run"] = f"{DAG} run-b"
d["updated"] = DAG
d["last_run_bevinding"] = (
    "Run B 3 okt 2026 — vijf regels op rangorde (§5b), waarvan één boven de lat, en drie "
    "bevindingen die alle drie van de soort 'faalt zonder foutmelding' zijn. "
    "(1) HET KALIBRATIELOGBOEK WIKKELDE AMERIKAANSE DUELS NOOIT AF. `calibration.settle` zocht "
    "de uitslag op de daglijst van de RUNDAG, terwijl een duel in een Amerikaanse tijdzone sinds "
    "runwindow.py (24 sep) op de daglijst van de dag ERNA staat. Gevolg: 195 waarnemingen van "
    "vóór vandaag stonden nog op `won = None`, waaronder élke CONCACAF-rij van Run C en de "
    "MLS-rijen van Run B — een systematisch lek in precies de steekproef waarop §1g de herijking "
    "fit. Hersteld in scripts/calibration.py (de dag zelf, dan de dag erna, dan de dag ervoor, "
    "zoals settling._days_to_try); 63 waarnemingen alsnog afgewikkeld. "
    "(2) ER BLIJVEN 132 WAARNEMINGEN OPEN MET EEN ANDERE OORZAAK. Dat zijn Europese duels waar de "
    "korte weergavenaam van de pick ('Sheff Utd', 'Nottm Forest', “M'gladbach”) niet koppelt aan "
    "de volledige naam in de Fotmob-daglijst. `settling.DayIndex.lookup` doet een eigen "
    "zes-tekens-voorvoegselvergelijking en kent de aliastabel van tmp-run/ra_names.py niet. "
    "Niet opgelost deze run: dat vraagt om die tabel naar scripts/ te verhuizen. "
    "(3) EEN GEPUBLICEERDE WEDSTRIJD KON ÓÓK EEN SCHADUWRIJ KRIJGEN. Sinds §5b publiceert de "
    "rangorde wedstrijden waarin geen selectie de drempel haalde; de `near_miss` van zo'n "
    "wedstrijd bleef dan staan als hij een ándere selectie beschreef dan de gepubliceerde. "
    "Vandaag raakte dat Exeter City – Rotherham United (gepubliceerd: Draw No Bet; near_miss: de "
    "1X2). De dedup gaat nu op de WEDSTRIJD in plaats van op de selectie; poort8- en "
    "herijkingsrijen blijven ongemoeid, want §1e eist die juist wél.")
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", d["last_run"])
