"""Run B 6 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct04_publiceer.py` — dezelfde mechaniek, alleen de `parameters`-tekst is
die van vandaag. Eén duel in het inzetvenster (MLS, Chicago Fire FC – Vancouver Whitecaps,
02:30 NL op 7 okt) en één regel op rangorde: geen enkele selectie haalde de lat van 8,0 pp.
`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-06"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-06T05:12:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct06_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.985025, b=-0.009728 op 3660 afgerekende gevallen, fitted_through "
                          "2026-10-05. Die datum is de vórige rundag, dus calibration.py settle "
                          "is niet blijven liggen (§6b-5c). De correctie is praktisch de "
                          "identiteit: het ruwe model zei gemiddeld 33,333% en het gebeurde "
                          "33,333%. Op de enige doorgerekende wedstrijd haalde ze 0,4 pp van de "
                          "edge af (5,55 ruw -> 5,15 herijkt). Let op wat die identiteit wél en "
                          "niet zegt: de reeks is de ONGESELECTEERDE ijksteekproef, breder dan "
                          "de selecties waarop gespeeld wordt — zie §1e, punt 3 van 30 sep."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "INTERLANDVENSTER": (
                "Zestien van de zeventien competities uit de runlijst hadden GEEN WEDSTRIJD. Dat "
                "is het interlandvenster en geen storing: scripts/idcheck.py gaf voor alle "
                "zeventien fotmob_id's een bruikbare stand (afsluitcode 0), dus geen enkele "
                "competitie is stil uit de lijst verdwenen. Dat is precies de controle waarvoor "
                "idcheck.py op 29 september is gebouwd — op een dag als vandaag is GEEN "
                "WEDSTRIJD de normale uitkomst en zou een kapot id er niet van te onderscheiden "
                "zijn. Alleen MLS speelt, met één duel in het inzetvenster."),
            "INZETVENSTER": (
                "Het enige duel van vandaag is precies het geval waarvoor scripts/runwindow.py "
                "op 24 september is gebouwd: Chicago Fire FC – Vancouver Whitecaps trapt af op "
                "2026-10-07T00:30Z, oftewel 02:30 NL op 7 oktober. Het staat dus op de DAGLIJST "
                "VAN MORGEN (source_day 2026-10-07) en hoort toch bij de run van vandaag, want "
                "het inzetvenster is [08:00 NL 6 okt, 08:00 NL 7 okt) en de gebruiker zet tussen "
                "07:00 en 08:00 vanochtend in. Op de UTC-datum filteren zou dit duel aan de run "
                "van morgen hebben gegeven, die het om 05:15 al gespeeld aantreft. "
                "RunMatch.playable = True."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                       "today=2026-10-06 aangeroepen zoals §1e eist. Hij hield vandaag geen "
                       "enkele kandidaat tegen als eerste dichte poort: poort8_geblokkeerd en "
                       "poort8_ruw zijn allebei leeg, dus de twee schaduwreeksen groeien deze "
                       "run niet. Wel zette would_block bij zes selecties aan — alle zes op de "
                       "THUISkant (Chicago, marktkans 33,3% tegen 41,9% voor Vancouver, onder "
                       "de 0,35). Die zes kwamen niet bij poort 8 aan omdat hun edge negatief "
                       "was: het model vindt Chicago nóg zwakker dan de markt. Daarom staat "
                       "poort8_vervallen.gepubliceerd op False — de gepubliceerde regel is een "
                       "doelpuntenmarkt zonder kant (§5b)."),
            "WAAROM_EEN_REGEL": (
                "Eén regel op drie plekken (dinsdag), en het is geen gevonden voordeel: Under "
                "3,5 staat op +5,15 pp tegen een lat van 8,0. Van de 23 doorgerekende selecties "
                "haalde er GEEN ENKELE zijn drempel. De regel staat er omdat §5b sinds 20 "
                "september aan het EIND van de dag snijdt: staan er minder selecties boven de "
                "drempel dan er regels in de lijst passen, dan bepaalt de rangorde de lijst en "
                "gaat de drempel mee als label. Er zijn geen drie regels geworden omdat er maar "
                "één wedstrijd in het inzetvenster lag en §1 één selectie per wedstrijd "
                "toestaat; aanvullen is precies wat §5 verbiedt. De §5b-afkapping op "
                "LIJSTLENGTE bond dus niet en de reeks 'lijstlengte' groeit deze run niet."),
            "WAT_DE_POORTEN_DEDEN": (
                "De twee sterkste selecties op ruwe score — Draw No Bet Vancouver @1,75 (+6,33 "
                "pp ruw) en 1X2 Vancouver wint @2,35 (+7,26 pp ruw) — sneuvelden allebei op "
                "poort 6, de robuustheid: hun edge draait om in het (shrink, rho)-grid "
                "(min_edge −0,90 respectievelijk −0,11 pp). Dat is de reden dat de "
                "doelpuntenmarkt de lijst aanvoert en niet de uitkomstmarkt: Under 3,5 houdt "
                "+2,62 pp over op het zwakste punt van het grid. Zeven Asian Handicap-lijnen op "
                "Vancouver vielen om dezelfde reden af. Poort 5 (tegenstrijdige methodes), "
                "poort 7 (context) en poort 2 (koersband) hielden vandaag niets tegen op de "
                "selecties die het verst kwamen."),
            "CONTEXT_EN_POORT7": (
                "Poort 7 staat dicht op de THUISkant: Chicago Fire mist 13% van de "
                "selectiewaarde (Anton Salétros en André Franco, allebei geblesseerd) tegen 1% "
                "bij Vancouver (Kenji Cabrera, Belal Halbouni). Dat raakte geen enkele "
                "kandidaat die het verst kwam, want die staan allemaal op de UITkant of op een "
                "markt zonder kant. Rust is gelijk (10,0 om 9,9 dagen), vorm DDLLW om WLLWD. "
                "Gespeeld wordt er op Soldier Field, het eigen stadion van Chicago — "
                "check_venue zet relocated = False. Opstelling: lastStarting11, dus een "
                "voorspelde en geen bevestigde elf (0 van 2 punten in de datarijkdom)."),
            "EENZIJDIGE_LIJST": (
                "Met één wedstrijd in het venster is er over marktbalans in de UITKOMST niets "
                "te zeggen, en daarom gaat het hier over de INKOOP (§1a). Alle zes de markten "
                "hebben werkelijk meegedongen: de bulk-aanroep leverde 1X2 op de beste prijs, "
                "Asian Handicap, Draw No Bet (de 0.0-lijn), Double Chance (de ±0,5-lijn) en "
                "Over/Under, en de tweede ronde kocht BTTS omdat dit duel een kandidaat-edge "
                "toonde. 23 selecties over zes markten (1X2 3, AH 7, DC 1, DNB 2, OU 8, BTTS "
                "2). De marktbalans-controle slaagt: de enige spelende competitie heeft zowel "
                "een uitkomstmarkt als een doelpuntenmarkt."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie is vandaag LEEG — factor 1,0000 over 0 speeldagen "
                "en 0 competities — en dat is correct gedrag en geen defect. MLS is de enige "
                "spelende competitie en uplift_observations laat haar weg: 28 van de 34 "
                "speeldagen is ruim over de helft, dus league_level kiest de route 'lopend' en "
                "haalt het niveau rechtstreeks uit het lopende seizoen (thuis 1,832 / uit 1,391 "
                "/ basis 1,531) in plaats van vorig seizoen × factor. Dat is precies wat "
                "prompts/run-b.md voor de vier kalenderjaarcompetities voorschrijft sinds 24 "
                "september. Het weglaten zelf is de meting en staat daarom in het rapport "
                "(§3 Stage 5)."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("4 credits van een plafond van 382 (19.885 over bij api_check.py, 115 "
                       "verbruikt deze maand, 26 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: één bulk-aanroep à 3 credits (h2h + spreads + totals) voor MLS "
                       "(USA) — de enige spelende competitie, met sportkey, dus "
                       "split_budget(382, 1) -> (1, 1) en niemand viel buiten de bulk. Stap 2: "
                       "BTTS à 1 credit voor het ene duel met een kandidaat-edge (§1a stap 2). "
                       "Marktbalans: de controle slaagt, en ruim — dezelfde competitie heeft "
                       "zowel de uitkomstmarkten als de doelpuntenmarkt. Na deze run staat het "
                       "maandverbruik op 119 van 20.000."),
            "BEURSKOERS": (
                "De gepubliceerde regel staat op een BEURS en is met oddsapi.net_price "
                "doorgerekend: Matchbook 1,78 bruto / 1,7644 na 2% commissie. De gebruiker ziet "
                "op de site 1,78; edge_pp en selection_score rekenen met 1,7644 (§5). Ook de "
                "beste 1X2-prijs op Chicago stond bij Matchbook (3,00 bruto / 2,96 netto) — de "
                "andere twee uitkomsten bij gewone boeken (Vancouver 2,35 BetOnline.ag, "
                "gelijkspel 4,00 Coolbet). De beste prijs lag 5,61% boven het "
                "BetExplorer-marktgemiddelde over 11 boeken."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
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
        for m in res["matches"]:
            if not m.get("bet"):
                continue
            pick = m.get("pick") or {}
            if (m["match"], pick.get("market"), pick.get("selection")) in gespeeld:
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

        # Dekkingstabel: óók de zestien competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/rb_oct06_stage3.json"))
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

    with open("data/picks.jsonl", "a") as f:
        for p in alle_picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(alle_picks)} picks toegevoegd aan data/picks.jsonl")


if __name__ == "__main__":
    if "--schrijf" in sys.argv:
        wegschrijven()
    else:
        for run, pad in (("B", "tmp-run/rb_oct06_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct06_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct06_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")
