# Repository Branches - Detailed Comparison

📋 **See [`README.md`](README.md) for quick start guide and overview**  
📋 **See [`POLICY_FAIRNESS_INTERACTION.md`](POLICY_FAIRNESS_INTERACTION.md) for how allocation policies interact with fairness approaches**

---

**All branches tested with 5,000 patients, 1,000 donors (proof-of-concept). Final experiments need 20k-150k patients, 3k-20k donors.**

---

## 🎯 Quick Comparison

**Test configuration:** Hybrid+Fair policy (α=0.5, η=1.0)

| Branch | Total Benefit | Fairness L1 | Organs Used | Rank |
|--------|--------------|-------------|-------------|------|
| **main** (single-dim) | **9,512 years** (Sex) | **0.0003** | **992/1,000** | 🥇 BEST |
| **multidim-fairness** ⭐ | **9,501 years** (Ethnicity+Distance) | **0.0015** | **1,000/1,000** | 🥈 Excellent |
| **main** (single-dim) | 9,125 years (Distance) | 0.0010 | 964/1,000 | 🥉 Good |
| **main** (single-dim) | 8,960 years (Ethnicity) | 0.0008 | 960/1,000 | Good |
| **composite-fairness** | 6,479 years | 0.0043 | 751/1,000 | ⚠️ Sparse groups |

**Key Finding:** Composite and Multidim are **different approaches** with **different results**:
- **Composite**: 6,479 years - creates 25 intersectional groups (e.g., "Black_>250"), many are sparse
- **Multidim**: 9,501 years - tracks 10 groups independently (5 ethnicities + 5 distances), always finds matches

**Winner:** `main` branch with **Sex** fairness performs best! `multidim-fairness` is close second and balances multiple dimensions effectively.

---

## 📌 Branch 1: `main` - Single-Dimension Fairness

### What It Does
- Balances fairness across **ONE dimension at a time**
- Run separate experiments: one for Ethnicity, Distance, or Sex
- Compare results across dimensions
- Standard approach in most allocation research

### How to Use
```bash
git checkout main

# For Ethnicity fairness
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Ethnicity

# For Distance to Treatment Center fairness (SRTR accessibility measure)
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col DistancetoCenterMiles

# For Sex fairness
python scripts/run_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --group_col Sex
```

### Test Results (5k patients, 1k donors)

| Policy | Total Benefit | Fairness L1 | Organs Used |
|--------|--------------|-------------|-------------|
| Urgency (α=1.0, η=0) | 8,038 years | 0.010 | 1,000/1,000 |
| Utility (α=0, η=0) | 10,391 years | 0.033 | 1,000/1,000 |
| Hybrid (α=0.5, η=0) | 9,794 years | 0.019 | 1,000/1,000 |
| **Hybrid+Fair (α=0.5, η=1.0) - Ethnicity** | **8,960 years** | **0.0008** | **960/1,000** |
| **Hybrid+Fair (α=0.5, η=1.0) - Distance** | **9,125 years** | **0.0010** | **964/1,000** |
| **Hybrid+Fair (α=0.5, η=1.0) - Sex** | **9,512 years** | **0.0003** | **992/1,000** |

### Why These Results Make Sense

**Sex fairness (9,512 years) performs best:**
- Only 2 groups (M, F) → easier to balance than 5 ethnicities
- 99% organs used (992/1,000) → fewer wasted organs
- Lowest disparity (L1=0.0003) → near-perfect fairness

**Distance fairness (9,125 years) performs well:**
- 5 distance categories → manageable number of groups
- SRTR accessibility measure → clinically relevant
- 96% organs used, good fairness (L1=0.0010)

**Ethnicity fairness (8,960 years) is standard:**
- 5 groups → more complex than Sex but still manageable
- 96% organs used, excellent fairness (L1=0.0008)
- Most common approach in research

**Why fewer groups perform better:** With fewer groups, it's easier to find compatible matches when enforcing fairness, so fewer organs go unused.

### When to Use
- Baseline comparison
- When only one fairness dimension matters
- Safe, reliable version for submission

---

## 📌 Branch 2: `composite-fairness` - Intersectional Groups

### What It Does
- Creates **intersectional groups** by combining attributes
- Example: "Black_<50", "White_50-100", "Hispanic_>250"
- Ethnicity (5 groups) × Distance (5 categories) = **25 composite groups**
- Treats each intersection as distinct demographic
- Balances across ALL 15 groups simultaneously

### How to Use
```bash
git checkout composite-fairness

# Step 1: Create composite groups (Ethnicity × Distance to Treatment Center)
python scripts/add_composite_groups.py \
  --patients_in data/patients.csv \
  --patients_out data/patients_composite.csv \
  --columns Ethnicity DistancetoCenterMiles

# Step 2: Run sweep with composite groups
python scripts/run_sweep.py \
  --patients data/patients_composite.csv \
  --donors data/donors.csv \
  --group_col Ethnicity_DistancetoCenterMiles
```

### Test Results (5k patients, 1k donors)

| Policy | Total Benefit | Fairness L1 | Organs Used |
|--------|--------------|-------------|-------------|
| Urgency (α=1.0, η=0) | 8,038 years | 0.028 | 1,000/1,000 |
| Utility (α=0, η=0) | 10,391 years | 0.055 | 1,000/1,000 |
| Hybrid (α=0.5, η=0) | 9,794 years | 0.033 | 1,000/1,000 |
| **Hybrid+Fair (α=0.5, η=1.0)** | **6,479 years** | **0.0043** | **751/1,000** ⚠️ |

