#!/usr/bin/env python
"""
Generate a comprehensive summary graph showing all policies side-by-side.
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.patches as mpatches

def get_group_info(group_col, patients_csv=None):
    """Get information about which groups are being compared."""
    if group_col == 'Ethnicity':
        return 'Ethnicity: Hispanic, Black, White, Asian, Other (5 groups)'
    elif group_col == 'Sex':
        return 'Sex: M, F (2 groups)'
    elif group_col == 'DistancetoCenterMiles':
        return 'Distance: <50, 50-100, 100-150, 150-250, >250 miles (5 groups)'
    elif 'Ethnicity_DistancetoCenterMiles' in str(group_col) or 'Ethnicity_Distance' in str(group_col):
        return 'Composite: Ethnicity × Distance (25 intersectional groups)'
    elif 'multidim' in str(group_col).lower() or '+' in str(group_col):
        return 'Multidim: Multiple dimensions with weights'
    else:
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
    
    # Create comprehensive summary figure
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # Colors
    colors = ['#2E86AB' if eta == 0 else '#C73E1D' for eta in df['fairness_eta']]
    
    # 1. Total Benefit by Policy (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    x_pos = np.arange(len(df))
    bars1 = ax1.bar(x_pos, df['total_benefit_years'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax1.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Total Benefit (years)', fontsize=11, fontweight='bold')
    ax1.set_title('Total Survival Benefit', fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, df['total_benefit_years'])):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 200,
                f'{int(val)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 2. Fairness L1 by Policy (top middle)
    ax2 = fig.add_subplot(gs[0, 1])
    bars2 = ax2.bar(x_pos, df['fairness_L1'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax2.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Fairness L1 Disparity', fontsize=11, fontweight='bold')
    ax2.set_title('Allocation Fairness (lower is better)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, df['fairness_L1'])):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.002,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 3. Mean Urgency by Policy (top right)
    ax3 = fig.add_subplot(gs[0, 2])
    bars3 = ax3.bar(x_pos, df['mean_urgency_norm'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax3.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Mean Recipient Urgency', fontsize=11, fontweight='bold')
    ax3.set_title('Mean Urgency of Recipients', fontsize=12, fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax3.grid(True, alpha=0.3, axis='y')
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars3, df['mean_urgency_norm'])):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{val:.3f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # 4. Organs Used (bottom left)
    ax4 = fig.add_subplot(gs[1, 0])
    bars4 = ax4.bar(x_pos, df['n_assigned'], color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    ax4.set_xlabel('Policy Configuration', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Organs Assigned', fontsize=11, fontweight='bold')
    ax4.set_title('Organs Successfully Allocated', fontsize=12, fontweight='bold')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([f"{row['policy']}\nα={row['alpha']:.2f}" for _, row in df.iterrows()], 
                        rotation=45, ha='right', fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars4, df['n_assigned'])):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{int(val)}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 5. Fairness vs Benefit Trade-off (bottom middle)
    ax5 = fig.add_subplot(gs[1, 1])
    for i, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = '#2E86AB'
            size = 150
        else:
            marker = 's'
            color = '#C73E1D'
            size = 150
        ax5.scatter(row['fairness_L1'], row['total_benefit_years'], 
                   marker=marker, s=size, color=color, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax5.text(row['fairness_L1'], row['total_benefit_years'] + 200,
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=8, ha='left')
    ax5.set_xlabel('Fairness L1 Disparity (lower = fairer)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Total Benefit (years)', fontsize=11, fontweight='bold')
    ax5.set_title('Fairness vs Benefit Trade-off', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.invert_xaxis()  # Lower disparity (better) on right
    
    # 6. Urgency vs Benefit Trade-off (bottom right)
    ax6 = fig.add_subplot(gs[1, 2])
    for i, row in df.iterrows():
        if row['fairness_eta'] == 0:
            marker = 'o'
            color = '#2E86AB'
            size = 150
        else:
            marker = 's'
            color = '#C73E1D'
            size = 150
        ax6.scatter(row['mean_urgency_norm'], row['total_benefit_years'], 
                   marker=marker, s=size, color=color, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax6.text(row['mean_urgency_norm'], row['total_benefit_years'] + 200,
                f" {row['policy']}\n α={row['alpha']:.2f}", 
                fontsize=8, ha='left')
    ax6.set_xlabel('Mean Recipient Urgency', fontsize=11, fontweight='bold')
    ax6.set_ylabel('Total Benefit (years)', fontsize=11, fontweight='bold')
    ax6.set_title('Urgency vs Benefit Trade-off', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # Add legend
    blue_patch = mpatches.Patch(color='#2E86AB', label='η=0: No fairness\n(Rank by medical score)')
    red_patch = mpatches.Patch(color='#C73E1D', label='η=1: Fairness active\n(Prioritize underrepresented)')
    fig.legend(handles=[blue_patch, red_patch], loc='upper center', ncol=2, fontsize=11, framealpha=0.9)
    
    # Overall title
    fig.suptitle(f'Comprehensive Policy Comparison\n{group_info}', fontsize=15, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    outpath = os.path.join(args.outdir, 'comprehensive_summary.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"✅ Saved {outpath}")
    plt.close()
    
    print(f"\nSummary: {len(df)} configurations plotted")
    print(f"Best benefit: {df.loc[df['total_benefit_years'].idxmax(), 'policy']} ({df['total_benefit_years'].max():.0f} years)")
    print(f"Best fairness: {df.loc[df['fairness_L1'].idxmin(), 'policy']} (L1={df['fairness_L1'].min():.4f})")

if __name__ == '__main__':
    main()

