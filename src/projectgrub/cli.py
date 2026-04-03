"""Interactive CLI for ProjectGRUB."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from projectgrub import __version__
from projectgrub.constants import (
    BANNER_ART,
    PACKAGE_NAME,
    RESOLUTION_DISPLAY_NAMES,
    SUPPORTED_RESOLUTIONS,
)
from projectgrub.exceptions import SystemCheckError
from projectgrub.grub_installer import GRUBInstaller
from projectgrub.preflight import PreflightReport, run_all_checks, validate_prerequisites
from projectgrub.theme_manager import Theme, ThemeManager
from projectgrub.utils import (
    clear_screen,
    confirm,
    get_distro,
    get_grub_dir,
    get_terminal_width,
    is_root,
    pause,
    print_error,
    print_menu_header,
    print_success,
    safe_input,
    truncate_string,
)
from projectgrub.validators import validate_theme_structure

console = Console()

app = typer.Typer(
    name=PACKAGE_NAME,
    help="Interactive GRUB theme manager for Linux",
    add_completion=False,
)


class MenuState:
    """Manages menu state and navigation."""

    def __init__(self):
        self.theme_manager = ThemeManager()
        self.installer = GRUBInstaller()
        self.running = True
        self.preflight_report: PreflightReport | None = None

    def show_banner(self) -> None:
        """Show the application banner."""
        console.print(BANNER_ART)
        console.print(f"[dim]Version {__version__} | Made with love for Linux[/]")
        console.print()

    def show_welcome(self) -> None:
        """Show welcome message with system info."""
        distro = get_distro()
        grub_dir = get_grub_dir()
        installed_theme = self.installer.get_installed_theme_name()

        welcome_text = f"""
[bold cyan]Welcome to ProjectGRUB![/]

[dim]System Information:[/]
  [dim]Distribution:[/] {distro.title()}
  [dim]GRUB Directory:[/] {grub_dir or "[red]Not detected[/]"}
  [dim]Installed Theme:[/] {f"[green]{installed_theme}[/]" if installed_theme else "[yellow]None[/]"}

