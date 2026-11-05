# MOMO

**Hyprland dotfiles for Arch Linux.** A personal Wayland desktop with a dark palette, compact tools and keyboard-driven window management.

![Arch Linux](https://img.shields.io/badge/Arch%20Linux-1793D1?style=flat-square&logo=archlinux&logoColor=white)
![Config checks](https://github.com/vampr5861-debug/arch-hyprland-dotfiles/actions/workflows/validate.yml/badge.svg)

[Desktop](#desktop) · [Features](#features) · [Installation](#installation) · [Keybindings](docs/KEYBINDINGS.md) · [Documentation](#documentation)

## Desktop

[<img src="screenshots/desktop-fastfetch.png" alt="Hyprland desktop with Kitty and Fastfetch" width="100%">](screenshots/desktop-fastfetch.png)

<sub>Hyprland · Waybar · Kitty · Fastfetch</sub>

<table>
  <tr>
    <td width="50%" align="center" valign="top">
      <a href="screenshots/waypaper-overview.png"><img src="screenshots/waypaper-overview.png" alt="Waypaper wallpaper gallery" width="100%"></a><br>
      <sub>Waypaper · Wallpapers</sub>
    </td>
    <td width="50%" align="center" valign="top">
      <a href="screenshots/rofi-launcher.png"><img src="screenshots/rofi-launcher.png" alt="Rofi application launcher" width="100%"></a><br>
      <sub>Rofi · App launcher</sub>
    </td>
  </tr>
</table>

> Screenshots show the supplied desktop, including local network information. Third-party wallpapers visible in them are not included in this repository.

## Features

- **Keyboard-oriented workspace.** Six persistent workspaces, a scratchpad, and shortcuts for window focus, movement, resizing, swapping and grouping.
- **Compact desktop controls.** Waybar status modules, a three-column Rofi launcher and Waypaper with the Hyprpaper backend.
- **Dark, consistent appearance.** Dark GTK settings, Papirus icons, the Notwaita-Black cursor and subtle window / workspace animations.
- **Everyday shortcuts.** Hyprlock screen locking, Wlogout session controls, screenshots, PipeWire audio controls, media keys and US / Russian layout switching with `Alt + Shift`.

## Components

| Component | Stack |
| :--- | :--- |
| Window manager | Hyprland · Lua configuration · Dwindle |
| Panel & launcher | Waybar · Rofi |
| Wallpapers | Waypaper · Hyprpaper |
| Terminal | Kitty · Fish · Starship |
| Lock & session | Hyprlock (screenshot blur) · Wlogout (text buttons & hotkeys) |
| Login (optional) | SDDM · `where_is_my_sddm_theme` |
| Desktop tools | Thunar · nwg-look · SwayNC · Cliphist · Cava · Btop |
| Appearance | Materia-dark GTK · Papirus icons · Notwaita-Black cursor |

Waybar shows workspaces, system stats, network, audio, Bluetooth and the clock. SwayNC uses its default configuration; no custom notification theme is bundled.

## Installation

This is a **manually installed personal configuration snapshot**. Start with an existing Arch Linux installation, working graphics drivers and a usable Wayland session. There is no automatic installer.

1. Read the [installation guide](docs/INSTALLATION.md) for dependencies and optional components.
2. Review [compatibility and hardware assumptions](#before-you-copy), then back up the destinations you will change.
3. Copy only the components you want and adapt them to your system. Keep the guide's rollback steps available.

~~~bash
git clone https://github.com/vampr5861-debug/arch-hyprland-dotfiles.git
cd arch-hyprland-dotfiles
~~~

The [package inventories](packages/README.md) are informational snapshots with unrelated applications, **not dependency lists**. Do not install them wholesale.

## Before you copy

> **Compatibility:** no known-good Hyprland or Waybar version is recorded in this snapshot. Confirm support for the Lua `hl.*` API, Waybar's `ext/workspaces` module and the included `hyprctl dispatch` expressions against the documentation for your installed releases. Lua syntax checks do not establish compatibility.

The original machine's settings need a review before copying:

| Check | Snapshot assumption |
| :--- | :--- |
| Monitor | Persistent workspace rules target `DP-1`; use your output name. |
| Display | Wlogout placement is tuned for 2560 × 1440. |
| GPU | Waybar calls NVIDIA's `nvidia-smi`; adapt the module for other GPUs. |
| CPU sensor | Waybar uses Intel's `coretemp`; select your CPU's sensor. |
| Fonts | JetBrainsMono Nerd Font, Iosevka Nerd Font and Adwaita Sans; missing families change spacing and glyphs. |
| Wallpaper | `~/Pictures/wallhaven-n6y9zl.jpg` is not included; supply your own image. |

### Session behavior

- **Clipboard:** Cliphist records copied text and images during the session and clears its history at each Hyprland start. No history-picker shortcut is configured.
- **Shell:** Kitty uses the account's login shell. Copying the Fish configuration does not select Fish automatically.

See the [keybinding reference](docs/KEYBINDINGS.md) for the complete shortcuts, including the scratchpad, window groups and media controls. Hardware compatibility, SDDM rendering and the appearance on other displays remain unverified.

### Validation

GitHub Actions runs lightweight static checks on pushes and pull requests:

- Waybar JSON, Wlogout layout, Starship TOML, selected INI and XML files.
- Hyprland Lua syntax.
- Shell syntax for the archived helper scripts.

A passing workflow catches syntax errors; it does **not** replace testing the configuration in a real Hyprland session.

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

The [audit](AUDIT.md#repository-review--november-5-2026) records unresolved Cava shader provenance, artwork permissions and the optional Dracula theme's missing resources. Preserved notices do not establish complete redistribution compliance.

[Back to top](#momo)
