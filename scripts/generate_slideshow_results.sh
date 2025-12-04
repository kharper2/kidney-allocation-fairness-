#!/bin/bash
# Generate all results and graphs for slideshow presentation
# Run from project root: bash scripts/generate_slideshow_results.sh

set -e  # Exit on error

echo "======================================"
echo "Generating Slideshow Results"
echo "======================================"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH=$(pwd):$PYTHONPATH

# Create directories
mkdir -p figures/slideshow
mkdir -p data/slideshow

echo "Step 1: Main branch - Sex fairness (best result)"
echo "----------------------------------------"
git checkout main
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --sample_patients 5000 \
  --sample_donors 1000 \
  --group_col Sex \
  --seed 42
python scripts/generate_plots.py --summary data/summary.csv --outdir figures/slideshow/main_sex
cp data/summary.csv data/slideshow/main_sex.csv
echo "✅ Main (Sex) complete"
echo ""

echo "Step 2: Main branch - Ethnicity fairness (baseline)"
echo "----------------------------------------"
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --sample_patients 5000 \
  --sample_donors 1000 \
  --group_col Ethnicity \
  --seed 42
python scripts/generate_plots.py --summary data/summary.csv --outdir figures/slideshow/main_ethnicity
cp data/summary.csv data/slideshow/main_ethnicity.csv
echo "✅ Main (Ethnicity) complete"
echo ""

echo "Step 3: Composite-fairness branch"
echo "----------------------------------------"
git checkout composite-fairness
# Create composite groups
python scripts/add_composite_groups.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_composite.csv \
  --columns Ethnicity DistancetoCenterMiles
# Run sweep
python scripts/run_sweep.py \
  --patients data/patients_composite.csv \
  --donors data/donors.csv \
  --sample_patients 5000 \
  --sample_donors 1000 \
  --group_col Ethnicity_DistancetoCenterMiles \
  --seed 42
python scripts/generate_plots.py --summary data/summary.csv --outdir figures/slideshow/composite
cp data/summary.csv data/slideshow/composite.csv
echo "✅ Composite complete"
echo ""

echo "Step 4: Multidim-fairness branch"
echo "----------------------------------------"
git checkout multidim-fairness
python scripts/run_multidim_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --sample_patients 5000 \
  --sample_donors 1000 \
  --fairness_dims Ethnicity DistancetoCenterMiles \
  --fairness_weights 0.7 0.3 \
  --alphas 0.25 0.5 0.75 \
  --etas 0 1.0 \
  --seed 42
python scripts/generate_plots.py --summary data/summary.csv --outdir figures/slideshow/multidim
cp data/summary.csv data/slideshow/multidim.csv
echo "✅ Multidim complete"
echo ""

echo "Step 5: Generate comparison graph"
echo "----------------------------------------"
python scripts/generate_comparison_graph.py \
  --main_sex data/slideshow/main_sex.csv \
  --main_ethnicity data/slideshow/main_ethnicity.csv \
  --composite data/slideshow/composite.csv \
  --multidim data/slideshow/multidim.csv \
  --outdir figures/slideshow

echo ""
echo "======================================"
echo "✅ All results generated!"
echo "======================================"
echo ""
echo "Results saved in:"
echo "  - figures/slideshow/ (all graphs)"
echo "  - data/slideshow/ (all summary CSVs)"
echo ""
echo "Switch back to main branch:"
echo "  git checkout main"
echo ""

