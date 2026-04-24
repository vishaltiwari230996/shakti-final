# How to Install Git on Windows

## Quick Install Steps

1. **Download Git**
   - Go to: https://git-scm.com/download/win
   - The download should start automatically
   - Or click "Click here to download manually" if it doesn't

2. **Run the Installer**
   - Double-click the downloaded `.exe` file
   - Click "Next" through the installation wizard
   - **Important selections:**
     - Default editor: Use Visual Studio Code (or your preference)
     - PATH environment: **"Git from the command line and also from 3rd-party software"** (recommended)
     - Line ending conversions: "Checkout Windows-style, commit Unix-style line endings"
     - Terminal emulator: "Use Windows' default console window"
     - Leave other options as default

3. **Verify Installation**
   - Close and reopen PowerShell/Terminal
   - Run: `git --version`
   - You should see something like: `git version 2.43.0.windows.1`

4. **Configure Git (First Time Setup)**
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## After Installation

Once Git is installed, continue with the deployment steps in `DEPLOYMENT_GUIDE.md`:

```powershell
cd "c:\New folder (2)\backend"
git init
git add .
git commit -m "Prepare backend for Render deployment"
```

---

## Alternative: GitHub Desktop (GUI Option)

If you prefer a graphical interface:

1. Download GitHub Desktop: https://desktop.github.com
2. Install and sign in with your GitHub account
3. Click "Add" → "Add existing repository"
4. Browse to your backend folder
5. Click "Create repository" if not already initialized
6. Make your initial commit using the GUI
7. Publish to GitHub

Both options work equally well for deployment!
