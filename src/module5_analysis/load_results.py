#wczytanie wyników eksperymentu i średnie z nagrań naturalnych
import numpy as np
import pandas as pd
from scipy import stats

RESULTS_FILE = "results/experiment_logs.csv"


def load_results():
    results = pd.read_csv(RESULTS_FILE)
    results["synthetic"] = results["content"].str[0].str.isdigit()
    return results


#średnia z nagrań naturalnych i 95% przedział ufności
def summarize(results, column, stage="po_kompresji"):
    natural = results[~results["synthetic"] & (results["stage"] == stage)]
    summary = natural.groupby(["method", "codec", "crf"], dropna=False)[column].agg(["mean", "std", "count"]).reset_index()
    summary["ci"] = stats.t.ppf(0.975, summary["count"] - 1) * summary["std"] / np.sqrt(summary["count"])
    return summary


if __name__ == "__main__":
    results = load_results()
    print(len(results), "pomiarów,", results["content"].nunique(), "nagrań")
    print(summarize(results, "ber_voted"))