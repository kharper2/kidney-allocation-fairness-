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
- **Main branch:** Balance one dimension (Ethnicity OR SES)
- **Composite branch:** Balance 15 intersectional groups
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

**Difference:** Fairness constraint balances across 15 intersectional groups (Black_Low, White_Middle, etc.) instead of 5 ethnicity groups.

### Multidim Branch (Weighted Multi-Dimensional)

| Base Policy | Fairness η=0 | Fairness η=1.0 |
|-------------|--------------|-----------------|
| **Urgency** | Rank by urgency only | Urgency ranking + balance Ethnicity (70%) + SES (30%) |
| **Utility** | Rank by utility only | Utility ranking + balance Ethnicity (70%) + SES (30%) |
| **Hybrid (α=0.5)** | Rank by 50% urgency + 50% utility | Hybrid ranking + balance Ethnicity (70%) + SES (30%) |
| **Hybrid+Fair** | Same as Hybrid | Same as Hybrid (η=1.0) |

**Difference:** Fairness constraint balances across BOTH dimensions simultaneously with configurable weights.

---

## What We Actually Test

In practice, we test these combinations:

### Main Branch Tests:
1. ✅ Urgency (η=0) - Baseline urgency-only
2. ✅ Utility (η=0) - Baseline utility-only
3. ✅ Hybrid (α=0.25, η=0) - Hybrid without fairness
4. ✅ Hybrid (α=0.50, η=0) - Hybrid without fairness
5. ✅ Hybrid (α=0.75, η=0) - Hybrid without fairness
6. ✅ Hybrid+Fair (α=0.25, η=1.0) - Hybrid with Ethnicity fairness
7. ✅ Hybrid+Fair (α=0.50, η=1.0) - Hybrid with Ethnicity fairness
8. ✅ Hybrid+Fair (α=0.75, η=1.0) - Hybrid with Ethnicity fairness

**Total: 8 configurations**

### Composite Branch Tests:
Same 8 configurations, but fairness balances 15 composite groups instead of 5 ethnicity groups.

### Multidim Branch Tests:
Same 8 configurations, but fairness balances Ethnicity (70%) + SES (30%) simultaneously.

---

## Why We Focus on Hybrid+Fair

**Most interesting combinations:**

1. **Urgency-only (η=0):** Pure medical urgency - sickest patients first
   - High urgency scores, but lower total benefit
   - No fairness consideration

2. **Utility-only (η=0):** Pure efficiency - maximize years gained
   - Highest total benefit, but lower urgency scores
   - No fairness consideration

3. **Hybrid (η=0):** Balance urgency and utility
   - Trade-off between medical need and efficiency
   - No fairness consideration

4. **Hybrid+Fair (η=1.0):** Balance urgency, utility, AND fairness ⭐
   - **This is where it gets interesting!**
   - Can we maintain good medical outcomes while achieving equity?
   - **Answer: YES!** Only ~6-8% benefit cost for near-perfect fairness

---

## Key Insight: Fairness is a Modifier

**Think of it this way:**

```
Base Policy = "What medical criteria matter?"
- Urgency: Sickness matters most
- Utility: Survival benefit matters most  
- Hybrid: Both matter (weighted)

Fairness = "How do we reorder to balance demographics?"
- Single-dim: Balance one dimension (Ethnicity OR SES)
- Composite: Balance intersectional groups
- Multidim: Balance multiple dimensions with weights
```

**The fairness constraint doesn't change the base policy - it just reorders the queue to ensure demographic balance.**

---

## Example: How Hybrid+Fair Works

**Scenario:** Donor arrives, need to pick recipient

**Step 1: Base Policy (Hybrid, α=0.5)**
```
Rank patients by: 0.5 × Urgency + 0.5 × Utility

Top 3 candidates:
1. Patient A: Urgency=0.8, Utility=0.7 → Score = 0.75 (White, High-SES)
2. Patient B: Urgency=0.7, Utility=0.8 → Score = 0.75 (Black, Low-SES)  
3. Patient C: Urgency=0.6, Utility=0.9 → Score = 0.75 (White, Middle-SES)
```

**Step 2: Fairness Constraint (Single-Dimension, Ethnicity)**
```
Current allocations: 70% White, 30% Black (waitlist is 50/50)
- White deficit: +20% (overrepresented)
- Black deficit: -20% (underrepresented)

Algorithm: "Prioritize Black patients"
Result: Pick Patient B (Black) even though tied with others
```

**Step 3: Fairness Constraint (Multi-Dimensional, 70% Ethnicity + 30% SES)**
```
Current allocations: 
- Ethnicity: 70% White, 30% Black (waitlist 50/50) → White +20%, Black -20%
- SES: 60% High, 30% Middle, 10% Low (waitlist 40/40/20) → High +20%, Low -10%

Patient A (White, High-SES): 
  Combined deficit = 0.7×(+20%) + 0.3×(+20%) = +20% (low priority)

Patient B (Black, Low-SES):
  Combined deficit = 0.7×(-20%) + 0.3×(-10%) = -17% (HIGH priority)

Result: Pick Patient B (underrepresented on BOTH dimensions)
```

---

## Summary Table

| Base Policy | Fairness Approach | What Gets Balanced | Result Quality |
|-------------|------------------|-------------------|----------------|
| Urgency | Single-dim | 5 ethnicity groups | High urgency, low benefit |
| Utility | Single-dim | 5 ethnicity groups | High benefit, low urgency |
| Hybrid | Single-dim | 5 ethnicity groups | Balanced, good fairness |
| Hybrid | Composite | 15 intersectional groups | Good fairness, lower benefit (sparse groups) |
| Hybrid | Multidim | 5 ethnicities + 3 SES (weighted) | **BEST: Good fairness + high benefit** ⭐ |

---

## For Your Paper

**Structure your Results section:**

1. **Baseline policies (η=0):** Show urgency vs utility trade-off
2. **Single-dimension fairness:** Show fairness can be achieved with small cost
3. **Composite vs Multidim comparison:** Show why flexibility matters
4. **Optimal configuration:** Hybrid (α=0.25-0.5) + Multidim fairness (70/30 weights)

**Key finding:** Fairness constraint works well with ANY base policy, but multidim approach maintains best efficiency while achieving fairness across multiple dimensions.

---

**Bottom line:** The 4 policies determine medical priorities. The 3 fairness approaches determine how to balance demographics. They work together: base policy ranks, fairness reorders. 🎯

