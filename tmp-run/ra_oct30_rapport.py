# -*- coding: utf-8 -*-
"""Run A, 30 okt 2026 — het markdown-runrapport samenstellen.

De uitvoer van de logboekscripts wordt LETTERLIJK ingevoegd uit de .txt-bestanden die deze run
heeft weggeschreven, niet overgetypt: §6b eist dat beide rapporten van dezelfde run dezelfde
getallen tonen, en overtypen is precies hoe ze uiteen gaan lopen.
"""
import json

def blok(pad):
    return open(f"tmp-run/{pad}").read().rstrip()

res = json.load(open("tmp-run/ra_oct30_results.json"))
top = json.load(open("tmp-run/ra_oct30_top_a.json"))
picks = json.load(open("tmp-run/ra_oct30_picks_a.json"))
st = json.load(open("data/run-state/2026-10-30-run-a.json"))
ART = "https://claude.ai/artifact/TF6wxvhUqyjsLtNX3cEKcj"
MD = "https://github.com/aistref/football/blob/main/runs/2026-10-30-run-a.dagrapport.md"

TOELICHTING = {
 "La Liga (ESP)": "1 duel, 21:00 NL — doorgerekend, geen bet (poort 7 dicht op blessures)",
 "Bundesliga (GER)": "1 duel, 20:30 NL — doorgerekend op `LIGHT` (promovendus), geen bet",
 "Ligue 1 (FRA)": "3 duels, 19:00–21:05 NL — alle drie doorgerekend, **3 bets**",
 "Championship (ENG)": "1 duel, 21:00 NL — doorgerekend, geen bet",
 "Primeira Liga (POR)": "1 duel, 21:15 NL — doorgerekend, geen bet",
 "Belgian Pro League (BEL)": "1 duel, 20:45 NL — doorgerekend, **1 bet**",
 "Super Lig (TUR)": "1 duel, 18:00 NL — doorgerekend, geen bet",
 "Danish Superliga (DEN)": "1 duel, 19:00 NL — doorgerekend op `LIGHT` (promovendus), geen bet",
 "Ekstraklasa (POL)": "2 duels, 18:00 en 20:30 NL — beide doorgerekend, geen bet (poort 7 dicht op rust)",
 "Premier League (ENG)": "weer op 1 nov 17:30",
 "Serie A (ITA)": "weer op 1 nov 12:30",
 "Eredivisie (NED)": "weer op 1 nov 12:15",
 "Scottish Premiership (SCO)": "weer op 1 nov 14:00",
 "UEFA Champions League": "hervat op 3 nov 18:45",
 "UEFA Europa League": "hervat op 4 nov 16:30",
 "UEFA Conference League": "hervat op 5 nov 18:45",
 "FA Cup (ENG)": "volgende ronde 6 nov 20:30 (BetExplorer; geen ronde vandaag)",
 "League Cup (ENG)": "volgende ronde 14 dec 20:45 (de vierde ronde was 28 okt)",
 "Coppa Italia (ITA)": "volgende ronde 1 dec 21:00",
 "KNVB Beker (NED)": "geen ronde op de fixturepagina (de tweede ronde was 28 okt)",
 "DFB Pokal (GER)": "geen ronde op de fixturepagina (de tweede ronde was 28 okt)",
}

rijen = []
for comp, blk in st["competitions"].items():
    status = blk["status"]
    label = f"`{status}`" if status != "GEANALYSEERD" else "**`GEANALYSEERD`**"
    naam = f"**{comp}**" if status == "GEANALYSEERD" else comp
    rijen.append(f"| {naam} | {label} | {TOELICHTING.get(comp, '—')} |")
dekking = "\n".join(rijen)

nn = []
for comp, blk in st["competitions"].items():
    for m in blk.get("matches") or []:
        k = m.get("near_miss") or m.get("near_miss_gepubliceerd")
        if not k:
            continue
        nn.append(f"| {m['match']} | {m['tier']} | {k.get('market','')} @ {k.get('odds')} | "
                  f"{k.get('edge_xg')} | {k.get('edge_split')} | {k.get('edge_robust_min')} | "
                  f"`{k.get('failed_gate')}` |")
netniet = "\n".join(nn) if nn else "| — | — | — | — | — | — | — |"

tl, rl = [], []
for i, r in enumerate(top["herijkt"], 1):
    tl.append(f"| {i} | {r['match']} | {r['market']} — {r['selection']} | {r['odds']} | "
              f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} | {r['score']} | {r['tier']} | "
              f"{r['status']} |")
for i, r in enumerate(top["ruw"], 1):
    rl.append(f"| {i} | {r['match']} | {r['market']} — {r['selection']} | {r['odds']} | "
              f"{r['prob']*100:.1f}% | {r['edge_pp']:+.2f} | {r['score']} | {r['status']} |")
toplijst, ruwlijst = "\n".join(tl), "\n".join(rl)

niv = []
for comp, v in (res.get("niveau") or {}).items():
    niv.append(f"| {comp} | `{v['source']}` | {v['played']} van {v['length']} | "
               f"{v['home_goals_per_match']:.3f} | {v['away_goals_per_match']:.3f} | "
               f"{v['avg_xg_per_match']:.3f} |")
niveau = "\n".join(niv)

pr = []
for m in res["matches"]:
    pr.append(f"| {m['match']} | {m.get('beste_prijs_winst_pct')}% | {m.get('odds_1x2_bron')} |")
prijzen = "\n".join(pr)

