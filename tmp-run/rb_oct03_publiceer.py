"""Run B 3 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct02_publiceer.py`, met één inhoudelijke wijziging die vandaag voor het eerst
bindt — zie `near_miss` hieronder en Bevinding 1 in het runrapport.
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-03"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-03T05:12:00+02:00"      # uitleestijd van het BetExplorer-marktgemiddelde


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
    for run, pad in (("B", "tmp-run/rb_oct03_results.json"),):
        st, top, picks, res = bouw(run, pad)
        json.dump(top, open(f"tmp-run/rb_oct03_top_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        json.dump(picks, open(f"tmp-run/rb_oct03_picks_{run.lower()}.json", "w"), ensure_ascii=False, indent=1)
        alle += picks
        print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} bets")
        for p in picks:
            print(f"   {p['selection'][:30]:30s} @{p['odds']:5.2f}  edge {p['edge_pp']:+5.2f}  {p['competition']}")
    print(f"\ntotaal {len(alle)} picks klaar om weg te schrijven")


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save, mark_completed
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct03_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.985897, b=-0.009161 op 3318 afgerekende gevallen, fitted_through "
                          "2026-10-02. De correctie is praktisch de identiteit: het ruwe model "
                          "zei gemiddeld 33.333% en het gebeurde 33.333%. fitted_through staat "
                          "op de vorige rundag (2 okt), dus calibration.py settle is niet "
                          "blijven liggen (§6b-5c). Let op wat die identiteit wél en niet zegt: "
                          "de reeks is de ONGESELECTEERDE ijksteekproef, breder dan de selecties "
                          "waarop gespeeld wordt — zie §1e, punt 3 van 30 september."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "POORT8": ("BINDT, derde dag op rij in Run B, in de lichte vorm met ondergrens 0.35 "
                       "(§1e). sides.check() is met today=2026-10-03 aangeroepen zoals §1e eist. "
                       "Vandaag hield de poort voor het eerst sinds het terugzetten ook "
                       "werkelijk iets tegen als EERSTE dichte poort, en het zijn precies de "
                       "handicaps op de zwakkere ploeg waar §6f over gaat: Burgos CF +1.5 @1.52 "
                       "bij Almería (markt 17.9% tegen 58.3%, score 8.844 — de hoogste ruwe "
                       "score van de hele run) en Fleetwood Town +0.75 @2.078 bij Salford "
                       "(markt 19.3% tegen 56.7%, score 5.582), met respectievelijk 1 en 3 "
                       "andere geblokkeerde selecties op dezelfde kant. Beide gaan als "
                       "failed_gate='underdog' het schaduwlogboek in; dat is de reeks die op "
                       "30 september op 20 afgewikkelde gevallen stond waar §6d er ~30 vraagt. "
                       "poort8_ruw is leeg omdat dezelfde twee selecties al in "
                       "poort8_geblokkeerd staan (§5a regel 2: nooit dezelfde selectie twee "
                       "keer). Wat het kostte: bij Salford is wél gepubliceerd, maar op de "
                       "doelpuntenmarkt (Under 2.75), niet op de geblokkeerde kant; bij Almería "
                       "leverde het duel geen regel in de lijst op."),
            "WAAROM_VIJF_BETS": (
                "Vijf regels, en maar één ervan is een gevonden voordeel. Alleen Accrington "
                "Stanley – Cheltenham Town haalt de lat van 8.0 pp (+9.45 pp herijkt, +9.67 pp "
                "ruw); de andere vier staan erin omdat §5b sinds 20 september aan het EIND van "
                "de dag snijdt: staan er minder selecties boven de drempel dan er regels in de "
                "lijst passen (vijf op zaterdag), dan bepaalt de rangorde de lijst en gaat de "
                "drempel mee als label. Van de 202 doorgerekende selecties haalde er precies "
                "één zijn drempel. Lees de lijst dus als 'het sterkste van vandaag' en niet als "
                "vijf gevonden voordelen — §1g heeft op 552 afgerekende gevallen gemeten dat er "
                "géén drempel op de herijkte edge bestaat die geld oplevert. De §5b-afkapping "
                "op LIJSTLENGTE bond vandaag niet: er stond maar één selectie boven de drempel, "
                "dus er viel niets gekwalificeerds buiten de lijst en de reeks 'lijstlengte' "
                "groeit deze run niet."),
            "MAX_LIGHT_TOEGEPAST": (
                "De lijst bevat exact twee LIGHT-regels — Exeter City – Rotherham United (Draw "
                "No Bet) en RKC Waalwijk – FC Emmen (1X2) — en dat is het plafond "
                "MAX_LIGHT_IN_SHORTLIST van §0. toplist.py heeft het toegepast; er stond geen "
                "derde LIGHT-regel te wachten, dus het plafond heeft vandaag niets afgesneden."),
            "WAAROM_TWEE_DUELS_GEEN_BET": (
                "Twee van de 22 duels komen op data_tier NONE uit en zijn niet doorgerekend, en "
                "het is twee keer DEZELFDE structurele oorzaak: een promovendus uit een divisie "
                "waarvoor promotion.TIER2 geen gemeten paar kent. Sabadell – FC Andorra "
                "(Segunda División): Sabadell komt uit de Primera Federación en TIER2 heeft "
                "geen Spaans paar LaLiga2/Primera Federación, dus de omrekening valt terug op "
                "de TIER1-tak (degradant uit La Liga) en die vindt hem daar natuurlijk ook "
                "niet. Rochdale – Swindon Town (English League Two): exact hetzelfde, nu met de "
                "National League onder League Two. Het coverage-briefje van 2 oktober noemde "
                "dit al als structureel gat in de Segunda; vandaag blijkt het net zo goed voor "
                "League Two te gelden, en dat zijn twee van de vijf spelende competities. §4 is "
                "hier hard in: buiten het gemeten bereik is er geen onafhankelijke kansinput op "
                "het niveau waarop gespeeld wordt, dus NONE en geen bet. Het kostte geen extra "
                "credits — de bulk wordt per competitie gekocht, niet per duel."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("20 credits van een plafond van 343 (19.949 over bij api_check.py, 51 "
                       "verbruikt deze maand, 29 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: vier bulk-aanroepen à 3 credits (h2h + spreads + totals) voor "
                       "Segunda División (ESP), English League One (ENG), English League Two "
                       "(ENG) en Série A (BRA) — alle vier de spelende competities met een "
                       "sportkey, dus split_budget(343, 4) -> (4, 4) en niemand viel buiten de "
                       "bulk. Stap 2: BTTS voor acht van de negen duels met een kandidaat-edge "
                       "(1 credit per duel, §1a stap 2); het negende, RKC Waalwijk – FC Emmen, "
                       "viel af omdat de Keuken Kampioen Divisie geen sportkey heeft. Die "
                       "competitie draait volledig op het gratis BetExplorer-marktgemiddelde; "
                       "dat staat per markt als reden in markets_checked en niet als gat "
                       "(§6b-5b). Marktbalans: alle vier de ingekochte competities hebben zowel "
                       "een uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U, en "
                       "bij acht duels ook BTTS) — 4 van 4, de ruimste marge sinds de controle "
                       "bestaat."),
            "NAAMKOPPELING": (
                "Eén echte fout gevonden en hersteld, en ze zat in de Braziliaanse Série A — "
                "niet in de diakrieten waar het coverage-briefje van 2 oktober voor "
                "waarschuwde, want die haalt norm() gewoon weg. Fotmob schrijft "
                "'Atlético-MG' en 'RB Bragantino', The Odds API 'Atletico Mineiro' en "
                "'Bragantino-SP': de tokens delen er telkens één maar geen van beide is een "
                "deelverzameling van de ander, en dat is wat resolve() eist. find_event() "
                "koppelde de wedstrijd nog wél via best_pair, maar side_of() gaf voor allebei "
                "de ploegen None. Gevolg bij de eerste doorrekening: van de 1X2 bleef alleen "
                "het gelijkspel over en kwamen Asian Handicap, Draw No Bet en Double Chance "
                "alle drie op nul selecties uit, terwijl de spreads-respons gewoon lijnen "
                "bevatte — 3 doorgerekende selecties in plaats van 13, met 'geen "
                "handicaplijnen' in markets_checked, wat leest als 'geen boek bood ze aan'. "
                "Vier aliassen toegevoegd in tmp-run/ra_names.py en de analyse opnieuw "
                "gedraaid. Dit is de vijfde keer dat deze faalstand toeslaat (FC København, "
                "NK Lokomotiva, Universitatea Craiova, Red Bull New York) en nog steeds is er "
                "geen code die zegt dat er MINDER uitkomsten zijn gekoppeld dan de respons er "
                "had; zie 'Wat ik nog moet doen'."),
            "AFGELASTINGEN": (
                "Negen van de 31 duels op de Engelse daglijst zijn afgelast en vallen daarmee "
                "buiten het inzetvenster: zes in League One (AFC Wimbledon – Stevenage, "
                "Barnsley – MK Dons, Bromley – Wycombe, Luton – Doncaster, Peterborough – "
                "Notts County, Wigan – Mansfield) en drie in League Two (Colchester – Port "
                "Vale, Northampton – Oldham, Walsall – Crawley). runwindow.matches_for_run "
                "filtert ze eruit op status.cancelled; zonder die vermelding leest League One "
                "als een competitie met drie duels op een zaterdag."),
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
