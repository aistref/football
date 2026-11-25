"""Run A, 25 nov 2026 — bronprobe voor source-health.json (§6b-3).

DERTIEN duels in het inzetvenster over TWEE competities, tegen een woensdagcap van 40: niets
afgekapt. Champions League-speelronde 5 vult de dag, met een midweekse Championship-ronde erbij;
geen beker heeft een ronde.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 13 tegen 13.
De enige bron die niet levert is Understat, en dat is zijn eigen onderhoudspagina — ZEVENDE
rundag op rij voor Run A, en vandaag zonder gevolg omdat geen van zijn vijf competities speelt.
"""

import json, datetime

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:28} {status:12} {detail[:80]}")


note("fotmob", "ok",
     "25 nov (run A): daglijsten 25 en 26 nov opgehaald (51 competities/133 duels en 28/75), en "
     "voor de afwikkeling die van 23 en 24 nov. Standen van twee competities over twee seizoenen "
     "(2025/2026 en 2026/2027), beide met xG in beide seizoenen. Wedstrijdcontext van ALLE "
     "DERTIEN duels opgehaald ZONDER EEN ENKELE FOUT, inclusief Lille - Bayern Munchen dat op "
     "tier NONE uitkwam - dat is wat Stage 4 eist (context VOOR de afkapping, ook voor wat "
     "afvalt). Marktvormfrequenties via marketform.match_block op alle twaalf doorgerekende "
     "duels, 0 fouten. Voorbeschouwingsblokken via preview.match_block op de twee gepubliceerde "
     "duels, 0 fouten. Ook de statuscontrole voor de afwikkeling liep hier langs: St. Louis City "
     "- Los Angeles FC (MLS-playoff) stond op Full-Time en niet op AET, dus scoreStr IS daar de "
     "stand na 90 minuten. ENIGE KANSBRON VAN DEZE RUN, want Understat ligt eruit: alle dertien "
     "duels halen hun kansinput hier, en dat is sinds 19 nov een enkel punt van falen in plaats "
     "van twee (Sec. 4). Kost geen credits.")

note("the_odds_api", "ok",
     "25 nov (run A): api_check.py meldt OK, 46 actieve voetbalcompetities, quota 18984 over en "
     "1016 verbruikt deze maand, 33 van 34 sportkeys actief (alleen soccer_france_ligue_two niet, "
     "en Ligue 2 staat niet op de runlijst van Run A). Plafond suggest_cap(18984, 6) = 1580; BEIDE "
     "spelende competities kregen de VOLLEDIGE bulk-aanroep (h2h + spreads + totals, 3 credits "
     "elk = 6). Tweede ronde BTTS voor de negen duels met een kandidaat-edge: 9 credits. TOTAAL "
     "15 van 1580, 18969 over met zes dagen tot de maandwissel. Nul fouten in store['errors']. "
     "Vijf actieve sportkeys die de repo niet kent (soccer_brazil_serie_b, "
     "soccer_england_efl_trophy, soccer_germany_liga3, soccer_sweden_superettan, "
     "soccer_uefa_nations_league) - geen van vijf staat op de runlijst van Run A.")

note("betexplorer", "ok",
     "25 nov (run A): fetch_league_fixtures voor alle 22 competities van de runlijst, inclusief "
     "de veertien zonder wedstrijd en de zes bekers. 22 VAN 22 EENS MET FOTMOB, 13 duels tegen "
     "13, en ook per competitie gelijk: Champions League 9-9 en Championship 4-4. Dat is de "
     "bevestiging door een tweede methode van Sec. 1, op de vraag WELKE wedstrijden er zijn. "
     "Levert daarnaast het gratis 1X2-marktgemiddelde voor het kalibratieblok van Sec. 6e en voor "
     "poort 8 (Sec. 1a: gemiddelde om te METEN, beste prijs om te SPELEN); 8 boeken bij de "
     "Championship, 16 bij de Champions League. Nul fouten. Uit dezelfde pagina's komt ook de "
     "eerstvolgende ronde van de zes bekers buiten de runlijst: 1 dec (Coppa Italia, DFB Pokal), "
     "4 dec (FA Cup) en 15 dec (League Cup); Copa del Rey en KNVB Beker hebben er geen staan.")

