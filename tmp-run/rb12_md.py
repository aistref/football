"""Run B, 12 sep 2026 — het markdown-runrapport opbouwen uit data/run-state/.

De vaste secties staan hieronder als tekst; de wedstrijdtabellen, de dekkingstabel en de
"Net niet"-tabel komen uit het voortgangsbestand, zodat ze niet kunnen afwijken van wat de
analyse werkelijk heeft gemeten (§5, laatste alinea bij "Net niet").
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

DAY = "2026-09-12"
SCRATCH = Path("/tmp/claude-0/-home-user-football/2d250b5e-0590-532f-b605-9b691704f6b5/scratchpad")

state = json.loads(Path(f"data/run-state/{DAY}-run-b.json").read_text())
res = json.load(open("tmp-run/rb12_results.json"))
odds = json.load(open("tmp-run/rb12_odds.json"))
comps = state["competitions"]

RUNLIJST = [
    "Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
    "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
    "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
    "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
    "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
    "Kategoria Superiore (ALB)", "Kosovo Superleague (KOS)",
]

def blok(naam):
    return SCRATCH.joinpath(naam).read_text().rstrip()

out = []
W = out.append

W(f"# Run B — {DAY}\n")
W("**Gestart:** 05:10 CEST · **Bets gepubliceerd:** 0 · "
  "**Wedstrijden diep geanalyseerd:** 45 van 59 · **Afgekapt:** 4\n")
W("Branch: de sessie startte op `claude/zealous-edison-nvw1hy`, maar alle commits van deze run")
W("staan op **`main`** (§6a) — de scheduler-tekst geeft daar expliciet toestemming voor.\n")
W("**Leesbaar dagrapport:** ARTIFACT_LINK\n")

# ---------------------------------------------------------------- samenvatting
W("""## Samenvatting in één alinea

De grootste Run B-dag sinds het bestaan van deze routine: **negenenvijftig duels in vijftien van
de zeventien competities**. Alleen de Hungarian NB I (geen programma) en de Kosovo Superleague
(nog altijd niet in de Fotmob-daglijst, ongewijzigd sinds 13 aug) stonden leeg. Dit is ook de
eerste Run B waarin `MAX_DEEP_ANALYSES` werkelijk knelt: de cap staat op 55 en er vielen vier
duels buiten — al zou één daarvan (Girona – Castellón) hoe dan ook op `NONE` zijn uitgekomen, dus
de afkapping kostte **drie** echte analyses. Vijfenveertig duels zijn volledig doorgerekend
(28 `FULL`, 17 `LIGHT`), samen **641 selecties en nul bets**. Elf duels vielen op `NONE`, in twee
scherp gescheiden groepen: vier buiten `conversion_in_range` en zeven zonder enig gemeten
divisiepaar. De bevinding van de dag staat niet bij een wedstrijd maar bij de herijking —
**negentien selecties in acht wedstrijden haalden alle acht poorten op de ruwe kans en sneuvelden
uitsluitend op §1g**, veruit de grootste zo'n groep tot nu toe. Tien van de vijftien competities
hadden een sportkey en kregen de volle bulk-aanroep; vijf niet. 76 van 509 credits.
""")

# ---------------------------------------------------------------- stage -2
W("""## Stage -2 — Branches

De opdracht schrijft de branchcontrole vóór alle andere stappen voor, en die is uitgevoerd vóórdat
deze regels zijn gelezen. `git fetch origin` bracht **30 takken** naast `main` in beeld, en de
eerste telling gaf een alarmerend beeld: eenentwintig takken met 1 tot 184 "eigen" commits.

Dat is het valse alarm waar Stage -2 zelf voor waarschuwt, en dit keer is de oorzaak met één
commando aangetoond in plaats van met handwerk:

```
git rev-parse --is-shallow-repository   ->  true
git fetch --unshallow origin            ->  276 commits in plaats van 58
```

De container kreeg de repo als **ondiepe kloon**. Bij een ondiepe kloon ontbreekt het punt waar
twee takken uit elkaar zijn gegaan, dus `git merge-base` geeft leeg terug en
`rev-list --count HEAD..<tak>` telt élke commit van vóór de knip als "nog niet hier".

