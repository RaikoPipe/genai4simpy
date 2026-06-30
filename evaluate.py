"""
Generic Multi-Replication Evaluation Harness  (corrected)
=========================================================

Model-agnostic implementation of Stage-2 of the evaluation methodology
(sections 2.2-2.5). Takes ANY simulation model that satisfies the output
contract (see CONTRACT below) plus ANY ground-truth file of the standard
structure, runs m replications, and reports KPIs / CIs / coverage / ratings / Q.

    python evaluate.py --model my_model.py --ground-truth ground_truth_block_A.py -n 30

--------------------------------------------------------------------------
CONTRACT - the generated model module MUST provide:
--------------------------------------------------------------------------
  run_single_replication(seed: int) -> pandas.DataFrame
      Returns a standard event log (one row per executed activity instance,
      INCLUDING rework rows for failures). May also return (df, anything);
      only the first element is used. Must seed `random` and `np.random`
      from `seed` so replications are reproducible and independent.

  SIMULATION_TIME : int   (optional)  sim horizon in seconds. The harness
      overrides this to the ground-truth observation window when available.

  RESOURCE_CAPACITIES : dict[str,int]  (optional) concrete-resource -> capacity.
      If absent, every concrete resource is assumed capacity 1.

Standard event-log columns (exact names):
  case_id            hashable     workpiece / case identifier
  variant            str          variant label (matches GT variant keys)
  activity           str          activity name (matches GT activity keys)
  resource           str          concrete resource that executed the step
  time:timestamp     float        case/step ENQUEUE time (sim-seconds from 0).
                                  Used as the case-arrival timestamp for flow
                                  time and IAT.
  service_start      float        OPTIONAL. Time the resource was acquired and
                                  service began (sim-seconds). Used for activity
                                  durations and utilisation. If absent, the
                                  harness falls back to time:timestamp, which is
                                  correct only for models without queueing.
  operation_end_time float        execution end, sim-seconds from 0
  lifecycle:state    str          'success' | 'failure'
  response_status_code int        optional (e.g. 200 / 418 / 401)

--------------------------------------------------------------------------
GROUND-TRUTH structure consumed:
--------------------------------------------------------------------------
  throughput                 int               cases observed in window
  observation_period_s       float
  failure_rate               float
  variant_distribution       dict[str,float]   (proportions)
  activity_mean_durations_s  dict[str,float]   service-time means
  mean_flow_time_s           float | None      (optional)
  terminal_activity          str   | None      (optional) activity marking case
                                                completion. If present, throughput
                                                is measured as COMPLETED cases
                                                (methodology 2.2). If absent,
                                                falls back to cases observed.
  completed_cases            int   | None      (optional) GT completed count, used
                                                when terminal_activity is set.
  resource_utilization       dict[str,float]|None (optional) per-resource % busy,
                                                enables utilisation error scoring.
  iat_values_s               list[float] | None (optional) observed inter-arrival
                                                samples, enables the IAT KS test.
"""

import argparse
import importlib.util
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

REQUIRED_COLS = {
    'case_id', 'variant', 'activity', 'resource',
    'time:timestamp', 'operation_end_time', 'lifecycle:state',
}

# Methodology-defined, dataset-independent (section 2.4)
THRESHOLDS = {
    'throughput_accuracy':    {'excellent': 5,    'good': 7,    'acceptable': 10},
    'mean_flow_time_error':   {'excellent': 5,    'good': 10,   'acceptable': 15},
    'variant_jsd':            {'excellent': 0.01, 'good': 0.02, 'acceptable': 0.05},
    'activity_duration_mape': {'excellent': 10,   'good': 15,   'acceptable': 20},
}

# KPI weights for the aggregated quality score Q (section 2.5).
# 'coverage' KPIs score on CI coverage of a GT point value; 'threshold' KPIs
# (error metrics with target -> 0) score on their accuracy rating.
Q_SPEC = {
    'throughput_total':       {'weight': 0.30, 'mode': 'coverage'},
    'mean_flow_time_s':       {'weight': 0.20, 'mode': 'coverage'},
    'failure_rate':           {'weight': 0.15, 'mode': 'coverage'},
    'variant_jsd':            {'weight': 0.15, 'mode': 'threshold',
                               'rating_key': 'variant_jsd'},
    'activity_duration_mape': {'weight': 0.20, 'mode': 'threshold',
                               'rating_key': 'activity_duration_mape'},
}


# ============================================================================
# LOADING / VALIDATION
# ============================================================================

