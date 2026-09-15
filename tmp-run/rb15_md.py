"""Run B, 15 sep 2026 — het markdown-runrapport opbouwen uit data/run-state/.

Zelfde opzet als `rb12_md.py`: de vaste secties staan hieronder als tekst, de wedstrijdtabellen,
de dekkingstabel en de "Net niet"-tabel komen uit het voortgangsbestand, zodat ze niet kunnen
afwijken van wat de analyse werkelijk heeft gemeten (§5, laatste alinea bij "Net niet").
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

DAY = "2026-09-15"
TMP = Path("tmp-run")

state = json.loads(Path(f"data/run-state/{DAY}-run-b.json").read_text())
res = json.load(open("tmp-run/rb15_results.json"))
odds = json.load(open("tmp-run/rb15_odds.json"))
comps = state["competitions"]

RUNLIJST = [
    "Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
    "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
    "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
    "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
    "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
    "Kategoria Superiore (ALB)", "Kosovo Superleague (KOS)",
]

GEEN_WEDSTRIJD_REDEN = {
    "Hungarian NB I (HUN)": "geen programma dit weekend",
    "English League One (ENG)": "speelronde op zaterdag gespeeld, niets op zondag",
    "English League Two (ENG)": "speelronde op zaterdag gespeeld, niets op zondag",
    "Kosovo Superleague (KOS)": "komt niet voor in de Fotmob-daglijst (ongewijzigd sinds 13 aug 2026)",
}


def blok(naam):
    return TMP.joinpath(naam).read_text().rstrip()


out = []
W = out.append

W(f"# Run B — {DAY}\n")
W("**Gestart:** 05:10 CEST · **Bets gepubliceerd:** 0 · "
  "**Wedstrijden diep geanalyseerd:** 29 van 39 · **Afgekapt:** 0\n")
W("Branch: de sessie startte op `claude/zealous-edison-slai50`, maar alle commits van deze run")
W("staan op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.\n")
W("**Leesbaar dagrapport:** https://claude.ai/code/artifact/7d54d8ab-86d9-466a-9e71-624279e09cfd\n")

# ---------------------------------------------------------------- samenvatting
W("## Samenvatting in één alinea\n")
W(state["parameters"]["toelichting"].split("\n\n")[0] + "\n")

# ---------------------------------------------------------------- Stage -2
W("""## Stage -2 — Branches

De opdracht schrijft de branchcontrole vóór alle andere stappen voor, en die is uitgevoerd vóórdat
deze regels zijn gelezen. `git fetch origin` bracht **30 takken** naast `main` in beeld. De eerste
telling, op de ondiepe kloon waarmee de container start, gaf eenentwintig takken met 4 tot 184
"eigen" commits — precies het valse alarm waar Stage -2 voor waarschuwt. Na
`git fetch --unshallow origin` (109+ commits geschiedenis erbij) staat de teller op **0 van de 30**:
elke tak is volledig in `main` opgenomen.

Om dat niet alleen op commit-niveau te geloven is het ook op inhoud nagetrokken, want dat is waar
de conflictregels van Stage -2 over gaan: van alle dertig takken is `data/picks.jsonl` uitgelezen
en vergeleken met de 274 pick-ids op `main`. **Geen enkele tak bevat een pick die `main` niet
heeft.** Er viel dus niets te verenigen, en er staan ook geen openstaande picks van een run die op
een andere tak nooit is afgewikkeld (`ledger.py open` gaf niets).

De sessie kreeg `claude/zealous-edison-slai50` toegewezen; die tak stond exact gelijk aan `main`.
Er is lokaal naar `main` overgeschakeld en alles is met `git push origin HEAD:main` gepusht.
""")

# ---------------------------------------------------------------- bronstatus
W("## Bronstatus deze run\n")
W("Uitvoer van `python3 scripts/api_check.py`, letterlijk (§3, Stage 3):\n")
W("```")
W(blok("rb15_apicheck.txt"))
W("```\n")
W("""Twee dingen bij het teruglezen van dat blok. De quota-regel hierboven is die van de
**tweede** aanroep, aan het eind van de run: 19.232 over en 768 gebruikt. Bij de eerste aanroep,
vóór de inkoop, stond hij op 19.261 over en 739 gebruikt — het verschil van 29 is precies wat deze
run heeft uitgegeven. En de lijst "relevante sportkeys" is een vaste selectie in `api_check.py` en
geen dekkingsuitspraak: de Griekse, Noorse, Zweedse, Zwitserse en Oostenrijkse sleutels staan er
niet in en leverden deze run wél gewoon events.

