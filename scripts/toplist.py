"""De dagelijkse top-N, twee keer: mét de herijking van §1g en zonder.

Toegevoegd 6 september 2026, op verzoek van de gebruiker. Aanleiding: de herijking maakt
sinds 5 sep ongeveer tien procentpunt van elke kansschatting af, en op de eerste dag dat ze
draaide leverde dat nul bets op waar de oude regels er vier hadden gegeven. Dan is "nul bets"
een correcte uitkomst maar een oncontroleerbare: je ziet niet wát er is afgevallen en je kunt
niet nagaan of de correctie klopt.

Deze module maakt dat zichtbaar en meetbaar. Ze doet drie dingen:

1. **Twee ranglijsten per run**, allebei `MAX_SHORTLIST` lang (3 op ma–do, 5 op vr–zo, precies
   de bestaande parameter uit §0). De ene rangschikt op `my_prob` ná de herijking, de andere op
   `my_raw` ervóór. Dezelfde weegregel voor beide: `selection_score` uit §5.
2. **Eén regel per wedstrijd**, want de 0-of-1-bet-regel van §1 geldt hier net zo goed. Dezelfde
   mening in vier markten is één bevinding, geen vier — anders vult één wedstrijd de hele lijst.
3. **De ruwe lijst is een meting, geen tip.** Elke selectie die zonder de herijking een bet zou
   zijn geweest en het mét de herijking niet is, gaat als schaduwpick naar `data/shadow.jsonl`
   met `failed_gate = "herijking"`, en wordt daar net zo afgerekend als elke andere kandidaat
   (§6d). Over enkele weken staat er dus een ROI onder "viel af op: herijking", en dán is met
   cijfers te zeggen of de correctie geld bespaart of alleen bets kost. Dat is dezelfde route
   waarlangs poort 5 en poort 8 worden herzien.

**Lees de ruwe lijst met §1g ernaast.** Die paragraaf meet op 552 afgerekende gevallen dat er
géén drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is
bij de hóógste geclaimde edge (−14.7% vanaf 8 pp). De ongecorrigeerde edge is precies de
grootheid waarvan dat is gemeten. De ruwe lijst laat dus zien wat de routine zonder correctie
zou hebben gespeeld — niet wat ze aanraadt. Het schaduwlogboek beslist wie er gelijk had.

Wat een bet is, verandert hierdoor niet. §1 blijft gelden: publiceren mag alleen als **alle**
poorten open staan, en de edge-poort meet op de herijkte `my_prob`. Binnen de speelbare koersband
(1.30-6.00, oftewel een kans tussen 16.7% en 76.9%) verlaagt de herijking een kans altijd, dus een
selectie die de herijkte drempel haalt, haalt hem ook ruw: "hij haalt beide modellen" is geen
versoepeling maar dezelfde regel, hardop gezegd.

Nagerekend met de fit van 6 sep 2026 (a=0.909, b=-0.445) verhoogt `recalibrate.apply` een kans
pas onder ongeveer 0.7% -- een koers van ruim 140, die poort 2 sowieso al afsluit. De
`bet_beide`-vlag controleert het niettemin per selectie: de fit loopt mee met het logboek en is
elke run een ander getal, en dan is "dit kan niet gebeuren" geen aanname om op te bouwen.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

try:                        # als pakket: `from scripts import toplist`
    from .model import selection_score
    from .ranking import max_shortlist
except ImportError:         # als los script: `python3 scripts/toplist.py`
    from model import selection_score          # type: ignore[no-redef]
    from ranking import max_shortlist          # type: ignore[no-redef]

STATE_DIR = Path("data/run-state")

# Volgorde waarin een selectie op een poort sneuvelt; gelijk aan die in de analyse, met
# `herijking` erbij als aparte uitkomst tussen `edge` en `tweede_methode`. Een selectie die
# alleen door de correctie van §1g afvalt, krijgt dat label in plaats van het vagere `edge`:
# "hij had genoeg edge, maar niet nadat ik mijn eigen optimisme eraf haalde" is een andere
# bevinding dan "hij had sowieso te weinig edge".
GATE_LABEL = {
    None: "BET",
    "odds": "koers buiten de band 1.30–6.00",
    "edge": "edge onder de drempel",
    "herijking": "alleen de herijking (§1g) hield hem tegen",
    "tweede_methode": "de twee methodes wijzen tegengesteld",
    "robuustheid": "edge draait om in het (shrink, rho)-grid",
    "context": "context spreekt de bet tegen (poort 7)",
    "underdog": "underdog-kant onder de ondergrens (poort 8)",
}


def _rows(state: dict) -> list[dict]:
    """Alle doorgerekende selecties van een run, plat, met de wedstrijd erbij."""
    out = []
    for comp, entry in (state.get("competitions") or {}).items():
        if not isinstance(entry, dict):
            continue
        for match in entry.get("matches") or []:
            tier = match.get("tier")
            if tier not in ("FULL", "LIGHT"):
                continue                      # NONE heeft geen kansbron, dus geen kandidaat
            for c in match.get("all_candidates") or []:
                if not isinstance(c, dict) or not isinstance(c.get("odds"), (int, float)):
                    continue
                out.append({**c, "competition": comp, "match": match.get("match"),
                            "kickoff_nl": match.get("kickoff_nl"), "tier": tier,
                            "bet": bool(match.get("bet"))})
    return out


def _edges(c: dict) -> tuple[float | None, float | None]:
    """(herijkte edge, ruwe edge) in procentpunten, of None waar het niet te bepalen is."""
    imp = c.get("implied")
    e_h = c.get("edge_pp")
    e_r = c.get("edge_raw")
    if e_r is None and isinstance(c.get("my_raw"), (int, float)) and isinstance(imp, (int, float)):
        e_r = round((c["my_raw"] - imp) * 100, 2)      # terugval voor oudere run-states
    return e_h, e_r


def build(state: dict, n: int | None = None) -> dict:
    """Twee ranglijsten van elk `n` regels: `herijkt` en `ruw`.

    `n` is standaard `MAX_SHORTLIST` voor de dag van de run — 3 op ma–do, 5 op vr–zo.
    Per wedstrijd komt er hoogstens één regel in elke lijst (§1, 0-of-1-bet), en dat is de
    selectie met de hoogste `selection_score` op díe schaal. De twee lijsten kunnen dus een
    andere markt van dezelfde wedstrijd noemen, en dat is geen fout: de weegregel telt de kans
    mee, en die kans is precies wat de herijking verandert.
    """
    if n is None:
        n = max_shortlist(date.fromisoformat(state["date"]))

    best_h: dict[str, dict] = {}
    best_r: dict[str, dict] = {}
    for c in _rows(state):
        e_h, e_r = _edges(c)
        tier = c["tier"]
        my_h, my_r = c.get("my_prob"), c.get("my_raw")
        key = c["match"]
        if isinstance(e_h, (int, float)) and isinstance(my_h, (int, float)):
            s = selection_score(e_h, my_h, tier)
            if key not in best_h or s > best_h[key]["_score"]:
                best_h[key] = {**c, "_score": s, "_edge": e_h, "_prob": my_h,
                               "_gate": c.get("failed_gate")}
        if isinstance(e_r, (int, float)) and isinstance(my_r, (int, float)):
            s = selection_score(e_r, my_r, tier)
            if key not in best_r or s > best_r[key]["_score"]:
                best_r[key] = {**c, "_score": s, "_edge": e_r, "_prob": my_r,
                               "_gate": c.get("failed_gate_ruw", c.get("failed_gate"))}

    def top(d: dict, schaal: str) -> list[dict]:
        rows = sorted(d.values(), key=lambda r: -r["_score"])[:n]
        out = []
        for r in rows:
            # Gepubliceerd is en blijft: alle poorten open op de HERIJKTE kans (§1). Een regel in
            # de ruwe lijst zonder open poort op die schaal is dus géén bet, ook al staat er op de
            # ruwe schaal niets in de weg. Dat verschil hier hard maken is belangrijker dan het
            # lijkt: anders leest de ruwe lijst als een tweede bettenlijst in plaats van als de
            # meting die ze is.
            gepubliceerd = bool(r.get("bet_beide")) and r.get("failed_gate") is None
            gate = r["_gate"]
            if schaal == "ruw" and gate is None and not gepubliceerd:
                stop = GATE_LABEL.get(r.get("failed_gate"), str(r.get("failed_gate")))
                status = f"zou een bet zijn geweest — nu tegengehouden door: {stop}"
            elif gepubliceerd:
                status = "BET — gepubliceerd"
            else:
                status = GATE_LABEL.get(gate, str(gate))
            out.append({
                "match": r["match"], "competition": r["competition"], "kickoff_nl": r["kickoff_nl"],
                "tier": r["tier"], "market": r["market"], "selection": r["selection"],
                "odds": r["odds"], "odds_source": r.get("odds_source"),
                "prob": round(r["_prob"], 4), "edge_pp": round(r["_edge"], 2),
                "score": round(r["_score"], 3),
                "failed_gate": gate, "status": status,
                "is_bet": gepubliceerd,
                "zou_bet_zijn_ruw": bool(r.get("bet_ruw")),
            })
        return out

    return {"n": n, "date": state.get("date"), "run": state.get("run"),
            "herijkt": top(best_h, "herijkt"), "ruw": top(best_r, "ruw"),
            "alleen_herijking": sum(1 for c in _rows(state)
                                    if c.get("failed_gate") == "herijking")}


def load(run: str, day: date) -> dict:
    p = STATE_DIR / f"{day.isoformat()}-run-{run.lower()}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _fmt(rows: list[dict], titel: str) -> str:
    if not rows:
        return f"\n{titel}\n  (geen enkele doorgerekende selectie)\n"
    out = [f"\n{titel}"]
    for i, r in enumerate(rows, 1):
        vlag = "  <-- BET" if r["is_bet"] else ""
        out.append(f"  {i}. {r['match']} · {r['kickoff_nl']} · {r['tier']}")
        out.append(f"     {r['market']} — {r['selection']} @ {r['odds']:.2f}")
        out.append(f"     kans {r['prob']*100:.1f}%  edge {r['edge_pp']:+.2f} pp  "
                   f"score {r['score']:.3f}  |  {r['status']}{vlag}")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, choices=["a", "b", "A", "B"])
    ap.add_argument("--date", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    day = date.fromisoformat(a.date)
    res = build(load(a.run, day), a.n)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return
    print(f"TOP {res['n']} — Run {res['run']} {res['date']}")
    print(_fmt(res["herijkt"], f"MET de herijking (§1g) — dit is de lijst waarop bets worden bepaald"))
    print(_fmt(res["ruw"], f"ZONDER de herijking — wat de routine vóór 5 sep 2026 zou hebben gezien"))
    n_bet = sum(r["is_bet"] for r in res["herijkt"])
    n_raw = sum(r["zou_bet_zijn_ruw"] and not r["is_bet"] for r in res["ruw"])
    print(f"Gepubliceerd: {n_bet} bet(s) — die haalden beide modellen. In deze top {res['n']} "
          f"zou{'' if n_raw == 1 else 'den'} er {n_raw} zonder de herijking wél door zijn gegaan; "
          f"over de hele run {res['alleen_herijking']} selectie(s) die alleen op §1g sneuvelden.")
    print("De ruwe lijst is een meting, geen tip: elke selectie die alleen door de herijking is")
    print("tegengehouden gaat als schaduwpick naar data/shadow.jsonl en wordt daar afgerekend.")


if __name__ == "__main__":
    main()