def _load_module(path):
    spec = importlib.util.spec_from_file_location("_loaded", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_ground_truth(path):
    if path.endswith('.json'):
        with open(path) as f:
            return json.load(f)
    mod = _load_module(path)
    if not hasattr(mod, 'GROUND_TRUTH'):
        raise AttributeError(f"{path} has no GROUND_TRUTH dict")
    return mod.GROUND_TRUTH


def load_model(path):
    mod = _load_module(path)
    if not hasattr(mod, 'run_single_replication'):
        raise AttributeError(f"{path} must expose run_single_replication(seed)")
    return mod


def validate_log(df, where=""):
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{where}: run_single_replication must return a DataFrame")
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"{where}: event log missing columns {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{where}: event log is empty")


def _service_span(df):
    """Service duration per row: operation_end_time - service_start.

    Falls back to time:timestamp when service_start is absent (correct only for
    models without queueing). Returns a Series aligned to df.index.
    """
    start = df['service_start'] if 'service_start' in df.columns else df['time:timestamp']
    return df['operation_end_time'] - start


# ============================================================================
# KPI COMPUTATION  (ground-truth-driven, so it generalises across datasets)
# ============================================================================

def jensen_shannon_divergence(p, q, labels):
    pv = np.array([p.get(l, 0.0) for l in labels], dtype=float)
    qv = np.array([q.get(l, 0.0) for l in labels], dtype=float)
    pv = pv / pv.sum() if pv.sum() > 0 else pv
    qv = qv / qv.sum() if qv.sum() > 0 else qv
    m = 0.5 * (pv + qv)
    with np.errstate(divide='ignore', invalid='ignore'):
        kl_pm = np.where(pv > 0, pv * np.log2(pv / m), 0)
        kl_qm = np.where(qv > 0, qv * np.log2(qv / m), 0)
    return float(0.5 * kl_pm.sum() + 0.5 * kl_qm.sum())


def compute_kpis(df, gt, sim_time, capacities):
    k = {}

    # ---- Throughput -------------------------------------------------------
    # Methodology 2.2: throughput = COMPLETED workpieces. If the GT declares a
    # terminal activity, count cases that reached it; otherwise fall back to
    # cases observed (and compare against gt['throughput']).
    terminal = gt.get('terminal_activity')
    if terminal:
        completed_mask = ((df['activity'] == terminal) &
                          (df['lifecycle:state'] == 'success'))
        total = int(df.loc[completed_mask, 'case_id'].nunique())
        gt_throughput = gt.get('completed_cases', gt['throughput'])
        k['throughput_basis'] = 'completed'
    else:
        total = int(df['case_id'].nunique())
        gt_throughput = gt['throughput']
        k['throughput_basis'] = 'observed'
    k['throughput_total'] = total
    k['throughput_gt'] = gt_throughput
    k['throughput_accuracy_pct'] = (abs(total - gt_throughput) / gt_throughput * 100
                                    if gt_throughput else float('nan'))

    # Also expose cases observed (entered) for reference.
    k['cases_observed'] = int(df['case_id'].nunique())

    # ---- Mean flow time ---------------------------------------------------
    # Arrival = first enqueue (time:timestamp); completion = last end.
    # When a terminal_activity is defined, compute flow time only for COMPLETED
    # cases (those reaching the terminal activity with success), since the GT
    # flow time is measured end-to-end for finished workpieces.
    ct = df.groupby('case_id').agg(a=('time:timestamp', 'min'),
                                   d=('operation_end_time', 'max'))
    if terminal:
        completed_ids = df.loc[completed_mask, 'case_id'].unique()
        ct_flow = ct.loc[ct.index.isin(completed_ids)]
    else:
        ct_flow = ct
    k['mean_flow_time_s'] = float((ct_flow['d'] - ct_flow['a']).mean()) if len(ct_flow) else float('nan')
    gt_ft = gt.get('mean_flow_time_s')
    k['mean_flow_time_error_pct'] = (
        abs(k['mean_flow_time_s'] - gt_ft) / gt_ft * 100 if gt_ft else float('nan'))

    # ---- Variant distribution (JSD) --------------------------------------
    sim_dist = df.groupby('case_id')['variant'].first().value_counts(normalize=True).to_dict()
    labels = sorted(set(gt['variant_distribution']) | set(sim_dist))
    k['variant_jsd'] = jensen_shannon_divergence(sim_dist, gt['variant_distribution'], labels)

    # ---- Per-activity duration MAPE --------------------------------------
    # Service span, SUCCESS rows only (matches GT start-event service durations).
    d = df.copy()
    d['dur'] = _service_span(d)
    succ = d[d['lifecycle:state'] == 'success']
    sim_means = succ.groupby('activity')['dur'].mean()
    apes, per_act = [], {}
    for act, gt_mean in gt['activity_mean_durations_s'].items():
        if act in sim_means.index and gt_mean > 0:
            ape = abs(sim_means[act] - gt_mean) / gt_mean * 100
            apes.append(ape); per_act[act] = ape
    k['activity_duration_mape'] = float(np.mean(apes)) if apes else float('nan')
    k['per_activity_error'] = per_act

    # ---- Failure rate -----------------------------------------------------
    # Denominator = total complete events (success + failure rows) = GT basis.
    n = len(df)
    k['failure_rate'] = float((df['lifecycle:state'] == 'failure').sum() / n) if n else 0.0
    # Absolute difference in PERCENTAGE POINTS (named accordingly).
    k['failure_rate_diff_pp'] = abs(k['failure_rate'] - gt['failure_rate']) * 100

    # ---- Resource utilisation --------------------------------------------
    # Busy time = service span held on the resource (success + failure, since a
    # failed attempt still occupies the resource). Uses service_start, so queue
    # wait is excluded.
    busy = d.assign(_b=_service_span(d)).groupby('resource')['_b'].sum()
    util = {r: float(b / (capacities.get(r, 1) * sim_time) * 100) for r, b in busy.items()}
    k['resource_utilization'] = util
    gt_util = gt.get('resource_utilization')
    if gt_util:
        errs = [abs(util.get(r, 0.0) - u) for r, u in gt_util.items()]
        k['resource_util_mae'] = float(np.mean(errs)) if errs else float('nan')
    else:
        k['resource_util_mae'] = float('nan')

    # ---- Inter-arrival times ---------------------------------------------
    arr = df.groupby('case_id')['time:timestamp'].min().sort_values()
    iats = arr.diff().dropna().values
    k['iat_mean_s'] = float(np.mean(iats)) if len(iats) else float('nan')
    k['iat_median_s'] = float(np.median(iats)) if len(iats) else float('nan')
    k['iat_values'] = iats
    return k


