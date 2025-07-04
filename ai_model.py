import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from sklearn.metrics import accuracy_score
import numpy as np
import os
from data_engine import DataEngine
from config import Config

class AIModel:
    def __init__(self):
        self.config = Config()
        self.data_engine = DataEngine()
        self.model = None
        
    def build_model(self, input_shape):
        """Build LSTM model for Python 3.11"""
        model = Sequential([
            Input(shape=input_shape),
            LSTM(64, return_sequences=True),
            Dropout(0.3),
            LSTM(32),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', 
                     loss='binary_crossentropy', 
                     metrics=['accuracy'])
        return model
    
    def train(self):
        """Train and save model"""
        # Get historical data
        hist_data = self.data_engine.fetch_historical_data(days=90)
        X, y = self.data_engine.prepare_training_data(hist_data)
        
        # Reshape for LSTM (samples, time steps, features)
        X = X.reshape((X.shape[0], 1, X.shape[1]))
        
        # Build and train model
        self.model = self.build_model((X.shape[1], X.shape[2]))
        self.model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=1)
        
        # Save model in .h5 format
        self.model.save(self.config.MODEL_PATH)
        
        # Backtesting
        y_pred = (self.model.predict(X) > 0.5).astype(int)
        accuracy = accuracy_score(y, y_pred)
        print(f"Backtesting Accuracy: {accuracy:.2%}")
        return accuracy
    
    def load_model(self):
        """Load pre-trained model"""
        if os.path.exists(self.config.MODEL_PATH):
            self.model = load_model(self.config.MODEL_PATH)
            return True
        return False
    
    def generate_signal(self, current_data):
        """Generate trading signal"""
        # Prepare data
        prediction_data = self.data_engine.prepare_prediction_data(current_data)
        prediction_data = prediction_data.reshape((1, 1, prediction_data.shape[1]))
        
        # Get model prediction
        prediction = self.model.predict(prediction_data)[0][0]
        
        # Generate signal
        signal_strength = abs(prediction - 0.5) * 2  # Convert to 0-1 range
        
        if prediction > 0.7 and signal_strength > 0.6:
            return "BUY", signal_strength
        elif prediction < 0.3 and signal_strength > 0.6:
            return "SELL", signal_strength
        return "HOLD", 0
