#!/usr/bin/env python
"""
Compare composite groups vs multi-dimensional fairness approaches.
"""

import pandas as pd
import os

def main():
    print("=" * 70)
    print("FAIRNESS APPROACH COMPARISON")
    print("=" * 70)
    print()
    
    # Load results
    composite_file = 'data/summary.csv'
    multidim_file = 'data/summary_multidim.csv'
    
    if not os.path.exists(composite_file):
        print(f"ERROR: {composite_file} not found. Run composite fairness first:")
        print("git checkout composite-fairness")
        print("python scripts/run_sweep.py --patients data/patients_composite.csv ...")
        return
    
    if not os.path.exists(multidim_file):
        print(f"ERROR: {multidim_file} not found. Run multidim fairness first:")
        print("git checkout multidim-fairness")
        print("python scripts/run_multidim_sweep.py ...")
        return
    
    composite = pd.read_csv(composite_file)
    multidim = pd.read_csv(multidim_file)
    
    # Compare results for hybrid with fairness
    comp_fair = composite[(composite['policy'] == 'Hybrid+Fair') & (composite['alpha'] == 0.5)]
    multi_fair = multidim[(multidim['policy'] == 'Hybrid+Fair') & (multidim['alpha'] == 0.5)]
    
    if len(comp_fair) == 0 or len(multi_fair) == 0:
        print("No comparable fairness results found")
        return
    
    comp_fair = comp_fair.iloc[0]
    multi_fair = multi_fair.iloc[0]
    
    print("Comparison: Hybrid (α=0.5) with Fairness Constraints (η=1.0)")
    print("-" * 70)
    print()
    
    print("COMPOSITE GROUPS (Ethnicity × SES):")
    print(f"  Total Benefit:     {comp_fair['total_benefit_years']:.1f} years")
    print(f"  Mean Urgency:      {comp_fair['mean_urgency_norm']:.4f}")
    print(f"  Fairness L1:       {comp_fair['fairness_L1']:.6f}")
    print(f"  N Assigned:        {comp_fair['n_assigned']}")
    print()
    
    print("MULTI-DIMENSIONAL (Ethnicity 70%, SES 30%):")
    print(f"  Total Benefit:     {multi_fair['total_benefit_years']:.1f} years")
    print(f"  Mean Urgency:      {multi_fair['mean_urgency_norm']:.4f}")
    print(f"  Fairness L1:       {multi_fair['fairness_L1']:.6f}")
    print(f"  N Assigned:        {multi_fair['n_assigned']}")
    print()
    
    print("DIFFERENCES:")
    benefit_diff = multi_fair['total_benefit_years'] - comp_fair['total_benefit_years']
    fairness_diff = multi_fair['fairness_L1'] - comp_fair['fairness_L1']
    urgency_diff = multi_fair['mean_urgency_norm'] - comp_fair['mean_urgency_norm']
    
    print(f"  Benefit Difference: {benefit_diff:+.1f} years ({benefit_diff/comp_fair['total_benefit_years']*100:+.1f}%)")
    print(f"  Fairness Difference: {fairness_diff:+.6f} ({'Better' if fairness_diff < 0 else 'Worse'})")
    print(f"  Urgency Difference: {urgency_diff:+.4f}")
    print()
    
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print()
    
    if abs(benefit_diff) < 100 and abs(fairness_diff) < 0.01:
        print("→ Both approaches perform SIMILARLY")
        print("  Choose based on interpretability:")
        print("  - Composite: Better for intersectionality (Black_Low as distinct group)")
        print("  - Multi-dim: Better for flexibility (can weight dimensions)")
    elif benefit_diff > 0 and fairness_diff > 0:
        print("→ Multi-dimensional achieves MORE benefit but LESS fairness")
    elif benefit_diff < 0 and fairness_diff < 0:
        print("→ Multi-dimensional achieves LESS benefit but MORE fairness")
    elif benefit_diff > 0 and fairness_diff < 0:
        print("→ Multi-dimensional DOMINATES (more benefit AND more fairness)")
    else:
        print("→ Composite DOMINATES (more benefit AND more fairness)")

if __name__ == '__main__':
    main()

