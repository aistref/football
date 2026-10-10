"""Bevinding 3 bijschrijven in `data/run-state/2026-10-10-run-b.json`.

Apart script en geen tweede `--schrijf`: die zou de picks nog een keer aan
`data/picks.jsonl` toevoegen. Dit raakt alleen het `parameters`-blok.

De bevinding is tijdens Stage 6 gevonden, bij het narekenen van `ctxlog.py collect`: dat
voegde 25 van de 77 wedstrijden toe terwijl alle 77 een contextblok hebben. De EERSTE
lezing was "Fotmob heeft op deze runlijst geen marktwaardes", en die is bij het
narekenen onjuist gebleken — zie de kruistabel in de tekst hieronder. Het is grotendeels
een TIJDSEFFECT, en dat verandert de remedie volledig.
"""
import json
from pathlib import Path

PAD = Path("data/run-state/2026-10-10-run-b.json")
state = json.loads(PAD.read_text())

state["parameters"]["BEVINDING_3_TWEEDERDE_VAN_DE_DAG_KOMT_HET_CONTEXTLOGBOEK_NIET_IN_EN_DE_OORZAAK_IS_DE_KLOK"] = (
    "Gevonden bij het narekenen van Stage 6, en het raakt de meting waar §1c zijn hele "
    "opzet op bouwt. `ctxlog.py collect` voegde vandaag 25 van de 77 wedstrijden aan het "
    "contextlogboek toe, terwijl ALLE 77 een contextblok in data/run-state hebben. Dat is "
    "geen overgeslagen stap: `_rows_from_state` eist een meetbaar aandeel ontbrekende "
    "selectiewaarde aan BEIDE kanten (`out_share`), en dat bestaat alleen als Fotmob een "
    "`squad_value` voor die ploeg geeft. 90 van de 154 ploegzijden (58%) hebben "
    "squad_value 0 of ontbrekend, dus vallen 52 van de 77 duels af. "
    "DE OORZAAK IS NIET DE COMPETITIE MAAR DE KLOK, en dat is het hele punt van deze "
    "bevinding. De eerste lezing was 'tweede divisies hebben bij Fotmob geen "
    "marktwaardes', wat zou volgen uit het competitiepatroon (Serie B 6 van 6 onmeetbaar, "
    "Czech First League 4 van 4, 2. Bundesliga 4 van 4, English League Two 10 van 12). "
    "Die lezing is onjuist. De kruistabel van lineup_type tegen squad_value zegt iets "
    "anders: "
    "lineup_type 'unavailable' 52 ploegzijden, ALLE 52 met squad_value 0; 'standard' 6, "
    "alle 6 op 0; leeg/ontbrekend 14, alle 14 op 0; 'lastStarting11' 78 ploegzijden "
    "waarvan 60 MET waarde en 18 zonder; 'predicted' 4, alle 4 met waarde. Met andere "
    "woorden: zodra er een opstelling is, is er in 64 van de 82 gevallen ook een "
    "marktwaarde. Het probleem zit bij de 72 ploegzijden waar om 05:10 NL nog helemaal "
    "geen opstellingsblok staat — en dat is te verwachten bij een aftrap om 13:00 tot "
    "16:00, acht tot elf uur later. Dit bevestigt de lezing die Run B op 9 oktober in "
    "source-health.json zette ('oorzaak is timing') en weerlegt de competitielezing; de "
    "18 ploegzijden met wél een opstelling en toch geen waarde zijn de rest, en die groep "
    "is klein. "
    "WAAROM DIT MEER IS DAN EEN VOETNOOT. §1c heeft op 5 september gemeten dat er geen "
    "effect van ontbrekende spelers te vinden is, en de uitweg die daar is opgeschreven is "
    "EEN GROTERE STEEKPROEF: 'door élke wedstrijd met context te loggen in plaats van "
    "alleen de doorgerekende worden het er ruim honderd per dag, en is de vraag over drie "
    "tot vier weken beantwoordbaar.' Die rekensom gaat uit van élke wedstrijd. Hij levert "
    "vandaag een derde daarvan, en die drie tot vier weken zijn inmiddels vijf weken "
    "voorbij: het logboek staat op 1001 wedstrijden (943 afgewikkeld) en de drempel voor "
    "een aantoonbaar effect ligt nog op ~19 pp per eenheid, met het model op t = -1,12 en "
    "de markt op t = -1,07. De reeks groeit dus wél, maar langzamer dan §1c aanneemt, en "
    "de reden is nu bekend en meetbaar in plaats van vermoed. "
    "WAT DE REMEDIE WEL EN NIET IS. Een tweede bron voor marktwaardes helpt hier NIET — "
    "het ontbrekende gegeven is de opstelling, niet de prijskaart. Wat wél zou werken is "
    "de context een tweede keer ophalen dichter bij de aftrap, maar dat botst rechtstreeks "
    "met §0: de rapporten moeten om 06:30 NL klaar staan omdat de gebruiker tussen 07:00 "
    "en 08:00 inzet, en de vroegste aftrap van vandaag was 13:00. Een run die op de "
    "opstellingen wacht, is te laat voor de inzet. Dat is geen gat in de code maar een "
    "echte spanning tussen twee eisen, en ze hoort als zodanig op tafel te liggen in "
    "plaats van als ontbrekende regel. Een derde weg is een gewicht dat niet op de "
    "opstelling leunt — speelminuten van dit seizoen per uitvaller, uit de Opta-respons "
    "die §4 beschrijft — maar dat is een nieuwe maat en geen aanpassing. Het staat als "
    "besluit bij de gebruiker. "
    "WAT ER VANDAAG NIET IS GEDAAN, EN WAAROM: `out_share` een nul laten teruggeven waar "
    "de waarde ontbreekt. Dat zou de 52 duels als 'niemand ontbreekt' in het logboek "
    "zetten en de regressie met een halve steekproef verzonnen nullen vervuilen — precies "
    "wat §1c verbiedt ('een meting die er niet is, is geen bewijs van een probleem'). "
    "VOOR DE POORT ZELF VERANDERT ER NIETS: bij een onmeetbaar aandeel staat poort 7 per "
    "definitie open (§1c, 'ontbrekende data laat de poort open'), dus er is geen bet door "
    "tegengehouden of doorgelaten die er anders niet was. Het is de MÉTING die hier "
    "ontbreekt, niet de rem."
)
state["parameters"]["CONTEXTLOGBOEK_DEZE_RUN"] = (
    "25 van de 77 wedstrijden toegevoegd; logboek staat op 1001, waarvan 943 afgewikkeld "
    "en 58 open. ctxlog.py settle wikkelde 0 af, en dat is juist: de 58 openstaande zijn "
    "de duels van vandaag van Run A en Run B, die nog niet gespeeld zijn. Zie BEVINDING_3 "
    "voor waarom het er 25 zijn en niet 77 — de oorzaak is de klok en niet de competitie."
)
PAD.write_text(json.dumps(state, ensure_ascii=False, indent=1))
print(f"bevinding 3 + contextlogboek bijgeschreven; {len(state['parameters'])} parameter-sleutels")
