"""
Risk Management Module
Position sizing, stop losses, and portfolio protection
"""

import logging
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk management for trading bot"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Risk parameters
        self.max_position_size = config.get("max_position_size", 0.1)  # 10% of portfolio
        self.max_positions = config.get("max_positions", 10)
        self.max_daily_loss = config.get("max_daily_loss", 0.05)  # 5% daily loss limit
        self.stop_loss_pct = config.get("stop_loss", 0.02)  # 2% stop loss
        self.take_profit_pct = config.get("take_profit", 0.06)  # 6% take profit
        self.max_drawdown = config.get("max_drawdown", 0.15)  # 15% max drawdown
        
        # State
        self.daily_pnl = 0.0
        self.peak_value = 0.0
        self.current_drawdown = 0.0
        self.circuit_breaker_triggered = False
        
        logger.info("🛡️ Risk Manager initialized")
    
    def can_trade(self, signal: Dict, active_trades: List) -> bool:
        """Check if trade can be executed based on risk rules"""
        
        # Circuit breaker check
        if self.circuit_breaker_triggered:
            logger.warning("🚫 Circuit breaker active - no trading allowed")
            return False
        
        # Max positions check
        if len(active_trades) >= self.max_positions:
            logger.warning(f"🚫 Max positions reached ({self.max_positions})")
            return False
        
        # Daily loss limit check
        if self.daily_pnl < -self.max_daily_loss:
            logger.warning(f"🚫 Daily loss limit reached: {self.daily_pnl:.2%}")
            return False
        
        # Drawdown check
        if self.current_drawdown > self.max_drawdown:
            logger.warning(f"🚫 Max drawdown reached: {self.current_drawdown:.2%}")
            self.circuit_breaker_triggered = True
            return False
        
        # Position already open check
        symbol = signal.get("symbol")
        open_symbols = [t.symbol for t in active_trades]
        if symbol in open_symbols:
            logger.warning(f"🚫 Position already open for {symbol}")
            return False
        
        return True
    
    def calculate_position_size(self, signal: Dict) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        portfolio_value = signal.get("portfolio_value", 10000)
        
        # Get win rate and avg win/loss from strategy backtest
        win_rate = signal.get("win_rate", 0.55)
        avg_win = signal.get("avg_win", 0.06)
        avg_loss = signal.get("avg_loss", 0.02)
        
        # Kelly Criterion: f* = (p*b - q) / b
        # where p = win rate, q = loss rate, b = avg win / avg loss
        if avg_loss == 0:
            avg_loss = 0.01
        
        b = avg_win / avg_loss
        q = 1 - win_rate
        
        kelly_pct = (win_rate * b - q) / b
        
        # Use half Kelly for safety
        half_kelly = kelly_pct / 2
        
        # Cap at max position size
        position_pct = min(half_kelly, self.max_position_size)
        
        # Calculate quantity
        position_value = portfolio_value * position_pct
        price = signal.get("price", 1)
        quantity = position_value / price
        
        logger.info(f"📊 Position size: {position_pct:.2%} (${position_value:,.2f})")
        
        return quantity
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """Calculate stop loss price"""
        if side == "BUY":
            return entry_price * (1 - self.stop_loss_pct)
        else:
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """Calculate take profit price"""
        if side == "BUY":
            return entry_price * (1 + self.take_profit_pct)
        else:
            return entry_price * (1 - self.take_profit_pct)
    
    def update_portfolio_value(self, value: float):
        """Update portfolio value and calculate drawdown"""
        if value > self.peak_value:
            self.peak_value = value
        
        if self.peak_value > 0:
            self.current_drawdown = (self.peak_value - value) / self.peak_value
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker (call manually after review)"""
        self.circuit_breaker_triggered = False
        logger.info("✅ Circuit breaker reset")


class Position:
    """Represents an open trading position"""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ):
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
    
    def update_pnl(self, current_price: float):
        """Update unrealized P&L"""
        if self.side == "BUY":
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
    
    def check_exit(self, current_price: float) -> Optional[str]:
        """Check if position should be closed"""
        if self.side == "BUY":
            if current_price <= self.stop_loss:
                return "STOP_LOSS"
            if current_price >= self.take_profit:
                return "TAKE_PROFIT"
        else:
            if current_price >= self.stop_loss:
                return "STOP_LOSS"
            if current_price <= self.take_profit:
                return "TAKE_PROFIT"
        
        return None
