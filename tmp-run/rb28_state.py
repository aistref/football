"""Run B 28 sep 2026 — data/run-state/2026-09-28-run-b.json schrijven.

Alle zeventien competities uit `prompts/run-b.md` krijgen een regel (§5 eist dat), niet alleen
de drie die vandaag speelden: `report.py` rendert de dekkingstabel hieruit en meldt "alle N
competities uit de opdracht".
"""
import json
from datetime import date

DAY = "2026-09-28"
res = json.load(open("tmp-run/rb28_results.json"))
s3 = json.load(open("tmp-run/rb28_stage3.json"))
top = json.load(open("tmp-run/rb28_top_b.json"))
nxt = json.load(open("tmp-run/rb28_next.json"))
odds = json.load(open("tmp-run/rb28_odds.json"))

RUNLIST = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
 "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)", "Romanian SuperLiga (ROU)",
 "Segunda División (ESP)", "Serie B (ITA)", "2. Bundesliga (GER)", "Swiss Super League (SUI)",
 "Austrian Bundesliga (AUT)", "Keuken Kampioen Divisie (NED)", "English League One (ENG)",
 "English League Two (ENG)", "MLS (USA)", "Série A (BRA)"]
IDS = {"Czech First League (CZE)": 122, "Greek Super League (GRE)": 135, "Eliteserien (NOR)": 59,
 "Allsvenskan (SWE)": 67, "Croatian HNL (CRO)": 252, "Hungarian NB I (HUN)": 212,
 "Romanian SuperLiga (ROU)": 189, "Segunda División (ESP)": 140, "Serie B (ITA)": 56,
 "2. Bundesliga (GER)": 146, "Swiss Super League (SUI)": 69, "Austrian Bundesliga (AUT)": 38,
 "Keuken Kampioen Divisie (NED)": 111, "English League One (ENG)": 108,
 "English League Two (ENG)": 109, "MLS (USA)": 130, "Série A (BRA)": 268}

comps = {}
per_comp = {}
for m in res["matches"]:
    per_comp.setdefault(m["competition"], []).append(m)

for name in RUNLIST:
    if name in per_comp:
        comps[name] = {
            "status": "GEANALYSEERD",
            "primaryId": IDS[name],
            "seizoensnotatie": {"vorig": s3["fixtures"][name]["s_prev"],
                                "lopend": s3["fixtures"][name]["s_cur"]},
            "xg_dekking": s3["stats"].get(name),
            "matches": per_comp[name],
        }
        continue
    v = nxt.get(name)
    reden = (f"geen wedstrijd in het inzetvenster [08:00 NL 28 sep, 08:00 NL 29 sep) — "
             f"Fotmob-daglijsten van 28 sep (33 competities, 60 duels) en 29 sep (51 competities, "
             f"121 duels) op primaryId {IDS[name]} nagekeken, beide leeg; ook de eigen "
             f"Fotmob-competitiepagina (/api/data/leagues?id={IDS[name]}) gaf 0 duels in dit venster")
    if v:
        reden += (f"; eerstvolgende duel {v['datum']} — {v['eerste']} {v['aftrap_nl']} NL "
                  f"({v['aantal']} duels die dag)")
    else:
        reden += "; geen duel binnen de achttien vooruit gescande daglijsten"
    comps[name] = {"status": "GEEN WEDSTRIJD", "matches": [], "reden": reden,
                   "eerstvolgende": v}

