# Where and When Patient Features Are Used

## Patient Features Available in CSV

From `patients.csv`:
- `Age` - Patient age
- `DialysisYears` - Years on dialysis
- `Diabetes` - Binary (0 or 1)
- `EPTSScore` - Expected Post-Transplant Survival score (0-100)
- `Sex` - M or F
- `Ethnicity` - Hispanic, Black, White, Asian, Other
- `DistancetoCenterMiles` - Distance to treatment center (<50, 50-100, etc.)
- `BloodType` - O, A, B, AB
- `WaitTimeYears` - Wait time on list (categorical)
- `UrgencyScore` - Pre-computed urgency (from CSV)
- `UtilityScore` - Pre-computed utility component (from CSV)

---

## Feature Usage Map

### 1. `compute_patient_features()` - Line 13-31
**When:** Called once at the start, before allocation begins
**Purpose:** Pre-compute all derived features from raw CSV data

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **Age** | Line 16: `Age80 = min(Age, 80) / 80.0` | Normalize age, cap at 80 |
| **DialysisYears** | Line 19: `UrgencyScore` (from CSV) | Already in CSV, used directly |
| **Diabetes** | Line 19: `UrgencyScore` (from CSV) | Already in CSV, used directly |
| **EPTSScore** | Line 15: `EPTS_norm = EPTS/100` | Normalize EPTS to 0-1 |
| **DialysisYears** | Line 25: `- 0.6*DialysisYears` | NoTx calculation |
| **Diabetes** | Line 25: `- 1.0*Diabetes` | NoTx calculation |
| **Age80** | Line 25: `- 0.5*Age80` | NoTx calculation |
| **EPTS_norm** | Line 29: `6.0*(1-E)` | A_part calculation |
| **Age80** | Line 29: `1.0*(1-Age80)` | A_part calculation |
| **NoTx** | Line 29: `- NoTx` | A_part calculation |
| **EPTS_norm** | Line 30: `2.0*(1-E)` | B_part calculation |

**Output:** DataFrame with computed features:
- `EPTS_norm` (0-1)
- `Age80` (0-1)
- `Urgency_norm` (from CSV UrgencyScore)
- `NoTx` (survival without transplant)
- `A_part` (utility component A)
- `B_part` (utility component B)

---

### 2. `build_sorted_lists()` - Line 39-62
**When:** Called once per allocation run, before processing donors
**Purpose:** Pre-sort patients by medical score for each KDPI bin

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **Urgency_norm** | Line 41: `U = pat_df['Urgency_norm']` | For urgency policy ranking |
| **A_part** | Line 42: `A = pat_df['A_part']` | Utility component A |
| **B_part** | Line 43: `B = pat_df['B_part']` | Utility component B |
| **BloodType** | Line 44: `pat_df['BloodType']` | Group by ABO type for compatibility |

**How it works:**
- For each KDPI bin (0-9), creates sorted lists
- Sorts by: Urgency, Utility, or Hybrid (depending on policy)
- Separate lists for each BloodType (O, A, B, AB)
- Result: Pre-sorted patient indices for fast lookup

---

### 3. `exact_utility_for_pair()` - Line 64-70
**When:** Called for each donor-recipient pair during allocation
**Purpose:** Calculate exact utility (survival benefit) for a specific pairing

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **EPTS_norm** | Line 65: `E = EPTS_norm` | Line 67: `6.0*(1-E)` - Patient quality component |
| **EPTS_norm** | Line 67: `2.0*(1-E)*(1-K)` | Interaction with donor KDPI |
| **Age80** | Line 65: `Age80 = Age80` | Line 67: `1.0*(1-Age80)` - Age factor |
| **NoTx** | Line 68: `no_tx = NoTx` | Line 69: `util = max(post - no_tx, 0.0)` - Baseline survival |
| **KDPI** (donor) | Line 65: `K = kdpi_norm` | Line 67: `3.0*(1-K)` - Donor quality component |

**Formula:**
```
post = 5.0 + 6.0*(1-EPTS) + 3.0*(1-KDPI) + 1.0*(1-Age80) + 2.0*(1-EPTS)*(1-KDPI)
util = max(post - NoTx, 0.0)
```

---

### 4. `allocate()` - Line 72-144
**When:** Called once per allocation run
**Purpose:** Main allocation algorithm - matches donors to recipients

