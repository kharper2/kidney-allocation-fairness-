"""
ML Models for Survival Prediction

This module provides ML-based alternatives to the fixed formulas for:
- Post-transplant survival prediction
- No-transplant survival prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os


class SurvivalPredictor:
    """Base class for survival prediction models"""
    
    def __init__(self, model_type='random_forest', **model_kwargs):
        """
        Initialize survival predictor.
        
        Args:
            model_type: Type of model ('random_forest', 'xgboost', etc.)
            **model_kwargs: Additional arguments for the model
        """
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.model_kwargs = model_kwargs
        
    def _create_model(self):
        """Create the ML model instance"""
        if self.model_type == 'random_forest':
            default_kwargs = {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 20,
                'random_state': 42
            }
            default_kwargs.update(self.model_kwargs)
            return RandomForestRegressor(**default_kwargs)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def prepare_features(self, df: pd.DataFrame, kdpi_norm=None):
        """
        Prepare features for prediction.
        
        Args:
            df: DataFrame with patient features
            kdpi_norm: Normalized KDPI (0-1) for post-tx prediction
        
        Returns:
            Feature matrix X
        """
        raise NotImplementedError("Subclasses must implement prepare_features")
    
    def train(self, X, y, test_size=0.2, random_state=42):
        """
        Train the model.
        
        Args:
            X: Feature matrix
            y: Target values (survival years)
            test_size: Proportion of data for testing
            random_state: Random seed
        """
        if self.model is None:
            self.model = self._create_model()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        self.is_trained = True
        
        return {
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse
        }
    
    def predict(self, X):
        """
        Predict survival.
        
        Args:
            X: Feature matrix
        
        Returns:
            Predicted survival values
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict(X)
    
    def save(self, filepath):
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        joblib.dump(self.model, filepath)
    
    def load(self, filepath):
        """Load a trained model"""
        self.model = joblib.load(filepath)
        self.is_trained = True


class PostTxSurvivalPredictor(SurvivalPredictor):
    """ML model for post-transplant survival prediction"""
    
    def prepare_features(self, df: pd.DataFrame, kdpi_norm=None):
        """
        Prepare features for post-tx survival prediction.
        
        Features include:
        - EPTS (patient quality)
        - KDPI (donor quality)
        - Age80 (normalized age)
        - DialysisYears
        - Diabetes
        - Interactions (EPTS × KDPI, etc.)
        """
        features = []
        
        # Normalize EPTS
        if 'EPTSScore' in df.columns:
            epts_norm = df['EPTSScore'].clip(0, 100) / 100.0
        elif 'EPTS_norm' in df.columns:
            epts_norm = df['EPTS_norm']
        else:
            raise ValueError("EPTS information not found in dataframe")
        
        # Normalize age
        if 'Age' in df.columns:
            age80 = np.minimum(df['Age'], 80.0) / 80.0
        elif 'Age80' in df.columns:
            age80 = df['Age80']
        else:
            raise ValueError("Age information not found in dataframe")
        
        # Base features
        features.append(('EPTS_norm', epts_norm))
        features.append(('Age80', age80))
        
        # KDPI (donor quality) - must be provided
        if kdpi_norm is not None:
            if isinstance(kdpi_norm, (int, float)):
                kdpi_norm = np.full(len(df), kdpi_norm)
            features.append(('KDPI_norm', kdpi_norm))
        else:
            raise ValueError("KDPI_norm must be provided for post-tx prediction")
        
        # Additional patient features
        if 'DialysisYears' in df.columns:
            features.append(('DialysisYears', df['DialysisYears']))
        
        if 'Diabetes' in df.columns:
            features.append(('Diabetes', df['Diabetes'].astype(float)))
        
        # Interaction terms (important for post-tx survival)
        features.append(('EPTS_x_KDPI', epts_norm * kdpi_norm))
        features.append(('EPTS_x_Age', epts_norm * age80))
        if kdpi_norm is not None:
            features.append(('KDPI_x_Age', kdpi_norm * age80))
        
        # Build feature matrix
        X = pd.DataFrame({name: values for name, values in features})
        
        return X
    
    def predict_survival(self, df: pd.DataFrame, kdpi_norm):
        """
        Predict post-transplant survival for patient-donor pairs.
        
        Args:
            df: DataFrame with patient features
            kdpi_norm: Normalized KDPI (0-1) for each patient-donor pair
        
        Returns:
            Predicted survival years
        """
        X = self.prepare_features(df, kdpi_norm)
        return self.predict(X)


class NoTxSurvivalPredictor(SurvivalPredictor):
    """ML model for no-transplant survival prediction"""
    
    def prepare_features(self, df: pd.DataFrame, kdpi_norm=None):
        """
        Prepare features for no-tx survival prediction.
        
        Features include:
        - DialysisYears
        - Diabetes
        - Age80
        - EPTS (patient quality)
        - Additional patient characteristics
        """
        features = []
        
        # DialysisYears (key factor)
        if 'DialysisYears' in df.columns:
            features.append(('DialysisYears', df['DialysisYears']))
        else:
            raise ValueError("DialysisYears not found in dataframe")
        
        # Diabetes (binary)
        if 'Diabetes' in df.columns:
            features.append(('Diabetes', df['Diabetes'].astype(float)))
        else:
            raise ValueError("Diabetes not found in dataframe")
        
        # Normalize age
        if 'Age' in df.columns:
            age80 = np.minimum(df['Age'], 80.0) / 80.0
        elif 'Age80' in df.columns:
            age80 = df['Age80']
        else:
            raise ValueError("Age information not found in dataframe")
        features.append(('Age80', age80))
        
        # EPTS (patient quality - may affect survival without transplant)
        if 'EPTSScore' in df.columns:
            epts_norm = df['EPTSScore'].clip(0, 100) / 100.0
            features.append(('EPTS_norm', epts_norm))
        elif 'EPTS_norm' in df.columns:
            features.append(('EPTS_norm', df['EPTS_norm']))
        
        # Additional features that might be available
        if 'Ethnicity' in df.columns:
            # One-hot encode ethnicity
            ethnicity_encoded = pd.get_dummies(df['Ethnicity'], prefix='Ethnicity')
            for col in ethnicity_encoded.columns:
                features.append((col, ethnicity_encoded[col]))
        
        if 'Sex' in df.columns:
            # Encode sex as binary
            features.append(('Sex_M', (df['Sex'] == 'M').astype(float)))
        
        # Build feature matrix
        X = pd.DataFrame({name: values for name, values in features})
        
        return X
    
    def predict_survival(self, df: pd.DataFrame):
        """
        Predict no-transplant survival for patients.
        
        Args:
            df: DataFrame with patient features
        
        Returns:
            Predicted survival years
        """
        X = self.prepare_features(df)
        return self.predict(X)


def load_trained_models(post_tx_model_path=None, no_tx_model_path=None):
    """
    Load pre-trained survival prediction models.
    
    Args:
        post_tx_model_path: Path to saved post-tx model
        no_tx_model_path: Path to saved no-tx model
    
    Returns:
        Tuple of (post_tx_predictor, no_tx_predictor) or None if not available
    """
    post_tx = None
    no_tx = None
    
    if post_tx_model_path and os.path.exists(post_tx_model_path):
        post_tx = PostTxSurvivalPredictor()
        post_tx.load(post_tx_model_path)
    
    if no_tx_model_path and os.path.exists(no_tx_model_path):
        no_tx = NoTxSurvivalPredictor()
        no_tx.load(no_tx_model_path)
    
    return post_tx, no_tx