wb = []
for comp, blk in st["competitions"].items():
    for m in blk.get("matches") or []:
        regel = next((r for r in top["herijkt"] if r["match"] == m["match"]), None)
        kop = f"### {m['match']} · {m['kickoff_nl']} NL · {comp}"
        if regel:
            cand = next((c for c in m["all_candidates"]
                         if c["market"] == regel["market"] and c["selection"] == regel["selection"]), {})
            wb.append(
                f"{kop}\n\n```\nData: {m['tier']}\n"
                f"Bet: {regel['market']} — {regel['selection']} — Odds: best {regel['odds']} "
                f"({regel['odds_source']})\n"
                f"Implied prob: {100/regel['odds']:.1f}%  •  My prob: {cand.get('my_prob',0)*100:.1f}% "
                f"(ruw {cand.get('my_raw',0)*100:.1f}%)\n"
                f"Edge: {cand.get('edge_pp'):+.2f} pp (ruw {cand.get('edge_raw'):+.2f})  •  "
                f"selection_score {regel.get('score')}  •  Confidence: "
                f"{'Medium' if m['tier']=='FULL' else 'Low'}\n"
                f"xG-methode {cand.get('edge_xg'):+.2f} pp · splitsmethode {cand.get('edge_split'):+.2f} pp · "
                f"zwakste stand van het grid {cand.get('edge_robust_min'):+.2f} pp\n"
                f"lambdas xG {m.get('lambdas',{}).get('xg')} · splits {m.get('lambdas',{}).get('split')}\n"
                f"bet_beide: {cand.get('bet_beide')} · bet_ruw: {cand.get('bet_ruw')}\n```\n")
        else:
            reden = m.get("reason") or "geen publiceerbare selectie"
            wb.append(f"{kop}\n\n```\nData: {m['tier']}\nGEEN BET — {reden}\n```\n")
wedstrijden = "\n".join(wb)

