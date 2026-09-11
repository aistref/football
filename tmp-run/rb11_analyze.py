"""Stage 5 — analyse Run B 11 sep 2026. Beide methodes, alle zes markten, acht poorten.

Drie verschillen met de versie van 5 sep, alle drie regelwijzigingen van die avond:
  * 1X2 komt van de beste prijs uit de h2h-bulk en niet meer van het BetExplorer-
    marktgemiddelde, en gaat door `oddsapi.net_price` als het een beurs is (§1a).
  * `my_raw` is 0.80 xG / 0.20 splits in plaats van het ongewogen gemiddelde (§1f).
  * `my_prob` loopt daarna door `recalibrate.apply` — herijking op uitslagen (§1g).
Het BetExplorer-gemiddelde blijft in gebruik voor het kalibratieblok (§6e) en poort 8:
dat zijn oordelen over de wedstrijd, geen prijzen om op te spelen.
"""
import json, sys
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from scripts import fotmob, model, calibration, oddsapi, promotion, understat, sides, recalibrate
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
                           edge_pp, asian_prob, dnb_prob, totals_prob, robustness_check,
                           selection_score, early_season_uplift, scale_level, splits_from_fotmob,
                           blend_seasons, blend_weight, combine_probs)
from ra_names import resolve, best_pair
from b_merge import merge_teams


def fetch_stats(pid, season):
    """Fotmob-stand met de half-uiteengevallen rijen samengevoegd (b_merge).

    Nodig voor Run B en niet voor Run A: op LaLiga2 2025/2026 levert Fotmob 30 'ploegen'
    voor een competitie van 22, doordat acht clubs onder twee verschillend geaccentueerde
    namen staan — de ene rij met xg/xga/mp, de andere met gf/ga/played/home/away. Zonder
    samenvoegen valt zo'n ploeg ten onrechte op NONE (gemeten 4 sep 2026).
    """
    st = dict(fotmob.fetch_league_stats(pid, season))
    st["teams"], st["_merged"] = merge_teams(st["teams"])
    return st

DAY = date(2026, 9, 11)
NL = timezone(timedelta(hours=2))
THRESH = {"FULL": 8.0, "LIGHT": 16.0}   # verhoogd 31 aug 2026, zie _shared-rules.md §0
# Vanaf welke edge een afgewezen kandidaat nog een `near_miss` krijgt (en dus in shadow.jsonl
# belandt). Dit is met opzet de OUDE drempel: zonder deze ondergrens verdwijnt precies de groep
# die door de verhoging van vandaag wegvalt uit het schaduwlogboek, en is over een maand niet te
# meten of die verhoging geld bespaarde of alleen bets kostte.
NEAR = {"FULL": 3.0, "LIGHT": 6.0}
MIN_ODDS, MAX_ODDS = 1.30, 6.00

# Een bekercompetitie heeft zelf geen stand en dus geen divisie erboven of eronder. De ploegen
# komen wél uit een divisie: dit is de competitie waarvan de basis (niveau, splits) is genomen in
# ra_stage3.py, en dus ook de competitie waarop `promotion.TIER1/TIER2` moet worden opgezocht.
PROMO_COMP = {
    "Coppa Italia (ITA)": "Serie A (ITA)",
    "DFB Pokal (GER)":    "Bundesliga (GER)",
    "KNVB Beker (NED)":   "Eredivisie (NED)",
    "FA Cup (ENG)":       "Premier League (ENG)",
    "League Cup (ENG)":   "Premier League (ENG)",
}

FIT = recalibrate.load_fit()            # §1g — één keer per run, leest picks.jsonl + shadow.jsonl
print(f"herijking: {FIT}")

cands = json.load(open("tmp-run/rb11_ctx.json"))
s3 = json.load(open("tmp-run/rb11_stage3.json"))
stats_meta, us_meta = s3["stats"], s3["understat"]
odds = json.load(open("tmp-run/rb11_odds.json"))

# ---------- vroeg-seizoenscorrectie (§3 Stage 5) -------------------------------------------
# Afwijking van de gebruikelijke vorm, en die hoort in het runrapport. De enige competitie die
# vandaag op de Run B-kalender staat (Czech First League) heeft géén xG bij Fotmob, dus de
# gebruikelijke observatie `(avg_xg vorig, avg_xg dit, speeldagen)` bestaat hier niet en
# `early_season_uplift([])` zou stilzwijgend op factor 1.0 uitkomen — dat is niet "geen
# correctie nodig" maar "niet gemeten".
#
# Wat er in plaats daarvan in gaat: hetzelfde niveauverschil, gemeten op DOELPUNTEN. Dat is de
# eenheid waarin de hele run rekent (zie `league_ctx` hieronder: zonder xG komt zowel het
# competitieniveau als de teamsterkte uit doelpunten), dus teller en noemer staan in dezelfde
# eenheid. Het blijft een waarneming uit de stand en er komt geen enkele bookmakerprijs aan te
# pas — §2 en de waarschuwing bij `early_season_uplift` blijven dus gerespecteerd. Wat het NIET
# is: een correctie die over competities is gepoold. Het is één competitie, en dat is precies de
# ruis waar de docstring voor waarschuwt; de prior van 8 speeldagen trekt hem daarom stevig terug.
obs, obs_comps, obs_eenheid = [], [], {}
for comp, s in stats_meta.items():
    p, c = s["prev"], s["cur"]
    if p.get("has_xg") and c.get("has_xg") and p.get("avg_xg") and c.get("avg_xg") and c.get("played"):
        obs.append((p["avg_xg"], c["avg_xg"], c["played"])); obs_comps.append(comp)
        obs_eenheid[comp] = "xG"
    elif p.get("home_gpm") and p.get("away_gpm") and c.get("played"):
        cur_stats = fotmob.fetch_league_stats(s3["fixtures"][comp]["primaryId"],
                                              s3["fixtures"][comp]["s_cur"])
        base = (p["home_gpm"] + p["away_gpm"]) / 2
        cur = (cur_stats["home_goals_per_match"] + cur_stats["away_goals_per_match"]) / 2
        if base > 0 and cur > 0:
            obs.append((base, cur, c["played"])); obs_comps.append(comp)
            obs_eenheid[comp] = f"doelpunten ({base:.3f} -> {cur:.3f} per ploeg per duel)"