| | ondiep (58 commits lokaal) | na `--unshallow` (276 commits) |
|---|---|---|
| takken met "eigen" commits | 21 van de 30 (1 t/m 184 stuks) | **0 van de 30** |
| `merge-base` met `main` | leeg | gewoon een commit |

Ter controle is daarnáást op **inhoud** gekeken, want een telling die eerst fout was verdient geen
blind vertrouwen: over alle dertig takken staat er **geen enkele pick-id** in `picks.jsonl` die
`main` niet ook heeft (274 op `main`, elke tak een deelverzameling), en `prompts/_shared-rules.md`
is op elke tak kleiner dan op `main`. Het enige wat de oude takken extra hebben is
`tmp-run/`-kladwerk en een `oddspapi`-regel in `source-health.json`, die op 31 aug bewust is
geschrapt bij de overstap naar het 20K-plan (commit `f342894`).

Er viel dus niets te mergen, geen enkele conflictregel is toegepast, en de run is op **`main`**
uitgekomen. Eén aantekening voor de volgende run: het unshallowen kostte **1,9 seconde**. Dat is
de moeite van dat handwerk elke dag niet waard — doe het als eerste, altijd.
""")

# ---------------------------------------------------------------- stage 0
W("""## Stage 0 — Afwikkelen

```
python3 scripts/ledger.py open    ->  Geen picks klaar om af te wikkelen.
python3 scripts/shadow.py open    ->  Geen schaduwpicks klaar om af te wikkelen.
```

Run A van vanochtend (02:3x) heeft alles van 11 september afgewikkeld. Er stond bij aanvang **geen
enkele** echte pick open (274 picks, 0 open) en de tweeëntwintig openstaande schaduwpicks zijn
allemaal van Run A van vandaag — die wedstrijden moeten nog beginnen (`bron meldt nog niet
afgelopen`). Ook de controle die Stage -2 na de merge eist, is gedaan: er staat geen openstaande
pick van een run die op een andere tak nooit is afgewikkeld.
""")

# ---------------------------------------------------------------- bronstatus
W("## Bronstatus deze run\n")
W("Letterlijke uitvoer van `python3 scripts/api_check.py`:\n")
W("```")
W(blok("api.txt"))
W("```\n")
W("""**`API_FOOTBALL_KEY` ontbreekt nog steeds** — niet afgewezen, maar niet gezet: `api_check.py`
slaat de bron over zonder één HTTP-verzoek te doen. Dit is een staande blokkade sinds 8 augustus
en geen nieuwe storing; zie `README.md` → "Sleutels toevoegen". Het kost deze run concreet zes van
de vijfenveertig doorgerekende duels een `FULL`-label: de vijf competities zonder Fotmob-xG
(Tsjechië, Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) rekenen nu op doelpunten voor en
tegen en blijven daardoor `LIGHT`, met een drempel van 16.0 in plaats van 8.0.

| Bron | Status | Detail |
|---|---|---|
| `the_odds_api` | **ok** | 48 actieve competities, 19.386 credits over, 614 gebruikt deze maand. 76 uitgegeven in 56 aanroepen. |
| `fotmob` | **ok** | 59 duels, 15 competities, standen van beide seizoenen, context voor alle 59 zonder één fout. |
| `betexplorer` | **ok** | vijftien slugs, alle vijftien raak — **voor het eerst inclusief Albanië**. |
| `api_football` | `key_missing` | sleutel niet gezet in de omgeving van de geplande taak. |
| `understat` | ongewijzigd | niet aangeroepen: dekt geen enkele Run B-competitie. Normale uitkomst. |

Wijzigingen t.o.v. vorige run: **één correctie in de administratie.** Op 11 september stond in
`coverage.json` dat de Kategoria Superiore geen BetExplorer-slug had. Dat is nagetrokken en het
klopt niet: `albania/abissnet-superiore` levert gewoon vier rijen. De aantekening is aangepast.
Praktisch maakte het vandaag niets uit — beide Albanese duels zijn afgekapt — maar het is precies
het soort aanname dat anders jaren blijft staan.

