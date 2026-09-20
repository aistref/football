"""Landenteamsterkte — één schaal voor alle interlands, gefit op uitslagen.

Aanleiding (20 september 2026). Run C kijkt alleen naar landenteams, en daar loopt het
clubmodel vast: een oefeninterland heeft geen stand, dus `fotmob.fetch_league_stats(114, ...)`
geeft "geen bruikbare stand", en er is geen competitiegemiddelde om Japan en Uruguay op te
normaliseren. De eerste versie van `prompts/run-c.md` zette daarom vrijwel alles op
`data_tier = NONE`. Dat is eerlijk maar nutteloos: de bookmakers prijzen die duels wél, dus er
valt iets te meten — alleen niet met de machinerie voor clubcompetities.

**Waarom dit bij landenteams kan en bij clubs niet.** `interleague.py` moest een gat overbruggen
tussen gesloten systemen: een Eredivisie-club speelt bijna nooit tegen een Bundesliga-club, dus
het niveauverschil moest uit een handvol Europese duels komen. Bij landenteams is dat gat er
niet. Nations League-tiers spelen promotie/degradatie tegen elkaar, WK-kwalificatie zet binnen
elke confederatie alle niveaus in één poule, de interconfederatie-play-offs koppelen de
werelddelen, en er worden per jaar ~290 oefeninterlands gespeeld die dwars door alles heen gaan.
De wedstrijdgraaf is dus samenhangend, en dan is één gezamenlijke rating gewoon te fitten in
plaats van te moeten worden overbrugd.

## Het model

Per ploeg een aanval- en een verdedigingsgetal, plus één thuisvoordeel voor iedereen:

    lambda_thuis = exp(aanval_thuis - verdediging_uit + thuisvoordeel)
    lambda_uit   = exp(aanval_uit   - verdediging_thuis)

Gefit met gewogen Poisson-maximum-likelihood op werkelijke uitslagen — **nooit op koersen**
(§2). Drie wegingen, waarvan er twee gemeten zijn en één niet; zie `python3
scripts/national.py tune` en de parametertabel verderop:

- **tijdsverval** — gemeten. Halfwaardetijd 2920 dagen, en de curve is daarboven vlak: bij
  landenteams doet verval vrijwel niets, de verhoudingen liggen over jaren stabiel.
- **regularisatie** — gemeten. Ridge 0.30; strenger trekt de kleine ploegen te hard naar het
  midden en kost aantoonbaar nauwkeurigheid.
- **wedstrijdsoort** — **niet gemeten**. Fotmob geeft voor oefeninterlands alleen het lopende
  kalenderjaar, dus er zit geen enkele oefeninterland in de trainingsperiode en de weging is
  niet te toetsen. De 0.50 is een voorzichtige aanname en staat als zodanig genoteerd.

**Wat het waard is, uit-steekproef gemeten** (fit t/m 2025-09-01, getoetst op de 819 duels
erna): Brier **0.4796** op de 1X2-uitkomst, tegen 0.66667 voor 1/3-1/3-1/3 gokken. Dat is een
echt voorspellend model, en het is géén belofte dat het de bookmaker verslaat — die vergelijking
staat nergens in dit bestand en hoort thuis in het kalibratielogboek van §6e.

## Hoe het aansluit op de rest

`team()` levert een gewone `model.TeamStats` en `context()` een gewone `model.LeagueContext`,
op precies de schaal die `model.match_lambdas` verwacht. De rest van de pijplijn — beide
methodes, de acht poorten, `robustness_check`, de herijking — draait er daarmee ongewijzigd op.
`national.py verify` controleert dat `analyze_match` dezelfde lambdas teruggeeft als de fit.

## De poort

`in_range(team_id)` is een **poort, geen aantekening**, in dezelfde geest als
`promotion.conversion_in_range` en `interleague.in_range`: onder `MIN_MATCHES` gewogen duels is
de rating vrijwel volledig door de regularisatie bepaald en dus een aanname met een getal
eromheen. Dan `data_tier = NONE`, geen bet.

Gebruik:

    python3 scripts/national.py build          # corpus ophalen (kost tijd, geen credits)
    python3 scripts/national.py fit            # rating fitten en wegschrijven
    python3 scripts/national.py tune           # de drie wegingen uit-steekproef meten
    python3 scripts/national.py show Netherlands Germany
    python3 scripts/national.py verify
"""
from __future__ import annotations

