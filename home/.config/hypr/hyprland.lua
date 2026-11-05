
-- ============================================================
-- MOMO HYPRLAND V6
-- Arch Linux + Hyprland + EndeavourOS Rofi
-- Minimal / Gray / Polished
-- ============================================================


-- ============================================================
-- PROGRAMS
-- ============================================================

local mainMod     = "SUPER"

local terminal    = "kitty"
local fileManager = "thunar"
local browser     = "firefox"

local rofiApps    = "rofi -no-config -show drun -theme ~/.config/rofi/launchers/type-4/style-8.rasi"



-- ============================================================
-- MONITOR
-- ============================================================

hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = "auto",
})


-- ============================================================
-- CURSOR / ENVIRONMENT
-- ============================================================

hl.env("XCURSOR_THEME", "Notwaita-Black")
hl.env("XCURSOR_SIZE", "20")


-- Use KDE integration for a consistent Qt theme in Hyprland.


-- ============================================================
-- AUTOSTART
-- ============================================================

-- AUTOSTART: independent desktop services.
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("waypaper --restore --backend hyprpaper")
    hl.exec_cmd("hyprsunset --temperature 5500")
    hl.exec_cmd("swaync")
    -- Native cliphist startup; keep the previous per-login history cleanup.
    hl.exec_cmd("cliphist wipe")
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    hl.exec_cmd("systemctl --user start hyprpolkitagent.service")
end)


-- ============================================================
-- MAIN CONFIG
-- ============================================================

hl.config({

    general = {

        -- Always keep clean gaps around windows.
        gaps_in = 7,
        gaps_out = 10,
        float_gaps = 10,

        -- No window borders.
        border_size = 0,

        col = {

            -- Active window: pink to purple gradient.
            active_border = {
                colors = {
                    "rgba(ff79c6ff)",
                    "rgba(bd93f9ff)",
                },
                angle = 45,
            },

            -- Inactive windows: muted pink.
            inactive_border = "rgba(ff79c666)",
        },

        resize_on_border = true,
        extend_border_grab_area = 15,
        hover_icon_on_border = true,

        -- Native magnetic snapping for floating windows.
        snap = {
            enabled = true,
            window_gap = 7,
            monitor_gap = 10,
            border_overlap = false,
            respect_gaps = true,
        },

        allow_tearing = false,

        layout = "dwindle",
    },


    decoration = {

        rounding = 12,
        rounding_power = 2,

        active_opacity = 1.0,
        inactive_opacity = 0.985,

        shadow = {
            enabled = true,
            range = 6,
            render_power = 3,
            color = 0xaa000000,
        },

        blur = {
            enabled = true,
            size = 6,
            passes = 2,
            vibrancy = 0.06,
        },
    },


    animations = {
        enabled = true,
        workspace_wraparound = true,
    },


    input = {

        -- English + Russian.
        kb_layout = "us,ru",

        kb_variant = "",
        kb_model = "",

        -- Alt + Shift
        kb_options = "grp:alt_shift_toggle",

        kb_rules = "",

        -- Keep hotkeys in the same physical positions
        -- when Russian layout is active.
        resolve_binds_by_sym = false,

        numlock_by_default = true,

        repeat_rate = 35,
        repeat_delay = 300,

        follow_mouse = 1,
        focus_on_close = 2,

        sensitivity = -0.5,

        touchpad = {
            natural_scroll = false,
        },
    },


    dwindle = {

        preserve_split = false,

        smart_resizing = true,

        use_active_for_splits = true,

        precise_mouse_move = true,

        default_split_ratio = 1.0,
    },


    render = {
        direct_scanout = 2,
    },


    misc = {

        force_default_wallpaper = 0,

        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        vrr = 2,
    },

})


-- ============================================================
-- ANIMATION CURVES
-- ============================================================

hl.curve(
    "momoOut",
    {
        type = "bezier",
        points = {
            { 0.23, 1.0 },
            { 0.32, 1.0 },
        },
    }
)

hl.curve(
    "momoSmooth",
    {
        type = "bezier",
        points = {
            { 0.45, 0.0 },
            { 0.10, 1.0 },
        },
    }
)

hl.curve(
    "momoFast",
    {
        type = "bezier",
        points = {
            { 0.15, 0.0 },
            { 0.10, 1.0 },
        },
    }
)


-- ============================================================
-- ANIMATIONS
-- ============================================================

