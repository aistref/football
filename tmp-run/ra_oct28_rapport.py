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
mv = json.load(open("tmp-run/ra_oct28_marktvorm.json"))
ART = "https://claude.ai/artifact/B1PkMihNK16M2ubJzgQr3V"
MD = "https://github.com/aistref/football/blob/main/runs/2026-10-28-run-a.dagrapport.md"

# --- dekkingstabel ---
TOELICHTING = {
 "Serie A (ITA)": "3 duels, 18:30-20:45 NL — alle drie doorgerekend, alle drie een bet",
 "DFB Pokal (GER)": "8 duels, 18:00-20:45 NL — 5 doorgerekend, 3 op `NONE`",
 "KNVB Beker (NED)": "9 duels, 18:45-21:00 NL — 2 doorgerekend, 7 op `NONE`",
 "League Cup (ENG)": "2 duels, 20:45-21:00 NL — 1 doorgerekend, 1 op `NONE`",
 "Premier League (ENG)": "weer op 1 nov 17:30",
 "La Liga (ESP)": "weer op 1 nov 14:00",
 "Bundesliga (GER)": "weer op 1 nov 15:30",
 "Ligue 1 (FRA)": "weer op 1 nov 15:00",
 "Championship (ENG)": "weer op 30 okt 21:00",
 "Eredivisie (NED)": "weer op 1 nov 12:15",
 "Primeira Liga (POR)": "weer op 1 nov 16:30",
 "Belgian Pro League (BEL)": "weer op 1 nov 13:30",
 "Super Lig (TUR)": "weer op 1 nov 11:30",
 "Scottish Premiership (SCO)": "weer op 1 nov 14:00",
 "Danish Superliga (DEN)": "weer op 1 nov 14:00",
 "Ekstraklasa (POL)": "weer op 2 nov 18:00",
 "UEFA Champions League": "hervat op 3 nov 18:45",
 "UEFA Europa League": "hervat op 5 nov 18:45",
 "UEFA Conference League": "hervat op 5 nov (geen tijd bij BetExplorer)",
 "FA Cup (ENG)": "volgende ronde 6 nov 20:45 (BetExplorer; geen fotmob_id in coverage.json)",
 "Coppa Italia (ITA)": "volgende ronde 1 dec 21:00 (BetExplorer; geen fotmob_id in coverage.json)",
}
rijen = []
for comp, blk in st["competitions"].items():
    status = blk["status"]
    n = len(blk.get("matches") or [])
    label = f"`{status}`" if status != "GEANALYSEERD" else "**`GEANALYSEERD`**"
    naam = f"**{comp}**" if status == "GEANALYSEERD" else comp
    rijen.append(f"| {naam} | {label} | {TOELICHTING.get(comp, '—')} |")
dekking = "\n".join(rijen)

# --- net niet ---
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

# --- wedstrijdblokken ---
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

**Dinsdag 27 oktober 2026.** Vier van de eenentwintig competities uit de runlijst speelden, samen
**22 duels** in het inzetvenster — het drukste Run A-programma van deze maand — en **negentien
ervan zitten in een beker**: acht in de DFB Pokal, negen in de KNVB Beker en twee in de League Cup,
naast drie midweekse duels in Serie A. Tweeëntwintig onder de dinsdagcap van 40, dus de cap bindt
nergens. De twaalf overige competities sloten hun ronde zondag af en beginnen de volgende op 30
oktober of 1 november; de drie Europese toernooien spelen 3 en 5 november. §3 Stage 2 noemt dat
`GEEN WEDSTRIJD`.

**Er zijn vandaag twee fouten in de repo gevonden, en de eerste is de ernstigste van deze maand —
zie bevinding 1.** `tmp-run/ra_names.resolve` koppelde op een **deelverzameling** van tokens, en
een deelverzameling zegt alleen dat alle woorden van de korte naam in de lange voorkomen en niet
wáár. `fc` staat in `_DROP`, dus `FC Eindhoven` houdt het ene token `eindhoven` over en dat is een
deelverzameling van `{{psv, eindhoven}}`: **de Eerste-Divisieclub FC Eindhoven koppelde aan PSV
Eindhoven in de Eredivisie-stand.** Precies één treffer, dus de veiligheidsregel "alleen bij één
kandidaat" ving het niet, en FC Eindhoven – FC Volendam kwam op `FULL` uit met de xG van de
kampioen achter de thuisploeg. **Geen van de negen poorten kan dat zien** — het is geen te ruime
kans maar een verkeerde ploeg, en dat is een categorie erger dan de `ob`-alias van gisteren, die
alleen een poort blind maakte. Gerepareerd **vóór** de analyse (§4) met de eis die §4 al aan
`promotion.find_team` stelt: een afkorting laat de staart weg, nooit de kop.
`teamnames.is_abbreviation` doet dat op woordniveau. Regressie over alle 44 teamnamen van vandaag:
**precies twee verschillen**, en dat zijn exact de twee verkeerd gekoppelde ploegen — FC Eindhoven
en Excelsior '31 (zie bevinding 1 voor dat tweede geval, dat de eerste reparatie nog doorliet).

**De tweede bevinding gaat over het vinden van wedstrijden: de drie bekers met een ronde staan wél
in de Fotmob-daglijst** — EFL Cup onder id 133 (2 duels), DFB Pokal onder 209 (8) en KNVB Cup onder
235 (9), exact dezelfde aantallen als BetExplorer. Die id's staan niet in `coverage.json`, dus
`runwindow.matches_for_run` kan ze niet filteren en elke run van oktober heeft de bekers langs
BetExplorer gedaan. **Het gat zat dus niet in de bron maar in de administratie**, en dat is de
stille faalvorm van §6b-5b: een controle die groen staat omdat ze een rij niet meet. Het verschil
is niet academisch — via de daglijst komen de duels mét `match_id` en dus mét context, opstelling,
uitvallers en poort 7; via BetExplorer alleen met namen en een koers. Dat is precies wat het op
6 oktober kostte, toen vier van de vijf FA Cup-duels daardoor niet door te rekenen waren. Zie
bevinding 2.

**Twaalf van de 22 duels komen op `NONE` uit, en dat is bij een bekerronde de verwachting.** Acht
duels zijn `FULL`, twee `LIGHT` en twaalf `NONE`. Acht NONE-duels betreffen een ploeg die in geen
enkele divisie staat waarvoor een gemeten omrekenfactor bestaat (Fleetwood Town, RW Essen, Sonnenhof
Großaspach en de vijf clubs onder de Eerste Divisie: Excelsior '31, Barendrecht, Kloetinge,
Rijnsburgse Boys en Koninklijke HFC); de andere vier vallen op `promotion.conversion_in_range` — de
Coventry-val (Bochum, Karlsruher SC, FC Eindhoven, Almere City FC). **Vier duels zijn door
`shared_lower_division` gered** (§4, 15 sep):
Bradford City – Peterborough United in League One (`FULL`), Elversberg – Darmstadt in de 2.
Bundesliga (`FULL`), en Helmond Sport – Willem II en Roda JC – De Graafschap in de Eerste Divisie
(`LIGHT`, want die divisie heeft geen xG). Daar valt niets te overbruggen, dus geldt "een
omgerekende ploeg is nooit `FULL`" er niet: er is niets omgerekend.

