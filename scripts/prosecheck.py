"""Tel de kopjes, de AI-tells en de herhaalde vormen in de voorbeschouwingen van een run.

Hoort bij §6c, "Minder AI-tells" (7 nov 2026, op verzoek van de gebruiker, bindend vanaf 8 nov
2026). Die regel is op de vijf voorbeschouwingen van 7 november gemeten, en dit script is de
meting zelf, zodat een volgende run niet op zijn gevoel hoeft af te gaan.

**LET OP — DE KOPJESREGEL IS OP 18 NOV 2026 OMGEDRAAID** en bindt vanaf 19 nov 2026. Waar hier
eerst `"kopjes": 0` stond, staat nu `"kopjes_min": 3`: de gebruiker wil kopjes in plaats van een
lap tekst. Alle andere tellers staan onveranderd. Zie `KOPJES_OMGEDRAAID` hieronder voor het
volledige besluit en voor wat er juist níet mee verandert.

    python3 scripts/prosecheck.py --date 2026-11-08 --run a
    python3 scripts/prosecheck.py selftest        # geen netwerk, geen repo nodig

**Dit is een hulpmiddel en geen poort.** Anders dan `progress.py verify` — dat groen moet zijn
vóór de commit (§6b-5b) — blokkeert dit niets. Het kan namelijk precies het ergste geval niet
zien: vijf teksten die met ándere woorden toch hetzelfde sjabloon volgen. Een tekst die hier
groen door komt, kan nog steeds vijf keer dezelfde vorm hebben. De exitcode is 1 zodra er iets
boven de norm staat, want een controle die altijd 0 teruggeeft is makkelijk te negeren — maar
een run wordt er niet door tegengehouden en hoort er zelf naar te kijken.

Wat het meet, en waarom precies dit:

* **kopjes** — `#`-kopjes en vetgedrukte aanhefregels, en er moeten er nu **minstens drie** zijn
  (norm `kopjes_min` = 3, omgedraaid op 18 nov 2026). Tot die datum was de norm nul. Op 7 nov
  waren het er nul en zat het probleem volledig in de taal, niet in de opmaak — dat is precies
  waarom deze teller omgedraaid kón worden zonder het besluit van 7 november aan te tasten.
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
    "kopjes_min": 3,        # MINSTENS drie kopjes — omgedraaid op 18 nov 2026, zie KOPJES_OMGEDRAAID
    "em_dash": 2,           # per voorbeschouwing; op 7 nov was het gemiddeld 5,2
    "label_openers": 0,     # alinea's die met hun rubriek als opschrift beginnen
    "tells": 3,             # alle tells samen, per voorbeschouwing
    "jargon": 0,            # rekenwoorden die §6c sinds 17 okt verbiedt
    "woorden_min": 300,
    "woorden_max": 600,
}

#: Vanaf deze dag geldt `kopjes_min`. Vóór die dag gold het omgekeerde (`kopjes` = 0), dus een
#: hermeting van de voorbeschouwingen van 7 t/m 17 november hoort op de oude norm te lopen.
KOPJES_BINDS_FROM = "2026-11-19"

KOPJES_OMGEDRAAID = """De kopjesregel is op 18 nov 2026 OMGEDRAAID, op besluit van de gebruiker.

> *"Daarnaast wil ik dat je, vanaf dat je weer weddenschappen hebt, in de voorbeschouwing werkt
> met kopjes, in plaats van een grote lap tekst."*

Van 8 t/m 18 november gold hier `"kopjes": 0` — geen `#`-kopje en geen vetgedrukte aanhef. Die
norm kwam uit het besluit van 7 november, en dat besluit ging over iets anders dan het nu lijkt:
op die dag stonden er NUL markdown-kopjes in de vijf teksten en zat het probleem volledig in de
TAAL (vijf van de vijf teksten openden hun alinea's met hun eigen rubriek als label, en twee
formuleringen kwamen letterlijk in alle vijf voor). De teller op 0 was er alleen om te voorkomen
dat het via de opmaak terug zou komen.

Het gevolg was een tekst van 300 tot 600 woorden zonder enige structuur, en dat is waar de
gebruiker nu over valt. Kopjes zijn de oplossing voor de LAP TEKST; ze waren nooit de oorzaak van
de sjabloonklacht.

**Wat hiermee verandert:** alleen de kopjes. `kopjes_min` = 3.

**Wat NIET verandert, en dat is het grootste deel van 7 november:**

* `label_openers` blijft 0, en wordt er strenger van in plaats van losser. Een kopje draagt nu het
  onderwerp, dus de alinea eronder hoeft het niet te herhalen — *"Teamnieuws"* als kopje met
  daaronder *"Het teamnieuws is..."* is het invulveld in het kwadraat.
* `em_dash` blijft 2, `tells` blijft 3, `jargon` blijft 0, de lengte blijft 300-600 woorden.
* De harde inhoudelijke eisen van §6c blijven onverkort: een frequentie die de bet TEGENSPREEKT
  staat vooraan, er staat één alinea over wat de bet kan slopen, en de cursieve verantwoording
  sluit af. Een kopjesstructuur mag nooit een vaste kopjesstructuur worden — vijf teksten op één
  ochtend met dezelfde vijf kopjes in dezelfde volgorde is precies het sjabloon waar 7 november
  over ging, nu met opschriften erboven.
