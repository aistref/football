# Gedeelde analyseregels — Run A & Run B

Deze regels gelden voor **elke** run. Wijzig ze hier in de repo, niet in de scheduler.
De scheduler-prompt is met opzet kort en verwijst naar dit bestand, zodat je regels kunt
aanpassen zonder de geplande taak aan te raken.

---

## 0. Vaste parameters

| Parameter | Waarde | Waarom |
|---|---|---|
| `MAX_DEEP_ANALYSES` | **30** (ma–do) / **35** (vr–zo) | Harde cap. Zonder cap loopt een run met 40+ wedstrijden altijd zijn tijdslimiet in en levert een halve lijst. Verhoogd van 12 naar 30 op 8 aug 2026 nadat `scripts/fotmob.py`, `scripts/model.py`, `scripts/betexplorer.py` en `scripts/oddsapi.py` de ophaal- en rekenlogica herbruikbaar maakten. **Weekendwaarde 35 toegevoegd 29 aug 2026, op verzoek van de gebruiker**: die zaterdag stonden er 49 duels op de Run A-runlijst en 59 op die van Run B, dus er paste ongeveer 60%. Gebruik `ranking.max_deep_analyses(date.today())`; dezelfde dagindeling als `MAX_SHORTLIST`. |
| `MAX_SHORTLIST` | **3** (ma–do) / **5** (vr–zo) | Onveranderd t.o.v. de oude opdracht. |
| `EDGE_THRESHOLD_FULL` | **8.0 procentpunt** | Verhoogd van 3.0 op 31 aug 2026, op verzoek van de gebruiker, en dit keer op **uitkomsten** gemeten in plaats van beredeneerd. Zie "Waarom de drempel op 8 staat" hieronder. |
| `EDGE_THRESHOLD_LIGHT` | **16.0 procentpunt** | Zwakkere data eist een grotere marge: exact tweemaal `EDGE_THRESHOLD_FULL`. Die verhouding is geen keuze maar een afhankelijkheid — `model.DATA_WEIGHT` leidt het LIGHT-gewicht van 0.5 in `selection_score` er rechtstreeks uit af (§1a). Verander de een niet zonder de ander. |
| `MAX_LIGHT_IN_SHORTLIST` | **2** | Voorkomt dat de topselectie volloopt met zwak onderbouwde bets. |
| `MIN_ODDS` / `MAX_ODDS` | **1.30** / **6.00** | Buiten deze band is de kansschatting te onnauwkeurig om edge zinvol te noemen. |
| `SETTLE_AFTER_HOURS` | **vervallen** | Vervangen op 3 sep 2026 door de statusregel hieronder. Stond van de eerste commit tot die datum op 12 uur na de **aftrap**, zonder onderbouwing. |
| `SETTLE_FALLBACK_HOURS` | **2.0** | Alleen de terugval als de bron geen status geeft. `scripts/settling.FALLBACK_HOURS`. |
| `XG_WEIGHT` | **0.80** | Hoe zwaar de xG-methode weegt in `my_prob` tegenover de splitsmethode. Was tot 5 sep 2026 impliciet 0.50 (ongewogen gemiddelde), en dat was nooit ergens op gebaseerd. Op **uitslagen** gemeten over 392 afgerekende gevallen; zie §1f. De curve is vlak tussen 0.7 en 1.0 — niet op fijnregelen. `scripts/model.XG_WEIGHT`. |
| `CREDIBILITY_K` | **8** | Na hoeveel duels het lopende seizoen even zwaar weegt als het hele vorige. Op 5 sep 2026 op verzoek van de gebruiker van 16 naar 8 gezet: sneller meebewegen, tegen 13% van de gemeten blendwinst. Zie §4. `scripts/model.CREDIBILITY_K`. |
| `UNDERDOG_FLOOR` | **0.35** | Onder deze marktkans gaat poort 8 dicht op de underdog-kant; daarboven staat hij open. Verving op 5 sep 2026 de zware versie die élke underdog blokkeerde. Zie §1e. `scripts/sides.UNDERDOG_FLOOR`. |
| `EXCHANGE_COMMISSION` | **2%** | Commissie over de nettowinst bij een beurs (Betfair, Matchbook). Op 5 sep 2026 stond de beste 1X2-prijs in 61% van de gevallen bij een beurs, dus dit is geen randgeval: reken elke koers door `oddsapi.net_price` voordat je er edge op meet. `scripts/oddsapi.EXCHANGE_COMMISSION`. |
| `MIN_OBSERVATIONS` | **150** | Onder dit aantal afgerekende gevallen wordt `my_prob` niet herijkt en gaat hij ongewijzigd door. Zie §1g. `scripts/recalibrate.MIN_OBSERVATIONS`. |

### Wanneer een pick afwikkelbaar is (herzien 3 sep 2026, op verzoek van de gebruiker)

**Een wedstrijd is afwikkelbaar zodra de bron hem als afgelopen meldt**, niet zodra er een aantal uur
sinds de aftrap verstreken is:

```python
from scripts.settling import DayIndex, settleable
index = DayIndex()                      # één Fotmob-verzoek per kalenderdag
ok, reden = settleable(pick, index)     # `finished` van de bron; klok alleen als terugval
```

`scripts/ledger.py open` en `scripts/shadow.py open` doen dit allebei, uit **dezelfde** module — zie
hieronder waarom dat laatste geen detail is. Geeft de bron niets terug (geen netwerk, wedstrijd niet
gevonden, veld ontbreekt), dan valt de regel terug op `SETTLE_FALLBACK_HOURS` = 2 uur na de aftrap.
Twee uur is de speelduur inclusief rust en blessuretijd, en die terugval is met opzet krap: hij geldt
alleen wanneer er géén status te krijgen was, en anders wacht een run opnieuw een hele dag.

Wat de oude regel fout deed, en waarom een tussenwaarde als "6 uur na het fluitsignaal" het probleem
niet oplost:

1. **De 12 was nooit onderbouwd.** Hij stond in de eerste commit van de repo en deze tabel gaf alleen
   een beschrijving, geen reden — anders dan `EDGE_THRESHOLD_FULL`, waar hierboven een halve pagina
   staat waarop de 8 gemeten is. Er was dus geen antwoord op "waarom 12 en niet 8".
2. **Hij mat vanaf de aftrap.** Een wedstrijd duurt met rust en blessuretijd ongeveer twee uur, dus de
   feitelijke marge ná het laatste fluitsignaal was ~10 uur.
3. **Hij viel systematisch verkeerd uit.** Run A draait rond 04:10 en avondwedstrijden trappen af
   tussen 20:00 en 21:00 CEST; die staan dan op 7 à 8 uur, vielen dus **élke keer** net buiten de
   grens, en werden pas door de vólgende run afgewikkeld — na ~24 uur in plaats van na 12. Gemeten
   over de eerste 246 afgewikkelde picks: mediaan 9,7 uur, met een kwart in de staart van 12 tot
   18 uur. Dat is precies die groep.
4. **`shadow.py` had helemaal geen filter.** De docstring adverteerde `--hours 12`, maar `cmd_open`
   filterde alleen op `result == pending` en die vlag bestond niet eens. Daardoor rekende de routine
   de afgewezen kandidaten van een wedstrijd wél af en de gespeelde bet van diezelfde wedstrijd niet.
   Op 2 sep 2026 leverde dat een runrapport op waarin stond wat de tegengehouden kandidaten deden en
   niet wat de bets deden. Dat is de reden dat de regel nu in één module staat in plaats van twee keer
   los: zolang beide scripts hun eigen versie hebben, lopen ze uiteen.

Wat de marge moest voorkomen blijft gelden — een uitslag noteren van een duel dat is uitgesteld,
gestaakt of waar nog verlenging loopt — maar `finished` is dáár het directe antwoord op, waar een klok
er een schatting van was. Een klok van zes uur na het fluitsignaal zou punten 1 en 3 verzachten en
punt 4 helemaal niet raken.

**Dit verandert niet wélke stand je gebruikt.** `status.scoreStr` is de **eind**stand, inclusief
verlenging en strafschoppen; §6d eist afrekenen op de stand na 90 minuten. `finished` zegt alleen
wanneer je mág afwikkelen. Zoek bij een knock-outduel dus nog steeds de doelpuntminuten op — op
3 sep 2026 was Sassuolo – Frosinone (Coppa Italia) na 90 minuten 1–1 en ging Sassuolo op strafschoppen
door; de schaduwpick op "Frosinone of gelijk" is daarom **gewonnen**, niet verloren.

### Waarom de drempel op 8 staat (31 aug 2026)

Van 8 t/m 31 aug stond `EDGE_THRESHOLD_FULL` op 3.0, met als motivering "onder deze grens is de
schatting niet te onderscheiden van modelruis". Dat was een redenering, geen meting. Inmiddels
liggen er 179 beslist afgewikkelde picks, en die zeggen iets anders:

| geclaimde edge | picks | hit rate | ROI |
|---|---|---|---|
| 3–5 pp | 33 | 42.4% | **−7.6%** |
| 5–8 pp | 59 | 37.3% | **−14.3%** |
| 8–12 pp | 47 | 48.9% | +4.5% |
| 12–20 pp | 36 | 52.8% | +7.4% |

Cumulatief, alleen `FULL` (n=156): bij drempel 3 is de ROI −5.4%, bij 5 −4.8%, bij **6 −8.4%**,
bij 7 −4.6%, en pas bij **8.0 draait het teken om** (+0.6%), daarna +3.5% (9) en +10.6% (10).

Twee dingen die daaruit volgen en die je niet moet vergeten als je hieraan komt te sleutelen:

1. **Een tussenwaarde is het slechtste van twee werelden.** Bij de bespreking op 31 aug was 6 het
   eerste voorstel, als voorzichtige stap. De meting wees dat af: bij 6 verlies je een derde van je
   bets én blijf je op −8.4% staan. De keuze is er dus een tussen 3 (veel bets, structureel verlies)
   en 8 (ongeveer de helft minder bets, rond break-even) — niet een schuifregelaar waar elk punt
   ertussen een beetje helpt.
2. **Dit is in-sample gekozen en dat is een echt bezwaar.** De grens is bepaald op dezelfde 179
   waarnemingen waarop hij hierboven wordt verantwoord; precies de fout waar §6d voor waarschuwt.
   Wat het meer maakt dan één anekdote: het teken is consistent over vier aaneengesloten banden,
   en het gaat om alle picks samen en niet om één poort of één markt. Wat het minder maakt: bij
   drempel 12 zakt de ROI weer naar +1.4% (n=29), en die niet-monotone staart is ruis. Behandel 8
   dus als "de eerste waarde waarbij het teken omslaat", niet als een optimum — en herzie hem op
   uitkomsten, niet op een nieuwe redenering.

**`EDGE_THRESHOLD_LIGHT` is niet gefit.** Er zijn maar 23 afgewikkelde LIGHT-picks; boven drempel 12
zijn het er nog 11, 8, 4 en 3, en dan meet je niets meer. De 16.0 volgt daarom uitsluitend uit de
2:1-verhouding waar `model.DATA_WEIGHT` van afhangt. Gevolg: LIGHT-bets worden zeldzaam. Dat is
aanvaard omdat LIGHT per definitie de categorie met de dunste onderbouwing is, maar het is een
gevolg van een afhankelijkheid en niet van een meting — noteer het als zodanig als de LIGHT-reeks
ooit groot genoeg wordt om er wél iets over te zeggen.

---

## 1. Selectie: **0 of 1** bet per wedstrijd

> Dit vervangt de oude regel "exact één beste valuebet per wedstrijd".

Per geanalyseerde wedstrijd geldt precies één van twee uitkomsten:

- **BET** — er is één markt/selectie die alle poorten hieronder passeert.
- **GEEN BET** — met een reden in één regel. Dit is een volwaardige, correcte uitkomst.

**Draai altijd beide methodes**, weeg ze, en herijk het resultaat op uitslagen:

