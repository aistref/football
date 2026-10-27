"""Stage -1 / §6b-7: looptijd en Artifact-link vastleggen en het voortgangsbestand afsluiten."""
from datetime import date
from scripts.progress import load_or_start, save, mark_completed

state = load_or_start("b", date(2026, 10, 27))
state["artifact"] = "https://claude.ai/artifact/Sj1irkvWARynCngHrpgBaL"
state["dagrapport_markdown"] = (
    "https://github.com/aistref/football/blob/main/runs/2026-10-27-run-b.dagrapport.md")
state["duur"] = {
    "start": "2026-10-27T03:03:00+00:00",
    "eind": "2026-10-27T03:38:00+00:00",
    "minuten": 35.0,
    "noot": ("Looptijd van de run, §0: de rapporten moeten om 06:30 NL klaar staan en dat is "
             "ruim gehaald (klaar om 04:38 NL). 15 duels en 123 selecties bij een cap van 40, "
             "dus de cap bond niet en de tijdsgrens evenmin."),
}
state["rendercontrole"] = {
    "uitgevoerd": True,
    "noot": ("§6c, 15 okt 2026: de HTML is lokaal in Chromium gerenderd vóór het publiceren. "
             "scrollHeight 16.741 px, 39.483 tekens zichtbare tekst, 53 blokken, 6 tabellen, "
             "3 bet-blokken, nul console- of pagefouten, en correct in licht én donker. Komt het "
             "dagrapport bij de gebruiker niet door, dan ligt dat dus niet aan de pagina en is "
             "opnieuw publiceren zinloos — dan is de Markdown-route op GitHub het antwoord."),
}
mark_completed(state)
save(state)
print("voortgangsbestand afgesloten:", state.get("completed"), state.get("completed_at"))
