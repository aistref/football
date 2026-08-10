# Gedeelde analyseregels — Run A & Run B

Deze regels gelden voor **elke** run. Wijzig ze hier in de repo, niet in de scheduler.
De scheduler-prompt is met opzet kort en verwijst naar dit bestand, zodat je regels kunt
aanpassen zonder de geplande taak aan te raken.

---

## 0. Vaste parameters

| Parameter | Waarde | Waarom |
|---|---|---|
| `MAX_DEEP_ANALYSES` | **30** | Harde cap. Zonder cap loopt een run met 40+ wedstrijden altijd zijn tijdslimiet in en levert een halve lijst. Verhoogd van 12 naar 30 op 8 aug 2026 nadat `scripts/fotmob.py`, `scripts/model.py`, `scripts/betexplorer.py` en `scripts/oddsapi.py` de ophaal- en rekenlogica herbruikbaar maakten — zie de toelichting eronder. |
| `MAX_SHORTLIST` | **3** (ma–do) / **5** (vr–zo) | Onveranderd t.o.v. de oude opdracht. |
| `EDGE_THRESHOLD_FULL` | **3.0 procentpunt** | Onder deze grens is de schatting niet te onderscheiden van modelruis. |
| `EDGE_THRESHOLD_LIGHT` | **6.0 procentpunt** | Zwakkere data eist een grotere marge. |
| `MAX_LIGHT_IN_SHORTLIST` | **2** | Voorkomt dat de topselectie volloopt met zwak onderbouwde bets. |
| `MIN_ODDS` / `MAX_ODDS` | **1.30** / **6.00** | Buiten deze band is de kansschatting te onnauwkeurig om edge zinvol te noemen. |
| `SETTLE_AFTER_HOURS` | **12** | Openstaande picks ouder dan dit worden afgewikkeld. |

---

## 1. Selectie: **0 of 1** bet per wedstrijd

> Dit vervangt de oude regel "exact één beste valuebet per wedstrijd".

Per geanalyseerde wedstrijd geldt precies één van twee uitkomsten:

- **BET** — er is één markt/selectie die alle poorten hieronder passeert.
- **GEEN BET** — met een reden in één regel. Dit is een volwaardige, correcte uitkomst.

Een bet mag alleen gepubliceerd worden als **alle** voorwaarden gelden:

1. `edge_pp ≥ EDGE_THRESHOLD_FULL` bij `data_tier = FULL`, of `≥ EDGE_THRESHOLD_LIGHT` bij `LIGHT`;
2. `MIN_ODDS ≤ odds ≤ MAX_ODDS`;
3. de anti-circulariteitsregel (§2) is voldaan;
4. `data_tier ≠ NONE`;
5. **twee methodes bevestigen de edge.** `model.analyze_match` (op xG) én
   `model.analyze_match_from_splits` (op wat de ploegen thuis en uit werkelijk scoorden) moeten
   allebei boven de drempel uitkomen. Zakt de tweede eronder, dan hangt de edge aan één
   modelkeuze en gaat de bet eruit met reden "data conflicterend".

Toegevoegd op 9 aug 2026, met een concreet geval: Gil Vicente – Rio Ave stond op het xG-model op
+10.3 pp — de op één na grootste edge van die dag — en op de tweede methode op +2.7 pp. De twee
bets die wél werden gepubliceerd, werden door beide bevestigd.

**Een run met nul bets is geen mislukte run.** Nul bets rapporteren met een heldere reden is
correct gedrag; bets forceren om het format te vullen is dat niet.

Ga alle markten langs — 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS —
en publiceer alleen de sterkste. Geen "gevoel", geen reputatie-argumenten.

---

## 2. Anti-circulariteitsregel (hard, niet optioneel)

`my_prob` mag **nooit** afgeleid zijn van de odds waartegen je hem afzet. Doe je dat, dan meet
`edge = my_prob − implied_prob` alleen je eigen afwijking van de markt, zonder onafhankelijk
anker — een getal dat overtuigend lijkt en niets betekent.

Daarom: elke bet heeft **minstens één onafhankelijke kansinput** in `prob_sources`, en die mag
géén bookmaker of odds-aggregator zijn. Geldig zijn o.a. xG/xGA, rolling-xG, shot- en
big-chance-data, gepubliceerde modelkansen, goal averages, BTTS%/O-U-percentages,
home/away-splits, blessures/schorsingen van sleutelspelers.

