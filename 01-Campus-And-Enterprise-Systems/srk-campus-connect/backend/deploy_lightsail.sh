#!/bin/bash
# ==============================================================================
# 🏛️ SRK Campus Platform — AWS Lightsail 24/7 Automated Deployment Script
# ==============================================================================
set -e

echo "🚀 Step 1: Updating system packages & installing Node.js..."
sudo apt update -y
sudo apt install -y curl git ufw

# Install Node.js 20 LTS if not present
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi

echo "📦 Node Version: $(node -v)"
echo "📦 NPM Version: $(npm -v)"

echo "🚀 Step 2: Installing PM2 process manager for 24/7 uptime..."
sudo npm install -g pm2

echo "🚀 Step 3: Installing dependencies and compiling backend..."
npm install
npm run build

echo "🚀 Step 4: Starting 24/7 backend daemon with PM2..."
pm2 delete srk-backend || true
pm2 start dist/server.js --name "srk-backend"

# Ensure PM2 starts automatically if server reboots
pm2 save
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $USER --hp $HOME || true

echo "🚀 Step 5: Configuring firewall for Port 5000..."
sudo ufw allow 5000/tcp || true
sudo ufw allow 80/tcp || true
sudo ufw allow 443/tcp || true

echo ""
echo "=================================================================="
echo "🎉 SUCCESS! SRK Campus Backend is now running 24/7 in the Cloud!"
echo "👉 Status check: pm2 status"
echo "👉 Live logs:    pm2 logs srk-backend"
echo "=================================================================="
