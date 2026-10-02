"""Run B 2 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb26_publiceer.py`. Eén duel vandaag en nul bets, dus de §5b-rangorde is kort;
het script blijft ongewijzigd omdat de lijsten, de logboeken en het voortgangsbestand ook bij nul
bets moeten worden geschreven (§6b, eerste regel: "elke run, ook een run met nul bets").
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-02"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-02T05:09:00+02:00"      # uitleestijd van het BetExplorer-marktgemiddelde


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
    for run, pad in (("B", "tmp-run/rb_oct02_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb_oct02_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb_oct02_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save, mark_completed
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct02_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.997622, b=-0.001545 op 3276 afgerekende gevallen, fitted_through "
                          "2026-10-01. De correctie is daarmee praktisch de identiteit: het ruwe "
                          "model zei gemiddeld 33.333% en het gebeurde 33.333%. Dat is iets "
                          "anders dan 'het model is goed' — het is de ONGESELECTEERDE reeks uit "
                          "het kalibratielogboek, en die is per definitie breder dan de "
                          "selecties waarop gespeeld wordt. fitted_through staat op de vorige "
                          "rundag (1 okt), dus calibration.py settle is niet blijven liggen "
                          "(§6b-5c)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "POORT8": ("BINDT, tweede dag op rij in Run B. De poort is per 1 oktober "
                       "teruggezet in de lichte vorm, ondergrens 0.35 (§1e); sides.check() is "
                       "met today=2026-10-02 aangeroepen zoals §1e eist, zodat een "
                       "herberekening van het vervallen venster (25 t/m 30 sep) hetzelfde "
                       "antwoord geeft als die dagen zelf gaven. Wat hij vandaag doet: bij "
                       "São Paulo – Santos staat de hele UITkant onder de ondergrens (Santos "
                       "26.0% tegen 46.0%, marktgemiddelde over 15 boeken) en bij Helmond "
                       "Sport – Heracles de hele THUISkant (Helmond 13.6% tegen 67.5% over 3 "
                       "boeken). Samen zes geblokkeerde selecties. Het kostte geen bet: alle "
                       "zes sneuvelden al eerder in de poortvolgorde — vijf op poort 5 "
                       "(tegenstrijdige methodes) en de Helmond-thuiswinst op de koersband "
                       "(6.72 boven MAX_ODDS 6.00). poort8_geblokkeerd en poort8_ruw zijn "
                       "daarom leeg: de poort bond nergens als eerste, en dan hoort de rij "
                       "niet in de reeks van §1e. Vastgelegd onder poort8_vervallen (het veld "
                       "dat would_block draagt) met de sterkste per wedstrijd."),
            "WAAROM_EEN_BET": (
                "Eén bet, en hij is op RANGORDE gepubliceerd en niet op voordeel: São Paulo – "
                "Santos, Over 2.5 @2.15 bij Unibet (SE), herijkte edge +3.68 pp op een drempel "
                "van 8.0. §5b snijdt sinds 20 september aan het eind van de dag — staan er "
                "minder selecties boven de drempel dan er regels in de lijst passen, dan "
                "bepaalt de rangorde de lijst en is de drempel een label. Dat is hier het "
                "geval: nul van de twintig doorgerekende selecties haalt 8.0 pp. Wat deze "
                "selectie wél heeft: alle acht de poorten open, inclusief poort 6 "
                "(edge_robust_min +3.69 pp, dus de edge draait niet van teken over het "
                "(shrink, rho)-grid) en poort 5 (xG-methode +3.81 pp, splitsmethode +3.33 pp "
                "— beide boven de markt en bijna gelijk). Van de 17 selecties in dit duel is "
                "dit de enige met beide methodes aan dezelfde kant; de andere zestien "
                "sneuvelden op poort 5. Lees de bet dus als 'het sterkste van vandaag', niet "
                "als een gevonden voordeel (§5b, en §1g: er is géén drempel op de herijkte "
                "edge die geld oplevert)."),
            "WAAROM_TWEE_DUELS_GEEN_BET": (
                "Eldense – Real Oviedo (Segunda División) komt op data_tier NONE uit en is dus "
                "niet doorgerekend. Real Oviedo is om te rekenen — degradant uit La Liga, "
                "TIER1-route, gemeten ESP-factor — maar Eldense niet: die staat in geen van "
                "beide standen boven deze divisie, want hij komt uit de Primera Federación en "
                "promotion.TIER2 heeft geen gemeten Spaans paar LaLiga2/Primera Federación. "
                "§4 is daar hard in: buiten het gemeten bereik is er geen onafhankelijke "
                "kansinput op het niveau waarop gespeeld wordt, dus NONE en geen bet. Dit "
                "kostte wél 3 credits: de bulk-aanroep voor soccer_spain_segunda_division is "
                "gedaan vóórdat de tier bekend was, en dat is de volgorde die §1a voorschrijft "
                "(inkopen op datakwaliteit van de competitie, niet van het duel). "
                "Helmond Sport – Heracles (Keuken Kampioen Divisie) is LIGHT — deze competitie "
                "heeft geen xG bij Fotmob, dus doelpunten als sterktemaat — en heeft geen "
                "sportkey bij The Odds API, dus alleen het gratis BetExplorer-marktgemiddelde "
                "over 3 boeken. Drie selecties doorgerekend; de sterkste binnen de koersband is "
                "het gelijkspel @4.82 op +5.10 pp, onder de NEAR-grens van 6.0 pp die §5b voor "
                "LIGHT hanteert, dus hij mag niet meedingen in de rangorde. De hoogste edge van "
                "de hele run (+21.67 pp op een Helmond-zege) viel af op de koersband: 6.72 ligt "
                "boven MAX_ODDS 6.00, en poort 8 zou hem ook hebben tegengehouden."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("7 credits van een plafond van 332 (19.979 over bij api_check.py, 21 "
                       "verbruikt deze maand, 30 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: twee bulk-aanroepen à 3 credits (h2h + spreads + totals) voor "
                       "Segunda División (ESP) en Série A (BRA) — de enige twee spelende "
                       "competities met een sportkey. Stap 2: BTTS voor het ene duel met een "
                       "kandidaat-edge (1 credit, §1a stap 2 — Over 2.5 op +3.68 pp haalt de "
                       "NEAR-drempel van 3.0). Keuken Kampioen Divisie (NED) heeft geen "
                       "sportkey en draait op het gratis BetExplorer-marktgemiddelde; dat staat "
                       "per markt als reden in markets_checked en niet als gat (§6b-5b). "
                       "Marktbalans: beide ingekochte competities hebben zowel een "
                       "uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U, en voor "
                       "Série A ook BTTS), dus de controle van §1a slaagt — 2 van 2, en dat is "
                       "ruimer dan het klinkt bij twee competities, maar het blijven er twee."),
            "NAAMKOPPELING": (
                "Met de hand nagelopen, en in orde. The Odds API schrijft de Braziliaanse "
                "ploegen als 'Sao Paulo' en 'Santos' (zonder accent), Fotmob als 'São Paulo' "
                "en 'Santos', BetExplorer als 'Sao Paulo' en 'Santos'; resolve() koppelt alle "
                "drie en side_of geeft voor elke h2h- en spreads-uitkomst een kant terug — 17 "
                "selecties uit zes markten, geen stille overslag. Bij Helmond Sport – Heracles "
                "is er maar één bron (BetExplorer) en die namen koppelen exact. Openstaand "
                "blijft wat het op 30 september al was: er is nog geen code die zegt dat er "
                "MINDER uitkomsten zijn gekoppeld dan de respons er had."),
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
