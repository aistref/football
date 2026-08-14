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

**Draai altijd beide methodes** en middel ze tot één schatting:

```python
p_xg    = analyze_match(...)              # op xG, genormaliseerd op de competitie
p_split = analyze_match_from_splits(...)  # op wat de ploegen thuis en uit werkelijk scoorden
my_prob = (p_xg + p_split) / 2            # dit is de kans die in de pick komt
edge_pp = (my_prob - 1 / odds) * 100
```

Een bet mag alleen gepubliceerd worden als **alle** voorwaarden gelden:

1. `edge_pp ≥ EDGE_THRESHOLD_FULL` bij `data_tier = FULL`, of `≥ EDGE_THRESHOLD_LIGHT` bij `LIGHT`
   — gemeten op de **gemiddelde** `my_prob` hierboven, niet op één van de twee afzonderlijk;
2. `MIN_ODDS ≤ odds ≤ MAX_ODDS`;
3. de anti-circulariteitsregel (§2) is voldaan;
4. `data_tier ≠ NONE`;
5. **de twee methodes spreken elkaar niet tegen.** Beide moeten de markt dezelfde kant op
   verslaan: `p_xg > 1/odds` **én** `p_split > 1/odds`. Zakt één van de twee onder de
   marktkans, dan wijzen ze tegengesteld en gaat de bet eruit met reden "data conflicterend";
6. **de edge draait niet om bij een andere parameterkeuze:**
   `robustness_check(...).min_edge > 0` over het hele (shrink, rho)-grid.

### Waarom poort 5 en 6 zo staan (herzien 11 aug 2026)

Van 9 t/m 11 aug luidde poort 5 "**beide** methodes moeten boven de drempel uitkomen" en poort 6
"`min_edge ≥ drempel`". Dat is drie keer dezelfde volle drempel op drie ruizige statistieken, en
dat bleek in de praktijk een filter dat vrijwel alles wegvangt: **acht kandidaten met een echte
edge, nul bets** over vier runs (10–11 aug, beide runs).

De constructie was ook statistisch te streng. `min(A, B) ≥ drempel` eisen van twee schatters van
dezelfde grootheid ligt veel hoger dan `gemiddelde(A, B) ≥ drempel`: het middelen van twee
schattingen verkleint juist de ruis, terwijl de min-regel de ruis maximaal laat meetellen. Wat je
wilt uitsluiten is niet "de tweede methode is wat lager", maar "de twee methodes wijzen
tegengesteld" — en dát is precies wat poort 5 nu toetst.

Op de acht kandidaten tot nu toe geeft de herziene regel 5 bets in plaats van 0, en houdt hij de
twee gevallen tegen waar de methodes werkelijk tegenover elkaar stonden (Sirius – Brommapojkarna
+3.4 / **−8.4** en Västerås – Djurgården +4.6 / **−4.3**). De aanleiding voor de oude poort,
Gil Vicente – Rio Ave op 9 aug (+10.3 / +2.7), zou onder de nieuwe regel wél doorgaan — met
`my_prob` op het gemiddelde, dus met een navenant lagere geclaimde edge.

**Dit is een verruiming zonder bewijs, en daarom loopt er vanaf nu een schaduwlogboek mee.** Er is
namelijk nooit gemeten of de oude poort iets opleverde: alle acht picks in `picks.jsonl` dateren
van vóór 9 aug, dus er is geen enkele afgerekende bet onder het oude regime. Zolang dat zo blijft
is "strenger is beter" een aanname, geen bevinding. §6d legt vast hoe elke afgewezen kandidaat
alsnog wordt afgerekend, zodat over enkele weken met cijfers te zeggen is of deze poorten geld
besparen of alleen bets.

**Een run met nul bets is geen mislukte run.** Nul bets rapporteren met een heldere reden is
correct gedrag; bets forceren om het format te vullen is dat niet.

Ga alle markten langs — 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS —
en publiceer alleen de sterkste. Geen "gevoel", geen reputatie-argumenten.