FACTOR, POOLED, TOTAL_MD = early_season_uplift(obs)
print(f"vroeg seizoen: factor {FACTOR:.4f} (gepoold {POOLED:.4f} over {TOTAL_MD} speeldagen, "
      f"{len(obs)} competities) — eenheid: {obs_eenheid}")

# ---------- competitiebasis ------------------------------------------------------------------
league_cache = {}
league_raw = {}   # het ongecorrigeerde niveau, alleen om de correctie te controleren (§3 Stage 5)
def league_ctx(comp, pid, season, season_cur=None):
    if comp not in league_cache:
        st = fetch_stats(pid, season)
        # Zes van de dertien Run B-competities hebben geen xG bij Fotmob. Het competitieniveau
        # komt daar uit de doelpunten zelf; de teamsterktes hieronder doen hetzelfde, zodat
        # teller en noemer in dezelfde eenheid staan.
        avg = st["avg_xg_per_match"] or (st["home_goals_per_match"] + st["away_goals_per_match"]) / 2
        lg = LeagueContext(home_goals_per_match=st["home_goals_per_match"],
                           away_goals_per_match=st["away_goals_per_match"],
                           avg_xg_per_match=avg)
        # De stand van het LOPENDE seizoen, voor blend_seasons (§4). Dit is de reden dat de
        # routine gedurende het seizoen beter wordt in plaats van op augustus te blijven staan.
        cur_teams = {}
        if season_cur:
            try:
                cur_teams = fetch_stats(pid, season_cur)["teams"]
            except Exception as e:
                print(f"  {comp}: lopend seizoen niet op te halen ({type(e).__name__}) — "
                      f"alleen vorig seizoen")
        league_raw[comp] = lg
        league_cache[comp] = (scale_level(lg, FACTOR), st["teams"], st, cur_teams,
                              st["avg_xg_per_match"] is not None)
    return league_cache[comp]

# ---------- Understat, tweede xG-model (§4) ---------------------------------------------------
us_cache = {}
def understat_pair(comp, code, season, home, away, lg_fotmob):
    """(TeamStats, TeamStats, LeagueContext) op Understat-schaal, of None."""
    if not code:
        return None
    if comp not in us_cache:
        try:
            d = understat.fetch_league(code, understat.season_code(season))
            t = understat.team_stats(d)
            c = understat.league_context(t)
            us_cache[comp] = (t, LeagueContext(home_goals_per_match=c["home_goals_per_match"],
                                               away_goals_per_match=c["away_goals_per_match"],
                                               avg_xg_per_match=c["avg_xg_per_match"]), d)
        except Exception as e:
            us_cache[comp] = None
            print(f"  understat {comp}: {type(e).__name__}: {e}")
    if not us_cache[comp]:
        return None
    teams, uctx, raw = us_cache[comp]
    rh, ra = resolve(home, teams), resolve(away, teams)
    if not (rh and ra):
        return None
    # normaliseren op het EIGEN competitiegemiddelde van Understat (§4), daarna op het niveau
    # dat de run gebruikt: alleen de sterkteverhouding komt van Understat, niet het niveau.
    uctx_scaled = scale_level(uctx, FACTOR)
    hs = TeamStats(xg=teams[rh]["xg"], xga=teams[rh]["xga"], matches_played=teams[rh]["mp"])
    as_ = TeamStats(xg=teams[ra]["xg"], xga=teams[ra]["xga"], matches_played=teams[ra]["mp"])
    roll = {"home": understat.rolling_xg(raw, rh, 8), "away": understat.rolling_xg(raw, ra, 8)}
    return hs, as_, uctx_scaled, rh, ra, roll

# ---------- prijzen terugvinden ---------------------------------------------------------------
def find_1x2(comp, home, away):
    rows = odds["fixtures"].get(comp) or []
    pool = [r for r in rows if r["is_today"]] or rows
    for r in pool:
        if resolve(home, {r["home"]: 1}) and resolve(away, {r["away"]: 1}):
            return r
    return best_pair(home, away, pool, lambda r: r["home"], lambda r: r["away"])

def find_event(comp, kind, home, away):
    evs = (odds["raw"].get(kind) or {}).get(comp) or []
    for e in evs:
        if resolve(home, {e["home_team"]: 1}) and resolve(away, {e["away_team"]: 1}):
            return e
    return best_pair(home, away, evs, lambda e: e["home_team"], lambda e: e["away_team"])

def side_of(outcome, home, away):
    if resolve(outcome, {home: 1}): return "home"
    if resolve(outcome, {away: 1}): return "away"
    return None

def best_btts(match_id):
    evs = odds["raw"]["btts"].get(str(match_id)) or []
    ev = evs if isinstance(evs, dict) else (evs[0] if evs else None)
    if not ev: return {}
    best = {}
    for b in ev.get("bookmakers", []):
        for m in b.get("markets", []):
            if m.get("key") != "btts": continue
            for o in m.get("outcomes", []):
                n = o["name"].lower()
                if n not in best or o["price"] > best[n][0]:
                    best[n] = (o["price"], b["title"])
    return best

