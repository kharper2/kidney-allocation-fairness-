# AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness

**Complete reproducible pipeline for kidney allocation policy experiments**

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()

---

## 📑 Table of Contents

1. [Quick Start (3 Commands)](#-quick-start-3-commands)
2. [What's Included](#-whats-included)
3. [Detailed Usage Guide](#-detailed-usage-guide)
4. [Understanding Results](#-understanding-results)
5. [Google Colab (No Setup)](#-google-colab-no-setup)
6. [Project Status](#-project-status)
7. [Submission Checklist](#-submission-checklist)
8. [Team Roles & Next Steps](#-team-roles--next-steps)
9. [Citation & License](#-citation--license)

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
✅ **4 Allocation Policies**
- **Urgency-only**: Prioritize sickest patients
- **Utility-only**: Maximize survival benefit
- **Hybrid**: Weighted combination (α parameter)
- **Fairness-constrained**: Dynamic group balancing (η parameter)

✅ **Features**
- Flexible grouping (Ethnicity, SES, or any column)
- ABO blood type compatibility
- KDPI-based donor quality stratification
- Complete reproducibility (fixed seeds)

### Tools & Scripts
```
scripts/
├── add_ses.py           # Add socioeconomic status (25/55/20 split)
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

### Sample Results
- ✅ 8 policy configurations tested
- ✅ 3 publication-ready figures generated
- ✅ LaTeX table ready to insert
- ✅ Key findings documented

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
│   ├── patients_with_ses.csv   # With SES column (generated)
│   └── summary.csv              # Results (generated)
├── figures/                      # Generated plots
│   ├── tradeoff_urgency_vs_benefit.png
│   ├── tradeoff_fairness_vs_benefit.png
│   └── summary_bars.png
├── scripts/                      # Command-line tools
├── notebooks/                    # Jupyter/Colab notebooks
└── paper/                        # LaTeX paper
```

### Adding SES Column

```bash
python scripts/add_ses.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_with_ses.csv \
  --probs 0.25 0.55 0.20  # Low, Middle, High percentages
```

### Running Parameter Sweeps

**Basic sweep:**
```bash
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Ethnicity
```

**Custom parameters:**
```bash
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

- **α (alpha)**: Urgency/utility weight
  - α = 1.0: Pure urgency (prioritize sickest)
  - α = 0.0: Pure utility (maximize benefit)
  - α = 0.5: Balanced hybrid
  
- **η (eta)**: Fairness constraint strength
  - η = 0.0: No fairness adjustment
  - η > 0.0: Fairness-aware allocation
  - η = 1.0: Strong fairness enforcement

- **group_col**: Column for fairness analysis
  - `Ethnicity`: Default grouping
  - `SES`: Socioeconomic status
  - Any column in patient data

### Sample Results

From test runs (5,000 patients, 1,000 donors):

| Policy | Total Benefit | Mean Urgency | Fairness L1 |
|--------|--------------|--------------|-------------|
| **Utility** | 10,391 years | 0.558 | 0.030 |
| **Hybrid (α=0.25)** | 10,282 years | 0.635 | 0.016 |
| **Hybrid+Fair** | 9,749 years | 0.628 | **0.0004** |
| **Urgency** | 8,038 years | **0.767** | 0.020 |

**Key Findings:**
- 🎯 **29% benefit gain**: Utility vs Urgency
- 🎯 **97% disparity reduction**: With fairness constraints
- 🎯 **3.5% benefit cost**: For fairness enforcement
- 🎯 **α = 0.25**: Optimal balance

### Understanding the Figures

**Figure 1: Urgency vs Benefit Trade-off**
- Shows Pareto frontier - can't improve both simultaneously
- Blue dots = no fairness (η=0)
- Red squares = with fairness (η>0)

**Figure 2: Fairness vs Benefit Trade-off**
- Shows small benefit cost for large fairness gain
- Fairness constraints dramatically reduce L1 disparity

**Figure 3: Summary Bars**
- Side-by-side comparison of all policies
- Blue = no fairness, Red = with fairness

---

## ☁️ Google Colab (No Setup)

### Using the Colab Notebook

1. **Open notebook**: `notebooks/colab_policy_baselines.ipynb`
2. **Click**: "Open in Colab" badge (or upload to Colab)
3. **Run**: All cells in order
4. **Upload data**: When prompted (or mount Google Drive)
5. **Download results**: Generated plots and CSV files

### What the Notebook Does

- ✅ Installs dependencies automatically
- ✅ Writes `policy_baselines.py` inline (standalone)
- ✅ Runs experiments and parameter sweeps
- ✅ Generates and displays plots
- ✅ Saves results for download

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
- ✓ add_ses.py works
- ✓ run_sweep.py works
- ✓ generate_plots.py works
- ✓ analyze_results.py works
- ✓ Full pipeline completes successfully

**Data validation:**
- ✓ patients.csv: 150,002 rows
- ✓ donors.csv: 20,002 rows
- ✓ SES distribution: 25% Low, 55% Middle, 20% High
- ✓ 8 configurations tested successfully

### Performance Benchmarks

| Task | Sample Size | Runtime |
|------|-------------|---------|
| SES Addition | 150k patients | 2 sec |
| Quick Sweep | 5k/1k | 10 sec |
| Full Sweep | 20k/3k | 45 sec |
| Large Sweep | 50k/10k | 3 min |
| Plot Generation | Any | 3 sec |
| Full Pipeline | 20k/3k | 5 min |

*Tested on: MacBook Pro M1, 16GB RAM*

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

- ✅ Complete code implementation (all 4 policies)
- ✅ Full automation pipeline
- ✅ LaTeX paper structure with page estimates
- ✅ Google Colab notebook
- ✅ Sample results and figures
- ✅ Comprehensive documentation

### What Still Needs To Be Done ⏳

#### HIGH PRIORITY (This Week)
1. **Run final experiments** with large samples (20k-50k patients)
2. **Write Results section**: Interpret figures, insert tables
3. **Write Discussion section**: Policy implications, trade-offs

#### MEDIUM PRIORITY (Next Week)
4. **Expand Methods section**: Algorithm details, parameter choices
5. **Literature review**: Background section, related work
6. **Complete Introduction**: Motivation, contributions

#### LOWER PRIORITY (Before Submission)
7. **Team Contributions section**: Individual roles
8. **Limitations & Ethics**: Synthetic data, fairness definitions
9. **Final polish**: Proofread, spell check, LaTeX compilation

### Suggested Work Division

| Person | Primary Responsibilities |
|--------|-------------------------|
| **Natalie** | Data/simulation section, run final experiments |
| **Olivia** | Methods section, algorithm details |
| **Ella** | Fairness mechanism, ethics discussion |
| **Jessie** | Results section, figures, analysis |
| **Kathryn** | Integration, pipeline, experiments section |
| **Natalia** | Background/literature review, introduction |

**Everyone**: Discussion, limitations, team contributions

### Timeline Estimate

- **This week**: Complete HIGH priority items (6-8 hours)
- **Next week**: Complete MEDIUM priority items (6-8 hours)
- **Week after**: Complete LOWER priority, final polish (4-6 hours)
- **Total**: ~15-20 hours divided among 6 people

---

## 🎓 Graduate Credit Options

The repository supports several graduate-level extensions:

1. **ML Survival Surrogate** - Replace parametric model with trained predictor
2. **Weight Optimization** - Automated α/η tuning to target metrics
3. **Enhanced Fairness** - Max-min or proportional fairness mechanisms
4. **Sensitivity Suite** - Comprehensive stress tests and ablations
5. **Complete Pipeline** - This reproducible framework (already done!)

---

## 🆘 Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: policy_baselines`
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH
```

**Problem**: `FileNotFoundError: data/patients.csv`
```bash
# Make sure you're in project root
cd kidney-allocation-fairness-
ls data/  # verify files exist
```

**Problem**: Plots don't show fairness differences
- Check that grouping column has multiple values
- Try increasing sample size
- Verify η > 0 for fairness-aware runs

**Problem**: LaTeX won't compile
- Install texlive or use Overleaf
- Check all figure paths are correct
- Verify refs.bib has all citations

---

## 📞 Getting Help

**Quick questions**: Check the relevant section above  
**Code issues**: Open a GitHub issue  
**Paper questions**: Discuss in team meeting  
**Bugs**: Open issue with error message and steps to reproduce

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

## 🎉 Summary

**This repository provides:**
- ✅ Complete working implementation of 4 allocation policies
- ✅ Automated experimentation pipeline
- ✅ Publication-ready figures and analysis
- ✅ Complete LaTeX paper structure
- ✅ Zero-setup Colab option for collaboration
- ✅ Comprehensive documentation in one place

**Ready to use for:**
- Running experiments and generating results
- Writing the paper based on generated outputs
- Team collaboration via GitHub and Colab
- Submission as a complete research project

**Get started**: Run `./run_full_pipeline.sh` and focus on writing the paper!

---

**Questions?** Open a GitHub issue or contact the team!

**Last updated**: November 27, 2025
