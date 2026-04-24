# Quick Start: Google OAuth Setup

## For Users: Get Your Google Credentials (5 minutes)

### Step 1: Open Google Cloud Console
Go to: https://console.cloud.google.com

### Step 2: Create a Project
1. Click **"New Project"** (top-left dropdown)
2. Name: `Shakti 1.2`
3. Click **Create**
4. Wait for project to be created (might take a minute)

### Step 3: Enable Google+ API
1. In the left sidebar, click **APIs & Services** → **Library**
2. Search for **"Google+ API"**
3. Click on it
4. Click **Enable**

### Step 4: Create OAuth Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose: **Web application**
4. Under **Authorized redirect URIs**, add:
   - `http://localhost:5173`
   - `http://localhost:3000`
   (For production, add your domain)
5. Click **Create**
6. A popup appears with your credentials:
   - **Client ID** (copy this)
   - **Client Secret** (copy this)

### Step 5: Configure Shakti

#### For Backend:
Create/update `backend/.env`:
```
GOOGLE_CLIENT_ID=paste_your_client_id_here
GOOGLE_CLIENT_SECRET=paste_your_client_secret_here
```

#### For Frontend:
Update `frontend/.env`:
```
VITE_GOOGLE_CLIENT_ID=paste_your_client_id_here
```

### Step 6: Restart Servers
```powershell
# Kill existing processes
taskkill /F /IM python.exe 2>$null; taskkill /F /IM node.exe 2>$null

# Start backend
cd "c:\New folder (2)\backend"
python -m uvicorn main:app --host 127.0.0.1 --port 8001

# Start frontend (in another terminal)
cd "c:\New folder (2)\frontend"
npm run dev
```

### Step 7: Test Login
1. Go to http://localhost:5173
2. Click **"Sign in with Google"**
3. Select your Google account
4. You should see the dashboard with your usage limits!

## What You Get

✅ **Login with Google** - No password to remember
✅ **Usage Limits** - 5 analyses, 5 batch ops per 72 hours
✅ **Usage Stats** - See exactly how many you've used
✅ **Reset Timer** - Know when your quota resets
✅ **Secure** - Tokens verified by Google

## Troubleshooting

### "Google login button not showing"
- Check `VITE_GOOGLE_CLIENT_ID` in `frontend/.env`
- Restart frontend: `npm run dev`
- Clear browser cache

### "Invalid credentials"
- Make sure Client ID and Secret are correct
- Check for extra spaces when copying
- Verify http://localhost:5173 is in OAuth redirect URIs

### "Can't reach this page"
- Make sure both servers are running
- Backend: http://127.0.0.1:8001 should show message
- Frontend: http://localhost:5173 should show login page

### "CORS error"
- This means backend isn't receiving request properly
- Check if Authorization header is being sent
- Verify CORS is configured in backend

## What's Next?

1. Log in with Google ✓
2. Check your usage stats ✓
3. Use Product Analysis (5 times in 72h)
4. Use Batch Optimization (5 times in 72h)
5. See error when you exceed limits
6. Wait for 72-hour window to reset

## More Information

- Full setup guide: `_Documentation/GOOGLE_OAUTH_SETUP.md`
- Implementation details: `_Documentation/OAUTH_IMPLEMENTATION_COMPLETE.md`
- Troubleshooting: `_Documentation/GOOGLE_OAUTH_SETUP.md#troubleshooting`

---

**Questions?** Check the documentation files or review the implementation notes.
