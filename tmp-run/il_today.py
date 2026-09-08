"""Controle 4: het gemeten model naast de markt, op de zes Champions League-duels van 8 sep 2026.

Dit is CONTROLEREN, geen fitten (§2 / §6e, Stage 5): de factoren komen uitsluitend uit Europese
uitslagen t/m 2025/2026 en er is geen enkele marktprijs in de meting gegaan. Wat deze tabel
beantwoordt is: staat het model na de omrekening in dezelfde orde van grootte als de bookmakers,
of zegt het iets onmogelijks? Dat laatste was op 19 aug 2026 het geval zonder omrekening —
zeventien procentpunt op één uitwinst.
"""
import json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from il_fit import fit, SHRINK
from scripts.model import score_grid, DEFAULT_RHO
from scripts import calibration, oddsapi

PRIOR = 5.0
DS = json.load(open("tmp-run/il_dataset.json"))
CROSS = json.load(open("tmp-run/il_rows.json"))
FIT = fit([dict(r) for r in CROSS], prior=PRIOR)

# Ploeg-id's van vandaag komen uit de Fotmob-daglijst; de binnenlandse stand is 2025/2026.
MATCHES = json.load(open("tmp-run/ra8_cands.json"))
UCL = [m for m in MATCHES if m["competition"] == "UEFA Champions League"]

# De fit gebruikt binnenlandse seizoenen t/m 2024/2025 (dat is wat de Europese seizoenen t/m
# 2025/2026 nodig hadden). Voor de duels van VANDAAG is het seizoen 2025/2026 nodig; dat wordt
# hier bijgehaald, met dezelfde functie en dezelfde cache als de dataset zelf.
from il_fetch import LEAGUES, league_table, domestic_season as _ds

available = DS["available"]
LIVE: dict[str, dict] = {}
for cc, (lid, _name) in LEAGUES.items():
    season = _ds(cc, "2026/2027", available.get(cc) or [])
    if not season:
        continue
    tbl = league_table(lid, season)
    if tbl:
        LIVE[cc] = {"season": season, "table": tbl}
print(f"binnenlandse standen voor vandaag: {len(LIVE)} competities bijgehaald")


def domestic(team_id: str):
    """(ccode, seizoen, stand) van het laatst afgeronde binnenlandse seizoen van deze ploeg."""
    for cc, v in LIVE.items():
        if team_id in v["table"]["teams"]:
            return cc, v["season"], v["table"]
    return None, None, None


def strength(row, avg):
    att = 1 + SHRINK * ((row["gf"] / row["played"]) / avg - 1)
    dfn = 1 + SHRINK * ((row["ga"] / row["played"]) / avg - 1)
    return max(att, 0.05), max(dfn, 0.05)


def probs(lh, la):
    g = score_grid(lh, la, DEFAULT_RHO)
    n = len(g)
    h = sum(g[i][j] for i in range(n) for j in range(n) if i > j)
    d = sum(g[i][i] for i in range(n))
    return h, d, max(0.0, 1 - h - d)


odds_raw = json.load(open("tmp-run/ra8_odds.json"))["raw"]["h2h"].get("UEFA Champions League") or []


def market(home, away):
    """De-vigde marktkans uit de beste h2h-prijzen. Alleen ter controle, niet als invoer."""
    for ev in odds_raw:
        if home.split()[0].lower() in ev["home_team"].lower() or ev["home_team"].split()[0].lower() in home.lower():
            if away.split()[0].lower() in ev["away_team"].lower() or ev["away_team"].split()[0].lower() in away.lower():
                best = oddsapi.best_by_line(ev, "h2h")
                got = {}
                for (outcome, _), (price, book) in best.items():
                    if outcome.lower() in ("draw", "gelijkspel"):
                        got["X"] = price
                    elif outcome.lower() in ev["home_team"].lower():
                        got["1"] = price
                    else:
                        got["2"] = price
                if len(got) == 3:
                    return calibration.devig([got["1"], got["X"], got["2"]])
    return None


print(f"fit: prior {PRIOR:g}, vlakke seizoensgewichten, {len(CROSS)} kruis-grensduels 2021/2022-2025/2026")
print(f"Europees niveau: thuis {FIT['H']:.3f} / uit {FIT['W']:.3f} doelpunten\n")
print(f"{'wedstrijd':38s} {'competities':11s} | {'model 1/X/2':22s} | {'markt 1/X/2':22s} | max |verschil|")
print("-" * 118)
gaps = []
for m in UCL:
    cc_h, s_h, th = domestic(str(m["home_id"]))
    cc_a, s_a, ta = domestic(str(m["away_id"]))
    if not cc_h or not cc_a:
        print(f"{m['home']} – {m['away']}: geen binnenlandse stand ({cc_h}/{cc_a})")
        continue
    rh, ra = th["teams"][str(m["home_id"])], ta["teams"][str(m["away_id"])]
    att_h, dfn_h = strength(rh, th["goals_per_team_per_match"])
    att_a, dfn_a = strength(ra, ta["goals_per_team_per_match"])
    A, D = FIT["A"], FIT["D"]
    lh = FIT["H"] * att_h * A[cc_h] * dfn_a * D[cc_a]
    la = FIT["W"] * att_a * A[cc_a] * dfn_h * D[cc_h]
    p = probs(lh, la)
    mk = market(m["home"], m["away"])
    name = f"{m['home']} – {m['away']}"
    mstr = "  ".join(f"{x:5.1%}" for x in p)
    if mk:
        kstr = "  ".join(f"{x:5.1%}" for x in mk)
        gap = max(abs(a - b) for a, b in zip(p, mk)) * 100
        gaps.append(gap)
        print(f"{name:38s} {cc_h}/{cc_a:7s} | {mstr:22s} | {kstr:22s} | {gap:+6.1f} pp")
    else:
        print(f"{name:38s} {cc_h}/{cc_a:7s} | {mstr:22s} | {'geen prijs':22s} |")
if gaps:
    print(f"\ngemiddelde grootste afwijking t.o.v. de markt: {sum(gaps)/len(gaps):.1f} pp "
          f"(bereik {min(gaps):.1f}-{max(gaps):.1f})")