**De statistiekensleutel ontbreekt nog steeds.** `API_FOOTBALL_KEY` is niet gezet in de
omgeving van de geplande taak — ontbrekend, niet afgewezen: `api_check.py` slaat de bron over
zonder één HTTP-verzoek te doen. Dat is dezelfde stand als op elke voorgaande rundag en het is
geen nieuwe blokkade, maar het kost wel iets concreets: de vijf competities zonder Fotmob-xG
(Tsjechië, Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) hadden met een werkende
statistiekenbron mogelijk `FULL` kunnen zijn in plaats van `LIGHT`, en dat raakt acht van de
negenentwintig doorgerekende duels. Zie `README.md` → "Sleutels toevoegen".

De oddssleutel werkt: 19.261 credits over van het 20.000-plan, 739 gebruikt deze maand, 48 actieve
voetbalcompetities. Geen enkele bron viel om deze run — Fotmob leverde de daglijst, alle standen en
de context van alle 39 duels zonder één fout, en BetExplorer leverde alle dertien slugs.
""")

# ---------------------------------------------------------------- dekking
W("## Dekkingsrapportage\n")
W("| Competitie | Status | Toelichting |")
W("|---|---|---|")
for naam in RUNLIJST:
    b = comps.get(naam)
    if not b or not b.get("matches"):
        reden = GEEN_WEDSTRIJD_REDEN.get(naam, "niets op de kalender vandaag")
        W(f"| {naam} | `GEEN WEDSTRIJD` | {reden} |")
        continue
    ms = b["matches"]
    n_none = sum(1 for m in ms if m["tier"] == "NONE")
    n_ok = len(ms) - n_none
    if n_ok == 0:
        W(f"| {naam} | `BUITEN DATADEKKING` | {len(ms)} duel(s), alle op `NONE` — "
          f"geen omrekenbare historie in deze divisie |")
    else:
        extra = f"{n_ok} doorgerekend"
        if n_none:
            extra += f", {n_none} op `NONE`"
        tiers = sorted({m["tier"] for m in ms if m["tier"] != "NONE"})
        extra += f" ({', '.join(tiers)})"
        W(f"| {naam} | `GEANALYSEERD` | {extra} |")
W("")
W("""Geen enkele competitie kreeg de status `AFGEKAPT`: met 39 duels tegen een cap van 55 heeft
`MAX_DEEP_ANALYSES` deze run niets gekost. Dat is voor het eerst sinds de cap op 5 september naar
40/55 ging dat een Run B-weekenddag ruim onder de grens blijft — gisteren vielen er nog vier duels
buiten.
""")

# ---------------------------------------------------------------- NONE
W("""## De tien duels op `NONE`, in twee even grote groepen

**Groep 1 — geen gemeten divisiepaar voor dat land, 5 duels.** Hier bestaat de omrekening
helemaal niet: `promotion` kent voor deze landen noch een `TIER1`- noch een `TIER2`-regel, in geen
van beide richtingen.

| Wedstrijd | Ploeg | Waarom er geen factor is |
|---|---|---|
| Kalamata – NFC Volos | Kalamata | geen divisiepaar gemeten voor **Griekenland** |
| NK Istra 1961 – Rudeš | Rudeš | idem voor **Kroatië** |
| Corvinul Hunedoara – Universitatea Craiova | Corvinul Hunedoara | idem voor **Roemenië** |
| Austria Wien – Austria Lustenau | Austria Lustenau | idem voor **Oostenrijk** |
| Laçi – Vllaznia | Laçi | idem voor **Albanië** |

**Groep 2 — de ploeg komt uit een DERDE divisie, 5 duels.** Deze ploegen spelen dit seizoen in de
tweede divisie en zijn dus geen degradant maar een promovendus van onderaf. `promotion` kijkt één
divisie omhoog en één omlaag; een derde niveau kent het niet, en dan komt de omrekening uit op
"staat niet in de stand van de divisie erboven".

