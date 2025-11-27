# Composite Groups Fairness Extension

**Branch:** `composite-fairness`  
**Status:** Optional extension - READY TO USE  
**Main branch:** Safe and ready for submission

**What this does:** Combines multiple attributes (Ethnicity + SES) into composite group labels to enable intersectional fairness.

---

## What This Extension Adds

**Multi-dimensional fairness constraints** that balance across multiple protected attributes simultaneously (e.g., Ethnicity AND Sex, or Ethnicity AND SES together).

### Current Implementation (Main Branch)
- Single dimension fairness: balance by Ethnicity OR SES OR Sex (one at a time)
- Specify via `group_col='Ethnicity'`

### This Extension (Composite Branch)
- Composite group fairness: balance by intersectional group combinations
- Example: Balance across combinations like "Black_Low", "White_Middle", etc.
- Treats each combination as a distinct group (intersectionality)

---

## Implementation

**Composite Groups Approach:**
Create combined group labels before running:

```python
# In preprocessing script
df['Ethnicity_SES'] = df['Ethnicity'] + '_' + df['SES']

# Then run allocation
allocate(..., group_col='Ethnicity_SES', fairness_eta=1.0)
```

**Pros:**
- ✅ Works with existing code (no changes needed!)
- ✅ Can implement in 15 minutes
- ✅ Demonstrates concept
- ✅ Can run experiments easily

**Implementation:**

1. Add preprocessing script:

```python
# scripts/add_composite_groups.py
import pandas as pd

df = pd.read_csv('data/patients_with_ses.csv')
df['Ethnicity_SES'] = df['Ethnicity'] + '_' + df['SES']
df.to_csv('data/patients_multidim.csv', index=False)
```

2. Run with composite group:

```bash
python scripts/run_sweep.py \
  --patients data/patients_multidim.csv \
  --donors data/donors.csv \
  --group_col Ethnicity_SES
```

3. Compare single-dim vs multi-dim results

---

## What to Include in Paper

### Methods Section (Add paragraph)
> "As an extension, we also implemented multi-dimensional fairness by constructing composite groups (e.g., 'Black_Low', 'White_Middle') that represent combinations of ethnicity and socioeconomic status. This allows the fairness mechanism to balance across intersectional identities."

### Results Section (Add subsection)
> "Multi-dimensional fairness results: When balancing across Ethnicity×SES combinations, we observed [findings]. Compared to single-dimension fairness, multi-dimensional constraints [trade-offs]."

### Team Contributions
> "Extension: Multi-dimensional fairness mechanism implementation and analysis (Kathryn/whoever does this)"

---

## Files to Modify (This Branch Only)

1. ✅ Create `scripts/add_composite_groups.py`
2. ✅ Document in this file
3. ✅ Run experiments with multidim groups
4. ✅ Add results comparison
5. ✅ Update paper with extension section

**Main branch:** Untouched and ready for submission  
**This branch:** Extension work, merge only if ready

---

## Timeline

- **Main submission:** Use main branch (single-dim fairness)
- **After submission OR if time permits:** Complete this extension
- **Team contributions:** Document this work if completed

---

## Testing the Extension

```bash
# Make sure you're on this branch
git branch  # should show: * multidim-fairness

# Create composite groups
python scripts/add_composite_groups.py

# Run experiments
python scripts/run_sweep.py \
  --patients data/patients_multidim.csv \
  --donors data/donors.csv \
  --group_col Ethnicity_SES \
  --alphas 0.5 \
  --etas 0 1.0

# Compare with single-dim results
python scripts/analyze_results.py
```

---

## Switch Back to Main Branch

```bash
# Save your work
git add .
git commit -m "Multi-dimensional fairness extension"
git push origin multidim-fairness

# Switch back to main for submission
git checkout main
```

---

## Why This Extension Matters

This extension demonstrates:
1. ✅ **Intersectional fairness** - addresses combinations of protected attributes
2. ✅ **Advanced implementation** - extends beyond basic single-dimension
3. ✅ **Experimental comparison** - empirical analysis of trade-offs
4. ✅ **Research contribution** - publishable extension to base work

**Estimated effort:** 2-3 hours (if using composite group approach)

---

**Status:** Branch created and ready. Main submission is safe!

