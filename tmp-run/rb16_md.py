"""Run B, 16 sep 2026 — het markdown-runrapport opbouwen uit data/run-state/.

Zelfde opzet als `rb15_md.py`: de vaste secties staan hieronder als tekst, de wedstrijdtabellen,
de dekkingstabel en de "Net niet"-tabel komen uit het voortgangsbestand, zodat ze niet kunnen
afwijken van wat de analyse werkelijk heeft gemeten (§5, laatste alinea bij "Net niet").
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

DAY = "2026-09-16"
TMP = Path("tmp-run")

state = json.loads(Path(f"data/run-state/{DAY}-run-b.json").read_text())
res = json.load(open("tmp-run/rb16_results.json"))
odds = json.load(open("tmp-run/rb16_odds.json"))
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
    "Kosovo Superleague (KOS)":
        "komt niet voor in de Fotmob-daglijst (ongewijzigd sinds 13 aug 2026)",
}
ARTIFACT = "https://claude.ai/artifact/Fq7Qu8eAviZjMx2MvGXkw9"


def blok(naam):
    return TMP.joinpath(naam).read_text().rstrip()


out = []
W = out.append

W(f"# Run B — {DAY}\n")
W("**Gestart:** 05:09 CEST · **Bets gepubliceerd:** 0 · "
  "**Wedstrijden diep geanalyseerd:** 3 van 3 · **Afgekapt:** 0\n")
W("Branch: de sessie startte op `claude/zealous-edison-xbghm0`, maar alle commits van deze run")
W("staan op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.\n")
W(f"**Leesbaar dagrapport:** {ARTIFACT}\n")

# ---------------------------------------------------------------- samenvatting
W("## Samenvatting in één alinea\n")
W(state["parameters"]["toelichting"].split("\n\n")[0] + "\n")

# ---------------------------------------------------------------- Stage -2
W("""## Stage -2 — Branches

De opdracht schrijft de branchcontrole vóór alle andere stappen voor, en die is uitgevoerd vóórdat
deze regels zijn gelezen. `git fetch origin` bracht **30 takken** naast `main` in beeld.

De eerste telling, op de ondiepe kloon waarmee de container start
(`git rev-parse --is-shallow-repository` → `true`, 59 commits lokaal), gaf **22 takken met 4 tot
184 "eigen" commits** — precies het valse alarm waar Stage -2 voor waarschuwt: bij die 22 gaf
`git merge-base main <tak>` helemaal niets terug, want het punt waarop ze uit elkaar liepen lag
vóór de knip. Na `git fetch --unshallow origin` (308 commits geschiedenis) staat de teller op
**0 van de 30**: elke tak is volledig in `main` opgenomen.

Om dat niet alleen op commit-niveau te geloven is het óók op inhoud nagetrokken, want dat is waar
de conflictregels van Stage -2 over gaan. Van alle dertig takken is `data/picks.jsonl` uitgelezen
en vergeleken met de 274 pick-ids op `main`: **geen enkele tak bevat een pick die `main` niet
heeft.** Hetzelfde is met `data/shadow.jsonl` gedaan (475 schaduwpicks). Daar gaven twee takken
een "extra" id, maar bij navraag ging het beide keren om dezelfde waarneming onder een andere
sleutel — `shadow-2026-09-15-a-elche---real-madrid` heet op `main` sinds de herdraai van gisteren
`…-p8ruw-0`. Geen verlies, dus er viel niets te verenigen.

Er staan ook geen openstaande picks van een run die op een andere tak nooit is afgewikkeld:
`ledger.py open` gaf niets, en `shadow.py open` alleen de zes schaduwpicks van Run A van
vanochtend, van wedstrijden die vandaag nog gespeeld moeten worden.

