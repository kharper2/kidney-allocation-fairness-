# Usage Guide: Kidney Allocation Policy Experiments

## Quick Commands Cheat Sheet

### Basic Setup
```bash
# One-time setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### Add SES to Patient Data
```bash
python scripts/add_ses.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_with_ses.csv \
  --probs 0.25 0.55 0.20  # Low, Middle, High percentages
```

### Run Parameter Sweep
```bash
# Basic sweep
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Ethnicity

# Custom sweep with specific parameters
python scripts/run_sweep.py \
  --patients data/patients_with_ses.csv \
  --donors data/donors.csv \
  --sample_patients 50000 \
  --sample_donors 10000 \
  --alphas 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 \
  --etas 0 0.25 0.5 0.75 1.0 \
  --group_col SES \
  --seed 42
```

### Generate Plots
```bash
python scripts/generate_plots.py \
  --summary data/summary.csv \
  --outdir figures
```

### Full Pipeline (All Steps)
```bash
./run_full_pipeline.sh
```

## Understanding the Parameters

### λ (alpha): Urgency vs Utility Weight
- **λ = 1.0**: Pure urgency (prioritize sickest)
- **λ = 0.0**: Pure utility (maximize survival benefit)
- **λ = 0.5**: Balanced hybrid
- **λ ∈ [0,1]**: Any weight between extremes

**Trade-off**: Higher λ → higher mean urgency, lower total benefit

### η (eta): Fairness Constraint
- **η = 0.0**: No fairness adjustment (baseline)
- **η > 0.0**: Fairness-aware (counters underrepresentation)
- **η = 1.0**: Strong fairness enforcement

**Trade-off**: Higher η → lower disparity (fairer), potentially lower total benefit

### Sample Sizes
- `--sample_patients`: Number of patients to sample (default: 20000)
- `--sample_donors`: Number of donors to sample (default: 3000)
- Use smaller samples for quick tests, larger for final results

### Group Column
- `--group_col Ethnicity`: Analyze fairness by ethnicity
- `--group_col SES`: Analyze fairness by socioeconomic status
- Any column in your patient data can be used

## Expected Results

### Policy Performance (Typical Patterns)

| Policy | Total Benefit | Mean Urgency | Fairness L1 |
|--------|--------------|--------------|-------------|
| Urgency-only (λ=1) | ★★☆☆ Low | ★★★★ High | ★★★☆ Medium |
| Utility-only (λ=0) | ★★★★ High | ★★☆☆ Low | ★★☆☆ Medium |
| Hybrid (λ=0.5) | ★★★☆ Med-High | ★★★☆ Medium | ★★★☆ Medium |
| Hybrid+Fair (λ=0.5, η=1) | ★★★☆ Medium | ★★★☆ Medium | ★★★★ Low (best) |

### Key Metrics Explained

**Total Benefit (years)**: Sum of survival benefit (post-transplant years - no-transplant years) across all allocations. Higher is better.

**Mean Urgency (normalized)**: Average urgency score of recipients. Based on log(1 + dialysis years) + diabetes penalty. Range [0,1], higher means prioritizing sicker patients.

**Fairness L1**: Allocation disparity = 0.5 × Σ|allocation_share - population_share|. Lower is fairer (0 = perfect proportional representation).

**N Assigned**: Number of successful allocations. Should be close to number of donors unless many compatibility issues.

## Common Workflows

### Experiment 1: Find Optimal λ (Alpha)
```bash
# Fine-grained alpha sweep
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --alphas 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 \
  --etas 0 \
  --group_col Ethnicity

# Generate trade-off plot
python scripts/generate_plots.py
```

### Experiment 2: Fairness Analysis by SES
```bash
# Add SES
python scripts/add_ses.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_with_ses.csv

# Run with fairness constraints
python scripts/run_sweep.py \
  --patients data/patients_with_ses.csv \
  --donors data/donors.csv \
  --alphas 0.5 \
  --etas 0 0.5 1.0 \
  --group_col SES
```

### Experiment 3: Compare Ethnicity vs SES Fairness
```bash
# Run both
python scripts/run_sweep.py --patients data/patients.csv --donors data/donors.csv --group_col Ethnicity
mv data/summary.csv data/summary_ethnicity.csv

python scripts/run_sweep.py --patients data/patients_with_ses.csv --donors data/donors.csv --group_col SES
mv data/summary.csv data/summary_ses.csv

# Plot both
python scripts/generate_plots.py --summary data/summary_ethnicity.csv --outdir figures/ethnicity
python scripts/generate_plots.py --summary data/summary_ses.csv --outdir figures/ses
```

## Colab Usage

### Option A: Upload Files
1. Open `notebooks/colab_policy_baselines.ipynb` in Colab
2. Run cell 1 (install dependencies)
3. Run cell 2 (write policy_baselines.py)
4. Run cell 4 (upload CSVs when prompted)
5. Run cells 6-9 (experiments and plots)
6. Download generated files

### Option B: Mount Google Drive
1. Upload your CSVs to Google Drive
2. Open notebook in Colab
3. Run cell 1-2
4. Uncomment and run cell 5 (mount Drive)
5. Update paths in cell 5 to point to your Drive files
6. Run cells 6-9

## Troubleshooting

### "ModuleNotFoundError: No module named 'policy_baselines'"
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### "FileNotFoundError: data/patients.csv"
```bash
# Make sure you're in the project root
cd /Users/kathryn/Downloads/project_repo_skeleton
# Verify files exist
ls data/
```

### Plots don't show fairness differences
- Check that your grouping column has multiple distinct values
- Try increasing sample size
- Verify η > 0 for fairness-aware runs

### Low number of assignments (n_assigned << n_donors)
- Check blood type compatibility in your data
- Verify KDPI values are in [0, 100] range
- Check for NaN/missing values in key columns

## Team Roles & Responsibilities

Based on the paper structure, suggested division:

1. **Data & Simulation** (Natalie, Kathryn): Patient/donor generation, SES integration
2. **Policy Implementation** (Olivia, Kathryn): Core algorithms in policy_baselines.py
3. **Fairness Mechanism** (Ella, Natalia): Fairness-constrained hybrid policy
4. **Evaluation & Plots** (Jessie): Metrics, visualization, trade-off analysis
5. **Literature Review** (All): Background section
6. **ML Survival Surrogate** (Graduate credit option): Replace parametric model
7. **Weight Optimization** (Graduate credit option): Automated λ/η tuning

## LaTeX Paper Compilation

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
open main.pdf  # or xdg-open main.pdf on Linux
```

### Updating Figures in Paper
1. Generate figures with `generate_plots.py`
2. They're already referenced in `paper/main.tex`:
   - `tradeoff_urgency_vs_benefit.png`
   - `tradeoff_fairness_vs_benefit.png`
3. Copy additional figures to `paper/` if needed
4. Update `\includegraphics{...}` paths if necessary

## Advanced: Custom Policies

To add a new policy:

1. Edit `policy_baselines.py`
2. Add new scoring logic in `allocate()` function
3. Update `run_experiment()` or `sweep()` to include new policy
4. Re-run experiments

Example: Add age-adjusted urgency:
```python
# In compute_patient_features():
out['Urgency_age_adj'] = out['Urgency_norm'] * (1 + 0.1 * out['Age80'])

# In allocate():
elif policy == 'urgency_age':
    score = U_age_adj[i]
```

## Questions?

- Check README.md for overview
- See paper/main.tex for methodology details
- Review policy_baselines.py for implementation
- Open an issue or contact team members

