# Run C — interlandvoetbal

## Rol

Je bent een professionele betting-analist. Dit is **RUN C van 3**. Run A behandelt de
kerncompetities en clubtoernooien, Run B de overige clubcompetities; meld hun ontbreken niet als
gat. Run C kijkt **uitsluitend naar landenteams**.

Markten: 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS.

**Altijd en alleen volwassen mannenteams (senior A-elftallen).** Zie "Wat er níet op staat".

## Runlijst

**Doorlopend, het hele jaar:**

- Vriendschappelijke interlands (Fotmob `Friendlies`, id **114**, ccode `INT`)
- **CAF Afrika Cup-kwalificatie** (Fotmob id **10608**) — toegevoegd op 20 sep 2026 op verzoek
  van de gebruiker. Speelt in dezelfde vensters als de Nations League en had op 24 september
  tien duels op de kalender.

**Seizoensgebonden — de kalender waar deze runlijst op staat:**

| Toernooi | Wanneer | Status |
|---|---|---|
| UEFA Nations League — groepsfase | 24 sep t/m 17 nov 2026 | **loopt nu** |
| CONCACAF Nations League — groepsfase | sep/okt 2026 | **loopt nu** |
| UEFA Nations League — kwartfinales en play-offs | maart 2027 | |
| CONCACAF Nations League — finales | maart 2027 | |
| Kwalificatie UEFA EK 2028 | heel 2027 (loting 6 dec 2026) | |
| CAF Afrika Cup (AFCON) | 19 jun t/m 17 jul 2027, Tanzania/Kenia/Oeganda | |
| CONCACAF Gold Cup | zomer 2027, data volgen | |
| UEFA Nations League — Finals | juni 2027 | |
| AFC Asian Cup | jan/feb 2028, Saudi-Arabië | |
| UEFA EK 2028 | 9 jun t/m 9 jul 2028, ENG/IRL/SCO/WAL | |
| CONMEBOL Copa América | jun/jul 2028 | |

De kalender is een **verwachting**, geen poort. Een toernooi dat volgens deze tabel niet speelt
maar wél op de Fotmob-daglijst staat, hoort er gewoon bij; een toernooi dat wél zou moeten spelen
maar er niet staat is `GEEN WEDSTRIJD`, geen storing. Werk de tabel bij als een datum verschuift.

## Wat er níet op staat, en waarom

- **Olympische Spelen Los Angeles 2028.** Het olympisch voetbaltoernooi voor mannen is een
  **U23**-toernooi (met drie dispensatiespelers). Dat botst met "altijd volwassen mannenteams",
  dus het staat **niet** op de runlijst. Dit is een keuze die is voorgelegd en niet stilzwijgend
  gemaakt — wil je hem er toch op, zet hem er dan bij en haal deze alinea weg.
- **Vrouwen- en jeugdinterlands.** Nooit. Fotmob zet die onder eigen namen in de daglijst, en die
  namen lijken op de onze. Sluit elke competitie uit waarvan de naam `Women`, `W.`, `U17`, `U19`,
  `U20`, `U21`, `U23` of `Olympic` bevat, en **controleer dat expliciet per run** in plaats van
  erop te vertrouwen dat ze vanzelf buiten de lijst vallen.
- **WK-kwalificatie.** Staat niet op de runlijst. De kwalificatie voor 2030 begint pas rond
  2028; komt ze op de kalender, leg dan eerst aan de gebruiker voor of ze erbij hoort.
  *(AFCON-kwalificatie stond hier tot 20 sep 2026 als openstaand beslispunt en staat sindsdien
  gewoon op de runlijst — de gebruiker heeft ja gezegd.)*

## Werkwijze

Volg **`prompts/_shared-rules.md`** onverkort: parameters, de 0-of-1-bet-regel, de
anti-circulariteitsregel, de pipeline (Stage 0 t/m 6), datalabels, outputformat, vastleggen in de
repo en notificatiebeleid. Eén uitzondering staat hieronder onder "De landenrating", en die
vervangt §4 "Promovendi" en §4 "Kruis-grens" voor deze run.

Run-specifieke waarden:

| Variabele | Waarde |
|---|---|
| `RUN_ID` | `c` |
| Runrapport | `runs/YYYY-MM-DD-run-c.md` |
| `run` in ledger | `"C"` |

---

## Wat je moet weten voordat je begint