[dim]This tool helps you install and manage GRUB boot themes.[/]
"""

        panel = Panel(
            welcome_text.strip(),
            border_style="cyan",
            width=min(get_terminal_width(), 70),
        )
        console.print(panel)

    def run_preflight(self, verbose: bool = True) -> bool:
        """Run pre-flight checks and report results."""
        try:
            self.preflight_report = validate_prerequisites(raise_on_failure=False)
        except SystemCheckError:
            self.preflight_report = run_all_checks()

        if verbose:
            console.print()
            console.print("[bold cyan]System Checks:[/]")

            for check in self.preflight_report.checks:
                if check.passed:
                    console.print(f"  [green]+[/] {check.message}")
                else:
                    console.print(f"  [red]-[/] {check.message}")
                    if check.suggestion:
                        console.print(f"    [dim]-> {check.suggestion}[/]")

            console.print()
            if not self.preflight_report.all_passed:
                console.print(
                    "[yellow]Some checks failed. You may need to run as root or fix system issues.[/]"
                )

        return self.preflight_report.all_passed

    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        clear_screen()
        self.show_banner()
        self.show_welcome()

        installed_theme = self.installer.get_installed_theme_name()
        if installed_theme:
            console.print(f"  [dim]Current theme:[/] [cyan]{installed_theme}[/]")

        console.print()
        console.print("[bold cyan]Main Menu:[/]\n")

        menu_items = [
            ("1", "Browse Themes", "View all available GRUB themes"),
            ("2", "Quick Install", "Install a theme (recommended settings)"),
            ("3", "Advanced Install", "Choose resolution and custom options"),
            ("4", "Preview Theme", "View theme details and validation"),
            ("5", "Uninstall Theme", "Remove current GRUB theme"),
            ("6", "System Diagnostics", "Check GRUB health and compatibility"),
            ("7", "Theme Validation", "Validate a theme before install"),
            ("8", "Contribute Guide", "Learn how to add new themes"),
            ("9", "Refresh Themes", "Reload themes from disk"),
            ("10", "Help", "Documentation and tips"),
            ("0", "Exit", "Exit ProjectGRUB"),
        ]

        table = Table(box=None, show_header=False, padding=(0, 2))
        table.add_column("num", width=4)
        table.add_column("name", width=20)
        table.add_column("desc")

        for num, name, desc in menu_items:
            table.add_row(
                f"[yellow]{num}[/]",
                f"[bold white]{name}[/]",
                f"[dim]{desc}[/]",
            )

        console.print(table)
        console.print()

        return safe_input("Enter your choice: ", allow_empty=False)

    def handle_browse_themes(self) -> None:
        """Handle browse themes option."""
        clear_screen()
        print_menu_header("Browse Themes")

        available_resolutions = self.theme_manager.get_available_resolutions()

        console.print("[bold]Filter by Resolution:[/]")
        console.print("  [dim]0.[/] All Resolutions")
        for i, res in enumerate(available_resolutions, 1):
            display = RESOLUTION_DISPLAY_NAMES.get(res, res)
            console.print(f"  [dim]{i}.[/] {display}")
        console.print()

        choice = safe_input(
            f"Select resolution (0-{len(available_resolutions)}): ", allow_empty=True
        )

        resolution = None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_resolutions):
                resolution = available_resolutions[idx]

        themes = self.theme_manager.get_themes(resolution=resolution)

        if not themes:
            console.print("\n[yellow]No themes found.[/]")
            pause()
            return

        console.print(f"\n[bold cyan]Available Themes ({len(themes)}):[/]\n")

        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("#", width=3, style="dim")
        table.add_column("Theme", width=20)
        table.add_column("Resolution", width=15)
        table.add_column("Author", width=15)
        table.add_column("Status", width=10)
        table.add_column("Size", width=8)

        for i, theme in enumerate(themes, 1):
            status = "[green]Valid[/]" if theme.is_valid else "[yellow]Invalid[/]"
            author = theme.author or "[dim]Unknown[/]"
            size = f"{theme.size_mb:.1f} MB"

            table.add_row(
                str(i),
                truncate_string(theme.display_name, 18),
                theme.resolution_display,
                truncate_string(author, 13),
                status,
                size,
            )

        console.print(table)
        console.print()

        user_input = safe_input(
            "Enter number to preview (or press Enter to go back): ",
            allow_empty=True,
        )

        if user_input and user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(themes):
                self._show_theme_detail(themes[idx])

        pause()

    def _show_theme_detail(self, theme: Theme) -> None:
        """Show detailed information about a theme."""
        clear_screen()

        validation = theme.validation
        valid_status = "[green]Passed[/]" if validation and validation.valid else "[red]Failed[/]"

        console.print(f"\n[bold cyan]+{'-' * 50}+[/]")
        console.print(f"[bold cyan]|[/]  [bold]{theme.display_name}[/]")
        console.print(f"[bold cyan]+{'-' * 50}+[/]\n")

        console.print(f"[bold cyan]Resolution:[/] {theme.resolution_display}\n")
        console.print(f"[bold cyan]Path:[/] [dim]{theme.path}[/]\n")

        if theme.author:
            console.print(f"[bold cyan]Author:[/] {theme.author}\n")
        if theme.description:
            console.print(f"[bold cyan]Description:[/] {theme.description}\n")
        if theme.version:
            console.print(f"[bold cyan]Version:[/] {theme.version}\n")
        if theme.license:
            console.print(f"[bold cyan]License:[/] {theme.license}\n")

        console.print(f"[bold cyan]Validation:[/] {valid_status}")
        if validation:
            console.print(f"  [dim]Files:[/] {validation.file_count}")
            console.print(f"  [dim]Size:[/] {validation.total_size_mb:.2f} MB")
            if validation.warning_count > 0:
                console.print(f"  [yellow]Warnings:[/] {validation.warning_count}")
        console.print()

        if validation and validation.issues:
            console.print("[bold cyan]Validation Issues:[/]")
            for issue in validation.issues:
                severity = "[yellow]Warning[/]" if issue.severity == "warning" else "[red]Error[/]"
                msg = f"  {severity}: {issue.message}"
                if issue.file:
                    msg += f" ({issue.file}"
                    if issue.line:
                        msg += f":{issue.line}"
                    msg += ")"
                console.print(msg)
            console.print()

    def handle_quick_install(self) -> None:
        """Handle quick install option."""
        clear_screen()
        print_menu_header("Quick Install")

        if not is_root():
            console.print("\n[red]Error: Root privileges required.[/]")
            console.print("[dim]Please run with sudo or as root user.[/]\n")
            pause()
            return

        themes = self.theme_manager.get_themes(resolution="1080p", valid_only=True)

        if not themes:
            themes = self.theme_manager.get_themes(valid_only=True)

        if not themes:
            console.print("\n[yellow]No valid themes found.[/]\n")
            pause()
            return

        console.print("[bold]Select a theme to install:[/]\n")

        for i, theme in enumerate(themes[:10], 1):
            installed_marker = ""
            if self.installer.is_theme_installed(theme.name):
                installed_marker = " [green](installed)[/]"
            console.print(f"  [yellow]{i}.[/] {theme.display_name}{installed_marker}")

        console.print()
        choice = safe_input("Enter theme number: ", allow_empty=False)

        if not choice.isdigit():
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        idx = int(choice) - 1
        if idx < 0 or idx >= len(themes):
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        selected_theme = themes[idx]

        if self.installer.is_theme_installed(selected_theme.name):
            console.print(
                f"\n[yellow]Theme '{selected_theme.display_name}' is already installed.[/]\n"
            )
            pause()
            return

        console.print(f"\n[bold cyan]Ready to install:[/] {selected_theme.display_name}")
        console.print(f"[dim]Resolution:[/] {selected_theme.resolution_display}")
        console.print(f"[dim]Path:[/] {selected_theme.path}\n")

        console.print("[bold]This will:[/]")
        console.print("  1. Backup current GRUB configuration")
        console.print("  2. Copy theme files to /boot/grub/themes/")
        console.print("  3. Update /etc/default/grub")
        console.print("  4. Run grub-mkconfig\n")

        if confirm("Proceed with installation?", default=True):
            self._do_install(selected_theme)

        pause()

    def handle_advanced_install(self) -> None:
        """Handle advanced install with options."""
        clear_screen()
        print_menu_header("Advanced Install")

        if not is_root():
            console.print("\n[red]Error: Root privileges required.[/]")
            console.print("[dim]Please run with sudo or as root user.[/]\n")
            pause()
            return

        console.print("[bold]Step 1: Select Resolution[/]\n")
        for i, res in enumerate(SUPPORTED_RESOLUTIONS, 1):
            display = RESOLUTION_DISPLAY_NAMES.get(res, res)
            console.print(f"  [yellow]{i}.[/] {display}")

        console.print()
        res_choice = safe_input(
            f"Select resolution (1-{len(SUPPORTED_RESOLUTIONS)}): ", allow_empty=False
        )

        if not res_choice.isdigit():
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        idx = int(res_choice) - 1
        if idx < 0 or idx >= len(SUPPORTED_RESOLUTIONS):
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        resolution = SUPPORTED_RESOLUTIONS[idx]
        themes = self.theme_manager.get_themes(resolution=resolution)

        if not themes:
            console.print(f"\n[yellow]No themes found for {resolution} resolution.[/]\n")
            pause()
            return

        console.print(
            f"\n[bold]Step 2: Select Theme (Resolution: {RESOLUTION_DISPLAY_NAMES.get(resolution, resolution)})[/]\n"
        )

        for i, theme in enumerate(themes, 1):
            status = "[green]Valid[/]" if theme.is_valid else "[yellow]Invalid[/]"
            console.print(f"  [yellow]{i}.[/] {theme.display_name} {status}")

        console.print()
        theme_choice = safe_input(f"Select theme (1-{len(themes)}): ", allow_empty=False)

        if not theme_choice.isdigit():
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        idx = int(theme_choice) - 1
        if idx < 0 or idx >= len(themes):
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        selected_theme = themes[idx]

        console.print("\n[bold]Step 3: Summary[/]\n")
        console.print(f"[cyan]Theme:[/] {selected_theme.display_name}")
        console.print(f"[cyan]Resolution:[/] {selected_theme.resolution_display}")
        console.print(f"[cyan]Author:[/] {selected_theme.author or 'Unknown'}")
        console.print(f"[cyan]Path:[/] {selected_theme.path}")
        console.print()

        if confirm("Install this theme?", default=True):
            self._do_install(selected_theme)

        pause()

    def _do_install(self, theme: Theme) -> None:
        """Perform the actual installation."""
        console.print(f"\n[cyan]Installing {theme.display_name}...[/]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task_id = progress.add_task("Running pre-flight checks...", total=None)
            self.run_preflight(verbose=False)

            progress.update(task_id, description="Installing theme...")
            result = self.installer.install(theme, auto_update=True)

            progress.update(task_id, description="Complete!")

        console.print()
        if result.success:
            print_success(f"Successfully installed {theme.display_name}!")
            console.print(f"[dim]Theme installed at:[/] {result.installed_path}")
            console.print(f"[dim]Backup saved at:[/] {result.backup_path}")
            console.print()
            console.print("[yellow]Please reboot your system to see the new theme![/]")
        else:
            print_error("Installation failed!")
            for error in result.errors:
                console.print(f"  [red]• {error}[/]")
            if result.warnings:
                console.print()
                for warning in result.warnings:
                    console.print(f"  [yellow]• {warning}[/]")

    def handle_uninstall(self) -> None:
        """Handle uninstall option."""
        clear_screen()
        print_menu_header("Uninstall Theme")

        if not is_root():
            console.print("\n[red]Error: Root privileges required.[/]")
            console.print("[dim]Please run with sudo or as root user.[/]\n")
            pause()
            return

        installed_theme = self.installer.get_installed_theme_name()

        if not installed_theme:
            console.print("\n[yellow]No theme is currently installed.[/]\n")
            pause()
            return

        console.print(f"[bold cyan]Currently installed:[/] {installed_theme}\n")

        if confirm(f"Uninstall theme '{installed_theme}'?", default=False):
            result = self.installer.uninstall(auto_update=True)

            console.print()
            if result.success:
                print_success(f"Theme '{installed_theme}' uninstalled successfully!")
                console.print()
                console.print("[yellow]Please reboot to see the default GRUB theme.[/]")
            else:
                print_error("Uninstallation failed!")
                for error in result.errors:
                    console.print(f"  [red]• {error}[/]")

        console.print()
        pause()

    def handle_diagnostics(self) -> None:
        """Handle system diagnostics."""
        clear_screen()
        print_menu_header("System Diagnostics")

        console.print("\n[cyan]Running comprehensive system checks...[/]\n")

        self.run_preflight(verbose=True)

        console.print()
        console.print("[bold cyan]Additional Information:[/]\n")

        grub_dir = get_grub_dir()
        console.print(f"  [dim]GRUB Directory:[/] {grub_dir or '[red]Not found[/]'}")
        console.print(f"  [dim]User:[/] {'root' if is_root() else 'non-root'}")
        console.print(f"  [dim]Distribution:[/] {get_distro().title()}")

        themes_dir = self.installer.get_themes_dir()
        import os

        if os.path.exists(themes_dir):
            themes_count = len(
                [d for d in os.listdir(themes_dir) if os.path.isdir(os.path.join(themes_dir, d))]
            )
            console.print(f"  [dim]Installed themes:[/] {themes_count}")
        else:
            console.print("  [dim]Themes directory:[/] [red]Not found[/]")

        console.print()
        pause()

    def handle_theme_validation(self) -> None:
        """Handle theme validation."""
        clear_screen()
        print_menu_header("Theme Validation")

        themes = self.theme_manager.get_themes()

        if not themes:
            console.print("\n[yellow]No themes found.[/]\n")
            pause()
            return

        console.print("[bold]Select a theme to validate:[/]\n")

        for i, theme in enumerate(themes[:15], 1):
            status = "[green]Valid[/]" if theme.is_valid else "[yellow]Invalid[/]"
            console.print(f"  [yellow]{i}.[/] {theme.display_name} ({theme.resolution}) - {status}")

        console.print()
        choice = safe_input("Enter theme number: ", allow_empty=False)

        if not choice.isdigit():
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        idx = int(choice) - 1
        if idx < 0 or idx >= len(themes):
            console.print("\n[yellow]Invalid selection.[/]\n")
            pause()
            return

        selected_theme = themes[idx]

        console.print(
            f"\n[cyan]Validating:[/] {selected_theme.display_name} ({selected_theme.resolution})\n"
        )

        validation = validate_theme_structure(selected_theme.path, selected_theme.resolution)

        console.print(
            f"[bold]Validation Result:[/] {'[green]PASSED[/]' if validation.valid else '[red]FAILED[/]'}\n"
        )
        console.print(f"  [dim]Files:[/] {validation.file_count}")
        console.print(f"  [dim]Total Size:[/] {validation.total_size_mb:.2f} MB")
        console.print(f"  [dim]Errors:[/] {validation.error_count}")
        console.print(f"  [dim]Warnings:[/] {validation.warning_count}")
        console.print()

        if validation.issues:
            console.print("[bold]Issues Found:[/]")
            for issue in validation.issues:
                severity = "[yellow]Warning[/]" if issue.severity == "warning" else "[red]Error[/]"
                location = ""
                if issue.file:
                    location = f" ({issue.file}"
                    if issue.line:
                        location += f":{issue.line}"
                    location += ")"
                console.print(f"  {severity}: {issue.message}{location}")
            console.print()

        pause()

    def handle_contribute(self) -> None:
        """Show contribution guide."""
        clear_screen()
        print_menu_header("Contribute a Theme")

        guide = """
