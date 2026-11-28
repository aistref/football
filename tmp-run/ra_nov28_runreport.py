"""Bouwt het markdown-runrapport van Run A, 28 nov 2026 (§6b-1).

De tabellen komen uit data/run-state/ en de meetblokken uit de vastgelegde uitvoer in tmp-run/,
zodat het rapport niet met de hand wordt overgetypt. De prozastukken staan hieronder.
"""
import json
from datetime import date

DAG = "2026-11-28"
S = "tmp-run/ra_nov28_"


def lees(naam):
    return open(S + naam).read().rstrip()


st = json.load(open(f"data/run-state/{DAG}-run-a.json"))
res = json.load(open(S + "results.json"))
s3 = json.load(open(S + "stage3.json"))
odds = json.load(open(S + "odds.json"))
bev = json.load(open(S + "bevestiging.json"))
top = st["selectie_5b"]
picks = json.load(open(S + "picks_a.json"))
idx = {m["match"]: m for m in res["matches"]}

ORDER = ["Premier League (ENG)", "Serie A (ITA)", "La Liga (ESP)", "Bundesliga (GER)",
         "Ligue 1 (FRA)", "Championship (ENG)", "Eredivisie (NED)", "Primeira Liga (POR)",
         "Belgian Pro League (BEL)", "Super Lig (TUR)", "Scottish Premiership (SCO)",
         "Danish Superliga (DEN)", "Ekstraklasa (POL)", "UEFA Champions League",
         "UEFA Europa League", "UEFA Conference League", "FA Cup (ENG)", "League Cup (ENG)",
         "Coppa Italia (ITA)", "KNVB Beker (NED)", "DFB Pokal (GER)", "Copa del Rey (ESP)"]

EERSTE = {  # eerstvolgende ronde, uit de BetExplorer-fixturepagina van de bevestigingsstap
 "Danish Superliga (DEN)": "eerste duel 29 nov 14:00",
 "UEFA Champions League": "league phase hervat 8 dec",
 "UEFA Europa League": "league phase hervat 10 dec",
 "UEFA Conference League": "league phase hervat 10 dec",
 "FA Cup (ENG)": "eerstvolgende ronde 4 dec — valt nog buiten de lijst",
 "League Cup (ENG)": "eerstvolgende ronde 15 dec — valt nog buiten de lijst",
 "Coppa Italia (ITA)": "eerstvolgende ronde 1 dec — valt nog buiten de lijst",
 "KNVB Beker (NED)": "geen ronde in de fixturelijst",
 "DFB Pokal (GER)": "eerstvolgende ronde 1 dec — valt nog buiten de lijst",
 "Copa del Rey (ESP)": "geen ronde in de fixturelijst",
}

# ---------- dekkingstabel ----------
dek = ["| Competitie | Status | Toelichting |", "|---|---|---|"]
for naam in ORDER:
    blok = st["competitions"].get(naam) or {}
    status = blok.get("status", "?")
    ms = blok.get("matches") or []
    if status == "GEANALYSEERD":
        tiers = {}
        for m in ms:
            tiers[m["tier"]] = tiers.get(m["tier"], 0) + 1
        bets = sum(1 for m in ms if m.get("bet"))
        t = f"{len(ms)} duel{'s' if len(ms) != 1 else ''} · " \
            + " / ".join(f"{v}× {k}" for k, v in sorted(tiers.items())) \
            + (f" · **{bets} bet{'s' if bets != 1 else ''}**" if bets else " · geen bet")
    elif status == "BUITEN DE RUNLIJST":
        t = f"besluit 18/19 nov 2026: alleen 1 jan t/m 30 jun. Speelt vandaag óók niet; {EERSTE.get(naam, '')}"
    else:
        t = f"niets op de kalender in het venster; {EERSTE.get(naam, '')}"
    dek.append(f"| {naam} | `{status}` | {t} |")
DEK = "\n".join(dek)

# ---------- wedstrijdtabel ----------
rij = ["| Wedstrijd | Aftrap NL | Tier | Rijkdom | Selecties | Uitkomst |", "|---|---|---|---|---|---|"]
for naam in ORDER:
    for m in (st["competitions"].get(naam) or {}).get("matches") or []:
        p = m.get("pick") or {}
        if m.get("bet"):
            uit = f"**BET — {p['market']} {p['selection']} @ {p['odds']:.4f}** ({p['edge_pp']:+.2f} pp)"
        else:
            r = idx[m["match"]]
            fg = sorted({c.get("failed_gate") for c in r.get("all_candidates", [])
                         if c.get("failed_gate")})
            uit = "GEEN BET — " + (", ".join(f"`{x}`" for x in fg) if fg else "geen kandidaat binnen de koersband")
        rij.append(f"| {m['match']} | {m['kickoff_nl']} | {m['tier']} | {m['richness']:.1f} | "
                   f"{len(idx[m['match']].get('all_candidates', []))} | {uit} |")
WED = "\n".join(rij)

