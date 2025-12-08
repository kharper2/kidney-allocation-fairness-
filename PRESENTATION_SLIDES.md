# Kidney Allocation Policy Presentation Slides

## Slide 1: Title Slide
**AI and Decision Making in Kidney Allocation: Balancing Urgency, Utility, and Fairness**

Team: Natalie Barnouw, Olivia Joseph, Ella Tubbs, Jessie Liu, Kathryn Harper, Natalia Siwek

---

## Slide 2: Problem Statement
**The Challenge:**
- Kidney allocation must balance multiple competing objectives
- **Urgency**: Save the sickest patients (longer on dialysis)
- **Utility**: Maximize survival benefit (years of life gained)
- **Fairness**: Ensure equitable access across demographic groups

**Question:** How do we design policies that balance these goals?

---

## Slide 3: Our Approach
**Four Allocation Policies:**

1. **Urgency-only** (α=1.0): Prioritize sickest patients
2. **Utility-only** (α=0.0): Maximize survival benefit
3. **Hybrid** (0<α<1): Weighted combination of urgency + utility
4. **Hybrid+Fair** (η=1): Hybrid with fairness constraint

**Fairness Dimensions:** Ethnicity, Distance to Treatment Center, Sex

---

## Slide 4: Two-Layer System: How Policies and Fairness Work Together

**Prerequisite: Blood Type Compatibility (Hard Constraint)**
- **ABO compatibility enforced:** O→all, A→A/AB, B→B/AB, AB→AB only
- Only compatible patients are considered for each donor
- This happens **before** any policy or fairness considerations

**Layer 1: Base Allocation Policy (Medical Ranking)**
- Determines **initial ranking** of patients by medical score
- **Urgency-only:** Rank by urgency score (sickest first)
- **Utility-only:** Rank by survival benefit (highest first)
- **Hybrid:** Rank by `α × Urgency + (1-α) × Utility`
- **This happens FIRST** - creates the medical priority queue

**Layer 2: Fairness Constraint (Group Balancing)**
- **η = 0:** Use base policy ranking as-is (no fairness)
- **η = 1:** Modify ranking to balance demographic groups
  - Still uses the same medical scores from Layer 1
  - **BUT** prioritizes patients from under-served groups
  - Dynamically tracks which groups are behind and boosts them

**How They Combine:**
1. **Filter by blood type compatibility** (prerequisite)
2. **Compute medical score** (Layer 1) for all compatible patients
3. **Check group deficits** (Layer 2) - which groups are under-served?
4. **Select patient** with highest medical score from the group that needs an organ most
5. **Result:** Medical priorities maintained, but allocation balanced across groups

**Key Point:** Fairness doesn't change the utility formula - it only changes **who gets picked first** when groups are imbalanced.

---

## Slide 5: Key Results - Total Benefit
**Total Survival Benefit (Years Gained)**

| Policy | Benefit | Fairness L1 |
|--------|---------|-------------|
| **Utility** | **10,391 years** | 0.033 |
| **Hybrid (α=0.5)** | 10,041 years | 0.028 |
| **Hybrid+Fair (α=0.5)** | 9,174 years | **0.0008** |
| **Urgency** | 8,395 years | 0.007 |

**Key Finding:** Utility beats Urgency by 29% (10,391 vs 8,395 years)

*[Show: summary_bars.png]*

---

## Slide 6: Fairness Trade-off
**Fairness vs Benefit Trade-off**

- **Without fairness (η=0):** Higher benefit, but unfair allocation
- **With fairness (η=1):** Slight benefit cost (~8%), but dramatically fairer

**Fairness improvement:**
- L1 disparity drops from 0.021 → 0.0008 (96% reduction)
- All groups receive proportional allocation

*[Show: tradeoff_fairness_vs_benefit.png]*

---

## Slide 7: Urgency vs Benefit Trade-off
**Can we prioritize both urgency and benefit?**

**Finding:** Trade-off exists - can't maximize both simultaneously

- **Urgency-focused:** Higher mean recipient urgency, lower total benefit
- **Utility-focused:** Lower mean urgency, higher total benefit
- **Hybrid:** Balance between the two

*[Show: tradeoff_urgency_vs_benefit.png]*

---

## Slide 8: Fairness Approaches (3 Ways)
**We tested three ways to add fairness on top of the same medical scores (urgency + utility):**

1. **Single-dimension fairness**
   - Pick **one column** from `patients.csv` (e.g., Ethnicity, Distance, Sex)
   - Track how many organs each group gets vs. its share of the waitlist
   - When η=1, boost under-served groups so allocation across that **one dimension** is balanced

