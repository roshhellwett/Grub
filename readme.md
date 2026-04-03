<!-- 🧩 PROJECT GRUB README — By Rosh Hellwett -->

<h1 align="center">✨ PROJECT GRUB — GRUB Theme Manager ✨</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Linux-2ea44f?style=for-the-badge&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Stable-success?style=for-the-badge" />
</p>

---

<p align="center">
  <em>"The ultimate tool to customize your Linux boot loader." 💻🖌️</em>
</p>

---

## 🌟 Overview

**ProjectGRUB** is an interactive CLI tool that helps you browse, install, and manage GRUB boot themes on Linux. Instead of manually copying files and editing configurations, just run the menu and pick your theme.

## ✨ Features

- 🎨 **Browse Themes** - View all available GRUB themes with details
- 🚀 **Quick Install** - Install a theme in 3 clicks
- ⚙️ **Advanced Install** - Choose resolution (1080p, 2K, 4K) and options
- 🔍 **Theme Validation** - Verify themes before installing
- 🔧 **System Diagnostics** - Check GRUB health and compatibility
- 📦 **Auto-Discovery** - New themes appear automatically in the menu
- 🛡️ **Safe Operations** - Backup before changes, rollback on failure
- 💾 **Pre-flight Checks** - Validates system readiness before any operation

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

## 🤝 Contributing Themes

Want to add your own theme? Easy!

### Step 1: Create Theme Folder
```
themes/your-theme-name/
```

### Step 2: Add Resolution Subfolders
```
themes/your-theme-name/
├── 1080p/
│   ├── theme.txt
│   ├── background.png
│   └── ... assets
├── 2k/
│   └── ...
└── 4k/
    └── ...
```

### Step 3: Create theme.txt
```txt
title-text: ""
desktop-image: "background.png"
desktop-color: "#000000"
terminal-font: "Terminus Regular 14"
terminal-box: "terminal_box_*.png"

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

### Step 4: Add metadata.json (optional)
```json
{
  "name": "Your Theme Name",
  "author": "Your Name",
  "description": "A beautiful GRUB theme",
  "version": "1.0.0",
  "license": "MIT"
}
```

### Step 5: Submit
1. Fork the repository
2. Add your theme to the `themes/` folder
3. Create a pull request

Your theme will automatically appear in the menu!

---

## 🔧 CLI Commands

```bash
# Interactive menu
python -m projectgrub start

# List all themes
python -m projectgrub list

# Show theme info
python -m projectgrub info themename

# Run system checks
python -m projectgrub check
```

---

## 📋 Requirements

- Linux operating system
- Python 3.10 or higher
- GRUB bootloader installed
- Root/sudo privileges
- At least 50MB free space in /boot

### Supported Distributions
- Ubuntu / Debian
- Arch / Manjaro
- Fedora / RHEL
- openSUSE
- And other Linux distributions with GRUB

---

## 🐛 Troubleshooting

### "Root privileges required"
Run with sudo:
```bash
sudo python -m projectgrub start
```

### "GRUB not found"
Make sure GRUB is installed and /boot is mounted.

### "Theme not working after install"
1. Reboot your system
2. Check /etc/default/grub for GRUB_THEME line
3. Run `sudo grub-mkconfig` manually

---

## 📄 License

MIT License - See [LICENSE](license) file for details.

---

## 🙏 Credits

- GRUB Theme: [Vimix](https://github.com/vinceliuice/vimix-grub-themes)
- Dark Matter & DedSec: [VandalByte](https://gitlab.com/VandalByte)
- Xenlism: [Xenlism](https://github.com/xenlism)
- Tela: [Tela](https://github.com/vinceliuice/Tela-grub-theme)

---

© 2026 [Zenith Open Source Projects](https://zenithopensourceprojects.vercel.app/). All Rights Reserved.  
Zenith is an Open Source Project Idea by @roshhellwett
