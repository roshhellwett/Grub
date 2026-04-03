"""GRUB theme installation and uninstallation logic."""

import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime

from projectgrub.constants import (
    BACKUP_DIR_NAME,
    GRUB_THEMES_DIR_FEDORA,
    GRUB_THEMES_DIR_STANDARD,
)
from projectgrub.exceptions import (
    GRUBConfigError,
    InstallationError,
    UninstallationError,
)
from projectgrub.theme_manager import Theme
from projectgrub.utils import (
    ensure_directory,
    get_grub_dir,
    get_grub_update_cmd,
    is_root,
    read_grub_config,
    run_command,
    write_grub_config,
)


@dataclass
class InstallationResult:
    """Result of a theme installation."""

    success: bool
    theme_name: str
    theme_path: str
    installed_path: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    backup_path: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


@dataclass
class UninstallationResult:
    """Result of a theme uninstallation."""

    success: bool
    removed_path: str | None = None
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class GRUBInstaller:
    """Handles GRUB theme installation and uninstallation."""

    def __init__(self):
        """Initialize GRUB installer."""
        self.grub_dir = get_grub_dir()
        self.update_cmd = get_grub_update_cmd()
        self._backup_data: str | None = None

    def is_ready(self) -> bool:
        """Check if installer is ready to perform operations."""
        return self.grub_dir is not None and self.update_cmd is not None

    def get_themes_dir(self) -> str:
        """Get the GRUB themes directory."""
        if self.grub_dir == "/boot/grub2/":
            return GRUB_THEMES_DIR_FEDORA
        return GRUB_THEMES_DIR_STANDARD

    def get_installed_theme_name(self) -> str | None:
        """Get the name of the currently installed theme."""
        try:
            lines = read_grub_config()
            for line in lines:
                if line.strip().startswith("GRUB_THEME="):
                    theme_path = line.split("=", 1)[1].strip().strip('"')
                    if "/themes/" in theme_path:
                        parts = theme_path.split("/themes/")
                        if len(parts) > 1:
                            return parts[1].split("/")[0]
        except Exception:
            pass
        return None

    def is_theme_installed(self, theme_name: str) -> bool:
        """Check if a specific theme is installed."""
        return self.get_installed_theme_name() == theme_name

    def _create_backup(self) -> str | None:
        """Create backup of current GRUB configuration."""
        try:
            config_path = "/etc/default/grub"
            backup_dir = os.path.join(os.path.dirname(config_path), BACKUP_DIR_NAME)
            ensure_directory(backup_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"grub_backup_{timestamp}")

            shutil.copy2(config_path, backup_path)
            return backup_path
        except (OSError, shutil.Error):
            return None

    def _restore_backup(self, backup_path: str) -> bool:
        """Restore GRUB configuration from backup."""
        try:
            config_path = "/etc/default/grub"
            shutil.copy2(backup_path, config_path)
            return True
        except (OSError, shutil.Error):
            return False

    def _update_grub_config(self, theme_path: str) -> None:
        """Update GRUB configuration with theme path."""
        try:
            lines = read_grub_config()
            theme_line = f'GRUB_THEME="{theme_path}"\n'
            found = False

            new_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("GRUB_THEME="):
                    new_lines.append(theme_line)
                    found = True
                elif stripped.startswith("#GRUB_THEME="):
                    uncommented = stripped.lstrip("#")
                    if uncommented.startswith("GRUB_THEME="):
                        new_lines.append(f"#{theme_line}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            if not found:
                new_lines.append(theme_line)

            write_grub_config(new_lines)
        except Exception as e:
            raise GRUBConfigError(f"Failed to update GRUB config: {e}") from e

    def _reset_grub_config(self) -> None:
        """Reset GRUB configuration by removing theme line."""
        try:
            lines = read_grub_config()
            new_lines = [line for line in lines if not line.strip().startswith("GRUB_THEME=")]
            write_grub_config(new_lines)
        except Exception as e:
            raise GRUBConfigError(f"Failed to reset GRUB config: {e}") from e

    def _copy_theme_files(self, source_path: str, theme_name: str) -> str:
        """Copy theme files to GRUB themes directory."""
        themes_dir = self.get_themes_dir()
        ensure_directory(themes_dir)

        target_path = os.path.join(themes_dir, theme_name)
        if os.path.exists(target_path):
            raise InstallationError(
                f"Theme '{theme_name}' already exists at {target_path}",
                suggestion="Uninstall the existing theme first.",
            )

        try:
            shutil.copytree(source_path, target_path)
            return target_path
        except (OSError, shutil.Error) as e:
            raise InstallationError(f"Failed to copy theme files: {e}") from e

    def _remove_theme_files(self, theme_name: str) -> None:
        """Remove theme files from GRUB themes directory."""
        themes_dir = self.get_themes_dir()
        theme_path = os.path.join(themes_dir, theme_name)

        if os.path.exists(theme_path):
            try:
                shutil.rmtree(theme_path)
            except OSError as e:
                raise UninstallationError(f"Failed to remove theme files: {e}") from e
        else:
            raise UninstallationError(f"Theme directory not found: {theme_path}")

    def _run_grub_update(self) -> None:
        """Run GRUB update command."""
        if not self.update_cmd:
            raise GRUBConfigError("GRUB update command not available")

        try:
            result = run_command(self.update_cmd, check=False, timeout=120)
            if result.returncode != 0:
                raise GRUBConfigError(
                    f"GRUB update failed with exit code {result.returncode}",
                    suggestion="Check GRUB configuration manually.",
                )
        except (RuntimeError, TimeoutError) as e:
            raise GRUBConfigError(f"GRUB update failed: {e}") from e

    def install(self, theme: Theme, auto_update: bool = True) -> InstallationResult:
        """Install a GRUB theme."""
        result = InstallationResult(
            success=False,
            theme_name=theme.name,
            theme_path=theme.path,
        )

        if not is_root():
            result.errors.append("Root privileges required for installation")
            return result

        if not self.is_ready():
            result.errors.append("GRUB is not properly configured on this system")
            return result

        backup_path = self._create_backup()
        if backup_path:
            result.backup_path = backup_path
        else:
            result.warnings.append("Could not create backup of GRUB config")

        try:
            installed_path = self._copy_theme_files(theme.path, theme.name)
            result.installed_path = installed_path

            theme_txt_path = os.path.join(installed_path, "theme.txt")
            self._update_grub_config(theme_txt_path)

            if auto_update:
                self._run_grub_update()

            result.success = True

        except InstallationError as e:
            result.errors.append(str(e))
            if backup_path and self._restore_backup(backup_path):
                result.warnings.append("Rolled back GRUB config changes")
            if result.installed_path and os.path.exists(result.installed_path):
                try:
                    shutil.rmtree(result.installed_path)
                except OSError:
                    pass

        except GRUBConfigError as e:
            result.errors.append(str(e))
            if backup_path and self._restore_backup(backup_path):
                result.warnings.append("Rolled back GRUB config changes")

        except Exception as e:
            result.errors.append(f"Unexpected error during installation: {e}")
            if backup_path and self._restore_backup(backup_path):
                result.warnings.append("Rolled back GRUB config changes")

        return result

    def uninstall(
        self,
        theme_name: str | None = None,
        auto_update: bool = True,
    ) -> UninstallationResult:
        """Uninstall a GRUB theme."""
        result = UninstallationResult(success=False)

        if not is_root():
            result.errors.append("Root privileges required for uninstallation")
            return result

        if theme_name is None:
            theme_name = self.get_installed_theme_name()

        if not theme_name:
            result.errors.append("No theme is currently installed")
            return result

        try:
            self._remove_theme_files(theme_name)
            result.removed_path = os.path.join(self.get_themes_dir(), theme_name)

            self._reset_grub_config()

            if auto_update:
                self._run_grub_update()

            result.success = True

        except UninstallationError as e:
            result.errors.append(str(e))

        except GRUBConfigError as e:
            result.errors.append(str(e))

        except Exception as e:
            result.errors.append(f"Unexpected error during uninstallation: {e}")

        return result

    def rollback(self, backup_path: str) -> bool:
        """Rollback to a previous GRUB configuration."""
        if not os.path.exists(backup_path):
            return False

        try:
            return self._restore_backup(backup_path)
        except Exception:
            return False

    def verify_installation(self, theme_name: str) -> bool:
        """Verify that a theme is properly installed."""
        theme_path = os.path.join(self.get_themes_dir(), theme_name)

        if not os.path.exists(theme_path):
            return False

        if not os.path.exists(os.path.join(theme_path, "theme.txt")):
            return False

        current_theme = self.get_installed_theme_name()
        return current_theme == theme_name


def get_installer() -> GRUBInstaller:
    """Get a GRUB installer instance."""
    return GRUBInstaller()
