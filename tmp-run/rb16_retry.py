"""Run B, 12 sep 2026 — één herhaalpoging om Fotmob-verzoeken heen.

Aanleiding: bij de eerste poging van Stage 3 vanochtend brak de TLS-verbinding naar
fotmob.com halverwege af (`SSLEOFError: UNEXPECTED_EOF_WHILE_READING`) op de stand van
English League Two, nadat vijftien eerdere verzoeken in dezelfde run wél waren geslaagd.
`scripts.fotmob._get_json` doet geen enkele poging opnieuw, dus zo'n eenmalige hik zet de
hele run stil op een bron die het gewoon doet.

Dit is met opzet géén wijziging in `scripts/fotmob.py`: het is een herhaalpoging en geen
regel, en hij hoort bij de omstandigheden van deze run. Alleen netwerk- en TLS-fouten worden
herhaald; een HTTP-status (403, 404, 429) komt ongewijzigd door, want dat is een antwoord van
de bron en geen storing onderweg — daar is een tweede poging zinloos of zelfs schadelijk.
"""
import time

from scripts import fotmob

_origineel = fotmob._get_json
POGINGEN = 4
PAUZE = (2, 5, 10)


def _met_herhaling(url: str) -> dict:
    laatste = None
    for poging in range(POGINGEN):
        try:
            return _origineel(url)
        except fotmob.FotmobError as exc:
            # "HTTP 403" e.d. is een antwoord van de bron; niet herhalen.
            if str(exc).startswith("HTTP "):
                raise
            laatste = exc
            if poging < POGINGEN - 1:
                pauze = PAUZE[min(poging, len(PAUZE) - 1)]
                print(f"    fotmob hik ({type(exc).__name__}), opnieuw over {pauze}s: {url[-60:]}")
                time.sleep(pauze)
    raise laatste


fotmob._get_json = _met_herhaling
