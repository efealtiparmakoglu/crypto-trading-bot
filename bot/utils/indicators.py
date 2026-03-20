"""
Technical Indicators Module
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def calculate_all(klines: List[Dict]) -> Dict:
    """Calculate all technical indicators"""
    df = pd.DataFrame(klines)
    
    indicators = {
        "rsi": calculate_rsi(df["close"]),
        "macd": calculate_macd(df["close"]),
        "bbands": calculate_bollinger_bands(df["close"]),
        "ema": calculate_ema(df["close"]),
        "sma": calculate_sma(df["close"]),
        "volume": calculate_volume_metrics(df["volume"]),
        "atr": calculate_atr(df),
        "vwap": calculate_vwap(df),
        "momentum": calculate_momentum(df["close"]),
        "stochastic": calculate_stochastic(df),
    }
    
    return indicators


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> Dict:
    """Calculate MACD"""
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return {
        "macd": macd.iloc[-1],
        "signal": signal_line.iloc[-1],
        "histogram": histogram.iloc[-1]
    }


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: float = 2.0
) -> Dict:
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return {
        "upper": upper.iloc[-1],
        "middle": sma.iloc[-1],
        "lower": lower.iloc[-1],
        "bandwidth": (upper.iloc[-1] - lower.iloc[-1]) / sma.iloc[-1]
    }


def calculate_ema(prices: pd.Series, period: int = 20) -> float:
    """Calculate Exponential Moving Average"""
    return prices.ewm(span=period, adjust=False).mean().iloc[-1]


def calculate_sma(prices: pd.Series, period: int = 20) -> float:
    """Calculate Simple Moving Average"""
    return prices.rolling(window=period).mean().iloc[-1]


def calculate_volume_metrics(volumes: pd.Series) -> Dict:
    """Calculate volume metrics"""
    return {
        "current": volumes.iloc[-1],
        "sma_20": volumes.rolling(window=20).mean().iloc[-1],
        "trend": "increasing" if volumes.iloc[-1] > volumes.iloc[-5] else "decreasing"
    }


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """Calculate Average True Range"""
    high = df["high"]
    low = df["low"]
    close = df["close"]
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr.iloc[-1]


def calculate_vwap(df: pd.DataFrame) -> float:
    """Calculate Volume Weighted Average Price"""
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap.iloc[-1]


def calculate_momentum(prices: pd.Series, period: int = 10) -> float:
    """Calculate Price Momentum"""
    return prices.iloc[-1] - prices.iloc[-period]


def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
    """Calculate Stochastic Oscillator"""
    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()
    
    k = 100 * ((df["close"] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    
    return {
        "k": k.iloc[-1],
        "d": d.iloc[-1]
    }