| | |
|---|---|
| Gepubliceerd | **3** — Sassuolo – Lazio (Under 2.75 @ 2.06), Torino – Como (BTTS nee @ 2.3524), Roma – Cagliari (Under 3 @ 1.84) |
| Waarvan boven de eigen lat | **1 van 3** — +15,15 pp; de andere twee staan op +5,28 en +3,82 pp en zijn op rangorde gepubliceerd (§5b) |
| `bet_beide` | **1 van 3 TRUE** (Sassuolo – Lazio); de twee regels onder de lat halen hem op geen van beide schalen |
| Gekwalificeerd, niet gepubliceerd | **0** — de lijstlengte bindt niet (3 publiceerbare selecties, 3 plekken) |
| Afgekapt door de cap | **0** van 40 |
| Doorgerekend | 10 van 22 duels, **79 selecties** over alle zes de markten; `progress.py verify` groen op 10 van 10 |
| Bronstoringen | **0** |
| Credits | 9 van een dagplafond van 1864; 18.652 over met vijf dagen tot de maandwissel |

**Wat bovenaan de bets hoort en niet in een voetnoot: alle drie de regels wedden op weinig
doelpunten, en drie onafhankelijke metingen wijzen daar vandaag tegenin.** Twee regels zijn een
Under en de derde is BTTS "nee", wat dezelfde mening in een andere markt is.

1. **De vormfout van §6g.** `margins.py goalbias` van vanmorgen, over 1698 doorgerekende duels: het
   model als geheel klopt (verwacht 3,034 doelpunten per duel tegen werkelijk 3,068, z = +0,82),
   maar er is massa verschoven van 2 doelpunten (voorspeld 22,4%, werkelijk 20,9%) naar 4 en 5
   (+1,0 en +1,3 pp). Daardoor staat `P(Under 2.5)` over alle duels **2,1 pp te hoog** en
   `P(Under 3/3.5)` 1,5 pp. Daar bovenop het selectie-effect: de duels waarin werkelijk een Under
   is gespeeld leverden 3,320 doelpunten tegen 2,739 verwacht — **+0,581 per duel over 100 gevallen,
   z = +3,51**, tegen −0,296 op de Over-kant (z = −1,25 over 60).
2. **Pinnacle.** `ra_oct28_pinnacle_ou.py`: alle drie de Serie A-duels hebben een Pinnacle-totaal en
   **alle drie staan boven Pinnacle op de Under-kant**, gemiddeld **+9,93 pp**. Sassuolo – Lazio
   staat er met +14,26 pp op lijn 2.75 het verst vanaf. Dat is een onafhankelijke meting in dezelfde
   richting als punt 1 — de scherpste bookmaker van de markt zet P(Under) lager dan dit model, bij
   alle drie de duels.
3. **De telling van §4.** De marktvormtelling spreekt **alle drie** de regels tegen: Sassuolo ging
   dit seizoen in zes van de acht competitieduels boven 2,5 (gemiddeld 3,50) en in zijn drie
   thuisduels scoorden altijd beide ploegen; Torino had dit seizoen in zes van de acht duels BTTS
   (75%) en Como in vijf van de acht, uit zelfs vier van de vijf; en Roma kwam in vier van de acht
   duels boven 3,5 (gemiddeld 3,12). Alleen bij Roma – Cagliari wijst de onderlinge historie de
   andere kant op, en wel sterk: 2-0, 1-0, 1-0, 0-0 en 4-0, met nul keer BTTS in vijf duels.

**Trek dus ongeveer twee procentpunt van de genoemde kansen af voordat je ze leest.** En §5b zegt er
het tweede bij: een lijst die dagen achtereen uit één hoek komt is een signaal over het **model** en
niet over de rangorderegel. Gisteren stonden alle drie de regels ook op de Under-kant; dit is de
tweede dag op rij. **Poort 9 raakt vandaag geen van de drie regels** — hij bindt alleen in de band
8–10 pp op `FULL` (+15,15 staat erboven, +3,82 eronder) en BTTS is er met opzet buiten gehouden
(§1h punt 2). Deze run verzet die poort niet: §1h punt 3 en §6g leggen vast dat dat een besluit van
de gebruiker is en geen werk dat een run op eigen initiatief doet.

**Dagrapport (§6c):** <{ART}> ·
Markdown-terugval: <{MD}>

De pagina is preventief in Chromium gerenderd (`tmp-run/ra_oct28_rendercheck.js`, de controle die
§6c sinds 15 oktober voorschrijft): 16.986 px hoog, 41.280 zichtbare tekens, 51 blokken, 6 tabellen,
3 bets, **nul console- of pagefouten**, en correct in zowel licht als donker. Komt de Artifact bij de
gebruiker tóch niet door, dan is opnieuw publiceren zinloos en is de Markdown-link hierboven het
antwoord.

---

## Branchaudit (Stage -2)

**De repo kwam als ondiepe kloon aan, en dat is precies de valkuil die §3 Stage -2 beschrijft.**
`git rev-parse --is-shallow-repository` gaf `true`, en de naïeve telling vóór het unshallowen zag
**69 van de 79 takken met "eigen" commits** (van 27 tot 581 stuks), met voor elk van die takken een
**lege `merge-base`** — wat er van binnenuit uitziet als een tak met een eigen, niet-verwante
geschiedenis. Na `git fetch --unshallow origin` (639 commits lokaal) is dat **0 van de 79**. Dat is
woord voor woord de meting van 20 augustus 2026, en het is een vals alarm dat er precies uitziet als
het echte geval van 10 augustus. Het is vandaag ook bijna verkeerd gelezen: de tiplijsten van die
69 takken lopen tot 17 oktober en de oudste commit van `main` is van 18 oktober, wat de indruk gaf
dat `main` op die datum met een verse geschiedenis is begonnen. Dat is níet zo — de knip van de
ondiepe kloon lag daar.

Daarna de controle die wél iets zegt — `scripts/branchaudit.py`, **per record op de inhoud** en
niet op de commitgraaf, over alle zes de logboeken:

| Logboek | Records op `origin/main` | Uitkomst |
|---|---|---|
| `data/picks.jsonl` | 471 | VOLLEDIG |
| `data/shadow.jsonl` | 1465 | VOLLEDIG |
| `data/context-log.jsonl` | 1659 | VOLLEDIG |
| `data/calibration.jsonl` | 6281 | VOLLEDIG |
| `data/source-health.json` | 136 bladpaden | VOLLEDIG |
| `data/coverage.json` | 302 bladpaden | VOLLEDIG |

