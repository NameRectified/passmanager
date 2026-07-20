import logging
import string
from pathlib import Path

import joblib

from config import MIN_LENGTH
from training.features import FEATURE_NAMES, _count_sequential, extract_features

logger = logging.getLogger(__name__)

_MODEL: object | None = None
_MODEL_PATH: Path = Path(__file__).parent / "models" / "strength_model.pkl"


def _load_model():
    global _MODEL
    if _MODEL is None and _MODEL_PATH.exists():
        _MODEL = joblib.load(_MODEL_PATH)
        logger.info("Loaded ML model from %s", _MODEL_PATH)
    return _MODEL


def _heuristic_issues(password: str) -> list[str]:
    issues: list[str] = []
    length = len(password)
    if length < MIN_LENGTH:
        issues.append("too_short")
    if not any(c.islower() for c in password):
        issues.append("no_lowercase")
    if not any(c.isupper() for c in password):
        issues.append("no_uppercase")
    if not any(c.isdigit() for c in password):
        issues.append("no_digit")
    if not any(c in string.punctuation for c in password):
        issues.append("no_special")
    if _count_sequential(password) > 0:
        issues.append("sequential_chars")
    issues.extend(_detect_repeats(password))
    return issues


def _detect_repeats(password: str) -> list[str]:
    seen: set[str] = set()
    issues: list[str] = []
    count = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            count += 1
        else:
            if count >= 3:
                ch = password[i - 1]
                issue = f"repeated_char_{ch}"
                if issue not in seen:
                    seen.add(issue)
                    issues.append(issue)
            count = 1
    if count >= 3:
        ch = password[-1]
        issue = f"repeated_char_{ch}"
        if issue not in seen:
            seen.add(issue)
            issues.append(issue)
    return issues


def analyze_password(password: str) -> dict:
    """Analyze password strength using a trained ML model.

    Falls back to heuristic scoring if the model is not available.

    Args:
        password: The password to analyze.

    Returns:
        A dict with keys:
            score (int): 0–100.
            strength (str): "weak", "fair", "strong", or "very_strong".
            issues (list[str]): Machine-readable issue codes.
    """
    model = _load_model()

    if model is not None:
        features = extract_features(password)
        row = [[features[name] for name in FEATURE_NAMES]]
        raw_score = float(model.predict(row)[0])
        score = max(0, min(100, round(raw_score)))
    else:
        score = 50

    issues = _heuristic_issues(password)

    if score >= 80:
        strength = "very_strong"
    elif score >= 60:
        strength = "strong"
    elif score >= 40:
        strength = "fair"
    else:
        strength = "weak"

    logger.debug("Password scored %d/100 (%s)", score, strength)
    return {"score": score, "strength": strength, "issues": issues}


def get_suggestions(
    password: str,
    breach_count: int,
    analysis: dict,
) -> list[str]:
    """Generate human-readable, password-specific suggestions.

    Args:
        password: The original password.
        breach_count: Number of breaches found (0 if clean).
        analysis: Result from analyze_password().

    Returns:
        A list of suggestion strings (2–5 items).
    """
    suggestions: list[str] = []
    issues = analysis["issues"]

    if breach_count > 0:
        suggestions.append(
            f"This password appears in {breach_count:,} data breach(es) — never reuse it"
        )

    issue_map: dict[str, str] = {
        "too_short": (
            f"Password is only {len(password)} characters "
            f"(aim for {MIN_LENGTH}+)"
        ),
        "no_lowercase": "Add at least one lowercase letter",
        "no_uppercase": "Add at least one uppercase letter",
        "no_digit": "Add at least one digit",
        "no_special": "Add at least one special character",
        "sequential_chars": (
            "Avoid sequential characters like '123' or 'abc'"
        ),
    }

    for issue in issues:
        if issue.startswith("repeated_char_"):
            ch = issue[-1]
            count = password.count(ch)
            suggestions.append(
                f"Repeated character '{ch}' appears {count} times"
            )
        elif issue in issue_map:
            suggestions.append(issue_map[issue])

    suggestions.append(
        "Use a mix of upper/lowercase, digits, and special characters"
    )

    return suggestions[:5]