**Dit is tot 14 aug 2026 niet gebeurd, en het lag aan de code.** `MatchProbabilities` had velden
voor 1X2, Over/Under **2.5** en BTTS en verder niets; Asian Handicap en Draw No Bet waren niet uit
te rekenen, andere O/U-lijnen evenmin. Aan de oddskant was er wél een `fetch_totals` maar geen
`fetch_spreads`, en `fetch_event_markets` (voor BTTS en Double Chance) is nooit aangeroepen. Het
resultaat is te tellen in `data/picks.jsonl`: van de eerste 15 picks waren er **11 een 1X2, 3 een
Over/Under 2.5 en 1 een Double Chance** — nul Asian Handicap, nul BTTS, nul Draw No Bet. In
`data/shadow.jsonl` was 19 van de 20 een 1X2. De routine koos dus niet de sterkste markt maar de
sterkste van de twee die toevallig geïmplementeerd waren.

Sinds 14 aug 2026 kan het wel, en het kost niets extra aan modelwerk — alle markten komen uit
hetzelfde scoregrid dat `analyze_match` toch al berekent:

```python
p = analyze_match(...)                              # p.grid is nu beschikbaar
asian_prob(p.grid, -0.75, "home", odds)             # Asian Handicap, incl. kwart- en hele lijnen
dnb_prob(p.grid, "away", odds)                      # Draw No Bet (= de handicap op 0.0)
totals_prob(p.grid, 3.0, "over", odds)              # elke O/U-lijn, niet alleen 2.5
p.dc_1x, p.dc_x2, p.dc_12                           # Double Chance
p.btts                                              # BTTS
```

Aan de oddskant: `fetch_spreads(sport_key)` kost **1 credit**, precies zoveel als `fetch_totals`, en
levert de handicaplijnen van alle wedstrijden in een competitie. BTTS en Double Chance gaan via
`fetch_event_markets(sport_key, event_id, ["btts", "double_chance"])` en kosten 2 credits **per
wedstrijd** — vraag die dus pas op voor wedstrijden die al een kandidaat-edge tonen, niet voor de
hele kalender. `best_by_line(event, markt)` geeft de beste prijs per (uitkomst, lijn); vergelijk
nooit prijzen over verschillende lijnen heen, want een andere lijn is een andere bet.

Twee dingen om bij het rangschikken in de gaten te houden. Een handicap of totaal met push is geen
gewone kans — bij een push komt de inzet terug — dus `asian_prob` geeft de kans terug die bij díe
koers dezelfde verwachtingswaarde oplevert, zodat `edge_pp` en alle zes poorten er ongewijzigd op
werken. En dezelfde onderliggende inschatting levert vaak op vier of vijf markten tegelijk een
edge op (gemeten op Viborg – AGF, 14 aug: 1X2 +17.6, AH +0.5 +15.5, DNB +15.2, Double Chance +12.2,
Over 2.5 +5.1, BTTS ja +3.0). Dat zijn geen vijf bevindingen maar één, vijf keer uitgedrukt — de
0-of-1-bet-regel hierboven blijft dus onverkort gelden, en "de sterkste" betekent één selectie per
wedstrijd, niet één per markt.

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

### Stage -2 — Eén werkbranch (vóór alles, ook vóór het lezen van deze regels)

Elke sessie krijgt een eigen branchnaam, en de twee geplande taken lopen los van elkaar. Zonder
maatregel schrijven Run A en Run B naar twee takken die elkaars werk niet zien. Dat is geen
theoretisch risico:

- **9 aug 2026** — de scheduler wees naar een branch die zeven commits achterliep.
- **10 aug 2026** — Run A en Run B schreven allebei naar een eigen tak, allebei met echt werk erop.
  Run A startte op de tak van Run B en miste daardoor poort 5 (§1.5) en de vroeg-seizoenscorrectie
  (Stage 5), regels die Run A zelf de dag ervoor had toegevoegd. Er is een bet gepubliceerd en
  verstuurd die onder de volledige regelset niet had gemogen, en twee picks van de dag ervoor bleven
  onafgewikkeld omdat hun tak nooit is aangeraakt.

