"""Renders high-resolution chart images specifically for the PDF document."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import ticker

OUTPUT_DIR = Path("docs/report_figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Styling defaults: restrained executive styling
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

PRIMARY_NAVY = '#1F4E78'
MUTED_TEAL = '#2E8B57'
AMBER = '#D97706'
MUTED_SLATE = '#64748B'
LIGHT_GRAY = '#F1F5F9'
BORDER_GRAY = '#CBD5E1'

# 1. Chart 1: Monthly Spend & Orders Trend
def plot_monthly_trend():
    df = pd.read_csv("outputs/exports/monthly_summary.csv")
    fig, ax1 = plt.subplots(figsize=(8, 3.8))

    x = range(len(df))
    ax1.bar(x, df['total_value'] / 1000, color=PRIMARY_NAVY, width=0.6, label='Gross Spend (£k)', alpha=0.9)
    ax1.set_ylabel('Gross Spend (£ Thousands)', color=PRIMARY_NAVY, fontsize=9, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=PRIMARY_NAVY, labelsize=8)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'£{int(y):,}k'))
    ax1.set_xticks(x[::2])
    ax1.set_xticklabels(df['year_month'].iloc[::2], rotation=45, ha='right', fontsize=8)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(x, df['total_orders'], color=AMBER, linewidth=2, marker='o', markersize=3, label='Orders')
    ax2.set_ylabel('Order Count', color=AMBER, fontsize=9, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=AMBER, labelsize=8)
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{int(y):,}'))

    plt.title('Monthly Gross Spend and Order Volume (2009-12 to 2011-12)', fontsize=10, fontweight='bold', pad=12)
    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig1_monthly_trend.png", bbox_inches='tight')
    plt.close()

# 2. Chart 2: Lorenz Value Concentration Curve
def plot_lorenz_curve():
    df = pd.read_csv("outputs/exports/customer_summary.csv")
    sorted_vals = np.sort(df['total_value'].values)
    cum_vals = np.cumsum(sorted_vals) / np.sum(sorted_vals) * 100
    cum_custs = np.linspace(0, 100, len(cum_vals))

    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.plot(cum_custs, cum_vals, color=PRIMARY_NAVY, linewidth=2.2, label='Observed Customer Spend')
    ax.plot([0, 100], [0, 100], color=MUTED_SLATE, linestyle='--', linewidth=1.2, label='Equal Distribution Parity')

    # Annotate Top 5% and Top 20%
    top5_idx = int(len(cum_vals) * 0.95)
    top20_idx = int(len(cum_vals) * 0.80)
    ax.scatter([95, 80], [cum_vals[top5_idx], cum_vals[top20_idx]], color=AMBER, s=35, zorder=5)
    ax.annotate('Top 5% Accounts\nGenerate 53.8%', xy=(95, cum_vals[top5_idx]), xytext=(65, 60),
                arrowprops={"arrowstyle": "->", "color": PRIMARY_NAVY, "lw": 1}, fontsize=8, fontweight='bold', color=PRIMARY_NAVY)
    ax.annotate('Top 20% Accounts\nGenerate 83.1%', xy=(80, cum_vals[top20_idx]), xytext=(45, 30),
                arrowprops={"arrowstyle": "->", "color": PRIMARY_NAVY, "lw": 1}, fontsize=8, fontweight='bold', color=PRIMARY_NAVY)

    ax.set_xlabel('Cumulative Customer Percentile (%)', fontsize=8.5, fontweight='bold')
    ax.set_ylabel('Cumulative Spend Contribution (%)', fontsize=8.5, fontweight='bold')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='upper left', fontsize=8)
    plt.title('Customer Spend Concentration (Empirical Lorenz Curve)', fontsize=10, fontweight='bold', pad=12)
    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig2_lorenz_curve.png", bbox_inches='tight')
    plt.close()

# 3. Chart 3: Segment Value & Share Comparison
def plot_segment_comparison():
    df = pd.read_csv("outputs/exports/segment_summary.csv")
    fig, ax = plt.subplots(figsize=(6.5, 3.2))

    y = np.arange(len(df))
    bars = ax.barh(y, df['total_value'] / 1e6, color=[PRIMARY_NAVY, MUTED_TEAL, MUTED_SLATE], height=0.55)
    ax.set_yticks(y)
    ax.set_yticklabels(df['segment_name'], fontsize=8.5, fontweight='bold')
    ax.set_xlabel('Gross Value (£ Millions)', fontsize=8.5, fontweight='bold')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'£{x:.1f}M'))
    ax.grid(axis='x', linestyle='--', alpha=0.3)

    for i, bar in enumerate(bars):
        val = df['total_value'].iloc[i] / 1e6
        share = df['value_share'].iloc[i]
        c_share = df['customer_share'].iloc[i]
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2, f'£{val:.2f}M ({share:.1%} spend | {c_share:.1%} accounts)',
                va='center', fontsize=8, fontweight='bold', color='#1E293B')

    ax.set_xlim(0, 15)
    plt.title('Value Contribution Across Empirical Behavioral Segments', fontsize=10, fontweight='bold', pad=12)
    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig3_segment_comparison.png", bbox_inches='tight')
    plt.close()

# 4. Chart 4: Decision Signal Breakdown
def plot_decision_signals():
    df = pd.read_csv("outputs/exports/decision_signals.csv")
    counts = df.groupby(['signal_name', 'signal_strength']).size().unstack(fill_value=0)
    counts['total'] = counts.sum(axis=1)
    counts = counts.sort_values('total', ascending=True)

    fig, ax = plt.subplots(figsize=(7, 3.4))
    y = np.arange(len(counts))

    ax.barh(y, counts.get('High', 0), color='#DC2626', label='High Severity', height=0.55)
    ax.barh(y, counts.get('Medium', 0), left=counts.get('High', 0), color='#F59E0B', label='Medium Severity', height=0.55)
    ax.barh(y, counts.get('Low', 0), left=counts.get('High', 0) + counts.get('Medium', 0), color='#94A3B8', label='Low Severity', height=0.55)

    ax.set_yticks(y)
    ax.set_yticklabels(counts.index, fontsize=8, fontweight='bold')
    ax.set_xlabel('Identified Account Count', fontsize=8.5, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.legend(loc='lower right', fontsize=8)

    for i, total in enumerate(counts['total']):
        ax.text(total + 30, i, f'{total:,}', va='center', fontsize=8, fontweight='bold', color='#1E293B')

    ax.set_xlim(0, 2400)
    plt.title('Triggered Decision Signals by Severity Tier', fontsize=10, fontweight='bold', pad=12)
    fig.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig4_decision_signals.png", bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    plot_monthly_trend()
    plot_lorenz_curve()
    plot_segment_comparison()
    plot_decision_signals()
    print("Report figures successfully generated in docs/report_figures/")
