import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Pocket Option API credentials
    POCKET_EMAIL = os.getenv("POCKET_EMAIL", "your_email@domain.com")
    POCKET_PASSWORD = os.getenv("POCKET_PASSWORD", "your_password")
    
    # Telegram configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_telegram_bot_token")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your_chat_id")
    
    # Trading parameters
    ASSET = "EURUSD"
    TIMEFRAME = "5m"
    INITIAL_BALANCE = 10000
    RISK_PERCENT = 1
    
    # Indicator configuration (Rian's settings)
    INDICATORS = {
        'ema_fast': {'period': 5, 'color': '#39FF14', 'width': 2},
        'ema_slow': {'period': 20, 'color': '#FF3131', 'width': 2},
        'rsi': {'period': 6},
        'macd': {'fast': 8, 'slow': 18, 'signal': 6}
    }
    
    # Path configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "trading_model.h5")
    SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
