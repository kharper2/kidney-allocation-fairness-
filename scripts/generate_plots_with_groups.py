#!/usr/bin/env python
"""
Generate plots with explicit group information.
Shows which fairness dimension and groups are being compared.
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np

def get_group_info(group_col, patients_csv=None):
    """Get information about which groups are being compared."""
    if group_col == 'Ethnicity':
        return 'Ethnicity: Hispanic, Black, White, Asian, Other (5 groups)'
    elif group_col == 'Sex':
        return 'Sex: M, F (2 groups)'
    elif group_col == 'DistancetoCenterMiles':
        return 'Distance: <50, 50-100, 100-150, 150-250, >250 miles (5 groups)'
    elif 'Ethnicity_DistancetoCenterMiles' in group_col or 'Ethnicity_Distance' in group_col:
        return 'Composite: Ethnicity × Distance (25 intersectional groups)'
    elif 'multidim' in str(group_col).lower() or '+' in str(group_col):
        return 'Multidim: Multiple dimensions with weights'
    else:
        # Try to read from CSV if available
        if patients_csv and os.path.exists(patients_csv):
            try:
                df = pd.read_csv(patients_csv, nrows=1000)
                if group_col in df.columns:
                    unique_groups = sorted(df[group_col].unique())
                    return f'{group_col}: {", ".join(map(str, unique_groups[:10]))} ({len(unique_groups)} groups)'
            except:
                pass
        return f'Fairness dimension: {group_col}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', type=str, default='data/summary.csv')
    ap.add_argument('--outdir', type=str, default='figures')
    ap.add_argument('--patients', type=str, default='data/patients.csv', help='For group info')
    args = ap.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.summary)
    
    # Get fairness dimension and group info
    if 'group_col' in df.columns:
        fairness_dim = df['group_col'].iloc[0] if len(df) > 0 else 'Ethnicity'
        group_info = get_group_info(fairness_dim, args.patients)
    else:
        fairness_dim = 'Ethnicity'
        group_info = 'Fairness dimension: Ethnicity'
    
    # Plot 1: Urgency vs Total Benefit
    plt.figure(figsize=(11, 7))
    for _, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = 'blue'
        else:
            marker = 's'
            color = 'red'
        plt.scatter(row['mean_urgency_norm'], row['total_benefit_years'], 
                   marker=marker, s=120, alpha=0.7, color=color, edgecolor='black', linewidth=1)
        plt.text(row['mean_urgency_norm'], row['total_benefit_years'], 
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=9, ha='left', weight='bold')
    
    plt.xlabel('Mean Recipient Urgency (normalized 0-1)\nHigher = sicker patients prioritized', fontsize=12)
    plt.ylabel('Total Survival Benefit (years)\nSum of years of life gained across all transplants', fontsize=12)
    title = f'Trade-off: Urgency vs Total Benefit\n{group_info}'
    plt.title(title, fontsize=13, fontweight='bold', pad=15)
    plt.grid(True, alpha=0.3)

    handle_no_fair = mlines.Line2D([], [], 
                                color='blue', marker='o', linestyle='None',
                                markersize=10, label='η=0: No fairness\n(Rank by medical score only)', 
                                markeredgecolor='black', markeredgewidth=1)

    handle_fair = mlines.Line2D([], [], 
                                color='red', marker='s', linestyle='None',
                                markersize=10, label='η=1: Fairness active\n(Prioritize underrepresented groups)',
                                markeredgecolor='black', markeredgewidth=1)

    plt.legend(handles=[handle_no_fair, handle_fair], loc='best', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'tradeoff_urgency_vs_benefit.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    # Plot 2: Fairness (L1 disparity) vs Total Benefit
    plt.figure(figsize=(11, 7))
    for _, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = 'blue'
        else:
            marker = 's'
            color = 'red'
        plt.scatter(row['fairness_L1'], row['total_benefit_years'], 
                   marker=marker, s=120, alpha=0.7, color=color, edgecolor='black', linewidth=1)
        plt.text(row['fairness_L1'], row['total_benefit_years'], 
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=9, ha='left', weight='bold')
    
    plt.xlabel('Allocation Disparity L1 (lower = more fair)\n0.0 = perfect fairness, 1.0 = maximum disparity', fontsize=12)
    plt.ylabel('Total Survival Benefit (years)', fontsize=12)
    title = f'Trade-off: Fairness vs Total Benefit\n{group_info}'
    plt.title(title, fontsize=13, fontweight='bold', pad=15)
    plt.grid(True, alpha=0.3)
    
    handle_no_fair = mlines.Line2D([], [], 
                                color='blue', marker='o', linestyle='None',
                                markersize=10, label='η=0: No fairness\n(Rank by medical score only)',
                                markeredgecolor='black', markeredgewidth=1)

    handle_fair = mlines.Line2D([], [], 
                                color='red', marker='s', linestyle='None',
                                markersize=10, label='η=1: Fairness active\n(Prioritize underrepresented groups)',
                                markeredgecolor='black', markeredgewidth=1)

    plt.legend(handles=[handle_no_fair, handle_fair], loc='best', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'tradeoff_fairness_vs_benefit.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    # Plot 3: Summary bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    x = range(len(df))
    colors = ['#2E86AB' if eta == 0 else '#C73E1D' for eta in df['fairness_eta']]

    labels = []
    for i, (policy, alpha) in enumerate(zip(df['policy'], df['alpha'])):
        if policy == "Urgency":
            labels.append("α=1.00")
        elif policy == "Utility":
            labels.append("α=0.00")
        elif policy in ["Hybrid", "Hybrid+Fair"]:
            labels.append(f"α={alpha:.2f}")
        else:
            labels.append("")

    # Subplot 1: Total benefit
    bars1 = ax1.bar(x, df['total_benefit_years'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Benefit (years)', fontsize=11, fontweight='bold')
    ax1.set_title(f'Total Survival Benefit by Configuration\n{group_info}', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')

    for i, (bar, val, eta) in enumerate(zip(bars1, df['total_benefit_years'], df['fairness_eta'])):
        height = bar.get_height()
        fairness_label = "η=1" if eta > 0 else "η=0"
        ax1.text(bar.get_x() + bar.get_width()/2., height + 300,
                f'{int(val)}\n{fairness_label}', ha='center', va='bottom', fontsize=8, weight='bold')

    # Subplot 2: Fairness L1
    bars2 = ax2.bar(x, df['fairness_L1'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax2.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Fairness L1 Disparity', fontsize=11, fontweight='bold')
    ax2.set_title(f'Allocation Disparity by Configuration\n{group_info}', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')

    for i, (bar, val, eta) in enumerate(zip(bars2, df['fairness_L1'], df['fairness_eta'])):
        height = bar.get_height()
        fairness_label = "η=1" if eta > 0 else "η=0"
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.0005,
                f'{val:.4f}\n{fairness_label}', ha='center', va='bottom', fontsize=8, weight='bold')

    blue_patch = mpatches.Patch(color='#2E86AB', label='η=0: No fairness\n(Rank by medical score)')
    red_patch = mpatches.Patch(color='#C73E1D', label='η=1: Fairness active\n(Prioritize underrepresented)')

    ax1.legend(handles=[blue_patch, red_patch], loc='upper right', fontsize=10, framealpha=0.9)
    ax2.legend(handles=[blue_patch, red_patch], loc='upper right', fontsize=10, framealpha=0.9)

    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'summary_bars.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()

    print(f"\n✅ Graphs generated with group information: {group_info}")

if __name__ == '__main__':
    main()

