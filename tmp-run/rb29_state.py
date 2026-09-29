"""Run B 29 sep 2026 — data/run-state/2026-09-29-run-b.json schrijven.

Nul wedstrijden in het inzetvenster, dus alle zeventien competities krijgen `GEEN WEDSTRIJD`.
§5 eist een regel per competitie uit de opdracht, niet alleen voor de competities die speelden;
`report.py` rendert de dekkingstabel hieruit.
"""
import json

DAY = "2026-09-29"
nxt = json.load(open("tmp-run/rb29_next.json"))

RUNLIST = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
 "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)", "Romanian SuperLiga (ROU)",
 "Segunda División (ESP)", "Serie B (ITA)", "2. Bundesliga (GER)", "Swiss Super League (SUI)",
 "Austrian Bundesliga (AUT)", "Keuken Kampioen Divisie (NED)", "English League One (ENG)",
 "English League Two (ENG)", "MLS (USA)", "Série A (BRA)"]
IDS = {"Czech First League (CZE)": 122, "Greek Super League (GRE)": 135, "Eliteserien (NOR)": 59,
 "Allsvenskan (SWE)": 67, "Croatian HNL (CRO)": 252, "Hungarian NB I (HUN)": 212,
 "Romanian SuperLiga (ROU)": 189, "Segunda División (ESP)": 140, "Serie B (ITA)": 86,
 "2. Bundesliga (GER)": 146, "Swiss Super League (SUI)": 69, "Austrian Bundesliga (AUT)": 38,
 "Keuken Kampioen Divisie (NED)": 111, "English League One (ENG)": 108,
 "English League Two (ENG)": 109, "MLS (USA)": 130, "Série A (BRA)": 268}

comps = {}
for name in RUNLIST:
    v = nxt.get(name)
    reden = (f"geen wedstrijd in het inzetvenster [08:00 NL 29 sep, 08:00 NL 30 sep) — "
             f"Fotmob-daglijsten van 29 sep (53 competities, 122 duels) en 30 sep (35 competities, "
             f"83 duels) op primaryId {IDS[name]} nagekeken via runwindow.matches_for_run, beide leeg")
    if v:
        reden += (f"; eerstvolgende duel {v['datum']} — {v['eerste']} {v['aftrap_nl']} NL "
                  f"({v['aantal']} duels op die daglijst)")
    comps[name] = {"status": "GEEN WEDSTRIJD", "matches": [], "reden": reden,
                   "eerstvolgende": v, "primaryId": IDS[name]}

