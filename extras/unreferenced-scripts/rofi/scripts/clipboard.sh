#!/usr/bin/env bash
# Rofi script-mode clipboard, cliphist keeps original text/image bytes.
set -euo pipefail

if [[ "${ROFI_RETV:-0}" == "1" ]]; then
    if [[ "${ROFI_INFO:-}" =~ ^[0-9]+$ ]]; then
        cliphist decode "$ROFI_INFO" | wl-copy
    fi
    exit 0
fi

# Selection only from the list; ignore arbitrary typed commands.
printf '\0no-custom\x1ftrue\n'
while IFS=$'\t' read -r id preview; do
    [[ "$id" =~ ^[0-9]+$ ]] || continue
    # The visible label omits cliphist's internal database ID.
    preview="${preview//$'\r'/ }"
    preview="${preview//$'\x1f'/ }"
    [[ -n "$preview" ]] || preview="(empty item)"
    printf '%s\0display\x1f%s\x1finfo\x1f%s\n' "$id $preview" "$preview" "$id"
done < <(cliphist list)