Is er voor een wedstrijd géén enkele onafhankelijke input? → `data_tier = NONE` → **GEEN BET**.
Niet "LIGHT met lage confidence" — geen bet. Vermeld bij elk cijfer de bron. Niet gevonden =
schrijf "niet gevonden", nooit gokken.

**Een "gepubliceerde modelkans"-site is niet automatisch schoon.** De expliciete bookmaker/
aggregator-uitsluiting (Oddschecker, BetExplorer, The Odds API e.d.) vangt niet alles: sommige
voorspellingssites nemen odds of marktbeweging zelf al op als invoer voor hun "modelkans" — hun
getal is dan een verkapte afgeleide van de markt, ook al staat het niet op een bookmakerpagina.
Controleer de methodetekst van een nieuwe bron voordat je hem als onafhankelijk aanmerkt.
Concreet voorbeeld, ontdekt op 8 aug 2026: prognosist.com noemt zelf "team form, xG, odds and
market movement" als invoer voor zijn "Model probability" — daarom staat die bron in
`coverage.json` met `"blends_market_data": true` en telt hij niet als schone onafhankelijke input
op zichzelf. Twijfel je over een bron? Zoek de "methodology"/"how it works"-pagina op en lees hem,
net zo goed als je bij een cijfer de bron leest.

---

## 3. Pipeline — filter vóór de analyse, niet erna

### Stage -1 — Onderbreking en hervatting (Claude-limiet)

Een sessie kan halverwege stoppen doordat de gebruiker zijn Claude-gebruikslimiet raakt. Zonder
maatregel begint de volgende poging weer bij wedstrijd 1 — met `MAX_DEEP_ANALYSES = 30` is dat
zonde van precies het werk dat al gedaan was. Daarom, **vóór Stage 0**:

```python
from datetime import date
from scripts.progress import load_or_start, is_completed, is_done, mark, save, mark_completed

state = load_or_start(RUN_ID, date.today())
```

- `is_completed(state)` is waar → deze run is vandaag al helemaal afgerond (rapport geschreven,
  picks gecommit). Stop meteen, doe niets — anders analyseer je dezelfde dag twee keer.
- `state["resumed_count"] > 0` → dit is een hervatting. Meld dat bovenaan het runrapport in één
  zin ("hervat om HH:MM na onderbreking, N competities al gedaan"). Geen drama, geen aparte
  sectie — gewoon vermelden.
- Loop je vervolgens door de runlijst (Stage 4/5): sla een competitie over met `is_done(state,
  naam)` als hij al in het voortgangsbestand staat, en verwerk alleen wat nog ontbreekt.
- **Commit en push het voortgangsbestand na elke afgeronde competitie** (`mark(...)` gevolgd door
  `save(...)`), niet pas aan het eind. Dit is de kern van hervatten: zonder tussentijdse commit
  overleeft niets een afgebroken sessie, want de container wordt weggegooid zodra hij stopt.
- Aan het eind van Stage 6, ná de normale vastlegging (rapport, picks, source-health, push): roep
  `mark_completed(state)` en `save(state)` aan. Dat is het signaal voor een eventuele latere
  aanroep diezelfde dag dat er niets meer te doen is.

`data/run-state/` staat **niet** in `.gitignore` (in tegenstelling tot `data/cache/`) — dit
bestand moet juist wél overleven tussen sessies, dat is zijn hele functie.

### Stage 0 — Afwikkelen (vorige runs)
Lees `data/picks.jsonl`. Zoek de uitslagen op van picks met `result = null` en een aftrap ouder
dan `SETTLE_AFTER_HOURS`. Werk ze bij via `scripts/ledger.py settle`. Zonder deze stap is de
kwaliteit van de routine niet meetbaar.

### Stage 1 — Fixtures van vandaag
Bepaal zelf de actuele datum. Haal fixtures op; probeer meerdere bronnen (zie
`data/source-health.json` voor wat laatst werkte). Werk uitsluitend met wedstrijden van **vandaag**.

