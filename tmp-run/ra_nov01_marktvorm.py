"""Run A, 26 okt 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

Op verzoek van de gebruiker (17 okt): de onderbouwing van een Over/Under- of BTTS-bet noemde de
doelverwachting van het model en de vorm als `WWDLW`, maar nooit hoe vaak de markt werkelijk
opging. Deze aanroep telt dat met `scripts/marketform.py` voor elke doorgerekende wedstrijd en
legt het in `data/run-state/` onder `marktvorm`.

Let op wat dit NIET is: de telling gaat niet in `my_prob` en verandert geen enkele pick, kans of
rangorde van vandaag. Ze komt naast het model te staan (§2, §4 — een getal met een gewicht
verzinnen waarvoor geen meting bestaat is verboden).
"""
import json, re
from scripts import marketform

res = json.load(open("tmp-run/ra_nov01_results.json"))
s3 = json.load(open("tmp-run/ra_nov01_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_nov01_picks_a.json"))}

meta = {naam: (v.get("primaryId"), v.get("s_prev"), v.get("s_cur"))
        for naam, v in s3["fixtures"].items()}

uit, fouten = {}, {}
for m in res["matches"]:
    lid, s_prev, s_cur = meta.get(m["competition"], (None, None, None))
    # EEN BEKERDUEL DAT DOOR `shared_lower_division` IS GERED, TELT IN DIE DIVISIE EN NIET IN DE
    # BASISDIVISIE (gevonden en gerepareerd 30 okt 2026). `meta` geeft voor een beker de
    # `primaryId` uit `promotion.CUP_BASE` — voor de DFB Pokal dus de Bundesliga — terwijl de
    # analyse Hannover 96 - Kaiserslautern in de 2. BUNDESLIGA heeft doorgerekend. De telling
    # zocht die twee ploegen daarna in de Bundesliga-stand en gaf vier keer "speelde die
    # competitie niet" op een GEPUBLICEERDE bet. Dat is geen foutmelding maar een leeg blok, en
    # §4 eist juist bij een doelpuntenmarkt dat de frequenties erbij staan. Het id staat in de
    # `note` van `basis_per_wedstrijd`, in dezelfde vorm als `promotion.shared_lower_division`
    # hem schrijft.
    bpw = m.get("basis_per_wedstrijd") or {}
    if bpw.get("note"):
        gevonden = re.search(r"\(Fotmob (\d+)\)", bpw["note"])
        if gevonden:
            lid = int(gevonden.group(1))
            print(f"  {m['match']}: telling in {bpw['competitie']} (id {lid}) en niet in "
                  f"{m['competition']}")
    if not lid or m["tier"] == "NONE":
        continue
    try:
        uit[m["match"]] = marketform.match_block(lid, s_cur, s_prev, m["home"], m["away"])
    except Exception as e:
        fouten[m["match"]] = f"{type(e).__name__}: {e}"

