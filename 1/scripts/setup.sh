#!/bin/bash

set -e

LAB_DIR="/opt/lab"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "LMS Portal Lab Setup Script"
echo "=========================================="
echo ""

echo "[1/10] Checking OS version..."
if [ -f /etc/debian_version ]; then
    DEBIAN_VERSION=$(cat /etc/debian_version)
    echo "Debian version: $DEBIAN_VERSION"
    if [[ ! "$DEBIAN_VERSION" =~ ^12\. ]]; then
        echo "⚠️  Warning: This script is designed for Debian 12.x"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  Warning: Not running on Debian. Some steps may fail."
fi

echo ""
echo "[2/10] Updating system packages..."
apt update
apt upgrade -y

echo ""
echo "[3/10] Installing base packages..."
apt install -y \
    sudo \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    php8.2-fpm \
    php8.2-sqlite3 \
    php8.2-mbstring \
    php8.2-xml \
    php8.2-curl \
    nodejs \
    npm \
    sqlite3

echo "Verifying installation..."
if ! command -v nginx &> /dev/null && [ ! -f /usr/sbin/nginx ] && [ ! -f /usr/bin/nginx ]; then
    echo "⚠️  Warning: nginx not found in PATH, trying to locate..."
    which nginx || find /usr -name nginx 2>/dev/null | head -1
    if [ $? -ne 0 ]; then
        echo "ERROR: nginx installation failed. Reinstalling..."
        apt install --reinstall -y nginx
    fi
fi

echo ""
echo "[4/10] Creating directory structure..."
mkdir -p "$LAB_DIR"/{django-lms,php-support,react-components,static/{css,js,images},nginx,scripts,docs,config}
cp -r "$PROJECT_DIR"/* "$LAB_DIR/" 2>/dev/null || true

if [ ! -f "$LAB_DIR/config/lab.env" ]; then
    cat > "$LAB_DIR/config/lab.env" << EOF
LAB_DIFFICULTY=hard
RSC_TOKEN=lms-integration-token
EOF
fi

bash "$LAB_DIR/scripts/create_credentials.sh"
if [ -f /root/lab_credentials.env ]; then
    set -a
    source /root/lab_credentials.env
    set +a
fi

echo ""
echo "[5/10] Setting up Django application..."
cd "$LAB_DIR/django-lms"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput

deactivate

echo ""
echo "[6/10] Initializing Django data..."
cd "$LAB_DIR/django-lms"
source venv/bin/activate
export PYTHONPATH="$LAB_DIR/django-lms:$PYTHONPATH"
python "$LAB_DIR/scripts/init_data.py"
deactivate

echo ""
echo "[7/10] Setting up PHP application..."
cd "$LAB_DIR/php-support"
php init_db.php

chown -R www-data:www-data "$LAB_DIR/php-support"
chmod 755 "$LAB_DIR/php-support"
chmod 666 "$LAB_DIR/php-support/support.db" 2>/dev/null || true

echo ""
echo "[8/10] Setting up React Server Components..."
cd "$LAB_DIR/react-components"
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "[9/10] Configuring Nginx..."

if ! command -v nginx &> /dev/null && [ ! -f /usr/sbin/nginx ]; then
    echo "ERROR: nginx not found. Installing..."
    apt install -y nginx
fi

NGINX_CMD="nginx"
if [ ! -f /usr/bin/nginx ] && [ -f /usr/sbin/nginx ]; then
    NGINX_CMD="/usr/sbin/nginx"
fi

cp "$LAB_DIR/nginx/lms.conf" /etc/nginx/sites-available/lms
ln -sf /etc/nginx/sites-available/lms /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

if command -v nginx &> /dev/null; then
    nginx -t
elif [ -f /usr/sbin/nginx ]; then
    /usr/sbin/nginx -t
else
    echo "⚠️  Warning: Cannot test nginx configuration (nginx command not found)"
    echo "   Configuration files copied, but please verify manually"
fi

echo ""
echo "[10/10] Creating SUID binary..."
bash "$LAB_DIR/scripts/create_suid_binary.sh"

bash "$LAB_DIR/scripts/create_flag.sh"

chown -R www-data:www-data "$LAB_DIR/static"
chown -R www-data:www-data "$LAB_DIR/django-lms"

echo ""
echo "Creating systemd services..."

cat > /etc/systemd/system/lms-django.service << EOF
[Unit]
Description=LMS Portal Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$LAB_DIR/django-lms
Environment="PATH=$LAB_DIR/django-lms/venv/bin"
ExecStart=$LAB_DIR/django-lms/venv/bin/gunicorn --bind 127.0.0.1:8000 lms_portal.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/lms-react.service << EOF
[Unit]
Description=LMS Portal React RSC Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$LAB_DIR/react-components
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/node --conditions=react-server server.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lms-django
systemctl enable lms-react
systemctl restart lms-django
systemctl restart lms-react
systemctl restart nginx
systemctl restart php8.2-fpm

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Services status:"
systemctl status lms-django --no-pager -l | head -5
echo ""
systemctl status lms-react --no-pager -l | head -5
echo ""
echo "Access the application at:"
echo "  http://localhost/"
echo "  http://localhost/portal/  (Django LMS)"
echo "  http://localhost/support/  (PHP Support)"
echo "  http://localhost/api/rsc/demo  (React RSC)"
echo ""
echo "Admin credentials are stored in /root/lab_credentials.txt"
echo ""
echo "⚠️  This is a vulnerable lab environment!"
echo "   Do not use in production!"