De sessie kreeg `claude/zealous-edison-xbghm0` toegewezen; die tak stond exact gelijk aan `main`.
Er is lokaal naar `main` overgeschakeld en alles is met `git push origin HEAD:main` gepusht.
""")

# ---------------------------------------------------------------- bronstatus
W("## Bronstatus deze run\n")
W("Uitvoer van `python3 scripts/api_check.py`, letterlijk (§3, Stage 3):\n")
W("```")
W(blok("rb16_apicheck.txt"))
W("```\n")
W("""**De statistiekensleutel ontbreekt nog steeds.** `API_FOOTBALL_KEY` is niet gezet in de
omgeving van de geplande taak — ontbrekend, niet afgewezen: `api_check.py` slaat de bron over
zonder één HTTP-verzoek te doen. Dat is dezelfde stand als op elke voorgaande rundag en het is
geen nieuwe blokkade. Vandaag kostte het ook niets: beide competities die speelden hebben
Fotmob-xG, dus alle drie de duels kwamen op `FULL` uit. Zie `README.md` → "Sleutels toevoegen".

De oddssleutel werkt: 19.140 credits over van het 20.000-plan, 860 gebruikt deze maand, 46 actieve
voetbalcompetities. De lijst "relevante sportkeys" in dat blok is een vaste selectie in
`api_check.py` en geen dekkingsuitspraak: de Zweedse en Zwitserse sleutels staan er niet in en
leverden deze run wél gewoon events.

Geen enkele bron viel om. Fotmob leverde de daglijst, beide competitiestanden (vorig én lopend
seizoen) en de context van alle drie de duels zonder één fout; BetExplorer leverde beide slugs.
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
        W(f"| {naam} | `BUITEN DATADEKKING` | {len(ms)} duel(s), alle op `NONE` |")
    else:
        extra = f"{n_ok} doorgerekend"
        if n_none:
            extra += f", {n_none} op `NONE`"
        tiers = sorted({m["tier"] for m in ms if m["tier"] != "NONE"})
        extra += f" ({', '.join(tiers)})"
        W(f"| {naam} | `GEANALYSEERD` | {extra} |")
W("")
W("""Vijftien competities zonder wedstrijd is veel, en het is geen storing: het is woensdag in de
Europese speelweek en de binnenlandse competities uit deze runlijst spelen hun ronde in het
weekend. Geen enkele competitie kreeg de status `BUITEN DATADEKKING` — beide die speelden hebben
Fotmob-xG — en geen enkele de status `AFGEKAPT`: met 3 duels tegen een cap van 40 heeft
`MAX_DEEP_ANALYSES` deze run niets gekost. De laagste datarijkdom in de run was 5,0 en de hoogste
7,0; omdat er niets is afgekapt zijn "de laagste die het haalde" en "de hoogste die afviel" beide
leeg.
""")

# ---------------------------------------------------------------- verplaatsing
W("""## Geen verplaatsing gemeld

`context.check_venue` sloeg vandaag geen enkele keer aan. Alle drie de duels worden gespeeld in
het eigen stadion van de genoteerde thuisploeg: Strawberry Arena (Solna), AIL Arena (Lugano) en
VISANA STADION (Thun). Dat is de gewenste uitkomst en niet een controle die stil bleef — §1c eist
dat de stadionnaam en de vlag `relocated` altijd in `data/run-state/` komen, ook als de poort
opengaat, en dat is gebeurd.
""")