note("understat", "http_503",
     "25 nov (run A): ZEVENDE RUNDAG OP RIJ ERUIT. getLeagueData geeft HTTP 200 met een "
     "onderhoudspagina (26.719 bytes, geen JSON) voor EPL, Serie_A en La_liga. Zelfde respons en "
     "zelfde bytegrootte als op 19 t/m 24 november, dus geen nieuwe storing maar een "
     "voortdurende - vermoedelijk een permanent gewijzigde route of een blokkadepagina. NIET "
     "OMZEILD (Sec. 3, 'Niet doen': geen headless browser, geen challenge-solver, geen proxy). "
     "VANDAAG ZONDER FEITELIJK GEVOLG, en dat hoort erbij te staan: geen van Understats vijf "
     "competities (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) speelt vandaag, dus ook "
     "een werkende Understat had aan geen enkel duel van deze run iets toegevoegd. WEL: "
     "p_xg_understat blijft leeg in het kalibratieblok van Sec. 6e, dus de reeks die moet "
     "uitwijzen of het ene xG-model beter voorspelt dan het andere groeit voor de zevende rundag "
     "niet. GEEN gevolg voor my_prob, de tiers of de poorten. Dit is dus GEEN geval van de "
     "uitzondering in Sec. 3 punt 3 (die gaat over Fotmob) en hoort niet vooraan in de "
     "notificatie. Staat als openstaand punt in het dagrapport met owner = 'ik'.")

note("interleague_kruis_grens", "ok",
     "25 nov (run A): TWEEDE VOLLE KRUIS-GRENSDAG OP RIJ, en de module deed opnieuw wat Sec. 4 "
     "(8 sep 2026) van hem vraagt. interleague.convert_team op het laatst AFGERONDE seizoen "
     "(2025/2026) voor alle 18 ploegen van de negen Champions League-duels. ACHT van de negen "
     "duels kwamen door de omrekening heen en staan daarmee op LIGHT - nooit FULL, dat is de "
     "regel en geen aantekening. EEN OP NONE: Lille - Bayern Munchen, want Bayerns omgerekende "
     "AANVAL komt op 2,742 uit en dat valt BOVEN het gemeten bereik van 0,585-2,432 (in_range, "
     "Sec. 4 punt 3 - dezelfde Coventry-val als bij promotion.conversion_in_range). Dat is de "
     "spiegel van gisteren, toen Arsenal op de VERDEDIGINGSvloer van 0,388 strandde. Stil "
     "terugvallen op factor 1,0 is wat deze module wegneemt. WAT OPVALT EN IN HET RUNRAPPORT "
     "STAAT: beide gepubliceerde regels komen uit deze acht duels, terwijl de lat daar op het "
     "DUBBELE staat (16,0 pp), en het zijn exact de twee duels waar het model het verst van "
     "Pinnacle af zit. Dat is het patroon waar Sec. 4 punt 4 voor waarschuwt.")

note("pinnacle_via_odds_api", "ok",
     "25 nov (run A): Pinnacle zat bij 12 duels in de 1X2-respons en bij 12 (duel, lijn)-paren in "
     "de doelpuntenrespons, met een gemiddelde marge van 3,49 procent tegen 6 tot 10 procent bij "
     "de rest. Gebruikt als TOETS naast de eigen kans (Sec. 3 Stage 5 stap 2), nooit in my_prob "
     "of prob_sources (Sec. 2). Gemiddelde absolute afstand tot het Pinnacle-1X2-oordeel 5,99 pp. "
     "OP DE DOELPUNTENKANT STAAT HET MODEL GEMIDDELD +3,11 pp BOVEN PINNACLE OP P(UNDER), 8 van "
     "12 erboven, en op de drie zuivere halve lijnen +9,53 pp. DE TWEE GROOTSTE AFWIJKINGEN VAN "
     "DE DAG ZIJN DE TWEE GEPUBLICEERDE DUELS, en de eerste is de grootste die deze vergelijking "
     "tot nu toe gaf: Paris Saint-Germain - Roma +27,93 pp (model 73,7 tegen Pinnacle 45,8 "
     "procent) en Atletico Madrid - Viking +16,34 pp (63,5 tegen 47,2). Daaronder Sabah - "
     "Barcelona +10,12; aan de andere kant Shakhtar - Fenerbahce -15,53 en Bolton - West "
     "Bromwich Albion -13,29. OP DE UITSLAGMARKT WIJST HET DEZELFDE KANT OP: Atletico -26,83 pp "
     "op de thuiszege (model 60,2 tegen Pinnacle 87,0) en PSG -17,96 pp (48,6 tegen 66,6). Het "
     "model houdt de favoriet op die twee avonden dus veel minder sterk dan de scherpste markt, "
     "en dat is dezelfde afwijking als te weinig doelpunten verwachten.")

note("forebet", "http_403",
     "Niet opnieuw geprobeerd op 25 nov (run A): bekende Cloudflare-blokkade, status overgenomen "
     "conform Stage 3. Wordt bewust niet omzeild.")

note("pinnacle_articles", "http_404",
     "Niet opnieuw geprobeerd op 25 nov (run A): /betting-articles/soccer/ bestaat sinds 20 sep "
     "2026 niet meer. De PRIJS van Pinnacle komt via The Odds API binnen en vult stap 2 van "
     "Stage 5 wel; zie pinnacle_via_odds_api. Vandaag is dat ook de koers van de BOVENSTE regel: "
     "Paris Saint-Germain - Roma, Under 3,5 @2,12 bij Pinnacle.")

