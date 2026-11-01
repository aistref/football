# -*- coding: utf-8 -*-
import json

P = {}

P["_doc"] = [
 "Alleen de tekst die een mens moet schrijven (§6c). Bets, dekkingstabel, de 'Net niet'-tabel",
 "en de stand van het logboek komen uit picks.jsonl en data/run-state/ en staan hier dus NIET;",
 "report.py rendert die zelf. Overtypen is precies hoe de twee rapporten uiteen gaan lopen."
]
P["started"] = "03:05"
P["truncated"] = 0
P["sources"] = (
 "Wedstrijdkalender van Fotmob — twee daglijsten, plus per wedstrijd de opstellingen, de "
 "uitvallers met hun marktwaarde, de vorm, de rustdagen, de onderlinge historie, het stadion en "
 "het weer; prijzen van The Odds API (de beste prijs per uitkomst over 25 aanbieders) en van "
 "BetExplorer (het gemiddelde over alle boeken, dat ik gebruik om te meten en niet om op te "
 "spelen); een tweede, onafhankelijk xG-model van Understat voor de vijf grote competities; en "
 "de fixturepagina's van BetExplorer als tweede bron op de vraag wélke wedstrijden er vandaag "
 "zijn. Vandaag waren alle vier die bronnen in orde en was er geen enkele storing."
)
P["coverage_labels"] = {"GEANALYSEERD": "doorgerekend", "GEEN WEDSTRIJD": "speelt vandaag niet",
                        "BUITEN DATADEKKING": "geen bruikbare cijfers",
                        "AFGEKAPT": "buiten het dagbudget gevallen"}

P["verdict"] = (
 "Een rustige zondag na een volle zaterdag, en voor het eerst in drie dagen staan er niet alleen "
 "doelpuntenweddenschappen in de lijst. Zevenendertig wedstrijden in het venster waarin u kunt "
 "inzetten, verdeeld over elf competities, tegen een dagbudget van vijfenvijftig — er is dus "
 "niets afgekapt en ik heb alles doorgerekend. Serie A speelt vijf duels, La Liga, Ligue 1, de "
 "Eredivisie, de Primeira Liga, de Belgische competitie, de Süper Lig en de Deense Superliga elk "
 "vier, de Bundesliga twee, en de Premier League en de Schotse Premiership elk één. De "
 "Championship en de Poolse Ekstraklasa hebben vandaag geen ronde, de Champions League, Europa "
 "League en Conference League spelen dinsdag tot donderdag, en geen van de vijf bekers heeft een "
 "ronde. Dat laatste heb ik bij twee bronnen nagekeken en niet aangenomen.\n\n"
 "Er staan vijf weddenschappen in de lijst en twee ervan verdienen hun plek op eigen kracht: "
 "Juventus – Napoli en Kasımpaşa – Beşiktaş, beide op 'niet beide ploegen scoren', en bij beide "
 "zit mijn schatting ruim twaalf procentpunt boven wat de markt vraagt. De andere drie — Lyon – "
 "Angers, Getafe – Sevilla en Liverpool – Arsenal — staan erin omdat ze vandaag het beste zijn "
 "wat er is, niet omdat ik er een duidelijk voordeel in zie. Lees de lijst dus van boven naar "
 "beneden en niet als vijf gelijkwaardige tips; dat onderscheid staat bij elke regel.\n\n"
 "De vondst van vandaag is er een over werkwijze en niet over voetbal. Prijzen voor 'beide "
 "ploegen scoren' kosten mij geld per wedstrijd, dus ik koop die pas in een tweede ronde, voor de "
 "duels waar al iets te vinden lijkt. Vandaag veranderde die tweede ronde op béide topregels wat "
 "ik publiceer: voordat ik die prijzen had, stonden Juventus – Napoli en Kasımpaşa – Beşiktaş er "
 "als een weddenschap op weinig doelpunten, met een lagere waardering. Met de BTTS-prijzen erbij "
 "is dezelfde mening in een andere markt meer waard. Een run die die ronde zou overslaan om een "
 "paar centen te sparen, publiceert dus iets anders.\n\n"
 "En wat ik niet mooier maak dan het is: vier van de vijf regels hebben hun beste prijs bij "
 "Matchbook, een wedbeurs die 2% commissie op de winst rekent. De koers die u op de site ziet "
 "staan is daarom hóger dan de koers waarmee ik reken — bij elke regel staan beide getallen, en u "
 "hoeft zelf niets af te trekken."
)

