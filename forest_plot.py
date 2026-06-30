import matplotlib.pyplot as plt
import numpy as np

colors = {'A': '#D55E00', 'B': '#0072B2', 'C': '#009E73'}
markers = {'A': 's', 'B': 'o', 'C': 'D'}
block_labels = ['A', 'B', 'C']
offsets = {'A': 0.22, 'B': 0.0, 'C': -0.22}

# ===== COVERAGE KPIs: (point %, CI_lo %, CI_hi %) =====
# Throughput: A=+500%, B=−3.3%, C=+0.5%
tp_A = (500, 500, 500)
tp_B = (-3.3, -17.5, 10.9)
tp_C = (0.5, -12.4, 13.2)

# Mean flow time: A=−2.8%, B=+6.3%, C=−38.7%
ft_A = (-2.8, -5.3, -0.3)
ft_B = (6.3, -3.9, 16.5)
ft_C = (-38.7, -44.2, -33.1)

# Failure rate: A=+1.5%, B=+7.6%, C=−3.0%
fr_A = (1.5, -9.5, 9.5)
fr_B = (7.6, -10.0, 20.0)
fr_C = (-3.0, -16.7, 13.6)

# ===== THRESHOLD KPIs: (point, CI_lo, CI_hi) absolute =====
# Variant JSD (threshold = 0.05): A=0.000, B=0.052, C=0.045
jsd_A = (0.000, None, None)
jsd_B = (0.052, 0.037, 0.067)
jsd_C = (0.045, 0.034, 0.056)

# Duration MAPE % (threshold = 20%): A=11.8%, B=6.7%, C=5.1%
mape_A = (11.8, None, None)
mape_B = (6.7, 6.1, 7.4)
mape_C = (5.1, 4.6, 5.6)

jsd_t, mape_t = 0.05, 20.0

def nt(v, t):
    return (v / t) * 100 if v is not None else None

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.2),
                                gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.5})

def plot_entry(ax, y, pt, lo, hi, blk):
    col, mk = colors[blk], markers[blk]
    if lo is not None and hi is not None:
        ax.plot([lo, hi], [y, y], color=col, linewidth=1.8, solid_capstyle='round')
        cap_h = 0.07
        ax.plot([lo, lo], [y - cap_h, y + cap_h], color=col, linewidth=1.1)
        ax.plot([hi, hi], [y - cap_h, y + cap_h], color=col, linewidth=1.1)
    ax.plot(pt, y, marker=mk, color=col, markersize=5.5,
            markeredgecolor='white', markeredgewidth=0.4, zorder=5)

def fmt_cov(pt, lo, hi):
    """Format coverage label: point [lo, hi] in %."""
    sign = '+' if pt > 0 else ''
    if lo is not None and hi is not None and not (lo == pt and hi == pt):
        return f'{sign}{pt:.1f}% [{lo:+.1f}, {hi:+.1f}]'
    return f'{sign}{pt:.1f}%'

def fmt_thresh_abs(pt, lo, hi, is_pct=False):
    """Format threshold label with absolute values."""
    if is_pct:
        if lo is not None and hi is not None:
            return f'{pt:.1f}% [{lo:.1f}, {hi:.1f}]'
        return f'{pt:.1f}%'
    else:
        if lo is not None and hi is not None:
            return f'{pt:.3f} [{lo:.3f}, {hi:.3f}]'
        return f'{pt:.3f}'

# ======= LEFT PANEL =======
coverage = {
    'Failure\nrate':   [fr_A, fr_B, fr_C],
    'Mean\nflow time': [ft_A, ft_B, ft_C],
    'Throughput':       [tp_A, tp_B, tp_C],
}
knames_c = list(coverage.keys())

ax1.axvspan(-55, 0, color='#fdf6ef', zorder=0)
ax1.axvspan(0, 65, color='#eff6fd', zorder=0)

for i, kpi in enumerate(knames_c):
    for j, blk in enumerate(block_labels):
        pt, lo, hi = coverage[kpi][j]
        y = i + offsets[blk]
        if kpi == 'Throughput' and blk == 'A':
            ax1.annotate('+500%', xy=(56, y), xytext=(38, y),
                         fontsize=6.5, fontweight='bold', color=colors[blk],
                         va='center', ha='right',
                         arrowprops=dict(arrowstyle='-|>', color=colors[blk],
                                        lw=1.3, mutation_scale=8))
            continue
        plot_entry(ax1, y, pt, lo, hi, blk)
        # Annotation
        label = fmt_cov(pt, lo, hi)
        # Place label to the right of the CI endpoint (or point if no CI)
        x_anchor = hi if (hi is not None and hi != pt) else pt
        ax1.text(x_anchor + 1.5, y, label, fontsize=5.0, color=colors[blk],
                 va='center', ha='left', clip_on=True)

