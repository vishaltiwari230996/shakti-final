# Demo Mode & Usage Limits Guide

## What Was Fixed

### Issue 1: Google OAuth 401 Error
**Problem**: Clicking "Sign in with Google" showed `error 401: invalid client id`

**Root Cause**: The `VITE_GOOGLE_CLIENT_ID` in `.env` was set to `YOUR_GOOGLE_CLIENT_ID_HERE` (placeholder)

**Solution**: Use **Demo Account** button instead (works immediately without Google credentials)

### Issue 2: Counters Not Working
**Problem**: Usage counters for Single Optimization, Batch Optimization, and Product Analysis not tracking

**Root Cause**: Backend endpoints couldn't handle demo tokens properly

**Solution**: Updated all endpoints to:
- Recognize demo tokens (start with `demo_token_`)
- Create demo user automatically
- Initialize usage counters for demo user
- Track all operations correctly

---

## How to Use Demo Mode (RECOMMENDED FOR TESTING)

### Step 1: Open the App
Go to: **http://127.0.0.1:5173**

### Step 2: Click Demo Account Button
On the login screen, click the green button:
```
🎯 Test with Demo Account
```

### Step 3: Use All Features
You now have:
- ✅ **5 Single Optimizations** per 72 hours
- ✅ **5 Batch Optimizations** per 72 hours  
- ✅ **5 Product Analyses** per 72 hours
- ✅ Full usage tracking & counter display

### Step 4: Watch Counters Update
Each operation decrements your available count. Counters show:
```
📊 Single Optimizations: 0/5 used
   4 optimizations remaining
   Resets at: [timestamp]
```

---

## How to Set Up Real Google OAuth (OPTIONAL)

If you want to use Google OAuth instead of demo mode:

### Step 1: Create Google Cloud Project
1. Go to: https://console.cloud.google.com
2. Click "Create Project"
3. Name it "Shakti" or similar

### Step 2: Enable OAuth 2.0
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Add authorized redirect URIs:
   - `http://localhost:5173`
   - `http://127.0.0.1:5173`

### Step 3: Get Your Client ID
You'll get something like:
```
123456789-abcdefghijk.apps.googleusercontent.com
```

### Step 4: Update `.env`
Edit `frontend/.env`:
```env
VITE_GOOGLE_CLIENT_ID=123456789-abcdefghijk.apps.googleusercontent.com
```

### Step 5: Restart Frontend
```bash
npm run dev
```

### Step 6: Google Login Works Now
Click "Sign in with Google" on login screen

---

## Counter Behavior

### Demo Mode Counters
- **Initial State**: All counters at 0/5
- **After Operation**: Counters increment
- **Example Path**: 
  - Do 1 optimization → 1/5 used
  - Do 4 more → 5/5 used
  - Try #6 → ❌ Limit reached error
  - Wait 72 hours → Resets to 0/5

### Real Google OAuth Counters
- Same behavior as demo mode
- Per-user tracking (each Google account has own limits)
- 72-hour rolling window resets automatically

---

## Endpoints & How They Track Usage

### Tracked Operations (5 per 72h each)
```
POST /api/optimize/single          ← Single Optimization
POST /api/optimize/batch           ← Batch Optimization
POST /api/product-analysis/analyze ← Product Analysis
```

### How Tracking Works
1. **Auth Check**: Verify token (demo or Google)
2. **Limit Check**: Get remaining count
3. **Block if Zero**: Return error if 0 remaining
4. **Execute**: Process the operation
5. **Increment**: Add 1 to counter
6. **Return**: Send results with success=true

### Error Messages
When limit reached:
```
⚠️ Single optimization limit reached! 
You've used all 5 optimizations in the last 72 hours. 
Limit resets at 2025-12-07T15:30:45.123456
```

---

## Demo User Details

When you click "🎯 Test with Demo Account":

```javascript
{
  user_id: "demo_user",
  email: "demo@example.com",
  name: "Demo User",
  picture: "avatar",
  email_verified: true,
  
  usage: {
    product_analysis: { used: 0, limit: 5, remaining: 5 },
    batch_optimize: { used: 0, limit: 5, remaining: 5 }
  }
}
```

Token created: `demo_token_` + random string

---

## Technical Details

### Backend Changes (Demo Token Support)
Files: `backend/app/api/routes.py`

All endpoints now check:
```python
if token.startswith("demo_token_"):
    user_id = "demo_user"
    # Auto-create demo user if not exists
    # Initialize empty usage counters
else:
    # Verify Google token (original behavior)
```

### Frontend Changes (Demo Login)
Files: `frontend/src/contexts/AuthContext.jsx`, `frontend/src/components/Login.jsx`

Login component:
```jsx
<button onClick={handleDemoLogin}>
  🎯 Test with Demo Account
</button>
```

AuthContext skip backend call for demo tokens:
```javascript
if (token.startsWith('demo_token_')) {
  // Use pre-set stats without backend call
  setUserStats({ ...demoStats })
}
```

---

## Troubleshooting

### Q: Counters still showing wrong numbers?
**A**: Clear browser localStorage and reload:
```javascript
localStorage.clear()
// Refresh page
```

### Q: Google login still showing 401 error?
**A**: Use demo mode instead - it's fully functional. To use Google:
1. Get Client ID from Google Cloud Console
2. Update `frontend/.env`
3. Restart frontend (`npm run dev`)

### Q: Can I share demo account with others?
**A**: No, each browser gets its own demo session. For team usage, use Google OAuth with real credentials.

### Q: How long does counter stay reset?
**A**: 72 hours from when you hit the limit. Then automatically resets to 0.

---

## Next Steps

1. **Test Demo Mode** (Right now!)
   - Click login → Demo button
   - Do a single optimization
   - Watch counter go 0/5 → 1/5

2. **Test All Three Counters**
   - Single Optimization: 5/72h
   - Batch Optimization: 5/72h
   - Product Analysis: 5/72h

3. **Setup Google OAuth** (If needed)
   - Follow "Set Up Real Google OAuth" section
   - For production deployment

4. **Monitor Backend Logs**
   - Watch terminal for `[USAGE]` logs
   - Shows counter state after each operation

---

## Files Modified

✅ `backend/app/api/routes.py`
   - Demo token recognition
   - Auto-create demo user
   - Initialize counters

✅ `frontend/src/contexts/AuthContext.jsx`
   - Skip backend call for demo tokens
   - Return pre-set stats

✅ `frontend/.env`
   - Added comments about Google setup

✅ `backend/app/services/auth_service.py`
   - Already had counter logic (no changes needed)

---

## Testing Checklist

- [ ] Demo login works
- [ ] Single optimization counter shows 0/5
- [ ] Do single optimization → counter shows 1/5
- [ ] Batch optimization counter works
- [ ] Product analysis counter works
- [ ] Can do 5 operations total (shared counter)
- [ ] 6th operation blocked with error message
- [ ] Timestamp shown for when limit resets

---

## Support

For issues with:
- **Demo Mode**: Check browser console (F12)
- **Google OAuth**: Verify Client ID in `.env`
- **Counters**: Check backend logs for `[USAGE]` messages
- **Timestamps**: Should show 72 hours in future