P["settled_note"] = (
 "Gisteren was een goede dag, en hij was ook grotendeels een eerlijke. Van de tien weddenschappen "
 "van zaterdag gingen er zes goed en vier niet, en dat leverde ruim twee keer de inzet op winst "
 "op. Belangrijker dan die uitslag is of de wedstrijden liepen zoals ik ze had voorgerekend, en "
 "bij vier van de zes winnaars klopte dat tot op de halve goal: Middlesbrough – Charlton werd "
 "3–0 waar ik drie doelpunten verwachtte, Moreirense – Estrela 2–1 bij een verwachting van drie, "
 "Columbus Crew – DC United 3–0 bij bijna drie, en San Jose – Real Salt Lake 2–1 bij ruim drie. "
 "Dat zijn winsten op de juiste redenering en niet alleen op de juiste uitkomst.\n\n"
 "De vier verliezers zeggen meer. Drie van de vier waren doelpuntenweddenschappen die aan de "
 "verkeerde kant uitliepen, en twee daarvan waren 'weinig doelpunten': Kifisia – Olympiacos werd "
 "2–3 waar ik op ruim twee doelpunten zat, en Anderlecht – Westerlo 4–1 waar ik op drie zat. Over "
 "alle tien wedstrijden samen vielen er vijfendertig doelpunten tegen bijna dertig verwachte, "
 "een halve goal per wedstrijd te veel. Dat is precies het scheve beeld dat ik sinds oktober "
 "meet: op de weddenschappen waar ik zelf op 'weinig doelpunten' speel, vallen er gemiddeld "
 "tweederde goal per wedstrijd meer dan ik voorspel, nu over honderdvijftien gevallen. Dat is "
 "geen bevinding van gisteren maar een reeks die gisteren weer dezelfde kant op wees.\n\n"
 "De afgewezen kandidaten van zaterdag — de wedstrijden waar een poort de weddenschap "
 "tegenhield — deden het gisteren bijna net zo goed als de gespeelde: van de vierenzeventig "
 "gingen er negenendertig goed en eenendertig niet. Twee van die poorten houden me vooral van de "
 "winnaars af: de controle dat mijn twee rekenmethodes het eens zijn (dertien van achttien goed) "
 "en de drempel zelf (veertien van vierentwintig). Eén dag is geen reeks, en op achttien gevallen "
 "mag daar nog niets uit geconcludeerd worden; over de hele looptijd bespaart die eerste poort "
 "nog steeds geld. Maar het is de derde dag op rij dat hij driekwart van alles wegvangt, en dat "
 "is het soort cijfer dat ik in de gaten moet houden."
)

P["coverage_notes"] = {
 "Serie A (ITA)": (
  "De drukste competitie van de dag met vijf wedstrijden, en de competitie waar mijn beste "
  "weddenschap uit komt. Twee van de vijf duels hebben een ploeg die vorig seizoen een divisie "
  "lager speelde — Venezia en Frosinone — en bij zulke ploegen moet ik de cijfers eerst omrekenen "
  "voordat ik ze kan gebruiken. Dat lukte bij beide, maar het betekent wel dat ik daar een hogere "
  "lat aanleg, en geen van de twee kwam er in de buurt."
 ),
 "Premier League (ENG)": (
  "Eén wedstrijd, en wel de grootste van het weekend: Liverpool tegen Arsenal op Anfield. De rest "
  "van de ronde was zaterdag. Dat die ene wedstrijd in mijn lijst staat is dus geen voorkeur voor "
  "de topcompetitie maar simpelweg alles wat er vandaag te kiezen was."
 ),
 "Danish Superliga (DEN)": (
  "De enige competitie die al over de helft van zijn seizoen is — dertien van tweeëntwintig "
  "speeldagen — en daarom de enige waar ik het doelpuntenniveau uit dit seizoen haal in plaats van "
  "uit vorig jaar met een opslag. Vier wedstrijden, geen weddenschap. Bij Viborg – AC Horsens kon "
  "ik niets: AC Horsens kwam uit de divisie eronder en die omrekening valt buiten het bereik waarin "
  "ik haar heb gemeten, dus die wedstrijd heb ik niet doorgerekend in plaats van er een slag naar "
  "te slaan."
 ),
 "Primeira Liga (POR)": (
  "Vier wedstrijden waarvan twee met een promovendus (Académico Viseu en Marítimo), en één "
  "wedstrijd die om een andere reden afviel: bij Arouca – Nacional miste Nacional bijna een vijfde "
  "van de waarde van zijn selectie tegen zes procent bij de tegenstander, en dan houdt mijn "
  "blessurecontrole de weddenschap tegen. Dat is geen oordeel over de wedstrijd maar een rem die "
  "ik met opzet grof heb gehouden."
 ),
 "Championship (ENG)": (
  "Geen ronde vandaag; die was zaterdag met elf wedstrijden. Dinsdag speelt de competitie weer."
 ),
 "UEFA Champions League": (
  "Speelt dinsdag 3 november. De Europa League donderdag 4 en 5 november, de Conference League "
  "5 november. Vier van mijn vijf weddenschappen gaan over ploegen die binnen vijf dagen Europa "
  "in moeten, en dat weegt mee in de voorbeschouwingen."
 ),
}

P["bets"] = {}

