"""ProjectGRUB - Interactive GRUB theme manager for Linux."""

import logging

__version__ = "1.0.0"
__author__ = "Roshan Kr Singh"
__email__ = "roshellwett@icloud.com"

from projectgrub.exceptions import (
    GRUBConfigError,
    InstallationError,
    PermissionError,
    ProjectGRUBError,
    RollbackError,
    SystemCheckError,
    ThemeValidationError,
)
from projectgrub.grub_installer import GRUBInstaller, InstallationResult
from projectgrub.theme_manager import Theme, ThemeManager, ThemeResolution

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "ProjectGRUBError",
    "SystemCheckError",
    "ThemeValidationError",
    "PermissionError",
    "GRUBConfigError",
    "InstallationError",
    "RollbackError",
    "ThemeManager",
    "Theme",
    "ThemeResolution",
    "GRUBInstaller",
    "InstallationResult",
]
