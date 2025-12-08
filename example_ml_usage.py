"""
Example: Using ML models for survival prediction in allocation

This script demonstrates how to:
1. Load trained ML models
2. Use them in the allocation pipeline
3. Compare results with fixed formulas
"""

import pandas as pd
from ml_models import load_trained_models
from policy_baselines import compute_patient_features, allocate

# Example: Load trained models (if available)
# post_tx_model, no_tx_model = load_trained_models(
#     post_tx_model_path='models/post_tx_survival_model.joblib',
#     no_tx_model_path='models/no_tx_survival_model.joblib'
# )

# Load data
patients = pd.read_csv('data/patients.csv')
donors = pd.read_csv('data/donors.csv')

# Sample for quick test
patients_sample = patients.sample(n=1000, random_state=42).reset_index(drop=True)
donors_sample = donors.sample(n=200, random_state=42).reset_index(drop=True)

print("=" * 80)
print("EXAMPLE: Using Fixed Formulas (Default)")
print("=" * 80)

# Option 1: Use fixed formulas (default, no ML)
patients_feat = compute_patient_features(patients_sample)
alloc_df, metrics = allocate(
    donors_sample,
    patients_feat,
    policy='hybrid',
    alpha=0.5,
    fairness_eta=0.0,
    group_col='Ethnicity'
)

print(f"Total benefit: {metrics['total_benefit_years']:.2f} years")
print(f"Mean urgency: {metrics['mean_urgency_norm']:.3f}")
print(f"Fairness L1: {metrics['fairness_L1']:.3f}")
print(f"Assigned: {metrics['n_assigned']} patients")
print()

# Uncomment below when you have trained models:
# print("=" * 80)
# print("EXAMPLE: Using ML Models")
# print("=" * 80)
# 
# # Option 2: Use ML models
# patients_feat_ml = compute_patient_features(
#     patients_sample,
#     use_ml=True,
#     no_tx_model=no_tx_model
# )
# 
# alloc_df_ml, metrics_ml = allocate(
#     donors_sample,
#     patients_feat_ml,
#     policy='hybrid',
#     alpha=0.5,
#     fairness_eta=0.0,
#     group_col='Ethnicity',
#     use_ml=True,
#     post_tx_model=post_tx_model,
#     no_tx_model=no_tx_model
# )
# 
# print(f"Total benefit (ML): {metrics_ml['total_benefit_years']:.2f} years")
# print(f"Mean urgency (ML): {metrics_ml['mean_urgency_norm']:.3f}")
# print(f"Fairness L1 (ML): {metrics_ml['fairness_L1']:.3f}")
# print(f"Assigned (ML): {metrics_ml['n_assigned']} patients")
# print()
# 
# print("=" * 80)
# print("COMPARISON")
# print("=" * 80)
# print(f"Benefit difference: {metrics_ml['total_benefit_years'] - metrics['total_benefit_years']:.2f} years")
# print(f"Urgency difference: {metrics_ml['mean_urgency_norm'] - metrics['mean_urgency_norm']:.3f}")

print()
print("=" * 80)
print("NOTE: To use ML models, you need to:")
print("  1. Train models using train_survival_models.py")
print("  2. Uncomment the ML code sections above")
print("=" * 80)