**Eén storing onderweg, en die is opgelost.** Bij de eerste poging van Stage 3 brak de
TLS-verbinding naar `fotmob.com` halverwege af (`SSLEOFError: UNEXPECTED_EOF_WHILE_READING`) op de
stand van English League Two, ná vijftien geslaagde verzoeken in dezelfde run.
`scripts/fotmob._get_json` doet geen enkele poging opnieuw, dus zo'n eenmalige hik zet de hele run
stil op een bron die het gewoon doet. `tmp-run/rb12_retry.py` legt daar vier pogingen met
oplopende pauze omheen — alleen voor netwerk- en TLS-fouten, nooit voor een HTTP-status, want dat
is een antwoord van de bron en geen storing onderweg. Bij de tweede poging kwam alles binnen en is
de herhaling verder geen enkele keer aangesproken. Dit staat met opzet in `tmp-run/` en niet in
`scripts/`: het is een herhaalpoging en geen regel.
""")

# ---------------------------------------------------------------- dekking
W("## Dekkingsrapportage\n")
W("| Competitie | Status | Toelichting |")
W("|---|---|---|")
for naam in RUNLIJST:
    blokje = comps.get(naam)
    if not blokje or blokje.get("status") == "GEEN WEDSTRIJD":
        reden = ("geen programma dit weekend" if naam.startswith("Hungarian")
                 else "geen enkele competitie met ccode KOS in de Fotmob-daglijst, "
                      "ongewijzigd sinds 13 aug 2026")
        W(f"| {naam} | GEEN WEDSTRIJD | {reden} |")
        continue
    ms = blokje["matches"]
    n_afg = sum(1 for m in ms if m.get("afgekapt"))
    n_none = sum(1 for m in ms if m["tier"] == "NONE")
    n_ana = len(ms) - n_afg - n_none
    stat = "GEANALYSEERD" if n_ana else ("AFGEKAPT" if n_afg else "BUITEN DATADEKKING")
    delen = [f"{len(ms)} duel(s)"]
    if n_ana:
        tiers = [m["tier"] for m in ms if not m.get("afgekapt") and m["tier"] != "NONE"]
        delen.append(f"{n_ana} doorgerekend ({tiers.count('FULL')}× FULL, {tiers.count('LIGHT')}× LIGHT)")
    if n_none:
        delen.append(f"{n_none}× NONE")
    if n_afg:
        delen.append(f"{n_afg}× AFGEKAPT")
    delen.append("volle bulk-aanroep" if naam in odds["bought"]["spreads"]
                 else "geen sportkey — alleen BetExplorer-1X2")
    W(f"| {naam} | {stat} | {' · '.join(delen)} |")
W("")
afk = res["afkapping"]
W(f"""**Afgekapt door `MAX_DEEP_ANALYSES`:** {afk['afgekapt']} wedstrijden — {', '.join(afk['lijst'])}.

De laagste wedstrijd die het nog haalde is **{afk['laagste_die_het_haalde']['match']}** met
datarijkdom {afk['laagste_die_het_haalde']['richness']}; de hoogste die afviel is
**{afk['hoogste_die_afviel']['match']}** met {afk['hoogste_die_afviel']['richness']}. Die twee
getallen zijn gelijk, en dat is precies wat §3 Stage 4 sinds 5 september over deze score zegt: hij
scheidt niet. De afkapping loopt hier dwars door een groep duels met dezelfde rijkdom, en welke er
dan afvalt bepaalt de vierde sorteersleutel (aftraptijd). De spreiding over de hele run is
{afk['laagste_richness_in_run']} tot {afk['hoogste_richness_in_run']}.

