import hashlib
import logging

import requests

from config import HIBP_API_URL

logger = logging.getLogger(__name__)


def _sha1_hash(password: str) -> str:
    """Return uppercase SHA-1 hex digest of the given password."""
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def check_breach(password: str) -> int:
    """Check if a password appears in known data breaches via the HIBP API.

    Uses the k-anonymity model — only the first 5 characters of the SHA-1 hash
    are sent over the network.

    Args:
        password: The password to check.

    Returns:
        The number of times the password appears in breaches (0 if not found).

    Raises:
        ConnectionError: If the API request fails.
    """
    full_hash = _sha1_hash(password)
    prefix, suffix = full_hash[:5], full_hash[5:]

    logger.debug("Checking breach for hash prefix %s", prefix)

    try:
        response = requests.get(HIBP_API_URL + prefix, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ConnectionError(f"Failed to reach HIBP API: {exc}") from exc

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            logger.info("Password found in %s breach(es)", count)
            return int(count)

    logger.info("Password not found in any known breaches")
    return 0