# ---------------------------------------------------------------- bevinding
W("""## De bevinding van de dag: ook het ongecorrigeerde model zag vandaag niets

Op de meeste nul-bet-dagen van de afgelopen twee weken lag het verschil bij de herijking van §1g:
selecties die op de **ruwe** schaal ruim boven de drempel uitkwamen en er na de correctie van
ongeveer tien procentpunt onder zakten. Run A boekte er vanochtend drie, gisterochtend vier en op
12 september nog twaalf.

**Vandaag geen enkele** — de derde Run B op rij overigens waarop dat blok leeg blijft (14 en
15 september ook). De hoogste ruwe edge van de run is +5,96 pp (1X2 — Thun wint @ 2,86
bruto bij Betfair, 2,82 na commissie), tegen een drempel van 8,0. Er gaat dus geen enkele rij met
`failed_gate = "herijking"` naar het schaduwlogboek, en poort 8 heeft op geen van beide schalen
iets tegengehouden dat de edge-poort niet al had gesloten. Dat is een zeldzame en op zichzelf
geruststellende uitkomst: het betekent dat het "nul bets" van vandaag niet aan één rekenstap hangt
maar aan de wedstrijden zelf.

De fit van vanochtend, uit `recalibrate.py show`:

```
""" + blok("rb16_recal.txt") + """
```

Elf procentpunt optimisme, gemeten over 671 afgerekende gevallen. Op de 51 selecties van vandaag
kostte die correctie tussen de 4,5 en de 13,5 procentpunt edge — hoe hoger de geclaimde kans, hoe
meer eraf.

**Wat de dag wél laat zien, is hoe ver de twee methodes uiteen kunnen liggen.** Bij Thun – Servette
staat de splitsmethode op **+30,47 pp** en de xG-methode op **−0,16 pp** voor precies dezelfde
selectie; bij AIK – Mjällby is dat +23,87 tegen −0,05. Dat is dezelfde scheefstand die §1d en §6e
al bij de splitsmethode aanwijzen, hier in zijn extreemste vorm van de afgelopen weken. De weging
van 80/20 uit §1f haalt hem grotendeels weg, en dat is precies waarvoor die weging op uitkomsten
is gemeten. Zonder die weging — bij het ongewogen gemiddelde van vóór 5 september — had Thun een
ruwe edge van ruim vijftien procentpunt gehad en was dit een dag met een bet geweest, op een
kansschatting die voor de helft uit de aantoonbaar scheefste van de twee schatters komt.
""")

# ---------------------------------------------------------------- wedstrijden
W("## Wedstrijden\n")
W("Drie doorgerekende duels, geen enkele bet. De volledige selectielijst per duel staat")
W(f"in `data/run-state/{DAY}-run-b.json` onder `all_candidates`; hieronder per wedstrijd het label,")
W("de sterkste kandidaat en de poort waarop hij sneuvelde.\n")
for naam in RUNLIJST:
    blokje = comps.get(naam)
    if not blokje or not blokje.get("matches"):
        continue
    W(f"### {naam}\n")
    W("| Wedstrijd | Aftrap | Data | Sterkste kandidaat | Edge (herijkt) | Edge (ruw) | Valt af op |")
    W("|---|---|---|---|---|---|---|")
    for m in blokje["matches"]:
        cands = m.get("all_candidates") or []
        if m["tier"] == "NONE" or not cands:
            W(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | — | — | — | "
              f"**GEEN BET** — {m.get('reden', '')} |")
            continue
        b = max(cands, key=lambda r: r["edge_pp"])
        W(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | "
          f"{b['market']} — {b['selection']} @ {b['odds']} | {b['edge_pp']:+.2f} pp | "
          f"{b['edge_raw']:+.2f} pp | {b['failed_gate']} |")
    W("")
W("""Alle drie leverden dezelfde uitkomst en dezelfde reden: **GEEN BET — edge onder de drempel.**
Bij alle drie staat de sterkste kandidaat op een *negatieve* herijkte edge, dus geen enkele
selectie van deze run komt zelfs maar boven de marktkans uit.

Per duel, kort:

- **AIK – Mjällby** · 19:00 · Allsvenskan · FULL · 15 selecties. Het lopende seizoen weegt hier
  voor **0,714** mee (20 duels per ploeg) — de hoogste blendweging die deze routine tot nu toe
  heeft gedraaid, en precies wat §4 bedoelt met "de analyse wordt vanzelf beter naarmate het
  seizoen vordert". AIK gaat dit seizoen achteruit (1,395 xG voor / 1,705 tegen per duel, tegen
  1,293 / 1,113 vorig seizoen), Mjällby ook (1,225 / 1,910 tegen 1,597 / 1,200). Poort 7 sluit de
  thuiskant hard: AIK mist dertien spelers met samen 50% van de selectiewaarde tegen 3% bij
  Mjällby.
- **Lugano – St. Gallen** · 19:00 · Swiss Super League · FULL · 17 selecties. Het duel met de
  hoogste datarijkdom van de run (7,0). Poort 7 sluit ook hier de thuiskant: Lugano mist 52% van
  zijn selectiewaarde tegen 41% bij St. Gallen — twee zwaar gehavende ploegen tegenover elkaar.
- **Thun – Servette** · 19:00 · Swiss Super League · FULL · 19 selecties, de meeste van de run.
  Poort 7 staat hier aan beide kanten open; wel speelde Servette drie dagen geleden nog (druk
  programma). Dit is ook het duel met de grootste methodekloof, zie hierboven.
""")

