#!/bin/bash

set -e

echo "=========================================="
echo "Starting LMS Portal Services"
echo "=========================================="

if [ ! -d "/opt/lab" ]; then
    echo "Error: /opt/lab not found. Run setup.sh first."
    exit 1
fi

if systemctl is-enabled lms-django >/dev/null 2>&1; then
    echo "[1/4] Starting Django (systemd)..."
    sudo systemctl start lms-django
    sudo systemctl status lms-django --no-pager -l | head -3
else
    echo "[1/4] Starting Django (manual)..."
    cd /opt/lab/django-lms
    if [ ! -d "venv" ]; then
        echo "Error: Django venv not found. Run setup.sh first."
        exit 1
    fi
    source venv/bin/activate
    if ! pgrep -f "gunicorn.*lms_portal" > /dev/null; then
        nohup gunicorn --bind 0.0.0.0:8000 lms_portal.wsgi:application > /tmp/gunicorn.log 2>&1 &
        echo "Django started on port 8000 (PID: $!)"
    else
        echo "Django already running"
    fi
    deactivate
fi

if systemctl is-enabled lms-react >/dev/null 2>&1; then
    echo ""
    echo "[2/4] Starting React RSC (systemd)..."
    sudo systemctl start lms-react
    sudo systemctl status lms-react --no-pager -l | head -3
else
    echo ""
    echo "[2/4] Starting React RSC (manual)..."
    cd /opt/lab/react-components
    if [ ! -d "node_modules" ]; then
        echo "Error: React node_modules not found. Run 'npm install' first."
        exit 1
    fi
    if ! pgrep -f "node.*server.js" > /dev/null; then
        nohup node server.js > /tmp/react-rsc.log 2>&1 &
        echo "React RSC started on port 3000 (PID: $!)"
    else
        echo "React RSC already running"
    fi
fi

echo ""
echo "[3/4] Starting PHP-FPM..."
sudo systemctl start php8.2-fpm
sudo systemctl status php8.2-fpm --no-pager -l | head -3

echo ""
echo "[4/4] Starting Nginx..."
sudo systemctl start nginx
sudo systemctl status nginx --no-pager -l | head -3

echo ""
echo "=========================================="
echo "Checking services..."
echo "=========================================="

sleep 2

if curl -s http://127.0.0.1:8000/ > /dev/null; then
    echo "✓ Django (port 8000): OK"
else
    echo "✗ Django (port 8000): FAILED"
fi

if curl -s http://127.0.0.1:3000/api/rsc/demo > /dev/null; then
    echo "✓ React RSC (port 3000): OK"
else
    echo "✗ React RSC (port 3000): FAILED"
fi

if systemctl is-active php8.2-fpm > /dev/null; then
    echo "✓ PHP-FPM: OK"
else
    echo "✗ PHP-FPM: FAILED"
fi

if curl -s http://127.0.0.1/ > /dev/null; then
    echo "✓ Nginx (port 80): OK"
else
    echo "✗ Nginx (port 80): FAILED"
fi

echo ""
echo "=========================================="
echo "Network Information"
echo "=========================================="
echo "VM IP addresses:"
hostname -I | tr ' ' '\n' | grep -v '^127.0.0.1' | while read ip; do
    echo "  http://$ip/"
done

echo ""
echo "Access URLs:"
hostname -I | tr ' ' '\n' | grep -v '^127.0.0.1' | head -1 | while read ip; do
    echo "  Main page:    http://$ip/"
    echo "  Django LMS:   http://$ip/portal/"
    echo "  PHP Support:  http://$ip/support/"
    echo "  Django Admin: http://$ip/admin/"
    echo "  React RSC:    http://$ip/api/rsc/demo"
done

echo ""
echo "=========================================="
echo "Services started!"
echo "=========================================="
echo ""
echo "To view logs:"
echo "  Django:  sudo journalctl -u lms-django -f"
echo "  React:   sudo journalctl -u lms-react -f"
echo "  Nginx:   sudo tail -f /var/log/nginx/error.log"
echo ""
echo "To stop services:"
echo "  sudo systemctl stop lms-django lms-react nginx php8.2-fpm"
