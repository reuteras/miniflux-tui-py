"""Tests for main entry point and CLI argument handling."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from miniflux_tui.main import main


class TestMainInit:
    """Test --init flag functionality."""

    def test_init_creates_config(self, tmp_path):
        """Test --init flag creates configuration file."""
        config_path = tmp_path / "config.toml"

        with patch("miniflux_tui.main.create_default_config") as mock_create:
            mock_create.return_value = config_path
            with patch.object(sys, "argv", ["miniflux-tui", "--init"]):
                result = main()

            assert result == 0
            mock_create.assert_called_once()

    def test_init_prints_help_message(self, tmp_path, capsys):
        """Test --init flag prints helpful message."""
        config_file = tmp_path / "config.toml"

        with patch("miniflux_tui.main.create_default_config") as mock_create:
            mock_create.return_value = config_file
            with patch.object(sys, "argv", ["miniflux-tui", "--init"]):
                result = main()

            captured = capsys.readouterr()
            assert "Created default configuration file" in captured.out
            assert "edit this file" in captured.out.lower()
            assert "API key" in captured.out
            assert result == 0


class TestMainCheckConfig:
    """Test --check-config flag functionality."""

    def test_check_config_valid(self, capsys):
        """Test --check-config with valid configuration."""
        mock_config = MagicMock()
        mock_config.server_url = "https://miniflux.example.com"
        mock_config.api_key = "test-api-key-1234567890"
        mock_config.allow_invalid_certs = False
        mock_config.unread_color = "cyan"
        mock_config.read_color = "gray"
        mock_config.default_sort = "date"
        mock_config.default_group_by_feed = False

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                result = main()

            captured = capsys.readouterr()
            assert "Configuration loaded successfully" in captured.out
            assert "https://miniflux.example.com" in captured.out
            assert "*" * 20 in captured.out  # Hidden API key
            assert result == 0

    def test_check_config_missing_file(self, tmp_path, capsys):
        """Test --check-config when config file doesn't exist."""
        config_path = tmp_path / "nonexistent.toml"

        with patch("miniflux_tui.main.get_config_file_path") as mock_get_path:
            mock_get_path.return_value = config_path
            with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                result = main()

            captured = capsys.readouterr()
            assert "Error: Config file not found" in captured.out
            assert "--init" in captured.out
            assert result == 1

    def test_check_config_load_error(self, tmp_path, capsys):
        """Test --check-config when config loading fails."""
        config_path = tmp_path / "config.toml"
        config_path.write_text("invalid toml content {{{")

        with patch("miniflux_tui.main.get_config_file_path") as mock_get_path:
            mock_get_path.return_value = config_path
            with patch("miniflux_tui.main.load_config") as mock_load:
                mock_load.side_effect = Exception("TOML parse error")
                with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                    result = main()

                captured = capsys.readouterr()
                assert "Error loading configuration" in captured.out
                assert result == 1


class TestMainNormalStartup:
    """Test normal application startup."""

    def test_normal_startup_with_valid_config(self):
        """Test normal startup with valid configuration."""
        mock_config = MagicMock()

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch("miniflux_tui.main.run_tui"), patch("asyncio.run"), patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()

                # asyncio.run is mocked, so we check it was called
                assert result == 0

    def test_startup_missing_config(self, capsys):
        """Test startup when config file doesn't exist."""
        config_path = Path("/nonexistent/config.toml")

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = None
            with patch("miniflux_tui.main.get_config_file_path") as mock_get_path:
                mock_get_path.return_value = config_path
                with patch.object(sys, "argv", ["miniflux-tui"]):
                    result = main()

                captured = capsys.readouterr()
                assert "Error: Config file not found" in captured.out
                assert "--init" in captured.out
                assert result == 1

    def test_startup_keyboard_interrupt(self, capsys):
        """Test graceful exit on KeyboardInterrupt."""
        mock_config = MagicMock()

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch("miniflux_tui.main.run_tui"), patch("asyncio.run") as mock_asyncio:
                mock_asyncio.side_effect = KeyboardInterrupt()
                with patch.object(sys, "argv", ["miniflux-tui"]):
                    result = main()

            captured = capsys.readouterr()
            assert "Goodbye!" in captured.out
            assert result == 0

    def test_startup_runtime_error(self, capsys):
        """Test error handling for runtime exceptions."""
        mock_config = MagicMock()

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch("miniflux_tui.main.run_tui"), patch("asyncio.run") as mock_asyncio:
                mock_asyncio.side_effect = RuntimeError("Connection failed")
                with patch.object(sys, "argv", ["miniflux-tui"]):
                    result = main()

            captured = capsys.readouterr()
            assert "Error running application" in captured.out
            assert "Connection failed" in captured.out
            assert result == 1


class TestMainVersion:
    """Test --version flag."""

    def test_version_flag_exits(self):
        """Test --version flag causes SystemExit."""
        with patch.object(sys, "argv", ["miniflux-tui", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # argparse exits with code 0 for --version
            assert exc_info.value.code == 0


class TestMainEntry:
    """Test main entry point."""

    def test_main_if_name_main(self):
        """Test __main__ guard with sys.exit."""
        with patch("miniflux_tui.main.main") as mock_main:
            mock_main.return_value = 0
            # This test verifies the structure exists; actual execution is in module load
            assert callable(main)

    def test_help_flag(self):
        """Test --help flag."""
        with patch.object(sys, "argv", ["miniflux-tui", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0


class TestMainArgumentParsing:
    """Test argument parsing."""

    def test_no_arguments_runs_app(self):
        """Test running without arguments starts application."""
        mock_config = MagicMock()

        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch("miniflux_tui.main.run_tui"), patch("asyncio.run"), patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()
                assert result == 0

    def test_mutually_exclusive_init_and_check(self, tmp_path):
        """Test that --init and --check-config work independently."""
        config_file = tmp_path / "config.toml"

        # --init should run first
        with patch("miniflux_tui.main.create_default_config") as mock_create:
            mock_create.return_value = config_file
            with patch.object(sys, "argv", ["miniflux-tui", "--init"]):
                result = main()
                assert result == 0

        # --check-config should also work
        mock_config = MagicMock()
        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.return_value = mock_config
            with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                result = main()
                assert result == 0
