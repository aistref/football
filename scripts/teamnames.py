"""Clubnamen koppelen tussen de bronnen — de aliastabel en de normalisatie.

**Verhuisd uit `tmp-run/ra_names.py` op 5 oktober 2026 (Run B), en het is geen opruimklus.**
De tabel hieronder stond in een wegwerpbestand in `tmp-run/`, dus alleen de runscripts konden
hem gebruiken: een module in `scripts/` kan niet uit `tmp-run/` importeren. Gevolg was dat
`scripts/settling.py` — de module die beslist of een pick afwikkelbaar is en met welke uitslag
— zijn eigen, veel simpelere naamkoppeling had: exacte naam, en anders de eerste zes letters
van beide namen als voorvoegsel. Dat bridget "Swansea" naar "Swansea City" niet eens, laat
staan "PSG" naar "Paris Saint-Germain".

**Wat dat heeft gekost, in cijfers van vandaag.** 141 van de 3831 waarnemingen in
`data/calibration.jsonl` stonden onafgewikkeld — 47 wedstrijden over dertien rundagen van
22 augustus tot 3 oktober, allemaal competities uit Run A en Run C. Dat logboek is sinds
20 september de bron van de herijking van §1g (zie de docstring van `recalibrate.observations`),
dus die 47 wedstrijden ontbreken in de fit die élke gepubliceerde bet gebruikt. Het faalt
stil, en dat is de kern: `calibration.py settle` meldt netjes "0 waarnemingen afgewikkeld" en
`load_fit()` geeft gewoon een geldige fit op de rijen die hij wél heeft. Run B van 4 oktober
noteerde de staart (toen 129 rijen, 43 duels) als bevinding en wees `DayIndex.lookup` aan;
dit is die reparatie.

**31 van de 47 zijn hiermee op te lossen, en de overige 16 zijn nieuwe aliasregels** van
precies de soort die de geschiedenis in deze tabel laat zien ("Sheff Wed", "MK Dons",
"Tottenham", "Köln"). Daarvan zijn er vandaag een paar bijgeschreven; de FA Cup-duels van
3 oktober staan helemaal niet op de Fotmob-daglijst en zijn dus iets anders.

Alleen de standaardbibliotheek. `tmp-run/ra_names.py` importeert nu uit dit bestand, zodat er
één tabel is en niet twee die uiteenlopen — dezelfde reden waarom de afwikkelregel van §0 in
één module staat in plaats van twee keer los.

De oorspronkelijke kop van `ra_names.py`, omdat hij uitlegt waaróm de tabel bestaat:

    Naamkoppeling tussen de Fotmob-daglijst en de Fotmob-standtabel. Beide komen van Fotmob,
    maar de daglijst gebruikt de korte weergavenaam ("Wigan", "Cádiz") en de tabel de
    volledige ("Wigan Athletic", "Cadiz"). Zonder koppeling leest dat als "ploeg zonder
    historie in deze divisie" en dus als tier NONE — op 30 aug 2026 gebeurde dat bij 12 van de
    18 vermeende NONE-duels, allemaal ten onrechte.
"""
import re, unicodedata

_DROP = {"fc", "afc", "cf", "sc", "ac", "as", "sv", "vfl", "vfb", "tsv", "bsc", "se", "if", "ff",
         "town", "city", "united", "utd", "athletic", "wanderers", "rovers", "county", "argyle",
         "albion", "kf", "ks", "cd", "ad", "ca", "ud", "sd", "us", "club", "calcio", "1905"}

