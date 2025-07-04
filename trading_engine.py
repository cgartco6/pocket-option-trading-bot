import time
from datetime import datetime
import os
import signal
import sys
from config import Config
from data_engine import DataEngine
from ai_model import AIModel
from telegram_bot import TelegramBot

class TradingEngine:
    def __init__(self):
        self.config = Config()
        self.data_engine = DataEngine()
        self.ai_model = AIModel()
        self.bot = TelegramBot()
        self.running = True
        self.balance = self.config.INITIAL_BALANCE
        self.equity = []
        
        # Register signal handler
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        
    def exit_gracefully(self, signum, frame):
        """Handle shutdown signals"""
        self.running = False
        self.bot.send_alert("🛑 Trading bot stopped gracefully")
        sys.exit(0)
    
    def execute_trade(self, signal):
        """Execute trade (placeholder)"""
        print(f"Executing {signal} trade at {datetime.utcnow()}")
        return True
    
    def risk_management(self):
        """Calculate position size based on risk"""
        risk_amount = self.balance * (self.config.RISK_PERCENT / 100)
        return risk_amount
    
    def run(self):
        """Main trading loop"""
        if not self.ai_model.load_model():
            self.bot.send_alert("⚠️ Model not found! Starting training...")
            self.ai_model.train()
            
        self.bot.send_alert("🤖 Trading bot started successfully")
        
        while self.running:
            try:
                # Get market data
                data = self.data_engine.fetch_real_time_data()
                
                # Generate AI signal
                signal, strength = self.ai_model.generate_signal(data)
                
                if signal != "HOLD":
                    # Execute trade with risk management
                    amount = self.risk_management()
                    self.execute_trade(f"{signal} - Strength: {strength:.2f}")
                    self.bot.send_signal(signal, strength)
                
                # Record equity for performance tracking
                self.equity.append(self.balance)
                
                # Sleep until next candle
                time.sleep(300)  # 5-minute interval
                
            except Exception as e:
                self.bot.send_alert(f"🚨 ERROR: {str(e)}")
                time.sleep(60)  # Wait before retrying
