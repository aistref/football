"""Run B, 28 sep 2026 — `data/source-health.json` en `data/coverage.json` bijwerken (§3, §6b-3)."""
import json

DAG = "2026-09-28"
NOTE = {
    "oddsapi": ("28 sep 2026 (Run B): OK. 43 actieve voetbalcompetities, quota 18.642 over / "
                "1.358 gebruikt deze maand bij aanvang. Eén bulk-aanroep (h2h + spreads + "
                "totals, 3 credits) voor soccer_spain_segunda_division (11 events), plus één "
                "btts-event-aanroep (1 credit) voor het enige duel met een kandidaat-edge. "
                "Totaal 4 credits van een plafond van 3103 — het budget was op geen enkel "
                "moment bindend. Segunda División was vandaag de enige spelende competitie en "
                "die heeft een sportkey, dus er is niets op het gratis marktgemiddelde "
                "teruggevallen."),
    "api_football": ("28 sep 2026 (Run B): API_FOOTBALL_KEY niet gezet, en dat is sinds het "
                     "besluit van de gebruiker op 27 sep 2026 de bewuste opzet en geen storing "
                     "(§3, 'API_FOOTBALL_KEY komt er niet'). api_check.py meldt het feitelijk en "
                     "dringt niet meer aan. De kanskant komt van Fotmob en Understat; zolang die "
                     "leveren is §2 gedekt."),
    "fotmob": ("28 sep 2026 (Run B): OK op alle aanroepen, geen enkele fout. Twee daglijsten "
               "(28 sep: 33 competities / 60 duels, 29 sep: 51 / 121) voor runwindow, plus "
               "achttien daglijsten vooruit voor de dekkingsnotities. NIEUW DEZE RUN: ook het "
               "endpoint /api/data/leagues?id=<primaryId> is voor alle zeventien competities "
               "aangeroepen als tweede methode onder de kalenderbevestiging — dat werkt en geeft "
               "de fixtures onder `fixtures.allMatches` (niet onder `matches`, waar een eerste "
               "poging op 404/leeg uitkwam). Competitiestand voor Segunda División (140) in "
               "beide seizoenen, en wedstrijdcontext voor het enige duel."),
    "betexplorer": ("28 sep 2026 (Run B): OK. spain/laliga2 11 rijen, waarvan 1 als 'vandaag' "
                    "gemarkeerd — dat komt exact overeen met het inzetvenster van §3 Stage 1, "
                    "anders dan bij de MLS-duels van eerdere runs waar de UTC-dagvlag van "
                    "BetExplorer en het venster uiteenliepen. Gebruikt voor het "
                    "1X2-marktgemiddelde over 12 boeken (§6e-kalibratieblok en het marktoordeel "
                    "over wie de mindere ploeg is), niet voor de gespeelde koers."),
    "understat": ("28 sep 2026 (Run B): niet aangeroepen. Understat dekt vijf competities (PL, "
                  "La Liga, Bundesliga, Serie A, Ligue 1) en geen daarvan staat op de "
                  "Run B-runlijst, dus er was hier niets te halen. Dat is geen storing en ook "
                  "geen gat: de status van 28 sep komt van Run A van deze ochtend."),
}

h = json.load(open("data/source-health.json"))
for key, note in NOTE.items():
    src = h["sources"].setdefault(key, {"status": "unknown", "role": "?", "detail": ""})
    src["last_checked"] = DAG
    if key == "api_football":
        src["status"] = "missing_key"
    elif key == "understat":
        pass                      # status niet aanraken: deze run heeft hem niet gemeten
    else:
        src["status"] = "ok"
    src["detail"] = (src.get("detail", "") + " | " + note).strip(" |")
h["last_run"] = f"{DAG} run-b"
h["updated"] = DAG
json.dump(h, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt voor:", ", ".join(NOTE))

c = json.load(open("data/coverage.json"))
comp = c["competitions"]
comp["Segunda División (ESP)"]["notes"] += (
    " Run B 28 sep 2026: xG opnieuw bevestigd in beide seizoenen (vorig 22 ploegen / 42 "
    "speeldagen / avg_xg 1.360; lopend 7 speeldagen / avg_xg 1.320), dus FULL. `league_level` "
    "koos route `vorig+uplift` (7 van 42 speeldagen = 17%, onder de helft), met "
    "vroeg-seizoensfactor 0.9864 op een gepoolde 0.9709 — de factor komt deze run volledig uit "
    "deze ene competitie, want er speelde niets anders. Eén duel op de maandagavond: Leganés – "
    "Castellón, beide ploegen staan in de stand van 2025/2026, dus geen omrekening nodig en "
    "geen NONE. Dat is het rustige geval; de promovendus-val uit de notitie van 27 sep (Primera "
    "Federación heeft geen gemeten divisiefactor) speelde vandaag niet.")
c["updated"] = DAG
json.dump(c, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage bijgewerkt: Segunda División (ESP)")
