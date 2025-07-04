import requests
from datetime import datetime
import time
from config import Config

class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.base_url = f"https://api.telegram.org/bot{self.config.TELEGRAM_TOKEN}"
        
    def send_signal(self, signal, strength):
        """Send signal to Telegram with retry logic"""
        message = (
            f"🚀 *AI Trading Signal* 🚀\n\n"
            f"• **Asset**: {self.config.ASSET}\n"
            f"• **Signal**: {signal}\n"
            f"• **Strength**: {strength:.2%}\n"
            f"• **Time**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
        
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.config.TELEGRAM_CHAT_ID,
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return True
            except Exception as e:
                print(f"Telegram send error (attempt {attempt+1}): {str(e)}")
                time.sleep(5)
        return False
    
    def send_alert(self, message):
        """Send custom alert to Telegram"""
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.config.TELEGRAM_CHAT_ID,
                        "text": message
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return True
            except Exception as e:
                print(f"Telegram alert error (attempt {attempt+1}): {str(e)}")
                time.sleep(5)
        return False
