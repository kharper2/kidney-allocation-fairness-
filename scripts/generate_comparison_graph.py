#!/usr/bin/env python
"""
Generate comparison graph across all 3 fairness approaches for slideshow.
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--main_sex', type=str, required=True)
    ap.add_argument('--main_ethnicity', type=str, required=True)
    ap.add_argument('--composite', type=str, required=True)
    ap.add_argument('--multidim', type=str, required=True)
    ap.add_argument('--outdir', type=str, default='figures/slideshow')
    args = ap.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    
    # Load all results
    main_sex = pd.read_csv(args.main_sex)
    main_ethnicity = pd.read_csv(args.main_ethnicity)
    composite = pd.read_csv(args.composite)
    multidim = pd.read_csv(args.multidim)
    
    # Extract best Hybrid+Fair result from each (α=0.5, η=1.0)
    def get_best_fair(df, name):
        fair = df[(df['fairness_eta'] == 1.0) & (df['policy'] == 'Hybrid+Fair')]
        if len(fair) == 0:
            return None
        # Get α=0.5 if available, otherwise best
        best = fair[fair['alpha'] == 0.5]
        if len(best) == 0:
            best = fair.loc[fair['total_benefit_years'].idxmax()]
        else:
            best = best.iloc[0]
        return {
            'name': name,
            'benefit': best['total_benefit_years'],
            'fairness': best['fairness_L1'],
            'organs': best['n_assigned']
        }
    
    results = []
    for df, name in [(main_sex, 'Single-dim (Sex)'),
                     (main_ethnicity, 'Single-dim (Ethnicity)'),
                     (composite, 'Composite (Ethnicity×Distance)'),
                     (multidim, 'Multidim (Ethnicity+Distance)')]:
        r = get_best_fair(df, name)
        if r:
            results.append(r)
    
    results_df = pd.DataFrame(results)
    
    # Create comparison bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    x = range(len(results_df))
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    
    # Left: Total Benefit
    bars1 = ax1.bar(x, results_df['benefit'], color=colors[:len(results_df)], alpha=0.8)
    ax1.set_xlabel('Fairness Approach', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Benefit (years)', fontsize=12, fontweight='bold')
    ax1.set_title('Total Survival Benefit by Fairness Approach', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(results_df['name'], rotation=15, ha='right', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars1, results_df['benefit'])):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'{val:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Right: Fairness L1
    bars2 = ax2.bar(x, results_df['fairness'], color=colors[:len(results_df)], alpha=0.8)
    ax2.set_xlabel('Fairness Approach', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Fairness L1 Disparity (lower is better)', fontsize=12, fontweight='bold')
    ax2.set_title('Allocation Fairness by Approach', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(results_df['name'], rotation=15, ha='right', fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars2, results_df['fairness'])):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.0002,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'fairness_approaches_comparison.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"✅ Saved {outpath}")
    plt.close()
    
    # Create summary table
    print("\n" + "="*60)
    print("SUMMARY TABLE FOR SLIDESHOW")
    print("="*60)
    print(results_df.to_string(index=False))
    print("="*60)
    print(f"\nBest benefit: {results_df.loc[results_df['benefit'].idxmax(), 'name']} ({results_df['benefit'].max():.0f} years)")
    print(f"Best fairness: {results_df.loc[results_df['fairness'].idxmin(), 'name']} (L1={results_df['fairness'].min():.4f})")
    print()

if __name__ == '__main__':
    main()

