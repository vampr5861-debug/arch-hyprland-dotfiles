<div align="center">

# MOMO

**Arch Linux · Hyprland · Wayland**

A personal desktop configuration with a quiet dark palette, compact controls, subtle motion, and a keyboard-first workflow.

[![Configuration checks](https://github.com/vampr5861-debug/arch-hyprland-dotfiles/actions/workflows/validate.yml/badge.svg)](https://github.com/vampr5861-debug/arch-hyprland-dotfiles/actions/workflows/validate.yml)
![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?style=flat-square&logo=archlinux&logoColor=white)

[**Desktop**](#desktop) · [**Features**](#features) · [**Get started**](#get-started) · [**Customize**](docs/CUSTOMIZATION.md) · [**Keybindings**](docs/KEYBINDINGS.md)

</div>

---

## Desktop

[<img src="screenshots/desktop-fastfetch.png" width="100%" alt="MOMO Hyprland desktop, Waybar and a Kitty terminal with Fastfetch">](screenshots/desktop-fastfetch.png)

<sub>Hyprland · Waybar · Kitty · Fastfetch</sub>

<table>
  <tr>
    <td width="50%" valign="top" align="center">
      <a href="screenshots/waypaper-overview.png"><img src="screenshots/waypaper-overview.png" width="100%" alt="Waypaper wallpaper picker in MOMO"></a>
      <sub>Waypaper · Wallpaper picker</sub>
    </td>
    <td width="50%" valign="top" align="center">
      <a href="screenshots/rofi-launcher.png"><img src="screenshots/rofi-launcher.png" width="100%" alt="Rofi application launcher in MOMO"></a>
      <sub>Rofi · Application launcher</sub>
    </td>
  </tr>
</table>

<sub>The original screenshots show local network and machine information. The wallpaper artwork visible in them is third-party material; the wallpaper files are not bundled.</sub>

## Features

| | |
| :--- | :--- |
| **Keyboard-first** | Six persistent workspaces, a scratchpad, window groups and directional window controls |
| **Minimal desktop** | A compact Waybar, Rofi launcher, Waypaper gallery, and lightweight application stack |
| **Consistent appearance** | Dark GTK styling, Papirus icons, Notwaita-Black cursor and subtle window animations |
| **Everyday controls** | Screenshots, notifications, Bluetooth, PipeWire audio, locking and session actions |

### Components

| Role | Included configuration |
| :--- | :--- |
| Compositor | [Hyprland](home/.config/hypr/hyprland.lua) · Lua · Dwindle |
| Status bar | [Waybar](home/.config/waybar/) · workspaces, CPU/GPU, memory, network, audio and clock |
| Launcher | [Rofi](home/.config/rofi/) · application launcher and window switcher |
| Wallpaper | [Waypaper](home/.config/waypaper/) + Hyprpaper |
| Terminal | [Kitty](home/.config/kitty/) · Fish · Starship |
| Session | [Hyprlock](home/.config/hypr/hyprlock.conf) · [Wlogout](home/.config/wlogout/) |
| Login (optional) | [SDDM](system/) · `where_is_my_sddm_theme` |
| Other tools | Thunar · nwg-look · SwayNC · Cliphist · Cava · Btop |

These are **configuration snapshots**, not bundled replacements for the applications. SwayNC uses its default configuration; no custom notification theme is included.

## Get started

MOMO is intended for an **existing Arch Linux installation** with working graphics drivers and a usable Wayland session. There is no one-click installer, and copying every file into a live desktop is neither necessary nor recommended.

```bash
git clone https://github.com/vampr5861-debug/arch-hyprland-dotfiles.git
cd arch-hyprland-dotfiles
```

1. **Read** the [installation guide](docs/INSTALLATION.md) and check the required packages.
2. **Back up** each destination before copying or replacing configuration files.
3. **Select** only the components you want; adapt machine-specific values before starting the session.
4. **Verify** the result using the [troubleshooting checks](docs/TROUBLESHOOTING.md) and keep your backup for rollback.

> [!IMPORTANT]
> The lists under [`packages/`](packages/) are historical package snapshots, **not** an installation manifest. They contain unrelated applications and should not be installed wholesale.

## Make it yours

The [configuration guide](docs/CUSTOMIZATION.md) maps the actual files to the settings they control and explains how to adjust them **without a custom installation framework or helper scripts**.

| Change | Where to look |
| :--- | :--- |
| Monitor and workspaces | [`hyprland.lua`](home/.config/hypr/hyprland.lua) · `hl.workspace_rule()` and monitor settings |
| Bar modules, actions and spacing | [`config.jsonc`](home/.config/waybar/config.jsonc) · [`style.css`](home/.config/waybar/style.css) |
| Launcher theme and fonts | [`rofi/`](home/.config/rofi/) · explicit launcher theme path |
| Wallpaper folder and backend | [`waypaper/config.ini`](home/.config/waypaper/config.ini) · Hyprpaper |
| Terminal colors and fonts | [`kitty.conf`](home/.config/kitty/kitty.conf) |
| Lock screen and power menu | [`hyprlock.conf`](home/.config/hypr/hyprlock.conf) · [`wlogout/`](home/.config/wlogout/) |

### Compatibility notes

This snapshot has **no recorded known-good Hyprland or Waybar version pair**. Hyprland uses the Lua `hl.*` configuration API, while Waybar uses `ext/workspaces`. Check your installed versions and their upstream documentation before copying: static syntax validation does not prove runtime compatibility.

The original machine also has several hardware-specific settings:

| Assumption | Required adaptation on other systems |
| :--- | :--- |
| `DP-1`, 2560 × 1440 | Persistent workspace assignment and Wlogout placement |
| NVIDIA GPU | Waybar's `nvidia-smi` temperature readout |
| Intel `coretemp` sensor | Waybar CPU temperature source |
| Installed Nerd Fonts | Launcher, terminal, bar and lock-screen typography |
| `~/Pictures/wallhaven-n6y9zl.jpg` | Supply your own wallpaper; that image is not distributed |

For dependencies, backup steps, optional SDDM setup and recovery, follow the [installation guide](docs/INSTALLATION.md).

## Documentation

| Guide | Covers |
| :--- | :--- |
| [Installation](docs/INSTALLATION.md) | Dependencies, selective copying, backups, rollback and optional SDDM |
| [Customization](docs/CUSTOMIZATION.md) | Configuration map, safe edits, verification and hardware adjustments |
| [Keybindings](docs/KEYBINDINGS.md) | Desktop, windows, workspaces, media keys and Wlogout |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Runtime diagnostics and common configuration issues |
| [Audit](AUDIT.md) | Audit scope, unverified compatibility and third-party resource notes |
| [Publishing](PUBLISH.md) | Safely reviewing and publishing future updates |

<details>
<summary><strong>Repository structure</strong></summary>

```text
.
├── home/         # User-level application configurations and visual resources
├── system/       # Optional system-wide SDDM files
├── screenshots/  # Three original desktop previews
├── packages/     # Historical package inventories (not installation manifests)
├── assets/       # Third-party asset notes
├── LICENSES/     # Notices and third-party licensing information
├── extras/       # Inactive helper scripts, retained for reference
├── docs/         # Installation, customization, shortcuts and troubleshooting
├── AUDIT.md
└── PUBLISH.md
```

</details>

## Validation and limitations

[GitHub Actions](https://github.com/vampr5861-debug/arch-hyprland-dotfiles/actions/workflows/validate.yml) performs static checks for selected configuration formats, shell syntax and local documentation links. A passing check does **not** demonstrate successful installation, SDDM rendering or a working Hyprland session on another machine.

Some optional assets remain unverified or incomplete. See the [audit](AUDIT.md#repository-review--november-5-2026) before redistributing the Cava shaders or relying on the bundled Dracula GTK variant. The screenshots contain visible third-party wallpaper artwork and local machine details; review those before reuse.

## Credits and licensing

MOMO includes or configures software from the wider open-source desktop community: [Hyprland](https://hypr.land/), [Waybar](https://github.com/Alexays/Waybar), [Rofi](https://github.com/davatorium/rofi), [Dracula GTK](https://github.com/dracula/gtk), [Notwaita Cursor](https://github.com/ful1e5/notwaita-cursor), and [Where is my SDDM theme?](https://github.com/stepanzubkov/where-is-my-sddm-theme).

Third-party notices and available license texts are kept in [`LICENSES/`](LICENSES/) and alongside their resources. **No project-wide license has been selected for the original dotfiles.** Public visibility does not grant permission to redistribute or relicense them. The presence of a license notice alone does not resolve all outstanding attribution or redistribution questions.

<div align="center">

---

*Built for a quieter desktop.*

[Back to top](#momo)

</div>
