# PassManager — Interview Preparation

## Project Overview

A cross-platform CLI password manager with:
- **Breach checking** via the Have I Been Pwned API (k-anonymity model)
- **Password generation** using Python's `secrets` module
- **ML-powered strength scoring** using a RandomForest model trained on real breach data

Built with Python 3.10+, no external services at runtime (model runs locally).

---

## Architecture Decisions

### Why functional style (no classes)?
The tool is simple enough that classes add ceremony without benefit. Pure functions are easier to test, compose, and reason about. Each module exports only what's needed.

### Why CLI, not a web app?
APIs (FastAPI/Django) are a valid choice, but a CLI tool is more portable, has zero hosting cost, and the user explicitly preferred it. The core logic modules (`checker.py`, `scorer.py`) are already decoupled — wrapping them in a REST API later would be straightforward.

### Why flat modules instead of packages?
With only 5 source files, nested packages add unnecessary navigation overhead. Each module has a single responsibility:
- `checker.py` — HIBP API interaction
- `generator.py` — password generation
- `scorer.py` — strength analysis (ML + heuristic)
- `config.py` — central constants
- `passmanager.py` — CLI wiring only

---

## Security Design

### K-Anonymity (HIBP)
When checking a password, we:
1. SHA-1 hash the password
2. Send only the first 5 hex characters of the hash
3. Receive a list of all matching hash suffixes + their breach counts
4. Compare locally — never send the full hash

This means even if the API server is compromised, it cannot recover the original password.

### Password Input
- Passwords can be passed as CLI args (convenient, visible in process list)
- Or prompted via `getpass` (hidden, secure)
- The `or` operator handles both: `password = args.password or getpass.getpass()`

### Generation Security
Uses `secrets.choice()` (cryptographically secure) instead of `random.choice()` (predictable). Ambiguous characters (`0`, `O`, `1`, `l`, `I`, `|`) are excluded to avoid visual confusion.

---

## ML Pipeline

### Data Collection (`training/build_dataset.py`)
1. Downloads 3000 common passwords from SecLists (10k-most-common.txt)
2. Queries HIBP API for each password's breach count
3. Generates 500 strong passwords (breach count = 0)
4. Saves as CSV with `password, breach_count` columns

### Feature Engineering (`training/features.py`)
Extracts 17 numeric features per password:

| Feature group | Examples | Purpose |
|---|---|---|
| Counts | `length`, `uppercase_count`, `digit_count` | Raw measures |
| Ratios | `lowercase_ratio`, `special_ratio` | Scale-invariant measures |
| Binary flags | `has_uppercase`, `has_digit` | Clean tree splits |
| Patterns | `sequential_runs`, `repeated_groups` | Detect common weakness patterns |
| Entropy | `entropy` | Information-theoretic randomness |

### Model Training (`training/train.py`)
- **Algorithm**: RandomForestRegressor (100 trees, max depth 15)
- **Target**: Breach count converted to score buckets (0/100 → 100, 1-99 → 80, 100-9999 → 50, 10000+ → 15)
- **Split**: 80/20 train-test with random seed 42
- **Metrics**: MAE 2.8 points, R² 0.94
- **Top features**: `length`, `has_uppercase`, `entropy`, `unique_chars`

### Why RandomForest?
- Handles non-linear relationships well
- Feature importance is interpretable (unlike neural networks)
- No scaling/normalization needed (unlike SVM or k-NN)
- Works well with small-to-medium datasets (1500-3500 samples)

### Why bucketed scores instead of raw breach counts?
Raw breach counts range from 0 to 23 million. Predicting such a wide range is difficult — the model's R² was -2.38 (worse than guessing the mean). Bucketing constrains the output to 4 values (15, 50, 80, 100), making the problem tractable.

### Hybrid approach: ML score + heuristic suggestions
- **Score**: Model predicts the strength number (data-driven, more accurate)
- **Suggestions**: Rule-based (`get_suggestions()` in scorer.py) — tells you *why* and *how to fix*

This is a common production pattern: use ML for the core prediction, use rules for the human-readable explanation.

---

## Key Trade-Offs

| Decision | Trade-off |
|---|---|
| ML for score, heuristic for issues | Score is more accurate; suggestions are reliable but generic |
| 3000 passwords from SecLists | Heavily skewed toward weak passwords; model is good at extremes but shaky in the middle |
| Flat project structure | Simple to navigate but can't grow into a large app without refactoring |
| CLI only | More portable than web app, but no API for integration |

---

## Resume-Worthy Talking Points

1. **End-to-end ML pipeline**: Data collection → feature engineering → training → deployment → inference
2. **K-anonymity implementation**: Security-aware design, not just a basic API wrapper
3. **Production-quality code**: Type hints, logging, docstrings, tests (32 passing), CI-ready
4. **Cross-platform**: Pure Python, no OS-specific dependencies, pip-installable
5. **Hybrid ML + rules**: Real-world pattern — pure ML is fragile for user-facing explanations

---

## Potential Improvements (Interview Fodder)

- **Better dataset**: Collect more medium-strength passwords for balanced training
- **Deep learning**: Try an LSTM or transformer that reads the password as a sequence
- **Model explainability**: Add SHAP or LIME to show *why* the model gave a specific score
- **Distributed checking**: Add async/parallel HIBP checking for bulk operations
- **Password vault**: Add encrypted local storage for managing multiple passwords
- **CI/CD**: GitHub Actions for auto-test + lint

---

## Glossary

| Term | Meaning |
|---|---|
| **R²** | Proportion of variance explained by the model. 1.0 = perfect, 0.0 = as good as guessing the mean. Negative = worse than guessing. |
| **MAE** | Mean Absolute Error. Average distance between predictions and true values. |
| **K-Anonymity** | Privacy model where data is indistinguishible from at least k-1 other individuals. HIBP uses k=5 (first 5 hash chars). |
| **SHA-1** | Cryptographic hash function. Used by HIBP for password lookup. |
| **RandomForest** | Ensemble of decision trees. Each tree votes, the forest averages their predictions. |
| **Shannon Entropy** | Measure of unpredictability. Higher entropy = harder to guess. |