hl.animation({
    leaf = "border",
    enabled = true,
    speed = 4.5,
    bezier = "momoOut",
})

hl.animation({
    leaf = "windows",
    enabled = true,
    speed = 4,
    bezier = "momoOut",
})

hl.animation({
    leaf = "windowsIn",
    enabled = true,
    speed = 4,
    bezier = "momoOut",
    style = "popin 92%",
})

hl.animation({
    leaf = "windowsOut",
    enabled = true,
    speed = 2.4,
    bezier = "momoFast",
    style = "popin 94%",
})

hl.animation({
    leaf = "fade",
    enabled = true,
    speed = 3,
    bezier = "momoSmooth",
})

hl.animation({
    leaf = "layers",
    enabled = true,
    speed = 3.8,
    bezier = "momoOut",
})

hl.animation({
    leaf = "workspaces",
    enabled = true,
    speed = 3.3,
    bezier = "momoOut",
    style = "slidefade 18%",
})


-- ============================================================
-- PERSISTENT WORKSPACES
-- ============================================================

for i = 1, 6 do

    hl.workspace_rule({
        workspace = tostring(i),
        monitor = "DP-1",
        persistent = true,
        default = (i == 1),
    })

end


-- ============================================================
-- SCRATCHPAD
-- ============================================================

-- Preserve a compact special workspace using workspace-specific gaps.
-- Approximate the former 0.92 scale on a 2560x1440 monitor.
hl.workspace_rule({
    workspace = "special:scratch",
    gaps_out = { top = 58, bottom = 58, left = 102, right = 102 },
})

-- Open Kitty only when the scratch workspace is first created empty.
hl.on("workspace.created", function(ws)
    if ws.name ~= "special:scratch" or not ws.is_empty then
        return
    end

    hl.exec_cmd(terminal, { workspace = "special:scratch silent" })
end)


-- ============================================================
-- TOUCHPAD GESTURES
-- ============================================================

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})


-- ============================================================
-- APPLICATIONS
-- ============================================================

-- Kitty
hl.bind(
    mainMod .. " + Return",
    hl.dsp.exec_cmd(terminal)
)

-- Thunar
hl.bind(
    mainMod .. " + E",
    hl.dsp.exec_cmd(fileManager)
)

-- Firefox
hl.bind(
    mainMod .. " + B",
    hl.dsp.exec_cmd(browser)
)


-- ============================================================
-- ROFI
-- ============================================================

-- Application launcher
hl.bind(
    mainMod .. " + Space",
    hl.dsp.exec_cmd(rofiApps)
)

-- Application launcher (same as SUPER + Space)
hl.bind(
    mainMod .. " + R",
    hl.dsp.exec_cmd(rofiApps)
)

-- Window switcher (EndeavourOS Rofi)
hl.bind(
    mainMod .. " + SHIFT + Space",
    hl.dsp.exec_cmd("rofi -show window")
)


-- ============================================================
-- BASIC WINDOW MANAGEMENT
-- ============================================================

-- Close window
hl.bind(
    mainMod .. " + Q",
    hl.dsp.window.close()
)

-- Kill frozen window
hl.bind(
    mainMod .. " + CTRL + Q",
    hl.dsp.window.kill()
)

-- Tiled <-> floating
hl.bind(
    mainMod .. " + V",
    hl.dsp.window.float({
        action = "toggle",
    })
)

-- True fullscreen
hl.bind(
    mainMod .. " + F",
    hl.dsp.window.fullscreen({
        mode = "fullscreen",
        action = "toggle",
    })
)

-- Maximize
hl.bind(
    mainMod .. " + M",
    hl.dsp.window.fullscreen({
        mode = "maximized",
        action = "toggle",
    })
)

-- Pseudotile
hl.bind(
    mainMod .. " + P",
    hl.dsp.window.pseudo({
        action = "toggle",
    })
)

-- Pin floating window
hl.bind(
    mainMod .. " + SHIFT + P",
    hl.dsp.window.pin({})
)

-- Center floating window
hl.bind(
    mainMod .. " + ALT + C",
    hl.dsp.window.center({})
)


-- ============================================================
-- DWINDLE
-- ============================================================

-- preserve_split = false keeps Dwindle dynamic.
-- Therefore togglesplit is intentionally not bound here:
-- Hyprland requires preserve_split = true for togglesplit.

hl.bind(
    mainMod .. " + SHIFT + T",
    hl.dsp.layout("swapsplit")
)