# ============================================================================
# STATISTICS  (sections 2.3-2.5)
# ============================================================================

def confidence_interval(values, alpha=0.05):
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n == 0:
        return (np.nan,) * 5
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    if n < 2 or std == 0:
        return mean, mean, mean, 0.0, std
    hw = sp_stats.t.ppf(1 - alpha / 2, df=n - 1) * std / np.sqrt(n)
    return mean, mean - hw, mean + hw, hw, std


def rate(value, t):
    if np.isnan(value):
        return 'N/A'
    if value <= t['excellent']:
        return 'EXCELLENT'
    if value <= t['good']:
        return 'GOOD'
    if value <= t['acceptable']:
        return 'ACCEPTABLE'
    return 'BELOW THRESHOLD'


def ks_test_iat(reps, gt):
    """Two-sample KS test pooling simulated IATs vs observed IATs (2.2)."""
    obs = gt.get('iat_values_s')
    if not obs:
        return None
    sim = np.concatenate([r['iat_values'] for r in reps if len(r['iat_values'])])
    if len(sim) == 0:
        return None
    stat, p = sp_stats.ks_2samp(sim, np.asarray(obs, dtype=float))
    return {'ks_stat': float(stat), 'p_value': float(p), 'pass': bool(p > 0.05)}


# ============================================================================
# RUNNER + ANALYSIS
# ============================================================================

def run_replications(model, m, base_seed, sim_time, verbose):
    caps = getattr(model, 'RESOURCE_CAPACITIES', {})
    reps = []
    for i in range(m):
        seed = base_seed + i
        out = model.run_single_replication(seed)
        df = out[0] if isinstance(out, tuple) else out
        validate_log(df, where=f"seed {seed}")
        k = compute_kpis(df, model._GT, sim_time, caps)
        k['seed'] = seed
        reps.append(k)
        if verbose and (i + 1) % 10 == 0:
            print(f"  {i+1}/{m} replications")
    return reps


