# Betting-analyse routine

Repo achter twee terugkerende geplande taken (Run A en Run B) die dagelijks voetbalwedstrijden
analyseren op valuebets. Deze repo bevat de opdracht, de brondekking en het logboek — zodat elke
run voortbouwt op de vorige in plaats van bij nul te beginnen.

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.

## Waarom deze structuur bestaat

De oorspronkelijke opdracht stond volledig in de scheduler-prompt en liep structureel vast. De
diagnose van 8 aug 2026 staat in `runs/2026-08-08-run-a.md`; de drie doorgevoerde fixes:

| # | Probleem | Fix |
|---|---|---|
| 2 | "Exact één valuebet per wedstrijd" dwong bets af, ook zonder value → overwegend ruis | **0 of 1 bet per wedstrijd**, met een edge-drempel en een harde anti-circulariteitsregel. Nul bets is een geldige uitkomst. |
| 3 | 46 wedstrijden × volledige analyse zonder plafond → elke run liep zijn tijdslimiet in en leverde een halve lijst | **Filteren vóór de analyse** op datadekking, plus een cap van 12 diepe analyses. Afkapping wordt altijd gemeld. |
| 5 | Niets werd bewaard: dezelfde dode bronnen werden elke run opnieuw ontdekt, en "gaat het goed?" was niet te beantwoorden | **Logboek in de repo**: runrapporten, een picks-ledger met uitkomsten, en een bronstatusbestand. |

## Indeling

```
prompts/
  SCHEDULER-RUN-A.txt   korte prompt om in de geplande taak te plakken
  run-a.md              Run A: competitielijst + run-specifieke instellingen
  run-b.md              Run B: idem, overige competities
  SCHEDULER-RUN-B.txt   idem, voor Run B
  _shared-rules.md      de eigenlijke opdracht — parameters, regels, pipeline, format
data/
  coverage.json         welke bron welke competitie kan bedienen, en in welke rol
  source-health.json    wat elke bron laatst deed toen we hem probeerden
  picks.jsonl           het logboek: één gepubliceerde bet per regel
  cache/fotmob/         team-xG per competitie, per dag ververst (.gitignore, geen bron van waarheid)
  run-state/            voortgang per lopende run — NIET .gitignore, moet een onderbreking overleven
schema/
  pick.schema.json      velddefinitie van een pick
scripts/
  ledger.py             valideren, afwikkelen en meten (alleen stdlib)
  fotmob.py             fixtures + team-xG ophalen, met caching per dag
  betexplorer.py        gratis 1X2-odds ophalen
  oddsapi.py            Over/Under en overige markten ophalen, credit-bewust
  xgscore.py            gepubliceerde 1X2-modelkansen van xgscore.io ophalen
  model.py              Poisson met Dixon-Coles-correctie + de robuustheidstest
  progress.py           voortgangsbestand: hervat een run na een Claude-limiet i.p.v. opnieuw te beginnen
  report.py             het leesbare dagrapport als HTML-pagina, voor wie de repo niet kent
runs/
  TEMPLATE.md           vorm van een runrapport
  YYYY-MM-DD-run-a.md   het technische rapport van elke run
  YYYY-MM-DD-run-a.prose.json   de leesbare tekst bij dat rapport (invoer voor report.py)
  YYYY-MM-DD-run-a.html         de pagina die de gebruiker krijgt, als Artifact gepubliceerd
```

De scheduler-prompt is met opzet kort en verwijst naar `prompts/`. **Regels aanpassen doe je in de
repo, niet in de scheduler.**

## Installeren in de scheduler

Vervang de lange prompt van je Run A-taak door de tekst onder de streep in
`prompts/SCHEDULER-RUN-A.txt`. Doe hetzelfde voor Run B met `prompts/SCHEDULER-RUN-B.txt`.

Beide wijzen naar dezelfde branch (**`main`**) en dezelfde `picks.jsonl` — dat is bewust, `run:
"A"`/`"B"` in het schema houdt ze uit elkaar. Plan de twee taken niet op hetzelfde tijdstip:
gelijktijdige commits + push vanaf twee sessies kunnen tegen elkaar in botsen.

### De branchval, en de twee dingen die hem dichtzetten

