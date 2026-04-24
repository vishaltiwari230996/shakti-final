# GitHub Desktop Deployment Guide - Step by Step

## 🎯 Quick Overview
We'll create two separate repositories:
1. **shakti-frontend** - For Vercel
2. **shakti-backend** - For Render

---

## Part 1: Setup Backend Repository

### Step 1: Open GitHub Desktop
- Launch GitHub Desktop application
- Sign in with your GitHub account (or create one if needed)

### Step 2: Create Backend Repository

1. **Add Local Repository**
   - Click: `File` → `Add local repository...`
   - Click `Choose...` button
   - Navigate to: `C:\New folder (2)\backend`
   - Select the `backend` folder
   - Click `Select Folder`

2. **Initialize Repository** (if prompted)
   - If you see "This directory does not appear to be a Git repository"
   - Click `create a repository`
   - Repository name: `shakti-backend`
   - Description: `Shakti SEO Optimizer - Backend API`
   - **Uncheck** "Initialize this repository with a README"
   - Click `Create Repository`

### Step 3: Make Initial Commit

1. **Review Changes**
   - You should see all your backend files listed on the left
   - Check that these files are included:
     - ✅ `main.py`
     - ✅ `requirements.txt`
     - ✅ `runtime.txt`
     - ✅ `start.sh`
     - ✅ `.gitignore`
     - ✅ `app/` folder

2. **Create Commit**
   - In the bottom left, you'll see:
     - Summary field (required)
     - Description field (optional)
   - Summary: `Initial commit - Backend setup for deployment`
   - Description: `FastAPI backend with all deployment files`
   - Click `Commit to main`

### Step 4: Publish to GitHub

1. **Publish Repository**
   - Click the blue `Publish repository` button in the top toolbar
   - Settings:
     - Name: `shakti-backend`
     - Description: `Shakti SEO Optimizer Backend API`
     - **Keep your code private**: Check if you want it private
     - Organization: Keep as "None" (use your personal account)
   - Click `Publish repository`

2. **Wait for Upload**
   - GitHub Desktop will upload your code
   - You'll see a success message when done
   - Note: It might take 30-60 seconds

