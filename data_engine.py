import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
from config import Config
import pytz
from datetime import datetime, timedelta

class DataEngine:
    def __init__(self):
        self.config = Config()
        self.scaler = None
        
    def fetch_real_time_data(self):
        """Fetch real-time data"""
        now = datetime.now(pytz.utc)
        return pd.DataFrame({
            'timestamp': [now],
            'open': [1.0850],
            'high': [1.0855],
            'low': [1.0845],
            'close': [1.0852],
            'volume': [10000]
        })
    
    def fetch_historical_data(self, days=30):
        """Generate synthetic historical data"""
        end_date = datetime.now(pytz.utc)
        start_date = end_date - timedelta(days=days)
        date_rng = pd.date_range(start=start_date, end=end_date, freq='5min')
        
        # Create realistic price movement
        price = 100 + np.cumsum(np.random.randn(len(date_rng)) * 0.1
        return pd.DataFrame({
            'timestamp': date_rng,
            'open': price,
            'high': price + np.abs(np.random.randn(len(date_rng))) * 0.2,
            'low': price - np.abs(np.random.randn(len(date_rng))) * 0.2,
            'close': price + np.random.randn(len(date_rng)) * 0.1,
            'volume': (np.random.rand(len(date_rng)) * 10000).astype(int)
        })
    
    def calculate_indicators(self, df):
        """Calculate Rian's indicators"""
        # Fast EMA (5-period)
        df['ema5'] = df['close'].ewm(span=self.config.INDICATORS['ema_fast']['period'], adjust=False).mean()
        
        # Slow EMA (20-period)
        df['ema20'] = df['close'].ewm(span=self.config.INDICATORS['ema_slow']['period'], adjust=False).mean()
        
        # RSI (6-period)
        delta = df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.config.INDICATORS['rsi']['period']).mean()
        avg_loss = loss.rolling(self.config.INDICATORS['rsi']['period']).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (8,18,6)
        fast_ema = df['close'].ewm(span=self.config.INDICATORS['macd']['fast'], adjust=False).mean()
        slow_ema = df['close'].ewm(span=self.config.INDICATORS['macd']['slow'], adjust=False).mean()
        df['macd'] = fast_ema - slow_ema
        df['signal'] = df['macd'].ewm(span=self.config.INDICATORS['macd']['signal'], adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        return df
    
    def prepare_training_data(self, df):
        """Prepare data for model training"""
        # Feature engineering
        df['ema_cross'] = np.where(df['ema5'] > df['ema20'], 1, 0)
        df['macd_cross'] = np.where(df['macd'] > df['signal'], 1, 0)
        df['rsi_signal'] = np.where(df['rsi'] > 70, -1, np.where(df['rsi'] < 30, 1, 0))
        
        # Select features
        features = df[['ema_cross', 'macd_cross', 'rsi_signal', 'histogram']]
        
        # Create target (1 if next candle is green, 0 otherwise)
        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        targets = df['target'].values[:-1]  # Remove last row which has no target
        
        # Scale features
        self.scaler = MinMaxScaler()
        scaled_features = self.scaler.fit_transform(features.iloc[:-1])
        
        # Save scaler
        joblib.dump(self.scaler, self.config.SCALER_PATH)
        
        return scaled_features, targets
    
    def prepare_prediction_data(self, df):
        """Prepare real-time data for prediction"""
        df = self.calculate_indicators(df)
        
        # Feature engineering
        df['ema_cross'] = np.where(df['ema5'] > df['ema20'], 1, 0)
        df['macd_cross'] = np.where(df['macd'] > df['signal'], 1, 0)
        df['rsi_signal'] = np.where(df['rsi'] > 70, -1, np.where(df['rsi'] < 30, 1, 0))
        
        # Load scaler
        if not self.scaler:
            self.scaler = joblib.load(self.config.SCALER_PATH)
        
        # Select and scale features
        features = df[['ema_cross', 'macd_cross', 'rsi_signal', 'histogram']].tail(1)
        return self.scaler.transform(features)