P["bets"]["2026-11-01-serie-a-ita-juventus-napoli-btts-beide-ploegen-scoren-nee"] = {
 "book": "Matchbook (wedbeurs) — 2,18 op de site, 2,1564 na 2% commissie",
 "risk_level": "med",
 "preview": (
  "Juventus – Napoli op een zondagavond in november is in Italië geen gewone wedstrijd, en het is "
  "er dit jaar een tussen twee ploegen die elkaar in gemoedstoestand niet hadden kunnen "
  "verschillen. Napoli komt hier na 4–1 bij Monza, met twaalf doelpunten in vijf wedstrijden en "
  "een aanval die om de paar dagen iemand anders laat scoren. Juventus komt hier na 2–0 verlies bij "
  "Genoa, met zes doelpunten in diezelfde vijf wedstrijden en een vorm die je nauwelijks vorm kunt "
  "noemen: winst, verlies, gelijk, winst, verlies. Op papier is dit de wedstrijd waarin Napoli het "
  "verschil maakt. Mijn weddenschap zegt dat het er één van de twee niet in krijgt, en dat vraagt "
  "uitleg.\n\n"
  "Begin bij de ziekenboeg van Juventus, want die is bijna niet te overzien. Zeven spelers zijn er "
  "niet, en het gaat niet om reserves: Kenan Yıldız tot begin december, Khéphren Thuram tot "
  "halverwege januari, Manuel Locatelli tot eind maart, Nicolás González en Francisco Conceição "
  "tot halverwege november, Zeki Çelik erbij, en keeper Kamil Grabara het hele seizoen. Dat is "
  "zo'n beetje de hele creatieve laag van het elftal. Het is ook precies wat je terugziet in die "
  "zes doelpunten: Juventus maakt dit seizoen thuis gemiddeld iets meer dan twee goals per "
  "wedstrijd mét de tegenstander erbij, en in drie van hun vier thuiswedstrijden hield één van de "
  "twee ploegen de nul. Edon Zhegrova is met bijna vier schoten op doel per wedstrijd de enige die "
  "structureel dreigt, en een ploeg die op één man leunt wordt makkelijker uitgezet.\n\n"
  "Napoli mist er acht, en dat is misschien een nog vreemder lijstje: Stanislav Lobotka tot eind "
  "december, Alessandro Buongiorno, David Neres, Leonardo Spinazzola en Benoît Badiashile er ook "
  "niet, en trainer Massimiliano Allegri zit een schorsing uit en staat vanavond niet op de lijn. "
  "In waarde raakt dat Napoli minder hard dan Juventus — het is ongeveer een kwart van hun "
  "selectie tegen bijna de helft — maar het is wel de verdediging die eraan gaat, en Napoli heeft "
  "in vijf wedstrijden geen enkele keer de nul gehouden.\n\n"
  "De onderlinge geschiedenis spreekt mijn weddenschap tegen, en dat hoort hier te staan: 3–0, "
  "2–1, 2–1, 0–0, 2–1. Gemiddeld tweeënhalf doelpunt, maar in drie van die vijf wedstrijden "
  "scoorden beide ploegen. De keren dat het niet gebeurde waren de 0–0 van september 2024 en de "
  "3–0 van afgelopen januari, allebei in Turijn. De cijfers van dit seizoen vertellen hetzelfde "
  "gespleten verhaal: bij Juventus kwam het in slechts drie van negen wedstrijden tot doelpunten "
  "aan beide kanten en thuis in één van vier, bij Napoli in vijf van negen en in drie van vijf "
  "uitwedstrijden. Mijn weddenschap leunt dus op de thuisploeg en niet op de gast, en dat is de "
  "eerlijkste samenvatting die ik kan geven.\n\n"
  "Wat deze weddenschap sloopt is simpel: één moment waarin Zhegrova of een spits die er nog wel "
  "is Napoli's gehavende achterhoede openlegt, en dan moet Juventus de nul houden tegen een ploeg "
  "die er twaalf in vijf wedstrijden maakte. Dat is geen klein risico. En er is nog iets: Napoli "
  "moet woensdag naar FC Porto in de Champions League, Juventus donderdag naar AZ in Alkmaar. "
  "Twee ploegen met een Europese reis in het vooruitzicht spelen soms een voorzichtige wedstrijd, "
  "maar ze rouleren ook — en bij Juventus is er niet veel om mee te rouleren.\n\n"
  "*Dit is de hoogst gewaardeerde regel van vandaag en de enige waarbij ook mijn controle op "
  "andere aannames ruim overeind bleef. Beide rekenmethodes wijzen dezelfde kant op.*"
 ),
 "risk": (
  "De onderlinge geschiedenis en de cijfers van Napoli spreken deze weddenschap tegen: in drie van "
  "de laatste vijf ontmoetingen scoorden beide ploegen, Napoli maakte er twaalf in vijf "
  "wedstrijden en hield in geen van die vijf de nul. Ik leun hier bijna volledig op Juventus, en "
  "op een Juventus dat zeven spelers mist — wat ook kan betekenen dat ze juist achterin niet meer "
  "dichthouden. Mijn tweede rekenmethode ziet hier maar een fractie van het voordeel dat mijn "
  "hoofdmethode ziet; ze zijn het eens over de richting en verder nergens over."
 ),
}