note("matchbook_blog", "http_530",
     "Niet opnieuw geprobeerd op 25 nov (run A): server lag er op 20 sep uit, status overgenomen "
     "conform Stage 3. De KOERSEN van Matchbook komen wel binnen via The Odds API, inclusief de "
     "2 procent beurscommissie van oddsapi.net_price - vandaag staat Matchbook bij Sporting CP - "
     "Manchester United op de beste gelijkspelprijs (4,00 bruto, 3,94 netto), maar GEEN van de "
     "twee gepubliceerde koersen komt van een beurs: Pinnacle en Coolbet zijn gewone bookmakers, "
     "dus bruto is daar gelijk aan netto.")

note("betfair_blog", "http_403",
     "Niet opnieuw geprobeerd op 25 nov (run A): Cloudflare, status overgenomen conform Stage 3. "
     "De KOERSEN van Betfair komen wel binnen via The Odds API, inclusief commissie, en vandaag "
     "leveren ze de beste prijs op elf van de dertien 1X2-selecties van de Championship.")

note("kwartlijn_halve_uitkomst", "ok",
     "25 nov (run A): DERDE KEER IN ZES DAGEN, EN WEER GOED GEBOEKT. De pick van 24 nov op RB "
     "Leipzig - Lens stond op UNDER 3,75 en het werd 3-1, oftewel vier doelpunten. Een kwartlijn "
     "valt uiteen in twee halve bets (3,5 en 4,0): de 3,5-helft verliest, de 4,0-helft is een "
     "PUSH, dus de netto uitkomst is -0,50u en niet -1,00u. Geboekt met ledger.py settle --units "
     "-0.5. Zonder die correctie zou het dagresultaat van Stage 0 +1,107u zijn in plaats van "
     "+1,607u. Eerdere gevallen: 18 nov Cruzeiro - Palmeiras, 20 nov Vitoria - RB Bragantino, "
     "24 nov Wieczysta Krakow - Motor Lublin. LET OP HET ANDERE GEVAL VAN VANDAAG, dat GEEN "
     "kwartlijn is: Bradford City - Barnsley stond op UNDER 3 (een HELE lijn) en werd 3-0, dus "
     "exact drie doelpunten - dat is een volledige push en is als void geboekt, niet als halve "
     "uitkomst. OPENSTAAND PUNT ONGEWIJZIGD: er is nog geen script dat de boeking van kwartlijnen "
     "nacontroleert, en of een afwikkeling achteraf mag worden bijgesteld is een vraag voor de "
     "gebruiker (zie het runrapport van 20 nov).")

note("branchaudit", "ok",
     "25 nov (run A): 99 takken nagelopen met scripts/branchaudit.py, per record op de inhoud. DE "
     "CONTAINER KREEG DE REPO OPNIEUW ALS ONDIEPE KLOON en dat gaf eerst het valse alarm dat "
     "Sec. 3 Stage -2 beschrijft: 87 van de 99 takken leken 27 tot 730 eigen commits te hebben "
     "terwijl hun merge-base met main leeg was. Na git fetch --unshallow origin staat main op 794 "
     "commits en heeft GEEN ENKELE tak nog een eigen commit. picks.jsonl (597), "
     "context-log.jsonl (2560), calibration.jsonl (9139) en coverage.json (339) staan op "
     "VOLLEDIG. shadow.jsonl meldt vier ontbrekende rijen (Canada - Peru, Croatia - England, "
     "Estonia - Luxembourg, Switzerland - Slovenia van 3 okt) en die blijven BEWUST weg: het zijn "
     "de dubbeltellingen die Run D op 7 nov heeft verwijderd. source-health.json meldt elf "
     "bladpaden en ALLE ELF STAAN AL OP MAIN, genest in last_run_run_b.history (19 nov en 8 nov) "
     "en last_run_run_c.detail_history (14 nov); het pad-gewijze oordeel ziet die nestlaag niet "
     "omdat een LIJST daar een blad is. Per naam in het bestand nagemeten. Er viel dus niets te "
     "verenigen en dit bestand is op dat punt niet aangeraakt.")

