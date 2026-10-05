"""§6b-3 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft."""
import json

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
DAG = "2026-10-05"


def bij(key, status, tekst, **extra):
    v = S.setdefault(key, {})
    v["status"] = status
    v["last_checked"] = DAG
    v["detail"] = (str(v.get("detail", "")).rstrip() + f"  [Run B] {tekst}").strip()
    v.update(extra)


bij("fotmob", "ok",
    "Run B 5 okt: twee daglijsten (5 okt: 30 competities/55 duels; 6 okt: 58/110), 34 "
    "standenverzoeken voor scripts/idcheck.py (17 competities, alle 17 OK, afsluitcode 0), twee "
    "standen voor de enige spelende competitie (Segunda División, vorig en lopend seizoen) en de "
    "wedstrijdcontext van het enige duel in het inzetvenster. Alles HTTP 200, geen storing; "
    "Fotmob was opnieuw de enige kansbron. VEEL ZWAARDER GEBRUIKT DAN EEN GEWONE RUNDAG, en met "
    "een reden die buiten de dag van vandaag ligt: voor de reparatie van de afwikkeling (zie "
    "scripts/teamnames.py) zijn de daglijsten van dertien eerdere rundagen van 22 aug t/m 3 okt "
    "opnieuw opgehaald, plus de dag erná voor de competities in Amerikaanse tijdzones. Alle "
    "verzoeken gaven HTTP 200 en een bruikbare lijst — ook die van zes weken terug, dus de "
    "daglijsten blijven historisch opvraagbaar en een vastgelopen afwikkeling is naderhand nog "
    "te repareren. TWEE DUELS STAAN OP GEEN ENKELE DAGLIJST en dat is een echte bronlacune, geen "
    "naamprobleem: Levante – Athletic Club (16 sep, La Liga) en Red Bull New York – St. Louis "
    "City (26 sep, MLS) zijn op hun eigen dag én de dag erna afwezig, onder welke naam dan ook. "
    "Idem de vier FA Cup-kwalificatieduels van 3 okt. Die zeven blijven onafgewikkeld.")

bij("the_odds_api", "ok",
    "Run B 5 okt: api_check.py geeft 48 actieve voetbalcompetities en 19.901 van de 20.000 "
    "credits over (99 deze maand). Sleutel niet afgewezen. 3 credits uitgegeven: één "
    "bulk-aanroep (h2h + spreads + totals) voor soccer_spain_segunda_division, de enige spelende "
    "competitie met een sportkey; quota daarna 19.898. Stap 2 (BTTS per duel) is niet gezet — "
    "het enige duel kwam op data_tier NONE uit en heeft dus geen kandidaat-edge (§1a stap 2). De "
    "prijzen zijn opgehaald vóórdat de tier bekend was; dat is de volgorde van §1a (inkopen per "
    "competitie) en die 3 credits zijn daarmee achteraf aan een duel besteed dat niet is "
    "doorgerekend. Geen fout en niet te vermijden zonder de inkoop per duel te doen, wat op een "
    "volle speeldag veel duurder is.")

bij("oddsapi", "ok",
    "Sleutel geaccepteerd (api_check.py 5 okt 2026). Gebruikt voor Segunda División (ESP): 3 "
    "credits.")

bij("betexplorer", "ok",
    "Run B 5 okt: één fixturepagina opgehaald (spain/laliga2, 8 rijen waarvan 1 vandaag), HTTP "
    "200. Het marktgemiddelde is deze run nergens voor gebruikt: §6e (kalibratieblok) en poort 8 "
    "hebben beide een doorgerekend duel nodig en dat was er niet.")

bij("understat", "ok",
    "Run B 5 okt: niet aangeroepen — Segunda División (ESP) zit niet in de vijf competities die "
    "Understat dekt (§4). Status ongewijzigd overgenomen. Geen storing, maar wél de reden dat "
    "deze run geen tweede xG-model had.")

bij("api_football", "missing_key",
    "Met opzet afwezig sinds het besluit van de gebruiker op 27 sep 2026 (§3). Geen gat, geen "
    "actiepunt, niet in de notificatie. api_check.py meldt het onveranderd als feit en dringt "
    "niet aan.")