Daarom, als allereerste handeling van elke run:

```bash
git fetch origin
git branch -r
for b in $(git branch -r | grep -v HEAD); do
  echo "$b: $(git rev-list --count HEAD..$b) commits die hier nog niet zijn"
done
```

Elke branch met méér dan 0 eigen commits wordt **gemerged**, niet weggegooid en niet vervangen.
"Pak gewoon de nieuwste" is expliciet fout: op 10 aug bevatten beide takken werk dat de ander niet
had, dus kiezen betekende hoe dan ook iets verliezen.

Bij conflicten:

| Bestand | Regel |
|---|---|
| `data/picks.jsonl` | **Vereniging.** Een pick die op één tak staat is een echte, gepubliceerde pick. Staat dezelfde id op beide takken, neem dan de versie die het meest weet — een afgewikkelde regel wint van `pending`. |
| `data/source-health.json`, `data/coverage.json` | **Vereniging.** Beide runs hebben echt gemeten; bewaar beide waarnemingen naast elkaar in `detail` in plaats van er een te laten winnen. |
| `prompts/_shared-rules.md`, `scripts/*` | De **nieuwste** versie wint. Regels en rekencode zijn geen metingen. |

Lees deze regels pas ná de merge opnieuw: vóór de merge kun je een oudere versie van dit bestand in
handen hebben dan er in de repo bestaat. Kom je uit op een andere branch dan de scheduler noemt, meld
dat dan bovenaan het runrapport én in de notificatie — anders blijft het elke run handwerk.

Controleer na de merge of `picks.jsonl` openstaande picks bevat van een run die op de andere tak
nooit is afgewikkeld. Die horen bij Stage 0.

Deze stap ruimt op wat al uiteen is gelopen. Dat er niets nieuws bij komt, regelt §6a: je pusht
aan het eind naar `main`, niet naar de tak die deze sessie toevallig kreeg toegewezen. De twee
horen bij elkaar — Stage -2 alleen betekent dat je elke run opnieuw hetzelfde opruimwerk doet.

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

### "Net niet" — verplicht, ook (juist) bij nul bets

Elke afgewezen kandidaat die een echte edge liet zien, krijgt een regel met **het cijfer per poort**.
Niet alleen de poort die hem afwees: alle drie de getallen, zodat zichtbaar is of het één poort was
of een breed tekort.

| Kolom | Wat erin staat |
|---|---|
| xG-model | `edge_pp` uit `analyze_match`, mét de vroeg-seizoenscorrectie |
| 2e methode | `edge_pp` uit `analyze_match_from_splits` |
| zwakste stand | `min_edge` uit `robustness_check` — het laagste punt van het (shrink, rho)-grid |
| valt af op | `edge` / `robuustheid` / `tweede_methode` / `odds` / `data` |

Leg die cijfers vast in `data/run-state/` onder de wedstrijd, als `near_miss`:

```json
{"match": "Silkeborg – OB Odense", "tier": "FULL", "bet": false,
 "near_miss": {"market": "1X2 — OB Odense wint", "odds": 2.58,
               "edge_xg": 7.29, "edge_split": 0.54, "edge_robust_min": 5.65,
               "failed_gate": "tweede_methode"}}
```

`scripts/report.py` rendert daar de sectie "Net niet" van het dagrapport uit. **Typ die tabel niet
over in het prosebestand** — dan lopen de twee rapporten van dezelfde run uiteen, en dat is precies
de fout die `report.py` moest wegnemen.

Waarom dit moet (verzoek van de gebruiker, 10 aug 2026): een run met nul bets leest anders als "er
was niets", terwijl het verschil tussen *geen enkele kandidaat* en *drie kandidaten die op een haar
afvielen* precies is wat je over meerdere dagen wilt kunnen zien. Het is ook de enige manier om te
merken dat één poort structureel alles wegvangt: valt er een week lang alles af op `tweede_methode`,
dan is de vraag of de twee methodes systematisch uiteenlopen — en dat is een bevinding, geen ruis.
Neem dezelfde tabel op in het markdown-runrapport onder de topselectie.

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

