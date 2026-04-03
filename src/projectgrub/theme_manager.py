"""Theme management for ProjectGRUB."""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from projectgrub.constants import RESOLUTION_DISPLAY_NAMES, SUPPORTED_RESOLUTIONS
from projectgrub.validators import (
    ValidationResult,
    validate_theme_structure,
)


class ThemeResolution(Enum):
    """Supported GRUB theme resolutions."""

    RES_1080P = "1080p"
    RES_2K = "2k"
    RES_4K = "4k"

    def display_name(self) -> str:
        return RESOLUTION_DISPLAY_NAMES.get(self.value, self.value)

    @classmethod
    def from_string(cls, value: str) -> Optional["ThemeResolution"]:
        """Create resolution from string."""
        value_lower = value.lower()
        for res in cls:
            if res.value == value_lower:
                return res
        return None


@dataclass
class Theme:
    """Represents a GRUB theme."""

    name: str
    path: str
    resolution: str
    author: str | None = None
    description: str | None = None
    version: str | None = None
    license: str | None = None
    preview_image: str | None = None
    validation: ValidationResult | None = None

    def __post_init__(self):
        if not self.resolution:
            self.resolution = "1080p"

    @property
    def display_name(self) -> str:
        """Get display-friendly theme name."""
        return self.name.replace("-", " ").replace("_", " ").title()

    @property
    def resolution_display(self) -> str:
        """Get human-readable resolution."""
        res = ThemeResolution.from_string(self.resolution)
        if res:
            return res.display_name()
        return self.resolution

    @property
    def is_valid(self) -> bool:
        """Check if theme passed validation."""
        return self.validation is not None and self.validation.valid

    @property
    def size_mb(self) -> float:
        """Get theme size in MB."""
        if self.validation:
            return self.validation.total_size_mb
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "resolution": self.resolution,
            "author": self.author,
            "description": self.description,
            "version": self.version,
            "license": self.license,
        }


@dataclass
class ThemeCollection:
    """Collection of themes with grouping capabilities."""

    themes: list[Theme] = field(default_factory=list)

    def get_by_resolution(self, resolution: str) -> list[Theme]:
        """Get themes by resolution."""
        resolution_lower = resolution.lower()
        return [t for t in self.themes if t.resolution.lower() == resolution_lower]

    def get_by_name(self, name: str) -> list[Theme]:
        """Get themes by name (case-insensitive)."""
        name_lower = name.lower()
        return [
            t for t in self.themes if t.name.lower() == name_lower or name_lower in t.name.lower()
        ]

    def get_valid(self) -> list[Theme]:
        """Get only valid themes."""
        return [t for t in self.themes if t.is_valid]

    @property
    def unique_names(self) -> list[str]:
        """Get unique theme names."""
        seen = set()
        names = []
        for t in self.themes:
            if t.name not in seen:
                seen.add(t.name)
                names.append(t.name)
        return sorted(names)

    @property
    def resolution_counts(self) -> dict[str, int]:
        """Get count of themes per resolution."""
        counts = dict.fromkeys(SUPPORTED_RESOLUTIONS, 0)
        for t in self.themes:
            if t.resolution in counts:
                counts[t.resolution] += 1
        return counts


