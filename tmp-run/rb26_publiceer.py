"""Run B 21 sep 2026 onder §5b: run-state, picks en logboeken.

Vervangt de emit van de ochtendrun. Het verschil met die versie is §5b: niet de edge-poort
bepaalt wat er gepubliceerd wordt, maar de rangorde over alle wedstrijden van de run, met de
drempel als afkapping wanneer er meer kandidaten boven staan dan er regels passen.
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-09-26"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-26T05:15:00+02:00"      # uitleestijd van het BetExplorer-marktgemiddelde


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
    for run, pad in (("B", "tmp-run/rb26_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb26_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb26_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save, mark_completed
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb26_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen — a=1.030, b=+0.019 op 2346 "
                          "gevallen t/m 18 sep. Onveranderd sinds 20 sep: de correctie is "
                          "vrijwel neutraal (+0.8 pp bij 63%) in plaats van de ~10 pp aftrek "
                          "van begin september."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "POORT8": ("VERVALLEN sinds 25 sep 2026 (sides.LAPSES_ON, keuze van de gebruiker "
                       "op 18 sep). sides.check() laat elke kant door en zegt alleen nog met "
                       "would_block wat de poort zou hebben gedaan; dat staat per wedstrijd "
                       "onder `poort8_vervallen`, en bij een gepubliceerde bet op zo'n kant als "
                       "`poort8_zou_hebben_geblokkeerd` in de pick. De herijking van §1g is "
                       "daarmee de enige bescherming die op de underdog-kant overblijft."),
            "SELECTIE_BINDT_OP_LIJSTLENGTE": (
                "Vandaag haalden ZEVEN selecties alle acht de poorten en hun drempel (8.0 pp bij "
                "FULL, 16.0 bij LIGHT), en er passen vijf regels in de lijst van §5b. Sinds die "
                "regel op 20 sep inging is dat de eerste keer dat de rangorde bindt in plaats van "
                "de drempel. De twee die afvielen - Granada - FC Andorra (1X2 FC Andorra wint "
                "@3.45, +9.44 pp, score 3.595) en Heracles - Vitesse (1X2 Vitesse wint @4.78, "
                "+16.74 pp, score 3.148, LIGHT) - staan per wedstrijd onder "
                "`gekwalificeerd_niet_gepubliceerd` en gaan als `lijstlengte` het schaduwlogboek "
                "in, dezelfde categorie die Run C op 24 sep voor Portugal - Wales aanlegde. Geen "
                "poort heeft ze tegengehouden; ze hadden alleen minder score dan vier andere "
                "wedstrijden."),
            "POORTVOLGORDE": ("`edge` staat sinds 25 sep 2026 ACHTERAAN in de poortvolgorde in "
                              "plaats van op plek twee, omdat §5b de drempel op 20 sep van poort "
                              "naar afkapping maakte en `failed_gate` alleen de eerste dichte "
                              "poort geeft. Vandaag scheidt dat de zes wedstrijden die op poort 5 "
                              "sneuvelden (de twee methodes wijzen tegengesteld) van de "
                              "wedstrijden die simpelweg te weinig voordeel toonden."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("32 credits uitgegeven van een plafond van 1868 (18.707 over, 5 dagen "
                       "tot de maandwissel, 2 runs per dag). Stap 0: vier bulk-aanroepen (h2h + "
                       "spreads + totals, 3 credits elk) voor Segunda Division, English League "
                       "One, English League Two en MLS - de vier van de vijf spelende "
                       "competities met een sportkey bij The Odds API. Stap 2: BTTS voor de 20 "
                       "van de 23 duels met een kandidaat-edge die in een competitie met "
                       "sportkey spelen (20 credits; de drie overige zijn Keuken Kampioen "
                       "Divisie en daar is niets te koop). De Keuken Kampioen Divisie draait op "
                       "het gratis BetExplorer-marktgemiddelde; AH, DNB, DC, OU en BTTS zijn "
                       "daar niet te koop. Marktbalans (§1a): vier competities met een "
                       "doelpuntenmarkt en vier met een uitkomstmarkt, op vijf spelende - de "
                       "controle slaagt ruim, en niet met de marge van een op twee van 25 sep. "
                       "De tweede ronde veranderde geen enkele keuze: BTTS werd in geen van de "
                       "20 duels de sterkste selectie."),
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
