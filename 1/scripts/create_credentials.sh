#!/bin/bash
set -e

LAB_DIR="/opt/lab"
CONFIG_DIR="$LAB_DIR/config"
CONFIG_FILE="$CONFIG_DIR/credentials.env"
ROOT_ENV_FILE="/root/lab_credentials.env"
ROOT_TXT_FILE="/root/lab_credentials.txt"

mkdir -p "$CONFIG_DIR"

if [ -f "$ROOT_ENV_FILE" ] && [ -f "$CONFIG_FILE" ]; then
    exit 0
fi

DJANGO_PASSWORD=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(16))
PY
)

PHP_PASSWORD=$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(16))
PY
)

PHP_PASSWORD_HASH=$(php -r 'echo password_hash($argv[1], PASSWORD_DEFAULT);' "$PHP_PASSWORD")

cat > "$ROOT_ENV_FILE" << EOF
DJANGO_ADMIN_PASSWORD=$DJANGO_PASSWORD
PHP_ADMIN_PASSWORD=$PHP_PASSWORD
EOF

cat > "$ROOT_TXT_FILE" << EOF
LMS Portal Lab Credentials
==========================
Django Admin Username: admin
Django Admin Password: $DJANGO_PASSWORD
PHP Support Admin Password: $PHP_PASSWORD
EOF

cat > "$CONFIG_FILE" << EOF
PHP_ADMIN_PASSWORD_HASH=$PHP_PASSWORD_HASH
EOF

chown root:root "$ROOT_ENV_FILE" "$ROOT_TXT_FILE"
chmod 600 "$ROOT_ENV_FILE" "$ROOT_TXT_FILE"

chown root:www-data "$CONFIG_FILE"
chmod 640 "$CONFIG_FILE"