```python
from scripts.model import combine_probs
from scripts.recalibrate import load_fit, apply

fit     = load_fit()                      # één keer per run, leest picks.jsonl + shadow.jsonl
p_xg    = analyze_match(...)              # op xG, genormaliseerd op de competitie
p_split = analyze_match_from_splits(..., league=league)   # LET OP: league meegeven, zie §1d
my_raw  = combine_probs(p_xg, p_split)    # 0.80 op xG, 0.20 op de splits — zie §1f
my_prob = apply(my_raw, fit)              # herijking op uitslagen — zie §1g
edge_pp = (my_prob - 1 / odds) * 100
```

**Beide stappen zijn nieuw op 5 sep 2026 en allebei op uitkomsten gemeten.** Tot die datum was
`my_prob` het ongewogen gemiddelde van de twee methodes, ongecorrigeerd. Noteer in de pick zowel
`my_raw` als `my_prob`, zodat achteraf te zien is wat de herijking heeft gedaan.

Een bet mag alleen gepubliceerd worden als **alle** voorwaarden gelden:

1. `edge_pp ≥ EDGE_THRESHOLD_FULL` bij `data_tier = FULL`, of `≥ EDGE_THRESHOLD_LIGHT` bij `LIGHT`
   — gemeten op de **gewogen en herijkte** `my_prob` hierboven, niet op één van de twee methodes
   afzonderlijk en niet op `my_raw`;
2. `MIN_ODDS ≤ odds ≤ MAX_ODDS`;
3. de anti-circulariteitsregel (§2) is voldaan;
4. `data_tier ≠ NONE`;
5. **de twee methodes spreken elkaar niet tegen.** Beide moeten de markt dezelfde kant op
   verslaan: `p_xg > 1/odds` **én** `p_split > 1/odds`. Zakt één van de twee onder de
   marktkans, dan wijzen ze tegengesteld en gaat de bet eruit met reden "data conflicterend";
6. **de edge draait niet om bij een andere parameterkeuze:**
   `robustness_check(...).min_edge > 0` over het hele (shrink, rho)-grid;
7. **de context spreekt de bet niet tegen** (§1c): `context.check(ctx, side).passed`;
8. **de selectie staat niet op een underdog-kant die de markt onder `UNDERDOG_FLOOR` zet** (§1e):
   `sides.check(side, odds_1x2).passed`.

### Poort 7 — contextfactoren (toegevoegd 23 aug 2026, op aanwijzing van de gebruiker)

Tot deze datum rekende de routine uitsluitend met xG en doelpuntensplits van vórig seizoen. Alles
wat een mens als eerste noemt — blessures, schorsingen, vorm, een zware midweekse wedstrijd — zat
niet in `my_prob` en werd nergens vastgelegd, terwijl §4 die factoren nadrukkelijk als geldige
categorie-1-input noemt. De code deed er niets mee.

Dat gat wijst één kant op. Ontbrekende context is gemiddeld slecht nieuws voor de ploeg die het
treft, en de routine zette structureel op de zwakkere ploeg: **89% van alle picks die een ploeg
speelden, speelde de zwakkere kant**, met een ROI van −29.7% tegen −14.4% voor de markten zonder
kant (O/U, BTTS). Juist bij een zwakke ploeg hakt een uitgevallen spits of een Europese
uitwedstrijd op woensdag er het hardst in.

```python
from scripts import context
ctx = context.fetch_match_context(match_id, kickoff_utc)   # Fotmob, geen credits
gate = context.check(ctx, side)                            # side: "home" | "away" | None
```

De poort is met opzet **asymmetrisch en grof**:

- Hij houdt alleen tegen; hij laat nooit iets extra's door en stelt `my_prob` niet bij. Er is geen
  enkele meting die zegt hoeveel procentpunt een geblesseerde middenvelder waard is, en zo'n getal
  verzinnen is precies wat §2 en §4 verbieden.
- Bij `side = None` (Over/Under, BTTS, gelijkspel) staat hij altijd open: er is geen kant om te
  benadelen, en in welke richting context een *totaal* verschuift is zonder meting niet te zeggen.
- Ontbrekende data laat de poort open. Een meting die er niet is, is geen bewijs van een probleem.

**Derde controle: wordt er wel gespeeld waar je denkt?** `context.check_venue` vergelijkt het
stadion van de wedstrijd met het eigen stadion van de genoteerde thuisploeg (beide uit Fotmob) en
zet `relocated` als die verschillen. Aanleiding, 23 aug 2026: Rennes – PSG was in werkelijkheid
**PSG's thuiswedstrijd**, verplaatst naar Roazhon Park omdat de mat van het Parc des Princes na de
hittegolven onbespeelbaar was. Thuisvoordeel is de aanname waar het model het zwaarst op leunt, en
een verplaatsing raakt hem rechtstreeks.

Let op wat deze controle wél en niet vangt. Op 23 aug sloeg hij **niet** aan, en terecht: Fotmob,
BetExplorer en The Odds API hadden de omwisseling alle drie al verwerkt en noteerden Rennes als
thuisploeg in Roazhon Park — wat feitelijk klopt. Wat geen enkele van die bronnen laat zien, is dat
het oorspronkelijk PSG's thuiswedstrijd was. Dat is **nieuws, geen data**, en een geplande run heeft
geen nieuwsbron. De controle vangt dus het geval waarin een ploeg buiten de eigen deur speelt zonder
dat de bronnen dat verwerken; hij vangt niet dat een fixture van eigenaar is gewisseld. Zet
`relocated` en de stadionnaam altijd in `data/run-state/`, en noem een verplaatsing in het
runrapport — ook als de poort opengaat.

Twee criteria, allebei **voorlopig** — ze zijn niet gefit, want er is nog geen enkele afgerekende
bet mét contextdata:

| Criterium | Drempel | Bron |
|---|---|---|
| blessures/schorsingen | de gespeelde kant mist ≥ 10 procentpunt méér selectiewaarde dan de tegenstander | `lineup.*.unavailable` + `totalStarterMarketValue` |
| rust | de gespeelde kant heeft ≤ 4 dagen rust én ≥ 2 dagen minder dan de tegenstander | data uit `matchFacts.teamForm` |

Marktwaarde is een grove maat voor hoe belangrijk een speler is, maar het is de enige die Fotmob
per uitvaller meegeeft, en hij onderscheidt in elk geval een eerste spits van een derde keeper.
**Leg de volledige context van élke wedstrijd waarvoor je haar hebt opgehaald vast in
`data/run-state/`** — dus ook als de poort opengaat, én ook als het duel door `MAX_DEEP_ANALYSES` is
afgekapt. Dat laatste is nieuw op 5 sep 2026 en het is de kern van de meting hieronder: Stage 4 eist
toch al dat de context vóór de afkapping wordt opgehaald, dus die duels kosten niets extra en ze
verdrievoudigen de steekproef.

Draai daarna, elke run:

```bash
python3 scripts/ctxlog.py collect --run <a|b> --date YYYY-MM-DD
python3 scripts/ctxlog.py settle
python3 scripts/ctxlog.py stats        # in het runrapport
```

#### De bijstelling is geprobeerd te meten en er is niets gevonden (5 sep 2026)

Op verzoek van de gebruiker is nagegaan of poort 7 van een **rem** een **bijstelling** kon worden —
of ontbrekende spelers voorspellen waar het model naast zit. Gemeten op 147 wedstrijden met een
contextblok, een marktkans én een uitslag, tegen **uitkomsten** en niet tegen de markt:

| | r | t | helling |
|---|---|---|---|
| fout van het model tegen het beschikbaarheidsverschil | −0.007 | −0.08 | −2.2 pp per eenheid |
| fout van de markt tegen hetzelfde verschil | −0.028 | −0.34 | −9.1 pp per eenheid |

**Niets.** Het teken wijst de verwachte kant op maar het effect is over het hele waargenomen bereik
1.5 procentpunt, en dat blijft zo in elke variant: zonder uitschieters, alleen wedstrijden waarin
iemand ontbreekt, en ook op doelpunten in plaats van op de uitslag.

**Lees dat niet als "blessures doen er niet toe".** Met 147 wedstrijden was alleen een effect van
~54 pp per eenheid aantoonbaar geweest, en zo groot is het zeker niet. Wat er nodig is:

| effect (pp per eenheid) | wedstrijden nodig |
|---|---|
| 30 | ~475 |
| 20 | ~1.070 |
| 15 | ~1.900 |
| 10 | ~4.270 |

Bij tien bruikbare wedstrijden per dag duurt dat zeven maanden; door élke wedstrijd met context te
loggen in plaats van alleen de doorgerekende worden het er ruim honderd per dag, en is de vraag over
drie tot vier weken beantwoordbaar. Dat is precies wat `scripts/ctxlog.py` doet.

**Tot die meting er is blijft poort 7 een rem en geen bijstelling.** Een getal verzinnen omdat het
plausibel klinkt is exact wat §2 en §4 verbieden, en het zou hier bovendien ruis toevoegen aan een
model dat al te optimistisch is (§1g). Dezelfde discipline als bij §6d: liever een bet te veel
tegengehouden dan een verzonnen kansbijstelling.

**Eén valkuil bij het narekenen, want die is bij de eerste poging misgegaan.** Het aandeel
ontbrekende selectiewaarde is `out / (basis + out)` en **niet** `out / basis`: `squad_value` is de
waarde van de vermoedelijke basiself en de uitvallers zitten daar niet in. Met de verkeerde noemer
kwam Lommel – Club Brugge op 247% uit — onmogelijk — en liep de regressie bovendien op twee
verschillende definities door elkaar, want de oudere tekstvorm van het contextblok gebruikte wél de
goede. `ctxlog.out_share` doet het nu op één plek, voor beide vormen.

### Poort 8 — niet op de underdog-kant (toegevoegd 4 sep 2026, op verzoek van de gebruiker)

```python
from scripts import sides
gate = sides.check(side, odds_1x2)      # side: "home" | "away" | None; odds_1x2: [1, X, 2]
```

**Dit is een rem, geen fijnregeling, en hij is met opzet grof.** Aanleiding is de spiegelanalyse in
`runs/2026-09-04-run-a.md`: van alle 207 afgewikkelde picks hebben er 118 een kant, en daarvan stond
**89 — driekwart — op de underdog**. Drie metingen, alle drie op **uitkomsten** en niet tegen de
markt, en dus vrij van het circulariteitsbezwaar waarop de correctie van 31 aug is ingetrokken:

| | n | trefkans | rendement |
|---|---|---|---|
| underdog-kant, zoals gespeeld | 89 | 36.0% | **−15.76u (−17.7%)** |
| dezelfde bet op de favorietenkant | 89 | 53.9% | +6.28u (geschatte koersen) |
| alle overige picks samen | 118 | — | **+1.46u (+1.2%)** |

1. **Alle verlies van de routine zit in die ene kant.** Het logboek staat op −14.31u; de
   underdog-bets op −15.76u en al het andere op +1.46u.
2. **De kansschatting daar is aantoonbaar te hoog.** Over die 89 verwachtte het model 47.1
   winnaars, de markt 38.0, werkelijk 33.0 — **z = −3.14** voor het model tegen −1.11 voor de
   markt. Dat is dezelfde bevinding als de −4.42 pp op favorieten in §6e, maar gemeten op
   uitslagen.
3. **Een hogere drempel lost het niet op — dat is nagerekend en verworpen.** Het eerste voorstel
   was een asymmetrische edge-eis. De cijfers wijzen het af: op de underdog-kant zakt de ROI
   naarmate de drempel stijgt (−26.3% vanaf 8 pp, −46.4% vanaf 12, −64.4% vanaf 20 bij n=5),
   terwijl hij bij alle andere picks juist stijgt (+15.6% vanaf 8 pp, +26.4% vanaf 10). Een
   grotere geclaimde edge is daar geen sterker signaal dat de bet goed is maar dat het model
   ernaast zit. Een signaal dat averechts werkt naarmate het sterker wordt, is niet zwak maar
   kapot — en daarop hoor je niet te spelen.

