#!/bin/bash
set -e

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$LAB_DIR/config/lab.env"
DIFFICULTY="$1"

if [ -z "$DIFFICULTY" ]; then
    echo "Usage: $0 hard"
    exit 1
fi

if [ "$DIFFICULTY" != "hard" ]; then
    echo "Invalid value: $DIFFICULTY"
    echo "Only 'hard' mode is supported."
    echo "Usage: $0 hard"
    exit 1
fi

mkdir -p "$LAB_DIR/config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "LAB_DIFFICULTY=$DIFFICULTY" > "$CONFIG_FILE"
    echo "RSC_TOKEN=lms-integration-token" >> "$CONFIG_FILE"
else
    if grep -q "^LAB_DIFFICULTY=" "$CONFIG_FILE"; then
        sed -i "s/^LAB_DIFFICULTY=.*/LAB_DIFFICULTY=$DIFFICULTY/" "$CONFIG_FILE"
    else
        echo "LAB_DIFFICULTY=$DIFFICULTY" >> "$CONFIG_FILE"
    fi
fi

echo "LAB_DIFFICULTY set to $DIFFICULTY in $CONFIG_FILE"
echo ""
echo "Restart services to apply:"
echo "  sudo systemctl restart lms-django lms-react nginx php8.2-fpm"
