from scorer import analyze_password, get_suggestions


class TestAnalyzePassword:
    def test_short_password_is_weak(self) -> None:
        result = analyze_password("ab")
        assert result["score"] <= 20
        assert result["strength"] == "weak"
        assert "too_short" in result["issues"]

    def test_long_and_diverse_is_very_strong(self) -> None:
        result = analyze_password("Kd9#mP2$xL8@qR5zA7&")
        assert result["score"] >= 70
        assert result["strength"] in ("strong", "very_strong")

    def test_detects_missing_uppercase(self) -> None:
        result = analyze_password("abcdef123!")
        assert "no_uppercase" in result["issues"]

    def test_detects_missing_digit(self) -> None:
        result = analyze_password("Abcdefgh!")
        assert "no_digit" in result["issues"]

    def test_detects_missing_special(self) -> None:
        result = analyze_password("Abcdef123")
        assert "no_special" in result["issues"]

    def test_detects_sequential_chars(self) -> None:
        result = analyze_password("abcXYZ789!")
        assert "sequential_chars" in result["issues"]

    def test_detects_repeated_chars(self) -> None:
        result = analyze_password("Aaaabc123!")
        assert any(i.startswith("repeated_char_") for i in result["issues"])


class TestGetSuggestions:
    def test_breach_suggestion_included(self) -> None:
        analysis = {"score": 30, "strength": "weak", "issues": ["too_short"]}
        suggestions = get_suggestions("abc", breach_count=50, analysis=analysis)
        assert any("breach" in s.lower() for s in suggestions)

    def test_no_breach_suggestion_when_zero(self) -> None:
        analysis = {"score": 95, "strength": "very_strong", "issues": []}
        suggestions = get_suggestions("Str0ng!Pass#", breach_count=0, analysis=analysis)
        assert not any("breach" in s.lower() for s in suggestions)

    def test_max_five_suggestions(self) -> None:
        analysis = {
            "score": 10,
            "strength": "weak",
            "issues": [
                "too_short",
                "no_uppercase",
                "no_digit",
                "no_special",
                "sequential_chars",
            ],
        }
        suggestions = get_suggestions("abc", breach_count=100, analysis=analysis)
        assert len(suggestions) <= 5

    def test_suggestions_are_strings(self) -> None:
        analysis = {"score": 50, "strength": "fair", "issues": ["no_uppercase"]}
        suggestions = get_suggestions("hello", breach_count=0, analysis=analysis)
        assert all(isinstance(s, str) for s in suggestions)
