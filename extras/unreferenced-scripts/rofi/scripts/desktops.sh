#!/usr/bin/env bash
# One searchable Rofi list: Hyprland workspaces + their open windows.
set -euo pipefail

if [[ "${ROFI_RETV:-0}" == "1" ]]; then
    case "${ROFI_INFO:-}" in
        ws:[1-9]* )
            id="${ROFI_INFO#ws:}"
            [[ "$id" =~ ^[1-9][0-9]*$ ]] || exit 0
            hyprctl dispatch "hl.dsp.focus({ workspace = $id })" >/dev/null 2>&1
            ;;
        win:0x* )
            address="${ROFI_INFO#win:}"
            [[ "$address" =~ ^0x[0-9a-fA-F]+$ ]] || exit 0
            hyprctl dispatch "hl.dsp.focus({ window = \"address:$address\" })" >/dev/null 2>&1
            ;;
    esac
    exit 0
fi

printf '\0no-custom\x1ftrue\n'
clients="$(hyprctl -j clients 2>/dev/null)" || exit 0
workspaces="$(hyprctl -j workspaces 2>/dev/null)" || exit 0
active="$(hyprctl -j activeworkspace 2>/dev/null | jq -r '.id // 1')"
[[ "$active" =~ ^[0-9]+$ ]] || active=1

# Render workspaces 1–6 even if empty, plus any additional occupied workspaces.
# A row selects a workspace; an indented row focuses a specific window.
while IFS=$'\t' read -r kind target label; do
    [[ -n "$kind" ]] || continue
    printf '%s\0info\x1f%s:%s\n' "$label" "$kind" "$target"
done < <(
    jq -rn --argjson clients "$clients" --argjson workspaces "$workspaces" --argjson active "$active" '
        def clean: tostring | gsub("[\u0000-\u001f]"; " ") | .[0:65];
        (([range(1;7)]
          + ($workspaces | map(.id | select(. > 0)))
          + ($clients | map(.workspace.id | select(. > 0))))
          | unique | sort)[] as $id
        | ($clients | map(select(.workspace.id == $id)) | sort_by(.class // "")) as $windows
        | (["ws", ($id|tostring),
            ((if $id == $active then "●" else "○" end)
            + "  Workspace " + ($id|tostring)
            + "    ·    " + ($windows|length|tostring)
            + (if ($windows|length) == 1 then " window" else " windows" end))] | @tsv),
          ($windows[] | ["win", (.address|tostring),
             ("     ↳  " + ((.class // .initialClass // "Window") | clean)
                + (if (.title // "") == "" then "" else " — " + (.title|clean) end))] | @tsv)
    '
)
