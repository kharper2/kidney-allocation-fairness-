# What the Fairness Constraint Does (For Graphs)

## η=0 (No Fairness Constraint) - Blue Circles

**What happens:**
- Algorithm ranks patients **purely by medical score** (urgency, utility, or hybrid)
- Highest scoring patient gets the kidney, regardless of their demographic group
- **No balancing** - groups that happen to have higher medical scores get more organs

**Result:**
- Higher total benefit (no constraints)
- But may have **high disparity** (some groups get way more organs than their population share)

---

## η=1 (Fairness Constraint Active) - Red Squares

**What happens:**
1. Algorithm still ranks by medical score
2. **BUT** when selecting a recipient, it checks: "Which group is most underrepresented?"
3. If a group is underrepresented (got fewer organs than their population share), the algorithm **prioritizes patients from that group**
4. It still picks the **best patient within that group** (doesn't sacrifice medical quality completely)

**Example:**
- Waitlist: 50% White, 50% Black
- Allocations so far: 60% White, 40% Black
- **Black is underrepresented** (40% < 50%)
- Next donor: Algorithm prioritizes Black patients, but still picks the **highest-scoring Black patient**

**Result:**
- Slightly lower total benefit (small constraint cost)
- **Much lower disparity** (groups get organs proportional to their waitlist share)

---

## Visual Guide for Graphs

**Figure 1: Urgency vs Benefit**
- **Blue circles (η=0)**: Higher benefit, but may prioritize sicker patients
- **Red squares (η=1)**: Slightly lower benefit, but balances urgency with fairness

**Figure 2: Fairness vs Benefit**
- **Blue circles (η=0)**: High benefit, but high disparity (unfair)
- **Red squares (η=1)**: Slightly lower benefit, but low disparity (fair)
- **Key insight**: Small benefit cost (~3-8%) for huge fairness gain (96% disparity reduction)

**Figure 3: Summary Bars**
- **Blue bars**: No fairness (η=0) - higher benefit, higher disparity
- **Red bars**: With fairness (η=1) - slightly lower benefit, much lower disparity

---

## Plain English Summary

**η=0 (No fairness):** "Give the kidney to whoever has the best medical score, period."

**η=1 (With fairness):** "Give the kidney to whoever has the best medical score, BUT if one group is getting left behind, prioritize the best patient from that group instead."

