"""
Web Dashboard API
FastAPI backend for trading bot dashboard
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Crypto Trading Bot API",
    description="API for monitoring and controlling the trading bot",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Portfolio(BaseModel):
    total_value: float
    available_balance: float
    daily_pnl: float
    total_pnl: float
    drawdown: float


class Trade(BaseModel):
    id: str
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    timestamp: datetime


class Strategy(BaseModel):
    name: str
    description: str
    active: bool
    win_rate: float
    profit_factor: float
    total_trades: int


@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Crypto Trading Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/v1/portfolio", response_model=Portfolio)
async def get_portfolio():
    """Get current portfolio status"""
    # This would fetch from database
    return Portfolio(
        total_value=12543.21,
        available_balance=5000.00,
        daily_pnl=234.56,
        total_pnl=1543.21,
        drawdown=0.05
    )


@app.get("/api/v1/trades/active", response_model=List[Trade])
async def get_active_trades():
    """Get currently active trades"""
    # Mock data - would fetch from database
    return [
        Trade(
            id="trade-001",
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.1,
            entry_price=65000.0,
            current_price=67000.0,
            pnl=200.0,
            pnl_percent=3.08,
            timestamp=datetime.now()
        ),
        Trade(
            id="trade-002",
            symbol="ETHUSDT",
            side="BUY",
            quantity=1.5,
            entry_price=3500.0,
            current_price=3450.0,
            pnl=-75.0,
            pnl_percent=-1.43,
            timestamp=datetime.now()
        )
    ]


@app.get("/api/v1/trades/history")
async def get_trade_history(
    limit: int = Query(50, ge=1, le=1000),
    symbol: Optional[str] = None
):
    """Get trade history"""
    # Mock data
    return {
        "total": 150,
        "trades": [
            {
                "id": "trade-000",
                "symbol": "BTCUSDT",
                "side": "SELL",
                "quantity": 0.1,
                "entry_price": 63000.0,
                "exit_price": 65000.0,
                "pnl": 200.0,
                "pnl_percent": 3.17,
                "status": "CLOSED",
                "close_reason": "TAKE_PROFIT",
                "timestamp": datetime.now()
            }
        ]
    }


@app.get("/api/v1/strategies", response_model=List[Strategy])
async def get_strategies():
    """Get all available strategies"""
    return [
        Strategy(
            name="momentum",
            description="RSI + MACD momentum strategy",
            active=True,
            win_rate=0.62,
            profit_factor=1.8,
            total_trades=145
        ),
        Strategy(
            name="mean_reversion",
            description="Bollinger Bands mean reversion",
            active=False,
            win_rate=0.58,
            profit_factor=1.6,
            total_trades=89
        ),
        Strategy(
            name="ml_prediction",
            description="LSTM-based price prediction",
            active=True,
            win_rate=0.55,
            profit_factor=1.5,
            total_trades=67
        )
    ]


@app.post("/api/v1/strategies/{strategy_name}/toggle")
async def toggle_strategy(strategy_name: str):
    """Enable/disable a strategy"""
    # Implementation would toggle strategy in bot
    return {"status": "success", "strategy": strategy_name, "active": True}


@app.get("/api/v1/performance")
async def get_performance():
    """Get trading performance metrics"""
    return {
        "daily": {
            "trades": 12,
            "win_rate": 0.67,
            "pnl": 234.56,
            "pnl_percent": 1.87
        },
        "weekly": {
            "trades": 67,
            "win_rate": 0.61,
            "pnl": 1234.56,
            "pnl_percent": 10.87
        },
        "monthly": {
            "trades": 234,
            "win_rate": 0.58,
            "pnl": 4567.89,
            "pnl_percent": 57.23
        },
        "all_time": {
            "trades": 1450,
            "win_rate": 0.56,
            "pnl": 15432.10,
            "pnl_percent": 154.32,
            "sharpe_ratio": 1.85,
            "max_drawdown": 0.12,
            "profit_factor": 1.72
        }
    }


@app.get("/api/v1/signals")
async def get_latest_signals(limit: int = Query(10, ge=1, le=100)):
    """Get latest trading signals"""
    return {
        "signals": [
            {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "price": 67000.0,
                "confidence": 0.78,
                "strategy": "momentum",
                "timestamp": datetime.now()
            }
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "api": "up",
            "bot": "running",
            "database": "connected"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
