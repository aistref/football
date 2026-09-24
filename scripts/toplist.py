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

# De oude edge-poort, sinds 20 sep 2026 een afkapping aan het eind in plaats van een poort vooraf
# (§5b). Hij bepaalt nog wel de grens zodra er méér kandidaten boven staan dan er regels in de
# lijst passen, en hij blijft als label per regel meelopen.
THRESH = {"FULL": 8.0, "LIGHT": 16.0}
MAX_LIGHT = 2          # MAX_LIGHT_IN_SHORTLIST uit §0
# Ondergrens voor §5b: onder dit niveau is een kandidaat niet eens een schaduwpick waard
# (de NEAR-drempel uit de analyse), en dus ook geen bet. Gelijk aan wat `ledger.py
# validate` afdwingt.
NEAR = {"FULL": 3.0, "LIGHT": 6.0}

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


def _poorten_open(r: dict) -> bool:
    """Alle poorten behalve `edge` open — afzonderlijk getoetst, niet via `failed_gate`.

    `failed_gate` geeft alleen de eerste dichte poort in de volgorde, en `edge` staat daar op
    plek twee. Een selectie met `failed_gate == "edge"` kan dus óók op context of robuustheid
    gesneuveld zijn. Op 20 sep 2026 stond Athletic Club - Alavés daardoor op het punt
    gepubliceerd te worden terwijl poort 7 dicht was (Alavés 4 dagen rust tegen 7). De analyse
    legt sindsdien de volledige poortstand vast in `poorten`.
    """
    g = r.get("poorten")
    if isinstance(g, dict):
        return all(v is True for k, v in g.items() if k != "edge")
    # Oudere run-states zonder poortkaart: dan is `failed_gate` het enige dat er is, en valt
    # niet uit te sluiten dat er een latere poort dicht stond. Niet publiceren.
    return False