**Let op één boekhoudkundig punt.** `Girona – Castellón` staat in deze afkaplijst én is in de
wedstrijdtabel hieronder `NONE`. Dat is geen dubbeltelling maar een volgorde-effect: de
rangschikking van Stage 4 draait vóórdat de omrekening van promovendi en degradanten heeft
plaatsgevonden, dus een duel met tier `PROMO?` telt daar nog als `LIGHT` mee. Wie de afkapping over
meerdere dagen vergelijkt moet de `NONE`-duels er dus uit halen: vier afgekapt, drie verloren
analyses.
""")

# ---------------------------------------------------------------- NONE
W("""## De elf duels op `NONE`, in twee groepen

Dit is met afstand het grootste aantal `NONE`-duels op één Run B-dag, en het is de moeite waard om
te zien dat ze niet allemaal hetzelfde zijn.

**Groep 1 — buiten het gemeten bereik (`conversion_in_range`), 4 duels.** De ploeg is wél om te
rekenen, maar de uitkomst ligt buiten het bereik waarop de omrekenfactor ooit is gemeten. Dat is
een poort en geen aantekening (§4, de Coventry-val).

| Wedstrijd | Ploeg | Kwam uit |
|---|---|---|
| Girona – Castellón | Girona | LaLiga (degradant) |
| Cambridge United – Reading | Cambridge United | League Two (promovendus) |
| Stockport County – Leicester City | Leicester City | Championship (degradant) |
| Port Vale – Exeter City | Port Vale | League One (degradant) |

**Groep 2 — geen gemeten divisiepaar, 7 duels.** Hier bestaat de omrekening helemaal niet.

| Wedstrijd | Ploeg | Waarom er geen factor is |
|---|---|---|
| Iraklis – Atromitos | Iraklis | `promotion` kent voor **Griekenland** geen enkel divisiepaar, in geen van beide richtingen |
| Sepsi OSK – CFR Cluj | Sepsi OSK | idem voor **Roemenië** |
| Rapid București – FC Voluntari | FC Voluntari | idem voor **Roemenië** |
| Padova – Ascoli | Ascoli | komt uit de **Serie C**; `TIER2` heeft geen regel voor de Serie B |
| LR Vicenza – Juve Stabia | LR Vicenza | idem |
| Walsall – Rochdale | Rochdale | komt uit de **National League**; de omrekening zoekt alleen in League One |
| York City – Swindon Town | York City | idem |

De tweede groep wijst allemaal dezelfde kant op en het is een structureel gat, geen toeval: de
routine kan één divisie omhoog en één omlaag kijken, en in september zitten de lagere Engelse en
Italiaanse divisies vol met ploegen die uit de derde divisie komen. Roemenië en Griekenland kosten
vandaag samen drie duels omdat er voor die landen überhaupt niets gemeten is. Dat is niet met een
regelwijziging op te lossen — er moet een meting komen, en die staat onder "Openstaand".
""")

# ---------------------------------------------------------------- bevinding
W("""## De bevinding van de dag: negentien selecties die alleen op de herijking sneuvelden

Dit is het grootste effect dat §1g tot nu toe op één dag heeft gehad, en het is precies de meting
waarvoor die paragraaf op 5 september is ingevoerd.

**Negentien selecties, verdeeld over acht wedstrijden, haalden alle acht poorten op de ruwe kans.**
Geen van die negentien sneuvelde op poort 5 (tweede methode), poort 6 (robuustheid), poort 7
(context) of poort 8 (underdog). Ze waren op de ongecorrigeerde schaal compleet. Zonder de
herijking was dit dus een dag met acht bets geweest.

De fit van vanochtend, uit `recalibrate.py show`:

```
""" + blok("recal.txt") + """
```

Elf procentpunt optimisme, gemeten over 616 afgerekende gevallen. Dat is de scheefstand die hier
van elke schatting af gaat, en in het midden van de koersband (rond 60% kans) is dat het verschil
tussen +12 pp geclaimde edge en 0. Eén regel per wedstrijd gaat als schaduwpick naar
`data/shadow.jsonl` met `failed_gate = "herijking"`, geboekt op de **ruwe** schaal zoals §5a eist:

