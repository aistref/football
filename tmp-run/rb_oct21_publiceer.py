"""Run B 21 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct20_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. TWEE van de zeventien competities speelden, met samen twee duels
in het inzetvenster en nul afgekapt (cap 40 op woensdag). ÉÉN gepubliceerde regel, en die haalt
zowel de drempel van 8,0 als de verzwaarde lat van poort 9.

Drie dingen die vandaag in de parameters horen:

* **De bet bestaat alleen dank zij `runwindow.py`.** FC Cincinnati – DC United trapt af om 01:00
  NL op 22 oktober en stond op de UTC-daglijst van 21 oktober; onder de oude UTC-regel was dit
  duel in de run van morgen beland en dan al gespeeld geweest.
* **Pinnacle spreekt de bet tegen**, en dat is het zwaarste voorbehoud: op zijn eigen lijn 3,75
  staat het model +6,87 pp meer aan de Under-kant dan de scherpste bookmaker — precies de richting
  waarvan §6g meet dat ze fout staat.
* **De vroeg-seizoenspool bestaat uit één competitie**, omdat MLS halverwege zijn seizoen is en
  route `lopend` krijgt. Een pool van één is geen pool; dat hoort erbij te staan.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-21"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-21T04:21:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct21_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.0215, b=0.0139 "
                "op 5298 afgerekende gevallen, fitted_through 2026-10-20. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). "
                "De correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3% — en ze VERHOOGT een kans over vrijwel de hele speelbare band. Op de "
                "enige gepubliceerde regel telde ze dus edge BIJ in plaats van af: Under 3,5 van +12,59 "
                "pp ruw naar +13,08 pp herijkt. DAT RAAKT VANDAAG GEEN POORT: de regel staat op beide "
                "schalen ruim boven de verzwaarde lat van poort 9 (10,0 pp), en bet_beide = True. Lees "
                "de identiteit zoals §1e punt 3 voorschrijft: de reeks is de ONGESELECTEERDE "
                "ijksteekproef en breder dan de staart waarop deze routine speelt."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de zeventien competities speelden, met samen TWEE duels in het inzetvenster: "
                "English League One (Reading – Leyton Orient, 21:00 NL) en MLS (FC Cincinnati – "
                "DC United, 01:00 NL). VIJFTIEN competities hadden GEEN WEDSTRIJD — Czech First League, "
                "Greek Super League, Eliteserien, Allsvenskan, Croatian HNL, Hungarian NB I, Romanian "
                "SuperLiga, Segunda División, Serie B, 2. Bundesliga, Swiss Super League, Austrian "
                "Bundesliga, Keuken Kampioen Divisie, English League Two en Série A (BRA). Dat is de "
                "smalste runlijst van deze maand en het is geen storing: het is woensdagnacht in Europa "
                "tussen twee speelronden, de Europese toernooien staan niet op deze lijst (die zijn van "
                "Run A) en de kalenderjaarcompetities zijn aan hun laatste duels toe. scripts/idcheck.py "
                "gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode 0), dus "
                "geen enkele competitie is stil uit de lijst verdwenen — ook niet die vijftien die "
                "vandaag niet spelen, en dat is precies waarom die controle bestaat. BEIDE spelende "
                "competities hebben xG bij Fotmob en alle vier de ploegen staan in de stand van hun "
                "vorige seizoen, dus BEIDE duels zijn FULL, de lat is 8,0 pp en er is vandaag GEEN "
                "ENKELE OMREKENING nodig geweest — geen promovendus, geen degradant, geen kruis-grens, "
                "en dus ook geen gepoolde factor in deze run."
            ),
            "DE_MLS_NACHTBAND_IS_VANDAAG_HET_HELE_VERSCHIL": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN ZE HOORT VOORAAN. De enige gepubliceerde bet staat "
                "op een duel dat onder de OUDE regel niet in deze run had gezeten: FC Cincinnati – DC "
                "United trapt af op 2026-10-21T23:00Z, oftewel 01:00 NL op 22 oktober, en stond op de "
                "UTC-daglijst van 21 oktober. runwindow.py plaatst hem in het venster [08:00 NL 21 okt, "
                "08:00 NL 22 okt) met playable = True, want de gebruiker zet tussen 07:00 en 08:00 in en "
                "de aftrap ligt daarna. Dat is exact het geval dat prompts/run-b.md beschrijft en dat op "
                "24 september 2026 een hele MLS-ronde kostte: onder de UTC-regel was dit duel 'de run "
                "van morgen' geweest, en morgenochtend was hij al gespeeld. Vandaag is het niet één duel "
                "van de twintig maar de HELFT van de hele runlijst en de ENIGE bet. RunMatch.source_day "
                "staat op 2026-10-21 voor beide duels; er zat vandaag dus geen duel in de nachtband van "
                "de vórige rundag, en de eenmalige include_carry_over van de overstap is hier niet "
                "gebruikt (die is eenmalig geweest op 24 september)."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "ÉÉN REGEL, EN DIE HAALT ZIJN EIGEN LAT: FC Cincinnati – DC United, Under 3,5 @2,2348 "
                "(Matchbook, beurs — 2,26 bruto) met +13,08 pp tegen een lat van 8,0 pp, en tegen de "
                "VERZWAARDE lat van 10,0 pp die poort 9 op een FULL-Under legt. Hij staat er dus als "
                "vondst en niet alleen als rangorde, en dat is op deze runlijst de uitzondering. "
                "MAX_SHORTLIST is 3 op woensdag en er is één gekwalificeerde regel, dus de lijstlengte "
                "bindt niet en er is geen `lijstlengte`-rij. MAX_LIGHT_IN_SHORTLIST (2) bindt evenmin: "
                "de enige regel is FULL. Van de 29 doorgerekende selecties over twee duels haalde er "
                "precies één alle negen poorten."
            ),
            "WAT_ER_TEGEN_DEZE_BET_PLEIT_EN_DAT_IS_PINNACLE": (
                "DE ZWAARSTE WAARSCHUWING BIJ DE ENIGE REGEL VAN VANDAAG KOMT VAN STAP 2 VAN STAGE 5, "
                "NIET VAN DE EIGEN POORTEN. Pinnacle noteert dit duel op lijn 3,75 met 1,88/1,98 (marge "
                "3,7%) en zegt daarmee de-vigd 48,7% voor de Under; het eigen scoregrid zegt op diezelfde "
                "lijn 55,6%. Het model staat dus +6,87 pp MEER aan de Under-kant dan de scherpste "
                "bookmaker van de markt — en dat is precies de richting waarvan §6g meet dat ze "
                "structureel fout staat: een vormfout in score_grid zet P(Under) bij élk duel 1,6 tot 2,4 "
                "pp te hoog, en bovenop die fout meet §6g een selectie-effect van +0,584 doelpunt per "
                "duel in de duels waar werkelijk een Under is gespeeld. Poort 9 vangt daar 2,0 pp van af "
                "en deze regel haalt die lat ruim; de rest van het verschil met Pinnacle blijft staan. "
                "Op 1X2 is de afstand tot Pinnacle klein (3,63 pp op de thuiszege, 3,61 pp gemiddeld over "
                "de twee duels bij een gemiddelde Pinnacle-marge van 4,58%), dus het is specifiek de "
                "doelpuntenkant waar de twee uiteenlopen. Lees de bet dus met dat cijfer erbij: de markt "
                "verwacht hier een open wedstrijd en het model niet."
            ),
            "DE_MARKT_ZET_DEZE_WEDSTRIJD_OPVALLEND_HOOG": (
                "EEN WAARNEMING OVER DE PRIJS ZELF, want ze is ongebruikelijk en hoort daarom "
                "opgeschreven. Under 3,5 staat bij veertien boeken tussen 1,93 en 2,26 en Over 3,5 "
                "tussen 1,61 en 1,77; Pinnacle legt zijn evenwichtslijn op 3,75 en William Hill noteert "
                "Over 2,5 op 1,25. De markt verwacht hier dus een totaal van bijna vier doelpunten — "
                "hoog voor een voetbalwedstrijd, en de reden dat een Under 3,5 hier tegen een koers van "
                "boven de 2,20 te spelen is in plaats van rond de 1,50. Het eigen model komt op 3,41 "
                "doelpunten uit op de xG-arm (2,053 thuis / 1,359 uit) en op 3,02 op de splitsarm; dat "
                "verschil van drie tot zeven tienden doelpunt IS de hele edge van deze bet. Die prijs is "
                "tegen de ruwe respons van The Odds API gecontroleerd en is geen artefact van één boek: "
                "veertien aanbieders staan in dezelfde band, de beste prijs (Matchbook 2,26) ligt 5,87% "
                "boven het BetExplorer-marktgemiddelde over twaalf boeken."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 23 VAN DE 29 SELECTIES WEG (79,3%) — 'tweede_methode', de twee methodes "
                "verslaan de markt niet dezelfde kant op. Daarna 2 op de koersband, 1 op poort 9 en 1 op "
                "de edge; 2 selecties haalden alle poorten (de gepubliceerde Under 3,5 en de Under 3,75 "
                "van hetzelfde duel, dat is dezelfde mening in een naburige markt). Die 79,3% ligt in "
                "dezelfde band als de afgelopen weken en voegt er geen nieuwe waarneming aan toe. WAAR "
                "HET BIJ READING VANDAAG WEL SCHERP TE ZIEN IS: de twee methodes staan daar lijnrecht "
                "tegenover elkaar. De xG-arm komt op 2,157 thuis / 0,788 uit (Reading veel sterker), de "
                "splitsarm op 1,845 / 1,323 (bijna gelijkwaardig), en op de thuiszege geeft dat +5,00 pp "
                "tegen −14,15 pp. Dat is geen klein verschil in weging maar twee verschillende "
                "wedstrijden, en poort 5 doet daar precies wat §1 beschrijft: de bet gaat eruit met reden "
                "'data conflicterend' in plaats van op het gewogen gemiddelde te worden gepubliceerd."
            ),
            "NET_NIET_IS_VANDAAG_LEEG_EN_DAT_IS_ZELF_EEN_UITKOMST": (
                "ER STAAT GEEN ENKELE RIJ IN DE 'NET NIET'-TABEL, en §5 eist juist bij een smalle dag "
                "dat dat verschil zichtbaar is. De reden is te geven: de sterkste afgewezen selectie van "
                "de dag is Reading −1 (Asian Handicap) op +2,14 pp, en de ondergrens om als near_miss in "
                "het schaduwlogboek te komen is 3,0 pp op FULL. Bij Reading haalt dus geen enkele "
                "selectie die ondergrens; bij Cincinnati is er één rij, maar die hoort niet in 'Net "
                "niet' omdat op dat duel wél is gepubliceerd — een andere selectie van dezelfde "
                "wedstrijd is dezelfde mening in een andere markt (§1a, §6d) en staat daarom als "
                "`near_miss_gepubliceerd` in de run-state. Nul rijen betekent hier dus 'geen enkele "
                "kandidaat kwam in de buurt', niet 'er is niet gekeken'."
            ),
            "POORT7": (
                "BINDT MAAR HOUDT NUL SELECTIES TEGEN, en dat is vandaag bij uitzondering een MEETBARE "
                "nul in plaats van een gat. Van de vier ploegen heeft er één een uitvallerslijst bij "
                "Fotmob: DC United mist Gabriel Segal (blessure, terug eind oktober) met 146.632 euro op "
                "een selectiewaarde van 16,3 miljoen — 0,9% van de selectiewaarde, ver onder de drempel "
                "van 10 procentpunt verschil. De andere drie ploegen hebben een LEGE uitvallerslijst, en "
                "§1c zegt uitdrukkelijk dat een lege lijst informatie is en geen gat. MARKTWAARDE is er "
                "voor alle vier de ploegen. DE RUSTPOOT BINDT NERGENS: Reading en Leyton Orient staan "
                "beide op 4,2 dagen rust (geen van beide congested), Cincinnati op 3,1 en DC United op "
                "4,0 — een verschil van 0,9 dag, waar de poort er minstens twee eist. DE "
                "STADIONCONTROLE GAF NUL ALARMEN: beide duels in het eigen stadion van de genoteerde "
                "thuisploeg (Select Car Leasing Stadium, TQL Stadium), relocated = false. OPSTELLINGEN: "
                "het MLS-duel staat op 'standard' en het Engelse op 'lastStarting11' — geen van beide "
                "bevestigd, dezelfde klokbevinding als de afgelopen weken, ruim vijftien respectievelijk "
                "twintig uur voor de aftrap. De context van BEIDE duels is opgehaald en vastgelegd; de "
                "cap (40 op woensdag) kapte niets af, dus de steekproef van ctxlog.py is volledig."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                "today=2026-10-21 aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ HOUDT "
                "VANDAAG NUL SELECTIES TEGEN en er gaat dus geen enkele rij als `underdog` of "
                "`underdog_ruw` het schaduwlogboek in. De reden is de samenstelling van de dag en niet "
                "een versoepeling: in beide duels is de thuisploeg favoriet (Reading 1,58 / Cincinnati "
                "1,67 beste prijs) en geen enkele selectie die de eerdere poorten haalde staat op een "
                "kant onder de ondergrens. De gepubliceerde regel is een Over/Under en heeft per "
                "definitie geen kant, dus daar staat poort 8 open. Dit is geen aanleiding om de vraag "
                "van 25 september opnieuw te stellen (§1e verbiedt dat zolang er niets wezenlijk "
                "verandert); de stand van beide reeksen staat in het runrapport onder 'Stand van het "
                "logboek'."
            ),
            "POORT9": (
                "BINDT EN HOUDT ÉÉN SELECTIE TEGEN, OP HETZELFDE DUEL WAAR DE BET VANDAAN KOMT. FC "
                "Cincinnati – DC United, Under 2,5 @3,70 met +8,38 pp: dat is de band 8–10 pp waarop de "
                "lat van 10,0 pp mikt en die volgens §6g op −47,7% over vijftien gevallen staat, de "
                "slechtste band van de hele Under-reeks. De rij gaat als failed_gate = "
                "'doelpunten_onder' het schaduwlogboek in; de reeks groeit daarmee naar 3 rijen sinds 12 "
                "oktober. Lees hem niet onder ~30 gevallen (§6d) — precies zoals §1h voorspelde is dat "
                "eerder een vraag voor december dan voor deze week. OPVALLEND EN HET HOORT ERBIJ: de "
                "poort houdt hier de ZWAKKERE Under van het duel tegen en laat de sterkere door (+13,08 "
                "pp op lijn 3,5), dus de omgekeerde volgorde van 20 oktober, toen de routine een "
                "FULL-Under op +7,10 pp publiceerde en er twee op +8,99 en +9,08 pp blokkeerde. Dat gat "
                "tussen §1h en §5b staat als besluitpunt in het dagrapport van 20 oktober en is nog "
                "steeds niet gedicht; vandaag valt het alleen de goede kant op uit."
            ),
            "PINNACLE": (
                "STAP 2 VAN STAGE 5 — het scherpste publieke expertoordeel, LOS van de beste prijs waarop "
                "gespeeld wordt en nooit in my_prob (§2). Pinnacle noteerde BEIDE duels, met een "
                "gemiddelde marge van 4,58% op 1X2 (4,8% bij Reading, 4,4% bij Cincinnati) en 3,7–3,9% "
                "op de totalen. Op 1X2 staat het model gemiddeld 3,61 pp van het Pinnacle-oordeel af, en "
                "de twee duels wijzen tegengesteld: bij Reading zit het model +7,20 pp BOVEN Pinnacle op "
                "de thuiszege (68,4% tegen 61,2%) en bij Cincinnati −3,63 pp eronder (53,1% tegen "
                "56,7%). Op de TOTALEN — de markt waar de enige bet staat — is het beeld eenduidig en "
                "ongunstig: op Pinnacle's eigen lijn 3,75 zegt het model 55,6% Under tegen 48,7% "
                "de-vigd, dus +6,87 pp meer aan de Under-kant. Bij Reading is het andersom (−3,85 pp op "
                "lijn 2,75). Gemiddeld over de twee (duel, lijn)-paren staat het model +1,51 pp boven "
                "Pinnacle op de Under-kant, 1 van de 2 erboven — de bekende richting van §6g, en bij "
                "n=2 geen reeks maar één waarneming per duel."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0664 (gepoold 1,1106 over 12 "
                "speeldagen) EN RUST OP ÉÉN COMPETITIE. uplift_observations sloeg MLS over met reden — "
                "'halverwege het seizoen (31 van 34 speeldagen)' — dus de pool bestaat vandaag "
                "uitsluitend uit English League One, en dat staat hier omdat een stil weggelaten "
                "waarneming hetzelfde probleem is als een stille truncatie (§3 Stage 5). EEN POOL VAN "
                "ÉÉN IS GEEN POOL, en dat is de zwakste plek van deze run: de factor 1,0664 is de "
                "gemeten ratio van League One zelf, naar 1,0 teruggetrokken, zonder enige andere "
                "competitie om hem tegen te houden. Lees hem navenant terughoudend. HIJ RAAKT BOVENDIEN "
                "MAAR ÉÉN VAN DE TWEE DUELS: league_level kiest voor English League One route "
                "'vorig+uplift' (12 van 46 speeldagen, 26%, onder SEASON_MATURE_SHARE) met thuis 1,576 / "
                "uit 1,229 / basis 1,389, en voor MLS route 'lopend' (31 van 34 speeldagen) met thuis "
                "1,838 / uit 1,411 / basis 1,545 — het lopende seizoen zelf, ongeschaald. De bet van "
                "vandaag komt dus uit de route die de uplift-factor NIET gebruikt, en dat is precies "
                "waarvoor league_level op 24 september is gebouwd: een kalenderjaarcompetitie halverwege "
                "zijn seizoen hoort zijn niveau uit het lopende seizoen te halen."
            ),
            "BEURSKOERS": (
                "DE ENIGE GEPUBLICEERDE REGEL STAAT WÉL OP EEN BEURS, dus de dubbele notatie van §5 is "
                "vandaag verplicht: Matchbook noteert Under 3,5 op 2,26 en na 2% commissie over de "
                "nettowinst houdt de gebruiker 2,2348 over. Met die netto-koers is gerekend — edge_pp "
                "(+13,08) en selection_score (7,565) staan allebei op 2,2348 en niet op 2,26 — zoals §1a "
                "eist. De gebruiker ziet op zijn scherm 2,26; dat verschil van 1,1% is geen detail op "
                "een drempel van 8,0 pp. De tweede beste prijs zonder beurs is 2,18 (BetAnything), dus "
                "ook zonder Matchbook was dit een bet geweest. BEIDE spelende competities hebben een "
                "sportkey en kregen via de bulk álle zes de markten, dus er is vandaag geen enkel duel "
                "dat op het gratis BetExplorer-marktgemiddelde als enige 1X2-bron draait — de ruimste "
                "dekking die deze runlijst kan hebben. De beste prijs lag 8,53% (Reading) en 5,87% "
                "(Cincinnati) boven dat marktgemiddelde, in dezelfde orde als de +7,78% die §1a op 5 "
                "september mat."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 21 okt, 08:00 NL 22 okt) en runwindow.py levert TWEE duels, "
                "beide met RunMatch.playable = True. Reading – Leyton Orient trapt af om 21:00 NL op de "
                "rundag zelf; FC Cincinnati – DC United om 01:00 NL in de nacht naar 22 oktober, dus in "
                "de band [00:00, 08:00) NL van de volgende dag. BEIDE komen van de UTC-daglijst van 21 "
                "oktober (RunMatch.source_day = 2026-10-21), dus geen van de twee stond op de lijst van "
                "morgen en er is geen carry-over gebruikt. Zie de aparte paragraaf hierboven: zonder "
                "runwindow.py was het MLS-duel in de run van morgen beland en dan al gespeeld geweest. "
                "De run begon om 04:14 NL, zestien uur voor de eerste aftrap en eenentwintig uur voor de "
                "tweede."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ZEVENTIEN VAN DE ZEVENTIEN COMPETITIES ZIJN DOOR BETEXPLORER BEVESTIGD, inclusief alle "
                "vijftien die vandaag GEEN WEDSTRIJD hebben (0-0) — en juist daar moet de tweede bron "
                "kijken, want 'nul wedstrijden' is de uitkomst die een kapot id en een lege speeldag "
                "niet van elkaar onderscheidt. English League One: 1-1, eens. MLS: 1-1, eens. Twee van "
                "twee duels bevestigd, geen enkele afwijking en geen spookrij. BetExplorer labelt in "
                "UK-tijd (NL −1 uur), dus het venster is daar [21.10. 07:00, 22.10. 07:00); dat is "
                "omgerekend en de omrekening staat in rb_oct21_bevestiging.py. DAT DE TWEEDE BRON "
                "VANDAAG NIETS VINDT IS HET PUNT: vijftien lege competities op een rij is precies het "
                "beeld dat een stil gebroken id ook geeft, en alleen een onafhankelijke bron plus "
                "idcheck.py maken het verschil zichtbaar."
            ),
            "inkoop": (
                "7 CREDITS VAN EEN PLAFOND VAN 951 (19.045 over bij api_check.py, 955 verbruikt deze "
                "maand, 10 dagen tot de maandwissel, 2 runs per dag). Stap 0: TWEE bulk-aanroepen à 3 "
                "credits (h2h + spreads + totals = 6) voor de twee spelende competities, allebei met "
                "sportkey — English League One (17 events) en MLS (16); split_budget(951, 2) -> (2, 2), "
                "dus niemand viel buiten de bulk en de losse totals-stap was niet nodig. Stap 2: BTTS "
                "voor 1 van de 2 duels met een kandidaat-edge, 1 credit. Het andere duel (Reading) kreeg "
                "geen BTTS en staat met die reden in markets_checked — 'niet opgevraagd, geen "
                "kandidaat-edge in dit duel' — en niet als gat (§1a stap 2). MARKTBALANS-CONTROLE: "
                "GEHAALD, en zo ruim als deze runlijst kan — BEIDE inkoopbare competities kregen via de "
                "bulk álle markten uit de bulk (1X2, AH, DNB, DC, OU), dus twee op twee, en er is geen "
                "enkele competitie met alléén een uitkomstmarkt of alléén een doelpuntenmarkt. Let op "
                "één echte lacune in de respons zelf: bij BEIDE duels zat er geen 0.0-lijn en geen "
                "±0.5-lijn in de spreads, dus Draw No Bet en Double Chance waren er feitelijk niet te "
                "koop; dat staat per duel in markets_checked met die reden en is dus 'bekeken met een "
                "reden' en geen overgeslagen markt."
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

        for comp, blok in st["competitions"].items():
            entry = {"status": "GEANALYSEERD", "matches": []}
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
        s3 = json.load(open("tmp-run/rb_oct21_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct21_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct21_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct21_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")