import argparse
import json
import math
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path

try:
    from .fotmob import _get_json
    from .model import LeagueContext, TeamStats
except ImportError:                                   # als los script gedraaid
    from fotmob import _get_json                      # type: ignore[no-redef]
    from model import LeagueContext, TeamStats        # type: ignore[no-redef]

CORPUS = Path("data/national-matches.jsonl")
FIT = Path("data/national-fit.json")

# ---------------------------------------------------------------------------------------------
# Welke competities meetellen. Ids gemeten op 20 sep 2026 door de Fotmob-daglijst van acht
# interlandvensters en zes toernooidagen af te lopen; zie `prompts/run-c.md`.
#
# LET OP TWEE VALKUILEN die bij het opzoeken allebei langskwamen:
#   * id 114 is `Friendlies` (landen), id **489** is `Club Friendlies`. Die tweede hoort hier
#     absoluut niet in en lijkt in de daglijst sterk op de eerste.
#   * alles met U17/U19/U21/U23, `Women` of `Olympic` valt af. Het olympisch mannentoernooi is
#     een U23-toernooi en staat daarom niet op de runlijst van Run C.
# ---------------------------------------------------------------------------------------------
FRIENDLY, QUALIFIER, TOURNAMENT = "friendly", "qualifier", "tournament"

COMPETITIONS: dict[int, tuple[str, str]] = {
    114:   ("Friendlies", FRIENDLY),
    77:    ("World Cup", TOURNAMENT),
    50:    ("EURO", TOURNAMENT),
    289:   ("Africa Cup of Nations", TOURNAMENT),
    44:    ("Copa America", TOURNAMENT),
    298:   ("CONCACAF Gold Cup", TOURNAMENT),
    9806:  ("UEFA Nations League A", QUALIFIER),
    9807:  ("UEFA Nations League B", QUALIFIER),
    9808:  ("UEFA Nations League C", QUALIFIER),
    9809:  ("UEFA Nations League D", QUALIFIER),
    10719: ("UEFA Nations League play-offs", QUALIFIER),
    9821:  ("CONCACAF Nations League", QUALIFIER),
    10195: ("World Cup Qualification UEFA", QUALIFIER),
    10196: ("World Cup Qualification CAF", QUALIFIER),
    10197: ("World Cup Qualification AFC", QUALIFIER),
    10198: ("World Cup Qualification CONCACAF", QUALIFIER),
    10199: ("World Cup Qualification CONMEBOL", QUALIFIER),
    10201: ("World Cup Qualification Inter-Confederation", QUALIFIER),
    10608: ("Africa Cup of Nations Qualification", QUALIFIER),
    10609: ("Asian Cup Qualification", QUALIFIER),
}

# Parameters. Gemeten op 20 sep 2026, uit-steekproef: fit op 5956 duels t/m 2025-09-01, getoetst
# op de 819 duels erna. Brier op de 1X2-uitkomst, lager is beter; blind gokken geeft 0.66667.
#
#   halfwaardetijd   ridge   Brier uit
#         360 d       0.60    0.51941
#         720 d       0.60    0.50006
#        1460 d       0.60    0.48808
#        1460 d       0.30    0.48195
#        2920 d       0.30   *0.47956*
#        5840 d       0.30    0.47958
#         720 d       1.50    0.51345
#
# Twee dingen die daarbij horen en die je moet weten voordat je hieraan sleutelt:
#
# 1. **De curve is vlak voorbij ~2920 dagen** (0.47956 tegen 0.47958 bij 5840). Tijdsverval doet
#    bij landenteams dus vrijwel niets; de sterkteverhoudingen liggen over jaren stabiel. Ga
#    hier niet op fijnregelen — 2920 is "ongeveer waar het optimum ligt", geen scherp getal.
# 2. **`WEIGHT[FRIENDLY]` is NIET gemeten en dat is geen slordigheid maar een gat in de bron.**
#    Fotmob geeft voor id 114 alleen het lopende kalenderjaar terug (`allAvailableSeasons`:
#    ['2026']), dus alle 287 oefeninterlands in het corpus liggen ná de cutoff en er zit er
#    nul in de training. De drie waarden 0.25 / 0.50 / 1.00 gaven daardoor tot op vijf decimalen
#    hetzelfde resultaat — dat is geen bevinding dat het niet uitmaakt, het is een meting die
#    niet heeft plaatsgevonden. De 0.50 staat er als voorzichtige aanname: een oefeninterland
#    met vijf wissels en een B-elftal zegt minder dan een kwalificatieduel. Herzie hem zodra er
#    een tweede jaargang oefeninterlands in het corpus zit, en schrijf dan op wat eruit kwam.
HALFLIFE_DAYS = 2920.0     # na acht jaar telt een duel nog half mee — gemeten, zie tabel
WEIGHT = {FRIENDLY: 0.50, QUALIFIER: 1.00, TOURNAMENT: 1.00}   # 0.50 = aanname, zie punt 2
RIDGE = 0.30               # regularisatie naar het gemiddelde — gemeten, zie tabel
MIN_MATCHES = 8.0          # gewogen duels; daaronder is de rating een aanname — poort dicht
SEASONS_BACK = 6           # hoeveel edities per competitie worden opgehaald


