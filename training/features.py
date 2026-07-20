import math
import string


def extract_features(password: str) -> dict[str, float]:
    """Convert a password into a dict of numeric features for the model."""
    length = len(password)
    lower = sum(c.islower() for c in password)
    upper = sum(c.isupper() for c in password)
    digits = sum(c.isdigit() for c in password)
    special = sum(c in string.punctuation for c in password)

    entropy = 0.0
    if length:
        unique_chars = len(set(password))
        entropy = math.log2(unique_chars) * length

    sequential_count = _count_sequential(password)
    repeated_count = _count_repeats(password)

    return {
        "length": length,
        "lowercase_count": lower,
        "uppercase_count": upper,
        "digit_count": digits,
        "special_count": special,
        "lowercase_ratio": lower / length if length else 0.0,
        "uppercase_ratio": upper / length if length else 0.0,
        "digit_ratio": digits / length if length else 0.0,
        "special_ratio": special / length if length else 0.0,
        "unique_chars": len(set(password)),
        "entropy": entropy,
        "has_lowercase": float(lower > 0),
        "has_uppercase": float(upper > 0),
        "has_digit": float(digits > 0),
        "has_special": float(special > 0),
        "sequential_runs": sequential_count,
        "repeated_groups": repeated_count,
    }


def _count_sequential(password: str) -> int:
    """Count how many 3-char sequential patterns exist (abc, 123, etc.)."""
    sequences = ["abcdefghijklmnopqrstuvwxyz", "0123456789"]
    lowered = password.lower()
    count = 0
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i : i + 3] in lowered:
                count += 1
    return count


def _count_repeats(password: str) -> int:
    """Count how many characters repeat 3+ times consecutively."""
    count = 0
    run = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            run += 1
        else:
            if run >= 3:
                count += 1
            run = 1
    if run >= 3:
        count += 1
    return count


FEATURE_NAMES = list(extract_features("").keys())