Alles hieronder is **gemeten op 20 september 2026**, niet aangenomen. Reken het na als het
verouderd lijkt; de commando's staan erbij.

### 1. De daglijst geeft GROEPEN, geen competities

Fotmob zet elke Nations League-groep als een eigen regel in de daglijst. Op 24 september 2026:

```
UEFA Nations League A Grp. 2   (id 9806)   Netherlands – Germany, Serbia – Greece
UEFA Nations League A Grp. 4   (id 9806)   Norway – Denmark, Portugal – Wales
UEFA Nations League B Grp. 3   (id 9807)   Austria – Israel, Kosovo – Ireland
UEFA Nations League D Grp. 1   (id 9809)   Andorra – Malta
UEFA Nations League D Grp. 2   (id 9809)   Liechtenstein – Lithuania
CONCACAF Nations League B Grp. 1 (id 9821) Puerto Rico – Guyana
Friendlies                     (id 114)    7 duels
```

**`fotmob.find_league(fx, "UEFA Nations League", "INT")` vindt dus niets.** Verzamel alle entries
waarvan de naam met de toernooinaam begint, en voeg hun wedstrijden samen. De `primaryId` is per
**tier** (A/B/C/D), niet per groep — dat is precies de indeling die je verderop nodig hebt.

Bekende ids, gemeten:

| | Fotmob id |
|---|---|
| Vriendschappelijke interlands | 114 |
| UEFA Nations League A / B / C / D | 9806 / 9807 / 9808 / 9809 |
| CONCACAF Nations League (tier B gezien) | 9821 |
| AFCON-kwalificatie | 10608 |
| WK-kwalificatie UEFA/CAF/AFC/CONCACAF/CONMEBOL | 10195 / 10196 / 10197 / 10198 / 10199 |
| WK-kwalificatie interconfederatie-play-off | 10201 |
| Asian Cup-kwalificatie | 10609 |
| WK · EK · AFCON · Copa América · Gold Cup | 77 · 50 · 289 · 44 · 298 |
| **Club** Friendlies — NIET gebruiken | 489 |

De overige toernooien hebben pas een id zodra ze op de kalender staan. Zoek hem dan op in de
daglijst en **schrijf hem in deze tabel** in plaats van hem elke run opnieuw te zoeken.

### 2. De competitiebasis bestaat wél voor de Nations League en NIET voor oefenduels

```bash
python3 -c "from scripts import fotmob; print(fotmob.fetch_league_stats(9806,'2024/2025'))"
```

| | uitkomst op 20 sep 2026 |
|---|---|
| Nations League A, editie **2024/2025** | **16 ploegen, alle 16 met xG** (Spanje 22,8 xG in 10 duels), competitiegemiddelde 1,528 xG per ploeg per duel, thuis 1,75 |
| Nations League A, editie **2026/2027** | 4 ploegen, **geen xG, 0 gespeeld** — de editie was nog niet begonnen |
| Vriendschappelijk (id 114), seizoen 2026 | **`FotmobError: geen bruikbare stand gevonden`** |

> **Achterhaald op 20 september 2026, en met opzet blijven staan.** Dit was het probleem waarop
> de eerste versie van Run C vastliep, en het is opgelost door `scripts/national.py` — zie "De
> landenrating" hieronder. De metingen in de tabel kloppen nog steeds en zijn nuttig om te
> weten; de conclusie eronder niet meer. Lees ze dus als achtergrond, niet als werkwijze.

Wat er destijds uit volgde:

1. **Binnen één Nations League-tier is het gewone model gewoon toepasbaar.** De vorige voltooide
   editie speelt de rol die "vorig seizoen" bij een competitie speelt: teamsterktes uit
   2024/2025, competitiegemiddelde uit diezelfde tabel, `blend_seasons` voor de lopende editie.
2. **De lopende editie is aan het begin leeg of onvolledig.** Controleer dat de tabel van het
   lopende seizoen compleet is (16 ploegen in tier A, niet 4) voordat je hem meegeeft;
   `blend_seasons` geeft bij `mp = 0` vanzelf gewicht 0, maar een halve tabel is erger dan geen.
3. **Een oefeninterland heeft geen stand en dus geen basis.** Er is geen competitiegemiddelde om
   Japan en Uruguay op te normaliseren, en er is geen gemeten verhouding tussen de AFC en de
   CONMEBOL. Dat is geen ontbrekende bron maar een ontbrekende **meting**.

### 3. `interleague.py` helpt hier NIET

