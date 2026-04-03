"""Constants and configuration for ProjectGRUB."""

import sys

PACKAGE_NAME = "projectgrub"
PACKAGE_VERSION = "1.0.0"
PACKAGE_AUTHOR = "Roshan Kr Singh - Zenith Open Source Projects"

IS_LINUX = sys.platform.startswith("linux")
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

TERMINAL_WIDTH_DEFAULT = 80
TERMINAL_WIDTH_MAX = 120
MENU_WIDTH = 70

SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
INFO_COLOR = "cyan"
BORDER_COLOR = "cyan"
HEADER_COLOR = "bold cyan"

CLEAR_SCREEN_CMD = "clear"
if IS_WINDOWS:
    CLEAR_SCREEN_CMD = "cls"

GRUB_THEMES_DIR_STANDARD = "/boot/grub/themes/"
GRUB_THEMES_DIR_FEDORA = "/boot/grub2/themes/"

GRUB_CONFIG_FILE = "/etc/default/grub"

GRUB_UPDATE_CMD_STANDARD = "grub-mkconfig -o /boot/grub/grub.cfg"
GRUB_UPDATE_CMD_FEDORA = "grub2-mkconfig -o /boot/grub2/grub.cfg"

SUPPORTED_RESOLUTIONS = ["1080p", "2k", "4k"]

RESOLUTION_DISPLAY_NAMES = {
    "1080p": "Full HD (1920x1080)",
    "2k": "QHD (2560x1440)",
    "4k": "UHD (3840x2160)",
}

MIN_DISK_SPACE_MB = 50

BANNER = r"""
    ____       __             ____
   / __ \___  / /__________  / __ \_      ______  ___  _____
  / /_/ / _ \/ __/ ___/ __ \/ / / / | /| / / __ \/ _ \/ ___/
 / _, _/  __/ /_/ /  / /_/ / /_/ /| |/ |/ / / / /  __/ /
/_/ |_|\___/\__/_/   \____/\____/ |__/|__/_/ /_/\___/_/
"""

BANNER_ART = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]              [bold white]ProjectGRUB - GRUB Theme Manager[/]                 [bold cyan]║[/]
[bold cyan]╠══════════════════════════════════════════════════════════════╣[/]
[bold cyan]║[/]  [dim]The ultimate tool to customize your Linux boot loader[/]       [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/]
"""

REQUIRED_THEME_FILES = ["theme.txt"]

REQUIRED_THEME_TXT_FIELDS = ["desktop-image"]

INSTALLATION_STEPS = [
    "Running pre-flight checks",
    "Creating backup of current GRUB configuration",
    "Validating theme integrity",
    "Copying theme files to GRUB themes directory",
    "Updating GRUB configuration",
    "Verifying installation",
]

BACKUP_DIR_NAME = ".projectgrub_backups"
