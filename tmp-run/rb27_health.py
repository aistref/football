"""Run B, 27 sep 2026 — `data/source-health.json` en `data/coverage.json` bijwerken (§3, §6b-3)."""
import json

DAG = "2026-09-27"
NOTE = {
    "oddsapi": ("27 sep 2026 (Run B): OK. 43 actieve voetbalcompetities, quota 18.666 over / "
                "1.334 gebruikt deze maand bij aanvang. Twee bulk-aanroepen (h2h + spreads + "
                "totals, 3 credits elk) voor soccer_spain_segunda_division (11 events) en "
                "soccer_usa_mls (23), plus 5 btts-event-aanroepen (1 credit elk) voor de duels "
                "met een kandidaat-edge. Totaal 11 credits van een plafond van 2330. De Keuken "
                "Kampioen Divisie heeft geen sportkey en is dus niet inkoopbaar; die draait op "
                "het gratis BetExplorer-marktgemiddelde."),
    "api_football": ("27 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet — ongewijzigd "
                     "sinds de eerste run, en dat is nu 51 dagen. api_check.py meldt "
                     "'statistieken (kansen) niet beschikbaar'. Fotmob vangt het op, dus de run "
                     "kan door; zie README 'Sleutels toevoegen'."),
    "fotmob": ("27 sep 2026 (Run B): OK op alle aanroepen. Twee daglijsten (27 sep: 85 "
               "competities / 288 duels, 28 sep: 33 / 60) voor runwindow, plus achttien "
               "daglijsten vooruit voor de dekkingsnotities. Competitiestanden voor Segunda "
               "División (140), Eerste Divisie (111) en MLS (130) in beide seizoenen, en La Liga "
               "(87) voor de degradantenomrekening. Wedstrijdcontext voor alle 7 duels zonder "
               "één fout. Ook Stage 0 liep hierlangs: acht schaduwpicks en twee echte picks als "
               "afgelopen gemeld, twee MLS-duels van 26 sep nog niet."),
    "betexplorer": ("27 sep 2026 (Run B): OK voor alle drie de actieve competities. "
                    "spain/laliga2 11 rijen (5 vandaag), netherlands/eerste-divisie 1 rij (1 "
                    "vandaag), usa/mls 23 rijen (4 als 'vandaag' gemarkeerd). Bij MLS valt de "
                    "is_today-vlag van BetExplorer opnieuw niet samen met het inzetvenster van "
                    "§3 Stage 1 — de vlag volgt de UTC-dag en het venster loopt tot 08:00 NL de "
                    "dag erna. De koppeling op namen vond het juiste duel wel."),
}

h = json.load(open("data/source-health.json"))
for key, note in NOTE.items():
    src = h["sources"].setdefault(key, {"status": "unknown", "role": "?", "detail": ""})
    src["last_checked"] = DAG
    src["status"] = "missing_key" if key == "api_football" else "ok"
    src["detail"] = (src.get("detail", "") + " | " + note).strip(" |")
h["last_run"] = f"{DAG} run-b"
h["updated"] = DAG
json.dump(h, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt voor:", ", ".join(NOTE))

c = json.load(open("data/coverage.json"))
comp = c["competitions"]
comp["Segunda División (ESP)"]["notes"] += (
    " Run B 27 sep 2026: xG bevestigd in beide seizoenen (vorig 22 ploegen / 42 speeldagen / "
    "avg_xg 1.360; lopend 7 speeldagen / avg_xg 1.306), dus FULL. `league_level` koos route "
    "`vorig+uplift`. NIEUW GEMETEN EN VASTGELEGD: voor een ploeg die uit de derde divisie "
    "(Primera Federación) is gepromoveerd bestaat GEEN gemeten divisiefactor — `promotion.TIER2` "
    "heeft geen ingang voor \"LaLiga2 (ESP)\", alleen TIER1 naar La Liga. CD Eldense staat "
    "daardoor niet in de stand van 2025/2026 en ook niet in die van La Liga, en komt terecht op "
    "tier NONE uit; Burgos CF – Eldense is daarom niet doorgerekend. Dat is dezelfde situatie als "
    "bij Série A (BRA) en Série B, die prompts/run-b.md al benoemt. Mallorca en Real Oviedo zijn "
    "wél omgerekend: dat zijn degradanten uit La Liga en die route (TIER1) is gemeten, waarna ze "
    "op LIGHT uitkomen.")
json.dump(c, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage bijgewerkt: Segunda División (ESP)")