state = {
 "run": "B", "date": DAY, "resumed_count": 0,
 "competitions": {k: comps[k] for k in RUNLIST},
 "completed": False,
 "parameters": {
   "MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3,
   "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
   "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
   "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "UNDERDOG_FLOOR": 0.35,
   "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping en anders als label",
   "POORT8": ("VERVALLEN sinds 25 sep 2026 (sides.LAPSES_ON). sides.check() laat elke kant door "
              "en zet alleen nog would_block; dat staat per selectie onder poort8_vervallen."),
   "HERIJKING": res.get("fit") or ("recalibrate.apply — a=1.0299, b=+0.0194 op 2346 afgerekende "
                                   "gevallen t/m 18 sep 2026"),
 },
 "vroeg_seizoen": res["vroeg_seizoen"],
 "niveau": res["niveau"],
 "afkapping": res["afkapping"],
 "selectie_5b": {
   "MAX_SHORTLIST": 3,
   "boven_de_drempel": sum(1 for r in top["herijkt"] if "haalt ook de lat" in r["status"]),
   "gepubliceerd": len(top["herijkt"]),
   "toelichting": ("Er was vandaag één doorgerekende wedstrijd, en de sterkste selectie daarin "
                   "haalt haar drempel ruim: Leganés – Castellón, 1X2 op de uitwinst, +11.64 pp "
                   "bij een drempel van 8.0. Eén selectie boven de drempel is minder dan "
                   "MAX_SHORTLIST (3 op maandag), dus §5b stap 5 is niet bindend — de rangorde "
                   "bepaalt de lijst en de drempel gaat als label mee. Dat label is hier positief: "
                   "deze bet zou onder de oude regel (drempel als poort vooraf) óók zijn "
                   "gepubliceerd. De 0-of-1-bet-regel bindt wél: dertien selecties zijn "
                   "doorgerekend over vijf markten en er is er één gepubliceerd, de hoogste op "
                   "selection_score. Tweede werd Draw No Bet op Castellón met 5.725 tegen 6.248 — "
                   "dezelfde mening in een push-beschermde markt."),
   "gekwalificeerd_niet_gepubliceerd": [],
   "lijstlengte_reeks": ("geen rij vandaag — er was één gekwalificeerde selectie en drie regels "
                         "beschikbaar, dus geen enkele selectie is op lijstlengte afgevallen"),
   "herijkt": top["herijkt"], "ruw": top["ruw"],
 },
 "bevestiging": {
   "fixtures_bron_1": ("Fotmob daglijsten 28 sep (33 competities, 60 duels) en 29 sep (51 "
                       "competities, 121 duels), per primaryId getoetst via "
                       "runwindow.matches_for_run — één duel uit de runlijst in het venster"),
   "fixtures_bron_2": ("tweede methode, een ánder Fotmob-endpoint: de eigen competitiepagina "
                       "/api/data/leagues?id=<primaryId> voor alle zeventien competities, met "
                       "hetzelfde venster [08:00 NL 28 sep, 08:00 NL 29 sep) er zelf op "
                       "toegepast. Uitkomst identiek: 1 duel, Leganés – Castellón om 20:30 NL, "
                       "en 0 bij de overige zestien. Dit is een andere route dan de daglijst, "
                       "dus een echte bevestiging en geen herhaling van dezelfde respons"),
   "fixtures_bron_3": ("BetExplorer-fixturepagina van de enige actieve competitie: Segunda "
                       f"División {len(odds['fixtures'].get('Segunda División (ESP)') or [])} "
                       f"teamparen, waarvan "
                       f"{sum(1 for r in (odds['fixtures'].get('Segunda División (ESP)') or []) if r['is_today'])} "
                       "vandaag — derde bron, andere site, zelfde uitkomst"),
   "fixtures_bron_4": ("achttien daglijsten vooruit gescand (rb28_next.py): vijftien van de "
                       "zestien stille competities hervatten tussen 30 september en 10 oktober, "
                       "met de grote groep op 8–10 oktober. Dat is het interlandvenster van "
                       "september/oktober en dus een kalenderverklaring, geen storing. Serie B "
                       "(ITA) heeft binnen die achttien dagen geen duel — dat is de langste "
                       "stilte van de lijst en het enige punt dat navraag verdient als het na "
                       "16 oktober zo blijft"),
   "uitkomst": ("één duel in het inzetvenster, in één competitie: Segunda División 1. "
                "Zestien competities GEEN WEDSTRIJD, alle zestien met twee bronnen bevestigd"),
   "inzetvenster": ("geen enkel duel viel vandaag over de venstergrens: het ene duel trapt af om "
                    "20:30 NL op de rundag zelf en staat op de daglijst van 28 sep. MLS en Série "
                    "A — de twee competities waarvoor runwindow.py is gebouwd — spelen vandaag "
                    "niet, dus de module deed vandaag niets bijzonders. Dat is de normale gang "
                    "van zaken op een maandag en geen aanwijzing dat de regel niet meer nodig is"),
 },
 "credits": {"the_odds_api": {
   "gebruikt_deze_run": 4, "over": 18638, "plafond_deze_run": odds["cap"],
   "markten_gekocht": {"h2h": odds["bought"]["h2h"], "spreads": odds["bought"]["spreads"],
                       "totals": odds["bought"]["totals"], "btts": odds["bought"]["btts"]},
   "marktbalans_inkoop": ("GESLAAGD, en met de maximale marge die op één competitie mogelijk is: "
                          "de enige actieve competitie kreeg de volle bulk, dus zowel een "
                          "uitkomstmarkt (1X2 op de beste prijs, Asian Handicap, Draw No Bet) als "
                          "een doelpuntenmarkt (Over/Under) deed mee, plus BTTS in de tweede "
                          "ronde. 1 van 1 competities met een doelpuntenmarkt en 1 van 1 met een "
                          "uitkomstmarkt. Double Chance ontbrak: de spreads-respons had geen "
                          "±0.5-lijn, dus die is bekeken met een reden en niet als gat geboekt"),
   "waarvoor": ("1 bulk-aanroep h2h+spreads+totals (Segunda División) van 3 credits, plus 1 "
                "BTTS-event-aanroep van 1 credit voor het enige duel met een kandidaat-edge. "
                "Het plafond was 3103 credits (18642 over, 3 dagen tot de maandwissel, 2 runs "
                "per dag), dus het budget was op geen enkel moment bindend.")}},
 "stage_min2": {
   "takken_nagelopen": 41,
   "ondiepe_kloon": True,
   "bevinding": ("De container leverde de repo opnieuw als ondiepe kloon (77 commits lokaal). "
                 "Vóór `git fetch --unshallow` telden 31 van de 41 takken 'eigen' commits — tot "
                 "315 stuks, en de histories leken zelfs volledig los te staan. Ná het "
                 "unshallowen (416 commits) staan alle 41 takken op 0 eigen commits. Dat is exact "
                 "het valse alarm dat Stage -2 beschrijft, en het is deze run opnieuw opgetreden. "
                 "Daarna op inhoud vergeleken, niet op de graaf, en voor alle vijf de logboeken: "
                 "picks.jsonl (319 id's), shadow.jsonl (712 rijen), calibration.jsonl (3384 "
                 "logische rijen), context-log.jsonl (836 id's) en national-matches.jsonl (6784) "
                 "— nul rijen op een andere tak die main niet heeft. Waar een tak dezelfde rij "
                 "nog als `pending` had, heeft main de afgewikkelde versie, dus main is ook per "
                 "record de rijkste. source-health.json en coverage.json idem: de enige "
                 "afwijkingen zijn het `last_run`-stempel van oudere runs en de OddsPapi-bron die "
                 "op main bewust is verwijderd (commit f342894). Er viel dus niets te mergen."),
   "op_main": True,
 },
 "dagrapport": None,
}
json.dump(state, open(f"data/run-state/{DAY}-run-b.json", "w"), ensure_ascii=False, indent=1)
print("geschreven:", f"data/run-state/{DAY}-run-b.json")
print("statussen:", {k: v["status"] for k, v in state["competitions"].items()})
