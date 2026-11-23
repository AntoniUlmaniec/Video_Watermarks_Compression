#BER w funkcji CRF i BER w funkcji jakości po kompresji (VMAF)
from pathlib import Path

import matplotlib.pyplot as plt

from module5_analysis.load_results import summarize

PLOTS_DIR = Path("results/plots")
LINE_STYLES = ["-", "--", ":", "-."]


#jak szybko metoda traci znak przy coraz silniejszej kompresji
def plot_ber_vs_crf(results):
    summary = summarize(results, "ber_voted")
    methods = sorted(summary["method"].unique())
    codecs = sorted(summary["codec"].unique())
    fig, axes = plt.subplots(1, len(codecs), figsize=(5 * len(codecs), 4.5), sharey=True, squeeze=False, layout="constrained")
    axes = axes[0]
    for ax, codec in zip(axes, codecs):
        for number, method in enumerate(methods):
            rows = summary[(summary["method"] == method) & (summary["codec"] == codec)]
            ax.errorbar(rows["crf"], rows["mean"], yerr=rows["ci"], color=f"C{number}", marker="o", capsize=3, label=method)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=1)  # poziom zgadywania
        ax.set_xticks(rows["crf"])
        ax.set_title(codec)
        ax.set_xlabel("CRF")
    axes[0].set_ylabel("BER")
    axes[0].set_ylim(bottom=-0.02)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=len(methods))
    fig.savefig(PLOTS_DIR / "ber_vs_crf.png", dpi=300)
    plt.close(fig)


#BER przy danej jakości po kompresji, kolejne punkty to kolejne CRF, wszystkie kodeki na jednym wykresie
def plot_ber_vs_vmaf(results):
    ber = summarize(results, "ber_voted")
    vmaf = summarize(results, "vmaf")
    both = ber.merge(vmaf, on=["method", "codec", "crf"], suffixes=("_ber", "_vmaf"))
    methods = sorted(both["method"].unique())
    codecs = sorted(both["codec"].unique())
    fig, ax = plt.subplots(figsize=(7, 5), layout="constrained")
    for number, method in enumerate(methods):
        for codec, style in zip(codecs, LINE_STYLES):
            rows = both[(both["method"] == method) & (both["codec"] == codec)]
            ax.plot(rows["mean_vmaf"], rows["mean_ber"], color=f"C{number}", linestyle=style, marker="o", label=f"{method}, {codec}")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("VMAF po kompresji")
    ax.set_ylabel("BER")
    ax.set_ylim(bottom=-0.02)
    fig.legend(loc="outside lower center", ncol=len(methods), fontsize=8)
    fig.savefig(PLOTS_DIR / "ber_vs_vmaf.png", dpi=300)
    plt.close(fig)