| Wedstrijd | Markt @ koers | Ruwe edge | Herijkt | Ook geblokkeerd |
|---|---|---|---|---|""")
for m in res["matches"]:
    for z in m.get("zonder_herijking", []):
        W(f"| {m['match']} | {z['market']} @ {z['odds']} | {z['edge_pp']:+.2f} pp | "
          f"{z['edge_pp_herijkt']:+.2f} pp | {z['ook_geblokkeerd']} |")
W("""
**En nu het ongemakkelijke deel.** Onder `shadow.py stats` staat `viel af op: herijking` inmiddels
op **+36.0% ROI over 8 afgewikkelde gevallen** (6 van de 8 gewonnen). Dat is de enige poort in het
hele schaduwlogboek met een positief rendement — alle andere besparen geld. Als dat standhoudt,
houdt deze correctie winnende bets tegen en hoort ze herzien.

**Lees dat vandaag niet.** §6d is daar expliciet over: onder ~30 afgewikkelde gevallen per poort is
elk verschil ruis, en acht is niet dertig. Er is vandaag dan ook **niets** aan de drempel of aan de
herijking veranderd. Wat er wél is gebeurd: de reeks groeit hard. Van de tweeëndertig
`herijking`-kandidaten staan er nu twintig open, waarvan acht van vandaag. Bij dit tempo staat de
teller binnen twee weken boven de dertig, en dan is de vraag voor het eerst beantwoordbaar. Zet er
tot die tijd geen conclusie op — precies de fout waarmee de oude poort 5 ooit is ingevoerd.
""")

# ---------------------------------------------------------------- wedstrijden
W("## Wedstrijden\n")
W("Vijfenveertig doorgerekende duels, geen enkele bet. De volledige selectielijst per duel staat in")
W("`data/run-state/2026-09-12-run-b.json` onder `all_candidates`; hieronder per wedstrijd het label,")
W("de sterkste kandidaat en de poort waarop hij sneuvelde.\n")
for naam in RUNLIJST:
    blokje = comps.get(naam)
    if not blokje or not blokje.get("matches"):
        continue
    W(f"### {naam}\n")
    W("| Wedstrijd | Aftrap | Data | Sterkste kandidaat | Edge | Valt af op |")
    W("|---|---|---|---|---|---|")
    for m in blokje["matches"]:
        if m.get("afgekapt"):
            W(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | — | — | "
              f"**AFGEKAPT** (buiten de cap van 55) |")
            continue
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

Uitvoer van `python3 scripts/toplist.py --run b --date 2026-09-12`:

```
""" + blok("top.txt") + """
```
""")

# ---------------------------------------------------------------- net niet
W("""### Net niet

Drie kandidaten met een echte edge die het niet haalden, met het cijfer per poort:

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|""")
for m in res["matches"]:
    nm = m.get("near_miss")
    if nm:
        W(f"| {m['match']} | {nm['market']} @ {nm['odds']} | {nm['edge_xg']:+.2f} pp | "
          f"{nm['edge_split']:+.2f} pp | {nm['edge_robust_min']:+.2f} pp | {nm['failed_gate']} |")
W("""
Alle drie wijzen dezelfde kant op, en het is dezelfde richting als de bevinding hierboven: een
ruime edge op het ongecorrigeerde model (+15 tot +23 pp op beide methodes, en een zwakste stand van
het (shrink, rho)-grid die er nauwelijks onder ligt) die na de correctie ruim onder de drempel
uitkomt. Er is vandaag dus geen enkele kandidaat afgevallen op poort 5, 6, 7 of 8 als eerste poort
— de verdeling van alle 641 selecties is: edge 603, koersband 19, herijking 19.

Op de **ruwe** schaal verschuift dat: edge 594, koersband 19, poort 8 vijf keer, poort 7 vier keer
en negentien selecties die helemaal niets tegenkwamen. Dat poort 8 op de herijkte schaal geen
enkele selectie als eerste tegenhoudt is precies wat §1e voorspelde toen die poort op 5 september
werd verlicht: de herijking pakt de oorzaak aan waar poort 8 een symptoom van afdekte, dus er komen
vanzelf veel minder underdog-selecties tot aan die poort.
""")

