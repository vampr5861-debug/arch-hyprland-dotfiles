# Installation

This guide describes a **manual, selective setup**. It does not run an installer, change your display manager automatically or overwrite your system without review.

> [!WARNING]
> These files are a snapshot of one Arch Linux machine. Back up your current configuration first. Read each section and adapt hardware-specific settings before using them.

## 1. Clone the repository

~~~bash
git clone https://github.com/vampr5861-debug/arch-hyprland-dotfiles.git
cd arch-hyprland-dotfiles
~~~

## 2. Install the components you need

Start from an existing Arch Linux system with working graphics drivers and a usable Wayland session. Keep a TTY recovery path before changing a working desktop.

This snapshot does not record a known-good Hyprland or Waybar version. Check `hyprctl version` and `waybar --version`, then consult the [Hyprland documentation](https://wiki.hypr.land/) and [Waybar documentation](https://github.com/Alexays/Waybar/wiki) for those releases. In particular, this setup needs the Lua `hl.*` API, the `ext/workspaces` module and the Lua expressions passed to `hyprctl dispatch`. Parsing as Lua or JSON does not establish support for these features.

The following is a practical starting set for the desktop configuration. It is not a complete package export and does not include every optional application.

~~~bash
sudo pacman -Syu --needed \
  hyprland waybar rofi kitty thunar firefox \
  hyprlock hyprpaper hyprsunset hyprpolkitagent hyprshot \
  swaync cliphist wl-clipboard \
  pipewire pipewire-pulse wireplumber pavucontrol libpulse \
  fish starship playerctl \
  blueman nwg-look papirus-icon-theme materia-gtk-theme \
  noto-fonts adwaita-fonts ttf-jetbrains-mono-nerd ttf-iosevka-nerd otf-font-awesome \
  btop cava qt6ct \
  gvfs tumbler thunar-volman exo \
  xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
~~~

`-Syu` performs a full system upgrade as well as installing packages; review the transaction and current Arch upgrade notices. Do not refresh package databases and then perform a partial upgrade.

| Dependency | Used by |
| :--- | :--- |
| `libpulse` | `pactl` for Waybar's microphone mute action; `pipewire-pulse` provides the server |
| `wireplumber`, `playerctl` | `wpctl` audio controls and media-key actions |
| `exo` | Thunar's `exo-open` custom action; select your preferred terminal in Xfce's preferred applications if needed |
| `ttf-jetbrains-mono-nerd` | Kitty, Waybar, Hyprlock and the Rofi window switcher |
| `ttf-iosevka-nerd` | The application launcher's `Iosevka Nerd Font` family |
| `adwaita-fonts` | The GTK settings' `Adwaita Sans Heavy` font request |

These package names describe the intended Arch dependencies; the exported inventories do not pin their versions. SwayNC is started with its defaults: no custom SwayNC configuration is included. Bluetooth controls also require a functioning Bluetooth service and adapter.

### Optional packages

| Package | Needed for |
| :--- | :--- |
| `waypaper`, `wlogout` | Required for the supplied wallpaper startup / picker and session menu; foreign packages on the original system |
| `sddm`, `qt6-declarative`, `qt6-5compat` | Optional login manager and the theme's Qt Quick / `Qt5Compat.GraphicalEffects` imports |
| `nvidia-utils` | Waybar's `nvidia-smi` GPU temperature module |
| `file-roller`, `thunar-archive-plugin` | Thunar archive integration |
| `xsettingsd` | Optional XSettings configuration; it is not started by the included Hyprland autostart |

Waypaper and Wlogout are optional only if you omit their integrations. If you already use `yay`, review the package build files and install the two foreign packages with:

~~~bash
yay -S --needed waypaper wlogout
~~~

Use a trusted AUR helper or follow the relevant package instructions if you do not use `yay`.

## 3. Back up your current configuration

Before copying, back up each destination you intend to modify. For `~/.config`, run in Bash:

Stop if any backup command fails; do not continue with an incomplete backup. If a symlink manager controls your configuration, use its backup and installation workflow instead: `cp -a` preserves symlinks and does not back up their external targets.

~~~bash
backup_root=$(mktemp -d "$HOME/momo-backup.XXXXXXXX")
if [ -e "$HOME/.config" ]; then
  cp -a "$HOME/.config" "${backup_root:?Backup directory was not created}/config"
fi
printf 'Backup directory: %s\n' "$backup_root"
~~~

Record the printed path and keep it until you have verified the new setup. If `~/.config` did not exist, there is no previous configuration to restore. Backups may contain credentials; keep them private and outside this repository. Optional theme and SDDM destinations need their own backups as described below.

## 4. Copy selected user configurations

Run these commands from the **repository root**. Copy only the components you intend to use.

~~~bash
mkdir -p ~/.config
cp -a home/.config/hypr ~/.config/
cp -a home/.config/waybar ~/.config/
cp -a home/.config/rofi ~/.config/
cp -a home/.config/wlogout ~/.config/
cp -a home/.config/waypaper ~/.config/
cp -a home/.config/kitty ~/.config/
cp -a home/.config/fish ~/.config/
cp -a home/.config/cava ~/.config/
cp -a home/.config/Thunar ~/.config/
cp -a home/.config/nwg-look ~/.config/
cp -a home/.config/gtk-3.0 ~/.config/
cp -a home/.config/gtk-4.0 ~/.config/
cp -a home/.config/xsettingsd ~/.config/
cp -a home/.config/starship.toml ~/.config/
~~~

`cp -a` merges files into existing directories and may replace files with the same names. The backup in the previous step is important.

The GTK settings select `Materia-dark`. The included `Dracula-pink-accent` theme is an additional option; it is not selected automatically by those settings.

Kitty uses your account's login shell. To try the included Fish / Starship configuration, run `fish` in a terminal; copying these files does not change your login shell.

## 5. Install the included cursor and GTK theme (optional)

Before copying, back up any existing `~/.local/share/icons/Notwaita-Black`, `~/.local/share/icons/default` and `~/.local/share/themes/Dracula-pink-accent` directories to your private backup directory. Copy only the resources you want.

**The optional Dracula theme is incomplete:** some CSS image references have no matching bundled files. See the [audit](../AUDIT.md#repository-review--november-5-2026) for examples. It is not the selected GTK theme; keep Materia for the supplied appearance. Test the optional theme separately before relying on it.

~~~bash
mkdir -p ~/.local/share/themes ~/.local/share/icons
cp -a home/.local/share/themes/Dracula-pink-accent ~/.local/share/themes/
cp -a home/.local/share/icons/Notwaita-Black ~/.local/share/icons/
cp -a home/.local/share/icons/default ~/.local/share/icons/
~~~

The Notwaita cursor contains internal relative symlinks. Preserve them when copying.

## 6. Install the SDDM theme (optional; system-wide)

Only follow this section if your system already uses SDDM and you intend to use the included theme.

The theme metadata declares **Qt 6** and theme version **1.12.0**. Its QML imports Qt Quick Controls, `SddmComponents` and `Qt5Compat.GraphicalEffects`; ensure the optional packages above are installed. A compatible SDDM / Qt Quick runtime is required; the theme version is not an SDDM version pin. Verify with your installed SDDM release before selecting it.

Back up both the existing SDDM configuration and any theme with the same name. Run in Bash; record the backup path:

~~~bash
sudo mkdir -p /var/backups
sddm_backup=$(sudo mktemp -d /var/backups/momo-sddm.XXXXXXXX)
if [ -d /etc/sddm.conf.d ]; then
  sudo cp -a /etc/sddm.conf.d "${sddm_backup:?Backup directory was not created}/sddm.conf.d"
fi
if [ -d /usr/share/sddm/themes/where_is_my_sddm_theme ]; then
  sudo cp -a /usr/share/sddm/themes/where_is_my_sddm_theme "${sddm_backup:?Backup directory was not created}/theme"
fi
printf 'SDDM backup: %s\n' "$sddm_backup"
~~~

Copy the theme and its configuration:

~~~bash
sudo mkdir -p /usr/share/sddm/themes /etc/sddm.conf.d
sudo cp -a system/usr/share/sddm/themes/where_is_my_sddm_theme /usr/share/sddm/themes/
sudo cp -a system/etc/sddm.conf.d/99-where-is-my-sddm.conf /etc/sddm.conf.d/
~~~

The last file selects the included theme. Do not replace your display manager or restart SDDM from inside your active graphical session as an experiment. Keep a working TTY or recovery path available.

## Before copying

Review these machine-specific settings and change them where necessary:

| File | Setting | Why it may need changing |
| :--- | :--- | :--- |
| `home/.config/hypr/hyprland.lua` | Persistent workspaces use `DP-1` | Your monitor may have a different output name |
| `home/.config/waybar/config.jsonc` | CPU sensor `coretemp` | This is an Intel sensor name; other CPUs may expose another sensor |
| `home/.config/waybar/config.jsonc` | `nvidia-smi` GPU module | NVIDIA-specific; remove or replace it on other GPUs |
| `home/.config/waypaper/config.ini` | `~/Pictures/wallhaven-n6y9zl.jpg` | The wallpaper file is not included |
| `home/.config/wlogout/` and Hyprland / Waybar launch commands | Fixed margins for 2560 × 1440 | Revisit placement on other resolutions |
| Rofi theme files | Nerd Font family | Install the expected font or change the theme |

The wallpaper is deliberately not bundled because its redistribution rights have not been verified.

Waypaper also refers to `~/.config/waypaper/keybindings.ini`, which is not included. Custom Waypaper keybindings cannot be reproduced from this snapshot; check your installed version's defaults or configuration options if it reports a missing file.

## Verify the setup

After applying the configuration and starting a Hyprland session:

~~~bash
hyprctl configerrors
hyprctl monitors
systemctl --user --failed --no-pager
~~~

If you see configuration errors, do not keep layering changes on top. Restore the affected file from your backup and resolve the reported issue first.

For common adjustments, see [Troubleshooting](TROUBLESHOOTING.md). For the full shortcut list, see [Keybindings](KEYBINDINGS.md).

Cliphist stores copied text and images, which can include sensitive data. The included autostart wipes its history at each Hyprland start, then starts two watchers. There is no active history-picker binding. Check existing user services before starting additional copies of Waybar, SwayNC or clipboard watchers.

## Roll back selected components

If a component fails, use a TTY or another working session. Restore only the affected component from the recorded backup. For example, in Bash, replace the example backup path with your actual one:

~~~bash
backup_root="$HOME/momo-backup.REPLACE_WITH_YOUR_BACKUP"
if [ -d "$backup_root/config/hypr" ]; then
  failed_copy=$(mktemp -d "$HOME/momo-failed.XXXXXXXX")
  if [ -e "$HOME/.config/hypr" ] || [ -L "$HOME/.config/hypr" ]; then
    mv "$HOME/.config/hypr" "${failed_copy:?Recovery directory was not created}/hypr"
  fi && cp -a "$backup_root/config/hypr" "$HOME/.config/hypr"
fi
~~~

Moving the failed component aside avoids merging newly introduced files into the restored version. Apply the same approach to other selected components and optional themes. If a component was absent before installation, move the newly added directory aside instead of restoring a nonexistent backup.

For SDDM, use a TTY to restore the previous `99-where-is-my-sddm.conf` from the recorded system backup. If that file did not exist before, move the newly added selector out of `/etc/sddm.conf.d/`. Restore any previous theme directory separately. Avoid restarting SDDM inside a graphical session: it ends that session.
