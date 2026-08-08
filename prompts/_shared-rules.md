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
4. `data_tier ≠ NONE`.

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

**Gebruik `scripts/fotmob.py`, `scripts/betexplorer.py`, `scripts/oddsapi.py` en
`scripts/model.py` voor Stage 3-5** in plaats van de ophaal- en rekenlogica opnieuw te schrijven.
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

### Stage 6 — Vastleggen
Volg §6. Zonder commit is de run niet gebeurd.

---

## 4. Datahiërarchie en labels

1. **Hard data**: team xG/xGA (seizoen); rolling xG (laatste 5–8); match-level predicted xG;
   shots, SOT, big chances; fitheid, blessures/schorsingen key-players.
2. **Bij ontbrekende xG**: gepubliceerde modelkansen; goal averages, BTTS%, over/under-lijnen;
   home/away-splits; recente vorm (5–6).

Benoem waar data onzeker of conflicterend is.

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

Elke run, ook een run met nul bets:

1. **Runrapport** → `runs/YYYY-MM-DD-run-<a|b>.md` (zie `runs/TEMPLATE.md`).
2. **Picks** → append één JSON-regel per gepubliceerde bet aan `data/picks.jsonl`
   (schema: `schema/pick.schema.json`; valideer met `scripts/ledger.py validate`).
3. **Bronstatus** → werk `data/source-health.json` bij met wat je deze run gemeten hebt.
4. **Afwikkeling** → uitkomsten van Stage 0 verwerkt in `data/picks.jsonl`.
5. **Commit en push** naar de werkbranch. Zonder push is de run verdwenen zodra de container
   wordt opgeruimd.
6. **Voortgangsbestand afsluiten** — `scripts/progress.py`: `mark_completed(state)` + `save(state)`,
   en nog een keer committen/pushen (zie Stage -1). Zonder deze stap denkt een latere aanroep
   diezelfde dag dat de run nog loopt.

Draai daarna `python3 scripts/ledger.py stats` en neem hit rate, ROI en Brier score op in het
runrapport. Dit is de enige manier waarop "gaat het goed of niet" een antwoord met een getal krijgt.

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

---

## 8. Wat deze regels expliciet níet oplossen

De bronnen zijn nog steeds grotendeels dichtgezet (zie `data/source-health.json`). Zolang er geen
API-key beschikbaar is, zullen veel competities in `BUITEN DATADEKKING` blijven vallen en zullen
runs vaak nul bets opleveren. Dat is de eerlijke uitkomst van de huidige input, niet een defect
in deze regels. De structurele fix staat in `README.md` onder "Nog te doen".