### Stage 2 — Competitiepoort
Competities uit je runlijst **zonder** wedstrijden vandaag: overslaan, één regel in de
dekkingstabel, geen verdere aandacht. Rapporteer ze niet als "gat" — buiten het seizoen is geen
storing.

### Stage 3 — Bronprobe + datadekkingspoort

Begin met de sleutelcontrole — dit is de eerste opdracht van elke run na het afwikkelen:

```bash
python3 scripts/api_check.py
```

Neem de uitvoer letterlijk over in het runrapport onder "Bronstatus deze run". Wat je eruit haalt:

- **Beide sleutels ontbreken** → er is geen API-bron. Ga verder met de scrape-bronnen uit
  `coverage.json`; verwacht dat vrijwel alles `BUITEN DATADEKKING` wordt. Meld in het rapport dat
  de sleutels ontbreken, met verwijzing naar `README.md` → "Sleutels toevoegen".
- **`API_FOOTBALL_KEY` werkt** → er is een onafhankelijke kansbron. Deze competities kunnen nu de
  datadekkingspoort passeren. Trek per competitie na of er daadwerkelijk xG in de respons zit:
  zo ja `FULL`, zo nee `LIGHT` op basis van teamstatistieken, doelgemiddelden en home/away-splits.
- **Een sleutel wordt afgewezen** → meld de exacte foutmelding in het rapport en stuur een
  notificatie (§7, "nieuwe blokkade"). Een stilzwijgend afgewezen sleutel is het soort storing dat
  maanden onopgemerkt blijft.
- **Quota bijna op** → verlaag het aantal opvragingen deze run en meld het. Bij The Odds API kost
  een verzoek `markten × regio's`; houd het op één regio en maximaal twee markten.

Werk daarna `data/source-health.json` bij met wat je gemeten hebt: de statusregels van
`api_check.py` én de scrape-bronnen die je deze run hebt geprobeerd (inclusief HTTP-status bij
falen). Zet de sleutelbronnen op `ok` of op de foutmelding, niet meer op `untested`.

Bepaal dan per resterende competitie of er een werkende, onafhankelijke kansbron is. Competities
zonder dekking gaan naar **"buiten datadekking"** en worden niet geanalyseerd.

**Niet doen:** de Cloudflare-challenge op fbref, Forebet, FootyStats of PredictZ omzeilen. Die
sites sluiten bots bewust af (zie `README.md` → "Waarom de bronnen dicht zitten"). Blijft hun
status `cloudflare_challenge`, dan is dat de uitkomst — probeer geen headless browser, geen
challenge-solver en geen proxy om er langs te komen.

Deze stap maakt de routine zelfherstellend: zodra een bron terugkomt of er een API-key
beschikbaar is, stroomt het werk automatisch weer door — zonder de prompt te wijzigen.

### Stage 4 — Rangschikken en afkappen
Rangschik de overgebleven wedstrijden op verwachte datakwaliteit (FULL boven LIGHT, meer
onafhankelijke inputs boven minder). Neem de top `MAX_DEEP_ANALYSES` mee naar de diepe analyse.
Noteer expliciet hoeveel wedstrijden hierdoor zijn afgekapt — **stille truncatie is verboden**;
een afgekapte lijst leest anders als volledige dekking.

**Gebruik `scripts/fotmob.py`, `scripts/betexplorer.py`, `scripts/oddsapi.py`, `scripts/xgscore.py`
en `scripts/model.py` voor Stage 3-5** in plaats van de ophaal- en rekenlogica opnieuw te schrijven.
Dat is precies wat de vorige aanpak duur maakte: niet het aantal wedstrijden, maar het aantal
**nieuwe, nog niet opgehaalde competities** — voor elke competitie moet één keer een team-xG-
dossier worden opgebouwd (`fotmob.fetch_league_stats`, met caching per dag), maar zodra dat er
is, kost een extra wedstrijd binnen diezelfde competitie bijna niets: alleen nog
`model.analyze_match` en `model.robustness_check` aanroepen. Reken dus niet met wedstrijden als
eenheid van "hoeveel kan ik aan vandaag", maar met **hoeveel competities voor het eerst worden
opgehaald**. Een dag met 30 wedstrijden in 3 al-bekende competities is goedkoop; een dag met
10 wedstrijden in 10 nieuwe competities is duur — ook al is het aantal wedstrijden lager. Val bij
twijfel terug op de volgorde uit deze paragraaf (FULL boven LIGHT), en meld in het runrapport
welke competities deze run voor het eerst zijn opgehaald (en dus in `data/cache/fotmob/` zijn
gecached voor de volgende run).