Die module bevat aanval- en verdedigingsfactoren per **nationale clubcompetitie**, gefit op 2111
kruis-grensduels uit UCL/UEL/UECL. Landenteams komen daar niet in voor, en de Nederlandse
*clubcompetitie* zegt niets over het Nederlands *elftal*. Gebruik hem niet en val niet stilletjes
terug op factor 1,0 — dat is precies de fout die §4 met die module heeft weggenomen.

---

## De landenrating — dit vervangt §4 "Promovendi" en §4 "Kruis-grens" voor Run C

**`scripts/national.py` geeft élk landenteam een aanval- en een verdedigingsgetal op één
gezamenlijke schaal, gefit op 6784 werkelijke interlanduitslagen.** Daarmee vervalt het hele
probleem waar de eerste versie van dit bestand op vastliep: er hoeft geen competitiebasis meer
te zijn, want de rating ís de basis.

```python
from scripts import national
fit = national.load_fit()                 # één keer per run
ok_h, reden_h = national.in_range(home_id, fit)
ok_a, reden_a = national.in_range(away_id, fit)
if not (ok_h and ok_a):
    tier = "NONE"                         # te weinig duels — zie de poort hieronder
else:
    lg   = national.context(fit)
    hs   = national.team(home_id, fit)
    as_  = national.team(away_id, fit)
    p_xg = analyze_match(hs, as_, lg)     # ongewijzigd, zelfde functie als bij clubvoetbal
```

`team()` levert een gewone `model.TeamStats` en `context()` een gewone `model.LeagueContext`,
dus **de rest van de pijplijn draait er ongewijzigd op**: beide methodes, de acht poorten,
`robustness_check`, `selection_score`, de herijking van §1g, het schaduwlogboek.
`python3 scripts/national.py verify` controleert dat `analyze_match` dezelfde lambdas
teruggeeft als de fit zelf berekent.

### Wat het waard is, en wat niet

Uit-steekproef gemeten op 20 september 2026 — gefit op 5956 duels t/m 1 september 2025 en
getoetst op de 819 duels daarna:

| | Brier op de 1X2-uitkomst |
|---|---|
| **de landenrating** | **0,4796** |
| 1/3-1/3-1/3 gokken | 0,6667 |

Dat is een echt voorspellend model. Wat het **niet** is: een bewijs dat het de bookmaker
verslaat. Die vergelijking staat nergens in `national.py` en hoort thuis in het
kalibratielogboek van §6e — leg dus vanaf de eerste run een `calibration`-blok per doorgerekend
duel vast, precies zoals Run A en Run B dat doen, zodat over enkele weken met cijfers te zeggen
is hoe deze rating zich tot de markt verhoudt.

### De poort: `in_range`

`national.in_range(team_id)` is een **poort, geen aantekening** — dezelfde constructie als
`promotion.conversion_in_range` en `interleague.in_range`. Onder `MIN_MATCHES` = 8 gewogen
duels is de rating vrijwel volledig door de regularisatie bepaald: een aanname met een getal
eromheen, geen meting. Dan `data_tier = NONE` en geen bet. Vang hem af en val **niet** stil
terug op een gemiddelde ploeg.

### Welk datatier

| Situatie | `data_tier` |
|---|---|
| Beide ploegen door `in_range`, en het duel is een **kwalificatie-, Nations League- of toernooiduel** | `LIGHT` |
| Beide ploegen door `in_range`, en het duel is een **oefeninterland** | `LIGHT` |
| Een van beide ploegen valt buiten `in_range` | `NONE` |

**Nooit `FULL`, en dat is met opzet.** `FULL` eist in §4 minstens twee onafhankelijke inputs
waarvan één uit categorie 1, en de landenrating is er één: hij komt uit doelpunten, niet uit
xG, en er is geen tweede, onafhankelijk landenmodel naast gezet. `LIGHT` betekent
`EDGE_THRESHOLD_LIGHT` = 16,0 procentpunt, en daar gaat de herijking van §1g nog overheen — dus
verwacht ook met deze rating weinig bets. Dat is de juiste voorzichtigheid en geen defect.

Twee dingen die je daarbij niet moet doen:

- **Reken een oefeninterland niet zwaarder dan hij is.** De rating weegt oefenduels voor de
  helft mee, maar dat gewicht is **niet gemeten** — Fotmob geeft voor oefeninterlands alleen het
  lopende kalenderjaar, dus er zat er geen enkele in de trainingsperiode. Dat staat in de
  parametertabel van `national.py` en het is de eerlijke stand: een aanname, geen bevinding.
