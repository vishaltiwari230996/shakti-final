#!/bin/bash

# Quick Update Script for Shakti Enterprise
# Run this after making code changes

set -e

echo "🔄 Updating Shakti Enterprise..."

PROJECT_DIR="/var/www/ikshan"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Pull latest changes
echo "📥 Pulling latest code..."
cd $PROJECT_DIR
git pull origin main

# Update backend
echo "🔧 Updating backend..."
cd $BACKEND_DIR
source venv/bin/activate
pip install -r requirements.txt
pm2 restart shakti-api

# Update frontend
echo "💻 Rebuilding frontend..."
cd $FRONTEND_DIR
npm install
npm run build

# Restart services
echo "♻️  Restarting services..."
sudo systemctl restart nginx

echo "✅ Update complete!"
echo ""
echo "Check status with:"
echo "  pm2 status"
echo "  pm2 logs shakti-api"