| Wedstrijd | Ploeg | Kwam uit |
|---|---|---|
| Sporting Gijón – Eldense | Eldense | Primera Federación (derde niveau ESP) |
| Mallorca – Sabadell | Sabadell | Primera Federación |
| Tenerife – Leganés | Tenerife | Primera Federación |
| Karlsruher SC – Energie Cottbus | Energie Cottbus | 3. Liga (derde niveau GER) |
| VfL Osnabrück – Hertha BSC | VfL Osnabrück | 3. Liga |

Dat is precies openstaand punt 2 van gisteren, nu met vijf duels in plaats van vier en in twee
andere landen. Het is geen toeval en geen regelkwestie: in september zit de tweede divisie vol met
ploegen die uit de derde komen, en zolang er geen gemeten Segunda ↔ Primera Federación- en
2. Bundesliga ↔ 3. Liga-paar is, kost dat elke Run B-dag analyses. Beide zijn met
`promotion.measure_gap` op Fotmob-standen te meten, net zoals op 31 augustus voor zes landen is
gedaan.
""")

# ---------------------------------------------------------------- verplaatsing
W("""## Eén verplaatsing gemeld

`context.check_venue` sloeg vandaag één keer aan, en §1c eist dat die melding in het runrapport
komt ook als de poort opengaat:

> **Kalamata – NFC Volos** wordt niet gespeeld in Dimotiko Stadio Kalamatas maar in **Dimotiko
> Stadio Peristeriou in Athene** — niet het stadion van de uitploeg, dus een neutraal of geleend
> veld.

Thuisvoordeel is de aanname waar het model het zwaarst op leunt, dus dit is het soort melding dat
je wilt zien. Praktisch maakte het vandaag niets uit: dat duel viel hoe dan ook op `NONE`, omdat
Kalamata niet in de Griekse stand van 2025/2026 staat en er voor Griekenland geen omrekenfactor is.
""")

# ---------------------------------------------------------------- bevinding
W("""## De bevinding van de dag: vier selecties die alleen op de herijking sneuvelden

**Vier selecties, verdeeld over twee wedstrijden, haalden alle acht poorten op de ruwe kans.** Geen
van de vier sneuvelde op poort 5 (tweede methode), poort 6 (robuustheid), poort 7 (context) of
poort 8 (underdog); ze waren op de ongecorrigeerde schaal compleet. Zonder de herijking van §1g was
dit dus een dag met twee bets geweest. Ter vergelijking: gisteren waren dat negentien selecties in
acht wedstrijden.

De fit van vanochtend, uit `recalibrate.py show`:

```
""" + blok("rb15_recal.txt") + """
```

Ruim tien procentpunt optimisme, gemeten over 646 afgerekende gevallen. Eén regel per wedstrijd
gaat als schaduwpick naar `data/shadow.jsonl` met `failed_gate = "herijking"`, geboekt op de
**ruwe** schaal zoals §5a eist:

