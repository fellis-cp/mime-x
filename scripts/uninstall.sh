#!/bin/bash
# Uninstall Mime-X from the local application menu

TARGET_FILE="$HOME/.local/share/applications/mime-x.desktop"

if [ -f "$TARGET_FILE" ]; then
    rm "$TARGET_FILE"
    update-desktop-database "$(dirname "$TARGET_FILE")"
    echo "Mime-X has been uninstalled from your application menu."
else
    echo "Mime-X desktop entry not found."
fi
