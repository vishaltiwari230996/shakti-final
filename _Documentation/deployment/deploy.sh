#!/bin/bash

# Shakti Enterprise Deployment Script
# For deploying to ikshan.in

set -e

echo "🚀 Starting Shakti Enterprise Deployment..."

# Configuration
DOMAIN="ikshan.in"
PROJECT_DIR="/var/www/ikshan"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Update system
print_info "Updating system packages..."
apt update && apt upgrade -y
print_status "System updated"

# Step 2: Install dependencies
print_info "Installing dependencies..."
apt install -y python3 python3-pip python3-venv nginx git curl

# Install Node.js 20.x
if ! command -v node &> /dev/null; then
    print_info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
    print_status "Node.js installed"
else
    print_status "Node.js already installed"
fi

# Install PM2
if ! command -v pm2 &> /dev/null; then
    print_info "Installing PM2..."
    npm install -g pm2
    print_status "PM2 installed"
else
    print_status "PM2 already installed"
fi

# Step 3: Create project directory
print_info "Setting up project directory..."
mkdir -p $PROJECT_DIR
print_status "Project directory created"

# Step 4: Setup Backend
print_info "Setting up backend..."
cd $BACKEND_DIR

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
print_status "Backend dependencies installed"

# Step 5: Setup Frontend
print_info "Setting up frontend..."
cd $FRONTEND_DIR

# Install Node dependencies
npm install
print_status "Frontend dependencies installed"

# Build frontend
print_info "Building frontend..."
npm run build
print_status "Frontend built successfully"

# Step 6: Configure PM2 for backend
print_info "Configuring PM2 for backend..."
cd $BACKEND_DIR
pm2 delete shakti-api 2>/dev/null || true
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000" --name shakti-api
pm2 save
pm2 startup systemd -u $SUDO_USER --hp /home/$SUDO_USER
print_status "Backend configured with PM2"

# Step 7: Configure Nginx
print_info "Configuring Nginx..."
cat > /etc/nginx/sites-available/ikshan <<'EOF'
server {
    listen 80;
    server_name ikshan.in www.ikshan.in;

    # Frontend (React build)
    location / {
        root /var/www/ikshan/frontend/dist;
        try_files $uri /index.html;
        add_header Cache-Control "public, max-age=3600";
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/ikshan /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
systemctl restart nginx
print_status "Nginx configured and restarted"

# Step 8: Configure firewall
print_info "Configuring firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable
print_status "Firewall configured"

# Step 9: Install SSL certificate
print_info "Setting up SSL certificate..."
if ! command -v certbot &> /dev/null; then
    apt install -y certbot python3-certbot-nginx
fi

print_info "Run the following command to get SSL certificate:"
echo "sudo certbot --nginx -d ikshan.in -d www.ikshan.in --email your-email@example.com --agree-tos --non-interactive"

print_status "Deployment completed!"
echo ""
echo "============================================"
echo "🎉 Shakti Enterprise is now deployed!"
echo "============================================"
echo ""
echo "Frontend: http://ikshan.in"
echo "Backend API: http://ikshan.in/api"
echo ""
echo "Next steps:"
echo "1. Set up your .env file in $BACKEND_DIR"
echo "2. Run: sudo certbot --nginx -d ikshan.in -d www.ikshan.in"
echo "3. Update DNS A records to point to this server's IP"
echo ""
echo "Useful commands:"
echo "  - Check backend logs: pm2 logs shakti-api"
echo "  - Restart backend: pm2 restart shakti-api"
echo "  - Check Nginx status: systemctl status nginx"
echo "  - View Nginx logs: tail -f /var/log/nginx/error.log"
echo ""