def analyse(reps, gt, verbose=True):
    res = {'n_replications': len(reps)}
    vectors = {n: [r[n] for r in reps] for n in
               ['throughput_total', 'throughput_accuracy_pct', 'mean_flow_time_s',
                'mean_flow_time_error_pct', 'variant_jsd', 'activity_duration_mape',
                'failure_rate', 'failure_rate_diff_pp', 'iat_mean_s', 'iat_median_s',
                'resource_util_mae']}

    ci = {}
    for name, vals in vectors.items():
        mean, lo, hi, hw, std = confidence_interval(vals)
        ci[name] = {'mean': mean, 'ci_lower': lo, 'ci_upper': hi,
                    'half_width': hw, 'std': std}
    res['confidence_intervals'] = ci

    # --- Coverage (does GT point value fall inside the between-replication CI?)
    # NOTE: with a single generated model this is a WITHIN-MODEL CI (simulation
    # stochasticity only). The methodology's coverage test uses the BETWEEN-MODEL
    # CI across k pipeline runs; wrap this harness in a k-run loop for that.
    gt_throughput = reps[0]['throughput_gt'] if reps else gt['throughput']
    gt_map = {'throughput_total': gt_throughput,
              'failure_rate': gt['failure_rate']}
    if gt.get('mean_flow_time_s') is not None:
        gt_map['mean_flow_time_s'] = gt['mean_flow_time_s']
    res['coverage'] = {n: {'ground_truth': v,
                           'ci': [ci[n]['ci_lower'], ci[n]['ci_upper']],
                           'covered': bool(ci[n]['ci_lower'] <= v <= ci[n]['ci_upper'])}
                       for n, v in gt_map.items()}

    # --- Accuracy ratings
    rmap = {'throughput_accuracy_pct': 'throughput_accuracy',
            'mean_flow_time_error_pct': 'mean_flow_time_error',
            'variant_jsd': 'variant_jsd',
            'activity_duration_mape': 'activity_duration_mape'}
    res['ratings'] = {n: {'value': ci[n]['mean'], 'rating': rate(ci[n]['mean'], THRESHOLDS[t])}
                      for n, t in rmap.items()}

    # --- Inter-arrival KS test (2.2)
    ks = ks_test_iat(reps, gt)
    if ks is not None:
        res['iat_ks_test'] = ks

    # --- Aggregated quality score Q (2.5)
    # coverage-mode KPIs award weight if GT in CI; threshold-mode KPIs award
    # weight if their rating is ACCEPTABLE or better (i.e. error <= acceptable).
    q, details = 0.0, {}
    for n, spec in Q_SPEC.items():
        w = spec['weight']
        if spec['mode'] == 'coverage':
            passed = res['coverage'].get(n, {}).get('covered')
        else:  # threshold
            thr = THRESHOLDS[spec['rating_key']]
            passed = bool(ci[n]['mean'] <= thr['acceptable']) if not np.isnan(ci[n]['mean']) else False
        contrib = w if passed else 0.0
        q += contrib
        details[n] = {'weight': w, 'mode': spec['mode'],
                      'passed': bool(passed), 'contribution': contrib}
    res['quality_score'] = {'Q': round(q, 4),
                            'max_possible': round(sum(s['weight'] for s in Q_SPEC.values()), 4),
                            'details': details}
    if verbose:
        _report(res, gt)
    return res


def build_comparison(res, gt):
    """Assemble a single ground-truth-vs-result row per KPI.

    Each row: (label, gt_value, sim_mean, ci_str, delta_str, verdict). Error-
    metric KPIs (target -> 0) carry their ideal target as ground truth so the
    side-by-side stays meaningful. Verdict is coverage (point KPIs) or rating
    (error KPIs).
    """
    ci = res['confidence_intervals']
    cov = res['coverage']
    rat = res['ratings']
    rows = []

    def cir(n):
        c = ci[n]
        return f"[{c['ci_lower']:.3f}, {c['ci_upper']:.3f}]"

    # --- point-value KPIs judged by coverage ---
    for n, label in [('throughput_total', 'Throughput (completed)'),
                     ('mean_flow_time_s', 'Mean flow time (s)'),
                     ('failure_rate', 'Failure rate')]:
        if n not in cov:
            continue
        gtv = cov[n]['ground_truth']; sim = ci[n]['mean']
        delta = sim - gtv
        pct = (delta / gtv * 100) if gtv else float('nan')
        verdict = 'COVERED' if cov[n]['covered'] else 'NOT COVERED'
        rows.append((label, gtv, sim, cir(n),
                     f"{delta:+.3f} ({pct:+.1f}%)", verdict, 'coverage'))

    # --- error-metric KPIs judged by threshold rating (target = ideal) ---
    for n, label, target in [
            ('throughput_accuracy_pct', 'Throughput accuracy (%)', 0.0),
            ('mean_flow_time_error_pct', 'Flow-time error (%)', 0.0),
            ('variant_jsd', 'Variant JSD', 0.0),
            ('activity_duration_mape', 'Activity duration MAPE (%)', 0.0)]:
        if n not in ci or np.isnan(ci[n]['mean']):
            continue
        sim = ci[n]['mean']
        verdict = rat[n]['rating'] if n in rat else ''
        rows.append((label, target, sim, cir(n),
                     f"{sim - target:+.3f} vs target", verdict, 'threshold'))

    return rows


