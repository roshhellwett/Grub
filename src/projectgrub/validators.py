"""Theme validation for ProjectGRUB."""

import os
import re
from dataclasses import dataclass, field

from projectgrub.constants import REQUIRED_THEME_FILES, SUPPORTED_RESOLUTIONS


@dataclass
class ValidationIssue:
    """A validation issue found in a theme."""

    severity: str
    message: str
    file: str | None = None
    line: int | None = None


@dataclass
class ValidationResult:
    """Result of theme validation."""

    valid: bool
    theme_name: str
    resolution: str
    issues: list[ValidationIssue] = field(default_factory=list)
    file_count: int = 0
    total_size_mb: float = 0.0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


def validate_theme_structure(theme_path: str, resolution: str) -> ValidationResult:
    """Validate the structure of a theme."""
    theme_name = os.path.basename(os.path.dirname(theme_path))
    issues: list[ValidationIssue] = []

    if not os.path.exists(theme_path):
        return ValidationResult(
            valid=False,
            theme_name=theme_name,
            resolution=resolution,
            issues=[
                ValidationIssue(
                    severity="error",
                    message=f"Theme directory not found: {theme_path}",
                )
            ],
        )

    theme_txt = os.path.join(theme_path, "theme.txt")
    if not os.path.exists(theme_txt):
        issues.append(
            ValidationIssue(
                severity="error",
                message="theme.txt not found in theme directory",
                file="theme.txt",
            )
        )
        return ValidationResult(
            valid=False,
            theme_name=theme_name,
            resolution=resolution,
            issues=issues,
        )

    file_count = 0
    total_size = 0
    for _root, _dirs, files in os.walk(theme_path):
        file_count += len(files)
        for f in files:
            filepath = os.path.join(_root, f)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass

    for req_file in REQUIRED_THEME_FILES:
        if req_file == "theme.txt":
            continue
        if not any(req_file.replace("*", "") in f for f in os.listdir(theme_path)):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Recommended file pattern not found: {req_file}",
                )
            )

    theme_txt_issues = validate_theme_txt(theme_txt)
    issues.extend(theme_txt_issues)

    valid = all(i.severity != "error" for i in issues)

    return ValidationResult(
        valid=valid,
        theme_name=theme_name,
        resolution=resolution,
        issues=issues,
        file_count=file_count,
        total_size_mb=total_size / (1024 * 1024),
    )


def validate_theme_txt(theme_txt_path: str) -> list[ValidationIssue]:
    """Validate theme.txt file content."""
    issues: list[ValidationIssue] = []
    required_fields = ["desktop-image"]

    try:
        with open(theme_txt_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
    except FileNotFoundError:
        issues.append(
            ValidationIssue(
                severity="error",
                message="theme.txt file not found",
                file="theme.txt",
            )
        )
        return issues
    except UnicodeDecodeError:
        issues.append(
            ValidationIssue(
                severity="error",
                message="theme.txt is not valid UTF-8",
                file="theme.txt",
            )
        )
        return issues

    found_fields = set()
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        for field_name in required_fields:
            if line.startswith(field_name):
                found_fields.add(field_name)
                break

        if ":" not in line and not line.startswith("+"):
            if not any(
                line.startswith(x) for x in ["desktop-image", "terminal-font", "title-text"]
            ):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message="Potentially malformed line",
                        file="theme.txt",
                        line=i,
                    )
                )

    for field_name in required_fields:
        if field_name not in found_fields:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    message=f"Recommended field missing: {field_name}",
                    file="theme.txt",
                )
            )

    has_boot_menu = "+ boot_menu" in content or "boot_menu" in content
    if not has_boot_menu:
        issues.append(
            ValidationIssue(
                severity="warning",
                message="boot_menu component not defined",
                file="theme.txt",
            )
        )

    return issues


def validate_resolution_name(resolution: str) -> bool:
    """Check if resolution name is valid."""
    return resolution.lower() in [r.lower() for r in SUPPORTED_RESOLUTIONS]


def get_resolution_from_path(theme_path: str) -> str | None:
    """Extract resolution from theme path."""
    path_lower = theme_path.lower()
    for res in SUPPORTED_RESOLUTIONS:
        if res in path_lower:
            return res

    parent_dir = os.path.basename(os.path.dirname(theme_path))
    if validate_resolution_name(parent_dir):
        return parent_dir

    return None


def check_theme_assets(theme_path: str) -> list[ValidationIssue]:
    """Check if theme has all required assets."""
    issues: list[ValidationIssue] = []

    required_patterns = [
        ("background", ["background.png", "background.jpg"]),
        ("select", ["select_"]),
        ("terminal_box", ["terminal_box_"]),
    ]

    all_files = []
    for _root, _dirs, files in os.walk(theme_path):
        all_files.extend(files)

    for pattern_name, patterns in required_patterns:
        if pattern_name == "background":
            if not any(any(p in f for p in patterns) for f in all_files):
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Background image not found (expected: {', '.join(patterns)})",
                    )
                )
        else:
            matching = [f for f in all_files if any(p in f for p in patterns)]
            if not matching:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        message=f"Asset pattern '{pattern_name}' not found (expected: {patterns[0]}*)",
                    )
                )

    return issues


def validate_theme_name(name: str) -> bool:
    """Validate theme name format."""
    if not name:
        return False

    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", name):
        return False

    forbidden = ["test", "tmp", "temp", "backup", ".", ".."]
    return name.lower() not in forbidden


def get_theme_metadata(theme_path: str) -> dict:
    """Get theme metadata from metadata.json if exists."""
    metadata_path = os.path.join(theme_path, "..", "metadata.json")
    if os.path.exists(metadata_path):
        try:
            import json

            with open(metadata_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
    return {}