**Niets te verenigen: elk record dat op een tak staat, staat ook op `origin/main`.** De enige
afwijking is `sources.oddspapi` (5 bladpaden), die het script zelf aanmerkt als bekend besluit —
OddsPapi is op 30 augustus 2026 verwijderd na de overstap naar het 20K-creditplan. Datzelfde is
vóór het unshallowen ook met de hand nagegaan op de nieuwste tak (`stoic-davinci-pwdn5x`, 17 okt):
`picks.jsonl` daar is 416 regels tegen 471 op `main` en **nul** van die 416 ontbreken hier, en voor
`shadow.jsonl` en `calibration.jsonl` geldt hetzelfde op sleutel — de 84 en 279 regels die
tekstueel verschillen zijn afwikkelingen, waar `main` de nieuwere versie van heeft.
`prompts/_shared-rules.md` staat op `main` op 3587 regels en dat is tevens de langste versie op alle
takken.

**Openstaande picks van een run die op een andere tak nooit is afgewikkeld: geen.** `ledger.py open`
en `shadow.py open` stonden bij de start op 4 picks en 10 schaduwrijen, alle veertien van 26
oktober en alle veertien van deze tak; na Stage 0 geven beide "Geen picks klaar om af te wikkelen".

**Deze sessie draait op branch `claude/stoic-davinci-j1cug5` en pusht naar `main`,** zoals §6a
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
zonder fout, voor alle 22 duels inclusief de context.

**Maar er is vandaag wél een echte beperking aan de prijzenkant, en die hoort als bronbevinding en
niet als krap plafond: twee van de vier spelende competities hebben geen sportkey.** De League Cup
(ENG) en de KNVB Beker (NED) staan niet bij de 49 actieve competities van The Odds API —
`soccer_germany_dfb_pokal` bestaat wél, de twee andere bekers niet. Gevolg: **elf van de 22 duels
hebben geen beste prijs**, geen spreads, geen totals en geen BTTS, en vallen terug op het gratis
BetExplorer-marktgemiddelde. De edge valt daar systematisch te laag uit (conservatief, dus geen
risico op te veel bets) en de bookmaker is niet herleidbaar (§1a). Alle drie de gepubliceerde regels
komen uit Serie A, waar de beste prijs er wél is.

### `scripts/idcheck.py` — alle 33 competitie-id's groen

```
{blok('ra_oct28_idcheck.txt').splitlines()[-1]}
```

De drie bekers staan hier met opzet niet bij: een beker heeft geen stand, dus `idcheck.py` kan hun
id niet op een bruikbare tabel controleren. Dat is ook de reden dat de drie vandaag niet in
`coverage.json` zijn gezet — zie bevinding 2 en het actiepunt in het dagrapport.

### `data/source-health.json` is bijgewerkt

