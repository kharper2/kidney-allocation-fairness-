# Submission Checklist

## Pre-Submission: Code & Experiments ✓

### Environment Setup
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Data files in place (`data/patients.csv`, `data/donors.csv`)
- [ ] PYTHONPATH configured if needed

### Data Preparation
- [ ] SES column added to patient data (if analyzing by SES)
- [ ] Data quality verified (no missing critical values)
- [ ] Sample sizes decided (recommend: 20k patients, 3k donors minimum)

### Experiments Run
- [ ] Baseline sweep completed (Ethnicity)
- [ ] SES sweep completed (if applicable)
- [ ] Parameter grid explored:
  - [ ] α (lambda) values: 0.0, 0.25, 0.5, 0.75, 1.0 (minimum)
  - [ ] η (eta) values: 0.0, 1.0 (minimum)
- [ ] Results saved to `data/summary_*.csv`

### Figures Generated
- [ ] Urgency vs Benefit trade-off plot
- [ ] Fairness vs Benefit trade-off plot
- [ ] Summary bar charts (optional)
- [ ] All figures saved to `figures/` directory
- [ ] Figure quality checked (300 DPI, readable labels)

### Analysis Completed
- [ ] Results analysis run (`scripts/analyze_results.py`)
- [ ] LaTeX table generated
- [ ] Pareto frontier identified
- [ ] Key findings documented

## Paper Preparation ✓

### LaTeX Structure
- [ ] All sections present with page estimates
- [ ] Abstract (0.5 page) - complete and concise
- [ ] Introduction (0.5-1 page) - motivation and contributions clear
- [ ] Background (2-3 pages) - literature review thorough
- [ ] Data & Simulation (0.5-1 page) - setup described
- [ ] Methods (2-3 pages) - algorithms explained with equations
- [ ] Experiments (1-2 pages) - setup and parameters documented
- [ ] Results (1-2 pages) - plots and tables included
- [ ] Discussion (1 page) - interpretation of findings
- [ ] Limitations (0.5 page) - ethical considerations addressed
- [ ] Team Contributions (1 page) - roles clearly defined
- [ ] Conclusion (0.25 page) - summary and future work

### Figures & Tables
- [ ] Figure paths correct in LaTeX (`\includegraphics{...}`)
- [ ] Figures copied to `paper/` directory (or use `../figures/...`)
- [ ] All figures referenced in text
- [ ] Figure captions descriptive and complete
- [ ] LaTeX table from `analyze_results.py` included
- [ ] Table formatting checked

### Citations
- [ ] SRTR cited in Background
- [ ] OPTN cited in Background
- [ ] All citations in `refs.bib`
- [ ] Bibliography compiled correctly (`bibtex main`)

### Compilation
- [ ] LaTeX compiles without errors
  ```bash
  cd paper
  pdflatex main.tex
  bibtex main
  pdflatex main.tex
  pdflatex main.tex
  ```
- [ ] PDF generated successfully
- [ ] PDF reviewed for:
  - [ ] Proper page breaks
  - [ ] Figures appear correctly
  - [ ] No overlapping text/figures
  - [ ] References formatted correctly

### Content Quality
- [ ] All equations numbered and explained
- [ ] Variable notation consistent throughout
- [ ] Results match figures and tables
- [ ] Findings clearly stated with evidence
- [ ] Limitations honestly discussed
- [ ] Team contributions detailed and fair

## Code Quality ✓

### Code Organization
- [ ] All scripts in `scripts/` directory
- [ ] Main module (`policy_baselines.py`) in root
- [ ] Notebooks in `notebooks/` directory
- [ ] No temporary/test files left in repo

### Documentation
- [ ] README.md comprehensive
- [ ] USAGE_GUIDE.md helpful for team
- [ ] Code comments adequate
- [ ] Docstrings for key functions

### Reproducibility
- [ ] `requirements.txt` complete
- [ ] Random seeds fixed (default: 42)
- [ ] Instructions clear in README
- [ ] Full pipeline script works (`run_full_pipeline.sh`)

### Testing
- [ ] Basic sanity test passed:
  ```bash
  python scripts/run_sweep.py --patients data/patients.csv --donors data/donors.csv --sample_patients 1000 --sample_donors 200
  ```
