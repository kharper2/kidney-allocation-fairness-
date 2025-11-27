
import numpy as np
import pandas as pd
from collections import Counter

ABO_RECIPIENTS = {
    'O': ['O', 'A', 'B', 'AB'],
    'A': ['A', 'AB'],
    'B': ['B', 'AB'],
    'AB': ['AB']
}

def compute_patient_features(df: pd.DataFrame):
    out = df.copy()
    out['EPTS_norm'] = out['EPTSScore'].clip(0,100) / 100.0
    out['Age80'] = np.minimum(out['Age'], 80.0) / 80.0
    urg_raw = np.log1p(out['DialysisYears'].clip(lower=0.0)) + 0.3 * out['Diabetes'].astype(float)
    umin, umax = urg_raw.min(), urg_raw.max()
    out['Urgency_norm'] = (urg_raw - umin) / (umax - umin + 1e-9)
    no_tx = 5.0 - 0.6 * out['DialysisYears'] - 1.0 * out['Diabetes'].astype(float) - 0.5 * out['Age80']
    out['NoTx'] = np.maximum(0.0, no_tx)
    E = out['EPTS_norm'].values
    Age80 = out['Age80'].values
    out['A_part'] = 6.0 * (1.0 - E) + 1.0 * (1.0 - Age80) - out['NoTx'].values
    out['B_part'] = 2.0 * (1.0 - E)
    return out

def bin_index(x, n_bins=10):
    i = int(np.floor(x * n_bins))
    if i >= n_bins: i = n_bins - 1
    if i < 0: i = 0
    return i

def build_sorted_lists(pat_df: pd.DataFrame, policy: str, alpha: float = 0.5, n_bins: int = 10):
    lists = {abo: {b: [] for b in range(n_bins)} for abo in ['O','A','B','AB']}
    U = pat_df['Urgency_norm'].values.astype(float)
    A = pat_df['A_part'].values.astype(float)
    B = pat_df['B_part'].values.astype(float)
    idx_by_abo = {abo: np.where(pat_df['BloodType'].values == abo)[0] for abo in ['O','A','B','AB']}
    for b in range(n_bins):
        x = (b + 0.5) / n_bins
        util_key = A + B * x
        kmin, kmax = util_key.min(), util_key.max()
        util_norm = (util_key - kmin) / (kmax - kmin + 1e-9)
        if policy == 'urgency':
            key = U
        elif policy == 'utility':
            key = util_norm
        elif policy == 'hybrid':
            key = alpha * U + (1.0 - alpha) * util_norm
        else:
            raise ValueError("Unknown policy")
        for abo in ['O','A','B','AB']:
            idxs = idx_by_abo[abo]
            order = np.argsort(-key[idxs], kind='mergesort')
            lists[abo][b] = idxs[order].tolist()
    return lists

def exact_utility_for_pair(pat_df_row, kdpi_norm):
    E = float(pat_df_row['EPTS_norm']); K = float(kdpi_norm); Age80 = float(pat_df_row['Age80'])
    theta0,theta1,theta2,theta3,theta4 = 5.0, 6.0, 3.0, 1.0, 2.0
    post = theta0 + theta1*(1.0-E) + theta2*(1.0-K) + theta3*(1.0-Age80) + theta4*(1.0-E)*(1.0-K)
    no_tx = float(pat_df_row['NoTx'])
    util = max(post - no_tx, 0.0)
    return util, post, no_tx