Acht bronregels herschreven met wat deze run gemeten heeft: `fotmob` (de drie bekers in de
daglijst), `the_odds_api` (de twee ontbrekende sportkeys), `oddsapi` (9 van 1864 credits),
`betexplorer` (negen fixturepagina's, nul faalmodi), `understat` (drie duels), `api_football`
(besluit, geen gat), `teamnames` (de reparatie van vandaag) en `settling`. Geen enkele bron op een
foutstatus.

### Geen verplaatste wedstrijd, en geen stadionnaam om op te controleren (§1c)

`context.check_venue` is voor alle 22 duels gedraaid en gaf 22 keer `relocated = false`. Lees dat
met de beperking die §1c er zelf bij zet: de respons gaf voor **geen enkel duel** een stadionnaam
(`venue.name = null`), dus de controle vergeleek twee keer niets. `relocated = false` betekent
vandaag dus "niet gemeten" en niet "gemeten en in orde". Dezelfde stand als op 25 en 26 oktober.
Wat de controle hoe dan ook niet vangt, is dat een fixture van eigenaar is gewisseld — dat is nieuws
en geen data (Rennes – PSG, 23 aug 2026).

### Opstellingen

`lineupType` gaf bij geen enkel duel `confirmed`, wat te verwachten is om 03:30 NL bij aftrappen
tussen 18:00 en 21:00. Alle 22 duels leverden wél een opstellingsblok met uitvallers en
marktwaarde, en 17 ervan zijn in het contextlogboek beland.

### De runlijst is door een tweede bron bevestigd (§1)

Fotmob levert de daglijst, BetExplorer de fixturepagina per competitie. **Zestien van de zestien**
competities met een `fotmob_id` zijn het eens, inclusief de vijftien die vandaag `GEEN WEDSTRIJD`
hebben: 3 duels bij Fotmob tegen 3 bij BetExplorer, nul afwijkingen, geen enkele bron die faalde
(`ra_oct28_bevestiging.py`).

**En voor het eerst is dat óók voor de bekers met twee bronnen gelukt:** BetExplorer geeft 2, 8 en 9
duels in het venster en de Fotmob-daglijst dezelfde 2, 8 en 9. Alle vijf bekerslugs leveren
teamparen (40, 8, 8, 26 en 16), dus geen van de drie faalmodi van `scripts/betexplorer.py`
(homepage-redirect, teamparen zonder koers, lege pagina) is opgetreden. De twee bekers zonder ronde
staan alleen op BetExplorer, met als eerstvolgende ronde FA Cup 6 november 20:45 en Coppa Italia
1 december 21:00.

**Tijdzone:** BetExplorer labelt in UK-tijd, sinds de wintertijd GMT tegen CET in Nederland — nog
steeds precies één uur verschil, dus het venster `[27.10. 08:00 NL, 28.10. 08:00 NL)` is in UK-tijd
`[27.10. 07:00, 28.10. 07:00)`.

### Het inzetvenster (§3 Stage 1)

`runwindow.matches_for_run` met het venster `[27.10. 08:00 NL, 28.10. 08:00 NL)`; voor de drie
bekers is dezelfde band met de hand toegepast in `ra_oct28_cupmatches.py`, omdat die competities
geen `fotmob_id` in `coverage.json` hebben. **Alle 22 duels stonden op de daglijst van 27 oktober**
(`source_day` = DAY, geen enkel duel uit de band 00:00–08:00 van morgen) en **alle 22 zijn
`playable`**: de vroegste aftrap is 18:00 NL (vier DFB Pokal-duels) en de laatste 21:00 NL
(Fleetwood – Arsenal en Koninklijke HFC – Go Ahead Eagles). Geen duel was al afgetrapt voordat de
gebruiker kon inzetten, en er is geen carry-over-band. `runwindow` rekent met `zoneinfo`, dus het
venster is in échte NL-tijd gemeten (CET, +01:00).

### Wat anderen voorspellen (Stage 5, stap 2)

Geschreven voorspellingen zijn grotendeels niet te halen — §3 Stage 5 meet sinds 20 september dat
Forebet 403 geeft, de Pinnacle-artikelroute 404, Matchbook 530 en voetbalwedden.net de duels van de
dag niet noemt. Wat deze stap vandaag invult is de **prijs van Pinnacle apart**, los van de beste
prijs waarop wordt gespeeld.

**1X2** (`ra_oct28_pinnacle.py`): 3 van de 22 duels hebben een Pinnacle-1X2, alle drie in Serie A.
Gemiddelde Pinnacle-marge **3,51%**, gemiddelde absolute afstand tot het eigen oordeel **3,95 pp** —
dicht bij Pinnacle, en dus geen van de grote afwijkingen die op 26 oktober in de Super Lig stonden.
De negentien bekerduels hebben geen Pinnacle-prijs, want twee van de drie bekers hebben geen
sportkey.

**Doelpunten** (`ra_oct28_pinnacle_ou.py`, push-gecorrigeerd zoals op 25 oktober gerepareerd):
dezelfde 3 duels, en **alle drie boven Pinnacle op de Under-kant**, gemiddeld +9,93 pp —
Sassuolo – Lazio +14,26 pp op lijn 2.75, Torino – Como +9,76 pp en Roma – Cagliari +5,76 pp. Zie de
kop van dit rapport: dit is meting 2 van de drie die vandaag dezelfde kant op wijzen.

**Harde grens (§2/§4):** geen van deze getallen gaat in `my_prob` of in `prob_sources`. Ze horen in
de vergelijking en niet in de kansschatting.

### Understat — de tweede, onafhankelijke xG-bron (§4)

Eén van de vijf Understat-competities speelde vandaag (Serie A), en voor **alle drie** de duels is
een tweede, onafhankelijk xG-model geleverd, inclusief rollende xG over acht duels. Dat raakt dus
alle drie de gepubliceerde regels — een gunstiger stand dan gisteren, toen één van de drie bets een
Understat-arm had. De negentien bekerduels leunen uitsluitend op Fotmob, in twee doorsnedes van
dezelfde meting; op een bekerdag is de afhankelijkheid van die ene bron dus groter dan op een gewone
competitiedag.

### Vroeg-seizoenscorrectie en het competitieniveau (§3 Stage 5)

`model.uplift_observations` + `early_season_uplift`: factor **1,0949**, berekend uit een gepoolde
1,1179 over **33 speeldagen** in **vier** competities. **Geen enkele competitie is overgeslagen in
de pool** (`overgeslagen` is leeg), en dat is vandaag vanzelfsprekend: de vier zijn Serie A en de
drie basisdivisies van de bekers (Premier League, Bundesliga, Eredivisie), alle vier op 7 tot 10
speeldagen van een seizoen van 34 of 38 — ruim onder de helft van `SEASON_MATURE_SHARE`.

Alle **zeven** competitiebases lopen daarom de route `vorig+uplift`. `model.league_level` per basis:

| Basis | Route | thuis / uit / basis |
|---|---|---|
| Serie A (ITA) | `vorig+uplift` | 1,397 / 1,259 / 1,401 |
| League Cup (ENG) → Premier League | `vorig+uplift` | 1,671 / 1,340 / 1,424 |
| League One (ENG) | `vorig+uplift` | 1,619 / 1,262 / 1,400 |
| DFB Pokal (GER) → Bundesliga | `vorig+uplift` | 1,947 / 1,596 / 1,669 |
| 2. Bundesliga (GER) | `vorig+uplift` | 1,785 / 1,424 / 1,567 |
| KNVB Beker (NED) → Eredivisie | `vorig+uplift` | 1,972 / 1,506 / 1,657 |
| Eerste Divisie (NED) | `vorig+uplift` | 1,902 / 1,596 / 1,716 |

**Let op de factor, want hij staat hoger dan de 1,0606 van gisteren.** De pool bestaat vandaag uit
andere competities — de drie bekerbases in plaats van vijf Zuid-Europese competities — en §3 Stage 5
waarschuwt uitdrukkelijk dat de pool competitie-overstijgend is en dus meebeweegt met wie erin zit.
Dat is geen drift in de meting maar een andere steekproef.

**De meting naast de markt** (controleren, niet fitten — §2): de gemiddelde absolute afstand van het
eigen 1X2 tot het Pinnacle-oordeel is 3,95 pp over 3 duels, zonder systematische kant.

## Afwikkeling (Stage 0)

Vier picks en tien schaduwrijen van 26 oktober afgewikkeld. **Alle veertien zijn competitieduels,
dus `status.scoreStr` van Fotmob *is* de stand na 90 minuten** en er hoefde geen doelpuntminuut te
worden opgezocht (§6d). Daarna stonden `ledger.py open` en `shadow.py open` beide op nul.

| Pick | Markt | Koers | Uitslag | Resultaat | verwacht/werkelijk doelpunten |
|---|---|---|---|---|---|
| Paris Saint-Germain – Lyon | Under 2.5 | 3.15 | 2-0 | **gewonnen** | 3,22 verwacht / 2 werkelijk |
| Beşiktaş – Başakşehir | Under 3.5 | 1.80 | 2-0 | **gewonnen** | 3,29 / 2 |
| Santa Clara – Benfica | Under 2.5 | 2.0976 | 1-2 | verloren | 2,29 / 3 |
| Walsall – Salford City | Under 2.5 | 2.23 | 2-4 | verloren | 2,50 / 6 |

Schaduwrijen: **4 gewonnen, 6 verloren** over vijf poorten — `underdog` 5 rijen (3 gewonnen),
`doelpunten_onder` 3 rijen (1 gewonnen), `context` 1 (verloren) en `tweede_methode` 1 (verloren).

Ook gedraaid: `calibration.py settle` (33 waarnemingen afgewikkeld; 6267 van 6294 compleet) en
`ctxlog.py settle` (13 wedstrijden). `recalibrate.load_fit().fitted_through` staat daarmee op
**2026-10-26**, dus op de vorige rundag, zoals §6b-5c eist.

### De reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)

**1. Klopte de redenering, of klopte alleen de uitkomst?** Hier zit het ongemakkelijke deel, en het
wijst precies de verkeerde kant op. Bij de **twee winnaars** lag de werkelijke uitslag ver **onder**
de eigen lambda: PSG – Lyon verwachtte 3,22 doelpunten en er vielen 2, Beşiktaş – Başakşehir
verwachtte 3,29 en er vielen 2. Beide bets waren dus gewonnen **terwijl het eigen model een
doelpuntrijke wedstrijd voorspelde** — ze stonden op de lijst omdat de bookmaker nóg verder de
andere kant op zat, niet omdat het model weinig doelpunten zag. Bij de **twee verliezers** was het
omgekeerd en forser: Santa Clara – Benfica 3 tegen 2,29 verwacht, en Walsall – Salford **6 tegen
2,50** — een afwijking van drieënhalf doelpunt. Over de vier picks samen: 13 werkelijke doelpunten
tegen 11,3 verwacht.

**2. Deden de poorten die iets tegenhielden hun werk, in dít geval?** Gemengd, en op één punt
ongemakkelijk. **Poort 8 hield er vijf tegen en drie daarvan zouden hebben gewonnen** — Santa Clara
+1.5 (1-2), OB Odense +1 (1-1) en Burgos +0.25 (2-3). Dat kost deze poort op één dag drie winnaars.
**Poort 9 hield drie kandidaten tegen en deed het in twee van de drie goed:** Walsall Under 2.75 (6
doelpunten tegen 2,50 verwacht) en Flamengo – Atlético-MG Under 3 (5 tegen 2,73) waren beide
verloren geweest; alleen PSG – Lyon Under 3.5 had gewonnen. Dat zijn precies de twee
uitschietersduels waarvoor die poort is gemaakt.

**3. Zat er een patroon in de dag dat geen toeval kan zijn?** Twee, en ze hangen samen. (a) In
**beide** verliezende Unders viel het werkelijke totaal boven de eigen lambda en in **beide**
winnende eronder — vier van vier in dezelfde ordening. (b) De drie `doelpunten_onder`-rijen gaven
twee duels met 5 en 6 doelpunten tegen lambdas van 2,73 en 2,50. Dat is dezelfde richting als de
+0,581 doelpunt per duel die `goalbias` over 100 gespeelde Unders meet.

**4. En dan de rem erop: wat betekent dit NIET?** Eén dag is geen reeks. Vier picks en tien
schaduwrijen zijn ver onder de ~30 afgewikkelde gevallen die §6d eist voordat een reeks gelezen mag
worden, en de drie winnaars die poort 8 gisteren tegenhield zijn vijf gevallen op een reeks van
**237** die op −4,0% staat. De `doelpunten_onder`-reeks staat na vandaag op **21** afgewikkelde
rijen (42,9% trefkans, −18,3%), nog steeds onder de dertig. Er wordt op grond van gisteren dus geen
enkele drempel, geen gewicht en geen poort verzet. Wat deze dag wél doet, is het patroon van §6g
nog eens laten zien op vier verse gevallen — en dat is de reden dat het hierboven bij de bets staat
en niet alleen hier.

## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
{dekking}

Geen enkele competitie viel onder `AFGEKAPT`: 22 duels op een cap van 40. De laagste datarijkdom in
de run is **4,5** en de hoogste **7,0**; omdat er niets is afgekapt zijn er geen twee scores rond de
grens te noemen (§3 Stage 4).

## Topselectie (§5b — rangorde over de hele runlijst)

| # | Wedstrijd | Markt / selectie | Koers | Kans | Edge | Score | Tier | Risico | Lat gehaald? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sassuolo – Lazio | Over/Under — Under 2.75 | 2.06 (Pinnacle) | 63,7% | **+15,15 pp** | 9,649 | FULL | High | **ja** — en ook de verzwaarde lat van poort 9 (10,0 pp) |
| 2 | Torino – Como | BTTS — nee | 2.3524 (Matchbook, beurs: 2.38 bruto) | 47,8% | +5,28 pp | 2,523 | FULL | High | nee — op rangorde (§5b) |
| 3 | Roma – Cagliari | Over/Under — Under 3 | 1.84 (Coolbet) | 58,2% | +3,82 pp | 2,222 | FULL | Medium | nee — op rangorde (§5b) |

**Waarom deze wél en de eerstvolgende net niet.** Er zijn precies drie duels met een publiceerbare
selectie en er passen drie regels in (`MAX_SHORTLIST` = 3, dinsdag), dus de lijstlengte bindt niet
en er valt **geen** gekwalificeerde selectie af. De eerstvolgende kandidaat is er dus niet: wat
daaronder staat is door een poort tegengehouden (zie "Net niet") of haalt de ondergrens van 3,0 pp
niet die `toplist._publiceerbaar` aanhoudt — wat te zwak is om te loggen, is te zwak om te spelen.
`MAX_LIGHT_IN_SHORTLIST` = 2 bindt niet: alle drie de regels staan op `FULL`.

**Welke selectie binnen de wedstrijd tweede werd** (§1a eist dit per bet): bij Sassuolo – Lazio was
dat Under 3 @1.75 (+13,67 pp, score 9,679 ruw / lager herijkt) — dezelfde mening op een andere lijn,
en dat is precies het geval waarvoor de 0-of-1-bet-regel bestaat. Bij Torino – Como was Under 2.75
@2.05 de sterkere uitdrukking op de ruwe schaal (+5,69 pp), maar die sneuvelde op poort 5 (de twee
methodes wijzen tegengesteld), waardoor BTTS "nee" overbleef.

### De ruwe dagranglijst (§5a) — een meting, geen tip

| # | Wedstrijd | Markt / selectie | Koers | Ruwe edge | Ruwe score | Uitkomst |
|---|---|---|---|---|---|---|
| 1 | Sassuolo – Lazio | Over/Under — Under 2.75 | 2.06 | +15,64 pp | 10,038 | BET |
| 2 | Torino – Como | Over/Under — Under 2.75 | 2.05 | +5,69 pp | 3,099 | de twee methodes wijzen tegengesteld |
| 3 | Roma – Cagliari | Over/Under — Under 3 | 1.84 | +4,24 pp | 2,484 | edge onder de drempel |

**Nul selecties sneuvelden alleen op de herijking** (§1g), dus de reeks `zonder_herijking` groeit
vandaag niet. Eén van de drie gepubliceerde regels haalt de lat ook op de ruwe schaal
(`bet_beide = true`).

**En lees wat er NIET meer in deze lijst staat, want dat is het scherpste geval van de dag.** In de
eerste doorrekening van vanmorgen stond op plek 2 van de ruwe lijst **Excelsior '31 – ADO Den Haag,
1X2 op de thuisploeg @12,66 met +37,85 pp** en een ruwe `selection_score` van 8,658 — de hoogste
ruwe edge van de hele run. Dat getal bestond **alleen** doordat `Excelsior '31` (Tweede Divisie,
Rijssen) aan `Excelsior` (Eredivisie, Rotterdam) was gekoppeld; na de reparatie van bevinding 1 is
het duel `NONE` en is de regel verdwenen.

**Wat er tussen die schijnedge en een gepubliceerde regel stond, was alleen poort 2** — de koersband
`MAX_ODDS` = 6,00. Die poort bestaat om een heel andere reden (buiten de band is de kansschatting te
onnauwkeurig om edge zinvol te noemen, §0) en is **geen verdediging tegen een verkeerde ploeg**: hij
hield deze selectie bij toeval tegen, omdat de koers van een amateurclub tegen een profclub nu
eenmaal hoog is. Was het een Eerste-Divisieclub geweest met een koers van 4,50, dan had niets hem
tegengehouden — de edge-drempel al niet, want +37,85 pp haalt elke lat. Van de 79 selecties van ná
de reparatie vallen er nog twee op `odds` (Cagliari @10,80 en Werder Bremen @7,20), tegen zes
ervoor.

**De les die wél blijft staan:** dat de grootste geclaimde edge van de dag bij de zwakste ploeg op
de hoogste koers stond, is precies het patroon waar §1g voor waarschuwt — alleen was het hier geen
modelfout maar een verkeerde ploeg, en dat is een categorie die §1g niet dekt.

## Marktbalans (§5, verplicht)

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 4 van 4 (2 betaald, 2 gratis marktgemiddelde) | 29 | 0 |
| Asian Handicap · DNB · Double Chance | 2 van 4 (uit de spreads van de bulk) | 14 + 2 + 2 | 0 |
| Over/Under | 2 van 4 | 26 | **2** |
| BTTS | 1 van 4 (4 duels, tweede ronde) | 6 | **1** |

**De controle van §1a is gehaald op de inkoop, niet op de uitkomst, en het is nuttig te zeggen hoe
ruim:** beide inkoopbare competities (Serie A en DFB Pokal) kregen de bulk-aanroep met zowel een
uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U) — **2 van 2**, waar de controle er
één eist. Daarna kregen 4 duels de tweede ronde BTTS. Totaal **9 van 1864 credits**: 2 bulk-aanroepen
à 3 credits en 4 event-aanroepen à 1 credit (het plafond kwam uit `suggest_cap(18661, 5)`).

