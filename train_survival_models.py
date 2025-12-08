"""
Training script for ML survival prediction models.

This script trains ML models for:
- Post-transplant survival prediction
- No-transplant survival prediction

Usage:
    python train_survival_models.py \
        --training_data data/srtr_training_data.csv \
        --output_dir models/
"""

import argparse
import pandas as pd
import numpy as np
from ml_models import PostTxSurvivalPredictor, NoTxSurvivalPredictor
import os


def prepare_training_data(csv_path):
    """
    Load and prepare training data.
    
    Expected columns:
    - Patient features: Age, DialysisYears, Diabetes, EPTSScore, etc.
    - Donor features: KDPI (for post-tx)
    - Outcomes: PostTxSurvivalYears, NoTxSurvivalYears
    """
    df = pd.read_csv(csv_path)
    
    # Validate required columns
    required_cols = ['Age', 'DialysisYears', 'Diabetes', 'EPTSScore']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df


def train_post_tx_model(df, model_type='random_forest', **model_kwargs):
    """
    Train post-transplant survival model.
    
    Requires:
    - KDPI (donor quality)
    - PostTxSurvivalYears (outcome)
    """
    print("=" * 80)
    print("TRAINING POST-TRANSPLANT SURVIVAL MODEL")
    print("=" * 80)
    
    if 'KDPI' not in df.columns:
        raise ValueError("KDPI column required for post-tx model")
    if 'PostTxSurvivalYears' not in df.columns:
        raise ValueError("PostTxSurvivalYears column required for post-tx model")
    
    # Prepare features
    predictor = PostTxSurvivalPredictor(model_type=model_type, **model_kwargs)
    
    # For training, we need to prepare features for each patient-donor pair
    # This is a simplified version - in practice, you'd have paired data
    X_list = []
    y_list = []
    
    for idx, row in df.iterrows():
        # Create a single-row dataframe for this patient
        patient_df = pd.DataFrame([row])
        
        # Get KDPI for this pair
        kdpi = float(row['KDPI'])
        kdpi_norm = np.clip(kdpi, 0.0, 100.0) / 100.0
        
        # Prepare features
        X = predictor.prepare_features(patient_df, kdpi_norm=kdpi_norm)
        X_list.append(X.iloc[0])
        y_list.append(row['PostTxSurvivalYears'])
    
    X = pd.DataFrame(X_list)
    y = np.array(y_list)
    
    print(f"Training data shape: {X.shape}")
    print(f"Features: {list(X.columns)}")
    print(f"Target range: [{y.min():.2f}, {y.max():.2f}] years")
    print()
    
    # Train model
    metrics = predictor.train(X, y)
    
    print("Training Results:")
    print(f"  Train R²: {metrics['train_r2']:.4f}")
    print(f"  Test R²:  {metrics['test_r2']:.4f}")
    print(f"  Train RMSE: {metrics['train_rmse']:.2f} years")
    print(f"  Test RMSE:  {metrics['test_rmse']:.2f} years")
    print()
    
    # Feature importance
    if hasattr(predictor.model, 'feature_importances_'):
        importances = predictor.model.feature_importances_
        feature_importance = sorted(
            zip(X.columns, importances),
            key=lambda x: x[1],
            reverse=True
        )
        print("Top 10 Most Important Features:")
        for feature, importance in feature_importance[:10]:
            print(f"  {feature}: {importance:.4f}")
    
    return predictor


def train_no_tx_model(df, model_type='random_forest', **model_kwargs):
    """
    Train no-transplant survival model.
    
    Requires:
    - NoTxSurvivalYears (outcome)
    """
    print("=" * 80)
    print("TRAINING NO-TRANSPLANT SURVIVAL MODEL")
    print("=" * 80)
    
    if 'NoTxSurvivalYears' not in df.columns:
        raise ValueError("NoTxSurvivalYears column required for no-tx model")
    
    # Prepare features
    predictor = NoTxSurvivalPredictor(model_type=model_type, **model_kwargs)
    
    # Prepare features for all patients
    X = predictor.prepare_features(df)
    y = df['NoTxSurvivalYears'].values
    
    print(f"Training data shape: {X.shape}")
    print(f"Features: {list(X.columns)}")
    print(f"Target range: [{y.min():.2f}, {y.max():.2f}] years")
    print()
    
    # Train model
    metrics = predictor.train(X, y)
    
    print("Training Results:")
    print(f"  Train R²: {metrics['train_r2']:.4f}")
    print(f"  Test R²:  {metrics['test_r2']:.4f}")
    print(f"  Train RMSE: {metrics['train_rmse']:.2f} years")
    print(f"  Test RMSE:  {metrics['test_rmse']:.2f} years")
    print()
    
    # Feature importance
    if hasattr(predictor.model, 'feature_importances_'):
        importances = predictor.model.feature_importances_
        feature_importance = sorted(
            zip(X.columns, importances),
            key=lambda x: x[1],
            reverse=True
        )
        print("Top 10 Most Important Features:")
        for feature, importance in feature_importance[:10]:
            print(f"  {feature}: {importance:.4f}")
    
    return predictor


def main():
    parser = argparse.ArgumentParser(
        description='Train ML models for survival prediction'
    )
    parser.add_argument(
        '--training_data',
        required=True,
        help='Path to CSV with training data (must include outcomes)'
    )
    parser.add_argument(
        '--output_dir',
        default='models/',
        help='Directory to save trained models'
    )
    parser.add_argument(
        '--model_type',
        default='random_forest',
        choices=['random_forest'],
        help='Type of ML model to use'
    )
    parser.add_argument(
        '--train_post_tx',
        action='store_true',
        help='Train post-transplant survival model'
    )
    parser.add_argument(
        '--train_no_tx',
        action='store_true',
        help='Train no-transplant survival model'
    )
    parser.add_argument(
        '--train_both',
        action='store_true',
        help='Train both models (default if neither flag specified)'
    )
    
    args = parser.parse_args()
    
    # Default to training both if neither specified
    if not args.train_post_tx and not args.train_no_tx:
        args.train_both = True
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load training data
    print("Loading training data...")
    df = prepare_training_data(args.training_data)
    print(f"Loaded {len(df)} records")
    print()
    
    # Train models
    if args.train_both or args.train_post_tx:
        post_tx_model = train_post_tx_model(df, model_type=args.model_type)
        post_tx_path = os.path.join(args.output_dir, 'post_tx_survival_model.joblib')
        post_tx_model.save(post_tx_path)
        print(f"Saved post-tx model to: {post_tx_path}")
        print()
    
    if args.train_both or args.train_no_tx:
        no_tx_model = train_no_tx_model(df, model_type=args.model_type)
        no_tx_path = os.path.join(args.output_dir, 'no_tx_survival_model.joblib')
        no_tx_model.save(no_tx_path)
        print(f"Saved no-tx model to: {no_tx_path}")
        print()
    
    print("=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