P["bets"]["2026-11-01-super-lig-tur-kasmpasa-besiktas-btts-beide-ploegen-scoren-nee"] = {
 "book": "Matchbook (wedbeurs) — 2,52 op de site, 2,4896 na 2% commissie",
 "risk_level": "high",
 "preview": (
  "Dit is de weddenschap met het grootste verschil tussen mijn cijfers en de markt, en tegelijk "
  "die met de zwakste steun uit het verleden. Die twee dingen horen naast elkaar te staan, dus "
  "begin ik met het bezwaar: in de laatste vijf ontmoetingen tussen Kasımpaşa en Beşiktaş scoorden "
  "beide ploegen állemaal. 2–1, 1–1, 1–1, 1–3, 2–1 — vijf wedstrijden, gemiddeld bijna drie "
  "doelpunten, en geen enkele keer hield iemand de nul. Als u alleen naar deze affiche kijkt, is "
  "een weddenschap op 'niet beide ploegen scoren' een vreemde keuze. Dat moet bovenaan, niet in "
  "een voetnoot.\n\n"
  "Het seizoen van Kasımpaşa zegt hetzelfde: in zes van hun negen competitiewedstrijden scoorden "
  "beide ploegen, thuis in drie van vier. Beşiktaş zit lager — vier van negen, en buiten de deur "
  "twee van vier — maar ook dat is geen reeks waar je een weddenschap op bouwt. Waar mijn cijfers "
  "wél op leunen is het doelpuntenniveau zelf: Kasımpaşa haalt dit seizoen bij elkaar nog geen "
  "twee en een half doelpunt per wedstrijd en Beşiktaş iets meer dan drie, en dat zijn voor Turkse "
  "begrippen bescheiden getallen. In een wedstrijd met tweeënhalf tot drie doelpunten verwacht is "
  "de kans dat één van de twee droog blijft gewoon aanzienlijk, en de markt prijst hem hier op "
  "veertig procent terwijl ik op ruim drieënvijftig uitkom.\n\n"
  "Dan de ploegen zelf. Kasımpaşa staat er beter op dan hun naam suggereert: gelijk, verlies, "
  "winst, winst, winst in de laatste vijf, negen doelpunten in die reeks, en donderdag in de "
  "beker 3–1 tegen Çorluspor. Dat laatste is wel de keerzijde — ze hebben drie dagen rust gehad en "
  "spelen vandaag hun tweede wedstrijd in vier dagen, terwijl Beşiktaş zes dagen vrij had na een "
  "2–0 thuiszege op Başakşehir. Vijf spelers van Kasımpaşa staan op de twijfellijst — Mouanga, "
  "Diabaté, Frimpong, Ben Ouanes en Cörekci — en bij deze club is dat geen groot verlies in waarde "
  "maar wel vijf vraagtekens in een selectie die niet diep is. Adrian Benedyczak is hun man: de "
  "meeste schoten op doel én de meeste kansen gecreëerd.\n\n"
  "Beşiktaş mist er ook vijf, en bij hen tikt dat harder aan: Orkun Kökçü, Milot Rashica, Václav "
  "Černý, Fabio Miretti en Ümit Akdağ zijn er allemaal niet, samen ruim de helft van wat hun "
  "middenveld en aanval waard zijn. Wat overblijft draait om Leandro Trossard, die met vier de "
  "meeste grote kansen creëerde, en İlhan Fakılı, die met 2,2 schoten op doel per wedstrijd het "
  "vaakst zelf aanlegt. En er is een agenda-argument: Beşiktaş moet donderdag naar Celtic Park in "
  "de Europa League en daarna meteen weer thuis tegen Gençlerbirliği. Dat is het soort week waarin "
  "een trainer niet alles geeft op een uitwedstrijd in Istanbul tegen een ploeg uit de middenmoot.\n\n"
  "Wat deze weddenschap sloopt is de geschiedenis die ik hierboven zelf heb opgeschreven: deze "
  "twee ploegen spelen tegen elkaar nu eenmaal open wedstrijden, en vijf uit vijf is niet niks. "
  "Eén vroeg doelpunt aan beide kanten en het is voorbij. Het weer helpt ook niet mee: zeventien "
  "graden, licht bewolkt, droog — geen enkele reden waarom het een stroperige wedstrijd zou worden.\n\n"
  "*Het hoogste verschil met de markt van vandaag, en daarom ook de regel waar ik het meest naast "
  "kan zitten. Het is de enige die ik als hoog risico label.*"
 ),
 "risk": (
  "Hoog risico, en het is precies de weddenschap waar ik het meest tegen mezelf moet waarschuwen. "
  "In de laatste vijf ontmoetingen tussen deze twee ploegen scoorden beide elftallen vijf keer op "
  "vijf, en Kasımpaşa zat dit seizoen in twee derde van zijn wedstrijden op diezelfde uitkomst. "
  "Mijn cijfers leunen op het doelpuntenniveau van beide ploegen en niet op deze affiche, en de "
  "opstelling van Kasımpaşa is niet bevestigd — ik reken met hun laatste elf. Dat ik hier het "
  "grootste verschil met de markt vind, kan evengoed betekenen dat ik iets mis wat de markt wel "
  "ziet."
 ),
}