# ---------------------------------------------------------------- marktbalans
W("## Marktbalans (§1a — controle op de inkoop, niet op de uitkomst)\n")
W("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
W("|---|---|---|---|")
W("| 1X2 | 13 van 13 (10× beste prijs uit de h2h-bulk, 3× BetExplorer-marktgemiddelde) | 134 | 0 |")
W("| Asian Handicap · DNB · Double Chance | 10 van 13 (1 credit per competitie, in de bulk) | 219 | 0 |")
W("| Over/Under | 10 van 13 (in dezelfde bulk) | 212 | 0 |")
W("| BTTS | 10 van 13 — 46 wedstrijden à 1 credit | 76 | 0 |")
W("")
W(state["credits"]["marktbalans"])
W("")
W("Uitvoer van `guard.report()`:\n")
W("```")
W(odds["guard"])
W("```\n")
W(state["credits"]["bron"])
W("""

**De beste prijs tegenover het marktgemiddelde.** Over de negenendertig duels waar beide bekend
zijn lag de beste prijs gemiddeld **+7,05%** boven het BetExplorer-gemiddelde, mediaan **+5,71%**.
Neem hier de mediaan: de uitschieter is Olympiacos – OFI Crete op +38,64%, waar Betfair de uitzege
op 17.5 noteerde tegen een marktgemiddelde van 10.67. Dat is een staarteffect op een longshot — bij
zulke koersen is de spreiding tussen boeken het grootst — en geen structurele winst. De mediaan
ligt netjes in lijn met de +6,07% die §1a op 5 september mat.
""")

# ---------------------------------------------------------------- vroeg seizoen
W("## Vroeg-seizoenscorrectie\n")
W(state["vroeg_seizoen"]["noot"])
W("")

# ---------------------------------------------------------------- contextlogboek
W("""## Contextlogboek — een gat in de meting, niet in de analyse

`ctxlog.py collect` legde **46 van de 59** duels vast. De dertien die wegvielen hebben allemaal
dezelfde oorzaak, en die is vandaag voor het eerst gemeten: **Fotmob geeft voor een deel van de
kleinere clubs `totalStarterMarketValue` = 0.** Zonder selectiewaarde kan `ctxlog.out_share` het
aandeel ontbrekende spelers niet uitrekenen — `out / (basis + out)` heeft een noemer nodig — en dan
valt de wedstrijd buiten het logboek.

Welke dertien: zes van de twaalf League Two-duels, beide Oostenrijkse duels, beide Albanese, plus
Granada – Albacete, Notts County – Bradford City en Shrewsbury Town – Northampton Town.

**Dit raakt de analyse niet.** Poort 7 staat bij ontbrekende data gewoon open (§1c: een meting die
er niet is, is geen bewijs van een probleem), en de datarijkdom-score geeft een ontbrekende meting
het middenpunt en nooit nul. Wat het wél raakt is het **tempo van de meting** die §1c plant. Daar
staat dat élke wedstrijd met context loggen de steekproef naar ruim honderd per dag tilt en de
vraag binnen drie tot vier weken beantwoordbaar maakt. Als structureel een vijfde tot een kwart van
de duels wegvalt — en juist de kleinere competities, waar deze routine het meeste aan het loggen
heeft — dan duurt dat navenant langer. Het logboek staat nu op 467 wedstrijden, 363 afgewikkeld.

```
""" + blok("ctx.txt") + """
```

De helling staat op −21,7 pp per eenheid met t = −1,26. Met 363 wedstrijden is pas een effect vanaf
~33 pp aantoonbaar, dus dit blijft precies waar het op 5 september stond: het teken wijst de
verwachte kant op, de omvang is niet vast te stellen, en poort 7 blijft een rem en geen bijstelling.
""")

# ---------------------------------------------------------------- afwikkeling
W("""## Afwikkeling vorige picks

**Geen.** Er stond bij aanvang geen enkele echte pick open en geen enkele schaduwpick was
afwikkelbaar — Run A van vanochtend had alles van 11 september al afgerekend, en de
tweeëntwintig openstaande schaduwpicks van Run A van vandaag moeten nog gespeeld worden. Deze run
voegt daar acht `herijking`-rijen en drie `near_miss`-rijen aan toe (één daarvan valt samen: de
Lillestrøm-selectie is zowel de near miss als de `zonder_herijking`-rij van dat duel, en krijgt
volgens §5a maar één regel).
""")

# ---------------------------------------------------------------- logboek
W("## Stand van het logboek\n")
W("Uitvoer van `python3 scripts/ledger.py stats` — dit is wat er wél door de poorten kwam:\n")
W("```")
W(blok("ledger.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/shadow.py stats` — dit is wat er is tegengehouden:\n")
W("```")
W(blok("shadow.txt"))
W("```\n")
W("Uitvoer van `python3 scripts/calibration.py stats` (§6e):\n")
W("```")
W(blok("calib.txt"))
W("```\n")

# ---------------------------------------------------------------- openstaand
W("""## Openstaand

1. **De herijking is de eerste poort met een positief rendement.** +36,0% over acht afgewikkelde
   gevallen. Acht is te weinig om iets van te vinden (§6d eist er ~30), maar de reeks groeit nu
   hard — twintig open, waarvan acht van vandaag. **Kijk hier over twee weken opnieuw naar**, en
   niet eerder. Wat er dan ook uitkomt: verander niets op één dag.
2. **Er is geen omrekening voor een derde divisie.** Vier duels vielen vandaag op `NONE` omdat
   Ascoli, LR Vicenza, Rochdale en York City uit de Serie C respectievelijk de National League
   komen, en `promotion` kijkt maar één divisie omhoog en één omlaag. In september zitten juist de
   lagere divisies daar vol mee. Een gemeten Serie B ↔ Serie C-paar en een League Two ↔ National
   League-paar zouden dit wegnemen; beide zijn met `promotion.measure_gap` op Fotmob-standen te
   meten, net zoals op 31 augustus voor zes landen is gedaan.
3. **Griekenland en Roemenië hebben helemaal geen divisiepaar.** Drie duels vandaag, en het is
   structureel: elke Griekse of Roemeense promovendus of degradant levert `NONE` op. Dit is
   hetzelfde werk als punt 2 en kan in dezelfde meting mee.
4. **Fotmob geeft voor kleine clubs geen selectiewaarde.** Dertien van de negenenvijftig duels
   vallen daardoor buiten het contextlogboek. Dat vertraagt de meting van §1c precies bij de
   competities waar deze routine het meest te leren heeft. Te onderzoeken: of `squad_value` uit een
   andere Fotmob-respons te halen is, of dat er een tweede maat naast moet (bijvoorbeeld het aantal
   uitvallers zonder waardeweging, dat is grover maar altijd beschikbaar).
5. **De vroeg-seizoenscorrectie loopt op in plaats van uit.** Factor 1,0829 vandaag, tegen 1,0661
   gisteren, en het effect op P(Over 2.5) is met +5,20 pp het grootste van deze maand. Run A
   signaleerde vanochtend hetzelfde en zette het al op deze lijst: sinds 3 september weegt het
   lopende seizoen óók mee in de teamsterkte (§4), dus het hogere doelpuntenniveau zit nu
   waarschijnlijk twee keer in dezelfde som. **Dit hoort tegen uitslagen te worden nagemeten, niet
   tegen de markt** (§2), en dat is werk voor een aparte sessie.
6. **De datarijkdom-score scheidt nog steeds niet.** De laagste die het haalde en de hoogste die
   afviel staan allebei op 5,0. Dat is geen nieuw probleem — §3 Stage 4 schrijft het sinds
   5 september met zoveel woorden op — maar vandaag is het voor het eerst een Run B-dag waarop de
   cap echt knelt, en dan wordt het praktisch: wie de score verfijnt, begin met de vraag of hij
   überhaupt iets voorspelt.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
""")

Path(f"runs/{DAY}-run-b.md").write_text("\n".join(out))
print(f"runs/{DAY}-run-b.md geschreven — {len(out)} blokken")
