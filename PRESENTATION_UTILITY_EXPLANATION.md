# Utility Calculation Explanation for Presentation

## Slide 1: Baseline Scores (From CSV)

**Baseline Urgency Score:**
- Pre-computed in CSV: `UrgencyScore = log(1 + DialysisYears) / max(log(1 + DialysisYears))`
- Higher = more urgent (longer on dialysis)
- Range: 0-1

**Baseline Utility Score:**
- Pre-computed in CSV: `UtilityScore = 1 - EPTS/100`
- Higher = better candidate (lower EPTS = healthier)
- Range: 0-1
- **This is just the patient component** - will be adjusted with donor quality

---

## Slide 2: No-Transplant Survival (What happens if patient doesn't get kidney)

**Formula:**
```
NoTx = 5.0 - 0.6*DialysisYears - 1.0*Diabetes - 0.5*Age80
```

**Plain English:**
- Base survival: 5 years
- **Subtract** 0.6 years per year on dialysis (longer dialysis = worse)
- **Subtract** 1.0 year if patient has diabetes
- **Subtract** 0.5 years per normalized age unit (older = worse)
- Result: Expected years of survival **without** transplant

**Why this matters:** We compare this to post-transplant survival to calculate the **benefit** of transplant.

---

## Slide 3: Post-Transplant Survival (What happens if patient gets kidney)

**Formula:**
```
Post = 5.0 
     + 6.0*(1 - EPTS/100)           [Patient quality: CSV UtilityScore]
     + 3.0*(1 - KDPI/100)           [Donor quality: KDPI normalized]
     + 1.0*(1 - Age80)              [Patient age]
     + 2.0*(1 - EPTS/100)*(1 - KDPI/100)  [Interaction: good patient + good donor]
```

**Plain English:**
- Base: 5 years
- **Add** 6 years × patient quality (CSV UtilityScore) - healthier patients do better
- **Add** 3 years × donor quality (1 - KDPI) - better kidneys (lower KDPI) help more
- **Add** 1 year × patient age factor - younger patients do better
- **Add** 2 years × patient quality × donor quality - **synergy effect**: matching good patients with good kidneys gives extra benefit

**Key insight:** This is where we **match good candidates with good kidneys** - the interaction term rewards optimal pairings!

---

## Slide 4: Final Utility (Survival Benefit)

**Formula:**
```
Utility = max(Post - NoTx, 0.0)
```

**Plain English:**
- **Benefit = Post-transplant survival - No-transplant survival**
- If benefit is negative (transplant makes things worse), set to 0
- This is the **years of life gained** by giving this specific kidney to this specific patient

**Example:**
- Patient: EPTS=20 (good), Age=50, 3 years dialysis, no diabetes
- Donor: KDPI=30 (good kidney)
- NoTx = 5.0 - 0.6×3 - 0 - 0.5×0.625 = 2.7 years
- Post = 5.0 + 6.0×0.8 + 3.0×0.7 + 1.0×0.375 + 2.0×0.8×0.7 = 13.0 years
- **Utility = 13.0 - 2.7 = 10.3 years gained** ✅

---

## Slide 5: How KDPI Affects Matching

**KDPI (Kidney Donor Profile Index):**
- Lower KDPI = better kidney quality
- Range: 0-100 (we normalize to 0-1)

**How it works in utility:**
1. **Direct effect:** `+ 3.0*(1 - KDPI)` - better kidneys add more years
2. **Interaction effect:** `+ 2.0*(1-EPTS)*(1-KDPI)` - **matches good patients with good kidneys**

**Example:**
- Good patient (EPTS=20) + Good kidney (KDPI=20):
  - Direct: +3.0×0.8 = +2.4 years
  - Interaction: +2.0×0.8×0.8 = +1.3 years
  - **Total from KDPI: +3.7 years**

- Good patient (EPTS=20) + Bad kidney (KDPI=80):
  - Direct: +3.0×0.2 = +0.6 years
  - Interaction: +2.0×0.8×0.2 = +0.3 years
  - **Total from KDPI: +0.9 years**

**Result:** Algorithm naturally prefers matching good patients with good kidneys!

---

## Summary for Presentation

1. **Baseline scores** (CSV): Patient-only components (urgency, EPTS-based utility)
2. **NoTx formula**: What happens without transplant (dialysis, diabetes, age reduce survival)
3. **Post formula**: What happens with transplant (combines patient quality + donor quality + synergy)
4. **Final utility**: Benefit = Post - NoTx (years gained)
5. **KDPI role**: Lower KDPI = better kidney = more years gained, especially when matched with good patients

**Key message:** We start with baseline patient scores, then **dynamically adjust utility based on donor quality** to match good candidates with good kidneys, maximizing survival benefit.

