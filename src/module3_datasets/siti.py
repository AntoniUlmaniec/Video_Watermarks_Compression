#SI i TI nagrań naturalnych

from pathlib import Path

from siti_tools.siti import ColorRange, SiTiCalculator

if __name__ == "__main__":
    Path("results").mkdir(exist_ok=True)
    with open("results/siti.csv", "w") as file:
        file.write("content,si_mean,si_max,ti_mean,ti_max\n")

        for video in Path("data/01_raw").glob("*.mp4"):
            calculator = SiTiCalculator(legacy=True, color_range=ColorRange.FULL)
            si, ti, frame_count = calculator.calculate(str(video))

            si_mean = sum(si) / len(si)
            ti_mean = sum(ti) / len(ti)
            file.write(f"{video.stem},{si_mean:.2f},{max(si):.2f},{ti_mean:.2f},{max(ti):.2f}\n")
            print(f"{video.stem}: SI={si_mean:.2f}  TI={ti_mean:.2f}")