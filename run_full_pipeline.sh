#!/bin/bash
# Full pipeline for kidney allocation experiments
# Run from project root: ./run_full_pipeline.sh

set -e  # Exit on error

echo "======================================"
echo "Kidney Allocation Policy Pipeline"
echo "======================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if patients.csv exists
if [ ! -f "data/patients.csv" ]; then
    echo "ERROR: data/patients.csv not found!"
    echo "Please add your patient data file to the data/ directory."
    exit 1
fi

# Check if donors.csv exists
if [ ! -f "data/donors.csv" ]; then
    echo "ERROR: data/donors.csv not found!"
    echo "Please add your donor data file to the data/ directory."
    exit 1
fi

echo ""
echo "Step 1: Adding SES column to patient data..."
python scripts/add_ses.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_with_ses.csv

echo ""
echo "Step 2: Running parameter sweep (Ethnicity)..."
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --sample_patients 20000 \
  --sample_donors 3000 \
  --alphas 0.25 0.5 0.75 \
  --etas 0 1.0 \
  --group_col Ethnicity

# Save Ethnicity results
mv data/summary.csv data/summary_ethnicity.csv
echo "Saved: data/summary_ethnicity.csv"

echo ""
echo "Step 3: Running parameter sweep (SES)..."
python scripts/run_sweep.py \
  --patients data/patients_with_ses.csv \
  --donors data/donors.csv \
  --sample_patients 20000 \
  --sample_donors 3000 \
  --alphas 0.25 0.5 0.75 \
  --etas 0 0.5 1.0 \
  --group_col SES

# Save SES results
mv data/summary.csv data/summary_ses.csv
echo "Saved: data/summary_ses.csv"

echo ""
echo "Step 4: Generating plots for Ethnicity..."
python scripts/generate_plots.py \
  --summary data/summary_ethnicity.csv \
  --outdir figures/ethnicity

echo ""
echo "Step 5: Generating plots for SES..."
python scripts/generate_plots.py \
  --summary data/summary_ses.csv \
  --outdir figures/ses

echo ""
echo "======================================"
echo "Pipeline complete!"
echo "======================================"
echo ""
echo "Results:"
echo "  - data/summary_ethnicity.csv"
echo "  - data/summary_ses.csv"
echo "  - figures/ethnicity/*.png"
echo "  - figures/ses/*.png"
echo ""
echo "Next steps:"
echo "  1. Review plots in figures/ directories"
echo "  2. Update paper/main.tex with insights"
echo "  3. Compile LaTeX: cd paper && pdflatex main.tex"
echo ""