ax1.axvline(x=0, color='#333', linewidth=0.7, alpha=0.7)
for i in range(1, len(knames_c)):
    ax1.axhline(y=i - 0.45, color='#ccc', linewidth=0.4)

ax1.set_xlim(-55, 90)
ax1.set_ylim(-0.5, len(knames_c) - 0.5)
ax1.set_yticks(range(len(knames_c)))
ax1.set_yticklabels(knames_c, fontsize=8.5)
ax1.set_xlabel('Deviation from ground truth (%)', fontsize=8.5)
ax1.set_title('(a) Coverage KPIs', fontsize=9.5, fontweight='bold', pad=6)
ax1.tick_params(axis='x', labelsize=7.5)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# ======= RIGHT PANEL =======
# Raw absolute data for annotation
thresh_raw = {
    'Duration\nMAPE': [(mape_A, True), (mape_B, True), (mape_C, True)],
    'Variant\nJSD':   [(jsd_A, False), (jsd_B, False), (jsd_C, False)],
}
thresh_norm = {
    'Duration\nMAPE': [
        (nt(mape_A[0], mape_t), nt(mape_A[1], mape_t), nt(mape_A[2], mape_t)),
        (nt(mape_B[0], mape_t), nt(mape_B[1], mape_t), nt(mape_B[2], mape_t)),
        (nt(mape_C[0], mape_t), nt(mape_C[1], mape_t), nt(mape_C[2], mape_t)),
    ],
    'Variant\nJSD': [
        (nt(jsd_A[0], jsd_t), nt(jsd_A[1], jsd_t), nt(jsd_A[2], jsd_t)),
        (nt(jsd_B[0], jsd_t), nt(jsd_B[1], jsd_t), nt(jsd_B[2], jsd_t)),
        (nt(jsd_C[0], jsd_t), nt(jsd_C[1], jsd_t), nt(jsd_C[2], jsd_t)),
    ],
}
knames_t = list(thresh_norm.keys())

ax2.axvspan(-8, 100, color='#f0f8f0', zorder=0)
ax2.axvspan(100, 150, color='#fdf0f0', zorder=0)

for i, kpi in enumerate(knames_t):
    for j, blk in enumerate(block_labels):
        pt, lo, hi = thresh_norm[kpi][j]
        y = i + offsets[blk]
        if pt is not None:
            plot_entry(ax2, y, pt, lo, hi, blk)
            # Annotation with absolute values
            raw_vals, is_pct = thresh_raw[kpi][j]
            label = fmt_thresh_abs(raw_vals[0], raw_vals[1], raw_vals[2], is_pct)
            x_anchor = hi if (hi is not None) else pt
            ax2.text(x_anchor + 2, y, label, fontsize=5.0, color=colors[blk],
                     va='center', ha='left', clip_on=True)

ax2.axvline(x=100, color='#333', linewidth=0.7, linestyle='--', alpha=0.7)

ax2.text(50, -0.47, 'pass', fontsize=7, ha='center', va='bottom',
         color='#4a8c4a', style='italic', alpha=0.7)
ax2.text(122, -0.47, 'fail', fontsize=7, ha='center', va='bottom',
         color='#8c4a4a', style='italic', alpha=0.7)

ax2.axhline(y=0.55, color='#ccc', linewidth=0.4)

ax2.set_xlim(-8, 195)
ax2.set_ylim(-0.5, len(knames_t) - 0.5)
ax2.set_yticks(range(len(knames_t)))
ax2.set_yticklabels(knames_t, fontsize=8.5)
ax2.set_xlabel('Fraction of threshold (%)', fontsize=8.5)
ax2.set_title('(b) Threshold KPIs', fontsize=9.5, fontweight='bold', pad=6)
ax2.tick_params(axis='x', labelsize=7.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# ======= LEGEND =======
legend_handles = [
    plt.Line2D([0], [0], marker=markers[b], color=colors[b], linestyle='-',
               markersize=5.5, markeredgecolor='white', markeredgewidth=0.4,
               label=f'Block {b}', linewidth=1.5)
    for b in block_labels
]
fig.legend(handles=legend_handles, loc='lower center', ncol=3, fontsize=8.5,
           frameon=True, edgecolor='#ccc', fancybox=False,
           bbox_to_anchor=(0.5, -0.12), handlelength=2.5, columnspacing=2.5)

plt.savefig('forest_plot_v3.pdf', bbox_inches='tight', dpi=300)
plt.savefig('forest_plot_v3.png', bbox_inches='tight', dpi=300)
print("Done.")