| Wedstrijd | Markt @ koers | Ruwe edge | Herijkt | Ook geblokkeerd |
|---|---|---|---|---|""")
for m in res["matches"]:
    for z in (m.get("zonder_herijking") or []):
        W(f"| {m['match']} | {z['market']} @ {z['odds']} | {z['edge_pp']:+.2f} pp | "
          f"{z['edge_pp_herijkt']:+.2f} pp | {z.get('ook_geblokkeerd') or '—'} |")
W("""
**De reeks die hier wordt opgebouwd staat inmiddels op 38 kandidaten**, waarvan 26 afgewikkeld:
hit rate 46,2%, ROI **−10,4%**. Dat is een omslag ten opzichte van gisteren, toen deze poort op
acht afgewikkelde gevallen nog **+36,0%** stond en daarmee de enige poort met een positief
rendement was. Met 26 gevallen zit de reeks nu net onder de ~30 die §6d als ondergrens noemt, en
precies dit is waarom die ondergrens er staat: achttien nieuwe waarnemingen draaiden het teken om.
**Er is vandaag niets aan de herijking of aan de drempel veranderd**, en dat hoort ook niet op één
dag te gebeuren — maar de eerstvolgende keer dat deze reeks boven de dertig komt is ze voor het
eerst leesbaar.
""")

# ---------------------------------------------------------------- wedstrijden
W("## Wedstrijden\n")
W("Negenentwintig doorgerekende duels, geen enkele bet. De volledige selectielijst per duel staat")
W(f"in `data/run-state/{DAY}-run-b.json` onder `all_candidates`; hieronder per wedstrijd het label,")
W("de sterkste kandidaat en de poort waarop hij sneuvelde.\n")
for naam in RUNLIJST:
    blokje = comps.get(naam)
    if not blokje or not blokje.get("matches"):
        continue
    W(f"### {naam}\n")
    W("| Wedstrijd | Aftrap | Data | Sterkste kandidaat | Edge | Valt af op |")
    W("|---|---|---|---|---|---|")
    for m in blokje["matches"]:
        if m["tier"] == "NONE":
            W(f"| {m['match']} | {m['kickoff_nl']} | NONE | — | — | "
              f"**GEEN BET** — {m.get('reden', '')} |")
            continue
        cands = m.get("all_candidates") or []
        if not cands:
            W(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | — | — | "
              f"**GEEN BET** — {m.get('reden', '')} |")
            continue
        b = max(cands, key=lambda r: r["edge_pp"])
        W(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | "
          f"{b['market']} — {b['selection']} @ {b['odds']} | {b['edge_pp']:+.2f} pp | "
          f"{b['failed_gate']} |")
    W("")

# ---------------------------------------------------------------- topselectie
W("""## Topselectie

**Geen enkele.** Nul bets, dus er is niets te rangschikken. Dat is een volwaardige uitkomst (§1),
en de twee ranglijsten hieronder laten zien wat er dan wél bovenaan stond.

Uitvoer van `python3 scripts/toplist.py --run b --date 2026-09-15`:

```
""" + blok("rb15_top.txt") + """
```
""")

# ---------------------------------------------------------------- net niet
W("""### Net niet

Twee kandidaten met een echte edge die het niet haalden, met het cijfer per poort:

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|""")
for m in res["matches"]:
    nm = m.get("near_miss")
    if nm:
        W(f"| {m['match']} | {nm['market']} @ {nm['odds']} | {nm['edge_xg']:+.2f} pp | "
          f"{nm['edge_split']:+.2f} pp | {nm['edge_robust_min']:+.2f} pp | {nm['failed_gate']} |")
W("""
Allebei wijzen ze dezelfde kant op, en het is dezelfde richting als de bevinding hierboven: een
ruime edge op het ongecorrigeerde model — bij Hammarby +19 pp op beide methodes, met een zwakste
stand van het (shrink, rho)-grid van +14,43 — die na de correctie onder de drempel uitkomt.

De verdeling van alle 325 selecties over de poort waarop ze als eerste sneuvelden:

| | herijkte schaal | ruwe schaal |
|---|---|---|
| edge onder de drempel | 308 | 298 |
| koers buiten de band | 13 | 13 |
| poort 5 — twee methodes tegengesteld | 0 | 2 |
| poort 8 — underdog onder de ondergrens | 0 | 8 |
| alleen de herijking (§1g) | 4 | — |
| niets tegengekomen | 0 | 4 |

Dat poort 7 en poort 8 op de herijkte schaal geen enkele selectie als eerste tegenhouden is precies
wat §1e voorspelde toen poort 8 op 5 september werd verlicht: de herijking pakt de oorzaak aan waar
die poort een symptoom van afdekte, dus er komen vanzelf veel minder underdog-selecties tot aan
die poort.
""")

# ---------------------------------------------------------------- marktbalans
W("## Marktbalans (§1a — controle op de inkoop, niet op de uitkomst)\n")
W("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
W("|---|---|---|---|")
W("| 1X2 | 13 van 13 (8× beste prijs uit de h2h-bulk, 5× BetExplorer-marktgemiddelde) | 86 | 0 |")
W("| Asian Handicap | 8 van 13 (in de bulk, 1 credit per competitie) | 81 | 0 |")
W("| Draw No Bet (de 0.0-lijn) | 8 van 13 (zit in diezelfde spreads) | 27 | 0 |")
W("| Double Chance (de ±0.5-lijn) | 5 van 13 (idem, waar die lijn genoteerd stond) | 9 | 0 |")
W("| Over/Under | 8 van 13 (in dezelfde bulk) | 112 | 0 |")
W("| BTTS | 3 van 13 — 5 wedstrijden à 1 credit, tweede ronde | 10 | 0 |")
W("")
W(state["credits"]["marktbalans"])
W("")
W("Uitvoer van `guard.report()` over de bulk-aanroepen, plus de tweede ronde:\n")
W("```")
W(odds["guard"])
W(odds.get("guard_totaal", ""))
W("```\n")
W(state["credits"]["bron"])
W("""