**Dat de twee bekers zonder sportkey alleen een gratis 1X2 kregen, is géén krap plafond maar een
ontbrekende competitie bij de bron** — zie "Bronstatus deze run". Dat raakt elf van de 22 duels, en
daarmee ook de vraag of §1a's balanscontrole hier wel het juiste meet: hij toetst of het *budget*
scheef is ingekocht, en vandaag is de scheefheid dat de bron twee van de vier competities niet heeft.
De drie gepubliceerde bets komen uit twee verschillende markten (Over/Under en BTTS), dus de
eenzijdigheid van 29 augustus doet zich niet voor; wél wedden alle drie op dezelfde **kant** —
weinig doelpunten — en dat staat bovenaan dit rapport.

### Net niet

| Wedstrijd | Tier | Markt / selectie | xG-model | 2e methode | zwakste stand | valt af op |
|---|---|---|---|---|---|---|
{netniet}

**De poortverdeling van vandaag is scheef, en dat is zelf een waarneming.** Van de 79 doorgerekende
selecties sneuvelen er **62 op `tweede_methode`** (poort 5), over 9 van de 10 doorgerekende duels;
daarnaast 6 op `context` (poort 7), 2 op de koersband (poort 2) en 5 op `edge`, en 4 halen alle
negen poorten. §5 "Net niet" noemt precies dit het signaal om op te letten: *"valt er een week lang
alles af op `tweede_methode`, dan is de vraag of de twee methodes systematisch uiteenlopen — en dat
is een bevinding, geen ruis."*

