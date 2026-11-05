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

The following is a practical starting set for the desktop configuration. It is not a complete package export and does not include every optional application.

~~~bash
sudo pacman -S --needed \
  hyprland waybar rofi kitty thunar firefox \
  hyprlock hyprpaper hyprsunset hyprpolkitagent hyprshot \
  swaync cliphist wl-clipboard \
  pipewire pipewire-pulse wireplumber pavucontrol \
  fish starship playerctl \
  blueman nwg-look papirus-icon-theme materia-gtk-theme \
  noto-fonts ttf-jetbrains-mono-nerd otf-font-awesome \
  btop cava qt6ct \
  gvfs tumbler thunar-volman \
  xdg-desktop-portal-hyprland xdg-desktop-portal-gtk
~~~

### Optional packages

| Package | Needed for |
| :--- | :--- |
| `waypaper`, `wlogout` | Wallpaper picker and session menu; foreign packages on the original system |
| `sddm` | Login manager, only if you use SDDM |
| `nvidia-utils` | Waybar's `nvidia-smi` GPU temperature module |
| `file-roller`, `thunar-archive-plugin` | Thunar archive integration |
| `xsettingsd` | Optional XSettings configuration; it is not started by the included Hyprland autostart |

If you already use `yay`, the two foreign packages can be installed with:

~~~bash
yay -S --needed waypaper wlogout
~~~

Use a trusted AUR helper or follow the relevant package instructions if you do not use `yay`.

## 3. Back up your current configuration

From your home directory:

~~~bash
cp -a ~/.config "$HOME/.config.backup-$(date +%F-%H%M%S)"
~~~

This creates a timestamped copy of your entire current `~/.config` directory. Keep it until you have verified the new setup.

## 4. Copy selected user configurations

Run these commands from the **repository root**. Copy only the components you intend to use.

~~~bash
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

## 5. Install the included cursor and GTK theme (optional)

~~~bash
mkdir -p ~/.local/share/themes ~/.local/share/icons
cp -a home/.local/share/themes/Dracula-pink-accent ~/.local/share/themes/
cp -a home/.local/share/icons/Notwaita-Black ~/.local/share/icons/
cp -a home/.local/share/icons/default ~/.local/share/icons/
~~~

The Notwaita cursor contains internal relative symlinks. Preserve them when copying.

## 6. Install the SDDM theme (optional; system-wide)

Only follow this section if your system already uses SDDM and you intend to use the included theme.

Back up the current SDDM configuration:

~~~bash
sudo cp -a /etc/sddm.conf.d "/etc/sddm.conf.d.backup-$(date +%F-%H%M%S)"
~~~

Copy the theme and its configuration:

~~~bash
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

## Verify the setup

After applying the configuration and starting a Hyprland session:

~~~bash
hyprctl configerrors
hyprctl monitors
systemctl --user --failed --no-pager
~~~

If you see configuration errors, do not keep layering changes on top. Restore the affected file from your backup and resolve the reported issue first.

For common adjustments, see [Troubleshooting](TROUBLESHOOTING.md). For the full shortcut list, see [Keybindings](KEYBINDINGS.md).