### Composite Groups Created (n=25)

Ethnicity (5) × Distance (5) = 25 groups: Black_<50, Black_50-100, White_<50, etc.

### Why These Results Make Sense

**Why composite performs worse (6,479 years):**
- **25 groups too many**: Many groups are tiny (<1% of population)
- **Hard to find matches**: When algorithm needs "Other_>250" patient, may not find compatible match
- **25% organs wasted**: Only 751/1,000 organs used (vs 960-1000 for other approaches)
- **34% benefit loss**: 6,479 vs 9,794 years (no fairness baseline)

**Example:** If only 0.5% of patients are "Other_>250", and algorithm needs one with specific blood type, it may wait too long and waste the organ.

### When to Use
- Theoretical comparison (intersectionality literature)
- Demonstrates why sparse groups are problematic
- Shows why flexible approaches (multidim) are better

---

## 📌 Branch 3: `multidim-fairness` - Weighted Multi-Dimensional ⭐

### What It Does
- Tracks **multiple dimensions independently**
- Combines deficits with **configurable weights**
- Example: 70% ethnicity fairness + 30% distance fairness (SRTR accessibility)
- Scales easily to 4+ dimensions

### How It Works

**Configuration:** 70% Ethnicity + 30% Distance to Treatment Center

**Example calculation:**
```
Current allocations: 60% White, 40% Black; 70% Middle, 30% Low

Patient A: Black, >250 miles
- Ethnicity deficit: -20% (Black underrepresented: 40% allocated, 50% in waitlist)
- Distance deficit: -10% (>250 miles underrepresented: 10% allocated, 20% in waitlist)
- Combined score: 0.7×(-20%) + 0.3×(-10%) = -17% 
→ HIGH PRIORITY

Patient B: White, <50 miles  
- Ethnicity deficit: +10% (White overrepresented)
- Distance deficit: +5% (<50 miles overrepresented)
- Combined score: 0.7×(+10%) + 0.3×(+5%) = +8.5%
→ LOW PRIORITY
```

Algorithm prioritizes Patient A to reduce deficits on BOTH dimensions.

### How to Use

**2 Dimensions (Example):**
```bash
git checkout multidim-fairness

# Run multi-dimensional sweep with 2 dimensions (Ethnicity + Distance to Treatment Center)
python scripts/run_multidim_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --fairness_dims Ethnicity DistancetoCenterMiles \
  --fairness_weights 0.7 0.3 \
  --alphas 0.25 0.5 0.75 \
  --etas 0 1.0
```

**3+ Dimensions (Supported!):**
```bash
# Example with 3 dimensions: Ethnicity, Distance, and Sex (all SRTR data)
python scripts/run_multidim_sweep.py \
  --patients data/patients.csv \
  --donors data/donors.csv \
  --fairness_dims Ethnicity DistancetoCenterMiles Sex \
  --fairness_weights 0.5 0.3 0.2 \
  --alphas 0.5 \
  --etas 0 1.0
```

**Note:** Weights are automatically normalized (they don't need to sum to 1.0). The algorithm tracks each dimension independently and combines deficits with your specified weights.

### Test Results (5k patients, 1k donors, 70% Ethnicity + 30% Distance)

| Policy | Total Benefit | Fairness L1 | Organs Used |
|--------|--------------|-------------|-------------|
| Urgency (α=1.0, η=0) | 8,038 years | 0.015 | 1,000/1,000 |
| Utility (α=0, η=0) | 10,391 years | 0.032 | 1,000/1,000 |
| Hybrid (α=0.5, η=0) | 9,744 years | 0.015 | 1,000/1,000 |
| **Hybrid+Fair (α=0.5, η=1.0)** | **9,501 years** | **0.0015** | **1,000/1,000** ✅ |

### Why These Results Make Sense

**Why multidim performs well (9,501 years):**
- **Tracks 10 groups independently**: 5 ethnicities + 5 distance categories (not 25 intersections)
- **Always finds matches**: Doesn't require exact intersection, just balances both dimensions
- **100% organs used**: All 1,000/1,000 organs allocated (vs 751 for composite)
- **Good fairness**: L1=0.0015 across both dimensions simultaneously
- **Only 3% cost**: 9,794 → 9,501 years (small fairness cost for multi-dimensional balance)

**Why multidim beats composite:**
- **Composite**: Needs "Black AND >250 miles" → if that group is tiny, can't find match → organ wasted
- **Multidim**: Needs "Black OR >250 miles" → always finds someone in one of those groups → organ used
- **Result**: 9,501 vs 6,479 years (+47% better) because multidim never wastes organs due to sparse groups

### When to Use
- **Recommended for final paper** ⭐
- When balancing multiple dimensions
- When you want configurable priorities (adjust weights)
- When you want best practical results

---


---

## 🚀 Next Steps

**✅ Done:** All 3 approaches implemented and tested (5k patients, 1k donors)  
**⚠️ To Do:** Run final experiments (20k-150k patients, 3k-20k donors), test multiple seeds, sensitivity analysis, generate final figures

---

**Summary:** All three approaches work. Single-dimension (Sex) performs best, but multidim balances multiple dimensions effectively with only 3% cost.
