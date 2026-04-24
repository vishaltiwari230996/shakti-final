# _Documentation Folder

Comprehensive guides, deployment configurations, and troubleshooting documentation for the Shakti 1.2 project.

## 📑 Folder Structure

```
_Documentation/
├── Setup & Troubleshooting Guides
│   ├── DEBUG_CONNECTION.md          # Fix frontend-backend connection issues
│   ├── DEPLOYMENT_GUIDE.md          # Production deployment steps
│   ├── DEPLOY_WITHOUT_GIT.md        # Manual deployment without Git
│   ├── GITHUB_DESKTOP_GUIDE.md      # Using GitHub Desktop app
│   ├── INSTALL_GIT.md               # Git installation instructions
│   ├── SPA_ROUTING_FIX.md           # React routing configuration
│   └── README.md                    # This file
│
└── deployment/                       # Server & deployment configs
    ├── nginx.conf                   # Nginx reverse proxy configuration
    ├── pm2.config.js                # PM2 process manager config
    ├── deploy.sh                    # Deployment shell script
    ├── update.sh                    # Update/redeploy shell script
    ├── README.md                    # Deployment setup guide
    └── DEPLOYMENT.md                # Detailed deployment instructions
```

## 📖 Guide Overview

### 🔧 Setup & Troubleshooting

#### `DEBUG_CONNECTION.md`
**Purpose**: Troubleshoot issues when frontend cannot connect to backend

**Common Issues Covered**:
- ECONNREFUSED on port 8000/8001
- Proxy configuration errors
- CORS issues
- Vite dev server not connecting

**When to Use**: Frontend shows API connection errors

---

#### `INSTALL_GIT.md`
**Purpose**: Install Git on Windows/Mac/Linux

**Covers**:
- Download links
- Installation steps per OS
- Verification commands
- Initial Git configuration

**When to Use**: First-time Git setup

---

#### `GITHUB_DESKTOP_GUIDE.md`
**Purpose**: Use GitHub Desktop instead of command line

**Covers**:
- Installation and setup
- Cloning repositories
- Committing changes
- Pushing to GitHub
- Managing branches

**When to Use**: Prefer GUI over terminal for Git

---

#### `SPA_ROUTING_FIX.md`
**Purpose**: Configure React SPA routing in development/production

**Covers**:
- Vite router setup
- 404 fixes on page refresh
- Deployment routing configuration

**When to Use**: React Router not working properly

---

#### `DEPLOYMENT_GUIDE.md`
**Purpose**: Deploy application to production servers

**Covers**:
- Environment preparation
- Backend deployment
- Frontend deployment
- Domain configuration
- SSL certificates
- Monitoring and logs

**When to Use**: Ready to deploy to Railway/Heroku/Custom server

---

#### `DEPLOY_WITHOUT_GIT.md`
**Purpose**: Deploy without using Git (manual upload)

**Covers**:
- Manual file upload methods
- Direct SSH deployment
- FTP configuration
- When to use this approach

**When to Use**: Git not available or not preferred

---

### 🚀 Deployment Configuration

#### `deployment/nginx.conf`
**Purpose**: Nginx reverse proxy configuration

**Handles**:
- Frontend serving (static files)
- Backend API proxying
- SSL/HTTPS setup
- Compression (gzip)
- Security headers

**Use Case**: Production server with Nginx

---

#### `deployment/pm2.config.js`
**Purpose**: PM2 process manager configuration

**Manages**:
- Backend server process
- Auto-restart on crash
- Logging
- Monitoring
- Graceful shutdown

**Use Case**: Keep backend running 24/7

---

#### `deployment/deploy.sh`
**Purpose**: One-command deployment script

**Performs**:
- Pull latest code
- Install dependencies
- Restart services
- Health checks

**Usage**:
```bash
bash deploy.sh
```

---

#### `deployment/update.sh`
**Purpose**: Quick update/redeploy without full setup

**Performs**:
- Pull changes
- Restart services
- Skip full installation