def allocate(don_df: pd.DataFrame, pat_df: pd.DataFrame, policy: str, alpha: float = 0.5, fairness_eta: float = 0.0, n_bins: int = 10, group_col: str = 'Ethnicity'):
    sorted_lists = build_sorted_lists(pat_df, policy, alpha, n_bins)
    available = np.ones(len(pat_df), dtype=bool)
    heads = {abo: {b: 0 for b in range(n_bins)} for abo in ['O','A','B','AB']}
    # Groups
    if group_col in pat_df.columns:
        groups = pat_df[group_col].astype(str).values
        gv, gc = np.unique(groups, return_counts=True)
        p_share = {g: gc[i] / len(groups) for i,g in enumerate(gv)}
    else:
        groups = np.array(['All']*len(pat_df))
        p_share = {'All': 1.0}
    alloc_counts = Counter({g: 0 for g in p_share.keys()})
    U = pat_df['Urgency_norm'].values.astype(float)
    records = []
    for d_idx,row in don_df.iterrows():
        donor_bt = str(row['DonorBloodType'])
        try:
            kdpi = float(row['KDPI'])
        except:
            kdpi = float(pd.to_numeric(row['KDPI'], errors='coerce'))
        K_norm = np.clip(kdpi, 0.0, 100.0) / 100.0
        x = 1.0 - K_norm
        b = bin_index(x, n_bins)
        recipient_abos = ABO_RECIPIENTS.get(donor_bt, [])
        restrict_group = None
        if fairness_eta > 0 and len(records) > 0:
            total_alloc = len(records)
            deficits = {g: p_share[g]*total_alloc - alloc_counts[g] for g in p_share.keys()}
            g_star, max_def = max(deficits.items(), key=lambda kv: kv[1])
            if max_def > 0:
                restrict_group = g_star
        best_score, best_i, best_abo = -np.inf, None, None
        for abo in recipient_abos:
            lst = sorted_lists[abo][b]
            h = heads[abo][b]
            while h < len(lst) and (not available[lst[h]] or (restrict_group is not None and groups[lst[h]] != restrict_group)):
                h += 1
            heads[abo][b] = h
            if h >= len(lst): continue
            i = lst[h]
            if policy == 'urgency':
                score = U[i]
            else:
                util, post, no_tx = exact_utility_for_pair(pat_df.iloc[i], K_norm)
                if policy == 'utility':
                    score = util
                elif policy == 'hybrid':
                    util_norm = util / 12.0
                    score = alpha * U[i] + (1.0 - alpha) * util_norm
                else:
                    score = util
            if score > best_score:
                best_score, best_i, best_abo = score, i, abo
        if best_i is None: 
            continue
        available[best_i] = False
        heads[best_abo][b] += 1
        util, post, no_tx = exact_utility_for_pair(pat_df.iloc[best_i], K_norm)
        records.append({
            'donor_index': d_idx, 'donor_bt': donor_bt, 'donor_kdpi': kdpi,
            'recipient_index': int(best_i), 'recipient_bt': pat_df.iloc[best_i]['BloodType'],
            'recipient_group': groups[best_i], 'urgency_norm': U[best_i],
            'utility_years': util, 'post_years': post, 'no_tx_years': no_tx,
            'policy': policy, 'alpha': alpha, 'fairness_eta': fairness_eta, 'group_col': group_col
        })
        alloc_counts[groups[best_i]] += 1
    alloc_df = pd.DataFrame(records)
    if len(alloc_df)==0:
        return alloc_df, {}
    total_benefit = alloc_df['utility_years'].sum()
    mean_urg = alloc_df['urgency_norm'].mean()
    alloc_share = alloc_df['recipient_group'].value_counts(normalize=True).to_dict()
    for g in p_share.keys():
        alloc_share.setdefault(g, 0.0)
    disparity = 0.5 * sum(abs(alloc_share[g] - p_share[g]) for g in p_share.keys())
    metrics = {'total_benefit_years': total_benefit, 'mean_urgency_norm': mean_urg, 'fairness_L1': disparity, 'n_assigned': len(alloc_df)}
    return alloc_df, metrics

def run_experiment(patients_csv: str, donors_csv: str, sample_patients: int = 20000, sample_donors: int = 3000, seed: int = 42, group_col: str = 'Ethnicity'):
    patients = pd.read_csv(patients_csv).sample(n=sample_patients, random_state=seed).reset_index(drop=True)
    donors = pd.read_csv(donors_csv).sample(n=sample_donors, random_state=seed).reset_index(drop=True)
    patients_feat = compute_patient_features(patients)
    results = []; allocations = {}
    # Urgency
    alloc, metr = allocate(donors, patients_feat, 'urgency', alpha=1.0, fairness_eta=0.0, group_col=group_col)
    metr['policy']='Urgency'; metr['alpha']=1.0; metr['fairness_eta']=0.0
    results.append(metr); allocations[('Urgency',1.0,0.0)] = alloc
    # Utility
    alloc, metr = allocate(donors, patients_feat, 'utility', alpha=0.0, fairness_eta=0.0, group_col=group_col)
    metr['policy']='Utility'; metr['alpha']=0.0; metr['fairness_eta']=0.0
    results.append(metr); allocations[('Utility',0.0,0.0)] = alloc
    # Hybrid
    for a in [0.25,0.5,0.75]:
        alloc, metr = allocate(donors, patients_feat, 'hybrid', alpha=a, fairness_eta=0.0, group_col=group_col)
        metr['policy']='Hybrid'; metr['alpha']=a; metr['fairness_eta']=0.0
        results.append(metr); allocations[('Hybrid',a,0.0)] = alloc
    # Fairness-constrained example
    alloc, metr = allocate(donors, patients_feat, 'hybrid', alpha=0.5, fairness_eta=1.0, group_col=group_col)
    metr['policy']='Hybrid+Fair'; metr['alpha']=0.5; metr['fairness_eta']=1.0
    results.append(metr); allocations[('Hybrid+Fair',0.5,1.0)] = alloc
    return pd.DataFrame(results), allocations

def sweep(patients_csv: str, donors_csv: str, alphas, etas, sample_patients: int = 20000, sample_donors: int = 3000, seed: int = 42, group_col: str = 'Ethnicity'):
    patients = pd.read_csv(patients_csv).sample(n=sample_patients, random_state=seed).reset_index(drop=True)
    donors = pd.read_csv(donors_csv).sample(n=sample_donors, random_state=seed).reset_index(drop=True)
    patients_feat = compute_patient_features(patients)
    out = []; allocs = {}
    # Always include urgency-only and utility-only
    for policy, a, e in [('urgency',1.0,0.0), ('utility',0.0,0.0)]:
        alloc, metr = allocate(donors, patients_feat, policy, alpha=a, fairness_eta=e, group_col=group_col)
        metr['policy']=policy.title() if policy!='utility' else 'Utility'
        metr['alpha']=a; metr['fairness_eta']=e
        out.append(metr); allocs[(metr['policy'],a,e)] = alloc
    # Hybrid grid
    for a in alphas:
        for e in etas:
            alloc, metr = allocate(donors, patients_feat, 'hybrid', alpha=a, fairness_eta=e, group_col=group_col)
            metr['policy']='Hybrid' if e==0 else 'Hybrid+Fair'
            metr['alpha']=a; metr['fairness_eta']=e
            out.append(metr); allocs[(metr['policy'],a,e)] = alloc
    return pd.DataFrame(out), allocs