2. **Composite groups fairness**
   - Create **intersectional groups** by combining dimensions, e.g. `Ethnicity × Distance`
   - 5 ethnicities × 5 distance bins → 25 composite groups
   - Fairness operates on these intersectional groups (harder to balance, more sparse groups)
   - **Sparse group problem:** Many groups are tiny (<1% of waitlist). When algorithm needs a patient from a tiny group with specific blood type, can't find match → organ wasted (25% organs wasted in our results)
   - **Note:** We use Ethnicity × Distance (not Sex) because adding Sex would create 50 groups, making the sparse group problem even worse

3. **Multi-dimensional fairness**
   - Track fairness **separately** across multiple dimensions at once (e.g., Ethnicity + Distance + Sex)
   - Compute a fairness score for each dimension, then combine with configurable weights
   - Our extension branch runs 3D fairness on the full dataset using equal weights

**Important:** All three reuse the **same urgency and utility scores**; they differ only in **how groups are tracked and boosted**, not in how medical benefit is calculated.

---

## Slide 9: Fairness Across Dimensions (Single-Dimension Example)
**Best Results by Fairness Dimension (η=1, single-dimension fairness):**

| Dimension | Benefit | Fairness L1 | Why Best? |
|-----------|---------|-------------|-----------|
| **Sex** | **9,512 years** | **0.0001** | Only 2 groups - easiest to balance |
| **Distance** | 9,125 years | 0.0010 | SRTR accessibility measure |
| **Ethnicity** | 8,960 years | 0.0008 | Standard approach, 5 groups |

**Key Insight:** Fewer groups = easier to balance = fewer “wasted” organs.

---

## Slide 10: How Fairness Works within a Policy
**Fairness Constraint (η parameter):**

**η = 0 (No Fairness):**
- Rank patients purely by **policy score**
  - Urgency-only: urgency score
  - Utility-only: utility (years gained)
  - Hybrid: α·urgency + (1–α)·utility
- Highest-scoring compatible patient gets organ

**η = 1 (Fairness Active):**
- Use the **same policy score** as above
- **BUT** within each donor, look at which group(s) are under-served (by Ethnicity / Distance / Sex or their combo)
- Temporarily boost patients from under-served groups so they move up in the queue

**Result:**
- **Utility formula does not change**
- Fairness only changes **who is picked first** when scores are close, to balance allocations across groups

---

## Slide 11: Utility Calculation
**How We Calculate Survival Benefit:**

1. **Baseline (NoTx):** Expected survival without transplant
   - Formula: `5.0 - 0.6×DialysisYears - 1.0×Diabetes - 0.5×Age80`

2. **Post-Transplant (Post):** Expected survival with transplant
   - Formula: `5.0 + 6.0×(1-EPTS) + 3.0×(1-KDPI) + 1.0×(1-Age80) + 2.0×(1-EPTS)×(1-KDPI)`

3. **Utility = Post - NoTx** (years of life gained)

**Key:** Matches good patients with good kidneys (KDPI interaction term)

---

## Slide 12: Methods Summary
**Data:**
- 150,000 patients (synthetic, based on SRTR patterns)
- 20,000 donors
- Features: Age, DialysisYears, Diabetes, EPTS, KDPI, Ethnicity, Distance, Sex

**Evaluation:**
- ABO blood type compatibility enforced
- 8 configurations tested per branch
- Metrics: Total benefit, mean urgency, fairness L1 disparity

---

## Slide 13: Key Findings
**1. Utility > Urgency**
- Healthy recipients gain more years: 10,391 vs 8,395 years (+29%)

**2. Fairness Works**
- Small benefit cost (~8%) for huge fairness gain (96% disparity reduction)

**3. Fewer Groups = Better**
- Sex (2 groups): 9,512 years
- Ethnicity (5 groups): 8,960 years

**4. Fairness Constraint Effective**
- L1 drops from 0.021 → 0.0008 with fairness

---

## Slide 14: Limitations
**What We Didn't Include:**
- **CPRA** (Calculated Panel Reactive Antibody) - measures donor-recipient incompatibility
- In practice, highly sensitized patients (98-100% CPRA) get national priority
- We focus on policy effects, not clinical precision

**What We Did Include:**
- ✅ **ABO blood type compatibility** (enforced as hard constraint - see Slide 4)
- ✅ KDPI (donor quality)
- ✅ EPTS (patient quality)

---

## Slide 15: Conclusions
**Takeaways:**

1. **Hybrid policies** balance urgency and utility effectively
2. **Fairness constraints** achieve equity with minimal benefit cost
3. **Fewer fairness groups** lead to better efficiency
4. **Policy design matters** - small changes have big impacts

**Future Work:**
- Test on real SRTR data
- Include CPRA modeling
- Multi-dimensional fairness (tested in extension branches)

---

## Slide 16: Questions?
**Repository:** https://github.com/kharper2/kidney-allocation-fairness-

**Key Files:**
- `figures/summary_bars.png` - Main results
- `figures/tradeoff_fairness_vs_benefit.png` - Fairness trade-off
- `README.md` - Complete documentation

Thank you!

