#!/usr/bin/env python
"""
Analyze sweep results and generate tables for LaTeX paper.
"""
import argparse
import pandas as pd
import numpy as np

def format_latex_table(df, caption, label):
    """Generate LaTeX table from DataFrame."""
    latex = "\\begin{table}[h]\n"
    latex += "\\centering\n"
    latex += "\\caption{" + caption + "}\n"
    latex += "\\label{" + label + "}\n"
    latex += "\\begin{tabular}{l" + "c" * (len(df.columns) - 1) + "}\n"
    latex += "\\hline\n"
    
    # Header
    latex += " & ".join([str(col).replace("_", " ").title() for col in df.columns]) + " \\\\\n"
    latex += "\\hline\n"
    
    # Rows
    for _, row in df.iterrows():
        values = []
        for i, val in enumerate(row):
            if i == 0:  # Policy name
                values.append(str(val))
            elif isinstance(val, float):
                if val < 1:
                    values.append(f"{val:.4f}")
                else:
                    values.append(f"{val:.1f}")
            else:
                values.append(str(val))
        latex += " & ".join(values) + " \\\\\n"
    
    latex += "\\hline\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n"
    return latex

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--summary', type=str, default='data/summary.csv')
    ap.add_argument('--output', type=str, default='data/analysis.txt')
    args = ap.parse_args()
    
    df = pd.read_csv(args.summary)
    
    print("=" * 70)
    print("KIDNEY ALLOCATION POLICY ANALYSIS")
    print("=" * 70)
    print()
    
    # Overall summary
    print("Overall Summary:")
    print("-" * 70)
    print(df.to_string(index=False))
    print()
    
    # Best policies by metric
    print("Best Policies by Metric:")
    print("-" * 70)
    best_benefit = df.loc[df['total_benefit_years'].idxmax()]
    print(f"Highest Total Benefit: {best_benefit['policy']} "
          f"(α={best_benefit['alpha']:.2f}, η={best_benefit['fairness_eta']:.2f})")
    print(f"  → {best_benefit['total_benefit_years']:.1f} years")
    
    best_urgency = df.loc[df['mean_urgency_norm'].idxmax()]
    print(f"\nHighest Mean Urgency: {best_urgency['policy']} "
          f"(α={best_urgency['alpha']:.2f}, η={best_urgency['fairness_eta']:.2f})")
    print(f"  → {best_urgency['mean_urgency_norm']:.4f}")
    
    best_fairness = df.loc[df['fairness_L1'].idxmin()]
    print(f"\nLowest Disparity (Fairest): {best_fairness['policy']} "
          f"(α={best_fairness['alpha']:.2f}, η={best_fairness['fairness_eta']:.2f})")
    print(f"  → L1 = {best_fairness['fairness_L1']:.4f}")
    print()
    
    # Trade-off analysis
    print("Trade-off Analysis:")
    print("-" * 70)
    
    # Compare baseline policies
    urgency = df[(df['policy'] == 'Urgency') & (df['fairness_eta'] == 0)]
    utility = df[(df['policy'] == 'Utility') & (df['fairness_eta'] == 0)]
    
    if len(urgency) > 0 and len(utility) > 0:
        urgency = urgency.iloc[0]
        utility = utility.iloc[0]
        
        benefit_gain = utility['total_benefit_years'] - urgency['total_benefit_years']
        urgency_loss = urgency['mean_urgency_norm'] - utility['mean_urgency_norm']
        
        print(f"Utility vs Urgency:")
        print(f"  Benefit gain: +{benefit_gain:.1f} years ({benefit_gain/urgency['total_benefit_years']*100:.1f}%)")
        print(f"  Urgency loss: -{urgency_loss:.4f} ({urgency_loss/urgency['mean_urgency_norm']*100:.1f}%)")
        print()
    
    # Fairness impact
    no_fairness = df[df['fairness_eta'] == 0]
    with_fairness = df[df['fairness_eta'] > 0]
    
    if len(with_fairness) > 0:
        print("Fairness Constraint Impact:")
        print(f"  Without fairness (η=0): L1 = {no_fairness['fairness_L1'].mean():.4f}")
        print(f"  With fairness (η>0):    L1 = {with_fairness['fairness_L1'].mean():.4f}")
        improvement = (no_fairness['fairness_L1'].mean() - with_fairness['fairness_L1'].mean()) / no_fairness['fairness_L1'].mean() * 100
        print(f"  Improvement: {improvement:.1f}%")
        
        benefit_cost = no_fairness['total_benefit_years'].mean() - with_fairness['total_benefit_years'].mean()
        print(f"  Benefit cost: -{benefit_cost:.1f} years ({benefit_cost/no_fairness['total_benefit_years'].mean()*100:.1f}%)")
        print()
    
    # Alpha (λ) sensitivity
    hybrid_only = df[(df['policy'] == 'Hybrid') & (df['fairness_eta'] == 0)]
    if len(hybrid_only) > 0:
        print("Alpha (λ) Sensitivity (Hybrid policies, η=0):")
        for _, row in hybrid_only.iterrows():
            print(f"  α={row['alpha']:.2f}: Benefit={row['total_benefit_years']:.1f}, "
                  f"Urgency={row['mean_urgency_norm']:.4f}, L1={row['fairness_L1']:.4f}")
        print()
    
    # Generate LaTeX tables
    print("=" * 70)
    print("LaTeX Tables (save to paper/):")
    print("=" * 70)
    print()
    
    # Table 1: Main results
    table_df = df[['policy', 'alpha', 'fairness_eta', 'total_benefit_years', 
                    'mean_urgency_norm', 'fairness_L1', 'n_assigned']].copy()
    table_df.columns = ['Policy', 'α', 'η', 'Benefit (yr)', 'Urgency', 'L1', 'N']
    
    latex_table = format_latex_table(table_df, 
                                     "Allocation policy performance across metrics.", 
                                     "tab:results")
    print(latex_table)
    print()
    
    # Pareto frontier analysis
    print("Pareto Frontier Analysis:")
    print("-" * 70)
    
    # Check for domination in benefit-urgency space
    pareto = []
    for i, row_i in df.iterrows():
        dominated = False
        for j, row_j in df.iterrows():
            if i != j:
                # row_j dominates row_i if it's better in both metrics
                if (row_j['total_benefit_years'] >= row_i['total_benefit_years'] and 
                    row_j['mean_urgency_norm'] >= row_i['mean_urgency_norm'] and
                    (row_j['total_benefit_years'] > row_i['total_benefit_years'] or 
                     row_j['mean_urgency_norm'] > row_i['mean_urgency_norm'])):
                    dominated = True
                    break
        if not dominated:
            pareto.append(i)
    
    print(f"Pareto-optimal policies (benefit-urgency): {len(pareto)}/{len(df)}")
    for idx in pareto:
        row = df.iloc[idx]
        print(f"  {row['policy']} (α={row['alpha']:.2f}, η={row['fairness_eta']:.2f}): "
              f"Benefit={row['total_benefit_years']:.1f}, Urgency={row['mean_urgency_norm']:.4f}")
    print()
    
    # Save to file
    with open(args.output, 'w') as f:
        f.write("KIDNEY ALLOCATION POLICY ANALYSIS\n")
        f.write("=" * 70 + "\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("LATEX TABLE\n")
        f.write("=" * 70 + "\n\n")
        f.write(latex_table)
    
    print(f"Analysis saved to: {args.output}")

if __name__ == '__main__':
    main()