### Stage 5 — Analyse en output
Analyseer de geselecteerde wedstrijden volgens §4 en §5.

**Zet eerst het doelpuntenniveau goed.** Haal per competitie de teamstatistieken van zowel het
vorige als het lopende seizoen op, en corrigeer de competitiebasis voordat je één wedstrijd
doorrekent:

```python
from scripts.model import early_season_uplift, scale_level
obs = [(vorig["avg_xg_per_match"], huidig["avg_xg_per_match"], speeldagen) for elke competitie]
factor, pooled, total_md = early_season_uplift(obs)
league = scale_level(league_uit_vorig_seizoen, factor)
```

Waarom dit moet: met teamsterktes uit vorig seizoen komt het niveau óók uit vorig seizoen, en
begin seizoen wordt er meer gescoord dan over een heel jaar gemiddeld. Op 9 aug 2026 lag het
model daardoor over 17 wedstrijden gemiddeld 3.0 pp onder de markt op P(Over 2.5) — tien van de
zeventien keer dezelfde kant op — waardoor zeven Under-kandidaten dezelfde scheefstand zeven keer
telden. Na de correctie: +0.9 pp, gemiddelde absolute fout van 4.5 naar 3.9 pp. De correctie dooft
vanzelf uit naarmate het seizoen vordert.

**Regel de correctie nooit af op de markt.** Hij komt volledig uit xG-waarnemingen; zou je
`prior_matchdays` bijstellen tot de afwijking tegenover de bookmakers nul is, dan is `my_prob`
alsnog van de odds afgeleid en meet de edge niets meer (§2). Meten tegen de markt om te zien of
de correctie werkt mag wel — dat is controleren, niet fitten. Meld de gemeten afwijking vóór en
na in het runrapport, zodat een volgende run ziet of de correctie nog klopt.

### Stage 6 — Vastleggen
Volg §6. Zonder commit is de run niet gebeurd.

---

## 4. Datahiërarchie en labels

1. **Hard data** (indien beschikbaar): team xG/xGA (seizoen); rolling xG-trend (laatste 5–8);
   match-level predicted xG (home/away); shots, SOT, big chances; fitheid, blessures/schorsingen
   key-players.
2. **Bij ontbrekende xG**: gepubliceerde modelkansen (Forebet, FootyStats, xGscore, Prognosist
   e.d.); goal averages, BTTS%, over/under-lijnen; home/away-splits; recente vorm (5–6).

**Consistentie-check:** benoem waar data onzeker of conflicterend is.

| Label | Voorwaarde |
|---|---|
| `FULL` | ≥ 2 onafhankelijke inputs, waarvan ≥ 1 uit categorie 1 |
| `LIGHT` | ≥ 1 onafhankelijke input, maar niet genoeg voor FULL |
| `NONE` | geen onafhankelijke input → geen bet |

**Vroeg seizoen (speeldag 1–5):** "rolling xG laatste 5–8" bestaat dan niet. Eis het niet en
verzin het niet. Gebruik xG van vorig seizoen en markeer expliciet transfers en
selectiewisselingen als onzekerheid. Bij promovendi/nieuwkomers zonder vergelijkbare historie:
`LIGHT` of `NONE`.

---

## 5. Outputformat

### Dekkingsrapportage (bovenaan, verplicht)

Een tabel met elke competitie uit je runlijst en precies één status:

| Status | Betekenis |
|---|---|
| `GEANALYSEERD` | wedstrijden vandaag + datadekking |
| `GEEN WEDSTRIJD` | niets op de kalender vandaag |
| `BUITEN DATADEKKING` | wedstrijden vandaag, maar geen werkende onafhankelijke kansbron (noem welke bron faalde + status) |
| `AFGEKAPT` | wel dekking, maar buiten `MAX_DEEP_ANALYSES` gevallen (noem het aantal) |

Doe niet alsof de dekking volledig is als dat niet zo is.

### Per wedstrijd

Bij een **bet**:

