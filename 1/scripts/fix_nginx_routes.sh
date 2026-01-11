#!/bin/bash

echo "Fixing Nginx configuration..."

sudo cp /opt/lab/nginx/lms.conf /etc/nginx/sites-available/lms

echo "Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✓ Nginx configuration is valid"
    
    echo "Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo "✓ Nginx reloaded successfully"
    echo ""
    echo "Fixed routes:"
    echo "  - Static pages (cases, pricing, contacts, products, about)"
    echo "  - Support system (/support/)"
    echo ""
    echo "Test URLs:"
    echo "  http://$(hostname -I | awk '{print $1}')/cases"
    echo "  http://$(hostname -I | awk '{print $1}')/pricing"
    echo "  http://$(hostname -I | awk '{print $1}')/contacts"
    echo "  http://$(hostname -I | awk '{print $1}')/products"
    echo "  http://$(hostname -I | awk '{print $1}')/support/"
else
    echo "✗ Nginx configuration has errors!"
    echo "Please check the configuration file manually."
    exit 1
fi
