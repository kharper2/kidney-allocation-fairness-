# ML-Based Survival Prediction

This branch adds machine learning models for survival prediction as an alternative to the fixed formulas.

## Overview

The ML implementation provides:
- **Post-transplant survival prediction** using Random Forest
- **No-transplant survival prediction** using Random Forest
- Seamless integration with existing allocation code
- Ability to switch between fixed formulas and ML models

## Files

- `ml_models.py`: ML model classes for survival prediction
- `train_survival_models.py`: Script to train ML models from data
- `policy_baselines.py`: Modified to support ML models (backward compatible)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare training data:**
   You need a CSV file with:
   - Patient features: `Age`, `DialysisYears`, `Diabetes`, `EPTSScore`, etc.
   - Donor features: `KDPI` (for post-tx model)
   - Outcomes: `PostTxSurvivalYears`, `NoTxSurvivalYears`

3. **Train models:**
   ```bash
   python train_survival_models.py \
       --training_data data/srtr_training_data.csv \
       --output_dir models/ \
       --train_both
   ```

   This will create:
   - `models/post_tx_survival_model.joblib`
   - `models/no_tx_survival_model.joblib`

## Usage

### Option 1: Use ML Models in Allocation

```python
from ml_models import load_trained_models
from policy_baselines import compute_patient_features, exact_utility_for_pair

# Load trained models
post_tx_model, no_tx_model = load_trained_models(
    post_tx_model_path='models/post_tx_survival_model.joblib',
    no_tx_model_path='models/no_tx_survival_model.joblib'
)

# Compute features with ML
patients_feat = compute_patient_features(
    patients,
    use_ml=True,
    no_tx_model=no_tx_model
)

# Calculate utility with ML
util, post, no_tx = exact_utility_for_pair(
    patient_row,
    kdpi_norm=0.5,
    use_ml=True,
    post_tx_model=post_tx_model
)
```

### Option 2: Use Fixed Formulas (Default)

The code defaults to fixed formulas, so existing code continues to work:

```python
# Uses fixed formulas (no ML)
patients_feat = compute_patient_features(patients)
util, post, no_tx = exact_utility_for_pair(patient_row, kdpi_norm=0.5)
```

## Model Details

### Post-Transplant Survival Model

**Features:**
- `EPTS_norm`: Patient quality (0-1)
- `KDPI_norm`: Donor quality (0-1)
- `Age80`: Normalized age (0-1)
- `DialysisYears`: Years on dialysis
- `Diabetes`: Binary indicator
- Interactions: `EPTS × KDPI`, `EPTS × Age`, `KDPI × Age`

**Model Type:** Random Forest Regressor
- `n_estimators`: 100
- `max_depth`: 10
- `min_samples_split`: 20

### No-Transplant Survival Model

**Features:**
- `DialysisYears`: Years on dialysis
- `Diabetes`: Binary indicator
- `Age80`: Normalized age (0-1)
- `EPTS_norm`: Patient quality (0-1)
- `Ethnicity`: One-hot encoded (if available)
- `Sex`: Binary encoded (if available)

**Model Type:** Random Forest Regressor
- Same hyperparameters as post-tx model

## Comparison: Fixed Formulas vs ML

| Aspect | Fixed Formulas | ML Models |
|--------|---------------|-----------|
| **Transparency** | ✅ Fully transparent | ⚠️ Less interpretable |
| **Data Requirements** | ✅ None | ❌ Requires training data |
| **Accuracy** | ⚠️ Fixed assumptions | ✅ Learned from data |
| **Reproducibility** | ✅ Deterministic | ⚠️ Depends on training data |
| **Flexibility** | ❌ Fixed coefficients | ✅ Can discover patterns |

## Future Enhancements

- [ ] Support for XGBoost and other models
- [ ] Hyperparameter tuning
- [ ] Cross-validation
- [ ] Model evaluation metrics
- [ ] Feature importance visualization
- [ ] Uncertainty quantification
- [ ] Integration with full allocation pipeline

## Notes

- ML models are **optional** - the code works with or without them
- If ML models are not available, the code falls back to fixed formulas
- Training data must include actual survival outcomes (not available in synthetic data)
- For real deployment, you'd need SRTR data with actual transplant outcomes

