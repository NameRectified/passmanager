# PassManager

A cross-platform CLI tool for passwords: breach checking via the HIBP API, secure generation, and strength scoring with specific suggestions.

## Requirements

- Python 3.10+
- `requests`
- `pyperclip`

```bash
pip install -r requirements.txt
```

## Commands

### check

Check if a password has been breached, get a strength score, and see specific suggestions for improvement.

```bash
passmanager check
Password: ********

Breach Status: Found in 2,266,543 data breaches
Strength:       25/100 (weak)

Suggestions:
  • This password appears in 2,266,543 data breach(es) — never reuse it
  • Add at least one uppercase letter
  • Add at least one special character
  • Avoid sequential characters like '123' or 'abc'
  • Use a mix of upper/lowercase, digits, and special characters

Suggested replacement: :_Y8$4Ur/v-&6FuN (copied to clipboard)
```

You can also pass the password directly as an argument:
```bash
passmanager check yourpassword
```
Omitting the argument prompts hidden-ly with `getpass`.

### generate

Generate a strong random password:

```bash
passmanager generate -l 16

Generated:      G_j2*8TUP8?7
Strength:       65/100 (strong)
Copied to clipboard.
```

- `-l`, `--length`: Password length (default: 16)

## Features

- **Breach checking**: Uses the [Have I Been Pwned](https://haveibeenpwned.com/API/v3#PwnedPasswords) API with k-anonymity — never sends the full hash over the network.
- **Password generation**: Uses `secrets` module. Excludes ambiguous characters (`0`, `O`, `1`, `l`, `I`, `|`). Guarantees at least one uppercase, one lowercase, three digits, and one special character.
- **Strength scoring**: Heuristic analysis based on length, character diversity, sequential patterns, and repeated characters. _(ML-powered scoring coming in Phase 2.)_
- **Specific suggestions**: Suggestions are derived from the actual password — not generic templates.

## Project Structure

```
passmanager/
├── passmanager.py    CLI entry point
├── checker.py        Breach checking (HIBP API)
├── generator.py      Password generation
├── scorer.py         Strength analysis and suggestions
├── config.py         Configuration constants
├── tests/            pytest test suite
├── requirements.txt
└── .progress/        Session log and decisions
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
