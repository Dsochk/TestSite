#!/bin/bash

echo "Stopping LMS Portal services..."

if systemctl is-active lms-django >/dev/null 2>&1; then
    sudo systemctl stop lms-django
    echo "✓ Django stopped"
fi

if systemctl is-active lms-react >/dev/null 2>&1; then
    sudo systemctl stop lms-react
    echo "✓ React RSC stopped"
fi

pkill -f "gunicorn.*lms_portal" && echo "✓ Django (manual) stopped"
pkill -f "node.*server.js" && echo "✓ React RSC (manual) stopped"

sudo systemctl stop nginx
sudo systemctl stop php8.2-fpm

echo "All services stopped."
