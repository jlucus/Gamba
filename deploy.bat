@echo off
REM 🚀 Crypto Analytics Platform - Vercel Deployment Script (Windows)

echo 🚀 Starting deployment of Crypto Analytics Platform...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo 📥 Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Vercel CLI...
    npm install -g vercel
)

REM Check if we're logged in to Vercel
echo 🔐 Checking Vercel authentication...
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo 🔑 Please log in to Vercel...
    vercel login
)

REM Clean up any previous deployment artifacts
echo 🧹 Cleaning up previous builds...
if exist .vercel rmdir /s /q .vercel

REM Verify required files are present
echo 📋 Verifying required files...
set "missing_files="

if not exist "index.html" set "missing_files=%missing_files% index.html"
if not exist "dashboard_launcher.html" set "missing_files=%missing_files% dashboard_launcher.html"
if not exist "advanced_tips_viewer.html" set "missing_files=%missing_files% advanced_tips_viewer.html"
if not exist "races_viewer.html" set "missing_files=%missing_files% races_viewer.html"
if not exist "tips_viewer.html" set "missing_files=%missing_files% tips_viewer.html"
if not exist "vercel.json" set "missing_files=%missing_files% vercel.json"
if not exist "package.json" set "missing_files=%missing_files% package.json"
if not exist "tips_consolidated.json" set "missing_files=%missing_files% tips_consolidated.json"
if not exist "advanced_portfolio_analysis.json" set "missing_files=%missing_files% advanced_portfolio_analysis.json"
if not exist "race_analysis.json" set "missing_files=%missing_files% race_analysis.json"
if not exist "races.json" set "missing_files=%missing_files% races.json"

if not "%missing_files%"=="" (
    echo ❌ Missing required files: %missing_files%
    pause
    exit /b 1
)

echo ✅ All required files present

REM Display project info
echo.
echo 📁 Project structure verified:
echo ├── 🌐 Frontend Pages
dir /b *.html
echo ├── 📊 Data Files  
dir /b *.json | findstr /v "package.json vercel.json"
echo └── ⚙️ Configuration
echo     ├── vercel.json
echo     ├── package.json
echo     └── requirements.txt

REM Deploy to Vercel
echo.
echo 🚀 Deploying to Vercel...
echo 📝 Deployment will include:
echo    • Portfolio Analytics Dashboard
echo    • Race Competition Analytics  
echo    • Transaction Browser
echo    • Real-time Navigation
echo    • Mobile-responsive Design
echo.

REM Deploy with production flag
vercel --prod

if errorlevel 1 (
    echo.
    echo ❌ Deployment failed!
    echo.
    echo 🔧 Troubleshooting steps:
    echo    1. Check vercel.json syntax
    echo    2. Verify all files are present
    echo    3. Check file size limits
    echo    4. Review build logs
    echo    5. Try: vercel --debug
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 Deployment successful!
echo.
echo 🌐 Your platform is now live at:
echo    📊 Dashboard: https://crypto-analytics-platform.vercel.app
echo    💼 Portfolio: https://crypto-analytics-platform.vercel.app/portfolio
echo    🏁 Races: https://crypto-analytics-platform.vercel.app/races
echo    📋 Transactions: https://crypto-analytics-platform.vercel.app/transactions
echo.
echo 🔧 Next steps:
echo    1. Test all pages and navigation
echo    2. Verify data loading correctly
echo    3. Check mobile responsiveness
echo    4. Set up custom domain (optional)
echo    5. Configure environment variables (if needed)
echo.
echo 📊 Monitor your deployment:
echo    • Vercel Dashboard: https://vercel.com/dashboard
echo    • Analytics: Built-in performance monitoring
echo    • Logs: Real-time error tracking
echo.
echo ✨ Deployment complete! Your crypto analytics platform is live!
echo.
pause