De poort werkt als poort 7: hij houdt alleen tegen, stelt `my_prob` niet bij, staat open bij
`side = None` (Over/Under, BTTS, gelijkspel), en staat ook open als er geen 1X2-prijzen zijn — dan
is er geen marktoordeel over wie de mindere ploeg is. Binnen `PICKEM_TOLERANCE` (3 pp verschil in
de-vigde marktkans) noemt de markt geen van beide ploegen de mindere en gaat de poort open.

### Verlicht op 5 september 2026, op verzoek van de gebruiker

**De poort blokkeerde tot die datum élke selectie op de underdog-kant. Dat is te grof gebleken.**
Twee bezwaren, allebei op uitslagen gemeten:

1. **Het geldverlies op die kant is niet significant.** De −17.7% over 89 gevallen staat op
   **t = −1.39**. De kalibratiefout (z = −3.14) is hard; het rendement is dat niet. De halve markt
   afsluiten op een resultaat dat ruis kan zijn, is niet in verhouding.
2. **De vergelijkingsgroep in de tabel hierboven deugt niet.** "Alle overige picks, +1.2%" bestaat
   voor driekwart uit doelpuntenmarkten. De écht gespeelde **favorietenkant** telt maar 21 gevallen
   en verliest óók: −10.9%. En de +6.28u voor de favorietenkant is een **spiegelberekening met
   geschatte koersen**, geen waarneming. Er is dus nooit aangetoond dat de andere kant beter is —
   alleen dat markten zónder kant het minder slecht doen.

Wat wél standhoudt is dat de schade ongelijk over de underdogs ligt. Naar de marktkans van de
gespeelde selectie zelf:

| marktkans van de selectie | n | trefkans | rendement |
|---|---|---|---|
| < 25% (zware outsider) | 11 | 18.2% | −10.2% |
| **25–35%** | **18** | **16.7%** | **−44.4%** |
| 35–45% | 9 | 33.3% | −7.8% |
| 45–55% (bijna gelijk) | 38 | 44.7% | −12.1% |
| ≥ 55% | 13 | 53.8% | −10.5% |

**De poort sluit daarom vanaf nu alleen onder `sides.UNDERDOG_FLOOR` = 0.35.** Dat houdt 29 van de
89 gevallen tegen (samen −31.4%) en laat de zestig overige door, die op −11.1% staan — niet te
onderscheiden van de favorietenkant. De niet-monotonie in die tabel (de bak onder 25% doet het
béter dan 25–35%) is bij deze aantallen ruis, dus 0.35 is "ongeveer waar het misgaat", geen scherp
getal.

**Wat dit kost, en waarom het zo is afgewogen.** De zware versie schakelde driekwart van alle
bets-met-een-kant uit; op 5 sep leverde dat 311 doorgerekende selecties op de uitkomstmarkten en
nul bets op. De lichte versie houdt ongeveer een derde van de underdog-kant tegen. Dat is minder
bescherming, maar het is ook minder bescherming tegen iets waarvan niet vaststaat dát het beschermd
moest worden.

**De belangrijkste reden dat het lichter kán, staat in §1g.** `my_prob` loopt sinds 5 sep door
`recalibrate.py`, dat de scheefstand van bijna tien procentpunt er op uitslagen af haalt. Die
correctie pakt de oorzaak aan waar deze poort een symptoom van afdekte, en er komen daardoor
sowieso veel minder underdog-selecties door de edge-poort. **Zet de herijking ooit uit, dan moet
deze poort weer zwaarder.**

**Dit is een tijdelijke maatregel met een einddatum.** Elke tegengehouden kandidaat gaat als
`failed_gate = "underdog"` naar `data/shadow.jsonl` en wordt daar net zo afgerekend als een echte
pick, precies zoals §6d dat voor de andere zeven poorten doet. **Herzien uiterlijk 25 september
2026.** Hij gaat eruit zodra één van beide waar is: het schaduwlogboek laat zien dat hij
structureel winnaars tegenhoudt (positieve ROI over ≥ 30 afgewikkelde kandidaten), óf de
kalibratie op de underdog-kant staat weer recht. Het echte werk blijft de rekenfout zelf — welke
stap maakt de mindere ploeg te sterk; §6e wijst richting `shrink`, maar `shrink = 0.8` is op
3 sep juist op Brier-score gemeten en goed bevonden, en die spanning moet eerst worden opgelost.

### 1f. De twee methodes wegen 80/20, niet 50/50 (gewijzigd 5 sep 2026)

```python
from scripts.model import combine_probs
my_raw = combine_probs(p_xg, p_split)      # = 0.80 * p_xg + 0.20 * p_split
```

Tot 5 sep was dit het **ongewogen** gemiddelde, en dat was nooit ergens op gebaseerd — het stond zo
in de eerste versie van deze regels en is daarna nooit tegen uitkomsten gelegd. §1d en §6e wezen de
splitsmethode al aan als de scheefste van de twee, maar dat was gemeten tegen de **markt** en mag
daarom hooguit een diagnose heten (§2).

Nu op **uitslagen** gemeten, over 392 afgerekende gevallen (155 gespeelde picks plus 237
tegengehouden kandidaten). Brier tegen de werkelijke uitkomst, lager is beter:

| gewicht xG | 0.0 | 0.3 | 0.5 (oud) | 0.7 | **0.8** | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|
| Brier | .24415 | .23934 | .23737 | .23638 | **.23625** | .23637 | .23674 |

Drie dingen die erbij horen:

1. **De curve is vlak tussen 0.7 en 1.0.** Ga hier niet op fijnregelen; 0.80 is ongeveer waar het
   optimum ligt, geen scherp getal.
2. **De splitsmethode voegt als kansbron vrijwel niets toe** — alleen xG is met .23674 nauwelijks
   slechter dan de beste mix. Ze blijft wél staan als **veto**: poort 5 eist dat beide methodes de
   markt dezelfde kant op verslaan, en die poort bespaart aantoonbaar geld (§6d). Meerekenen voor
   een vijfde, meebeslissen over ja/nee — dat is de rol.
3. **Dit maakt het model beter, niet goed.** Zie §1g.

### 1g. De herijking op uitslagen (toegevoegd 5 sep 2026)

```python
from scripts.recalibrate import load_fit, apply
fit     = load_fit()             # één keer per run
my_prob = apply(my_raw, fit)
```

**Waarom dit er is.** Over 552 afgerekende gevallen zegt het model gemiddeld 51.0% en gebeurt het
41.1% van de tijd — bijna tien procentpunt te optimistisch, en altijd dezelfde kant op. De
gemiddelde geclaimde edge is +9.7 pp. Het "voordeel" dat de routine meet is dus grotendeels haar
eigen fout, en wie selecteert op de grootste edge, selecteert op de grootste modelfout. Dat is ook
de verklaring voor de anomalie in §1e: een hógere drempel maakte de underdog-kant slechter in
plaats van beter.

**Waarom dit mag en de correctie van 31 aug niet mocht.** Die ingetrokken instructie mat de
afwijking tegen de **de-vigde marktkans**; dan hangt je kans af van de koers waartegen je hem
afzet en meet `edge_pp` niets meer (§2). Deze correctie meet tegen de **werkelijke uitslag**, en
een uitslag weet niet wat de prijs was. Dat is het hele onderscheid, en het is precies de route die
§1d zelf aanwijst: *"herzie hem op uitkomsten, niet op een redenering."*

**Uit-steekproef gecontroleerd.** Gefit op de eerste helft van de periode (196 gevallen t/m 28 aug)
en getest op de tweede helft, die bij het fitten geen rol speelde:

| | ruw | herijkt |
|---|---|---|
| ongewogen gemiddelde (oud) | .25624 | .24771 |
| 0.8/0.2-weging (nu) | .25343 | **.24741** |
| **de markt** | | **.23950** |

**Lees die onderste regel.** Ook herijkt en met de betere weging schat de bookmaker scherper dan
het model — en dat is nog een gunstige vergelijking, want in zijn getal zit zijn eigen marge, die
zijn score juist slechter maakt. Zolang die regel zo staat is elk gemeten voordeel eerder modelfout
dan marktfout, en is **"vandaag niets" op de meeste dagen het juiste antwoord, geen defect**. De
herijking maakt de routine eerlijker over wat ze weet; ze maakt haar niet winstgevend.

#### Wat de herijking blootlegt, en waarom je de drempel NIET moet verlagen

De drempel van 8.0 pp in §0 is op **ongecorrigeerde** kansen gemeten. Na de herijking gaat er
ongeveer tien procentpunt van elke schatting af, en dan komt er vrijwel niets meer boven de 8 uit.
Op de wedstrijden van 5 sep 2026: **zes bets onder de oude regels, nul onder de nieuwe.**

De verleiding is dan om de drempel mee te verlagen. **Doe dat niet.** Het is nagerekend op alle 552
afgerekende gevallen, met de herijkte edge, en er is géén drempel die geld oplevert:

| drempel op de herijkte edge | bets | trefkans | ROI |
|---|---|---|---|
| ≥ 0 pp | 156 | 38.5% | −13.0% |
| ≥ 2 pp | 115 | 39.1% | −6.1% |
| ≥ 3 pp | 100 | 38.0% | −5.9% |
| ≥ 4 pp | 85 | 37.6% | −6.5% |
| ≥ 6 pp | 63 | 36.5% | −8.9% |
| **≥ 8 pp** | **45** | **31.1%** | **−14.7%** |

Lees vooral de onderste regel: bij de hóógste geclaimde edge is het rendement het **slechtst**. Dat
is dezelfde anomalie als in §1e, nu over het hele logboek en na correctie — een signaal dat
averechts werkt naarmate het sterker wordt, is niet zwak maar kapot. Er is dus geen drempel te
kiezen waarop deze routine winst maakt; er is alleen een keuze tussen weinig verlies en veel
verlies.

**Nul bets is daarmee niet het probleem maar het antwoord.** §1 zegt het al: bets forceren om het
format te vullen is verboden. Dit is de kwantitatieve versie daarvan. Zolang de bookmaker scherper
schat dan het model (§1g hierboven), is elk gepubliceerd voordeel eerder modelfout dan marktfout,
en is stil blijven de enige eerlijke uitkomst. Wat dit wél mag veranderen is de **ambitie**: de
routine is hiermee een meetinstrument dat netjes bijhoudt hoe goed ze is, en dat is iets anders dan
een systeem dat geld verdient. Wie dat wil omdraaien heeft betere invoer nodig, geen scherpere
filters — zie "Openstaand" in `runs/2026-09-05-run-a.md`.

Praktisch: onder `recalibrate.MIN_OBSERVATIONS` (150 afgerekende gevallen) wordt er niet herijkt en
gaat `my_prob` ongewijzigd door. De fit loopt mee met het logboek en wordt elke run opnieuw
bepaald — het is een bewegend getal, geen constante. Neem `recalibrate.py show` op in het
runrapport onder "Stand van het logboek".

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

Een handicap of totaal met push is geen gewone kans — bij een push komt de inzet terug — dus
`asian_prob` geeft de kans terug die bij díe koers dezelfde verwachtingswaarde oplevert, zodat
`edge_pp` en alle acht poorten er ongewijzigd op werken. Gebruik voor markten met push dus altijd
`asian_prob` / `dnb_prob` / `totals_prob` en nooit de kale winkans, anders staan de markten niet op
dezelfde schaal en is de rangschikking hieronder betekenisloos.

### 1d. De splitsmethode is multiplicatief (gewijzigd 23 aug 2026)