Claude Code op het web geeft **elke sessie een eigen, willekeurige branchnaam** (`claude/<twee
woorden>-<code>`). Die naam wordt door de omgeving opgelegd; een naam in de scheduler-prompt kan dat
niet overrulen. Loopt het uiteen, dan merk je dat niet vanzelf: de run *slaagt* gewoon, alleen met
oude regels, oude scripts en een halve ledger. Drie keer misgegaan in drie dagen:

| Datum | Wat er gebeurde |
|---|---|
| 9 aug 2026 | De scheduler wees naar `claude/zealous-keller-ja4wwn` terwijl `scripts/model.py`, `scripts/xgscore.py`, `scripts/progress.py` en `MAX_DEEP_ANALYSES = 30` zeven commits verder stonden op een andere tak. |
| 10 aug 2026 | Run A startte op de tak van Run B en miste poort 5 (§1.5) en de vroeg-seizoenscorrectie — regels die Run A zelf de dag ervoor had toegevoegd. Er is een bet gepubliceerd én per notificatie verstuurd die onder de volledige regelset niet had gemogen, en twee picks van 9 aug bleven onafgewikkeld omdat hun tak nooit is aangeraakt. Zie `runs/2026-08-10-run-a.md`. |
| 10 aug 2026 | Run A en Run B legden allebei hun run vast op een eigen tak. Beide ledgers waren daardoor onvolledig: Run B rapporteerde 5 picks waar er 8 waren, en concludeerde op die halve set dat het eigen model slechter was dan de markt terwijl het op de volledige set net beter is. |

Er zijn **twee** maatregelen, en ze hebben elkaar nodig:

1. **Stage -2 in `prompts/_shared-rules.md`** — de allereerste handeling van elke run: alle remote
   branches nalopen en elke tak met eigen commits **mergen**. Let op het verschil met de oude
   formulering "neem bij twijfel de nieuwste branch": die was fout. Op 10 aug bevatten beide takken
   werk dat de ander niet had, dus kiezen betekende hoe dan ook iets weggooien. Bij conflicten
   worden `picks.jsonl`, `source-health.json` en `coverage.json` **verenigd** (het zijn metingen);
   bij de regels en de scripts wint de nieuwste versie.
2. **`main` als vast eindpunt** (§6a) — Stage -2 ruimt op wat al uiteen is gelopen, maar zonder een
   vaste plek om naartoe te pushen blijft het aantal takken groeien en doet elke run dat opruimwerk
   opnieuw. Daarom pusht elke run naar `main`, een naam die nooit verandert. Beide
   `SCHEDULER-RUN-*.txt` geven daar expliciet toestemming voor; zonder die toestemming weigert een
   sessie naar een andere branch te pushen dan de toegewezen.

Sinds 10 aug 2026 is `main` ook de **default branch** op GitHub, hernoemd vanaf
`claude/zealous-keller-ja4wwn`, zodat een nieuwe container hem binnenhaalt. De oude
`claude/*`-branches zijn alleen nog historie. Hiermee hoeft de branchnaam nergens meer bijgewerkt
te worden — dat was precies de stap die drie keer is vergeten.

## Het logboek gebruiken

```bash
python3 scripts/ledger.py validate                  # controleer picks.jsonl tegen schema + regels
python3 scripts/ledger.py add < pick.json           # voeg pick(s) toe (object of lijst)
python3 scripts/ledger.py open --hours 12           # wat moet afgewikkeld worden
python3 scripts/ledger.py settle <id> won --score 2-1
python3 scripts/ledger.py stats                     # hit rate, ROI, Brier, kalibratie
```

`validate` en `add` weigeren een pick die de regels overtreedt: een `implied_prob` die niet gelijk is
aan `1/odds`, een `edge_pp` die niet volgt uit de kansen, een edge onder de drempel voor zijn
datatier, odds buiten de band 1.30–6.00, of een odds-bron als onderbouwing van `my_prob`. Die laatste
is de belangrijkste: hij maakt het onmogelijk om een "edge" te loggen die stilletjes uit de
bookmakerprijs is afgeleid.

### De regel die er echt om gaat

`stats` zet **Brier eigen** naast **Brier markt**: de kwadratische fout van jouw `my_prob` tegenover
die van de marktkans, over dezelfde bets. Is Brier eigen niet lager, dan voegt de analyse geen
kansinformatie toe boven de prijs — hoe goed de hit rate er op korte termijn ook uitziet. Hit rate en
ROI zijn bij tientallen bets vooral ruis; deze vergelijking is het eerste signaal dat richting geeft.

## Twee rapporten per run, met opzet