#### 4a. Setup (Lines 73-85)

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **group_col** (e.g., Ethnicity) | Line 77-80: `pat_df[group_col]` | Extract groups for fairness |
| **Urgency_norm** | Line 85: `U = pat_df['Urgency_norm']` | For urgency scoring |

#### 4b. Per-Donor Loop (Lines 87-133)

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **DonorBloodType** | Line 88: `donor_bt = row['DonorBloodType']` | ABO compatibility |
| **Donor KDPI** | Line 90-92: `kdpi = row['KDPI']` | Normalized to K_norm, used for binning |
| **group_col** (e.g., Ethnicity) | Line 78: `groups = pat_df[group_col]` | Line 108: Check if patient matches restricted group |
| **group_col** | Line 133: `groups[best_i]` | Track which group got the organ |
| **Urgency_norm** | Line 114: `score = U[i]` | For urgency policy |
| **EPTS_norm, Age80, NoTx** | Line 116: `exact_utility_for_pair()` | Calculate utility for pair |
| **BloodType** | Line 128: `pat_df.iloc[best_i]['BloodType']` | Record recipient blood type |

**Fairness Constraint (Lines 97-103):**
- Uses `group_col` to identify underrepresented groups
- Line 108: `groups[lst[h]] != restrict_group` - Skip patients not in target group
- Line 133: `alloc_counts[groups[best_i]] += 1` - Track allocations per group

---

## Complete Flow

```
1. Load CSV → compute_patient_features()
   ├─ Age → Age80
   ├─ EPTS → EPTS_norm
   ├─ DialysisYears + Diabetes → UrgencyScore (from CSV)
   ├─ DialysisYears + Diabetes + Age80 → NoTx
   └─ EPTS_norm + Age80 + NoTx → A_part, B_part

2. build_sorted_lists()
   ├─ Urgency_norm → Urgency ranking
   ├─ A_part + B_part + KDPI bin → Utility ranking
   └─ BloodType → Separate lists per ABO type

3. For each donor:
   ├─ DonorBloodType → Find compatible recipients
   ├─ Donor KDPI → Determine quality bin
   ├─ group_col (Ethnicity/Sex/Distance) → Fairness constraint
   └─ exact_utility_for_pair()
       ├─ EPTS_norm → Patient quality
       ├─ KDPI → Donor quality
       ├─ Age80 → Age factor
       └─ NoTx → Baseline survival

4. Select best recipient based on:
   ├─ Medical score (urgency/utility/hybrid)
   ├─ ABO compatibility
   ├─ Fairness constraint (if η > 0)
   └─ Availability (not already assigned)
```

---

## Summary Table

| Patient Feature | Used In | Purpose |
|----------------|---------|---------|
| **Age** | compute_patient_features | → Age80 (normalized, capped at 80) |
| **DialysisYears** | compute_patient_features | → NoTx calculation |
| **Diabetes** | compute_patient_features | → NoTx calculation |
| **EPTSScore** | compute_patient_features | → EPTS_norm → A_part, B_part, exact_utility |
| **UrgencyScore** (CSV) | compute_patient_features | → Urgency_norm (used directly) |
| **BloodType** | build_sorted_lists, allocate | ABO compatibility matching |
| **group_col** (Ethnicity/Sex/Distance) | allocate | Fairness constraint balancing |
| **Age80** | exact_utility_for_pair | Post-transplant survival calculation |
| **EPTS_norm** | exact_utility_for_pair | Post-transplant survival calculation |
| **NoTx** | exact_utility_for_pair | Baseline for utility (benefit) calculation |

---

## Key Insights

1. **Age, DialysisYears, Diabetes** → Used in NoTx (baseline survival)
2. **EPTS** → Used in utility calculation (patient quality component)
3. **UrgencyScore** (CSV) → Used directly for urgency ranking
4. **BloodType** → Used for ABO compatibility (hard constraint)
5. **group_col** (Ethnicity/Sex/Distance) → Used only for fairness (if η > 0)
6. **KDPI** (donor) → Combined with EPTS in utility calculation

**Not used:**
- `PriorTx` - Prior transplant (in CSV but not used)
- `RawEPTS` - We use EPTSScore instead
- `WaitTimeYears` - We use DialysisYears for urgency (though there's a wait-time policy)

