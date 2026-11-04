"""Run A, 4 nov 2026 — de doelpunten- en BTTS-frequenties bij de bets van vandaag.

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

res = json.load(open("tmp-run/ra_nov04_results.json"))
s3 = json.load(open("tmp-run/ra_nov04_stage3.json"))
picks = {p["home"] + " – " + p["away"]: p
         for p in json.load(open("tmp-run/ra_nov04_picks_a.json"))}

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
          open("tmp-run/ra_nov04_marktvorm.json", "w"), ensure_ascii=False, indent=1)
print(f"{len(uit)} wedstrijden geteld, {len(fouten)} fout(en)")
for k, v in fouten.items():
    print("  FOUT", k, v)

# De lijn uit de selectie LEZEN in plaats van hem in een tabel bij te houden. De oude tabel
# kende vier selecties en gaf voor al het andere stil 2.5 terug; vandaag ("Under 4.5") zou dat
# betekenen dat de telling op 2,5 doelpunt onder een bet op 4,5 doelpunt komt te staan — een
# getal dat niets met de bet te maken heeft, zonder dat iets klaagt. Toegevoegd 4 nov 2026.
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
DAG = "2026-11-04"
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
    "4 nov 2026, NA het publiceren van deze run. Dit blok is een TELLING en verandert niets: "
    "geen pick, geen my_prob, geen edge, geen rangorde en geen regel in picks.jsonl. Een "
    "herberekening van 3 november geeft daarom exact dezelfde drie regels als de run zelf gaf. "
    "Zie _shared-rules.md §4, 'Hoe vaak ging deze markt eerder op?'. "
    "LEES DE REEKSEN VAN DE CHAMPIONS LEAGUE-DUELS MET DE AANTALLEN ERBIJ. `marketform` telt de "
    "duels van deze ploegen IN DIE COMPETITIE, en het lopende Champions League-seizoen staat op "
    "DRIE speeldagen - dus `lopend` is daar n=3 en `lopend_kant` n=1 of n=2. Dat zijn geen "
    "reeksen maar losse wedstrijden, en ze mogen niet als frequentie worden gelezen. De negen "
    "Championship-duels staan er heel anders voor: dertien speeldagen dit seizoen en een "
    "volledig vorig seizoen van 46, dus daar is `vorig` de stevige reeks. "
    "DE LIJN WORDT SINDS VANDAAG UIT DE SELECTIE GELEZEN en niet meer uit een tabel met vier "
    "ingangen. Die tabel kende 'Under 3.5' en 'Over 2.5' en gaf voor al het andere stil 2,5 "
    "terug; bij Barcelona - Aston Villa (Under 4.5) zou de telling daarmee op 2,5 doelpunt "
    "hebben gestaan onder een bet op 4,5 - een getal dat niets met de bet te maken heeft, zonder "
    "dat iets klaagt. Dezelfde stille faalvorm als de bekerbasis van 30 oktober. "
    "EN LET OP WAT DE TELLING VANDAAG ZEGT, WANT BIJ BEIDE UNDERS SPREEKT ZE DE BET TEGEN - EN "
    "DAT HOORT VOORAAN IN DE VOORBESCHOUWING EN NIET IN EEN VOETNOOT (§4, §6c). "
    "TEGEN: Bodo/Glimt - Lille, Under 3.5. Bodo/Glimt kwam in zijn drie Champions "
    "League-duels van dit seizoen twee keer boven 3,5 doelpunt uit (67%, gemiddeld 4,33) en "
    "Lille ook twee van drie (67%, gemiddeld 4,67). Over het hele vorige Champions "
    "League-seizoen staat Bodo/Glimt op 8 van 12 boven 3,5 (67%, gemiddeld 3,67) - twaalf duels, "
    "dus dat is de enige stevige reeks van de vier en hij zegt hetzelfde. Lille speelde het "
    "toernooi vorig jaar niet. Het model zegt 75,2% kans dat er DRIE of minder vallen, en elke "
    "reeks die er is zegt tweederde kans op VIER of meer. EEN HOEK ZEGT WEL IETS ANDERS: "
    "Bodo/Glimt THUIS staat dit seizoen op 0 van 1 boven 3,5 met een gemiddelde van 1,00 - een "
    "wedstrijd, dus geen reeks, maar het is het enige cijfer dat de bet steunt. Dit is de "
    "tegenspraak van vandaag, en ze gaat over dezelfde kant waarvan §6g een gemeten scheefstand "
    "heeft. "
    "TEGEN, EN STERKER: Barcelona - Aston Villa, Under 4.5. Barcelona kwam in alle DRIE zijn "
    "Champions League-duels van dit seizoen boven 4,5 doelpunt uit - drie van drie, honderd "
    "procent - met een gemiddelde van 5,67 doelpunt per duel, en thuis in zijn ene duel op 6,00. "
    "Aston Villa: twee van drie boven 4,5 dit seizoen, gemiddeld 5,00, en het toernooi vorig "
    "jaar niet gespeeld. De enige brede reeks is Barcelona vorig seizoen: 5 van 12 boven 4,5 "
    "(42%, gemiddeld 4,33), en die staat dichter bij de bet dan bij de tegenspraak. Maar een "
    "gemiddelde van 5,67 en 5,00 doelpunt per duel staat BOVEN de lijn van 4,5 waarop deze bet "
    "is afgesloten, en vijf van de zes cijfers wijzen dezelfde kant op. De aantallen zijn drie "
    "en drie en dus geen reeks; de richting is wel eenduidig en het is niet de richting van de "
    "bet. "
    "NEUTRAAL: West Bromwich Albion - Southampton, Draw No Bet Southampton. Een "
    "doelpuntentelling zegt over een Draw No Bet niets over de uitkomst zelf. Wat ze wel laat "
    "zien is dat dit op papier een krap duel is: West Bromwich kwam dit seizoen in 6 van 13 "
    "duels boven 2,5 doelpunt (46%, gemiddeld 2,54) en thuis in 2 van 6 (33%, gemiddeld 2,50), "
    "en vorig seizoen 21 van 46 (46%, gemiddeld 2,30). Southampton staat hoger: 8 van 13 dit "
    "seizoen (62%, gemiddeld 3,15) en 29 van 46 vorig jaar (63%). Een krap duel is precies waar "
    "een Draw No Bet zijn geld verdient of niet, en de thuisploeg is de ploeg die het krap "
    "houdt."
)
json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nmarktvorm-blok op {gezet} wedstrijden in run-state gezet")
