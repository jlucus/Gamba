# 🏗️ Project Structure

## 📁 Directory Layout

```
supitsj/
├── 📊 Data Files
│   ├── tips.json                           # Raw tip transaction data (concatenated)
│   ├── tips_consolidated.json              # Consolidated tip transactions
│   ├── races.json                          # Race competition data
│   ├── advanced_portfolio_analysis.json    # Complete portfolio analysis
│   ├── tips_analysis.json                  # Basic tip statistics
│   └── crypto_cache.db                     # Price data cache (SQLite)
│
├── 🌐 Web Interface
│   ├── dashboard_launcher.html             # Main dashboard entry point
│   ├── advanced_tips_viewer.html           # Advanced portfolio viewer
│   ├── tips_viewer.html                    # Transaction browser
│   └── races_viewer.html                   # Race analytics viewer (NEW)
│
├── 🐍 Python Scripts
│   ├── consolidate_tips.py                 # Consolidate tip data
│   ├── price_calculator.py                 # Portfolio analysis engine
│   ├── races_analyzer.py                   # Race data analyzer (NEW)
│   ├── gamba_api_client.py                 # Gamba API integration (NEW)
│   └── start_server.py                     # Web server launcher
│
├── 📄 Documentation
│   ├── README.md                           # Main documentation
│   ├── portfolio_summary_report.md         # Portfolio analysis report
│   ├── project_structure.md               # This file
│   └── api_documentation.md                # Gamba API docs (NEW)
│
├── 🚀 Launchers
│   ├── start_dashboard.bat                 # Windows launcher
│   └── requirements.txt                    # Python dependencies (NEW)
│
└── 📋 Sample Data
    ├── sample_race_queries.json            # Sample API payloads (NEW)
    └── sample_responses.json               # Sample API responses (NEW)
```

## 🎯 Component Overview

### 📊 **Data Layer**
- **Tips Data**: Transaction history and portfolio analysis
- **Races Data**: Competition standings and prize distributions
- **Market Data**: Real-time cryptocurrency prices
- **Cache Layer**: Local SQLite database for performance

### 🌐 **Presentation Layer**
- **Dashboard**: Central hub with overview metrics
- **Portfolio Viewer**: Advanced financial analysis
- **Transaction Browser**: Detailed transaction exploration
- **Race Viewer**: Competition analytics and standings

### 🔧 **Business Logic Layer**
- **Portfolio Analyzer**: Financial calculations and risk assessment
- **Race Analyzer**: Competition metrics and player performance
- **API Client**: Gamba endpoint integration
- **Data Consolidator**: Raw data processing and cleaning

### 🔌 **Integration Layer**
- **Gamba API**: Live race data and player standings
- **CoinGecko API**: Real-time cryptocurrency prices
- **Local Server**: HTTP server for web interface

## 🎮 **Race Analytics Features**

### 📈 **Competition Metrics**
- Prize pool analysis across races
- Player performance tracking
- VIP level distribution
- Wagering volume analysis

### 🏆 **Player Standings**
- Leaderboard visualization
- Performance trends
- Prize distribution analysis
- Cross-race comparison

### 💰 **Financial Integration**
- Race prize correlation with tip data
- Player overlap analysis
- Revenue impact assessment
- ROI calculations for sponsored races

## 🔄 **Data Flow**

```
Raw Data Sources
       ↓
Data Consolidation
       ↓
Analysis Engines
       ↓
Web Interface
       ↓
User Insights
```

### **Detailed Flow:**
1. **Data Ingestion**: Tips JSON + Races JSON + API calls
2. **Processing**: Consolidation, validation, enrichment
3. **Analysis**: Portfolio metrics + Race analytics + Cross-correlation
4. **Presentation**: Interactive dashboards + Reports
5. **Updates**: Real-time price feeds + Live race data

## 🎯 **Integration Points**

### **Tips ↔ Races**
- Player overlap identification
- Prize impact on tip behavior
- Sponsored race ROI analysis
- Community engagement metrics

### **Market Data ↔ Portfolio**
- Real-time valuation
- Risk assessment
- Performance tracking
- Tax implications

### **API ↔ Live Data**
- Race standings updates
- Player performance tracking
- Prize distribution monitoring
- Eligibility verification

## 🚀 **Deployment Architecture**

### **Local Development**
- Python HTTP server
- File-based data storage
- Browser-based interface
- Real-time API integration

### **Production Ready**
- Docker containerization
- Database backend
- API rate limiting
- Caching strategies

## 📊 **Analytics Capabilities**

### **Portfolio Analytics**
- Financial performance
- Risk assessment
- Diversification analysis
- Tax optimization

### **Race Analytics**
- Competition performance
- Player behavior analysis
- Prize efficiency metrics
- Engagement tracking

### **Cross-Platform Analytics**
- Player journey mapping
- Revenue attribution
- Community impact analysis
- Strategic insights

## 🔧 **Technical Stack**

### **Backend**
- Python 3.6+
- SQLite database
- HTTP server
- API clients

### **Frontend**
- HTML5/CSS3
- JavaScript ES6+
- Chart.js
- Responsive design

### **APIs**
- Gamba GraphQL API
- CoinGecko REST API
- Custom analytics endpoints

### **Data Formats**
- JSON for data exchange
- SQLite for caching
- Markdown for reports
- CSV for exports
