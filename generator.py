import logging
import string
import secrets

from config import DEFAULT_LENGTH, EXCLUDED_CHARS, MIN_DIGITS, MIN_SPECIAL

logger = logging.getLogger(__name__)

AMBIGUOUS: str = EXCLUDED_CHARS


def _build_pool(exclude_ambiguous: bool) -> str:
    pool = string.ascii_letters + string.digits + string.punctuation
    if exclude_ambiguous:
        for ch in AMBIGUOUS:
            pool = pool.replace(ch, "")
    return pool


def _meets_criteria(
    password: str,
    min_digits: int,
    min_special: int,
) -> bool:
    digit_count = sum(c.isdigit() for c in password)
    special_count = sum(c in string.punctuation for c in password)
    return (
        any(c.islower() for c in password)
        and any(c.isupper() for c in password)
        and digit_count >= min_digits
        and special_count >= min_special
    )


def generate_password(
    length: int = DEFAULT_LENGTH,
    min_digits: int = MIN_DIGITS,
    min_special: int = MIN_SPECIAL,
    exclude_ambiguous: bool = True,
) -> str:
    """Generate a cryptographically secure password.

    Args:
        length: Total character length of the password.
        min_digits: Minimum number of digits required.
        min_special: Minimum number of special characters required.
        exclude_ambiguous: If True, exclude characters like 0/O/1/l/I.

    Returns:
        A random password string that meets all criteria.
    """
    pool = _build_pool(exclude_ambiguous)

    while True:
        password = "".join(secrets.choice(pool) for _ in range(length))
        if _meets_criteria(password, min_digits, min_special):
            logger.debug("Generated password of length %d", length)
            return password
