# Documentation Consolidation Plan

## Current Problem
Information is duplicated across multiple files:
- **README.md** (24KB) - Has branch summaries, results, explanations
- **BRANCHES.md** (11KB) - Has same branch summaries, results, explanations  
- **RESULTS_SUMMARY.md** (3.5KB) - Has main branch results (duplicated, also has OLD 2k/500 data!)
- **POLICY_FAIRNESS_INTERACTION.md** (9KB) - Unique content, should keep

## Proposed Structure

### **README.md** - Main Entry Point (Keep concise)
**What to keep:**
- Quick start guide
- What's included
- Brief branch overview (summary table only, link to BRANCHES.md for details)
- Usage guide
- Links to other docs

**What to remove:**
- Detailed branch descriptions (move to BRANCHES.md)
- Full test results tables (keep summary, link to BRANCHES.md)
- "Why results make sense" explanations (move to BRANCHES.md)
- Duplicate comparison tables

### **BRANCHES.md** - Detailed Branch Reference (Keep comprehensive)
**What to keep:**
- Detailed branch descriptions
- Full test results for all branches
- Usage instructions
- Comparison tables
- "Why results make sense" explanations
- When to use each branch

**What to add:**
- Link back to README for quick start
- Link to POLICY_FAIRNESS_INTERACTION.md

### **RESULTS_SUMMARY.md** - DELETE
**Why:** All information is duplicated in README/BRANCHES, and it has outdated 2k/500 results

### **POLICY_FAIRNESS_INTERACTION.md** - Keep as-is
**Why:** Unique content explaining how policies and fairness interact

## Result
- **README.md** = Quick reference, entry point (~15KB)
- **BRANCHES.md** = Detailed branch comparison (~11KB)  
- **POLICY_FAIRNESS_INTERACTION.md** = Policy/fairness explanation (~9KB)
- **Total:** ~35KB (down from ~48KB, less duplication)

## Implementation Steps
1. Remove detailed branch sections from README, replace with summary + link
2. Ensure BRANCHES.md has all detailed info
3. Delete RESULTS_SUMMARY.md
4. Add cross-references between files

