"""Meet of het lopende seizoen meewegen de analyse béter maakt — op uitslagen, niet op de markt.

De vraag (gebruiker, 3 sep 2026): wordt de routine gedurende het seizoen beter naarmate er meer
gespeeld is? Nu niet: de teamsterktes komen uitsluitend uit het vórige seizoen en worden nooit
ververst. Deze test meet wat het oplevert om het lopende seizoen mee te wegen, en met hoeveel.

Opzet:
  - testseizoen 2025/2026, vijf competities bij Understat (EPL, La Liga, Bundesliga, Serie A,
    Ligue 1). Prior = 2024/2025.
  - Voor elke wedstrijd, in chronologische volgorde, weten we alleen wat er VOOR die wedstrijd
    bekend was: de cumulatieve xG/xGA van dit seizoen tot dat moment, plus de totalen van vorig
    seizoen. Geen enkele wedstrijd ziet zijn eigen uitslag.
  - Credibiliteitsweging met constante k, in wedstrijden:
        gewicht_nu = n / (n + k)
        tarief = gewicht_nu * tarief_dit_seizoen + (1 - gewicht_nu) * tarief_vorig_seizoen
    k = oneindig  -> uitsluitend vorig seizoen  = wat de routine vandaag doet
    k = 0         -> uitsluitend dit seizoen
  - Scoren op de werkelijke uitslag (1X2) met Brier en log loss. Lager is beter.

Geen bookmakerprijs komt hieraan te pas — dat zou §2 schenden en de meting betekenisloos maken.
"""
import json
import math
import sys
from datetime import datetime

sys.path.insert(0, ".")
from scripts import understat
from scripts.model import LeagueContext, TeamStats, analyze_match

LEAGUES = {"EPL": "Premier League", "La_liga": "La Liga", "Bundesliga": "Bundesliga",
           "Serie_A": "Serie A", "Ligue_1": "Ligue 1"}
PRIOR, TEST = "2024/2025", "2025/2026"

# k in wedstrijden; None = oneindig (alleen vorig seizoen, de huidige routine)
KS = [None, 16, 8]
SHRINKS = [0.8]


def team_totals(data: dict) -> dict:
    """{teamnaam: (xg, xga, mp)} over een heel seizoen."""
    out = {}
    for t in data["teams"].values():
        h = t["history"]
        out[t["title"]] = (sum(m["xG"] for m in h), sum(m["xGA"] for m in h), len(h))
    return out


def league_base(data: dict) -> LeagueContext:
    """Competitiebasis uit het priorseizoen, net als de routine hem opbouwt."""
    hg = ag = n = 0
    txg = tn = 0
    for t in data["teams"].values():
        for m in t["history"]:
            txg += m["xG"]; tn += 1
            if m["h_a"] == "h":
                hg += m["scored"]; ag += m["missed"]; n += 1
    return LeagueContext(home_goals_per_match=hg / n, away_goals_per_match=ag / n,
                         avg_xg_per_match=txg / tn)


def blend(cur_xg, cur_xga, n_cur, prior_rate_xg, prior_rate_xga, k):
    """Gewogen tarief per duel. k=None -> alleen prior."""
    if k is None or n_cur == 0:
        return prior_rate_xg, prior_rate_xga
    w = n_cur / (n_cur + k) if (n_cur + k) > 0 else 1.0
    return (w * (cur_xg / n_cur) + (1 - w) * prior_rate_xg,
            w * (cur_xga / n_cur) + (1 - w) * prior_rate_xga)


results = {(k, s): {"brier": 0.0, "logloss": 0.0, "n": 0} for k in KS for s in SHRINKS}
skipped = {"geen_prior": 0, "geen_uitslag": 0}
per_bucket = {(k, s): {} for k in KS for s in SHRINKS}