`analyze_match_from_splits` deed tot 23 aug `lambda = (aanval + verdediging) / 2`: twee
doelpuntgemiddeldes optellen en door twee delen. Dat is geen sterktemodel maar een gemiddelde, en
**middelen trekt naar het midden**. Omdat `my_prob` het ongewogen gemiddelde van deze methode en de
xG-methode is, sloeg die samendrukking door in elke gepubliceerde kans: over 165 waarnemingen
(22–23 aug) gaf de splitsmethode longshots +6.61 pp meer kans dan de markt en favorieten −11.86 pp
minder. Dat is de rekenkundige oorzaak van de 89% picks op de zwakkere kant uit §1c.

Geef daarom **altijd `league=` mee**. De methode rekent dan met verhoudingen tegen het
competitiegemiddelde, net als `analyze_match`, en beide schatters van §1 staan op dezelfde
grootheid — precies wat §6e als remedie aanwees. Gemeten op de 25 duels van 23 aug:

| | longshots | favorieten | gem. abs. fout |
|---|---|---|---|
| additief (t/m 22 aug) | +6.02 pp | −11.02 pp | 6.23 pp |
| **multiplicatief** | **+4.09 pp** | **−7.38 pp** | **5.61 pp** |

**Regresseer de splits niet — dat is geprobeerd en het werkt averechts.** Twee varianten zijn
gebouwd en gemeten: een vaste credibiliteitsweging `n/(n+9.5)` gaf +5.53 / −10.09, en een netjes
uit de competitiespreiding gemeten Bühlmann-credibiliteit (Z = 0.36 tot 0.76) gaf +6.09 / −11.11 —
slechter dan doen alsof er geen ruis is. Dat is geen toeval: regressie naar het gemiddelde ís de
samendrukking. Ze duwt elke wedstrijd richting "de ploegen ontlopen elkaar niet veel", en tegen een
markt die favoriet en underdog wél scheidt komt dat er als schijnedge op de zwakke kant uit. Ruis in
de invoer is een echt probleem, maar regresseren is er niet het antwoord op. Zie de docstring van
`analyze_match_from_splits` voor de volledige tabel.

**Wat hiermee níet is opgelost.** De scheefstand is kleiner, niet weg (+4.09 pp op longshots), en
het aandeel picks op de zwakkere kant bleef op de duels van 23 aug vrijwel gelijk (83% → 86%; in
absolute aantallen 10 → 6).

> **Ingetrokken op 31 aug 2026.** Hier stond tot die datum: *"zodra de longshotbak ~150
> waarnemingen heeft, hoort de gemeten afwijking van `my_prob` te worden afgetrokken vóórdat
> `edge_pp` wordt bepaald."* Die instructie is fout en moet **niet** worden uitgevoerd. Op 31 aug
> stond de longshotbak op 243 waarnemingen en is hij nagerekend; er kwamen twee bezwaren uit, en
> allebei zijn ze fataal:
>
> 1. **Hij is circulair.** De afwijking in §6e is gemeten tegen de **de-vigde marktkans**, niet
>    tegen uitkomsten. Trek je hem van `my_prob` af, dan hangt je kansschatting per definitie af
>    van de koers waartegen je hem afzet — precies wat §2 verbiedt. Dat §6e "meten tegen de markt
>    om te zien of de correctie werkt mag wel — dat is controleren, niet fitten" toestaat, maakt
>    het omgekeerde niet waar.
> 2. **Hij werkt de verkeerde kant op.** De correctie verhóógt de edge bij alles wat de markt
>    boven de 50% zet, want daar staat het model juist ónder de markt (−3.99 pp, n=125). Op de
>    tien duels van Run A op 31 aug zat géén van de acht bets in de longshotbak — ze lagen
>    allemaal tussen 47% en 61% marktkans — en de correctie zou elke edge hebben opgeblazen
>    (Sønderjyske +1.5 van +20.3 naar +24.3 pp) en er een negende bet bij hebben gemaakt. Een
>    regel die is bedoeld om te temperen en in de praktijk versoepelt, is geen voorzichtige regel.
>
> Wat de kalibratiereeks van §6e wél is en blijft: een **diagnose**, geen correctiefactor. Ze
> beantwoordt "staat het model scheef ten opzichte van de markt, en waar" — nuttig om te weten
> welke rekenstap de scheefstand veroorzaakt (§1d: de splitsmethode, niet `shrink`). Ze is geen
> getal om van je eigen kans af te trekken.
>
> Wat er in plaats daarvan is gebeurd, is de drempelverhoging in §0: gemeten op **uitkomsten**
> (179 afgewikkelde picks) in plaats van op de markt, en daarmee vrij van bezwaar 1. Dat is het
> antwoord op dezelfde vraag — "mijn geclaimde edge is te ruim, wat doe ik eraan" — via de enige
> maatstaf die geen bookmaker in zich heeft.

### 1a. Waar de prijzen vandaan komen — creditbudget (vastgesteld 15 aug 2026)

The Odds API is de gratis Starter met **500 credits per maand**. Op 15 aug verbruikten Run A en
Run B samen **132 credits op één dag** — een kwart van de maand — doordat alle zes markten voor het
eerst echt werden doorgerekend. Op dat tempo is het budget in twee dagen op, en een run zonder
prijzen levert per definitie nul bets. Daarom ligt vanaf nu vast wélke bron welke markt levert:

| Markt | Bron | Kosten |
|---|---|---|
| **1X2 — beste prijs** | `oddsapi.fetch_bulk(key, ["h2h","spreads","totals"])` | 1 credit per competitie |
| **1X2 — marktgemiddelde** | `betexplorer.fetch_league_fixtures(url)` | **gratis** |
| **Asian Handicap** | de `spreads` uit diezelfde bulk-aanroep | 1 credit per competitie |
| **Draw No Bet** | de **0.0**-lijn uit diezelfde `spreads` | **gratis, zit er al in** |
| **Double Chance** | de **±0.5**-lijn uit diezelfde `spreads` | **gratis, zit er al in** |
| Over/Under | de `totals` uit diezelfde bulk-aanroep | 1 credit per competitie |
| BTTS | `oddsapi.fetch_event_markets(...)` | 2 credits per wedstrijd |

### 1X2 op de beste prijs, niet op het marktgemiddelde (gewijzigd 5 sep 2026)

**Waarom dit is omgedraaid.** Tot 5 sep stond hier het omgekeerde, met dit argument: *"Ga niet
alsnog een h2h-bulkcall doen om dat recht te trekken: dat kost precies de 8 credits per run die
deze paragraaf bespaart."* Dat klopte — op het **500-creditplan**. Sinds 30 aug 2026 is het plan
20.000 credits per maand, en op 5 sep gebruikte Run A er 61 van een plafond van 381. Het argument
is dus niet fout maar verlopen, en het hield ondertussen de betrouwbaarste winst tegen die er te
halen is.

**Wat het oplevert, gemeten op 5 sep 2026** over 51 selecties in de Premier League en de
Championship:

| | |
|---|---|
| beste prijs t.o.v. het marktgemiddelde | **+7.78%** (mediaan +6.07%) |
| idem, na 2% beurscommissie | +6.89% |
| idem, zonder beurzen — alleen gewone bookmakers | +5.63% |
| **wat dat in edge doet** | **+1.84 procentpunt per selectie** |

Bijna twee procentpunt edge, gratis, op een drempel van 8.0 — dat is een kwart van de drempel
zonder één regel aan het model te veranderen. Dit is geen beter model maar **beter uitbetaald
krijgen voor hetzelfde model**, en dat is de enige verbetering in dit hele bestand waarvan de
omvang vooraf vaststaat.

**Reken altijd met `oddsapi.net_price`.** In 61% van de gevallen stond de beste prijs bij een
**beurs** (Betfair, Matchbook), en daar gaat commissie van je nettowinst af. De kale prijs is dan
niet de prijs die je krijgt: 3.00 bij 2% commissie is effectief 2.96. Wie dat overslaat overschat
zijn edge structureel — het scheelt hierboven bijna een vol procentpunt (+7.78% ruw tegen +6.89%
netto). Noteer bij de pick de kale prijs, de boeknaam **en** of het een beurs is.

**BetExplorer blijft, voor twee dingen die niet over de prijs gaan.** Verwar die twee rollen niet
en voeg ze niet samen:

1. **Het kalibratieblok van §6e** meet het model tegen het **marktoordeel**, en dat is het
   consensusgemiddelde over alle boeken — niet de gunstigste uitschieter. Blijf daar het
   BetExplorer-gemiddelde de-viggen.
2. **Poort 8** bepaalt wie de markt de mindere ploeg vindt. Dat is ook een oordeel en geen prijs;
   ook daar het gemiddelde.

Voor de **bet zelf** — `edge_pp`, `selection_score`, de gepubliceerde koers — geldt de beste prijs
na commissie. Kort: gemiddelde om te *meten*, beste prijs om te *spelen*.

**Voor competities zonder sportkey blijft BetExplorer de enige 1X2-bron.** Noteer dan bij de pick
dat het een marktgemiddelde is en dat de bookmaker niet herleidbaar is, precies zoals voorheen.

### Eén credit levert drie markten, niet één (gemeten 29 aug 2026)

`fetch_spreads` is de enige aanroep die voor **één** credit **drie** van de zes markten levert, en
dat is geen schatting maar een identiteit in de uitbetaling:

```
asian_prob(grid,  0.0, "home", odds) == dnb_prob(grid, "home", odds)     # AH 0.0  = Draw No Bet
asian_prob(grid, +0.5, "home", odds) == p.dc_1x  (bij dezelfde koers)    # AH +0.5 = Double Chance 1X
asian_prob(grid, +0.5, "away", odds) == p.dc_x2                          # AH +0.5 = Double Chance X2
```

Een handicap van +0.5 wint bij winst **en** bij gelijkspel — dat ís Double Chance; een handicap van
0.0 geeft bij gelijkspel de inzet terug — dat ís Draw No Bet. Nagerekend op het scoregrid komen ze
tot op zes decimalen uit.

**Dit betekent dat §1a stap 2 tot 29 aug 2026 geld weggooide.** Double Chance werd daar apart
gekocht via `fetch_event_markets`, à **2 credits per wedstrijd**, terwijl dezelfde bet voor
1 credit per héle competitie in de spreads-respons zat. De meting van 15 aug die DC en BTTS op
"30 credits per bet" zette, mat dus niet dat DC weinig oplevert — ze mat dat DC via de duurste
mogelijke weg werd ingekocht. Koop Double Chance nooit meer los; lees hem uit de ±0.5-lijn.

Bij het rapporteren: noem de bet zoals hij bij de bookmaker heet. Een +0.5 die je als Double
Chance publiceert, noteer je als `Double Chance` met de handicaplijn erbij in `notes`, zodat de
gebruiker hem terugvindt op de site waar hij hem speelt.

Gebruik **`fetch_league_fixtures`**, niet `fetch_league_odds`: die tweede leest de "Next matches"-
tabel en die toont er maar vijf. Op 15 aug had de Championship acht duels; drie zouden zonder 1X2
zijn gebleven. De fixtures-pagina geeft ze alle acht — gemeten op alle acht competities van die dag,
32 van de 32 wedstrijden gedekt, nul credits.

**Bepaal aan het begin van de run je plafond, verdeel het, en houd je eraan:**

```python
from scripts.oddsapi import CreditGuard, suggest_cap, split_budget
cap = suggest_cap(remaining_uit_api_check, dagen_tot_de_maandwissel)   # 2 runs per dag
n_spreads, n_totals = split_budget(cap, len(comps_met_sport_key))
guard = CreditGuard(cap=cap)
```

**Verdeel vóórdat je uitgeeft — de doelpuntenmarkt is een reservering, geen restpost**
(toegevoegd 30 aug 2026, op verzoek van de gebruiker). `split_budget` legt vooraf vast hoeveel
competities `spreads` krijgen en hoeveel `totals`. De volgorde van uitgeven verandert niet —
spreads blijft stap 0 — maar het aantal ligt vast in plaats van dat de doelpuntenmarkt krijgt wat
er toevallig overblijft.