**Eén dag is geen week, en vandaag is er een verklaring die geen bevinding is:** negentien van de 22
duels zijn bekerwedstrijden tussen ploegen van **ongelijke** sterkte, en juist daar lopen een
xG-model en een thuis/uit-doelpuntensplitsing het verst uiteen. De splitsmethode is bovendien sinds
§6e (22 aug) al de scheefste van de twee. Het staat hier **met een getal** zodat een volgende run
kan zien of het aanhoudt op een gewone competitiedag; er wordt vandaag geen poort en geen gewicht op
verzet (§6d). De reeks `tweede_methode` staat op 218 kandidaten, 209 afgewikkeld, −9,7% — die poort
bespaart tot nu toe aantoonbaar geld.

**Poort 8 en poort 9 binden vandaag nergens**, op geen van beide schalen: `poort8_geblokkeerd`,
`poort8_ruw` en `poort9_geblokkeerd` zijn alle drie leeg. Dat is geen versoepeling maar de
**poortvolgorde**, en het is exact het mechanisme dat §1e op 15 september beschrijft voor de reeks
die niet wilde groeien: `tweede_methode` staat vóór `underdog`, en wat die poort afvangt komt bij
poort 8 niet eens aan. Beide zijn met `today=2026-10-28` aangeroepen, zodat het stilstandvenster van
25 t/m 30 september (`sides.LAPSED_FROM`/`LAPSED_UNTIL`) en de ingangsdatum van poort 9
(`unders.BINDS_FROM`) uit de code worden gelezen in plaats van geraden.

## Wedstrijden

{wedstrijden}

## Bevindingen

### 1. `ra_names.resolve` koppelde FC Eindhoven aan PSV Eindhoven, en geen van de negen poorten kan dat zien

`tmp-run/ra_names.resolve` had als laatste koppelregel een **deelverzameling** van tokens:

```python
tn = tokens(name)
hits = [k for k in table if tokens(k) <= tn or tn <= tokens(k)]
if len(hits) == 1:
    return hits[0]
```

Een deelverzameling zegt alleen dat alle woorden van de korte naam in de lange voorkomen, en **niet
wáár**. `fc` staat in `teamnames._DROP`, dus:

```
tokens("FC Eindhoven")  = {{eindhoven}}
tokens("PSV Eindhoven") = {{eindhoven, psv}}
```

en `{{eindhoven}} ⊆ {{eindhoven, psv}}` is waar. In de Eredivisie-stand van 2025/2026 is **PSV
Eindhoven de enige ploeg** die aan die eis doet, dus `len(hits) == 1` en de veiligheidsregel "alleen
accepteren bij precies één kandidaat" hielp niet.

**Wat het zou hebben gekost.** FC Eindhoven – FC Volendam (KNVB Beker, 20:00 NL) kwam daarmee uit op
`tier = FULL` met `table_home = "PSV Eindhoven"` — de xG en de thuis/uit-splits van de landskampioen
achter een Eerste-Divisieclub. Dat is een andere categorie fout dan de `ob`-alias van gisteren of de
`qpr`-koppeling van 9 oktober: die maakten een **poort blind**, deze levert een **verkeerde ploeg**.
Alle negen poorten toetsen of een kans te ruim is, of de koers in de band valt, of de twee methodes
elkaar tegenspreken, of de context meewerkt — geen enkele toetst of het de juiste ploeg is. Het duel
zou als volledig onderbouwd te boek hebben gestaan.

**De eerste reparatie was de regel die §4 al voorschrijft — en die bleek niet genoeg.** Die
paragraaf zegt het bij `promotion.measure_gap` met zoveel woorden: *"`find_team` accepteert een
afkorting alleen als **voorvoegsel** (`Ipswich` op `Ipswich Town` wel, `Ajax` op `Jong Ajax`
niet)"* — en de aanleiding daar was identiek, een naamkoppeling die `Jong Ajax` aan `Ajax` koppelde
en een "promovendus-behoudt-zijn-aanval"-factor van 1.010 opleverde. Die voorvoegselregel is
ingevoerd, de dag is opnieuw doorgerekend, en toen liep er **een tweede geval door hetzelfde gat**:

```
ordered_tokens("Excelsior '31") = ['excelsior', '31']
ordered_tokens("Excelsior")     = ['excelsior']
```

`['excelsior']` is een **leidend voorvoegsel** van `['excelsior', '31']`, dus de nieuwe regel
accepteerde het — en koppelde **Excelsior '31** (Tweede Divisie, Rijssen) aan **Excelsior**
(Eredivisie, Rotterdam). Twee verschillende clubs, en hier zit het onderscheidende deel in de
**staart** in plaats van in de kop.

**De les van die twee samen: er is geen positieregel die beide gevallen vangt.** Het
onderscheidende deel van een clubnaam kan vooraan staan (`PSV`, `Jong`, `Sporting`) of achteraan
(`'31`, `II`, `Kerkrade`). Wat deze lus werkelijk hoort op te vangen is alleen het verschil in
**ruiswoorden** — de daglijst schrijft `Wigan` en de tabel `Wigan Athletic`, de daglijst `Ipswich`
en de tabel `Ipswich Town`, en `athletic`, `town` en `fc` staan allemaal in `_DROP`. De eis is
daarom: **gelijk ná het weglaten van `_DROP`, en anders niet.**

