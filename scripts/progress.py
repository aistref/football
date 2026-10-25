#!/usr/bin/env python3
"""Voortgangsbestand per run: overleeft een onderbreking (bv. een Claude-gebruikslimiet).

Zonder dit begint een hervatte run altijd weer bij wedstrijd 1, ook als hij al 25 van de 30 klaar
had. Het voortgangsbestand wordt tijdens Stage 4/5 na elke afgeronde wedstrijd/competitie
gecommit en gepusht — pas dát maakt hervatten mogelijk, want de container die de sessie draaide
is weg zodra de limiet toeslaat; alleen wat gepusht is overleeft.

    python3 scripts/progress.py show --run A --date 2026-08-08
    python3 scripts/progress.py reset --run A --date 2026-08-08   # forceer een verse start

Vanuit code (tijdens een run):

    from scripts.progress import load_or_start, save, is_done, mark

    state = load_or_start("A", date.today())
    if state["completed"]:
        raise SystemExit("deze run is vandaag al afgerond")
    for name in runlijst:
        if is_done(state, name):
            continue          # al gedaan vóór de onderbreking — niet opnieuw
        ... analyseer competitie `name` ...
        mark(state, name, resultaat)
        save(state)            # commit + push dit bestand meteen, niet pas aan het eind

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "data" / "run-state"


def _path(run_id: str, day: date) -> Path:
    return STATE_DIR / f"{day.isoformat()}-run-{run_id.lower()}.json"


# Welke omgevingsvariabelen de SESSIE identificeren, grofste eenheid eerst. De eenheid die telt is
# "wat er omvalt als de gebruikslimiet toeslaat": de container. Een subagent draait in dezelfde
# container maar kan een eigen sessie-id hebben, dus de container staat bewust vóór de sessie.
_SESSIE_VARIABELEN = (
    "CLAUDE_CODE_CONTAINER_ID",
    "CLAUDE_CODE_REMOTE_SESSION_ID",
    "CLAUDE_CODE_SESSION_ID",
)


def session_id() -> tuple[str, str]:
    """(id, bron) van de sessie waarin deze aanroep draait.

    Stabiel over álle processen binnen één run — en elke run bestaat uit losse processen, want
    Stage 1, de analyse, het publiceren en het afsluiten zijn aparte scripts. Verandert alleen als
    de sessie zelf verandert, en dát is precies wat een hervatting is.

    Lukt het niet, dan is de uitkomst `("onbekend", ...)` en **niet** een waarde per proces. Dat is
    met opzet de onderschattende kant: alle aanroepen vallen dan samen tot één sessie, dus een
    echte hervatting wordt gemist in plaats van dat er een verzonnen hervatting bij komt. Zie
    `_registreer_sessie` voor waarom die richting de juiste is.
    """
    for naam in _SESSIE_VARIABELEN:
        waarde = (os.environ.get(naam) or "").strip()
        if waarde:
            return waarde, f"omgevingsvariabele {naam}"
    # Terugval zonder die variabelen: de identiteit van de draaiende kernel. Let op dat een
    # container de boot_id van de HOST kan zien; dan zijn twee sessies op dezelfde host niet te
    # onderscheiden en wordt een hervatting gemist — weer de onderschattende kant.
    if not os.environ.get("_PROGRESS_GEEN_KERNEL"):
        # `_PROGRESS_GEEN_KERNEL` bestaat alleen voor `selftest`, om het geval "sessie niet te
        # bepalen" na te maken op een machine waar /proc er wél is.
        try:
            waarde = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
            if waarde:
                return waarde, "kernel boot_id (terugval)"
        except OSError:
            pass
        try:
            for regel in Path("/proc/stat").read_text().splitlines():
                if regel.startswith("btime "):
                    return regel.split()[1], "kernel btime (terugval)"
        except OSError:
            pass
    return "onbekend", "niet te bepalen"


def _registreer_sessie(state: dict) -> dict:
    """Zet de huidige sessie in `state["sessies"]` en leid `resumed_count` daaruit af.

    **Dit verving op 16 okt 2026 een teller die het verkeerde mat.** `load_or_start` deed
    `state["resumed_count"] += 1` bij elke aanroep op een bestaand bestand, en één run roept hem
    meerdere keren aan: Stage -1 aan het begin, daarna elk script dat de state nodig heeft. De
    teller mat dus het aantal AANROEPEN en niet het aantal HERVATTINGEN. Op 16 oktober stond hij
    aan het eind van een ononderbroken Run B op 3; over `data/run-state/` staan 88 bestanden met
    een waarde boven nul en vrijwel geen van die runs is werkelijk hervat.

    Waarom dat meer is dan een onzuiver cijfer: §3 Stage -1 van `prompts/_shared-rules.md` eist dat
    een run bij `resumed_count > 0` bovenaan het runrapport *"hervat om HH:MM na onderbreking, N
    competities al gedaan"* meldt. Dat is dan een onware mededeling, en een teller die te hoog
    staat klaagt niet — dezelfde stille faalvorm als het Serie B-id (29 sep),
    `calibration.py settle` (30 sep) en de verhuisde BetExplorer-slug (16 okt).

    De telling is nu **afgeleid in plaats van opgeteld**: `resumed_count = len(sessies) - 1`. Tien
    aanroepen binnen dezelfde sessie voegen niets toe, want het id staat er al in; een nieuwe
    sessie die hetzelfde bestand oppakt voegt één id toe en dát is een hervatting. Daarmee is de
    functie ook idempotent, wat een losse eis van zichzelf is: een runscript mag de state zo vaak
    openen als het wil.

    Twee dingen die bewust de onderschattende kant op vallen:

    1. **Is de sessie niet te bepalen** (`session_id()` geeft `"onbekend"`), dan vallen alle
       aanroepen samen tot één sessie en blijft de telling op 0. Een echte hervatting wordt dan
       gemist. Dat is de juiste richting: §3 Stage -1 heeft liever geen melding dan een onware, en
       het bestand zelf laat via `competitions` nog altijd zien wat er al gedaan was.
    2. **Bij een bestand van vóór deze fix** begint de lijst leeg en wordt de oude waarde bewaard
       onder `resumed_count_voor_de_fix`. Een zo'n bestand dat werkelijk hervat werd leest daarna
       eenmalig 0. Dat is de prijs van de overgang, in dezelfde richting, en het oude getal is niet
       weggegooid — de bestanden van vóór 16 okt 2026 blijven dus na te lezen als wat ze waren:
       een telling van aanroepen.
    """
    sid, bron = session_id()
    sessies = state.get("sessies")
    if sessies is None:
        sessies = []
        if state.get("resumed_count"):
            state["resumed_count_voor_de_fix"] = state["resumed_count"]
    if sid not in sessies:
        sessies.append(sid)
    state["sessies"] = sessies
    state["sessie_bron"] = bron
    state["resumed_count"] = max(0, len(sessies) - 1)
    return state


def new_state(run_id: str, day: date) -> dict:
    return _registreer_sessie({
        "run": run_id.upper(),
        "date": day.isoformat(),
        "resumed_count": 0,
        "sessies": [],       # zie `_registreer_sessie`: hieruit volgt resumed_count
        "competitions": {},  # naam -> {"status": ..., "matches": [...]}
        "completed": False,
        "duur": {"gestart": datetime.now(timezone.utc).isoformat(), "afgerond": None,
                 "minuten": None},
    })


def load(run_id: str, day: date) -> dict | None:
    p = _path(run_id, day)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def load_or_start(run_id: str, day: date) -> dict:
    """Geeft het bestaande voortgangsbestand van vandaag terug, of maakt een nieuwe aan.

    Is het bestand door een ANDERE sessie aangelegd (dus is dit een hervatting na onderbreking)?
    Dan telt dat en hoort het in het runrapport — een hervatte run is geen storing, maar wel iets
    om te vermelden (§3 Stage -1).

    **Deze functie is idempotent en dat is sinds 16 okt 2026 ook waar.** Tot die datum verhoogde
    ze `resumed_count` bij elke aanroep, waardoor één ononderbroken run op 3 uitkwam; de telling
    loopt nu via `_registreer_sessie`, dat de sessie-id in een lijst zet. Lees daar waarom dat
    nodig was en waar de grenzen van de nieuwe telling liggen.
    """
    state = load(run_id, day)
    if state is None:
        return new_state(run_id, day)
    if not state.get("completed"):
        _registreer_sessie(state)
    return state


def save(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _path(state["run"], date.fromisoformat(state["date"])).write_text(
        json.dumps(state, ensure_ascii=False, indent=1))


def is_done(state: dict, competition: str) -> bool:
    return competition in state["competitions"]


def mark(state: dict, competition: str, result: dict) -> None:
    """`result` bv. {"status": "GEANALYSEERD", "matches": [...]} of {"status": "GEEN WEDSTRIJD"}."""
    state["competitions"][competition] = result


def mark_completed(state: dict) -> None:
    """Sluit de run af en leg vast hoe lang hij erover deed.

    De looptijd staat hier sinds 5 sep 2026, en niet als sierlijkheid. `MAX_DEEP_ANALYSES` is een
    **tijds**grens: de gebruiker zet 's ochtends tussen 07:00 en 08:00 in, dus de rapporten moeten
    om 06:30 klaar zijn. Op diezelfde dag is de cap van 30/35 naar 40/55 gegaan omdat afgekapte
    duels aantoonbaar net zo vaak een bet opleveren als de rest. Of die verhoging binnen het
    tijdvenster past, is met dit veld te zien in plaats van te raden — en dat is precies de
    discipline die de rest van dit bestand ook oplegt.
    """
    state["completed"] = True
    duur = state.setdefault("duur", {})
    nu = datetime.now(timezone.utc)
    duur["afgerond"] = nu.isoformat()
    start = duur.get("gestart")
    if start:
        try:
            duur["minuten"] = round(
                (nu - datetime.fromisoformat(start)).total_seconds() / 60, 1)
        except ValueError:
            duur["minuten"] = None


def is_completed(state: dict | None) -> bool:
    return bool(state and state.get("completed"))


def _cmd_show(args: argparse.Namespace) -> int:
    state = load(args.run, date.fromisoformat(args.date))
    if state is None:
        print(f"Geen voortgangsbestand voor run {args.run} op {args.date}.")
        return 0
    done = [n for n, r in state["competitions"].items() if r.get("status") == "GEANALYSEERD"]
    print(f"Run {state['run']} — {state['date']}")
    if "sessies" in state:
        print(f"  compleet: {state['completed']}   hervat: {state['resumed_count']}x "
              f"({len(state['sessies'])} sessie(s), bron: {state.get('sessie_bron', '?')})")
    else:
        # Bestand van vóór 16 okt 2026: de teller gaf toen het aantal AANROEPEN en niet het aantal
        # hervattingen, dus hij hoort niet als hervattingen gelezen te worden.
        print(f"  compleet: {state['completed']}   "
              f"aanroepen (NIET hervattingen): {state['resumed_count']}x — bestand van vóór de "
              f"fix van 16 okt 2026, zie progress._registreer_sessie")
    print(f"  competities verwerkt: {len(state['competitions'])}  (waarvan geanalyseerd: {len(done)})")
    for name, result in state["competitions"].items():
        n_matches = len(result.get("matches", []))
        print(f"    {name:32s} {result['status']:20s} {n_matches or ''}")
    return 0


ALL_MARKETS = ("1X2", "DC", "DNB", "AH", "OU", "BTTS")
"""De zes markten uit _shared-rules.md §1. `markets_checked` in het voortgangsbestand hoort deze
namen te gebruiken; `verify` rekent af op deze lijst."""


def _cmd_verify(args: argparse.Namespace) -> int:
    """Controleer dat elke geanalyseerde wedstrijd alle zes markten heeft gehad.

    Bestaansreden (14 aug 2026). §1 schreef al vanaf het begin voor om 1X2, Double Chance, Draw No
    Bet, Asian Handicap, Over/Under en BTTS langs te gaan, en dat gebeurde een week lang niet: van
    de eerste 15 picks waren er 11 een 1X2 en 0 een handicap. Niemand merkte het, omdat er nergens
    werd vastgelegd wat er per wedstrijd was bekeken — alleen wat eruit kwam. Een regel die niemand
    kan nalopen is geen regel maar een voornemen.

    Dit is met opzet een controle op de **administratie**, niet op de uitkomst: nul bets is een
    geldige uitkomst, een wedstrijd waarbij vier markten niet eens zijn opgezocht niet.
    """
    state = load(args.run, date.fromisoformat(args.date))
    if state is None:
        print(f"Geen voortgangsbestand voor run {args.run} op {args.date}.")
        return 1

    gaten: list[str] = []
    gedekt = 0
    overgeslagen = {"NONE": 0, "afgekapt": 0}
    for comp, block in state["competitions"].items():
        if not isinstance(block, dict):
            continue
        if block.get("status") != "GEANALYSEERD":
            # 25 okt 2026 (Run B) — EEN COMPETITIE DIE NIET `GEANALYSEERD` IS WERD HIER VOLLEDIG
            # OVERGESLAGEN, OOK IN DE TELLING ERONDER. Er valt bij zo'n competitie niets te
            # controleren (geen kansbron of door de cap afgekapt, dus geen markt om te bekijken),
            # maar de staart van deze uitvoer zegt hoeveel duels zijn overgeslagen en die telling
            # klopte dan niet: vandaag staan vier duels op tier NONE en meldde hij er drie, omdat
            # het vierde (Osijek – Rudes) in een competitie zat die als geheel buiten de dekking
            # viel. Dat is precies de soort administratie die deze controle zelf wil voorkomen —
            # een getal dat niet optelt tot de dag. De duels worden daarom geteld en niet
            # bekeken; `gaten` blijft leeg voor deze competities.
            for match in block.get("matches", []):
                if not isinstance(match, dict):
                    continue
                if match.get("tier") == "NONE":
                    overgeslagen["NONE"] += 1
                else:
                    overgeslagen["afgekapt"] += 1
            continue
        for match in block.get("matches", []):
            if not isinstance(match, dict):
                continue
            naam = match.get("match", "?")
            if match.get("tier") == "NONE":
                overgeslagen["NONE"] += 1
                continue  # geen kansbron, dus geen markt om te bekijken
            if match.get("afgekapt"):
                # Buiten MAX_DEEP_ANALYSES gevallen (§3, Stage 4). Zo'n duel is niet
                # doorgerekend, dus er valt geen markt te bekijken — net als bij tier NONE.
                # Dit is geen stille uitzondering: de afkapping staat met naam en aantal in het
                # runrapport en in `parameters.afkapping`, en het aantal staat hieronder.
                overgeslagen["afgekapt"] += 1
                continue
            checked = match.get("markets_checked")
            if not checked:
                gaten.append(f"{comp} · {naam}: geen markets_checked vastgelegd")
                continue
            mist = [m for m in ALL_MARKETS if m not in checked]
            if mist:
                gaten.append(f"{comp} · {naam}: niet bekeken: {', '.join(mist)}")
            else:
                gedekt += 1

    staart = (f" Overgeslagen: {overgeslagen['NONE']} zonder kansbron (tier NONE), "
              f"{overgeslagen['afgekapt']} afgekapt door MAX_DEEP_ANALYSES."
              if any(overgeslagen.values()) else "")
    if not gaten:
        print(f"Alle {gedekt} geanalyseerde wedstrijd(en) hebben alle zes markten gehad.{staart}")
        return 0
    print(f"{len(gaten)} wedstrijd(en) met onvolledige marktdekking "
          f"({gedekt} wel volledig).{staart}\n")
    for regel in gaten:
        print(f"  {regel}")
    print("\nZie _shared-rules.md §1: 'Ga alle markten langs'. Een markt waarvoor geen odds te")
    print("vinden waren telt ook als bekeken — noteer hem dan met de reden, niet als gat.")
    return 1


def _cmd_selftest(args: argparse.Namespace) -> int:
    """Bewijst de drie gevallen waar de fix van 16 okt 2026 over gaat. Geen netwerk, geen repo.

    Zonder deze test is "de teller telt nu sessies" een bewering: de oude fout gaf namelijk geen
    foutmelding en viel pas op doordat iemand het getal nalas. Precies de faalvorm die een
    controle verdient in plaats van een goede bedoeling.
    """
    import tempfile

    global STATE_DIR
    echte_dir, echte_env = STATE_DIR, dict(os.environ)
    mislukt: list[str] = []

    def eis(voorwaarde: bool, wat: str) -> None:
        print(f"  {'OK  ' if voorwaarde else 'FOUT'} {wat}")
        if not voorwaarde:
            mislukt.append(wat)

    def zet_sessie(waarde: str | None) -> None:
        for naam in _SESSIE_VARIABELEN:
            os.environ.pop(naam, None)
        if waarde is not None:
            os.environ["CLAUDE_CODE_CONTAINER_ID"] = waarde

    try:
        with tempfile.TemporaryDirectory() as tmp:
            STATE_DIR = Path(tmp)
            dag = date(2026, 10, 16)

            # 1. Eén sessie, vier aanroepen — dit is het geval dat op 16 okt 3 opleverde.
            zet_sessie("sessie-1")
            state = load_or_start("b", dag)
            save(state)
            for _ in range(3):
                state = load_or_start("b", dag)
                save(state)
            eis(state["resumed_count"] == 0,
                f"vier aanroepen in één sessie -> resumed_count 0 (kreeg {state['resumed_count']})")
            eis(state["sessies"] == ["sessie-1"], f"één sessie-id vastgelegd ({state['sessies']})")

            # 2. Een tweede sessie pakt hetzelfde bestand op: DAT is een hervatting.
            zet_sessie("sessie-2")
            state = load_or_start("b", dag)
            save(state)
            eis(state["resumed_count"] == 1,
                f"tweede sessie -> resumed_count 1 (kreeg {state['resumed_count']})")
            state = load_or_start("b", dag)
            save(state)
            eis(state["resumed_count"] == 1,
                "nog een aanroep binnen die tweede sessie verhoogt niets "
                f"(kreeg {state['resumed_count']})")
            zet_sessie("sessie-3")
            state = load_or_start("b", dag)
            save(state)
            eis(state["resumed_count"] == 2,
                f"derde sessie -> resumed_count 2 (kreeg {state['resumed_count']})")

            # 3. Een afgeronde run wordt niet meer geteld (de run stopt dan toch meteen).
            mark_completed(state)
            save(state)
            zet_sessie("sessie-4")
            state = load_or_start("b", dag)
            eis(state["resumed_count"] == 2,
                f"afgeronde run telt geen nieuwe sessie (kreeg {state['resumed_count']})")

            # 4. Niet te bepalen sessie: alles valt samen, de telling blijft 0 (onderschattend).
            zet_sessie(None)
            os.environ["_PROGRESS_GEEN_KERNEL"] = "1"
            dag2 = date(2026, 10, 17)
            onbekend_sid, _ = session_id()
            state = load_or_start("b", dag2)
            save(state)
            state = load_or_start("b", dag2)
            save(state)
            eis(state["resumed_count"] == 0,
                "zonder sessie-id vallen aanroepen samen in plaats van op te tellen "
                f"(kreeg {state['resumed_count']})")
            eis(state["sessies"] == [onbekend_sid],
                f"één id, niet één per proces ({state['sessies']})")

            # 5. Migratie: een bestand van vóór de fix houdt zijn oude getal apart.
            dag3 = date(2026, 10, 18)
            oud = new_state("b", dag3)
            oud["resumed_count"] = 3
            oud.pop("sessies")
            oud.pop("sessie_bron", None)
            save(oud)
            zet_sessie("sessie-na-migratie")
            state = load_or_start("b", dag3)
            eis(state["resumed_count"] == 0,
                f"bestand van vóór de fix start op 0 (kreeg {state['resumed_count']})")
            eis(state.get("resumed_count_voor_de_fix") == 3,
                f"het oude getal is bewaard ({state.get('resumed_count_voor_de_fix')})")
    finally:
        STATE_DIR = echte_dir
        os.environ.clear()
        os.environ.update(echte_env)

    if mislukt:
        print(f"\n{len(mislukt)} controle(s) mislukt.")
        return 1
    print("\nAlle controles geslaagd.")
    return 0


def _cmd_reset(args: argparse.Namespace) -> int:
    p = _path(args.run, date.fromisoformat(args.date))
    if p.exists():
        p.unlink()
        print(f"Voortgangsbestand voor run {args.run} op {args.date} verwijderd — volgende start is vers.")
    else:
        print("Er was geen voortgangsbestand om te verwijderen.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    show = sub.add_parser("show", help="toon de voortgang van een run")
    show.add_argument("--run", required=True, choices=["A", "B", "C", "a", "b", "c"])
    show.add_argument("--date", required=True, help="YYYY-MM-DD")
    show.set_defaults(func=_cmd_show)

    verify = sub.add_parser("verify", help="controleer of elke wedstrijd alle zes markten heeft gehad")
    verify.add_argument("--run", required=True, choices=["A", "B", "C", "a", "b", "c"])
    verify.add_argument("--date", required=True, help="YYYY-MM-DD")
    verify.set_defaults(func=_cmd_verify)

    selftest = sub.add_parser("selftest", help="controleer de hervattingstelling (geen netwerk)")
    selftest.set_defaults(func=_cmd_selftest)

    reset = sub.add_parser("reset", help="verwijder het voortgangsbestand, forceer een verse start")
    reset.add_argument("--run", required=True, choices=["A", "B", "C", "a", "b", "c"])
    reset.add_argument("--date", required=True, help="YYYY-MM-DD")
    reset.set_defaults(func=_cmd_reset)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
