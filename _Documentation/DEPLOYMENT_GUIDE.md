   # Shakti SEO Optimizer - Deployment Guide

## 📦 Deployment Overview

This guide will help you deploy:
- **Frontend** → Vercel (free tier available)
- **Backend** → Render.com (free tier available)

---

## 🎨 Frontend Deployment (Vercel)

### Prerequisites
- GitHub account
- Vercel account (sign up at vercel.com)
- Push your code to GitHub repository

### Steps

1. **Clean Up Completed** ✅
   - Build logs removed
   - `.gitignore` created
   - `vercel.json` configuration added

2. **Push to GitHub**
   ```bash
   cd "c:\New folder (2)\frontend"
   git init
   git add .
   git commit -m "Prepare frontend for Vercel deployment"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

3. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Vite configuration
   - **Important**: Add environment variable:
     - Variable: `VITE_API_URL`
     - Value: `https://your-backend-app.onrender.com` (update after backend deployment)

4. **Build Settings** (auto-detected)
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

5. **Deploy!**
   - Click "Deploy"
   - Wait for deployment to complete
   - Save your Vercel URL: `https://your-app.vercel.app`

---

## 🚀 Backend Deployment (Render)

### Prerequisites
- GitHub account
- Render account (sign up at render.com)
- Push your code to GitHub repository

### Steps

1. **Deployment Files Created** ✅
   - `.gitignore` for Python
   - `runtime.txt` (Python 3.11)
   - `start.sh` startup script
   - `RENDER_DEPLOY.md` instructions

2. **Push to GitHub**
   ```bash
   cd "c:\New folder (2)\backend"
   git init
   git add .
   git commit -m "Prepare backend for Render deployment"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

3. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the backend repository/folder

4. **Configure Web Service**
   - **Name**: `shakti-backend` (or your choice)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank (or specify `backend` if monorepo)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables** (Add in Render dashboard)
   - Click "Environment" tab
   - Add:
     - **Key**: `ALLOWED_ORIGINS`
     - **Value**: `https://your-app.vercel.app` (your Vercel URL from step above)
   - Add:
     - **Key**: `PYTHON_VERSION`
     - **Value**: `3.11`

6. **Deploy!**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Save your Render URL: `https://shakti-backend.onrender.com`

---

## 🔗 Connecting Frontend & Backend

### Update Frontend Environment Variable

1. Go to your Vercel project dashboard
2. Navigate to: Settings → Environment Variables
3. Edit `VITE_API_URL`:
   - Value: `https://your-backend-app.onrender.com` (your Render URL)
4. Click "Save"
5. Trigger a new deployment (Settings → Deployments → Redeploy)

### Update Backend CORS

1. Go to your Render dashboard
2. Navigate to: Environment
3. Update `ALLOWED_ORIGINS`:
   - Value: `https://your-app.vercel.app` (your Vercel URL)
4. Click "Save" - Render will auto-redeploy

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Frontend loads at Vercel URL
- [ ] Settings page allows API key configuration
- [ ] Backend health check: `https://your-backend.onrender.com/` returns JSON
- [ ] API documentation: `https://your-backend.onrender.com/docs` loads
- [ ] Single optimize works with test data
- [ ] Chat feature works
- [ ] Batch processing works with CSV upload

---

## 📝 Important Notes

### Free Tier Limitations

**Vercel Free**:
- ✅ Unlimited deployments
- ✅ Automatic SSL
- ✅ Global CDN
- ⚠️ 100GB bandwidth/month

**Render Free**:
- ✅ Automatic deploys from GitHub
- ✅ Automatic SSL
- ⚠️ Service spins down after 15 min inactivity (first request will be slow)
- ⚠️ 750 hours/month free

### Cold Starts
- Render free tier services sleep after inactivity
- First request after sleep: 30-60 seconds
- Consider upgrading to paid tier ($7/month) for always-on service

### Custom Domains
- Both Vercel and Render support custom domains
- Configure in respective dashboards under "Domains"

---

## 🔧 Troubleshooting

### Frontend Issues

**Build Fails**
- Check Vercel build logs
- Verify all dependencies in `package.json`
- Test build locally: `npm run build`

**API Calls Fail**
- Verify `VITE_API_URL` is set correctly
- Check browser console for CORS errors
- Ensure backend URL doesn't have trailing slash

### Backend Issues

**Service Won't Start**
- Check Render logs
- Verify `requirements.txt` has all dependencies
- Test locally: `uvicorn main:app --host 0.0.0.0 --port 8000`

**CORS Errors**
- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check for trailing slashes (shouldn't have any)
- Test with browser DevTools Network tab

**Python Version Mismatch**
- Ensure `runtime.txt` specifies: `3.11`
- Or update to match your local Python version

---

## 📞 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vite Docs**: https://vitejs.dev

---

## 🎉 Success!

Once deployed, your Shakti SEO Optimizer will be accessible worldwide:
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-backend.onrender.com`
- API Docs: `https://your-backend.onrender.com/docs`

Share the frontend URL with your team and start optimizing! 🚀