ALIASES = {  # daglijstnaam -> tabelnaam, alleen waar geen enkele token overlapt
    "hamkam": "hamarkameratene",
    # 30 sep 2026 (Run B): woordVOLGORDE, niet een afkorting of een andere taal. Fotmob schrijft
    # "Red Bull New York", The Odds API "New York Red Bulls" — na _DROP blijft {red, bull, new,
    # york} tegen {new, york, red, bulls} over, en dat is in geen van beide richtingen een
    # deelverzameling ("bull" is niet "bulls"). Zoals bij FC København raakt dit niet de tier maar
    # de PRIJZEN, en het faalt stil: `side_of` gaf None en de analyse deed `continue`, dus de
    # THUISKANT van de 1X2 werd niet doorgerekend terwijl LeoVegas en negen andere boeken er een
    # koers voor hadden. Het duel stond op FULL en kreeg toch maar twee 1X2-selecties in plaats
    # van drie; in het runrapport is dat niet te zien, want een overgeslagen selectie laat geen
    # spoor na. MLS speelt in deze runlijst elke paar dagen.
    "new york red bulls": "red bull new york",
    "red bull new york": "new york red bulls",
    # 1 sep 2026: de Engelse daglijst kort af tot een deel dat na _DROP niets overhoudt dat
    # met de tabelnaam overlapt. Zonder deze drie leest een ploeg die gewoon in de stand
    # staat als "geen historie in deze divisie" en gaat hij ten onrechte de omrekening in.
    "sheff utd": "sheffield united",
    "wolves": "wolverhampton wanderers",
    "west ham": "west ham united",
    # 2 sep 2026: dezelfde val, twee nieuwe gevallen. "QPR" is een initiaalwoord en deelt geen
    # enkel token met "Queens Park Rangers"; bij "West Brom" valt "albion" weg in _DROP, zodat
    # "brom" en "bromwich" overblijven — verschillende tokens. Beide ploegen staan gewoon in de
    # Championship-stand van 2025/2026 en gingen zonder deze twee regels ten onrechte de
    # promovendi-omrekening in.
    "qpr": "queens park rangers",
    "west brom": "west bromwich albion",
    # 3 sep 2026: derde geval van dezelfde soort. De daglijst schrijft "Hearts", de
    # Premiership-stand "Heart of Midlothian" — enkelvoud tegen meervoud, dus geen enkel
    # gedeeld token. Hearts stond gewoon in de stand van 2025/2026 en ging zonder deze regel
    # ten onrechte de promovendi-omrekening in (en daarmee van FULL naar LIGHT).
    "hearts": "heart of midlothian",
    # 4 sep 2026: vierde geval van dezelfde soort, en het duurste tot nu toe. De daglijst
    # schrijft "PSG", de Ligue 1-stand "Paris Saint-Germain" — een initiaalwoord deelt geen
    # enkel token met de voluitnaam. PSG stond gewoon in de stand van 2025/2026 en ging zonder
    # deze regel ten onrechte de promovendi-omrekening in, die voor een ploeg uit de hoogste
    # divisie niets kán opleveren (er is geen divisie boven Ligue 1) en dus op NONE uitkomt.
    "psg": "paris saint germain",
    # 5 sep 2026: drie gevallen op één dag, alle drie dezelfde soort. De daglijst kort de
    # clubnaam zo af dat er na _DROP geen enkel token overblijft dat de tabelnaam ook heeft:
    # "Man City" houdt {man} over tegen {manchester}, "Nottm Forest" {nottm, forest} tegen
    # {nottingham, forest} (deelverzameling in geen van beide richtingen), en "M'gladbach"
    # {m, gladbach} tegen {borussia, monchengladbach}. Alle drie stonden gewoon in de stand
    # van 2025/2026 en gingen zonder deze regels ten onrechte de promovendi-omrekening in —
    # die voor een ploeg uit de hoogste divisie niets kán opleveren en dus op NONE uitkomt.
    "man city": "manchester city",
    "nottm forest": "nottingham forest",
    "m gladbach": "borussia monchengladbach",
    # 6 sep 2026: zelfde soort als "man city" van gisteren, en het kostte opnieuw een volledig
    # gedekt duel. "Man United" houdt na _DROP ({united} valt weg) alleen {man} over tegen
    # {manchester} in de tabel. Everton – Man United ging daardoor ten onrechte de
    # promovendi-omrekening in en kwam uit op NONE, terwijl Manchester United gewoon in de
    # Premier League-stand van 2025/2026 staat.
    "man united": "manchester united",
    # 6 sep 2026, andere oorzaak dan de rest van deze lijst: dit is geen afkorting maar een
    # ANDERE TAAL. Fotmob schrijft de Deense naam "FC København", The Odds API en BetExplorer
    # de Engelse "FC Copenhagen" — na _DROP blijft {kobenhavn} tegen {copenhagen} over, en dat
    # deelt geen enkel token. Anders dan de gevallen hierboven raakt dit niet de tier maar de
    # PRIJZEN: OB – FC København stond op FULL en kreeg toch nul selecties doorgerekend, omdat
    # `find_event` de wedstrijd bij geen enkele bron kon terugvinden.
    "fc kobenhavn": "fc copenhagen",
    # 6 sep 2026 (Run B), dezelfde soort als "fc kobenhavn": het raakt de PRIJZEN en niet de tier.
    # Fotmob schrijft "NK Lokomotiva" (en zo staat de ploeg ook in de HNL-stand, dus daar valt
    # niets te koppelen), maar BetExplorer kort af tot "Lok. Zagreb". Na _DROP blijft {nk,
    # lokomotiva} tegen {lok, zagreb} over — geen gedeeld token — en de naamgelijkenis over het
    # hele paar komt op 0.48, onder de vloer van 0.62. Slaven – NK Lokomotiva kreeg daardoor nul
    # selecties doorgerekend terwijl de Croatian HNL wél een 1X2-rij bij BetExplorer had.
    "nk lokomotiva": "lok zagreb",
    # 20 sep 2026 (Run B): de tegenhanger van de regel hierboven, in dezelfde wedstrijd. Met
    # alleen "nk lokomotiva" koppelt één van de twee ploegen en eist `find_1x2` ze allebei, dus
    # bleef Dinamo Zagreb – NK Lokomotiva alsnog op nul doorgerekende selecties staan. Fotmob
    # schrijft "Dinamo Zagreb", BetExplorer kort af tot "Din. Zagreb": na _DROP blijft {dinamo,
    # zagreb} tegen {din, zagreb} over — ze delen "zagreb", maar geen van beide is een
    # deelverzameling van de ander, en dat is wat `resolve` eist. Croatië heeft geen sportkey,
    # dus BetExplorer was ook hier de enige prijsbron.
    "dinamo zagreb": "din zagreb",
    # 7 sep 2026 (Run B), opnieuw de prijzen en niet de tier, en dit keer twee ploegen in
    # dezelfde wedstrijd. De Fotmob-stand van de Romanian SuperLiga schrijft de namen voluit
    # ("Universitatea Craiova", "Universitatea Cluj") en BetExplorer kort het eerste woord af
    # tot "Univ." respectievelijk "U.". Na _DROP blijft {universitatea, craiova} tegen {univ,
    # craiova} over: ze delen wél een token, maar geen van beide is een deelverzameling van de
    # ander, en dat is wat `resolve` eist. `best_pair` liep er net langs — 0.727 op Craiova en
    # 0.500 op Cluj is 0.614 over het paar, tegen een vloer van 0.62. Universitatea Craiova –
    # Universitatea Cluj kwam daardoor op nul doorgerekende selecties uit terwijl de rij met
    # vijf boeken gewoon bij BetExplorer stond; Romania heeft geen sportkey, dus dat was de
    # enige prijsbron die er was.
    "universitatea craiova": "univ craiova",
    "universitatea cluj": "u cluj",
    # 13 sep 2026: initiaalwoord tegen plaatsnaam, net als "qpr" en "psg", maar nu aan de prijskant.
    # Fotmob schrijft "AGF", BetExplorer "Aarhus" — geen gedeeld token en een naamgelijkenis van
    # 0.22. Samen met de æ-fout in `norm` hierboven zakte het paar Nordsjælland – AGF onder de
    # vloer van `best_pair`; met alleen de æ-fout hersteld zou het op 0.61 blijven staan, nog net
    # eronder. The Odds API schrijft "AGF Aarhus" en kwam wél door — daar is {agf} een
    # deelverzameling van {agf, aarhus}.
    "agf": "aarhus",
    # 3 okt 2026 (Run B): Braziliaanse Série A, en het is NIET de diakrietenval waar het
    # coverage-briefje van 2 oktober voor waarschuwt — `norm` haalt accenten gewoon weg. Hier
    # schrijven de twee bronnen een ANDER DEEL van de naam: Fotmob "Atlético-MG" (de
    # staatsafkorting) tegen The Odds API "Atletico Mineiro" (de staat voluit), en Fotmob
    # "RB Bragantino" (de sponsor) tegen The Odds API "Bragantino-SP". In beide paren delen de
    # tokens er één maar is geen van beide een deelverzameling van de ander, en dat is wat
    # `resolve` eist.
    #
    # Het faalt stil en het kost meer dan één prijs. `find_event` koppelt de wedstrijd nog wél
    # (`best_pair` haalt de vloer), maar `side_of` draait op `resolve` en gaf None voor allebei
    # de ploegen. Gevolg op 3 oktober bij Atlético-MG – RB Bragantino: van de 1X2 bleef alleen
    # het GELIJKSPEL over (dat heeft geen kant), en Asian Handicap, Draw No Bet en Double Chance
    # kwamen alle drie op nul selecties uit terwijl de spreads-respons gewoon lijnen bevatte.
    # Elf van de veertien doorgerekende selecties van dat duel vielen weg, en in
    # `markets_checked` stond "0 handicaplijnen" — wat leest als "geen boek bood ze aan".
    # BetExplorer koppelde wél ("Atletico-MG" en "Bragantino"), dus het marktgemiddelde en
    # daarmee het kalibratieblok en poort 8 bleven overeind; alleen de bet zelf was blind.
    "atletico mineiro": "atletico mg",
    "atletico mg": "atletico mineiro",
    "bragantino sp": "rb bragantino",
    "rb bragantino": "bragantino sp",
    # 5 okt 2026 (Run B), bij de verhuizing van deze tabel naar `scripts/`: vier gevallen die
    # `settling.DayIndex.lookup` nodig heeft en die de tokenregel niet haalt. Anders dan de
    # regels hierboven raken deze niet de tier en niet de prijzen maar DE AFWIKKELING — ze
    # hielden waarnemingen uit `data/calibration.jsonl` onafgewikkeld, en dat logboek is sinds
    # 20 september de bron van de herijking van §1g.
    #
    # "Sheff Wed" houdt na _DROP {sheff, wed} over tegen {sheffield, wednesday}: geen gedeeld
    # token en in geen van beide richtingen een deelverzameling — dezelfde val als "sheff utd"
    # van 1 september. "MK Dons" geeft {mk, dons} tegen {milton, keynes, dons}; ze delen "dons",
    # maar dat is niet wat de tokenregel eist. "Tottenham" is een deelverzameling van
    # {tottenham, hotspur} en koppelt op zichzelf wél — maar niet wanneer de daglijst óók
    # "Tottenham Hotspur" als aparte naam kent en er dus twee kandidaten zijn. En "Köln" komt na
    # norm op {koln} uit tegen {1, koln} in "1. FC Köln": het cijfer blijft staan omdat het geen
    # generiek woord is, dus de verzamelingen zijn niet gelijk en geen van beide bevat de ander.
    "sheff wed": "sheffield wednesday",
    "mk dons": "milton keynes dons",
    "tottenham": "tottenham hotspur",
    "koln": "1 fc koln",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("Ø", "o").replace("ł", "l").replace("đ", "d").replace("ß", "ss")
    # 13 sep 2026: æ en œ zijn LIGATUREN en geen letter-met-teken, dus NFKD laat ze staan en de
    # regex hieronder gooide ze wég in plaats van ze uit te schrijven. "Nordsjælland" werd daardoor
    # "nordsjlland" tegen "nordsjaelland" bij The Odds API en BetExplorer: geen gedeeld token, en
    # de naamgelijkenis over het paar Nordsjælland – AGF kwam op 0.57 tegen een vloer van 0.62.
    # Gevolg op 13 sep: één duel zonder 1X2-marktgemiddelde, dus zonder kalibratieblok (§6e) én
    # met poort 8 open omdat er geen marktoordeel over de zwakkere ploeg was.
    s = s.replace("æ", "ae").replace("Æ", "ae").replace("œ", "oe").replace("Œ", "oe")
    # Dubbele spaties platslaan: een punt of koppelteken wordt hierboven een spatie, zodat
    # "Lok. Zagreb" anders op "lok  zagreb" uitkomt en niet meer gelijk is aan de vorm waarin
    # een alias hierboven geschreven staat. Zonder dit is `norm` niet idempotent.
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def tokens(s: str) -> frozenset:
    return frozenset(t for t in norm(s).split() if t not in _DROP) or frozenset(norm(s).split())

