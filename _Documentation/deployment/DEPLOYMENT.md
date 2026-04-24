# 🚀 Shakti Enterprise Deployment Guide

Deploy your application to **ikshan.in**

## 📋 Prerequisites

Before starting, ensure you have:

- [x] A VPS server (Ubuntu 22.04 LTS recommended)
- [x] SSH access to your server
- [x] Domain name **ikshan.in** registered
- [x] Access to domain DNS settings
- [x] API keys for OpenAI, Google Gemini, and Anthropic Claude

---

## 🏢 Recommended Hosting Providers

### Budget-Friendly Options
| Provider | Price | Specs | Best For |
|----------|-------|-------|----------|
| **DigitalOcean** | $6/mo | 1GB RAM, 1 vCPU | Small projects |
| **Vultr** | $6/mo | 1GB RAM, 1 vCPU | Good performance |
| **Linode** | $5/mo | 1GB RAM, 1 vCPU | Starter apps |

### Production-Ready Options
| Provider | Price | Specs | Best For |
|----------|-------|-------|----------|
| **DigitalOcean** | $12/mo | 2GB RAM, 1 vCPU | Small-medium traffic |
| **AWS EC2** | ~$15/mo | t3.small | Enterprise features |
| **Google Cloud** | ~$13/mo | e2-small | Scalability |

**Recommendation**: Start with **DigitalOcean $12/mo droplet** for reliable performance.

---

## 🛠️ Step 1: Set Up Your Server

### 1.1 Create a Server Instance

**For DigitalOcean:**
1. Go to [DigitalOcean](https://www.digitalocean.com/)
2. Create a new Droplet
3. Choose:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($12/mo - 2GB RAM)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH Key (recommended) or Password
4. Note your server's **IP address**

### 1.2 Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with your actual server IP.

---

## 🌐 Step 2: Configure DNS

Point your domain to your server:

1. Log in to your domain registrar (where you bought ikshan.in)
2. Go to DNS settings
3. Add these A records:

```
Type: A
Name: @
Value: YOUR_SERVER_IP
TTL: 3600

Type: A
Name: www
Value: YOUR_SERVER_IP
TTL: 3600
```

> **Note**: DNS changes can take 24-48 hours to propagate worldwide.

---

## 📦 Step 3: Upload Your Project

### Option A: Using Git (Recommended)

```bash
# On your local machine, push to GitHub
cd "c:\New folder (2)"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/shakti-enterprise.git
git push -u origin main

# On your server
cd /var/www
sudo git clone https://github.com/yourusername/shakti-enterprise.git ikshan
sudo chown -R $USER:$USER /var/www/ikshan
```

### Option B: Using SCP

```bash
# On your local machine
scp -r "c:\New folder (2)" root@YOUR_SERVER_IP:/var/www/ikshan
```

---

## 🚀 Step 4: Run Deployment Script

### 4.1 Copy Deployment Files

```bash
cd /var/www/ikshan
chmod +x deployment/deploy.sh
```

### 4.2 Set Up Environment Variables

```bash
cd /var/www/ikshan/backend
cp ../deployment/.env.example .env
nano .env
```

Add your actual API keys:
```env
OPENAI_API_KEY=sk-your-actual-key-here
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
ENVIRONMENT=production
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 4.3 Run the Deployment Script

```bash
cd /var/www/ikshan
sudo ./deployment/deploy.sh
```

This script will:
- ✅ Install all dependencies
- ✅ Build the frontend
- ✅ Configure the backend with PM2
- ✅ Set up Nginx
- ✅ Configure the firewall

---

## 🔒 Step 5: Install SSL Certificate

After DNS has propagated (wait 1-24 hours), run:

```bash
sudo certbot --nginx -d ikshan.in -d www.ikshan.in --email your-email@example.com --agree-tos
```

Certbot will automatically:
- Obtain SSL certificate from Let's Encrypt
- Configure Nginx for HTTPS
- Set up automatic renewal

---

## ✅ Step 6: Verify Deployment

### Check Backend Status
```bash
pm2 status
pm2 logs shakti-api
```

Expected output:
```
┌─────┬────────────────┬─────────┬─────────┐
│ id  │ name           │ status  │ restart │
├─────┼────────────────┼─────────┼─────────┤
│ 0   │ shakti-api     │ online  │ 0       │
└─────┴────────────────┴─────────┴─────────┘
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### Test Your Application

Open your browser and visit:
- **Frontend**: https://ikshan.in
- **Backend API**: https://ikshan.in/api (should show: `{"message": "Shakti 1.2 Enterprise API is running"}`)

---

## 🔧 Maintenance & Updates

### Update Your Application

```bash
cd /var/www/ikshan

# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart shakti-api

# Update frontend
cd ../frontend
npm install
npm run build

# Restart Nginx
sudo systemctl restart nginx
```

### View Logs

```bash
# Backend logs
pm2 logs shakti-api

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

### Restart Services

```bash
# Restart backend
pm2 restart shakti-api

# Restart Nginx
sudo systemctl restart nginx

# Restart all services
pm2 restart all && sudo systemctl restart nginx
```

---

## 🐛 Troubleshooting

### Issue: DNS not resolving

**Solution**: Wait 24-48 hours for DNS propagation. Check with:
```bash
nslookup ikshan.in
```

### Issue: Backend not starting

**Solution**: Check logs and ensure .env file is configured:
```bash
pm2 logs shakti-api
cat /var/www/ikshan/backend/.env
```

### Issue: Frontend shows white screen

**Solution**: Rebuild frontend:
```bash
cd /var/www/ikshan/frontend
npm run build
sudo systemctl restart nginx
```

### Issue: API requests failing

**Solution**: Check Nginx proxy configuration:
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Issue: SSL certificate error

**Solution**: Ensure DNS has propagated, then retry:
```bash
sudo certbot --nginx -d ikshan.in -d www.ikshan.in --email your-email@example.com --agree-tos
```

---

## 🔐 Security Best Practices

1. **Keep system updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Change SSH port** (optional but recommended):
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change Port 22 to Port 2222
   sudo systemctl restart sshd
   ```

3. **Use SSH keys** instead of passwords

4. **Regular backups**:
   ```bash
   # Backup database and files
   tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/ikshan
   ```

5. **Monitor server resources**:
   ```bash
   htop
   pm2 monit
   ```

---

## 📊 Performance Optimization

### Enable HTTP/2 in Nginx

Edit `/etc/nginx/sites-available/ikshan`:
```nginx
listen 443 ssl http2;
```

### Enable Redis caching (optional)

```bash
sudo apt install redis-server
pip install redis
```

---

## 🎉 Success!

Your Shakti Enterprise application is now live at:

🌐 **https://ikshan.in**

Need help? Check the logs or refer to the troubleshooting section above.

---

## 📞 Quick Reference Commands

| Task | Command |
|------|---------|
| View backend logs | `pm2 logs shakti-api` |
| Restart backend | `pm2 restart shakti-api` |
| Restart Nginx | `sudo systemctl restart nginx` |
| Check SSL status | `sudo certbot certificates` |
| Renew SSL manually | `sudo certbot renew` |
| View server status | `pm2 status && sudo systemctl status nginx` |