`runs/YYYY-MM-DD-run-<a|b>.md` is de vindplaats voor de **methode**: welke bronnen deden wat, hoe
de kansen tot stand kwamen, welke metingen zijn gedaan. Geschreven voor wie de repo kent.

`runs/YYYY-MM-DD-run-<a|b>.html` is de vindplaats voor de **beslissing**: de bets met koers,
bookmaker en aftraptijd, wat de gebruiker zelf moet uitzoeken, de dekkingstabel en een
woordenlijst die het jargon uit het eerste rapport vertaalt. Gegenereerd door `scripts/report.py`
uit `picks.jsonl`, `data/run-state/` en een prosebestand — dus de cijfers kunnen niet uiteenlopen
met het technische rapport.

```bash
python3 scripts/report.py --run a --date 2026-08-09
```

De aanleiding staat in `runs/2026-08-09-run-a.md`: het markdown-rapport opent met bronstatus,
gebruikt `edge_pp`, "de-viggen" en Brier zonder uitleg, en de bets staan als twee regels tussen
27 andere wedstrijden. Voor de gebruiker die de routine alleen leest is dat onbruikbaar.

## Waarom de bronnen dicht zitten

Gemeten op 8 aug 2026, met bewijs in plaats van vermoedens:

- **Het is niet de netwerkpolicy van de omgeving.** De proxy maakt de verbinding (`200 Connection
  Established`) en er komt geen `x-deny-reason: host_not_allowed` terug. `api.the-odds-api.com`
  antwoordt zelfs gewoon met 200. Er hoeft dus **niets** aan **Allowed domains** te veranderen.
- **Het is geen user-agent-probleem.** Met een gewone Chrome-user-agent geven fbref, Forebet,
  FootyStats en PredictZ alle vier nog steeds 403, met bodies van vrijwel identieke grootte.
- **Het is Cloudflare-botbescherming.** De 403-pagina is Cloudflares `Just a moment...`-challenge.
  Die vier sites sluiten geautomatiseerde toegang bewust af.

Dat laatste is geen storing die overgaat en geen bug om omheen te werken: het is een dichte deur met
een bordje erop. Het antwoord is een dienst die datatoegang aanbiedt, niet een challenge omzeilen.

## Sleutels toevoegen

Twee diensten, met verschillende rollen. **De statistieken-sleutel is de belangrijke.**

| Variabele | Dienst | Levert | Nodig? |
|---|---|---|---|
| `API_FOOTBALL_KEY` | api-football.com (gratis: 100 verzoeken/dag) | statistieken, opstellingen, blessures | **Nee — op het gratis plan waardeloos, zie de waarschuwing hieronder** |
| `ODDS_API_KEY` | the-odds-api.com (gratis: 500 credits/maand) | odds per bookmaker als JSON | Ja, dit is de enige bron met een herleidbare bookmaker |

> **Het gratis plan van api-football.com is niet bruikbaar voor deze routine.** Gemeten op 10 aug
> 2026: de sleutel is geldig en `api_check.py` meldt "OK", maar elk verzoek om een seizoen ná 2024
> antwoordt met `results = 0` en `errors: {"plan": "Free plans do not have access to this season,
> try from 2022 to 2024."}`. Nagetrokken op Liga I (283/2026), Eerste Divisie (89/2025) en
> Allsvenskan (113/2026) — alle drie leeg. Een routine die de wedstrijden van *vandaag* analyseert
> heeft daar niets aan, ook niet als tier-2-bron. Zie `runs/2026-08-10-run-b.md`.
>
> De onafhankelijke kansinput komt daarom van **Fotmob** (team-xG, geen sleutel nodig) en
> **xGscore** (gepubliceerde modelkansen, geen sleutel nodig). Wie deze bron wél wil, heeft een
> betaald plan nodig; laat het gratis plan anders gewoon staan, `source-health.json` markeert hem
> als `plan_limited` en de datadekkingspoort slaat hem dan over.

### Stappen