```
[Thuis] – [Uit] · [aftrap lokale tijd NL] · [competitie]
Data: FULL | LIGHT
Bet: [markt + selectie] — Odds: best [x.xx] ([bron]) of target ≥ [x.xx]
Implied prob: xx.x%  •  My prob: xx.x%
Edge: +x.x pp  •  Confidence: High | Medium | Low
Inputs: [de sturende onafhankelijke inputs, met bron per cijfer]
Onderbouwing: [max 5 zinnen, data-gedreven]
```

Bij **geen bet**:

```
[Thuis] – [Uit] · [aftrap] · [competitie]
Data: FULL | LIGHT | NONE
GEEN BET — [reden in één regel: edge onder drempel / geen onafhankelijke input /
             odds buiten band / data conflicterend]
```

### Topselectie

Rangschik alle gepubliceerde bets op **Edge × Probability × Data-betrouwbaarheid**. Geef de top
`MAX_SHORTLIST`, met per bet: Probability • Edge • Risicoklasse (Low/Medium/High) • waarom
deze wél en de eerstvolgende net niet. Maximaal `MAX_LIGHT_IN_SHORTLIST` bets met `LIGHT`.

Zijn er minder gekwalificeerde bets dan `MAX_SHORTLIST`? Lever er minder. **Vul niet aan.**

### Aftraptijden

Rapporteer in **NL-tijd**. Let op de tijdzone van de bron: Britse sites (Sporting Life, Oddschecker,
BBC) geven doorgaans UK-tijd, wat in de zomer NL −1 uur is. Labelt een bron de tijdzone niet
expliciet, dan reken je om, **zeg je dat je hebt omgerekend**, en controleer je één aftraptijd tegen
een tweede bron als sanity-check. Een aftraptijd die er een uur naast zit maakt de hele bet
onbruikbaar.

### Odds

Noteer het tijdstip van uitlezen — odds bewegen. Geef beste prijs + bookmaker als die te bepalen
is; anders "target minimum odds ≥ …". Een geaggregeerde beste prijs zonder herleidbare
bookmaker: noteer de aggregator als bron en zeg dat de bookmaker niet herleidbaar was.

### Onderaan, letterlijk

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.

---

## 6. Vastleggen in de repo

### 6a. De branch — doe dit vóór Stage 0, niet aan het eind

**De canonieke branch is `main`.** Niet de branch die de omgeving je deze sessie heeft toegewezen,
en niet de naam die eventueel in de scheduler-prompt staat.

Claude Code op het web geeft elke sessie een eigen willekeurige branchnaam. Dat is geen instelling
die je kunt uitzetten, dus je *landt* elke run ergens anders. Zonder tegenmaatregel schrijven Run A
en Run B daardoor naar aparte branches die uit elkaar groeien — gemeten op 10 aug 2026: twee
ledgers, allebei onvolledig, en Run B rapporteerde 5 picks waar er 8 waren.

Begin daarom elke run hiermee:

```bash
git fetch origin main
git merge origin/main          # of: git checkout -B werk origin/main als je nog nergens zit
```

en eindig met:

```bash
git push origin HEAD:main
```

Twee dingen om te weten:

- **Toestemming.** Een sessie weigert standaard naar een andere branch te pushen dan de toegewezen.
  Beide scheduler-teksten geven daarom expliciet toestemming om naar `main` te pushen. Ontbreekt die
  toestemming in de prompt waarmee je draait, push dan naar je eigen branch, en **meld bovenaan het
  runrapport dat de run niet op `main` staat** — dan weet de volgende run dat hij moet samenvoegen.
- **Botsing.** Wordt de push geweigerd omdat `main` intussen is opgeschoven (de andere run was je
  voor), dan fetch je opnieuw, merge je, en push je nog een keer. Forceer nooit: aan de andere kant
  hangt een echte run met echte picks.

### 6b. Wat je vastlegt

Elke run, ook een run met nul bets:

1. **Runrapport** → `runs/YYYY-MM-DD-run-<a|b>.md` (zie `runs/TEMPLATE.md`).
2. **Picks** → append één JSON-regel per gepubliceerde bet aan `data/picks.jsonl`
   (schema: `schema/pick.schema.json`; valideer met `scripts/ledger.py validate`).
