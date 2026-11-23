#podgląd tej samej klatki: oryginał i ze znakiem
#python src/module5_analysis/compare_frames.py <nazwa_nagrania> <numer_klatki>
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

CROP = 300
GAIN = 10


def read_frame(path, number):
    video = cv2.VideoCapture(str(path))
    for _ in range(number + 1):
        ok, frame = video.read()
        if not ok:
            raise SystemExit(f"Za mało klatek w {path}")
    video.release()
    height, width = frame.shape[:2]
    top, left = (height - CROP) // 2, (width - CROP) // 2
    return cv2.cvtColor(frame[top:top + CROP, left:left + CROP], cv2.COLOR_BGR2RGB)


def main():
    content, number = sys.argv[1], int(sys.argv[2])
    source = Path(f"data/01_raw/{content}.mp4")
    if not source.exists():
        source = Path(f"data/02_synthetic/{content}.mp4")
    marked_files = sorted(Path("data/03_watermarked").glob(f"{content}_*.mkv"))
    if not marked_files:
        raise SystemExit(f"Brak nagrań ze znakiem dla {content}")

    original = read_frame(source, number)
    fig, axes = plt.subplots(2, len(marked_files) + 1, figsize=(3 * (len(marked_files) + 1), 6), layout="constrained")
    axes[0, 0].imshow(original)
    axes[0, 0].set_title("oryginał")
    for column, path in enumerate(marked_files, start=1):
        marked = read_frame(path, number)
        difference = np.clip(np.abs(marked.astype(int) - original.astype(int)) * GAIN, 0, 255).astype(np.uint8)
        axes[0, column].imshow(marked)
        axes[0, column].set_title(path.stem[len(content) + 1:])
        axes[1, column].imshow(difference)
        axes[1, column].set_title(f"różnica ×{GAIN}")
    for ax in axes.flat:
        ax.axis("off")

    Path("results/frames").mkdir(parents=True, exist_ok=True)
    output = f"results/frames/{content}_klatka{number}.png"
    fig.savefig(output, dpi=200)
    print("Zapisano:", output)


if __name__ == "__main__":
    main()