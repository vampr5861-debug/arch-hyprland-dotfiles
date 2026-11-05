<div align="center">

# MOMO · Hyprland Dotfiles

**A minimal, dark Arch Linux desktop built around Hyprland.**

A personal setup focused on a clean layout, compact tools, subtle animations and keyboard-driven workflows.

![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?style=flat-square&logo=archlinux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-Lua%20config-58E1FF?style=flat-square)
![Waybar](https://img.shields.io/badge/Waybar-Custom-222222?style=flat-square)
![Setup](https://img.shields.io/badge/Setup-Manual-555555?style=flat-square)

[Preview](#preview) · [Features](#features) · [Installation](docs/INSTALLATION.md) · [Keybindings](docs/KEYBINDINGS.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

</div>

---

## Preview

### Desktop · Fastfetch

[![Hyprland desktop with Kitty and Fastfetch](screenshots/desktop-fastfetch.png)](screenshots/desktop-fastfetch.png)

<sub>Arch Linux · Hyprland · Waybar · Kitty · Fastfetch</sub>

### Waypaper · Wallpaper gallery

[![Waypaper wallpaper gallery](screenshots/waypaper-overview.png)](screenshots/waypaper-overview.png)

### Rofi · Application launcher

[![Rofi application launcher](screenshots/rofi-launcher.png)](screenshots/rofi-launcher.png)

> Screenshots show the actual desktop. Third-party wallpapers visible in them are not included in this repository.

## Features

| Component | Setup |
| :--- | :--- |
| **Window manager** | Hyprland, Lua configuration, Dwindle layout |
| **Status bar** | Waybar with workspaces, system stats, network, audio, Bluetooth and clock |
| **Launcher** | Rofi with a custom three-column theme |
| **Wallpapers** | Waypaper + Hyprpaper |
| **Lock screen** | Hyprlock with a blurred screenshot background |
| **Session menu** | Wlogout with compact text buttons and keyboard navigation |
| **Login manager** | SDDM with the `where_is_my_sddm_theme` theme |
| **Terminal** | Kitty · Fish · Starship |
| **Desktop tools** | Thunar · nwg-look · SwayNC · Cliphist · Cava · Btop |
| **Appearance** | Dark GTK settings · Papirus icons · Notwaita-Black cursor |

### Workflow highlights

- Six persistent workspaces and a special scratchpad workspace.
- Window focus, movement, resizing, swapping and grouping from the keyboard.
- Subtle window and workspace animations.
- US / Russian keyboard layout switching with `Alt + Shift`.
- Screenshot shortcuts and PipeWire media / volume controls.
- A compact, dark interface with a consistent visual style.

## Installation

This repository is a **personal configuration snapshot**, not a universal Arch installer. It has no one-click installation script.

1. Read the [installation guide](docs/INSTALLATION.md).
2. Check the [hardware-specific settings](docs/INSTALLATION.md#before-copying).
3. Back up your existing configuration.
4. Copy only the components you want and adjust them for your system.

~~~bash
git clone https://github.com/vampr5861-debug/arch-hyprland-dotfiles.git
cd arch-hyprland-dotfiles
~~~

The [package lists](packages/) are snapshots of explicitly installed packages from the original machine. They include unrelated applications and are **not** a dependency list—do not install them blindly.

## Before copying

Some settings are specific to the original computer:

| Setting | Current assumption | What to check |
| :--- | :--- | :--- |
| Monitor | `DP-1` | Update persistent workspace rules for your output |
| Display | 2560 × 1440 | Wlogout placement was tuned for this resolution |
| GPU | NVIDIA | Waybar's GPU temperature module calls `nvidia-smi` |
| CPU sensor | `coretemp` | Change the Waybar sensor on non-Intel systems |
| Fonts | JetBrainsMono Nerd Font, Noto Sans | Install the fonts or change the font settings |
| Wallpaper | `~/Pictures/wallhaven-n6y9zl.jpg` | Supply your own image; it is not included |

The Hyprland configuration uses the Lua configuration format. Confirm that your installed Hyprland release supports it before copying the file.

## Documentation

- [Installation guide](docs/INSTALLATION.md) — dependencies, backups, selective copying and optional SDDM setup.
- [Keybindings](docs/KEYBINDINGS.md) — keyboard, mouse, workspace, audio and Wlogout controls.
- [Troubleshooting](docs/TROUBLESHOOTING.md) — common hardware and configuration adjustments.
- [Configuration audit](AUDIT.md) — scope, exclusions, licensing and static review notes.
- [Package snapshot](packages/README.md) — original explicitly installed package lists.
- [Publishing updates](PUBLISH.md) — safe repository maintenance.

## Repository layout

~~~text
.
├── home/        # User configuration and appearance assets
├── system/      # Optional system-wide SDDM files
├── screenshots/ # Desktop previews
├── packages/    # Original explicit package snapshots
├── assets/      # Third-party asset notes
├── extras/      # Unreferenced scripts kept for reference
├── LICENSES/    # Third-party license texts and notices
├── docs/        # Installation, keybindings and troubleshooting
├── AUDIT.md
└── PUBLISH.md
~~~

## Credits & licensing

This setup uses and includes work from the wider open-source desktop ecosystem, including [Hyprland](https://hypr.land/), [Waybar](https://github.com/Alexays/Waybar), [Rofi](https://github.com/davatorium/rofi), [Dracula GTK](https://github.com/dracula/gtk), [Notwaita Cursor](https://github.com/ful1e5/notwaita-cursor) and [Where is my SDDM theme?](https://github.com/stepanzubkov/where-is-my-sddm-theme).

Third-party license texts and notices are retained in [LICENSES/](LICENSES/) and alongside the relevant assets. **No project-wide license has been selected for the original dotfiles.** Public visibility does not automatically grant permission to redistribute or relicense the original configuration. Third-party components remain subject to their own licenses.

---

<div align="center">

**Made for Arch Linux · Hyprland · a calmer desktop**

[Back to top](#momo--hyprland-dotfiles)

</div>
