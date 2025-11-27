# Composite Fairness Results

**Branch:** `composite-fairness`  
**Date:** November 27, 2024  
**Test Configuration:** 5,000 patients, 1,000 donors (sampled from full dataset)  
**Fairness Approach:** Composite groups (Ethnicity × SES = 15 groups)  
**Random Seed:** 42

---

## Results

| Policy | Total Benefit | Mean Urgency | Fairness L1 | Organs Allocated |
|--------|--------------|--------------|-------------|------------------|
| **Urgency** | 8,038 years | **0.767** | 0.028 | 1,000/1,000 |
| **Utility** | **10,391 years** | 0.558 | 0.055 | 1,000/1,000 |
| **Hybrid (α=0.25)** | 10,282 years | 0.635 | 0.043 | 1,000/1,000 |
| **Hybrid+Fair (α=0.25, η=1.0)** | 8,266 years | 0.565 | **0.002** | **921/1,000** ⚠️ |
| **Hybrid (α=0.50)** | 9,794 years | 0.707 | 0.033 | 1,000/1,000 |
| **Hybrid+Fair (α=0.50, η=1.0)** | 7,708 years | 0.611 | **0.002** | **897/1,000** ⚠️ |
| **Hybrid (α=0.75)** | 8,853 years | 0.757 | 0.017 | 1,000/1,000 |
| **Hybrid+Fair (α=0.75, η=1.0)** | 7,232 years | 0.611 | **0.003** | **872/1,000** ⚠️ |

---

## Composite Groups Created

15 intersectional groups (Ethnicity × SES):

| Group | Count | Percentage |
|-------|-------|------------|
| Black_Middle | 26,227 | 17.5% |
| White_Middle | 29,664 | 19.8% |
| Hispanic_Middle | 17,195 | 11.5% |
| White_Low | 13,303 | 8.9% |
| Black_Low | 12,228 | 8.2% |
| White_High | 10,732 | 7.2% |
| Black_High | 9,645 | 6.4% |
| Asian_Middle | 7,929 | 5.3% |
| Hispanic_Low | 7,651 | 5.1% |
| Hispanic_High | 6,149 | 4.1% |
| Asian_Low | 3,677 | 2.5% |
| Asian_High | 2,864 | 1.9% |
| Other_Middle | 1,547 | 1.0% |
| Other_Low | 662 | 0.4% |
| Other_High | 527 | 0.4% |

**Problem:** "Other" groups are very small (<1%), making matches difficult.

---

## Key Findings

### 1. Fairness Performance
- **Excellent fairness:** L1 = 0.002-0.003 (each group within 0.2-0.3% of proportional share)
- Successfully balances across all 15 intersectional groups

### 2. Efficiency Problem ⚠️
- **~10% organs unused** with fairness constraints (872-921 allocated vs 1,000)
- **21-25% benefit loss** compared to non-fairness hybrid (α=0.5: 9,794 → 7,708 years = -21%)
- **Why:** When fairness requires allocation to tiny group with no compatible match → organ wasted

### 3. Comparison to Main Branch (Single-Dimension)
- **Main branch Hybrid+Fair (α=0.5):** 8,960 years, 960/1,000 allocated
- **Composite Hybrid+Fair (α=0.5):** 7,708 years, 897/1,000 allocated  
- **Composite is 14% worse** due to sparse groups

---

## Why Composite Has Lower Benefit

### The Sparse Group Problem

**Example scenario:**
1. Donor arrives: Blood Type AB, KDPI=20 (good kidney)
2. Fairness constraint activates: "Other_Low" group is underrepresented
3. Problem: Only 662 "Other_Low" patients total, none are Type AB compatible
4. Result: **Kidney goes unused** or algorithm forced to pick very suboptimal match

### Mathematical Issue
- 15 groups → average 6.7% per group
- Smallest groups < 0.5% of population
- With blood type constraint (8 types × 15 groups = 120 possible combinations!)
- Many combinations have **zero or very few patients**

---

## Comparison to Multi-Dimensional Approach

The multi-dimensional approach tracks 5 ethnicities + 3 SES = 8 groups (not 15) and combines deficits with weights. This avoids the sparse group problem while still achieving fairness across both dimensions.

**Expected next:** Run multi-dimensional branch for direct comparison.

---

## Files Generated

- `figures/tradeoff_urgency_vs_benefit.png` - Updated
- `figures/tradeoff_fairness_vs_benefit.png` - Updated
- `figures/summary_bars.png` - Updated

---

## Recommendation

Composite fairness achieves excellent intersectional fairness (L1<0.003) but at **significant efficiency cost** (~20-25% benefit loss, 10% organs wasted). This demonstrates the trade-off between strict intersectionality and practical outcomes.

For the paper, this serves as an important comparison point showing why flexibility (multi-dimensional) matters.