for code, naam in LEAGUES.items():
    prior = understat.fetch_league(code, understat.season_code(PRIOR))
    test = understat.fetch_league(code, understat.season_code(TEST))
    pt = team_totals(prior)
    base = league_base(prior)

    # chronologische wedstrijdlijst van het testseizoen, per team de historie op datum
    hist = {t["title"]: sorted(t["history"], key=lambda m: m["date"]) for t in test["teams"].values()}
    fixtures = []
    for title, ms in hist.items():
        for m in ms:
            if m["h_a"] != "h":
                continue
            # zoek de tegenstander: de uitwedstrijd met dezelfde datum
            opp = next((o for o, oms in hist.items() if o != title
                        and any(x["date"] == m["date"] and x["h_a"] == "a" for x in oms)), None)
            if opp is None:
                continue
            fixtures.append((m["date"], title, opp, m["scored"], m["missed"]))
    fixtures.sort()

    # cumulatieven die meelopen; state[team] = [xg, xga, n]
    state = {t: [0.0, 0.0, 0] for t in hist}
    for datum, home, away, gh, ga in fixtures:
        if home not in pt or away not in pt:
            skipped["geen_prior"] += 1
        else:
            ph_xg, ph_xga, ph_n = pt[home]
            pa_xg, pa_xga, pa_n = pt[away]
            uitkomst = 0 if gh > ga else (1 if gh == ga else 2)
            for k in KS:
                hx, hxa = blend(*state[home][:2], state[home][2], ph_xg / ph_n, ph_xga / ph_n, k)
                ax, axa = blend(*state[away][:2], state[away][2], pa_xg / pa_n, pa_xga / pa_n, k)
                hs = TeamStats(xg=hx, xga=hxa, matches_played=1)
                as_ = TeamStats(xg=ax, xga=axa, matches_played=1)
                for s in SHRINKS:
                    p = analyze_match(hs, as_, base, shrink=s)
                    probs = [p.home, p.draw, p.away]
                    brier = sum((probs[i] - (1 if i == uitkomst else 0)) ** 2 for i in range(3))
                    ll = -math.log(max(probs[uitkomst], 1e-9))
                    r = results[(k, s)]
                    r["brier"] += brier; r["logloss"] += ll; r["n"] += 1
                    # per speeldagbak, om te zien of het effect met het seizoen meegroeit
                    md = min(state[home][2], state[away][2])
                    bucket = "1-5" if md < 5 else ("6-12" if md < 12 else ("13-24" if md < 24 else "25+"))
                    b = per_bucket[(k, s)].setdefault(bucket, {"brier": 0.0, "n": 0})
                    b["brier"] += brier; b["n"] += 1

        # pas ná het scoren de stand bijwerken (geen enkele wedstrijd ziet zichzelf)
        hm = next(m for m in hist[home] if m["date"] == datum and m["h_a"] == "h")
        am = next(m for m in hist[away] if m["date"] == datum and m["h_a"] == "a")
        state[home][0] += hm["xG"]; state[home][1] += hm["xGA"]; state[home][2] += 1
        state[away][0] += am["xG"]; state[away][1] += am["xGA"]; state[away][2] += 1
    print(f"  {naam:16s} {len(fixtures)} wedstrijden verwerkt", flush=True)

out = {"ks": [("prior" if k is None else k) for k in KS], "shrinks": SHRINKS,
       "skipped": skipped, "rows": [], "buckets": {}}
print(f"\novergeslagen (promovendus zonder priorseizoen): {skipped['geen_prior']}\n")
print(f"{'k':>8} {'shrink':>7} {'n':>6} {'Brier':>9} {'log loss':>9}")
for s in SHRINKS:
    for k in KS:
        r = results[(k, s)]
        if not r["n"]:
            continue
        row = {"k": ("prior" if k is None else k), "shrink": s, "n": r["n"],
               "brier": r["brier"] / r["n"], "logloss": r["logloss"] / r["n"]}
        out["rows"].append(row)
        print(f"{str(row['k']):>8} {s:>7} {r['n']:>6} {row['brier']:>9.5f} {row['logloss']:>9.5f}")
    print()

for (k, s), buckets in per_bucket.items():
    for b, v in buckets.items():
        if v["n"]:
            out["buckets"][f"{'prior' if k is None else k}|{s}|{b}"] = {
                "brier": v["brier"] / v["n"], "n": v["n"]}
json.dump(out, open("tmp-run/backtest_k8.json", "w"), indent=1)
print("weggeschreven naar tmp-run/backtest_k8.json")
