"""Permission helpers used throughout the API package."""
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("api")


def get_query_permissions(request) -> List[Dict[str, Any]]:
    """Return query permissions passed via the gateway."""

    logger.debug("Get Permission function called.")
    raw = request.headers.get("X-Query-Permissions", "[]")
    try:
        raw_json = json.loads(raw)
        return raw_json
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse permissions header: %s", exc)
        return []
