"""Utility functions for ProjectGRUB."""

import os
import shutil
import subprocess
from pathlib import Path

from rich.console import Console

from projectgrub.constants import (
    CLEAR_SCREEN_CMD,
    ERROR_COLOR,
    INFO_COLOR,
    SUCCESS_COLOR,
    TERMINAL_WIDTH_DEFAULT,
    TERMINAL_WIDTH_MAX,
    WARNING_COLOR,
)

console = Console()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system(CLEAR_SCREEN_CMD)


def get_terminal_width() -> int:
    """Get the current terminal width."""
    try:
        size = shutil.get_terminal_size(fallback=(TERMINAL_WIDTH_DEFAULT, 24))
        return min(size.columns, TERMINAL_WIDTH_MAX)
    except (AttributeError, OSError):
        return TERMINAL_WIDTH_DEFAULT


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[{SUCCESS_COLOR}][OK][/] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[{ERROR_COLOR}][ERROR][/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[{WARNING_COLOR}][WARNING][/] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[{INFO_COLOR}][INFO][/] {message}")


def print_header(message: str) -> None:
    """Print a header message."""
    width = get_terminal_width()
    console.print()
    console.print(f"[bold cyan]{'=' * width}[/]")
    console.print(f"[bold cyan]|[/] {message.center(width - 4)} [bold cyan]|[/]")
    console.print(f"[bold cyan]{'=' * width}[/]")
    console.print()


def print_section(message: str) -> None:
    """Print a section header."""
    console.print()
    console.print(f"[bold cyan]{message}[/]")
    console.print(f"[dim]{'-' * len(message)}[/]")
    console.print()


def print_menu_header(message: str) -> None:
    """Print a menu header with border."""
    width = get_terminal_width()
    left = f"[bold cyan]+{'-' * (width - 2)}+[/]"
    middle = f"[bold cyan]|[/] [bold white]{message.center(width - 4)}[/] [bold cyan]|[/]"
    console.print()
    console.print(left)
    console.print(middle)
    console.print(left)
    console.print()


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def pause(message: str = "\nPress Enter to continue...") -> None:
    """Pause execution until user presses Enter."""
    try:
        input(f"[dim]{message}[/dim]")
    except (KeyboardInterrupt, EOFError):
        pass


def safe_input(prompt: str, allow_empty: bool = True) -> str:
    """Get user input safely, handling interrupts."""
    try:
        response = input(prompt).strip()
        if not response and not allow_empty:
            return ""
        return response
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n[yellow]Operation cancelled by user.[/]")
        return ""


def confirm(prompt: str, default: bool = True) -> bool:
    """Ask for user confirmation with a default."""
    default_str = "[Y/n]" if default else "[y/N]"
    try:
        response = input(f"{prompt} {default_str}: ").strip().lower()
        if not response:
            return default
        return response in ["y", "yes"]
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n[yellow]Operation cancelled by user.[/]")
        return False


def run_command(
    cmd: str,
    check: bool = True,
    capture_output: bool = True,
    timeout: int | None = 30,
) -> subprocess.CompletedProcess:
    """Run a shell command safely with error handling."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            check=check,
        )
        return result
    except subprocess.TimeoutExpired as err:
        raise TimeoutError(f"Command timed out after {timeout} seconds: {cmd}") from err
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed with exit code {e.returncode}: {cmd}") from e
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Command not found: {cmd}") from err


def is_root() -> bool:
    """Check if running as root."""
    if hasattr(os, "getuid"):
        return os.getuid() == 0
    try:
        result = subprocess.run(
            ["id", "-u"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() == "0"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_distro() -> str:
    """Get the current Linux distribution name."""
    try:
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"')
        result = subprocess.run(
            ["lsb_release", "-i"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.split(":")[-1].strip().lower()
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return "unknown"


def get_grub_dir() -> str | None:
    """Detect the GRUB directory based on distro."""
    if os.path.exists("/boot/grub/"):
        return "/boot/grub/"
    elif os.path.exists("/boot/grub2/"):
        return "/boot/grub2/"
    return None


def get_grub_update_cmd() -> str | None:
    """Get the GRUB update command based on distro."""
    grub_dir = get_grub_dir()
    if grub_dir == "/boot/grub/":
        return "grub-mkconfig -o /boot/grub/grub.cfg"
    elif grub_dir == "/boot/grub2/":
        return "grub2-mkconfig -o /boot/grub2/grub.cfg"
    return None


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_directory_size(path: str) -> int:
    """Get the total size of a directory in bytes."""
    total = 0
    try:
        for dirpath, _dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except (OSError, PermissionError):
        pass
    return total


def check_disk_space(path: str, min_mb: int = 50) -> bool:
    """Check if there's enough disk space available."""
    try:
        stat = os.statvfs(path)
        free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
        return free_mb >= min_mb
    except (AttributeError, OSError):
        try:
            import shutil as sh

            free_mb = sh.disk_usage(path).free / (1024 * 1024)
            return free_mb >= min_mb
        except Exception:
            return True


def ensure_directory(path: str) -> None:
    """Ensure a directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_grub_config() -> list[str]:
    """Read the GRUB config file and return lines."""
    config_path = "/etc/default/grub"
    try:
        with open(config_path) as f:
            return f.readlines()
    except FileNotFoundError as err:
        raise FileNotFoundError(f"GRUB config not found at {config_path}") from err
    except PermissionError as err:
        raise PermissionError(f"Permission denied reading {config_path}") from err


def write_grub_config(lines: list[str]) -> None:
    """Write lines to the GRUB config file."""
    config_path = "/etc/default/grub"
    try:
        with open(config_path, "w") as f:
            f.writelines(lines)
    except PermissionError as err:
        raise PermissionError(f"Permission denied writing to {config_path}") from err


def get_current_grub_theme() -> str | None:
    """Get the currently configured GRUB theme path."""
    try:
        lines = read_grub_config()
        for line in lines:
            if line.strip().startswith("GRUB_THEME="):
                theme_path = line.split("=", 1)[1].strip().strip('"')
                return theme_path
    except Exception:
        pass
    return None