# ---------- topselectie ----------
tops = ["| # | Wedstrijd | Markt @ koers | Kans | Edge | Score | Risico | Status |",
        "|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(top["herijkt"], 1):
    pk = next((p for p in picks if p["home"] + " – " + p["away"] == r["match"]), {})
    tops.append(f"| {i} | {r['match']} | {r['market']} — {r['selection']} @ {r['odds']:.4f} | "
                f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']:.3f} | "
                f"{pk.get('confidence','—')} | {r['status']} |")
TOP = "\n".join(tops)

ruw = ["| # | Wedstrijd | Markt @ koers | Ruwe kans | Ruwe edge | Score | Poort |",
       "|---|---|---|---|---|---|---|"]
for i, r in enumerate(top["ruw"], 1):
    ruw.append(f"| {i} | {r['match']} | {r['market']} — {r['selection']} @ {r['odds']:.4f} | "
               f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']:.3f} | {r['status']} |")
RUW = "\n".join(ruw)

# ---------- net niet ----------
nn = ["| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |",
      "|---|---|---|---|---|---|"]
rows = []
for m in res["matches"]:
    nmiss = m.get("near_miss")
    if not nmiss:
        continue
    rows.append((nmiss.get("edge_pp") or 0, m["match"], nmiss))
for _, naam, n in sorted(rows, key=lambda r: -r[0]):
    nn.append(f"| {naam} | {n['market']} @ {n['odds']:.4f} | {n.get('edge_xg', 0):+.2f} pp | "
              f"{n.get('edge_split', 0):+.2f} pp | {n.get('edge_robust_min', 0):+.2f} pp | "
              f"`{n['failed_gate']}` |")
NN = "\n".join(nn) if len(nn) > 2 else None

# ---------- marktbalans ----------
pm = {}
for m in res["matches"]:
    for markt, v in (m.get("per_market") or {}).items():
        d = pm.setdefault(markt, {"n": 0, "bets": 0, "comps": set()})
        d["n"] += v["n"]
        d["bets"] += v["bets"]
        if v["n"]:
            d["comps"].add(m["competition"])
bets_per_markt = {}
for pk in picks:
    bets_per_markt[pk["market"]] = bets_per_markt.get(pk["market"], 0) + 1
mb = ["| Markt | Competities met prijzen | Selecties doorgerekend | Gepubliceerde bets |",
      "|---|---|---|---|"]
for markt in ("1X2", "Asian Handicap", "Draw No Bet", "Double Chance", "Over/Under", "BTTS"):
    d = pm.get(markt, {"n": 0, "comps": set()})
    mb.append(f"| {markt} | {len(d['comps'])} van 12 | {d['n']} | {bets_per_markt.get(markt, 0)} |")
mb.append(f"| **totaal** | | {sum(v['n'] for v in pm.values())} | {len(picks)} |")
MB = "\n".join(mb)

bron = ["| Bron | Status | Detail |", "|---|---|---|"]
for k, v in json.load(open("data/source-health.json"))["last_run_run_a"]["sources_deze_run"].items():
    s, _, rest = v.partition(";")
    bron.append(f"| `{k}` | {s.strip()} | {rest.strip() or '—'} |")
BRON = "\n".join(bron)

tekst = f"""# Run A — {DAG}

**Runlijst:** kerncompetities + toernooien (`prompts/run-a.md`), zestien competities.
**Rundag:** zaterdag 28 november 2026. `MAX_DEEP_ANALYSES` = **55**, `MAX_SHORTLIST` = **5**
(`ranking.max_shortlist`, de tabel die sinds 19 nov 2026 bindt).
**Branch:** deze sessie kreeg `claude/stoic-davinci-dtqinr` toegewezen; de run staat op **`main`**
(§6a, de scheduler geeft daar expliciet toestemming voor).
**Looptijd:** gestart 03:06 CET — zie `duur` in `data/run-state/{DAG}-run-a.json`. Ruim binnen de
deadline van 06:30 die §0 stelt.
**Dagrapport:** Artifact https://claude.ai/artifact/Nm1Ne8t3KUv2WdM9nsr7te ·
Markdown https://github.com/aistref/football/blob/main/runs/{DAG}-run-a.dagrapport.md

## Het antwoord in vijf regels

1. **Eenenvijftig duels in het inzetvenster, verdeeld over twaalf van de zestien competities**, en
   alle eenenvijftig doorgerekend: de zaterdagcap van 55 bindt niet. Het scheelt vier duels en dat
   is het krapst van deze reeks. **Geen enkel duel op `NONE`**, bij TWINTIG
   promovendi-/degradantenomrekeningen — het grootste aantal van deze reeks, verdeeld over alle
   twaalf spelende competities.
2. **Vijf gepubliceerde regels, en vijf plekken in de zaterdaglijst.** Alle vijf halen hun eigen
   lat én hun ruwe schaal (`bet_beide` vijf van de vijf), dus de rangorde en de drempel wijzen
   exact dezelfde lijst aan, de lijstlengte bindt niet en er is geen enkele
   `lijstlengte`-schaduwrij. Vier van de vijf zijn een doelpuntenmarkt (drie Over, één Under), de
   vijfde een Draw No Bet.
3. **DE BELANGRIJKSTE BEVINDING VAN VANDAAG: de doelpuntenselectie staat op BEIDE kanten scheef en
   op één ervan is het nu hard.** `margins.py goalbias` geeft **Under gespeeld +0,661 doelpunt per
   duel over 153 gevallen bij z = +4,92** en **Over gespeeld −0,368 over 87 bij z = −1,87**,
   terwijl het model zelf goed staat (+0,019 over 2521, z = +0,56). Dat is geen gerichte
   **vorm**fout meer zoals §6g in oktober beschreef maar een **algemene winner's curse op de
   doelpuntenas**. Niets verzet: poort 9 blijft onveranderd (§1h, §6g).
4. **Tweede bevinding: poort 7 komt voor het eerst aan de meetgrens.** `ctxlog.py stats` geeft de
   fout van het model tegen het beschikbaarheidsverschil op **t = −1,99** bij een helling van
   **−11,8 pp per eenheid** over 2297 wedstrijden, en de aantoonbaarheidsgrens ligt bij ~11 pp. De
   richting is de verwachte. Blijft een **rem** en geen **bijstelling** (§1c).
5. **Stage 0 wikkelde vijf picks (vier gewonnen, één verloren) en zeventien schaduwrijen af**, en
   Stage -2 vond over 103 takken na het unshallowen **nul** eigen commits en main als **superset**
   op alle vijf de logboeken. Er is niets gemerged omdat er niets te mergen viel.

---

## Stage -2 — honderddrie takken op de inhoud vergeleken

De repo kwam opnieuw als **ondiepe kloon** aan (`git rev-parse --is-shallow-repository` → `true`)
en is ge-unshallowed: `main` ging daarmee van **57** naar **806** commits. Vóór die stap meldden
**90 van de 103** takken "eigen commits", tot **730** stuks voor `claude/bold-curie-i16v98`. Dat is
exact het valse alarm waar §3 Stage -2 voor waarschuwt: zonder de volledige geschiedenis bestaat
het punt waar twee takken uit elkaar gingen niet, `git merge-base` geeft niets terug en
`rev-list --count HEAD..<tak>` telt élke commit van vóór de knip mee. Na het unshallowen houden
**nul van de 103** takken eigen commits over.

Daarna is per record op de **inhoud** vergeleken en niet op de commitgraaf, zoals Stage -2 sinds
27 september eist ("0 eigen commits is een uitspraak over de graaf; alleen een vergelijking per
regel is een uitspraak over de metingen"). Per unieke blobversie van elk logboek zijn de
record-id's tegen `origin/main` gelegd:

| Logboek | Records op main | Unieke blobversies over de takken | Records die main mist |
|---|---|---|---|
| `data/picks.jsonl` | 609 | 77 | **0** |
| `data/shadow.jsonl` | 2269 | 94 | **0** |
| `data/context-log.jsonl` | 2637 | 91 | **0** |
| `data/calibration.jsonl` | 9369 | 94 | **0** |
| `data/coverage.json` | 50 competities | 49 | **0** |
| `data/source-health.json` | 74 bronnen | 88 | **1 — zie hieronder** |

Die ene is `oddspapi`, en het is **geen verloren meting maar een bewuste verwijdering**:
commit `f342894`, *"Promovendi via Fotmob-tweede divisies; OddsPapi-reserve verwijderd na overstap
naar 20K-plan"*. Hij hoort dus niet terug te komen, net als de vier dubbele `shadow.jsonl`-rijen
van 3 oktober die op 7 november met opzet zijn verwijderd en die §3 Stage -2 uitdrukkelijk niet
wil laten aanvullen. Main beschrijft de verwijdering zelf nog onder `besluiten_18_nov_2026`.

De andere "ontbrekende" paden in `source-health.json` (179 stuks bij een platte
padvergelijking) zijn per-run momentopnames van oudere Run B- en Run C-takken plus
lijstlengteverschillen: `last_run`, `last_run_run_b/history` en dergelijke. Dat zijn geen
accumulerende metingen maar de laatste-run-stand, die elke run wordt overschreven.

**Er is niets gemerged, want er viel niets te mergen.** `picks.jsonl` bevatte na het unshallowen
geen openstaande pick van een run die op een andere tak nooit is afgewikkeld (Stage -2 punt d):
`ledger.py open` gaf vijf afwikkelbare picks en één wachtende, alle zes van Run A en Run B van
27 november op `main` zelf.

---

## Dekkingsrapportage

{DEK}

**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 wedstrijden. 51 duels op een zaterdagcap van 55, dus de
cap bindt niet en de afkappingslijst is leeg. Het scheelt vier duels en dat is het krapst van deze
reeks; de laatste Run A-dagen zaten op 6, 14 en 19 duels. De **datarijkdom** in de run liep van
**5,0** tot **8,0** (`ranking.data_richness`), en omdat er niets is afgekapt zijn "de laagste die
het haalde" en "de hoogste die afviel" beide leeg — zoals §3 Stage 4 voor die situatie vraagt.

**De zes bekers staan op `BUITEN DE RUNLIJST` en niet op `GEEN WEDSTRIJD`.** §5 verbiedt dat
laatste met zoveel woorden: er wórdt in die toernooien gespeeld, het staat alleen niet op de
runlijst, en het als "niets op de kalender" opschrijven is hetzelfde probleem als een stille
truncatie in Stage 4. Vandaag valt het onderscheid feitelijk samen — nul duels in beide daglijsten
voor alle zes — maar de status blijft die van de regel en niet die van de uitkomst.

**De runlijst is door een tweede, onafhankelijke bron bevestigd** (§1, de vijfde poort). Fotmob
levert de daglijst en BetExplorer de fixturepagina per competitie, en ze zijn het over **alle 22
competities** eens: **51 duels tegen 51**, nul afwijkingen, inclusief de tien competities die
vandaag nul duels hebben. Juist die laatste zijn de reden dat deze controle bestaat — een gemiste
speelronde ziet er van buitenaf uit als een rustdag.

---

## Bronstatus deze run

Letterlijke uitvoer van `python3 scripts/api_check.py`, zoals §3 Stage 3 eist:

```
{lees('api_check.txt')}
```

**Geen sleutel is afgewezen en geen sleutel ontbreekt onverwacht.** `API_FOOTBALL_KEY` is er met
opzet niet (besluit van de gebruiker, 27 sep 2026) en dat is geen gat, geen actiepunt en het staat
niet in de notificatie — alleen hier, als boekhouding (§3 Stage 3, punt 2). Van de 34 sportkeys van
de repo waren er **33 actief**; de enige inactieve is `soccer_uefa_europa_conference_league`, en die
competitie heeft vandaag geen duel, dus het kost niets. Vijf actieve sportkeys kent de repo niet
(Brazil Série B, Coupe de France, 3. Liga, Superettan, Nations League) en **geen van de vijf staat
op de runlijst van Run A**.

{BRON}

**Creditverbruik** (`guard.report()`):

```
{odds.get('guard_totaal', odds.get('guard', ''))}
plafond: suggest_cap(18809, 3) = 3131 · split_budget(3131, 12) = (12, 12) · bulk: True
```

**Understat ligt er voor de tiende rundag op rij uit, en vandaag kost dat wél iets.** Alle vijf de
competities die hij dekt spelen vandaag, met **twintig duels** samen, dus het kalibratieblok van
§6e mist bij die twintig de `p_xg_understat`-arm en er is vandaag geen tweede, onafhankelijk
xG-model. Drie van de vijf gepubliceerde regels staan in die vijf competities. Wat het **niet**
raakt: `my_prob` komt uit Fotmob-xG en Fotmob-splits en verandert hier niet door (§4, 31 aug 2026 —
Understat is redundantie en meting, geen invoer), en §2 blijft gedekt zolang Fotmob levert. Zou
Fotmob omvallen, dan is er geen onafhankelijke kansinput meer, wordt élk duel `NONE` en levert elke
run gegarandeerd nul bets; **dát** is het geval dat §3 vooraan in de notificatie wil hebben, en het
is vandaag niet aan de orde.

---

## Stage 0 — Afwikkeling

**Vijf picks afgewikkeld: vier gewonnen, één verloren.** Alle vijf zijn binnenlandse
competitieduels, dus de eindstand ís de stand na 90 minuten en de verlengingsregel van §6d komt
niet aan de orde.

| Pick | Koers | Uitslag | Uitkomst |
|---|---|---|---|
| Alanyaspor – Konyaspor, Over 2.5 | 2.4308 | 1–2 (3 doelpunten) | **gewonnen** |
| Nottingham Forest – Chelsea, Over 2.5 | 1.931 | 3–2 (5) | **gewonnen** |
| Levante – Racing Santander, Over 3.5 | 2.10 | 1–3 (4) | **gewonnen** |
| Fluminense – Cruzeiro, BTTS nee | 2.32 | 0–1 | **gewonnen** |
| Leganés – Sabadell, Over 2.0 | 1.79 | 0–0 (0) | verloren |

**Zeventien schaduwrijen afgewikkeld: negen gewonnen, zeven verloren, één void** (Jong AZ Alkmaar –
TOP Oss, door de bron als afgelast gemeld). Eén pick blijft open (Real Salt Lake – Vancouver
Whitecaps, nog niet afgetrapt) en één schaduwrij (Columbus Crew – Inter Miami, 2,1 uur na de
aftrap en nog niet als afgelopen gemeld).

### Reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)

**Klopte de redenering, of klopte alleen de uitkomst?** Bij de drie Overs wel: Alanyaspor –
Konyaspor kwam op 3 doelpunten uit tegen een verwachting die daar net boven lag, Nottingham Forest –
Chelsea op 5 en Levante – Racing Santander op 4. Dat zijn wedstrijden die binnen een halve goal van
de voorspelling bleven of er ruim boven uitkwamen, dus de kant was goed gekozen. De BTTS-nee bij
Fluminense – Cruzeiro (0–1) is gewonnen met een correct ingeschatte lage score.

**De verliezer is het leerzaamste geval, en niet omdat hij verloor.** Bij Leganés – Sabadell
verwachtte het model 2,6 doelpunt en er vielen er **nul**. Diezelfde wedstrijd leverde óók een
schaduwrij op — `1X2 — 2 (Sabadell FC wint) @3.401`, tegengehouden door poort 8 — en die verloor op
0–0 eveneens. Op een duel dat de analyse aan twee kanten verkeerd had ingeschat heeft de rem dus
geld bespaard. Het omgekeerde gebeurde bij **Sønderjyske – Brøndby IF (1–1)**: daar hielden drie
verschillende poorten elk een kandidaat tegen — de herijking (Under 2.5 @2.40), poort 8 (Asian
Handicap SønderjyskE +0.75 @1.99) en poort 9 (Under 3 @1.88) — en **alle drie zouden ze gewonnen
hebben**, op een wedstrijd die precies op de voorspelde twee doelpunten uitkwam.

**Zat er een patroon in de dag?** Drie van de vier winnende picks waren een Over, en dat is precies
de kant waarvan `margins.py goalbias` vandaag meet dat hij terugloopt (+6,4% over 114 picks, tegen
+10,6% over 62 op 11 oktober). Vier van de vijf picks waren een doelpuntenmarkt.

**Wat dit NIET betekent.** Eén dag is geen reeks (§6d). Over het hele logboek staan 114 Over-picks;
de vier van gisteren verschuiven dat rendement met minder dan een procentpunt, en de richting van de
reeks is al weken dalend. De drie tegengehouden winnaars bij Sønderjyske zijn één wedstrijd op
reeksen van 54 tot 444 afgewikkelde gevallen. Er is op grond van gisteren geen drempel, gewicht of
poort aangeraakt.

---

## Wedstrijden

Alle 51 duels, in de volgorde van de runlijst. `Selecties` is het aantal doorgerekende
markt-en-kantcombinaties; `Uitkomst` noemt bij een `GEEN BET` élke poort die bij minstens één
kandidaat van dat duel dichtstond, niet alleen de eerste.

{WED}

---

## Topselectie (§5a, `toplist.py`)

**MET de herijking — dit is de lijst waaruit bets komen.**

{TOP}

**ZONDER de herijking — wat de routine vóór 5 sep 2026 zou hebben gezien.**

{RUW}

Letterlijke uitvoer:

```
{lees('toplist_py.txt')}
```

**Twee dingen aan de ruwe lijst.** Ze wordt aangevoerd door `Elche CF +1.5 @1.71` met een score van
**12,171**, hoger dan welke gepubliceerde regel ook — en poort 8 houdt die tegen omdat het de
underdog-kant onder `UNDERDOG_FLOOR` is. Hetzelfde geldt voor `Lorient +2 @1.90` bij Paris
Saint-Germain. Dat is de rem waarvan de gebruiker op 5 oktober 2026 heeft gezegd *"Rem blijft zoals
die nu is"*, en de reeks erachter staat op **444 afgewikkelde gevallen met −1,5%**: hij bespaart
geld, maar weinig. En drie van de vijf gepubliceerde regels staan óók in de ruwe top vijf, wat
betekent dat de herijking de kop van de lijst vandaag nauwelijks heeft verschoven.

**`bet_beide` is bij alle vijf de regels waar**, en `zonder_herijking` is over de hele run leeg: er
is geen enkele selectie die alleen op de ruwe schaal kwalificeerde, en geen enkele die alleen
herijkt kwalificeerde. Dat is de gunstige stand van §5a en ze komt niet elke dag voor.

### Stijlcontrole op de voorbeschouwingen (§6b-5j)

```
{lees('prosecheck.txt')}
```

Alles binnen de norm: vijf teksten, 2475 woorden, drie kopjes per tekst (de eis is minstens drie
sinds 19 nov 2026), gemiddeld 0,8 em-dash tegen een norm van twee en een nulmeting van 5,2, geen
verboden formuleringen, geen herhaalde alinea-openers en geen rekenjargon. De leeswijzer van het
script blijft gelden: het is een **hulpmiddel en geen poort** en het kan geen sjabloon zien dat met
andere woorden is geschreven.

---

## "Net niet" (§5)

{NN or '**Geen enkele afgewezen kandidaat kwam boven de `NEAR`-drempel uit.** Dat is bij 51 doorgerekende duels opmerkelijk en het verdient een regel in plaats van stilte.'}

---

## Marktbalans (§5, verplicht)

{MB}

**De controle slaagt zo ruim als hij kan.** `split_budget(3131, 12)` gaf `(12, 12)` en de volledige
bulk-aanroep paste voor **alle twaalf** inkoopbare competities, dus elke competitie kreeg uit
dezelfde aanroep zowel een **uitkomstmarkt** (1X2, Asian Handicap, Draw No Bet, Double Chance) als
een **doelpuntenmarkt** (Over/Under). Twaalf op twaalf, waar het op 30 augustus 2026 één op twaalf
was. §1a eist dat dat getal erbij staat, want twee bets uit één markt op een dag dat alleen die
markt te koop was is iets anders dan op een dag dat alle zes meededen.

**Vandaag deden alle zes mee bij alle twaalf, en er komen vier doelpuntenmarkten en één
uitkomstmarkt uit.** Die scheefheid komt dus uit de analyse en niet uit de portemonnee, en dat is
het onderscheid dat deze controle moet kunnen maken. BTTS is in de **tweede ronde** gekocht op de
vereniging van beide schalen (§1a, 13 sep 2026): 39 van de 51 duels toonden een kandidaat-edge en
kregen de markt, à 1 credit per duel. De analyse is daarna opnieuw gedraaid — §1a schrijft voor dat
ze twee keer loopt — en gaf **exact dezelfde vijf bets**: BTTS werd nergens de sterkste selectie.
Bij twee duels verschoof de reden van afwijzing wel (Real Madrid – Deportivo Alavés van `+4,45` naar
`+6,54` pp, St. Mirren – Kilmarnock van `data conflicterend` naar `edge onder drempel`), want daar
werd BTTS de sterkste niet-kwalificerende kandidaat.

De **beste prijs** leverde over de hele run gemiddeld **6,04%** meer dan het BetExplorer-gemiddelde
(§1a, 5 sep 2026: daar is +1,84 pp edge op gemeten). Twee van de vijf gepubliceerde koersen staan bij
een **beurs** en zijn daarom doorgerekend met `oddsapi.net_price`: Hamburger SV – Bayern München
(Matchbook 2.00 bruto, 1.98 na 2% commissie) en Vitória de Guimarães – Estrela da Amadora (Matchbook
1.87 bruto, 1.8526 netto). De gebruiker ziet op de site de koers ervóór; beide getallen staan in de
pick en op de pagina.

---

## Stand van het logboek

### `ledger.py stats` — wat er wél doorheen kwam

```
{lees('ledger_py_stats.txt')}
```

**Lees de Brier-regel, want dat is de enige die zegt of de edge-schatting iets waard is.** Eigen
Brier **0,2627** tegen **0,2438** voor de markt: de bookmaker schat nog steeds scherper, en in zijn
getal zit zijn eigen marge, die zijn score juist slechter maakt. Over 542 afgewikkelde bets
verwachtte het model **325,1** winnaars en werden het er **253** (−72,1). Zolang die regel zo staat
is elk gemeten voordeel eerder modelfout dan marktfout (§1g), en is een lijst van vijf een
**rangschikking van wat het model het sterkst vindt** en niet een gevonden voordeel.

### `shadow.py stats` — wat de poorten hebben tegengehouden

```
{lees('shadow_py_stats.txt')}
```

Per poort, met de leesregel van §6d erbij (niet lezen onder ~30 afgewikkelde gevallen):

| Poort | Afgewikkeld | Rendement | Lezing |
|---|---|---|---|
| `context` (poort 7) | 157 | **−22,0%** | overtuigendste van de negen; de poort doet zijn werk |
| `doelpunten_onder` (poort 9) | 54 | **−30,7%** | op wát hij vangt doet hij zijn werk; het probleem zit in wat er langs komt |
| `robuustheid` (poort 6) | 88 | −12,5% | bespaart geld |
| `odds` (poort 2) | 51 | zie uitvoer | koersband |
| `data` (poort 4) | 55 | −8,5% | bespaart geld |
| `herijking_omgekeerd` | 8 | −44,5% | te weinig gevallen om te lezen |
| `herijking` (§1g) | 59 | −3,3% | bespaart geld, nauwelijks |
| `tweede_methode` (poort 5) | 338 | −2,9% | bespaart geld, nauwelijks |
| `underdog` (poort 8) | 444 | −1,5% | bespaart geld, nauwelijks |
| `underdog_ruw` (poort 8, ruwe schaal) | 17 | −8,8% | te weinig gevallen; nooit optellen bij `underdog` |
| `edge` (§5b) | 738 | **+5,4%** | kostte geld; de drempel snijdt sinds 20 sep aan het eind |
| `lijstlengte` (§5b) | 34 | **+13,5%** | de gebruiker kijkt bij 100 gevallen |

**`lijstlengte` staat onveranderd op 34 gevallen**, want vandaag kwam er niets bij: vijf selecties
boven hun lat en vijf plekken. De gebruiker heeft op 18 november gezegd dat hij bij **100** gevallen
opnieuw kijkt; dat is de lat, en de vraag is vandaag **niet** voorgelegd. `MAX_SHORTLIST` is niet
aangeraakt (§5b: een run verandert die nooit op eigen initiatief).

**`underdog` en `underdog_ruw` mogen nooit worden opgeteld** — het zijn twee populaties (§1e,
15 sep 2026). Poort 8 hield vandaag **18** selecties tegen op de herijkte schaal en **0** op de
ruwe.

### `recalibrate.py show` — de stand van de herijking (§1g)

```
{lees('recalibrate_py_show.txt')}
```

**`fitted_through` staat op 2026-11-27, de vorige rundag**, zoals §6b-5c eist. Dat is geen
toeval maar het gevolg van de volgorde: `calibration.py settle` is vandaag in Stage 0 gedraaid
vóórdat `load_fit()` aan de analyse begon (75 waarnemingen afgewikkeld, 9321 van 9369 compleet,
48 nog open). Zonder die volgorde rekent de run door op een oudere fit zonder dat iets klaagt —
precies de stille faalstand die van 18 t/m 29 september elf dagen lang schade deed.

De fit **verhoogt** een kans over vrijwel de hele speelbare band en tilt elke gepubliceerde regel
ongeveer één procentpunt op. Bij géén van de vijf is dat beslissend: `bet_beide` is bij alle vijf
waar. Lees `a=1,037 / b=0,024` niet als "het model is goed" — het is gekalibreerd op de
**ongeselecteerde** ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in de
**geselecteerde** groep, waar `ledger.py stats` 72 winnaars te veel verwachtte.

### `calibration.py stats` — staat het model scheef tegenover de markt (§6e)

```
{lees('calibration_py_stats.txt')}
```

### `ctxlog.py stats` — het contextlogboek (§1c)

```
{lees('ctxlog_py_stats.txt')}
```

---

## Margelogboek (§6f) en doelpuntenlogboek (§6g)

### `margins.py stats` — de volle reeks

```
{lees('margins_stats.txt')}
```

### `margins.py stats --since 2026-09-20` — alleen de homogene lambdas

```
{lees('margins_since.txt')}
```

**Eén cel boven twee standaardfouten, en dat is het gelijkspel:** voorspeld 23,6% tegen werkelijk
20,8%, **−2,8 pp** over 1718 homogene duels. Derde dag op rij dezelfde cel. Op de volle reeks (2521
duels, beide `shrink`-instellingen door elkaar) is het −1,5 pp en haalt ze de grens niet.

Dit raakt **één** bet van vandaag: Motherwell – Hibernian is een **Draw No Bet**, de markt waar het
gelijkspel uit de berekening wordt gedeeld. Een grid dat te veel gelijkspelmassa legt, verdeelt die
massa bij een DNB naar rato over beide ploegen, dus het effect op de DNB-kans is tweede-orde en niet
eenduidig van teken — maar het is niet nul, en bij een handicap op 0.0 geldt hetzelfde.

**De kant waar §6f oorspronkelijk over ging staat recht.** "Favoriet wint met 3 of meer" op −0,9 pp
en "met 4 of meer" op +0,3 pp over 483 duels met een duidelijke favoriet. Dat gat is dicht sinds de
shrink-overstap van 19 september en blijft dicht; de aanleiding van 19 september (handicaps op de
underdog die er te goed uitzagen) is daarmee weg.

### `margins.py goalbias` — de bevinding van vandaag

```
{lees('goalbias.txt')}
```

**Dit is de belangrijkste meting van deze run en ze verandert de diagnose van §6g.** Drie regels,
en ze mogen nooit worden opgeteld:

| Groep | n | verwacht/duel | werkelijk/duel | verschil | z |
|---|---|---|---|---|---|
| alle doorgerekende duels (**het model**) | 2521 | 3,042 | 3,062 | +0,019 | **+0,56** |
| **Under gespeeld** (de selectie) | 153 | 2,763 | 3,425 | **+0,661** | **+4,92** |
| **Over gespeeld** (de selectie) | 87 | 3,379 | 3,011 | **−0,368** | **−1,87** |

**Het model staat goed.** +0,019 doelpunt per duel over 2521 duels is niet van nul te
onderscheiden, en ook de vorm van de verdeling is nu vlak: de grootste cel-afwijking is +1,1 pp (bij
5 doelpunten) en `P(Under 2.5)` staat op −1,3 pp. Vergelijk dat met §6g van 11 oktober, waar
4 doelpunten +2,9 pp te laag stond en `P(Under 2.5)` 2,4 pp te hoog — die **vormfout is weg**, zoals
de meting van 28 oktober al voorspelde (ze was grotendeels een nalatenschap van `shrink = 0.80`).

**De selectie staat wél scheef, en nu aan beide kanten.** De Under-kant is van z = +2,91 (n = 49,
11 okt) naar **z = +4,92 (n = 153)** gegroeid — het signaal is sterker geworden in plaats van
weggezakt. En de Over-kant, waarover §6g op 11 oktober schreef *"op de Over-kant gebeurt dat niet"*
(n = 38, z = −0,54), staat nu op **z = −1,87 (n = 87)**.

**Waarom dat de diagnose verandert.** §6g beschreef twee lagen: een **vormfout** in het grid die
`P(Under)` bij élk duel te hoog zette, plus een selectie-effect bovenop. In die lezing moest de
Over-kant juist **verdienen** aan de vormfout, en dat deed hij ook (+10,6% over 62 picks). Die
lezing houdt geen stand: de vormfout is weg en de Over-kant staat nu zélf de verkeerde kant op,
terwijl zijn rendement van +10,6% naar **+6,4% over 114 picks** is gezakt. Wat overblijft is geen
gerichte gridfout maar een **algemene winner's curse op de doelpuntenas** — de routine kiest aan
beide uiteinden juist die duels waar haar eigen lambda de verkeerde kant op staat. Dat is dezelfde
mechanica die §1g voor kansen beschrijft, nu op de doelpunten.

**Rendement per kant, over het hele logboek:**

| | picks | rendement |
|---|---|---|
| Over/Under — **Under** | 192 | **−15,2%** |
| Over/Under — **Over** | 114 | **+6,4%** |
| Over/Under samen | 306 | −7,2% |
| Draw No Bet | 19 | +22,6% (ruim onder de ~30 van §6d) |

**Wat hier NIET uit volgt, en dat is de helft van deze paragraaf.** Er is **niets verzet**:

1. **Poort 9 blijft onveranderd** op `UNDER_EXTRA` = 2,0 pp bovenop de 8,0, alleen op `FULL`. §1h
   en §6g zeggen beide met zoveel woorden dat een run die knop nooit op eigen initiatief verzet, en
   de reeks `doelpunten_onder` staat op 54 afgewikkelde gevallen met **−30,7%**: op wát hij vangt
   doet hij zijn werk. Het probleem zit in wat er **langs** komt.
2. **De Over-kant krijgt geen eigen lat.** |z| = 1,87 haalt de lat van deze repo niet
   (`CREDIBILITY_K` is ingevoerd op t = +2,11 / +1,71, rollende xG is afgewezen op +0,05 / +1,06),
   en een gemeten rem uitbreiden naar een populatie waar de meting hem niet steunt is wat §1h en §4
   verbieden.
3. **De voorwaarde van §1h is niet ingetreden.** Die zegt dat poort 9 opnieuw gemeten hoort te
   worden *"zodra de vormfout is gerepareerd"*. De vormfout is niet gerepareerd maar **verdwenen**,
   door de shrink-overstap van 19 september, en dat is iets anders. De vraag hoort voorgelegd zodra
   de reeks van ná 3 november groot genoeg is, en dat is dezelfde voorwaarde als bij de
   niveaucorrectie hieronder.

**Het hoort wél bij elke doelpuntenregel van vandaag genoemd te worden, en dat zijn er vier van de
vijf.** In het dagrapport staat het in gewone taal bij elke bet, en bij Torino – Lazio — de enige
Under — staat er bovendien bij dat Pinnacle er 11,20 pp anders over denkt.

---

## De niveaucorrectie van 2 november, apart gemeten op 545 duels

`gridfit.py measure` draait standaard op alle homogene duels sinds de shrink-overstap, en dat is
sinds 3 november geen homogene populatie meer op het **niveau**: de lambdas van ná die datum dragen
`model.LEVEL_SCALE` = 1.032 al in zich. §6g punt 4 eist daarom dat de vraag "werkt de correctie" op
**alléén die duels** wordt gelezen. `tmp-run/ra_nov28_gridfit_split.py` knipt de reeks op
`gridfit.LEVEL_SWITCH`:

| | duels | gemiddeld totaal (werkelijk − voorspeld) | z | fout op `P(Under 2.5)` |
|---|---|---|---|---|
| 20 sep t/m 2 nov, **zonder** de correctie | 1173 | **+0,099** | +1,92 | **−2,38 pp** |
| 3 t/m 27 nov, **mét** de correctie | 545 | **−0,097** | −1,22 | **+1,94 pp** |
| de gemengde reeks die `measure` standaard laat zien | 1718 | +0,037 | +0,84 | −1,01 pp |

**Het teken is op alle drie de diagnoseregels omgeslagen en de absolute omvang is vergelijkbaar
gebleven: de correctie heeft de fout gespiegeld en niet verkleind.** Tweede aanwijzing dezelfde kant
op: `scale = 1.032` nog een keer toepassen geeft op die 545 duels **t = −1,91**, tegen **t = +0,92**
op de 1173 ervóór.

**Let op de val in de bovenste tabel.** Op de gemengde reeks lijkt alles juist goed (+0,037,
z = +0,84), want 545 van die 1718 duels dragen de correctie al in zich en de twee helften heffen
elkaar op. Dat is exact de populatiemenging waarvoor `gridfit.py` in zijn eigen kop waarschuwt, en
het is de reden dat deze knip bestaat. Wie alleen de standaarduitvoer leest, concludeert dat het
probleem is opgelost.

**Niets verzet en de vraag niet voorgelegd.** Run A heeft op 21 november zelf de lat op *"ruim boven
de ~900 duels"* gezet en het zijn er **545**; z = −1,22 haalt die lat niet. Verwacht in januari, en
dan met `gridfit.py measure` in plaats van met een nieuwe redenering (§6g). Poort 9 hangt aan
hetzelfde besluit.

De volledige uitvoer van beide populaties staat in `tmp-run/ra_nov28_gridfit_na_niveau.txt`; de
gemengde meting:

```
{lees('gridfit.txt')}
```

---

## Vroeg-seizoenscorrectie en niveau (§3 Stage 5)

`uplift_observations` heeft **nul** competities overgeslagen: alle twaalf spelende competities
hebben xG in beide seizoenen en zitten alle twaalf in de pool. De gepoolde factor staat op
**{res['vroeg_seizoen']['factor']:.4f}** (gepoold {res['vroeg_seizoen']['gepoold']:.4f} over
{res['vroeg_seizoen']['speeldagen']} speeldagen, twaalf competities). Dat is ruim elf procent en dus
groot; hij **dooft uit** naarmate het seizoen vordert.

`model.league_level` koos bij **alle twaalf** de route `vorig+uplift`: geen enkel lopend seizoen is
over `SEASON_MATURE_SHARE` (de helft van zijn speeldagen) heen. De Championship is het verst (18 van
46), de Bundesliga het vroegst (11 van 34).

| Competitie | Route | Speeldagen | thuis | uit | basis |
|---|---|---|---|---|---|
""" + "\n".join(
    f"| {c} | `{n['source']}` | {n['played']} van {n['length']} ({n['share']*100:.0f}%) | "
    f"{n['home_goals_per_match']:.3f} | {n['away_goals_per_match']:.3f} | "
    f"{n['avg_xg_per_match']:.3f} |"
    for c, n in (res.get("niveau") or {}).items()
    if n.get("home_goals_per_match") is not None) + f"""

**Verwar deze correctie niet met `model.LEVEL_SCALE`.** `early_season_uplift` rekent een
competitieniveau van vórig seizoen om naar dit seizoen en dooft uit; `LEVEL_SCALE` is een residu dat
op uitkomsten is gemeten, geldt voor alle competities en dooft **niet** uit. Ze staan naast elkaar en
mogen nooit tot één factor worden samengevoegd (§3 Stage 5).

---

## Stap 2 van Stage 5 — wat anderen voorspellen

§3 Stage 5 heeft op 20 september 2026 gemeten dat geschreven voorspellingen vrijwel niet te halen
zijn (Forebet 403, Pinnacle-artikelen 404, Matchbook 530, voetbalwedden.net zonder de duels van de
dag). Wat er wél is, is **de prijs van Pinnacle apart**: de scherpste bookmaker van de markt, en
zijn de-vigde oordeel is het beste publieke expertoordeel dat beschikbaar is. Over 48 duels met een
Pinnacle-1X2 wijkt het model gemiddeld **3,93 pp** af bij een gemiddelde Pinnacle-marge van
**3,61%** — tegen 6 tot 10% bij de rest, dus dit is de strengste toets die er is. Over 49
(duel, lijn)-paren totalen ligt het model gemiddeld **2,98 pp onder** Pinnacle op de Under-kant
(19 van 49 erboven).

**Per gepubliceerde regel, en het is geen gunstig beeld:**

| Regel | Eigen | Pinnacle | Verschil |
|---|---|---|---|
| Manchester United – Brentford, `P(Under 3.0)` | 34,8% | 49,4% | **+14,54 pp meer doelpunten** |
| Hamburger SV – Bayern München, `P(Under 3.5)` | 38,4% | 49,9% | **+11,50 pp meer doelpunten** |
| Torino – Lazio, `P(Under 2.5)` | 60,6% | 49,4% | **+11,20 pp meer Under** |
| Motherwell – Hibernian, `P(Motherwell wint)` | 44,1% | 35,9% | **+8,18 pp** |
| Vitória de Guimarães – Estrela da Amadora | — | geen 1X2 en geen totaal | geen vergelijking |

**Vier van de vier vergelijkbare regels liggen meer dan acht procentpunt van de scherpste bookmaker
af**, en §1g heeft op 552 afgerekende gevallen gemeten dat de **grootste** geclaimde edge het
**slechtste** rendement geeft. Dat hoort hier te staan en het hoort niet weggeschreven te worden.
Bij Torino – Lazio telt het dubbel: dat is de enige Under, en dus de kant waar §6g de schade meet.

**De harde grens van §2 blijft staan.** Dit getal gaat nooit in `my_prob` of in `prob_sources` — het
is marktafgeleid en het hoort in de vergelijking, niet in de kansschatting. Het staat in
`data/run-state/` in een eigen blok.

---

## Bevinding — de doelpuntenselectie staat op beide kanten scheef en de vormfout is weg

Deze twee horen bij elkaar en het is één bevinding.

**Wat §6g sinds 11 oktober beschreef, waren twee lagen.** Laag 1 was een **vormfout** in
`score_grid`: te weinig massa op 4 en 5 doelpunten, waardoor `P(Under 2.5)` bij élk duel 2,4 pp te
hoog stond. Laag 2 was een **selectie-effect** daarbovenop, zichtbaar op de Under-kant (+0,68
doelpunt per duel, n = 49, z = +2,91) en níet op de Over-kant (n = 38, z = −0,54). Die lezing
verklaarde waarom Under geld kostte en Over juist geld opleverde: dezelfde vormfout die de ene kant
te duur maakte, maakte de andere te goedkoop.

**Laag 1 is weg.** Over 2521 doorgerekende duels staat het model nu op +0,019 doelpunt per duel
(z = +0,56), is de grootste celafwijking in de verdeling +1,1 pp en staat `P(Under 2.5)` op −1,3 pp.
De vormfout was grotendeels een nalatenschap van `shrink = 0.80` en is op 19 september opgelost door
een andere ingreep — dat is wat de meting van 28 oktober al concludeerde, en het is nu ook in de
volle reeks te zien.

**Laag 2 is er nog, groter, en nu aan beide kanten.** De Under-kant is van z = +2,91 (n = 49) naar
**z = +4,92 (n = 153)** gegroeid: in de duels waarin werkelijk een Under is gespeeld vallen er
+0,661 doelpunt per duel méér dan de eigen lambda zei. En de Over-kant, waarover §6g schreef dat er
niets aan de hand was, staat nu op **−0,368 bij z = −1,87 (n = 87)**.

**Daarmee verandert het karakter van het probleem.** Een gerichte gridfout raakt beide kanten
tegengesteld; dit raakt ze beide ongunstig. Wat overblijft is een **algemene winner's curse op de
doelpuntenas**: de routine kiest aan beide uiteinden juist die duels waar haar eigen lambda de
verkeerde kant op staat. Dat is precies de mechanica die §1g voor kansen beschrijft ("wie selecteert
op de grootste edge, selecteert op de grootste modelfout"), nu zichtbaar op de doelpunten in plaats
van op de uitkomsten. Het rendement beweegt mee: Over van +10,6% over 62 picks (11 okt) naar +6,4%
over 114, terwijl Under op −15,2% over 192 blijft staan.

**Wat er NIET is gedaan, en waarom.** Niets verzet. Poort 9 blijft staan zoals hij staat; de
Over-kant krijgt geen eigen lat; geen enkele drempel, gewicht of parameter is aangeraakt. Drie
redenen: |z| = 1,87 op de Over-kant haalt de lat van deze repo niet, een gemeten rem uitbreiden naar
een populatie waar de meting hem niet steunt is wat §1h en §4 verbieden, en een run verzet zo'n knop
nooit op eigen initiatief — het gaat over risicobereidheid en dat hoort bij de gebruiker (§1a, §1e,
§6g). De vraag hoort voorgelegd zodra de Over-kant boven |z| = 2 uitkomt, en dat is bij het huidige
tempo een vraag voor januari.

**Wat het voor vandaag betekent, staat bij de bets zelf.** Vier van de vijf regels zijn een
doelpuntenmarkt, en bij alle vier staat in het dagrapport in gewone taal welke kant van deze meting
hen raakt.

---

## Tweede bevinding — poort 7 komt voor het eerst aan de meetgrens

`ctxlog.py stats` geeft vandaag voor het eerst een bijna-significant verband tussen de **modelfout**
en het **beschikbaarheidsverschil** (het aandeel ontbrekende selectiewaarde van de ene ploeg minus
dat van de andere):

| | r | t | helling |
|---|---|---|---|
| fout van het **model** | −0,042 | **−1,99** | **−11,8 pp per eenheid** |
| fout van de **markt** | −0,033 | −1,60 | −9,3 pp per eenheid |

Bij 2629 afgewikkelde contextwedstrijden is alleen een effect vanaf ongeveer **11 pp per eenheid**
aantoonbaar, dus dit staat **aan** de grens. De richting is de verwachte: een ploeg die meer van zijn
selectiewaarde mist, doet het slechter dan het model zegt. En het model is iets gevoeliger voor
ontbrekende spelers dan de markt.

**Zet dat naast de meting van 5 september 2026** (§1c, "De bijstelling is geprobeerd te meten en er
is niets gevonden"). Die stond over **147** wedstrijden op r = −0,007 en **t = −0,08**, met een
helling van −2,2 pp per eenheid, en de tabel daar becijferde ~4270 wedstrijden voor een effect van
10 pp. Met 2629 wedstrijden is het verband nu zichtbaar en ongeveer zo groot als de steekproef kan
aantonen. Dat de reeks zo snel is gegroeid komt doordat §1c sinds 5 september de context van **élke**
wedstrijd laat loggen, ook de afgekapte — vandaag 51 van de 51.

**Niets verzet, en dat is geen voorlopigheid maar de regel.** Poort 7 blijft een **rem** en geen
**bijstelling**. §1c zegt met zoveel woorden dat er geen enkele meting bestaat die zegt hoeveel
procentpunt een geblesseerde middenvelder waard is, en zo'n getal verzinnen is wat §2 en §4
verbieden. Bovendien haalt |t| = 1,99 de lat van |t| = 2 net niet, laat staan de lat die deze repo
elders aanhoudt. Tweede dag dat deze reeks iets zegt; het staat als openstaand punt.

**Vandaag kostte de poort één duel**, en het is een duidelijk geval: Widzew Łódź – Zagłębie Lubin,
waar Zagłębie Lubin **62%** van zijn selectiewaarde mist tegen 21% bij Widzew Łódź — Marcel Reguła
(terug begin januari 2027), Michał Nalepa en Pawel Kosmalski (beiden twijfelachtig). De reeks
`context` staat op 157 afgewikkelde kandidaten met **−22,0%**, de overtuigendste van alle negen
poorten.

---

## De omrekening van promovendi en degradanten (§4)

**Twintig van de 51 duels** hadden minstens één ploeg die niet in de stand van 2025/2026 staat — het
grootste aantal van deze reeks — en ze gingen alle twintig langs `promotion.convert` /
`convert_relegated`. Het komt **niet** uit één competitie: alle twaalf spelende competities hebben
er minstens één.

| Competitie | Omrekeningen | van |
|---|---|---|
| Championship (ENG) | 4 | 10 |
| Premier League (ENG) | 2 | 3 |
| Bundesliga (GER) | 2 | 5 |
| Ligue 1 (FRA) | 2 | 5 |
| Belgian Pro League (BEL) | 2 | 4 |
| Ekstraklasa (POL) | 2 | 3 |
| Serie A (ITA) | 1 | 3 |
| La Liga (ESP) | 1 | 4 |
| Eredivisie (NED) | 1 | 3 |
| Primeira Liga (POR) | 1 | 4 |
| Super Lig (TUR) | 1 | 2 |
| Scottish Premiership (SCO) | 1 | 5 |

**Twee duels hebben een omgerekende ploeg aan beide kanten:** Paderborn – Schalke 04 (twee
promovendi uit de 2. Bundesliga) en Lincoln City – Wolverhampton Wanderers (een promovendus uit
League One tegen een degradant uit de Premier League, dus de opwaartse **en** de neerwaartse tak in
één duel).

**Nul op `NONE`: `conversion_in_range` heeft vandaag niets geweigerd.** Dat is bij deze aantallen
het vermelden waard, want die poort bestaat juist om te weigeren — de Coventry-val uit de docstring
van die functie, die anders +21 pp schijnedge oplevert die alle andere poorten haalt. En **nul werd
`FULL`**, want een omgerekende ploeg is dat nooit (§4: de omrekening haalt de systematische fout
eruit, niet de onzekerheid). De tierverdeling is dus **31 FULL en 20 LIGHT**.

Alle twintig staan daarmee op de LIGHT-lat van **16,0 pp**, en **geen van de vijf gepubliceerde
regels komt eruit** — alle vijf de bets zijn `FULL`. Dat is de prijs van die lat en geen gebrek: de
hoogste LIGHT-edge van vandaag is **+14,97 pp** (Frosinone – Parma, Under 3.5 @1.9212, enige dichte
poort `edge`), daarna +14,71 (Académico Viseu – Alverca) en +14,49 (West Ham United – Stoke City).
Drie regels binnen anderhalve procentpunt van hun lat, en alle drie gaan ze als `near_miss` het
schaduwlogboek in.

---

## Openstaande punten

1. **De doelpuntenselectie staat op beide kanten scheef** (zie Bevinding). De Over-kant op
   z = −1,87 over 87 gevallen haalt de lat niet; de vraag hoort voorgelegd zodra hij boven |z| = 2
   uitkomt. Niets verzet. *Werk voor een volgende run, niets van de gebruiker nodig.*
2. **De niveaucorrectie houdt haar omgeslagen teken op 545 duels.** De lat is "ruim boven de ~900
   duels" (Run A, 21 nov) en die is niet gehaald. Verwacht in januari, en dan met `gridfit.py
   measure`. Poort 9 hangt aan hetzelfde besluit. *Werk voor een volgende run.*
3. **Poort 7 staat op t = −1,99 en daarmee aan de meetgrens** (zie tweede bevinding). Blijft een
   rem. *Werk voor een volgende run.*
4. **Het gelijkspel staat drie dagen op rij 2,8 pp te hoog** op de homogene reeks. Raakt elke Draw
   No Bet en elke handicap op 0.0, en dus de rangorde van §1a. Nog geen reeks om iets aan te
   verzetten. *Werk voor een volgende run.*
5. **Understat ligt er tien rundagen uit.** Kost vandaag twintig waarnemingen in het kalibratieblok
   van §6e en het tweede xG-model. Wordt pas een echt probleem als Fotmob óók wegvalt; dán hoort
   het vooraan in de notificatie (§3). *Werk voor een volgende run.*
6. **`lijstlengte` staat op 34 afgewikkelde gevallen met +13,5%.** De gebruiker kijkt bij 100
   gevallen. *Besluit van de gebruiker, en pas bij 100 — vandaag niet voorgelegd.*
7. **De neerwaartse omrekening draait voor één paar nog op een gepoolde factor**
   (`Keuken Kampioen Divisie (NED)` → `Eredivisie (NED)`; §4 noemt x1.772 / x0.621 als gemeten op
   n = 23 maar niet toegepast). Raakte vandaag geen enkel duel van deze runlijst. *Besluit van de
   gebruiker; vraagt een eigen tabel voor de neerwaartse richting.*

---

## Wijziging in de code deze run

**Geen.** Er is geen regel in `scripts/` aangeraakt. De runscripts in `tmp-run/` zijn ongewijzigd
overgenomen van 27 november, met alleen de datum, de bestandsnamen en de kop verschillend — §6e en
§1g vragen om een reeks die over dagen heen vergelijkbaar is, en een script dat elke ochtend
opnieuw wordt getypt is elke ochtend een ander script.

Eén ding is bij het overnemen **gerepareerd en het hoort opgeschreven**: `ra_nov27_marktvorm.py`
had het pad naar de run-state hardgecodeerd als `data/run-state/2026-11-27-run-a.json` in plaats van
het uit de rundag af te leiden, terwijl de rest van het script wél op de nieuwe datum stond. De
eerste draai van vandaag schreef daardoor naar het bestand van **gisteren** en zette nul blokken.
Dat is zonder gevolgen gebleven — `git diff` op dat bestand is leeg, omdat de enige toegevoegde
sleutel er al in stond met dezelfde tekst — maar het is dezelfde stille faalvorm als de
hardgecodeerde datumparen in `rb_nov05_bevestiging.py` (7 nov) en de `\\s+`-regex van 14 oktober:
een stap die het verkeerde bestand raakt zonder te klagen. Het pad is nu uit `DAG` afgeleid en de
blokken staan op alle 51 duels van vandaag. **De run-state van 27 november is niet gewijzigd**,
zoals §6c eist.

---

## Dagrapport (§6c)

- **Artifact:** https://claude.ai/artifact/Nm1Ne8t3KUv2WdM9nsr7te — de eerste route, zoals de
  gebruiker op 19 november heeft besloten ("artifact eerst").
- **Markdown:** https://github.com/aistref/football/blob/main/runs/{DAG}-run-a.dagrapport.md — de
  tweede route, verplicht sinds 14 oktober en naast de Artifact-link in de notificatie.

Beide links staan ook in `data/run-state/{DAG}-run-a.json` onder `last_run_run_a` in
`data/source-health.json`, zodat Run D ze kan nalopen (§9: negen rundagen waarvan de Artifact-link
niet was vastgelegd, gevonden op 7 nov).

**De rendercontrole van §6c is gedraaid** (Chromium in de container, tegen `file:///…`), omdat de
Artifact op 14 en 15 oktober twee keer stil is omgevallen: `scrollHeight` 27.293 px, 63.590 zichtbare
tekens, 91 zichtbare blokken, **0** console- en pagefouten. De pagina rendert dus en is compleet.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open(f"runs/{DAG}-run-a.md", "w").write(tekst)
print(f"runs/{DAG}-run-a.md geschreven — {len(tekst.splitlines())} regels, {len(tekst)} tekens")
