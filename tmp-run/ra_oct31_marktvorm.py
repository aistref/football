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

res = json.load(open("tmp-run/ra_oct31_results.json"))
s3 = json.load(open("tmp-run/ra_oct31_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_oct31_picks_a.json"))}

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
          open("tmp-run/ra_oct31_marktvorm.json", "w"), ensure_ascii=False, indent=1)
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
DAG = "2026-10-31"
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
    "26 okt 2026, NA het publiceren van deze run. Dit blok is een TELLING en verandert niets: "
    "geen pick, geen my_prob, geen edge, geen rangorde en geen regel in picks.jsonl. Een "
    "herberekening van 26 oktober geeft daarom exact dezelfde drie regels als de run zelf gaf. "
    "Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. De telling meet hier wat "
    "ze hoort te meten: alle zeven duels zijn binnenlandse competitieduels, dus `marketform` "
    "telt de duels van deze ploegen IN DIE COMPETITIE, op dezelfde populatie waarop het model "
    "is genormaliseerd. Het lopende seizoen staat op 7 tot 12 speeldagen en het vorige is "
    "volledig, dus `vorig` is de stevige reeks en `lopend_recent` (vijf duels) de dunne. GEEN "
    "van de veertien ploegen is promovendus of degradant, dus `found` is overal waar en er is "
    "geen enkele reeks die als gemeten nul gelezen kan worden. EN LET OP WAT DE TELLING "
    "VANDAAG ZEGT: ze SPREEKT TWEE VAN DE DRIE GEPUBLICEERDE REGELS TEGEN en STEUNT DE DERDE. "
    "TEGEN: Benfica ging dit seizoen in alle vier de uitduels over 2,5 doelpunt (gemiddeld "
    "4,50) en in zeven van de acht competitieduels (3,88), terwijl de bet een Under 2.5 is - de "
    "Under leunt daar volledig op Santa Clara, dat op 2,00 tot 2,25 doelpunt per duel staat en "
    "in 35 tot 40% van zijn duels over 2,5 ging. En PSG ging in zes van zeven competitieduels "
    "over 2,5 (3,29) en in beide thuisduels (3,50), en ook daar is de bet een Under 2.5. VOOR: "
    "Besiktas - Basaksehir Under 3.5 wordt door vrijwel elke reeks gesteund - Besiktas 20 tot "
    "35% boven 3,5 doelpunt en Basaksehir 24 tot 38% - met als enige tegenspraak de laatste "
    "vijf duels van Basaksehir (3 van 5). §6c eist dat zo'n tegenspraak VOORAAN in de "
    "voorbeschouwing staat en niet in een voetnoot, en dat is in het dagrapport van vandaag "
    "gedaan."
)
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
