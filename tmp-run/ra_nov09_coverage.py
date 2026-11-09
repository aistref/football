"""Run A, 9 nov 2026 — dekkingsbevinding in `data/coverage.json` vastleggen.

Eén bevinding, en ze is herbruikbaar: een FA Cup-ronde tussen twee NON-LEAGUE-clubs komt
structureel op `NONE` uit, en dat is met de huidige `TIER2`-keten niet op te lossen. Zonder deze
notitie zoekt een volgende run dezelfde keten opnieuw af om tot hetzelfde antwoord te komen.
"""
import json

P = "data/coverage.json"
c = json.load(open(P))
fa = c["competitions"]["FA Cup (ENG)"]
fa.setdefault("notes_history", []).insert(0, {"date": "2026-11-07", "notes": fa.get("notes")})
fa["notes_history"] = fa["notes_history"][:6]
fa["notes"] = (
    "Run A 9 nov 2026: HET FOTMOB-ID BLIJFT 132 (bevestigd; de daglijst gaf er één duel onder, "
    "en BetExplorer /england/fa-cup/fixtures/ gaf hetzelfde duel met dezelfde aftrap 'Today "
    "20:30'). NIEUW EN HERBRUIKBAAR: EEN TIE TUSSEN TWEE NON-LEAGUE-CLUBS KOMT STRUCTUREEL OP "
    "`NONE` UIT, en dat is geen tekort in deze administratie. `promotion.CUP_BASE` hangt de FA Cup "
    "aan de Premier League en `promotion.shared_lower_division` loopt vandaar de `TIER2`-keten af; "
    "die keten is onder de Premier League ÉÉN schakel lang (Championship, id 48). Een club uit de "
    "National League of lager staat daar niet in, en er is geen gemeten divisiefactor die zo diep "
    "reikt — `MEASURED_TIER2_GAP` meet uitsluitend het paar hoogste divisie / divisie daaronder. "
    "Op 9 november liep Plymouth Parkway – Berkhamsted daarop vast: beide ploegen spelen in de "
    "Southern League Premier Division (achtste niveau), en nog in twee VERSCHILLENDE groepen "
    "(South en Central), dus er is ook geen gedeelde divisie om het duel in door te rekenen. "
    "Op 8 november gebeurde hetzelfde met Stafford Rangers, Cray Wanderers en Wimborne Town. "
    "WAT EEN VOLGENDE RUN HIERMEE MOET DOEN: dit meteen als `NONE` opschrijven met de reden, en "
    "er GEEN gepoolde factor op zetten (§2, §4) en geen nieuw `fotmob_id` voor gaan zoeken. Het "
    "is pas op te lossen met een eigen gemeten keten van meer dan één schakel diep, en dat is een "
    "besluit voor de gebruiker en geen regel die een run erbij schrijft. WAT WEL WERKT: een ronde "
    "waarin BEIDE ploegen in de Premier League of de Championship staan, of waarin ze samen in "
    "één divisie onder de basis staan — dan is er niets te overbruggen en rekent het duel gewoon "
    "door (§4, 15 sep 2026)."
)
c["updated"] = "2026-11-09"
json.dump(c, open(P, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt — FA Cup (ENG)")