3. **Verify on GitHub**
   - Click `Repository` → `View on GitHub`
   - Your backend code should be visible online
   - **Copy the repository URL** (you'll need it for Render)
   - Example: `https://github.com/yourusername/shakti-backend`

---

## Part 2: Setup Frontend Repository

### Step 1: Add Frontend Repository

1. **Switch Repository**
   - Click: `File` → `Add local repository...`
   - Click `Choose...` button
   - Navigate to: `C:\New folder (2)\frontend`
   - Select the `frontend` folder
   - Click `Select Folder`

2. **Initialize Repository**
   - Click `create a repository`
   - Repository name: `shakti-frontend`
   - Description: `Shakti SEO Optimizer - Frontend UI`
   - **Uncheck** "Initialize this repository with a README"
   - Click `Create Repository`

### Step 2: Make Initial Commit

1. **Review Changes**
   - Check that these files are included:
     - ✅ `package.json`
     - ✅ `vite.config.js`
     - ✅ `vercel.json`
     - ✅ `.gitignore`
     - ✅ `.env.example`
     - ✅ `src/` folder
   - **Should NOT see** (thanks to .gitignore):
     - ❌ `node_modules/`
     - ❌ `build_log.txt` files
     - ❌ `dist/` folder

2. **Create Commit**
   - Summary: `Initial commit - Frontend ready for Vercel`
   - Description: `React + Vite frontend with responsive design`
   - Click `Commit to main`

### Step 3: Publish to GitHub

1. **Publish Repository**
   - Click `Publish repository`
   - Settings:
     - Name: `shakti-frontend`
     - Description: `Shakti SEO Optimizer Frontend`
     - Choose private/public as preferred
   - Click `Publish repository`

2. **Verify on GitHub**
   - Click `Repository` → `View on GitHub`
   - **Copy the repository URL**
   - Example: `https://github.com/yourusername/shakti-frontend`

---

## Part 3: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to: https://render.com
2. Click `Get Started for Free`
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 2: Create Web Service

1. **New Web Service**
   - Click `New +` → `Web Service`
   - You should see your `shakti-backend` repository listed
   - Click `Connect` next to `shakti-backend`

2. **Configure Service**
   Fill in these settings:
   
   - **Name**: `shakti-backend` (or your choice)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

3. **Select Plan**
   - Choose `Free` plan
   - Scroll down

4. **Environment Variables** (Important!)
   - Click `Add Environment Variable`
   - Add:
     - **Key**: `PYTHON_VERSION`
     - **Value**: `3.11`
   - Click `Add Environment Variable` again
   - Add:
     - **Key**: `ALLOWED_ORIGINS`
     - **Value**: `*` (we'll update this later with Vercel URL)

5. **Create Web Service**
   - Click `Create Web Service`
   - Wait 5-10 minutes for deployment
   - ☕ Grab a coffee!

### Step 3: Get Backend URL

1. **Wait for Deploy**
   - Watch the logs as it deploys
   - Wait for "Your service is live 🎉"

2. **Copy Your Backend URL**
   - At the top, you'll see your service URL
   - Example: `https://shakti-backend.onrender.com`
   - **COPY THIS URL** - you'll need it for Vercel!

3. **Test Your Backend**
   - Open browser to: `https://your-backend-url.onrender.com`
   - You should see: `{"message":"Shakti 1.2 Enterprise API is running"}`
   - ✅ If you see this, backend is working!

---

## Part 4: Deploy Frontend to Vercel

### Step 1: Create Vercel Account
1. Go to: https://vercel.com
2. Click `Sign Up`
3. Choose `Continue with GitHub`
4. Authorize Vercel

### Step 2: Import Project

1. **New Project**
   - Click `Add New...` → `Project`
   - You should see your `shakti-frontend` repository
   - Click `Import` next to `shakti-frontend`

2. **Configure Project**
   - **Framework Preset**: Vite (should auto-detect)
   - **Root Directory**: Leave as `./`
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `dist` (auto-filled)
   - **Install Command**: `npm install` (auto-filled)

3. **Environment Variables** (CRITICAL!)
   - Click to expand "Environment Variables"
   - Add variable:
     - **Name**: `VITE_API_URL`
     - **Value**: `https://your-backend-url.onrender.com` (paste your Render URL from Part 3)
   - Make sure there's NO trailing slash!

4. **Deploy**
   - Click `Deploy`
   - Wait 2-3 minutes
   - ☕ Almost there!

### Step 3: Get Frontend URL

1. **Deployment Success**
   - You'll see confetti 🎉
   - Your app is live!

2. **Copy Your Frontend URL**
   - Example: `https://shakti-frontend.vercel.app`
   - Or: `https://shakti-frontend-abc123.vercel.app`
   - **COPY THIS URL**

3. **Test Your Frontend**
   - Click `Visit` or open the URL in browser
   - You should see your beautiful redesigned Shakti app!
   - ✅ App loads with white/blue theme

---

## Part 5: Connect Frontend & Backend (Final Step!)

### Update Backend CORS

1. **Go to Render Dashboard**
   - Open: https://dashboard.render.com
   - Click on your `shakti-backend` service

2. **Update Environment Variable**
   - Click `Environment` in left sidebar
   - Find `ALLOWED_ORIGINS`
   - Click `Edit`
   - Change value from `*` to your Vercel URL
   - Example: `https://shakti-frontend.vercel.app`
   - Click `Save Changes`

3. **Wait for Redeploy**
   - Render will automatically redeploy (1-2 minutes)
   - Watch the logs
   - Wait for "Your service is live"

---

## ✅ Final Verification

Test these features:

1. **Open Your App**
   - Go to your Vercel URL
   - Frontend should load ✅

2. **Test Settings Page**
   - Navigate to Settings
   - Try entering an API key
   - Click Save
   - Should save successfully ✅

3. **Test Single Optimize** (if you have API key)
   - Go to Optimize page
   - Enter test product data
   - Add your OpenAI API key in settings
   - Click "Run Optimization"
   - Should work! ✅

4. **Test Chat** (if you have API key)
   - Go to Chat page
   - Send a test message
   - Should get AI response ✅

---

## 🎉 Success!

Your app is now live at:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **API Docs**: `https://your-backend.onrender.com/docs`

---

## 📝 Making Updates

When you make code changes:

### Using GitHub Desktop:

1. **Make your code changes** in VS Code or your editor

2. **Open GitHub Desktop**
   - Switch to the repository you changed (frontend or backend)
   - You'll see your changes listed

3. **Commit changes**
   - Review the changes
   - Write a commit message
   - Click `Commit to main`

4. **Push to GitHub**
   - Click `Push origin` button (top right)
   - Your changes upload to GitHub

5. **Automatic Deployment**
   - Vercel: Automatically deploys in 1-2 minutes
   - Render: Automatically deploys in 5-10 minutes
   - You'll get email notifications when done

---

## 🆘 Troubleshooting

### Backend Issues

**"Service Unavailable" on first request**
- Render free tier sleeps after inactivity
- First request takes 30-60 seconds (cold start)
- Subsequent requests are fast
- This is normal for free tier

**API calls fail from frontend**
- Check CORS: Make sure `ALLOWED_ORIGINS` matches your Vercel URL exactly
- Check URL: Make sure `VITE_API_URL` in Vercel has no trailing slash
- Check logs: View Render logs for error messages

### Frontend Issues

**"Failed to fetch" errors**
- Check browser console (F12)
- Verify `VITE_API_URL` is set correctly in Vercel
- Make sure backend is awake (visit backend URL first)

**Environment variable not working**
- Did you redeploy after adding the variable?
- Go to Vercel → Settings → Environment Variables
- Make sure it's spelled exactly: `VITE_API_URL`
- Click Deployments → Redeploy latest

---

## 🎯 Pro Tips

1. **Custom Domain** (Optional)
   - Both Vercel and Render support custom domains
   - Configure in respective dashboards

2. **Monitoring**
   - Render: Has built-in logs and metrics
   - Vercel: Analytics available in dashboard

3. **Upgrade to Paid** (Optional)
   - Render: $7/month for always-on service (no cold starts)
   - Vercel: Free tier is usually sufficient

4. **GitHub Desktop Tips**
   - Use descriptive commit messages
   - Commit often (small changes)
   - Pull before pushing if working with team

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Desktop Help**: https://docs.github.com/desktop

Congratulations on deploying your app! 🚀🎉