def _publiceerbaar(r: dict, edge: float | None, tier: str) -> bool:
    """Mag deze selectie onder §5b meedingen naar een plek in de herijkte lijst?

    De zeven andere poorten blijven poorten — een selectie die op de koersband, de context, de
    robuustheid, de tweede methode, het datatier of de underdog-regel sneuvelde, hoort hier niet
    in. Wat overblijft is precies de groep die vóór 20 sep 2026 alleen op 8.0 strandde.

    ONDERGRENS. De eerste herdraai onder §5b zette bij Run B twee selecties met een NEGATIEVE
    edge in de lijst (Crewe -0.08, Pardubice -0.54) en bij beide runs een handvol onder de 3 pp.
    Dat is aanvullen, en §5 verbiedt dat met zoveel woorden: "zijn er minder gekwalificeerde bets
    dan MAX_SHORTLIST, lever er dan minder". De grens is niet nieuw verzonnen maar de bestaande
    NEAR-drempel: het niveau waaronder de routine een afgewezen kandidaat niet eens de moeite van
    het schaduwlogboek waard vindt. Wat te zwak is om te loggen, is te zwak om te spelen.
    `ledger.py validate` bewaakt dezelfde grens, dus rangorde en validatie spreken elkaar zo niet
    tegen.
    """
    return (r.get("failed_gate") in (None, "edge", "herijking")
            and _poorten_open(r)
            and isinstance(edge, (int, float)) and edge >= NEAR.get(tier, 3.0))


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
    # Run C is per ontwerp altijd LIGHT; daar zou de cap een vast plafond van twee bets per dag
    # zijn. Op 24 sep 2026 door de gebruiker voor Run C geschrapt (prompts/run-c.md).
    max_light = None if str(state.get("run", "")).upper() == "C" else MAX_LIGHT

    best_h: dict[str, dict] = {}
    best_r: dict[str, dict] = {}
    for c in _rows(state):
        e_h, e_r = _edges(c)
        tier = c["tier"]
        my_h, my_r = c.get("my_prob"), c.get("my_raw")
        key = c["match"]
        if isinstance(e_h, (int, float)) and isinstance(my_h, (int, float)):
            s = selection_score(e_h, my_h, tier)
            # De sterkste selectie van de wedstrijd wordt gekozen ONDER DE PUBLICEERBARE
            # (§1a: "van alle selecties die alle acht de poorten halen, publiceer je die met de
            # hoogste score"), niet eerst over alle kandidaten en daarna gefilterd.
            #
            # 20 sep 2026 — dat deed deze lus tot vandaag wél, en het kostte een bet. Bij
            # NEC Nijmegen – Go Ahead Eagles scoorde "1X2 — NEC wint" het hoogst (6.35) maar
            # stond poort 7 dicht (NEC mist selectiewaarde); `Over 3.5` stond op 5.86 met álle
            # poorten open. De oude volgorde koos het 1X2, `_pool` gooide het er daarna uit, en
            # de hele wedstrijd verdween — terwijl er een geldige selectie lag die hoger stond
            # dan twee bets die wél werden gepubliceerd. Poort 7 en 8 zijn kantgebonden en staan
            # bij `side = None` per definitie open (§1c), dus dit is geen randgeval: elke keer
            # dat een kantmarkt op de context sneuvelt kan de doelpuntenmarkt van diezelfde
            # wedstrijd er gewoon doorheen.
            if _publiceerbaar(c, e_h, tier) and (key not in best_h or s > best_h[key]["_score"]):
                best_h[key] = {**c, "_score": s, "_edge": e_h, "_prob": my_h,
                               "_gate": c.get("failed_gate")}
        if isinstance(e_r, (int, float)) and isinstance(my_r, (int, float)):
            s = selection_score(e_r, my_r, tier)
            if key not in best_r or s > best_r[key]["_score"]:
                best_r[key] = {**c, "_score": s, "_edge": e_r, "_prob": my_r,
                               "_gate": c.get("failed_gate_ruw", c.get("failed_gate"))}

    def _pool(d: dict) -> list[dict]:
        """§5b: de kandidaten waarvan alleen de drempel (of de herijking) hen tegenhield.

        De toets zelf staat in `_publiceerbaar` en is hierboven al per kandidaat toegepast; deze
        lus blijft staan zodat een aanroep met een zelfgebouwde `d` dezelfde grenzen krijgt.
        """
        return [r for r in d.values() if _publiceerbaar(r, r.get("_edge"), r["tier"])]

    def _cut(rows: list[dict]) -> tuple[list[dict], bool]:
        """Rangorde eerst, drempel alleen als er méér dan `n` boven staan (§5b stap 4-5)."""
        def _cap_light(xs: list[dict]) -> list[dict]:
            # MAX_LIGHT_IN_SHORTLIST uit §0: hoogstens twee regels op zwakke data, zodat de lijst
            # niet volloopt met omgerekende ploegen.
            uit, light = [], 0
            for r in xs:
                if r["tier"] != "FULL":
                    if max_light is not None and light >= max_light:
                        continue
                    light += 1
                uit.append(r)
                if len(uit) == n:
                    break
            return uit
        boven = [r for r in rows if r["_edge"] >= THRESH.get(r["tier"], 8.0)]
        if len(boven) > n:
            return _cap_light(sorted(boven, key=lambda r: -r["_score"])), True
        return _cap_light(sorted(rows, key=lambda r: -r["_score"])), False

    def top(d: dict, schaal: str) -> list[dict]:
        if schaal == "herijkt":
            rows, _ = _cut(_pool(d))
        else:
            rows = sorted(d.values(), key=lambda r: -r["_score"])[:n]
        out = []
        for r in rows:
            # Gepubliceerd is en blijft: alle poorten open op de HERIJKTE kans (§1). Een regel in
            # de ruwe lijst zonder open poort op die schaal is dus géén bet, ook al staat er op de
            # ruwe schaal niets in de weg. Dat verschil hier hard maken is belangrijker dan het
            # lijkt: anders leest de ruwe lijst als een tweede bettenlijst in plaats van als de
            # meting die ze is.
            # §5b (20 sep 2026): in de herijkte lijst IS de rangorde de publicatie. Alles wat de
            # andere zeven poorten haalde en in de bovenste `n` staat, wordt gespeeld; de drempel
            # is daar een label geworden. In de ruwe lijst verandert niets — die blijft de meting
            # die ze sinds 6 sep is.
            drempel = THRESH.get(r["tier"], 8.0)
            haalt_lat = isinstance(r["_edge"], (int, float)) and r["_edge"] >= drempel
            gepubliceerd = schaal == "herijkt"
            gate = r["_gate"]
            if schaal == "ruw":
                if gate is None and not (bool(r.get("bet_beide")) and r.get("failed_gate") is None):
                    stop = GATE_LABEL.get(r.get("failed_gate"), str(r.get("failed_gate")))
                    status = f"zou een bet zijn geweest — nu tegengehouden door: {stop}"
                else:
                    status = GATE_LABEL.get(gate, str(gate))
            elif haalt_lat:
                status = f"BET — en haalt ook de lat van {drempel:.1f} pp"
            else:
                status = f"BET op rangorde — onder de lat van {drempel:.1f} pp (§5b)"
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
    ap.add_argument("--run", required=True, choices=["a", "b", "c", "A", "B", "C"])
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
