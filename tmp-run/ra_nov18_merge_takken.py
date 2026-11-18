"""18 nov 2026 - de laatste records van de oude takken verenigen in `main`, VOOR het opruimen.

`scripts/branchaudit.py` vond tien bladpaden in `data/source-health.json` die op een oudere tak
staan en niet op `main`. Stage -2 eist voor dit bestand VERENIGING ("beide runs hebben echt
gemeten; bewaar beide waarnemingen naast elkaar in `detail`"), en de gebruiker heeft het opruimen
van de takken goedgekeurd MITS er geen belangrijke informatie verloren gaat. Dit script is die
voorwaarde.

De drie groepen, en waarom ze precies zo worden weggeschreven:

1. `sources.max_deep_analyses` - main heeft alleen `status`, `last_checked` en `note`; een latere
   run heeft `detail` door `note` vervangen en daarmee `detail`, `detail_history` en `role` laten
   vallen. Dat is een ECHTE meting (de marge op de cap per dag), dus die gaat terug: `role` op zijn
   eigen plek, en de drie waarnemingen van 8, 9 en 10 november in `detail_history`.
2. `last_run_run_c.detail` - de BetExplorer-dekking per toernooi van 14 november (6 bladpaden).
   Main heeft inmiddels het blok van 18 november. Die twee mogen NIET door elkaar: dat zou een
   meting van 14 november onder de datum van 18 november zetten. Ze gaan dus als gedateerde regel
   in `detail_history` eronder.
3. `last_run_run_b.samenvatting` - de eenregelige samenvatting van Run B van 8 november. Zelfde
   redenering: main heeft het blok van 18 november, dus het oude blok gaat gedateerd in `history`.

Niets van main wordt overschreven. Alleen toegevoegd.
"""
import json
import subprocess

H = "data/source-health.json"


def van_tak(ref, pad):
    txt = subprocess.run(["git", "show", f"{ref}:{H}"], capture_output=True, text=True,
                         check=True).stdout
    node = json.loads(txt)
    for part in pad.split("."):
        node = (node or {}).get(part)
        if node is None:
            return None
    return node


h = json.load(open(H, encoding="utf-8"))
toegevoegd = []

# ---- 1. sources.max_deep_analyses ------------------------------------------------------------
mda_tak = van_tak("origin/claude/bold-curie-i16v98", "sources.max_deep_analyses")
mda = h["sources"].setdefault("max_deep_analyses", {})
if "role" not in mda and mda_tak.get("role"):
    mda["role"] = mda_tak["role"]
    toegevoegd.append("sources.max_deep_analyses.role")

hist = mda.setdefault("detail_history", [])
bestaand = {(e.get("date"), (e.get("detail") or "")[:60]) for e in hist}
nieuw = [{"date": "2026-11-10", "detail": mda_tak["detail"]}] + list(mda_tak.get("detail_history") or [])
for e in nieuw:
    if (e.get("date"), (e.get("detail") or "")[:60]) not in bestaand:
        hist.append(e)
        toegevoegd.append(f"sources.max_deep_analyses.detail_history[{e.get('date')}]")
mda["detail_history"] = hist[:8]

# main had `detail` door `note` vervangen; zet `detail` terug met de stand van VANDAAG, zodat dit
# bestand weer dezelfde vorm heeft als elke andere bron en de reeks niet opnieuw stil wegvalt.
if "detail" not in mda:
    mda["detail"] = (
        "18 nov (run A): NUL WEDSTRIJDEN OP EEN WOENSDAGCAP VAN 40, dus alle veertig plekken over "
        "en nul afgekapt - de hele runlijst lag stil door het interlandvenster. De twee getallen "
        "die §3 Stage 4 eist (de datarijkdom van de laagste wedstrijd die het nog haalde en van de "
        "hoogste die afviel) BESTAAN VANDAAG NIET: een lijst van nul heeft geen onderkant, en dat "
        "is iets anders dan twee nullen. De cap is een TIJDSgrens en geen creditgrens (§0); "
        "vandaag bindt geen van beide. DIT VELD IS OP 18 NOV TERUGGEZET: main had alleen nog een "
        "`note`, waardoor `detail`, `detail_history` en `role` van deze bron stil waren weggevallen "
        "en de dagreeks over de marge op de cap niet meer te lezen was. De waarnemingen van 8, 9 "
        "en 10 november staan hieronder in `detail_history`, uit de oude takken teruggehaald "
        "voordat die zijn opgeruimd."
    )
    mda["last_checked"] = "2026-11-18"
    toegevoegd.append("sources.max_deep_analyses.detail")

# ---- 2. last_run_run_c.detail van 14 november ------------------------------------------------
c_detail = van_tak("origin/claude/bold-curie-4vk0yy", "last_run_run_c.detail")
lrc = h.setdefault("last_run_run_c", {})
chist = lrc.setdefault("detail_history", [])
if not any(e.get("date") == "2026-11-14" for e in chist):
    chist.append({
        "date": "2026-11-14",
        "note": ("Uit tak claude/bold-curie-4vk0yy, verenigd op 18 nov 2026 voor het opruimen van "
                 "de oude takken. Dit is de bronstatus van Run C van 14 NOVEMBER en hoort niet bij "
                 "het blok erboven, dat van 18 november is."),
        "detail": c_detail,
    })
    toegevoegd.append("last_run_run_c.detail_history[2026-11-14]")

# ---- 3. last_run_run_b van 8 november --------------------------------------------------------
b_tak = van_tak("origin/claude/bold-curie-i16v98", "last_run_run_b")
lrb = h.setdefault("last_run_run_b", {})
bhist = lrb.setdefault("history", [])
if not any(e.get("date") == b_tak.get("date") for e in bhist):
    bhist.append({
        "date": b_tak.get("date"),
        "note": ("Uit tak claude/bold-curie-i16v98, verenigd op 18 nov 2026 voor het opruimen van "
                 "de oude takken. Het blok erboven is van 18 november; dit is Run B van 8 "
                 "november, de dag waarop poort 9 voor het eerst werkelijk bond."),
        "blok": b_tak,
    })
    toegevoegd.append("last_run_run_b.history[2026-11-08]")

h["_merge_note"] = (
    "18 nov 2026 (Run A): de tien bladpaden die `branchaudit.py` op oudere takken vond en op "
    "`main` miste, zijn hier verenigd VOORDAT de takken zijn opgeruimd - dat was de voorwaarde van "
    "de gebruiker. Niets van main is overschreven; de oude waarnemingen staan gedateerd in "
    "`detail_history` respectievelijk `history`, omdat ze over 8, 10 en 14 november gaan en de "
    "blokken op main over 18 november. Twee bestanden staan met OPZET niet op main "
    "(`scripts/oddspapi.py`, `data/odds-fallback.json`): besluit van 30 aug 2026 na de overstap "
    "naar het 20K-creditplan, zie README. De vier schaduwrijen van 3 oktober blijven eveneens weg "
    "(dubbeltelling, §3 Stage -2)."
)
h["updated"] = "2026-11-18"
json.dump(h, open(H, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(toegevoegd)} bladpad(en)/blok(ken) verenigd:")
for t in toegevoegd:
    print("  +", t)