Waarom dat nodig was: aan het begin van de maand is het plafond groter dan het aantal competities
en blijft er vanzelf geld over voor `totals`. Aan het eind van de maand niet. Op **30 aug 2026**
gaf `suggest_cap(68, 2)` een plafond van 12 bij elf inkoopbare competities; "zoveel mogelijk"
betekende toen elf keer spreads en één credit over, dus de doelpuntenmarkt dong mee in **één van
de twaalf** competities. De marktbalans-controle hieronder werd gehaald, maar met de kleinst
mogelijke marge — en dat is de spiegel van 29 aug, toen negen van de elf competities alleen een
doelpuntenmarkt hadden en 12 van de 14 bets uit die ene markt kwamen. Beide keren was de scheve
uitkomst de inkoop en niet de analyse. Met `split_budget(12, 11)` → `(9, 3)` wordt dat 9 om 3.

Geef de credits daarna uit in deze volgorde, en stop zodra `guard.can_afford(...)` False geeft:

0. **De bulk-aanroep eerst, voor `n_spreads` competities** (3 credits per competitie: h2h +
   spreads + totals). Dit was tot 5 sep 2026 alleen `spreads` à 1 credit; sindsdien gaan
   `h2h` en `totals` in dezelfde aanroep mee, omdat het budget dat ruimschoots toelaat en de
   beste 1X2-prijs +1.84 pp edge oplevert (zie hierboven). Eén aanroep levert nu **vijf van de
   zes markten**: 1X2 op de beste prijs, Asian Handicap, Draw No Bet (de 0.0-lijn), Double Chance
   (de ±0.5-lijn) en Over/Under.

   ```python
   from scripts.oddsapi import fetch_bulk
   for comp in comps_op_datakwaliteit[:n_spreads]:
       if guard.can_afford(3):
           guard.record(fetch_bulk(sport_key[comp], ["h2h", "spreads", "totals"]), comp)
   ```

   **Bij een krap plafond valt de bulk terug op het oude gedrag.** Kun je geen 3 credits per
   competitie betalen, koop dan `spreads` en `totals` los zoals hieronder en laat `h2h` vallen —
   BetExplorer levert dan het gratis marktgemiddelde. `split_budget` rekent nog met 1 credit per
   competitie, dus deel het plafond in dat geval zelf door drie voordat je het erin stopt, en
   noteer in het runrapport dat de beste prijs deze run niet is opgehaald.
1. **`totals` los** (1 credit per competitie) voor de `n_totals` competities die **vandaag aan de
   beurt zijn** in de rotatie — alleen nog nodig voor competities die in stap 0 buiten de
   bulk-aanroep vielen; wie de bulk kreeg heeft zijn doelpuntenmarkt al binnen:

   ```python
   from scripts.oddsapi import rotate_for_day
   vandaag_aan_de_beurt = rotate_for_day(comps_op_datakwaliteit, date.today(), take=n_totals)
   ```

   Roteren en niet altijd dezelfde nemen: steeds de bovenste vier pakken betekent dat de andere
   structureel nooit een doelpuntenmarkt krijgen. Dat is precies de stille blinde vlek die §6b-5b
   moest wegnemen.

   **Bij een plafond van 1 credit gaat die ene credit naar `totals`, niet naar `spreads`** —
   `split_budget(1, n)` geeft `(0, 1)`. Dat is geen afrondingsfout. Asian Handicap, Draw No Bet en
   Double Chance zijn alle drie **uitkomstmarkten**, net als het gratis 1X2; een run die alleen
   spreads koopt heeft dus geen enkele doelpuntenmarkt en faalt de marktbalans-controle hieronder.
   Drie markten voor één credit is hier minder wáárd dan één markt die de enige van zijn soort is.
2. `btts` per wedstrijd (2 credits) **alleen als er daarna nog credits over zijn** — in de praktijk
   dus zelden. Double Chance staat hier met opzet níet meer bij: die zit sinds 29 aug in stap 0.

### Waarom deze volgorde op 29 aug 2026 is omgedraaid

Van 23 t/m 29 aug stond `totals` bovenaan en `spreads` in de rotatie. De aanleiding was goed — van
de eerste 113 picks ging 78% over de uitkomst tegen 22% over doelpunten, terwijl de doelpuntenmarkten
beter renderden (ROI −10.5% tegen −19.9%) — maar de remedie sloeg door naar de andere kant. Op
29 aug kocht Run A `totals` voor alle elf competities en `spreads` voor twee, en het resultaat was
**12 van de 14 bets op Over/Under**. De gebruiker noemde dat "weer te eenzijdig", en terecht: dit is
niet de analyse die spreekt maar de inkoop.

De rekensom die de omkering afdwingt:

| Aanroep | Kosten | Markten eruit | Markten per credit |
|---|---|---|---|
| `fetch_totals` | 1 | OU | **1** |
| `fetch_spreads` | 1 | AH + DNB + DC | **3** |
| `fetch_event_markets(["double_chance","btts"])` | 2 **per wedstrijd** | DC + BTTS | ~0,1 |

Met `spreads` bovenaan heeft élke competitie vier markten (1X2, AH, DNB, DC) in plaats van twee
(1X2, OU), en de rotatie zorgt dat de doelpuntenmarkt om de dag terugkomt in plaats van de
handicapmarkt. Dat de doelpuntenmarkten beter renderen blijft staan; het antwoord daarop is niet
"koop alleen doelpunten" maar "zorg dat alle zes de markten kúnnen meedingen en laat
`selection_score` kiezen".

**Marktbalans is vanaf nu een controle op de inkoop, niet op de uitkomst.** Geen enkele run mag
voor de hele runlijst maar één soort markt kopen. Concreet: als `guard` klaar is, moet gelden dat
er minstens één competitie met een doelpuntenmarkt én minstens één met een uitkomstmarkt in de
run zit — is dat niet zo, dan is het plafond te krap voor deze runlijst en meld je dat in het
runrapport. Sinds 30 aug 2026 zorgt `split_budget` daar vooraf voor in plaats van achteraf: die
controle hoort dus altijd te slagen, en slaagt hij níet, dan is er iets mis met de verdeling en
niet alleen met het plafond. Meld ook **hoe ruim** hij slaagt — één competitie met een
doelpuntenmarkt op twaalf is iets anders dan drie op twaalf, en dat verschil is van buitenaf
alleen te zien als je het opschrijft.
Noteer per run in `data/run-state/` onder `credits` de verdeling `markten_gekocht`,
en in het runrapport de verdeling van de gepubliceerde bets over doelpunten- en uitkomstmarkten.
Dat is geen quotum op bets — bets forceren om een verdeling te halen is precies wat §1 verbiedt —
maar het maakt zichtbaar wanneer een scheve uitkomst uit de portemonnee komt en niet uit de data.

Een markt die je door het plafond niet hebt opgevraagd is **bekeken met een reden**, niet een gat:
noteer hem in `markets_checked` als `"BTTS": "niet opgevraagd — creditplafond van de run bereikt"`.
Zo blijft `progress.py verify` groen zonder dat de administratie liegt. Neem `guard.report()` op in
het runrapport onder "Bronstatus deze run".

**De scheve vergelijking die dit oploste (historie, sinds 5 sep 2026 verholpen).** Zolang 1X2 van
BetExplorer kwam en de handicaps van The Odds API, stond de uitkomstmarkt op een **marktgemiddelde**
tegenover een **beste prijs**. Een 1X2 verloor daardoor de `selection_score` van een handicap ook
als hij in werkelijkheid beter was, en het runrapport moest dat elke keer als "mogelijk artefact van
de prijsbron" vermelden. Sinds de bulk-aanroep hierboven staan alle markten op dezelfde voet en is
die waarschuwing niet meer nodig.

Wat er wél blijft: **voor een competitie zonder sportkey is BetExplorer nog steeds de enige
1X2-bron.** Noteer daar `odds_source` als marktgemiddelde met het aantal boeken erbij, vermeld dat
de bookmaker niet herleidbaar is, en houd er rekening mee dat de edge daar systematisch te laag
uitvalt — conservatief, dus geen risico op te veel bets, maar niet vergelijkbaar met een duel waar
de beste prijs wél bekend is. Meld in het runrapport welke competities in die categorie vielen.

### Welke markt je publiceert: `selection_score`, hoogste wint

Dezelfde onderliggende inschatting levert vaak op vier tot zeven markten tegelijk een edge op.
Gemeten op Viborg – AGF (14 aug 2026): 1X2 +17.6 · AH +0.5 +15.5 · DNB +15.2 · Double Chance +12.2 ·
AH +1.0 +8.8 · Over 2.5 +5.1 · BTTS ja +3.0. Dat zijn geen zeven bevindingen maar **één, zeven keer
uitgedrukt**. De 0-of-1-bet-regel blijft dus onverkort gelden: "de sterkste" betekent één selectie
per wedstrijd, niet één per markt.

Welke van die uitdrukkingen je publiceert, is **vastgesteld op 14 aug 2026 op verzoek van de
gebruiker** en niet langer aan de run:

```python
from scripts.model import selection_score
selection_score(edge_pp, my_prob, data_tier)      # = edge_pp × my_prob × (FULL 1.0 | LIGHT 0.5)
```

Van alle selecties die **alle acht de poorten** halen, publiceer je die met de hoogste score. Dit is
dezelfde formule als bij de topselectie in §5 — één weegregel voor beide, zodat de bet die je kiest
en de plek die hij in de shortlist krijgt niet uit elkaar kunnen lopen.

Waarom deze en niet een andere. Er waren vier redelijke lezingen van "Edge × Probability ×
Data-betrouwbaarheid", en op de wedstrijden van 14 aug wezen ze niet dezelfde kant op:

| Lezing | Viborg – AGF | Cercle – St.Truiden | Telstar – Sparta |
|---|---|---|---|
| hoogste edge in procentpunten | 1X2 | 1X2 | 1X2 |
| **Edge × kans, letterlijk (gekozen)** | **AH +0.5** | **AH +0.25** | **1X2** |
| hoogste rendement per euro | 1X2 | 1X2 | 1X2 |
| grootste Kelly-inzet | AH +0.5 | AH +0.25 | 1X2 |

Tot die datum deed de routine feitelijk de eerste, zonder dat ooit te hebben opgeschreven. De
gekozen regel geeft de voorkeur aan een hogere trefkans boven een paar procentpunt extra edge. Dat
is een keuze over risicobereidheid — die hoort bij de gebruiker en niet bij de data — maar er is
één inhoudelijk argument dat dezelfde kant op wijst: de bekende zwakte van dit model (het kent geen
competitiesterkte) verschuift kansmassa tussen *winst* en *gelijkspel*. Een 1X2 is daar maximaal
gevoelig voor, want een gelijkspel is dan puur verlies; een handicap +0.5 of een Draw No Bet is er
ongevoelig voor, want daar wordt een gelijkspel gewonnen of teruggegeven. Zolang die fout er is,
kiest deze regel dus ook de minst blootgestelde uitdrukking van dezelfde mening.

**Het gewicht 0.5 voor LIGHT is afgeleid, niet gekozen:** het is `EDGE_THRESHOLD_FULL /
EDGE_THRESHOLD_LIGHT` = 8.0 / 16.0 (tot 31 aug 2026: 3.0 / 6.0). Zwakke data moet al twee keer zoveel edge opleveren om mee te
mogen doen; diezelfde verhouding bij het rangschikken houdt de twee met elkaar in de pas.

Noteer in het runrapport bij elke gepubliceerde bet **welke selectie tweede werd en met welke
score**. Zonder dat is niet na te gaan of deze weegregel iets doet, en dan staan we over een maand
weer waar we op 14 aug stonden.

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
git rev-parse --is-shallow-repository        # ZIE HIERONDER — doe dit eerst
git fetch --unshallow origin || git fetch origin
git branch -r
for b in $(git branch -r | grep -v HEAD); do
  echo "$b: $(git rev-list --count HEAD..$b) commits die hier nog niet zijn"