MD_TEXT = f"""# Run A — 2026-10-30

**Vrijdag 30 oktober 2026.** Negen van de eenentwintig competities uit de runlijst speelden, samen
**twaalf duels** in het inzetvenster — een vrijdagavond met zeven competities die één duel naar
voren schuiven, een volledige Ligue 1-ronde van drie en twee duels in de Ekstraklasa. Geen beker
heeft een ronde en geen Europees toernooi speelt. Twaalf duels tegen een cap van 55, dus
**niets afgekapt**; tien duels op `FULL`, twee op `LIGHT` (de promovendi Elversberg en Lyngby) en
**nul op `NONE`**.

**Vier regels (§5b), alle vier een Over/Under.** Eén haalt de lat van 8,0 pp ondubbelzinnig, één
staat op 0,00085 procentpunt eronder en twee staan op rangorde ver eronder — de twee laatste op de
Under-kant, waar §6g meetbaar ongeveer twee procentpunt te veel kans geeft.

**De bevinding van deze run zit in `scripts/shadow.py` en niet in een bron.** Een selectie die §5b
op rangorde publiceert kon tot vandaag óók als afgewezen kandidaat in het schaduwlogboek belanden.
Zie "De bevinding" hieronder.

**Gedraaid om 07:29 NL, en dat is laat.** §0 eist dat de rapporten om 06:30 klaar staan en de
gebruiker zet tussen 07:00 en 08:00 in. De scheduler is vanmorgen om 07:29 afgegaan en niet om
03:30; de notificatie ging om 07:55 uit, dus binnen het inzetvenster maar aan het eind ervan. Dat
is geen keuze van deze run en er is in de repo niets aan te doen — het staat hier omdat een
structureel late run het verschil tussen een bruikbaar en een onbruikbaar rapport is.

**Dagrapport (§6c):** [Artifact]({ART}) · [Markdown op GitHub]({MD})

**Rendercontrole gedraaid** (§6c, 15 okt 2026), preventief en niet na een klacht: de pagina rendert
in een echte Chromium volledig en zonder fouten, in licht én donker — 17.830 px hoog, 43.661
zichtbare tekens, 54 blokken, 6 tabellen, 4 bet-blokken, nul console- of pagefouten. Mocht de
Artifact onbereikbaar zijn, dan ligt dat dus niet aan de pagina en is opnieuw publiceren zinloos;
de Markdown-link hierboven is dan het antwoord.

---

## Branchaudit (Stage -2)

**Deze run staat op `main`.** De sessie kreeg `claude/stoic-davinci-mauyz0` toegewezen en de
scheduler-tekst geeft expliciet toestemming om naar `main` te pushen (§6a); er is dus niets te
melden over een afwijkende branch.

**De repo kwam als ondiepe kloon aan, en ik heb `--unshallow` pas aan het eind van de run
gedraaid in plaats van als eerste handeling.** Dat is in strijd met de letter van §3 Stage -2, die
`git rev-parse --is-shallow-repository` als allereerste opdracht voorschrijft, en het hoort hier te
staan in plaats van netjes te worden opgeschreven alsof het goed ging. Wat het kostte en wat het
niet kostte:

| | ondiep (654 commits nog niet binnen) | na `git fetch --unshallow origin` (654 commits) |
|---|---|---|
| takken met "eigen" commits | **70 van de 80** | **0 van de 80** |
| `merge-base` met `origin/claude/stoic-davinci-pwdn5x` | leeg | `b198c25`, 17 okt 2026 |

Dat is exact het valse alarm dat §3 Stage -2 beschrijft, en het ziet er precies uit als het echte
geval van 10 augustus. **De uitkomst is niet verkeerd geweest**, want de audit is niet op de
commitgraaf maar op de inhoud gedaan — en dat is wat §3 Stage -2 sinds 27 september zelf
voorschrijft: *"0 eigen commits is een uitspraak over de graaf; alleen een vergelijking per regel
is een uitspraak over de metingen."* Over alle 79 andere takken, per record vergeleken:

| controle | uitkomst |
|---|---|
| pick-id's in `data/picks.jsonl` die `main` niet heeft | **0** van de 483 |
| rij-id's in `data/shadow.jsonl` die `main` niet heeft | **0** van de 1510 |
| nieuwste `prompts/_shared-rules.md` | `main`, 3690 regels (de op één na langste staat op 3587) |

Er valt dus niets te verenigen en er is niets gemerged, en de graafcontrole na het unshallowen zegt
hetzelfde: **nul van de tachtig takken heeft een eigen commit**. `origin/main` en
`origin/claude/stoic-davinci-mauyz0` stonden bij de start op dezelfde commit (`69d679c`, 28 okt
07:16) en dat was de jongste tip van de hele repo.

**Openstaande picks van een tak die nooit is afgewikkeld** (§3 Stage -2, laatste alinea): geen.
`ledger.py open` gaf zes picks en die kwamen alle zes van `main` zelf, van de run van 28 oktober.

**Les voor de volgende run, en dit is het punt van deze paragraaf:** doe het `--unshallow` vóór de
inhoudelijke audit, niet erna. Ik ben vandaag op de juiste uitkomst gekomen omdat ik de inhoud heb
vergeleken in plaats van de graaf; wie alleen de graaf had geteld, had vanmorgen zeventig takken
willen mergen die er allemaal al in zaten.

---

## Bronstatus deze run

### De uitvoer van `api_check.py`, letterlijk (§3 Stage 3)

```
{blok('ra_oct30_apicheck.txt')}
```

**Geen enkele sleutel is afgewezen.** The Odds API staat op 18.579 credits over en 1.421 verbruikt
deze maand, van een plafond van 20.000. `API_FOOTBALL_KEY` ontbreekt en dat is een **besluit van de
gebruiker van 27 september 2026** — geen gat, geen actiepunt (§3). De kanskant komt van Fotmob
(alle competities) en Understat (vijf, waarvan er vandaag drie spelen).

**Twee bekende sportkeys zijn vandaag niet actief** — Coppa Italia en DFB Pokal — en dat klopt: die
competities hebben geen ronde. **Vier actieve sportkeys kent de repo niet:**
`soccer_brazil_serie_b`, `soccer_germany_liga3`, `soccer_sweden_superettan` en
`soccer_uefa_nations_league`. Alle vier vallen buiten de Run A-runlijst en zijn dus werk voor Run B
en Run C; ze staan hier zodat die runs ze niet opnieuw hoeven te zoeken. Een run raakt geen runlijst
aan die niet de zijne is.

### `scripts/idcheck.py` — alle 33 competitie-id's groen

```
{blok('ra_oct30_idcheck.txt')[-700:]}
```

### `data/source-health.json` is bijgewerkt

Zeven regels geschreven: `fotmob` ok, `the_odds_api` ok, `betexplorer` ok, `understat` ok,
`api_football` `plan_limited` (besluit, geen storing), `settling` ok en een nieuwe regel
`shadow_logboek` op `gerepareerd` — zie "De bevinding". **`store["errors"]` is over de hele run
leeg gebleven**: nul bronstoringen.

### De stadionvelden zijn gevuld en er is nul keer verplaatst (§1c)

`context.check_venue` heeft bij alle twaalf duels werkelijk kunnen vergelijken — het stadion is bij
alle twaalf gevuld — en zette **geen enkele keer** `relocated`. Dat is iets anders dan de stille
leegte van 25 t/m 27 oktober, toen `venue.name` bij álle duels `None` was en "niet verplaatst" in
werkelijkheid "niet gemeten" betekende. Vandaag is het een meting.

Twee stadions zijn het vermelden waard zonder dat ze een verplaatsing zijn: **Casa Pia** speelt
vast in het Estádio Municipal de Rio Maior, ruim zeventig kilometer van Lissabon, omdat de eigen
Pina Manique niet aan de competitie-eisen voldoet — dat is hun thuisveld en zo is het genoteerd; en
**Lille** speelt in de Decathlon Arena in Villeneuve-d'Ascq, eveneens hun eigen grond.

### Opstellingen

`lineupType`: **7 `predicted`** en **5 `lastStarting11`**, geen enkele `confirmed`. Dat is te
verwachten om 07:30 NL bij aftrappen van 18:00 tot 21:15 — opstellingen worden ongeveer een uur
voor de aftrap bevestigd.

### De runlijst is door een tweede bron bevestigd (§1)

`ra_oct30_bevestiging.py` legt de Fotmob-daglijst naast de BetExplorer-fixturepagina's en ze zijn
het over **alle zestien** competities met een eigen slug eens: 12 duels tegen 12, en geen enkele
competitie waar de ene bron een wedstrijd ziet en de andere niet.

```
{blok('ra_oct30_bevestiging.txt')}
```

Dat is precies de poort waar de duurste fouten van oktober zaten: in de vraag **wélke** wedstrijden
er zijn, niet in de analyse. De vijf bekers zonder ronde zijn bij BetExplorer nagetrokken en niet
uit de daglijst geconcludeerd — FA Cup 6 november, League Cup 14 december, Coppa Italia 1 december,
KNVB Beker en DFB Pokal geen teamparen op de pagina.

### Het inzetvenster (§3 Stage 1)

Alle twaalf duels komen van de daglijst van de rundag zelf (`source_day = 2026-10-30`), alle twaalf
staan op `playable = True`, en er is **geen carry-over-band**. De vroegste aftrap is 18:00 NL
(Konyaspor – Galatasaray en Cracovia – Motor Lublin), de laatste 21:15 (Casa Pia – Sporting).
`runwindow` rekent met `zoneinfo`, dus het venster is in échte NL-tijd gemeten: nu de wintertijd in
is komt een aftrap van 20:00 UTC op 21:00 NL uit (CET) en niet op 22:00 (CEST).

### De prijzen: alle twaalf duels op de beste prijs

| wedstrijd | winst beste prijs t.o.v. het gemiddelde | bron van het gemiddelde |
|---|---|---|
{prijzen}

Gemiddeld **+6,55%**, met een spreiding van +4,60% tot +8,98%. §1a meet dat zo'n verschil ongeveer
anderhalve procentpunt edge per selectie oplevert. Dit is de eerste Run A waarin **geen enkel duel**
op het gratis BetExplorer-marktgemiddelde hoefde te draaien voor de bet zelf; dat gemiddelde wordt
nog wel gebruikt waarvoor het bedoeld is (het kalibratieblok van §6e en poort 8).

### Wat anderen voorspellen (Stage 5, stap 2)

Geschreven voorspellingen zijn grotendeels niet te halen (§3 Stage 5, gemeten 20 sep: Forebet 403,
Pinnacle-artikelen 404, Matchbook 530). Wat er wél is, is **de prijs van Pinnacle apart** — de
scherpste bookmaker van de markt, en zijn de-vigde prijs is het beste publieke expertoordeel dat
beschikbaar is.

```
{blok('ra_oct30_pinnacle.txt')}
```

```
{blok('ra_oct30_pinnacle_ou.txt')}
```

**Pinnacle is het met alle vier de gepubliceerde regels oneens, en alle vier de verkeerde kant op.**
Dat is geen detail maar de scherpste externe controle die deze run heeft:

| wedstrijd | lijn | P(Under) Pinnacle | P(Under) eigen | verschil |
|---|---|---|---|---|
| Nice – Rennes | 3.00 | 52,8% | 44,0% | −8,79 pp (meer Over) |
| Lille – Lens | 2.50 | 49,6% | 38,8% | −10,83 pp (meer Over) |
| Le Havre – PSG | 3.50 | 52,2% | 58,6% | +6,41 pp (meer Under) |
| Zulte Waregem – Club Brugge | 3.25 | 48,1% | 51,9% | +3,86 pp (meer Under) |

Lees dat als een **waarschuwing en niet als een bevestiging**: §1g meet dat de bookmaker scherper
schat dan het model (Brier 0,2398 voor de markt tegen 0,2603 eigen over 422 afgerekende bets), dus
de grootste afstand tot Pinnacle is eerder de grootste modelfout dan de grootste vondst. Op het 1X2
is de grootste afstand **Le Havre – PSG**: het eigen model geeft PSG 62,0% waar Pinnacle 73,7%
zegt, 11,68 pp verschil — en dat is dezelfde wedstrijd die de duurste poort-8-blokkade van de dag
levert. Geen toeval, maar hetzelfde verschijnsel van twee kanten gezien.

**Harde grens (§2):** niets hiervan gaat in `my_prob` of in `prob_sources`. Het staat in de lezing
en in de vergelijking.

### Understat — de tweede, onafhankelijke xG-bron (§4)

Drie van de vijf gedekte competities spelen vandaag (La Liga, Bundesliga, Ligue 1) en Understat
leverde voor **vier** duels een tweede xG-model: Villarreal – Espanyol, Le Havre – PSG,
Nice – Rennes en Lille – Lens. Voor Elversberg – Mainz niets, wat te verwachten is bij een
promovendus die vorig seizoen niet in de Understat-tabel stond. Blijft genormaliseerd op het
**eigen** competitiegemiddelde van Understat (dat ligt structureel ~0,13 xG per ploeg per duel
hoger dan Fotmob) en gaat mee in het kalibratieblok, niet in `my_prob`.

### Vroeg-seizoenscorrectie en het competitieniveau (§3 Stage 5)

Gepoolde uplift-factor **1.0930** (gepoold 1.1028 over 76 speeldagen in acht competities).
**Overgeslagen in de pool:** Danish Superliga (DEN) — halverwege het seizoen (12 van 22 speeldagen),
dus daar komt het niveau uit het lopende seizoen zelf. Dat is de `lopend`-route van
`league_level`, en een stil weggelaten waarneming is hetzelfde probleem als een stille truncatie —
vandaar deze regel.

| competitie | route | speeldagen | thuisdoelpunten | uitdoelpunten | basis-xG |
|---|---|---|---|---|---|
{niveau}

---

## Afwikkeling (Stage 0)

**De run van 29 oktober is niet gedraaid.** Er is geen `runs/2026-10-29-run-*.md` en geen
`data/run-state/2026-10-29-*.json`. Gevolg: de picks en schaduwrijen van 28 oktober stonden **twee
dagen** open in plaats van één. Zes picks en 38 schaduwrijen afgewikkeld.

| pick | markt | koers | uitslag | resultaat |
|---|---|---|---|---|
| AFC Bournemouth – Aston Villa | 1X2 — 1 | 2.32 | 3–0 | **gewonnen** |
| Hannover 96 – Kaiserslautern | AH −0.25 | 2.06 | 0–2 | verloren |
| St. Mirren – Hibernian | Under 3 | 1.71 | 1–1 | **gewonnen** |
| Santos – Palmeiras | Under 2.5 | 2.0584 | 0–0 | **gewonnen** |
| Toronto FC – DC United | Under 3.5 | 1.6762 | 2–1 | **gewonnen** |
| New York City FC – Atlanta United | Under 3.5 | 1.6468 | 2–1 | **gewonnen** |

**Vijf van de zes gewonnen.** Schaduwrijen: **21 gewonnen, 17 verloren** over 38 rijen.

**Twee van de 44 rijen zijn knock-outduels** en §6d eist daar de stand na 90 minuten: AFC
Bournemouth – Aston Villa (EFL Cup) en Hannover 96 – Kaiserslautern (DFB Pokal). Beide melden
`reason = Full-Time` bij Fotmob, dus de eindstand **is** daar de stand na 90 minuten en er hoefde
geen doelpuntminuut te worden opgezocht. Dat is nagetrokken en niet aangenomen: 3–0 en 0–2 zijn
beslissende uitslagen, maar een 0–2 had ook ná verlenging kunnen vallen.

### De reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)

**1. Klopte de redenering, of klopte alleen de uitkomst?** Bij vier van de vijf winnaars klopte
beide: de verwachte doelpunten lagen dicht bij wat er viel. **Santos – Palmeiras is de uitzondering
en de belangrijkste** — het model verwachtte ruim twee doelpunten en er vielen er nul. Die pick is
gewonnen én aan de verkeerde kant verkeerd ingeschat; bij een iets andere dag was het 2–1 geweest.
**AFC Bournemouth – Aston Villa liep veel schever af dan voorgerekend**: het model gaf Bournemouth
43,1% en het werd een eenvoudige 3–0. Gewonnen, en de uitslag zegt dat de wedstrijd nog scheefer
was dan de grootste edge van die dag suggereerde.

**2. Deed de poort die hem tegenhield zijn werk, in dít geval?** Niet overal. De duurste rij van
woensdag is **Milan – Bologna, Bologna +1.5 @1,46**, tegengehouden door poort 8 en met 2–4
gewonnen — een winnaar die de underdog-rem heeft gekost, op een wedstrijd die precies de kant op
liep waar het model hem zag. Daartegenover hield dezelfde poort **Monza – Napoli, Monza +0.75**
tegen en dat werd 1–4: daar deed hij zijn werk. Eén dag, twee kanten.

**3. Zat er een patroon in de dag dat geen toeval kan zijn?** Ja, één: **vier van de vijf winnende
picks waren Unders** (St. Mirren, Santos, Toronto, New York City). Dat is precies de kant waarvan
§6g meet dat ze te hoog wordt ingeschat. Vier van de vijf op één dag.

**4. En wat betekent dit NIET?** Vier gevallen is geen reeks. §6d eist ~30 en de staande meting
over **107** gespeelde Unders zegt nog steeds het omgekeerde: daar vielen gemiddeld +0,609 doelpunt
per duel méér dan de eigen lambda zei, z = +3,81 — de hoogste stand die deze reeks heeft gehad. Eén
goede woensdag verandert daar niets aan, en er is op grond hiervan geen drempel, gewicht of poort
aangeraakt.

---

## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
{dekking}

**Afkapping (§3 Stage 4):** twaalf duels tegen een cap van 55 (vrijdag), dus
`MAX_DEEP_ANALYSES` bindt niet en er is **niets afgekapt**. De datarijkdom liep van **5,0**
(Zulte Waregem – Club Brugge en Górnik – Legia) tot **8,0** (Villarreal – Espanyol); omdat er niets
afvalt zijn "de laagste die het nog haalde" en "de hoogste die afviel" allebei leeg.

**Marktdekking (§6b-5b):** `progress.py verify` → *"Alle 12 geanalyseerde wedstrijd(en) hebben alle
zes markten gehad."* Groen vóór de commit.

---

## Topselectie (§5b — rangorde over de hele runlijst)

| # | wedstrijd | selectie | koers | kans | edge | score | tier | stand t.o.v. de lat |
|---|---|---|---|---|---|---|---|---|
{toplijst}

**De lijstlengte bindt niet.** Er zijn vier publiceerbare selecties en `MAX_SHORTLIST` is 5
(vrijdag), dus er valt geen gekwalificeerde selectie buiten de lijst en `failed_gate = lijstlengte`
krijgt vandaag geen enkele rij.

**De tweede regel staat op een afrondingsgrens en de twee rekenstappen zijn het oneens.**
Lille – Lens, Over 2.5 @1,94 komt op de herijkte schaal op **+7,99915 pp** uit en haalt de lat van
8,0 dus met 0,00085 procentpunt **niet**; op de ruwe schaal haalt hij hem met +8,37 pp wél.
`ra_oct30_analyze.py` toetst op de onafgeronde waarde en geeft hem daarom `failed_gate = herijking`;
`scripts/toplist.py` leest het veld `edge_pp`, dat met `round(..., 2)` is weggeschreven, en zegt in
zijn `status` "haalt ook de lat". Beide zijn verdedigbaar en ze spreken elkaar tegen. Voor de
publicatie maakt het niets uit — hij staat tweede van vier op een lijst met vijf plekken — en §0
zegt zelf dat de 8,0 "de eerste waarde waarbij het teken omslaat" is en geen optimum, dus een
duizendste procentpunt is geen grootheid waarop iets hoort te hangen. **Niet vandaag gewijzigd:**
een run verzet geen vergelijking in de rekencode op een randgeval van één dag (§6d). Het staat
onder "Openstaand".

**Twee van de vier regels staan op de Under-kant en zijn door geen van beide latten getoetst.**
Le Havre – PSG (Under 2.5 @3,10, +7,07 pp) en Zulte Waregem – Club Brugge (Under 3.25 @2,01,
+3,29 pp). §6g meet vandaag over **1752** doorgerekende duels dat het gemiddelde aantal doelpunten
klopt (voorspeld 3,031 tegen werkelijk 3,072, z = +0,99) maar de verdeling niet: massa verschoven
van 2 doelpunten (−1,4 pp) naar 4 (+1,1) en 5 (+1,4), waardoor **P(Under 2.5) 2,2 pp en
P(Under 3.0) 1,8 pp te hoog staat bij élk duel**, vóór er iets is gekozen. Trek dus ongeveer twee
procentpunt van de genoemde kans af — en dan blijft er van de +3,29 pp van Zulte Waregem vrijwel
niets over. Dat staat zo ook in het dagrapport, in gewone taal.

**Poort 9 hield de Under 3.5 van Le Havre tegen en liet de 2.5 van dezelfde wedstrijd door.** Dat
ziet eruit als een tegenstrijdigheid en het is er geen: `unders.check` bindt met opzet alleen in de
band 8,0–10,0 pp. De tegengehouden selectie staat op +9,01 pp (lat 10,0) en gaat als
`failed_gate = doelpunten_onder` naar het schaduwlogboek; de gepubliceerde staat op +7,07 pp en
wordt daar door `edge` tegengehouden in plaats van hierdoor — want anders loopt die reeks vol met
kandidaten die nooit een bet konden worden en meet ze niets meer (de "twee populaties"-fout van
§1e). Sinds §5b de drempel van een poort in een afkapping heeft veranderd betekent dat echter dat
een Under **onder** de 8,0 wél gepubliceerd kan worden en door geen van beide latten wordt getoetst
— en vandaag gebeurt dat twee keer in plaats van één. Dit is op 28 oktober als besluit aan de
gebruiker voorgelegd en dat punt staat nog open; §1h (12 okt) zegt uitdrukkelijk dat zo'n vraag niet
elke dag opnieuw hoort te worden gesteld, dus de stand van de reeks staat gewoon onder "Stand van
het logboek": `doelpunten_onder` 24 afgewikkelde gevallen, −13,1%.

**De runner-up binnen de gepubliceerde wedstrijd.** Bij Nice – Rennes haalden twee selecties alle
poorten: Over 2.5 @1,67 (score 5,997, gepubliceerd) en Over 3 @2,06 (edge +9,22 pp, kans 57,8%,
score 5,327). De gepubliceerde heeft een **lagere** edge en een **hogere** kans, en `selection_score`
kiest dan de hogere kans — precies de risicokeuze die §1a op 14 augustus heeft vastgelegd. Bij de
andere drie wedstrijden haalde maar één selectie de lijst.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | wedstrijd | selectie | koers | kans | edge | score | stand |
|---|---|---|---|---|---|---|---|
{ruwlijst}

**De sterkste selectie van de dag is niet gepubliceerd.** Le Havre +1.5 @2,09 voert deze lijst aan
met score 8,184 — hoger dan elke gepubliceerde regel — en is tegengehouden door poort 8: de markt
geeft Le Havre 10,7% tegen 73,6% voor PSG, ver onder de ondergrens van 35%. Dat is precies het geval
waarvoor die poort is gebouwd (§1e: over 89 gevallen verwachtte het model 47,1 winnaars, de markt
38,0, en het werden er 33,0 — z = −3,14). Lees deze lijst met §1g ernaast: daar is op 552
afgerekende gevallen gemeten dat er géén drempel op de herijkte edge bestaat die geld oplevert, en
dat het rendement het **slechtst** is bij de hoogste geclaimde edge.

---

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 (beste prijs) | 9 van 9 | 31 | 0 |
| Asian Handicap | 9 van 9 | 45 | 0 |
| Draw No Bet (0.0-lijn) | 9 van 9 | 11 | 0 |
| Double Chance (±0.5-lijn) | 9 van 9 | 6 | 0 |
| Over/Under | 9 van 9 | 56 | **4** |
| BTTS | 5 duels met kandidaat-edge | 10 | 0 |

**De controle is gehaald op de inkoop en zo ruim als ze kan.** Van de negen spelende competities
hebben **alle negen** een sportkey en kregen **alle negen** de volledige bulk (h2h + spreads +
totals, 3 credits per competitie), dus elke gekochte competitie heeft zowel een uitkomstmarkt als
een doelpuntenmarkt. Plafond `suggest_cap(18579, 2)` = **4639** credits, `split_budget(4639, 9)` =
9 spreads / 9 totals, werkelijk verbruikt **27 + 5 = 32** credits; nog 18.547 van het maandplafond
van 20.000 over.

BTTS is gekocht voor **5 van de 12** duels met een kandidaat-edge (§1a stap 2, de vereniging van
beide schalen sinds 13 sep). De andere zeven staan in `markets_checked` als *"niet opgevraagd —
geen kandidaat-edge in dit duel"* en niet als "geen boek noteerde deze markt".

**Alle vier de gepubliceerde regels zijn een Over/Under, en dat is eenzijdig.** Het is géén
inkoopartefact: alle zes markten dongen in elk duel mee en de uitkomstmarkten vielen af op poort 5
(123 selecties) en poort 8 (6 selecties). Het is dus de uitkomst, en bets forceren om een verdeling
te halen is precies wat §1 verbiedt — maar het is wel het soort eentonigheid waar de gebruiker op
19 september over viel, en het hoort daarom hier te staan en niet verzwegen.

### Net niet

| wedstrijd | tier | selectie | xG-model | 2e methode | zwakste stand | valt af op |
|---|---|---|---|---|---|---|
{netniet}

**Poort 5 vangt 123 van de 159 doorgerekende selecties — 77%.** Gisteren was dat 78%. §5 zegt met
zoveel woorden dat als er een week lang alles op `tweede_methode` afvalt, de vraag is of de twee
methodes systematisch uiteenlopen, en dat dat een bevinding is en geen ruis. Wat er tegenover staat:
§1f heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als **kansbron** vrijwel niets
toevoegt (Brier .23625 bij gewicht 0,80 tegen .23674 voor alleen xG) en dat haar waarde juist in dit
veto zit, dat aantoonbaar geld bespaart: `tweede_methode` staat op −8,4% over 219 afgewikkelde
gevallen. Noem het getal dus, lees het over weken en niet vandaag, en verzet er niets op.

Opvallend bij **Lille – Lens**: alle selecties behalve de gepubliceerde Over vielen hierop af, en de
splitsmethode staat daar op +3,20 pp tegen +9,66 pp voor de xG-methode. De twee methodes wijzen
dezelfde kant op maar liggen ver uiteen — en dat is precies waarom die regel op de grens staat.

**Poort 7 (context) sloot bij twee duels, en geen van beide op hetzelfde criterium.**
**Villarreal – Espanyol** op het beschikbaarheidsverschil: Villarreal mist 28% van de selectiewaarde
tegen 6% bij Espanyol — Nathan Saliba (blessure, terug begin november), Pape Gueye (schorsing, terug
eind oktober) en Ilias Akhomach (blessure, terug half november). **Górnik Zabrze – Legia Warszawa**
op rust: Górnik had 3 dagen tegen 5 bij Legia, precies het criterium (≤ 4 dagen én ≥ 2 dagen minder
dan de tegenstander). Die tweede is duur — de Górnik-thuiszege @2,16 staat vijfde op de ruwe
dagranglijst. De poort houdt alleen tegen en stelt `my_prob` niet bij; er is geen enkele meting die
zegt hoeveel procentpunt een uitvaller of een rustdag waard is, en het contextlogboek staat vandaag
op 1739 duels met r = −0,044 en t = −1,70 — nog steeds niets.

**Poort 8 hield zes selecties over twee wedstrijden tegen; `poort8_ruw` geen enkele.** Le Havre – PSG
(sterkste: Le Havre +1.5 @2,09, +12,98 pp) en Zulte Waregem – Club Brugge (Zulte-Waregem +1.25
@2,04, +6,65 pp). Dat `underdog_ruw` leeg blijft is bij een herijking die vrijwel de identiteit is
(a = 0,985, b = −0,010) te verwachten: de twee schalen liggen dan bijna op elkaar. **Tel die twee
reeksen nooit bij elkaar op** — `underdog` staat op 251 afgewikkelde gevallen en −2,8%,
`underdog_ruw` op 17 en −8,8%; het zijn twee populaties. `sides.check` is met `today=DAY` aangeroepen
zodat het venster van 25 t/m 30 september uit `LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in plaats
van geraden.

---

## De bevinding — een gepubliceerde tip stond ook in het logboek van tegengehouden tips

**`shadow.py collect` boekte een selectie die §5b op rangorde had gepubliceerd ook als afgewezen
kandidaat.** Vandaag concreet: **Lille – Lens, Over 2.5 @1,94** stond als tweede regel in
`data/picks.jsonl` **en** met `failed_gate = herijking` in `data/shadow.jsonl`, terwijl geen enkele
poort hem heeft tegengehouden.

**Waarom dit nieuw is en geen oude slordigheid.** Zolang `EDGE_THRESHOLD_FULL` een **poort** was
kon dit niet voorkomen: een `zonder_herijking`-blok beschrijft per definitie een selectie die de
drempel niet haalde en dus niet gepubliceerd kón worden. Sinds §5b op 20 september de drempel in een
**afkapping** heeft veranderd, kan dezelfde selectie wél op rangorde in de lijst komen — en dan
staat ze in beide logboeken. Dat telt twee kanten op: de bet staat in de opbrengst van het logboek
én in die van de poort die hem niet heeft tegengehouden. Het is dezelfde stille faalvorm als
`calibration.py settle` en het Serie B-id: **niets klaagt**, beide bestanden blijven geldig en
`ledger.py validate` blijft groen.

**Gerepareerd in `scripts/shadow.py`.** `cmd_collect` leest nu `data/picks.jsonl` voor dezelfde run
en dag en slaat een kandidaat over waarvan **markt én koers** gelijk zijn aan een gepubliceerde
pick. Dat is exact de vergelijking die `_dubbel` al deed voor een `near_miss` tegen
`poort8_geblokkeerd`, `poort8_ruw` en `poort9_geblokkeerd` (3 okt en 12 okt); ze ontbrak alleen voor
de categorie die sinds §5b kan botsen. Dit is geen nieuwe regel maar de uitvoering van een
bestaande: §1e punt 2 ("nooit dezelfde selectie twee keer") en §5a punt 2.

**En de historie is nagelopen, want een reparatie zonder terugblik meet nog steeds het verkeerde
getal.** Over alle 1515 rijen zijn tien paren gevonden waar een schaduwrij dezelfde markt en koers
heeft als een gepubliceerde pick:

- **Twee zijn dezelfde fout als vandaag en zijn verwijderd:** Wrexham – Southampton, Over 2.5 @1,78
  (gewonnen) en Hibernian – Aberdeen, 1 @1,8036 (verloren), beide van 19 september, beide
  `failed_gate = herijking`, beide met een pick die niet `void` is. Dat zijn precies twee van de
  vijf rijen die §3 Stage -2 noemt als op 27 september uit tak `elu4ga` gehaald — ze zijn dus via
  een merge binnengekomen en daarna nooit tegen `picks.jsonl` gelegd.
- **Acht zijn iets anders en zijn NIET aangeraakt:** daar staat de pick op `void` (23 en 31 aug,
  4 sep). Een void pick valt buiten de ROI, dus er wordt niets dubbel geteld. Waaróm die acht void
  zijn is niet uitgezocht; dat staat onder "Openstaand".

**Wat de correctie met de meting doet.** De reeks `herijking` gaat van **59 naar 57** afgewikkelde
gevallen en van **−3,3% naar −3,1%**. De conclusie eronder verandert niet — de herijking houdt nog
steeds licht verliesgevende kandidaten tegen en blijft dus staan. Maar §6d zegt zelf dat bij deze
aantallen één verkeerd geboekte regel zwaarder weegt dan alles wat de poort werkelijk doet (de
Bodø/Glimt-regel van 12 augustus verschoof een ROI met 81 procentpunt), en dan hoort hij goed te
staan.

---

## Stand van het logboek

### `ledger.py stats`

```
{blok('ra_oct30_ledgerstats.txt')}
```

### `shadow.py stats`

```
{blok('ra_oct30_shadowstats.txt')}
```

### `recalibrate.py show` (§1g)

```
{blok('ra_oct30_recalibrateshow.txt')}
```

**`fitted_through` staat op 2026-10-28** en dat is de vórige **rundag** — 29 oktober is niet
gedraaid. §6b-5c eist dat die datum op of na de vorige rundag staat, en dat is gehaald. De 135
waarnemingen die nog open stonden zijn vanmorgen door `calibration.py settle` afgewikkeld **voordat**
de fit is gelezen.

### `calibration.py stats` (§6e)

```
{blok('ra_oct30_calibrationstats.txt')}
```

### `ctxlog.py stats` (§1c)

```
{blok('ra_oct30_ctxlogstats.txt')}
```

### `margins.py stats` (§6f)

```
{blok('ra_oct30_marginsstats.txt')}
```

### `margins.py stats --since 2026-09-20` (§6b-5f)

```
{blok('ra_oct30_margins_since.txt')}
```

### `margins.py goalbias` (§6g)

```
{blok('ra_oct30_marginsgoalbias.txt')}
```

**Lees die twee tabellen apart, zoals de leeswijzer eronder zegt.** De bovenste meet het **model**
(z = +0,99 over 1752 duels: de lambdas kloppen gemiddeld), de regels eronder meten de **selectie**
(Under gespeeld: +0,609 doelpunt per duel, z = **+3,81** over 107 gevallen; Over gespeeld: −0,296,
z = −1,25 over 60). De vormfout staat in de tweede tabel: massa van 2 doelpunten (−1,4 pp) naar 4
(+1,1) en 5 (+1,4), waardoor P(Under 2.5) 2,2 pp te hoog staat. **Tel die twee nooit op** — de ene
meet het model, de andere de keuze.

De Under-reeks is sinds 28 oktober van **z = +4,04 over 103** naar **z = +3,81 over 107** gegaan: de
vier Unders van woensdag wonnen, dus de reeks is iets afgezwakt. Dat is nog ruim boven de twee
standaardfouten en het blijft de gemeten reden waarom poort 9 staat.

**Keuze (a) van 11 oktober is op 28 oktober uitgevoerd, gemeten en AFGEWEZEN** (§6g): de
voorgeschreven vormcorrectie verergert het symptoom, is op een gepaarde toets meetbaar slechter en
élke kandidaat draait van teken tussen de twee `shrink`-populaties; de vormfout blijkt grotendeels
een nalatenschap van `shrink = 0.80` en is op 19 september al door die wijziging opgelost. **Lees
het uitblijven van die trigger dus niet als een openstaande taak** — er is niets gerepareerd omdat
er niets te repareren viel, en poort 9 hoort pas opnieuw ter discussie als `gridfit.py measure` op
een grotere homogene reeks iets anders zegt.

### `toplist.py` (§5a)

```
{blok('ra_oct30_toplist.txt')}
```

---

## Wedstrijden

{wedstrijden}

---

## Openstaand

1. **Twee rekenstappen zijn het oneens over het label van Lille – Lens.** +7,99915 pp tegen een lat
   van 8,0: `ra_oct30_analyze.py` toetst op de float en zegt "net niet", `toplist.py` leest de
   afgeronde 8,00 en zegt "net wel". Voor welke regels er worden gepubliceerd maakt het niets uit.
   De nette oplossing is dat beide stappen dezelfde afgeronde waarde gebruiken; niet vandaag
   doorgevoerd, omdat een run geen vergelijking in de rekencode verzet op een randgeval van één dag.
2. **Acht paren waar een schaduwrij dezelfde markt en koers heeft als een `void` pick.** 23 en
   31 augustus en 4 september. Een void pick valt buiten de ROI, dus er wordt niets dubbel geteld;
   maar het is niet uitgezocht waarom die picks void staan, en dat is een audit en geen regel.
3. **Een Under onder de 8,0 pp wordt door geen van beide latten getoetst.** Gevolg van §5b plus
   §1h, vandaag twee keer voorgekomen. Op 28 oktober als besluit aan de gebruiker voorgelegd; staat
   ook vandaag in het dagrapport met `owner = besluit`, en wordt niet als nieuwe vraag gesteld.
4. **Vier actieve sportkeys staan niet in `oddsapi.SPORT_KEYS`:** `soccer_brazil_serie_b`,
   `soccer_germany_liga3`, `soccer_sweden_superettan` en `soccer_uefa_nations_league`. Alle vier
   buiten de Run A-runlijst, dus werk voor Run B en Run C. Niet hier opgelost: een run raakt geen
   runlijst aan die niet de zijne is.
5. **`scripts/settling.py` heeft nog de oude deelverzamelingsregel voor namen.** Onveranderd sinds
   27 oktober. Daar is ze met opzet ruim en beslist lookup op het **paar** thuis-en-uit plus de eis
   van precies één kandidaat, dus de rem is er anders — maar het is hetzelfde patroon. Vandaag niet
   aangeraakt: een poort verzetten die niet knelt is geen werk dat een run op eigen initiatief doet.
6. **De run is om 07:29 NL afgegaan in plaats van rond 03:30.** §0 eist de rapporten om 06:30,
   omdat de gebruiker tussen 07:00 en 08:00 inzet. Vandaag ging de notificatie om 07:55 uit — net
   binnen het venster. Dit is een eigenschap van de scheduler en niet van de repo; het staat hier
   zodat een structureel late run zichtbaar wordt in plaats van elke ochtend opnieuw te worden
   opgemerkt en vergeten.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-10-30-run-a.md", "w").write(MD_TEXT)
print("runs/2026-10-30-run-a.md geschreven —", len(MD_TEXT), "tekens")
