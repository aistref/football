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
state = load_or_start("a", date(2026, 11, 10))
state["artifact"] = "https://claude.ai/artifact/1EF7QdeTHCnXtdXph3Nrrj"
state["github_dagrapport"] = ("https://github.com/aistref/football/blob/main/runs/"
                              "2026-11-10-run-a.dagrapport.md")
nu = datetime.now(NL)
state["duur"] = {
    "start_nl": "03:05",
    "klaar_nl": nu.strftime("%H:%M"),
    "minuten": round((nu - nu.replace(hour=3, minute=5, second=0,
                                      microsecond=0)).total_seconds() / 60, 1),
    "note": ("Ruim binnen de 06:30-deadline van §0. De looptijd zegt vandaag niets over de cap: "
             "er was geen enkele wedstrijd in het inzetvenster, dus Stage 4 en 5 hebben niets "
             "gedaan. Het werk zat in Stage -2 (88 takken, en daarna de pick-id's per tak tegen "
             "die van main leggen omdat de commitgraaf bij unrelated histories niets zegt), in "
             "het lezen van de volledige regelset, en in het narekenen van twee uitspraken uit "
             "het rapport van gisteren."),
}
state["rendercontrole"] = {
    "bron": "tmp-run/ra_nov10_rendercheck.js (Playwright/Chromium, file://)",
    "licht": {"scrollHeight": 9401, "textLen": 21760, "blocks": 30, "tables": 1, "errors": 0},
    "donker": {"scrollHeight": 9401, "textLen": 21760, "blocks": 30, "tables": 1, "errors": 0},
    "note": ("Preventief gedraaid, zoals §6c (15 okt 2026) voorschrijft bij een melding over een "
             "onbereikbaar dagrapport. De pagina rendert in licht en donker volledig en zonder "
             "console- of pagefouten, met dezelfde achtergrond- en tekstkleur per schema, dus een "
             "onbereikbare Artifact zou een probleem van de sandbox-host zijn en opnieuw "
             "publiceren zinloos — dan is de Markdown-route het antwoord."),
}
state["branchcontrole"] = {
    "remote_branches": 88,
    "takken_zonder_eigen_commits": 8,
    "takken_met_eigen_commits": 80,
    "merge_base_met_main": "leeg bij alle 80 — unrelated histories",
    "main_commits": 57,
    "langste_tak_commits": 647,
    "unshallow_helpt_niet": ("de knip zit niet lokaal maar op de remote: de geschiedenis van vóór "
                             "1 nov 2026 bestaat daar niet meer onder main"),
    "inhoudelijke_vergelijking": {
        "main_picks": 550,
        "picks_op_een_tak_en_niet_in_main": 0,
        "nagekeken_takken": ["claude/zealous-edison-dkcki5", "claude/elegant-cannon-nzoe3l",
                             "claude/stoic-davinci-0icngk", "claude/zealous-edison-g7vuzh",
                             "claude/stoic-davinci-y66391"],
        "jongste_tak_tip": "main zelf (9 nov 09:15 UTC); geen tak is nieuwer",
        "pending_picks_op_main": 0,
    },
    "gemerged": False,
    "note": ("§3 Stage -2 eist een vergelijking op de INHOUD en niet op de commitgraaf, en dat is "
             "hier de enige controle die iets zegt. Elke onderzochte tak is een strikte "
             "deelverzameling van main: de dataketen is over de knip heen doorgelopen, alleen de "
             "commitgeschiedenis is afgekapt. Er valt niets te verenigen. Dat de controle in haar "
             "huidige vorm elke run 80 keer vals alarm geeft, staat als besluitpunt in het "
             "dagrapport — takken opruimen is een handeling op de repo van de gebruiker."),
}
mark_completed(state)
save(state)
print("voortgangsbestand afgesloten:", state.get("completed"))
print("artifact:", state["artifact"])
print("markdown:", state["github_dagrapport"])
print("looptijd:", state["duur"]["minuten"], "minuten")
