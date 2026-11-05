"""Run A, 5 nov 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

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

res = json.load(open("tmp-run/ra_nov05_results.json"))
s3 = json.load(open("tmp-run/ra_nov05_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_nov05_picks_a.json"))}

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
          open("tmp-run/ra_nov05_marktvorm.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(uit)} wedstrijden geteld, {len(fouten)} fout(en)")
for k, v in fouten.items():
    print("  FOUT", k, v)

# De lijn uit de selectie LEZEN in plaats van hem in een tabel bij te houden. De oude tabel
# kende vier selecties en gaf voor al het andere stil 2.5 terug; vandaag ("Under 4.5") zou dat
# betekenen dat de telling op 2,5 doelpunt onder een bet op 4,5 doelpunt komt te staan — een
# getal dat niets met de bet te maken heeft, zonder dat iets klaagt. Toegevoegd 5 nov 2026.
def _lijn(selectie: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)", selectie or "")
    return float(m.group(1)) if m else 2.5
print("\n=== DE GEPUBLICEERDE REGELS ===")
for naam, p in picks.items():
    b = uit.get(naam)
    if not b:
        print(f"\n{naam}: geen blok"); continue
    lijn = _lijn(p["selection"]) if p["market"] == "Over/Under" else 2.5
    # Op een hele lijn (Over 3) telt "meer dan 3" — marketform telt strikt groter dan de lijn,
    # dus 3.5 en 3.0 geven hetzelfde antwoord voor "4 of meer". Voor de leesbaarheid tellen we
    # op de gangbare lijn 2.5 én op de lijn van de bet zelf.
    # `marketform.LINES` telt alleen hele en halve lijnen (1.5, 2.0, 2.5, 3.0, 3.5, 4.5), dus
    # een KWARTLIJN als 3.75 staat er niet in en gaf een KeyError. Toon dan de naastgelegen
    # getelde lijn: bij Under 3.75 beslist het vierde doelpunt de bet, en dat is precies wat
    # ">3.5 doelpunten" telt. Zelfde reden als de bestaande 3.0 -> 3.5 afbeelding: 3.0 is een
    # push-lijn en de frequentie die de lezer wil zien is die van het doelpunt dat hem kost.
    from scripts import marketform as _mf
    toon = 3.5 if lijn == 3.0 else lijn
    if str(toon) not in b["teams"]["home"]["lopend"]["over"]:
        toon = min(_mf.LINES, key=lambda L: (abs(L - lijn), L))
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
DAG = "2026-11-05"
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
    "5 nov 2026, NA het publiceren van deze run. Dit blok is een TELLING en verandert niets: "
    "geen pick, geen my_prob, geen edge, geen rangorde en geen regel in picks.jsonl. Een "
    "herberekening van 5 november geeft daarom exact dezelfde twee regels als de run zelf gaf. "
    "Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. "
    "DE TELLING ZEGT VANDAAG VRIJWEL NIETS, EN DAT IS ZELF DE BEVINDING. `marketform` telt de "
    "duels van deze ploegen IN DIE COMPETITIE, en vandaag is die competitie een EUROPEES "
    "TOERNOOI in de league-fase. Het lopende Conference League-seizoen staat op TWEE speeldagen "
    "en de Europa League op VIER, dus `lopend` is n=2 en `lopend_kant` n=1. Erger: geen van de "
    "vier ploegen van de twee gepubliceerde bets speelde dit toernooi VORIG seizoen, dus "
    "`vorig` geeft bij alle vier 'speelde die competitie niet' en er is GEEN stevige reeks om "
    "op terug te vallen. Dat is het structurele verschil met 4 november, toen de Championship- "
    "duels dertien speeldagen en een volledig vorig seizoen van 46 hadden. "
    "LEES DE GETALLEN HIERONDER DUS NIET ALS FREQUENTIES. Een '0 van 1' of '1 van 2' is een "
    "losse wedstrijd en geen percentage, en §6d eist ~30 gevallen voordat een reeks gelezen mag "
    "worden. Ze staan er omdat §4 eist dat ze er bij een doelpuntenmarkt bij staan, niet omdat "
    "ze vandaag iets dragen. "
    "WAT ER DAN TOCH STAAT, met de aantallen er hard bij. FC TWENTE - PAFOS, UNDER 3.5: Twente "
    "kwam dit seizoen in 1 van 2 Conference League-duels boven 3,5 uit (gemiddeld 3,00) en "
    "thuis in 0 van 1 (gemiddeld 1,00); Pafos in 1 van 2 (gemiddeld 3,00) en uit in 1 van 1 "
    "(gemiddeld 4,00). Twee van de vier hoeken wijzen naar de bet, twee ertegen, en alle vier "
    "op een of twee wedstrijden. Dat is GEEN tegenspraak en GEEN steun - het is ruis, en dat is "
    "het eerlijke antwoord. Anders dan op 4 november, toen de telling bij beide Unders eenduidig "
    "tegen de bet in wees over drie tot twaalf duels. "
    "FC MIDTJYLLAND - AJAX, DNB FC MIDTJYLLAND: een doelpuntentelling zegt over een Draw No Bet "
    "niets over de uitkomst zelf. Wat ze laat zien is dat Midtjylland zijn twee duels doelpuntarm "
    "hield (0 van 2 boven 2,5, gemiddeld 1,50, thuis 1,00) en Ajax op 1 van 2 staat (gemiddeld "
    "2,50, uit 3,00). Ook hier: n=1 en n=2. "
    "DE LIJN WORDT UIT DE SELECTIE GELEZEN en niet uit een tabel met vier ingangen (toegevoegd "
    "5 nov 2026 n.a.v. Under 4.5 van 3 november, waar die tabel stil 2,5 teruggaf - een getal "
    "dat niets met de bet te maken heeft, zonder dat iets klaagt). "
    "EN EEN FOUT UIT DEZE RUN DIE HIER THUISHOORT: dit script had `DAG` HARDGECODEERD op "
    "2026-11-04 en schreef daarmee bij de eerste aanroep in het voortgangsbestand van GISTEREN "
    "in plaats van dat van vandaag. Omdat de wedstrijdnamen van vandaag daar niet in voorkomen "
    "kwam het op '0 wedstrijden gezet' uit en bleven de matchblokken van 4 november ongemoeid; "
    "alleen het veld `marktvorm_toegevoegd` van die dag kreeg de datum van vandaag. Dat is "
    "teruggedraaid met `git checkout` voordat er iets gecommit is, en de datum staat nu op "
    "2026-11-05. Het staat hier opgeschreven omdat het exact de stille faalvorm is waar deze "
    "repo op meerdere plekken voor waarschuwt: de telling klaagde niet, ze rapporteerde een "
    "nette nul."
)
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