```python
def is_abbreviation(a, b):
    ta, tb = ordered_tokens(a), ordered_tokens(b)
    return bool(ta) and ta == tb
```

Een echte afkorting die méér weglaat dan een ruiswoord — `QPR`, `M'gladbach` — hoort in `ALIASES`
te staan, waar ze **expliciet en na te lopen** is, en niet in een regel die raadt. Dat is precies
wat de alias van gisteren (`ob → odense`) ook is.

De functie staat **in `scripts/` en niet in `tmp-run/`**, en dat is dezelfde les als bij de
`ob`-alias van gisteren: een module in `scripts/` kan niet uit `tmp-run/` importeren, dus een
koppelregel die daar blijft hangen wordt een tweede, afwijkende implementatie.

**Regressie, want een reparatie die iets anders breekt is geen reparatie.** Alle 44 teamnamen van
vandaag zijn langs de oude en de nieuwe regel gelegd (`ra_oct28_namecheck.py`, plus 24
zelftestgevallen): **precies twee verschillen**, en dat zijn exact deze twee ploegen — FC Eindhoven
(nu `None`, dus langs de promovendi-omrekening van §4, waar hij op `conversion_in_range` alsnog op
`NONE` uitkomt) en Excelsior '31 (nu `None`, want hij staat niet in de Eerste Divisie-stand).
**Geen enkele andere koppeling verandert.** Eén verwachting in de eerste opzet van die zelftest was
overigens van mijzelf fout en niet van de regel: `Athletic Bilbao` normaliseert naar `bilbao` omdat
`athletic` in `_DROP` staat, dus die twee namen zijn na normalisatie gewoon gelijk en horen te
koppelen.

**En wat de run dit heeft gekost: twee volledige herdraaiingen op dezelfde, al ingekochte prijzen,
samen nul extra credits.** De eerste na de voorvoegselregel, de tweede na de gelijkheidsregel. De
gepubliceerde lijst is in alle drie de doorrekeningen **identiek** gebleven (dezelfde drie Serie
A-regels, dezelfde koersen, dezelfde edges) — wat verandert is de ruwe dagranglijst, het aantal
doorgerekende duels (11 → 10), het aantal selecties (83 → 79) en het kalibratielogboek (33 → 30
waarnemingen). De rijen van de eerste twee doorrekeningen zijn uit `picks.jsonl`, `shadow.jsonl`,
`calibration.jsonl` en `context-log.jsonl` verwijderd voordat de definitieve zijn weggeschreven.

**Wat niet is aangeraakt, en waarom.** `scripts/settling.py` heeft op regel 136 **dezelfde**
deelverzamelingsregel. Daar is ze met opzet ruim — de docstring zegt *"ruim, niet streng"* — en
beslist `lookup` op het **paar** thuis-en-uit plus de eis van precies één kandidaat, dus de rem zit
er ergens anders. Vandaag zijn langs dat pad veertien uitslagen afgewikkeld en alle veertien kwamen
bij de juiste wedstrijd uit. Een poort verzetten die niet knelt is geen werk dat een run op eigen
initiatief doet, en een verkeerde ingreep daar zou uitslagen kunnen verschuiven. **Wat wél
openstaat** is de vraag of die ruime regel in de 63 rundagen hiervoor ooit een uitslag bij de
verkeerde wedstrijd heeft gezet — die vraag stond er al sinds 25 oktober en is vandaag scherper
geworden. Staat als actiepunt met `owner = ik` in het dagrapport.

### 2. De drie bekers staan wél in de Fotmob-daglijst, en het gat zat in `coverage.json`

De vijf bekers van `prompts/run-a.md` hebben **geen `fotmob_id`** in `data/coverage.json`:

```
FA Cup (ENG)        -> {{'prob_sources': ['fotmob', 'fbref', 'forebet']}}
League Cup (ENG)    -> {{'prob_sources': ['fotmob', 'fbref', 'forebet']}}
Coppa Italia (ITA)  -> {{'prob_sources': ['fotmob', 'fbref', 'forebet']}}
KNVB Beker (NED)    -> {{'prob_sources': ['fotmob', 'fbref', 'footystats', 'forebet']}}
DFB Pokal (GER)     -> {{'prob_sources': ['fotmob', 'fbref', 'forebet']}}
```

Zonder id kan `runwindow.matches_for_run` ze niet uit de daglijst filteren, dus elke run van oktober
heeft ze langs BetExplorer gedaan. Vandaag leverde die route 19 duels in het venster — en de
Fotmob-daglijst van 27 oktober heeft ze alle drie gewoon staan:

| Competitie | Fotmob-daglijst | BetExplorer |
|---|---|---|
| League Cup (ENG) | id **133** ("EFL Cup"), 2 duels | 2 duels in het venster |
| DFB Pokal (GER) | id **209**, 8 duels | 8 duels |
| KNVB Beker (NED) | id **235** ("KNVB Cup"), 9 duels | 9 duels |

**Dezelfde aantallen bij beide bronnen, dus de dag is voor het eerst ook voor de bekers met twee
methodes vastgesteld** (§1) in plaats van met één.

**Het gat zat dus niet in de bron maar in de administratie, en dat is de stille faalvorm van
§6b-5b:** een controle die groen staat omdat ze een rij niet meet. `progress.py verify` kijkt of de
zes markten zijn doorgerekend, `idcheck.py` of de 33 competitie-id's een bruikbare stand geven —
geen van beide zegt iets over een competitie die helemaal geen id heeft.

**Wat het praktisch uitmaakt.** Via de daglijst komen de duels mét `match_id`, en daarmee met
context, voorspelde opstelling, uitvallers met marktwaarde, vorm, rustdagen en dus met een werkende
poort 7; via BetExplorer alleen met namen en een koers. **Dat is precies wat het op 6 oktober
kostte:** de FA Cup-kwalificatie stond toen niet in de daglijst en wél bij BetExplorer, en vier van
de vijf duels kwamen daardoor op `NONE` uit. Vandaag zijn alle negentien bekerduels mét context de
analyse in gegaan (`ra_oct28_cupmatches.py` haalt ze uit de daglijst, `ra_oct28_merge_cups.py` zet ze
in het Stage 3-record met `promotion.CUP_BASE` als `primaryId`).

**De drie id's zijn níet in `coverage.json` gezet, en dat is een keuze.** Ze zijn vandaag voor het
eerst gemeten, op één dag, en een beker heeft geen stand — dus `idcheck.py` kan ze niet groen
verklaren zoals het de 33 competitie-id's doet. De voor de hand liggende volgende stap is nagaan of
die id's ook op dagen **zonder** bekerronde het juiste antwoord geven: een id dat elke opgevraagde
dag dezelfde lijst teruggeeft is precies de stille faalstand die §4 bij de Hongaarse NB II (id 9117)
beschrijft. En voor de FA Cup en de Coppa Italia is er nog geen id, want die speelden vandaag niet.
Zolang dat zo is blijft de BetExplorer-route voor alle vijf de bekers staan, dus er gaat geen
wedstrijd verloren. Actiepunt met `owner = ik` in het dagrapport.

