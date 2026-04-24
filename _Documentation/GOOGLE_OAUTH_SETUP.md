# Google OAuth & Usage Limits Setup Guide

## Overview
Shakti 1.2 now includes Google OAuth authentication with built-in usage limits:
- **5 Product Analyses per 72 hours** 
- **5 Batch Optimizations per 72 hours**
- Unlimited competitor analysis, chat, and SEO features

## Backend Setup

### 1. Install Dependencies
```bash
# Google OAuth validation library (already included)
pip install google-auth
```

### 2. Configure Google OAuth

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project called "Shakti 1.2"
3. Enable the "Google+ API"

#### Step 2: Create OAuth Credentials
1. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
2. Select **Web application**
3. Set authorized redirect URIs:
   - `http://localhost:5173` (development)
   - `http://localhost:3000` (alternative)
   - Your production domain

4. Copy your **Client ID**

#### Step 3: Set Environment Variables
Create or update `.env` in the backend root:
```bash
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_FROM_STEP_2
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_FROM_STEP_2
```

### 3. Backend API Endpoints

#### POST `/api/auth/google-login`
Verify Google token and create/update user
```json
{
  "token": "google_id_token"
}
```
Response:
```json
{
  "success": true,
  "user": {
    "user_id": "google_sub",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://...",
    "email_verified": true
  },
  "message": "Login successful"
}
```

#### GET `/api/auth/user-stats`
Get current user's usage statistics
```
Headers: Authorization: Bearer {google_token}
```
Response:
```json
{
  "user": {...},
  "usage": {
    "product_analysis": {
      "used": 2,
      "limit": 5,
      "remaining": 3,
      "resets_at": "2024-12-07T10:00:00"
    },
    "batch_optimize": {
      "used": 1,
      "limit": 5,
      "remaining": 4,
      "resets_at": "2024-12-07T10:00:00"
    }
  }
}
```

### 4. Protected Endpoints

Both `/api/product-analysis/analyze` and `/api/optimize/batch` now require authorization:

```
Headers: Authorization: Bearer {google_token}
```

**Response if limit exceeded (429):**
```json
{
  "success": false,
  "error": "⚠️ Usage limit reached! You've used all 5 product analyses in the last 72 hours. Limit resets at ..."
}
```

## Frontend Setup

### 1. Install Dependencies
```bash
npm install @react-oauth/google react-ga4
```

### 2. Configure Environment Variables
Update `frontend/.env`:
```
VITE_GA_ID=G-YOUR-MEASUREMENT-ID
VITE_GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_FROM_GOOGLE_CONSOLE
```

### 3. Authentication Flow

#### AuthContext (`src/contexts/AuthContext.jsx`)
- Manages user authentication state
- Stores token in localStorage
- Provides `useAuth()` hook
- Automatically fetches user stats after login

#### Login Component (`src/components/Login.jsx`)
- Google OAuth login button
- Displays usage limit information
- Sends token to backend for verification
- Redirects to dashboard on success

#### UserProfile Component (`src/components/UserProfile.jsx`)
- Shows user avatar and name
- Displays current usage statistics with progress bars
- Shows reset time for limits
- Logout button

### 4. Protected Pages

All pages are protected - unauthenticated users see the login page:

```jsx
import { useAuth } from '../contexts/AuthContext'

function MyPage() {
  const { isAuthenticated, token, userStats } = useAuth()
  
  // Send requests with auth header
  const response = await axios.post('/api/endpoint', data, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
}
```

### 5. Component Integration

#### ProductAnalysis Page
- Sends token with `/api/product-analysis/analyze` request
- Receives usage limit errors if quota exceeded
- Displays error message to user

#### BatchOptimize Page
- Sends token with `/api/optimize/batch` request
- Receives usage limit errors if quota exceeded
- Supports batch processing within limits

## Usage Limit Implementation

### Backend Logic (`auth_service.py`)
```python
# Check if user has remaining quota
usage_check = AuthService.check_usage_limit(user_id, 'product_analysis')

if not usage_check['allowed']:
    # Return 429 or error response
    return {"error": "Usage limit reached..."}

# Perform operation...

# Increment counter
AuthService.increment_usage(user_id, 'product_analysis')
```

### 72-Hour Reset Window
- Limits are per 72-hour rolling window
- Reset time is returned in responses
- Automatically resets when window expires
- Users can see exact reset time in their profile

## Testing

### Test Login
```bash
# Navigate to http://localhost:5173
# Click "Sign in with Google"
# Accept permissions
# Verify you see dashboard and usage stats
```

### Test Usage Limits
1. Perform 5 product analyses within 72 hours
2. Attempt 6th analysis
3. You should see error: "Usage limit reached! ... Limit resets at ..."
4. Check UserProfile dropdown to see remaining quota

### Test Token Expiry
1. Open DevTools → Application → LocalStorage
2. Find `googleToken` entry
3. Clear it manually
4. Try to access any page
5. You should be redirected to login

## Troubleshooting

### Issue: "Invalid or expired token"
**Solution:** 
- Clear localStorage: `localStorage.clear()`
- Log out and log back in
- Check if token is still valid in Google Account settings

### Issue: CORS error on login
**Solution:**
- Ensure `http://localhost:5173` is in Google OAuth redirect URIs
- Check CORS configuration in backend
- Restart backend and frontend

### Issue: Google login button not appearing
**Solution:**
- Verify `VITE_GOOGLE_CLIENT_ID` is set correctly
- Check browser console for errors
- Ensure @react-oauth/google is installed: `npm install @react-oauth/google`

### Issue: Usage stats not updating
**Solution:**
- Manually refresh: Click user profile dropdown
- Check browser console for API errors
- Verify Authorization header is being sent

## API Reference

### AuthService Methods

```python
# Verify token
AuthService.verify_google_token(token: str) -> Dict

# Create or update user
AuthService.create_or_update_user(user_data: Dict) -> Dict

# Check limit
AuthService.check_usage_limit(user_id: str, operation: str) -> Dict

# Increment counter
AuthService.increment_usage(user_id: str, operation: str) -> Dict

# Get stats
AuthService.get_user_stats(user_id: str) -> Dict
```

## Future Enhancements

1. **Database Integration**
   - Replace in-memory storage with PostgreSQL/MongoDB
   - Persist user data and usage history

2. **Premium Tiers**
   - Free: 5 analyses, 5 batch ops per 72h
   - Pro: 50 analyses, 50 batch ops per 72h
   - Enterprise: Unlimited access

3. **Usage Analytics**
   - Track which features users use most
   - Monthly usage reports
   - Integration with Google Analytics

4. **Advanced Auth**
   - Two-factor authentication
   - API key generation for programmatic access
   - Role-based access control (RBAC)

5. **Billing**
   - Monthly subscription tracking
   - Stripe integration
   - Usage-based pricing

## Security Notes

1. **Token Storage**
   - Tokens stored in localStorage (development only)
   - For production, use secure HTTP-only cookies
   - Never expose tokens in URLs

2. **Backend Validation**
   - All tokens verified with Google
   - Invalid tokens rejected
   - CORS properly configured

3. **Data Privacy**
   - User data minimal: email, name, picture
   - Usage data stored server-side only
   - No personal data shared with third parties

## Deployment Checklist

- [ ] Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in production
- [ ] Add production domain to Google OAuth redirect URIs
- [ ] Use HTTPS for all OAuth flows
- [ ] Replace in-memory storage with database
- [ ] Configure secure session management
- [ ] Enable rate limiting on auth endpoints
- [ ] Set up logging for auth events
- [ ] Test OAuth flow end-to-end
- [ ] Document backup/recovery procedures