### 6a. Waar je naartoe pusht: `main`

Stage -2 ruimt aan het begin van de run op wat al uiteen is gelopen. Deze paragraaf zorgt dat er
niets nieuws bij komt: **je pusht naar `main`.** Niet naar de branch die de omgeving je deze sessie
heeft toegewezen — die naam is elke run anders, en dat is precies hoe de waaier aan takken ontstaat
die Stage -2 moet opruimen.

```bash
git push origin HEAD:main
```

Drie dingen om te weten:

- **Toestemming.** Een sessie weigert standaard naar een andere branch te pushen dan de toegewezen.
  Beide scheduler-teksten geven daarom expliciet toestemming om naar `main` te pushen. Ontbreekt die
  toestemming in de prompt waarmee je draait, push dan naar je eigen branch, **meld bovenaan het
  runrapport en in de notificatie dat de run niet op `main` staat**, en vraag om de scheduler-tekst
  bij te werken. Dan weet de volgende run dat er iets te mergen valt.
- **Botsing.** Wordt de push geweigerd omdat `main` intussen is opgeschoven (de andere run was je
  voor), fetch dan opnieuw, merge volgens de conflictregels van Stage -2, en push nog een keer.
  Forceer nooit: aan de andere kant hangt een echte run met echte picks. Dit is geen randgeval — het
  gebeurde op 10 aug 2026 al bij de eerste poging, omdat de twee runs elkaar overlapten.
- **Tussentijds.** Het voortgangsbestand na elke afgeronde competitie (Stage -1) push je ook naar
  `main`. Wacht daar niet mee tot het eind: de container wordt weggegooid zodra de sessie stopt.

### 6b. Wat je vastlegt

Elke run, ook een run met nul bets:

1. **Runrapport** → `runs/YYYY-MM-DD-run-<a|b>.md` (zie `runs/TEMPLATE.md`).
2. **Picks** → append één JSON-regel per gepubliceerde bet aan `data/picks.jsonl`
   (schema: `schema/pick.schema.json`; valideer met `scripts/ledger.py validate`).
3. **Bronstatus** → werk `data/source-health.json` bij met wat je deze run gemeten hebt.
4. **Afwikkeling** → uitkomsten van Stage 0 verwerkt in `data/picks.jsonl`.
5. **Schaduwlogboek** → `python3 scripts/shadow.py collect --date <datum> --run <a|b>`, en de
   schaduwpicks van vorige runs afwikkelen (zie 6d).
5b. **Marktdekking aantonen** → noteer bij elke geanalyseerde wedstrijd in `data/run-state/` een
   `markets_checked` met de markten die je werkelijk hebt doorgerekend, en draai daarna:

   ```bash
   python3 scripts/progress.py verify --run <a|b> --date YYYY-MM-DD
   ```

   Dit moet groen zijn vóór de commit. Namen: `1X2`, `DC`, `DNB`, `AH`, `OU`, `BTTS`. Een markt
   waarvoor geen odds te vinden waren telt óók als bekeken — noteer hem dan met de reden erbij
   (`"AH": "geen spreads bij The Odds API voor deze competitie"`), niet als gat. Wedstrijden met
   `tier = NONE` worden overgeslagen; daar valt geen markt door te rekenen.

   Waarom dit een aparte stap is: §1 schreef "ga alle markten langs" al vanaf het begin voor, en
   een week lang gebeurde het niet — 11 van de eerste 15 picks waren een 1X2, nul een handicap.
   Dat bleef onopgemerkt omdat er nergens werd vastgelegd wát er per wedstrijd was bekeken, alleen
   wát eruit kwam. Een regel die niemand kan nalopen is een voornemen, geen regel. Dit is met opzet
   een controle op de administratie en niet op de uitkomst: nul bets is een geldige uitkomst, een
   wedstrijd waarbij vier markten niet eens zijn opgezocht niet.
6. **Commit en push** naar `main` (zie 6a: `git push origin HEAD:main`). Zonder push is de run
   verdwenen zodra de container wordt opgeruimd.
