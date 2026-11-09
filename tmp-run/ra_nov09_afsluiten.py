"""Stage -1 afsluiten (§6b-7) en de twee dagrapport-links vastleggen (§6c).

`meta.py integriteit` klaagt sinds 2 november over runs waarbij het dagrapport wel is gerenderd
maar de Artifact-link niet in run-state staat — dan is later niet meer na te gaan welke pagina is
verstuurd. Daarom staan ze hier beide, de Artifact en de GitHub-terugval van §6c.
"""
import json
from datetime import date, datetime
from zoneinfo import ZoneInfo
from scripts.progress import load_or_start, mark_completed, save

NL = ZoneInfo("Europe/Amsterdam")
state = load_or_start("a", date(2026, 11, 9))
state["artifact"] = "https://claude.ai/artifact/NRRREoPaP5JsoSykjpBEQF"
state["github_dagrapport"] = ("https://github.com/aistref/football/blob/main/runs/"
                              "2026-11-09-run-a.dagrapport.md")
state["duur"] = {
    "start_nl": "03:05",
    "klaar_nl": datetime.now(NL).strftime("%H:%M"),
    "minuten": round((datetime.now(NL) - datetime.now(NL).replace(hour=3, minute=5, second=0,
                                                                  microsecond=0)).total_seconds() / 60, 1),
    "note": ("Ruim binnen de 06:30-deadline van §0. De looptijd zegt vandaag weinig over de cap: "
             "er was één wedstrijd in het venster en die kwam op NONE uit, dus Stage 4 en 5 hebben "
             "vrijwel niets gedaan. Het werk zat in Stage -2 (de vier logboeken per rij-id tegen "
             "87 takken leggen), Stage 0 (11 picks en 70 schaduwrijen) en de Understat-diagnose."),
}
state["rendercontrole"] = {
    "bron": "tmp-run/ra_nov09_rendercheck.js (Playwright/Chromium, file://)",
    "licht": {"scrollHeight": 10015, "textLen": 22673, "blocks": 32, "tables": 2, "errors": 0},
    "donker": {"scrollHeight": 10015, "textLen": 22673, "blocks": 32, "tables": 2, "errors": 0},
    "note": ("Preventief gedraaid, zoals §6c (15 okt 2026) voorschrijft bij een melding over een "
             "onbereikbaar dagrapport. De pagina rendert in licht en donker volledig en zonder "
             "console- of pagefouten, dus een onbereikbare Artifact zou een probleem van de "
             "sandbox-host zijn en opnieuw publiceren zinloos — dan is de Markdown-route het "
             "antwoord."),
}
mark_completed(state)
save(state)
print("voortgangsbestand afgesloten:", state.get("completed"))
print("artifact:", state["artifact"])
print("markdown:", state["github_dagrapport"])
