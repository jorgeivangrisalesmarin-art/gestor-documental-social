"""Auditoría estructurada (E17): registros sin identificadores en claro.

Regla del brief §11: NUNCA almacenar números de identificación en logs.
"""

import logging
import sys

log = logging.getLogger("gds.audit")
log.setLevel(logging.INFO)
if not log.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(handler)


def audit_event(event: str, **fields) -> None:
    """Emite un evento de auditoría en JSON de una línea.

    Los campos admitidos nunca incluyen identificadores en claro; las
    identificaciones deben pasarse como `document_hmac` (huella HMAC).
    """
    import json
    import time

    payload = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **fields}
    log.info(json.dumps(payload, ensure_ascii=False))