class ThemeManager:
    """Manages theme discovery and organization."""

    def __init__(self, themes_dir: str | None = None):
        """Initialize theme manager."""
        if themes_dir is None:
            self.themes_dir = self._find_themes_dir()
        else:
            self.themes_dir = themes_dir
        self._cache: ThemeCollection | None = None

    def _find_themes_dir(self) -> str:
        """Find the themes directory."""
        current = Path(__file__).parent

        themes_in_package = current / "themes"
        if themes_in_package.exists():
            return str(themes_in_package)

        project_root = current.parent.parent
        themes_path = project_root / "themes"
        if themes_path.exists():
            return str(themes_path)

        return str(themes_in_package)

    def discover_themes(self, force_refresh: bool = False) -> ThemeCollection:
        """Discover all themes in the themes directory."""
        if self._cache is not None and not force_refresh:
            return self._cache

        themes: list[Theme] = []

        if not os.path.exists(self.themes_dir):
            return ThemeCollection(themes=[])

        for theme_name in os.listdir(self.themes_dir):
            theme_base = os.path.join(self.themes_dir, theme_name)
            if not os.path.isdir(theme_base):
                continue

            metadata = self._load_metadata(theme_base)
            theme_resolutions = self._find_resolutions(theme_base)

            for resolution in theme_resolutions:
                theme_path = os.path.join(theme_base, resolution)
                if not os.path.exists(os.path.join(theme_path, "theme.txt")):
                    theme_path = self._find_theme_txt_dir(theme_base, resolution)

                if theme_path and os.path.exists(os.path.join(theme_path, "theme.txt")):
                    validation = validate_theme_structure(theme_path, resolution)
                    preview = self._find_preview_image(theme_path)

                    theme = Theme(
                        name=theme_name,
                        path=theme_path,
                        resolution=resolution,
                        author=metadata.get("author"),
                        description=metadata.get("description"),
                        version=metadata.get("version"),
                        license=metadata.get("license"),
                        preview_image=preview,
                        validation=validation,
                    )
                    themes.append(theme)

        self._cache = ThemeCollection(themes=themes)
        return self._cache

    def _load_metadata(self, theme_base: str) -> dict:
        """Load metadata from metadata.json."""
        metadata_path = os.path.join(theme_base, "metadata.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        return {}

    def _find_resolutions(self, theme_base: str) -> list[str]:
        """Find available resolutions for a theme."""
        resolutions = []
        for res in SUPPORTED_RESOLUTIONS:
            res_path = os.path.join(theme_base, res)
            if os.path.isdir(res_path):
                resolutions.append(res)

        if not resolutions:
            theme_txt = os.path.join(theme_base, "theme.txt")
            if os.path.exists(theme_txt):
                resolutions = ["1080p"]

        return resolutions if resolutions else ["1080p"]

    def _find_theme_txt_dir(self, theme_base: str, resolution: str) -> str | None:
        """Find directory containing theme.txt for given resolution."""
        for root, _dirs, files in os.walk(theme_base):
            if "theme.txt" in files:
                return root
        return None

    def _find_preview_image(self, theme_path: str) -> str | None:
        """Find preview image in theme directory."""
        for filename in ["preview.png", "preview.jpg", "background.png", "background.jpg"]:
            preview_path = os.path.join(theme_path, filename)
            if os.path.exists(preview_path):
                return preview_path
        return None

    def get_themes(
        self,
        resolution: str | None = None,
        valid_only: bool = False,
    ) -> list[Theme]:
        """Get themes with optional filtering."""
        collection = self.discover_themes()
        themes = collection.themes

        if resolution:
            themes = collection.get_by_resolution(resolution)

        if valid_only:
            themes = [t for t in themes if t.is_valid]

        return themes

    def get_theme(self, name: str, resolution: str | None = None) -> Theme | None:
        """Get a specific theme by name and optional resolution."""
        collection = self.discover_themes()
        matches = collection.get_by_name(name)

        if not matches:
            return None

        if resolution:
            for theme in matches:
                if theme.resolution.lower() == resolution.lower():
                    return theme

        return matches[0] if matches else None

    def search_themes(self, query: str) -> list[Theme]:
        """Search themes by name, author, or description."""
        collection = self.discover_themes()
        query_lower = query.lower()
        results = []

        for theme in collection.themes:
            if (
                query_lower in theme.name.lower()
                or (theme.author and query_lower in theme.author.lower())
                or (theme.description and query_lower in theme.description.lower())
            ):
                results.append(theme)

        return results

    def get_available_resolutions(self) -> list[str]:
        """Get list of resolutions that have themes."""
        collection = self.discover_themes()
        return [res for res, count in collection.resolution_counts.items() if count > 0]

    def refresh(self) -> None:
        """Clear cache and refresh theme discovery."""
        self._cache = None
        self.discover_themes(force_refresh=True)


def get_theme_manager(themes_dir: str | None = None) -> ThemeManager:
    """Get a singleton theme manager instance."""
    return ThemeManager(themes_dir)
