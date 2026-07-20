from pathlib import Path

import pytest

from scorer import analyze_password, _load_model


class TestModelLoading:
    def test_model_file_exists(self) -> None:
        model_path = Path(__file__).parent.parent / "models" / "strength_model.pkl"
        assert model_path.exists(), "Trained model not found — run training/train.py first"

    def test_model_loads_successfully(self) -> None:
        model = _load_model()
        assert model is not None

    def test_model_has_feature_importances(self) -> None:
        model = _load_model()
        assert hasattr(model, "feature_importances_")
        assert len(model.feature_importances_) == 17


class TestMLScoring:
    @pytest.fixture(autouse=True)
    def ensure_model(self) -> None:
        if _load_model() is None:
            pytest.skip("Model not found — run training/train.py first")

    def test_weak_password_scores_low(self) -> None:
        result = analyze_password("123456")
        assert result["score"] < 40
        assert result["strength"] == "weak"

    def test_strong_password_scores_high(self) -> None:
        result = analyze_password("Kd9#mP2$xL8@qR5zA7&")
        assert result["score"] >= 80
        assert result["strength"] in ("strong", "very_strong")

    def test_score_is_within_bounds(self) -> None:
        for pw in ["a", "abc", "password", "Hello123!", "Kd9#mP2$xL8@qR5zA7&"]:
            result = analyze_password(pw)
            assert 0 <= result["score"] <= 100

    def test_issues_are_returned(self) -> None:
        result = analyze_password("abc")
        assert isinstance(result["issues"], list)
        assert len(result["issues"]) > 0
