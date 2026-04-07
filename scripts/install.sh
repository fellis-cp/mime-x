#!/bin/bash
# Install Mime-X to the local application menu

# Get the project root directory (one level up from scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_FILE="$PROJECT_ROOT/data/mime-x.desktop"
TARGET_DIR="$HOME/.local/share/applications"

# Ensure target directory exists
mkdir -p "$TARGET_DIR"

if [ ! -f "$DESKTOP_FILE" ]; then
    echo "Error: Desktop file not found at $DESKTOP_FILE"
    exit 1
fi

# Copy and update the desktop file
cp "$DESKTOP_FILE" "$TARGET_DIR/"
# Update Exec to point to the venv python and the main.py in src/mime_x/
sed -i "s|Exec=.*|Exec=$PROJECT_ROOT/venv/bin/python3 $PROJECT_ROOT/src/mime_x/main.py|" "$TARGET_DIR/mime-x.desktop"

# Update desktop database
update-desktop-database "$TARGET_DIR"

echo "Mime-X has been installed to $TARGET_DIR"
echo "You can now find it in your application menu."
