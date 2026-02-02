#!/bin/bash

# Raj Leads Generator - Stop Script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   🛑 Stopping Raj Leads Generator       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Stop Nginx if running
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "Stopping Nginx..."
    sudo systemctl stop nginx
    echo -e "${GREEN}✅ Nginx stopped${NC}"
fi

# Stop PHP-FPM if running
if systemctl is-active --quiet php8.4-fpm 2>/dev/null; then
    echo "Stopping PHP-FPM..."
    sudo systemctl stop php8.4-fpm
    echo -e "${GREEN}✅ PHP-FPM stopped${NC}"
fi

# Stop Cloudflare tunnel
if pgrep -f "cloudflared tunnel" > /dev/null; then
    echo "Stopping Cloudflare tunnel..."
    pkill -f "cloudflared tunnel"
    echo -e "${GREEN}✅ Cloudflare tunnel stopped${NC}"
fi

# Kill any PHP dev server on port 8005
if fuser 8005/tcp > /dev/null 2>&1; then
    echo "Stopping PHP development server..."
    fuser -k 8005/tcp
    echo -e "${GREEN}✅ PHP dev server stopped${NC}"
fi

echo -e "${GREEN}All services stopped.${NC}"
