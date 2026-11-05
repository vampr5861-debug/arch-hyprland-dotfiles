# Original System Package Snapshot

The package lists were supplied directly from `pacman -Qqen` and `pacman -Qqem` on **November 5, 2026**.

- [official-explicit.txt](official-explicit.txt) — **129 explicitly installed packages** from official repositories.
- [foreign-explicit.txt](foreign-explicit.txt) — **11 explicitly installed foreign packages**. The `foreign` category is not synonymous with AUR-only.
- These lists are **snapshots of explicitly installed packages**, not the complete list of installed dependencies and not a minimal dotfiles dependency set.
- **Do not install these entire lists blindly.** They include unrelated applications, drivers and other software.

## Main explicitly installed desktop components

**Official repositories:** `hyprland`, `hyprlock`, `hyprpaper`, `hyprsunset`, `hyprpolkitagent`, `hyprshot`, `hyprpicker`, `waybar`, `rofi`, `swaync`, `cliphist`, `wl-clipboard`, `kitty`, `fish`, `starship`, `sddm`, `nwg-look`, `thunar`, `cava`, `btop`, `blueman`, `pavucontrol`, `pipewire`, `wireplumber`, `papirus-icon-theme`, `ttf-jetbrains-mono-nerd`, `otf-font-awesome`, `materia-gtk-theme` and `jq`.

**Foreign packages:** `waypaper` and `wlogout`.

Some required binaries may have been installed as transitive dependencies.

## Items to check when installing on another machine

- A configuration for `xsettingsd` is included, but the package is not in the explicitly installed snapshots; verify availability and whether it is needed.
- `hyprland.lua` references `playerctl`, which is not in the explicit package list; it may be installed as a dependency or absent.
- Waybar invokes `nvidia-smi`. `nvidia-utils` is not explicitly listed, although it may be installed as a dependency.
- The Rofi theme refers to **Iosevka Nerd Font**, which is not explicitly listed; `ttf-jetbrains-mono-nerd` is.
- `Notwaita-Black` and `Dracula-pink-accent` are included as local resources, not individually installed packages in the snapshot. Refer to their upstream attribution and licenses.
- `mpvpaper` is present as a foreign package, but the published Waypaper configuration uses the **Hyprpaper** backend.
- `yay-debug` is present in the snapshot but **is not a required desktop component**.

See the main [README](../README.md) for the selective installation instructions.