**Usage**:
```bash
bash update.sh
```

---

#### `deployment/README.md`
**Purpose**: Quick deployment reference guide

**Contains**:
- Port requirements
- Service startup commands
- Firewall rules
- Quick troubleshooting

---

#### `deployment/DEPLOYMENT.md`
**Purpose**: Detailed deployment instructions

**Covers**:
- Step-by-step setup
- File structure on server
- Service configuration
- Maintenance procedures
- Monitoring and logging

**When to Use**: Setting up production environment from scratch

---

## 🎯 Quick Navigation

**I need to...**

| Need | Read This |
|------|-----------|
| Fix connection errors | `DEBUG_CONNECTION.md` |
| Install Git | `INSTALL_GIT.md` |
| Use Git GUI | `GITHUB_DESKTOP_GUIDE.md` |
| Fix React routing | `SPA_ROUTING_FIX.md` |
| Deploy to production | `DEPLOYMENT_GUIDE.md` |
| Deploy without Git | `DEPLOY_WITHOUT_GIT.md` |
| Configure Nginx | `deployment/nginx.conf` |
| Run as daemon | `deployment/pm2.config.js` |
| Quick deploy | `deployment/deploy.sh` |
| Quick update | `deployment/update.sh` |
| Deployment overview | `deployment/README.md` |
| Detailed deployment | `deployment/DEPLOYMENT.md` |

---

## 📋 Before Reading Any Guide

1. **Ensure requirements met**:
   - Python 3.9+ installed
   - Node.js 18+ installed
   - Git installed (for most guides)
   - Appropriate OS (Windows/Mac/Linux)

2. **Have information ready**:
   - Server IP/hostname
   - SSH credentials
   - Domain name
   - SSL certificate (if applicable)
   - API keys (OpenAI, etc.)

3. **Check project README first**:
   - Located at project root
   - Has quick start instructions
   - Lists all endpoints and features

---

## 🐛 Troubleshooting Hierarchy

**Check in this order**:

1. **Project README** → Overview and quick start
2. **DEBUG_CONNECTION.md** → Connection issues
3. **Specific guide** → Feature-specific problems (routing, deployment, etc.)
4. **deployment/README.md** → Server/deployment issues
5. **Terminal output** → Backend logs and error messages
6. **Browser console** → Frontend JavaScript errors

---

## 💡 Best Practices

### For Development
- Keep local environment clean (follow quick start)
- Test API endpoints with Postman/curl
- Use browser DevTools for frontend debugging
- Check backend logs: `tail -f backend.log`

### For Deployment
- Test in staging first
- Keep backups before major changes
- Monitor logs and performance
- Document any custom configurations
- Set up SSL/HTTPS in production

### For Git Workflow
- Commit frequently with clear messages
- Use meaningful branch names
- Review changes before pushing
- Keep local branch updated

---

## 📞 Support Resources

**If stuck on**:

| Topic | First Look | Alternative |
|-------|-----------|-------------|
| Git | `INSTALL_GIT.md` | Official Git docs |
| Frontend | `SPA_ROUTING_FIX.md` | React Router docs |
| Backend | `DEBUG_CONNECTION.md` | FastAPI docs |
| Server | `deployment/README.md` | Nginx/PM2 official |
| Connection | `DEBUG_CONNECTION.md` | Check port 8001 |

---

## 📝 File Maintenance

**Last Updated**: December 2024

**Files that may need updates**:
- Port numbers (if changed from 8001/5173)
- Domain names (if deployed)
- Server configuration (if infrastructure changes)
- Dependency versions (regularly check)

---

## 🔒 Security Notes

⚠️ **Never commit**:
- `.env` files with API keys
- Credentials or passwords
- Private configuration files

✅ **Always use**:
- Environment variables for secrets
- `.gitignore` for sensitive files
- HTTPS in production
- Strong SSH keys

---

**Keep this folder organized and updated as the project evolves!**
