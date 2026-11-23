#wyniki z results/experiment_logs.csv -> wykresy i tabele
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from module5_analysis.load_results import load_results
from module5_analysis.plot_robustness import plot_ber_vs_crf, plot_ber_vs_vmaf
from module5_analysis.tables import content_table, method_card


def main():
    Path("results/plots").mkdir(parents=True, exist_ok=True)
    Path("results/tables").mkdir(parents=True, exist_ok=True)
    results = load_results()
    print(len(results), "pomiarów,", results["content"].nunique(), "nagrań")
    plot_ber_vs_crf(results)
    plot_ber_vs_vmaf(results)
    method_card(results)
    content_table(results)
    print("Gotowe: results/plots i results/tables")


if __name__ == "__main__":
    main()