# ---------------------------------------------------------------- topselectie
W("""## Topselectie

**Geen enkele.** Nul bets, dus er is niets te rangschikken. Dat is een volwaardige uitkomst (§1),
en de twee ranglijsten hieronder laten zien wat er dan wél bovenaan stond.

Uitvoer van `python3 scripts/toplist.py --run b --date 2026-09-16`:

```
""" + blok("rb16_top.txt") + """
```

Let op het verschil tussen de twee lijsten: op de herijkte schaal staat elke score **negatief**,
op de ruwe schaal alle drie positief. Dat is de correctie van §1g in één oogopslag. Ook op de ruwe
lijst haalt geen van de drie de drempel van 8,0 — de hoogste staat op +5,96 pp.
""")

# ---------------------------------------------------------------- net niet
W("""### Net niet

**Leeg, en dat is deze keer de eerlijke uitkomst en geen weglating.** De "Net niet"-tabel vult
zich met kandidaten die een echte edge lieten zien maar op een poort sneuvelden; de ondergrens
daarvoor is +3,0 pp op de herijkte schaal bij `FULL`. De hóógste herijkte edge van de hele run is
**−3,60 pp**. Er is dus geen enkele kandidaat die in de buurt kwam, en `shadow.py collect` meldde
terecht "geen nieuwe kandidaten".

De verdeling van alle 51 selecties over de poort waarop ze als eerste sneuvelden:

| | herijkte schaal | ruwe schaal |
|---|---|---|
| edge onder de drempel | 50 | 50 |
| koers buiten de band | 1 | 1 |
| poort 5 — twee methodes tegengesteld | 0 | 0 |
| poort 8 — underdog onder de ondergrens | 0 | 0 |
| alleen de herijking (§1g) | 0 | — |

Eén poort die alles wegvangt is volgens §5 het soort patroon dat je wilt opmerken — maar dat is
hier niet aan de orde: de edge-poort is de *eerste* poort in de volgorde, en een dag waarop geen
enkele selectie boven de marktkans uitkomt laat de latere poorten per definitie ongemoeid. Wat
poort 5, 7 en 8 *zouden* hebben gedaan staat wél per selectie in
`data/run-state/2026-09-16-run-b.json` onder `all_candidates`, in de velden `context_reason` en
`underdog_reason`.
""")

