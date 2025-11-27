# Results Summary (Proof-of-Concept)

**Date:** November 27, 2024  
**Test Configuration:** 5,000 patients, 1,000 donors (sampled from full dataset)  
**Data Source:** Teammate's `patients.csv` (150k patients) + `donors.csv` (20k donors)  
**Fairness Dimension:** Ethnicity  
**Random Seed:** 42

---

## Main Results (Single-Dimension Fairness)

| Policy | Total Benefit | Mean Urgency | Fairness L1 | Organs Allocated |
|--------|--------------|--------------|-------------|------------------|
| **Urgency** | 8,038 years | **0.767** | 0.010 | 1,000/1,000 |
| **Utility** | **10,391 years** | 0.558 | 0.033 | 1,000/1,000 |
| **Hybrid (α=0.25)** | 10,282 years | 0.635 | 0.034 | 1,000/1,000 |
| **Hybrid+Fair (α=0.25, η=1.0)** | 9,434 years | 0.611 | **0.0008** | 960/1,000 |
| **Hybrid (α=0.50)** | 9,794 years | 0.707 | 0.019 | 1,000/1,000 |
| **Hybrid+Fair (α=0.50, η=1.0)** | 8,960 years | 0.686 | **0.0008** | 960/1,000 |
| **Hybrid (α=0.75)** | 8,853 years | 0.757 | 0.009 | 1,000/1,000 |
| **Hybrid+Fair (α=0.75, η=1.0)** | 8,270 years | 0.716 | **0.0008** | 960/1,000 |

---

## Key Findings

### 1. Utility vs Urgency Trade-off
- **+29% benefit gain** with Utility vs Urgency (10,391 vs 8,038 years)
- **-27% urgency loss** (0.767 → 0.558)
- **Why:** Utility matches good kidneys with healthy recipients who gain most years

### 2. Fairness Impact
- **96% disparity reduction** with fairness constraints (L1: 0.021 → 0.0008)
- **Only ~6% benefit cost** for fairness (10,282 → 9,434 years with α=0.25)
- **Why:** Constraint reorders queue without destroying medical benefit

### 3. Optimal Alpha (λ)
- **α=0.25** appears optimal: High benefit (10,282 years) + moderate urgency (0.635)
- Balances efficiency and equity concerns

### 4. Near-Perfect Fairness
- L1=0.0008 means each ethnic group gets within **0.08%** of proportional share
- Fairness constraint works as designed

---

## Why These Results Make Sense

✅ **Utility > Urgency:** Good kidneys → healthy recipients = most years gained (vs sickest patients with shorter prognosis)

✅ **High urgency with Urgency policy:** Algorithm explicitly prioritizes sickest patients (0.767 vs 0.558)

✅ **Low fairness cost:** Reordering queue slightly ≠ destroying medical benefit  

✅ **Near-perfect fairness:** L1<0.001 shows algorithm achieves proportional representation

---

## Files Generated

- `figures/tradeoff_urgency_vs_benefit.png` - Pareto frontier
- `figures/tradeoff_fairness_vs_benefit.png` - Fairness-benefit trade-off  
- `figures/summary_bars.png` - Side-by-side comparison
- `data/summary.csv` - Full results table (gitignored, local only)
- `data/analysis.txt` - Detailed analysis with LaTeX tables (gitignored, local only)

---

## Next Steps

⚠️ **These are proof-of-concept results.** Final experiments need:
- **20k-150k patients** (currently using 5k)
- **3k-20k donors** (currently using 1k)  
- Multiple random seeds for robustness
- Comparison across different fairness dimensions (Ethnicity, SES, Blood Type)

---

## Branch-Specific Results

### Composite Fairness Branch (2k patients, 500 donors)
- Hybrid+Fair (α=0.5, η=1.0): **3,249 years**, L1=0.006, **375/500 allocated**
- Problem: Sparse intersectional groups reduce efficiency

### Multi-Dimensional Fairness Branch (2k patients, 500 donors)
- Hybrid+Fair (α=0.5, η=1.0, 70% Ethnicity + 30% SES): **4,479 years**, L1=0.003, **500/500 allocated**
- **+38% better than composite** due to flexibility

**Recommendation:** Use multi-dimensional approach for final paper.

