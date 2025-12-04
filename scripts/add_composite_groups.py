#!/usr/bin/env python
"""
Create composite groups for multi-dimensional fairness analysis.
Combines multiple protected attributes (e.g., Ethnicity + Distance) into single group labels.

Extension: Multi-Dimensional Fairness
"""

import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description='Create composite fairness groups')
    ap.add_argument('--patients_in', required=True, help='Input patients CSV')
    ap.add_argument('--patients_out', required=True, help='Output patients CSV with composite groups')
    ap.add_argument('--columns', nargs='+', default=['Ethnicity', 'DistancetoCenterMiles'], 
                    help='Columns to combine (default: Ethnicity DistancetoCenterMiles)')
    ap.add_argument('--separator', default='_', help='Separator for composite labels (default: _)')
    args = ap.parse_args()
    
    # Read data
    df = pd.read_csv(args.patients_in)
    
    # Verify columns exist
    missing = [col for col in args.columns if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found in data: {missing}")
    
    # Create composite group column
    composite_name = args.separator.join(args.columns)
    df[composite_name] = df[args.columns].apply(
        lambda row: args.separator.join(row.astype(str)), axis=1
    )
    
    # Save
    df.to_csv(args.patients_out, index=False)
    
    # Report
    print(f"Created composite group column: '{composite_name}'")
    print(f"Number of unique groups: {df[composite_name].nunique()}")
    print(f"\nGroup distribution:")
    print(df[composite_name].value_counts().sort_index())
    print(f"\nSaved to: {args.patients_out}")

if __name__ == '__main__':
    main()

