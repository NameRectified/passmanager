import logging
import string

from config import MIN_LENGTH

logger = logging.getLogger(__name__)


def _score_length(password: str) -> tuple[int, str | None]:
    length = len(password)
    if length < MIN_LENGTH:
        return 0, "too_short"
    if length < 12:
        return 15, None
    if length < 16:
        return 25, None
    return 35, None


def _score_classes(password: str) -> tuple[int, list[str]]:
    score = 0
    issues: list[str] = []
    checks = [
        (any(c.islower() for c in password), "no_lowercase"),
        (any(c.isupper() for c in password), "no_uppercase"),
        (any(c.isdigit() for c in password), "no_digit"),
        (any(c in string.punctuation for c in password), "no_special"),
    ]
    for present, issue in checks:
        if present:
            score += 10
        else:
            issues.append(issue)
    return score, issues


def _has_sequential(password: str) -> bool:
    sequences = ["abcdefghijklmnopqrstuvwxyz", "0123456789"]
    lowered = password.lower()
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i : i + 3] in lowered:
                return True
    return False


def _has_repeated(password: str) -> list[str]:
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
    """Analyze password strength and return a score, label, and list of issues.

    Args:
        password: The password to analyze.

    Returns:
        A dict with keys:
            score (int): 0–100.
            strength (str): "weak", "fair", "strong", or "very_strong".
            issues (list[str]): Machine-readable issue codes.
    """
    length_score, length_issue = _score_length(password)
    class_score, class_issues = _score_classes(password)

    issues: list[str] = []
    if length_issue:
        issues.append(length_issue)
    issues.extend(class_issues)

    if _has_sequential(password):
        issues.append("sequential_chars")
    repeated_issues = _has_repeated(password)
    issues.extend(repeated_issues)

    total = length_score + class_score
    if "sequential_chars" in issues:
        total = max(total - 10, 0)
    for issue in repeated_issues:
        total = max(total - 5, 0)

    if total >= 80:
        strength = "very_strong"
    elif total >= 60:
        strength = "strong"
    elif total >= 40:
        strength = "fair"
    else:
        strength = "weak"

    logger.debug("Password scored %d/100 (%s)", total, strength)
    return {"score": total, "strength": strength, "issues": issues}


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