- [ ] Plots generate without errors
- [ ] Analysis script runs successfully

## Colab Notebook ✓

### Functionality
- [ ] All cells run in order without errors
- [ ] Dependencies installed correctly
- [ ] `policy_baselines.py` written correctly in cell
- [ ] Upload/Drive mount options both work
- [ ] Experiments complete successfully
- [ ] Plots generated and displayed

### Documentation
- [ ] Instructions clear in markdown cells
- [ ] Expected outputs described
- [ ] Team members can run independently

### Shareability
- [ ] Notebook uploaded to Google Drive
- [ ] Sharing permissions set (team + instructor)
- [ ] Link tested in incognito mode

## Final Checks ✓

### Repository
- [ ] `.gitignore` configured
- [ ] Unnecessary files removed (e.g., `.DS_Store`, `__pycache__`)
- [ ] Large data files handled appropriately
- [ ] Repository structure clean and logical

### Results Verification
- [ ] Numbers in paper match latest experiment runs
- [ ] Figures correspond to correct data
- [ ] No placeholder text remains (e.g., "TODO", "INSERT DATA")
- [ ] Conclusions supported by evidence

### Team Coordination
- [ ] All team members reviewed materials
- [ ] Individual contributions documented
- [ ] Graduate credit components identified (if applicable)
- [ ] Everyone agrees on final submission

### Submission Materials
- [ ] PDF of paper
- [ ] Code repository (zip or GitHub link)
- [ ] Colab notebook link
- [ ] Any supplementary materials (if required)
- [ ] README with quick start instructions

## Optional Enhancements (If Time Permits)

### Advanced Analysis
- [ ] Sensitivity analysis (donor supply variations)
- [ ] Stress tests (extreme KDPI distributions)
- [ ] Statistical significance tests
- [ ] Confidence intervals for metrics

### Additional Experiments
- [ ] Fine-grained α sweep (0.0, 0.1, 0.2, ..., 1.0)
- [ ] Multiple η values (0, 0.25, 0.5, 0.75, 1.0)
- [ ] Comparison with other fairness definitions
- [ ] Cross-validation with different seeds

### Code Enhancements
- [ ] Unit tests for key functions
- [ ] Type hints throughout
- [ ] Performance profiling
- [ ] Parallel processing for large sweeps

### Paper Enhancements
- [ ] Appendix with detailed results
- [ ] Additional ablation studies
- [ ] Comparison with real-world policies (if data available)
- [ ] More sophisticated visualizations

## Pre-Submission Final Test

Run this complete test 24-48 hours before submission:

```bash
# Clean start
cd /Users/kathryn/Downloads/project_repo_skeleton
rm -rf .venv data/summary*.csv figures/*.png

# Full pipeline
./run_full_pipeline.sh

# Verify outputs
ls -la data/summary*.csv
ls -la figures/ethnicity/*.png
ls -la figures/ses/*.png

# Generate analysis
python scripts/analyze_results.py --summary data/summary_ses.csv

# Compile paper
cd paper
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
cd ..

# Test Colab (manual)
# Open notebook in fresh Colab session and run all cells
```

## Day-of-Submission Checks

- [ ] All files uploaded/submitted correctly
- [ ] PDF opens and displays properly
- [ ] Links work (Colab, GitHub, etc.)
- [ ] File sizes within limits
- [ ] Submission confirmation received
- [ ] Backup copies saved locally and in cloud

---

## Emergency Contacts

If something breaks last minute:

1. **LaTeX won't compile**: Check `.log` file, ensure all packages installed
2. **Python errors**: Verify Python 3.8+, check PYTHONPATH
3. **Missing data**: Re-download from team shared folder
4. **Colab timeout**: Use smaller sample sizes or run locally
5. **Git issues**: Use zip file backup

**Team Communication**: Use shared Slack/Discord/Email thread for quick issues

---

**Last Updated**: Run date of most recent full pipeline test: ___________

**Tested By**: ___________

**Final Approval**: All team members sign off: ☐ ☐ ☐ ☐ ☐ ☐

