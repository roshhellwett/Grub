![img](https://img.shields.io/badge/Platform-Linux-2ea44f?style=for-the-badge&logo=linux&logoColor=white) 
![img](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![img](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![img](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)

# PROJECT GRUB

Interactive CLI tool that helps you browse, install, and manage GRUB boot themes on Linux. Instead of manually copying files and editing configurations, just run the menu and pick your theme.

---

## 🚀 Quick Start

### Step 1: Install Python
If you don't have Python, download it here: https://www.python.org/downloads/

### Step 2: Install ProjectGRUB
```bash
pip install projectgrub
```

### Step 3: Run the Interactive Menu
```bash
python -m projectgrub start
```

### Step 4: Update (Optional)
```bash
projectgrub update
```

That's it! The tool will guide you through everything.

---

## 📋 Installation Options

### Option 1: Install via pip (Recommended)
```bash
pip install projectgrub
projectgrub
```

### Option 2: Run from local clone
```bash
git clone https://github.com/zenithopensourceprojects/projectgrub.git
cd projectgrub
pip install -e .
projectgrub
```

### Option 3: Run without installing
```bash
git clone https://github.com/zenithopensourceprojects/projectgrub.git
cd projectgrub
pip install -e .
python -m projectgrub start
```

---

## 💻 CLI Commands

```bash
projectgrub start         # Launch interactive menu
projectgrub list          # List all available themes
projectgrub info <name>   # Show theme details
projectgrub update        # Update to latest version
```

---

## 🎯 Menu Options

| Option | Description |
|--------|-------------|
| **1. Browse Themes** | View all available GRUB themes with previews |
| **2. Quick Install** | Install a theme with recommended settings |
| **3. Advanced Install** | Choose resolution (1080p/2K/4K) and custom options |
| **4. Preview Theme** | View detailed theme information |
| **5. Uninstall Theme** | Remove current GRUB theme |
| **6. System Diagnostics** | Check GRUB health and compatibility |
| **7. Theme Validation** | Validate a theme before install |
| **8. Contribute Guide** | Learn how to add new themes |
| **9. Refresh Themes** | Reload themes from disk |
| **10. Help** | Documentation and tips |
| **U. Check Updates** | Check for new versions |
| **0. Exit** | Exit the application |

---

## 🛡️ Safety Features

### Pre-flight Checks
Before any operation, ProjectGRUB validates:
- ✅ Running on Linux
- ✅ Root privileges available
- ✅ GRUB installed
- ✅ GRUB directory accessible
- ✅ Write permissions available
- ✅ Sufficient disk space

### Rollback on Failure
If installation fails:
1. GRUB config is restored from backup
2. Partially copied files are removed
3. User receives clear error message with suggestions

---

## 🎨 Available Themes

The tool automatically discovers themes from the `themes/` folder. Current themes include:

| Theme | Author | Description |
|-------|--------|-------------|
| Vimix | Vimix | Clean, modern flat-design |
| Xenlism | Xenlism | Minimal and elegant |
| Tela | Tela | Minimalist aesthetics |
| Dark Matter | VandalByte | Dark and sleek |
| DedSec | VandalByte | Cyberpunk hacker style |

---

### "GRUB not found"
Make sure GRUB is installed and /boot is mounted.

### "Theme not working after install"
1. Reboot your system
2. Check /etc/default/grub for GRUB_THEME line
3. Run `sudo grub-mkconfig` manually

---

## 🙏 Credits

- GRUB Theme: [Vimix](https://github.com/vinceliuice/vimix-grub-themes)
- Dark Matter & DedSec: [VandalByte](https://gitlab.com/VandalByte)
- Xenlism: [Xenlism](https://github.com/xenlism)
- Tela: [Tela](https://github.com/vinceliuice/Tela-grub-theme)

---

© 2026 [Zenith Open Source Projects](https://zenithopensourceprojects.vercel.app/). All Rights Reserved. Zenith is an Open Source Project Idea by @roshhellwett
