from pathlib import Path

HIBP_API_URL: str = "https://api.pwnedpasswords.com/range/"

DEFAULT_LENGTH: int = 16
MIN_LENGTH: int = 8
MIN_DIGITS: int = 3
MIN_SPECIAL: int = 1

EXCLUDED_CHARS: str = "0O1lI|"

PROJECT_ROOT: Path = Path(__file__).parent