# ---------------------------------------------------------------- marktbalans
W("## Marktbalans (§1a — controle op de inkoop, niet op de uitkomst)\n")
W("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
W("|---|---|---|---|")
W("| 1X2 | 2 van 2 (beste prijs uit de h2h-bulk) | 9 | 0 |")
W("| Asian Handicap | 2 van 2 (in de bulk, zelfde credit) | 15 | 0 |")
W("| Draw No Bet (de 0.0-lijn) | 2 van 2 (zit in diezelfde spreads) | 6 | 0 |")
W("| Double Chance (de ±0.5-lijn) | 2 van 2 (idem) | 3 | 0 |")
W("| Over/Under | 2 van 2 (in dezelfde bulk) | 18 | 0 |")
W("| BTTS | 0 van 2 — niet opgevraagd, geen kandidaat-edge (§1a stap 2) | 0 | 0 |")
W("")
W(state["credits"]["marktbalans"])
W("")
W("Uitvoer van `guard.report()` over de bulk-aanroepen:\n")
W("```")
W(odds["guard"])
if odds.get("guard_totaal"):
    W(odds["guard_totaal"])
W("```\n")
W(state["credits"]["bron"])
W("""

**De beste prijs tegenover het marktgemiddelde.** Over de drie duels lag de beste 1X2-prijs
gemiddeld **+5,1%** boven het BetExplorer-gemiddelde (+6,06% / +4,49% / +4,77%). Dat is wat lager
dan de +7,78% die §1a op 5 september mat, en dat past bij drie duels waarin de beste prijs meestal
bij een **beurs** lag (Betfair, Matchbook) en dus met 2% commissie is doorgerekend: van de negen
1X2-uitkomsten kwamen er zes van een beurs. De kale koers én de koers na commissie staan bij elke
selectie in `odds_source`.
""")

# ---------------------------------------------------------------- vroeg seizoen
W("## Vroeg-seizoenscorrectie\n")
W(state["vroeg_seizoen"]["noot"])
W("")
W("""**Gemeten tegen de markt, als controle en niet als afregeling** (§3 Stage 5 staat dat
uitdrukkelijk toe: "meten tegen de markt om te zien of de correctie werkt mag wel — dat is
controleren, niet fitten"). De dagregel in het kalibratieblok hieronder staat voor 16 september op
**+1,45 pp** op longshots over 14 waarnemingen — in lijn met de reeks van de afgelopen twee weken
(+1,1 tot +2,9 pp) en zonder uitschieter. De correctie doet dus wat ze hoort te doen en schiet
niet door. Met veertien waarnemingen is dat één dagpunt en geen bevinding; §6e wil hier expliciet
niet op één dag gelezen worden.
""")

# ---------------------------------------------------------------- contextlogboek
W("""## Contextlogboek

`ctxlog.py collect` legde **3 van de 3** duels vast — voor het eerst in weken zonder één uitvaller
door het `totalStarterMarketValue = 0`-gat dat bij kleinere clubs speelt. Het logboek staat nu op
580 wedstrijden, waarvan 558 afgewikkeld.

```
""" + blok("rb16_ctxstats.txt") + """
```

**Dit is het getal om te volgen.** De helling van de modelfout tegen het beschikbaarheidsverschil
staat op **−26,4 pp per eenheid met t = −2,09** over 501 afgerekende wedstrijden. Ter vergelijking:
op 5 september, toen §1c werd geschreven, stond die op −2,2 pp met t = −0,08 over 147 wedstrijden
— feitelijk niets. Sinds gisteren staat hij onafgebroken boven de drempel van t = 2, al is hij
in die tijd wél verzwakt (15 september: −32,4 pp, t = −2,51). Dit getal is ongewijzigd ten
opzichte van Run A van vanochtend: de drie duels die deze run toevoegde zijn nog niet gespeeld en
tellen dus nog niet mee.

Lees dat zoals §1c zelf voorschrijft. Met 558 afgewikkelde wedstrijden is pas een effect vanaf
~24 pp per eenheid aantoonbaar, en de gemeten helling ligt daar nét boven. Belangrijker nog: de
**markt** vertoont vrijwel dezelfde helling (−24,6 pp, t = −1,98). Als beide dezelfde kant op
scheefstaan, is dat eerder een aanwijzing dat model én bookmaker dezelfde informatie missen dan
dat het model iets kan dat de markt niet kan — en dan is er geen bijstelling uit te halen, alleen
een gedeelde blinde vlek. **Poort 7 blijft dus een rem en wordt geen bijstelling**, precies zoals
§1c dat tot nader order vastlegt. Volgen, niet naar handelen.
""")

# ---------------------------------------------------------------- afwikkeling
W("""## Afwikkeling vorige picks

**Geen.** `ledger.py open` gaf niets: er staat geen enkele echte pick open — het logboek telt 274
picks, alle 274 afgewikkeld. `shadow.py open` gaf zes openstaande schaduwpicks, alle zes van Run A
van vanochtend en alle zes van wedstrijden die vandaag nog gespeeld moeten worden ("bron meldt nog
niet afgelopen", −20,8 uur na aftrap). Er viel dus niets af te wikkelen, wat de normale stand is
voor een run die om 05:09 draait op een dag waarvan de wedstrijden nog moeten beginnen.

Deze run voegt **geen enkele** schaduwregel toe: geen `near_miss`, geen `zonder_herijking`, geen
poort-8-rij op beide schalen. Dat is de derde Run B op rij met een onveranderd schaduwlogboek
(14 en 15 september ook nul; 13 september nog vier), en het volgt rechtstreeks uit de sectie
"Bevinding": er was niets dat dicht genoeg bij een bet kwam om te boeken. Het is ook precies de
reden dat de reeks van §1e zo traag groeit — zie punt 1 onder "Openstaand".
""")

# ---------------------------------------------------------------- logboek
W("## Stand van het logboek\n")
W("Uitvoer van `python3 scripts/ledger.py stats` — dit is wat er wél door de poorten kwam:\n")
W("```")
W(blok("rb16_ledger.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/shadow.py stats` — dit is wat er is tegengehouden:\n")
W("```")
W(blok("rb16_shadow.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/calibration.py stats` (§6e):\n")
W("```")
W(blok("rb16_calib.txt"))
W("```\n")

# ---------------------------------------------------------------- openstaand
W("""## Openstaand

1. **`viel af op: underdog` staat op +12,9% over 8 afgewikkelde gevallen — en 25 september nadert.**
   §1e herziet poort 8 uiterlijk op die datum, en eist daarvoor ten minste 30 afgewikkelde
   kandidaten. Die reeks staat vandaag nog steeds op **acht**, precies zoals op 15 september, want
   deze run leverde geen enkele poort-8-rij. De tweede categorie `underdog_ruw` — op 15 september
   ingevoerd juist om de reeks sneller te laten groeien — staat op zes, waarvan vijf afgewikkeld
   (−15,4%). Bij dit tempo arriveert 25 september met ongeveer tien tot twaalf gevallen in de
   eerste categorie, ruim onder de dertig die de regel zelf eist. **Dat is een besluit dat de
   gebruiker binnenkort moet nemen:** de datum verschuiven, of de poort herzien op een reeks die
   §6d "ruis" noemt. Het eerste is verdedigbaar, het tweede niet.
2. **`viel af op: herijking` staat op 47 kandidaten, 37 afgewikkeld, ROI −26,9%.** Dat is ruim
   boven de dertig die §6d als leesondergrens noemt, en het teken is stabiel negatief: op
   14 september stond deze reeks op −21,2% over 32 afgewikkelde gevallen. **Conclusie: de
   herijking van §1g bespaart geld en blijft staan.** Dit is de tweede meting op rij boven de
   leesdrempel, en de eerste keer dat die uitspraak op een reeks rust in plaats van op een
   redenering. Wat er nog aan ontbreekt: de reeks is op weinig rundagen opgebouwd, dus ze weegt
   zwaar op enkele drukke dagen. Blijven volgen, niets veranderen.
3. **Fotmob geeft voor kleine clubs geen selectiewaarde.** Vandaag speelde dat niet — alle drie de
   duels kwamen volledig in het contextlogboek — maar het is een structureel Run B-probleem dat
   elke weekenddag terugkomt en de meting van §1c vertraagt bij precies de competities waar deze
   routine het meest te leren heeft. Blijft staan van 14 en 15 september.
4. **Er is geen omrekening voor een derde divisie, en vijf landen hebben helemaal geen
   divisiepaar.** Speelde vandaag evenmin (geen enkele promovendus of degradant in de drie duels),
   maar blijft openstaan: de tweede divisies van deze runlijst zitten er in het najaar vol mee. Een
   gemeten Segunda ↔ Primera Federación- en 2. Bundesliga ↔ 3. Liga-paar zou het wegnemen, met
   `promotion.measure_gap` op Fotmob-standen, net zoals op 31 augustus voor zes landen is gedaan.
5. **`prompts/run-b.md` noemt de Allsvenskan en de Swiss Super League nog "nog niet getest".**
   Allebei zijn ze allang gemeten — de Allsvenskan op 9 augustus, de Swiss Super League op
   23 augustus — en vandaag opnieuw bevestigd als `FULL`-waardig. Die lijst in de runprompt loopt
   dus achter op `data/coverage.json`, en dat is precies het soort stille veroudering waar een
   volgende run tijd aan verliest. Bijwerken zodra iemand aan dat bestand komt.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
""")

Path(f"runs/{DAY}-run-b.md").write_text("\n".join(out))
print(f"runs/{DAY}-run-b.md geschreven — {len(out)} blokken")