done
```

**Haal eerst de volledige geschiedenis op, anders meet je iets anders dan je denkt.** De container
krijgt de repo als **ondiepe kloon** aangeleverd (`--is-shallow-repository` → `true`, en dat was op
20 aug 2026 opnieuw zo, in een verse container). Bij een ondiepe kloon ontbreekt alles van vóór de
knip, en dus ook het punt waar twee takken uit elkaar zijn gegaan: `git merge-base main <tak>` geeft
**niets** terug en `rev-list --count HEAD..<tak>` telt élke commit van vóór de knip als "nog niet
hier". Het resultaat is een vals alarm dat er precies uitziet als het echte geval van 10 aug —
takken met tientallen "eigen" commits die er in werkelijkheid allemaal al in zitten.

Zo zag dat er op 20 aug 2026 uit, dezelfde repo, vóór en na één commando:

| | ondiep (60 commits lokaal) | na `--unshallow` (109 commits) |
|---|---|---|
| takken met "eigen" commits | 7 van de 15 (3 t/m 39 stuks) | **0 van de 15** |
| `merge-base` met `main` | leeg | gewoon een commit |

Kost dit één extra opdracht per run, dan is dat het waard: zonder die stap doet elke run opnieuw
het handwerk van 19 en 20 aug (per tak de picks, de runrapporten en de scripts vergelijken) om
uiteindelijk vast te stellen dat er niets te mergen viel. Blijkt ná het unshallowen dat er tóch
takken met eigen commits zijn, dan is dat het echte geval en geldt alles hieronder onverkort.

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
maatregel begint de volgende poging weer bij wedstrijd 1 — met een cap van 30 tot 35 duels is dat
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

```bash
python3 scripts/ledger.py open     # wat mag er af? beslist op de status van de bron (§0)
python3 scripts/shadow.py open     # dezelfde regel, dezelfde module
```

Beide geven per regel de reden erbij ("bron meldt afgelopen — 3 - 0" of "bron meldt nog niet
afgelopen"). Werk ze bij via `scripts/ledger.py settle` en `scripts/shadow.py settle`. **Wikkel de
echte picks en de schaduwpicks in dezelfde run af** — dat ze uiteenliepen is precies waar de
statusregel van §0 voor is gemaakt.

Reken 1X2, Double Chance, Draw No Bet, O/U en BTTS af op de stand **na 90 minuten inclusief
blessuretijd** (§6d), ook al meldt de bron een latere eindstand. Blessuretijd telt dus gewoon mee —
een doelpunt in de 90+4' is een doelpunt; wat niet meetelt is verlenging en strafschoppen. Zonder deze stap is de kwaliteit van de routine niet meetbaar.

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

Rangschik de overgebleven wedstrijden en neem de top `MAX_DEEP_ANALYSES` mee naar de diepe analyse
(30 op ma–do, 35 op vr–zo). Noteer expliciet hoeveel wedstrijden hierdoor zijn afgekapt —
**stille truncatie is verboden**; een afgekapte lijst leest anders als volledige dekking.

```python
from scripts.ranking import max_deep_analyses, data_richness, sort_key
from scripts import squad
```

De sortering heeft vier sleutels, in deze volgorde:

1. **datakwaliteit** — `FULL` boven `LIGHT` boven `NONE`. Onveranderd, dit blijft de primaire regel.
2. **datarijkdom** — `ranking.data_richness(...)`, zie hieronder.
3. **aantal beschikbare markten** — bij gelijke informatie krijgt het duel waar vier markten om de
   publicatie kunnen strijden de plek, boven een duel waar er maar één ligt. Dit is een eigenschap
   van de *prijs* en niet van de kansinput, en staat daarom achteraan.
4. **aftrap**, zodat de volgorde reproduceerbaar is.

#### De datarijkdom-score (ingevoerd 29 aug 2026, op aanwijzing van de gebruiker)

Tot deze datum was de tie-break binnen `FULL` het aantal speeldagen dat de **competitie** dit
seizoen al gespeeld had. Dat criterium is op 29 aug afgeschaft omdat het bijna niets meet: de
teamsterktes komen bij álle competities uit het volledige vorige seizoen, en het aantal speeldagen
van dit seizoen gaat alleen de gepoolde vroeg-seizoenscorrectie in — die is competitie-overstijgend.
Het gevolg die dag was dat de **hele Bundesliga** (vier duels met volledige dekking) uit de run
viel omdat die competitie pas één speeldag had gespeeld. De gebruiker noemde die regel nutteloos,
en dat is hij ook: hij gooide vier analyses weg op een getal dat aan die vier analyses niets
verandert.

De vervangende vraag is: **hoe goed beschrijft wat ik weet, deze twee ploegen vandaag?** Dat is te
meten, en het kost geen credits — alles komt gratis van Fotmob:

| Onderdeel | Punten | Bron |
|---|---|---|
| **selectiecontinuïteit** | 0–3 | `squad.turnover(team_id, squad_value)` — transfers sinds 1 juni, gewogen op marktwaarde. Een ploeg die de helft van zijn selectiewaarde heeft omgezet, wordt door de cijfers van vorig seizoen slechter beschreven dan een ploeg die intact bleef. |
| **opstelling** | 0–2 | `lineupType`: bevestigd (2) boven voorspeld (1) boven niets (0). |
| **blessures/schorsingen** | 0–2 | het opstellingsblok bestaat voor beide ploegen, dus poort 7 kan werkelijk werken. Een lege uitvallerslijst telt als informatie, niet als gat. |
| **vorm en rust** | 0–2 | `matchFacts.teamForm`: een reeks van ≥ 3 duels én bekende rustdagen, per ploeg. |
| **lopend seizoen** | 0–1 | de duels die **déze twee ploegen** dit seizoen al speelden — een teammaat, geen competitiemaat. |

**Ontbrekende metingen krijgen het middenpunt, nooit nul.** Een meting die er niet is, is geen
bewijs van een probleem — dezelfde regel als bij poort 7 (§1c). Een wedstrijd waarvan de context
niet op te halen was, zakt daardoor niet stilletjes naar de achterkant van de lijst.

**De gewichten zijn niet gefit, en dat staat er met opzet bij.** Er is geen enkele meting die zegt
hoeveel een bevestigde opstelling waard is ten opzichte van een lage transferomzet. Wat de score
wél doet, is de rangschikking baseren op gemeten aanwezigheid van *actuele* informatie in plaats
van op een proxy die met de wedstrijd niets te maken heeft. Leg de score en de deelscores per duel
vast in `data/run-state/` onder `datarijkdom`, en noem in het runrapport de score van de laagste
wedstrijd die het nog haalde en van de hoogste die afviel — zonder die twee getallen is niet na te
gaan of de afkapping ergens op sloeg.

**Haal de context dus vóór de afkapping op, niet erna.** Dat is een Fotmob-verzoek per kandidaat
en kost geen credits. Doe je het pas na de afkapping, dan rangschik je opnieuw op iets dat je niet
gemeten hebt.

**Gebruik `scripts/fotmob.py`, `scripts/betexplorer.py`, `scripts/oddsapi.py`, `scripts/xgscore.py`,
`scripts/context.py`, `scripts/squad.py`, `scripts/ranking.py` en `scripts/model.py` voor
Stage 3-5** in plaats van de ophaal- en rekenlogica opnieuw te schrijven.
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

**Twee onafhankelijke xG-bronnen sinds 31 aug 2026.** Naast Fotmob levert
`scripts/understat.py` team-xG voor vijf competities (PL, La Liga, Bundesliga, Serie A, Ligue 1),
gratis en zonder sleutel. Dat is er niet om `my_prob` te veranderen — dat blijft het gemiddelde van
de twee methodes uit §1 — maar om drie dingen:

- **Redundantie.** Tot 31 aug kwam élke kansinput van Fotmob. Viel die om, dan faalde §2 voor elke
  wedstrijd en leverde elke run nul bets. Nu niet meer, voor de competities waar het meeste omgaat.
- **Een echt onafhankelijke tweede bron in `prob_sources`.** Fotmob-xG en Fotmob-splits zijn twee
  doorsnedes van dezelfde meting; Understat is een ander xG-model.
- **Rollende xG over de laatste 5–8 duels** (`understat.rolling_xg`). Dat staat hieronder al vanaf
  het begin als categorie-1-input, maar er was geen bron voor — Fotmob geeft alleen seizoenstotalen.

Let op één gemeten verschil vóór je ze door elkaar gebruikt: **Understat ligt structureel ~0.13 xG
per ploeg per duel hoger dan Fotmob** (gemeten 31 aug 2026 over alle vijf competities: 1.529 tegen
1.398 in de PL, 1.501 tegen 1.354 in La Liga, enzovoort), terwijl beide exact dezelfde doelpunten
geven. Dat is een niveauverschil tussen twee xG-modellen, geen meningsverschil over welke ploegen
goed zijn. Het valt weg zodra je normaliseert op het **eigen** competitiegemiddelde van die bron —
`understat.league_context()` geeft dat — maar meng nooit een Understat-teamsterkte met een
Fotmob-competitiegemiddelde, want dan telt dat verschil van 9% wél mee.

`p_xg_understat` gaat sinds 31 aug mee in het kalibratieblok (§6e), zodat over enkele weken met
cijfers te zeggen is of het ene xG-model beter voorspelt dan het andere. Pas dán is het een vraag
of `my_prob` erop moet worden aangepast; vandaag is het een meting, geen wijziging.

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

### Het lopende seizoen weegt mee (toegevoegd 3 sep 2026, op verzoek van de gebruiker)

Tot deze datum kwamen de teamsterktes **uitsluitend** uit het vorige seizoen. De routine wist in mei
dus precies evenveel over een club als in augustus: het lopende seizoen kwam alleen binnen als
competitiebreed doelpuntenniveau (`early_season_uplift`), en dat is een correctie die juist
*uitdooft*. Er zat geen enkel mechanisme in dat met de tijd bijleerde over ploegen.

Bouw de teamsterkte daarom altijd zo op:

```python
from scripts.model import blend_seasons, blend_weight
prior = TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"])       # vorig seizoen
cur   = TeamStats(xg=cr["xg"], xga=cr["xga"], matches_played=cr["mp"])    # lopend seizoen
stats = blend_seasons(prior, cur)        # gewicht_nu = n / (n + 8)
```

Op speeldag 1 verandert dit niets (gewicht 0), na 4 duels weegt het lopende seizoen voor eenderde
mee, na 8 duels even zwaar als het hele vorige seizoen. **Hierdoor wordt de analyse vanzelf beter
naarmate het seizoen vordert**, zonder dat er iets aan de knoppen hoeft.

**`k` stond van 3 t/m 5 sep 2026 op 16 en is toen op verzoek van de gebruiker op 8 gezet.** Dat is
een stap wég van het gemeten optimum en dat hoort er eerlijk bij te staan. Exact nagemeten op
dezelfde backtest (1263 duels, 2025/26):

| | alleen vorig seizoen | k=16 (optimum) | **k=8 (nu)** | alleen dit seizoen |
|---|---|---|---|---|
| Brier | 0.61761 | **0.61269** | 0.61331 | 0.62396 |

k=8 houdt daarmee **87%** van de winst die blenden überhaupt oplevert. De prijs is reëel maar
klein, en er staat iets tegenover dat deze backtest niet kán meten: hij draait op één testseizoen
in vijf grote competities met stabiele selecties. Bij een ploeg die in de zomer half is omgebouwd —
en daar zitten de promovendi en de kleinere competities vol mee — is "reageer sneller op wat je dit
seizoen ziet" een argument dat niet in deze cijfers zit. Wie k terugzet naar 16 heeft de meting aan
zijn kant; wie hem op 8 laat kiest voor sneller bijleren tegen 13% van de blendwinst. Beide zijn
verdedigbaar, geen van beide is gratis.

De volledige tabel en de uit-steekproefcontrole staan in de docstring van `blend_seasons`.

Drie dingen die je moet weten voordat je hieraan sleutelt:

1. **Blenden, niet omschakelen.** Alleen het lopende seizoen gebruiken is *slechter* dan alleen het
   vorige. De winst zit in het wegen.
2. **De winst groeit mee met het seizoen** — bij 25+ gespeelde speeldagen is hij vier keer zo groot
   als vroeg in het seizoen (+0.0116 in-steekproef, +0.0112 uit-steekproef). Dat is het hele punt.
3. **Het is een bescheiden effect.** De blend is beter in 51% van de wedstrijden, niet in 60%
   (in-steekproef t=+2.11, uit-steekproef t=+1.71). Verwacht er geen ommekeer van.

Dit is géén regressie naar het competitiegemiddelde — dat is geprobeerd en werkte averechts (§1d).
Twee steekproeven van dezelfde ploeg tegen elkaar wegen trekt een ploeg niet naar het midden maar
naar zijn eigen recentere cijfers.

**De splitsmethode blijft op vorig seizoen.** Die heeft thuis/uit-doelpunten nodig en die zijn voor
het lopende seizoen pas laat betrouwbaar; met vier thuisduels is een thuis/uit-splitsing ruis.

**`shrink` hoeft niet af te lopen** — ook gemeten: `shrink=0.8` verslaat `shrink=1.0` bij elke waarde
van k. Daarmee is de openstaande vraag daarover in §6e beantwoord: laten staan.

Leg per doorgerekend duel in `data/run-state/` onder `seizoensweging` vast hoeveel duels er dit
seizoen meetellen, met welk gewicht, en de xG per duel vorig/dit/gewogen. Zonder dat is niet na te
gaan of de weging deed wat ze hoort te doen.

### Promovendi: eerst omrekenen, dan pas `NONE` (toegevoegd 30 aug 2026)

Een ploeg die niet in de tabel van vorig seizoen staat, is bijna nooit een ploeg zonder historie —
hij heeft die historie alleen in de divisie eronder. Reken hem daarom eerst om, en zet hem pas op
`NONE` als dat aantoonbaar niet kan:

```python
from scripts.promotion import convert, TIER2, PromotionError
c = convert("Eredivisie (NED)", "ADO Den Haag", "2025/2026", league)   # league ná scale_level
c.tier      # "LIGHT" binnen het gemeten bereik, "NONE" erbuiten — nooit FULL
c.stats, c.splits, c.note
```

`scripts/promotion.py` haalt de stand van de divisie eronder bij **Fotmob** (dertien
divisieparen in `TIER2`, alle dertien op naam en land geverifieerd) en rekent hem om met
`convert_strength` uit `scripts/footballdata.py`. Welke factor daarbij hoort, bepaalt
`gap_and_range()` in drie stappen:

1. het gemeten divisiepaar bij football-data.co.uk (E0/E1, SP1/SP2, D1/D2, I1/I2, F1/F2, SC0/SC1);
2. anders `promotion.MEASURED_TIER2_GAP` — **zelf gemeten op 31 aug 2026** over de seizoenen
   2016/2017 t/m 2024/2025, op Fotmob, voor NED, DEN, POR, BEL, TUR en POL;
3. en pas als laatste `POOLED_GAP`.

Na stap 2 draait geen enkele competitie uit de runlijst nog op een gepoolde factor. Dat was tot
31 aug wél zo, en het was geen detail: op 30 aug leverde de gepoolde factor de grootste edge van
de run op (ADO Den Haag +2.5 bij Feyenoord, +23.6 pp). De meting bevestigde Nederland grotendeels
(0.614/1.564 tegen 0.605/1.513 gepoold) maar corrigeerde **Denemarken** duidelijk: de
verdedigingsfactor is daar 1.807 in plaats van 1.513, oftewel een Deense promovendus incasseert
fors meer dan de gepoolde factor aannam.

**Meet zo'n gat nooit met een soepele naamvergelijking.** De eerste poging koppelde `Jong Ajax` aan
`Ajax` en `Jong FC Utrecht` aan `FC Utrecht` — beloftenelftallen spelen permanent in de Eerste
Divisie en promoveren nooit — en dat gaf een "promovendus behoudt zijn aanval"-factor van 1.010.
`measure_gap` eist daarom exacte of genormaliseerd-exacte namen, en `find_team` accepteert een
afkorting alleen als **voorvoegsel** (`Ipswich` op `Ipswich Town` wel, `Ajax` op `Jong Ajax` niet).

Aanleiding: op 30 aug 2026 kregen vier duels `NONE` — Feyenoord – ADO Den Haag, Willem II – SC
Heerenveen, Cambuur – FC Twente en Lyngby – OB — omdat football-data.co.uk de Eerste Divisie en de
Deense 1. Division niet dekt. Fotmob heeft die divisies wél, met doelpunten en thuis/uit-splits
voor alle vier de ploegen. Er was dus geen datagat maar een bronngat, en het kostte vier analyses.

Twee dingen die hier blijven gelden:

- **`conversion_in_range` is een poort, geen aantekening.** Buiten het gemeten bereik is er geen
  meting, dus geen onafhankelijke kansinput op het niveau waarop gespeeld wordt: `NONE`, geen bet.
  Dat is de Coventry-val uit de docstring van die functie, en hij kost anders +21 pp schijnedge die
  alle andere poorten haalt.
- **Een omgerekende ploeg is nooit `FULL`.** `RESIDUAL_SPREAD` houdt na correctie nog ~0.16
  relatieve sterkte over. De omrekening haalt de systematische fout eruit, niet de onzekerheid.

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

Rangschik alle gepubliceerde bets op **Edge × Probability × Data-betrouwbaarheid**, met dezelfde
formule waarmee je in §1 de markt binnen een wedstrijd hebt gekozen:

```python
from scripts.model import selection_score
selection_score(edge_pp, my_prob, data_tier)      # = edge_pp × my_prob × (FULL 1.0 | LIGHT 0.5)
```

Eén weegregel voor beide, zodat de selectie die je publiceert en de plek die hij in de shortlist
krijgt niet uit elkaar kunnen lopen. Zet de score in de tabel, zodat de volgorde na te rekenen is
in plaats van te geloven.

Geef de top `MAX_SHORTLIST`, met per bet: Probability • Edge • Score • Risicoklasse
(Low/Medium/High) • waarom deze wél en de eerstvolgende net niet. Maximaal
`MAX_LIGHT_IN_SHORTLIST` bets met `LIGHT`.

**Deze topselectie hoort óók op de HTML-pagina van §6c, niet alleen in het markdown-runrapport.**
Dat is toegevoegd op 22 aug 2026, op verzoek van de gebruiker, nadat hij hem in beide dagrapporten
miste. En terecht: `report.py` rendert de bets sinds zijn bestaan ongeordend onder elkaar en deed
niets met het `shortlisted`-veld dat wél in `picks.jsonl` staat — `grep -c shortlisted scripts/report.py`
gaf 0. Op een dag met dertien bets bleef daarmee precies de vraag onbeantwoord die de gebruiker
stelt: welke zou ik nou spelen. `render_shortlist()` doet dat nu, en `rank_picks()` zet ook de
bets zelf op scorevolgorde, zodat de twee rapporten van dezelfde run niet uiteen kunnen lopen.

Het opgeslagen `shortlisted`-veld is daarbij leidend, want dat is het besluit van de run zelf
(inclusief `MAX_LIGHT_IN_SHORTLIST`). **Zet dat veld dus goed** — staat het op elke pick `false`,
dan valt de pagina terug op de bovenste `MAX_SHORTLIST` op score en gaat `MAX_LIGHT_IN_SHORTLIST`
verloren. `report.py` leidt de dagsoort zelf af uit de datum (`max_shortlist()`: 3 op ma–do, 5 op
vr–zo), dus die hoeft nergens te worden meegegeven.

**Risicoklasse is iets anders dan score, en dat blijft zo.** De score rangschikt; de risicoklasse
waarschuwt. Een bet kan bovenaan staan én High risico zijn — dat was op 14 aug het geval bij AGF,
waar de markt 18 procentpunt afweek van het model. Vervang het een niet door het ander.

Zijn er minder gekwalificeerde bets dan `MAX_SHORTLIST`? Lever er minder. **Vul niet aan.**

### Marktbalans — verplicht, elke run (toegevoegd 29 aug 2026)

Zet onder de topselectie een tabel met **welke markten er te koop waren en wat eruit kwam**:

| Markt | Competities met prijzen | Selecties doorgerekend | Bets |
|---|---|---|---|
| 1X2 | 11 van 11 (gratis) | 33 | … |
| Asian Handicap · DNB · Double Chance | … | … | … |
| Over/Under | … | … | … |
| BTTS | 0 — niet opgevraagd | 0 | 0 |

Reden: op 29 aug 2026 kwamen 12 van de 14 bets uit één markt, en de gebruiker las dat — terecht —
als een eenzijdige analyse. Het was geen analyse maar inkoop: `Over/Under` was in negen van de elf
competities de enige betaalde markt. **Zonder deze tabel is dat verschil van buitenaf niet te
zien**, want het runrapport toont alleen wat eruit kwam. Twee bets uit één markt op een dag dat
alleen die markt te koop was, is iets heel anders dan twee bets uit één markt op een dag dat alle
zes meededen.

Dit is een rapportageplicht, geen quotum. Als alle zes markten meedingen en er komt toch een
eenzijdige lijst uit, dan is dat de uitkomst — bets forceren om een verdeling te halen is precies
wat §1 verbiedt.

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

**Is de beste prijs van een beurs** (Betfair, Matchbook, Smarkets, Betdaq), zeg dat er dan bij en
noem beide getallen: de genoteerde koers en de koers na commissie. `edge_pp` en `selection_score`
rekenen met de koers ná commissie (`oddsapi.net_price`); de gebruiker ziet op de site de koers
ervóór, en zonder die twee naast elkaar klopt het rapport niet met wat hij op zijn scherm heeft.
Zo bijvoorbeeld: *"Betfair 3.55 (na 2% commissie 3.50)"*.

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
5c. **Kalibratielogboek** → een `calibration`-blok per doorgerekende wedstrijd in
   `data/run-state/`, en daarna `python3 scripts/calibration.py collect --run <a|b> --date <datum>`.
   Zie 6e; neem `calibration.py stats` op in het runrapport.
5d. **Contextlogboek** → `python3 scripts/ctxlog.py collect --run <a|b> --date <datum>`, gevolgd
   door `ctxlog.py settle`. Dit vraagt om een contextblok bij **elke** wedstrijd waarvoor de context
   is opgehaald, dus ook bij de duels die `MAX_DEEP_ANALYSES` heeft afgekapt. Zie §1c; neem
   `ctxlog.py stats` op in het runrapport.
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
**plus blessuretijd**), nooit op de eindstand na verlenging of strafschoppen. Om elk misverstand weg
te nemen: een doelpunt in de 90+4' telt gewoon mee — blessuretijd is onderdeel van de reguliere
speeltijd. Alleen verlenging (91–120') en strafschoppen tellen niet mee. Bij bekerduels en
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

Draai daarna `python3 scripts/ledger.py stats` **en `python3 scripts/recalibrate.py show`** en
neem hit rate, ROI, Brier score en de stand van de herijking (§1g) op in het runrapport. Die laatste
is elke run een ander getal — hij loopt mee met het logboek — en zonder hem is niet na te gaan met
welke correctie een pick van die dag is gepubliceerd. Dit is de enige manier waarop "gaat het goed of niet" een antwoord met een getal krijgt.

### 6e. Het kalibratielogboek — zit het model systematisch scheef?

`ledger.py` meet of de bets winnen en `shadow.py` of de poorten iets tegenhouden. Geen van beide
beantwoordt de vraag daaronder: **staat `my_prob` als schatter systematisch scheef, en waar?**

Op 22 aug 2026 bleek dat te kunnen. Run A publiceerde die dag dertien bets, en nameten liet zien dat
het niet dertien vondsten waren maar grotendeels één afwijking: over de dertig doorgerekende duels lag
het model **+4.19 pp boven** de de-vigde marktkans op uitkomsten die de markt onder de 25% zet, en
**−6.67 pp eronder** bij favorieten. Tien van de dertien bets lagen daardoor in dezelfde hoek.

De uitsplitsing wees bovendien een andere oorzaak aan dan verwacht. Niet `shrink`:

| | longshots (<25%) | favorieten (>50%) |
|---|---|---|
| `analyze_match` bij `shrink = 1.0` | **+0.47 pp** | **+0.55 pp** |
| `analyze_match_from_splits` | **+5.75 pp** | **−9.87 pp** |

De xG-methode is vlak; de afwijking komt vrijwel volledig uit de splitsmethode. En dat is
rekenkundig: `analyze_match` **vermenigvuldigt** sterkteverhoudingen, terwijl
`analyze_match_from_splits` twee doelpuntgemiddelden **optelt en door twee deelt**. Middelen trekt
naar het midden — gemeten gebruikte de splitsmethode 62% van de spreiding in verwacht doelsaldo van
de xG-methode. Dat slijt dus niet naarmate het seizoen vordert; het is geen vroeg-seizoenseffect.

Omdat `my_prob` het **ongewogen gemiddelde** van die twee is, komt de helft van elke gepubliceerde
kans uit een structureel samengedrukte schatter. Dat is een reden om te meten, nog niet om te
verbouwen — één dag is geen bevinding (§6d). Daarom, **elke run**:

```bash
python3 scripts/calibration.py collect --run <a|b> --date YYYY-MM-DD
python3 scripts/calibration.py stats
```

Leg daarvoor per doorgerekende wedstrijd een `calibration`-blok in `data/run-state/` vast, met de
**de-vigde** marktkans en de modelkansen voor de drie 1X2-uitkomsten:

```json
"calibration": {
  "market":        [0.45, 0.27, 0.28],
  "p_xg":          [0.41, 0.28, 0.31],
  "p_xg_noshrink": [0.43, 0.28, 0.29],
  "p_split":       [0.38, 0.29, 0.33],
  "p_xg_understat":[0.42, 0.28, 0.30]
}
```

`scripts/calibration.devig(odds)` doet het wegdelen. 1X2 is met opzet de meetmarkt: die is via
BetExplorer elke run gratis en voor vrijwel elke wedstrijd beschikbaar, en de drie uitkomsten
sommeren tot 1. `p_xg_noshrink` is één extra `analyze_match(..., shrink=1.0)` per wedstrijd en kost
dus vrijwel niets — zonder dat veld is het aandeel van `shrink` niet te scheiden van dat van de
splitsmethode. Neem de uitvoer van `stats` op in het runrapport, naast `ledger.py stats` en
`shadow.py stats`.

**Lees dit net zo voorzichtig als 6d, en lees het als diagnose.** Onder ~150 waarnemingen in de
longshotbak (ruwweg vijf volle rundagen) is een paar procentpunt ruis.

**Dit blok is géén correctiefactor.** Zie de ingetrokken instructie in §1d: de afwijking die hier
gemeten wordt is er een ten opzichte van de **markt**, en die van `my_prob` aftrekken maakt je
kansschatting een afgeleide van de odds (§2). Waar dit blok wél voor is: uitzoeken wélke rekenstap
de scheefstand veroorzaakt. Dat heeft het ook opgeleverd — de xG-methode is vlak, de splitsmethode
niet (§1d) — en dat is een bevinding waar je iets aan kunt repareren zonder de markt binnen te
halen. Wil je weten of je geclaimde edge te ruim is, meet dan tegen **uitkomsten**: dat is wat de
drempelverhoging van 31 aug in §0 doet.

Wat hier nog openstaat: de splitsmethode is sinds 23 aug multiplicatief en op het
competitiegemiddelde genormaliseerd (§1d) maar nog steeds de scheefste van de twee.

**De `shrink`-vraag is op 3 sep 2026 beantwoord en staat niet meer open.** Hier stond tot die datum
dat `shrink` "hard op 0.8 staat zonder afloopmechanisme terwijl de docstring hem met vroeg seizoen
verantwoordt". Dat vermoeden — hij zou met het seizoen moeten aflopen — is nagemeten in de backtest
bij `blend_seasons` (§4) en klopt niet: `shrink=0.8` verslaat `shrink=1.0` bij élke waarde van de
credibiliteitsconstante, ook laat in het seizoen. Er hoeft dus geen afloopmechanisme te komen. Wat
wél ontbrak was iets anders, en dat is nu opgelost: niet de mate van regressie moest met het seizoen
mee bewegen, maar de **cijfers waarop hij wordt toegepast** — die kwamen tot 3 sep uitsluitend uit
het vorige seizoen.

Let ten slotte op wat poort 6 hier **niet** doet: het `(shrink, rho)`-grid van `robustness_check`
varieert alleen `analyze_match` — precies de methode die vlak blijkt. "Deze bet overleeft het hele
grid" zegt dus niets over de methode die de afwijking veroorzaakt.

### 6c. Het leesbare dagrapport — verplicht, elke run

Het markdown-runrapport hierboven is voor de repo: methode, metingen, bronstatus. De gebruiker
leest dat niet, en had daar gelijk in — het opent met bronstatus, gebruikt `edge_pp`, "de-viggen"
en Brier zonder uitleg, en de bets staan als twee regels tussen alle andere wedstrijden. Daarom
levert elke run **ook** een HTML-pagina op:

1. Schrijf `runs/YYYY-MM-DD-run-<a|b>.prose.json` — alleen de tekst die een mens moet schrijven:
   `verdict`, `bets` (per pick-id een `why` in gewone taal + een risicozin), `coverage_notes`,
   `todo`, `finding` en `settled`. Zie `runs/2026-08-09-run-a.prose.json` als voorbeeld.
   Gebruik voor `risk_level` **`low` / `med` / `high`**; `report.py` normaliseert sinds 22 aug 2026
   ook `medium`, `laag`, `gemiddeld` en `hoog`, maar tot die datum leverde het verschil tussen
   Run A's `med` en Run B's `medium` stilzwijgend een chip zonder kleur op.
2. Draai `python3 scripts/report.py --run <a|b> --date YYYY-MM-DD`. Bets, dekkingstabel en de
   stand van het logboek komen automatisch uit `picks.jsonl` en `data/run-state/` — niet
   overtypen, want dan gaan de twee rapporten uiteenlopen.
3. Publiceer het bestand als Artifact en **zet die link in de notificatie** (§7).

Schrijf de prose voor iemand die de repo niet kent en het jargon niet spreekt. Geen `edge_pp`,
geen "de-viggen", geen ρ of shrink: die staan in de woordenlijst onderaan de pagina en horen niet
in de lopende tekst. Noem bedragen, tijden en bookmakers concreet.

Ook bij **nul bets** draait dit. De pagina zegt dan met zoveel woorden dat er niets gekwalificeerd
heeft, en de dekkingstabel laat zien dat er wél gekeken is. Dat is precies het geval waarin een
lege notificatie de gebruiker in het ongewisse laat — en sinds 17 aug 2026 gaat er bij nul bets dus
ook echt een notificatie uit, met deze pagina eraan (§7).

---

## 7. Wanneer een notificatie sturen

De run draait terwijl niemand meekijkt; wat alleen in het transcript staat, bereikt niemand.

**Elke run stuurt precies één notificatie. Altijd, ook bij nul bets, ook als er niets bijzonders
is gebeurd.** Geen uitzonderingen, geen afweging — de afweging gaat alleen over de *inhoud*, niet
over het wel of niet sturen. Dit is een wijziging van 17 aug 2026; de reden staat onderaan deze
paragraaf en is belangrijk genoeg om te lezen voordat je hem terugdraait.

Zet in **elke** notificatie de link naar de HTML-pagina uit §6c. Dat is de plek waar de gebruiker
het hele verhaal kan lezen, en zonder die link is de melding een dood bericht.

### Welke vorm

**Zijn er bets** — leid met de beste: markt en selectie, de koers, de bookmaker, de aftraptijd in
NL-tijd. Dan het aantal overige bets, dan de link. Geen methodediscussie; die staat op de pagina en
in het markdown-rapport.

> Beste bet vandaag: Sønderjyske +1.25 @ 1.94 (Pinnacle), aftrap 20:00. Nog 2 andere bets in de
> selectie. Hele verhaal: <link>

**Zijn er geen bets** — dan is dit een hartslag: kort, feitelijk, en het moet er ondubbelzinnig in
staan dat de run *gedraaid* heeft. Noem het aantal wedstrijden dat je bekeek, hoeveel er door de
datadekkingspoort kwamen, en in één halve zin waaróm er niets kwalificeerde.

> Run B gedraaid, 0 bets. 9 wedstrijden, 1 met datadekking; die viel af op robuustheid. Bronnen
> allemaal in orde. <link>

**Is er iets mis** — een afgewezen sleutel, een omgevallen bron, een geweigerde push, een run die
niet op `main` staat, een afwikkelingsreeks die opvalt (5+ verliezers) — dan gaat dat **vooraan**,
vóór de bets of de hartslag. Dit is het enige geval waarin de notificatie langer mag zijn dan drie
regels: noem wat er stuk is en wat de gebruiker eraan kan doen.

Meer dan één notificatie per run is niet de bedoeling. Heb je zowel bets als een blokkade, zet ze
in hetzelfde bericht — blokkade eerst.

### Waarom dit is veranderd (17 aug 2026, op verzoek van de gebruiker)

Tot vandaag stond hier het omgekeerde: géén notificatie bij "een routinematige, gezonde run zonder
gekwalificeerde bets". De bedoeling was de aandacht van de gebruiker te sparen, en op zichzelf is
dat een goed doel. Maar de regel had een gat dat niemand had gezien: **een gezonde run met nul bets
en een run die nooit is afgegaan, zien er van de telefoon af precies hetzelfde uit.** Beide zijn
stilte.

Dat is geen theoretisch bezwaar. Run B stuurde op 11, 12, 13 en 17 aug 2026 geen notificatie, elke
keer correct volgens de oude regel, elke keer met een gepubliceerd dagrapport dat de gebruiker niet
wist te bestaan. Op 17 aug was de eerste vraag van de gebruiker na die vier dagen: *"Why did run b
didn't run this morning?"* — terwijl hij die ochtend om 05:11 gedraaid had, negen wedstrijden had
bekeken, alle zes markten had doorgerekend en drie commits naar `main` had gepusht. De routine had
vier dagen lang niet te onderscheiden gezwegen van een kapotte scheduler.

De winst van de nieuwe regel zit niet in het bericht zelf maar in wat stilte nu betekent: zolang er
elke run één melding komt, is **een uitgebleven melding zelf het signaal** dat er iets stuk is.
Onder de oude regel was die informatie er niet, en kon de gebruiker een defect alleen ontdekken
door in de repo te gaan kijken.

De kosten zijn eerlijk te noemen: dit is één extra bericht per dag per run op dagen dat er niets te
melden valt. Dat is precies wat de oude regel wilde voorkomen. De afweging is bewust die kant op
gemaakt — een melding die de gebruiker één seconde kost weegt niet op tegen dagen waarin hij niet
weet of zijn routine nog leeft. Draai dit niet terug zonder de vier dagen hierboven mee te wegen.

---

## 8. Wat deze regels expliciet níet oplossen

De bronnen zijn nog steeds grotendeels dichtgezet (zie `data/source-health.json`). Zolang er geen
API-key beschikbaar is, zullen veel competities in `BUITEN DATADEKKING` blijven vallen en zullen
runs vaak nul bets opleveren. Dat is de eerlijke uitkomst van de huidige input, niet een defect
in deze regels. De structurele fix staat in `README.md` onder "Nog te doen".