"""

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
        # OP HELE WOORDEN ZOEKEN, NIET OP LETTERREEKSEN (gerepareerd 8 nov 2026). `laag.count(w)`
        # vond `rho` in "voorhoede" en "achterhoede" en meldde twee volstrekt normale
        # voetbalwoorden als rekenjargon. Dezelfde val ligt klaar voor `edge` (in een Engelse
        # clubnaam) en `lat van`. Een controle die bij gewoon taalgebruik alarm slaat, leert je
        # hem te negeren, en dan vangt hij ook het echte geval niet meer.
        # `\b` werkt hier omdat elke term uit letters, cijfers of een underscore bestaat; bij
        # een term met een spatie erin (`lat van`, `poort 8`) staat de grens om het geheel.
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", laag))
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
    uit.append("§6c, 'Minder AI-tells' (8 nov 2026) plus de kopjesregel die op 18 nov 2026 is "
               "OMGEDRAAID: minstens "
               f"{NORM['kopjes_min']} kopjes per tekst in plaats van nul. Hulpmiddel, geen poort.")
    uit.append("")
    uit.append(f"  {'tekst':46s} {'woorden':>7s} {'—':>4s} {'kop':>4s} {'label':>6s} "
               f"{'tells':>6s} {'jargon':>7s}")
    uit.append("  " + "-" * 86)
    for naam, m in metingen.items():
        uit.append(f"  {naam[:46]:46s} {m['woorden']:7d} {m['em_dash']:4d} {m['kopjes']:4d} "
                   f"{len(m['label_openers']):6d} {m['tells_totaal']:6d} "
                   f"{sum(m['jargon'].values()):7d}")

        if m["kopjes"] < NORM["kopjes_min"]:
            fout.append(f"{naam}: {m['kopjes']} kopje(s) in de tekst "
                        f"({m['markdown_kopjes']} markdown, {m['vet_aanhef']} vetgedrukte aanhef) "
                        f"— norm is MINSTENS {NORM['kopjes_min']} (besluit 18 nov 2026: kopjes "
                        f"in plaats van een lap tekst)")
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
        # `why` ERBIJ OP 8 NOV 2026 (Run B), EN DIT IS DE REDEN. Dit script las alleen
        # `preview`, en geen enkel prosebestand van Run A, B of C gebruikt die sleutel voor de
        # tekst: alle 404 gepubliceerde bets staan onder `why` (88 oudere onder `preview`).
        # `report.py` accepteert sinds 17 okt beide (`text.get("preview") or text.get("why")`),
        # dit script niet — dus gaf het op élke run met bets "geen voorbeschouwingen (nul bets)"
        # terug, met afsluitcode 0. Een hulpmiddel dat niet kan afgaan is erger dan geen
        # hulpmiddel: het staat groen in het runrapport en §6b-5j eist die uitvoer juist als
        # controle op de stijlregel van 7 november. Dezelfde stille faalstand als
        # `calibration.py settle` (§6b-5c), het Serie B-id (`run-b.md`) en `settled_note` (§6c).
        # De zelftest ving het niet: die voedt de tekst rechtstreeks aan `meet()` en komt nooit
        # langs deze lus.
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
    eis("de vorm van 7 nov had nul kopjes — en haalt de norm van 18 nov dus niet", m["kopjes"], 0)

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
    eis("schoon: geen labelopeners", ms["label_openers"], [])
    eis("schoon: geen verboden formules", ms["verboden_zinnen"], {})
    eis("schoon: geen jargon", ms["jargon"], {})
    eis("schoon: em-dash binnen de norm", ms["em_dash"] <= NORM["em_dash"], True)
    # Deze tekst heeft geen kopjes, en dat is sinds 18 nov 2026 juist een TEKORT in plaats van
    # een verdienste: de norm is omgedraaid naar minstens drie (KOPJES_OMGEDRAAID).
    eis("schoon maar zonder kopjes: haalt de nieuwe norm NIET",
        ms["kopjes"] < NORM["kopjes_min"], True)

    # 4b. Dezelfde tekst MET kopjes haalt de norm wel — en de kopjes mogen het onderwerp niet
    # in de alinea eronder herhalen, want dan is `label_openers` terug.
    met_kopjes = (
        "## Acht duels zonder de nul\n\n"
        + schoon.split("\n\n")[0] + "\n\n"
        "## Debast en Silva ontbreken\n\n"
        + schoon.split("\n\n")[1] + "\n\n"
        "## Wat hier misgaat\n\n"
        + schoon.split("\n\n")[2]
    )
    mk = meet(met_kopjes)
    eis("met kopjes: drie kopjes geteld", mk["kopjes"], 3)
    eis("met kopjes: haalt de nieuwe norm", mk["kopjes"] >= NORM["kopjes_min"], True)
    eis("met kopjes: nog steeds geen labelopeners", mk["label_openers"], [])
    eis("met kopjes: nog steeds geen jargon", mk["jargon"], {})

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
    print(f"{26 - len(fouten)} van 26 controles goed.")
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
