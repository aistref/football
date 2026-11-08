"""Tel de AI-tells, de tussenkopjes en de herhaalde vormen in de voorbeschouwingen van een run.

Hoort bij §6c, "Geen tussenkopjes en minder AI-tells" (7 nov 2026, op verzoek van de gebruiker,
bindend vanaf 8 nov 2026). Die regel is op de vijf voorbeschouwingen van 7 november gemeten, en
dit script is de meting zelf, zodat een volgende run niet op zijn gevoel hoeft af te gaan.

    python3 scripts/prosecheck.py --date 2026-11-08 --run a
    python3 scripts/prosecheck.py selftest        # geen netwerk, geen repo nodig

**Dit is een hulpmiddel en geen poort.** Anders dan `progress.py verify` — dat groen moet zijn
vóór de commit (§6b-5b) — blokkeert dit niets. Het kan namelijk precies het ergste geval niet
zien: vijf teksten die met ándere woorden toch hetzelfde sjabloon volgen. Een tekst die hier
groen door komt, kan nog steeds vijf keer dezelfde vorm hebben. De exitcode is 1 zodra er iets
boven de norm staat, want een controle die altijd 0 teruggeeft is makkelijk te negeren — maar
een run wordt er niet door tegengehouden en hoort er zelf naar te kijken.

Wat het meet, en waarom precies dit:

* **kopjes** — `#`-kopjes en vetgedrukte aanhefregels horen er niet te zijn (norm 0). Op 7 nov
  waren het er nul en zat het probleem in de taal; deze teller staat er zodat het niet via de
  opmaak terugkomt.
* **tussenkopjes in woorden** — alinea's die openen met hun eigen onderwerp als label.
* **herhaalde vormen** — dezelfde opener of dezelfde zinswending in meerdere teksten van één
  dag. Dit is de belangrijkste teller: op 7 nov kwamen twee formuleringen in **vijf van de vijf**
  teksten letterlijk voor.
* **tells** — de lijst uit §6c, met de gemeten aantallen van 7 nov als vertrekpunt.
* **rekenjargon** — de woorden die §6c sinds 17 okt al verbiedt (`procentpunt`, `drempel`,
  `edge`, …). Daar was nog geen controle op.
* **lengte** — 300 tot 600 woorden (§6c).

De norm per tekst staat in `NORM`; de nulmeting van 7 november staat in `BASELINE_7_NOV` en is
alleen bedoeld om te kunnen zien of het beter wordt.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# --------------------------------------------------------------------------- norm

NORM = {
    "kopjes": 0,            # geen `#` en geen **vetgedrukte aanhef** in de preview-tekst
    "em_dash": 2,           # per voorbeschouwing; op 7 nov was het gemiddeld 5,2
    "label_openers": 0,     # alinea's die met hun rubriek als opschrift beginnen
    "tells": 3,             # alle tells samen, per voorbeschouwing
    "jargon": 0,            # rekenwoorden die §6c sinds 17 okt verbiedt
    "woorden_min": 300,
    "woorden_max": 600,
}

# De nulmeting waarop de regel is geschreven (vijf teksten, 2843 woorden).
BASELINE_7_NOV = {
    "teksten": 5, "woorden": 2843, "em_dash": 26, "precies": 8,
    "en_dat_is": 6, "meta": 6, "verboden_zinnen": 10,
}

# Formuleringen die op 7 nov in vijf van de vijf teksten stonden. De INHOUD die ze uitdrukken
# blijft verplicht (§6c punt 5 en 6); de woorden mogen niet elke dag dezelfde zijn.
VERBODEN_ZINNEN = {
    "slopen-formule": r"[Ww]at deze (weddenschap|bet) kan slopen",
    # Het is de OPENER die zich herhaalt, niet het woord 'omdat': op 7 nov openden vier van de
    # vijf slotregels met "Hij staat <positie> omdat…" en de vijfde met "Hij staat onderaan de
    # lijst van vijf, maar…". Vijf van de vijf begonnen dus met "Hij staat". Vandaar dat 'omdat'
    # hier optioneel is — anders meet de teller 4 waar de herhaling 5 is.
    "slotregel-formule": r"\bHij staat (bovenaan|onderaan|eerste|tweede|derde|vierde|vijfde|"
                         r"op de lijst|\d+e?)\b",
    "opener-tijd-stadion": r"^(Om |Kwart |Half |Tien voor |Vijf voor )[^.]{0,80}"
                           r"(, en dit is|en dit is) (de|het) (wedstrijd|weddenschap|duel)",
    "wat-pleit-ervoor": r"[Ww]at er v(oor|óór) pleit, (is|zit)|[Ww]at deze (weddenschap|bet) "
                        r"dan wél draagt",
}

# De tells uit §6c. Sleutel = hoe hij in het rapport heet.
TELLS = {
    "dat-is-precies-waarom": r"dat is precies waarom|dat is de hele vraag|en dat is precies",
    "dat-is-geen-X": r"[Dd]at is geen (detail|toeval|slap voorbehoud|pech|curiositeit|"
                     r"formaliteit|randgeval)",
    "antithese-als-afsluiter": r"\bniet \w+ maar \w+\b|\bis geen [^.]{1,30} maar [^.]{1,30}\b",
    "meta-aankondiging": r"dus laat ik daarmee beginnen|laat ik daarmee beginnen|"
                         r"hoort vooraan en niet in een voetnoot|hier moet ik eerlijk|"
                         r"ik wil daar niet overdreven|dus ook dat eerst|[Bb]egin bij de",
    "nadruk-fragment": r"(?<=[.!] )(?:[A-ZÉÁÍÓÚ][\w'’é]*(?: [\w'’é]+){0,2})\.(?=\s)",
    "gemanieerde-versterker": r"bijna komisch|griezelig|onaangenaam precies|vernietigend|"
                              r"ongebruikelijk eenduidig",
    "precies-als-stopwoord": r"\bprecies\b",
}

# Woorden die §6c sinds 17 okt 2026 uit een voorbeschouwing verbiedt (rekenverslag-taal).
JARGON = [
    "procentpunt", "drempel", "lat van", "edge", "scheefstand", "rangorde",
    "selection_score", "robuustheidstoets", "poort 7", "poort 8", "poort 9",
    "bet_beide", "herijking", "kalibratie", "brier", "shrink", "rho",
]

# Woorden waarmee een alinea niet mag openen: dan is de eerste zin een opschrift.
LABEL_OPENERS = [
    r"^Het teamnieuws\b", r"^Over de bezetting\b", r"^Qua bezetting\b",
    r"^Het weer\b", r"^De onderlinge historie (is|zegt|geeft)\b",
    r"^De vorm\b", r"^De cijfers\b", r"^De bezetting\b", r"^Teamnieuws\b",
    r"^De week eromheen\b", r"^Het tweede voorbehoud\b", r"^Het eerste voorbehoud\b",
]


# ----------------------------------------------------------------------- hulpjes

def _norm(t: str) -> str:
    """Kleinletters zonder accenten en zonder interpunctie, voor het vergelijken van openers."""
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", t)).strip()


def _alineas(tekst: str) -> list[str]:
    return [a.strip() for a in tekst.split("\n\n") if a.strip()]


def _is_slotregel(alinea: str) -> bool:
    """De cursieve verantwoording aan het eind (§6c punt 6) is geen gewone alinea."""
    return alinea.startswith("*") and alinea.rstrip().endswith("*")


def meet(tekst: str) -> dict:
    """Alle tellingen voor één voorbeschouwing."""
    alineas = _alineas(tekst)
    body = [a for a in alineas if not _is_slotregel(a)]

    kopjes = len(re.findall(r"(?m)^#{1,6} ", tekst))
    # Een vetgedrukte aanhef: vet aan het begin van een alinea. Vet midden in een zin is nadruk
    # en geen kopje, dus daar kijken we niet naar.
    vet_aanhef = sum(1 for a in alineas if re.match(r"\*\*[^*]{2,80}\*\*", a))

    labels = []
    for a in body:
        eerste = a.split(". ")[0]
        for pat in LABEL_OPENERS:
            if re.search(pat, eerste):
                labels.append(eerste[:60])
                break

    tells = {}
    for naam, pat in TELLS.items():
        n = len(re.findall(pat, tekst))
        if n:
            tells[naam] = n

    jargon = {}
    laag = tekst.lower()
    for w in JARGON:
        # OP WOORDGRENS EN NIET OP SUBSTRING (8 nov 2026). `laag.count(w)` vond `rho` in
        # "voorhoede" en meldde dat als verboden rekenjargon; `lat van` en `edge` hebben hetzelfde
        # probleem ("plat vanaf", "hedge" bestaat niet in het Nederlands maar "edge" zit in
        # "wedge"). Een controle die afgaat op een gewoon Nederlands woord leert de lezer hem te
        # negeren, en dan vangt hij het echte geval ook niet meer. `\b` aan beide kanten; de term
        # mag spaties bevatten (`lat van`, `poort 8`) en wordt daarom geëscaped.
        n = len(re.findall(rf"\b{re.escape(w)}\b", laag))
        if n:
            jargon[w] = n

    verboden = {}
    for naam, pat in VERBODEN_ZINNEN.items():
        n = len(re.findall(pat, tekst, re.M))
        if n:
            verboden[naam] = n

    return {
        "woorden": len(tekst.split()),
        "alineas": len(alineas),
        "kopjes": kopjes + vet_aanhef,
        "markdown_kopjes": kopjes,
        "vet_aanhef": vet_aanhef,
        "em_dash": tekst.count("—"),
        "label_openers": labels,
        "tells": tells,
        "tells_totaal": sum(tells.values()),
        "jargon": jargon,
        "verboden_zinnen": verboden,
        "openers": [_norm(a.split(". ")[0])[:48] for a in body],
    }


def herhaalde_vormen(metingen: dict[str, dict]) -> dict:
    """Welke openers en welke verboden formules in MEER DAN EEN tekst van de dag voorkomen.

    Dit is de belangrijkste teller van het script: een vorm die in één tekst staat is een keuze,
    dezelfde vorm in vijf teksten is een sjabloon.
    """
    per_opener: dict[str, list[str]] = {}
    for naam, m in metingen.items():
        for o in set(m["openers"]):
            if len(o.split()) >= 3:
                per_opener.setdefault(o, []).append(naam)
    herhaald = {o: v for o, v in per_opener.items() if len(v) > 1}

    per_formule: dict[str, list[str]] = {}
    for naam, m in metingen.items():
        for f in m["verboden_zinnen"]:
            per_formule.setdefault(f, []).append(naam)

    return {"openers": herhaald, "formules": per_formule}


# ------------------------------------------------------------------------ rapport

def rapport(metingen: dict[str, dict], herhaald: dict) -> tuple[list[str], list[str]]:
    """Geeft (regels om af te drukken, overtredingen)."""
    uit, fout = [], []
    n = len(metingen)
    tot_w = sum(m["woorden"] for m in metingen.values())
    tot_dash = sum(m["em_dash"] for m in metingen.values())

    uit.append(f"VOORBESCHOUWINGEN — {n} tekst(en), {tot_w} woorden")
    uit.append("§6c, 'Geen tussenkopjes en minder AI-tells' (bindt vanaf 8 nov 2026). "
               "Hulpmiddel, geen poort.")
    uit.append("")
    uit.append(f"  {'tekst':46s} {'woorden':>7s} {'—':>4s} {'kop':>4s} {'label':>6s} "
               f"{'tells':>6s} {'jargon':>7s}")
    uit.append("  " + "-" * 86)
    for naam, m in metingen.items():
        uit.append(f"  {naam[:46]:46s} {m['woorden']:7d} {m['em_dash']:4d} {m['kopjes']:4d} "
                   f"{len(m['label_openers']):6d} {m['tells_totaal']:6d} "
                   f"{sum(m['jargon'].values()):7d}")

        if m["kopjes"] > NORM["kopjes"]:
            fout.append(f"{naam}: {m['kopjes']} kopje(s) in de tekst "
                        f"({m['markdown_kopjes']} markdown, {m['vet_aanhef']} vetgedrukte aanhef) "
                        f"— norm {NORM['kopjes']}")
        if m["em_dash"] > NORM["em_dash"]:
            fout.append(f"{naam}: {m['em_dash']} em-dashes — norm {NORM['em_dash']}")
        for lab in m["label_openers"]:
            fout.append(f"{naam}: alinea opent met zijn rubriek als opschrift — \"{lab}…\"")
        if m["tells_totaal"] > NORM["tells"]:
            detail = ", ".join(f"{k}×{v}" for k, v in sorted(m["tells"].items()))
            fout.append(f"{naam}: {m['tells_totaal']} tells — norm {NORM['tells']} ({detail})")
        for w, c in m["jargon"].items():
            fout.append(f"{naam}: rekenjargon '{w}' ×{c} — §6c verbiedt dit in een "
                        f"voorbeschouwing")
        if not (NORM["woorden_min"] <= m["woorden"] <= NORM["woorden_max"]):
            fout.append(f"{naam}: {m['woorden']} woorden — norm "
                        f"{NORM['woorden_min']}–{NORM['woorden_max']}")

    uit.append("")
    if herhaald["formules"]:
        uit.append("  VERBODEN FORMULERINGEN (de inhoud blijft verplicht, de woorden niet):")
        for f, waar in sorted(herhaald["formules"].items()):
            uit.append(f"    {f:24s} in {len(waar)} van de {n}")
            fout.append(f"verboden formulering '{f}' in {len(waar)} van de {n} teksten")
    else:
        uit.append("  verboden formuleringen: geen")

    if herhaald["openers"]:
        uit.append("  HERHAALDE ALINEA-OPENERS (zelfde vorm in meerdere teksten van één dag):")
        for o, waar in sorted(herhaald["openers"].items(), key=lambda x: -len(x[1])):
            uit.append(f"    \"{o}…\" in {len(waar)} van de {n}")
            fout.append(f"herhaalde opener \"{o}…\" in {len(waar)} van de {n} teksten")
    else:
        uit.append("  herhaalde alinea-openers: geen")

    uit.append("")
    if n:
        uit.append(f"  em-dash gemiddeld {tot_dash / n:.1f} per tekst "
                   f"(7 nov 2026, de nulmeting: {BASELINE_7_NOV['em_dash'] / 5:.1f})")
    uit.append("")
    uit.append("  LEESWIJZER. Dit vangt de opmaak en de letterlijke herhaling. Het kan NIET zien")
    uit.append("  of vijf teksten met andere woorden toch hetzelfde sjabloon volgen — dat is")
    uit.append("  precies waar de klacht van 7 november over ging, en daar is geen teller voor.")
    uit.append("  Lees de vijf openers hierboven naast elkaar en vraag of het vijf verschillende")
    uit.append("  stukken zijn of één stuk met andere namen erin.")
    return uit, fout


def check_bestand(pad: Path) -> int:
    prose = json.loads(pad.read_text())
    bets = prose.get("bets") or {}
    metingen = {}
    for pid, blok in bets.items():
        # `why` EERST ERBIJ GEZET OP 8 NOV 2026, EN DIT IS DE REDEN. Dit script las alleen
        # `preview`, en geen enkel prosebestand van Run A, B of C gebruikt die sleutel voor de
        # tekst: alle 404 gepubliceerde bets staan onder `why` (88 oudere onder `preview`).
        # `report.py` accepteert sinds 17 okt beide (`text.get("preview") or text.get("why")`),
        # dit script niet — dus gaf het op élke run met bets "geen voorbeschouwingen (nul bets)"
        # terug, met exitcode 0. Een hulpmiddel dat niet kan afgaan is erger dan geen hulpmiddel:
        # het staat groen in het runrapport en §6b-5j eist die uitvoer juist als controle op de
        # stijlregel die op 7 november is afgesproken. Dezelfde stille faalstand als
        # `calibration.py settle` (§6b-5c), het Serie B-id (`run-b.md`) en `settled_note` — een
        # stap die kan wegvallen zonder dat iets klaagt. De zelftest ving het niet, want die
        # voedt de tekst rechtstreeks aan `meet()` en komt nooit langs deze lus.
        tekst = (blok or {}).get("preview") or (blok or {}).get("why")
        if not tekst:
            continue
        metingen[pid] = meet(tekst)
    if not metingen:
        print(f"{pad}: geen voorbeschouwingen (nul bets) — niets te meten.")
        return 0
    uit, fout = rapport(metingen, herhaalde_vormen(metingen))
    print("\n".join(uit))
    if fout:
        print(f"  BOVEN DE NORM — {len(fout)} punt(en):")
        for f in fout:
            print(f"    - {f}")
        return 1
    print("  Alles binnen de norm.")
    return 0


# ----------------------------------------------------------------------- zelftest

def _selftest() -> int:
    """Geen netwerk en geen repo: de tellers op verzonnen teksten."""
    fouten = []

    def eis(naam, gekregen, verwacht):
        if gekregen != verwacht:
            fouten.append(f"{naam}: {gekregen!r} != {verwacht!r}")

    # 1. De vorm van 7 november: labelopener, slopen-formule, slotregel-formule, veel em-dashes.
    slecht = (
        "Om twee uur 's middags, als eerste van de dag, en dit is de wedstrijd waar het "
        "om gaat — en dat is precies waarom hij hier staat.\n\n"
        "Het teamnieuws is aan beide kanten mild — twee uitvallers, geen aanvallers — en "
        "dat is geen detail.\n\n"
        "Wat deze weddenschap kan slopen is een zakelijke thuisploeg.\n\n"
        "*Hij staat bovenaan omdat het verschil met de prijs het grootst is.*"
    )
    m = meet(slecht)
    eis("slopen-formule gezien", "slopen-formule" in m["verboden_zinnen"], True)
    eis("slotregel-formule gezien", "slotregel-formule" in m["verboden_zinnen"], True)
    eis("opener tijd+stadion gezien", "opener-tijd-stadion" in m["verboden_zinnen"], True)
    eis("labelopener gezien", len(m["label_openers"]), 1)
    eis("dat-is-geen-X gezien", m["tells"].get("dat-is-geen-X"), 1)
    eis("em-dash geteld", m["em_dash"], 3)
    eis("em-dash boven de norm", m["em_dash"] > NORM["em_dash"], True)
    eis("geen kopjes in deze tekst", m["kopjes"], 0)

    # 2. Een vetgedrukte aanhef is een kopje; vet MIDDEN in een zin is nadruk en dus geen kopje.
    eis("vetgedrukte aanhef is een kopje",
        meet("**Teamnieuws, en nu wordt het lastig.** Twee spelers eruit.")["kopjes"], 1)
    eis("vet midden in de zin is geen kopje",
        meet("Straatsburg hield in **twintig** duels de nul niet.")["kopjes"], 0)
    eis("markdown-kopje geteld", meet("## Teamnieuws\n\nTwee spelers eruit.")["kopjes"], 1)

    # 3. Rekenjargon dat §6c verbiedt.
    mj = meet("De bet haalt zijn drempel met vier procentpunt edge over de lat van 8,0.")
    eis("jargon gevonden", sorted(mj["jargon"]), ["drempel", "edge", "lat van", "procentpunt"])

    # 4. Een schone tekst hoort nul te scoren op alles.
    schoon = (
        "Sporting ontvangt Moreirense in een stadion dat de laatste vijf thuisduels gemiddeld "
        "drie en een half doelpunt zag vallen. De bezoekers hielden acht wedstrijden op rij de "
        "nul niet, en dat cijfer draagt deze weddenschap meer dan de onderlinge historie, die "
        "op 0-3, 3-0, 3-1 en 2-1 staat.\n\n"
        "Zeno Debast ontbreekt bij de thuisploeg en Miguel Silva bij de bezoekers; allebei "
        "verdedigers, geen van beiden een aanvaller. Moreirense had zeven dagen rust, Sporting "
        "vier, na een uitwedstrijd in Oekraere op dinsdag.\n\n"
        "Een zakelijke thuisploeg die na een kwartier met 2-0 voor staat en de bal gaat "
        "rondtikken, maakt hier een einde aan. Dat is bij drie Europese duels in acht dagen "
        "geen ver gezocht scenario."
    )
    ms = meet(schoon)
    eis("schoon: geen kopjes", ms["kopjes"], 0)
    eis("schoon: geen labelopeners", ms["label_openers"], [])
    eis("schoon: geen verboden formules", ms["verboden_zinnen"], {})
    eis("schoon: geen jargon", ms["jargon"], {})
    eis("schoon: em-dash binnen de norm", ms["em_dash"] <= NORM["em_dash"], True)

    # 5. Herhaalde openers over MEERDERE teksten — de belangrijkste teller.
    a = "De bezoekers scoorden in acht duels op rij. Dat draagt de weddenschap.\n\nTwee uitvallers."
    b = "De bezoekers scoorden in acht duels op rij. Hier geldt hetzelfde.\n\nGeen uitvallers."
    h = herhaalde_vormen({"a": meet(a), "b": meet(b)})
    eis("herhaalde opener over twee teksten", len(h["openers"]), 1)
    # Eén tekst alleen kan per definitie geen herhaling opleveren.
    eis("een tekst geeft geen herhaling", herhaalde_vormen({"a": meet(a)})["openers"], {})

    # 6. De cursieve slotregel is geen gewone alinea en mag geen labelopener-alarm geven.
    eis("slotregel wordt overgeslagen",
        meet("Een gewone alinea.\n\n*De vorm van de dag was anders.*")["label_openers"], [])

    for f in fouten:
        print("FOUT:", f)
    print(f"{22 - len(fouten)} van 22 controles goed.")
    return 1 if fouten else 0


def main() -> int:
    if "selftest" in sys.argv:
        return _selftest()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", required=True, help="rundag, YYYY-MM-DD")
    ap.add_argument("--run", required=True, choices=list("abc"))
    ap.add_argument("--file", help="een prose.json rechtstreeks, in plaats van --date/--run")
    a = ap.parse_args([x for x in sys.argv[1:] if x != "selftest"])
    pad = Path(a.file) if a.file else Path(f"runs/{a.date}-run-{a.run}.prose.json")
    if not pad.exists():
        print(f"niet gevonden: {pad}", file=sys.stderr)
        return 2
    return check_bestand(pad)


if __name__ == "__main__":
    raise SystemExit(main())
