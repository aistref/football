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

DAG = "2026-09-25"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-25T05:20:00+02:00"      # uitleestijd van het BetExplorer-marktgemiddelde


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
                      f"shrink staat sinds 19 sep op 1.00 (§6e)."),
        })
    return st, top, picks, res


if __name__ == "__main__":
    alle = []
    for run, pad in (("B", "tmp-run/rb25_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb25_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb25_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save, mark_completed
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb25_results.json"),):
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
            "POORT8": ("VERVALLEN per vandaag (sides.LAPSES_ON = 2026-09-25, keuze van de "
                       "gebruiker op 18 sep 2026). sides.check() laat elke kant door en zegt "
                       "alleen nog met would_block wat de poort zou hebben gedaan; dat staat per "
                       "wedstrijd onder `poort8_vervallen`. De herijking van §1g is daarmee vanaf "
                       "vandaag de enige bescherming op de underdog-kant."),
            "POORTVOLGORDE": ("`edge` staat vanaf vandaag ACHTERAAN in de poortvolgorde in plaats "
                              "van op plek twee. §5b maakte de drempel op 20 sep van poort naar "
                              "afkapping, maar de volgorde ging niet mee, en `failed_gate` geeft "
                              "alleen de eerste dichte poort. Vandaag was dat letterlijk te zien: "
                              "alle drie de selecties van FC Dordrecht – Almere City sneuvelden op "
                              "poort 5 (xG +18.40 pp tegen splits −8.31 pp) en kregen `edge` als "
                              "label. Zo'n rij vervuilt in `shadow.py stats` de reeks van een "
                              "poort die de selectie niet heeft tegengehouden."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("3 credits uitgegeven van een plafond van 1558 (18.719 over, 6 dagen tot "
                       "de maandwissel): één bulk-aanroep (h2h + spreads + totals) voor Segunda "
                       "División, de enige van de twee competities met een sportkey bij The Odds "
                       "API. De Keuken Kampioen Divisie heeft er geen en draait op het gratis "
                       "BetExplorer-marktgemiddelde; AH, DNB, DC, OU en BTTS zijn daar niet te "
                       "koop. Marktbalans: de inkoop leverde één competitie met een "
                       "doelpuntenmarkt (Segunda, via de bulk) en twee met een uitkomstmarkt — "
                       "de controle van §1a slaagt, met de kleinst mogelijke marge van één op "
                       "twee, en de enige competitie mét doelpuntenmarkt kwam op NONE uit."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top
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