P["bets"]["2026-11-01-ligue-1-fra-lyon-angers-over-under-under-3-5"] = {
 "book": "Tipico — 1,60, geen commissie",
 "risk_level": "med",
 "preview": (
  "Lyon tegen Angers is op papier de minst spannende wedstrijd van mijn lijst, en dat is precies "
  "waarom hij erin staat. Dit is geen wedstrijd die ontploft. Lyon heeft Angers in de laatste "
  "zeven ontmoetingen niet verloren — zes zeges en één gelijkspel — en in die wedstrijden ging het "
  "zelden hard: 0–0, 1–0, 2–0, 0–3, 1–3. Gemiddeld twee doelpunten per duel, en in maar één van de "
  "vijf scoorden beide ploegen. Vier van die vijf wedstrijden zou deze weddenschap met ruime marge "
  "gewonnen hebben.\n\n"
  "Lyon komt hier na een avond die ze liever vergeten: 2–0 onderuit bij Paris Saint-Germain, en "
  "daarmee twee wedstrijden achter elkaar zonder zelf te scoren. Zes doelpunten in vijf "
  "wedstrijden, en een vorm van verlies-winst-winst-verlies-verlies. De oorzaak is niet "
  "geheimzinnig: ze missen vijf spelers en de twee die dat het meest uitmaken zijn aanvallers. "
  "Loïs Openda ligt eruit tot halverwege november, Pavel Šulc tot begin januari, Tyler Morton tot "
  "eind november, Mohamed Ouédraogo pas volgend seizoen weer. Bij elkaar is dat ruim een derde van "
  "de waarde van hun selectie, en vrijwel alles ervan zit in de helft van het veld waar doelpunten "
  "worden gemaakt. Dat Lyon bijna zes dagen rust had maakt dat niet goed.\n\n"
  "Angers is de rustigste ploeg van de Franse competitie, en dat is geen belediging maar een "
  "cijfer: vorig seizoen ging in slechts zes van hun vierendertig wedstrijden de teller boven "
  "drieënhalf doelpunt — achttien procent, en dat is de laagste van beide ploegen met ruime "
  "afstand. Ze komen hier na 0–0 tegen Lorient, hebben zeven dagen gerust, missen alleen Biumla en "
  "El Ouazzani, en hun keeper Anthony Lopes staat tweede in de competitie op reddingen per "
  "wedstrijd met 4,1. Een doelman die zoveel te doen krijgt zegt twee dingen tegelijk — zijn ploeg "
  "wordt onder druk gezet, maar er gaan er ook weinig in. Amine Sbaï creëerde met zes de meeste "
  "grote kansen; dat is hun enige echte dreiging naar voren.\n\n"
  "Wat de weddenschap tegenspreekt zit in de dunne reeksen, en dat wil ik niet wegmoffelen: Lyon "
  "ging dit seizoen in twee van zijn vier thuiswedstrijden wél over drieënhalf doelpunt — "
  "gemiddeld ruim drie per wedstrijd op eigen veld — en Angers in twee van zijn drie uitduels. Dat "
  "zijn reeksen van drie en vier wedstrijden en dus voor een flink deel toeval, maar het is de "
  "enige hoek die iets anders zegt dan de rest. En het weer geeft geen enkele hulp: elf graden, "
  "zon, droog, een briesje. Een perfect veld om op te voetballen.\n\n"
  "Wat deze weddenschap sloopt is een vroeg doelpunt van Lyon. Als Angers in de achtervolging moet "
  "en opschuift, komt er ruimte, en dan is drie-nul of vier-een in het Groupama Stadium geen "
  "uitzonderlijke uitslag — de 0–3 en de 1–3 uit het rijtje hierboven zijn precies zo gegaan, al "
  "waren dat uitwedstrijden van Lyon. Houd ook in gedachten dat Lyon donderdag naar Real Sociedad "
  "moet in de Europa League; met een al dunne selectie kan dat vandaag een voorzichtige, "
  "halfgevulde ploeg betekenen.\n\n"
  "*Deze regel staat in de lijst omdat hij vandaag bij de beste vijf hoort, niet omdat ik er een "
  "duidelijk voordeel in zie — mijn verschil met de markt blijft onder de grens die ik normaal "
  "aanhoud.*"
 ),
 "risk": (
  "Dit is de laagste koers van de lijst, dus u legt veel in voor weinig. De weddenschap komt niet "
  "boven mijn gebruikelijke grens uit en staat in de lijst op rangorde: hij is vandaag een van de "
  "vijf beste, niet een gevonden voordeel. Lyon ging dit seizoen in de helft van zijn "
  "thuiswedstrijden wél over deze grens, en dat is de hoek waar het mis kan gaan. Verder: "
  "weddenschappen op weinig doelpunten zijn precies de groep waar mijn rekenwerk de laatste weken "
  "te laag heeft gezeten — tel bij de genoemde kans in gedachten een paar procentpunt af."
 ),
}