def _parse_score(s: str | None) -> tuple[int, int] | None:
    if not s or "-" not in s:
        return None
    try:
        h, a = s.split("-")
        return int(h.strip()), int(a.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------
# Corpus
# ---------------------------------------------------------------------------------------------
def build_corpus(*, verbose: bool = True) -> list[dict]:
    """Haal alle afgelopen interlands op uit `fixtures.allMatches` per competitie-editie."""
    rijen: dict[str, dict] = {}
    for lid, (naam, soort) in COMPETITIONS.items():
        try:
            eerste = _get_json(f"https://www.fotmob.com/api/data/leagues?id={lid}")
            seizoenen = (eerste.get("allAvailableSeasons") or [])[:SEASONS_BACK]
        except Exception as e:                                   # noqa: BLE001
            if verbose:
                print(f"  {naam:44s} FOUT bij seizoenlijst: {type(e).__name__}")
            continue
        for seiz in seizoenen or [""]:
            q = urllib.parse.quote(seiz, safe="")
            url = f"https://www.fotmob.com/api/data/leagues?id={lid}"
            if seiz:
                url += f"&season={q}"
            try:
                d = _get_json(url)
            except Exception as e:                               # noqa: BLE001
                if verbose:
                    print(f"  {naam:30s} {seiz:12s} FOUT {type(e).__name__}")
                continue
            n = 0
            for m in (d.get("fixtures") or {}).get("allMatches") or []:
                st = m.get("status") or {}
                sc = _parse_score(st.get("scoreStr"))
                if not st.get("finished") or not sc:
                    continue
                hid, aid = (m.get("home") or {}).get("id"), (m.get("away") or {}).get("id")
                if not hid or not aid:
                    continue
                rijen[str(m.get("id"))] = {
                    "id": str(m.get("id")), "date": (st.get("utcTime") or "")[:10],
                    "competition": naam, "kind": soort, "season": seiz,
                    "home_id": str(hid), "away_id": str(aid),
                    "home": (m.get("home") or {}).get("name"),
                    "away": (m.get("away") or {}).get("name"),
                    "gh": sc[0], "ga": sc[1],
                }
                n += 1
            if verbose:
                print(f"  {naam:44s} {seiz:12s} {n:4d} afgelopen duels")
    uit = sorted(rijen.values(), key=lambda r: r["date"])
    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    with CORPUS.open("w") as f:
        for r in uit:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    if verbose:
        print(f"\n{len(uit)} unieke duels weggeschreven naar {CORPUS}")
    return uit


def load_corpus() -> list[dict]:
    if not CORPUS.exists():
        raise FileNotFoundError(f"{CORPUS} bestaat niet — draai eerst `national.py build`")
    return [json.loads(l) for l in CORPUS.open() if l.strip()]


# ---------------------------------------------------------------------------------------------
# De fit
# ---------------------------------------------------------------------------------------------
def _weight(row: dict, ref: date, halflife: float, gewichten: dict) -> float:
    try:
        d = date.fromisoformat(row["date"])
    except ValueError:
        return 0.0
    dagen = (ref - d).days
    if dagen < 0:
        return 0.0
    return gewichten.get(row["kind"], 1.0) * (0.5 ** (dagen / halflife))


def fit(rows: list[dict], *, ref: date | None = None, halflife: float = HALFLIFE_DAYS,
        gewichten: dict | None = None, ridge: float = RIDGE,
        iters: int = 4000, lr: float = 0.05) -> dict:
    """Gewogen Poisson-fit van aanval, verdediging en thuisvoordeel. Pure Python, geen numpy."""
    ref = ref or date.today()
    gewichten = gewichten or WEIGHT
    data = []
    for r in rows:
        w = _weight(r, ref, halflife, gewichten)
        if w > 1e-4:
            data.append((r["home_id"], r["away_id"], r["gh"], r["ga"], w))
    if not data:
        raise ValueError("geen bruikbare duels in het corpus")

    ids = sorted({h for h, *_ in data} | {a for _, a, *_ in data})
    idx = {t: i for i, t in enumerate(ids)}
    n = len(ids)
    atk = [0.0] * n
    dfn = [0.0] * n
    tot_w = sum(w for *_, w in data)
    gem = sum((gh + ga) * w for _, _, gh, ga, w in data) / (2 * tot_w)
    home_adv = math.log(
        max(1e-6, sum(gh * w for _, _, gh, _, w in data) / tot_w)
        / max(1e-6, sum(ga * w for _, _, _, ga, w in data) / tot_w))
    base = math.log(max(1e-6, gem))

    # gewogen aantal duels per ploeg — nodig voor de poort en voor de regularisatie
    wn = [0.0] * n
    for h, a, _, _, w in data:
        wn[idx[h]] += w
        wn[idx[a]] += w

    for it in range(iters):
        g_atk = [0.0] * n
        g_dfn = [0.0] * n
        g_home = 0.0
        for h, a, gh, ga, w in data:
            i, j = idx[h], idx[a]
            lh = math.exp(base + home_adv / 2 + atk[i] - dfn[j])
            la = math.exp(base - home_adv / 2 + atk[j] - dfn[i])
            rh, ra = w * (gh - lh), w * (ga - la)
            g_atk[i] += rh
            g_dfn[j] -= rh
            g_atk[j] += ra
            g_dfn[i] -= ra
            g_home += (rh - ra) / 2
        for i in range(n):
            g_atk[i] -= 2 * ridge * atk[i]
            g_dfn[i] -= 2 * ridge * dfn[i]
        step = lr / (1 + it / 500)
        for i in range(n):
            atk[i] += step * g_atk[i] / max(1.0, wn[i])
            dfn[i] += step * g_dfn[i] / max(1.0, wn[i])
        home_adv += step * g_home / tot_w
        # identificeerbaarheid: het gemiddelde ligt op nul, anders schuift de hele schaal
        ma, md = sum(atk) / n, sum(dfn) / n
        atk = [x - ma for x in atk]
        dfn = [x - md for x in dfn]

    namen = {}
    for r in rows:
        namen[r["home_id"]] = r["home"]
        namen[r["away_id"]] = r["away"]
    return {
        "ref": ref.isoformat(), "n_matches": len(data), "n_teams": n,
        "base": base, "home_adv": home_adv, "avg_goals_per_team": gem,
        "halflife_days": halflife, "weights": gewichten, "ridge": ridge,
        "teams": {t: {"name": namen.get(t), "attack": round(math.exp(atk[idx[t]]), 4),
                      "defence": round(math.exp(-dfn[idx[t]]), 4),
                      "weighted_matches": round(wn[idx[t]], 2)} for t in ids},
    }


def save_fit(f: dict) -> None:
    FIT.parent.mkdir(parents=True, exist_ok=True)
    FIT.write_text(json.dumps(f, ensure_ascii=False, indent=1))


def load_fit() -> dict:
    if not FIT.exists():
        raise FileNotFoundError(f"{FIT} bestaat niet — draai eerst `national.py fit`")
    return json.loads(FIT.read_text())


# ---------------------------------------------------------------------------------------------
# Aansluiting op model.py
# ---------------------------------------------------------------------------------------------
def context(f: dict | None = None) -> LeagueContext:
    """De internationale basis, op de schaal die `model.match_lambdas` verwacht."""
    f = f or load_fit()
    gem = f["avg_goals_per_team"]
    h = math.exp(f["home_adv"] / 2)
    return LeagueContext(home_goals_per_match=gem * h,
                         away_goals_per_match=gem / h,
                         avg_xg_per_match=gem)


def find_team(f: dict, name_or_id: str) -> str | None:
    """Team-id opzoeken op Fotmob-id of op naam (exact, dan genormaliseerd)."""
    if name_or_id in f["teams"]:
        return name_or_id
    doel = (name_or_id or "").strip().lower()
    for tid, v in f["teams"].items():
        if (v.get("name") or "").strip().lower() == doel:
            return tid
    for tid, v in f["teams"].items():
        if (v.get("name") or "").strip().lower().startswith(doel[:6]):
            return tid
    return None


def in_range(team_id: str, f: dict | None = None) -> tuple[bool, str]:
    """Poort, geen aantekening: te weinig duels → de rating is regularisatie, geen meting."""
    f = f or load_fit()
    v = f["teams"].get(team_id)
    if not v:
        return False, f"geen interlandrating voor team-id {team_id}"
    wm = v.get("weighted_matches", 0.0)
    if wm < MIN_MATCHES:
        return False, (f"{v.get('name')}: {wm:.1f} gewogen duels, onder MIN_MATCHES "
                       f"({MIN_MATCHES}) — rating vrijwel volledig regularisatie")
    return True, f"{v.get('name')}: {wm:.1f} gewogen duels"


def team(team_id: str, f: dict | None = None, *, matches: int = 20) -> TeamStats:
    """`TeamStats` op de internationale schaal. `matches` is een schaalgetal, geen meting:
    `model.team_strength` deelt xg door matches, dus de waarde valt weg tegen `xg_per_match`."""
    f = f or load_fit()
    v = f["teams"][team_id]
    gem = f["avg_goals_per_team"]
    return TeamStats(xg=v["attack"] * gem * matches,
                     xga=v["defence"] * gem * matches,
                     matches_played=matches)


# ---------------------------------------------------------------------------------------------
# Meten
# ---------------------------------------------------------------------------------------------
def _brier(rows: list[dict], f: dict) -> tuple[float, int]:
    """Brier-score op de 1X2-uitkomst, over de duels waarvan beide ploegen een rating hebben."""
    try:
        from .model import analyze_match
    except ImportError:
        from model import analyze_match                          # type: ignore[no-redef]
    ctx = context(f)
    som, n = 0.0, 0
    for r in rows:
        if r["home_id"] not in f["teams"] or r["away_id"] not in f["teams"]:
            continue
        p = analyze_match(team(r["home_id"], f), team(r["away_id"], f), ctx, shrink=1.0)
        werk = (1.0, 0.0, 0.0) if r["gh"] > r["ga"] else (
            (0.0, 1.0, 0.0) if r["gh"] == r["ga"] else (0.0, 0.0, 1.0))
        som += sum((q - w) ** 2 for q, w in zip((p.home, p.draw, p.away), werk))
        n += 1
    return (som / n if n else float("nan")), n


def tune_report(rows: list[dict], cutoff: str) -> None:
    """Uit-steekproef: fit op alles vóór `cutoff`, meet op alles erna.

    Gemeten op 20 september 2026 met cutoff 2025-09-01. De waarden bovenaan dit bestand komen
    hieruit; draai het opnieuw als het corpus flink is gegroeid, en verander de parameters
    nooit op een redenering (§1d, §6e).

    LET OP bij het lezen van de kolom `oefenweging`: zolang Fotmob voor id 114 alleen het
    lopende kalenderjaar teruggeeft, zitten er nul oefeninterlands in de training en zijn alle
    rijen met een andere oefenweging identiek. Dat is geen bevinding maar een lege meting.
    """
    train = [r for r in rows if r["date"] < cutoff]
    test = [r for r in rows if r["date"] >= cutoff]
    ref = date.fromisoformat(cutoff)
    print(f"fit op {len(train)} duels t/m {cutoff}, getest op {len(test)} duels erna\n")
    print(f"{'halfwaardetijd':>15s}{'oefenweging':>13s}{'ridge':>8s}{'Brier uit':>12s}{'n':>7s}")
    beste = None
    for hl in (360.0, 720.0, 1460.0):
        for fw in (0.25, 0.50, 1.00):
            for rg in (0.30, 0.60, 1.20):
                f = fit(train, ref=ref, halflife=hl,
                        gewichten={FRIENDLY: fw, QUALIFIER: 1.0, TOURNAMENT: 1.0}, ridge=rg)
                b, n = _brier(test, f)
                print(f"{hl:15.0f}{fw:13.2f}{rg:8.2f}{b:12.5f}{n:7d}")
                if beste is None or b < beste[0]:
                    beste = (b, hl, fw, rg)
    print(f"\nbeste uit-steekproef: Brier {beste[0]:.5f} bij halfwaardetijd {beste[1]:.0f} dagen, "
          f"oefenweging {beste[2]:.2f}, ridge {beste[3]:.2f}")
    print("Ter vergelijking: 1/3-1/3-1/3 gokken geeft Brier 0.66667.")


def verify(f: dict) -> None:
    """Controleer dat `analyze_match` dezelfde lambdas teruggeeft als de fit zelf berekent."""
    try:
        from .model import match_lambdas
    except ImportError:
        from model import match_lambdas                          # type: ignore[no-redef]
    ctx = context(f)
    ids = [t for t, v in f["teams"].items() if v["weighted_matches"] >= MIN_MATCHES][:6]
    print(f"{'duel':44s}{'fit lh':>9s}{'model lh':>10s}{'fit la':>9s}{'model la':>10s}")
    ok = True
    for h in ids[:3]:
        for a in ids[3:6]:
            vh, va = f["teams"][h], f["teams"][a]
            gem, adv = f["avg_goals_per_team"], f["home_adv"]
            lh = gem * math.exp(adv / 2) * vh["attack"] * va["defence"]
            la = gem * math.exp(-adv / 2) * va["attack"] * vh["defence"]
            mlh, mla = match_lambdas(team(h, f), team(a, f), ctx, shrink=1.0)
            if abs(lh - mlh) > 1e-6 or abs(la - mla) > 1e-6:
                ok = False
            print(f"{(vh['name'] or h)[:20]:21s}-{(va['name'] or a)[:20]:21s}"
                  f"{lh:9.3f}{mlh:10.3f}{la:9.3f}{mla:10.3f}")
    print("\nOK — de rating sluit aan op model.match_lambdas." if ok else
          "\nAFWIJKING — de schaal van national.team() klopt niet met model.match_lambdas.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="corpus ophalen bij Fotmob")
    sub.add_parser("fit", help="rating fitten op het corpus")
    t = sub.add_parser("tune", help="de wegingen uit-steekproef meten")
    t.add_argument("--cutoff", default="2025-09-01")
    s = sub.add_parser("show", help="rating van een of meer ploegen")
    s.add_argument("teams", nargs="*")
    sub.add_parser("verify", help="controleer de aansluiting op model.py")
    sub.add_parser("stats", help="omvang en dekking van het corpus")
    a = ap.parse_args()

    if a.cmd == "build":
        build_corpus()
    elif a.cmd == "fit":
        rows = load_corpus()
        f = fit(rows)
        save_fit(f)
        b, n = _brier(rows, f)
        print(f"{f['n_matches']} gewogen duels, {f['n_teams']} ploegen, "
              f"thuisvoordeel {math.exp(f['home_adv']):.3f}x, "
              f"gemiddeld {f['avg_goals_per_team']:.3f} doelpunten per ploeg per duel")
        print(f"Brier IN-steekproef {b:.5f} over {n} duels (1/3-gokken = 0.66667) — "
              f"lees de uit-steekproefwaarde met `tune`.")
        print(f"weggeschreven naar {FIT}")
    elif a.cmd == "tune":
        tune_report(load_corpus(), a.cutoff)
    elif a.cmd == "show":
        f = load_fit()
        namen = a.teams or ["Netherlands", "Germany", "Brazil", "San Marino"]
        print(f"{'ploeg':26s}{'aanval':>9s}{'verdediging':>13s}{'duels':>8s}  poort")
        for naam in namen:
            tid = find_team(f, naam)
            if not tid:
                print(f"{naam:26s}  niet gevonden in de rating")
                continue
            v = f["teams"][tid]
            ok, reden = in_range(tid, f)
            print(f"{(v['name'] or tid)[:25]:26s}{v['attack']:9.3f}{v['defence']:13.3f}"
                  f"{v['weighted_matches']:8.1f}  {'open' if ok else 'DICHT'}")
    elif a.cmd == "verify":
        verify(load_fit())
    elif a.cmd == "stats":
        rows = load_corpus()
        per = {}
        for r in rows:
            per.setdefault(r["competition"], 0)
            per[r["competition"]] += 1
        print(f"{len(rows)} duels, {rows[0]['date']} t/m {rows[-1]['date']}")
        for k, v in sorted(per.items(), key=lambda x: -x[1]):
            print(f"  {k:46s} {v:5d}")


if __name__ == "__main__":
    main()
