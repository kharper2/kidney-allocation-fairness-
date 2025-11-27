
import argparse, pandas as pd, os
from policy_baselines import sweep

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--patients', required=True)
    ap.add_argument('--donors', required=True)
    ap.add_argument('--sample_patients', type=int, default=20000)
    ap.add_argument('--sample_donors', type=int, default=3000)
    ap.add_argument('--alphas', type=float, nargs='+', default=[0.25,0.5,0.75])
    ap.add_argument('--etas', type=float, nargs='+', default=[0.0, 1.0])
    ap.add_argument('--group_col', type=str, default='Ethnicity')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--outdir', type=str, default='figures')
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df, allocs = sweep(args.patients, args.donors, args.alphas, args.etas,
                       sample_patients=args.sample_patients, sample_donors=args.sample_donors,
                       seed=args.seed, group_col=args.group_col)
    df.to_csv('data/summary.csv', index=False)
    # Minimal example figures left to the notebook or your plotting code
    print(df)

if __name__ == '__main__':
    main()