- **Verwar de rating niet met vorm.** Hij zegt hoe sterk een ploeg over jaren is, niet wie er
  dinsdag speelt. Poort 7 (context) blijft dus gewoon draaien, met de kanttekening hieronder
  over rustdagen bij interlands.

### Het corpus onderhouden

```bash
python3 scripts/national.py build     # haalt alle edities opnieuw op (~60 verzoeken, geen credits)
python3 scripts/national.py fit       # fit opnieuw en schrijft data/national-fit.json
python3 scripts/national.py stats     # omvang en dekking
python3 scripts/national.py tune      # de wegingen opnieuw uit-steekproef meten
```

**Draai `build` + `fit` aan het eind van elk interlandvenster**, niet elke dag: het corpus
verandert alleen als er interlands zijn gespeeld, en `build` kost een minuut of wat. Commit
`data/national-matches.jsonl` en `data/national-fit.json` mee — dat zijn metingen, geen cache.

Wat er in het corpus zit (gemeten 20 sep 2026, 6784 duels van 2006 t/m nu): WK-kwalificatie van
alle vijf de confederaties (2947), AFCON-kwalificatie (602), Nations League UEFA en CONCACAF,
de eindtoernooien WK/EK/AFCON/Copa América/Gold Cup, Asian Cup-kwalificatie, en 287
oefeninterlands. Dat laatste getal is het zwakke punt: het zijn er maar 287 en ze komen allemaal
uit één kalenderjaar.

### Wat hier nog niet goed aan is

1. **Geen historische oefeninterlands.** Zie hierboven. Zolang dat zo is, is de oefenweging een
   aanname. Een tweede jaargang lost het op; kijk of Fotmob ze ooit via een ander seizoenslabel
   teruggeeft.
2. **De AFC Asian Cup-eindronde zit niet in het corpus.** Zijn id is nog niet gevonden — het
   toernooi speelde niet in de doorzochte periode. Voeg hem toe aan `national.COMPETITIONS`
   zodra hij in de daglijst opduikt (jan/feb 2028) en draai `build` opnieuw.
3. **De rating kent geen xG, alleen doelpunten.** Bij clubvoetbal draait alles op xG; hier niet,
   want Fotmob geeft voor de meeste interlandcompetities geen team-xG. Een ploeg die veel
   scoort uit weinig kansen wordt hier dus overschat, en de correctie die §1f daarvoor heeft
   (de 80/20-weging tussen twee methodes) bestaat hier niet in dezelfde vorm.
4. **Er is geen tweede, onafhankelijke methode.** Poort 5 eist dat twee methodes de markt
   dezelfde kant op verslaan. Bij clubvoetbal zijn dat de xG-methode en de splitsmethode; hier
   is er er maar één. Dat is de belangrijkste reden dat het datatier op `LIGHT` blijft.

   Twee kandidaten zijn op 20 september 2026 onderzocht, op voorstel van de gebruiker:

   - **Een wereldranglijst (FIFA).** Bruikbaar, maar zwakker dan hij lijkt: die ranglijst wordt
     zelf berekend uit dezelfde uitslagen waarop `national.py` is gefit, en hij perst ze in één
     getal terwijl de rating aanval en verdediging apart houdt en met doelsaldo rekent in plaats
     van met winst/verlies. Als tweede methode voor poort 5 is hij dus grotendeels dezelfde
     meting in een armere vorm, en "ze zijn het eens" zegt dan weinig. Wáár hij wél iets
     toevoegt: als **prior voor ploegen onder `MIN_MATCHES`**, die nu helemaal wegvallen. Dat is
     een smalle maar echte winst, en het is de enige reden om hem op te halen.
   - **Individuele spelersvorm — de sterkste kandidaat.** Het `lineup`-blok geeft per speler
     `id`, `marketValue` én `primaryTeamId`/`primaryTeamName`: de club waar hij speelt. Daarmee
     is de clubvorm van de opgestelde spelers op te halen, en dát is informatie die
     **orthogonaal** is aan de interlanduitslagen waarop de rating is gefit — anders dan de
     ranglijst. Een landenteam is een greep uit clubspelers, en of die greep in vorm is weet een
     rating op landenuitslagen per definitie niet.

     Twee harde beperkingen voordat iemand dit bouwt, allebei gemeten op 20 sep 2026: de
     opstelling is er pas **vlak voor de aftrap** (bij Nederland – Duitsland stond er vier dagen
     vooraf nog helemaal niets, en Run C draait om 05:15), en het kost ~22 spelersopvragingen
     plus clubvorm per duel. Bouw het dus zo dat het duel gewoon doorgaat als de opstelling er
     nog niet is — mét de aantekening dat er niets gemeten is, en niet stilzwijgend als "gemeten"
     geteld. Dat is precies de fout die poort 7 hieronder wél maakt.

