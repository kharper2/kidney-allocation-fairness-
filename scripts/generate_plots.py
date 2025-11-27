#!/usr/bin/env python
"""
Generate plots for the kidney allocation paper.
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', type=str, default='data/summary.csv')
    ap.add_argument('--outdir', type=str, default='figures')
    args = ap.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.summary)
    
    # Plot 1: Urgency vs Total Benefit
    plt.figure(figsize=(10, 6))
    for _, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = 'blue'
        else:
            marker = 's'
            color = 'red'
        label = f"{row['policy']} (α={row['alpha']:.2f})"
        plt.scatter(row['mean_urgency_norm'], row['total_benefit_years'], 
                   marker=marker, s=100, alpha=0.6, color=color)
        plt.text(row['mean_urgency_norm'], row['total_benefit_years'], 
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=8, ha='left')
    
    plt.xlabel('Mean Recipient Urgency (normalized)', fontsize=12)
    plt.ylabel('Total Survival Benefit (years)', fontsize=12)
    plt.title('Trade-off: Urgency vs Total Benefit', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(['η=0 (no fairness)', 'η>0 (fairness-aware)'], loc='best')
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'tradeoff_urgency_vs_benefit.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    # Plot 2: Fairness (L1 disparity) vs Total Benefit
    plt.figure(figsize=(10, 6))
    for _, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = 'blue'
        else:
            marker = 's'
            color = 'red'
        label = f"{row['policy']} (α={row['alpha']:.2f})"
        plt.scatter(row['fairness_L1'], row['total_benefit_years'], 
                   marker=marker, s=100, alpha=0.6, color=color)
        plt.text(row['fairness_L1'], row['total_benefit_years'], 
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=8, ha='left')
    
    plt.xlabel('Allocation Disparity L1 (lower is fairer)', fontsize=12)
    plt.ylabel('Total Survival Benefit (years)', fontsize=12)
    plt.title('Trade-off: Fairness vs Total Benefit', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(['η=0 (no fairness)', 'η>0 (fairness-aware)'], loc='best')
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'tradeoff_fairness_vs_benefit.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    # Plot 3: Summary bar chart by policy
    plt.figure(figsize=(12, 6))
    policies = df['policy'].unique()
    x = range(len(df))
    width = 0.35
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subplot 1: Total benefit by configuration
    colors = ['blue' if eta == 0 else 'red' for eta in df['fairness_eta']]
    ax1.bar(x, df['total_benefit_years'], color=colors, alpha=0.7)
    ax1.set_xlabel('Configuration Index', fontsize=11)
    ax1.set_ylabel('Total Benefit (years)', fontsize=11)
    ax1.set_title('Total Survival Benefit by Configuration', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Subplot 2: Fairness L1 by configuration
    ax2.bar(x, df['fairness_L1'], color=colors, alpha=0.7)
    ax2.set_xlabel('Configuration Index', fontsize=11)
    ax2.set_ylabel('Fairness L1 Disparity', fontsize=11)
    ax2.set_title('Allocation Disparity by Configuration', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'summary_bars.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    print("\nSummary statistics:")
    print(df.to_string())

if __name__ == '__main__':
    main()

