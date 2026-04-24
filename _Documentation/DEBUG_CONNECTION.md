# Debugging API Connection

## 🔍 The Issue
The app is still trying to connect to `https://frontend.../api` instead of your backend. This means the environment variable isn't being picked up correctly.

## 🔧 The Fix
I've removed a configuration in `vite.config.js` that was likely blocking the variable, and added a debug log.

## 🚀 Steps to Fix

1. **Open GitHub Desktop**
   - Switch to `shakti-frontend`
   - Commit the changes to `vite.config.js` and `src/main.jsx`
   - Push to GitHub

2. **Check Vercel Environment Variable (CRITICAL)**
   - Go to Vercel Dashboard
   - Settings → Environment Variables
   - **Verify `VITE_API_URL` exists**
   - Value should be: `https://your-backend.onrender.com` (no trailing slash)
   - **IMPORTANT:** If you added this variable *after* the last deployment, you MUST redeploy.

3. **How to Redeploy in Vercel**
   - Go to **Deployments** tab
   - Click the three dots `...` on the top deployment
   - Select **Redeploy**
   - This forces Vercel to rebuild with the new environment variables

4. **Verify the Fix**
   - Open your app
   - Open Console (F12)
   - Look for the log: `Current API URL: ...`
   - It should show your backend URL.
   - If it shows `undefined` or empty, the variable is not set in Vercel.

Let me know what the console log says!
