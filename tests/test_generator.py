import string

from generator import generate_password


class TestGeneratePassword:
    def test_default_length(self) -> None:
        pw = generate_password()
        assert len(pw) == 16

    def test_custom_length(self) -> None:
        pw = generate_password(length=24)
        assert len(pw) == 24

    def test_has_lowercase(self) -> None:
        pw = generate_password()
        assert any(c.islower() for c in pw)

    def test_has_uppercase(self) -> None:
        pw = generate_password()
        assert any(c.isupper() for c in pw)

    def test_has_digits(self) -> None:
        pw = generate_password(min_digits=4)
        assert sum(c.isdigit() for c in pw) >= 4

    def test_has_special_chars(self) -> None:
        pw = generate_password(min_special=2)
        assert sum(c in string.punctuation for c in pw) >= 2

    def test_excludes_ambiguous_chars(self) -> None:
        pw = generate_password(exclude_ambiguous=True)
        assert not any(c in "0O1lI|" for c in pw)

    def test_unique_results(self) -> None:
        results = {generate_password() for _ in range(20)}
        assert len(results) == 20

    def test_minimal_length(self) -> None:
        pw = generate_password(length=4, min_digits=1, min_special=1)
        assert len(pw) == 4
