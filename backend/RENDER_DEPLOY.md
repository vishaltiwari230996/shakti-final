# Render Deployment Configuration

## Environment Variables
# Add these in your Render dashboard under "Environment"

# CORS Settings
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app

# Optional: Set Python version (Render auto-detects from runtime.txt if present)
# PYTHON_VERSION=3.11

## Deployment Settings (configure in Render dashboard)
# - Build Command: pip install -r requirements.txt
# - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
# - Python Version: 3.11 (or your preferred version)
