# Arbitrage Bot

A beginner-friendly cryptocurrency arbitrage detection and paper trading bot built with Python + Flask.

## Features

✨ **Price Monitoring** - Real-time price comparison across Binance and Kraken
📊 **Opportunity Detection** - Automatically detect profitable arbitrage opportunities
📈 **Paper Trading** - Simulate trades with a virtual $1000 wallet
💻 **Web Dashboard** - Beautiful UI to track opportunities and trades
🔄 **Auto-Refresh** - Live updates every 30 seconds

## Requirements

- Python 3.9+
- pip

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python run.py
   ```

4. Open http://127.0.0.1:5000 in your browser

## Project Structure

```
arbitrage-bot/
├── app/
│   ├── models/          # Database models (Wallet, Trade, Opportunity)
│   ├── exchanges/       # Exchange connectors (Binance, Kraken)
│   ├── strategies/      # Arbitrage detection & trading engine
│   └── routes/          # API endpoints & web routes
├── templates/           # HTML templates
├── static/
│   ├── css/            # Stylesheets
│   └── js/             # Frontend JavaScript
├── config.py           # Configuration
├── run.py              # Entry point
└── requirements.txt    # Dependencies
```

## How It Works

1. **Price Fetching** - Connects to Binance and Kraken APIs using CCXT
2. **Arbitrage Detection** - Compares prices across exchanges
3. **Profitability Calculation** - Accounts for exchange fees
4. **Paper Trading** - Simulates buy/sell trades on opportunities
5. **Tracking** - Stores all trades and opportunities in SQLite

## Configuration

Edit `config.py` to customize:
- Initial wallet balance ($1000)
- Minimum profit threshold (2%)
- Exchange fees (0.1%)
- Trading pairs

## API Endpoints

- `GET /api/opportunities` - Get opportunities
- `POST /api/opportunities/scan` - Scan for new opportunities
- `GET /api/trades` - Get trade history
- `POST /api/trades/execute` - Execute a simulated trade
- `GET /api/wallet` - Get wallet info
- `POST /api/wallet/reset` - Reset wallet

## Notes

- This is a **paper trading** bot (simulated trades only)
- No real money is involved
- Great for learning arbitrage concepts
- Extensible to support more exchanges
"# Arbitrage_Bot" 
