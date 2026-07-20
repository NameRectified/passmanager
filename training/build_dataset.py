import csv
import time
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator import generate_password
from checker import check_breach

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Public dataset of common passwords from SecLists (CC0 / public domain).
# We use the first 3000 to get a spread across breach count buckets.
# The top 1000 are usually heavily breached; deeper entries get more varied counts.
COMMON_PW_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt"


def download_common_passwords(url: str, limit: int = 1000) -> list[str]:
    """Download a list of common passwords from SecLists on GitHub.

    Args:
        url: Raw GitHub URL to the password list.
        limit: Maximum number of passwords to return.

    Returns:
        A list of password strings, trimmed to the given limit.
    """
    print(f"Downloading common passwords from SecLists...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    passwords = [line.strip() for line in resp.text.splitlines() if line.strip()]
    print(f"  Got {len(passwords)} passwords, using first {limit}")
    return passwords[:limit]


def fetch_breach_counts(passwords: list[str]) -> list[tuple[str, int]]:
    """Query HIBP for each password's breach count.

    Args:
        passwords: List of passwords to check.

    Returns:
        List of (password, breach_count) tuples.
        -1 if the API request failed for that password.
    """
    results: list[tuple[str, int]] = []
    total = len(passwords)
    for i, pw in enumerate(passwords):
        try:
            count = check_breach(pw)
        except ConnectionError:
            count = -1
        results.append((pw, count))
        if (i + 1) % 50 == 0:
            print(f"  Checked {i + 1}/{total}")
    return results


def generate_strong_passwords(count: int = 500) -> list[tuple[str, int]]:
    """Generate strong random passwords and label them with breach_count=0.

    These provide the "strong" class for the model — passwords that have
    diverse characters, good length, and no breach history.

    Args:
        count: How many passwords to generate.

    Returns:
        List of (password, 0) tuples.
    """
    print(f"Generating {count} strong passwords (breach_count=0)...")
    return [(generate_password(length=16), 0) for _ in range(count)]


def save_dataset(
    rows: list[tuple[str, int]], filename: str = "passwords.csv"
) -> Path:
    """Save password + label pairs to a CSV file for training.

    Args:
        rows: List of (password, breach_count) tuples.
        filename: Output filename inside training/data/.

    Returns:
        Path to the saved CSV file.
    """
    path = DATA_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["password", "breach_count"])
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")
    return path


def main() -> None:
    """Build the training dataset: common passwords + HIBP labels + generated strong passwords.

    Uses 3000 common passwords (to get varied breach counts) + 500 generated strong passwords.
    Total ~3500 API calls at ~50ms each ≈ 3 minutes.
    """
    common = download_common_passwords(COMMON_PW_URL, limit=3000)
    results = fetch_breach_counts(common)
    strong = generate_strong_passwords(500)
    all_rows = results + strong
    save_dataset(all_rows)


if __name__ == "__main__":
    main()
