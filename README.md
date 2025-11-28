# AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness

**Complete reproducible pipeline for kidney allocation policy experiments**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()

---

⚠️ **IMPORTANT:** All current results are from **proof-of-concept runs with 5,000 patients, 1,000 donors** (sampled from full dataset). All branches are **IMPLEMENTED & TESTED**, but **FINAL EXPERIMENTS MUST USE 20k-150k patients, 3k-20k donors for the paper.**

---

## 📑 Table of Contents

1. [Quick Start (3 Commands)](#-quick-start-3-commands)
2. [What's Included](#-whats-included)
3. [Repository Branches](#-repository-branches)
4. [Detailed Usage Guide](#-detailed-usage-guide)
5. [Understanding Results](#-understanding-results)
6. [Google Colab (No Setup)](#-google-colab-no-setup)
7. [Project Status](#-project-status)
8. [Submission Checklist](#-submission-checklist)
9. [Team Roles & Next Steps](#-team-roles--next-steps)
10. [Citation & License](#-citation--license)

---

## 🚀 Quick Start (3 Commands)

### Option 1: Automated (Recommended)
```bash
cd kidney-allocation-fairness-
./run_full_pipeline.sh
```
**Done!** All experiments run, all figures generated in ~5 minutes.

### Option 2: Manual Control
```bash
# 1. Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd):$PYTHONPATH

# 2. Run experiments
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --alphas 0.25 0.5 0.75 \
  --etas 0 1.0 \
  --group_col Ethnicity

# 3. Generate plots and analysis
python scripts/generate_plots.py
python scripts/analyze_results.py
```

### Option 3: Google Colab (No Setup)
1. Open `notebooks/colab_policy_baselines.ipynb`
2. Click "Open in Colab"
3. Run all cells
4. Upload data when prompted

---

## 📦 What's Included

### Core Implementation
✅ **5 Allocation Policies**
- **Urgency-only**: Prioritize sickest patients (uses dialysis time + diabetes)
- **Wait-Time-only**: Naive baseline using wait time only (for comparison)
- **Utility-only**: Maximize survival benefit
- **Hybrid**: Weighted combination of urgency + utility (α parameter)
- **Hybrid+Fair**: Hybrid with fairness constraint (η parameter)

✅ **Features**
- Flexible grouping (Ethnicity, DistancetoCenterMiles, Sex - SRTR data)
- ABO blood type compatibility
- KDPI-based donor quality stratification
- Complete reproducibility (fixed seeds)

### Tools & Scripts
```
scripts/
├── run_sweep.py         # Parameter sweeps over α and η
├── generate_plots.py    # Publication-quality figures (300 DPI)
└── analyze_results.py   # Summary statistics + LaTeX tables
```

### Paper
- `paper/main.tex` - Complete LaTeX structure with **page estimates in section titles**
- `paper/refs.bib` - Bibliography (SRTR, OPTN citations)
- All sections outlined: Abstract → Conclusion
- Equations for urgency, utility, fairness
- Figure placeholders configured

### Notebook
- `notebooks/colab_policy_baselines.ipynb` - Standalone Colab notebook
- Writes `policy_baselines.py` inline
- No local Python installation required
- Upload or Google Drive options

### Test Results (Proof of Concept - 5k patients, 1k donors)

**9 policy configurations tested per branch:**
- **3 Baseline policies:** Urgency, Wait-Time, Utility
- **6 Hybrid policies:** Grid search over α ∈ {0.25, 0.5, 0.75} × η ∈ {0.0, 1.0}

**All 3 branches tested and verified:**
- ✅ Main branch (single-dimension)
- ✅ Composite-fairness branch (intersectional groups)
- ✅ Multidim-fairness branch (weighted multi-dimensional)

---

## 🌳 Repository Branches - Three Fairness Approaches

This repository has **3 branches** testing different fairness approaches.

### Quick Summary

| Branch | Approach | Status | Best Result |
|--------|----------|--------|-------------|
| **`main`** | Single-dimension (Ethnicity, Distance, or Sex) | ✅ Tested | 9,512 years (Sex), 9,125 years (Distance), 8,960 years (Ethnicity) |
| **`multidim-fairness`** ⭐ | Weighted multi-dimensional (Ethnicity + Distance) | ✅ Tested | **9,501 years, L1=0.0015** |
| **`composite-fairness`** | Intersectional groups (Ethnicity × Distance) | ✅ Tested | 6,479 years, L1=0.0043 (sparse groups) |

**📋 See [`BRANCHES.md`](BRANCHES.md) for detailed descriptions, usage instructions, and full results**

**📋 See [`POLICY_FAIRNESS_INTERACTION.md`](POLICY_FAIRNESS_INTERACTION.md) for how allocation policies interact with fairness approaches**

---

## 📖 Detailed Usage Guide

### Repository Structure

```
kidney-allocation-fairness-/
├── policy_baselines.py          # Core allocation algorithms
├── requirements.txt              # Python dependencies
├── run_full_pipeline.sh          # One-command automation
├── data/
│   ├── patients.csv             # 150k synthetic patients
│   ├── donors.csv               # 20k synthetic donors
│   └── summary.csv              # Results (generated)
├── figures/                      # Generated plots
│   ├── tradeoff_urgency_vs_benefit.png
│   ├── tradeoff_fairness_vs_benefit.png
│   └── summary_bars.png
├── scripts/                      # Command-line tools
├── notebooks/                    # Jupyter/Colab notebooks
└── paper/                        # LaTeX paper
```

### Fairness Dimensions (SRTR Data)

**Available columns in `patients.csv` for fairness:**
- **`Ethnicity`** - Hispanic, Black, White, Asian, Other
- **`DistancetoCenterMiles`** - Distance to treatment center (<50, 50-100, 100-150, 150-250, >250 miles) - **SRTR accessibility measure**
- **`Sex`** - M, F

**Note:** We use only SRTR data fields. Distance to treatment center is a key accessibility measure used in transplant allocation.

### Running Parameter Sweeps (Grid Search)

**How it works:**
1. Always tests 2 baseline policies: **Urgency** (α=1.0) and **Utility** (α=0.0)
2. Then performs **grid search** over α and η for **Hybrid policies only**

**Basic sweep (default grid):**
```bash
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Ethnicity
```
**Default grid for Hybrid:** α ∈ {0.25, 0.5, 0.75} × η ∈ {0.0, 1.0} = **6 Hybrid configurations**  
**Plus 3 baselines** (Urgency, Wait-Time, Utility) = **9 total configurations**

**Custom grid search (finer grid):**
```bash
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --sample_patients 50000 \
  --sample_donors 10000 \
  --alphas 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 \
  --etas 0 0.25 0.5 0.75 1.0 \
  --group_col DistancetoCenterMiles \
  --seed 42
```
**This grid for Hybrid:** 11 α values × 5 η values = **55 Hybrid configurations**  
**Plus 2 baselines** = **57 total configurations**

**Note:** The grid search only applies to Hybrid policies. Urgency and Utility are always tested separately as baselines.

### Generating Plots

   ```bash
python scripts/generate_plots.py \
  --summary data/summary.csv \
  --outdir figures
```

Creates:
- `tradeoff_urgency_vs_benefit.png`
- `tradeoff_fairness_vs_benefit.png`
- `summary_bars.png`

### Analyzing Results

```bash
python scripts/analyze_results.py \
  --summary data/summary.csv \
  --output data/analysis.txt
```

Generates:
- Summary statistics
- Best policies by metric
- Trade-off analysis
- LaTeX table
- Pareto frontier identification

### Compiling LaTeX Paper

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
open main.pdf  # or xdg-open on Linux
```

---

## 📊 Understanding Results

### Key Metrics

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Total Benefit (years)** | Sum of survival gain (post-tx - no-tx) | Higher ↑ |
| **Mean Urgency (0-1)** | Avg normalized urgency of recipients | Higher ↑ for equity |
| **Fairness L1 (0-1)** | Allocation disparity vs population | Lower ↓ (0=perfect) |
| **N Assigned** | Number of successful allocations | Close to # donors |

### Parameters

- **α (alpha)**: Urgency/utility weight (1.0=pure urgency, 0.0=pure utility, 0.5=balanced)  
- **η (eta)**: Fairness strength (0.0=none, 1.0=strong enforcement)  
- **group_col**: Fairness dimension (`Ethnicity`, `DistancetoCenterMiles`, `Sex` - SRTR data)

### Sample Results (Preliminary - Proof of Concept)

**Verified Results (5k patients, 1k donors):**

| Approach | Best Result | Why It Works |
|----------|-------------|--------------|
| **Main (Sex)** | 9,512 years, L1=0.0003 | 2 groups easy to balance, high efficiency (99% organs used) |
| **Multidim (Ethnicity+Distance)** | 9,501 years, L1=0.0015 | Tracks 10 groups independently, avoids sparse group problem |
| **Main (Distance)** | 9,125 years, L1=0.0010 | SRTR accessibility measure, 5 distance categories |
| **Main (Ethnicity)** | 8,960 years, L1=0.0008 | Standard approach, 5 groups, 96% organs used |
| **Composite (Ethnicity×Distance)** | 6,479 years, L1=0.0043 | 25 intersectional groups too sparse, 25% organs wasted |

**Key Findings:**
- **Utility beats Urgency**: 10,391 vs 8,038 years (+29%) - healthy recipients gain more years
- **Fairness works well**: L1 drops from 0.021 to 0.0003-0.0015 with only 3-8% benefit cost
- **Sex fairness best**: 2 groups easier to balance than 5 (9,512 vs 8,960 years)
- **Multidim beats Composite**: 9,501 vs 6,479 years - flexible tracking avoids sparse groups

**📋 See [`BRANCHES.md`](BRANCHES.md) for complete results and detailed explanations**

### Understanding the Figures

**Figure 1: Urgency vs Benefit** - Pareto frontier (can't improve both)  
**Figure 2: Fairness vs Benefit** - Small benefit cost for large fairness gain  
**Figure 3: Summary Bars** - Side-by-side policy comparison (Blue=no fairness, Red=with fairness)

---

## ☁️ Google Colab (No Setup)

### Using the Colab Notebook

1. **Open notebook**: `notebooks/colab_policy_baselines.ipynb`
2. **Click**: "Open in Colab" badge (or upload to Colab)
3. **Run**: All cells in order
4. **Upload data**: When prompted (or mount Google Drive)
5. **Download results**: Generated plots and CSV files

**Perfect for**: Team members without local Python setup, quick experiments, sharing results

---

## 📈 Project Status

### ✅ Completed Components

| Component | Status | Tested |
|-----------|--------|--------|
| **Policy Algorithms** | ✅ Complete | ✅ Yes |
| **Parameter Sweep Tool** | ✅ Complete | ✅ Yes |
| **Plot Generation** | ✅ Complete | ✅ Yes |
| **Results Analysis** | ✅ Complete | ✅ Yes |
| **Full Pipeline** | ✅ Complete | ✅ Yes |
| **LaTeX Paper Structure** | ✅ Complete | N/A |
| **Colab Notebook** | ✅ Complete | ✅ Yes |
| **Documentation** | ✅ Complete | N/A |

### Test Results

**All tests passed:**
- ✓ policy_baselines imports successfully
- ✓ run_sweep.py works
- ✓ generate_plots.py works
- ✓ analyze_results.py works
- ✓ Full pipeline completes successfully

**Data validation:**
- ✓ patients.csv: 150,002 rows
- ✓ donors.csv: 20,002 rows
- ✓ 9 configurations tested successfully (3 baselines + 6 Hybrid)

### Performance Benchmarks

| Task | Sample Size | Runtime |
|------|-------------|---------|
| Quick Sweep | 5k/1k | 10 sec |
| Full Sweep | 20k/3k | 45 sec |
| Large Sweep | 50k/10k | 3 min |
| Full Pipeline | 20k/3k | 5 min |

---

## ✅ Submission Checklist

### Before Final Submission

#### Experiments
- [ ] Run full experiments with large sample sizes (20k-50k patients)
- [ ] Generate final figures at 300 DPI
- [ ] Verify results are stable across random seeds
- [ ] Export all summary tables

#### Paper
- [ ] Complete all sections (Abstract → Conclusion)
- [ ] Insert all figures with captions
- [ ] Insert LaTeX tables from analysis
- [ ] Verify all equations are correct
- [ ] Check all citations in refs.bib
- [ ] Compile LaTeX without errors
- [ ] Proofread entire paper
- [ ] Verify page count meets requirements

#### Code
- [ ] All scripts run without errors
- [ ] Code is well-commented
- [ ] Requirements.txt is complete
- [ ] Full pipeline works end-to-end
- [ ] Colab notebook tested

#### Documentation
- [ ] README is comprehensive
- [ ] Usage examples are clear
- [ ] Team contributions documented

#### Final Checks
- [ ] Generate final PDF
- [ ] Test Colab with all team members
- [ ] Verify GitHub repository is accessible
- [ ] Backup all materials

---

## 👥 Team Roles & Next Steps

### What's Done ✅

| Person | Work Completed |
|--------|----------------|
| **Ella** | Generated patient & donor data (~150k patients, ~20k donors) |
| **Natalie** | Urgency score feature engineering (log dialysis time) |
| **Kathryn** | Complete code implementation (all 4 policies), automation pipeline, scripts, LaTeX structure, Colab notebook, documentation, GitHub setup, **3 fairness approaches** (single-dimension, composite groups, weighted multi-dimensional), **proof-of-concept tests** on all branches (5k patients, 1k donors) |

### What Still Needs To Be Done ⏳

**⚠️ DEADLINE: 1 WEEK**

1. **Run final experiments with full dataset** (needs to be done FIRST)
   - **Main branch**: Run `./run_full_pipeline.sh` with larger samples (20k-50k patients)
   - **Multidim-fairness branch** (recommended): Run `scripts/run_multidim_sweep.py` with full data
2. **Results section** - Insert figures, tables, interpret findings
3. **Discussion section** - Policy implications, trade-offs, when to use each policy
4. **Methods section** - Expand algorithm details, parameter choices
5. **Background section** - Literature review, related work, cite SRTR/OPTN
6. **Introduction** - Expand motivation and contributions
7. **Experiments section** - Document parameters and setup used
8. **Data & Simulation section** - Describe data generation process
9. **Limitations & Ethics** - Synthetic data limits, fairness definitions, non-deployability
10. **Team Contributions** - Each person writes their paragraph
11. **Final compilation & proofread** - Compile LaTeX, check figures, proofread

**Time estimate:** ~18-20 hours total ÷ 6 people = **~3-4 hours per person**

**🚨 Critical:** Someone must run final experiments first - everything else depends on having actual results!

---

## 🆘 Troubleshooting

**`ModuleNotFoundError: policy_baselines`** → Set `export PYTHONPATH=$(pwd):$PYTHONPATH`

**`FileNotFoundError: data/patients.csv`** → Ensure you're in project root and data files exist

**Plots don't show fairness differences** → Verify grouping column has multiple values and η > 0

**LaTeX won't compile** → Install texlive or use Overleaf; check figure paths and citations

---

## 📚 Citation & License

### Citing This Work

```bibtex
@misc{kidney-allocation-fairness-2025,
  title={AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness},
  author={Barnouw, Natalie and Joseph, Olivia and Tubbs, Ella and 
          Liu, Jessie and Harper, Kathryn and Siwek, Natalia},
  year={2025},
  institution={MIT and Harvard University},
  url={https://github.com/kharper2/kidney-allocation-fairness-}
}
```

### Data Sources

- Synthetic cohorts based on SRTR and OPTN data structures
- SRTR: https://www.srtr.org/
- OPTN: https://optn.transplant.hrsa.gov/

### License

**Educational use only.** Not for clinical deployment.

---

**Get started**: Run `./run_full_pipeline.sh` and focus on writing the paper!
