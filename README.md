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
  run-b.md              Run B: idem (competitielijst nog in te vullen)
  _shared-rules.md      de eigenlijke opdracht — parameters, regels, pipeline, format
data/
  coverage.json         welke bron welke competitie kan bedienen, en in welke rol
  source-health.json    wat elke bron laatst deed toen we hem probeerden
  picks.jsonl           het logboek: één gepubliceerde bet per regel
schema/
  pick.schema.json      velddefinitie van een pick
scripts/
  ledger.py             valideren, afwikkelen en meten (alleen stdlib)
runs/
  TEMPLATE.md           vorm van een runrapport
  YYYY-MM-DD-run-a.md   het rapport van elke run
```

De scheduler-prompt is met opzet kort en verwijst naar `prompts/`. **Regels aanpassen doe je in de
repo, niet in de scheduler.**

## Installeren in de scheduler

Vervang de lange prompt van je Run A-taak door de tekst onder de streep in
`prompts/SCHEDULER-RUN-A.txt`. Doe hetzelfde voor Run B zodra de runlijst in `prompts/run-b.md` is
ingevuld.

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
| `API_FOOTBALL_KEY` | api-football.com (gratis: 100 verzoeken/dag) | statistieken, opstellingen, blessures | **Ja — dit is wat de routine deblokkeert** |
| `ODDS_API_KEY` | the-odds-api.com (gratis: 500 credits/maand) | odds per bookmaker als JSON | Optioneel, verbetering |

Waarom die volgorde: odds werken al via Oddschecker. Wat ontbreekt is een **onafhankelijke
kansinput**, want zonder die zou `my_prob` uit de bookmakerprijs komen — precies wat
`_shared-rules.md §2` verbiedt. `API_FOOTBALL_KEY` vult dat gat; `ODDS_API_KEY` maakt alleen de
prijskant netter.

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

**1. Run B-runlijst invullen** — `prompts/run-b.md` heeft een lege competitielijst. Die is met opzet
niet geraden.

**2. Ophaalcode schrijven zodra er een sleutel is.** `scripts/api_check.py` controleert alleen of de
sleutels werken. De code die daadwerkelijk statistieken en odds ophaalt en omzet naar `my_prob` is er
nog niet, omdat de responsevorm zonder werkende sleutel niet te verifiëren is — die op gok
schrijven levert code op die er goed uitziet en niet werkt.

**3. xG-dekking van API-Football per competitie natrekken.** Alle endpoints zitten in het gratis
plan, maar xG blijkt per competitie en seizoen wisselend aanwezig. Zolang dat niet nagetrokken is,
geldt API-Football als tier-2-bron (`LIGHT`), niet als xG-bron (`FULL`).

**4. Fotmob proberen** — de enige onafhankelijke kansbron met brede dekking die nog niet getest is.
Werkt hij, dan komen Eredivisie, Primeira Liga, Belgian Pro League en Ekstraklasa binnen bereik
zonder sleutel.

**5. Status van de overige diagnosepunten** — gevraagd waren punt 2, 3 en 5; die zijn af. Van de
rest: punt 4 (dynamische competitielijst) viel vanzelf uit de poort in Stage 2 en is meegenomen;
punt 6 (vroeg-seizoen-behandeling) staat als regel in `_shared-rules.md §4` maar is nog niet in de
praktijk getoetst; punt 1 (API-keys) staat hierboven en vraagt een key van de gebruiker.