### 3. Elf van de 22 duels op `NONE`, en dat is bij een bekerronde het juiste antwoord

Geen bevinding over een fout maar over de **vorm van een bekerdag**, en het is nuttig om de elf uit
te splitsen, want "geen datadekking" dekt twee heel verschillende gevallen:

| Duel | Reden | Soort |
|---|---|---|
| Fleetwood Town – Arsenal | Fleetwood staat niet in de Championship-stand (twee divisies onder de Premier League) | geen meting mogelijk |
| RW Essen – RB Leipzig | RW Essen staat niet in de 2. Bundesliga-stand (3. Liga) | geen meting mogelijk |
| Sonnenhof Großaspach – Augsburg | idem (Regionalliga) | geen meting mogelijk |
| Barendrecht – RKC Waalwijk | Barendrecht staat niet in de Eerste Divisie-stand | geen meting mogelijk |
| Kloetinge – Cambuur | idem | geen meting mogelijk |
| Rijnsburgse Boys – FC Den Bosch | idem | geen meting mogelijk |
| Koninklijke HFC – Go Ahead Eagles | idem | geen meting mogelijk |
| Bochum – Mainz 05 | omgerekend, maar buiten `conversion_in_range` | Coventry-val |
| Borussia Mönchengladbach – Karlsruher SC | idem | Coventry-val |
| FC Eindhoven – FC Volendam | idem | Coventry-val |
| Telstar – Almere City FC | idem | Coventry-val |

De eerste zeven zijn **één divisie te diep**: §4 rekent uitdrukkelijk één divisie om en niet twee,
want verder is er geen meting. De laatste vier zijn de **Coventry-val** waarvoor
`promotion.conversion_in_range` bestaat: de ploeg is wél omgerekend, maar zijn relatieve sterkte
valt buiten het bereik waarin de divisiefactor ooit is gemeten, en buiten dat bereik is er geen
onafhankelijke kansinput op het niveau waarop gespeeld wordt. Dat is een **poort en geen
aantekening** (§4), en zonder die poort kost hij volgens die paragraaf +21 pp schijnedge die alle
andere poorten haalt.

**Drie duels zijn door `shared_lower_division` gered** (§4, 15 sep 2026), en dat is de tegenhanger:
staan beide ploegen in dezelfde divisie **onder** de basis, dan valt er niets te overbruggen en is
het duel daarin gewoon door te rekenen. Bradford City – Peterborough United loopt via League One
(`FULL`), Elversberg – Darmstadt via de 2. Bundesliga (`FULL`), en Helmond Sport – Willem II en
Roda JC – De Graafschap via de Eerste Divisie (`LIGHT`, want die divisie heeft geen xG bij Fotmob).
Daar geldt "een omgerekende ploeg is nooit `FULL`" niet, want er is niets omgerekend.

### 4. Alle drie de regels wedden op weinig doelpunten, en drie onafhankelijke metingen wijzen daar tegenin

Dit staat volledig in de kop van dit rapport en wordt hier niet herhaald. Wat hier hoort is de
**rem**: §1h punt 3 en §6g leggen vast dat een run een poort nooit op eigen initiatief verzet en dat
de vraag pas opnieuw aan de gebruiker wordt voorgelegd als de reeks `doelpunten_onder` van teken
draait of als de vormfout van §6g is gerepareerd. **Geen van beide is gebeurd:** die reeks staat na
vandaag op 21 afgewikkelde rijen (42,9% trefkans, −18,3%) waar §6d er ~30 eist, en de vormfout is er
nog — keuze (a) van 11 oktober staat nog open en blijft het echte werk. De vraag die wél in het
dagrapport staat (met `owner = besluit`) is een andere en volgt uit §5b zelf: of de gebruiker de
lijst wil beperken tot regels die hun eigen lat halen, nu twee van de drie dat de tweede dag op rij
niet doen.

## Stand van het logboek

### `ledger.py stats` — wat er wél doorheen kwam

```
{blok('ra_oct28_ledger.txt')}
```

### `shadow.py stats` — wat de poorten hebben tegengehouden

```
{blok('ra_oct28_shadow.txt')}
```

### `recalibrate.py show` — de stand van de herijking (§1g)

```
{blok('ra_oct28_recalibrate.txt')}
```

`fitted_through` staat op **2026-10-26**, dus op de vorige rundag, zoals §6b-5c eist — de 33
waarnemingen van 26 oktober zijn vanmorgen door `calibration.py settle` afgewikkeld voordat de fit
is gelezen. De fit **verlaagt** vandaag over vrijwel de hele speelbare band (−0,1 pp op 40%, −0,3 pp
op 50%, −0,6 pp op 70%), dus een selectie die de herijkte lat haalt haalt hem ook ruw. Dat is bij
de enige regel bóven de lat ook zo (`bet_beide = true`). Vertrouw die vlag en niet de redenering —
§5a waarschuwt daar uitdrukkelijk voor, want de fit is elke run een ander getal.

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

### `ctxlog.py stats` — het contextlogboek (§1c)

```
{blok('ra_oct28_ctxstats.txt')}
```

### `scripts/branchaudit.py` — Stage -2 per record op de inhoud

```
{blok('ra_oct28_branchaudit.txt')}
```

## Openstaand

1. **De drie bekernummers vast in `coverage.json` zetten** (werk voor mij). Zie bevinding 2: eerst
   nagaan of id 133, 209 en 235 ook op dagen zonder bekerronde het juiste antwoord geven, met de
   controle die §4 bij de Hongaarse NB II voorschrijft (twee ver uit elkaar liggende opvragingen
   vergelijken). Voor de FA Cup en de Coppa Italia is er nog geen id; die speelden vandaag niet.
2. **De audit over `scripts/settling.py`** (werk voor mij). Onveranderd sinds 25 oktober, en vandaag
   scherper geworden: heeft de ruime deelverzamelingsregel in de 63 rundagen hiervoor ooit een
   uitslag bij de verkeerde wedstrijd gezet?
3. **Er is geen controle die méldt dat een doorgerekend duel geen marktgemiddelde of geen beste
   prijs heeft** (werk voor mij). Onveranderd sinds 26 oktober. Vandaag raakt het elf van de 22
   duels, en de oorzaak is deze keer bekend en legitiem (twee bekers zonder sportkey) — maar dat de
   routine dat zelf nergens als getal vastlegt, is dezelfde structurele leemte.
4. **De vormfout in `score_grid` repareren** (keuze (a) van 11 oktober, werk voor mij). Staat nog
   open en blijft het echte werk onder poort 9; raakt alle zes de markten, dus eerst doorrekenen wat
   het met de andere vijf doet.
5. **De `detail`-velden in `source-health.json` groeien onbeperkt** (werk voor mij). Onveranderd.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""

open("runs/2026-10-28-run-a.md", "w").write(MD_TEXT)
print(f"runs/2026-10-28-run-a.md geschreven — {len(MD_TEXT)} tekens, "
      f"{len(MD_TEXT.splitlines())} regels")
