#!/bin/bash

echo "Fixing nginx installation..."

if ! dpkg -l | grep -q nginx; then
    echo "Nginx not installed. Installing..."
    apt update
    apt install -y nginx
fi

if command -v nginx &> /dev/null; then
    NGINX_CMD=$(command -v nginx)
    echo "Found nginx at: $NGINX_CMD"
elif [ -f /usr/sbin/nginx ]; then
    NGINX_CMD="/usr/sbin/nginx"
    echo "Found nginx at: $NGINX_CMD"
    export PATH="/usr/sbin:$PATH"
elif [ -f /usr/bin/nginx ]; then
    NGINX_CMD="/usr/bin/nginx"
    echo "Found nginx at: $NGINX_CMD"
else
    echo "ERROR: nginx not found anywhere!"
    echo "Trying to reinstall..."
    apt install --reinstall -y nginx
    NGINX_CMD=$(which nginx || echo "/usr/sbin/nginx")
fi

echo "Testing nginx configuration..."
if [ -f "$NGINX_CMD" ]; then
    $NGINX_CMD -t
    if [ $? -eq 0 ]; then
        echo "✓ Nginx configuration is valid"
    else
        echo "✗ Nginx configuration has errors"
    fi
else
    echo "ERROR: Cannot find nginx executable"
    exit 1
fi

echo ""
echo "Nginx status:"
systemctl status nginx --no-pager -l | head -5
