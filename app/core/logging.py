import json
import logging

logger = logging.getLogger("changeguard")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

def log_event(event: str, **fields):
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload))
