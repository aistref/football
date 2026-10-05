"""Naschrift bij Run B 5 okt 2026: het duel is ná de meting wél doorgerekend, dus boek het.

Waarom dit bestaat. De run was om 05:31 afgerond met nul bets en één duel op `data_tier = NONE`,
en de notificatie was verstuurd. Daarna heeft de gebruiker toestemming gegeven het divisiepaar
LaLiga2/Primera Federación te meten (§4), en daarmee is Córdoba – Tenerife alsnog doorrekenbaar
geworden — vóór de aftrap van 20:30, dus het had nog een bet kunnen worden.

**Het is er geen geworden, en dat verandert de uitkomst van de dag dus niet: nul bets blijft nul
bets.** Alle elf doorgerekende selecties sneuvelen op een echte poort — vier op poort 8
(underdog-kant onder de ondergrens, precies de rem die de gebruiker diezelfde ochtend heeft laten
staan) en de rest op poort 5 (tegenstrijdige methodes). §5b heeft daardoor niets te rangschikken.

Wat er wél verandert zijn de METINGEN, en die horen geboekt: §6d eist dat elke afgewezen kandidaat
in het schaduwlogboek komt, §6e eist een kalibratieblok per doorgerekend duel, en §1e zegt met
zoveel woorden dat de `underdog`-reeks de enige is die de vraag van 25 september nog kan
beantwoorden. Die reeks een waarneming onthouden omdat het rapport al klaar was, zou precies de
stille administratiefout zijn waar §6b-5b voor is gebouwd.

De dekkingsstatus van Segunda División gaat daarom van BUITEN DATADEKKING naar GEANALYSEERD, en
beide rapporten worden opnieuw gegenereerd.
"""
import json, sys
from datetime import date
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.progress import load_or_start, mark, save

DAG = "2026-10-05"
RUN = "B"

res = json.load(open("tmp-run/rb_oct05b_results.json"))
s3 = json.load(open("tmp-run/rb_oct05_stage3.json"))

comps = {}
for naam, v in s3["fixtures"].items():
    if not v["matches"]:
        comps[naam] = {"status": "GEEN WEDSTRIJD", "matches": []}

for m in res["matches"]:
    e = dict(m)
    e["bet"] = False
    comps.setdefault(m["competition"], {"status": "GEANALYSEERD", "matches": []})
    comps[m["competition"]]["matches"].append(e)

state = load_or_start(RUN.lower(), date.fromisoformat(DAG))
top = toplist.build({"date": DAG, "run": RUN, "competitions": comps})

p = state.setdefault("parameters", {})
p["NASCHRIFT_METING"] = (
    "Dit voortgangsbestand is ná de afronding van 05:31 nog één keer bijgewerkt, en dat is geen "
    "hervatting (zie `duur`). Reden: de gebruiker gaf om 05:40 toestemming het divisiepaar "
    "LaLiga2/Primera Federación te meten, en met die factor is Córdoba – Tenerife alsnog "
    "doorrekenbaar — vóór de aftrap van 20:30. De uitkomst van de dag verandert er niet door: "
    "ALLE ELF doorgerekende selecties sneuvelen op een echte poort, vier op poort 8 (underdog, de "
    "rem die de gebruiker diezelfde ochtend heeft laten staan) en de rest op poort 5 "
    "(tegenstrijdige methodes), dus §5b heeft niets te rangschikken en het blijft nul bets. Wat "
    "er wél verandert zijn de metingen: één `underdog`-rij in het schaduwlogboek (§6d, en §1e "
    "noemt die reeks de enige die de vraag van 25 september nog kan beantwoorden), drie "
    "kalibratiewaarnemingen (§6e) en de dekkingsstatus van Segunda División van BUITEN "
    "DATADEKKING naar GEANALYSEERD. De sterkste geblokkeerde selectie is Double Chance 'Tenerife "
    "of gelijk' (AH +0.5) @1.98, +11.53 pp herijkt, score 3.576, met drie andere selecties op "
    "diezelfde kant.")
p["WAAROM_NUL_BETS"] = (
    "Nul bets, en na de meting van 05:40 om een ándere reden dan in de eerste versie van dit "
    "bestand stond. Toen: het enige duel in het inzetvenster kwam op data_tier NONE uit, dus er "
    "was niets om door te rekenen. Nu: het duel IS doorgerekend op LIGHT — elf selecties over vijf "
    "markten — en alle elf sneuvelen op een poort. Vier op poort 8 en de rest op poort 5. Dat is "
    "een inhoudelijk betere nul dan de eerste: er is nu gemeten in plaats van overgeslagen, en de "
    "wedstrijd levert een rij op in het schaduwlogboek en drie in het kalibratielogboek. §1 noemt "
    "nul bets een volwaardige uitkomst en §1g heeft op 552 afgerekende gevallen gemeten dat er "
    "geen drempel bestaat die geld oplevert; de drempel van 16.0 pp voor LIGHT werd hier door de "
    "sterkste selectie ook niet gehaald (+11.53 pp).")
p["POORT8"] = (
    "BINDT, in de lichte vorm met ondergrens 0.35 (§1e), en vandaag is hij de poort die de dag "
    "bepaalt. De gebruiker heeft hem om 05:40 uitdrukkelijk laten staan terwijl de meetlat van "
    "§1e wél was gehaald (36 afgewikkelde kandidaten, +16.9%) — en in hetzelfde half uur blokkeert "
    "hij de vier sterkste selecties van het enige duel van de run, alle vier op de Tenerife-kant "
    "(markt 24.0% tegen 49.4%, onder de 35%). Zonder die rem had §5b hier een regel gepubliceerd "
    "op rangorde, onder de lat van 16.0 pp. De sterkste gaat als failed_gate='underdog' het "
    "schaduwlogboek in; poort8_ruw blijft leeg omdat het dezelfde selectie is (§5a regel 2). "
    "sides.check() is met today=2026-10-05 aangeroepen zoals §1e eist.")
p["TIER_NA_DE_METING"] = (
    "LIGHT, en dat kan niet anders: §4 zegt dat een omgerekende ploeg NOOIT FULL is, want de "
    "omrekening haalt de systematische fout eruit en niet de onzekerheid (RESIDUAL_SPREAD houdt "
    "~0.16 relatieve sterkte over). Tenerife is omgerekend uit de Primera Federación, groep "
    "Group 1, relatieve aanval 1.346 en verdediging 0.521, beide binnen het gemeten bereik — zie "
    "het promovendi-blok op de wedstrijd. Drempel dus 16.0 pp en niet 8.0.")
p["DEKKINGSSTATUS"] = (
    "Segunda División (ESP) staat nu op GEANALYSEERD. In de eerste versie van dit bestand stond "
    "BUITEN DATADEKKING, met de aantekening dat die status wrong omdat de bron niet faalde maar "
    "een gemeten omrekening ontbrak. Die omrekening is er nu, dus de status is gewoon juist.")
state["vroeg_seizoen"] = res.get("vroeg_seizoen")
state["niveau"] = res.get("niveau")
state["selectie_5b"] = top

for comp, blok in comps.items():
    mark(state, comp, blok)
save(state)
print(f"run-state bijgewerkt ({len(comps)} competities); Segunda nu "
      f"{comps['Segunda División (ESP)']['status']}")
print("toplist herijkt:", len(top["herijkt"]), "ruw:", len(top["ruw"]))
