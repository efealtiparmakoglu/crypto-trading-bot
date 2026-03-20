# Crypto Trading Bot with ML 🚀💰

**Enterprise-grade cryptocurrency trading bot** with machine learning predictions, risk management, and real-time WebSocket feeds.

## 🌟 Features

### Trading Engine
- ✅ **Multi-Exchange Support** - Binance, Coinbase Pro, Kraken
- ✅ **Real-time WebSocket** - Live price feeds and order execution
- ✅ **Paper Trading** - Test strategies without real money
- ✅ **Live Trading** - Production-ready with API keys
- ✅ **Arbitrage Detection** - Cross-exchange price differences

### Machine Learning
- ✅ **Price Prediction** - LSTM neural networks for price forecasting
- ✅ **Sentiment Analysis** - Twitter/Reddit crypto sentiment
- ✅ **Pattern Recognition** - Technical indicator pattern detection
- ✅ **Reinforcement Learning** - Self-improving trading strategies

### Risk Management
- ✅ **Position Sizing** - Kelly Criterion and risk-based sizing
- ✅ **Stop Loss/Take Profit** - Automated risk controls
- ✅ **Portfolio Rebalancing** - Auto-adjust based on market conditions
- ✅ **Drawdown Protection** - Circuit breakers for large losses

### Technical Analysis
- ✅ **50+ Indicators** - RSI, MACD, Bollinger Bands, Ichimoku, etc.
- ✅ **Custom Strategies** - Strategy builder with Python
- ✅ **Backtesting Engine** - Historical data simulation
- ✅ **Walk-forward Analysis** - Strategy validation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADING BOT CORE                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Binance    │  │   Coinbase   │  │    Kraken    │     │
│  │   WebSocket  │  │   WebSocket  │  │   WebSocket  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         └─────────────────┼──────────────────┘              │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │           DATA NORMALIZATION LAYER                  │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │         TECHNICAL ANALYSIS ENGINE                   │   │
│  │  RSI | MACD | BB | EMA | VWAP | Fibonacci | etc   │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │         ML PREDICTION ENGINE                        │   │
│  │  LSTM | Sentiment | Pattern | Reinforcement       │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │         STRATEGY EXECUTION                          │   │
│  │  Signal Generation → Risk Check → Order Execution │   │
│  └────────────────────────┬───────────────────────────┘   │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │         RISK MANAGEMENT                             │   │
│  │  Position Size | Stop Loss | Take Profit | Max DD │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    WEB DASHBOARD                            │
│  React Frontend + FastAPI Backend + PostgreSQL + Redis     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/efealtiparmakoglu/crypto-trading-bot.git
cd crypto-trading-bot

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Access dashboard
open http://localhost:3000
```

### Local Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-ml.txt

# Database setup
python scripts/init_db.py

# Run backtest
python -m bot.backtest --strategy momentum --symbol BTCUSDT

# Start paper trading
python -m bot.trader --mode paper --config config/paper_trading.yml

# Start live trading (⚠️ Real money!)
python -m bot.trader --mode live --config config/live_trading.yml
```

## 📊 Configuration

### Strategy Configuration
```yaml
# config/strategies/momentum.yml
name: Momentum Strategy
description: RSI + MACD momentum strategy

indicators:
  rsi:
    period: 14
    overbought: 70
    oversold: 30
  
  macd:
    fast: 12
    slow: 26
    signal: 9

signals:
  buy:
    - rsi < 30
    - macd_histogram > 0
  
  sell:
    - rsi > 70
    - macd_histogram < 0

risk_management:
  position_size: 0.1  # 10% of portfolio
  stop_loss: 0.02     # 2% stop loss
  take_profit: 0.06   # 6% take profit
```

## 🤖 ML Models

### Train Price Prediction Model
```bash
# Download historical data
python scripts/download_data.py --symbol BTCUSDT --days 365

# Train LSTM model
python -m bot.ml.train --model lstm --data data/btc_365d.csv --epochs 100

# Evaluate model
python -m bot.ml.evaluate --model models/lstm_btc.h5
```

### Sentiment Analysis
```bash
# Collect social media data
python -m bot.sentiment.collect --sources twitter,reddit --keywords bitcoin,crypto

# Train sentiment model
python -m bot.ml.train_sentiment --data data/sentiment.csv
```

## 💻 Web Dashboard

### Features
- 📈 Real-time portfolio value
- 📊 Trading history and P&L
- 🤖 Active strategies and signals
- 📉 Price charts with indicators
- ⚙️ Strategy configuration
- 📱 Mobile responsive

### API Endpoints
```python
# Get portfolio
GET /api/v1/portfolio

# Get active trades
GET /api/v1/trades/active

# Get trading history
GET /api/v1/trades/history

# Start strategy
POST /api/v1/strategies/start
{
    "strategy": "momentum",
    "symbol": "BTCUSDT",
    "timeframe": "1h"
}
```

## 🧪 Backtesting

```bash
# Run backtest with default config
python -m bot.backtest --strategy momentum --symbol BTCUSDT --days 90

# Custom parameters
python -m bot.backtest \
    --strategy mean_reversion \
    --symbol ETHUSDT \
    --start 2024-01-01 \
    --end 2024-03-01 \
    --initial 10000 \
    --fee 0.001

# Generate report
python -m bot.backtest --report --output reports/backtest_result.html
```

## 🛡️ Risk Management

### Position Sizing
- **Fixed** - Fixed amount per trade
- **Percent** - Percentage of portfolio
- **Kelly** - Kelly Criterion optimal sizing
- **Risk-based** - Based on volatility

### Risk Controls
- Maximum daily loss limit
- Maximum open positions
- Correlation limits
- Drawdown circuit breakers

## 📈 Performance Metrics

- **Sharpe Ratio** - Risk-adjusted returns
- **Sortino Ratio** - Downside risk
- **Maximum Drawdown** - Peak to trough decline
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Gross profit / gross loss
- **Calmar Ratio** - Return / max drawdown

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_risk_management.py -v

# Coverage report
pytest --cov=bot --cov-report=html
```

## 📝 Environment Variables

```bash
# Exchange API Keys (Paper Trading)
BINANCE_TESTNET_KEY=your_key
BINANCE_TESTNET_SECRET=your_secret

# Exchange API Keys (Live Trading - ⚠️ CAUTION)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# Database
DATABASE_URL=postgresql://user:pass@localhost/trading_bot
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# Trading
DEFAULT_TRADE_SIZE=0.01
MAX_POSITIONS=10
RISK_PER_TRADE=0.02
```

## ⚠️ Disclaimer

**WARNING**: Cryptocurrency trading involves substantial risk. This bot is for educational purposes. Always:
- Start with paper trading
- Never risk more than you can afford to lose
- Monitor the bot closely
- Use stop losses
- Test strategies thoroughly

## 👥 Authors

- **Efe Altıparmakoğlu** - [@efealtiparmakoglu](https://github.com/efealtiparmakoglu)

## 📄 License

MIT License - see [LICENSE](LICENSE) file
