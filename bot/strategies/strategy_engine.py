"""
Strategy Engine
Generate trading signals based on indicators
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class StrategyEngine:
    """Trading strategy engine"""
    
    def __init__(self, strategies: List[Dict]):
        self.strategies = strategies
        self.active_strategies = []
        
        for strategy_config in strategies:
            strategy = self._load_strategy(strategy_config)
            if strategy:
                self.active_strategies.append(strategy)
        
        logger.info(f"✅ Loaded {len(self.active_strategies)} strategies")
    
    def _load_strategy(self, config: Dict) -> Optional['BaseStrategy']:
        """Load a strategy from config"""
        strategy_type = config.get("type", "momentum")
        
        if strategy_type == "momentum":
            return MomentumStrategy(config)
        elif strategy_type == "mean_reversion":
            return MeanReversionStrategy(config)
        elif strategy_type == "breakout":
            return BreakoutStrategy(config)
        else:
            logger.warning(f"⚠️ Unknown strategy type: {strategy_type}")
            return None
    
    def generate_signal(
        self,
        symbol: str,
        price: float,
        indicators: Dict,
        ml_prediction: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Generate trading signal from all strategies"""
        
        signals = []
        
        for strategy in self.active_strategies:
            signal = strategy.generate_signal(symbol, price, indicators)
            if signal:
                signals.append(signal)
        
        # Combine signals
        if not signals:
            return None
        
        # Simple majority vote
        buy_count = sum(1 for s in signals if s["side"] == "BUY")
        sell_count = sum(1 for s in signals if s["side"] == "SELL")
        
        # Incorporate ML prediction if available
        if ml_prediction:
            ml_confidence = ml_prediction.get("confidence", 0)
            if ml_prediction["type"] == "BUY":
                buy_count += ml_confidence
            elif ml_prediction["type"] == "SELL":
                sell_count += ml_confidence
        
        if buy_count > sell_count and buy_count >= len(signals) / 2:
            return {
                "symbol": symbol,
                "side": "BUY",
                "price": price,
                "confidence": buy_count / len(signals),
                "strategy": "combined",
                "indicators": indicators
            }
        elif sell_count > buy_count and sell_count >= len(signals) / 2:
            return {
                "symbol": symbol,
                "side": "SELL",
                "price": price,
                "confidence": sell_count / len(signals),
                "strategy": "combined",
                "indicators": indicators
            }
        
        return None


class BaseStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.name = config.get("name", "unnamed")
    
    def generate_signal(
        self,
        symbol: str,
        price: float,
        indicators: Dict
    ) -> Optional[Dict]:
        raise NotImplementedError


class MomentumStrategy(BaseStrategy):
    """RSI + MACD momentum strategy"""
    
    def generate_signal(
        self,
        symbol: str,
        price: float,
        indicators: Dict
    ) -> Optional[Dict]:
        rsi = indicators.get("rsi", 50)
        macd = indicators.get("macd", {})
        macd_hist = macd.get("histogram", 0)
        
        # Buy signal: RSI oversold + MACD turning positive
        if rsi < 30 and macd_hist > 0:
            return {
                "symbol": symbol,
                "side": "BUY",
                "price": price,
                "confidence": 0.7,
                "strategy": "momentum"
            }
        
        # Sell signal: RSI overbought + MACD turning negative
        if rsi > 70 and macd_hist < 0:
            return {
                "symbol": symbol,
                "side": "SELL",
                "price": price,
                "confidence": 0.7,
                "strategy": "momentum"
            }
        
        return None


class MeanReversionStrategy(BaseStrategy):
    """Bollinger Bands mean reversion strategy"""
    
    def generate_signal(
        self,
        symbol: str,
        price: float,
        indicators: Dict
    ) -> Optional[Dict]:
        bbands = indicators.get("bbands", {})
        if not bbands:
            return None
        
        upper = bbands.get("upper", price * 1.1)
        lower = bbands.get("lower", price * 0.9)
        
        # Buy at lower band
        if price <= lower * 1.01:  # Within 1% of lower band
            return {
                "symbol": symbol,
                "side": "BUY",
                "price": price,
                "confidence": 0.6,
                "strategy": "mean_reversion"
            }
        
        # Sell at upper band
        if price >= upper * 0.99:  # Within 1% of upper band
            return {
                "symbol": symbol,
                "side": "SELL",
                "price": price,
                "confidence": 0.6,
                "strategy": "mean_reversion"
            }
        
        return None


class BreakoutStrategy(BaseStrategy):
    """Price breakout strategy"""
    
    def generate_signal(
        self,
        symbol: str,
        price: float,
        indicators: Dict
    ) -> Optional[Dict]:
        # Simplified breakout detection
        momentum = indicators.get("momentum", 0)
        volume = indicators.get("volume", {})
        volume_trend = volume.get("trend", "neutral")
        
        # Strong momentum + increasing volume
        if momentum > 50 and volume_trend == "increasing":
            return {
                "symbol": symbol,
                "side": "BUY",
                "price": price,
                "confidence": 0.65,
                "strategy": "breakout"
            }
        
        if momentum < -50 and volume_trend == "increasing":
            return {
                "symbol": symbol,
                "side": "SELL",
                "price": price,
                "confidence": 0.65,
                "strategy": "breakout"
            }
        
        return None
