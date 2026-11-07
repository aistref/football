"""Run D — de wekelijkse controlerun: leest de drie runs na en analyseert ze.

    python3 scripts/meta.py week --end 2026-11-08     # de week die net klaar is
    python3 scripts/meta.py integriteit --weeks 1
    python3 scripts/meta.py bets
    python3 scripts/meta.py poorten
    python3 scripts/meta.py markten
    python3 scripts/meta.py selftest                  # geen netwerk, geen repo nodig

**Dit script is READ-ONLY op alles wat van een run komt.** Het schrijft nooit naar `data/`, raakt
geen afgewikkelde pick aan en rendert geen gepubliceerd rapport opnieuw. Het rapporteert en legt
voor; het beslist niet. Een systeem dat zijn eigen drempels bijstelt op zijn eigen uitvoer maakt
de logboeken waardeloos, en dat is dezelfde circulariteit die §2 in een andere vorm verbiedt.

WAAROM DIT ER IS. De drie runs meten al veel: `ledger stats`, `shadow stats`,
`calibration stats`, `ctxlog stats`, `margins stats`, `goalbias`, `recalibrate show` en
`gridfit measure`. Het ontbrak aan twee dingen, en het tweede is het belangrijkste:

1. **Niemand las die cijfers over de tijd.** Elke run drukt een momentopname af in een rapport
   dat daarna niemand opent. Een reeks die vier weken dezelfde kant op kruipt, ziet er elke
   ochtend uit als ruis.
2. **Niemand controleerde of de runs deden wat de regels zeggen.** De geschiedenis van deze repo
   is een reeks stille administratiefouten: `calibration.py settle` elf dagen niet gedraaid
   (18–29 sep), het Serie B-id dat stil het verkeerde seizoen gaf, het Hongaarse id dat de
   seizoensparameter negeerde, `settled_note` als prosesleutel die `report.py` nooit las,
   `resumed_count` die aanroepen telde in plaats van hervattingen in 88 bestanden, de gepoolde
   promotiefactor die drie runrapporten lang onwaar werd overgenomen, en `week_around` dat op
   naam koppelde (7 nov). **De dominante faalvorm hier is geen verkeerde bet maar een stille
   administratiefout waardoor de metingen gaan liegen**, en daar was geen enkele controle op.

DE STATISTISCHE HOOFDREGEL VAN DIT SCRIPT, en hij staat vooraan omdat alles eronder erop leunt:
**rendement beantwoordt de hoofdvraag op deze tijdschaal niet.** Bij ~47 afgewikkelde bets per
week, een trefkans rond 46% en gemiddelde koers 2,17 is de standaardfout op het weekrendement
ongeveer 16 procentpunt. Een week op +10% of −20% zegt niets. Om een echte voorsprong van 5
procentpunt met t = 2 aan te tonen zijn ~1900 bets nodig, oftewel veertig weken. Daarom drukt dit
script bij élk rendement een t-waarde en een interval af, en daarom staan de kalibratiecijfers
(~780 nieuwe waarnemingen per week) vóór de winst-en-verliesrekening.

MEERVOUDIG TOETSEN. Wie 540 picks opsplitst naar markt × tier × koersband × competitie vindt met
zekerheid "significante" dingen die niet bestaan. De uitsplitsingen van dit script staan daarom
VOORAF vast in `VERGELIJKINGEN` en het meldt hoeveel vergelijkingen het heeft gemaakt. Voeg er
geen toe zonder dat getal mee te verhogen, en lees een |t| onder 2 als ruis — ook als het verhaal
erbij klopt.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE = DATA / "run-state"
RUNS = ROOT / "runs"

# Vooraf vastgelegde uitsplitsingen (zie de kop: meervoudig toetsen).
VERGELIJKINGEN = [
    "markt (7)", "data_tier (2)", "koersband (4)", "edgeband (4)", "kant (3)",
    "run (3)", "poort (8)", "rang in de shortlist (5)", "push vs binair (2)",
]

# Run C draait niet dagelijks: de gebruiker zet hem zelf aan als het interlandvoetbal
# begint (besluit 7 nov 2026). Zijn afwezigheid is dus GEEN storing en hoort niet als gat
# gemeld te worden — zelfde soort besluit als `API_FOOTBALL_KEY` (§3, 27 sep 2026).
DAGELIJKSE_RUNS = ("a", "b")
HANDMATIGE_RUNS = ("c",)

# Breekpunten in de meetreeks. Een cijfer over een periode die er een kruist, meet twee
# populaties door elkaar — de fout waar `gridfit.py` in zijn eigen kop voor waarschuwt.
BREEKPUNTEN = [
    (date(2026, 8, 31), "EDGE_THRESHOLD_FULL 3.0 -> 8.0 (§0)"),
    (date(2026, 9, 5), "XG_WEIGHT 0.5 -> 0.8, herijking §1g aan, CREDIBILITY_K 16 -> 8"),
    (date(2026, 9, 20), "DEFAULT_SHRINK 0.8 -> 1.0 (§6e) en de drempel naar §5b"),
    (date(2026, 10, 1), "poort 8 terug na zes dagen vervallen (§1e)"),
    (date(2026, 10, 12), "poort 9 bindt: Under op FULL eist 10.0 pp (§1h)"),
    (date(2026, 11, 3), "LEVEL_SCALE 1.032 in de lambdaketen (§6g)"),
]

OPEN = "pending"
BESLIST = ("won", "lost")


# ------------------------------------------------------------------ statistiek

def units(row: dict) -> float:
    """Netto eenheden bij 1u inzet. Zelfde regel als `ledger.net_units` (kwartlijnen)."""
    u = row.get("settled_units")
    if u is not None:
        return float(u)
    return (row["odds"] - 1) if row.get("result") == "won" else -1.0


def wilson(k: int, n: int) -> tuple[float, float]:
    """95%-interval op een trefkans. Wilson en niet normaal: bij kleine n is dat eerlijker."""
    if not n:
        return (0.0, 0.0)
    z, p = 1.96, k / n
    d = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, mid - half), min(1.0, mid + half))


def roi_stats(rows: list[dict]) -> dict:
    """Rendement MET een t-waarde en een interval. Een punt zonder spreiding misleidt."""
    d = [r for r in rows if r.get("result") in BESLIST]
    n = len(d)
    if not n:
        return {"n": 0, "won": 0, "hit": None, "roi": None, "t": None, "se": None,
                "lo": None, "hi": None, "ci_hit": (None, None)}
    u = [units(r) for r in d]
    won = sum(1 for r in d if r["result"] == "won")
    mean = sum(u) / n
    var = sum((x - mean) ** 2 for x in u) / (n - 1) if n > 1 else 0.0
    se = math.sqrt(var / n) if n > 1 else 0.0
    return {
        "n": n, "won": won, "hit": won / n, "roi": mean, "se": se,
        "t": (mean / se) if se else None,
        "lo": mean - 1.96 * se, "hi": mean + 1.96 * se,
        "ci_hit": wilson(won, n),
        "units": sum(u),
    }


def fmt_roi(s: dict) -> str:
    if not s["n"]:
        return "geen afgewikkelde gevallen"
    t = f"t={s['t']:+.2f}" if s["t"] is not None else "t=n.v.t."
    lo, hi = s["ci_hit"]
    return (f"n={s['n']:4d}  trefkans {100*s['hit']:5.1f}% [{100*lo:.0f}–{100*hi:.0f}]  "
            f"rendement {100*s['roi']:+6.1f}% [{100*s['lo']:+.0f}–{100*s['hi']:+.0f}]  {t}")


def brier(rows: list[dict], *, markt: bool = False) -> float | None:
    d = [r for r in rows if r.get("result") in BESLIST]
    vals = []
    for r in d:
        p = r.get("implied_prob") if markt else r.get("my_prob")
        if p is None:
            continue
        vals.append((p - (1.0 if r["result"] == "won" else 0.0)) ** 2)
    return sum(vals) / len(vals) if vals else None


# -------------------------------------------------------------------- inlezen

def jsonl(naam: str) -> list[dict]:
    p = DATA / naam
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def run_states() -> dict[tuple[str, str], dict]:
    """{(datum, run): state} voor alles in data/run-state/."""
    out = {}
    if not STATE.exists():
        return out
    for f in sorted(STATE.glob("*.json")):
        m = re.match(r"(\d{4}-\d\d-\d\d)-run-([abcd])\.json$", f.name)
        if not m:
            continue
        try:
            out[(m.group(1), m.group(2))] = json.loads(f.read_text())
        except json.JSONDecodeError:
            out[(m.group(1), m.group(2))] = {"_leesfout": True}
    return out


def wedstrijden(st: dict):
    """Loop de wedstrijdrecords van één run-state af, en sla over wat geen record is.

    Oudere voortgangsbestanden schrijven een competitie soms als platte string in plaats van
    als `{"status": ..., "matches": [...]}` — Run B deed dat op 10 aug 2026 — en een enkele
    `matches`-lijst bevat strings. `report.normalise_competitions` dekt dat daar al af; hier
    gebeurt hetzelfde, want een controlerun die omvalt op de invoer van een andere run is zelf
    het probleem.
    """
    for comp, v in (st.get("competitions") or {}).items():
        if not isinstance(v, dict):
            continue
        for m in v.get("matches") or []:
            if isinstance(m, dict):
                yield comp, m


def kandidaten(states: dict) -> list[dict]:
    """Alle doorgerekende selecties met hun poortuitkomsten, plat."""
    out = []
    for (dag, run), st in states.items():
        for comp, m in wedstrijden(st):
            for c in m.get("all_candidates") or []:
                if not isinstance(c, dict) or not c.get("poorten"):
                    continue
                out.append({"dag": dag, "run": run, "competition": comp,
                            "match": m.get("match"), **c})
    return out


# ---------------------------------------------------------------- integriteit

def integriteit(states: dict, picks: list[dict], shadow: list[dict],
                v_begin: date, v_eind: date) -> list[tuple[str, str]]:
    """Geeft [(ernst, melding)]. 'FOUT' is iets stuks, 'LET OP' is iets om te bekijken."""
    uit: list[tuple[str, str]] = []

    # 1. Draaide elke dagelijkse run elke dag, en is hij afgerond?
    d = v_begin
    while d <= v_eind:
        iso = d.isoformat()
        for r in DAGELIJKSE_RUNS:
            st = states.get((iso, r))
            if st is None:
                uit.append(("FOUT", f"{iso} Run {r.upper()}: geen voortgangsbestand — "
                                    f"de run is niet gedraaid of heeft niets vastgelegd"))
            elif not st.get("completed"):
                uit.append(("FOUT", f"{iso} Run {r.upper()}: voortgangsbestand niet afgesloten "
                                    f"(`mark_completed` niet gezet) — de run is halverwege "
                                    f"gestopt of §6b-7 is overgeslagen"))
        d += timedelta(days=1)

    # Run C met zoveel woorden NIET als gat melden (besluit 7 nov 2026).
    c_dagen = sorted(dg for (dg, r) in states if r in HANDMATIGE_RUNS)
    laatste_c = c_dagen[-1] if c_dagen else "nooit"
    uit.append(("INFO", f"Run C draait op verzoek en niet dagelijks (besluit 7 nov 2026); "
                        f"laatste run {laatste_c}. Afwezigheid is hier geen storing."))

    # 2. De herijking: `fitted_through` hoort op de vorige rundag te staan of later (§6b-5c).
    try:
        sys.path.insert(0, str(ROOT))
        from scripts.recalibrate import load_fit
        fit = load_fit()
        ft = getattr(fit, "fitted_through", None)
        rundagen = sorted({dg for (dg, _) in states})
        vorige = [x for x in rundagen if x < v_eind.isoformat()]
        verwacht = vorige[-1] if vorige else None
        if ft and verwacht and ft < verwacht:
            uit.append(("FOUT", f"herijking is gefit t/m {ft} terwijl de laatste rundag "
                                f"{verwacht} is — `calibration.py settle` is blijven liggen "
                                f"(§6b-5c: dit heeft in september elf dagen stil schade gedaan)"))
        else:
            uit.append(("INFO", f"herijking gefit t/m {ft} — bij de laatste rundag, dus "
                                f"`calibration.py settle` is gedraaid"))
    except Exception as e:
        uit.append(("LET OP", f"herijking niet te lezen: {type(e).__name__}: {e}"))

    # 3. Te lang openstaande rijen. Een pick die drie dagen na de aftrap nog `pending` staat,
    #    is niet afgewikkeld — en een niet-afgewikkeld logboek klaagt nooit zelf.
    grens = (v_eind - timedelta(days=3)).isoformat()
    for naam, rijen, sleutel in (("picks.jsonl", picks, "kickoff"),
                                 ("shadow.jsonl", shadow, "date")):
        oud = [r for r in rijen if r.get("result") == OPEN
               and str(r.get(sleutel) or "")[:10] < grens]
        if oud:
            vb = ", ".join(str(r.get("id"))[:52] for r in oud[:3])
            uit.append(("FOUT", f"{naam}: {len(oud)} rij(en) staan nog open terwijl de aftrap "
                                f"meer dan 3 dagen geleden is — {vb}"))

    # 4. Dezelfde wedstrijd twee keer in dezelfde schaduwcategorie op dezelfde dag.
    #    §1e en §5a verbieden dat: het telt één populatie dubbel.
    dubbel = Counter((r.get("date"), r.get("match"), r.get("failed_gate")) for r in shadow)
    dd = {k: v for k, v in dubbel.items() if v > 1}
    if dd:
        uit.append(("FOUT", f"shadow.jsonl: {len(dd)} wedstrijd(en) staan dubbel in dezelfde "
                            f"categorie op dezelfde dag (§1e/§5a verbieden dat) — "
                            f"bv. {list(dd)[:2]}"))

    # 5. Dubbele pick-id's.
    ids = Counter(p.get("id") for p in picks)
    dup = [k for k, v in ids.items() if v > 1]
    if dup:
        uit.append(("FOUT", f"picks.jsonl: {len(dup)} dubbele id('s) — {dup[:3]}"))

    # 6. Gepubliceerde bets zonder de blokken die §6b eist.
    week_picks = [p for p in picks
                  if v_begin.isoformat() <= str(p.get("run_date")) <= v_eind.isoformat()]
    eisen = (("voorbeschouwing", "§6b-5i"), ("marktvorm", "§6b-5h"),
             ("context", "§6c"), ("calibration", "§6b-5c"))
    mist = defaultdict(list)
    for p in week_picks:
        st = states.get((p.get("run_date"), str(p.get("run", "")).lower()))
        if not st:
            continue
        rec = None
        naam = f"{p.get('home')} – {p.get('away')}"
        for _comp, m in wedstrijden(st):
            if m.get("match") == naam:
                rec = m
        if rec is None:
            mist["wedstrijdrecord"].append(naam)
            continue
        for sleutel, par in eisen:
            if not rec.get(sleutel):
                mist[f"{sleutel} ({par})"].append(naam)
    for wat, waar in sorted(mist.items()):
        uit.append(("LET OP", f"{len(waar)} gepubliceerde bet(s) zonder `{wat}` in run-state — "
                              f"{', '.join(waar[:2])}"))

    # 7. Zijn de poortnamen consistent? Een tweede spelling splitst één reeks in twee, en dan
    #    haalt geen van beide ooit de ~30 afgewikkelde gevallen die §6d eist — dezelfde fout
    #    die §5b bij `lijstlengte` met zoveel woorden verbiedt.
    # `anticirc` (poort 3) en `tier` (poort 4) zijn geldige, oudere sleutels en horen hier dus
    # in de lijst: een controle die aanslaat op correcte namen leert je hem te negeren.
    bekend = {"edge", "odds", "data", "tweede_methode", "robuustheid", "context", "underdog",
              "underdog_ruw", "doelpunten_onder", "herijking", "herijking_omgekeerd",
              "lijstlengte", "anticirc", "tier"}
    vreemd = {g: n for g, n in
              Counter(r.get("failed_gate") for r in shadow if r.get("failed_gate")).items()
              if g not in bekend}
    if vreemd:
        uit.append(("FOUT", f"shadow.jsonl gebruikt onbekende poortnaam(en): {vreemd} — een "
                            f"tweede spelling splitst één reeks in twee en dan haalt geen van "
                            f"beide de ~30 van §6d"))
    in_state = Counter()
    for st in states.values():
        for _comp, m in wedstrijden(st):
            for c in m.get("all_candidates") or []:
                if isinstance(c, dict):
                    in_state.update((c.get("poorten") or {}).keys())
    afwijkend = {g: n for g, n in in_state.items() if g not in bekend}
    if afwijkend:
        uit.append(("LET OP", f"`poorten` in run-state gebruikt naam(en) die niet in de vaste "
                              f"lijst staan: {afwijkend} — vermoedelijk een oudere spelling "
                              f"(`robuust` naast `robuustheid`); de reeks wordt daardoor over "
                              f"twee sleutels verdeeld"))

    # 8. Artifact-link vastgelegd? §6c eist publicatie, §7 de link in de notificatie.
    for (dag, r), st in sorted(states.items()):
        if not (v_begin.isoformat() <= dag <= v_eind.isoformat()):
            continue
        if r in HANDMATIGE_RUNS:
            continue
        if st.get("completed") and not st.get("artifact"):
            # Onderscheid maken, want dit zijn twee heel verschillende problemen: is de PAGINA
            # er niet, dan is §6c overgeslagen; is de pagina er wel maar de LINK niet
            # vastgelegd, dan is alleen de administratie incompleet en is de link later niet
            # meer terug te vinden.
            if (RUNS / f"{dag}-run-{r}.html").exists():
                uit.append(("LET OP", f"{dag} Run {r.upper()}: dagrapport is gerenderd maar de "
                                      f"Artifact-link is niet in run-state vastgelegd — later "
                                      f"niet meer terug te vinden welke pagina is verstuurd"))
            else:
                uit.append(("FOUT", f"{dag} Run {r.upper()}: geen dagrapport gerenderd en geen "
                                    f"Artifact-link — §6c eist beide, elke run"))
    return uit


# ------------------------------------------------------------------ analyses

def band(x: float | None, grenzen: tuple, labels: tuple) -> str:
    if x is None:
        return "onbekend"
    for g, lab in zip(grenzen, labels):
        if x < g:
            return lab
    return labels[-1]


PUSH_MARKTEN = ("Asian Handicap", "Draw No Bet", "Double Chance")


def analyse_bets(picks: list[dict]) -> list[str]:
    uit = ["", "BETS — de hele reeks", "=" * 78]
    alles = roi_stats(picks)
    uit.append(f"  alle picks            {fmt_roi(alles)}")
    be, bm = brier(picks), brier(picks, markt=True)
    if be and bm:
        uit.append(f"  Brier eigen {be:.4f} tegen markt {bm:.4f} — "
                   f"{'de markt schat scherper' if bm < be else 'het model schat scherper'} "
                   f"(verschil {be - bm:+.4f})")
        uit.append("  Dit is de regel die zegt of de kansschatting iets toevoegt. Zolang de")
        uit.append("  markt lager staat, is elk gemeten voordeel eerder modelfout dan marktfout.")

    uit += ["", "  per markt (Over/Under gesplitst op de kant)"]
    groepen = defaultdict(list)
    for p in picks:
        k = p.get("market")
        if k == "Over/Under":
            sel = str(p.get("selection", "")).lower()
            k = "Over/Under — Under" if sel.startswith("under") else "Over/Under — Over"
        groepen[k].append(p)
    for k, rows in sorted(groepen.items(), key=lambda x: -len(x[1])):
        uit.append(f"    {k:26s} {fmt_roi(roi_stats(rows))}")

    uit += ["", "  push-beschermd tegen binair"]
    push = [p for p in picks if p.get("market") in PUSH_MARKTEN]
    bin_ = [p for p in picks if p.get("market") not in PUSH_MARKTEN]
    uit.append(f"    {'push (AH/DNB/DC)':26s} {fmt_roi(roi_stats(push))}")
    uit.append(f"    {'binair (1X2/O-U/BTTS)':26s} {fmt_roi(roi_stats(bin_))}")
    uit.append("    §1a koos `selection_score` deels omdat push-markten minder blootstaan aan de")
    uit.append("    gelijkspelfout die §6f meet. Dit is de regel die zegt of dat zich uitbetaalt.")

    uit += ["", "  per data_tier"]
    for t in ("FULL", "LIGHT"):
        uit.append(f"    {t:26s} {fmt_roi(roi_stats([p for p in picks if p.get('data_tier') == t]))}")

    uit += ["", "  per koersband"]
    kb = defaultdict(list)
    for p in picks:
        kb[band(p.get("odds"), (1.7, 2.2, 3.0), ("< 1.70", "1.70–2.20", "2.20–3.00", "> 3.00"))].append(p)
    for k in ("< 1.70", "1.70–2.20", "2.20–3.00", "> 3.00"):
        if kb.get(k):
            uit.append(f"    {k:26s} {fmt_roi(roi_stats(kb[k]))}")

    uit += ["", "  per geclaimde edge"]
    eb = defaultdict(list)
    for p in picks:
        eb[band(p.get("edge_pp"), (8, 10, 14), ("< 8 pp", "8–10 pp", "10–14 pp", "> 14 pp"))].append(p)
    for k in ("< 8 pp", "8–10 pp", "10–14 pp", "> 14 pp"):
        if eb.get(k):
            uit.append(f"    {k:26s} {fmt_roi(roi_stats(eb[k]))}")
    uit.append("    §1g heeft op 552 gevallen gemeten dat het rendement het SLECHTST is bij de")
    uit.append("    hoogste geclaimde edge. Loopt deze kolom oplopend, dan is dat nieuws.")

    uit += ["", "  per run"]
    for r in ("A", "B", "C"):
        rows = [p for p in picks if p.get("run") == r]
        if rows:
            uit.append(f"    Run {r:22s} {fmt_roi(roi_stats(rows))}")

    uit += ["", "  samenhang binnen een dag (waarom de spreiding groter is dan n suggereert)"]
    per_dag = defaultdict(list)
    for p in picks:
        if p.get("result") in BESLIST:
            per_dag[p.get("run_date")].append(units(p))
    dagen = [sum(v) for v in per_dag.values() if v]
    n_bets = sum(len(v) for v in per_dag.values())
    if dagen and n_bets > 1:
        m = sum(dagen) / len(dagen)
        var_dag = sum((x - m) ** 2 for x in dagen) / (len(dagen) - 1) if len(dagen) > 1 else 0
        se_dag = math.sqrt(var_dag / len(dagen)) * len(dagen) / n_bets if n_bets else 0
        uit.append(f"    {len(dagen)} rundagen, {n_bets} bets, gemiddeld "
                   f"{n_bets/len(dagen):.1f} per dag")
        uit.append(f"    standaardfout per bet, onafhankelijk gerekend : "
                   f"{100*alles['se']:.2f} pp")
        uit.append(f"    idem, per DAG geclusterd                      : "
                   f"{100*se_dag:.2f} pp")
        if alles["se"]:
            uit.append(f"    verhouding {se_dag/alles['se']:.2f}× — boven 1 betekent dat bets op "
                       f"dezelfde dag samenhangen")
        uit.append("    Vijf Over-bets op één zaterdag zijn geen vijf onafhankelijke bets. Dit is")
        uit.append("    de eerlijke spreiding; de kolom hierboven onderschat hem.")

    uit += ["", "  doet de rangorde van `selection_score` iets? (§1a, nooit eerder gemeten)"]
    rang = defaultdict(list)
    for dag_run, rows in _per_run_dag(picks).items():
        gesorteerd = sorted([p for p in rows if p.get("shortlisted")],
                            key=lambda p: -(p.get("edge_pp") or 0) * (p.get("my_prob") or 0))
        for i, p in enumerate(gesorteerd, 1):
            rang[i].append(p)
    for i in sorted(rang):
        if len(rang[i]) >= 10:
            uit.append(f"    rang {i:<21d} {fmt_roi(roi_stats(rang[i]))}")
    uit.append("    Loopt dit niet aflopend, dan rangschikt `selection_score` niets — en dan is")
    uit.append("    de keuze van 14 aug een smaakkwestie en geen weegregel.")
    return uit


def _per_run_dag(picks: list[dict]) -> dict:
    out = defaultdict(list)
    for p in picks:
        out[(p.get("run_date"), p.get("run"))].append(p)
    return out


def analyse_poorten(shadow: list[dict], kand: list[dict]) -> list[str]:
    uit = ["", "POORTEN — wat ze tegenhielden en of dat geld bespaarde", "=" * 78]
    uit.append("  Een poort is verdiend als zijn schaduwreeks NEGATIEF staat: dan houdt hij")
    uit.append("  verliezers tegen. Positief betekent dat hij winnende bets kost.")
    uit.append("  Lees niets onder ~30 afgewikkelde gevallen (§6d).")
    uit.append("")
    per = defaultdict(list)
    for r in shadow:
        per[r.get("failed_gate") or "onbekend"].append(r)
    for g, rows in sorted(per.items(), key=lambda x: -len(x[1])):
        s = roi_stats(rows)
        vlag = ""
        if s["n"] >= 30 and s["roi"] is not None:
            if s["roi"] > 0 and (s["t"] or 0) > 2:
                vlag = "  <-- POSITIEF en significant: houdt winnaars tegen"
            elif s["roi"] > 0:
                vlag = "  <-- positief, maar t onder 2: ruis"
        elif s["n"] < 30:
            vlag = "  (onder de ~30 van §6d — niet lezen)"
        uit.append(f"    {g:22s} {fmt_roi(s)}{vlag}")

    uit += ["", "  POORTINTERACTIE — hoe vaak doet een poort het werk alléén?", ""]
    alleen, samen = Counter(), Counter()
    totaal = 0
    for c in kand:
        po = c.get("poorten") or {}
        dicht = [k for k, v in po.items() if v is False]
        if not dicht:
            continue
        totaal += 1
        if len(dicht) == 1:
            alleen[dicht[0]] += 1
        else:
            for k in dicht:
                samen[k] += 1
    uit.append(f"    {totaal} geblokkeerde kandidaten in `data/run-state/`")
    uit.append(f"    {'poort':22s} {'alleen':>8s} {'met andere':>11s} {'aandeel alleen':>15s}")
    for g in sorted(set(alleen) | set(samen), key=lambda g: -(alleen[g] + samen[g])):
        a, s = alleen[g], samen[g]
        deel = f"{100*a/(a+s):.0f}%" if (a + s) else "—"
        uit.append(f"    {g:22s} {a:8d} {s:11d} {deel:>15s}")
    uit.append("")
    uit.append("    Dit is de kolom die telt. Een poort die bijna altijd samen met een andere")
    uit.append("    afgaat, houdt weinig tegen dat niet toch al werd tegengehouden — zijn")
    uit.append("    MARGINALE nut is dan veel kleiner dan het ruwe aantal suggereert.")
    return uit


def analyse_breekpunten(picks: list[dict], v_eind: date) -> list[str]:
    uit = ["", "BREEKPUNTEN — waarom een cijfer over 'de hele reeks' twee populaties mengt",
           "=" * 78]
    laatste = max((d for d, _ in BREEKPUNTEN if d <= v_eind), default=None)
    for d, wat in BREEKPUNTEN:
        merk = "  <-- laatste" if d == laatste else ""
        uit.append(f"    {d.isoformat()}  {wat}{merk}")
    if laatste:
        na = [p for p in picks if str(p.get("run_date")) >= laatste.isoformat()]
        uit.append("")
        uit.append(f"    sinds het laatste breekpunt ({laatste.isoformat()}):")
        uit.append(f"      {fmt_roi(roi_stats(na))}")
        uit.append("    Elk cijfer in dit rapport dat over de hele reeks gaat, mengt de")
        uit.append("    populaties van vóór en ná deze data. Dat is de fout waar `gridfit.py`")
        uit.append("    in zijn eigen kop voor waarschuwt.")
    return uit


# -------------------------------------------------------------------- rapport

def week_rapport(v_eind: date) -> int:
    v_begin = v_eind - timedelta(days=6)
    states = run_states()
    picks = jsonl("picks.jsonl")
    shadow = jsonl("shadow.jsonl")
    kand = kandidaten(states)

    week_picks = [p for p in picks
                  if v_begin.isoformat() <= str(p.get("run_date")) <= v_eind.isoformat()]
    week_shadow = [r for r in shadow
                   if v_begin.isoformat() <= str(r.get("date")) <= v_eind.isoformat()]

    print(f"RUN D — CONTROLERUN over {v_begin.isoformat()} t/m {v_eind.isoformat()}")
    print("=" * 78)
    print("Read-only: dit rapport verandert geen enkele parameter, poort of drempel. Het legt")
    print("voor; de gebruiker beslist (§9).")
    print()
    print(f"  picks deze week            {len(week_picks)} "
          f"({sum(1 for p in week_picks if p.get('result') in BESLIST)} al beslist)")
    print(f"  schaduwrijen deze week     {len(week_shadow)}")
    print(f"  logboek totaal             {len(picks)} picks, {len(shadow)} schaduwrijen")
    print(f"  vergelijkingen in dit rapport: {len(VERGELIJKINGEN)} vooraf vastgelegd "
          f"({', '.join(VERGELIJKINGEN)})")

    print()
    print("INTEGRITEIT — deden de runs wat de regels zeggen?")
    print("=" * 78)
    meldingen = integriteit(states, picks, shadow, v_begin, v_eind)
    fouten = [m for m in meldingen if m[0] == "FOUT"]
    for ernst, tekst in meldingen:
        print(f"  [{ernst:6s}] {tekst}")
    print()
    print(f"  {len(fouten)} fout(en), "
          f"{sum(1 for m in meldingen if m[0] == 'LET OP')} punt(en) om te bekijken.")

    for regel in analyse_bets(picks):
        print(regel)
    for regel in analyse_poorten(shadow, kand):
        print(regel)
    for regel in analyse_breekpunten(picks, v_eind):
        print(regel)

    print()
    print("DE REM — lees dit voordat je iets verzet", "=" * 78, sep="\n")
    print("  * Rendement over één week heeft een standaardfout van ongeveer 16 procentpunt.")
    print("    Een week op +10% of -20% is ruis. Alleen de kalibratiecijfers bewegen per week.")
    print("  * Er zijn hierboven negen vooraf vastgelegde uitsplitsingen gemaakt. Bij negen")
    print("    vergelijkingen hoort ongeveer een halve 'significante' uitkomst puur door kans.")
    print("  * Een reeks onder ~30 afgewikkelde gevallen zegt niets (§6d).")
    print("  * Deze run verzet nooit zelf een parameter. Staat er iets in dat om een besluit")
    print("    vraagt, dan gaat dat EEN keer naar de gebruiker en daarna niet opnieuw (§9).")
    return 1 if fouten else 0


# ------------------------------------------------------------------- zelftest

def _selftest() -> int:
    fouten = []

    def eis(naam, gekregen, verwacht):
        if gekregen != verwacht:
            fouten.append(f"{naam}: {gekregen!r} != {verwacht!r}")

    def dicht(naam, a, b, tol=1e-6):
        if abs(a - b) > tol:
            fouten.append(f"{naam}: {a!r} != {b!r}")

    # units: hele winst, heel verlies, en de halve uitkomst op een kwartlijn
    dicht("units winst", units({"odds": 2.5, "result": "won"}), 1.5)
    dicht("units verlies", units({"odds": 2.5, "result": "lost"}), -1.0)
    dicht("units half", units({"odds": 2.5, "result": "won", "settled_units": 0.75}), 0.75)

    # roi_stats op een handmatig narekenbaar geval: 2 winst @2.0, 2 verlies
    rows = [{"odds": 2.0, "result": "won"}, {"odds": 2.0, "result": "won"},
            {"odds": 2.0, "result": "lost"}, {"odds": 2.0, "result": "lost"}]
    s = roi_stats(rows)
    eis("roi n", s["n"], 4)
    eis("roi won", s["won"], 2)
    dicht("roi hit", s["hit"], 0.5)
    dicht("roi gemiddelde", s["roi"], 0.0)
    dicht("roi units", s["units"], 0.0)

    # void telt niet mee als beslist
    eis("void niet beslist", roi_stats([{"odds": 2.0, "result": "void"}])["n"], 0)
    eis("open niet beslist", roi_stats([{"odds": 2.0, "result": "pending"}])["n"], 0)

    # Wilson: 0/10 en 10/10 mogen niet buiten [0,1] vallen
    lo, hi = wilson(0, 10)
    eis("wilson 0/10 ondergrens", lo, 0.0)
    eis("wilson 0/10 bovengrens binnen 1", hi <= 1.0, True)
    lo, hi = wilson(10, 10)
    eis("wilson 10/10 bovengrens", hi, 1.0)
    dicht("wilson 5/10 symmetrisch", (wilson(5, 10)[0] + wilson(5, 10)[1]) / 2, 0.5, 1e-9)
    eis("wilson n=0", wilson(0, 0), (0.0, 0.0))

    # Brier: een perfecte en een maximaal foute voorspelling
    dicht("brier perfect", brier([{"my_prob": 1.0, "result": "won", "odds": 2.0}]), 0.0)
    dicht("brier maximaal fout", brier([{"my_prob": 1.0, "result": "lost", "odds": 2.0}]), 1.0)
    dicht("brier markt-arm",
          brier([{"implied_prob": 0.0, "result": "lost", "odds": 2.0}], markt=True), 0.0)

    # band
    eis("band onder", band(1.5, (1.7, 2.2), ("laag", "mid", "hoog")), "laag")
    eis("band boven", band(9.9, (1.7, 2.2), ("laag", "mid", "hoog")), "hoog")
    eis("band onbekend", band(None, (1.7,), ("a", "b")), "onbekend")

    # Run C mag NOOIT als gat worden gemeld (besluit 7 nov 2026)
    st = {("2026-11-02", "a"): {"completed": True, "artifact": "x"},
          ("2026-11-02", "b"): {"completed": True, "artifact": "x"}}
    m = integriteit(st, [], [], date(2026, 11, 2), date(2026, 11, 2))
    eis("geen FOUT bij ontbrekende Run C", [x for x in m if x[0] == "FOUT"], [])
    eis("Run C wel als INFO genoemd",
        any("Run C draait op verzoek" in t for _, t in m), True)

    # een ontbrekende Run A IS een fout
    m2 = integriteit({("2026-11-02", "b"): {"completed": True, "artifact": "x"}},
                     [], [], date(2026, 11, 2), date(2026, 11, 2))
    eis("ontbrekende Run A is een fout",
        any(x[0] == "FOUT" and "Run A" in x[1] for x in m2), True)

    # een niet-afgesloten voortgangsbestand is een fout
    m3 = integriteit({("2026-11-02", "a"): {"completed": False},
                      ("2026-11-02", "b"): {"completed": True, "artifact": "x"}},
                     [], [], date(2026, 11, 2), date(2026, 11, 2))
    eis("niet afgesloten run is een fout",
        any(x[0] == "FOUT" and "niet afgesloten" in x[1] for x in m3), True)

    # een te lang openstaande pick is een fout
    m4 = integriteit(st, [{"id": "oud", "result": "pending", "kickoff": "2026-10-01T12:00:00Z"}],
                     [], date(2026, 11, 2), date(2026, 11, 2))
    eis("oude openstaande pick is een fout",
        any(x[0] == "FOUT" and "nog open" in x[1] for x in m4), True)

    # dubbele schaduwrij in dezelfde categorie op dezelfde dag is een fout
    dub = [{"date": "2026-11-02", "match": "X – Y", "failed_gate": "edge", "result": "won",
            "odds": 2.0}] * 2
    m5 = integriteit(st, [], dub, date(2026, 11, 2), date(2026, 11, 2))
    eis("dubbele schaduwrij is een fout",
        any(x[0] == "FOUT" and "dubbel" in x[1] for x in m5), True)

    for f in fouten:
        print("FOUT:", f)
    print(f"{26 - len(fouten)} van 26 controles goed.")
    return 1 if fouten else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("actie", choices=["week", "integriteit", "bets", "poorten", "markten",
                                      "selftest"])
    ap.add_argument("--end", help="laatste dag van het venster, YYYY-MM-DD (default: gisteren)")
    ap.add_argument("--weeks", type=int, default=1)
    a = ap.parse_args()

    if a.actie == "selftest":
        return _selftest()

    eind = date.fromisoformat(a.end) if a.end else date.today() - timedelta(days=1)
    if a.actie == "week":
        return week_rapport(eind)

    picks, shadow = jsonl("picks.jsonl"), jsonl("shadow.jsonl")
    states = run_states()
    if a.actie == "integriteit":
        for ernst, tekst in integriteit(states, picks, shadow,
                                        eind - timedelta(days=7 * a.weeks - 1), eind):
            print(f"[{ernst:6s}] {tekst}")
    elif a.actie in ("bets", "markten"):
        print("\n".join(analyse_bets(picks)))
    elif a.actie == "poorten":
        print("\n".join(analyse_poorten(shadow, kandidaten(states))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
