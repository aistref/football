## Marktvorm — hoe vaak ging deze markt eerder op? (§4, toegevoegd 17 okt 2026)

Op verzoek van de gebruiker, en **ná** het publiceren van deze run. Dit blok is een **telling**
en het verandert niets: geen pick, geen `my_prob`, geen edge, geen rangorde en geen regel in
`data/picks.jsonl`. Een herberekening van 17 oktober geeft dus exact dezelfde vijf regels als de
run zelf gaf. Wat het wél doet is de vraag beantwoorden die bij elke doelpuntenbet hoort en die
tot vandaag onbeantwoord bleef: *hoe vaak gebeurde dit eerder?*

Geteld met `scripts/marketform.py` over uitsluitend **competitieduels** (dus zonder beker- en
Europese wedstrijden, anders dan de `WWDLW`-reeks uit `teamForm`), uit de competitierespons die
de run toch al ophaalt — nul extra credits.

| Bet | Ploeg | laatste 5 | dit seizoen | eigen kant | vorig seizoen | modelkans |
|---|---|---|---|---|---|---|
| **Under 3.5** @2.0600 | Strasbourg | 4/5 (80%) | 4/6 (67%) | 2/2 (100%) | 22/34 (65%) | 58.6% |
|  | Paris Saint-Germain | 3/5 (60%) | 3/6 (50%) | 2/4 (50%) | 23/34 (68%) |  |
| **Over 3** @1.7500 | Villarreal | 3/5 (60%) | 5/8 (62%) | 2/3 (67%) | 14/38 (37%) | 66.0% |
|  | Elche | 3/5 (60%) | 5/8 (62%) | 2/4 (50%) | 15/38 (39%) |  |
| **Under 3.5** @1.7200 | Union Berlin | 1/5 (20%) | 1/5 (20%) | 1/3 (33%) | 18/34 (53%) | 65.8% |
|  | Borussia Dortmund | 3/5 (60%) | 3/5 (60%) | 1/2 (50%) | 23/34 (68%) |  |
| **Over 2.5** @1.5978 | Motor Lublin | 3/5 (60%) | 6/10 (60%) | 2/5 (40%) | 17/34 (50%) | 74.9% |
|  | Śląsk Wrocław | 4/5 (80%) | 8/10 (80%) | 4/5 (80%) | *speelde deze divisie niet* |  |
| **Under 3.5** @1.4200 | Roma | 3/5 (60%) | 3/6 (50%) | 1/3 (33%) | 31/38 (82%) | 76.2% |
|  | Genoa | 4/5 (80%) | 5/6 (83%) | 2/2 (100%) | 32/38 (84%) |  |

De kolom is telkens **hoe vaak de gepubliceerde kant goed uitkwam**: bij een Under het aantal
duels ónder de lijn, bij een Over het aantal erboven. "eigen kant" is thuis voor de thuisploeg
en uit voor de uitploeg — de splitsing waarmee het model zelf ook rekent (§1d).

**Wat eruit te lezen is, en het is niet overal hetzelfde verhaal:**

1. **Roma – Genoa is de regel die de telling het sterkst steunt.** Beide ploegen bleven vorig
   seizoen in ruim tachtig procent van hun duels onder 3,5 doelpunt (31 van 38 en 32 van 38), en
   Genoa doet dat dit seizoen in vijf van de zes. Dat is de laagst-rangschikkende regel van de
   dag op `selection_score`, en op deze maat de best onderbouwde.
2. **Union Berlin – Borussia Dortmund is de regel waar de telling de bet tegenspreekt, en dat
   is de belangrijkste bevinding van dit blok.** Het model geeft Under 3,5 een kans van 65,8%,
   terwijl Union Berlin dit seizoen in **vier van de vijf** duels bóven 3,5 uitkwam, met
   gemiddeld **4,40** doelpunten per wedstrijd — het hoogste van alle tien ploegen op de lijst.
   Op de uitslagen van dit seizoen zou je rond de 40% uitkomen in plaats van 66%. Vijf duels is
   te weinig om de modelkans te overrulen (§6d eist ~30), maar ruim genoeg om het bij de bet te
   zetten — en dat staat nu vóóraan in de `why`-tekst van die regel.
3. **Villarreal – Elche leunt op het lopende seizoen en niet op een jaar.** Vijf van de acht
   duels boven 3,5 voor beide ploegen dit seizoen (62%), tegen 37% en 39% vorig seizoen. De
   modelkans van 66% past bij het eerste en niet bij het tweede.
4. **Śląsk Wrocław heeft geen vorig seizoen om naast te leggen**, want die speelde een divisie
   lager — `marketform` geeft daar `found = False` in plaats van een nul die als gemeten nul
   leest. Tien duels op dit niveau is alles wat er is, en acht ervan gingen boven 2,5.
5. **Strasbourg – Paris Saint-Germain: de telling zit aan de voorzichtige kant van het model.**
   Strasbourg bleef dit seizoen in vier van de zes onder 3,5 en thuis in beide duels. Wat
   ertegen pleit staat er ook: in álle vijf de laatste duels van Strasbourg scoorden beide
   ploegen. Het zijn dus 1-1- en 2-1-wedstrijden, en die vallen aan de goede kant van 3,5.

**En dit gaat niet in `my_prob`.** Een frequentie met een gewicht in de kansschatting stoppen zou
een getal verzinnen waarvoor geen meting bestaat (§2, §4) — dezelfde reden dat poort 7 een rem is
en geen bijstelling. Wie haar ooit wél wil meewegen, meet eerst op **uitkomsten** of ze de
Brier-score verbetert, zoals §1f voor de 80/20-weging heeft gedaan.
