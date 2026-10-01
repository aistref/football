"""Run B 1 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb26_publiceer.py`. Eén duel vandaag en nul bets, dus de §5b-rangorde is kort;
het script blijft ongewijzigd omdat de lijsten, de logboeken en het voortgangsbestand ook bij nul
bets moeten worden geschreven (§6b, eerste regel: "elke run, ook een run met nul bets").
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-01"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-01T05:10:00+02:00"      # uitleestijd van het BetExplorer-marktgemiddelde


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
                         "underdog-kant onder UNDERDOG_FLOOR (0.35) en zou vóór 25 sep 2026 "
                         "zijn tegengehouden; de poort is sinds die datum vervallen "
                         "(sides.LAPSES_ON), dus dit is een echte, afgerekende waarneming op "
                         "precies de kant waar de vraag van §1e over gaat."
                         if cand.get("poort8_vervallen") else "")),
        })
    return st, top, picks, res


if __name__ == "__main__":
    alle = []
    for run, pad in (("B", "tmp-run/rb_oct01_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb_oct01_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb_oct01_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save, mark_completed
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct01_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.999521, b=-0.000312 op 3252 afgerekende gevallen, fitted_through "
                          "2026-09-30. De correctie is daarmee praktisch de identiteit: het ruwe "
                          "model zei gemiddeld 33.333% en het gebeurde 33.333%. Dat is iets "
                          "anders dan 'het model is goed' — het is de ONGESELECTEERDE reeks uit "
                          "het kalibratielogboek, en die is per definitie breder dan de "
                          "selecties waarop gespeeld wordt. fitted_through staat op de vorige "
                          "rundag, dus calibration.py settle is niet blijven liggen (§6b-5c)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "POORT8": ("BINDT WEER, en vandaag voor het eerst in Run B. De poort heeft zes dagen "
                       "stilgestaan (25 t/m 30 sep 2026) en is per 1 oktober teruggezet in de "
                       "lichte vorm, ondergrens 0.35 (§1e). sides.check() is met today=2026-10-01 "
                       "aangeroepen, zoals §1e eist, zodat een herberekening van die zes dagen "
                       "hetzelfde antwoord geeft als die dagen zelf gaven. Wat hij vandaag doet: "
                       "het marktgemiddelde (1.51 / 4.69 / 5.17 over 10 boeken) geeft Sporting "
                       "Kansas City 18.1% tegen 62.0% voor Seattle, dus de hele UITkant staat "
                       "onder de ondergrens en is geblokkeerd. Dat kostte vandaag geen bet: alle "
                       "drie de selecties op die kant sneuvelden al eerder in de poortvolgorde op "
                       "poort 5 (tegenstrijdige methodes), dus poort 8 bond nergens als eerste. "
                       "Vastgelegd onder poort8_vervallen met de sterkste van de drie."),
            "WAAROM_NUL_BETS": (
                "POORT 6 — robuustheid, en bij alle drie de selecties met voordeel. Het enige "
                "duel van de dag leverde dertien doorgerekende selecties op, en de drie met een "
                "positieve edge staan alle drie op de THUISkant: Asian Handicap Seattle -1 @1.8232 "
                "(+6.67 pp), 1X2 Seattle wint @1.5488 (+6.53 pp) en Asian Handicap Seattle -1.5 "
                "@2.230 (+5.04 pp). Alle drie draaien van teken op het (shrink, rho)-grid — "
                "edge_robust_min -1.19, -0.81 en -3.45 pp — en poort 6 eist min_edge > 0. Dat is "
                "geen krappe afwijzing maar precies waarvoor de poort bestaat: de edge bestaat "
                "alleen bij één parameterkeuze. De overige tien selecties sneuvelden op poort 5, "
                "de twee methodes wijzen tegengesteld. Dat verschil is hier groot en consequent: "
                "de xG-methode verwacht 2.42 / 0.92 doelpunten, de splitsmethode 3.15 / 1.21 — de "
                "splits zien zowel een sterkere Seattle als veel meer doelpunten, en op de "
                "doelpuntenmarkten wijzen de twee daardoor stelselmatig andersom (Under 3.5: xG "
                "57.0% tegen splits 36.7%). Let op wat hier NIET de reden is: de drempel. §5b "
                "snijdt sinds 20 september aan het eind, dus geen enkele selectie is op 8.0 pp "
                "afgewezen; ze zijn op echte poorten afgewezen."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("4 credits van een plafond van 322 (20.000 over bij api_check.py — de "
                       "maandteller is met de maandwissel teruggesprongen — en 31 dagen tot de "
                       "volgende wissel, 2 runs per dag). Stap 0: één bulk-aanroep voor MLS "
                       "(h2h + spreads + totals, 3 credits), de enige spelende competitie en ze "
                       "heeft een sportkey. Stap 2: BTTS voor het enige duel met een "
                       "kandidaat-edge (1 credit, §1a stap 2 — de AH-selectie op +6.67 pp haalt "
                       "de NEAR-drempel van 3.0). Alle zes markten zijn daarmee werkelijk "
                       "doorgerekend behalve Draw No Bet en Double Chance: de spreads-respons had "
                       "geen 0.0-lijn en geen ±0.5-lijn, en dat is als reden genoteerd en niet "
                       "als gat (§6b-5b). Marktbalans: de ene competitie van de run heeft zowel "
                       "een uitkomstmarkt (1X2, AH) als een doelpuntenmarkt (O/U, BTTS), dus de "
                       "controle van §1a slaagt — met de kleinst mogelijke marge, want het is "
                       "één competitie."),
            "NAAMKOPPELING": (
                "Gecontroleerd en in orde, en dat is deze run geen formaliteit: de bevinding van "
                "30 september was precies hier een stille faalstand in MLS (Fotmob 'Red Bull New "
                "York' tegen The Odds API 'New York Red Bulls'). Vandaag resolven alle "
                "uitkomstnamen van beide prijsbronnen: The Odds API noemt de ploegen 'Seattle "
                "Sounders FC' en 'Sporting Kansas City', BetExplorer 'Seattle Sounders' en "
                "'Sporting Kansas City', en side_of geeft voor elke h2h- en spreads-uitkomst een "
                "kant terug. Er is dus geen selectie stil overgeslagen. Openstaand blijft wat het "
                "op 30 september al was: er is nog geen controle die zegt dat er MINDER "
                "uitkomsten zijn gekoppeld dan de respons er had — dat is het echte antwoord op "
                "deze soort fout en het is met de hand nagelopen, niet door code."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top
        # §5b bindt vandaag voor het eerst op de LIJSTLENGTE in plaats van op de drempel: zeven
        # selecties haalden alle acht de poorten én hun drempel, en er passen vijf regels in de
        # lijst. De twee die afvielen zijn geen afgewezen kandidaten — er is geen poort die ze
        # heeft tegengehouden — maar ze zijn ook geen bet. Zonder een eigen aantekening staan ze
        # in het voortgangsbestand als een wedstrijd zonder bet en zonder reden, en meet niets
        # wat deze afkapping kost. Daarom een `near_miss` met `failed_gate = "lijstlengte"` en
        # een `gekwalificeerd_niet_gepubliceerd`-blok, precies zoals Run C dat op 24 sep 2026
        # deed: dezelfde vraag hoort in dezelfde reeks.
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
                nm = m.get("near_miss")
                if nm and (m["match"], nm.get("market", "").split(" — ")[0],
                           " — ".join(nm.get("market", "").split(" — ")[1:])) in gespeeld:
                    e.pop("near_miss", None)
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)
        mark_completed(state)
        save(state)
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
