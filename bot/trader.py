"""
Crypto Trading Bot - Main Trading Engine
Enterprise-grade trading bot with ML and risk management
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel

from bot.exchanges.binance_client import BinanceClient
from bot.strategies.strategy_engine import StrategyEngine
from bot.risk_management.risk_manager import RiskManager
from bot.ml.predictor import MLPredictor
from bot.utils.logger import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


class Trade(BaseModel):
    """Trade model"""
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    price: float
    timestamp: datetime
    strategy: str
    confidence: Optional[float] = None


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, config_path: str, mode: str = "paper"):
        self.config = self._load_config(config_path)
        self.mode = mode
        self.running = False
        
        # Initialize components
        self.exchange = BinanceClient(
            testnet=(mode == "paper"),
            api_key=self.config.get("api_key"),
            api_secret=self.config.get("api_secret")
        )
        
        self.strategy_engine = StrategyEngine(self.config.get("strategies", []))
        self.risk_manager = RiskManager(self.config.get("risk", {}))
        self.ml_predictor = MLPredictor(self.config.get("ml", {}))
        
        # Trading state
        self.active_trades: List[Trade] = []
        self.portfolio_value = 0.0
        self.daily_pnl = 0.0
        
        logger.info(f"🚀 Trading Bot initialized in {mode.upper()} mode")
    
    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    async def start(self):
        """Start the trading bot"""
        self.running = True
        logger.info("▶️ Starting trading bot...")
        
        # Connect to exchange
        await self.exchange.connect()
        
        # Start WebSocket feeds
        symbols = self.config.get("symbols", ["BTCUSDT", "ETHUSDT"])
        for symbol in symbols:
            asyncio.create_task(self._process_symbol(symbol))
        
        # Start monitoring
        asyncio.create_task(self._monitor_portfolio())
        
        logger.info(f"✅ Bot started. Monitoring {len(symbols)} symbols")
    
    async def _process_symbol(self, symbol: str):
        """Process trading logic for a symbol"""
        while self.running:
            try:
                # Get latest price data
                ticker = await self.exchange.get_ticker(symbol)
                
                # Get technical indicators
                indicators = await self._calculate_indicators(symbol)
                
                # ML prediction
                ml_signal = await self.ml_predictor.predict(symbol, indicators)
                
                # Generate trading signal
                signal = self.strategy_engine.generate_signal(
                    symbol=symbol,
                    price=ticker["price"],
                    indicators=indicators,
                    ml_prediction=ml_signal
                )
                
                if signal:
                    # Risk check
                    if self.risk_manager.can_trade(signal, self.active_trades):
                        await self._execute_trade(signal)
                    else:
                        logger.warning(f"⚠️ Risk check failed for {symbol}")
                
                await asyncio.sleep(self.config.get("check_interval", 60))
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
                await asyncio.sleep(5)
    
    async def _calculate_indicators(self, symbol: str) -> Dict:
        """Calculate technical indicators"""
        # Get historical data
        klines = await self.exchange.get_klines(symbol, interval="1h", limit=100)
        
        # Calculate indicators
        from bot.utils.indicators import calculate_all
        return calculate_all(klines)
    
    async def _execute_trade(self, signal: Dict):
        """Execute a trade"""
        try:
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(signal)
            
            # Place order
            if self.mode == "live":
                order = await self.exchange.place_order(
                    symbol=signal["symbol"],
                    side=signal["side"],
                    quantity=position_size,
                    order_type="MARKET"
                )
                logger.info(f"✅ LIVE ORDER: {signal['side']} {position_size} {signal['symbol']}")
            else:
                # Paper trading - simulate order
                order = {
                    "symbol": signal["symbol"],
                    "side": signal["side"],
                    "quantity": position_size,
                    "price": signal["price"],
                    "status": "FILLED"
                }
                logger.info(f"📊 PAPER TRADE: {signal['side']} {position_size} {signal['symbol']} @ {signal['price']}")
            
            # Record trade
            trade = Trade(
                symbol=signal["symbol"],
                side=signal["side"],
                quantity=position_size,
                price=signal["price"],
                timestamp=datetime.now(),
                strategy=signal["strategy"],
                confidence=signal.get("confidence")
            )
            self.active_trades.append(trade)
            
            # Save to database
            await self._save_trade(trade)
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
    
    async def _monitor_portfolio(self):
        """Monitor portfolio value and performance"""
        while self.running:
            try:
                # Calculate portfolio value
                balances = await self.exchange.get_balances()
                self.portfolio_value = sum(
                    b["value_usdt"] for b in balances.values()
                )
                
                logger.info(f"💰 Portfolio Value: ${self.portfolio_value:,.2f}")
                logger.info(f"📈 Daily P&L: ${self.daily_pnl:,.2f}")
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Portfolio monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _save_trade(self, trade: Trade):
        """Save trade to database"""
        # Implementation for database save
        pass
    
    async def stop(self):
        """Stop the trading bot"""
        self.running = False
        await self.exchange.disconnect()
        logger.info("🛑 Trading bot stopped")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Crypto Trading Bot")
    parser.add_argument("--config", required=True, help="Path to config file")
    parser.add_argument("--mode", choices=["paper", "live"], default="paper")
    args = parser.parse_args()
    
    bot = TradingBot(args.config, args.mode)
    
    try:
        await bot.start()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️ Keyboard interrupt received")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
