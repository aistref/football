"""Run B 4 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct03_publiceer.py`. Ongewijzigd in de mechaniek; alleen de
`parameters`-tekst is die van vandaag. `mark_completed` is hier bewust UIT gehaald en gebeurt
pas na het runrapport en de push (Stage -1, §6b-7) — anders zou een hervatting na een
afgebroken sessie denken dat de run al klaar was terwijl het rapport nog niet bestond.
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-04"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-04T05:14:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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


if __name__ == "__main__":
    alle = []
    for run, pad in (("B", "tmp-run/rb_oct04_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb_oct04_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb_oct04_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct04_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.998964, b=-0.000675 op 3459 afgerekende gevallen, fitted_through "
                          "2026-10-03. De correctie is praktisch de identiteit: het ruwe model "
                          "zei gemiddeld 33.333% en het gebeurde 33.333%. fitted_through staat "
                          "op de vorige rundag (3 okt), dus calibration.py settle is niet "
                          "blijven liggen (§6b-5c). Let op wat die identiteit wel en niet zegt: "
                          "de reeks is de ONGESELECTEERDE ijksteekproef, breder dan de selecties "
                          "waarop gespeeld wordt — zie §1e, punt 3 van 30 september."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "INTERLANDVENSTER": (
                "Vijftien van de zeventien competities uit de runlijst hadden GEEN WEDSTRIJD, en "
                "dat is het interlandvenster en geen storing: scripts/idcheck.py gaf voor alle "
                "zeventien fotmob_id's een bruikbare stand (afsluitcode 0), dus geen enkele "
                "competitie is stil uit de lijst verdwenen. Dat is precies de controle waarvoor "
                "idcheck.py op 29 september is gebouwd — op een dag als vandaag is GEEN "
                "WEDSTRIJD de normale uitkomst en zou een kapot id er niet van te onderscheiden "
                "zijn. Wat wel speelde: Segunda División (ESP) met vijf duels en Keuken Kampioen "
                "Divisie (NED) met één. MLS en Série A (BRA) staan op geen van beide daglijsten "
                "(4 en 5 okt), dus ook met het inzetvenster van runwindow.py valt er daar niets "
                "te halen; de audit in tmp-run/rb_oct04_stage3.json legt dat per daglijst vast."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                       "today=2026-10-04 aangeroepen zoals §1e eist. De poort was vandaag bij "
                       "één duel de eerste dichte poort: Girona – Mallorca, Asian Handicap "
                       "Mallorca +0.25 @1.8722 (markt 30.9% tegen 41.1% voor de tegenstander, "
                       "score 0.752, met 2 andere geblokkeerde selecties op dezelfde kant). Die "
                       "gaat als failed_gate='underdog' het schaduwlogboek in — de reeks die op "
                       "30 september op 20 afgewikkelde gevallen stond waar §6d er ~30 vraagt. "
                       "poort8_ruw is leeg omdat het dezelfde selectie is (§5a regel 2: nooit "
                       "dezelfde selectie twee keer). Wat het kostte: niets in de lijst — op "
                       "ditzelfde duel is wél gepubliceerd, maar op de doelpuntenmarkt (Under "
                       "2.5), niet op de geblokkeerde kant. Bij Castellón – AD Ceuta FC en Las "
                       "Palmas – Real Valladolid staat poort 8 als would_block in "
                       "poort8_vervallen, maar daar was de edge-poort al eerder dicht; "
                       "gepubliceerd blijft daar False, zoals §5b eist."),
            "WAAROM_DRIE_BETS": (
                "Drie regels op vijf plekken (zondag), en maar één ervan is een gevonden "
                "voordeel. Alleen Las Palmas – Real Valladolid haalt de lat van 8.0 pp (+10.39 "
                "pp herijkt, +10.42 pp ruw); de andere twee staan erin omdat §5b sinds 20 "
                "september aan het EIND van de dag snijdt: staan er minder selecties boven de "
                "drempel dan er regels in de lijst passen, dan bepaalt de rangorde de lijst en "
                "gaat de drempel mee als label. Van de 53 doorgerekende selecties haalde er "
                "precies één zijn drempel. Lees de lijst dus als 'het sterkste van vandaag' en "
                "niet als drie gevonden voordelen — §1g heeft op 552 afgerekende gevallen "
                "gemeten dat er géén drempel op de herijkte edge bestaat die geld oplevert. De "
                "§5b-afkapping op LIJSTLENGTE bond vandaag niet: er stond één selectie boven de "
                "drempel en er zijn drie regels op vijf plekken, dus er viel niets "
                "gekwalificeerds buiten de lijst en de reeks 'lijstlengte' groeit deze run niet. "
                "Er zijn ook geen vijf regels geworden: twee van de zes duels leverden geen "
                "enkele selectie op die alle zeven overige poorten haalde, en één kwam op NONE "
                "uit — aanvullen tot vijf is precies wat §5 verbiedt."),
            "EENZIJDIGE_LIJST": (
                "Alle drie de gepubliceerde regels zijn Under 2.5, en alle drie staan in de "
                "Segunda División. Dat is een bevinding en hoort niet weggepoetst: §1a eist dat "
                "zichtbaar is of zo'n scheve uitkomst uit de inkoop komt of uit de analyse, en "
                "vandaag komt hij uit de analyse. De bulk-aanroep leverde voor de Segunda alle "
                "vijf de markten (1X2 op de beste prijs, Asian Handicap, Draw No Bet, de "
                "0.0-lijn, Over/Under) en de tweede ronde kocht BTTS voor de drie duels met een "
                "kandidaat-edge; alle zes de markten hebben er dus werkelijk meegedongen — 53 "
                "selecties over zes duels — en selection_score koos drie keer dezelfde markt. De "
                "onderliggende oorzaak is ook dezelfde drie keer: het model schat het "
                "doelpuntenniveau van de Segunda lager in dan de markt (route vorig+uplift, "
                "basis 1.354 met een uplift-factor van 0.9959 — dus een factor ONDER 1, voor het "
                "eerst op deze runlijst). Dat is één mening, drie keer uitgedrukt, en dat is "
                "precies de reden dat §5 vraagt per regel op te schrijven waar hij staat. Blijft "
                "dit dagen achtereen zo, dan is dat een signaal over het model en niet over §5b."),
            "UPLIFT_ONDER_EEN": (
                "De vroeg-seizoenscorrectie kwam op 0.9959 uit (gepoold 0.9918 over 8 "
                "speeldagen, 1 competitie) — voor het eerst een factor onder 1. De correctie is "
                "gebouwd op de waarneming dat er begin seizoen MEER wordt gescoord dan over een "
                "heel jaar gemiddeld; de Segunda doet dit seizoen het omgekeerde (avg_xg 1.349 "
                "lopend tegen 1.360 vorig seizoen) en dan draait de factor mee. Dat is correct "
                "gedrag en geen defect — de correctie is een gemeten verhouding en geen aanname "
                "in één richting — maar het is wél een pool van PRECIES ÉÉN competitie, want "
                "Keuken Kampioen Divisie (NED) valt eruit (geen xG in beide seizoenen, zie "
                "uplift_observations). Een gepoolde correctie over één waarneming is geen pool; "
                "lees die 0.9959 dus als 'de Segunda zelf', en let erop dat hij op een dag met "
                "meer spelende competities weer een gemiddelde over meerdere is."),
            "WAAROM_EEN_DUEL_GEEN_BET": (
                "Eén van de zes duels komt op data_tier NONE uit en is niet doorgerekend, en het "
                "is DE DERDE KEER IN DRIE RUNS DEZELFDE STRUCTURELE OORZAAK: Sporting Gijón – "
                "Celta Fortuna, met Celta Fortuna als promovendus uit de Primera Federación. "
                "promotion.TIER2 kent geen Spaans paar LaLiga2/Primera Federación, dus de "
                "omrekening valt terug op de TIER1-tak (degradant uit La Liga) en die vindt hem "
                "daar natuurlijk ook niet; de foutmelding noemt daarom alleen de degradantenkant, "
                "wat de oorzaak makkelijk verkeerd laat lezen. Op 2 en 3 oktober was het Sabadell "
                "in dezelfde competitie, vandaag een ander elftal — het ligt dus niet aan één "
                "ploeg. §4 is hier hard in: buiten het gemeten bereik is er geen onafhankelijke "
                "kansinput op het niveau waarop gespeeld wordt, dus NONE en geen bet. Het kostte "
                "geen extra credits — de bulk wordt per competitie gekocht, niet per duel."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("6 credits van een plafond van 355 (19.914 over bij api_check.py, 86 "
                       "verbruikt deze maand, 28 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: één bulk-aanroep à 3 credits (h2h + spreads + totals) voor "
                       "Segunda División (ESP) — de enige spelende competitie met een sportkey, "
                       "dus split_budget(355, 1) -> (1, 1) en niemand viel buiten de bulk. Stap "
                       "2: BTTS voor drie van de zes duels met een kandidaat-edge (1 credit per "
                       "duel, §1a stap 2); de andere drie toonden geen kandidaat-edge op "
                       "beide schalen en krijgen daarom 'niet opgevraagd — geen kandidaat-edge' "
                       "in markets_checked, niet 'geen boek noteerde deze markt'. Keuken "
                       "Kampioen Divisie (NED) heeft geen sportkey en draait volledig op het "
                       "gratis BetExplorer-marktgemiddelde over 3 boeken; AH, DNB, DC, OU en "
                       "BTTS staan daar per markt met die reden in markets_checked en niet als "
                       "gat (§6b-5b). Marktbalans: de controle slaagt, maar met de kleinst "
                       "mogelijke marge — 1 van de 2 spelende competities heeft zowel een "
                       "uitkomstmarkt als een doelpuntenmarkt, de andere heeft alleen het "
                       "gratis 1X2. Dat is geen te krap plafond (er was 355 beschikbaar en er is "
                       "6 uitgegeven) maar een competitie die bij The Odds API niet te koop is."),
            "BEURSKOERSEN": (
                "Twee van de drie gepubliceerde regels staan op een beurs en zijn met "
                "oddsapi.net_price doorgerekend: Real Sociedad B – Granada Under 2.5 bij "
                "Matchbook 1.96 bruto / 1.9408 na 2% commissie, en Girona – Mallorca Under 2.5 "
                "bij Matchbook 2.04 bruto / 2.0192 na commissie. De gebruiker ziet op de site de "
                "koers ervóór; edge_pp en selection_score rekenen met de koers erná (§5). De "
                "derde, Las Palmas – Real Valladolid Under 2.5 @1.86, staat bij 1xBet en is een "
                "gewone bookmaker zonder commissie."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top
        # §5b-afkapping op LIJSTLENGTE. Vandaag bindt ze NIET — er zijn drie regels op vijf
        # plekken — maar de lus blijft staan, want ze is de enige plek waar een gekwalificeerde
        # selectie die niet in de lijst past wordt vastgelegd: een `near_miss` met
        # `failed_gate = "lijstlengte"` plus een `gekwalificeerd_niet_gepubliceerd`-blok,
        # precies zoals Run C dat op 24 sep 2026 deed en Run B op 26 sep. Bewust dezelfde naam
        # en geen tweede: het is één vraag — wat kost de lijstlengte ons — en twee namen zouden
        # één populatie in twee reeksen splitsen (§5b).
        alles_op_score = sorted(
            [{"match": m["match"], "score": (m.get("pick") or {}).get("score") or 0.0}
             for m in res["matches"] if m.get("bet")],
            key=lambda r: -r["score"])
        gepubliceerd_scores = [r["score"] for r in top["herijkt"] if r.get("score") is not None]
        drempel_score = min(gepubliceerd_scores) if gepubliceerd_scores else None
        buiten = 0
        for m in res["matches"]:
            if not m.get("bet"):
                continue
            pick = m.get("pick") or {}
            if (m["match"], pick.get("market"), pick.get("selection")) in gespeeld:
                continue
            rang = next((i for i, r in enumerate(alles_op_score, 1)
                         if r["match"] == m["match"]), None)
            # Zelfde constructie als Run C op 24 sep 2026 (Portugal – Wales): een `near_miss` met
            # `failed_gate = "lijstlengte"`, plus `gekwalificeerd_niet_gepubliceerd` op de
            # wedstrijd. Bewust DEZELFDE naam als die run gebruikte en niet een nieuwe: het is
            # dezelfde vraag — wat kost de lijstlengte ons — en twee namen zouden één populatie in
            # twee reeksen splitsen, waarna geen van beide ooit de ~30 gevallen haalt die §6d eist.
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
                          f"{len(top['herijkt'])} (zaterdag); laagste gepubliceerde "
                          f"selection_score {drempel_score}")}
            buiten += 1
        print(f"{buiten} gekwalificeerde selectie(s) buiten de lijst van §5b")

        for comp, blok in st["competitions"].items():
            entry = {"status": "GEANALYSEERD", "matches": []}
            for m in blok["matches"]:
                e = dict(m)
                sleutel_bet = any((m["match"], mk, se) in gespeeld
                                  for mk, se in [(c["market"], c["selection"])
                                                 for c in m.get("all_candidates", [])])
                # Een selectie die nu gespeeld wordt, mag niet óók als schaduwpick worden geboekt
                # (§6d: nooit dezelfde selectie twee keer).
                # Tot 2 okt 2026 werd een `near_miss` alleen verwijderd als hij exact dezelfde
                # SELECTIE beschreef als een gepubliceerde bet. Sinds §5b (20 sep) publiceert de
                # rangorde ook wedstrijden waarin geen enkele selectie de drempel haalde, en dan
                # blijft er een `near_miss` staan op een wedstrijd waarop wél is gespeeld. Dat
                # klopte zolang de drempel een poort was en zo'n wedstrijd dus écht niets
                # opleverde; het klopt niet meer.
                #
                # Vandaag bindt dat verschil voor het eerst. Vier van de vijf gepubliceerde
                # regels komen van wedstrijden zonder enkele selectie boven de lat, en bij drie
                # ervan is de gepubliceerde selectie dezelfde als de near_miss (die drie werden
                # dus al verwijderd). Bij Exeter City – Rotherham United niet: §5b publiceert de
                # hoogste `selection_score` (Draw No Bet, 3.785) en `near_miss` bewaart de
                # hoogste `edge_pp` (de 1X2, +12.33 pp). Zonder deze wijziging gaat die 1X2 als
                # `failed_gate = "edge"` het schaduwlogboek in terwijl we op diezelfde wedstrijd
                # een bet spelen — dezelfde mening, twee keer geteld, in precies de reeks waar
                # §6d voor waarschuwt dat één verkeerd geboekte regel zwaarder weegt dan alles
                # wat de poort werkelijk doet (§1a: dezelfde mening in een andere markt is één
                # bevinding).
                #
                # De vergelijking gaat daarom vanaf nu op de WEDSTRIJD en niet op de selectie: is
                # er op dit duel gepubliceerd, dan is het geen afgewezen kandidaat en hoort het
                # niet in het schaduwlogboek. `poort8_geblokkeerd`, `poort8_ruw` en
                # `zonder_herijking` blijven wél staan — §1e zegt met zoveel woorden dat een
                # poort-8-rij ook meetelt "als de wedstrijd daarna alsnog een andere bet
                # opleverde", en die reeksen beantwoorden een andere vraag dan `edge`.
                #
                # De regel wordt niet weggegooid maar hernoemd naar
                # `near_miss_gepubliceerd`, zodat hij in `data/run-state/` na te lezen blijft.
                # Hij verdwijnt daarmee ook uit de "Net niet"-tabel van §5, en dat is juist: die
                # tabel gaat over kandidaten die zijn afgewezen, en op deze wedstrijd is
                # gespeeld. Het runrapport noemt zo'n regel apart onder de bet zelf.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)
        save(state)   # mark_completed pas na het runrapport en de push (Stage -1)
        print(f"run-state Run {run} weggeschreven ({len(st['competitions'])} competities)")

    # schaduwrijen van vanochtend die nu een gepubliceerde bet zijn
    sel = {(p["home"] + " – " + p["away"], p["market"] + " — " + p["selection"]) for p in alle_picks}
    rijen = [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]
    houden = [r for r in rijen if not (r["date"] == DAG and (r["match"], r["market"]) in sel)]
    weg = len(rijen) - len(houden)
    with open("data/shadow.jsonl", "w") as f:
        for r in houden:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{weg} schaduwrij(en) verwijderd die nu een echte bet zijn")

    with open("data/picks.jsonl", "a") as f:
        for p in alle_picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(alle_picks)} picks toegevoegd aan data/picks.jsonl")