state = {
 "run": "B", "date": DAY, "resumed_count": 0,
 "competitions": {k: comps[k] for k in RUNLIST},
 "completed": False,
 "parameters": {
   "MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3,
   "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
   "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
   "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
   "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping en anders als label",
   "afkapping": {"cap": 40, "afgekapt": 0, "laagste_die_het_haalde": None,
                 "hoogste_die_afviel": None, "lijst": [],
                 "reden": "0 wedstrijden in de runlijst, dus de cap bond nergens"},
   "HERIJKING": ("niet toegepast — er is geen wedstrijd doorgerekend. De fit is wel gelezen: "
                 "a=1.030, b=0.019 op 2346 afgerekende gevallen t/m 18 sep 2026."),
   "POORT8": {"lapses_on": "2026-09-25", "actief_vandaag": False,
              "toelichting": ("Vervallen sinds 25 sep 2026 (sides.LAPSES_ON): sides.check() laat "
                              "elke kant door en zet alleen nog would_block. Opnieuw geen selectie "
                              "om hem op toe te passen. De eerste Run B waarin het vervallen iets "
                              "kan doen is die van 2 oktober (Segunda División, Keuken Kampioen "
                              "Divisie en Série A spelen dan); leg daar poort8_vervallen per "
                              "selectie vast en zet poort8_zou_hebben_geblokkeerd in de pick zodra "
                              "zo'n selectie een gepubliceerde bet wordt (§1e).")},
 },
 "stage1": {
   "module": "scripts/runwindow.py",
   "venster_nl": "[08:00 29 sep 2026, 08:00 30 sep 2026)",
   "venster_utc": "[2026-09-29T06:00Z, 2026-09-30T06:00Z)",
   "include_carry_over": False,
   "reden_carry_over": ("Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van "
                        "25 september. Aanzetten zou de band [00:00, 08:00) NL in twee "
                        "runrapporten zetten."),
   "daglijsten": {"2026-09-29": 53, "2026-09-30": 35},
   "gevonden_in_venster": 0, "source_day_plus_1": 0, "onspeelbaar": 0,
   "venstergrens": ("Er viel vandaag één duel net búiten het venster en dat is precies het geval "
                    "waarvoor runwindow.py bestaat: MLS, Red Bull New York – St. Louis City, "
                    "aftrap 2026-09-30T23:30Z = 01:30 NL op 1 oktober. Dat hoort bij de run van "
                    "30 september, niet bij deze en niet bij die van 1 oktober. Onder de oude "
                    "UTC-dagregel was het aan de run van 30 september toegewezen en dan was het "
                    "bij aankomst al gespeeld. Run B van 30 september moet dit duel dus hebben."),
 },
 "credits": {"the_odds_api": {
   "plafond_deze_run": 0, "uitgegeven": 0, "over": 18627, "markten_gekocht": {},
   "reden": ("nul competities in de runlijst met een wedstrijd, dus geen enkele competitie om "
             "prijzen voor te kopen. api_check.py: 18.627 van de 20.000 credits over."),
   "marktbalans_inkoop": ("niet van toepassing — er is niets ingekocht, dus er kan ook geen scheve "
                          "inkoop zijn. §1a eist minstens één competitie met een doelpuntenmarkt "
                          "én één met een uitkomstmarkt zodra er wél wordt ingekocht.")}},
 "bevestiging": {
   "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de id of naam niet?",
   "methode_1": ("Fotmob-daglijsten van 29 en 30 sep 2026 (53 respectievelijk 35 competities, "
                 "122 en 83 duels), per competitie getoetst op primaryId via "
                 "runwindow.matches_for_run. 17 van de 17 leeg."),
   "methode_2": ("Tweede methode, en met opzet een ándere sleutel: dezelfde twee daglijsten "
                 "gescand op NAAM en ccode in plaats van op id, over alle competities in de "
                 "zestien runlijstlanden. Dat leverde 43 duels in het venster op — en geen enkele "
                 "in een competitie van de runlijst: National League (10), Isthmian/Northern/"
                 "Southern Premier (19), National League North/South (2), Regionalliga Bayern (1), "
                 "Noorse 3. Divisjon (1), Braziliaanse Série B (1, id 8814 — niet onze Série A) en "
                 "de rest. Dat de naamroute en de idroute op dezelfde nul uitkomen is de "
                 "bevestiging; dat de naamroute 43 duels vindt bewijst dat de daglijsten gevuld "
                 "waren en de nul dus geen leeg antwoord is."),
   "methode_3": ("Achttien daglijsten vooruit gescand (rb29_next.py): alle zeventien competities "
                 "hervatten tussen 30 september en 10 oktober. Dat is het interlandvenster van "
                 "eind september/begin oktober en dus een kalenderverklaring, geen storing."),
   "methode_4": ("scripts/idcheck.py — nieuw vandaag: elk fotmob_id uit coverage.json getoetst op "
                 "een bruikbare stand, juist óók voor de competities die vandaag stil zijn. "
                 "17 van de 17 in orde ná de reparatie hieronder; vóór de reparatie 16 van de 17."),
   "uitkomst": ("nul duels in het inzetvenster, in nul competities. Alle zeventien GEEN WEDSTRIJD, "
                "met twee onafhankelijke routes (id en naam) plus een kalenderverklaring."),
 },
 "bevinding_serie_b": {
   "wat": ("Serie B (ITA) stond in de runlijst op fotmob primaryId 56 in plaats van 86. Bij Fotmob "
           "is 56 'Serie B Qualification' en dat id heeft helemaal geen stand "
           "(fetch_league_stats geeft FotmobError op beide seizoensnotaties); 86 is de echte Serie "
           "B, met xG voor alle twintig ploegen."),
   "sinds": ("De Run B van 17 september 2026 (tmp-run/rb17_stage3.py is de eerste met 56; rb16 en "
             "alle eerdere stonden op 86). coverage.json noteerde het juiste id al op 23 augustus, "
             "maar als prozaregel in `notes` en niet machineleesbaar."),
   "waarom_stil": ("Stage 1 matcht op id en nooit op naam. Een fout id geeft geen foutmelding maar "
                   "nul wedstrijden, en nul wedstrijden is GEEN WEDSTRIJD — de normale uitkomst op "
                   "deze runlijst. Stage 3 vangt het niet, want die haalt de stand alleen op voor "
                   "competities die wél wedstrijden in het venster hebben; bij een fout id zijn "
                   "die er niet, dus werd de stand nooit opgevraagd."),
   "kosten": {"duels": 10, "18 sep": 1, "19 sep": 5, "20 sep": 4,
              "toelichting": ("Alle tien als 'geen wedstrijd' gerapporteerd. Van 21 t/m 29 "
                              "september viel er niets te missen: interlandvenster. Serie B "
                              "speelt weer op 9 oktober (Avellino – Sampdoria, 20:30 NL) — zonder "
                              "deze controle was dát de eerste run die het had gemerkt.")},
   "gerepareerd": ["data/coverage.json: fotmob_id per competitie, machineleesbaar, voor alle 17",
                   "prompts/run-b.md: 56 -> 86, plus de regel dat de id's uit coverage.json komen",
                   "scripts/idcheck.py: nieuw, toetst elk id elke run, ook bij nul wedstrijden"],
   "hoe_gevonden": ("Het runrapport van Run B van 28 september noemde 'Serie B (ITA) heeft binnen "
                    "achttien dagen geen duel' als de langste stilte van de lijst en als het enige "
                    "punt dat navraag verdiende. Die navraag is vandaag gedaan en het was geen "
                    "kalenderstilte maar een fout id."),
 },
 "stage_min2": {
   "takken_nagelopen": 43, "ondiepe_kloon": True, "op_main": True,
   "bevinding": ("De container leverde de repo opnieuw als ondiepe kloon (77 commits lokaal). Vóór "
                 "`git fetch --unshallow` telden 31 van de 43 takken 'eigen' commits — 1 tot 315 "
                 "stuks, en `git merge-base` gaf niets terug. Ná het unshallowen staan alle 43 "
                 "takken op 0 eigen commits. Exact het valse alarm dat Stage -2 beschrijft. "
                 "Daarna, zoals de tabel sinds 27 september eist, per regel op inhoud vergeleken "
                 "voor alle vijf de logboeken: picks.jsonl (323 id's), shadow.jsonl, "
                 "calibration.jsonl, context-log.jsonl en de json-logboeken — nul rijen op een "
                 "andere tak die main niet heeft. De enige afwijkingen in source-health.json en "
                 "coverage.json zijn het `last_run`-stempel van oudere runs en de OddsPapi-bron "
                 "die op main bewust is verwijderd (commit f342894). Er viel niets te mergen."),
 },
 "afwikkeling": {
   "picks": "ledger.py open: geen picks klaar om af te wikkelen (alle 323 al afgewikkeld).",
   "shadow": ("shadow.py open: één rij wacht — shadow-2026-09-28-c-guatemala---el-salvador. De "
              "bron meldt hem 3,1 uur na aftrap nog niet als afgelopen, en dat is nagetrokken in "
              "plaats van aangenomen: Fotmob geeft ongoing=true, finished=false, 47' bij 3-0 "
              "(aftrap 2026-09-29T02:00Z). De statusregel van §0 doet dus precies wat ze moet doen "
              "en er is geen afwikkelfout. Het is een pick van Run C; die wikkelt hem vandaag af."),
   "openstaand_van_andere_tak": ("geen — Stage -2 vond nul rijen op een andere tak, dus er staat "
                                 "geen pick open van een run die daar nooit is afgewikkeld."),
 },
 "dagrapport": None,
}
json.dump(state, open(f"data/run-state/{DAY}-run-b.json", "w"), ensure_ascii=False, indent=1)
print("geschreven:", f"data/run-state/{DAY}-run-b.json")
print("statussen:", sorted({v["status"] for v in state["competitions"].values()}))