# How to Contribute a GRUB Theme

## Step 1: Create Theme Folder

Create a new folder in the `themes/` directory:

```bash
themes/your-theme-name/
```

## Step 2: Add Resolution Subfolders

Add subfolders for each resolution you support:

```bash
themes/your-theme-name/
├── 1080p/
│   ├── theme.txt
│   ├── background.png
│   └── ... (other assets)
├── 2k/
│   └── ...
└── 4k/
    └── ...
```

## Step 3: Create theme.txt

Create a `theme.txt` file with GRUB theme configuration:

```txt
title-text: ""
desktop-image: "background.png"
desktop-color: "#000000"
terminal-font: "Terminus Regular 14"
terminal-box: "terminal_box_*.png"
terminal-left: "0"
terminal-top: "0"
terminal-width: "100%"
terminal-height: "100%"

+ boot_menu {
  left = 30%
  top = 30%
  width = 45%
  height = 60%
  item_font = "Unifont Regular 16"
  item_color = "#cccccc"
  selected_item_color = "#ffffff"
  selected_item_pixmap_style = "select_*.png"
}
```

## Step 4: Add Optional Metadata

Create a `metadata.json` file:

```json
{
  "name": "Your Theme Name",
  "author": "Your Name",
  "description": "A beautiful GRUB theme",
  "version": "1.0.0",
  "license": "MIT"
}
```

