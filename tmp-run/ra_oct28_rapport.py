# -*- coding: utf-8 -*-
"""Run A, 28 okt 2026 — het markdown-runrapport samenstellen.

De uitvoer van de logboekscripts wordt LETTERLIJK ingevoegd uit de .txt-bestanden die deze run
heeft weggeschreven, niet overgetypt: §6b eist dat beide rapporten van dezelfde run dezelfde
getallen tonen, en overtypen is precies hoe ze uiteen gaan lopen.
"""
import json

def blok(pad):
    return open(f"tmp-run/{pad}").read().rstrip()

res = json.load(open("tmp-run/ra_oct28_results.json"))
top = json.load(open("tmp-run/ra_oct28_top_a.json"))
picks = json.load(open("tmp-run/ra_oct28_picks_a.json"))
st = json.load(open("data/run-state/2026-10-28-run-a.json"))
ART = "https://claude.ai/artifact/1J6FTLfqMbPpyD3FqX8Gsc"
MD = "https://github.com/aistref/football/blob/main/runs/2026-10-28-run-a.dagrapport.md"

TOELICHTING = {
 "Serie A (ITA)": "5 duels, 18:30-20:45 NL — alle vijf doorgerekend, geen bet",
 "Scottish Premiership (SCO)": "6 duels, 20:45-21:00 NL — alle zes doorgerekend, 1 bet",
 "League Cup (ENG)": "5 duels, 20:30-21:00 NL — alle vijf doorgerekend (Premier League onderling), 1 bet",
 "DFB Pokal (GER)": "8 duels, 18:00-20:45 NL — 4 doorgerekend, 4 op `NONE`, 1 bet",
 "KNVB Beker (NED)": "9 duels, 18:45-21:00 NL — 2 doorgerekend, 7 op `NONE`",
 "Premier League (ENG)": "weer op 1 nov 17:30",
 "La Liga (ESP)": "weer op 1 nov 14:00",
 "Bundesliga (GER)": "weer op 1 nov 15:30",
 "Ligue 1 (FRA)": "weer op 1 nov 15:00",
 "Championship (ENG)": "weer op 30 okt 21:00",
 "Eredivisie (NED)": "weer op 1 nov 12:15",
 "Primeira Liga (POR)": "weer op 1 nov 16:30",
 "Belgian Pro League (BEL)": "weer op 1 nov 13:30",
 "Super Lig (TUR)": "weer op 1 nov 11:30",
 "Danish Superliga (DEN)": "weer op 1 nov 14:00",
 "Ekstraklasa (POL)": "weer op 2 nov 18:00",
 "UEFA Champions League": "hervat op 3 nov 18:45",
 "UEFA Europa League": "hervat op 4 nov 16:30",
 "UEFA Conference League": "hervat op 5 nov 18:45",
 "FA Cup (ENG)": "volgende ronde 6 nov 20:30 (BetExplorer; geen fotmob_id in coverage.json)",
 "Coppa Italia (ITA)": "volgende ronde 1 dec 21:00 (BetExplorer; geen fotmob_id in coverage.json)",
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
                f"bet_beide: {cand.get('bet_beide')}\n```\n")
        else:
            reden = m.get("reason") or "geen publiceerbare selectie"
            wb.append(f"{kop}\n\n```\nData: {m['tier']}\nGEEN BET — {reden}\n```\n")
wedstrijden = "\n".join(wb)

