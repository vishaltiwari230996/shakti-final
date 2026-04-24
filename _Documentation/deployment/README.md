# Shakti Enterprise - Deployment Package

This directory contains all the files needed to deploy Shakti Enterprise to **ikshan.in**.

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | **START HERE** - Complete step-by-step deployment guide |
| `deploy.sh` | Automated deployment script for Ubuntu server |
| `update.sh` | Quick update script for future code changes |
| `nginx.conf` | Nginx web server configuration |
| `pm2.config.js` | PM2 process manager configuration |
| `.env.example` | Template for environment variables (API keys) |

## 🚀 Quick Start

1. **Read** [DEPLOYMENT.md](./DEPLOYMENT.md) for complete instructions
2. **Get a VPS** server (DigitalOcean, AWS, etc.)
3. **Upload** your project to the server
4. **Run** `deploy.sh` script
5. **Configure** DNS records for ikshan.in
6. **Install** SSL certificate with certbot

## 📖 Documentation

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

## 🔄 Updating Your App

After making code changes:

```bash
./deployment/update.sh
```

## 💡 Need Help?

Check the troubleshooting section in [DEPLOYMENT.md](./DEPLOYMENT.md)
