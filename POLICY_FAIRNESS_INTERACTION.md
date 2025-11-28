# How Allocation Policies Interact with Fairness Approaches

📋 **See [`README.md`](README.md) for quick start guide and overview**  
📋 **See [`BRANCHES.md`](BRANCHES.md) for detailed branch comparison and results**

---

## Overview

**4 Allocation Policies** (determine HOW to rank patients):
1. **Urgency-only** - Prioritize sickest patients
2. **Utility-only** - Maximize survival benefit
3. **Hybrid** - Weighted combination of urgency + utility
4. **Hybrid+Fair** - Hybrid + fairness constraint

**3 Fairness Approaches** (determine HOW to implement fairness):
1. **Single-dimension** (`main` branch) - Balance one demographic at a time
2. **Composite groups** (`composite-fairness` branch) - Balance intersectional groups
3. **Multi-dimensional** (`multidim-fairness` branch) - Balance multiple dimensions with weights

---

## The Two-Layer System

### Layer 1: Base Allocation Policy (Scoring/Ranking)

**What it does:** Determines the **initial ranking** of patients

```
Policy = 'urgency' → Rank by: Urgency score (sickest first)
Policy = 'utility' → Rank by: Survival benefit (highest first)  
Policy = 'hybrid' → Rank by: α × Urgency + (1-α) × Utility
```

**This happens BEFORE fairness is applied.**

### Layer 2: Fairness Constraint (Reordering)

**What it does:** Modifies the ranking to balance demographic groups

```
fairness_eta = 0.0 → No fairness (use base policy ranking as-is)
fairness_eta > 0.0 → Apply fairness constraint (reorder to balance groups)
```

**The fairness constraint implementation differs across branches:**
- **Main branch:** Balance one dimension (Ethnicity, DistancetoCenterMiles, or Sex - SRTR data)
- **Composite branch:** Balance 25 intersectional groups (Ethnicity × Distance)
- **Multidim branch:** Balance multiple dimensions with weights

---

## How They Combine

### Example: Hybrid Policy + Single-Dimension Fairness

**Step 1: Base Ranking (Hybrid Policy)**
```
Patient A: Urgency=0.8, Utility=0.6 → Score = 0.5×0.8 + 0.5×0.6 = 0.70
Patient B: Urgency=0.7, Utility=0.7 → Score = 0.5×0.7 + 0.5×0.7 = 0.70
Patient C: Urgency=0.6, Utility=0.8 → Score = 0.5×0.6 + 0.5×0.8 = 0.70
```
All three have same score → tie broken by urgency (A > B > C)

**Step 2: Fairness Constraint Applied**
```
Current allocations: 60% White, 40% Black (waitlist is 50/50)
Patient A: White → deficit = -10% (overrepresented)
Patient B: Black → deficit = +10% (underrepresented)
Patient C: White → deficit = -10% (overrepresented)
```
**Result:** Algorithm picks Patient B (Black) even though A has higher urgency, because fairness constraint prioritizes underrepresented group.

---

## Complete Interaction Matrix

### Main Branch (Single-Dimension Fairness)

| Base Policy | Fairness η=0 | Fairness η=1.0 |
|-------------|--------------|-----------------|
| **Urgency** | Rank by urgency only | Urgency ranking + balance Ethnicity |
| **Utility** | Rank by utility only | Utility ranking + balance Ethnicity |
| **Hybrid (α=0.5)** | Rank by 50% urgency + 50% utility | Hybrid ranking + balance Ethnicity |
| **Hybrid+Fair** | Same as Hybrid | Same as Hybrid (η=1.0) |

**Note:** "Hybrid+Fair" is just shorthand for Hybrid policy with η=1.0

### Composite Branch (Intersectional Groups)

| Base Policy | Fairness η=0 | Fairness η=1.0 |
|-------------|--------------|-----------------|
| **Urgency** | Rank by urgency only | Urgency ranking + balance 15 composite groups |
| **Utility** | Rank by utility only | Utility ranking + balance 15 composite groups |
| **Hybrid (α=0.5)** | Rank by 50% urgency + 50% utility | Hybrid ranking + balance 15 composite groups |
| **Hybrid+Fair** | Same as Hybrid | Same as Hybrid (η=1.0) |

**Difference:** Fairness constraint balances across 25 intersectional groups (Black_<50, White_>250, etc.) instead of 5 ethnicity groups.

### Multidim Branch (Weighted Multi-Dimensional)

| Base Policy | Fairness η=0 | Fairness η=1.0 |
|-------------|--------------|-----------------|
| **Urgency** | Rank by urgency only | Urgency ranking + balance Ethnicity (70%) + Distance (30%) |
| **Utility** | Rank by utility only | Utility ranking + balance Ethnicity (70%) + Distance (30%) |
| **Hybrid (α=0.5)** | Rank by 50% urgency + 50% utility | Hybrid ranking + balance Ethnicity (70%) + Distance (30%) |
| **Hybrid+Fair** | Same as Hybrid | Same as Hybrid (η=1.0) |

**Difference:** Fairness constraint balances across BOTH dimensions simultaneously with configurable weights.

---

## What We Actually Test

**9 configurations per branch:**
- 3 baselines: Urgency (α=1.0, η=0), Wait-Time (α=1.0, η=0), Utility (α=0.0, η=0)
- 6 Hybrid: Grid search over α ∈ {0.25, 0.5, 0.75} × η ∈ {0.0, 1.0}

**Difference across branches:** Fairness constraint balances different groups (5 ethnicity vs 25 composite vs 10 independent groups for multidim)

---

## Why We Focus on Hybrid+Fair

**Baseline policies (η=0):** Urgency prioritizes sickest, Utility maximizes benefit - no fairness  
**Hybrid (η=0):** Balances urgency and utility - no fairness  
**Hybrid+Fair (η=1.0):** ⭐ Balances urgency, utility, AND fairness - **only ~6-8% benefit cost for near-perfect fairness**

---

## Key Insight: Fairness is a Modifier

**Base Policy** = Medical ranking (urgency, utility, or hybrid)  
**Fairness** = Reorders queue to balance demographics (single-dim, composite, or multidim)  
**Result:** Base policy ranks, fairness reorders - doesn't change medical priorities, just ensures demographic balance

---

## Example: How Hybrid+Fair Works

**Step 1: Base Policy ranks** by 0.5 × Urgency + 0.5 × Utility  
**Step 2: Fairness reorders** - prioritizes underrepresented groups  
**Result:** Patient B (Black, >250 miles) selected even if tied with others, because fairness constraint prioritizes underrepresented groups

---

## Summary Table

| Base Policy | Fairness Approach | What Gets Balanced | Result Quality |
|-------------|------------------|-------------------|----------------|
| Urgency | Single-dim | 5 ethnicity groups | High urgency, low benefit |
| Utility | Single-dim | 5 ethnicity groups | High benefit, low urgency |
| Hybrid | Single-dim | 5 ethnicity groups | Balanced, good fairness |
| Hybrid | Composite | 25 intersectional groups | Lower benefit (sparse groups, 25% organs wasted) |
| Hybrid | Multidim | 5 ethnicities + 5 distance categories (weighted) | **Excellent: Good fairness + high benefit** ⭐ |

---

## Summary

**4 policies** determine medical priorities (urgency, utility, hybrid, or wait-time).  
**3 fairness approaches** determine demographic balancing (single-dim, composite, multidim).  
**They work together:** Base policy ranks patients, fairness reorders to balance groups.

**Tested results:** Single-dimension (Sex) performs best (9,512 years), multidim balances multiple dimensions well (9,501 years), composite struggles with sparse groups (6,479 years).

