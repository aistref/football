"""Run B 5 okt 2026 onder §5b: run-state en de logboeken. Nul bets, één duel in het venster.

Veel lichter dan `rb_oct04_publiceer.py`, en dat is geen versimpeling maar de uitkomst: het
enige duel in het inzetvenster komt op `data_tier = NONE` uit, dus er zijn geen kandidaten,
geen near_misses en geen picks om weg te schrijven. Wat er wél moet gebeuren is de volledige
boekhouding van §6b: de dekkingstabel met alle zeventien competities, het parameterblok, en
het voortgangsbestand (zonder `mark_completed` — dat gebeurt pas na het rapport en de push).
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.progress import load_or_start, mark, save
from scripts.ranking import max_shortlist

DAG = "2026-10-05"
RUN = "B"

res = json.load(open("tmp-run/rb_oct05_results.json"))
s3 = json.load(open("tmp-run/rb_oct05_stage3.json"))

# --- de dekkingstabel: alle zeventien competities, ook de stille (§5) ---
comps = {}
for naam, v in s3["fixtures"].items():
    if not v["matches"]:
        comps[naam] = {"status": "GEEN WEDSTRIJD", "matches": []}

for m in res["matches"]:
    e = dict(m)
    e["bet"] = False
    # §6b-5b: een markt die niet is doorgerekend hoort met een REDEN in markets_checked, niet
    # als gat. Bij tier NONE is er niets door te rekenen en slaat progress.py verify het duel
    # over; de reden hoort er toch bij te staan, anders leest een leeg blok later als verzuim.
    e["markets_checked"] = {k: ("niet doorgerekend — data_tier NONE: geen onafhankelijke "
                                "kansinput op het niveau waarop gespeeld wordt (§4)")
                            for k in ("1X2", "DC", "DNB", "AH", "OU", "BTTS")}
    comps.setdefault(m["competition"], {"status": "BUITEN DATADEKKING", "matches": []})
    comps[m["competition"]]["matches"].append(e)

state = load_or_start(RUN.lower(), date.fromisoformat(DAG))
top = toplist.build({"date": DAG, "run": RUN, "competitions": comps})

state["parameters"] = {
    "HERIJKING": (
        "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.988642, "
        "b=-0.007376 op 3507 afgerekende gevallen, fitted_through 2026-10-04. Praktisch de "
        "identiteit: het ruwe model zei gemiddeld 33.333% en het gebeurde 33.333%. "
        "fitted_through staat op de vorige rundag (4 okt), dus calibration.py settle is niet "
        "blijven liggen (§6b-5c). De correctie is deze run op geen enkele selectie toegepast, "
        "want er is geen selectie: het enige duel kwam op NONE uit."),
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
    "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
    "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
    "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
    "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
    "INTERLANDVENSTER": (
        "Zestien van de zeventien competities uit de runlijst hadden GEEN WEDSTRIJD, en dat is "
        "het interlandvenster en geen storing: scripts/idcheck.py gaf voor alle zeventien "
        "fotmob_id's een bruikbare stand (afsluitcode 0), dus geen enkele competitie is stil "
        "uit de lijst verdwenen. Dat is precies de controle waarvoor idcheck.py op 29 september "
        "is gebouwd — op een dag als vandaag is GEEN WEDSTRIJD de normale uitkomst en zou een "
        "kapot id er niet van te onderscheiden zijn. Eén competitie speelde: Segunda División "
        "(ESP) met één duel. MLS en Série A (BRA) staan op geen van beide daglijsten (5 en 6 "
        "okt), dus ook met het inzetvenster van runwindow.py valt daar niets te halen; de audit "
        "in tmp-run/rb_oct05_stage3.json legt dat per daglijst vast — op de daglijst van 6 okt "
        "staat geen enkele competitie uit deze runlijst."),
    "POORT8": (
        "BINDT, in de lichte vorm met ondergrens 0.35 (§1e). Hij is deze run niet aan de orde "
        "gekomen: poort 4 (data_tier ≠ NONE) sloot eerder, dus er is geen selectie waarop "
        "sides.check() is aangeroepen. De twee schaduwreeksen `underdog` en `underdog_ruw` "
        "groeien deze run dus niet; ze staan op 31 respectievelijk 17 afgewikkelde gevallen."),
    "WAAROM_NUL_BETS": (
        "Nul bets, en de oorzaak zit vóór de analyse en niet erin: er was precies ÉÉN wedstrijd "
        "in het inzetvenster van de hele runlijst van zeventien competities, en die kwam op "
        "data_tier NONE uit. Er is dus geen selectie doorgerekend, geen poort getoetst en geen "
        "rangorde om op te snijden — §5b kan niets afkappen waar niets staat. Dat is geen "
        "mislukte run: §1 noemt nul bets een volwaardige uitkomst en §8 zegt dat dit bij deze "
        "runlijst de normale uitkomst is. Wat het wél betekent: deze run heeft over de kwaliteit "
        "van het model vandaag niets gemeten, want er is niets gemeten. Het kalibratielogboek "
        "groeit deze run met nul waarnemingen."),
    "WAAROM_DAT_ENE_DUEL_NONE_IS": (
        "Córdoba – Tenerife (20:30 NL) komt op NONE uit, en het is DE VIERDE RUN OP RIJ DEZELFDE "
        "STRUCTURELE OORZAAK in deze competitie. Tenerife staat niet in de Segunda-stand van "
        "2025/2026 en ook niet in die van La Liga: het is een promovendus uit de Primera "
        "Federación. promotion.TIER2 kent geen Spaans paar LaLiga2/Primera Federación, dus er is "
        "geen tak om langs om te rekenen; de omrekening valt terug op de TIER1-tak (degradant uit "
        "La Liga) en vindt hem daar natuurlijk ook niet. DE FOUTMELDING NOEMT DAAROM ALLEEN DE "
        "DEGRADANTENKANT ('staat niet in de stand van La Liga (ESP) 2025/2026'), wat de oorzaak "
        "makkelijk verkeerd laat lezen — de echte oorzaak is het ontbrekende divisiepaar ONDER "
        "LaLiga2. Op 2 en 3 oktober was het Sabadell, op 4 oktober Celta Fortuna, vandaag "
        "Tenerife: drie verschillende ploegen, één gat. §4 is hier hard in en deze run wijkt daar "
        "niet van af: buiten het gemeten bereik is er geen onafhankelijke kansinput op het niveau "
        "waarop gespeeld wordt, dus NONE en geen bet. Wat vandaag wél opvalt en in het rapport "
        "staat: Tenerife heeft inmiddels 7 duels LaLiga2 mét xG in het LOPENDE seizoen (6.2 xG / "
        "8.2 xGA). De data op het juiste niveau bestaat dus; wat ontbreekt is een prior uit vorig "
        "seizoen. Of dat genoeg is om zo'n duel door te rekenen is een regelwijziging en een "
        "besluit van de gebruiker, geen keuze van deze run."),
    "DEKKINGSSTATUS": (
        "Segunda División (ESP) staat als BUITEN DATADEKKING in de dekkingstabel, en dat verdient "
        "één regel uitleg omdat de letterlijke definitie van §5 ('geen werkende onafhankelijke "
        "kansbron') hier net niet past. De bron wérkt: Fotmob gaf voor deze competitie een "
        "bruikbare stand over beide seizoenen, met xG, en ook de volledige wedstrijdcontext "
        "(datarijkdom 5.0, opstelling lastStarting11, uitvallers met marktwaarde, vorm en rust "
        "voor beide ploegen). Wat ontbreekt is een kansinput voor Tenerife OP HET NIVEAU WAAROP "
        "GESPEELD WORDT. Van de vier statussen die §5 toestaat is dit de enige die klopt — "
        "GEANALYSEERD zou liegen, want er is geen enkele markt doorgerekend. De reden staat er "
        "daarom bij, in beide rapporten."),
    "inkoop": (
        "3 credits van een plafond van 368 (19.901 over bij api_check.py, 99 verbruikt deze "
        "maand, 27 dagen tot de maandwissel, 2 runs per dag). Eén bulk-aanroep à 3 credits (h2h "
        "+ spreads + totals) voor Segunda División (ESP), de enige spelende competitie en de "
        "enige met een sportkey: split_budget(368, 1) -> (1, 1), dus niemand viel buiten de bulk. "
        "Die prijzen zijn opgehaald VOORDAT de tier bekend was — dat is de volgorde van §1a (per "
        "competitie inkopen, niet per duel) en het kost niets extra. Stap 2 (BTTS, 1 credit per "
        "duel) is niet gezet: §1a stap 2 vraagt een kandidaat-edge en bij NONE is er geen "
        "selectie om er een te hebben. MARKTBALANS: de controle van §1a slaagt formeel — de ene "
        "spelende competitie heeft zowel een uitkomst- als een doelpuntenmarkt uit dezelfde "
        "bulk — maar met de kleinst mogelijke marge die er bestaat, namelijk één competitie. Dat "
        "is geen te krap plafond (368 beschikbaar, 3 uitgegeven) maar een kalender met één duel."),
    "BEURSKOERSEN": "Niet van toepassing: geen gepubliceerde regels.",
    "p_xg_shrink08": ("Niet van toepassing: geen doorgerekende wedstrijd, dus geen "
                      "calibration-blok en geen shrink-arm om vast te leggen (§6e)."),
    "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = res.get("vroeg_seizoen")
state["niveau"] = res.get("niveau")
state["selectie_5b"] = top

for comp, blok in comps.items():
    mark(state, comp, blok)
save(state)
print(f"run-state Run {RUN} weggeschreven ({len(comps)} competities)")
print("toplist herijkt:", len(top["herijkt"]), "ruw:", len(top["ruw"]))
print("picks: 0 — niets toe te voegen aan data/picks.jsonl")
