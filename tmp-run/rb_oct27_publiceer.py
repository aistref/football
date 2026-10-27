"""Run B 27 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct25_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. VIJF van de zeventien competities speelden, met samen VIJFTIEN
duels in het inzetvenster en nul afgekapt (cap 40 op dinsdag). DRIE gepubliceerde regels, waarvan
er ÉÉN zijn eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Pinnacle spreekt de bovenste regel hard tegen.** Op 1X2 staat het model +15,71 pp boven
  Pinnacle op de Cesena-kant — de grootste afstand van de acht toetsbare duels.
* **Twee van de drie regels staan op de minder-doelpunten-kant**, en dat is de kant waarvan §6g
  meet dat ze fout staat. Poort 9 raakt geen van beide, want beide liggen ónder de band 8–10 pp
  waarin die rem werkt.
* **Zes van de vijftien duels komen op `NONE` uit**, allemaal door de omrekening van §4: drie
  Italiaanse promovendi uit de Serie C waarvoor geen divisiepaar is gemeten, en drie Engelse
  ploegen waarvan de omgerekende sterkte buiten het gemeten bereik valt.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-27"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026, dus +01:00
CAPTURED = "2026-10-27T04:05:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), wintertijd


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def state_uit(res, run):
    st = {"date": DAG, "run": run, "competitions": {}}
    for m in res["matches"]:
        st["competitions"].setdefault(m["competition"],
                                      {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)
    return st


def bouw(run, pad):
    res = json.load(open(pad))
    st = state_uit(res, run)
    top = toplist.build(st)
    idx = {m["match"]: m for m in res["matches"]}
    picks = []
    for r in top["herijkt"]:
        m = idx[r["match"]]
        home, away = r["match"].split(" – ", 1)
        cand = next((c for c in m["all_candidates"]
                     if c["market"] == r["market"] and c["selection"] == r["selection"]), {})
        bronnen = m.get("prob_sources") or cand.get("prob_sources") or []
        if not bronnen:
            lam = (m.get("lambdas") or {}).get("xg") or []
            bronnen = [
                f"Fotmob team-xG {m['competition']} — gewogen over vorig en lopend seizoen "
                f"(§4 blend_seasons); doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                if len(lam) == 2 else f"Fotmob team-xG {m['competition']}",
                f"Fotmob thuis/uit-splits {m['competition']} (tweede methode, §1d)",
                "Fotmob wedstrijdcontext: opstelling, uitvallers met marktwaarde, vorm en rustdagen",
            ]
        picks.append({
            "id": f"{DAG}-{slug(m['competition'])}-{slug(home)}-{slug(away)}-{slug(r['market'])}-{slug(r['selection'])}",
            "run": run, "run_date": DAG, "kickoff": m["kickoff_utc"],
            "competition": m["competition"], "home": home, "away": away,
            "market": r["market"], "selection": r["selection"], "odds": r["odds"],
            "odds_source": r["odds_source"], "odds_captured_at": CAPTURED,
            "implied_prob": round(1 / r["odds"], 4), "my_prob": r["prob"],
            "edge_pp": r["edge_pp"], "data_tier": r["tier"],
            "confidence": "Medium" if r["tier"] == "FULL" else "Low",
            "prob_sources": bronnen, "shortlisted": True, "result": "pending",
            "notes": (f"Gepubliceerd op rangorde (§5b): plek {top['herijkt'].index(r)+1} van "
                      f"{len(top['herijkt'])} over {len(res['matches'])} doorgerekende wedstrijden. "
                      f"{r['status']}. selection_score {r['score']}. "
                      f"Ruwe kans {cand.get('my_raw')}, ruwe edge {cand.get('edge_raw')} pp; "
                      f"xG-methode {cand.get('edge_xg')} pp, splitsmethode {cand.get('edge_split')} pp, "
                      f"zwakste stand van het (shrink, rho)-grid {cand.get('edge_robust_min')} pp. "
                      f"shrink staat sinds 19 sep op 1.00 (§6e)."
                      + (" poort8_zou_hebben_geblokkeerd: JA — deze selectie staat op de "
                         "underdog-kant onder UNDERDOG_FLOOR (0.35). Let op: de poort BINDT "
                         "sinds 1 okt 2026 weer (§1e), dus zo'n selectie kan geen gepubliceerde "
                         "bet meer zijn; staat deze regel er toch, dan is er iets mis met de "
                         "poortvolgorde en hoort dat uitgezocht."
                         if cand.get("poort8_vervallen") else "")),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct27_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.983, b=-0.011 "
                "op 6060 afgerekende gevallen, fitted_through 2026-10-26. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die Sec. 6b-5c sinds 30 sep "
                "eist). DE CORRECTIE IS OPNIEUW VRIJWEL DE IDENTITEIT, aan de licht verlagende kant: "
                "-0,4 pp op 50%, -0,5 pp op 60% en -0,7 pp op 70% — het ruwe model zei gemiddeld 33,3% "
                "en het gebeurde 33,3%. Op de drie gepubliceerde regels haalt ze tussen 0,4 en 0,5 pp "
                "van de kans af. bet_beide is TRUE bij de bovenste regel (Cesena, ruw +12,06 pp tegen "
                "herijkt +11,68 pp, beide boven 8,0) en FALSE bij de twee andere, omdat die hun lat op "
                "geen van beide schalen halen en puur op rangorde staan. Lees die identiteit zoals Sec. "
                "1e punt 3 voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de "
                "staart waarop deze routine speelt. Dat ze bijna niets corrigeert betekent niet dat er "
                "niets scheef staat."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "VIJF VAN DE ZEVENTIEN COMPETITIES SPELEN, met samen VIJFTIEN duels in het "
                "inzetvenster. Per competitie: Serie B 7, English League One 5, Allsvenskan 1, Croatian "
                "HNL 1 en English League Two 1. TWAALF COMPETITIES OP `GEEN WEDSTRIJD`: Czech First "
                "League, Greek Super League, Eliteserien, Hungarian NB I, Romanian SuperLiga, Segunda "
                "Division, 2. Bundesliga, Swiss Super League, Austrian Bundesliga, Keuken Kampioen "
                "Divisie, MLS en Serie A (BRA) — de Europese competities spelen in het weekend, "
                "Eliteserien en MLS hebben hun eerstvolgende ronde op 29 oktober en Brazilie op 3 "
                "november. Dat is geen gat (Sec. 3 Stage 2). scripts/idcheck.py gaf voor alle 33 "
                "fotmob_id\'s uit coverage.json een bruikbare stand (afsluitcode 0), ook voor de twaalf "
                "competities die vandaag stil zijn — dat is precies de controle die op naam noch op "
                "uitkomst zou zijn opgevallen. De tweede bron bevestigde de daglijst voor 17 van de 17 "
                "competities (BetExplorer tegen Fotmob, 15 duels tegen 15, geen enkele afwijking)."
            ),
            "DE_CAP_BINDT_VANDAAG_NIET": (
                "MAX_DEEP_ANALYSES = 40 (dinsdag) EN ER STAAN 15 DUELS, DUS ER IS NIETS AFGEKAPT en de "
                "dekkingstabel heeft geen AFGEKAPT-regel. De datarijkdom over de hele run loopt van 4,5 "
                "(Dinamo Zagreb - Rijeka) tot 6,5 (Milton Keynes Dons - Bromley en Oxford United - "
                "Stockport County); omdat er niets afvalt zijn er geen twee getallen rond de capgrens te "
                "noemen. De looptijd is daarmee vandaag ook niet de grens: 19 van 1863 credits gebruikt "
                "en 15 duels doorgerekend, ruim binnen de 06:30 van Sec. 0."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "DRIE REGELS, WAARVAN ER PRECIES EEN ZIJN EIGEN LAT HAALT EN TWEE OP RANGORDE OP DE "
                "LIJST STAAN (Sec. 5b). Boven de lat van 8,0: alleen CESENA - EMPOLI, 1X2 Cesena wint "
                "@2,27 met +11,68 pp. Eronder, en dus puur op rangorde: Luton Town - Doncaster Rovers "
                "Under 3,5 @1,6272 (+5,05 pp) en Virtus Entella - Avellino \'beide ploegen scoren - "
                "nee\' @1,9212 (+5,26 pp). Van de 123 doorgerekende selecties over 15 duels haalden er "
                "TWEE alle negen poorten inclusief de drempel, en die twee zijn DEZELFDE WEDSTRIJD "
                "(Cesena - Empoli: het 1X2 op score 6,51 en de Asian Handicap -1 op 3,70 - twee "
                "uitdrukkingen van een mening, Sec. 1a). Er is dus EEN duel dat de volle lat haalt. Er "
                "passen drie regels in de dinsdaglijst, dus de drempel bindt vandaag niet als grens "
                "maar staat als label per regel. Lees de lijst als \'dit is het sterkste dat het model "
                "vandaag ziet\' en niet als \'hier ligt waarde\'."
            ),
            "PINNACLE_SPREEKT_DE_BOVENSTE_REGEL_HARD_TEGEN": (
                "DIT IS DE ZWAARSTE WAARSCHUWING VAN DEZE RUN EN ZE HOORT VOORAAN. STAP 2 VAN STAGE 5 - "
                "het scherpste publieke expertoordeel, LOS van de beste prijs waarop gespeeld wordt en "
                "nooit in my_prob (Sec. 2). Pinnacle noteerde 8 van de 15 duels op 1X2; de zeven andere "
                "zijn niet te toetsen (zes op tier NONE plus Dinamo Zagreb - Rijeka, uit de enige "
                "competitie zonder sportkey). OP 1X2 STAAT HET MODEL GEMIDDELD 4,17 pp VAN PINNACLE AF "
                "bij een gemiddelde Pinnacle-marge van 4,31%. BIJ DE BOVENSTE REGEL IS DIE AFSTAND DE "
                "GROOTSTE VAN DE ACHT: CESENA - EMPOLI staat op 0,589 / 0,237 / 0,174 tegen Pinnacle\'s "
                "0,432 / 0,285 / 0,283 - dus +15,71 pp op de Cesena-kant, -4,74 op het gelijkspel en "
                "-10,96 op Empoli. De scherpste bookmaker van de markt vindt Cesena dus 43% en het "
                "model 59%, en de hele bet bestaat uit dat verschil. Sec. 1g is er onomwonden over dat "
                "de bookmaker gemiddeld scherper schat dan dit model, en dat het rendement het slechtst "
                "is bij de hoogste geclaimde edge. OP DE TOTALEN: 8 (duel, lijn)-paren, gemiddeld +3,12 "
                "pp boven Pinnacle op de Under-kant met 6 van de 8 erboven. Dat raakt de tweede regel "
                "rechtstreeks: LUTON TOWN - DONCASTER ROVERS staat op Pinnacle\'s eigen lijn van 3,00 op "
                "+9,54 pp boven Pinnacle aan de Under-kant, de grootste van de acht paren. De "
                "gepubliceerde regel staat op de 3,5-lijn, een andere lijn en dus een andere bet, maar "
                "de richting is dezelfde. Uitgesplitst naar vorm: de zes lijnen MET push staan "
                "gemiddeld +4,16 pp boven Pinnacle en de twee zuivere halve lijnen op +0,02 pp - "
                "dezelfde tweedeling als de afgelopen dagen."
            ),
            "TWEE_VAN_DE_DRIE_REGELS_STAAN_OP_DE_MINDER_DOELPUNTEN_KANT": (
                "EEN UNDER EN EEN \'BEIDE PLOEGEN SCOREN - NEE\': TWEE VAN DE DRIE REGELS WEDDEN OP "
                "MINDER DOELPUNTEN, EN DAT IS PRECIES DE KANT WAARVAN Sec. 6g MEET DAT ZE FOUT STAAT. "
                "Het logboek staat daar op Under 76 picks / -16,5% tegen Over 62 picks / +10,6%, met "
                "twee gemeten oorzaken: een vormfout in het scoregrid die P(Under) bij elk duel 1,6 tot "
                "2,4 pp te hoog zet, en een selectie-effect daarbovenop. GEEN VAN DE TWEE WORDT DOOR "
                "POORT 9 GERAAKT, en dat is geen toeval maar het ontwerp: beide komen niet aan de 8,0 "
                "(+5,05 en +5,26 pp) en liggen dus ONDER de band 8-10 pp waarin de poort werkt. POORT 9 "
                "HEEFT VANDAAG GEEN ENKELE SELECTIE TEGENGEHOUDEN: er was geen enkele FULL-Under in die "
                "band. Dat is de keerzijde van Sec. 5b die Sec. 6g ook noemt - sinds 20 september worden "
                "regels gepubliceerd die helemaal onder de drempel liggen, en daar meet Sec. 6g -34,1% "
                "over 26 gevallen, terwijl de rem alleen de band 8-10 pp pakt. DIT IS GEEN REDEN OM "
                "VANDAAG EEN DREMPEL OF EEN POORT TE VERZETTEN (Sec. 1h en Sec. 6d verbieden dat "
                "uitdrukkelijk); het is de waarneming die bij deze twee regels hoort. Het BTTS-geval "
                "valt per ontwerp buiten poort 9 (Sec. 1h punt 2: vijftien afgewikkelde BTTS-picks in "
                "beide richtingen samen is geen meting)."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 89 VAN DE 123 SELECTIES WEG (72,4%) - \'tweede_methode\', de twee "
                "methodes verslaan de markt niet dezelfde kant op. Daarna 13 op poort 8 (10,6%), 12 op "
                "de edge (9,8%), 5 op poort 7 (4,1%), 1 op robuustheid (0,8%) en 1 op de koersband "
                "(0,8%). TWEE selecties kwamen door alles heen, en het zijn twee uitdrukkingen van "
                "hetzelfde duel. Die 72,4% ligt in dezelfde band als de afgelopen weken en voegt er "
                "geen nieuwe waarneming aan toe. LET OP BIJ DE BOVENSTE REGEL: Cesena haalt poort 5 "
                "maar nauwelijks - de xG-methode staat op +14,84 pp en de splitsmethode op +0,94 pp, "
                "dus de tweede methode verslaat de markt met minder dan een procentpunt. De poort "
                "toetst de RICHTING en niet de hoogte (Sec. 1, herzien 11 aug 2026), dus hij staat "
                "terecht open, maar het hoort bij de lezing van deze bet."
            ),
            "POORT7": (
                "BINDT EN HOUDT VIJF SELECTIES TEGEN, ALLE VIJF OP EEN DUEL: AIK - ELFSBORG. AIK mist "
                "51% van de selectiewaarde tegen 0% bij Elfsborg - Kevin Filling en Adrian Helm (beide "
                "injury, terug eind oktober) en Dino Besirovic (injury, \'a few weeks\') - en dat is ruim "
                "boven de drempel van 10 procentpunt verschil. DAT KOST DE TWEEDE REGEL VAN DE RUWE "
                "DAGLIJST: AIK +0,25 @1,8918 staat daar op +7,65 pp met score 4,63, en op de herijkte "
                "schaal zou het 1X2 AIK wint @3,205 (+9,32 pp) de near-miss van het duel zijn geweest. "
                "Die rij gaat als `context` het schaduwlogboek in. STADIONCONTROLE: 15 duels, EEN "
                "ALARM - LR VICENZA - MODENA wordt volgens Fotmob gespeeld in Stadio Romeo Menti "
                "(Vicenza) terwijl het eigen stadion van de genoteerde thuisploeg daar Stadio Comunale "
                "Rino Mercante is. Dat is vermoedelijk een bronfout en geen verplaatsing (Romeo Menti "
                "IS het stadion van LR Vicenza; Rino Mercante hoort bij Bassano), maar Sec. 1c eist dat "
                "een alarm wordt genoemd ook als de poort opengaat - en dat is hier het geval, want het "
                "duel staat hoe dan ook op tier NONE. OPSTELLINGEN: 14 van de 15 op \'lastStarting11\' en "
                "1 op \'unavailable\' - de gewone klokbevinding, zestien tot eenentwintig uur voor de "
                "aftrap. De context van ALLE 15 duels is opgehaald en vastgelegd, ook van de zes op "
                "tier NONE, zoals Sec. 1c eist; de steekproef van ctxlog.py is dus volledig."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (Sec. 1e); sides.check() is met "
                "today=2026-10-27 aangeroepen zoals Sec. 1e eist, zodat het vervallen venster van 25 "
                "t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ "
                "HOUDT 13 SELECTIES TEGEN, verdeeld over VIER duels: Padova - Sudtirol, Mantova - "
                "Cremonese, Luton Town - Doncaster Rovers en Oxford United - Stockport County. Op de "
                "RUWE schaal is er GEEN ENKELE poort-8-rij (`poort8_ruw` is leeg): elke kandidaat die "
                "de poort tegenhield, sneuvelde ruw al op een eerdere poort of op de drempel. GEEN VAN "
                "DE DRIE GEPUBLICEERDE REGELS WORDT ERDOOR GERAAKT: de Under en de BTTS hebben side = "
                "None en daar staat de poort per ontwerp open, en Cesena is bij de markt juist de "
                "FAVORIET (Pinnacle 43,2% tegen 28,3% voor Empoli). Dit is geen aanleiding om de vraag "
                "van 25 september opnieuw te stellen (Sec. 1e verbiedt dat zolang er niets wezenlijk "
                "verandert); de stand van beide reeksen staat in het runrapport onder \'Stand van het "
                "logboek\'. Die twee blijven twee populaties en mogen nooit worden opgeteld."
            ),
            "POORT9": (
                "BINDT MAAR HOUDT VANDAAG NIETS TEGEN. `unders.BINDS_FROM` is 12 oktober en "
                "`unders.TIERS` is (\'FULL\',), dus een Under op FULL moet 10,0 pp halen in plaats van "
                "8,0. Er was geen enkele FULL-Under in de band 8-10 pp: de sterkste FULL-Unders van de "
                "dag staan op +5,85 pp (Luton Town - Doncaster Rovers, lijn 3,0), +5,05 pp (dezelfde "
                "wedstrijd, lijn 3,5, de gepubliceerde regel) en +4,61 pp (Padova - Sudtirol, lijn "
                "2,5), allemaal onder de 8,0 waar de rem begint. De reeks `doelpunten_onder` groeit "
                "vandaag dus niet; ze stond bij de vorige lezing nog ver onder de ~30 afgewikkelde "
                "gevallen die Sec. 6d eist, en Sec. 1h waarschuwt zelf dat die reeks ongeveer een rij "
                "per twee dagen oplevert. Dat de twee minder-doelpunten-regels van vandaag ONDER de "
                "band liggen waarin de rem werkt, is precies het gat dat in de waarschuwing hierboven "
                "staat."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0743 (gepoold 1,0917 over 34 "
                "speeldagen) EN RUST OP DRIE COMPETITIES: Serie B, English League One en English League "
                "Two. uplift_observations sloeg er TWEE over, beide met reden, en dat staat hier omdat "
                "een stil weggelaten waarneming hetzelfde probleem is als een stille truncatie (Sec. 3 "
                "Stage 5): CROATIAN HNL wegens \'geen xG in vorig of lopend seizoen\' en ALLSVENSKAN "
                "wegens \'halverwege het seizoen\' (25 van 30 speeldagen). Allsvenskan krijgt daarmee "
                "route \'lopend\' van league_level en haalt zijn niveau rechtstreeks uit het lopende "
                "seizoen, ongeschaald: thuis 1,595 / uit 1,325 / basis 1,471. De vier andere spelende "
                "competities krijgen route \'vorig+uplift\': Croatian HNL 1,570 / 1,289 / 1,440 (op "
                "doelpunten, want geen xG), Serie B 1,597 / 1,153 / 1,334, English League One 1,588 / "
                "1,238 / 1,400 en English League Two 1,475 / 1,294 / 1,370. ALLE DRIE DE GEPUBLICEERDE "
                "REGELS KOMEN UIT DE UPLIFT-ROUTE (twee in de Serie B, een in English League One) en "
                "worden door de factor 1,0743 rechtstreeks geraakt. EEN POOL VAN DRIE IS EEN KLEINE "
                "POOL en dat hoort erbij te staan - de factor is vandaag op 34 speeldagen gemeten tegen "
                "57 gisteren."
            ),
            "BEURSKOERS": (
                "TWEE VAN DE DRIE GEPUBLICEERDE REGELS STAAN OP EEN BEURS en daar is met "
                "oddsapi.net_price gerekend zoals Sec. 1a eist: LUTON TOWN - DONCASTER ROVERS Under 3,5 "
                "staat bij MATCHBOOK op 1,64 bruto, na 2% commissie 1,6272; VIRTUS ENTELLA - AVELLINO "
                "\'beide ploegen scoren - nee\' bij MATCHBOOK op 1,94 bruto, na commissie 1,9212. Dat "
                "zijn de koersen waarmee edge_pp en selection_score rekenen. Sec. 5 eist beide getallen "
                "naast elkaar omdat de gebruiker op de site de brutokoers ziet. De bovenste regel staat "
                "bij een gewone bookmaker zonder commissie: CODERE (IT) 2,27 voor Cesena. Elke koers "
                "van de run is door net_price gehaald voordat er edge op is gemeten."
            ),
            "ZES_VAN_DE_VIJFTIEN_DUELS_OP_NONE_DOOR_DE_OMREKENING": (
                "DIT IS DE VORM VAN DEZE DAG EN HET IS GEEN STORING. NEGEN van de vijftien duels hebben "
                "een ploeg zonder stand in 2025/2026 en gaan langs de omrekening van Sec. 4; ZES "
                "daarvan komen op NONE uit en zijn dus niet doorgerekend. DRIE WEGENS EEN ONTBREKEND "
                "DIVISIEPAAR: Benevento, Ascoli en LR Vicenza zijn promovendi uit de Serie C, en "
                "promotion.TIER2 heeft geen divisie onder Serie B - er is dus geen gemeten factor, net "
                "zoals bij een Braziliaanse promovendus (Sec. run-b.md). York City is hetzelfde geval in "
                "Engeland: onder League Two staat de National League niet in de kaart. DRIE WEGENS "
                "BUITEN HET GEMETEN BEREIK (conversion_in_range): Leicester City (aanval 0,968 buiten "
                "0,473-0,939 voor E1/E2 down) en Cambridge United (verdediging 0,557 net buiten "
                "0,565-1,068 voor E2/E3 up) - en bij dat laatste duel was Sheffield Wednesday zelf WEL "
                "om te rekenen. DRIE OMREKENINGEN SLAAGDEN WEL en leverden LIGHT: Cremonese "
                "(degradant uit de Serie A), Milton Keynes Dons en Bromley (beide promovendus uit "
                "League Two) en Oxford United (degradant uit de Championship). Sec. 4 is er duidelijk "
                "over dat NONE de eerlijke uitkomst is zodra de omrekening aantoonbaar niet kan - niet "
                "\'LIGHT met lage confidence\'."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 27 okt, 08:00 NL 28 okt) en runwindow.py levert VIJFTIEN "
                "duels, alle 15 met RunMatch.playable = True - er is dus geen enkel duel dat al was "
                "afgetrapt voordat de gebruiker kon inzetten. De eerste aftrap is 18:00 NL (Dinamo "
                "Zagreb - Rijeka) en de laatste 20:45 NL (de vijf Engelse duels). GEEN ENKEL DUEL ZIT "
                "VANDAAG IN DE NACHTBAND waarvoor runwindow.py bestaat: MLS en Serie A (BRA) spelen "
                "niet, en RunMatch.source_day staat voor alle vijftien duels op 2026-10-27. "
                "include_carry_over is niet gebruikt (die is eenmalig geweest op 24 september). DE "
                "WINTERTIJD STAAT ERIN: NL is ZoneInfo(\'Europe/Amsterdam\') en dus +01:00, zodat "
                "odds_captured_at en kickoff_nl kloppen - de hardgecodeerde +02:00 is op 25 oktober uit "
                "de runscripten verdwenen."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "17 VAN DE 17 COMPETITIES BEVESTIGD, 15 duels tegen 15. Fotmob levert de daglijst en "
                "BetExplorer de fixturepagina per competitie - twee losse bronnen - en de controle slaat "
                "vandaag ook aan op de TWAALF competities die niets op de kalender hebben: BetExplorer "
                "geeft daar eveneens nul duels in het venster en noemt de eerstvolgende speeldag "
                "(Eliteserien en MLS 29.10., 2. Bundesliga 30.10., Keuken Kampioen Divisie 01.11., "
                "Serie A BRA 03.11.). Dat is juist de kant van de controle die iets kan opleveren, want "
                "een competitie die stil wegvalt door een fout id leest als GEEN WEDSTRIJD; hier zeggen "
                "twee bronnen hetzelfde. Geen enkele afwijking in de aantallen per competitie."
            ),
            "inkoop": (
                "19 CREDITS VAN EEN PLAFOND VAN 1863 (18.652 over bij 5 dagen tot de maandwissel, twee "
                "runs per dag). VIER van de vijf spelende competities hebben een sportkey en kregen "
                "ALLE VIER de volledige bulk-aanroep van 3 credits (h2h + spreads + totals = 12 "
                "credits), dus vijf van de zes markten; daarna 7 credits voor BTTS op de 7 duels met "
                "een kandidaat-edge (Sec. 1a stap 2, de vereniging van beide schalen). DIE TWEEDE RONDE "
                "HEEFT WAT OPGELEVERD: Virtus Entella - Avellino staat op de lijst MET een BTTS, en in "
                "ronde 1 zonder BTTS kwam dat duel als \'data conflicterend\' uit de analyse. EEN "
                "spelende competitie heeft GEEN sportkey - CROATIAN HNL - en draait dus volledig op het "
                "gratis BetExplorer-marktgemiddelde als enige 1X2-bron, zonder enige andere markt. Dat "
                "raakt een duel (Dinamo Zagreb - Rijeka) met drie selecties, alle drie een 1X2, en de "
                "edge valt daar systematisch te laag uit omdat een marktgemiddelde geen beste prijs is "
                "(conservatief, dus geen risico op te veel bets, maar niet vergelijkbaar). Dat die ene "
                "competitie zonder prijzen ook precies de enige zonder xG is, is geen toeval maar "
                "hetzelfde onderliggende feit: het is de kleinste competitie van de dag. "
                "MARKTBALANS-CONTROLE GEHAALD EN ZEER RUIM: vier van de vier inkoopbare competities "
                "kregen zowel een uitkomstmarkt als een doelpuntenmarkt uit dezelfde bulk, dus er is "
                "geen enkele competitie met alleen het een of het ander. split_budget(1863, 4) gaf "
                "(4, 4) en het plafond bond nergens. ALLE ZES MARKTEN DONGEN MEE: Over/Under 34 "
                "selecties, Asian Handicap 33, 1X2 27, BTTS 14, Draw No Bet 12 en Double Chance 3 - en "
                "de drie regels komen uit drie verschillende markten (1X2, Over/Under, BTTS). De "
                "uitkomst van vandaag is dus niet eenzijdig in de markt, al staat ze wel twee van de "
                "drie keer op de minder-doelpunten-KANT; dat verschil is precies wat deze tabel "
                "zichtbaar moet maken (Sec. 5, Marktbalans)."
            ),
        }

        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping op LIJSTLENGTE — bindt vandaag niet (één regel op drie plekken), maar de
        # lus blijft staan: ze is de enige plek waar een gekwalificeerde selectie die niet in de
        # lijst past wordt vastgelegd (`failed_gate = "lijstlengte"`, bewust dezelfde naam).
        alles_op_score = sorted(
            [{"match": m["match"], "score": (m.get("pick") or {}).get("score") or 0.0}
             for m in res["matches"] if m.get("bet")], key=lambda r: -r["score"])
        gepubliceerd_scores = [r["score"] for r in top["herijkt"] if r.get("score") is not None]
        drempel_score = min(gepubliceerd_scores) if gepubliceerd_scores else None
        buiten = 0
        gepubliceerde_duels = {mm for mm, _, _ in gespeeld}
        for m in res["matches"]:
            if not m.get("bet"):
                continue
            pick = m.get("pick") or {}
            if (m["match"], pick.get("market"), pick.get("selection")) in gespeeld:
                continue
            # 7 okt 2026 — DIT IS GEEN LIJSTLENGTE als de wedstrijd zelf wél een regel kreeg.
            # Sinds §5b de edge-drempel uit de poorten heeft gehaald, kiest `toplist.build` de
            # sterkste selectie van een wedstrijd onder de ZEVEN overgebleven poorten, en dat kan
            # een andere zijn dan de selectie die óók de drempel haalde: vandaag staat bij
            # Internacional – Corinthians het 1X2 op +8,04 pp (score 4,127) en de Draw No Bet op
            # +6,64 pp (score 4,515), en `selection_score` geeft de voorkeur aan de hogere
            # trefkans (§1a). Die niet-gekozen selectie is dezelfde mening in een andere markt
            # (§1, 0-of-1-bet), geen gekwalificeerde selectie die door de LIJSTLENGTE afviel —
            # de lijst had vandaag drie plekken voor twee regels. Ze apart boeken zou de reeks
            # `lijstlengte` vervuilen met een vraag die ze niet beantwoordt (§5b, 26 sep 2026).
            if m["match"] in gepubliceerde_duels:
                m["binnen_wedstrijd_niet_gekozen"] = {
                    "selection": pick.get("selection"), "market": pick.get("market"),
                    "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                    "score": pick.get("score"),
                    "reden": ("alle acht poorten open en boven de drempel, maar een andere "
                              "selectie van DEZELFDE wedstrijd scoorde hoger op "
                              "selection_score (§1a); gepubliceerd is die andere"),
                }
                continue
            rang = next((i for i, r in enumerate(alles_op_score, 1) if r["match"] == m["match"]), None)
            m["near_miss"] = {
                "match": m["match"],
                "market": f"{pick.get('market')} — {pick.get('selection')}",
                "odds": pick.get("odds"), "my_prob": pick.get("my_prob"),
                "my_raw": pick.get("my_raw"), "edge_pp": pick.get("edge_pp"),
                "edge_xg": pick.get("edge_xg"), "edge_split": pick.get("edge_split"),
                "edge_robust_min": pick.get("edge_robust_min"),
                "failed_gate": "lijstlengte"}
            m["gekwalificeerd_niet_gepubliceerd"] = {
                "selection": pick.get("selection"), "market": pick.get("market"),
                "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                "score": pick.get("score"), "rang": rang,
                "reden": (f"alle acht poorten open en {pick.get('edge_pp'):+.2f} pp boven de "
                          f"drempel, maar rang {rang} bij MAX_SHORTLIST = "
                          f"{len(top['herijkt'])}; laagste gepubliceerde selection_score "
                          f"{drempel_score}")}
            buiten += 1
        print(f"{buiten} gekwalificeerde selectie(s) buiten de lijst van §5b")

        # 24 okt 2026 — EEN COMPETITIE WAARVAN DE CAP ALLE DUELS HEEFT AFGEKAPT, KRIJGT
        # `AFGEKAPT` EN NIET `GEANALYSEERD`. Sec. 5 geeft vier statussen en eist er precies een per
        # competitie; `AFGEKAPT` is er een van ("wel dekking, maar buiten MAX_DEEP_ANALYSES
        # gevallen"). Op 24 oktober bond dat voor het eerst: 88 duels tegen een cap van 55, en bij
        # Czech First League (4 duels), Croatian HNL (2) en Keuken Kampioen Divisie (1) was er geen
        # enkel duel doorgerekend. Die als GEANALYSEERD neerzetten is precies de stille truncatie
        # die Stage 4 verbiedt: de dekkingstabel leest dan als volledige dekking.
        #
        # GEREPAREERD 25 okt 2026 (Run B), WANT DE REGEL VAN GISTEREN TOETSTE HET VERKEERDE.
        # Hij leidde de status af uit "nul duels met kandidaten", en dat is niet hetzelfde als
        # "afgekapt": een duel krijgt óók geen kandidaten als het op `data_tier = NONE` uitkomt,
        # en dan is de juiste status `BUITEN DATADEKKING` ("wedstrijden vandaag, maar geen
        # werkende onafhankelijke kansbron"). Vandaag kapt de cap NIETS af (36 duels op een
        # zondagcap van 55) en tóch kreeg Croatian HNL `AFGEKAPT`, puur omdat zijn enige duel
        # (Osijek – Rudes) op NONE staat: Kroatië heeft bij Fotmob geen tweede divisie, dus een
        # promovendus is daar niet om te rekenen (Sec. 4). Dat is een onware status — hij zegt dat
        # de cap iets heeft weggegooid wat de cap niet heeft aangeraakt — en hij verbergt
        # bovendien een duel: `progress.py verify` sloeg de hele AFGEKAPT-competitie over en
        # meldde "3 zonder kansbron" waar er 4 op NONE staan.
        #
        # De status wordt daarom bepaald op de REDEN en niet op de uitkomst: eerst de
        # afkappingslijst van Stage 4 (die noemt de duels bij naam), dan de tier.
        afgekapt_namen = {m for m in (res["afkapping"].get("lijst") or [])}
        for comp, blok in st["competitions"].items():
            n_door = sum(1 for m in blok["matches"] if m.get("all_candidates"))
            n_trunc = sum(1 for m in blok["matches"] if m["match"] in afgekapt_namen)
            n_none = sum(1 for m in blok["matches"] if m.get("tier") == "NONE")
            if n_door:
                status = "GEANALYSEERD"
            elif n_trunc:
                status = "AFGEKAPT"
            elif n_none == len(blok["matches"]):
                status = "BUITEN DATADEKKING"
            else:
                status = "AFGEKAPT"
            entry = {"status": status, "matches": []}
            for m in blok["matches"]:
                e = dict(m)
                sleutel_bet = any((m["match"], mk, se) in gespeeld
                                  for mk, se in [(c["market"], c["selection"])
                                                 for c in m.get("all_candidates", [])])
                # §6d/§1a: is er op dit duel gepubliceerd, dan is een andere selectie van
                # dezelfde wedstrijd dezelfde mening en geen afgewezen kandidaat — die hoort
                # niet in het schaduwlogboek (regel van 2 okt 2026, `rb_oct04_publiceer.py`).
                # De regel wordt hernoemd in plaats van weggegooid, zodat hij in
                # `data/run-state/` na te lezen blijft; hij verdwijnt daarmee uit de "Net
                # niet"-tabel en wordt in het runrapport onder de bet zelf genoemd.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)

        # Dekkingstabel: óók de vijftien competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/rb_oct27_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        save(state)   # mark_completed pas na het runrapport en de push (Stage -1)
        print(f"run-state Run {run} weggeschreven ({len(state['competitions'])} competities)")

    # schaduwrijen van vanochtend die nu een gepubliceerde bet zijn
    sel = {(p["home"] + " – " + p["away"], p["market"] + " — " + p["selection"]) for p in alle_picks}
    rijen = [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]
    houden = [r for r in rijen if not (r["date"] == DAG and (r["match"], r["market"]) in sel)]
    weg = len(rijen) - len(houden)
    with open("data/shadow.jsonl", "w") as f:
        for r in houden:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{weg} schaduwrij(en) verwijderd die nu een echte bet zijn")

    # IDEMPOTENT (16 okt 2026). Een correctie in de `parameters`-tekst is een reden om dit script
    # nog een keer te draaien, en dan mogen de picks niet dubbel in het logboek komen: `ledger.py`
    # telt per regel en een dubbele pick verschuift hit rate en ROI zonder dat iets klaagt.
    # Dezelfde stille faalstand als de rest van deze ochtend, dus hier een harde controle.
    bestaand = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
    nieuw = [p for p in alle_picks if p["id"] not in bestaand]
    with open("data/picks.jsonl", "a") as f:
        for p in nieuw:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(nieuw)} picks toegevoegd aan data/picks.jsonl "
          f"({len(alle_picks) - len(nieuw)} stonden er al in en zijn overgeslagen)")


if __name__ == "__main__":
    if "--schrijf" in sys.argv:
        wegschrijven()
    else:
        for run, pad in (("B", "tmp-run/rb_oct27_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct27_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct27_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")