d["last_run"] = f"{DAG} run-b"
d["updated"] = DAG
d["last_run_bevinding"] = (
    "Run B 5 okt 2026 — nul bets, en de oorzaak ligt vóór de analyse: ÉÉN wedstrijd in het "
    "inzetvenster van de hele runlijst (interlandvenster), en die kwam op data_tier NONE uit. "
    "Drie dingen die een volgende run moet weten. "
    "(1) DE VASTGELOPEN AFWIKKELING VAN HET KALIBRATIELOGBOEK IS GEREPAREERD. Bevinding 3 van "
    "4 oktober stond op 129 onafgewikkelde waarnemingen; bij het begin van deze run waren het "
    "141 (47 wedstrijden over dertien rundagen). Nu 21 (7 wedstrijden). De oorzaak was precies "
    "waar Run B van 4 oktober hem aanwees, maar in DRIE lagen: (a) de aliastabel stond in "
    "tmp-run/ra_names.py, waar een module in scripts/ niet uit kan importeren, dus "
    "settling.DayIndex.lookup koppelde alleen op exacte naam of op de eerste zes letters — dat "
    "bridget 'Swansea' niet naar 'Swansea City' en 'PSG' niet naar 'Paris Saint-Germain'. De "
    "tabel staat nu in scripts/teamnames.py en ra_names.py importeert eruit, zodat er één tabel "
    "is. (b) ctxlog.py _cmd_settle las de index RAUW uit met index._day(...).get(...) en sloeg "
    "de naamkoppeling van DayIndex volledig over — dezelfde faalstand waar de kop van "
    "settling.py voor waarschuwt, nu tussen een module en haar aanroeper; 22 wedstrijden van 9 "
    "sep t/m 3 okt stonden daardoor op pending terwijl ze gespeeld waren. (c) ctxlog.py keek "
    "alleen naar de RUNDATUM, terwijl een wedstrijd sinds 24 sep bij de run hoort wiens "
    "inzetvenster hem kan bedienen: tien MLS-duels van 26 sep en vijf interlands van 2 en 3 okt "
    "staan op de UTC-daglijst van de dag ERNA. Het contextlogboek staat nu op 3 open in plaats "
    "van 23. De 120 nieuw afgewikkelde kalibratiewaarnemingen zijn per stuk tegen de bron "
    "nagelopen: nul afwijkingen. De herijking van §1g loopt nu op 3627 gevallen in plaats van "
    "3507. "
    "(2) HET STRUCTURELE TIER2-GAT IN DE SEGUNDA IS DE VIERDE RUN OP RIJ, en vandaag kostte het "
    "de ENIGE wedstrijd van de run. Córdoba – Tenerife op NONE omdat Tenerife uit de Primera "
    "Federación promoveerde en promotion.TIER2 geen Spaans paar LaLiga2/Primera Federación kent; "
    "2 en 3 okt was het Sabadell, 4 okt Celta Fortuna. Nieuw gemeten vandaag, en het maakt de "
    "vraag scherper: Tenerife heeft inmiddels 7 duels LaLiga2 MÉT xG in het lopende seizoen (6.2 "
    "xG / 8.2 xGA, Fotmob). De data op het juiste niveau bestaat dus; wat ontbreekt is een prior "
    "uit vorig seizoen. Of een lopend seizoen van 7 duels genoeg is om zonder prior door te "
    "rekenen, is een regelwijziging en een besluit van de gebruiker — niet van een run. "
    "(3) DE MEETLAT VAN §1e VOOR POORT 8 STAAT NU OP 36 AFGEWIKKELDE GEVALLEN MET +16,9%. Op 4 "
    "oktober waren het 31 met +12,6%, op 30 september 20. §1e noemt zelf precies deze uitweg: de "
    "poort gaat eruit zodra de reeks laat zien dat hij structureel winnaars tegenhoudt "
    "(positieve ROI over >= 30 afgewikkelde kandidaten). Die drempel is nu met marge gehaald en "
    "de reeks blijft positief. Wat er eerlijk bij hoort: underdog_ruw staat op -8,8% over 17 "
    "(andere populatie, nooit optellen) en de kalibratiefout die de poort afdekt staat nog "
    "(+1,95 pp longshots, -3,80 pp favorieten over 3831 uitkomsten). Deze run voert niets door; "
    "§1e legt de keuze bij de gebruiker. Staat als besluit in het dagrapport.")
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", d["last_run"])
