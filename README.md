# PassCheck

A cross-platform CLI tool for password security: breach checking via the HIBP API, secure password generation, and ML-powered strength scoring with specific suggestions.

## Quick Install

```bash
git clone https://github.com/NameRectified/passcheck.git
cd passcheck
pip install -e .
```

Then run `passcheck` anywhere.

## Usage

### Interactive mode

```bash
passcheck
```

Shows a menu where you can pick **Check** or **Generate** without remembering flags.

### Check a password

```bash
passcheck check
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

You can also pass the password directly:
```bash
passcheck check yourpassword
```
Omitting the argument prompts hidden-ly with `getpass`.

### Generate a password

```bash
passcheck generate -l 16

Generated:      G_j2*8TUP8?7
Strength:       65/100 (strong)
Copied to clipboard.
```

- `-l`, `--length`: Password length (default: 16)

## Features

- **Breach checking**: Uses the [Have I Been Pwned](https://haveibeenpwned.com/API/v3#PwnedPasswords) API with k-anonymity — never sends the full hash over the network.
- **Password generation**: Uses `secrets` module. Excludes ambiguous characters (`0`, `O`, `1`, `l`, `I`, `|`). Guarantees at least one uppercase, one lowercase, three digits, and one special character.
- **ML strength scoring**: RandomForest model trained on 3500 passwords. Scores 0–100 with specific suggestions for improvement.
- **Specific suggestions**: Suggestions derived from the actual password — not generic templates.

## Requirements

- Python 3.10+
- `requests`, `pyperclip`, `scikit-learn`, `joblib`

## Project Structure

```
passcheck/
├── passcheck.py     CLI entry point
├── checker.py       Breach checking (HIBP API)
├── generator.py     Password generation
├── scorer.py        ML strength analysis + suggestions
├── config.py        Configuration constants
├── training/        ML pipeline (features, dataset, training)
├── tests/           pytest test suite (32 tests)
├── models/          Trained model (.pkl)
├── .progress/       Session log and interview prep
├── requirements.txt
└── pyproject.toml
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
