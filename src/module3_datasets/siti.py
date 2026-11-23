#SI i TI nagrań naturalnych

from pathlib import Path

import matplotlib.pyplot as plt
from siti_tools.siti import ColorRange, SiTiCalculator

if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    names, si_means, ti_means = [], [], []
    with open("results/siti.csv", "w") as file:
        file.write("content,si_mean,si_max,ti_mean,ti_max\n")

        for video in Path("data/01_raw").glob("*.mp4"):
            calculator = SiTiCalculator(legacy=True, color_range=ColorRange.FULL)
            si, ti, frame_count = calculator.calculate(str(video))

            si_mean = sum(si) / len(si)
            ti_mean = sum(ti) / len(ti)
            file.write(f"{video.stem},{si_mean:.2f},{max(si):.2f},{ti_mean:.2f},{max(ti):.2f}\n")
            print(f"{video.stem}: SI={si_mean:.2f}  TI={ti_mean:.2f}")
            names.append(video.stem.split("_")[1])
            si_means.append(si_mean)
            ti_means.append(ti_mean)

    fig, ax = plt.subplots(figsize=(6, 4.5), layout="constrained")
    ax.scatter(si_means, ti_means)
    for name, si_mean, ti_mean in zip(names, si_means, ti_means):
        ax.annotate(name, (si_mean, ti_mean), textcoords="offset points", xytext=(5, 5))
    ax.set_xlabel("SI (średnia)")
    ax.set_ylabel("TI (średnia)")
    fig.savefig("results/siti.png", dpi=300)