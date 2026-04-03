"""Pre-flight system checks for ProjectGRUB."""

import os
import shutil
import sys
from dataclasses import dataclass, field

from projectgrub.exceptions import (
    SystemCheckError,
)
from projectgrub.utils import (
    check_disk_space,
    get_distro,
    get_grub_dir,
    get_grub_update_cmd,
    is_root,
)


@dataclass
class CheckResult:
    """Result of a single system check."""

    name: str
    passed: bool
    message: str
    suggestion: str | None = None
    critical: bool = True


@dataclass
class PreflightReport:
    """Complete pre-flight check report."""

    all_passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)

    @property
    def critical_failures(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed and c.critical]


def check_platform() -> CheckResult:
    """Check if running on Linux."""
    is_linux = sys.platform.startswith("linux")
    return CheckResult(
        name="Platform",
        passed=is_linux,
        message="Linux platform detected" if is_linux else "Non-Linux platform detected",
        suggestion="ProjectGRUB only works on Linux systems.",
        critical=True,
    )


def check_root() -> CheckResult:
    """Check if running with root privileges."""
    root = is_root()
    return CheckResult(
        name="Root Access",
        passed=root,
        message="Running as root" if root else "Not running as root",
        suggestion="Run with sudo or as root user.",
        critical=True,
    )


def check_grub_installed() -> CheckResult:
    """Check if GRUB is installed."""
    grub_dirs = ["/boot/grub", "/boot/grub2", "/usr/sbin/grub-mkconfig", "/usr/sbin/grub2-mkconfig"]
    found = any(os.path.exists(d) for d in grub_dirs)

    return CheckResult(
        name="GRUB Installed",
        passed=found,
        message="GRUB bootloader detected" if found else "GRUB not found on system",
        suggestion="Install GRUB bootloader first.",
        critical=True,
    )


def check_grub_directory() -> CheckResult:
    """Check if GRUB directory exists and is accessible."""
    grub_dir = get_grub_dir()
    if grub_dir and os.path.exists(grub_dir):
        return CheckResult(
            name="GRUB Directory",
            passed=True,
            message=f"GRUB directory found at {grub_dir}",
        )

    return CheckResult(
        name="GRUB Directory",
        passed=False,
        message="No GRUB themes directory found",
        suggestion="Check GRUB installation or mount /boot partition.",
        critical=True,
    )


def check_grub_update_command() -> CheckResult:
    """Check if GRUB update command is available."""
    cmd = get_grub_update_cmd()
    if cmd:
        cmd_name = cmd.split()[0]
        if shutil.which(cmd_name) or os.path.exists(f"/usr/sbin/{cmd_name}"):
            return CheckResult(
                name="GRUB Update Command",
                passed=True,
                message=f"GRUB update command available: {cmd}",
            )

    return CheckResult(
        name="GRUB Update Command",
        passed=False,
        message="GRUB update command not found",
        suggestion="Install or reinstall GRUB bootloader.",
        critical=True,
    )


def check_grub_config_readable() -> CheckResult:
    """Check if GRUB config file is readable."""
    config_path = "/etc/default/grub"
    if os.path.exists(config_path) and os.access(config_path, os.R_OK):
        return CheckResult(
            name="GRUB Config Readable",
            passed=True,
            message="GRUB config is readable",
        )

    return CheckResult(
        name="GRUB Config Readable",
        passed=False,
        message="Cannot read GRUB config file",
        suggestion="Check permissions on /etc/default/grub",
        critical=True,
    )


def check_grub_config_writable() -> CheckResult:
    """Check if GRUB config file is writable."""
    config_path = "/etc/default/grub"
    if os.access(config_path, os.W_OK):
        return CheckResult(
            name="GRUB Config Writable",
            passed=True,
            message="GRUB config is writable",
        )

    return CheckResult(
        name="GRUB Config Writable",
        passed=False,
        message="Cannot write to GRUB config file",
        suggestion="Run with sudo or as root user.",
        critical=True,
    )


def check_disk_space_available() -> CheckResult:
    """Check if there's enough disk space."""
    grub_dir = get_grub_dir() or "/boot"
    has_space = check_disk_space(grub_dir, min_mb=50)

    return CheckResult(
        name="Disk Space",
        passed=has_space,
        message="Sufficient disk space available" if has_space else "Low disk space",
        suggestion="Free up at least 50MB in /boot partition.",
        critical=False,
    )


def check_themes_directory_writable() -> CheckResult:
    """Check if GRUB themes directory is writable."""
    grub_dir = get_grub_dir()
    if not grub_dir:
        return CheckResult(
            name="Themes Directory",
            passed=False,
            message="No GRUB directory found",
            critical=True,
        )

    themes_dir = os.path.join(grub_dir, "themes")
    if os.path.exists(themes_dir):
        if os.access(themes_dir, os.W_OK):
            return CheckResult(
                name="Themes Directory",
                passed=True,
                message=f"Themes directory writable at {themes_dir}",
            )
    else:
        if os.access(grub_dir, os.W_OK):
            return CheckResult(
                name="Themes Directory",
                passed=True,
                message=f"Can create themes directory at {themes_dir}",
            )

    return CheckResult(
        name="Themes Directory",
        passed=False,
        message="Cannot write to themes directory",
        suggestion="Check permissions on /boot/grub/themes",
        critical=True,
    )


def check_distro_compatibility() -> CheckResult:
    """Check if distribution is known to be compatible."""
    distro = get_distro()
    known_distros = {
        "ubuntu",
        "debian",
        "arch",
        "manjaro",
        "fedora",
        "centos",
        "rhel",
        "opensuse",
        "opensuse-tumbleweed",
        "linuxmint",
        "pop",
        "elementary",
        "zorin",
        "kali",
        "gentoo",
    }

    compatible = distro in known_distros

    return CheckResult(
        name="Distro Compatibility",
        passed=True,
        message=f"Distribution detected: {distro}",
        suggestion=None if compatible else "Your distribution may not be fully compatible.",
        critical=False,
    )


def run_all_checks() -> PreflightReport:
    """Run all pre-flight checks."""
    checks = [
        check_platform(),
        check_root(),
        check_grub_installed(),
        check_grub_directory(),
        check_grub_update_command(),
        check_grub_config_readable(),
        check_grub_config_writable(),
        check_themes_directory_writable(),
        check_disk_space_available(),
        check_distro_compatibility(),
    ]

    critical_failures = [c for c in checks if not c.passed and c.critical]
    warnings = [c for c in checks if not c.passed and not c.critical]

    return PreflightReport(
        all_passed=len(critical_failures) == 0,
        checks=checks,
        warnings=[c.message for c in warnings],
    )


def validate_prerequisites(raise_on_failure: bool = True) -> PreflightReport:
    """Validate all prerequisites for ProjectGRUB."""
    report = run_all_checks()

    if raise_on_failure and not report.all_passed:
        failures = report.critical_failures
        if failures:
            error_messages = "\n".join(
                f"  - {f.name}: {f.message}" + (f" ({f.suggestion})" if f.suggestion else "")
                for f in failures
            )
            raise SystemCheckError(
                f"Pre-flight checks failed:\n{error_messages}",
                suggestion="Fix the above issues before running ProjectGRUB.",
            )

    return report