## Step 5: Submit Your Theme

1. Fork the repository
2. Add your theme to the `themes/` folder
3. Create a pull request

Your theme will automatically appear in the menu!
"""
        md = Markdown(guide)
        console.print(md)
        pause()

    def handle_refresh(self) -> None:
        """Refresh theme list."""
        console.print("\n[cyan]Refreshing themes...[/]")
        self.theme_manager.refresh()
        themes = self.theme_manager.discover_themes()
        print_success(
            f"Found {len(themes.themes)} theme(s) in {len(themes.unique_names)} collection(s)"
        )
        console.print()

    def handle_help(self) -> None:
        """Show help and documentation."""
        clear_screen()
        print_menu_header("Help & Documentation")

        help_text = """
# ProjectGRUB Help

## Quick Start

```bash
# Install via pip (recommended)
pip install projectgrub

# Run the interactive menu
python -m projectgrub start

# Or if installed via pip
projectgrub
```

## Prerequisites

- Linux operating system
- GRUB bootloader installed
- Root/sudo privileges
- At least 50MB free space in /boot

## Common Issues

### "Root privileges required"
Run the command with sudo:
```bash
sudo python -m projectgrub start
```

### "GRUB not found"
Make sure GRUB is installed and /boot is mounted.

### "Theme not working after install"
1. Reboot your system
2. Check /etc/default/grub for GRUB_THEME line
3. Run `sudo grub-mkconfig` manually

