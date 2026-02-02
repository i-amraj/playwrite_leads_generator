#!/bin/bash

# Raj Leads Generator - Start Script (Nginx Version)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   🚀 Raj Leads Generator Starter       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed!${NC}"
    exit 1
fi

# Check if Nginx is installed
if command -v nginx &> /dev/null; then
    echo -e "${GREEN}✅ Using Nginx + PHP-FPM (Multi-user support)${NC}"
    
    # Start Nginx and PHP-FPM
    echo -e "Starting services..."
    sudo systemctl start nginx php8.4-fpm
    
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx is running${NC}"
    else
        echo -e "${RED}❌ Nginx failed to start${NC}"
        exit 1
    fi
    
    if systemctl is-active --quiet php8.4-fpm; then
        echo -e "${GREEN}✅ PHP-FPM is running${NC}"
    else
        echo -e "${RED}❌ PHP-FPM failed to start${NC}"
        exit 1
    fi
    
else
    # Fallback to PHP dev server
    echo -e "${YELLOW}⚠️  Nginx not found, using PHP development server${NC}"
    echo -e "${YELLOW}   (Limited to 1-2 concurrent users)${NC}"
    
    # Kill any existing PHP server on port 8005
    fuser -k 8005/tcp > /dev/null 2>&1
    
    # Start PHP in background
    php -S localhost:8005 > php_server.log 2>&1 &
    PHP_PID=$!
    
    # Ensure PHP stops when script exits
    trap "kill $PHP_PID 2>/dev/null" EXIT
    
    sleep 2
    
    if ! ps -p $PHP_PID > /dev/null; then
        echo -e "${RED}❌ PHP Server failed to start. Check php_server.log${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}👉 Local App: http://localhost:8005/ ${NC}"

# Check cloudflared
if command -v cloudflared &> /dev/null; then
    echo -e "${BLUE}☁️  Starting Cloudflare Tunnel...${NC}"
    echo -e "   (Initial connection may take a few seconds)"
    # Run cloudflared attached so user sees the URL output
    cloudflared tunnel --url http://localhost:8005
else
    echo -e "${YELLOW}⚠️  'cloudflared' not found.${NC}"
    echo -e "   To expose to internet, install cloudflared or read RUN_INSTRUCTIONS.md"
    echo -e "   App is running locally. Press Ctrl+C to stop."
    
    # If using Nginx, wait indefinitely
    if command -v nginx &> /dev/null; then
        echo -e "${GREEN}Services running. Press Ctrl+C to stop.${NC}"
        while true; do sleep 3600; done
    else
        wait $PHP_PID
    fi
fi
