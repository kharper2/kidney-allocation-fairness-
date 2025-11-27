
import argparse
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--patients_in', required=True)
    ap.add_argument('--patients_out', required=True)
    ap.add_argument('--probs', type=float, nargs=3, default=[0.25, 0.55, 0.20])
    args = ap.parse_args()
    df = pd.read_csv(args.patients_in)
    rng = np.random.default_rng(42)
    cats = ['Low','Middle','High']
    df['SES'] = rng.choice(cats, size=len(df), p=args.probs)
    df.to_csv(args.patients_out, index=False)
    print(f"Wrote {args.patients_out} with SES column.")

if __name__ == '__main__':
    main()