## Menu Options

1. **Browse Themes** - View all available themes
2. **Quick Install** - Install with recommended settings
3. **Advanced Install** - Choose resolution and options
4. **Preview Theme** - View detailed theme information
5. **Uninstall Theme** - Remove current theme
6. **System Diagnostics** - Check system compatibility
7. **Theme Validation** - Validate a theme
8. **Contribute Guide** - How to add new themes
9. **Refresh Themes** - Reload themes from disk

## Distribution Support

Tested on:
- Ubuntu/Debian
- Arch/Manjaro
- Fedora/RHEL
- openSUSE

Other distributions may work but are not officially tested.
"""
        md = Markdown(help_text)
        console.print(md)
        pause()

    def run(self) -> None:
        """Run the main menu loop."""
        try:
            while self.running:
                try:
                    choice = self.show_main_menu()

                    handlers = {
                        "1": self.handle_browse_themes,
                        "2": self.handle_quick_install,
                        "3": self.handle_advanced_install,
                        "4": lambda: self.handle_browse_themes(),
                        "5": self.handle_uninstall,
                        "6": self.handle_diagnostics,
                        "7": self.handle_theme_validation,
                        "8": self.handle_contribute,
                        "9": self.handle_refresh,
                        "10": self.handle_help,
                        "0": self._exit,
                    }

                    handler = handlers.get(choice)
                    if handler:
                        handler()
                    else:
                        console.print("\n[yellow]Invalid choice. Please try again.[/]\n")
                        pause()

                except KeyboardInterrupt:
                    console.print("\n\n[yellow]Use '0' to exit.[/]\n")
                    pause()
                except SystemCheckError as e:
                    console.print(f"\n[red]System check failed:[/] {e.message}\n")
                    pause()

        except Exception as e:
            console.print(f"\n[red]An unexpected error occurred:[/] {e}\n")
            raise

    def _exit(self) -> None:
        """Exit the application."""
        self.running = False
        clear_screen()
        console.print()
        console.print("[cyan]Thank you for using ProjectGRUB![/]")
        console.print("[dim]Made with love for the Linux community[/]\n")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main entry point."""
    if ctx.invoked_subcommand is None:
        state = MenuState()
        state.run()


