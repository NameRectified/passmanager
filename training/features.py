import math
import string


def extract_features(password: str) -> dict[str, float]:
    """Convert a password into a dict of numeric features for the ML model.

    The model can't read raw text — it needs numbers. Each feature
    captures some property of the password (length, character diversity,
    patterns, etc.).

    Args:
        password: The password string to analyze.

    Returns:
        A dict mapping feature names to numeric values.
    """
    length = len(password)
    lower = sum(c.islower() for c in password)
    upper = sum(c.isupper() for c in password)
    digits = sum(c.isdigit() for c in password)
    special = sum(c in string.punctuation for c in password)

    # Shannon entropy: measures how random the password is.
    # Higher entropy = harder to guess (typically stronger).
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
        # Ratios are scale-invariant — a 10-char pw with 3 digits
        # has the same ratio as a 20-char pw with 6 digits.
        "lowercase_ratio": lower / length if length else 0.0,
        "uppercase_ratio": upper / length if length else 0.0,
        "digit_ratio": digits / length if length else 0.0,
        "special_ratio": special / length if length else 0.0,
        "unique_chars": len(set(password)),
        "entropy": entropy,
        # Binary flags are useful for tree-based models — they create
        # clean split points (e.g., "has_uppercase >= 0.5").
        "has_lowercase": float(lower > 0),
        "has_uppercase": float(upper > 0),
        "has_digit": float(digits > 0),
        "has_special": float(special > 0),
        "sequential_runs": sequential_count,
        "repeated_groups": repeated_count,
    }


def _count_sequential(password: str) -> int:
    """Count 3+ character sequential patterns (abc, bcd, 123, 234, etc.).

    Sequential characters are common in weak passwords and make them
    easier to guess.

    Args:
        password: The password to scan.

    Returns:
        Number of 3-char sequential runs found.
    """
    sequences = ["abcdefghijklmnopqrstuvwxyz", "0123456789"]
    lowered = password.lower()
    count = 0
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i : i + 3] in lowered:
                count += 1
    return count


def _count_repeats(password: str) -> int:
    """Count how many characters appear 3+ times consecutively (aaa, bbbb, etc.).

    Repeated characters reduce password entropy and often appear in
    weak passwords.

    Args:
        password: The password to scan.

    Returns:
        Number of repeat groups found (each distinct character counted once).
    """
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


# Column order for the model's feature matrix. Must be consistent
# between training (train.py) and inference (scorer.py).
FEATURE_NAMES = list(extract_features("").keys())
