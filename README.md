# 🐋 Polymarket Whale Tracker

> **Track the smart money.** Real-time monitoring of large trades (≥$10,000) on Polymarket prediction markets.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🔥 Features

### **🐋 Whale Activity Monitoring**
- Real-time alerts for trades ≥ $10,000
- Track top whale traders
- Buy/Sell sentiment analysis
- Desktop notifications

### **📊 Market Intelligence**
- Opportunity scoring algorithm
- Liquidity & volume analysis
- Category performance tracking
- Market trend identification

### **📈 Actionable Analytics**
- Auto-generated trading signals
- Market sentiment indicators
- Confidence levels
- Top performer leaderboards

### **🎨 Modern Dark UI**
- Glassmorphism design
- Red/Black theme
- Smooth animations
- Fully responsive

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Sigmabrogz/cooming-soon.git
cd cooming-soon

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

Visit **http://localhost:8080** in your browser! 🎉

## 📸 Screenshots

### Dashboard
- Overview of market activity
- Top markets by volume
- Recent whale trades

### Whale Activity
- Live whale alerts
- Top trader leaderboards
- Market sentiment analysis

### Markets
- Opportunity scores
- Best trading opportunities
- Category filtering

### Analytics
- Trading signals
- Market insights
- Performance metrics

## 🎯 Use Cases

### **Follow the Smart Money**
Track large trades to identify where experienced traders are betting.

### **Find Opportunities**
Discover high-volume, high-liquidity markets for smooth trading.

### **Market Sentiment**
Understand bullish/bearish trends before the crowd.

### **Risk Management**
Monitor whale activity to spot potential market moves.

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: Polymarket Data API
- **Real-time**: Background threading
- **Design**: Glassmorphism, Dark theme

## 📁 Project Structure

```
polybotw/
├── app.py                  # Flask application
├── whale_tracker.py        # Whale monitoring logic
├── polymarket/             # Polymarket SDK
│   ├── __init__.py
│   ├── auth.py
│   ├── clob.py
│   ├── data_api.py
│   ├── gamma.py
│   ├── websocket.py
│   └── models.py
├── templates/              # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── whales.html
│   ├── markets.html
│   └── analytics.html
├── requirements.txt        # Python dependencies
└── README.md
```

## 🔧 Configuration

The app works out-of-the-box with public Polymarket data. No API keys required for read-only features!

For advanced features (placing orders), create a `.env` file:

```bash
POLYMARKET_PRIVATE_KEY=your_private_key_here
POLYMARKET_API_KEY=your_api_key_here
```

## 📊 How It Works

### **Whale Detection**
1. Monitors Polymarket's `/trades` endpoint
2. Filters trades ≥ $10,000
3. Tracks trader information
4. Generates real-time alerts

### **Opportunity Scoring**
```
Opportunity Score = (Volume Score + Liquidity Score)
- High volume = More active trading
- High liquidity = Easier entry/exit
- Higher score = Better opportunity
```

### **Trading Signals**
- **Bullish**: >60% buying activity
- **Bearish**: <40% buying activity
- **High Confidence**: Large volume imbalance

## 🎨 Design Philosophy

**Dark & Minimal**: Easy on the eyes, focuses on data.

**Glassmorphism**: Modern blur effects with transparency.

**Actionable**: Every metric answers "What should I do?"

**Gen Z Aesthetic**: Bold colors, smooth animations, clean layout.

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - feel free to use this project however you like!

## ⚠️ Disclaimer

This tool is for informational purposes only. Not financial advice. Trade responsibly!

## 🔗 Links

- [Polymarket](https://polymarket.com/)
- [Polymarket API Docs](https://docs.polymarket.com/)

---

**Built with 🔥 by Sigmabrogz**

*Track whales. Find opportunities. Trade smarter.* 🐋