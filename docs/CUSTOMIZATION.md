# Customizing MOMO

A practical map of the **included configuration snapshot**, not a system-wide installer. All examples use existing application settings or ordinary Linux commands; no custom setup scripts are required.

> [!IMPORTANT]
> Keep your working configuration and backups separate from the Git checkout. Changes made in `home/` inside this repository do **not** automatically change your live `~/.config/` files, and editing your live session does **not** automatically update the repository.

## Find the right file

| Goal | Source in the repository | Notes |
| :--- | :--- | :--- |
| Workspaces, monitor, window behavior, binds, animations | [`home/.config/hypr/hyprland.lua`](../home/.config/hypr/hyprland.lua) | Uses Hyprland's Lua `hl.*` API |
| Lock screen | [`home/.config/hypr/hyprlock.conf`](../home/.config/hypr/hyprlock.conf) | Hyprlock, not Hyprland's Lua file |
| Wallpaper backend | [`home/.config/hypr/hyprpaper.conf`](../home/.config/hypr/hyprpaper.conf) | Hyprpaper settings |
| Wallpaper picker and current image | [`home/.config/waypaper/config.ini`](../home/.config/waypaper/config.ini) | Current wallpaper is not bundled |
| Panel modules and click commands | [`home/.config/waybar/config.jsonc`](../home/.config/waybar/config.jsonc) | `ext/workspaces`, hardware sensors, audio and network |
| Panel fonts and spacing | [`home/.config/waybar/style.css`](../home/.config/waybar/style.css) | GTK CSS; avoid changing all GTK menu labels unintentionally |
| Application launcher | [`home/.config/rofi/`](../home/.config/rofi/) | Check the explicitly selected Rofi theme |
| Terminal appearance | [`home/.config/kitty/kitty.conf`](../home/.config/kitty/kitty.conf) | Uses the account's login shell |
| Shell prompt | [`home/.config/fish/config.fish`](../home/.config/fish/config.fish) and [`starship.toml`](../home/.config/starship.toml) | Copying Fish config does not change the login shell |
| Power menu | [`home/.config/wlogout/`](../home/.config/wlogout/) | Text buttons and application keybindings |
| Login theme | [`system/`](../system/) | System-wide, optional, requires extra care |

For complete installation and restoration instructions, use [Installation](INSTALLATION.md). For the current actual keyboard shortcuts, use [Keybindings](KEYBINDINGS.md).

## Safe editing workflow

1. Work on **one component at a time**. Identify whether you are changing a repository file or your live configuration.
2. Before replacing an existing live file or directory, back it up as described in [Installation](INSTALLATION.md#3-back-up-your-current-configuration). Preserve symbolic links and permissions where applicable.
3. Check the option in the version of the application's official documentation that you have installed. Syntax can remain valid while runtime APIs change.
4. Reload or restart only the affected application using its documented mechanism. Keep a terminal or TTY available to restore the backup.
5. If an experiment fails, restore that component instead of stacking more speculative edits on top.

For a repository-only edit, check the proposed changes before copying them into a live system:

```bash
git status --short
git diff --check
git diff
```

These commands are read-only checks; they do not reload your desktop.

## Monitor and workspaces

`hyprland.lua` includes a generic monitor definition, but its **six persistent workspace rules target `DP-1`**. Identify the real output on your system before changing that field:

```bash
hyprctl monitors
hyprctl version
hyprctl configerrors
```

Update only the monitor value in the relevant `hl.workspace_rule()` calls if your output has a different name. The current layout uses Dwindle, a scratchpad workspace and custom animations; no changes to those behaviors are required for a monitor-name adjustment.

Refer to the [Hyprland configuration documentation](https://wiki.hypr.land/Configuring/Start/) for the API matching your installed release. Lua syntax checks alone cannot validate `hl.*` calls.

## Waybar: hardware modules and interactions

Two modules are machine-specific:

- The CPU temperature module uses the `coretemp` hardware monitor, typically associated with Intel systems.
- The GPU temperature module runs `nvidia-smi`. It needs a working NVIDIA driver and utility.

On other hardware, select an available sensor or disable the relevant module in the **copied** configuration rather than editing an unrelated module. Module membership is defined in `modules-left`, `modules-center` and `modules-right`.

Click actions are defined alongside each module in `config.jsonc`. The Arch icon currently launches Rofi, while the power icon launches Wlogout. The stylesheet controls appearance only; changing it will not change what a button executes.

Waybar uses `ext/workspaces`. Check your version and compositor support before replacing it with a different workspace module. Consult the [Waybar project](https://github.com/Alexays/Waybar) for current configuration references.

## Rofi: why one config may not affect the launcher

The application launcher binding in `hyprland.lua` explicitly runs:

```bash
rofi -no-config -show drun -theme ~/.config/rofi/launchers/type-4/style-8.rasi
```

Because the command uses `-no-config`, **editing only `~/.config/rofi/config.rasi` is not sufficient** to change that launcher's appearance. Review the explicitly referenced theme and its `shared/` resources. Keep all related theme files together when copying them. The separate window switcher may use different defaults.

The application launcher requests Iosevka Nerd Font; other components request JetBrainsMono Nerd Font. Missing fonts can change alignment and glyph display.

## Wallpaper picker and lock screen

Waypaper uses the Hyprpaper backend. The configured wallpaper points to a file under `~/Pictures/` that is **not included** in this repository. Select a real image using Waypaper or update its `wallpaper` setting before expecting restoration at startup.

Hyprlock is configured independently in `hyprlock.conf`, including a blurred screenshot background. Do not assume Waypaper or Hyprpaper settings control the lock-screen appearance.

The Waypaper configuration also names a `keybindings.ini` file that is not bundled. Check the behavior of your installed Waypaper version rather than creating arbitrary bindings to silence an error.

## Power menu and login manager

Wlogout layout actions live in `home/.config/wlogout/layout`, and its styling lives in `style.css`. The launch commands in both Hyprland and Waybar include margins tuned for a 2560 × 1440 display. On another resolution, adjust the launch parameters and layout as a coordinated change.

SDDM files under `system/` are **optional system-wide** resources. They are not copied by editing `~/.config/`. Follow the separate backup, dependency and rollback instructions in [Installation](INSTALLATION.md#6-install-the-sddm-theme-optional-system-wide). Do not restart SDDM casually from a working graphical session.

## Validate on a real session

After applying an approved change to the running system:

```bash
hyprctl configerrors
hyprctl monitors
systemctl --user --failed --no-pager
```

Also verify the actual user interaction you changed: a Waybar click, Rofi opening with the expected theme, wallpaper restoration, or the relevant keybinding. Static checks cannot replace those runtime observations.

If the result is wrong, use the recorded backup and the [rollback procedure](INSTALLATION.md#roll-back-selected-components).

## Publishing changes safely

Do not copy browser profiles, secrets, local authentication data, entire home directories or unreviewed wallpaper assets into the repository. Screenshots may reveal network or machine information. Review third-party licenses before adding icons, themes, shaders or artwork.

Use [Publishing updates](../PUBLISH.md) for a branch-based review workflow. Keep configuration snapshots intentional: a public Git repository is not a live synchronization service.
