"""Tests for theme_manager module."""

import pytest
import os
from pathlib import Path


class TestThemeResolution:
    """Tests for ThemeResolution enum."""

    def test_resolution_from_string_valid(self):
        from projectgrub.theme_manager import ThemeResolution

        assert ThemeResolution.from_string("1080p") == ThemeResolution.RES_1080P
        assert ThemeResolution.from_string("2k") == ThemeResolution.RES_2K
        assert ThemeResolution.from_string("4k") == ThemeResolution.RES_4K

    def test_resolution_from_string_case_insensitive(self):
        from projectgrub.theme_manager import ThemeResolution

        assert ThemeResolution.from_string("1080P") == ThemeResolution.RES_1080P
        assert ThemeResolution.from_string("2K") == ThemeResolution.RES_2K

    def test_resolution_from_string_invalid(self):
        from projectgrub.theme_manager import ThemeResolution

        assert ThemeResolution.from_string("invalid") is None
        assert ThemeResolution.from_string("") is None

    def test_resolution_display_name(self):
        from projectgrub.theme_manager import ThemeResolution

        assert "1920x1080" in ThemeResolution.RES_1080P.display_name()
        assert "2560x1440" in ThemeResolution.RES_2K.display_name()
        assert "3840x2160" in ThemeResolution.RES_4K.display_name()


class TestTheme:
    """Tests for Theme dataclass."""

    def test_theme_creation(self):
        from projectgrub.theme_manager import Theme

        theme = Theme(
            name="test-theme",
            path="/path/to/theme",
            resolution="1080p",
            author="Test Author",
            description="A test theme",
        )

        assert theme.name == "test-theme"
        assert theme.path == "/path/to/theme"
        assert theme.resolution == "1080p"
        assert theme.author == "Test Author"

    def test_theme_display_name(self):
        from projectgrub.theme_manager import Theme

        theme = Theme(name="test-theme", path="/path", resolution="1080p")
        assert theme.display_name == "Test Theme"

        theme = Theme(name="test_theme", path="/path", resolution="1080p")
        assert theme.display_name == "Test Theme"

    def test_theme_default_resolution(self):
        from projectgrub.theme_manager import Theme

        theme = Theme(name="test", path="/path", resolution="")
        assert theme.resolution == "1080p"


class TestThemeCollection:
    """Tests for ThemeCollection."""

    def test_collection_by_resolution(self):
        from projectgrub.theme_manager import Theme, ThemeCollection

        themes = [
            Theme(name="a", path="/a/1080p", resolution="1080p"),
            Theme(name="a", path="/a/2k", resolution="2k"),
            Theme(name="b", path="/b/1080p", resolution="1080p"),
        ]

        collection = ThemeCollection(themes=themes)

        res_1080p = collection.get_by_resolution("1080p")
        assert len(res_1080p) == 2

        res_2k = collection.get_by_resolution("2k")
        assert len(res_2k) == 1

    def test_collection_unique_names(self):
        from projectgrub.theme_manager import Theme, ThemeCollection

        themes = [
            Theme(name="a", path="/a/1080p", resolution="1080p"),
            Theme(name="a", path="/a/2k", resolution="2k"),
            Theme(name="b", path="/b/1080p", resolution="1080p"),
        ]

        collection = ThemeCollection(themes=themes)
        assert len(collection.unique_names) == 2
        assert "a" in collection.unique_names
        assert "b" in collection.unique_names


class TestThemeManager:
    """Tests for ThemeManager."""

    def test_manager_initialization(self):
        from projectgrub.theme_manager import ThemeManager

        manager = ThemeManager()
        assert manager.themes_dir is not None

    def test_manager_finds_themes_dir(self):
        from projectgrub.theme_manager import ThemeManager

        manager = ThemeManager()
        assert os.path.exists(manager.themes_dir)

    def test_discover_themes(self):
        from projectgrub.theme_manager import ThemeManager

        manager = ThemeManager()
        collection = manager.discover_themes()

        assert isinstance(collection.themes, list)
