from unittest.mock import patch

import pytest
import requests

from checker import _sha1_hash, check_breach


class TestSha1Hash:
    def test_returns_uppercase_hex(self) -> None:
        result = _sha1_hash("hello")
        assert result == "AAF4C61DDCC5E8A2DABEDE0F3B482CD9AEA9434D"

    def test_different_passwords_different_hashes(self) -> None:
        assert _sha1_hash("abc") != _sha1_hash("xyz")


class TestCheckBreach:
    @patch("checker.requests.get")
    def test_returns_count_when_hash_found(self, mock_get) -> None:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = (
            "0018A45C4D1DEF81644B54AB7F969B88D65:1\n"
            "00D4F6E8CB6C2DBB9F0C9C1C3B7E0A9B8C7:5\n"
        )

        count = check_breach("P@ssw0rd")
        assert count == 0

    @patch("checker.requests.get")
    def test_returns_zero_when_not_found(self, mock_get) -> None:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "SOMEOTH:999\nANOTHER:2\n"

        count = check_breach("not_breached_unique_xyz")
        assert count == 0

    @patch("checker.requests.get")
    def test_raises_on_network_error(self, mock_get) -> None:
        mock_get.side_effect = requests.ConnectionError("no network")

        with pytest.raises(ConnectionError):
            check_breach("anything")
