import torch
import torch.nn as nn
from typing import Dict, List
import numpy as np

class LSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int):
        super(LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class PricePredictionModel:
    def __init__(self):
        self.model = LSTM(input_size=10, hidden_size=64, num_layers=2)
        self.model.eval()
    
    async def predict(self, token_data: Dict) -> Dict:
        try:
            # Feature Extraction and Preprocessing
            features = self._extract_features(token_data)
            
            # Model Prediction
            with torch.no_grad():
                prediction = self.model(features)
            
            # Result Processing
            return {
                "predicted_price": float(prediction.numpy()[0][0]),
                "confidence_score": self._calculate_confidence(prediction),
                "price_trends": self._analyze_trends(token_data),
                "volatility_index": self._calculate_volatility(token_data)
            }
        
        except Exception as e:
            print(f"Price prediction error: {str(e)}")
            return {
                "error": "Price prediction failed",
                "details": str(e)
            }
    
    def _extract_features(self, token_data: Dict) -> torch.Tensor:
        # Extract Price-related Features
        price_history = np.array(token_data.get("price_history", []))
        volume_history = np.array(token_data.get("volume_history", []))
        liquidity_data = np.array(token_data.get("liquidity_data", []))
        
        # Feature Standardization
        features = np.column_stack([
            self._normalize(price_history),
            self._normalize(volume_history),
            self._normalize(liquidity_data)
        ])
        
        return torch.FloatTensor(features).unsqueeze(0)
    
    def _normalize(self, data: np.ndarray) -> np.ndarray:
        if len(data) == 0:
            return np.zeros(10)
        return (data - np.mean(data)) / (np.std(data) + 1e-8)
    
    def _calculate_confidence(self, prediction: torch.Tensor) -> float:
        # Calculate Confidence Based on Prediction Variance
        return float(torch.sigmoid(prediction.std()).item())
    
    def _analyze_trends(self, token_data: Dict) -> List[str]:
        trends = []
        price_history = token_data.get("price_history", [])
        
        if len(price_history) > 0:
            recent_trend = np.mean(np.diff(price_history[-5:]))
            if recent_trend > 0:
                trends.append("Upward Trend")
            elif recent_trend < 0:
                trends.append("Downward Trend")
            else:
                trends.append("Sideways Movement")
        
        return trends
    
    def _calculate_volatility(self, token_data: Dict) -> float:
        price_history = token_data.get("price_history", [])
        if len(price_history) > 1:
            returns = np.diff(np.log(price_history))
            return float(np.std(returns) * np.sqrt(365))
        return 0.0