1. Maak een gratis account op api-football.com en kopieer de sleutel uit je dashboard.
2. Ga naar [claude.ai/code/routines](https://claude.ai/code/routines) en klik op de routine.
3. Klik het pennetje (**Edit routine**).
4. Onder het **Instructions**-vak: klik het wolkje met de naam van je omgeving (bv. **Default**).
5. Ga met de muis over de omgeving in de lijst en klik het instellingen-icoontje rechts.
6. In **Update cloud environment**, in het veld voor omgevingsvariabelen, één regel per sleutel in
   `.env`-vorm:
   ```
   API_FOOTBALL_KEY=jouwsleutelhier
   ```
7. **Save changes.** Dit geldt vanaf de volgende run; een lopende sessie leest het niet opnieuw.
8. Klik **Run now** op de routine, of wacht op de volgende run. Controleer met:
   ```bash
   python3 scripts/api_check.py
   ```

**Netwerkinstellingen niet aanpassen** — beide API's zijn al bereikbaar op **Trusted**.

### Twee waarschuwingen

**Zichtbaarheid.** Claude Code heeft nog geen aparte kluis voor geheimen; het dialoogvenster
waarschuwt daar zelf voor. Iedereen die de omgeving gebruikt kan de waarde lezen. Bij een
persoonlijke omgeving op een Pro/Max-account ben jij dat alleen. Gebruik hier alleen een
gratis-tier-sleutel die niets anders opent, en zet hem **nooit** in de repo (zie `.gitignore`).
Plak een sleutel ook niet in een chatgesprek.

**Quota.** Bij The Odds API is de prijs per verzoek `aantal markten × aantal regio's`. Met 500
credits per maand en twee runs per dag betekent dat: één regio (`eu`), maximaal twee markten, en
alleen competities die vandaag spelen. Acht competities per dag à 2 credits is ~480 per maand — dat
past net. Laat een run stoppen zodra `x-requests-remaining` onder een reserve komt.

## Nog te doen

**1. ~~Run B-runlijst invullen~~ — gedaan (8 aug 2026).** `prompts/run-b.md` en
`prompts/SCHEDULER-RUN-B.txt` staan klaar met de 17 competities die de gebruiker heeft opgegeven.
Nog wél te doen: van 14 van die 17 is de databekking niet getest (zie de "Let op"-sectie in
run-b.md) — dat trekt de eerste Run B na.

**2. ~~Ophaalcode schrijven~~ — gedaan (8 aug 2026).** `scripts/fotmob.py` (fixtures + team-xG,
met caching per dag in `data/cache/fotmob/`), `scripts/betexplorer.py` (gratis 1X2-odds),
`scripts/oddsapi.py` (Over/Under en de overige markten, credit-bewust) en `scripts/model.py`
(Poisson met Dixon-Coles-correctie + de robuustheidstest) vervangen de ad-hoc-scripts van de
Run A-diagnose. Elk heeft een zelftest (`python3 scripts/<naam>.py`) die tegen echte, actuele data
draait. Zie de toelichting bij Stage 4 in `_shared-rules.md` voor waarom dit `MAX_DEEP_ANALYSES`
van 12 naar 30 heeft gebracht: niet het aantal wedstrijden was de bottleneck, maar het aantal
competities waarvoor nog geen team-xG was opgehaald.

**3. ~~xG-dekking van API-Football per competitie natrekken~~ — nagetrokken (10 aug 2026), en het
antwoord is een ander dan verwacht.** Het probleem is niet dat xG per competitie wisselt, maar dat
het **gratis plan geen enkel seizoen na 2024 teruggeeft** — zie de waarschuwing bij "Sleutels
toevoegen" en `runs/2026-08-10-run-b.md`. De bron staat nu op `plan_limited` in
`source-health.json` en telt niet mee in de datadekkingspoort. Wil je hem alsnog gebruiken, dan is
een betaald plan de enige weg; anders verandert er niets, want Fotmob en xGscore dragen de
kanskant al zonder sleutel.

**4. ~~Fotmob proberen~~ — gedaan (8 aug 2026).** Werkt, zonder sleutel. Bevestigde xG-dekking:
Eredivisie, Primeira Liga, Belgian Pro League, Ekstraklasa, Scottish Premiership, Championship,
League One, League Two, Serie B (ITA) en Serie C (ITA). Zie `data/coverage.json` en
`runs/2026-08-08-run-a-2.md` voor de meting.

**5. Status van de overige diagnosepunten** — gevraagd waren punt 2, 3 en 5; die zijn af. Van de
rest: punt 4 (dynamische competitielijst) viel vanzelf uit de poort in Stage 2 en is meegenomen;
punt 6 (vroeg-seizoen-behandeling) staat als regel in `_shared-rules.md §4` maar is nog niet in de
praktijk getoetst; punt 1 (API-keys) staat hierboven en vraagt een key van de gebruiker.
