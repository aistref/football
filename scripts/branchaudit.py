#!/usr/bin/env python3
"""Stage -2 als gereedschap — staat er op een andere tak werk dat `main` nooit heeft gekregen?

Waarom dit bestaat (29 sep 2026). §3 Stage -2 eist aan het begin van elke run dat alle takken
worden nagelopen op werk dat hier nog niet is, en sinds 27 september eist het dat expliciet voor
**alle vijf de logboeken** en **per record op de inhoud** in plaats van op de commitgraaf. Die
controle is drie ochtenden op rij met de hand geschreven als wegwerpscript (27, 28 en 29 september),
en het runrapport van 28 september noemde dat zelf een probleem: een controle die elke dag opnieuw
wordt getypt, is elke dag opnieuw een andere controle.

Dat is geen theoretisch bezwaar. De twee vondsten die deze regel hebben opgeleverd, zijn allebei
gedaan doordat iemand nét iets grondiger keek dan de dag ervoor:

- **27 sep 2026** — Run A controleerde alleen de pick-id's, vond niets en concludeerde dat er niets
  te verenigen viel. Run B liep daarna alle vijf de logboeken na en vond in `data/shadow.jsonl`
  vijf rijen van Run A van 19 september die `main` nooit had gekregen.
- **28 sep 2026** — dezelfde vergelijking, nu vanaf het begin op alle vijf, vond er nog vier.

Beide keren ging het om een logboek dat een **script** bijwerkt (`shadow.jsonl`,
`calibration.jsonl`, `context-log.jsonl`) en niet om `picks.jsonl`. Dat is ook te begrijpen: de
gepubliceerde bets zijn het bestand dat elke run bewust aanraakt, dus het bestand dat het minst
vaak uiteenloopt.

    python3 scripts/branchaudit.py                      # alle takken tegen origin/main
    python3 scripts/branchaudit.py --ref HEAD           # tegen de werkkopie
    python3 scripts/branchaudit.py --json               # machineleesbaar, voor data/run-state/

**Twee dingen die dit script met opzet anders doet dan de naïeve versie.**

1. **Het vergelijkt op identiteit, niet op bytes.** Een regelvergelijking op de ruwe tekst wijst
   op 29 september 18 takken aan als afwijkend op `picks.jsonl`, en een vergelijking op `id` nul.
   Het verschil zit in records die `main` in **afgewikkelde** vorm heeft en de tak nog als
   `pending`: dezelfde meting, verder in de tijd. De byte-vergelijking is dus niet strenger maar
   luidruchtiger, en luidruchtige controles worden weggeklikt.
2. **Het zegt niets over de commitgraaf, en dat is de hele les van 27 september.** Tak
   `claude/zealous-edison-elu4ga` telde ná een `--unshallow` **0** eigen commits en zág er dus
   schoon uit, terwijl er vijf metingen op stonden die `main` niet had. `0 eigen commits` is een
   uitspraak over de graaf; alleen een vergelijking per record is een uitspraak over de metingen.
   In een **ondiepe** kloon is het nog erger: dan geeft `git diff main...<tak>` "no merge base" en
   lijken tientallen takken honderden eigen commits te hebben die er allemaal al in zitten.

**Wat dit script níet doet: mergen.** Het rapporteert alleen. De conflictregels van §3 Stage -2 zijn
per bestand verschillend — vereniging voor de logboeken, nieuwste versie voor de regels en de
scripts — en die keuze hoort bij de run, met het oog erop. Wat hier uitkomt is de lijst waarop die
keuze gemaakt wordt.

**Bekende, goedgekeurde afwijking.** `sources.oddspapi` staat op negen oudere takken en niet op
`main`. Dat is geen verlies maar een besluit: OddsPapi is op 30 aug 2026 verwijderd na de overstap
naar het 20K-creditplan (commit `f342894`, en `README.md`). Het script kent hem bij naam en meldt
hem als `bekend_besluit` in plaats van als vondst, zodat hij niet elke ochtend opnieuw als
afwijking moet worden uitgezocht — en zodat een échte afwijking in dat bestand wél opvalt.

Alleen de standaardbibliotheek.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

# ---------------------------------------------------------------------------
# Wat er per logboek de identiteit van een record is.
#
# De sleutel moet hetzelfde record op twee takken aan elkaar koppelen, óók als het op de ene tak
# al is afgewikkeld en op de andere nog `pending` staat. Daarom nooit het hele record, en nooit een
# veld dat de afwikkeling verandert (`result`, `settled_at`, `settled_score`).
# ---------------------------------------------------------------------------
JSONL_KEYS: dict[str, tuple[str, ...]] = {
    "data/picks.jsonl": ("id",),
    "data/shadow.jsonl": ("id",),
    "data/context-log.jsonl": ("id",),
    # calibration.jsonl heeft geen id-veld: één regel per (wedstrijd, markt, methode) per rundag.
    "data/calibration.jsonl": ("date", "run", "match", "market", "method"),
}

# Deze twee zijn geen regellogboeken maar geneste objecten; §3 eist ook daar vereniging, dus
# vergelijken we tot op het bladpad.
JSON_TREES: tuple[str, ...] = ("data/source-health.json", "data/coverage.json")

# Bladpaden die met opzet van `main` zijn verwijderd. Zie de docstring.
BEKENDE_BESLUITEN: dict[str, dict[str, str]] = {
    "data/source-health.json": {
        "sources.oddspapi": "OddsPapi is op 30 aug 2026 verwijderd na de overstap naar het "
                            "20K-creditplan (commit f342894, README). Besluit, geen verlies.",
    },
}

# Per-run-boekhouding, geen meting: dat de ene tak een ander `last_run`-stempel heeft dan de andere
# is geen afwijking om uit te zoeken.
GEEN_METING: dict[str, tuple[str, ...]] = {
    "data/source-health.json": ("last_run", "updated", "_merge_note"),
    "data/coverage.json": ("updated",),
}


class GitError(RuntimeError):
    pass


def _git(*args: str) -> str:
    r = subprocess.run(("git", *args), capture_output=True, text=True)
    if r.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def show(ref: str, path: str) -> str | None:
    """De inhoud van `path` op `ref`, of None als het bestand daar niet bestaat."""
    r = subprocess.run(("git", "show", f"{ref}:{path}"), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def branches(include_local: bool = False) -> list[str]:
    fmt = "%(refname:short)"
    refs = _git("branch", "-r", "--format", fmt).split()
    if include_local:
        refs += _git("branch", "--format", fmt).split()
    return [b for b in refs if "HEAD" not in b]


def _identity(obj: dict, fields: tuple[str, ...]):
    return obj[fields[0]] if len(fields) == 1 else tuple(obj.get(f) for f in fields)


def load_jsonl(text: str, fields: tuple[str, ...]) -> dict:
    """{identiteit: record}. Regels die niet te lezen zijn worden overgeslagen, niet geraden."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        try:
            out[_identity(obj, fields)] = obj
        except KeyError:
            continue
    return out


