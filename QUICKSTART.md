# 🚀 Arbitrage Bot - Quick Start Guide

## ✅ What's Been Built

Your cryptocurrency arbitrage bot is **READY TO USE**! Here's what you have:

### Features Implemented ✨
- ✅ **Multi-Exchange Support** - Binance and Kraken connectors
- ✅ **Price Monitoring** - Real-time price fetching using CCXT
- ✅ **Arbitrage Detection** - Automatically finds profitable opportunities
- ✅ **Paper Trading** - Simulates trades with virtual wallet ($1000 starting balance)
- ✅ **Web Dashboard** - Beautiful UI to view opportunities and trades
- ✅ **REST API** - Full API for integration and automation
- ✅ **SQLite Database** - Persistent storage for wallets, trades, and opportunities

### Project Structure
```
arbitrage-bot/
├── app/
│   ├── models/          # Database models (Wallet, Trade, Opportunity, PriceSnapshot)
│   ├── exchanges/       # Exchange connectors (Binance, Kraken)
│   ├── strategies/      # Arbitrage detection & trading engine
│   └── routes/          # API endpoints & web routes
├── templates/           # HTML dashboard pages
├── static/
│   ├── css/            # Styling
│   └── js/             # Frontend logic
├── config.py           # Configuration
├── run.py              # Entry point
└── requirements.txt    # Dependencies
```

## 🎯 How to Use

### 1. Access the Dashboard
Open your browser and go to:
```
http://127.0.0.1:5000
```

**Dashboard Features:**
- Real-time wallet balance
- Profit/Loss tracking
- Active opportunities
- Recent trades
- Quick "Scan Now" button

### 2. Scan for Opportunities
Click the **"Scan Now"** button to detect arbitrage opportunities between exchanges.

The bot will:
- Fetch prices from Binance and Kraken
- Compare prices across exchanges
- Calculate profitability after fees
- Display opportunities > 2% profit

### 3. Execute Trades
Click **"Execute"** on any opportunity to simulate a trade:
- Buy from the cheaper exchange
- Sell to the more expensive exchange
- Track profit/loss

### 4. Monitor Results
- **Opportunities Page** - See all detected opportunities
- **Trades Page** - Trading history with P&L
- **Wallet Page** - Portfolio value and statistics

## 📊 API Endpoints

### Status & Configuration
```
GET /api/status
```
Returns bot status, version, and trading pairs

### Opportunities
```
GET /api/opportunities?limit=50&active_only=true
POST /api/opportunities/scan
```
Get opportunities or manually scan

### Trades
```
GET /api/trades?limit=50
POST /api/trades/execute
```
Get trade history or execute a simulated trade

### Wallet
```
GET /api/wallet
POST /api/wallet/reset
```
Get wallet info or reset to initial state

### Statistics
```
GET /api/stats
```
Overall bot statistics

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Initial wallet balance (default: $1000)
INITIAL_WALLET_BALANCE = 1000

# Minimum profit threshold (default: 2%)
MIN_PROFIT_PERCENTAGE = 2.0

# Exchange fee per transaction (default: 0.1%)
TRANSACTION_FEE = 0.001

# Trading pairs to monitor
TRADING_PAIRS = ['BTC/USD', 'ETH/USD', 'LTC/USD']

# Exchanges to monitor
EXCHANGES = ['binance', 'kraken']
```

## 🔑 Key Concepts

### Arbitrage Opportunity
A profitable price difference between two exchanges.
- **Example**: BTC costs $45,000 on Binance, $45,100 on Kraken
- **Opportunity**: Buy on Binance, sell on Kraken for profit
- **P&L**: After 0.1% fee each way ≈ 0.8% profit

### Paper Trading
Simulated trades with virtual money to learn and test strategies.
- No real money involved
- Perfect for understanding arbitrage mechanics
- Can reset wallet anytime

### Profit Calculation
```
Profit % = (Sell Price - Buy Price) / Buy Price - (Fees × 2)
Example: (45100 - 45000) / 45000 - 0.002 = 0.002 - 0.002 = 0% (break even after fees)
```

## 🎓 Next Steps

### 1. **Learn the Mechanics**
- Scan for opportunities multiple times
- Execute a few trades
- Watch profit/loss accumulate

### 2. **Customize Configuration**
- Add more trading pairs
- Adjust minimum profit threshold
- Change exchange fees based on your account tier

### 3. **Add More Exchanges** (Advanced)
Create new exchange connectors in `app/exchanges/`:
```python
from app.exchanges.base_connector import ExchangeConnector

class NewExchangeConnector(ExchangeConnector):
    def __init__(self):
        super().__init__('exchangename')
        self.supported_pairs = ['BTC/USD', 'ETH/USD', ...]
```

### 4. **Automate Scanning**
Modify `app/routes/api.py` to add background scanning:
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(scan_opportunities, 'interval', minutes=5)
scheduler.start()
```

## 🐛 Troubleshooting

### Bot Won't Start
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (3.9+)
python --version
```

### API Connection Issues
```bash
# Check if server is running
curl http://127.0.0.1:5000/api/status

# Check firewall port 5000
netstat -ano | findstr :5000
```

### No Opportunities Detected
- Market conditions may not have arbitrage opportunities
- Check if exchanges are responding: `GET /api/status`
- Adjust minimum profit threshold in config.py
- Try with different trading pairs

## 📝 Notes

- **Paper Trading**: This bot simulates trades. Real money is never involved.
- **Exchange Fees**: Default 0.1% per transaction (typical for most exchanges)
- **Rate Limiting**: CCXT handles rate limiting automatically
- **No Account Required**: Uses public APIs (no API keys needed)
- **Educational Purpose**: Great for learning arbitrage concepts!

## 🚀 Performance Tips

1. **Increase Scan Frequency** - More opportunities detected
2. **Optimize Thresholds** - Balance between volume and profitability  
3. **Add More Pairs** - More trading pairs = more opportunities
4. **Monitor Fees** - Different exchanges have different fee structures

## 📚 Additional Resources

- [CCXT Documentation](https://docs.ccxt.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Arbitrage Trading Basics](https://en.wikipedia.org/wiki/Arbitrage)
- [Cryptocurrency Exchanges](https://www.coinbase.com/learn)

---

**Happy Trading! 🎉**

Questions? Review the code comments or check the API documentation at `/docs`