hl.bind(
    mainMod .. " + bracketleft",
    hl.dsp.layout("splitratio -0.1")
)

hl.bind(
    mainMod .. " + bracketright",
    hl.dsp.layout("splitratio +0.1")
)


-- ============================================================
-- FOCUS
-- ============================================================

hl.bind(
    mainMod .. " + left",
    hl.dsp.focus({
        direction = "left",
    })
)

hl.bind(
    mainMod .. " + right",
    hl.dsp.focus({
        direction = "right",
    })
)

hl.bind(
    mainMod .. " + up",
    hl.dsp.focus({
        direction = "up",
    })
)

hl.bind(
    mainMod .. " + down",
    hl.dsp.focus({
        direction = "down",
    })
)

-- Previous focused window
hl.bind(
    mainMod .. " + BackSpace",
    hl.dsp.focus({
        last = true,
    })
)

-- Cycle windows
hl.bind(
    mainMod .. " + Tab",
    hl.dsp.window.cycle_next({
        next = true,
    })
)


-- ============================================================
-- MOVE WINDOWS
-- ============================================================

hl.bind(
    mainMod .. " + SHIFT + left",
    hl.dsp.window.move({
        direction = "left",
    })
)

hl.bind(
    mainMod .. " + SHIFT + right",
    hl.dsp.window.move({
        direction = "right",
    })
)

hl.bind(
    mainMod .. " + SHIFT + up",
    hl.dsp.window.move({
        direction = "up",
    })
)

hl.bind(
    mainMod .. " + SHIFT + down",
    hl.dsp.window.move({
        direction = "down",
    })
)


-- ============================================================
-- RESIZE WINDOWS
-- ============================================================

hl.bind(
    mainMod .. " + CTRL + left",
    hl.dsp.window.resize({
        x = -40,
        y = 0,
        relative = true,
    }),
    {
        repeating = true,
    }
)

hl.bind(
    mainMod .. " + CTRL + right",
    hl.dsp.window.resize({
        x = 40,
        y = 0,
        relative = true,
    }),
    {
        repeating = true,
    }
)

hl.bind(
    mainMod .. " + CTRL + up",
    hl.dsp.window.resize({
        x = 0,
        y = -40,
        relative = true,
    }),
    {
        repeating = true,
    }
)

hl.bind(
    mainMod .. " + CTRL + down",
    hl.dsp.window.resize({
        x = 0,
        y = 40,
        relative = true,
    }),
    {
        repeating = true,
    }
)


-- ============================================================
-- SWAP TILED WINDOWS
-- ============================================================

hl.bind(
    mainMod .. " + ALT + left",
    hl.dsp.window.swap({
        direction = "left",
    })
)

hl.bind(
    mainMod .. " + ALT + right",
    hl.dsp.window.swap({
        direction = "right",
    })
)

hl.bind(
    mainMod .. " + ALT + up",
    hl.dsp.window.swap({
        direction = "up",
    })
)

hl.bind(
    mainMod .. " + ALT + down",
    hl.dsp.window.swap({
        direction = "down",
    })
)


-- ============================================================
-- WORKSPACES
-- ============================================================

for i = 1, 6 do

    local key = tostring(i)

    -- Switch workspace
    hl.bind(
        mainMod .. " + " .. key,
        hl.dsp.focus({
            workspace = i,
        })
    )

    -- Move active window to workspace
    hl.bind(
        mainMod .. " + SHIFT + " .. key,
        hl.dsp.window.move({
            workspace = i,
        })
    )

end


-- SUPER + mouse wheel
hl.bind(
    mainMod .. " + mouse_down",
    hl.dsp.focus({
        workspace = "e+1",
    })
)

hl.bind(
    mainMod .. " + mouse_up",
    hl.dsp.focus({
        workspace = "e-1",
    })
)


-- ============================================================
-- SCRATCHPAD BINDS
-- ============================================================

-- Show / hide scratchpad
hl.bind(
    mainMod .. " + grave",
    hl.dsp.workspace.toggle_special("scratch")
)

-- Send active window to scratchpad
hl.bind(
    mainMod .. " + SHIFT + grave",
    hl.dsp.window.move({
        workspace = "special:scratch",
        follow = false,
    })
)


-- ============================================================
-- WINDOW GROUPS
-- ============================================================

