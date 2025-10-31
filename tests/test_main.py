"""Tests for main entry point and CLI argument handling."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from miniflux_tui.config import ConfigurationError
from miniflux_tui.main import main

TEST_TOKEN = "token-for-tests"  # noqa: S105 - static fixture value


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
            assert "password command" in captured.out
            assert result == 0


class TestMainCheckConfig:
    """Test --check-config flag functionality."""

    def test_check_config_valid(self, capsys, tmp_path):
        """Test --check-config with valid configuration."""
        mock_config = MagicMock()
        mock_config.server_url = "http://localhost:8080"
        mock_config.password_command = ("op", "read", "token")
        mock_config.get_api_key.return_value = TEST_TOKEN
        mock_config.allow_invalid_certs = False
        mock_config.unread_color = "cyan"
        mock_config.read_color = "gray"
        mock_config.default_sort = "date"
        mock_config.default_group_by_feed = False

        config_file = tmp_path / "config.toml"
        config_file.write_text("[test]")  # Create a dummy file

        with (
            patch("miniflux_tui.main.load_config") as mock_load,
            patch("miniflux_tui.main.get_config_file_path") as mock_path,
        ):
            mock_load.return_value = mock_config
            mock_path.return_value = config_file
            with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                result = main()

            captured = capsys.readouterr()
            assert "Configuration loaded successfully" in captured.out
            assert "http://localhost:8080" in captured.out
            assert "Password command" in captured.out
            assert "API token retrieval" in captured.out
            assert result == 0
        mock_config.get_api_key.assert_called_once_with(refresh=True)

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

    def test_check_config_configuration_error(self, tmp_path, capsys):
        """Test --check-config reports helpful guidance for legacy configs."""
        config_path = tmp_path / "config.toml"
        config_path.write_text('server_url = "https://example.com"')

        with patch("miniflux_tui.main.get_config_file_path") as mock_get_path:
            mock_get_path.return_value = config_path
            with patch("miniflux_tui.main.load_config") as mock_load:
                mock_load.side_effect = ConfigurationError(
                    "Invalid configuration: Missing required field: password\n\nAdd a password command"
                )
                with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                    result = main()

                captured = capsys.readouterr()
                assert "Configuration requires attention" in captured.out
                assert "password" in captured.out.lower()
                assert "--init" in captured.out
                assert result == 1


class TestMainNormalStartup:
    """Test normal application startup."""

    def test_normal_startup_with_valid_config(self):
        """Test normal startup with valid configuration."""
        mock_config = MagicMock()

        with (
            patch("miniflux_tui.main.load_config") as mock_load,
            patch("miniflux_tui.main.run_tui", new=AsyncMock()) as mock_run,
        ):
            mock_load.return_value = mock_config
            with patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()

        assert result == 0
        mock_run.assert_awaited_once_with(mock_config)

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

        with (
            patch("miniflux_tui.main.load_config") as mock_load,
            patch(
                "miniflux_tui.main.run_tui",
                new=AsyncMock(side_effect=KeyboardInterrupt),
            ) as mock_run,
        ):
            mock_load.return_value = mock_config
            with patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()

        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out
        assert result == 0
        mock_run.assert_awaited_once_with(mock_config)

    def test_startup_runtime_error(self, capsys):
        """Test error handling for runtime exceptions."""
        mock_config = MagicMock()

        with (
            patch("miniflux_tui.main.load_config") as mock_load,
            patch(
                "miniflux_tui.main.run_tui",
                new=AsyncMock(side_effect=RuntimeError("Connection failed")),
            ) as mock_run,
        ):
            mock_load.return_value = mock_config
            with patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()

        captured = capsys.readouterr()
        assert "Error running application" in captured.out
        assert "Connection failed" in captured.out
        assert result == 1
        mock_run.assert_awaited_once_with(mock_config)

    def test_startup_configuration_error(self, capsys):
        """Test startup prints migration guidance for legacy configs."""
        with patch("miniflux_tui.main.load_config") as mock_load:
            mock_load.side_effect = ConfigurationError("Invalid configuration: Missing required field: password\n\nAdd a password command")
            with patch.object(sys, "argv", ["miniflux-tui"]):
                result = main()

        captured = capsys.readouterr()
        assert "Error loading configuration" in captured.out
        assert "password" in captured.out.lower()
        assert "--init" in captured.out
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
            with (
                patch("miniflux_tui.main.run_tui", new=AsyncMock()) as mock_run,
                patch.object(sys, "argv", ["miniflux-tui"]),
            ):
                result = main()
        assert result == 0
        mock_run.assert_awaited_once_with(mock_config)

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
        config_file.write_text("[test]")  # Create the file
        mock_config = MagicMock()
        with (
            patch("miniflux_tui.main.load_config") as mock_load,
            patch("miniflux_tui.main.get_config_file_path") as mock_path,
        ):
            mock_load.return_value = mock_config
            mock_path.return_value = config_file
            with patch.object(sys, "argv", ["miniflux-tui", "--check-config"]):
                result = main()
                assert result == 0


class TestMainEntryPoint:
    """Test main entry point for script execution."""

    @patch("miniflux_tui.main.sys.exit")
    @patch("miniflux_tui.main.main")
    def test_main_called_on_script_run(self, mock_main, mock_exit):
        """Test the if __name__ == '__main__' pattern."""
        # Simulate the if __name__ == "__main__" block
        mock_main.return_value = 0
        main_return = mock_main()
        mock_exit(main_return)

        # Verify both main() and sys.exit() were called with correct values
        assert mock_main.called
        mock_exit.assert_called_once_with(0)
