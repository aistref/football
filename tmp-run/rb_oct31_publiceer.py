"""Run B 30 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct28_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. ACHT van de zeventien competities speelden, met samen TWAALF
duels in het inzetvenster en nul afgekapt (cap 55 op vrijdag). EEN gepubliceerde regel, en die
haalt zijn eigen lat — met 0,03 procentpunt.

Drie dingen die vandaag in de parameters horen:

* **De enige regel staat op de Under-kant en haalt poort 9 met drie honderdsten van een
  procentpunt.** Dat is de smalste doorgang die die rem ooit heeft gegeven.
* **Pinnacle spreekt hem het hardst tegen van alle vijf toetsbare (duel, lijn)-paren** (+13,67 pp
  op de Under-kant), terwijl hij op de 1X2 van hetzelfde duel juist het meest met Pinnacle eens is.
* **Een naamkoppeling is gerepareerd die Roda JC Kerkrade – Jong AZ Alkmaar al zijn prijzen
  kostte** — zie bevinding 1.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-31"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026, dus +01:00
CAPTURED = "2026-10-31T04:20:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), wintertijd


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
    for run, pad in (("B", "tmp-run/rb_oct31_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        from rb_oct31_params import parameters
        state["parameters"] = parameters(res, max_shortlist(date.fromisoformat(DAG)))

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
        s3 = json.load(open("tmp-run/rb_oct31_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct31_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct31_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct31_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")