P["bets"]["2026-11-01-la-liga-esp-getafe-sevilla-btts-beide-ploegen-scoren-nee"] = {
 "book": "Matchbook (wedbeurs) — 1,80 op de site, 1,784 na 2% commissie",
 "risk_level": "med",
 "preview": (
  "Als er één wedstrijd op de Spaanse kalender staat waar doelpunten schaars zijn, is het deze. De "
  "laatste vijf ontmoetingen tussen Getafe en Sevilla: 0–1, 1–2, 0–0, 1–0, 0–1. Dat is gemiddeld "
  "iets meer dan één doelpunt per wedstrijd, en in vier van de vijf hield één van de twee ploegen "
  "de nul. In het Coliseum is dat nog sterker: Getafe speelde dit seizoen vijf thuiswedstrijden en "
  "in geen enkele daarvan vielen er meer dan twee doelpunten — gemiddeld anderhalf per wedstrijd, "
  "het laagste cijfer van de hele competitie. Dit is de wedstrijd waarin niets gebeurt, en dat "
  "gebeurt hier consequent.\n\n"
  "Toch is dit niet de makkelijke weddenschap die dat suggereert, en het bezwaar komt van twee "
  "kanten. Ten eerste Sevilla: zij zitten dit seizoen in zeven van hun tien competitiewedstrijden "
  "op doelpunten aan beide kanten, buiten de deur zelfs in vier van de vijf, en ze maken "
  "gemiddeld ruim drieënhalf doelpunt per uitwedstrijd mét tegenstander erbij. Tien goals in vijf "
  "wedstrijden en een reeks van verlies-gelijk-verlies-winst-winst. Ten tweede Getafe zelf: hun "
  "thuiswedstrijden zijn láág, maar niet dícht — in drie van die vijf scoorden beide ploegen "
  "alsnog, meestal in een 1–1. En hun eigen statistiek is pijnlijk duidelijk: Getafe hield in zes "
  "wedstrijden geen enkele keer de nul. Mijn weddenschap heeft precies dat nodig, aan één van de "
  "twee kanten.\n\n"
  "Wat de balans voor mij toch die kant op duwt, is in welke staat Getafe hier staat. Ze missen "
  "vijf spelers en dat is bijna de helft van de waarde van hun selectie: Christantus Uche ligt er "
  "het hele seizoen uit, Johan Mojica en Mario Martín zijn geschorst tot begin november, Juanmi is "
  "er voor onbepaalde tijd niet bij, Zaid Romero traint net weer mee. Vorige week werden ze bij "
  "Athletic Club met 4–0 weggespeeld, donderdag moesten ze in de Copa del Rey nog vol aan de bak "
  "bij amateurclub UB Lebrijana (3–2 gewonnen, met moeite), en woensdag komt Brighton op bezoek in "
  "de Conference League. Dat zijn tweeëneenhalve dag rust en een halfvolle selectie. Een ploeg in "
  "die toestand maakt zelf meestal niets; de vraag is alleen of ze het achterin dichthouden.\n\n"
  "Sevilla heeft bijna geen blessures — twee namen, samen een paar procent van de selectiewaarde — "
  "maar ook zij speelden donderdag beker (3–0 bij Sporting Hortaleza) en hebben dus net zo weinig "
  "rust. Lucas Stassin is hun gevaarlijkste man met 1,2 schoten op doel per wedstrijd, Robbie Ure "
  "creëerde de meeste grote kansen. Negentien graden en een strakblauwe hemel in Getafe; het veld "
  "biedt geen enkel excuus.\n\n"
  "Wat deze weddenschap sloopt is het meest waarschijnlijke scenario van allemaal: een 1–1. "
  "Sevilla komt op voorsprong, Getafe prikt er in de slotfase een tegen, en u bent uw inzet kwijt "
  "aan de uitslag die in het Coliseum het vaakst voorkomt. Dat is geen theoretisch risico maar de "
  "uitslag van drie van hun vijf thuiswedstrijden dit seizoen.\n\n"
  "*Staat in de lijst op rangorde en niet op een gehaalde grens; mijn tweede rekenmethode ziet "
  "hier vrijwel geen voordeel, dus de twee methodes zijn het hier alleen over de richting eens.*"
 ),
 "risk": (
  "Mijn twee rekenmethodes staan hier het verst uit elkaar van alle vijf de regels: de ene ziet "
  "een duidelijk voordeel, de andere praktisch niets. Ze zijn het eens over de richting en verder "
  "nergens over, en als ik aan mijn aannames draai blijft er bijna niets van het voordeel over. "
  "Daar komt bij dat Sevilla buiten de deur in vier van de vijf wedstrijden op doelpunten aan "
  "beide kanten uitkwam en Getafe in zes wedstrijden geen enkele keer de nul hield. De 1–1 is hier "
  "de meest waarschijnlijke uitslag en die kost u uw inzet."
 ),
}