## Let op bij deze runlijst

- **De meeste dagen is er niets.** Interlandvoetbal speelt in ongeveer vijf vensters per jaar.
  Buiten die vensters staat élke competitie op `GEEN WEDSTRIJD` en is de notificatie een
  hartslag van één regel. Dat is correct gedrag (§7): zolang er elke run een melding komt, is
  een uitgebleven melding zelf het signaal dat er iets stuk is.
- **Prijzen zijn dunner dan bij clubvoetbal.** Op 20 september 2026 had van de hele runlijst
  alleen `soccer_uefa_nations_league` een sportkey bij The Odds API. Oefeninterlands en de
  CONCACAF Nations League hadden er geen. Bepaal de sportkey per run uit de **actieve** lijst
  van `api_check.py` in plaats van hem hier hard te coderen, en noteer in het runrapport welke
  competities alleen een BetExplorer-marktgemiddelde hadden — daar valt de edge systematisch te
  laag uit (§1a).
- **`MAX_DEEP_ANALYSES` zal nooit knellen.** Twintig duels op de drukste dag van het jaar tegen
  een cap van 40 of 55. Rapporteer de afkapping toch, met 0.
- **POORT 7 IS OP INTERLANDS INERT, EN DAT ZIET ERUIT ALS "POORT OPEN".** Nagemeten op
  20 september 2026, en dit is de belangrijkste valkuil van deze run.
  `context.fetch_match_context` draait wél op een interland, maar geeft lege of misleidende
  waarden terug:

  | | gemeten op een interland |
  |---|---|
  | uitvallers (`out_count`, `out_value`) | **altijd 0** — Fotmob houdt geen blessurelijst per landenteam bij |
  | `squad_value` | wél gevuld zodra de opstelling er is (Frankrijk € 819 mln; bij Irak € 0) |
  | `lineup_type` | leeg tot vlak voor de aftrap; bij NED – GER vier dagen vooraf helemaal niets |
  | ploegnamen | vóór publicatie van de opstelling letterlijk `"thuis"` en `"uit"` |
  | `rest_days` | tijd sinds de vórige **interland**, niet sinds het vorige clubduel — bij NED – GER **86,7 dagen** |

  Gevolg: de blessure-arm van poort 7 kan nooit afgaan (0% ontbrekende waarde tegen 0%) en de
  rust-arm evenmin (86 dagen haalt de drempel van "≤ 4 dagen rust" nooit). De poort meldt dan
  `"geen materieel nadeel gemeten"` en gaat open — **niet omdat er geen nadeel is, maar omdat er
  niets gemeten is.** Dat is precies het soort stille administratiefout waar §6b-5b voor is
  ingevoerd, en het is erger dan een dichte poort: hij telt mee als geslaagde controle.

  **Wat je daarom doet:** noteer per duel in `data/run-state/` onder `context` expliciet
  `"poort7_meetbaar": false` zodra `out_count == 0` én `squad_value == 0`, en schrijf in het
  runrapport dat poort 7 deze run niet heeft kúnnen meten in plaats van hem als geslaagde
  controle op te voeren. Laat hem verder gewoon draaien — hij kost niets en gaat vanzelf werken
  zodra Fotmob meer levert — maar tel hem niet mee als bescherming. `ctxlog.py` houdt deze groep
  bovendien apart: een interland hoort niet in dezelfde reeks als een clubduel, want het
  beschikbaarheidsverschil is daar per definitie nul en zou de meting van §1c verwateren.
- **De 90-minutenregel van §6d is hier extra belangrijk.** Nations League-play-offs, EK-
  kwalificatie-play-offs en alle knock-outrondes van AFCON, Gold Cup, Asian Cup, EK en Copa
  América kennen verlenging en strafschoppen. Wikkel af op de stand na 90 minuten inclusief
  blessuretijd, nooit op `status.scoreStr`.