H["last_run"] = now
H["last_run_bevinding"] = (
    "25 nov 2026, Run A — TWEE BEVINDINGEN. (1) BEIDE GEPUBLICEERDE REGELS STAAN OP DE TWEE "
    "DUELS WAAR HET MODEL HET VERST VAN PINNACLE AF ZIT, en bij Paris Saint-Germain - Roma is "
    "dat +27,93 pp op P(Under 3,5) - de grootste afstand die deze vergelijking tot nu toe gaf. "
    "Beide duels zijn kruis-grensduels op LIGHT en beide regels wedden op MINDER doelpunten, de "
    "kant waar margins.py goalbias vandaag op z = +4,99 staat over 150 duels (+0,677 doelpunt "
    "per duel meer dan de eigen lambda zei) - de scherpste stand die die meting ooit gaf. Op de "
    "uitslagmarkt wijst het dezelfde kant op: het model houdt Atletico en PSG veel minder sterk "
    "dan Pinnacle (-26,83 en -17,96 pp op de thuiszege). Het MODEL zelf staat goed (+0,020 "
    "doelpunt per duel over 2478 duels, z = +0,56); het is de SELECTIE die scheef staat. En de "
    "marktvormtelling spreekt de bovenste regel vlak tegen: PSG kwam in vier Champions "
    "League-duels van dit seizoen op 6,25 doelpunt per duel uit en bleef geen enkele keer onder "
    "3,5. Niets aangepast - de regels staan zoals ze staan en dit is een dag, geen reeks. "
    "(2) DE VROEG-SEIZOENSCORRECTIE KWAM UIT EEN POOL VAN EEN COMPETITIE (factor 1,0856, "
    "Championship, 17 speeldagen), omdat de Champions League halverwege zijn leaguefase staat en "
    "uit de pool valt. Een factor uit een pool van een is niet meer competitie-overstijgend maar "
    "de gemeten verhouding van die ene competitie; het raakte vier duels en geen enkele bet. "
    "Gemeld omdat het een versmalling is die niet opvalt als niemand hem opschrijft."
)
# Het blok van de vorige Run A gaat GEDATEERD naar de historie in plaats van te worden
# overschreven (§3 Stage -2: source-health is een meting en metingen worden verenigd).
_prev_a = H.get("last_run_run_a") or {}
_hist_a = H.get("last_run_run_a_history") or []
if _prev_a:
    _hist_a = [{"date": _prev_a.get("date"),
                "note": f"Tekstblok van Run A van {_prev_a.get('date')}, bewaard bij het "
                        f"bijwerken van {now[:10]}.",
                "blok": _prev_a}] + _hist_a
H["last_run_run_a_history"] = _hist_a[:6]
H["last_run_run_a"] = {
    "run": "A", "date": "2026-11-25",
    "matches_in_window": 13, "analysed": 12, "truncated": 0, "bets": 2,
    "qualified_not_published": 0,
    "credits": "15 van een plafond van 1580 (6 bulk voor 2 competities + 9 BTTS); 18.984 over, "
               "1016 gebruikt deze maand bij het begin van de run",
    "bevinding": H["last_run_bevinding"],
    "sources_deze_run": {
        "fotmob": "ok; daglijsten 25+26 nov, standen 2 competities x 2 seizoenen, context 13/13 "
                  "zonder fout, marktvorm 12/12, voorbeschouwing 2/2",
        "the_odds_api": "ok, 46 actief, 18984 over, 15 credits verbruikt (6 bulk + 9 BTTS)",
        "betexplorer": "ok; 22 van 22 fixturepagina's, 13 tegen 13 duels eens met Fotmob, plus "
                       "het gratis 1X2-marktgemiddelde (8 resp. 16 boeken)",
        "understat": "http_503, zevende rundag op rij; vandaag zonder gevolg, geen van zijn vijf "
                     "competities speelt",
        "api_football": "niet beschikbaar; besluit van de gebruiker 27 sep 2026, geen gat en geen "
                        "actiepunt (Sec. 3 Stage 3)",
        "pinnacle": "ok; 12 duels 1X2 en 12 (duel, lijn)-paren totalen, marge 3,49 procent",
    },
    "note": "TWEE van de ZESTIEN competities van de runlijst spelen in het venster "
            "[08:00 NL 25 nov, 08:00 NL 26 nov): Champions League 9 duels (speelronde 5) en "
            "Championship 4. Veertien op GEEN WEDSTRIJD, de zes bekers op BUITEN DE RUNLIJST "
            "(cups.py, besluit 18/19 nov) en geen van de zes speelt vandaag werkelijk. "
            "Woensdagcap 40, niets afgekapt; datarijkdom 5,5 tot 8,5. EEN duel op NONE "
            "(Lille - Bayern Munchen, omgerekende aanval 2,742 boven het gemeten bereik). "
            "181 selecties doorgerekend, 2 door alle poorten; poort 5 ving er 117 weg (65%), "
            "poort 7 hield de hoogste FULL-edge van de dag tegen (Millwall bij Stoke City, "
            "+13,92 pp, 69% van de selectiewaarde afwezig). MAX_SHORTLIST is 2 op woensdag; een "
            "gekwalificeerde selectie en twee plekken, dus de lijstlengte bindt niet en de tweede "
            "regel staat er op rangorde (Sec. 5b) onder zijn eigen lat van 16,0 pp.",
}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")
