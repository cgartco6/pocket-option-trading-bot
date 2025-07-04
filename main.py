
from trading_engine import TradingEngine
import threading
import time
import schedule
import os
from config import Config

def training_job():
    """Scheduled model training"""
    from ai_model import AIModel
    from telegram_bot import TelegramBot
    
    try:
        ai = AIModel()
        accuracy = ai.train()
        bot = TelegramBot()
        bot.send_alert(f"🔄 Model retraining completed. Accuracy: {accuracy:.2%}")
    except Exception as e:
        print(f"Training failed: {e}")
        try:
            bot.send_alert(f"❌ Model training failed: {str(e)}")
        except:
            pass  # If bot isn't defined

def run_scheduler():
    """Background scheduler for periodic tasks"""
    # Daily retraining at 1 AM UTC
    schedule.every().day.at("01:00").do(training_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs(os.path.dirname(Config().MODEL_PATH), exist_ok=True)
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start trading engine
    engine = TradingEngine()
    engine.run()