P["bets"]["2026-11-01-premier-league-eng-liverpool-arsenal-draw-no-bet-dnb-arsenal"] = {
 "book": "Matchbook (wedbeurs) — 1,83 op de site, 1,8134 na 2% commissie",
 "risk_level": "med",
 "preview": (
  "De grootste wedstrijd van het weekend, en de enige Premier League-wedstrijd van vandaag: "
  "Liverpool tegen Arsenal op Anfield, half zes 's middags Nederlandse tijd. Mijn weddenschap is "
  "Arsenal zonder het gelijkspel — wint Arsenal, dan is het een winnende weddenschap; wordt het "
  "gelijk, dan krijgt u uw inzet terug; verliest Arsenal, dan is hij weg. Dat laatste is "
  "belangrijk, want het gelijkspel is hier verre van onwaarschijnlijk.\n\n"
  "De onderlinge geschiedenis spreekt de weddenschap tegen en dat hoort vooraan: Liverpool heeft "
  "in de laatste vijf ontmoetingen niet van Arsenal verloren — twee zeges en drie gelijke spelen, "
  "met 0–0, 1–0, 2–2, 2–2 en 2–1 als uitslagen. Op Anfield gebeurt dit soort wedstrijden zelden "
  "wat Arsenal wil. En Liverpool is in vorm: winst, winst, winst, winst, gelijk in de laatste "
  "vijf, vijftien doelpunten in die reeks, vorige week 2–0 tegen Brighton.\n\n"
  "Waarom ik hier toch Arsenal neem, zit in de ziekenboeg van beide ploegen — en vooral in de "
  "verhouding ertussen. Liverpool mist er zes, en het zijn geen namen uit de marge: Hugo Ekitiké "
  "tot begin januari, Jeremie Frimpong tot halverwege november, Giovanni Leoni tot eind november, "
  "Conor Bradley tot begin januari, en Dominik Szoboszlai en Víctor Muñoz zijn twijfelgevallen. "
  "Bij elkaar is dat ruim een derde van de waarde van hun selectie, en het raakt vooral de "
  "vleugels en de spits. Daar komt bij dat Liverpool woensdag een zware avond had — 1–1 tegen "
  "Chelsea in de League Cup — en dus met net geen vier dagen rust aan deze wedstrijd begint. "
  "Woensdag wacht Fenerbahçe in de Champions League.\n\n"
  "Arsenal mist er vier en dat weegt ongeveer even zwaar in geld: Bukayo Saka is er tot halverwege "
  "december niet bij, William Saliba tot eind november, Max Dowman is geschorst, Christos Tzolis "
  "twijfelt. Dat Saka ontbreekt is een serieus gat — hij was tot zijn blessure hun gevaarlijkste "
  "man — maar Declan Rice heeft er met drie de meeste grote kansen gecreëerd en Arsenal maakte er "
  "negen in vijf wedstrijden met een reeks van winst-winst-gelijk-winst-gelijk. En ze hebben er "
  "een hele dag meer rust: zij speelden maandag al hun bekerwedstrijd (1–1 bij Fleetwood Town, "
  "met een B-elftal) en daarna niets.\n\n"
  "Wat hier verder opvalt is hoe laag beide ploegen dit seizoen scoren vergeleken met vorig jaar. "
  "Liverpool komt op nog geen twee en een half doelpunt per wedstrijd uit, tegen ruim drie vorig "
  "seizoen; Arsenal op iets meer dan twee, tegen tweeënhalf. Arsenal kwam in zijn vier "
  "uitwedstrijden geen enkele keer tot doelpunten aan beide kanten. Dat alles wijst op een krappe, "
  "gespannen wedstrijd — en in een krappe wedstrijd is precies dát de reden dat ik het gelijkspel "
  "liever buiten de weddenschap houd dan erop te gokken.\n\n"
  "Wat de weddenschap sloopt: Anfield op een bewolkte novembermiddag, een vol stadion en een "
  "Liverpool dat in vijf wedstrijden niet verloor. Elf graden, droog, nauwelijks wind — geen enkele "
  "omstandigheid die de thuisploeg in de weg zit. En de geschiedenis van deze affiche zegt dat je "
  "hier niet komt winnen.\n\n"
  "*De laagst gewaardeerde regel van de vijf, en de regel die het dunst overeind blijft als ik aan "
  "mijn aannames draai. Hij staat in de lijst op rangorde, niet op een gehaalde grens.*"
 ),
 "risk": (
  "De zwakste regel van de vijf, en hij staat erin omdat er vandaag niet meer te kiezen was. "
  "Liverpool verloor in de laatste vijf ontmoetingen niet van Arsenal en is in vorm met vier zeges "
  "uit vijf. Als ik aan mijn aannames draai, blijft er van het voordeel bijna niets over — dit is "
  "het randje van wat ik nog publiceerbaar vind. Het gelijkspel geeft u uw inzet terug, en dat is "
  "bij deze affiche een reële uitkomst: drie van de laatste vijf ontmoetingen eindigden gelijk."
 ),
}

