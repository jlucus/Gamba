# 💰 Crypto Tips Portfolio Analyzer

A comprehensive cryptocurrency portfolio analysis dashboard that transforms your tip transaction data into professional-grade financial insights.

## 🚀 Quick Start

### Option 1: Windows Users (Easiest)
1. Double-click `start_dashboard.bat`
2. Your dashboard will open automatically in your browser

### Option 2: Command Line
```bash
python start_server.py
```

### Option 3: Manual Server
```bash
python -m http.server 8000
```
Then open: http://localhost:8000/dashboard_launcher.html

## 📊 What's Included

### 🎯 **Dashboard Launcher** (`dashboard_launcher.html`)
- Central hub with portfolio overview
- Quick access to all analysis tools
- Real-time summary statistics

### 📈 **Advanced Portfolio Viewer** (`advanced_tips_viewer.html`)
- Interactive charts and visualizations
- Real-time market data integration
- Risk analysis and diversification metrics
- **Dan vs Others Analysis** - Compare benefactor contributions vs your tips to others
- 5 comprehensive tabs:
  - 📊 Overview - Financial summary and key metrics
  - 💼 Portfolio - Currency breakdown with current prices
  - 👥 Demographics - Top senders, recipients, counterparty analysis
  - 📈 Analytics - Activity trends and transaction patterns
  - ⚠️ Risk Analysis - Portfolio risk assessment

### 📋 **Transaction Browser** (`tips_viewer.html`)
- Browse all 643 transactions
- Advanced filtering and search
- Sortable columns
- Pagination support

### 📄 **Detailed Report** (`portfolio_summary_report.md`)
- Comprehensive written analysis
- Strategic recommendations
- Tax implications
- Market context

## 💡 Key Features

### 💰 **Financial Analysis**
- **Total Received:** $9,606.41
- **Total Sent:** $10,762.60
- **Net Position:** -$1,156.19 (-10.74% ROI)
- **Best Performer:** USDT (+$1,508.88)
- **Biggest Loss:** SOL (-$1,291.06)

### 👥 **Demographics & Insights**
- **Top Benefactor:** Dan ($2,952.66 received)
- **Biggest Recipient:** BetOnGamba ($3,755.88 sent)
- **Dan Coverage Analysis:** Shows Dan covered 27.6% of your tips to others
- **Net Deficit:** $7,755.18 between Dan's contributions and your tips to others

### ⚠️ **Risk Analysis**
- **Overall Risk Score:** 35.8/100 (Medium)
- **Diversification Score:** 76.4/100 (Good)
- **10 Different Cryptocurrencies**
- **Currency-specific risk assessments**

### 📈 **Advanced Analytics**
- Monthly activity trends
- Transaction pattern analysis
- Behavioral insights
- Market context integration
- Tax implications calculator

## 🔧 Technical Details

### **Data Files**
- `tips_consolidated.json` - Clean transaction data (643 transactions)
- `advanced_portfolio_analysis.json` - Complete analysis results
- `tips_analysis.json` - Basic statistics
- `crypto_cache.db` - Price data cache

### **Scripts**
- `price_calculator.py` - Advanced portfolio analyzer
- `consolidate_tips.py` - Data consolidation script
- `start_server.py` - Web server launcher

### **Requirements**
- Python 3.6+
- Internet connection (for real-time price data)
- Modern web browser

## 🎯 Usage Tips

### **Updating Data**
1. Replace `tips.json` with new data
2. Run: `python consolidate_tips.py`
3. Run: `python price_calculator.py`
4. Refresh your browser

### **Customization**
- Edit CSS in HTML files for styling changes
- Modify `price_calculator.py` for new analysis features
- Add new currencies in the currency mapping

### **Troubleshooting**
- **Data not loading?** Make sure you're using the local server (not file://)
- **Port 8000 in use?** Try: `python start_server.py --port 8080`
- **Charts not showing?** Check browser console for JavaScript errors

## 📊 Portfolio Summary

### **Profitable Positions**
1. **USDT:** +$1,508.88 (98.4% gain)
2. **XRP:** +$137.10 (7.7% gain)
3. **ETH:** +$100.04 (33.4% gain)
4. **LTC:** +$20.14 (1.6% gain)
5. **ADA:** +$8.21 (pure gain)

### **Loss Positions**
1. **SOL:** -$1,291.06 (45.2% loss)
2. **TRX:** -$983.14 (42.4% loss)
3. **USDC:** -$516.61 (99.8% loss)
4. **DOT:** -$139.98 (98.5% loss)

### **Top Trading Partners**
1. **BetOnGamba:** $7,255.85 total volume
2. **Dan:** $3,007.42 total volume
3. **letgonowok:** $1,699.74 total volume

## 🔒 Privacy & Security

- All data processing happens locally
- No data is sent to external servers (except for price fetching)
- Your transaction data never leaves your computer
- Price data is cached locally for performance

## 📞 Support

This is a custom-built portfolio analyzer. For questions or issues:
1. Check the browser console for error messages
2. Ensure all JSON files are valid
3. Verify Python dependencies are installed
4. Make sure you're using the local server

---

**Built with:** Python, JavaScript, Chart.js, HTML5, CSS3
**Data Source:** Your consolidated tip transactions
**Price Data:** CoinGecko API
**Last Updated:** May 26, 2025

## 🎮 Gamba API Integration

### 🔌 **Race Data API**

The application can fetch live race data from Gamba's GraphQL API. See `gamba_api_client.py` for implementation details.

#### **Sample Query Structure**
```
operationName: getRaceById
variables: {"raceId": 98}
extensions: {"persistedQuery": {"version": 1, "sha256Hash": "c682a2e9795a0f35f291d417f01543135f4be142180598bcb6159c26ba2177ef"}}
```

#### **Required Headers**
```
Method: GET
URL: https://gamba.com/_api/@
Content-Type: application/json
Authorization: Bearer [YOUR_TOKEN_HERE]
User-Agent: [STANDARD_BROWSER_USER_AGENT]
```

#### **Authentication**
- Requires valid Gamba authentication token
- Token should be added to `authorization` header
- See `gamba_api_client.py` for implementation

#### **Rate Limiting**
- Recommended: 1 request per second
- Use delays between batch requests
- Monitor for rate limit responses

#### **Sample Usage**
```python
from gamba_api_client import GambaAPIClient

# Initialize with your token
client = GambaAPIClient(auth_token="YOUR_TOKEN_HERE")

# Fetch single race
race_data = client.get_race_by_id(98)

# Fetch multiple races
races = client.get_multiple_races([34, 98, 99], delay=1.0)
```

### 🔒 **Security Notes**
- Never commit authentication tokens to version control
- Store tokens in environment variables
- Rotate tokens regularly
- Use HTTPS for all API calls

### 📋 **Sample Payloads**
See `sample_race_queries.json` for complete API examples and response formats.