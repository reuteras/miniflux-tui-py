"""Tests for configuration management."""


from miniflux_tui.config import validate_config


class TestValidateConfig:
    """Test configuration validation."""

    def test_valid_config(self, valid_config_dict):
        """Test validation of valid configuration."""
        is_valid, msg = validate_config(valid_config_dict)
        assert is_valid
        assert msg == "Configuration valid"

    def test_missing_server_url(self, valid_config_dict):
        """Test validation fails when server_url is missing."""
        del valid_config_dict["server_url"]
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "server_url" in msg

    def test_missing_api_key(self, valid_config_dict):
        """Test validation fails when api_key is missing."""
        del valid_config_dict["api_key"]
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "api_key" in msg

    def test_empty_server_url(self, valid_config_dict):
        """Test validation fails with empty server_url."""
        valid_config_dict["server_url"] = ""
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "non-empty" in msg.lower() or "empty" in msg.lower()

    def test_invalid_server_url_protocol(self, valid_config_dict):
        """Test validation fails with non-http(s) server_url."""
        valid_config_dict["server_url"] = "ftp://example.com"
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "http" in msg.lower()

    def test_server_url_with_http(self, valid_config_dict):
        """Test validation passes with http:// server_url."""
        valid_config_dict["server_url"] = "http://miniflux.local"
        is_valid, _ = validate_config(valid_config_dict)
        assert is_valid

    def test_empty_api_key(self, valid_config_dict):
        """Test validation fails with empty api_key."""
        valid_config_dict["api_key"] = ""
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "non-empty" in msg.lower() or "empty" in msg.lower()

    def test_short_api_key(self, valid_config_dict):
        """Test validation fails with api_key < 10 characters."""
        valid_config_dict["api_key"] = "short"
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "short" in msg.lower()

    def test_api_key_with_spaces(self, valid_config_dict):
        """Test validation fails when api_key is only whitespace."""
        valid_config_dict["api_key"] = "   "
        is_valid, _ = validate_config(valid_config_dict)
        assert not is_valid

    def test_invalid_sort_mode(self, valid_config_dict):
        """Test validation fails with invalid default_sort."""
        valid_config_dict["sorting"]["default_sort"] = "invalid"
        is_valid, msg = validate_config(valid_config_dict)
        assert not is_valid
        assert "default_sort" in msg

    def test_valid_sort_modes(self, valid_config_dict):
        """Test validation passes with all valid sort modes."""
        for sort_mode in ["date", "feed", "status"]:
            valid_config_dict["sorting"]["default_sort"] = sort_mode
            is_valid, _ = validate_config(valid_config_dict)
            assert is_valid, f"Failed for sort mode: {sort_mode}"

    def test_config_without_optional_fields(self):
        """Test validation of minimal valid config."""
        config = {
            "server_url": "https://miniflux.example.com",
            "api_key": "1234567890",
        }
        is_valid, _ = validate_config(config)
        assert is_valid
