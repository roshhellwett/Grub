"""Custom exceptions for ProjectGRUB."""


class ProjectGRUBError(Exception):
    """Base exception for all ProjectGRUB errors."""

    def __init__(self, message: str, suggestion: str | None = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.suggestion:
            return f"{self.message}\n  Suggestion: {self.suggestion}"
        return self.message


class SystemCheckError(ProjectGRUBError):
    """Raised when a system pre-flight check fails."""

    pass


class ThemeValidationError(ProjectGRUBError):
    """Raised when theme validation fails."""

    pass


class PermissionError(ProjectGRUBError):
    """Raised when insufficient permissions."""

    pass


class GRUBConfigError(ProjectGRUBError):
    """Raised when GRUB configuration cannot be modified."""

    pass


class InstallationError(ProjectGRUBError):
    """Raised when installation fails."""

    pass


class RollbackError(ProjectGRUBError):
    """Raised when rollback during installation fails."""

    pass


class UninstallationError(ProjectGRUBError):
    """Raised when uninstallation fails."""

    pass


class DiskSpaceError(ProjectGRUBError):
    """Raised when there's insufficient disk space."""

    pass


class ThemeNotFoundError(ProjectGRUBError):
    """Raised when a requested theme is not found."""

    pass


class UnsupportedPlatformError(ProjectGRUBError):
    """Raised when running on unsupported platform."""

    pass
