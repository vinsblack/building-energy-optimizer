import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib

class BuildingEnergyOptimizer:
    def __init__(self):
        """Initialize the Building Energy Optimizer."""
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self._is_trained = False

    def preprocess_data(self, data: pd.DataFrame) -> tuple:
        """
        Preprocess raw building data for training or prediction.
        
        Args:
            data (pd.DataFrame): Raw data with timestamps, weather, and energy data
            
        Returns:
            tuple: (X_scaled, y) preprocessed features and target
        """
        # Extract time features
        data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
        data['day_of_week'] = pd.to_datetime(data['timestamp']).dt.dayofweek
        data['month'] = pd.to_datetime(data['timestamp']).dt.month
        
        # Select features
        feature_columns = [
            'temperature', 'humidity', 'occupancy',
            'hour', 'day_of_week', 'month'
        ]
        
        X = data[feature_columns]
        y = data['energy_consumption'].to_numpy() if 'energy_consumption' in data.columns else None
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X) if not self._is_trained else self.scaler.transform(X)
        
        return X_scaled, y

    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the energy consumption prediction model.
        
        Args:
            X (np.ndarray): Scaled feature matrix
            y (np.ndarray): Target energy consumption values
        """
        self.model.fit(X, y)
        self._is_trained = True
        
    def predict(self, X: np.ndarray) -> tuple:
        """
        Predict energy consumption and generate optimization suggestions.
        
        Args:
            X (np.ndarray): Scaled feature matrix
            
        Returns:
            tuple: (predictions, suggestions) predicted values and optimization recommendations
        """
        if not self._is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        predictions = self.model.predict(X)
        suggestions = self._generate_optimization_suggestions(X, predictions)
        
        return predictions, suggestions
    
    def _generate_optimization_suggestions(self, X: np.ndarray, predictions: np.ndarray) -> list:
        """
        Generate energy optimization suggestions based on predictions.
        
        Args:
            X (np.ndarray): Feature matrix
            predictions (np.ndarray): Predicted energy consumption
            
        Returns:
            list: List of dictionaries containing optimization suggestions
        """
        suggestions = []
        avg_consumption = np.mean(predictions)
        
        for i, consumption in enumerate(predictions):
            if consumption > avg_consumption * 1.2:  # 20% above average
                suggestion = {
                    'timestamp': i,
                    'current_consumption': consumption,
                    'suggestions': []
                }
                
                # HVAC optimization
                if X[i][0] > 24:  # temperature > 24°C
                    suggestion['suggestions'].append({
                        'type': 'HVAC',
                        'action': 'Increase temperature setpoint by 2°C',
                        'estimated_savings': f"{(consumption * 0.1):.2f} kWh"
                    })
                
                # Lighting optimization based on hour
                if 23 <= X[i][2] <= 5:  # Night hours
                    suggestion['suggestions'].append({
                        'type': 'Lighting',
                        'action': 'Reduce lighting to 50% in unoccupied areas',
                        'estimated_savings': f"{(consumption * 0.05):.2f} kWh"
                    })
                
                if suggestion['suggestions']:
                    suggestions.append(suggestion)
        
        return suggestions

    def save_model(self, path: str) -> None:
        """
        Save the trained model and scaler.
        
        Args:
            path (str): Path to save the model
        """
        if not self._is_trained:
            raise ValueError("Cannot save untrained model")
            
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self._is_trained
        }, path)
    
    def load_model(self, path: str) -> None:
        """
        Load a trained model and scaler.
        
        Args:
            path (str): Path to the saved model
        """
        saved_objects = joblib.load(path)
        self.model = saved_objects['model']
        self.scaler = saved_objects['scaler']
        self._is_trained = saved_objects['is_trained']

def create_example_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Create example data for testing the optimizer.
    
    Args:
        start_date (str): Start date for the data
        end_date (str): End date for the data
        
    Returns:
        pd.DataFrame: Example dataset
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='h')
    np.random.seed(42)
    
    return pd.DataFrame({
        'timestamp': dates,
        'temperature': np.random.normal(22, 5, len(dates)),
        'humidity': np.random.normal(50, 10, len(dates)),
        'occupancy': np.random.randint(0, 100, len(dates)),
        'energy_consumption': np.random.normal(100, 20, len(dates))
    })