# ---------- Stage 4: rangschikken en afkappen --------------------------------------------------
from scripts.ranking import sort_key, max_deep_analyses
CAP = max_deep_analyses(DAY)

def markets_available(c):
    n = 0
    if find_1x2(c["competition"], c["home"], c["away"]): n += 1
    if c["competition"] in odds["bought"]["spreads"] and find_event(c["competition"], "spreads", c["home"], c["away"]): n += 3
    if c["competition"] in odds["bought"]["totals"] and find_event(c["competition"], "totals", c["home"], c["away"]): n += 1
    if best_btts(c["match_id"]): n += 1
    return n

ranked = [c for c in cands if c["tier"] != "NONE"]
for c in ranked:
    c["markets"] = markets_available(c)
ranked.sort(key=lambda c: sort_key("FULL" if c["tier"] == "FULL" else "LIGHT",
                                   c["richness"], c["markets"], c["kickoff_utc"]))
keep = {id(c) for c in ranked[:CAP]}
trunc = ranked[CAP:]
TRUNC = {"cap": CAP, "afgekapt": len(trunc),
         "laagste_die_het_haalde": (None if len(ranked) < CAP else
             {"match": f"{ranked[CAP-1]['home']} – {ranked[CAP-1]['away']}",
              "richness": ranked[CAP-1]["richness"], "markets": ranked[CAP-1]["markets"]}),
         "hoogste_die_afviel": ({"match": f"{trunc[0]['home']} – {trunc[0]['away']}",
              "richness": trunc[0]["richness"], "markets": trunc[0]["markets"]} if trunc else None),
         "lijst": [f"{c['home']} – {c['away']}" for c in trunc],
         "laagste_richness_in_run": min(c["richness"] for c in ranked) if ranked else None,
         "hoogste_richness_in_run": max(c["richness"] for c in ranked) if ranked else None}
print("afkapping:", json.dumps(TRUNC, ensure_ascii=False))