P["finding"] = [{
 "title": "Twee van mijn vijf weddenschappen bestonden pas nadat ik een extra prijs had gekocht",
 "paragraphs": [
  "Niet alle prijzen kosten mij hetzelfde. Voor de meeste markten — wie er wint, hoeveel doelpunten "
  "er vallen, handicaps — koop ik ze per competitie in één keer in, en dan kost een extra wedstrijd "
  "binnen die competitie mij niets. Maar 'beide ploegen scoren' wordt per wedstrijd afgerekend, en "
  "daarom koop ik die pas in een tweede ronde, alleen voor de duels waar al iets te vinden lijkt. "
  "Vandaag waren dat drieëntwintig wedstrijden, voor drieëntwintig eenheden van mijn maandbudget "
  "van twintigduizend.",
  "Die tweede ronde veranderde vandaag op béide wedstrijden die hun grens halen wat ik publiceer. "
  "Vóór de BTTS-prijzen stond Juventus – Napoli in mijn lijst als 'minder dan 2,5 doelpunt' en "
  "Kasımpaşa – Beşiktaş als 'minder dan 2,75 doelpunt'. Dat is in de kern dezelfde mening — ik "
  "verwacht in beide wedstrijden weinig doelpunten — maar in de BTTS-markt is die mening meer waard: "
  "de prijs is hoger en de waardering die ik eraan geef gaat van 7,49 naar 7,54 bij Juventus en van "
  "6,48 naar 7,06 bij Kasımpaşa. Mijn eigen regel zegt dat ik binnen één wedstrijd de hoogst "
  "gewaardeerde markt publiceer, dus zijn het nu twee BTTS-weddenschappen geworden.",
  "Waarom dit het opschrijven waard is: er zit een stille verleiding in die tweede ronde. Ze kost "
  "geld per wedstrijd, ze komt achteraan in de pijplijn, en als een run haar zou overslaan klaagt "
  "er niets — het rapport ziet er daarna volkomen normaal uit, met twee weddenschappen op weinig "
  "doelpunten erin. Vandaag is het bewijs dat die stap werkelijk bijt en geen formaliteit is. En er "
  "zit een tweede winst in: na twee dagen waarop álle gepubliceerde weddenschappen een "
  "doelpuntenmarkt waren — vier van vier op vrijdag, vijf van vijf op zaterdag — staan er vandaag "
  "drie markten in de lijst. Dat is geen maatregel en geen quotum; ik heb niets veranderd. Het laat "
  "alleen zien dat die eentonigheid een uitkomst was en geen vorm.",
 ],
}]

P["todo"] = [
 {"title": "Welke van mijn twee rekenmethodes zit er eigenlijk naast?",
  "owner": "ik",
  "detail": (
   "Ik reken elke wedstrijd op twee manieren door en publiceer alleen als ze het eens zijn over de "
   "richting. Die controle vangt inmiddels driekwart van alles weg: vandaag 356 van de 479 "
   "doorgerekende mogelijkheden, gisteren 71 procent, en de dag ervoor ook boven de zeventig. Dat "
   "is drie dagen op rij, en mijn eigen regels zeggen dat een controle die structureel alles "
   "wegvangt een bevinding is en geen bijzaak. Wat ik nog niet weet, is wélke van de twee methodes "
   "er dan naast zit. Vandaag zie ik bij Getafe – Sevilla de ene methode bijna tien procentpunt "
   "voordeel zien en de andere vrijwel nul, en bij Juventus – Napoli vijftien tegen twee. Dat is "
   "een verschil dat ik kan narekenen over de honderden afgerekende gevallen die er inmiddels "
   "liggen, en daar hoort het antwoord ook te komen — niet uit een redenering. Wat ik vandaag "
   "nadrukkelijk niet doe, is er een drempel of een gewicht op verzetten: dat zou precies de fout "
   "zijn waar mijn eigen regels voor waarschuwen."),
  "action": "Niets — ik meet dit zelf uit, en ik verwacht er binnen een week iets zinnigs over te kunnen zeggen."},
 {"title": "Wil u het dagrapport liever eerst als GitHub-pagina in plaats van als Artifact?",
  "owner": "besluit",
  "detail": (
   "Op 14 en 15 oktober was het dagrapport voor u niet te openen — één keer met een DNS-fout, één "
   "keer als wit scherm — terwijl de pagina zelf aantoonbaar in orde was. Sindsdien lever ik hem "
   "langs twee routes: de Artifact (die mooier leest) en een markdown-versie in de repo, die GitHub "
   "zelf rendeert. Beide staan in elke notificatie. De Artifact heeft het sindsdien goed gedaan, "
   "dus er is geen aanleiding om te wisselen; ik stel de vraag omdat de keuze wélke van de twee de "
   "eerste route is bij u hoort en niet bij mij. Ik verander die volgorde niet op eigen initiatief, "
   "en ik stel de vraag ook niet elke dag opnieuw."),
  "action": "Laat me weten of de Artifact de eerste route moet blijven, of dat u liever met de GitHub-pagina begint. Zegt u niets, dan blijft het zoals het is."},
 {"title": "Moeten de twee weddenschappen van 3 en 4 oktober uit mijn logboek?",
  "owner": "besluit",
  "detail": (
   "Dit punt staat sinds 31 oktober open en ik haal het hier nog één keer terug omdat er nog geen "
   "antwoord is. Het gaat om Exeter City – Rotherham United (3 oktober) en Girona – Mallorca "
   "(4 oktober). Door een rekenfout die ik op 31 oktober heb gevonden en gerepareerd, hadden die "
   "twee niet gepubliceerd mogen worden. Beide zijn gewonnen, dus eruit halen maakt mijn resultaten "
   "iets slechter en niet beter — dat is juist de reden om het te vragen in plaats van het zelf te "
   "beslissen. Mijn voorkeur is ze laten staan: ze staan in de rapporten van die dagen, het zijn "
   "twee van ruim vijfhonderd afgerekende weddenschappen, en ze verschuiven geen enkel cijfer. Maar "
   "het is uw logboek."),
  "action": "Laat me weten of ik die twee regels uit het logboek moet halen of moet laten staan."},
]

json.dump(P, open('runs/2026-11-01-run-a.prose.json','w'), ensure_ascii=False, indent=1)
import re
for k,v in P["bets"].items():
    print(k, '->', len(v["preview"].split()), 'woorden')
print('prose geschreven')