**De beste prijs tegenover het marktgemiddelde.** Over de eenentwintig duels waar beide bekend zijn
lag de beste prijs gemiddeld **+7,74%** boven het BetExplorer-gemiddelde, mediaan **+6,03%**, met
+16,19% als hoogste. Dat ligt netjes in lijn met de +7,78% / +6,07% die §1a op 5 september mat, en
het is de reden dat de h2h-bulk sinds die datum wordt gekocht: bijna twee procentpunt edge zonder
één regel aan het model te veranderen.
""")

# ---------------------------------------------------------------- vroeg seizoen
W("## Vroeg-seizoenscorrectie\n")
W(state["vroeg_seizoen"]["noot"])
W("")
W("""**Gemeten tegen de markt, als controle en niet als afregeling** (§3 Stage 5 staat dat
uitdrukkelijk toe: "meten tegen de markt om te zien of de correctie werkt mag wel — dat is
controleren, niet fitten"). Over de negenentwintig doorgerekende duels tilt de correctie
P(Over 2.5) gemiddeld van 45,7% naar 49,9%, en het kalibratieblok van §6e laat zien waar het model
daarna staat: op doelpuntenmarkten is de afwijking ten opzichte van de de-vigde marktkans klein en
zonder duidelijk teken. De correctie doet dus wat ze hoort te doen — ze haalt een systematisch
tekort weg — en ze schiet niet door.
""")

# ---------------------------------------------------------------- contextlogboek
W("""## Contextlogboek

`ctxlog.py collect` legde **30 van de 39** duels vast. De negen die wegvielen hebben dezelfde
oorzaak als op 12 september: **Fotmob geeft voor een deel van de kleinere clubs
`totalStarterMarketValue` = 0**, en zonder selectiewaarde kan `ctxlog.out_share` het aandeel
ontbrekende spelers niet uitrekenen — `out / (basis + out)` heeft een noemer nodig. Het raakte
vandaag beide Kroatische duels, beide Albanese, alle drie de Oostenrijkse en twee Zwitserse.

**Dit raakt de analyse niet.** Poort 7 staat bij ontbrekende data gewoon open (§1c: een meting die
er niet is, is geen bewijs van een probleem) en de datarijkdom-score geeft een ontbrekende meting
het middenpunt en nooit nul. Wat het wél raakt is het tempo van de meting die §1c plant.

```
""" + blok("rb15_ctxstats.txt") + """
```

Let op wat er sinds gisteren is veranderd: de helling staat nu op **−32,4 pp per eenheid met
t = −2,23** over 414 wedstrijden, tegen −21,7 pp en t = −1,26 gisteren. Dat is voor het eerst een
teken dat de drempel van t = 2 haalt. §1c is daar expliciet over hoe je dit moet lezen: met 462
wedstrijden is pas een effect vanaf ~28 pp aantoonbaar, en de gemeten helling ligt daar nét boven —
dus dit is het soort waarneming dat over twee weken bevestigd of weggeruisd is, geen aanleiding om
poort 7 vandaag van rem naar bijstelling te promoveren. De markt vertoont bovendien vrijwel
dezelfde helling (−34,0 pp, t = −2,38), en dat is een aanwijzing dat beide dezelfde ontbrekende
informatie missen in plaats van dat het model iets ziet wat de markt niet ziet.
""")

# ---------------------------------------------------------------- afwikkeling
W("""## Afwikkeling vorige picks

**Geen.** `ledger.py open` gaf niets: er staat geen enkele echte pick open — het logboek telt 274
picks, alle 274 afgewikkeld. `shadow.py open` gaf elf openstaande schaduwpicks, alle elf van Run A
van vanochtend en alle elf van wedstrijden die vandaag nog gespeeld moeten worden ("bron meldt nog
niet afgelopen"). Er viel dus niets af te wikkelen, wat de normale stand is voor een run die om
05:10 draait op een dag waarvan de wedstrijden nog moeten beginnen.

Deze run voegt vier schaduwregels toe: twee `near_miss` en twee `zonder_herijking`. Die vallen
niet samen — de near miss van Hammarby is de Asian Handicap, de `zonder_herijking`-rij van dat duel
is de Under 3.5, en §5a boekt per wedstrijd één rij per categorie.
""")

# ---------------------------------------------------------------- logboek
W("## Stand van het logboek\n")
W("Uitvoer van `python3 scripts/ledger.py stats` — dit is wat er wél door de poorten kwam:\n")
W("```")
W(blok("rb15_ledger.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/shadow.py stats` — dit is wat er is tegengehouden:\n")
W("```")
W(blok("rb15_shadow.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/calibration.py stats` (§6e):\n")
W("```")
W(blok("rb15_calib.txt"))
W("```\n")

# ---------------------------------------------------------------- openstaand
W("""## Openstaand

1. **`viel af op: herijking` is van +36,0% naar −10,4% gedraaid.** Gisteren stond deze poort op
   acht afgewikkelde gevallen als enige op een positief rendement en noteerde Run B dat als punt 1
   van deze lijst. Vandaag staat ze op 26 afgewikkelde gevallen en op −10,4%. Dat is geen nieuwe
   bevinding maar een demonstratie van §6d: onder ~30 gevallen is elk getal ruis. **Kijk hier over
   twee weken opnieuw naar**, wanneer de reeks ruim boven de dertig staat, en verander tot die tijd
   niets.
2. **Er is geen omrekening voor een derde divisie.** Vijf duels vielen vandaag op `NONE` omdat
   Eldense, Sabadell, Tenerife, Energie Cottbus en VfL Osnabrück uit de Primera Federación
   respectievelijk de 3. Liga komen. Dit stond gisteren ook op de lijst (toen: Serie C en National
   League) en het is structureel Run B-werk: de tweede divisies van deze runlijst zitten er vol
   mee. Een gemeten Segunda ↔ Primera Federación- en 2. Bundesliga ↔ 3. Liga-paar zou dit wegnemen.
3. **Vijf landen hebben helemaal geen divisiepaar.** Griekenland, Kroatië, Roemenië, Oostenrijk en
   Albanië kosten vandaag samen vijf duels, en dat herhaalt zich elke keer dat daar een promovendus
   of degradant speelt. Zelfde werk als punt 2, kan in dezelfde meting mee.
4. **Fotmob geeft voor kleine clubs geen selectiewaarde.** Negen van de negenendertig duels vallen
   daardoor buiten het contextlogboek — vandaag vooral Kroatië, Oostenrijk, Zwitserland en Albanië.
   Dit stond gisteren op dezelfde lijst met dertien van de negenenvijftig; het is dus een stabiel
   aandeel van ongeveer een kwart en het vertraagt de meting van §1c precies bij de competities
   waar deze routine het meest te leren heeft.
5. **Het contextlogboek haalt voor het eerst t = −2,23.** Zie de sectie hierboven. Niet naar
   handelen, wel volgen: als dit teken over twee weken standhoudt is het de eerste keer dat er iets
   over de omvang van het blessure-effect te zeggen valt.
6. **Run A van vanochtend noteert BTTS verkeerd in `markets_checked`.** Sinds vandaag koopt de
   routine BTTS in een tweede ronde (§1a stap 2), en voor de duels die dan géén kandidaat-edge
   tonen wordt de markt niet opgevraagd. `ra13_analyze.py` schrijft daar nog "btts opgevraagd, maar
   geen boek noteerde deze markt" — dat is precies het onderscheid dat §6b-5b wil kunnen zien. In
   `rb15_analyze.py` is het vandaag gerepareerd (met de reden en het onbenutte plafond erbij); de
   volgende Run A hoort dezelfde reparatie over te nemen.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
""")

Path(f"runs/{DAY}-run-b.md").write_text("\n".join(out))
print(f"runs/{DAY}-run-b.md geschreven — {len(out)} blokken")