def leaf_paths(node, prefix: str = "") -> set[str]:
    """Alle bladpaden van een genest object, als 'a.b.c'. Lijsten gelden als blad."""
    out: set[str] = set()
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}{k}"
            out.add(path)
            out |= leaf_paths(v, path + ".")
    return out


def _negeer(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == p or path.startswith(p + ".") for p in prefixes)


def audit(ref: str = "origin/main", include_local: bool = False) -> dict:
    result: dict = {"ref": ref, "shallow": _git("rev-parse", "--is-shallow-repository").strip(),
                    "takken": 0, "logboeken": {}, "vondsten": 0}
    refs = [b for b in branches(include_local) if b not in (ref, ref.removeprefix("origin/"))]
    result["takken"] = len(refs)

    for path, fields in JSONL_KEYS.items():
        base_txt = show(ref, path)
        if base_txt is None:
            result["logboeken"][path] = {"fout": f"bestaat niet op {ref}"}
            continue
        base = load_jsonl(base_txt, fields)
        ontbreekt: dict = {}
        for b in refs:
            txt = show(b, path)
            if txt is None:
                continue
            for ident, obj in load_jsonl(txt, fields).items():
                if ident not in base:
                    ontbreekt.setdefault(str(ident), {"takken": [], "record": obj})
                    ontbreekt[str(ident)]["takken"].append(b)
        result["logboeken"][path] = {
            "sleutel": ".".join(fields), "records_op_ref": len(base),
            "ontbreekt": ontbreekt, "aantal_ontbreekt": len(ontbreekt),
        }
        result["vondsten"] += len(ontbreekt)

    for path in JSON_TREES:
        base_txt = show(ref, path)
        if base_txt is None:
            result["logboeken"][path] = {"fout": f"bestaat niet op {ref}"}
            continue
        base = leaf_paths(json.loads(base_txt))
        negeer = GEEN_METING.get(path, ())
        besluiten = BEKENDE_BESLUITEN.get(path, {})
        ontbreekt: dict = {}
        bekend: dict = {}
        for b in refs:
            txt = show(b, path)
            if txt is None:
                continue
            try:
                paths = leaf_paths(json.loads(txt))
            except json.JSONDecodeError:
                continue
            for p in paths - base:
                if _negeer(p, negeer):
                    continue
                besluit = next((v for k, v in besluiten.items() if _negeer(p, (k,))), None)
                doel = bekend if besluit else ontbreekt
                doel.setdefault(p, {"takken": [], "reden": besluit})
                doel[p]["takken"].append(b)
        result["logboeken"][path] = {
            "sleutel": "bladpaden", "records_op_ref": len(base),
            "ontbreekt": ontbreekt, "aantal_ontbreekt": len(ontbreekt),
            "bekend_besluit": bekend,
        }
        result["vondsten"] += len(ontbreekt)
    return result


