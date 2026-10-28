"""Zelftest op de voorvoegselregel van 28 okt 2026 (`teamnames.is_abbreviation`).

Het eerste blok is het geval van vandaag en de twee gevallen die §4 bij naam noemt; het tweede
blok is de REGRESSIE: alle koppelingen die de oude deelverzamelingsregel maakte, moeten ze ook
nog maken, anders is een reparatie een nieuw gat.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts.teamnames import is_abbreviation, tokens
from ra_names import resolve

MOET_NIET = [("FC Eindhoven", "PSV Eindhoven"), ("Ajax", "Jong Ajax"),
             ("FC Utrecht", "Jong FC Utrecht"), ("Eindhoven", "PSV"),
             ("Madrid", "Real Madrid"),
             # Toegevoegd nadat de EERSTE reparatie van vanmorgen (een voorvoegselregel) dit geval
             # wel doorliet: Excelsior '31 uit Rijssen is niet Excelsior uit Rotterdam, en het
             # onderscheidende deel staat hier in de STAART. Zelfde eis, andere kant van de naam.
             ("Excelsior '31", "Excelsior"), ("Roda JC", "Roda JC Kerkrade"),
             ("Sporting", "Sporting Gijon"), ("1. FC Koln", "Koln")]
MOET_WEL = [("Ipswich", "Ipswich Town"), ("Wigan", "Wigan Athletic"),
            ("Bradford City", "Bradford City"),
            ("Borussia Dortmund", "Borussia Dortmund"), ("Hamburger SV", "Hamburger"),
            ("Plymouth", "Plymouth Argyle"), ("Hamburger SV", "Hamburger SV"),
            # Deze twee stonden bij de eerste opzet van deze zelftest onder MOET_NIET, en dat
            # was een verkeerde verwachting van mij en geen fout in de regel. "Athletic" staat
            # in `_DROP`, dus `Athletic Bilbao` houdt `bilbao` over en de twee namen zijn na
            # normalisatie gewoon gelijk — Bilbao IS de gangbare korte naam. En een losse
            # KOPnaam is juist het geldige afkortingsgeval (`Ipswich` op `Ipswich Town`); dat
            # `Sporting` meerdere clubs kan zijn, vangt de eis van precies één treffer in de
            # tabel en niet deze regel.
            ("Bilbao", "Athletic Bilbao")]
fout = 0
for a, b in MOET_NIET:
    if is_abbreviation(a, b):
        print(f"FOUT  koppelt wel: {a!r} ~ {b!r}"); fout += 1
    else:
        print(f"ok    koppelt niet: {a!r} ~ {b!r}")
for a, b in MOET_WEL:
    if not is_abbreviation(a, b):
        print(f"FOUT  koppelt niet: {a!r} ~ {b!r}"); fout += 1
    else:
        print(f"ok    koppelt wel: {a!r} ~ {b!r}")

print("\n--- regressie: wat de oude regel koppelde en de nieuwe ook moet koppelen ---")
def oud(name, table):
    if name in table: return name
    tn = tokens(name)
    hits = [k for k in table if tokens(k) <= tn or tn <= tokens(k)]
    return hits[0] if len(hits) == 1 else None

from scripts import fotmob
COV = json.load(open("data/coverage.json"))["competitions"]
namen = set()
for c in json.load(open("tmp-run/ra_oct28_cands.json")):
    namen.add((c["competition"], c["primaryId"], c["season"], c["home"]))
    namen.add((c["competition"], c["primaryId"], c["season"], c["away"]))
verschil = 0
for comp, pid, season, naam in sorted(namen):
    tbl = fotmob.fetch_league_stats(pid, season)["teams"]
    a, b = oud(naam, tbl), resolve(naam, tbl)
    if a != b:
        verschil += 1
        print(f"  VERSCHIL {comp:20s} {naam:26s} oud={a!r}  nieuw={b!r}")
print(f"\n{len(namen)} namen nagelopen, {verschil} verschil(len), {fout} fout(en) in de zelftest")
sys.exit(1 if fout else 0)