@app.command()
def start():
    """Launch the interactive menu."""
    state = MenuState()
    state.run()


@app.command()
def list():
    """List all available themes."""
    manager = ThemeManager()
    themes = manager.discover_themes()

    console.print()
    console.print("[bold cyan]Available Themes:[/]\n")

    if not themes.themes:
        console.print("[yellow]No themes found.[/]")
        return

    for name in themes.unique_names:
        theme_themes = themes.get_by_name(name)
        resolutions = [t.resolution for t in theme_themes]
        console.print(f"  [yellow]•[/] [bold]{name}[/] ({', '.join(resolutions)})")

    console.print()
    console.print(
        f"[dim]Total: {len(themes.themes)} themes in {len(themes.unique_names)} collections[/]"
    )


@app.command()
def info(theme_name: str):
    """Show information about a theme."""
    manager = ThemeManager()
    theme = manager.get_theme(theme_name)

    if not theme:
        console.print(f"[red]Theme '{theme_name}' not found.[/]")
        raise typer.Exit(1)

    console.print()
    console.print(f"[bold cyan]{theme.display_name}[/]")
    console.print(f"  Resolution: {theme.resolution_display}")
    console.print(f"  Path: {theme.path}")
    if theme.author:
        console.print(f"  Author: {theme.author}")
    if theme.description:
        console.print(f"  Description: {theme.description}")
    console.print(f"  Valid: {'[green]Yes[/]' if theme.is_valid else '[red]No[/]'}")
    console.print()


@app.command()
def check():
    """Run system checks without launching menu."""
    state = MenuState()
    state.run_preflight(verbose=True)


if __name__ == "__main__":
    app()
