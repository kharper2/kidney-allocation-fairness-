#!/usr/bin/env python
"""
Run parameter sweep with multi-dimensional fairness.
Tracks deficits across multiple dimensions independently and combines with weights.
"""

import argparse
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_baselines import sweep_multidim

def main():
    ap = argparse.ArgumentParser(description='Multi-dimensional fairness parameter sweep')
    ap.add_argument('--patients', required=True, help='Path to patients CSV')
    ap.add_argument('--donors', required=True, help='Path to donors CSV')
    ap.add_argument('--sample_patients', type=int, default=20000, help='Number of patients to sample')
    ap.add_argument('--sample_donors', type=int, default=3000, help='Number of donors to sample')
    ap.add_argument('--alphas', type=float, nargs='+', default=[0.25, 0.5, 0.75], 
                    help='Alpha values (urgency/utility weight)')
    ap.add_argument('--etas', type=float, nargs='+', default=[0.0, 1.0], 
                    help='Eta values (fairness constraint strength)')
    ap.add_argument('--fairness_dims', type=str, nargs='+', default=['Ethnicity', 'SES'],
                    help='Dimensions to track for fairness (column names)')
    ap.add_argument('--fairness_weights', type=float, nargs='+', default=None,
                    help='Weights for each dimension (default: equal weights)')
    ap.add_argument('--seed', type=int, default=42, help='Random seed')
    ap.add_argument('--output', type=str, default='data/summary_multidim.csv', 
                    help='Output CSV file')
    args = ap.parse_args()
    
    # Default: equal weights
    if args.fairness_weights is None:
        args.fairness_weights = [1.0 / len(args.fairness_dims)] * len(args.fairness_dims)
    
    # Validate dimensions and weights match
    if len(args.fairness_dims) != len(args.fairness_weights):
        raise ValueError(f"Number of fairness_dims ({len(args.fairness_dims)}) must match "
                        f"number of fairness_weights ({len(args.fairness_weights)})")
    
    print(f"Running multi-dimensional fairness sweep...")
    print(f"Dimensions: {args.fairness_dims}")
    print(f"Weights: {args.fairness_weights}")
    print(f"Alphas: {args.alphas}")
    print(f"Etas: {args.etas}")
    print()
    
    # Run sweep
    df, allocs = sweep_multidim(
        args.patients, args.donors, 
        args.alphas, args.etas,
        sample_patients=args.sample_patients,
        sample_donors=args.sample_donors,
        seed=args.seed,
        fairness_dims=args.fairness_dims,
        fairness_weights=args.fairness_weights
    )
    
    # Save results
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    df.to_csv(args.output, index=False)
    
    print("Results:")
    print(df.to_string())
    print()
    print(f"Saved to: {args.output}")

if __name__ == '__main__':
    main()