def render(res: dict) -> str:
    lines = [f"STAGE -2 — alle takken vergeleken met {res['ref']}, per record op de inhoud",
             f"  {res['takken']} tak(ken) nagelopen · ondiepe kloon: {res['shallow']}",
             ""]
    for path, info in res["logboeken"].items():
        if "fout" in info:
            lines.append(f"  {path:32s} {info['fout']}")
            continue
        n = info["aantal_ontbreekt"]
        vlag = "VOLLEDIG" if n == 0 else f"{n} ONTBREEKT"
        lines.append(f"  {path:32s} {info['records_op_ref']:5d} op {res['ref']}"
                     f"  (sleutel: {info['sleutel']})  -> {vlag}")
        for ident, d in info["ontbreekt"].items():
            lines.append(f"       {ident}")
            lines.append(f"         staat op: {', '.join(d['takken'][:3])}"
                         + (f" (+{len(d['takken']) - 3})" if len(d["takken"]) > 3 else ""))
        # Eén regel per besluit, niet per bladpad: `sources.oddspapi` levert er anders zes.
        per_reden: dict[str, list[str]] = {}
        for ident, d in (info.get("bekend_besluit") or {}).items():
            per_reden.setdefault(d["reden"], []).append(ident)
        for reden, idents in per_reden.items():
            kort = min(idents, key=len)
            lines.append(f"       {kort} (+{len(idents) - 1} bladpad(en)) — bekend besluit, "
                         f"geen vondst")
            lines.append(f"         {reden}")
    lines.append("")
    if res["vondsten"] == 0:
        lines += ["Niets te verenigen: elk record dat op een tak staat, staat ook op "
                  f"{res['ref']}.",
                  "",
                  "LET OP wat dit NIET zegt. Dit is een uitspraak over de metingen, niet over de",
                  "commitgraaf — en dat is met opzet de enige uitspraak die telt (§3 Stage -2). Een",
                  "tak met 0 eigen commits kan metingen dragen die hier ontbreken, en in een ondiepe",
                  "kloon lijken tientallen takken eigen commits te hebben die er al in zitten."]
    else:
        lines += [f"{res['vondsten']} record(s) staan op een tak en niet op {res['ref']}.",
                  "",
                  "Verenig ze volgens de conflicttabel van §3 Stage -2: logboeken worden VERENIGD",
                  "(een pick die op één tak staat is een echte pick; een afgewikkelde regel wint van",
                  "pending), regels en scripts gaan op de NIEUWSTE versie. Dit script mergt niet —",
                  "die keuze hoort bij de run. Controleer daarna of picks.jsonl openstaande picks",
                  "bevat van een run die nooit is afgewikkeld: die horen bij Stage 0."]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="origin/main",
                    help="waarmee vergeleken wordt (standaard origin/main)")
    ap.add_argument("--include-local", action="store_true",
                    help="ook lokale takken meenemen, niet alleen origin/*")
    ap.add_argument("--json", action="store_true", help="machineleesbare uitvoer")
    args = ap.parse_args(argv)
    try:
        res = audit(args.ref, args.include_local)
    except GitError as e:
        print(f"fout: {e}", file=sys.stderr)
        return 2
    if args.json:
        # De volledige records zijn voor een run-state-blok te groot; alleen de identiteiten.
        slim = dict(res)
        slim["logboeken"] = {
            p: ({**i, "ontbreekt": {k: v["takken"] for k, v in i["ontbreekt"].items()}}
                if "ontbreekt" in i else i)
            for p, i in res["logboeken"].items()
        }
        print(json.dumps(slim, ensure_ascii=False, indent=1))
    else:
        print(render(res))
    return 1 if res["vondsten"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