# ---------- analyse ----------------------------------------------------------------------------
results = []
for c in cands:
    ko = datetime.fromisoformat(c["kickoff_utc"].replace("Z", "+00:00"))
    row = {"competition": c["competition"], "match": f"{c['home']} – {c['away']}",
           "match_id": c["match_id"], "home": c["home"], "away": c["away"],
           "kickoff_utc": c["kickoff_utc"], "kickoff_nl": ko.astimezone(NL).strftime("%H:%M"),
           "richness": c["richness"], "richness_parts": c.get("richness_parts"),
           "markets": c.get("markets"), "bet": False, "all_candidates": [], "markets_checked": {},
           # §1c eist het contextblok bij ELKE wedstrijd waarvoor de context is opgehaald. Het
           # stond hieronder pas ná de tier-poort, waardoor een duel op NONE zijn (al gratis
           # opgehaalde) context verloor en niet in het contextlogboek terechtkwam. Vandaag zijn
           # dat er zeven van de negenendertig — precies de steekproef die §1c wil vergroten.
           "context": c.get("ctx")}

    lg, teams, st, cur_teams, HAS_XG = league_ctx(c["competition"], c["primaryId"], c["season"],
                                                  c.get("season_cur"))
    row["eenheid"] = "xG" if HAS_XG else "doelpunten (geen xG bij Fotmob voor deze competitie)"

    # --- teamsterktes: uit de stand, of omgerekend uit de divisie eronder (promovendi) dan wel
    #     erboven (degradanten). Beide richtingen zijn §4; de tweede kan sinds 1 sep 2026. ---
    promo_notes, tier_box = {}, [c["tier"]]

    def _source_name(name, fotmob_id, season):
        """De naam zoals de brontabel hem schrijft, of de originele als hij er niet in staat."""
        try:
            tbl = fetch_stats(fotmob_id, season)["teams"]
        except Exception:
            return name
        return resolve(name, tbl) or name

    blend_notes = {}

    def side_stats(name, table_key):
        if table_key:
            r = teams[table_key]
            if HAS_XG and r.get("xg") is not None:
                prior = TeamStats(xg=r["xg"], xga=r["xga"], matches_played=r["mp"])
            else:
                # Geen xG in deze competitie: doelpunten voor/tegen zijn dan de kansinput, en
                # de competitiebasis hierboven staat in dezelfde eenheid. Dat is `LIGHT` (§4).
                if r.get("gf") is None or not r.get("played"):
                    raise promotion.PromotionError(
                        f"{name}: geen xG en geen doelpuntenrij in de stand van {c['season']}")
                prior = TeamStats(xg=float(r["gf"]), xga=float(r["ga"]), matches_played=r["played"])
                tier_box[0] = "LIGHT"
            # Lopend seizoen meewegen naar rato van gespeelde duels (§4, blend_seasons).
            cur_key = resolve(name, cur_teams) if cur_teams else None
            cur = None
            if cur_key:
                cr = cur_teams[cur_key]
                if HAS_XG and cr.get("mp") and cr.get("xg") is not None:
                    cur = TeamStats(xg=cr["xg"], xga=cr["xga"], matches_played=cr["mp"])
                elif (not HAS_XG) and cr.get("played") and cr.get("gf") is not None:
                    cur = TeamStats(xg=float(cr["gf"]), xga=float(cr["ga"]),
                                    matches_played=cr["played"])
            merged = blend_seasons(prior, cur)
            if cur is not None:
                blend_notes[name] = {
                    "eenheid": "xG" if HAS_XG else "doelpunten",
                    "duels_dit_seizoen": cur.matches_played,
                    "gewicht_dit_seizoen": round(blend_weight(cur.matches_played), 3),
                    "xg_per_duel": {"vorig": round(prior.xg_per_match, 3),
                                     "dit": round(cur.xg_per_match, 3),
                                     "gewogen": round(merged.xg_per_match, 3)},
                    "xga_per_duel": {"vorig": round(prior.xga_per_match, 3),
                                      "dit": round(cur.xga_per_match, 3),
                                      "gewogen": round(merged.xga_per_match, 3)}}
            # De splits blijven van vorig seizoen: die methode heeft thuis/uit-doelpunten
            # nodig en Fotmob geeft die voor het lopende seizoen pas laat betrouwbaar.
            return merged, splits_from_fotmob(r), None
        errors = []
        pcomp = PROMO_COMP.get(c["competition"], c["competition"])
        # `TIER2`/`TIER1` staan onder de namen uit run-a.md; run-b.md schrijft er drie
        # anders (Segunda División, English League One/Two). `promotion._resolve` vertaalt
        # dat — een rauwe dict-lookup vindt ze niet en dat kostte op 5 sep 2026 acht duels.
        pkey = promotion._resolve(pcomp)
        t2 = promotion.TIER2.get(pkey)
        if t2:
            try:
                conv = promotion.convert(pcomp, _source_name(name, t2.fotmob_id, c["season"]),
                                         c["season"], lg)
                tier_box[0] = "NONE" if not conv.in_range else "LIGHT"
                return conv.stats, conv.splits, conv.note
            except promotion.PromotionError as e:
                errors.append(f"promovendus: {e}")
        t1 = promotion.TIER1.get(pkey)
        if t1:
            try:
                conv = promotion.convert_relegated(pcomp,
                                                   _source_name(name, t1.fotmob_id, c["season"]),
                                                   c["season"], lg)
                tier_box[0] = "NONE" if not conv.in_range else "LIGHT"
                return conv.stats, conv.splits, conv.note
            except promotion.PromotionError as e:
                errors.append(f"degradant: {e}")
        raise promotion.PromotionError("; ".join(errors) or
                                       f"geen divisie boven of onder {pcomp!r} bekend")
    try:
        hs, sp_h, nh = side_stats(c["home"], c["table_home"])
        as_, sp_a, na = side_stats(c["away"], c["table_away"])
        tier = tier_box[0]
    except promotion.PromotionError as e:
        row["tier"] = "NONE"; row["reason"] = f"geen historie in deze divisie: {e}"
        results.append(row); continue
    if nh: promo_notes["thuis"] = nh
    if na: promo_notes["uit"] = na
    row["tier"] = tier
    if promo_notes: row["promovendi"] = promo_notes
    if blend_notes: row["seizoensweging"] = blend_notes
    if tier == "NONE":
        row["reason"] = "omrekening buiten het gemeten bereik (conversion_in_range) — data_tier NONE"
        results.append(row); continue
    if id(c) not in keep:
        row["afgekapt"] = True
        row["reason"] = f"AFGEKAPT — buiten MAX_DEEP_ANALYSES ({CAP})"
        results.append(row); continue

    p_xg = analyze_match(hs, as_, lg)
    # Controle op de vroeg-seizoenscorrectie: dezelfde wedstrijd op het ONGECORRIGEERDE niveau.
    # Tegen de markt meten mag hier — dat is controleren of de correctie werkt, niet fitten (§2).
    p_xg_nc = analyze_match(hs, as_, league_raw[c["competition"]])
    row["ou25"] = {"met_correctie": round(totals_prob(p_xg.grid, 2.5, "over", 2.0), 4),
                   "zonder_correctie": round(totals_prob(p_xg_nc.grid, 2.5, "over", 2.0), 4)}
    p_xg_ns = analyze_match(hs, as_, lg, shrink=1.0)
    p_sp = analyze_match_from_splits(sp_h, sp_a, league=lg)
    row["lambdas"] = {"xg": [round(p_xg.lambda_home, 3), round(p_xg.lambda_away, 3)],
                      "split": [round(p_sp.lambda_home, 3), round(p_sp.lambda_away, 3)]}

    # Understat als tweede, onafhankelijke xG-bron — meting voor §6e, niet voor my_prob
    up = understat_pair(c["competition"], c.get("understat"), c["season"], c["home"], c["away"], lg)
    p_us = None
    if up:
        uh, ua, uctx, urh, ura, roll = up
        p_us = analyze_match(uh, ua, uctx)
        row["understat"] = {"home": urh, "away": ura,
                            "lambdas": [round(p_us.lambda_home, 3), round(p_us.lambda_away, 3)],
                            "rolling_xg_8": {k: (None if v is None else [round(v[0], 2), round(v[1], 2), v[2]])
                                             for k, v in roll.items()}}

    gate7 = (c.get("ctx") or {}).get("gate") or {}
    row["context"] = c.get("ctx")
    ven = ((c.get("ctx") or {}).get("venue") or {})
    if ven.get("relocated"):
        row["verplaatst"] = ven

    # --- markten verzamelen ---
    sel = []
    # Het marktGEMIDDELDE (BetExplorer) blijft de meetlat voor §6e en poort 8: dat is een
    # oordeel over de wedstrijd. De bet zelf gaat op de BESTE prijs uit de h2h-bulk (§1a).
    m1 = find_1x2(c["competition"], c["home"], c["away"])
    if m1:
        row["odds_1x2"] = list(m1["odds"])          # marktgemiddelde — poort 8 en de-viggen
        row["odds_1x2_bron"] = f"BetExplorer, gemiddelde over {m1['books']} boeken"

    ev_h2h = find_event(c["competition"], "h2h", c["home"], c["away"])
    best_h2h = oddsapi.best_by_line(ev_h2h, "h2h") if ev_h2h else {}
    if best_h2h:
        got, note = {}, []
        for (outcome, _), (o, book) in best_h2h.items():
            if outcome.lower() in ("draw", "gelijkspel"):
                key, side, fn, naam = "X", None, (lambda p: p.draw), "X (gelijkspel)"
            else:
                s = side_of(outcome, c["home"], c["away"])
                if s is None:
                    continue
                key = "1" if s == "home" else "2"
                side = s
                fn = (lambda p: p.home) if s == "home" else (lambda p: p.away)
                naam = f"{key} ({outcome} wint)"
            net = oddsapi.net_price(o, book)
            exch = oddsapi.is_exchange(book)
            got[key] = (o, net, book, exch)
            note.append(f"{key} @{o}" + (f" ({book}, beurs; na commissie {net:g})" if exch
                                          else f" ({book})"))
            sel.append(("1X2", naam, net, f"The Odds API — beste prijs {book}"
                        + (f", beurs: {o} bruto / {net:g} na {int(oddsapi.EXCHANGE_COMMISSION*100)}% commissie"
                           if exch else ""), side, fn))
        row["odds_1x2_best"] = {k: {"bruto": v[0], "netto": v[1], "boek": v[2], "beurs": v[3]}
                                for k, v in got.items()}
        row["markets_checked"]["1X2"] = ("The Odds API h2h, beste prijs per uitkomst — "
                                         + ", ".join(note))
        if m1:
            avg = dict(zip(("1", "X", "2"), m1["odds"]))
            gains = [(got[k][1] / avg[k] - 1) * 100 for k in got if avg.get(k)]
            if gains:
                row["beste_prijs_winst_pct"] = round(sum(gains) / len(gains), 2)
    elif m1:
        # Terugval: geen h2h in de respons, dan is het marktgemiddelde de enige 1X2-bron.
        o1, ox, o2 = m1["odds"]
        srcname = f"BetExplorer ({m1['books']} boeken, marktgemiddelde; bookmaker niet herleidbaar)"
        _waarom = ("geen sportkey bij The Odds API, dus geen bulk-aanroep en geen beste prijs"
                   if not c.get("sportkey") else "geen h2h in de bulk-respons")
        row["markets_checked"]["1X2"] = (f"{_waarom} — BetExplorer-marktgemiddelde over "
                                         f"{m1['books']} boeken is de enige 1X2-bron: "
                                         f"1 @{o1}, X @{ox}, 2 @{o2} "
                                         f"(bookmaker niet herleidbaar; edge valt hier "
                                         f"systematisch te laag uit — §1a)")
        sel += [("1X2", f"1 ({c['home']} wint)", o1, srcname, "home", lambda p: p.home),
                ("1X2", "X (gelijkspel)", ox, srcname, None, lambda p: p.draw),
                ("1X2", f"2 ({c['away']} wint)", o2, srcname, "away", lambda p: p.away)]
    else:
        row["markets_checked"]["1X2"] = "niet gevonden bij The Odds API en niet bij BetExplorer"

    # §1a: een markt die je niet hebt opgevraagd is "bekeken met een reden", geen gat — en de
    # reden is vandaag niet het creditplafond (er is 19.520 credits over) maar het ontbreken van
    # een sportkey voor de enige competitie die speelt.
    GEEN_KEY = ("geen sportkey voor deze competitie bij The Odds API — niet in te kopen "
                "(coverage.json, 9 aug 2026); niet het creditplafond, dat stond op 485 met "
                "23 uitgegeven, dus 462 ongebruikt")
    ev_sp = find_event(c["competition"], "spreads", c["home"], c["away"])
    if ev_sp is None:
        reden = (GEEN_KEY if not c.get("sportkey")
                 else "spreads opgehaald, maar deze wedstrijd stond niet in de respons")
        for k in ("AH", "DNB", "DC"):
            row["markets_checked"][k] = reden
    else:
        lines = oddsapi.best_by_line(ev_sp, "spreads")
        n_ah = n_dnb = n_dc = 0
        for (outcome, line), (o, book) in lines.items():
            side = side_of(outcome, c["home"], c["away"])
            if line is None or side is None: continue
            ln = float(line)
            if abs(ln) < 1e-9:
                sel.append(("Draw No Bet", f"DNB — {outcome}", o, f"The Odds API ({book})", side,
                            (lambda s, oo: (lambda p: dnb_prob(p.grid, s, oo)))(side, o))); n_dnb += 1
            elif abs(abs(ln) - 0.5) < 1e-9:
                naam = c["home"] if side == "home" else c["away"]
                if ln > 0:
                    sel.append(("Double Chance", f"Double Chance — {naam} of gelijk (AH +0.5 @ {o})", o,
                                f"The Odds API ({book})", side,
                                (lambda s, oo: (lambda p: asian_prob(p.grid, 0.5, s, oo)))(side, o))); n_dc += 1
                else:
                    sel.append(("Asian Handicap", f"{outcome} {ln:+g}", o, f"The Odds API ({book})", side,
                                (lambda s, l, oo: (lambda p: asian_prob(p.grid, l, s, oo)))(side, ln, o))); n_ah += 1
            else:
                sel.append(("Asian Handicap", f"{outcome} {ln:+g}", o, f"The Odds API ({book})", side,
                            (lambda s, l, oo: (lambda p: asian_prob(p.grid, l, s, oo)))(side, ln, o))); n_ah += 1
        row["markets_checked"]["AH"] = f"The Odds API spreads, beste prijs per lijn — {n_ah} handicaplijnen"
        row["markets_checked"]["DNB"] = (f"The Odds API spreads, 0.0-lijn — {n_dnb} selecties" if n_dnb
                                         else "geen 0.0-lijn in de spreads-respons")
        row["markets_checked"]["DC"] = (f"The Odds API spreads, +0.5-lijn — {n_dc} selecties" if n_dc
                                        else "geen +0.5-lijn in de spreads-respons")

    ev_to = find_event(c["competition"], "totals", c["home"], c["away"])
    if ev_to is None:
        row["markets_checked"]["OU"] = (GEEN_KEY if not c.get("sportkey")
            else "totals opgehaald, maar deze wedstrijd stond niet in de respons")
    else:
        lines = oddsapi.best_by_line(ev_to, "totals")
        n = 0
        for (outcome, line), (o, book) in lines.items():
            if line is None: continue
            ln, sd = float(line), outcome.lower()
            sel.append(("Over/Under", f"{outcome} {ln:g}", o, f"The Odds API ({book})", None,
                        (lambda l, s, oo: (lambda p: totals_prob(p.grid, l, s, oo)))(ln, sd, o))); n += 1
        row["markets_checked"]["OU"] = f"The Odds API totals, beste prijs per lijn — {n} lijnen"

    bt = best_btts(c["match_id"])
    if bt:
        for naam, (o, book) in bt.items():
            ja = naam.startswith("y")
            sel.append(("BTTS", f"Beide ploegen scoren — {'ja' if ja else 'nee'}", o,
                        f"The Odds API ({book})", None,
                        (lambda j: (lambda p: p.btts if j else 1 - p.btts))(ja)))
        row["markets_checked"]["BTTS"] = f"The Odds API event-markt btts — {len(bt)} selecties"
    else:
        row["markets_checked"]["BTTS"] = (GEEN_KEY if not c.get("sportkey")
            else "btts opgevraagd, maar geen boek noteerde deze markt")
    row["markets_checked"]["context"] = "Fotmob blessures/schorsingen + vorm + rust + stadioncontrole"

    # --- poorten ---
    # Sinds 6 sep 2026 worden de poorten TWEE KEER gewogen: één keer met de herijkte `my_prob`
    # (§1g) en één keer met de ruwe `my_raw`. Alleen de eerste bepaalt of er een bet uit komt —
    # §1 is daar niet in veranderd. De tweede is er om de correctie zelf te kunnen meten: elke
    # selectie die zonder de herijking een bet zou zijn geweest gaat als schaduwpick naar
    # data/shadow.jsonl met `failed_gate = "herijking"` en wordt daar afgerekend (§6d).
    #
    # Let op waaróm dit een echte wijziging is en niet alleen een extra veld: `robustness_check`
    # draaide tot vandaag alleen als de HERIJKTE edge de drempel haalde. Voor een kandidaat die
    # ruw wel en herijkt niet door de edge-poort komt, was poort 6 dus nooit bepaald, en dan is
    # "zou dit zonder de correctie een bet zijn geweest" niet te beantwoorden — alleen te raden.
    # De aanroep hangt nu aan "haalt hij de drempel op minstens één van de twee schalen".
    ORDER = ("odds", "edge", "tweede_methode", "robuustheid", "context", "underdog")
    thresh = THRESH[tier]
    evaluated = []
    for markt, oms, o, bron, side, f in sel:
        try:
            px, ps = f(p_xg), f(p_sp)
        except Exception:
            continue
        if not (0 < px < 1 and 0 < ps < 1):
            continue
        my_raw = combine_probs(px, ps)          # §1f — 0.80 op xG, 0.20 op de splits
        my = recalibrate.apply(my_raw, FIT)     # §1g — herijking op uitslagen
        e_pp, e_raw = edge_pp(my, o), edge_pp(my_raw, o)
        e_xg, e_sp = edge_pp(px, o), edge_pp(ps, o)

        g7 = gate7.get(side if side else "None") or {"passed": True, "reason": "geen kant om te benadelen"}
        # Poort 8 (§1e, 4 sep 2026): niet op de kant die de markt zwakker vindt.
        g8 = sides.check(side, row.get("odds_1x2"))
        base = {"odds": MIN_ODDS <= o <= MAX_ODDS,
                "tweede_methode": (px > 1 / o) and (ps > 1 / o),
                "context": bool(g7["passed"]), "underdog": g8.passed}

        # `robustness_check` varieert alleen `analyze_match` en weet van de herijking niets af,
        # dus één aanroep bedient beide schalen — de uitkomst is dezelfde.
        rb = None
        if all(base.values()) and (e_pp >= thresh or e_raw >= thresh):
            rb = robustness_check(hs, as_, lg, f, o)

        def _fail(edge_value, _base=base, _rb=rb):
            g = dict(_base)
            g["edge"] = edge_value >= thresh
            g["robuustheid"] = (_rb.min_edge > 0) if _rb is not None else None
            return next((k for k in ORDER if g.get(k) is False), None)

        fail, fail_raw = _fail(e_pp), _fail(e_raw)
        # Een selectie die alleen op de herijking sneuvelt krijgt dat label in plaats van het
        # vagere `edge`: "genoeg edge, maar niet nadat mijn eigen optimisme eraf ging" is een
        # andere bevinding dan "sowieso te weinig edge", en §6d moet die twee kunnen scheiden.
        if fail == "edge" and fail_raw is None:
            fail = "herijking"
        evaluated.append({"market": markt, "selection": oms, "odds": o, "odds_source": bron,
                          "side": side, "my_prob": round(my, 4), "my_raw": round(my_raw, 4),
                          "implied": round(1 / o, 4),
                          "p_xg": round(px, 4), "p_split": round(ps, 4),
                          "edge_pp": round(e_pp, 2), "edge_raw": round(e_raw, 2),
                          "edge_xg": round(e_xg, 2), "edge_split": round(e_sp, 2),
                          "edge_robust_min": (round(rb.min_edge, 2) if rb else None),
                          "failed_gate": fail, "failed_gate_ruw": fail_raw,
                          "bet_ruw": fail_raw is None,
                          # "haalt beide modellen" — de voorwaarde waaronder gepubliceerd wordt.
                          # De herijking verlaagt een kans in dit bereik altijd, dus dit is
                          # dezelfde eis als `fail is None`; hij staat er als controle, niet als
                          # versoepeling, zodat een toekomstige fit die dat niet doet opvalt.
                          "bet_beide": fail is None and fail_raw is None,
                          "context_reason": g7.get("reason", ""),
                          "underdog_reason": g8.reason,
                          "score": round(selection_score(e_pp, my, tier), 3) if fail is None else None,
                          "score_ruw": round(selection_score(e_raw, my_raw, tier), 3)})
    row["candidates_evaluated"] = len(evaluated)
    # Selecties die alléén op poort 8 sneuvelden: alle eerdere poorten stonden open. Die gaan naar
    # het schaduwlogboek, ook als deze wedstrijd daarna alsnog een andere bet oplevert (§1e).
    _p8 = [r for r in evaluated if r["failed_gate"] == "underdog"]
    # Alleen de selectie die zónder poort 8 gepubliceerd zóu zijn — de hoogste selection_score.
    # Alle andere geblokkeerde selecties zijn dezelfde mening in een andere markt (§1a); ze
    # allemaal opnemen zou de gemeten opbrengst van deze poort vier keer meetellen.
    row["poort8_geblokkeerd"] = []
    if _p8:
        b8 = max(_p8, key=lambda r: selection_score(r["edge_pp"], r["my_prob"], tier))
        row["poort8_geblokkeerd"] = [
            {"market": f"{b8['market']} — {b8['selection']}", "odds": b8["odds"],
             "edge_pp": b8["edge_pp"], "my_prob": b8["my_prob"], "my_raw": b8["my_raw"],
             "edge_xg": b8["edge_xg"], "edge_split": b8["edge_split"],
             "edge_robust_min": b8["edge_robust_min"], "failed_gate": "underdog",
             "score": round(selection_score(b8["edge_pp"], b8["my_prob"], tier), 3),
             "ook_geblokkeerd": len(_p8) - 1, "reden": b8["underdog_reason"]}]
    tally = {}
    for r in evaluated:
        t = tally.setdefault(r["market"], {"n": 0, "bets": 0})
        t["n"] += 1
    row["per_market"] = tally
    row["all_candidates"] = sorted(evaluated, key=lambda r: -r["edge_pp"])

    passed = [r for r in evaluated if r["bet_beide"]]
    if passed:
        best = max(passed, key=lambda r: r["score"])
        rest = sorted([r for r in evaluated if r is not best and r["failed_gate"] is None],
                      key=lambda r: -r["score"])
        row["bet"] = True; row["pick"] = best
        row["runner_up"] = ({"selection": f"{rest[0]['market']} — {rest[0]['selection']}",
                             "score": rest[0]["score"]} if rest else None)
        # Haalde maar één selectie alle poorten, dan is "de tweede" niet leeg maar de sterkste
        # die wél afviel — met de poort erbij. Zonder dat staat er in het runrapport 'geen
        # tweede' terwijl er zes selecties waren doorgerekend (§1, laatste alinea).
        if not rest:
            others = sorted([r for r in evaluated if r is not best],
                            key=lambda r: -r["edge_pp"])
            if others:
                o0 = others[0]
                row["runner_up_rejected"] = {
                    "selection": f"{o0['market']} — {o0['selection']}",
                    "odds": o0["odds"], "edge_pp": o0["edge_pp"],
                    "failed_gate": o0["failed_gate"] or "edge"}
    else:
        # Kandidaten die op poort 8 sneuvelden staan al in `poort8_geblokkeerd` en horen hier dus
        # niet nóg een keer: anders krijgt dezelfde mening twee schaduwregels en telt de opbrengst
        # van die poort dubbel mee bij de herziening van 25 september.
        near = [r for r in evaluated if r["edge_pp"] >= NEAR[tier]
                and MIN_ODDS <= r["odds"] <= MAX_ODDS and r["failed_gate"] != "underdog"]
        if near:
            b = max(near, key=lambda r: r["edge_pp"])
            gate = b["failed_gate"] or ("edge" if b["edge_pp"] < thresh else None)
            # §5 eist alle drie de getallen in de "Net niet"-tabel, niet alleen de poort die hem
            # afwees. `robustness_check` draait hierboven alleen voor selecties die de edge-poort
            # halen, dus voor een net-nietter is `edge_robust_min` daar per definitie leeg — en
            # dan valt precies niet te zien of het één poort was of een breed tekort. Eén extra
            # aanroep per wedstrijd, alleen voor de kandidaat die in het rapport komt.
            rmin = b["edge_robust_min"]
            if rmin is None:
                fn = next((f for markt, oms, o, bron, side, f in sel
                           if markt == b["market"] and oms == b["selection"]), None)
                if fn is not None:
                    try:
                        rmin = round(robustness_check(hs, as_, lg, fn, b["odds"]).min_edge, 2)
                    except Exception:
                        rmin = None
            row["near_miss"] = {"market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
                                "edge_pp": b["edge_pp"],
                                # de kans waarmee de poorten werkelijk hebben gerekend (§1f + §1g);
                                # zonder dit veld reconstrueert shadow.py het oude ongewogen
                                # gemiddelde en meet §6d tegen een edge die nooit is geclaimd
                                "my_prob": b["my_prob"], "my_raw": b["my_raw"],
                                "edge_xg": b["edge_xg"], "edge_split": b["edge_split"],
                                "edge_robust_min": rmin,
                                "failed_gate": gate}
            row["reason"] = {"edge": f"edge onder drempel ({b['edge_pp']:+.2f} pp, nodig {thresh:.1f})",
                             "herijking": (f"alleen de herijking hield hem tegen: ruw "
                                           f"{b.get('edge_raw', 0):+.2f} pp, herijkt "
                                           f"{b['edge_pp']:+.2f} pp, nodig {thresh:.1f}"),
                             "odds": "odds buiten band",
                             "tweede_methode": "data conflicterend",
                             "robuustheid": "edge niet robuust over het (shrink, rho)-grid",
                             "context": f"context spreekt de bet tegen — {b['context_reason']}",
                             "underdog": f"poort 8 — {b['underdog_reason']}"}[gate]
        elif evaluated:
            row["reason"] = "edge onder drempel"
        else:
            row["reason"] = "geen prijzen gevonden voor deze wedstrijd"

    # --- wat zonder de herijking een bet was geweest (§5, 6 sep 2026) ---
    # Elke selectie die alle acht poorten haalt op de RUWE kans maar niet op de herijkte, is
    # precies het verschil dat §1g maakt. Die gaat als schaduwpick mee en wordt afgerekend, zodat
    # over enkele weken onder "viel af op: herijking" een ROI staat. Zonder die reeks blijft de
    # correctie een aanname die zichzelf niet kan weerleggen.
    #
    # Eén regel per wedstrijd, net als bij poort 8 (§1e): dezelfde mening in vier markten is één
    # bevinding. En niet als de near_miss hierboven al dezelfde selectie beschrijft — die draagt
    # dan zelf het label `herijking` en een tweede rij zou de opbrengst dubbel tellen.
    _raw_only = [r for r in evaluated if r["bet_ruw"] and r["failed_gate"] is not None]
    row["zonder_herijking"] = []
    if _raw_only:
        b = max(_raw_only, key=lambda r: r["score_ruw"])
        # LET OP welke kans hier in gaat. De schaduwrij toetst de hypothese "het ongecorrigeerde
        # model had gelijk", en dan hoort de RUWE kans erin — niet de herijkte. De herijkte kans
        # is juist het model dat zegt "niet spelen"; die erin zetten zou de correctie tegen
        # zichzelf laten getuigen en de kalibratieregel van §6d betekenisloos maken. `my_prob` en
        # `edge_pp` zijn hier dus bewust de ruwe getallen; de herijkte staan ernaast.
        row["zonder_herijking"] = [{
            "market": f"{b['market']} — {b['selection']}", "odds": b["odds"],
            "my_prob": b["my_raw"], "edge_pp": b["edge_raw"],
            "my_prob_herijkt": b["my_prob"], "edge_pp_herijkt": b["edge_pp"],
            "edge_xg": b["edge_xg"], "edge_split": b["edge_split"],
            "edge_robust_min": b["edge_robust_min"],
            "failed_gate": "herijking", "score_ruw": b["score_ruw"],
            "ook_geblokkeerd": len(_raw_only) - 1,
            "reden": (f"ruw {b['edge_raw']:+.2f} pp (drempel {thresh:.1f}), herijkt "
                      f"{b['edge_pp']:+.2f} pp — alleen §1g hield hem tegen")}]

    # --- kalibratie (§6e) ---
    if m1:
        cal = {"market": [round(x, 4) for x in calibration.devig(list(m1["odds"]))],
               "p_xg": [round(p_xg.home, 4), round(p_xg.draw, 4), round(p_xg.away, 4)],
               "p_xg_noshrink": [round(p_xg_ns.home, 4), round(p_xg_ns.draw, 4), round(p_xg_ns.away, 4)],
               "p_split": [round(p_sp.home, 4), round(p_sp.draw, 4), round(p_sp.away, 4)]}
        if p_us:
            cal["p_xg_understat"] = [round(p_us.home, 4), round(p_us.draw, 4), round(p_us.away, 4)]
        row["calibration"] = cal
    results.append(row)

json.dump({"vroeg_seizoen": {"factor": FACTOR, "gepoold": POOLED, "speeldagen": TOTAL_MD,
                             "competities": obs_comps},
           "afkapping": TRUNC, "matches": results},
          open("tmp-run/rb11_results.json", "w"), ensure_ascii=False, indent=1)

for r in results:
    tag = "BET " if r["bet"] else "    "
    extra = (f"{r['pick']['market']} {r['pick']['selection']} @{r['pick']['odds']} "
             f"edge {r['pick']['edge_pp']:+.1f} score {r['pick']['score']}") if r["bet"] else r.get("reason", "")
    print(f"{tag}{r['tier']:5s} {r['match'][:38]:38s} n={r.get('candidates_evaluated', 0):3d}  {extra}")
print("\nBETS:", sum(r["bet"] for r in results))