MD_TEXT = f"""# Run A — 2026-10-28

**Woensdag 28 oktober 2026.** Vijf van de eenentwintig competities uit de runlijst speelden, samen
**33 duels** in het inzetvenster — het drukste Run A-programma van deze maand — en **22 ervan zitten
in een beker**: vijf in de League Cup, acht in de DFB Pokal en negen in de KNVB Beker, naast een
midweekse Serie A-ronde van vijf en een volle Schotse speelronde van zes. Drieëndertig onder de
woensdagcap van 40, dus de cap bindt nergens. De overige elf competities beginnen hun volgende ronde
op 30 oktober of 1 november, de drie Europese toernooien spelen 3 t/m 5 november. §3 Stage 2 noemt
dat `GEEN WEDSTRIJD`.

**De bevinding van vandaag gaat over de inkoop en niet over de analyse — zie bevinding 1.** De
Scottish Premiership en de League Cup kregen in de runscripts van oktober `sportkey = None` mee,
terwijl beide sleutels bestaan: `soccer_england_efl_cup` staat sinds 10 augustus in
`oddsapi.SPORT_KEYS`, en voor `soccer_spl` noteert `coverage.json` bij die competitie **al sinds
9 september** dat hij werkte — die bevinding is alleen nooit in `SPORT_KEYS` geland.
`api_check.py` kon het niet vinden omdat die controle zijn lijst op de **sleutel** filterde en daar
het woord "scot" in zocht, en `soccer_spl` noemt het land alleen in `title` en `description`. De
controle stond dus elke ochtend groen terwijl ze de verkeerde grootheid mat — dezelfde stille
faalvorm als het Serie B-id (§ `idcheck.py`) en als `calibration.py settle` (§6b-5c). **Het kostte
zeven weken:** de Scottish Premiership draaide van 9 september t/m 27 oktober uitsluitend op het
gratis BetExplorer-marktgemiddelde, en dat gemiddelde gaat daar over maar **drie** boeken. Vandaag
ligt de beste prijs er tussen **+4,90% en +11,95%** boven; bij de vijf League Cup-duels tussen
+4,09% en +6,02%. §1a meet dat verschil op +1,84 procentpunt edge per selectie. Gerepareerd **vóór**
de analyse (§4) in `scripts/oddsapi.py` en `scripts/api_check.py`.

**Gevolg voor vandaag: 20 van de 22 doorgerekende duels hebben een beste prijs met een herleidbare
bookmaker, tegen 11 van de 22 gisteren.** Alleen de twee doorgerekende KNVB Beker-duels draaien nog
op het marktgemiddelde; die competitie heeft werkelijk geen sportkey bij de bron. En de derde regel
van de dag is er rechtstreeks een gevolg van: St. Mirren – Hibernian staat op 1.71 bij Coolbet in
plaats van op een gemiddelde over drie boeken.

**De tweede bevinding is kort en bevestigt iets van gisteren.** De voorvoegselregel die op
27 oktober in `teamnames.is_abbreviation` is gezet, hield vandaag meteen iets tegen: de oude
deelverzamelingsregel koppelde **Excelsior Maassluis** (amateurclub, KNVB Beker) aan **Excelsior**
in de Eredivisie-stand. De zelftest over 66 namen geeft precies dat ene verschil. Zonder de
reparatie was Excelsior Maassluis – SC Heerenveen doorgerekend met de xG van Excelsior Rotterdam
achter de thuisploeg, en **geen van de negen poorten kan dat zien** — het is geen te ruime kans maar
een verkeerde ploeg. Zie bevinding 2.

**Elf van de 33 duels komen op `NONE` uit, en dat is bij een bekerronde de verwachting.** Zeventien
duels zijn `FULL`, vijf `LIGHT` en elf `NONE`. Zes NONE-duels betreffen een ploeg die in geen enkele
divisie staat waarvoor een gemeten omrekenfactor bestaat (SSV Jeddeloh uit de Regionalliga, en de
vijf amateurclubs Genemuiden, JOS Watergraafsmeer, Quick Boys, VVSB en Excelsior Maassluis); de
andere vijf vallen op `promotion.conversion_in_range` — de Coventry-val (1. FC Nürnberg, Magdeburg,
Holstein Kiel, MVV Maastricht en TOP Oss). **Drie duels zijn door `shared_lower_division` gered**
(§4, 15 sep): Dynamo Dresden – Schalke 04 en Hannover 96 – Kaiserslautern in de 2. Bundesliga
(`FULL`, want die divisie heeft xG) en VVV-Venlo – Vitesse in de Eerste Divisie (`LIGHT`, want die
niet). Daar valt niets te overbruggen, dus geldt "een omgerekende ploeg is nooit `FULL`" er niet: er
is niets omgerekend. **En een van die drie is een bet geworden** — Hannover 96 – Kaiserslautern, de
tweede regel van de dag.

| | |
|---|---|
| Gepubliceerd | **3** — AFC Bournemouth – Aston Villa (1X2 Bournemouth @ 2.32), Hannover 96 – Kaiserslautern (AH −0.25 @ 2.06), St. Mirren – Hibernian (Under 3 @ 1.71) |
| Waarvan boven de eigen lat | **2 van 3** — +15,39 pp en +11,14 pp; de derde staat op +6,43 pp en is op rangorde gepubliceerd (§5b) |
| `bet_beide` | **2 van 3 TRUE**; de regel onder de lat haalt hem op geen van beide schalen |
| Gekwalificeerd, niet gepubliceerd | **0** — de lijstlengte bindt niet (3 publiceerbare selecties, 3 plekken) |
| Afgekapt door de cap | **0** van 40 |
| Doorgerekend | 22 van 33 duels, **299 selecties** over alle zes de markten; `progress.py verify` groen op 22 van 22 |
| Bronstoringen | **0** |
| Credits | 26 van een dagplafond van 2326; 18.607 over met vier dagen tot de maandwissel |

**Drie regels uit drie competities en drie markten, en dat is op zichzelf nieuws.** Op 26 en
27 oktober stonden alle drie de regels in Serie A en alle drie op de weinig-doelpuntenkant; vandaag
is het een 1X2, een Asian Handicap en een Over/Under, uit de League Cup, de DFB Pokal en de Scottish
Premiership. §5b waarschuwt dat een lijst die dagen achtereen uit één hoek komt een signaal is over
het **model** en niet over de rangorderegel; die eenzijdigheid is vandaag weg.

**Wat er wél bij de derde regel hoort en niet in een voetnoot: St. Mirren – Hibernian staat op de
Under-kant, en die staat meetbaar scheef (§6g).** `margins.py goalbias` van vanmorgen, over **1717**
doorgerekende duels: het model als geheel klopt (verwacht 3,031 doelpunten per duel tegen werkelijk
3,075, z = +1,05), maar er is massa verschoven van 2 doelpunten (−1,5 pp) naar 4 (+1,0) en 5 (+1,4).
Daardoor staat `P(Under 2.5)` over alle duels **2,2 pp te hoog** en `P(Under 3.0)` 1,7 pp — bij élk
duel, vóór er iets is gekozen. Daar bovenop het selectie-effect: in de **103** duels waarin werkelijk
een Under is gespeeld vielen er **+0,659 doelpunt per duel méér** dan de eigen lambda zei, **z =
+4,04** — de hoogste stand die deze reeks tot nu toe heeft gehad (11 oktober: +0,68 over 49 gevallen,
z = +2,91). Op de Over-kant gebeurt dat niet: −0,296 over 60 gevallen, z = −1,25. **Trek dus ongeveer
twee procentpunt van de genoemde kans af.** Het onafhankelijke cijfer erbij: Pinnacle zet
P(Under 2.75) bij dit duel op 47,4% tegen 53,2% voor dit model — 5,75 pp lager, dezelfde kant op als
de gemeten scheefstand.

**Dagrapport (§6c):** <https://claude.ai/artifact/1J6FTLfqMbPpyD3FqX8Gsc> ·
Markdown-terugval: <https://github.com/aistref/football/blob/main/runs/2026-10-28-run-a.dagrapport.md>

De pagina is preventief in Chromium gerenderd (`tmp-run/ra_oct28_rendercheck.js`, de controle die
§6c sinds 15 oktober voorschrijft): 17.399 px hoog, 42.098 zichtbare tekens, 53 blokken, 6 tabellen,
3 bets, **nul console- of pagefouten**, en correct in zowel licht als donker. Komt de Artifact bij de
gebruiker tóch niet door, dan is opnieuw publiceren zinloos en is de Markdown-link hierboven het
antwoord.

---

## Branchaudit (Stage -2)

**De repo kwam als ondiepe kloon aan, en dat is precies de valkuil die §3 Stage -2 beschrijft — en
ze is vanmorgen bijna verkeerd gelezen.** `git rev-parse --is-shallow-repository` gaf `true`, en de
naïeve telling vóór het unshallowen zag **69 van de 79 takken met "eigen" commits** (van 6 tot 581
stuks), met voor elk van die takken een **lege `merge-base`**. Van binnenuit ziet dat eruit als een
`main` met een verse, niet-verwante geschiedenis die op 18 oktober zou zijn begonnen, en dat is
precies de verkeerde conclusie: de knip van de ondiepe kloon lag daar. Na
`git fetch --unshallow origin` (645 commits lokaal in plaats van 55) is het **0 van de 79**, en
`git merge-base origin/main origin/claude/bold-curie-09mzgz` geeft weer gewoon een commit. Woord
voor woord de meting van 20 augustus 2026.

Daarna de controle die wél iets zegt — `scripts/branchaudit.py`, **per record op de inhoud** en niet
op de commitgraaf, over alle zes de logboeken:

| Logboek | Records op `origin/main` | Uitkomst |
|---|---|---|
| `data/picks.jsonl` | 480 | VOLLEDIG |
| `data/shadow.jsonl` | 1490 | VOLLEDIG |
| `data/context-log.jsonl` | 1715 | VOLLEDIG |
| `data/calibration.jsonl` | 6404 | VOLLEDIG |
| `data/source-health.json` | 136 bladpaden | VOLLEDIG |
| `data/coverage.json` | 302 bladpaden | VOLLEDIG |

**Niets te verenigen: elk record dat op een tak staat, staat ook op `origin/main`.** De enige
afwijking is `sources.oddspapi` (5 bladpaden), die het script zelf aanmerkt als bekend besluit —
OddsPapi is op 30 augustus 2026 verwijderd na de overstap naar het 20K-creditplan. Dat is ook
onafhankelijk nagegaan vóór het unshallowen, op de pick-id's van alle 78 takken: **nul** pick-id's
die hier ontbreken, en `prompts/_shared-rules.md` staat op `main` op 3587 regels, tevens de langste
versie op alle takken.

**Openstaande picks van een run die op een andere tak nooit is afgewikkeld: geen.** `ledger.py open`
stond bij de start op 6 picks en `shadow.py open` op 7 schaduwrijen, alle dertien van 27 oktober en
alle dertien van deze tak; na Stage 0 geven beide "Geen picks klaar om af te wikkelen".

**Deze sessie draait op branch `claude/stoic-davinci-y66391` en pusht naar `main`,** zoals §6a
voorschrijft en zoals de scheduler-tekst expliciet toestaat. Er is dus niets te melden over een run
die niet op `main` staat.

## Bronstatus deze run

### De uitvoer van `api_check.py`, letterlijk (§3 Stage 3)

```
{blok('ra_oct28_apicheck.txt')}
```

**De sleutels:** The Odds API werkt en is niet afgewezen; `API_FOOTBALL_KEY` ontbreekt en dat is
sinds 27 september een besluit van de gebruiker en geen gat — niet als actiepunt gemeld, wel hier
als boekhouding (§3). De uitzondering van §3 punt 3 is niet aan de orde: Fotmob leverde deze run
zonder fout, voor alle 33 duels inclusief de context.

**Deze uitvoer is vanmorgen veranderd, en dat is bevinding 1.** Waar hier tot gisteren een lijst
"relevante sportkeys" stond die op de **sleutel** werd gefilterd, staat er nu per bekende sleutel of
hij vandaag actief is (28 van 29; alleen `soccer_italy_coppa_italia` niet, en de Coppa Italia speelt
inderdaad pas 1 december) plus de actieve sleutels die de repo **niet** kent. Die tweede lijst wijst
vijf gaten aan die buiten de Run A-runlijst vallen en dus voor Run B en C zijn:
`soccer_norway_eliteserien`, `soccer_sweden_superettan`, `soccer_germany_liga3`,
`soccer_spain_copa_del_rey` en `soccer_uefa_nations_league`. De twee resterende regels
(`soccer_germany_bundesliga_women` en `soccer_uefa_champs_league_women`) staan in geen enkele
runlijst.

### `scripts/idcheck.py` — alle 33 competitie-id's groen

```
{blok('ra_oct28_idcheck.txt').splitlines()[-1]}
```

De drie bekers staan hier met opzet niet bij: een beker heeft geen stand, dus `idcheck.py` kan hun
id niet op een bruikbare tabel controleren. Dat is ook de reden dat hun daglijst-id's (133, 209,
235) niet onder `fotmob_id` in `coverage.json` horen — daar zou deze controle elke run een vals
alarm van geven op precies de vraag waarvoor ze is gebouwd.

### `data/source-health.json` is bijgewerkt

Acht bronregels herschreven met wat deze run gemeten heeft: `fotmob` (33 contextblokken, en de
stadionvelden zijn weer gevuld), `the_odds_api` (de twee sportkeys van bevinding 1), `oddsapi`
(26 van 2326 credits), `betexplorer` (tien fixturepagina's, nul faalmodi), `understat` (twee duels),
`api_football` (besluit, geen gat), `teamnames` (de regel van gisteren die vandaag beet) en
`settling`. Geen enkele bron op een foutstatus.

### Twee verplaatste wedstrijden, en de stadionvelden zijn weer gevuld (§1c)

`context.check_venue` is voor alle 33 duels gedraaid en gaf **twee keer** `relocated = true`:

- **SSV Jeddeloh – Hertha BSC** wordt gespeeld in het **Marschwegstadion (Oldenburg)** en niet in de
  HASKAMP-Arena — een Regionalliga-club die voor een tweededivisionist naar een groter stadion in de
  buurt verhuist.
- **JOS Watergraafsmeer – NAC Breda** staat op **Sportpark Goed Genoeg (Amsterdam)** en niet op
  Sportpark Drieburg.

Beide duels komen op `NONE` uit, dus geen gepubliceerde bet wordt geraakt. **Maar dat de controle
weer aanslaat is zelf de waarneming:** op 25, 26 en 27 oktober gaf de respons bij **geen enkel**
duel een stadionnaam, en `relocated = false` betekende daar dus "niet gemeten" in plaats van "gemeten
en in orde" — de stille leegte die het runrapport van die dagen expliciet benoemt. Vandaag is het
stadion bij **alle 33** duels gevuld. Wat de controle hoe dan ook niet vangt, is dat een fixture van
eigenaar is gewisseld; dat is nieuws en geen data (Rennes – PSG, 23 aug 2026).

### Opstellingen

`lineupType` gaf bij geen enkel duel `confirmed`, wat te verwachten is om 03:30 NL bij aftrappen
tussen 18:00 en 21:00: 5 keer `predicted`, 22 keer `lastStarting11`, 2 keer `unavailable` en 4 keer
leeg. Alle 33 duels leverden een contextblok; **26** ervan zijn in het contextlogboek beland. De
zeven die ontbreken zijn de amateurclubs van de KNVB Beker: daar is geen selectiewaarde, dus
`ctxlog.out_share` is `None` en `ctxlog.py` slaat de rij terecht over in plaats van er een nul van
te maken.

### De runlijst is door een tweede bron bevestigd (§1)

Fotmob levert de daglijst, BetExplorer de fixturepagina per competitie. **Negentien van de negentien**
competities met een slug zijn het eens, inclusief de dertien die vandaag `GEEN WEDSTRIJD` hebben:
**33 duels bij Fotmob tegen 33 bij BetExplorer**, nul afwijkingen, geen enkele bron die faalde
(`ra_oct28_bevestiging.py`). Ook de drie bekers met een ronde zijn door twee bronnen bevestigd: 5, 8
en 9 duels bij BetExplorer en dezelfde 5, 8 en 9 in de Fotmob-daglijst. De twee bekers zonder ronde
staan alleen op BetExplorer, met als eerstvolgende ronde FA Cup 6 november 20:30 en Coppa Italia
1 december 21:00.

**Let op de breedte van het gratis marktgemiddelde:** 16 boeken bij Serie A en 11 bij de DFB Pokal,
maar maar **drie** bij de Scottish Premiership en de League Cup. Dat is precies waarom het uitmaakt
dat die twee vanaf vandaag ook een beste prijs hebben (bevinding 1).

**Tijdzone:** BetExplorer labelt in UK-tijd, sinds de wintertijd GMT tegen CET in Nederland — nog
steeds precies één uur verschil, dus het venster `[28.10. 08:00 NL, 29.10. 08:00 NL)` is in UK-tijd
`[28.10. 07:00, 29.10. 07:00)`.

### Het inzetvenster (§3 Stage 1)

`runwindow.matches_for_run` met het venster `[28.10. 08:00 NL, 29.10. 08:00 NL)`; voor de drie bekers
is dezelfde band met de hand toegepast in `ra_oct28_cupmatches.py`, omdat die competities geen
`fotmob_id` in `coverage.json` hebben. **Alle 33 duels stonden op de daglijst van 28 oktober**
(`source_day` = DAY, geen enkel duel uit de band 00:00–08:00 van morgen) en **alle 33 zijn
`playable`**: de vroegste aftrap is 18:00 NL (vier DFB Pokal-duels) en de laatste 21:00 NL
(Liverpool – Chelsea en Excelsior Maassluis – SC Heerenveen). Geen duel was al afgetrapt voordat de
gebruiker kon inzetten, en er is geen carry-over-band. `runwindow` rekent met `zoneinfo`, dus het
venster is in échte NL-tijd gemeten (CET, +01:00).

### Wat anderen voorspellen (Stage 5, stap 2)

Geschreven voorspellingen zijn grotendeels niet te halen — §3 Stage 5 meet sinds 20 september dat
Forebet 403 geeft, de Pinnacle-artikelroute 404, Matchbook 530 en voetbalwedden.net de duels van de
dag niet noemt. Wat deze stap vandaag invult is de **prijs van Pinnacle apart**, los van de beste
prijs waarop wordt gespeeld.

**1X2** (`ra_oct28_pinnacle.py`): **20 van de 33** duels hebben een Pinnacle-1X2 — ruim meer dan de
drie van gisteren, en dat is opnieuw bevinding 1. Gemiddelde Pinnacle-marge **4,18%** (tegen 6 à 10%
bij de rest), gemiddelde absolute afstand tot het eigen oordeel **4,01 pp**, zonder systematische
kant. Twee uitschieters horen genoemd: bij **Hannover 96 – Kaiserslautern** staat dit model
**14,2 pp boven** Pinnacle op de thuiszege (55,1% tegen 40,9%) — en dat is precies het duel dat de
tweede regel van de dag levert — en bij Paderborn – VfB Stuttgart 8,6 pp boven Pinnacle. **Lees die
eerste als een waarschuwing en niet als een bevestiging:** §1g meet dat de bookmaker scherper schat
dan dit model (Brier 0,2449 tegen 0,2657 over het hele logboek), dus de grootste afstand tot
Pinnacle is eerder de grootste modelfout dan de grootste vondst.

**Doelpunten** (`ra_oct28_pinnacle_ou.py`, push-gecorrigeerd zoals op 25 oktober gerepareerd): 20
(duel, lijn)-paren, gemiddeld **+1,65 pp** boven Pinnacle op de Under-kant en **11 van de 20** keer
erboven — dezelfde richting als de vormfout van §6g, maar veel minder uitgesproken dan gisteren
(+9,93 pp over 3 duels). Bij St. Mirren – Hibernian staat dit model 5,75 pp boven Pinnacle op
P(Under 2.75).

**Harde grens (§2/§4):** geen van deze getallen gaat in `my_prob` of in `prob_sources`. Ze horen in
de vergelijking en niet in de kansschatting.

### Understat — de tweede, onafhankelijke xG-bron (§4)

Eén van de vijf Understat-competities speelde vandaag (Serie A), en voor **twee van de vijf** duels
is een tweede, onafhankelijk xG-model geleverd: Milan – Bologna en Genoa – Juventus. Bij de andere
drie staat minstens één ploeg niet in de Understat-tabel van vorig seizoen (Venezia en Monza zijn
promovendus; Parma en Udinese ontbreken op naam). **Geen van de drie gepubliceerde regels heeft dus
een Understat-arm** — een ongunstiger stand dan gisteren, toen alle drie de bets uit Serie A kwamen.
De 22 bekerduels en de zes Schotse duels leunen uitsluitend op Fotmob, in twee doorsnedes van
dezelfde meting; op een bekerdag is de afhankelijkheid van die ene bron dus groter dan op een gewone
competitiedag, en dat is de reden dat §3 een uitvallende Fotmob vooraan in de notificatie wil hebben.

### Vroeg-seizoenscorrectie en het competitieniveau (§3 Stage 5)

`model.uplift_observations` + `early_season_uplift`: factor **1,1146**, berekend uit een gepoolde
**1,1355** over **44 speeldagen** in **vijf** competities. **Geen enkele competitie is overgeslagen
in de pool** (`overgeslagen` is leeg): de vijf zijn Serie A, de Scottish Premiership en de drie
basisdivisies van de bekers (Premier League, Bundesliga, Eredivisie), alle op 7 tot 10 speeldagen van
een seizoen van 33 tot 38 — ruim onder de helft van `SEASON_MATURE_SHARE`.

Alle **zeven** competitiebases lopen daarom de route `vorig+uplift`. `model.league_level` per basis
(thuis / uit / basis-xG, en de stand van het lopende seizoen):

| Basis | Route | thuis / uit / basis | lopend seizoen |
|---|---|---|---|
| Serie A (ITA) | `vorig+uplift` | 1,423 / 1,282 / 1,422 | 9 van 38 |
| Scottish Premiership (SCO) | `vorig+uplift` | 1,762 / 1,289 / 1,523 | 10 van 33 |
| League Cup (ENG) → Premier League | `vorig+uplift` | 1,701 / 1,364 / 1,424 | 8 van 38 |
| 2. Bundesliga (GER) | `vorig+uplift` | 1,818 / 1,450 / 1,575 | 9 van 34 |
| DFB Pokal (GER) → Bundesliga | `vorig+uplift` | 1,982 / 1,625 / 1,669 | 7 van 34 |
| KNVB Beker (NED) → Eredivisie | `vorig+uplift` | 2,007 / 1,534 / 1,657 | 10 van 34 |
| Eerste Divisie (NED) | `vorig+uplift` | 1,936 / 1,625 / 1,716 | 12 van 38 |

**Let op de factor, want hij staat hoger dan de 1,0606 van eerder deze maand.** De pool bestaat
vandaag uit andere competities — drie bekerbases plus Serie A en Schotland — en §3 Stage 5
waarschuwt uitdrukkelijk dat de pool competitie-overstijgend is en dus meebeweegt met wie erin zit.
Dat is geen drift in de meting maar een andere steekproef.

**De meting naast de markt** (controleren, niet fitten — §2): de gemiddelde absolute afstand van het
eigen 1X2 tot het Pinnacle-oordeel is 4,01 pp over 20 duels, zonder systematische kant.

## Afwikkeling (Stage 0)

Zes picks en zeven schaduwrijen van 27 oktober afgewikkeld. **Alle dertien zijn competitieduels, dus
`status.scoreStr` van Fotmob *is* de stand na 90 minuten** en er hoefde geen doelpuntminuut te worden
opgezocht (§6d). Daarna stonden `ledger.py open` en `shadow.py open` beide op nul.

| Pick | Markt | Koers | Uitslag | Resultaat | verwacht/werkelijk doelpunten |
|---|---|---|---|---|---|
| Cesena – Empoli | 1X2 — Cesena | 2.27 | 2-1 | **gewonnen** | — (uitkomstmarkt) |
| Sassuolo – Lazio | Under 2.75 | 2.06 | 2-6 | verloren | 2,45 verwacht / **8** werkelijk |
| Roma – Cagliari | Under 3 | 1.84 | 4-2 | verloren | 2,55 / 6 |
| Torino – Como | BTTS — nee | 2.3524 | 1-3 | verloren | — (beide scoorden) |
| Luton Town – Doncaster Rovers | Under 3.5 | 1.6272 | 3-1 | verloren | 2,72 / 4 |
| Virtus Entella – Avellino | BTTS — nee | 1.9212 | 1-1 | verloren | — (beide scoorden) |

Schaduwrijen: **3 gewonnen, 4 verloren** — Padova – Südtirol Under 2.5 en Mantova – Cremonese
AH +0.25 en Oxford – Stockport Double Chance gewonnen; Hamburger SV – Eintracht Frankfurt, AIK –
Elfsborg, Padova – Südtirol AH +0.25 en Luton – Doncaster AH +1 verloren.

Ook gedraaid: `calibration.py settle` (57 waarnemingen afgewikkeld; 6324 van 6351 compleet) en
`ctxlog.py settle` (30 wedstrijden). `recalibrate.load_fit().fitted_through` staat daarmee op
**2026-10-27**, dus op de vorige rundag, zoals §6b-5c eist.

### De reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)

**1. Klopte de redenering, of klopte alleen de uitkomst?** Bij de enige winnaar klopten beide:
Cesena won thuis van Empoli met 2-1, en dat was een uitkomstmarkt waar de rekensom Cesena ook als de
sterkere had. Bij de vijf verliezers klopte de redenering **niet**, en niet marginaal. Sassuolo –
Lazio werd **2-6** tegen een eigen verwachting van 2,45 doelpunten — vijfeneenhalf doelpunt ernaast,
en de grootste enkelvoudige afwijking die deze routine in oktober heeft gezien. Roma – Cagliari 6
tegen 2,55 verwacht, Luton – Doncaster 4 tegen 2,72. Over de drie Over/Under-picks samen: **18
werkelijke doelpunten tegen 7,7 verwacht.** De twee BTTS-picks ("nee") hadden allebei een wedstrijd
waarin beide ploegen scoorden.

**2. Deden de poorten die iets tegenhielden hun werk, in dít geval?** Gemengd en klein van aantal.
Van de zeven schaduwrijen zijn er drie gewonnen, waarvan er één op `underdog` sneuvelde
(Oxford – Stockport, Double Chance) — die poort kostte daar dus een winnaar. Twee rijen op
`tweede_methode` (Hamburger SV, AIK) waren verloren, dus daar deed poort 5 zijn werk. Bij Padova –
Südtirol zijn twee rijen van hetzelfde duel verschillend afgelopen (Under 2.5 gewonnen, AH +0.25 bij
Südtirol verloren), wat laat zien dat het hier om de selectie gaat en niet om de wedstrijd.

**3. Zat er een patroon in de dag dat geen toeval kan zijn?** Ja, en het is het patroon van §6g in
zijn scherpste vorm. **Vier van de vijf verliezende picks stonden op de weinig-doelpuntenkant** (drie
Unders en twee keer BTTS "nee"; de twee BTTS-picks tellen in dezelfde richting), en in **alle vier**
viel het werkelijke totaal **boven** de eigen lambda — drie keer meer dan twee doelpunten erboven.
Dat is dezelfde richting als de +0,659 doelpunt per duel die `goalbias` nu over 103 gespeelde Unders
meet, en de z-waarde van die reeks is vandaag van +2,91 (11 oktober) naar **+4,04** gelopen.

**4. En dan de rem erop: wat betekent dit NIET?** Eén dag is geen reeks. Zes picks en zeven
schaduwrijen zijn ver onder de ~30 afgewikkelde gevallen die §6d eist, en één winnaar die poort 8
gisteren tegenhield is één geval op een reeks van **241** die op −4,0% staat. De
`doelpunten_onder`-reeks staat na vandaag op **21** afgewikkelde rijen (42,9% trefkans, −18,3%), nog
steeds onder de dertig. Er wordt op grond van gisteren dus geen enkele drempel, geen gewicht en geen
poort verzet. **Wat deze dag wél doet, is de reeks van §6g van ruis naar hard tillen:** z = +4,04
over 103 gevallen is geen getal meer dat je als toeval kunt lezen, en dat is de reden dat de
reparatie van de oorzaak — keuze (a) van 11 oktober — als besluit in het dagrapport staat.

## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
{dekking}

Geen enkele competitie viel onder `AFGEKAPT`: 33 duels op een cap van 40. De laagste datarijkdom in
de run is **3,5** (JOS Watergraafsmeer – NAC Breda) en de hoogste **6,5**; omdat er niets is
afgekapt zijn er geen twee scores rond de grens te noemen (§3 Stage 4).

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Wedstrijd | Markt / selectie | Koers | Kans | Edge | Score | Tier | Risico | Lat gehaald? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | AFC Bournemouth – Aston Villa | 1X2 — Bournemouth wint | 2.32 (1xBet) | 58,5% | **+15,39 pp** | 9,003 | FULL | Medium | **ja** — boven de lat van 8,0 pp |
| 2 | Hannover 96 – Kaiserslautern | Asian Handicap — Hannover 96 −0.25 | 2.06 (Pinnacle) | 59,7% | **+11,14 pp** | 6,649 | FULL | Medium | **ja** |
| 3 | St. Mirren – Hibernian | Over/Under — Under 3 | 1.71 (Coolbet) | 64,9% | +6,43 pp | 4,174 | FULL | High | nee — op rangorde (§5b) |

**Waarom deze wél en de eerstvolgende net niet.** Er zijn precies drie duels met een publiceerbare
selectie en er passen drie regels in (`MAX_SHORTLIST` = 3, woensdag), dus de lijstlengte bindt niet
en er valt **geen** gekwalificeerde selectie af; `failed_gate = lijstlengte` krijgt vandaag geen
enkele rij. Wat daaronder staat is door een poort tegengehouden (zie "Net niet") of haalt de
ondergrens van 3,0 pp niet die `toplist._publiceerbaar` aanhoudt. `MAX_LIGHT_IN_SHORTLIST` = 2 bindt
niet: alle drie de regels staan op `FULL`.

**Welke selectie binnen de wedstrijd tweede werd** (§1a eist dit per bet):

- **Bournemouth – Aston Villa**: Asian Handicap Bournemouth −0.25 @2.00 (+13,91 pp, score 8,890) —
  dezelfde mening met push-bescherming, en 0,11 lager op score. Derde was Draw No Bet Bournemouth
  @1.68 (score 8,477). Dat zijn drie uitdrukkingen van één bevinding, precies het geval waarvoor de
  0-of-1-bet-regel bestaat.
- **Hannover 96 – Kaiserslautern**: 1X2 Hannover 96 @2.3524 (+11,74 pp, score 6,370) — een **hógere**
  edge dan de gepubliceerde handicap, en toch tweede. Dat is `selection_score` die doet waarvoor hij
  op 14 augustus is gekozen: hij geeft de voorkeur aan een hogere trefkans boven een paar procentpunt
  extra edge, en bij een handicap van −0.25 wordt een gelijkspel half teruggegeven in plaats van
  helemaal verloren.
- **St. Mirren – Hibernian**: BTTS "nee" @2.4112 (+6,66 pp) had een **hogere edge** dan de
  gepubliceerde Under 3 (+6,43 pp) maar een lagere score (2,76 tegen 4,174), omdat de trefkans er
  twintig procentpunt onder ligt. De twee sterkste selecties van dit duel — Under 2.75 @2.04 (+8,81
  pp) en Under 2.5 @2.274 (+8,76 pp) — zijn door **poort 9** tegengehouden; zie hieronder.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Wedstrijd | Markt / selectie | Koers | Ruwe edge | Ruwe score | Uitkomst |
|---|---|---|---|---|---|---|
| 1 | AFC Bournemouth – Aston Villa | 1X2 — Bournemouth wint | 2.32 | +15,57 pp | 9,135 | BET |
| 2 | Genoa – Juventus | BTTS — nee | 1.8624 | +12,00 pp | 7,884 | de twee methodes wijzen tegengesteld |
| 3 | Hannover 96 – Kaiserslautern | Asian Handicap — Hannover 96 −0.25 | 2.06 | +11,32 pp | 6,777 | BET |

**Nul selecties sneuvelden alleen op de herijking** (§1g), dus de reeks `zonder_herijking` groeit
vandaag niet. Dat is bij een fit die vrijwel de identiteit is (a=0,9928, b=−0,0047) ook te
verwachten: de correctie verlaagt een kans met 0,0 tot 0,2 procentpunt over de hele speelbare band,
en daar sneuvelt niemand op. Twee van de drie gepubliceerde regels halen hun lat ook op de ruwe
schaal (`bet_beide = true`).

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 5 van 5 (4 betaald + beste prijs, 1 gratis marktgemiddelde) | 62 | **1** |
| Asian Handicap | 4 van 5 (uit de spreads van de bulk) | 78 | **1** |
| Draw No Bet | 4 van 5 (de 0.0-lijn uit diezelfde spreads) | 22 | 0 |
| Double Chance | 3 van 5 (de ±0.5-lijn uit diezelfde spreads) | 9 | 0 |
| Over/Under | 4 van 5 (de totals uit de bulk) | 100 | **1** |
| BTTS | 4 van 5 (14 duels, tweede ronde) | 28 | 0 |

**De controle van §1a is gehaald op de inkoop, niet op de uitkomst, en het is nuttig te zeggen hoe
ruim:** alle **vier** inkoopbare competities (Serie A, Scottish Premiership, League Cup, DFB Pokal)
kregen de volledige bulk-aanroep met zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een
doelpuntenmarkt (O/U) — **4 van 4**, waar de controle er één eist, en ruimer dan de 2 van 2 van
gisteren. Daarna kregen **14** duels de tweede ronde BTTS, op grond van `kandidaat_edge` (de
vereniging van beide schalen, §1a stap 2). Het vijftiende duel met een kandidaat-edge was Sparta
Rotterdam – Fortuna Sittard, waar geen sportkey is en de markt dus niet te koop was; dat staat als
zodanig in `markets_checked` en niet als "geen boek noteerde deze markt".

Totaal **26 van 2326 credits**: 4 bulk-aanroepen à 3 credits en 14 event-aanroepen à 1 credit (het
plafond kwam uit `suggest_cap(18633, 4)`, verdeling `split_budget(2326, 4)` → 4 spreads / 4 totals).
Er staan nog 18.607 credits open van het maandplafond van 20.000.

**Dat de KNVB Beker alleen een gratis 1X2 kreeg, is géén krap plafond maar een ontbrekende
competitie bij de bron.** Dat raakt vandaag twee doorgerekende duels — tegen elf van de 22 gisteren,
en dat verschil is bevinding 1. De drie gepubliceerde bets komen uit drie verschillende markten
(1X2, Asian Handicap, Over/Under), dus de eenzijdigheid van 29 augustus doet zich niet voor, en voor
het eerst in drie dagen wedden ze ook niet alle drie op dezelfde kant.

### Net niet

| Wedstrijd | Tier | Markt / selectie | xG-model | 2e methode | zwakste stand | valt af op |
|---|---|---|---|---|---|---|
{netniet}

**De poortverdeling van vandaag is scheef, en dat is zelf een waarneming.** Van de **299**
doorgerekende selecties sneuvelen er **234 op `tweede_methode`** (poort 5) — 78% — daarnaast 20 op
`edge`, 19 op `underdog` (poort 8), 9 op `context` (poort 7), 7 op de koersband (poort 2), 2 op
`doelpunten_onder` (poort 9) en 1 op `robuustheid`; 7 selecties halen alle negen poorten. §5 "Net
niet" noemt precies dit het signaal om op te letten: *"valt er een week lang alles af op
`tweede_methode`, dan is de vraag of de twee methodes systematisch uiteenlopen — en dat is een
bevinding, geen ruis."*

**Eén dag is geen week, en vandaag is er een verklaring die geen bevinding is:** 22 van de 33 duels
zijn bekerwedstrijden, vaak tussen ploegen van **ongelijke** sterkte, en juist daar lopen een
xG-model en een thuis/uit-doelpuntensplitsing het verst uiteen. De splitsmethode is bovendien sinds
§6e (22 aug) al de scheefste van de twee, en §1f heeft op 392 afgerekende gevallen gemeten dat ze als
kansbron vrijwel niets toevoegt (Brier .23625 bij gewicht 0,80 tegen .23674 voor alleen xG) terwijl
haar waarde juist in dit veto zit. Het staat hier **met een getal** zodat een volgende run kan zien
of het aanhoudt; er wordt vandaag geen poort en geen gewicht op verzet (§6d). De reeks
`tweede_methode` staat op 224 kandidaten, 209 afgewikkeld, **−9,7%** — die poort bespaart tot nu toe
aantoonbaar geld. Vijf FULL-duels met vijftien tot eenentwintig doorgerekende selecties vielen hier
volledig op af: Milan – Bologna, Genoa – Juventus, Manchester City – Brighton, Sunderland –
Brentford en Liverpool – Chelsea.

**Poort 8 hield negentien selecties tegen, verdeeld over vijf wedstrijden**, in de lichte vorm
(ondergrens `sides.UNDERDOG_FLOOR` = 0,35) en met `today=2026-10-28` aangeroepen zodat het
stilstandvenster van 25 t/m 30 september uit `sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in
plaats van geraden. De vijf sterkste per wedstrijd gaan als `underdog`-rij het schaduwlogboek in:
Milan – Bologna (Bologna +1.5 @1,46, +7,78 pp), Monza – Napoli (Monza +0.75 @1,93, +9,12 pp),
St. Johnstone – Motherwell (Motherwell wint @2,862, +1,94 pp), Heart of Midlothian – Rangers (Hearts
+0.25 @2,07, +5,92 pp) en Sunderland – Brentford (Double Chance Sunderland of gelijk @1,872,
+5,04 pp). **`poort8_ruw` krijgt vandaag geen enkele rij:** er is geen selectie die op de ruwe kans
alle eerdere poorten haalde en alléén op poort 8 sneuvelde. Dat is bij een herijking die vrijwel de
identiteit is te verwachten — de twee schalen liggen dan bijna op elkaar. Tel die twee reeksen nooit
bij elkaar op; het zijn twee populaties.

**Poort 9 hield twee selecties tegen, en ze zaten in het duel waarvan de derde regel komt.** Dat
ziet eruit als een tegenstrijdigheid en het is er geen, maar het hoort uitgelegd:

- Tegengehouden: **St. Mirren – Hibernian, Under 2.75 @2.04 (+8,81 pp)** en **Under 2.5 @2.274
  (+8,76 pp)** — beide boven de gewone drempel van 8,0 pp en beide onder de verzwaarde lat van
  **10,0 pp** die §1h aan een Under op `FULL`-data stelt. Ze gaan als `failed_gate =
  doelpunten_onder` naar het schaduwlogboek.
- Gepubliceerd: **Under 3 @1.71 (+6,43 pp)** uit datzelfde duel. Die is door poort 9 **heengekomen**,
  omdat `unders.check` met opzet alléén in de band 8,0–10,0 pp bindt: een Under die de gewone drempel
  al niet haalt wordt door `edge` tegengehouden en niet hierdoor, want anders loopt de reeks
  `doelpunten_onder` vol met kandidaten die nooit een bet konden worden en meet ze niets meer — de
  "twee populaties"-fout die §1e bij `underdog_ruw` en §5b bij `lijstlengte` benoemt.

**Maar sinds §5b op 20 september de drempel van een poort in een afkapping heeft veranderd, betekent
dat ook dat een Under ónder de 8,0 pp wél gepubliceerd kan worden en door géén van beide latten
wordt getoetst.** Dat is geen omissie in de uitvoering maar het gevolg van twee regels die elkaar
raken — en het is dezelfde constructie die §1h punt 1 bij `LIGHT` uitdrukkelijk heeft gekozen (een
LIGHT-Under die de rangorde haalt wordt gepubliceerd, ook zonder zijn eigen lat van 16,0 te halen).
Het is bovendien precies de kant waarvan §6g vandaag de hardste meting tot nu toe geeft (z = +4,04
over 103 gevallen). **Deze run verzet die poort niet**: §1h punt 3 en §6g leggen vast dat dat over
risicobereidheid gaat en dus een besluit van de gebruiker is. Het staat één keer als vraag in het
dagrapport onder "Wat er nog moet gebeuren", met `owner = besluit`, en wordt daarna niet herhaald.

## Wedstrijden

{wedstrijden}

## Bevindingen

### 1. Twee sportkeys die bestonden en niet werden gebruikt — en een controle die groen stond omdat ze het verkeerde veld las

**Wat er aan de hand was.** §1a legt vast waar de prijzen vandaan komen: The Odds API levert per
competitie de beste prijs per uitkomst (1 credit voor `h2h`, of 3 voor de volledige bulk met
`spreads` en `totals` erbij), BetExplorer levert gratis het marktgemiddelde over alle boeken. Het
gemiddelde is om te **meten** (het kalibratieblok van §6e, en poort 8), de beste prijs is om op te
**spelen**. Het verschil daartussen is op 5 september gemeten op **+7,78% prijs en +1,84 procentpunt
edge per selectie** — "beter uitbetaald krijgen voor hetzelfde model", en §1a noemt het de enige
verbetering in dat bestand waarvan de omvang vooraf vaststaat.

Voor een competitie zonder sportkey is BetExplorer de enige 1X2-bron, en dat is een geldige
uitkomst. **Maar de Scottish Premiership en de League Cup hebben wél een sportkey**, en de
runscripts van oktober gaven voor beide `None` mee:

| Competitie | Sportkey | Sinds wanneer bekend |
|---|---|---|
| League Cup (ENG) | `soccer_england_efl_cup` | staat sinds **10 aug 2026** in `oddsapi.SPORT_KEYS` |
| Scottish Premiership (SCO) | `soccer_spl` | `coverage.json` noteert sinds **9 sep 2026**: *"sportkey soccer_spl werkte deze run voor het eerst (5 events op h2h+spreads+totals)"* |

**Waarom niemand het zag, en dat is het eigenlijke punt.** `api_check.py` drukt elke run een lijst
"relevante sportkeys" af, en die lijst werd gefilterd op een woordenlijst **tegen de sleutel**:

```python
wanted = ("eredivisie", "portugal", "belgium", "poland", "scot", "epl", "italy",
          "spain", "germany", "france", "efl_champ", "denmark", "turkey", "uefa")
hits = sorted(s["key"] for s in soccer if any(w in s["key"] for w in wanted))
```

De Schotse sleutel heet `soccer_spl` — het woord "scot" staat alleen in `title`
("Premiership - Scotland") en `description` ("Scottish Premiership"). En `soccer_england_efl_cup`
bevat wél "england", maar dat woord stond niet in de lijst; "efl_champ" matcht er niet op. **Beide
sleutels zijn dus nooit in de uitvoer van de controle voorbijgekomen**, terwijl die controle precies
bestaat om te melden welke competities bij de bron te koop zijn. Dat is de stille faalvorm die deze
repo al drie keer heeft gekost — het Serie B-id (een verkeerd id geeft nul wedstrijden, en nul
wedstrijden is een normale uitkomst), `calibration.py settle` (een niet afgewikkeld logboek geeft
gewoon een geldige fit) en `settled_note` (een prosesleutel die nooit werd gelezen) — nu in een
vierde gedaante: **een controle die groen staat omdat ze de verkeerde grootheid meet.**

**Wat het kostte.** De Scottish Premiership heeft van 9 september t/m 27 oktober uitsluitend op het
BetExplorer-gemiddelde gedraaid, en dat gemiddelde gaat daar over **drie** boeken — de dunste die
deze routine tegenkomt (Serie A heeft er 16, de DFB Pokal 11). Vandaag gemeten per duel, als
percentage waarmee de beste prijs het gemiddelde verslaat:

| Duel | beste prijs t.o.v. het gemiddelde |
|---|---|
| Celtic – Dundee United | **+11,95%** |
| Heart of Midlothian – Rangers | +6,26% |
| St. Mirren – Hibernian | +5,66% |
| Aberdeen – Falkirk | +7,15% |
| Dundee FC – Kilmarnock | +4,92% |
| St. Johnstone – Motherwell | +4,90% |
| League Cup, vijf duels | +4,09% tot +6,02% |

**Wat er is gerepareerd, vóór de analyse en niet erna** (§4: *"meet een nieuwe factor liever vóór de
analyse van de dag, niet erna"*):

1. **`scripts/oddsapi.py`** — `"Scottish Premiership (SCO)": "soccer_spl"` staat er nu in, met de
   reden en de datum erbij. Daarnaast de drie Europese toernooien (`soccer_uefa_champs_league`,
   `soccer_uefa_europa_league`, `soccer_uefa_europa_conference_league`), die in de runlijst van
   `run-a.md` staan en elke dag in de /sports/-lijst, maar die alleen in de runscripts zelf stonden.
   Die laatste drie kostten niets — de scripts gaven hun sleutel wel mee — maar dan staat een sleutel
   in een script van één dag in plaats van op de plek waar `api_check.py` hem kan controleren. Alle
   vier zijn vandaag actief bevonden.
2. **`scripts/api_check.py`** — de controle noemt nu **per bekende sleutel** of hij vandaag actief is
   (28 van 29, en de enige die niet actief is, is de Coppa Italia, die ook werkelijk pas 1 december
   speelt), en daarnaast **welke actieve sleutels de repo níet kent**, gefilterd op sleutel, titel én
   beschrijving. Dat is de controle die het gat van vandaag wél zou hebben gevonden.

**En die tweede lijst vindt meteen vijf nieuwe gaten**, alle vijf buiten de Run A-runlijst en dus
werk voor Run B en C: `soccer_norway_eliteserien`, `soccer_sweden_superettan`,
`soccer_germany_liga3`, `soccer_spain_copa_del_rey` en `soccer_uefa_nations_league`. Eliteserien,
Superettan en de 3. Liga staan in de runlijst van Run B en de Nations League in die van Run C; die
runs draaien daar vandaag dus nog op een marktgemiddelde terwijl de beste prijs te koop is. Het is
hier niet opgelost omdat een run geen runlijst aanraakt die niet de zijne is — het staat als
actiepunt met `owner = ik` in het dagrapport.

**Wat dit niet is.** Geen modelverbetering. Er is geen kans, geen drempel en geen poort aangeraakt;
alleen de prijs waartegen de edge wordt gemeten. Dat is precies het soort winst dat §1a bedoelt met
"beter uitbetaald krijgen voor hetzelfde model", en het is de enige winst in dit hele bestand waarvan
de omvang vooraf vaststaat — **daarom is het ook de ergste om zeven weken te laten liggen.**

### 2. De voorvoegselregel van gisteren hield vandaag meteen iets tegen

Op 27 oktober is `tmp-run/ra_names.resolve` gerepareerd: de koppeling tussen de naam uit de
Fotmob-daglijst en de naam in de standtabel gaat sindsdien via `teamnames.is_abbreviation`, dat een
afkorting alleen als **voorvoegsel** accepteert — de staart mag weg, de kop nooit. De oude regel
vergeleek een **deelverzameling** van tokens, en die zegt alleen dat alle woorden van de korte naam
in de lange voorkomen en niet wáár.

De zelftest van vandaag (`ra_oct28_namecheck.py`, 66 namen uit alle vijf de competities) geeft
**precies één verschil** tussen de oude en de nieuwe regel, en dat is een echt geval uit de lijst van
vandaag:

```
VERSCHIL KNVB Beker (NED)     Excelsior Maassluis        oud='Excelsior'  nieuw=None
```

**Excelsior Maassluis** is een amateurclub uit Maassluis; **Excelsior** is de Eredivisieclub uit
Rotterdam. De oude regel koppelde de eerste aan de tweede, want `{{excelsior}}` is een
deelverzameling van `{{excelsior, maassluis}}`. Precies één treffer, dus de veiligheidsregel "alleen
bij één kandidaat" had het niet gevangen, en Excelsior Maassluis – SC Heerenveen zou met de xG van
Excelsior Rotterdam achter de thuisploeg zijn doorgerekend. **Geen van de negen poorten kan dat
zien** — het is geen te ruime kans maar een verkeerde ploeg, en dat is een categorie die §1g niet
dekt. Nu komt het duel op `NONE` uit, wat het hoort te zijn: een amateurclub zonder vergelijkbare
historie in een divisie met een gemeten factor.

Het is een kleine bevinding en ze staat hier om één reden: **ze bevestigt waarom §4 wil dat zo'n
reparatie vóór de analyse van de dag gebeurt.** Eén dag later en dit was een rij in de dagranglijst
geweest, net als de schijnedge van +37,85 pp die de reparatie van 27 oktober zelf opleverde.

### 3. Elf van de 33 duels op `NONE`, en dat is bij een bekerronde het juiste antwoord

Een beker heeft zelf geen stand en dus geen competitiegemiddelde om ploegen op te normaliseren. §4
hangt elk toernooi daarom aan één vaste basisdivisie (`promotion.CUP_BASE`), en een ploeg die daar
niet in staat wordt uit de divisie eronder omgerekend — **één** divisie diep, want verder is er geen
meting. Dat geeft vandaag drie uitkomsten:

**(a) Zes duels waar een ploeg in geen enkele divisie met een gemeten factor staat.** SSV Jeddeloh
speelt in de Regionalliga, twee divisies onder de Bundesliga; Genemuiden, JOS Watergraafsmeer, Quick
Boys, VVSB en Excelsior Maassluis spelen onder de Eerste Divisie. Daar is geen relatieve
invoersterkte en dus niets om op te extrapoleren.

**(b) Vijf duels die op `promotion.conversion_in_range` vallen — de Coventry-val.** Deze ploegen zijn
wél omgerekend, maar hun relatieve sterkte valt buiten het bereik waarin de factor ooit is gemeten:

| Ploeg | Divisie | Buiten bereik |
|---|---|---|
| 1. FC Nürnberg | 2. Bundesliga | aanval 0,943 tegen gemeten 0,999–1,673 |
| Magdeburg | 2. Bundesliga | verdediging 1,164 tegen gemeten 0,613–0,996 |
| Holstein Kiel | 2. Bundesliga | aanval 0,883 tegen 0,999–1,673 |
| MVV Maastricht | Eerste Divisie | buiten het gemeten bereik |
| TOP Oss | Eerste Divisie | buiten het gemeten bereik |

Buiten dat bereik is er geen meting, dus geen onafhankelijke kansinput op het niveau waarop gespeeld
wordt: `NONE`, geen bet. §4 noemt dat expliciet een **poort en geen aantekening** — hij kost anders
+21 pp schijnedge die alle andere poorten haalt.

**(c) Drie duels die door `shared_lower_division` zijn gered** (§4, 15 sep 2026). Staan beide ploegen
in dezelfde divisie onder de basis, dan is er niets te overbruggen en wordt het duel daarin
doorgerekend:

- **Dynamo Dresden – Schalke 04** en **Hannover 96 – Kaiserslautern**, beide 2. Bundesliga → `FULL`,
  want die divisie heeft xG bij Fotmob. De tweede is een gepubliceerde bet geworden.
- **VVV-Venlo – Vitesse**, beide Eerste Divisie → `LIGHT`, want die divisie heeft geen xG.

Dat de tier uit de gevonden divisie komt en niet uit de beker is geen detail: er is **niets**
omgerekend, dus de regel "een omgerekende ploeg is nooit `FULL`" is hier niet van toepassing.

**En één gevolg daarvan is vanmorgen gerepareerd.** De marktvormtelling van §4
(`marketform.match_block`) kreeg per competitie de `primaryId` uit `CUP_BASE` mee — voor de DFB Pokal
dus de **Bundesliga** — terwijl Hannover 96 en Kaiserslautern in de **2. Bundesliga** zijn
doorgerekend. De telling zocht die twee ploegen in de Bundesliga-stand en gaf vier keer "speelde die
competitie niet" **op een gepubliceerde bet**. Dat is geen foutmelding maar een leeg blok, terwijl §4
juist bij een doelpuntenmarkt eist dat de frequenties erbij staan. `ra_oct28_marktvorm.py` leest het
id nu uit de `note` van `basis_per_wedstrijd`, en daarmee staat er bij Kaiserslautern wat er hoort te
staan: **1,4 doelpunten per duel in de laatste vijf competitiewedstrijden en nul keer BTTS in die
vijf.**

## Stand van het logboek

### `ledger.py stats` — wat er wél doorheen kwam

```
{blok('ra_oct28_ledger.txt')}
```

### `shadow.py stats` — wat de poorten hebben tegengehouden

```
{blok('ra_oct28_shadow.txt')}
```

**Twee reeksen horen genoemd, en de eerste is nieuw.** De `underdog`-reeks staat vandaag op **241
afgewikkelde gevallen met −4,0% rendement** (49,4% trefkans). Op 5 oktober stond diezelfde reeks op
**+16,9% over 36 gevallen** en was dat de meting die de vraag van 25 september moest beantwoorden —
*"haalt de reeks een positieve ROI over ≥ 30 gevallen, dan is dat een aanleiding om de vraag te
stellen"*. **Met zeven keer zoveel gevallen is het teken omgeslagen**, en het slaat de kant op die
de poort steunt: poort 8 bespaart nu 9,59u. §1e zegt dat zo'n omslag een aanleiding is om de vraag
opnieuw voor te leggen — maar de vraag luidde of de rem eruit kon, en dit antwoord zegt nee. **Er is
dus niets voor te leggen en niets te veranderen;** het hoort gewoon in deze sectie, zoals elke
andere reeks.

De tweede: **`edge` staat op +1,1% over 532 gevallen** en `lijstlengte` op **+24,2% over 20**. Die
eerste is de poort die sinds 20 september geen poort meer is maar een afkapping (§5b), en een
positieve ROI betekent daar dat de afgekapte groep het niet slechter deed dan de gepubliceerde —
precies wat §5b zelf voorspelde ("niet beter dan de rest, maar ook niet slechter"). De tweede staat
op twintig gevallen en daar is §6d duidelijk over: niet lezen onder ~30.

### `recalibrate.py show` — de stand van de herijking (§1g)

```
{blok('ra_oct28_recalibrate.txt')}
```

`fitted_through` staat op **2026-10-27**, dus op de vorige rundag — de controle die §6b-5c in één
getal voorschrijft, en ze is groen. De fit is met `a=0,9928` en `b=−0,0047` vrijwel de identiteit:
hij verlaagt een kans met 0,0 tot 0,2 procentpunt over de hele speelbare band. Dat is de reden dat
`zonder_herijking` vandaag niet groeit, en het is ook de reden dat poort 8 zwaarder weegt dan in de
tijd dat de herijking tien procentpunt van elke schatting afhaalde (§1e, 30 sep).

### `calibration.py stats` — zit het model systematisch scheef? (§6e)

```
{blok('ra_oct28_calstats.txt')}
```

### `margins.py stats` — klopt de vórm van de uitslag? (§6f)

```
{blok('ra_oct28_margins.txt')}
```

### `margins.py stats --since 2026-09-20` — alleen lambdas van ná de shrink-overstap

```
{blok('ra_oct28_margins_since.txt')}
```

### `margins.py goalbias` — de doelpuntenkant per gespeelde kant (§6g)

```
{blok('ra_oct28_goalbias.txt')}
```

**Dit is het getal van de dag.** De regel "Under gespeeld" staat op **103 gevallen, +0,659 doelpunt
per duel, z = +4,04**. Op 11 oktober — de dag waarop poort 9 is besloten — was het +0,68 over 49
gevallen bij z = +2,91. De reeks is dus verdubbeld en het teken is sterker geworden, niet zwakker.
Lees de twee tabellen apart, zoals de leeswijzer eronder zegt: de bovenste meet het **model** (z =
+1,05 over 1717 duels, dus de lambdas kloppen gemiddeld) en de onderste de **selectie**. De vormfout
staat in de tweede tabel: massa van 2 doelpunten (−1,5 pp) naar 4 (+1,0) en 5 (+1,4), waardoor
`P(Under 2.5)` 2,2 pp en `P(Under 3.0)` 1,7 pp te hoog staat. **De rem (poort 9) staat er; de
oorzaak — keuze (a) van 11 oktober — staat nog open, en dat is een besluit van de gebruiker.**

### `ctxlog.py stats` — het contextlogboek (§1c)

```
{blok('ra_oct28_ctxstats.txt')}
```

### `scripts/branchaudit.py` — Stage -2 per record op de inhoud

```
{blok('ra_oct28_branchaudit.txt')}
```

## Openstaand

1. **De vormfout in `score_grid` (keuze (a) van 11 okt 2026).** Onveranderd het echte werk, en
   vandaag met het hardste cijfer tot nu toe onderbouwd (z = +4,04 over 103 gespeelde Unders). Poort 9
   is een rem op een symptoom; `score_grid` zet nog steeds te weinig massa op 4 en 5 doelpunten, en
   die fout werkt ook door in BTTS en — in de andere richting — in de Over-kant, die er juist aan
   verdient. Besluit van de gebruiker; staat als zodanig in het dagrapport.
2. **Poort 9 toetst een Under onder de 8,0 pp niet, en §5b publiceert die wél.** Nieuw opgeschreven
   vandaag, en vandaag voor het eerst zichtbaar in één wedstrijd: de 2.75- en 2.5-lijn van
   St. Mirren – Hibernian zijn tegengehouden en de 3.0-lijn is gepubliceerd. Geen fout in de
   uitvoering maar het gevolg van twee regels die elkaar raken. Besluit van de gebruiker; één keer
   voorgelegd en niet herhaald.
3. **De vijf sportkeys die Run B en Run C missen.** `soccer_norway_eliteserien`,
   `soccer_sweden_superettan`, `soccer_germany_liga3`, `soccer_spain_copa_del_rey` en
   `soccer_uefa_nations_league` staan actief bij de bron en niet in `oddsapi.SPORT_KEYS`. Dezelfde
   acht procent op de koers die hierboven in Schotland zat. Werk voor de eerstvolgende run die ze op
   de kalender heeft; niet hier opgelost, omdat een run geen runlijst aanraakt die niet de zijne is.
4. **De drie bekerid's (133, 209, 235) staan niet in `coverage.json` onder `fotmob_id`.** Dat is een
   bewuste keuze — `idcheck.py` eist van elk id in dat veld een bruikbare stand en een beker heeft er
   geen — maar het betekent dat elke run ze met de hand in een eigen script moet meegeven. Een eigen
   veld (`fotmob_daglijst_id`) dat `idcheck.py` overslaat zou dat oplossen. Niet vandaag gedaan: het
   raakt het schema van `coverage.json` en dat is meer dan een regel bijschrijven.
5. **`scripts/settling.py` heeft nog de oude deelverzamelingsregel voor namen.** Onveranderd sinds
   27 oktober. Daar is ze met opzet ruim en beslist lookup op het **paar** thuis-en-uit plus de eis
   van precies één kandidaat, dus de rem is er anders — maar het is hetzelfde patroon. Vandaag niet
   aangeraakt: een poort verzetten die niet knelt is geen werk dat een run op eigen initiatief doet.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-10-28-run-a.md", "w").write(MD_TEXT)
print("runs/2026-10-28-run-a.md geschreven —", len(MD_TEXT), "tekens")
