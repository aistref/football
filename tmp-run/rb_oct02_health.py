"""§6b-3 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft.

Schrijfwijze volgens `_doc`: één doorlopende tekst per bron, chronologisch, oudste feit eerst.
Geen runverslagen achter elkaar plakken.
"""
import json

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
DAG = "2026-10-02"


def bij(key, status, tekst, **extra):
    v = S.setdefault(key, {})
    v["status"] = status
    v["last_checked"] = DAG
    v["detail"] = (str(v.get("detail", "")).rstrip() + f"  [Run B] {tekst}").strip()
    v.update(extra)


bij("fotmob", "ok",
    "Run B 2 okt: twee daglijsten (2 okt: 55 competities/98 duels; 3 okt: 107/431), 34 "
    "standenverzoeken voor scripts/idcheck.py (17 competities × twee seizoensnotaties, alle 17 "
    "OK, afsluitcode 0), zes standen voor de drie spelende competities (Segunda División, Keuken "
    "Kampioen Divisie, Série A BRA — vorig en lopend seizoen), de wedstrijdcontext en het "
    "wedstrijddossier van alle drie de duels. Alles HTTP 200, geen storing. Fotmob was ook "
    "vandaag de enige kansbron: Understat dekt geen van deze drie competities, dus de "
    "redundantie van 31 aug bestaat op deze runlijst niet. De uitzondering van §3 punt 3 is niet "
    "aan de orde. WEL gemeten en nieuw: Fotmob geeft voor Eldense en Helmond Sport een "
    "selectiewaarde van 0, en daardoor valt zo'n duel stil uit het contextlogboek (ctxlog kan "
    "out/(basis+out) niet rekenen zonder noemer). Over alle rundagen tot nu toe raakt dat 22,1% "
    "van de Run B-duels met een contextblok tegen 5,4% bij Run A.")

bij("the_odds_api", "ok",
    "Run B 2 okt: api_check.py geeft 45 actieve voetbalcompetities en 19.979 van de 20.000 "
    "credits over (21 deze maand). Sleutel niet afgewezen. 7 credits uitgegeven: twee "
    "bulk-aanroepen (h2h + spreads + totals, 3 credits elk) voor soccer_spain_segunda_division en "
    "soccer_brazil_campeonato, plus één per-duel BTTS-verzoek (1 credit) voor São Paulo – Santos; "
    "quota daarna 19.972. De h2h-respons gaf 23 boeken met een volledige 1X2 voor São Paulo – "
    "Santos (Pinnacle de-vigd 46,0 / 28,1 / 25,9) en 20 voor Eldense – Real Oviedo. Alle zes "
    "markten waren voor São Paulo – Santos werkelijk te koop: 5 handicaplijnen, een 0.0-lijn "
    "(DNB), een +0.5-lijn (DC), 4 totaallijnen en BTTS.")

bij("oddsapi", "ok",
    "Sleutel geaccepteerd (api_check.py 2 okt 2026). Gebruikt voor Segunda División en Série A "
    "(BRA): 7 credits.")

bij("betexplorer", "ok",
    "Run B 2 okt: drie fixturepagina's opgehaald (spain/laliga2 11 rijen, "
    "netherlands/eerste-divisie 8 rijen, brazil/serie-a-betano 22 rijen), alle HTTP 200. Voor de "
    "Keuken Kampioen Divisie is dit de ENIGE 1X2-bron — die competitie heeft geen sportkey bij "
    "The Odds API — en het marktgemiddelde komt daar over maar 3 boeken (6.72 / 4.82 / 1.35). Bij "
    "Série A (BRA) stond geen enkele rij op is_today omdat de aftrap in NL-tijd op 3 oktober "
    "valt; de terugval op de volledige lijst vond het duel wel (15 boeken, 2.04 / 3.35 / 3.61).")

bij("understat", "ok",
    "Run B 2 okt: niet aangeroepen — geen van de drie spelende competities (Segunda División, "
    "Keuken Kampioen Divisie, Série A BRA) zit in de vijf die Understat dekt (§4). Status "
    "ongewijzigd overgenomen. Geen storing, maar wél de reden dat deze run geen tweede xG-model "
    "had.")

bij("api_football", "missing_key",
    "Met opzet afwezig sinds het besluit van de gebruiker op 27 sep 2026 (§3). Geen gat, geen "
    "actiepunt, niet in de notificatie. api_check.py meldt het onveranderd als feit en dringt "
    "niet aan.")

d["last_run"] = f"{DAG} run-b"
d["updated"] = DAG
d["last_run_bevinding"] = (
    "Run B 2 okt 2026 — één bet op rangorde (§5b) en twee bevindingen over de administratie, "
    "beide van de soort 'faalt zonder foutmelding'. "
    "(1) HET CONTEXTLOGBOEK MIST SYSTEMATISCH DE KLEINE CLUBS. `ctxlog.out_share` eist een "
    "selectiewaarde als noemer en Fotmob geeft die voor Eldense en Helmond Sport niet (0,0), dus "
    "twee van de drie duels van vandaag gingen niet het logboek in — zonder melding, want de rij "
    "wordt met `continue` overgeslagen. Nagerekend over alle rundagen: 109 van de 493 Run "
    "B-duels met een contextblok (22,1%) vallen zo weg, tegen 26 van 482 bij Run A (5,4%) en 27 "
    "van 159 bij Run C (17,0%). De meting van §1c heeft 475 tot 4.270 wedstrijden nodig en "
    "mist dus juist de competities waar Run B werkt. "
    "(2) RUN C HEEFT ctxlog.py collect NOOIT GEDRAAID. Het logboek bevat 456 rijen van Run A en "
    "384 van Run B en nul van Run C, terwijl er 159 Run C-duels met een contextblok in "
    "`data/run-state/` staan waarvan 132 een bruikbaar beschikbaarheidsverschil hebben. §6b-5d "
    "geldt voor elke run; dit is 14% van de steekproef die nooit is verzameld en het is met de "
    "bestaande run-states alsnog in te halen.")
json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", d["last_run"])
