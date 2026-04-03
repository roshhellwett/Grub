"""Tests for validators module."""

import pytest
import tempfile
import os


class TestThemeValidation:
    """Tests for theme validation."""

    def test_validate_resolution_name(self):
        from projectgrub.validators import validate_resolution_name

        assert validate_resolution_name("1080p") is True
        assert validate_resolution_name("2k") is True
        assert validate_resolution_name("4k") is True
        assert validate_resolution_name("invalid") is False
        assert validate_resolution_name("") is False

    def test_validate_theme_name(self):
        from projectgrub.validators import validate_theme_name

        assert validate_theme_name("valid-theme") is True
        assert validate_theme_name("valid_theme") is True
        assert validate_theme_name("Theme123") is True
        assert validate_theme_name("") is False
        assert validate_theme_name("test") is False
        assert validate_theme_name("..") is False

    def test_get_resolution_from_path(self):
        from projectgrub.validators import get_resolution_from_path

        assert get_resolution_from_path("/themes/theme/1080p/theme.txt") == "1080p"
        assert get_resolution_from_path("/themes/theme/2k/theme.txt") == "2k"
        assert get_resolution_from_path("/themes/theme/4k/theme.txt") == "4k"

    def test_validate_theme_structure_missing_directory(self):
        from projectgrub.validators import validate_theme_structure

        result = validate_theme_structure("/nonexistent/path", "1080p")

        assert result.valid is False
        assert result.error_count >= 1

    def test_validate_theme_txt_missing(self):
        from projectgrub.validators import validate_theme_structure

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "1080p"))
            result = validate_theme_structure(os.path.join(tmpdir, "1080p"), "1080p")

            assert result.valid is False
            assert result.error_count >= 1

    def test_validate_theme_txt_valid(self):
        from projectgrub.validators import validate_theme_structure

        with tempfile.TemporaryDirectory() as tmpdir:
            theme_dir = os.path.join(tmpdir, "1080p")
            os.makedirs(theme_dir)

            theme_txt = os.path.join(theme_dir, "theme.txt")
            with open(theme_txt, "w") as f:
                f.write('desktop-image: "background.png"\n')
                f.write('title-text: ""\n')
                f.write("+ boot_menu {\n")
                f.write("  left = 30%\n")
                f.write("}\n")

            result = validate_theme_structure(theme_dir, "1080p")

            assert result.valid is True