def _report(res, gt):
    W = 104
    print("\n" + "=" * W)
    print(f"GROUND-TRUTH vs MODEL  -  MULTI-REPLICATION EVALUATION  (m = {res['n_replications']})")
    print("=" * W)

    rows = build_comparison(res, gt)
    print(f"\n{'KPI':<28}{'Ground Truth':>14}{'Model Mean':>14}"
          f"{'95% CI':>26}{'Delta':>22}")
    print("-" * W)
    for label, gtv, sim, cistr, delta, verdict, basis in rows:
        print(f"{label:<28}{gtv:>14.3f}{sim:>14.3f}{cistr:>26}{delta:>22}")
    print("-" * W)

    print(f"\n{'KPI':<28}{'Basis':>12}   Verdict")
    print("-" * W)
    for label, gtv, sim, cistr, delta, verdict, basis in rows:
        print(f"{label:<28}{basis:>12}   {verdict}")

    if 'iat_ks_test' in res:
        ks = res['iat_ks_test']
        gt_mean = gt.get('iat_mean_s')
        sim_mean = res['confidence_intervals']['iat_mean_s']['mean']
        gt_str = f"{gt_mean:.1f}s" if gt_mean is not None else "n/a"
        print(f"\nInter-arrival distribution (KS two-sample):")
        print(f"  GT mean {gt_str}   model mean {sim_mean:.1f}s   "
              f"D = {ks['ks_stat']:.3f}  p = {ks['p_value']:.4f}  "
              f"-> {'PASS' if ks['pass'] else 'FAIL'} (p > 0.05)")

    q = res['quality_score']
    span = max(s['weight'] for s in Q_SPEC.values())
    print(f"\n{'Aggregated Quality Score':<28}Q = {q['Q']} / {q['max_possible']}")
    print("-" * W)
    for n, d in q['details'].items():
        flag = 'PASS' if d['passed'] else 'fail'
        bar = '#' * int(round(d['contribution'] / span * 20))
        print(f"   {n:<26} w={d['weight']:.2f}  {d['mode']:<9} {flag:<5} {bar}")
    print("=" * W)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    ap = argparse.ArgumentParser(description="Generic multi-rep evaluation harness")
    ap.add_argument('--model', required=True, help="path to model .py (the contract)")
    ap.add_argument('--ground-truth', required=True, help="path to GT .py or .json")
    ap.add_argument('-n', '--replications', type=int, default=30)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--sim-time', type=float, default=None,
                    help="override sim horizon (s); default = GT observation window")
    ap.add_argument('-o', '--output', default='output/evaluation')
    ap.add_argument('-q', '--quiet', action='store_true')
    args = ap.parse_args()
    verbose = not args.quiet

    gt = load_ground_truth(args.ground_truth)
    model = load_model(args.model)
    model._GT = gt

    sim_time = (args.sim_time or gt.get('observation_period_s')
                or getattr(model, 'SIMULATION_TIME', None))
    if sim_time is None:
        sys.exit("No sim horizon: pass --sim-time or set GT observation_period_s")
    if hasattr(model, 'SIMULATION_TIME'):
        model.SIMULATION_TIME = sim_time  # align model horizon to GT window

    if verbose:
        print(f"Model: {args.model}\nGround truth: {args.ground_truth}")
        print(f"Horizon: {sim_time:.0f}s   Replications: {args.replications}\n")

    reps = run_replications(model, args.replications, args.seed, sim_time, verbose)
    res = analyse(reps, gt, verbose)

    os.makedirs(args.output, exist_ok=True)
    with open(os.path.join(args.output, 'evaluation_results.json'), 'w') as f:
        json.dump(res, f, indent=2, default=str)
    rows = [{kk: vv for kk, vv in r.items()
             if not isinstance(vv, (dict, np.ndarray))} for r in reps]
    pd.DataFrame(rows).to_csv(os.path.join(args.output, 'replication_kpis.csv'), index=False)
    if verbose:
        print(f"\nSaved to {args.output}/")
    return res


if __name__ == '__main__':
    main()