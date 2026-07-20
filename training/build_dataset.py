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

COMMON_PW_URL = (
    "https://raw.githubusercontent.com/danielmiessler/SecLists/"
    "master/Passwords/Common-Credentials/"
    "10k-most-common.txt"
)


def download_common_passwords(url: str, limit: int = 1000) -> list[str]:
    print(f"Downloading common passwords from SecLists...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    passwords = [line.strip() for line in resp.text.splitlines() if line.strip()]
    print(f"  Got {len(passwords)} passwords, using first {limit}")
    return passwords[:limit]


def fetch_breach_counts(passwords: list[str]) -> list[tuple[str, int]]:
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
    print(f"Generating {count} strong passwords (breach_count=0)...")
    return [(generate_password(length=16), 0) for _ in range(count)]


def save_dataset(
    rows: list[tuple[str, int]], filename: str = "passwords.csv"
) -> Path:
    path = DATA_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["password", "breach_count"])
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")
    return path


def main() -> None:
    common = download_common_passwords(COMMON_PW_URL, limit=1000)
    results = fetch_breach_counts(common)
    strong = generate_strong_passwords(500)
    all_rows = results + strong
    save_dataset(all_rows)


if __name__ == "__main__":
    main()