json.dump({"blokken": uit, "fouten": fouten},
          open("tmp-run/ra_nov01_marktvorm.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(uit)} wedstrijden geteld, {len(fouten)} fout(en)")
for k, v in fouten.items():
    print("  FOUT", k, v)

LIJN = {"Over 3": 3.0, "Under 3": 3.0, "Under 3.5": 3.5, "Over 2.5": 2.5}
print("\n=== DE GEPUBLICEERDE REGELS ===")
for naam, p in picks.items():
    b = uit.get(naam)
    if not b:
        print(f"\n{naam}: geen blok"); continue
    lijn = LIJN.get(p["selection"], 2.5)
    # Op een hele lijn (Over 3) telt "meer dan 3" — marketform telt strikt groter dan de lijn,
    # dus 3.5 en 3.0 geven hetzelfde antwoord voor "4 of meer". Voor de leesbaarheid tellen we
    # op de gangbare lijn 2.5 én op de lijn van de bet zelf.
    toon = 3.5 if lijn == 3.0 else lijn
    print(f"\n{naam} — {p['market']} {p['selection']} @{p['odds']:.4f} "
          f"(model: {p['my_prob']*100:.1f}%)")
    for rol in ("home", "away"):
        t = b["teams"][rol]
        for sleutel, label in (("lopend_recent", "laatste 5 in de competitie"),
                               ("lopend", "heel lopend seizoen"),
                               ("lopend_kant", "dit seizoen thuis" if rol == "home" else "dit seizoen uit"),
                               ("vorig", "heel vorig seizoen")):
            d = t[sleutel]
            if not d["found"]:
                print(f"   {t['team']:22s} {label:28s} speelde die competitie niet")
                continue
            if not d["n"]:
                continue
            o = d["over"][str(toon)]
            print(f"   {t['team']:22s} {label:28s} n={d['n']:2d}  "
                  f">{toon:g} doelp.: {o:2d} ({100*o/d['n']:3.0f}%)  "
                  f"BTTS: {d['btts']:2d} ({d['btts_pct']:3.0f}%)  "
                  f"gem. {d['goals_per_match']:.2f}")

# --- en in data/run-state/, zodat report.py het kan renderen -------------------------------
DAG = "2026-11-01"
STATE = f"data/run-state/{DAG}-run-a.json"
st = json.load(open(STATE))
gezet = 0
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        b = uit.get(m.get("match"))
        if b:
            m["marktvorm"] = b
            gezet += 1
st["marktvorm_toegevoegd"] = (
    "1 nov 2026, NA het publiceren van deze run. Dit blok is een TELLING en verandert niets: "
    "geen pick, geen my_prob, geen edge, geen rangorde en geen regel in picks.jsonl. Een "
    "herberekening van 1 november geeft daarom exact dezelfde vijf regels als de run zelf gaf. "
    "Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. De telling meet hier wat ze "
    "hoort te meten: alle 37 duels zijn binnenlandse competitieduels, dus `marketform` telt de "
    "duels van deze ploegen IN DIE COMPETITIE, op dezelfde populatie waarop het model is "
    "genormaliseerd. Het lopende seizoen staat op 8 tot 13 speeldagen en het vorige is volledig, "
    "dus `vorig` is de stevige reeks en `lopend_recent` (vijf duels) de dunne. NEGEN van de 37 "
    "duels hebben een promovendus of degradant aan boord, en bij die ploegen is `found` in de "
    "basisdivisie onwaar — lees zo'n lege reeks als ONBEKEND en niet als een gemeten nul. Geen "
    "van die negen is een gepubliceerde bet geworden. "
    "EN LET OP WAT DE TELLING VANDAAG ZEGT, want ze is bij de vijf gepubliceerde regels niet "
    "eenduidig. STEUNT: Juventus - Napoli, BTTS nee. Juventus kwam dit seizoen in 3 van 10 "
    "competitieduels tot beide ploegen die scoren (30%) en thuis in 1 van 5 (20%), Napoli uit in "
    "2 van 5 (40%); over heel vorig seizoen 42% en 50%. Een BTTS-nee op twee ploegen die hun "
    "duels vaak dichthouden is wat de reeksen zeggen. STEUNT OOK, MAAR SCHEEF: Getafe - Sevilla, "
    "BTTS nee. Getafe is de hele onderbouwing - 3 van 10 met BTTS dit seizoen, 1 van de laatste "
    "5, en thuis exact NUL duels boven 2,5 doelpunt op vijf wedstrijden (gemiddeld 1,60). "
    "SEVILLA SPREEKT DE BET TEGEN: 7 van 10 met BTTS dit seizoen, uit 4 van 5 (80%), gemiddeld "
    "3,60 doelpunt per uitduel. De bet leunt dus volledig op de thuisploeg, en §6c eist dat die "
    "tegenspraak VOORAAN in de voorbeschouwing staat en niet in een voetnoot. "
    "GEMENGD: Kasimpasa - Besiktas, BTTS nee. Kasimpasa zat dit seizoen in 6 van 9 duels op BTTS "
    "(67%) en thuis in 3 van 4 (75%) - dat is tegen de bet - terwijl Besiktas op 4 van 9 (44%) "
    "en uit 2 van 4 staat. Vorig seizoen: Kasimpasa 53%, Besiktas 59%. Dit is de regel met de "
    "hoogste edge van de dag en de zwakste frequentiesteun, en die twee dingen horen naast elkaar "
    "te staan. "
    "TEGEN, OP DE DUNNE REEKS: Lyon - Angers, Under 3.5. De brede reeksen steunen hem ruim - Lyon "
    "25% boven 3,5 dit seizoen en 32% vorig jaar, Angers 38% en 18% - maar Lyon THUIS staat dit "
    "seizoen op 2 van 4 boven 3,5 (gemiddeld 3,25) en Angers UIT op 2 van 3 (3,33). Dat zijn "
    "reeksen van drie en vier duels en dus ruis, maar het is de enige hoek die iets anders zegt. "
    "NEUTRAAL: Liverpool - Arsenal, DNB Arsenal. Een doelpuntentelling zegt over een Draw No Bet "
    "niets over de uitkomst zelf; wat ze wel laat zien is dat beide ploegen dit seizoen laag "
    "scoren tegenover vorig jaar (Liverpool 2,38 tegen 3,05 per duel, Arsenal 2,25 tegen 2,58) en "
    "dat Arsenal in zijn vier uitduels geen enkele keer beide ploegen zag scoren. Dat past bij een "
    "krap duel, en een krap duel is precies waar een DNB zijn geld verdient of niet."
)
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
