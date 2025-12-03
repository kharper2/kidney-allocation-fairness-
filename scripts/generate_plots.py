#!/usr/bin/env python
"""
Generate plots for the kidney allocation paper.
"""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.lines as mlines
import matplotlib.patches as mpatches


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

    # Legend handles that match your plot markers
    handle_no_fair = mlines.Line2D([], [], 
                                color='blue', marker='o', linestyle='None',
                                markersize=8, label='η=0 (no fairness)')

    handle_fair = mlines.Line2D([], [], 
                                color='red', marker='s', linestyle='None',
                                markersize=8, label='η>0 (fairness-aware)')

    plt.legend(handles=[handle_no_fair, handle_fair], loc='best')
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
    # Legend handles that match your plot markers
    handle_no_fair = mlines.Line2D([], [], 
                                color='blue', marker='o', linestyle='None',
                                markersize=8, label='η=0 (no fairness)')

    handle_fair = mlines.Line2D([], [], 
                                color='red', marker='s', linestyle='None',
                                markersize=8, label='η>0 (fairness-aware)')

    plt.legend(handles=[handle_no_fair, handle_fair], loc='best')
    # plt.legend(['η=0 (no fairness)', 'η>0 (fairness-aware)'], loc='best')
    plt.tight_layout()
    outpath = os.path.join(args.outdir, 'tradeoff_fairness_vs_benefit.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    print(f"Saved {outpath}")
    plt.close()
    
    # Plot 3: Summary bar chart by policy
    plt.figure(figsize=(12, 6))
    x = range(len(df))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Colors by fairness
    colors = ['blue' if eta == 0 else 'red' for eta in df['fairness_eta']]

    # Create label text for each bar
    labels = []
    for i, (policy, alpha) in enumerate(zip(df['policy'], df['alpha'])):
        
        # Urgency baseline → α = 1
        if policy == "Urgency":
            labels.append("α=1.00")
        
        # Utility baseline → α = 0
        elif policy == "Utility":
            labels.append("α=0.00")
        
        # Hybrid & Hybrid+Fair → use actual alpha
        elif policy in ["Hybrid", "Hybrid+Fair"]:
            labels.append(f"α={alpha:.2f}")
        
        # Any others (e.g., WaitTime)
        else:
            labels.append("")
    # Subplot 1: Total benefit
    ax1.bar(x, df['total_benefit_years'], color=colors, alpha=0.7)
    ax1.set_xlabel('Configuration Index', fontsize=11)
    ax1.set_ylabel('Total Benefit (years)', fontsize=11)
    ax1.set_title('Total Survival Benefit by Configuration', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Add labels above bars (benefit)
    for i, (label, benefit) in enumerate(zip(labels, df['total_benefit_years'])):
        if label != "":
            ax1.text(i, benefit + 300, label, ha='center', fontsize=9)

    # Subplot 2: Fairness L1
    ax2.bar(x, df['fairness_L1'], color=colors, alpha=0.7)
    ax2.set_xlabel('Configuration Index', fontsize=11)
    ax2.set_ylabel('Fairness L1 Disparity', fontsize=11)
    ax2.set_title('Allocation Disparity by Configuration', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Add labels above bars (fairness)
    for i, (label, disparity) in enumerate(zip(labels, df['fairness_L1'])):
        if label != "":
            ax2.text(i, disparity + 0.0005, label, ha='center', fontsize=9)

    # Create legend handles
    blue_patch = mpatches.Patch(color='blue', label='η=0 (no fairness)')
    red_patch = mpatches.Patch(color='red', label='η>0 (fairness-aware)')

    # Legends
    ax1.legend(handles=[blue_patch, red_patch], loc='center right', fontsize=10)
    ax2.legend(handles=[blue_patch, red_patch], loc='center right', fontsize=10)

    plt.tight_layout()

    outpath = os.path.join(args.outdir, 'summary_bars.png')
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close()

    print("\nSummary statistics:")
    print(df.to_string())

if __name__ == '__main__':
    main()