hl.bind(
    mainMod .. " + G",
    hl.dsp.group.toggle({})
)

hl.bind(
    mainMod .. " + CTRL + G",
    hl.dsp.group.next({})
)

hl.bind(
    mainMod .. " + SHIFT + G",
    hl.dsp.group.prev({})
)


-- ============================================================
-- MOUSE CONTROL
-- ============================================================

-- SUPER + LMB = move
hl.bind(
    mainMod .. " + mouse:272",
    hl.dsp.window.drag(),
    {
        mouse = true,
    }
)

-- SUPER + RMB = resize
hl.bind(
    mainMod .. " + mouse:273",
    hl.dsp.window.resize(),
    {
        mouse = true,
    }
)


-- ============================================================
-- MOMO SUNSET: NOTIFICATIONS, SCREENSHOTS, SESSION
-- ============================================================
hl.bind(mainMod .. " + S", hl.dsp.exec_cmd("swaync-client -t"))
hl.bind(mainMod .. " + SHIFT + N", hl.dsp.exec_cmd("swaync-client -d"))
hl.bind(mainMod .. " + SHIFT + B", hl.dsp.exec_cmd("pkill -SIGUSR1 waybar"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("hyprshot -m region -z --clipboard-only"))
hl.bind("Print", hl.dsp.exec_cmd("hyprshot -m output --clipboard-only"))
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + Escape", hl.dsp.exec_cmd("wlogout -b 4 -c 0 -L 1055 -R 1055 -T 664 -B 664 -p layer-shell"))
hl.bind("ALT + Tab", hl.dsp.window.cycle_next({ next = true }))

-- Audio / microphone through existing PipeWire / WirePlumber
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })

-- Media keys
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl pause"), { locked = true })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })


-- ============================================================
-- WINDOW RULES
-- ============================================================

-- Stop apps from maximizing themselves automatically.
hl.window_rule({

    name = "suppress-app-maximize",

    match = {
        class = ".*",
    },

    suppress_event = "maximize",
})


-- Fullscreen video / game keeps system awake.
hl.window_rule({

    name = "fullscreen-idle-inhibit",

    match = {
        class = ".*",
    },

    idle_inhibit = "fullscreen",
})


-- Picture-in-Picture.
-- Keep Firefox PiP floating, pinned and tucked into the bottom-right corner.
hl.window_rule({

    name = "picture-in-picture",

    match = {
        class = "firefox",
        title = "^(Picture-in-Picture|Picture in picture)$",
    },

    float = true,
    pin = true,

    size = {
        640,
        360,
    },

    move = {
        "monitor_w-window_w-20",
        "monitor_h-window_h-20",
    },

    keep_aspect_ratio = true,
})


-- Modal dialogs.
-- Confirmation/auth/dialog windows stay out of the tiling tree.
hl.window_rule({

    name = "modal-dialogs",

    match = {
        modal = true,
    },

    float = true,
    center = true,
})


-- Pinentry should keep keyboard focus while visible.
hl.window_rule({

    name = "pinentry-focus",

    match = {
        class = "(pinentry-)(.*)",
    },

    stay_focused = true,
})


-- XWayland drag workaround.
hl.window_rule({

    name = "fix-xwayland-drags",

    match = {

        class = "^$",
        title = "^$",

        xwayland = true,

        float = true,

        fullscreen = false,

        pin = false,
    },

    no_focus = true,
})


-- ============================================================
-- ROFI LAYER
-- ============================================================

hl.layer_rule({

    name = "rofi",

    match = {
        namespace = "rofi",
    },

    blur = true,

    ignore_alpha = 0.35,
})

-- Blur only the Waybar layer, respecting its transparent rounded corners.
hl.layer_rule({
    name = "waybar-glass",
    match = { namespace = "waybar" },
    blur = true,
    ignore_alpha = 0.2,
})

-- Waypaper wallpaper manager
hl.bind(
    "SUPER + W",
    hl.dsp.exec_cmd("/usr/bin/waypaper --backend hyprpaper")
)

-- MOMO: Waypaper floating window
hl.window_rule({
    name = "momo-waypaper",
    match = { class = ".*[Ww]aypaper.*" },
    float = true,
    size = { 1650, 950 },
    center = true,
})

hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")

-- Wlogout: native background blur
hl.layer_rule({ name = "wlogout-native-blur", match = { namespace = "^logout_dialog$" }, blur = true, ignore_alpha = 0.0 })
