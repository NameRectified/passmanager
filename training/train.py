import csv
import logging
import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from training.features import FEATURE_NAMES, extract_features

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


def breach_to_score(count: int) -> int:
    """Convert a raw breach count to a 0–100 strength score.

    Bounding the target this way makes training much easier than
    predicting raw counts (which range from 0 to millions).

    Args:
        count: Number of times the password appeared in breaches.

    Returns:
        A score from 0–100 (higher = stronger).
    """
    if count == 0:
        return 100
    if count < 100:
        return 80
    if count < 10000:
        return 50
    return 15


def load_data(path: Path) -> tuple[list[dict], list[int]]:
    """Read the CSV dataset and return features + target scores.

    Args:
        path: Path to the CSV file with password,breach_count columns.

    Returns:
        X_raw: List of feature dicts (one per password).
        y: List of target scores (0–100).
    """
    X_raw: list[dict] = []
    y: list[int] = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = extract_features(row["password"])
            X_raw.append(features)
            y.append(breach_to_score(int(row["breach_count"])))
    return X_raw, y


def to_matrix(X_raw: list[dict]) -> list[list[float]]:
    """Convert a list of feature dicts to a 2D list (rows × columns).

    The column order matches FEATURE_NAMES so the model sees consistent input.
    """
    return [[row[name] for name in FEATURE_NAMES] for row in X_raw]


def main() -> None:
    """Train a RandomForest model to predict password strength scores."""
    data_path = DATA_DIR / "passwords.csv"
    logger.info(f"Loading data from {data_path}...")
    X_raw, y = load_data(data_path)
    X = to_matrix(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info(f"Training on {len(X_train)} samples, testing on {len(X_test)}...")
    model = RandomForestRegressor(
        n_estimators=100,  # 100 decision trees
        max_depth=15,      # limit depth to avoid overfitting
        random_state=42,   # reproducible results
        n_jobs=-1,         # use all CPU cores
    )
    model.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logger.info(f"MAE: {mae:.1f} points, R2: {r2:.3f}")

    feature_importances = sorted(
        zip(FEATURE_NAMES, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True,
    )
    logger.info("Top 5 features:")
    for name, imp in feature_importances[:5]:
        logger.info(f"  {name}: {imp:.3f}")

    # Save the trained model so scorer.py can load it at runtime
    model_path = MODELS_DIR / "strength_model.pkl"
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    main()
