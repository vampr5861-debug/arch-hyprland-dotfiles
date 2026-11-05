<div align="center">

# MOMO · Hyprland Dotfiles

**Arch Linux / Hyprland · a minimal dark desktop**

A personal Arch Linux setup built around Hyprland, Waybar, Rofi, Waypaper, Hyprlock and SDDM.  
Clean typography, subtle animations, a dark color palette and manual installation—no one-click scripts.

![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?style=flat-square&logo=archlinux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-Lua%20config-58E1FF?style=flat-square)
![Waybar](https://img.shields.io/badge/Waybar-Custom-222222?style=flat-square)
![Installation](https://img.shields.io/badge/Installation-Manual-555555?style=flat-square)

[Preview](#preview) · [Components](#components) · [Installation](#installation) · [Keybindings](#keybindings) · [Structure](#structure) · [Notes](#notes) · [Credits](#credits)

</div>

---

## Preview

### Desktop & Fastfetch

[![Hyprland desktop with Kitty and Fastfetch](screenshots/desktop-fastfetch.png)](screenshots/desktop-fastfetch.png)

<sub>Arch Linux · Hyprland · Waybar · Kitty · Fastfetch</sub>

### Waypaper

[![Waypaper wallpaper gallery](screenshots/waypaper-overview.png)](screenshots/waypaper-overview.png)

<sub>Waypaper with the Hyprpaper backend</sub>

### Rofi

[![Rofi application launcher](screenshots/rofi-launcher.png)](screenshots/rofi-launcher.png)

<sub>Minimal three-column application launcher</sub>

> These are screenshots of the actual desktop. The third-party wallpapers visible in them are **not distributed** in this repository.

## Components

| Component | Configuration |
| :--- | :--- |
| **Window manager** | Hyprland using a Lua configuration; `dwindle` layout |
| **Status bar** | Waybar: workspaces, CPU/GPU, memory, networking, audio, Bluetooth and clock |
| **App launcher** | Rofi, `type-4/style-8` theme |
| **Wallpapers** | Waypaper with Hyprpaper |
| **Lock screen** | Hyprlock, clock/date and a blurred background |
| **Power menu** | Wlogout with minimal text-based buttons |
| **Login manager** | SDDM with `where_is_my_sddm_theme` |
| **Terminal / shell** | Kitty, Fish, Starship |
| **Files / GTK** | Thunar, GTK themes, Papirus and Notwaita-Black cursor |
| **Extras** | SwayNC, Cava, Btop and Cliphist |

**Highlights:** six persistent workspaces, keyboard-focused window management, a scratchpad, animated transitions and US/Russian layout switching with `Alt + Shift`.

## Installation

> [!WARNING]
> This is a **snapshot of a personal desktop**, not a complete Arch Linux installer. Review the files and adapt hardware-specific settings before using them. **Back up existing configurations before copying anything.** There is no automated installer.

### 1. Clone the repository

~~~bash
git clone https://github.com/vampr5861-debug/arch-hyprland-dotfiles.git
cd arch-hyprland-dotfiles
~~~

### 2. Install the main dependencies

For Arch Linux, using the official repositories:

~~~bash
sudo pacman -S --needed git hyprland waybar rofi kitty thunar firefox \
  hyprlock hyprpaper hyprsunset hyprpolkitagent hyprshot \
  swaync cliphist wl-clipboard fish starship \
  pipewire pipewire-pulse wireplumber pavucontrol \
  nwg-look papirus-icon-theme materia-gtk-theme \
  ttf-jetbrains-mono-nerd otf-font-awesome \
  btop cava blueman qt6ct sddm \
  xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
~~~

`waypaper` and `wlogout` were installed as third-party packages on the original system. If you already use `yay`:

~~~bash
yay -S --needed waypaper wlogout
~~~

These are the **main desktop dependencies**, not a guarantee that every optional keybinding will work out of the box. The [packages/](packages/) directory contains snapshots of the original system's explicitly installed packages; **do not install everything from those lists blindly**.

### 3. Back up and copy selected configurations

User configuration files are stored in `home/.config/`. Copy **only what you need**.

Example: install the Waybar configuration. If you already have `~/.config/waybar/`, back it up first:

~~~bash
cp -a ~/.config/waybar ~/.config/waybar.backup
~~~

Then, from the root of this cloned repository:

~~~bash
mkdir -p ~/.config/waybar
cp -a home/.config/waybar/. ~/.config/waybar/
~~~

Skip the backup command if the destination directory does not yet exist. Follow the same approach for `hypr`, `rofi`, `kitty`, `waypaper`, `wlogout` and other folders within `home/.config/`.

For the included GTK theme and cursor:

~~~bash
mkdir -p ~/.local/share/themes ~/.local/share/icons
cp -a home/.local/share/themes/Dracula-pink-accent ~/.local/share/themes/
cp -a home/.local/share/icons/Notwaita-Black ~/.local/share/icons/
~~~

Check for existing directories with those names before copying. Preserve symlinks when transferring the cursor theme.

### 4. SDDM (optional; system-wide)

SDDM uses system paths rather than the user's home directory. Inspect and back up your current SDDM configuration before changing it:

| Repository path | Destination |
| :--- | :--- |
| `system/usr/share/sddm/themes/where_is_my_sddm_theme/` | `/usr/share/sddm/themes/where_is_my_sddm_theme/` |
| `system/etc/sddm.conf.d/99-where-is-my-sddm.conf` | `/etc/sddm.conf.d/99-where-is-my-sddm.conf` |

Copy manually with administrator privileges **only after reviewing the theme files and checking for conflicts**. Do not enable or replace your current display manager without confirming how your login session is configured.

### 5. Adjust your setup

Some settings are specific to the original computer:

- **Monitor:** persistent workspaces 1–6 use the output `DP-1` in [hyprland.lua](home/.config/hypr/hyprland.lua).
- **Resolution:** Wlogout positioning was tuned for a 2560 × 1440 display.
- **GPU:** Waybar's GPU temperature module uses `nvidia-smi`, which requires NVIDIA drivers. Adapt or disable it on other GPUs.
- **CPU:** the Waybar CPU temperature module expects a sensor named `coretemp`.
- **Wallpaper:** Waypaper references `~/Pictures/wallhaven-n6y9zl.jpg`. The image itself is not included due to unverified redistribution rights; choose your own wallpaper.
- **Fonts:** some Rofi elements refer to Iosevka Nerd Font; other Nerd Fonts may also be useful.
- **GTK:** the exported settings select `Materia-dark`. `Dracula-pink-accent` is included as a separately selectable theme.

Check your running Hyprland configuration:

~~~bash
hyprctl configerrors
~~~

> [!NOTE]
> Your Hyprland version must support the Lua configuration format used here. This setup has **not** been tested across all Hyprland releases, GPUs or display layouts. Review and adapt it manually rather than using an unverified `curl | sh` installer.

## Keybindings

**`Super` means the Windows / Meta key.** The bindings below document the exported [Hyprland configuration](home/.config/hypr/hyprland.lua).

### Applications & system

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>Enter</kbd> | Open Kitty |
| <kbd>Super</kbd> + <kbd>E</kbd> | Open Thunar |
| <kbd>Super</kbd> + <kbd>B</kbd> | Open Firefox |
| <kbd>Super</kbd> + <kbd>Space</kbd> / <kbd>Super</kbd> + <kbd>R</kbd> | Rofi application launcher |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>Space</kbd> | Rofi window switcher |
| <kbd>Super</kbd> + <kbd>W</kbd> | Open Waypaper |
| <kbd>Super</kbd> + <kbd>S</kbd> | SwayNC notification center |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd> | Dismiss notifications |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd> | Toggle Waybar visibility |
| <kbd>Super</kbd> + <kbd>L</kbd> | Lock the screen with Hyprlock |
| <kbd>Super</kbd> + <kbd>Esc</kbd> | Open Wlogout |
| <kbd>Print</kbd> | Copy an output screenshot to the clipboard |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | Copy a region screenshot to the clipboard |
| <kbd>Alt</kbd> + <kbd>Shift</kbd> | Switch US / Russian keyboard layout |

### Window management

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>Q</kbd> | Close focused window |
| <kbd>Super</kbd> + <kbd>Ctrl</kbd> + <kbd>Q</kbd> | Force-kill focused window |
| <kbd>Super</kbd> + <kbd>V</kbd> | Toggle tiling / floating |
| <kbd>Super</kbd> + <kbd>F</kbd> | Toggle fullscreen |
| <kbd>Super</kbd> + <kbd>M</kbd> | Toggle maximized state |
| <kbd>Super</kbd> + <kbd>P</kbd> | Toggle pseudotiling |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> | Pin floating window |
| <kbd>Super</kbd> + <kbd>← ↑ ↓ →</kbd> | Focus a window |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>← ↑ ↓ →</kbd> | Move a window |
| <kbd>Super</kbd> + <kbd>Ctrl</kbd> + <kbd>← ↑ ↓ →</kbd> | Resize a window |
| <kbd>Super</kbd> + <kbd>Alt</kbd> + <kbd>← ↑ ↓ →</kbd> | Swap windows |
| <kbd>Super</kbd> + <kbd>Tab</kbd> | Cycle windows |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd> | Swap Dwindle split |
| <kbd>Super</kbd> + <kbd>left/right mouse button</kbd> | Move / resize a window |

### Workspaces & scratchpad

| Shortcut | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>1–6</kbd> | Switch workspace |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>1–6</kbd> | Move a window to workspace |
| <kbd>Super</kbd> + <kbd>mouse wheel</kbd> | Cycle workspaces |
| <kbd>Super</kbd> + <kbd>\`</kbd> | Toggle scratchpad |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>\`</kbd> | Move window to scratchpad |
| <kbd>Super</kbd> + <kbd>G</kbd> | Toggle window grouping |

### Wlogout controls

| Key | Action |
| :--- | :--- |
| <kbd>S</kbd> | Shut down |
| <kbd>R</kbd> | Reboot |
| <kbd>E</kbd> | Log out |
| <kbd>L</kbd> | Lock |

The public Wlogout configuration uses **text labels** instead of the original PNG icons, whose license could not be established.

## Structure

~~~text
arch-hyprland-dotfiles/
├── home/
│   ├── .config/            # Hyprland, Waybar, Rofi, Kitty, etc.
│   └── .local/share/      # Dracula GTK, Notwaita cursor
├── system/                # SDDM config and theme
├── screenshots/           # Real desktop previews
├── assets/                # Wallpaper and third-party asset notes
├── packages/              # Package snapshots and dependency notes
├── extras/                # Unreferenced scripts (not installed)
├── LICENSES/              # Third-party licenses and notices
├── AUDIT.md               # Configuration audit
└── README.md
~~~

## Notes

- This repository **does not ship an automatic installer**. Copy configurations manually and selectively.
- Configurations were captured on **November 5, 2026**; later changes to the live system are not synchronized automatically.
- Third-party wallpapers shown in screenshots are **not included**.
- Paths, fonts, display layout and drivers may require adjustments.
- `extras/unreferenced-scripts/` contains scripts preserved for reference; they are **not part of the active setup**.
- Never commit credentials, personal tokens, private keys, application sessions or other private files.

## Credits

Thanks to the creators and contributors of these projects:

- **[Hyprland](https://hypr.land/)**, **[Waybar](https://github.com/Alexays/Waybar)**, **[Rofi](https://github.com/davatorium/rofi)** and the other open-source components used here.
- **[Where is my SDDM theme?](https://github.com/stepanzubkov/where-is-my-sddm-theme)** — Stepan Zubkov, MIT.
- **[adi1090x/rofi](https://github.com/adi1090x/rofi)** — Rofi theme components, GPL-3.0.
- **[Dracula GTK](https://github.com/dracula/gtk)** — Eliver Lara and contributors, GPL-3.0.
- **[Notwaita Cursor](https://github.com/ful1e5/notwaita-cursor)** — see the [licensing notice](LICENSES/notwaita-cursor-NOTICE.md).

Third-party license details are retained in [LICENSES/](LICENSES/) and the relevant theme directories. **No overall license has been selected for the original dotfiles**; third-party code retains its own terms.

---

<div align="center">

**Made for Arch Linux + Hyprland**

[Back to top](#momo--hyprland-dotfiles)

</div>
