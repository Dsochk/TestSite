#!/bin/bash
set -e

FLAG_PATH="/root/flag.txt"
FLAG_VALUE="FLAG{PT-45119-29389-48817}"

if [ -f "$FLAG_PATH" ]; then
    echo "Flag already exists at $FLAG_PATH"
    exit 0
fi

echo "$FLAG_VALUE" > "$FLAG_PATH"
chown root:root "$FLAG_PATH"
chmod 600 "$FLAG_PATH"

echo "Flag created at $FLAG_PATH"
