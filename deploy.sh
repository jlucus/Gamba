#!/bin/bash

# 🚀 Crypto Analytics Platform - Vercel Deployment Script

echo "🚀 Starting deployment of Crypto Analytics Platform..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if we're logged in to Vercel
echo "🔐 Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "🔑 Please log in to Vercel..."
    vercel login
fi

# Clean up any previous deployment artifacts
echo "🧹 Cleaning up previous builds..."
rm -rf .vercel

# Verify all required files are present
echo "📋 Verifying required files..."
required_files=(
    "index.html"
    "dashboard_launcher.html"
    "advanced_tips_viewer.html"
    "races_viewer.html"
    "tips_viewer.html"
    "vercel.json"
    "package.json"
    "tips_consolidated.json"
    "advanced_portfolio_analysis.json"
    "race_analysis.json"
    "races.json"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ Missing required files:"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ All required files present"

# Check file sizes (Vercel has limits)
echo "📏 Checking file sizes..."
large_files=$(find . -name "*.json" -size +10M)
if [[ -n "$large_files" ]]; then
    echo "⚠️  Warning: Large files detected (>10MB):"
    echo "$large_files"
    echo "Consider compressing or splitting these files"
fi

# Display project structure
echo "📁 Project structure:"
echo "├── 🌐 Frontend Pages"
ls -la *.html | awk '{print "│   ├── " $9 " (" $5 " bytes)"}'
echo "├── 📊 Data Files"
ls -la *.json | head -5 | awk '{print "│   ├── " $9 " (" $5 " bytes)"}'
echo "└── ⚙️  Configuration"
echo "    ├── vercel.json"
echo "    ├── package.json"
echo "    └── requirements.txt"

# Deploy to Vercel
echo ""
echo "🚀 Deploying to Vercel..."
echo "📝 Deployment will include:"
echo "   • Portfolio Analytics Dashboard"
echo "   • Race Competition Analytics"
echo "   • Transaction Browser"
echo "   • Real-time Navigation"
echo "   • Mobile-responsive Design"
echo ""

# Deploy with production flag
vercel --prod

# Check deployment status
if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "🌐 Your platform is now live at:"
    echo "   📊 Dashboard: https://crypto-analytics-platform.vercel.app"
    echo "   💼 Portfolio: https://crypto-analytics-platform.vercel.app/portfolio"
    echo "   🏁 Races: https://crypto-analytics-platform.vercel.app/races"
    echo "   📋 Transactions: https://crypto-analytics-platform.vercel.app/transactions"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Test all pages and navigation"
    echo "   2. Verify data loading correctly"
    echo "   3. Check mobile responsiveness"
    echo "   4. Set up custom domain (optional)"
    echo "   5. Configure environment variables (if needed)"
    echo ""
    echo "📊 Monitor your deployment:"
    echo "   • Vercel Dashboard: https://vercel.com/dashboard"
    echo "   • Analytics: Built-in performance monitoring"
    echo "   • Logs: Real-time error tracking"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Check vercel.json syntax"
    echo "   2. Verify all files are committed"
    echo "   3. Check file size limits"
    echo "   4. Review build logs"
    echo "   5. Try: vercel --debug"
    echo ""
    exit 1
fi

echo "✨ Deployment complete! Your crypto analytics platform is live!"
