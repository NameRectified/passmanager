import argparse
import getpass
import logging
import sys

import pyperclip

import config
import checker
import generator
import scorer

logger = logging.getLogger(__name__)

# ANSI escape codes for terminal text coloring.
# \033[92m = green, \033[94m = blue, \033[93m = yellow, \033[91m = red.
# \033[0m resets formatting back to default.
_STRENGTH_LABELS = {
    "very_strong": "\033[92m",
    "strong": "\033[94m",
    "fair": "\033[93m",
    "weak": "\033[91m",
}
_RESET = "\033[0m"


def _color_strength(strength: str) -> str:
    """Wrap a strength label in ANSI color codes for terminal output."""
    color = _STRENGTH_LABELS.get(strength, "")
    return f"{color}{strength}{_RESET}" if color else strength


def cmd_check(args: argparse.Namespace) -> None:
    """Check a password for breaches, score its strength, and show suggestions."""
    password = args.password or getpass.getpass("Password: ")

    logger.info("Checking password...")

    try:
        breach_count = checker.check_breach(password)
    except ConnectionError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    analysis = scorer.analyze_password(password)
    suggestions = scorer.get_suggestions(password, breach_count, analysis)

    print()
    if breach_count > 0:
        print(f"Breach Status: Found in {breach_count:,} data breaches")
    else:
        print("Breach Status: Not found in known breaches")
    print(
        f"Strength:       {analysis['score']}/100 "
        f"({_color_strength(analysis['strength'])})"
    )
    print()

    needs_replacement = breach_count > 0 or analysis["score"] < 60
    if suggestions:
        print("Suggestions:")
        for s in suggestions:
            print(f"  \u2022 {s}")  # \u2022 = bullet character (•)
        print()

    if needs_replacement:
        replacement = generator.generate_password()
        pyperclip.copy(replacement)
        print(f"Suggested replacement: {replacement} (copied to clipboard)")
    else:
        pyperclip.copy(password)
        print("Password is safe. Copied to clipboard.")


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate a strong random password, display its score, and copy to clipboard."""
    password = generator.generate_password(length=args.length)
    analysis = scorer.analyze_password(password)
    pyperclip.copy(password)

    print()
    print(f"Generated:      {password}")
    print(
        f"Strength:       {analysis['score']}/100 "
        f"({_color_strength(analysis['strength'])})"
    )
    print("Copied to clipboard.")


def create_parser() -> argparse.ArgumentParser:
    """Build the argument parser with check and generate subcommands."""
    parser = argparse.ArgumentParser(
        prog="passmanager",
        description="Password manager — check breaches, generate passwords, score strength.",
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    check_parser = subparsers.add_parser(
        "check",
        help="Check a password for breaches and get a strength score",
    )
    check_parser.add_argument(
        "password",
        nargs="?",
        help="Password to check (omit for hidden prompt)",
    )
    check_parser.set_defaults(func=cmd_check)

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a strong random password",
    )
    generate_parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=config.DEFAULT_LENGTH,
        help="Password length (default: %(default)s)",
    )
    generate_parser.set_defaults(func=cmd_generate)

    return parser


def main() -> None:
    """Entry point: set up logging (only WARNING+ shown by default), parse args, dispatch."""
    logging.basicConfig(
        # Only show WARNING and above; change to logging.DEBUG for verbose output.
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
