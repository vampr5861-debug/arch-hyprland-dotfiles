# Troubleshooting

Start with the actual error message. Avoid changing several configuration files at once.

## Basic checks

~~~bash
hyprctl configerrors
hyprctl monitors
systemctl --user --failed --no-pager
~~~

For user-session warnings:

~~~bash
journalctl --user -b -p warning --no-pager
~~~

## Hyprland does not apply the workspace rules

First check `hyprctl version` against the documentation for your installed release. This snapshot uses Lua's `hl.*` API and does not record a tested Hyprland version. An unsupported configuration format or API must be resolved before hardware-specific rules can be assessed; a successful Lua syntax check alone does not validate it.

The persistent workspace rules in `hyprland.lua` target `DP-1`.

Check your output names:

~~~bash
hyprctl monitors
~~~

Replace `DP-1` in the workspace rules with the output name reported by your system. Do not change the monitor mode unless you know the display's supported modes.

## Waybar shows missing temperature or GPU data

The included Waybar config uses:

- `coretemp` for the CPU temperature sensor (commonly found on Intel systems).
- `nvidia-smi` for the GPU temperature module (NVIDIA-specific).

On an AMD CPU or a non-NVIDIA GPU, identify the sensor / GPU tool available on your system and adapt the relevant module, or remove that module from `modules-center`. Do not leave a hardware-specific command in the config if the machine cannot run it.

## Waypaper does not restore the wallpaper

The configuration expects `~/Pictures/wallhaven-n6y9zl.jpg`, which is not included.

1. Choose a wallpaper that exists on your machine.
2. Set it through Waypaper or update the `wallpaper` path in `~/.config/waypaper/config.ini`.
3. Confirm that Hyprpaper is installed.
4. Try restoring from a terminal:

~~~bash
waypaper --restore --backend hyprpaper
~~~

## Rofi uses the wrong theme or cannot find the font

The application launcher binding explicitly points to:

~~~bash
rofi -no-config -show drun -theme ~/.config/rofi/launchers/type-4/style-8.rasi
~~~

Check that the theme and its `shared/` files were copied together. The theme expects a Nerd Font; install the expected font or adjust the font declarations in the Rofi theme files.

The application launcher requests **Iosevka Nerd Font** (`ttf-iosevka-nerd`); the separate window-switcher configuration requests **JetBrainsMono Nerd Font** (`ttf-jetbrains-mono-nerd`). Installing one family does not supply the other.

## Wlogout is misplaced on another resolution

The launch command includes fixed margins tuned for a 2560 × 1440 display. It appears in both the Hyprland binding and the Waybar power module.

On another resolution, review the `wlogout` command in:

- `~/.config/hypr/hyprland.lua`
- `~/.config/waybar/config.jsonc`

Adjust the margins for your display or use a simpler `wlogout` command and tune the layout separately.

## Clipboard history is unavailable

The Hyprland autostart starts `wl-paste` watchers for text and image content and stores entries with Cliphist.

It also runs `cliphist wipe` at each Hyprland start. No history-picker shortcut is configured; scripts under `extras/unreferenced-scripts/` are archived references and are not installed by the guide. See their limitations in [AUDIT.md](../AUDIT.md#repository-review--november-5-2026).

Check that the relevant tools are installed and that the watchers are running:

~~~bash
pgrep -af 'wl-paste|cliphist'
~~~

## SDDM theme does not appear

The SDDM configuration is optional and system-wide. Confirm that the theme directory exists at `/usr/share/sddm/themes/where_is_my_sddm_theme/` and that `/etc/sddm.conf.d/99-where-is-my-sddm.conf` selects the intended theme.

Keep a backup and a TTY recovery path available before changing login-manager settings. Do not experiment by restarting SDDM from your active graphical session.

## Still stuck?

Capture the exact error, the relevant config section and your Hyprland / Waybar versions. Remove private information (usernames, local IP addresses, tokens and personal paths) before posting logs publicly.