7. **Voortgangsbestand afsluiten** — `scripts/progress.py`: `mark_completed(state)` + `save(state)`,
   en nog een keer committen/pushen (zie Stage -1). Zonder deze stap denkt een latere aanroep
   diezelfde dag dat de run nog loopt.

### 6d. Het schaduwlogboek — wat de poorten hebben tegengehouden

`picks.jsonl` bevat alleen wat er wél doorheen kwam. Daaruit is per definitie niet af te lezen of
een poort je geld bespaart of alleen bets: de afgewezen kandidaten verdwenen tot 11 aug 2026
spoorloos. `data/shadow.jsonl` sluit dat gat — elke `near_miss` uit `data/run-state/` wordt daar
een schaduwpick en wordt daarna net zo afgerekend als een echte.

Twee handelingen per run, allebei verplicht:

```bash
# 1. de kandidaten van vandaag erin (leest data/run-state/, doet niets bij nul kandidaten)
python3 scripts/shadow.py collect --date YYYY-MM-DD --run <a|b>

# 2. de schaduwpicks van eerdere runs afwikkelen, net als Stage 0 voor echte picks
python3 scripts/shadow.py open
python3 scripts/shadow.py settle <id> won|lost|void --score 2-1
```

**Reken 1X2, Double Chance, Draw No Bet, O/U en BTTS af op de stand na 90 minuten** (reguliere tijd
plus blessuretijd), nooit op de eindstand na verlenging of strafschoppen. Bij bekerduels en
Europese voorrondes zijn dat verschillende getallen, en `status.scoreStr` van Fotmob geeft de
**eind**stand — dus inclusief verlenging. Zoek bij een knock-outduel de doelpuntminuten op en tel
zelf tot 90'. Dit is geen theoretisch punt: op 12 aug 2026 wikkelde Run B Bodø/Glimt – Union
St.Gilloise af op 3–2 en zette de gelijkspelpick op `lost`, terwijl het na 90 minuten 2–2 stond en
die pick dus **gewonnen** was. Die ene regel verschoof de ROI van poort `tweede_methode` met 81
procentpunt (−33.8% → +47.0% over zes gevallen) en keerde de conclusie eronder om. Bij de kleine
aantallen waar 6d over gaat, weegt één verkeerd afgerekende regel zwaarder dan alles wat de poort
werkelijk doet.

Neem `python3 scripts/shadow.py stats` op in het runrapport, náást `ledger.py stats`. De
uitsplitsing per `failed_gate` is het punt: staat één poort structureel op een positieve ROI, dan
houdt die poort winnende bets tegen en hoort hij ruimer; is de ROI structureel negatief, dan doet
hij zijn werk en blijft hij zoals hij is.

**Lees dit niet te vroeg.** Bij minder dan ~30 afgewikkelde schaduwpicks per poort is elk verschil
ruis — de eerste meting op 11 aug 2026 stond op 5 afgewikkelde kandidaten en zei dus niets. Kijk
naar de richting over weken, niet naar het getal van vandaag, en pas geen enkele drempel aan op
basis van één dag. Dat laatste zou dezelfde fout zijn als waarmee de oude poort 5 werd ingevoerd:
één anekdote tot regel verheffen.

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

**Stuur je er wel een, zet dan de link naar de HTML-pagina uit §6c erin** — dat is de plek waar
de gebruiker het hele verhaal kan lezen. Houd de notificatie zelf kort: de beste bet, de koers,
de bookmaker en de aftraptijd, dan de link. Geen methodediscussie in de notificatie; die staat
op de pagina en in het markdown-rapport.

---

## 8. Wat deze regels expliciet níet oplossen

De bronnen zijn nog steeds grotendeels dichtgezet (zie `data/source-health.json`). Zolang er geen
API-key beschikbaar is, zullen veel competities in `BUITEN DATADEKKING` blijven vallen en zullen
runs vaak nul bets opleveren. Dat is de eerlijke uitkomst van de huidige input, niet een defect
in deze regels. De structurele fix staat in `README.md` onder "Nog te doen".
