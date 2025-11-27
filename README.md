# AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness

This repository contains a complete reproducible pipeline for kidney allocation policy experiments comparing urgency, utility, hybrid, and fairness-constrained allocation strategies.

## Repository Structure

```
project_repo_skeleton/
├── policy_baselines.py          # Core allocation policies (urgency/utility/hybrid/fairness)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── data/                         # Data files
│   ├── patients.csv             # Synthetic patient cohort
│   ├── donors.csv               # Synthetic donor cohort
│   └── summary.csv              # Generated results from sweeps
├── figures/                      # Generated plots for paper
├── scripts/
│   ├── add_ses.py               # Add SES column to patient data
│   ├── run_sweep.py             # Parameter sweep runner (λ and η)
│   └── generate_plots.py        # Generate figures for paper
├── notebooks/
│   └── colab_policy_baselines.ipynb  # Standalone Colab notebook
└── paper/
    ├── main.tex                 # LaTeX paper with page estimates
    └── refs.bib                 # Bibliography (SRTR, OPTN)
```

## Quick Start (Local + Cursor)

### 1. Set up environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Add SES (Socioeconomic Status) to patient data

If your `patients.csv` doesn't have an SES column, add it with the 25/55/20 distribution (Low/Middle/High):

```bash
python scripts/add_ses.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_with_ses.csv
```

### 3. Run parameter sweep

```bash
# Set PYTHONPATH so policy_baselines can be imported
export PYTHONPATH=/Users/kathryn/Downloads/project_repo_skeleton:$PYTHONPATH

# Run sweep over λ (alpha: urgency/utility weight) and η (fairness weight)
python scripts/run_sweep.py \
  --patients data/patients_with_ses.csv \
  --donors data/donors.csv \
  --sample_patients 20000 \
  --sample_donors 3000 \
  --alphas 0.25 0.5 0.75 \
  --etas 0 0.5 1.0 \
  --group_col SES
```

This creates `data/summary.csv` with metrics for each configuration.

### 4. Generate plots for paper

```bash
python scripts/generate_plots.py --summary data/summary.csv --outdir figures
```

This generates:
- `figures/tradeoff_urgency_vs_benefit.png`
- `figures/tradeoff_fairness_vs_benefit.png`
- `figures/summary_bars.png`

### 5. Compile LaTeX paper

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The paper includes section titles with page estimates matching your assignment requirements.

## Google Colab (No Local Setup Required)

Your team can run experiments without local setup:

1. Open `notebooks/colab_policy_baselines.ipynb` in Google Colab
2. Run the installation cell (installs dependencies)
3. Either:
   - **Upload** `patients.csv` and `donors.csv` directly, or
   - **Mount Google Drive** and point to your data files
4. The notebook writes `policy_baselines.py` inline, so it's completely standalone
5. Run experiment and sweep cells
6. Download generated plots and `policy_comparison_summary.csv`

## Fairness Analysis

The framework supports **any grouping column** for fairness analysis:

### By Ethnicity (default)
```bash
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Ethnicity
```

### By SES (Socioeconomic Status)
```bash
python scripts/run_sweep.py \
  --patients data/patients_with_ses.csv \
  --donors data/donors.csv \
  --group_col SES
```

### By any other column
Just specify `--group_col YourColumnName`

## Key Metrics

The pipeline tracks:
- **Total benefit (years)**: Sum of survival benefit across all allocations
- **Mean urgency**: Average normalized urgency of recipients
- **Fairness L1**: Allocation disparity = 0.5 × Σ|allocation_share - population_share|
- **N assigned**: Number of successful allocations

## Policies Compared

1. **Urgency-only**: Prioritize sickest candidates (highest dialysis time + diabetes)
2. **Utility-only**: Maximize survival benefit (post-tx years - no-tx years)
3. **Hybrid**: λ × Urgency + (1-λ) × Utility, with grid search over λ ∈ [0,1]
4. **Fairness-constrained Hybrid**: Add dynamic adjustment to counter group underrepresentation

## Parameters

- **λ (alpha)**: Weight between urgency (λ=1) and utility (λ=0)
- **η (eta)**: Fairness constraint strength (η=0: no fairness, η>0: fairness-aware)
- **n_bins**: Number of KDPI bins for donor quality stratification (default: 10)
- **group_col**: Column name for fairness grouping (Ethnicity, SES, etc.)

## Citation

If you use this code, please cite:

```bibtex
@misc{kidney-allocation-fairness-2025,
  title={AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness},
  author={Barnouw, Natalie and Joseph, Olivia and Tubbs, Ella and Liu, Jessie and Harper, Kathryn and Siwek, Natalia},
  year={2025},
  note={MIT and Harvard University}
}
```

## Data Sources

- Synthetic cohorts based on SRTR and OPTN data structures
- SRTR: https://www.srtr.org/
- OPTN: https://optn.transplant.hrsa.gov/

## License

Educational use only. Not for clinical deployment.