3. **Bronstatus** → werk `data/source-health.json` bij met wat je deze run gemeten hebt.
4. **Afwikkeling** → uitkomsten van Stage 0 verwerkt in `data/picks.jsonl`.
5. **Commit en push** naar `main` (zie 6a: `git push origin HEAD:main`). Zonder push is de run
   verdwenen zodra de container wordt opgeruimd.
6. **Voortgangsbestand afsluiten** — `scripts/progress.py`: `mark_completed(state)` + `save(state)`,
   en nog een keer committen/pushen (zie Stage -1). Zonder deze stap denkt een latere aanroep
   diezelfde dag dat de run nog loopt.

Draai daarna `python3 scripts/ledger.py stats` en neem hit rate, ROI en Brier score op in het
runrapport. Dit is de enige manier waarop "gaat het goed of niet" een antwoord met een getal krijgt.

### 6c. Het leesbare dagrapport — verplicht, elke run

Het markdown-runrapport hierboven is voor de repo: methode, metingen, bronstatus. De gebruiker
leest dat niet, en had daar gelijk in — het opent met bronstatus, gebruikt `edge_pp`, "de-viggen"
en Brier zonder uitleg, en de bets staan als twee regels tussen alle andere wedstrijden. Daarom
levert elke run **ook** een HTML-pagina op:

1. Schrijf `runs/YYYY-MM-DD-run-<a|b>.prose.json` — alleen de tekst die een mens moet schrijven:
   `verdict`, `bets` (per pick-id een `why` in gewone taal + een risicozin), `coverage_notes`,
   `todo`, `finding` en `settled`. Zie `runs/2026-08-09-run-a.prose.json` als voorbeeld.
2. Draai `python3 scripts/report.py --run <a|b> --date YYYY-MM-DD`. Bets, dekkingstabel en de
   stand van het logboek komen automatisch uit `picks.jsonl` en `data/run-state/` — niet
   overtypen, want dan gaan de twee rapporten uiteenlopen.
3. Publiceer het bestand als Artifact en **zet die link in de notificatie** (§7).

Schrijf de prose voor iemand die de repo niet kent en het jargon niet spreekt. Geen `edge_pp`,
geen "de-viggen", geen ρ of shrink: die staan in de woordenlijst onderaan de pagina en horen niet
in de lopende tekst. Noem bedragen, tijden en bookmakers concreet.

Ook bij **nul bets** draait dit. De pagina zegt dan met zoveel woorden dat er niets gekwalificeerd
heeft, en de dekkingstabel laat zien dat er wél gekeken is. Dat is precies het geval waarin een
lege notificatie de gebruiker in het ongewisse laat.

---

## 7. Wanneer een notificatie sturen

De run draait terwijl niemand meekijkt; wat alleen in het transcript staat, bereikt niemand.

**Stuur een notificatie bij:**
- een niet-lege topselectie (leid met de beste bet en de aftraptijd);
- een run die niet kon draaien, of nul bets door een **nieuwe** oorzaak (bron omgevallen,
  fixtures onvindbaar, push geweigerd);
- een afwikkelingsresultaat dat opvalt (bijv. een reeks van 5+ verliezende picks).

**Stuur geen notificatie bij:**
- nul bets om dezelfde reden als de vorige run (bijv. "nog steeds geen dekking voor deze comps");
- een routinematige, gezonde run zonder gekwalificeerde bets.

**Stuur je er wel een, zet dan de link naar de HTML-pagina uit §6b erin** — dat is de plek waar
de gebruiker het hele verhaal kan lezen. Houd de notificatie zelf kort: de beste bet, de koers,
de bookmaker en de aftraptijd, dan de link. Geen methodediscussie in de notificatie; die staat
op de pagina en in het markdown-rapport.

---

## 8. Wat deze regels expliciet níet oplossen

De bronnen zijn nog steeds grotendeels dichtgezet (zie `data/source-health.json`). Zolang er geen
API-key beschikbaar is, zullen veel competities in `BUITEN DATADEKKING` blijven vallen en zullen
runs vaak nul bets opleveren. Dat is de eerlijke uitkomst van de huidige input, niet een defect
in deze regels. De structurele fix staat in `README.md` onder "Nog te doen".
