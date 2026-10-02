"""Run A, 2 okt 2026 — Stage -1/6: het voortgangs- en runstate-bestand schrijven.

Nul wedstrijden in de runlijst (interlandvenster), dus elke competitie krijgt GEEN WEDSTRIJD en
er is niets in te kopen. De structuur volgt die van 1 oktober, zodat report.py en de
collect-scripts hetzelfde vinden als elke andere dag.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, save
from scripts.ranking import max_deep_analyses
from scripts.recalibrate import load_fit
from scripts import sides, model, oddsapi, recalibrate

DAY = date(2026, 10, 2)
RUN = "a"

st3 = json.load(open("tmp-run/ra_oct02_stage3.json"))
bev = json.load(open("tmp-run/ra_oct02_bevestiging.json"))
gap = json.load(open("tmp-run/ra_oct02_gap.json"))

state = load_or_start(RUN, DAY)
state.setdefault("duur", {})
state["duur"].setdefault("gestart", "2026-10-02T02:18:00+00:00")

fit = load_fit()
state["parameters"] = {
    "MAX_DEEP_ANALYSES": max_deep_analyses(DAY),
    "MAX_SHORTLIST": 5,
    "EDGE_THRESHOLD_FULL": 8.0,
    "EDGE_THRESHOLD_LIGHT": 16.0,
    "MAX_LIGHT_IN_SHORTLIST": 2,
    "MIN_ODDS": 1.30,
    "MAX_ODDS": 6.00,
    "SHRINK": model.DEFAULT_SHRINK,
    "XG_WEIGHT": model.XG_WEIGHT,
    "CREDIBILITY_K": model.CREDIBILITY_K,
    "EXCHANGE_COMMISSION": oddsapi.EXCHANGE_COMMISSION,
    "MIN_OBSERVATIONS": recalibrate.MIN_OBSERVATIONS,
    "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
    "dagsoort": "vrijdag — dus 55/5 en niet 40/3",
    "afgekapt": 0,
    "afkapping": {
        "cap": max_deep_analyses(DAY),
        "afgekapt": 0,
        "laagste_die_het_haalde": None,
        "hoogste_die_afviel": None,
        "lijst": [],
        "reden": "0 wedstrijden in de runlijst, dus de cap bond nergens",
    },
    "HERIJKING": (
        f"niet toegepast — er is geen wedstrijd doorgerekend. De fit zelf is wel gelezen: "
        f"a={fit.a:.3f}, b={fit.b:.3f} over {fit.n} afgerekende gevallen, "
        f"fitted_through {fit.fitted_through}."
    ),
    "POORT8": {
        "lapsed_from": str(sides.LAPSED_FROM),
        "lapsed_until": str(sides.LAPSED_UNTIL),
        "underdog_floor": sides.UNDERDOG_FLOOR,
        "actief_vandaag": True,
        "toelichting": (
            "Poort 8 bindt sinds 1 oktober 2026 weer, in de lichte vorm (UNDERDOG_FLOOR = 0.35). "
            "Er is vandaag geen selectie om hem op toe te passen — nul wedstrijden in de runlijst. "
            "De eerste Run A waarin hij werkelijk iets doet is die van 9 oktober; leg daar per "
            "selectie sides.check(side, odds_1x2, today=DAY) vast en boek op beide schalen "
            "(underdog en underdog_ruw)."
        ),
    },
}

state["stage_min2"] = {
    "ondiepe_kloon_bij_start": True,
    "takken_nagelopen": 46,
    "methode": (
        "scripts/branchaudit.py --ref HEAD over alle 46 origin-takken, per record op de inhoud en "
        "niet op de commitgraaf: picks.jsonl op id, shadow.jsonl op id, context-log.jsonl op id, "
        "calibration.jsonl op (datum, run, wedstrijd, markt, methode), source-health.json en "
        "coverage.json op bladpaden."
    ),
    "vals_alarm_op_de_graaf": (
        "Op de graaf leken 34 van de 46 takken 2 tot 359 eigen commits te hebben, en voor 33 ervan "
        "geeft git merge-base met main zelfs niets terug. Dat is het valse alarm dat §3 Stage -2 "
        "beschrijft, hier in zijn sterkste vorm: de huidige main-lijn heeft een eigen wortel van "
        "23 september 2026 (c6ddc35), dus elke commit van vóór die knip telt als 'nog niet hier'. "
        "De vergelijking per record geeft nul."
    ),
    "gevonden": {
        "data/picks.jsonl": "volledig — 331 id's op HEAD, geen tak heeft er een die hier mist",
        "data/shadow.jsonl": "volledig — 777 records",
        "data/context-log.jsonl": "volledig — 839 records",
        "data/calibration.jsonl": "volledig — 3600 records",
        "data/source-health.json": (
            "volledig — 106 bladpaden; alleen sources.oddspapi staat op oudere takken en niet op "
            "HEAD, en dat is het bekende besluit van 30 aug 2026 (commit f342894), geen verlies"
        ),
        "data/coverage.json": "volledig — 285 bladpaden",
    },
    "verenigd": [],
    "openstaande_picks_van_een_andere_tak": (
        "Geen. De drie openstaande picks die Stage 0 vond (Wales – Norway, Azerbaijan – "
        "Liechtenstein en Malta – Gibraltar, alle drie van Run C op 1 oktober) stonden gewoon op "
        "main en zijn deze run afgewikkeld."
    ),
    "branch": (
        "main — de scheduler-prompt geeft expliciet toestemming (§6a). De sessiebranch "
        "claude/stoic-davinci-wxaq4n stond al op origin/main; er wordt met "
        "git push origin HEAD:main gepusht. Niets te melden bovenaan het rapport."
    ),
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 2 okt 2026, 08:00 3 okt 2026)",
    "include_carry_over": False,
    "reden_carry_over": (
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van 25 september. Hem "
        "aanzetten zou de band [00:00, 08:00) NL in twee runrapporten zetten."
    ),
    "daglijsten": {"2026-10-02": 55, "2026-10-03": 107},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1": (
        "Fotmob-daglijsten van 2 en 3 oktober 2026 (55 respectievelijk 107 competities), per "
        "competitie uit de runlijst getoetst met find_league op naam, ccode en aliassen — 21 van de "
        "21 leeg, op beide dagen. Dat het geen naamkwestie is, is aan de daglijsten zelf te zien: "
        "wat er staat is interlandvoetbal (UEFA Nations League A t/m D, CONCACAF Nations League, "
        "EURO U21-kwalificatie, FIFA ASEAN Cup, Gulf Cup, Asian Games, friendlies) plus lagere "
        "divisies. Dezelfde bijna-treffer als op 29 september en 1 oktober: op de daglijst van "
        "2 oktober staat de Deense 2. Division (id 239) wél en Superligaen (id 46) niet, en op "
        "3 oktober staan ENG League One (108) en League Two (109), SCO Championship (123), "
        "League One (124) en League Two (125), ESP LaLiga2 (140) en NED Eerste Divisie (111) — "
        "telkens het niveau ónder de runlijstcompetitie. Bij een afwijkende naam zou juist de "
        "hoogste divisie er staan; hier staan alleen de lagere niveaus op de lijst, en dat is het "
        "omgekeerde van wat een naamfout zou geven."
    ),
    "methode_2": (
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 komende "
        "duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Championship 12, Eredivisie 18, "
        "Primeira Liga 9, Pro League 9, Süper Lig 9, Scottish Premiership 12, Danish Superliga 6, "
        "Ekstraklasa 10, UCL 18, UEL 18, UECL 18, League Cup 8 — nul daarvan op vandaag, en de "
        "eerstvolgende staat op 9, 10, 11, 13, 15 of 27 oktober. Coppa Italia gaf HTTP 200 met een "
        "lege tabel. Ekstraklasa gaf deze run 10 rijen waar de pagina op 1 oktober nog leeg was."
    ),
    "methode_3_de_drie_bekers_zonder_url": (
        "FA Cup, KNVB Beker en DFB Pokal hebben geen URL in de hoofdlijst en zijn apart opgehaald. "
        "DFB Pokal 16 komende duels, eerste op 27 oktober. KNVB Beker geeft bij BetExplorer een "
        "lege tabel, dus daar blijft Fotmob de enige bron — een bronbeperking, geen bevestiging. "
        "FA Cup gaf 39 komende duels met de eerste al op 3 oktober; zie het blok fa_cup_gat "
        "hieronder."
    ),
    "methode_4_tegenproef": (
        "De Fotmob-daglijsten van 2 t/m 15 oktober zijn met dezelfde toets nagelopen. 2 t/m "
        "8 oktober geven alle zeven nul runlijstwedstrijden terwijl die lijsten wél gevuld zijn "
        "(55, 107, 88, 30, 58, 22 en 25 competities). Vanaf 9 oktober springt het terug: 12 "
        "wedstrijden in 10 competities op 9 okt, 56 in 12 op 10 okt, 41 in 13 op 11 okt, 9 in 7 op "
        "12 okt, dan de Champions League op 13 en 14 okt en Europa/Conference League op 15 okt. De "
        "daglijsten zijn dus gezond; het zijn werkelijk alleen de topdivisies die stilliggen."
    ),
    "conclusie": (
        "Nul wedstrijden in de runlijst is de werkelijkheid en geen storing. Dit is het "
        "FIFA-interlandvenster; de eerste Run A-speeldag is vrijdag 9 oktober 2026, en dat getal "
        "komt uit twee bronnen (Fotmob-daglijst en BetExplorer-fixturepagina's) in plaats van uit "
        "één."
    ),
}

state["fa_cup_gat"] = {
    "wat": (
        "BetExplorer heeft 39 FA Cup-duels met aftrap op 3 oktober 2026 (12:30 en 15:00 UK); de "
        "Fotmob-daglijst van 3 oktober noemt géén FA Cup. Het zijn kwalificatierondeduels tussen "
        "niet-ligaclubs: Brentwood – Dag & Red, AFC Rushden & Diamonds – Braintree, Barton Town – "
        "Chorley, Bedford – Wingate & Finchley, Brackley Town – Chelmsford, Bury – Bromsgrove, "
        "Bury Town – Spalding United, Buxton – South Shields, Cambridge City – Alvechurch, "
        "Chesham – Real Bedford, en 29 andere."
    ),
    "gevolg_voor_vandaag": (
        "Geen. 12:30 en 15:00 op 3 oktober liggen ná 08:00 NL op 3 oktober en vallen dus buiten "
        "het inzetvenster van deze run (§3 Stage 1). Ze horen bij de run van 3 oktober."
    ),
    "gevolg_voor_morgen": (
        "Wél. Een run die alleen de Fotmob-daglijst leest, zet de FA Cup op 3 oktober op GEEN "
        "WEDSTRIJD terwijl er 39 duels liggen. De 14-daagse tegenproef vond tot en met 15 oktober "
        "geen enkele FA Cup-dag bij Fotmob, dus dit is geen eenmalige hapering in de daglijst maar "
        "het patroon dat Fotmob de kwalificatierondes niet in zijn daglijsten zet. Verwacht "
        "overigens BUITEN DATADEKKING voor deze duels — het is precies de categorie waarvoor "
        "prompts/run-a.md bij League Cup ronde 1–2 al waarschuwt dat er vrijwel geen publieke xG "
        "of modelkans van bestaat — maar dat is een uitkomst van de datadekkingspoort en hoort niet "
        "stil langs de competitiepoort te verdwijnen."
    ),
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": (
        "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. The "
        "Odds API staat op 19.979 van de 20.000 over (api_check.py deze run: 'Quota: 19979 over, "
        "21 gebruikt deze maand')."
    ),
    "marktbalans": (
        "niet van toepassing — er is niets ingekocht. §1a eist minstens één doelpunten- en één "
        "uitkomstmarkt zodra er wél wordt ingekocht."
    ),
}

state["competitions"] = {
    name: {"status": "GEEN WEDSTRIJD", "matches": [], "fotmob_id": st3["ids"].get(name)}
    for name in st3["fixtures"]
}

state["afwikkeling"] = {
    "picks_afgewikkeld": 3,
    "schaduw_afgewikkeld": 13,
    "niet_afgewikkeld": [
        "shadow-2026-10-01-b-seattle-sounders-fc---sporting-kansas-city — Fotmob meldde het duel "
        "bij shadow.py open niet als afgelopen, dus hij blijft open (§0: de status van de bron "
        "beslist, de klok alleen als terugval)."
    ],
    "picks_uitslag": {"gewonnen": 2, "verloren": 1, "void": 0},
    "schaduw_uitslag": {"gewonnen": 3, "verloren": 8, "void": 2},
    "negentig_minuten": (
        "Alle zestien rijen komen uit interlandvoetbal in groeps- of kwalificatievorm dat Fotmob "
        "als afgelopen meldde zonder verlenging of strafschoppen, dus de eindstand ís hier de stand "
        "na 90 minuten (§6d). Nagekeken op de knock-outval: de UEFA Nations League-duels (Wales – "
        "Norway, Azerbaijan – Liechtenstein, Malta – Gibraltar, Germany – Serbia, Greece – "
        "Netherlands, Denmark – Portugal, Ireland – Austria, Israel – Kosovo) zijn groepsduels; "
        "Maldives – Lebanon, Uzbekistan – Syria, Dominica – Guyana, Cayman Islands – Puerto Rico "
        "en Guinea – Kenya zijn kwalificatie- of groepsduels. Geen enkele rij komt uit een "
        "tweeluik of play-offduel waar 90 minuten en eindstand kunnen verschillen."
    ),
    "void_toelichting": (
        "Twee void: Draw No Bet +0 — Ireland bij Ireland – Austria 2-2 en Draw No Bet +0 — Israel "
        "bij Israel – Kosovo 0-0. Bij een gelijkspel komt de inzet op een DNB terug, dus dat is "
        "geen verlies en geen winst."
    ),
    "bevinding": (
        "Zestien rijen afgewikkeld: 3 echte picks (2 gewonnen, 1 verloren) en 13 schaduwrijen "
        "(3 gewonnen, 8 verloren, 2 void), alle zestien van Run C van 1 oktober. Dat is geen "
        "bevinding over de routine maar één dag (§6d), en het is geen reeks van 5+ verliezende "
        "picks in de zin van §7 — het is één verliezende pick; de acht andere verliezers zijn "
        "tegengehouden kandidaten en die horen niet bij de picks opgeteld te worden."
    ),
    "poort8_noot": (
        "Vier van de dertien schaduwrijen zijn poort-8-rijen van Run C van 1 oktober — de eerste "
        "dag waarop de poort weer bond. Germany – Serbia (AH +2.5 Serbia) en de twee "
        "poort8_geblokkeerd-rijen Azerbaijan – Liechtenstein (AH +2.5 Liechtenstein) en Malta – "
        "Gibraltar (AH +1.5 Gibraltar) zijn gewonnen; Denmark – Portugal (DC 1X), Ireland – "
        "Austria (1 @ 3.65), Israel – Kosovo (DNB Israel, void) en Guinea – Kenya (2 @ 5.68) niet. "
        "Dat is één dag en §6d eist ~30 gevallen voordat de reeks gelezen mag worden — niet lezen, "
        "wel boeken."
    ),
}

save(state)
print("geschreven:", f"data/run-state/{DAY}-run-{RUN}.json")
print("competities:", len(state["competitions"]),
      "— alle op", {v["status"] for v in state["competitions"].values()})
