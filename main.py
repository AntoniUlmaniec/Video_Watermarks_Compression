#nagranie -> znakowanie -> kompresja -> ocena -> plik CSV
import csv
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).parent / "src"))

from module2_compression.compression import compress_video, get_bitrate_kbps
from module4_metrics.quality_eval import compute_psnr, compute_vmaf
from module4_metrics.watermark_eval import compute_ber

#-config-
SOURCES = sorted(Path("data/01_raw").glob("*.mp4")) + sorted(Path("data/02_synthetic").glob("*.mp4"))

METHODS = [
    {
        "name": "dwtDct",
        "python": sys.executable,
        "adapter": "src/module1_watermark/dwtdct_adapter.py",
        "n_bits": 32,
    },
    {
        "name": "videoseal",
        "python": r"C:\Users\antek\anaconda3\envs\videoseal\python.exe",
        "adapter": "src/module1_watermark/videoseal_adapter.py",
        "n_bits": 256,
    },
    {
        "name": "stegastamp",
        "python": r"C:\Users\antek\anaconda3\envs\stegastamp\python.exe",
        "adapter": "src/module1_watermark/stegastamp_adapter.py",
        "n_bits": 100,
    },
]

CODECS = {
    "libx264": [17, 23, 29, 35, 41],
    "libx265": [22, 28, 34, 40, 46],
    #"libx264": [23],
    #"libx265": [28],
}

SEED = 2026
RESULTS_FILE = "results/experiment_logs.csv"
#-config-

COLUMNS = ["content", "method", "stage", "codec", "crf", "bitrate_kbps", "psnr_y_db", "psnr_u_db", "vmaf", "ber_mean", "ber_voted", "embed_s", "extract_s"]


def make_message(n_bits):
    rng = np.random.default_rng(SEED)
    return rng.permutation(np.arange(n_bits) % 2)


def run_adapter(method, *args):
    command = [method["python"], method["adapter"]] + [str(arg) for arg in args]
    subprocess.run(command, check=True)


#odczyt znaku i BER, przepływność oraz PSNR i VMAF
def measure(method, video, reference, message, row):
    bits_file = f"data/05_extracted/{method['name']}_{video.stem}.txt"
    start = time.perf_counter()
    run_adapter(method, "extract", video, bits_file, len(message))
    row["extract_s"] = round(time.perf_counter() - start, 1)

    with open(bits_file) as file:
        bits = np.array([[int(char) for char in line.strip()] for line in file])

    row.update(compute_ber(bits, message))
    row["bitrate_kbps"] = get_bitrate_kbps(video)
    if reference is not None:
        row["psnr_y_db"], row["psnr_u_db"] = compute_psnr(video, reference)
        row["vmaf"] = compute_vmaf(video, reference)
    return row


def save(writer, results_file, row):
    writer.writerow(row)
    results_file.flush()
    print(row["content"], row["method"], row["stage"], row["codec"], row["crf"], "BER =", row["ber_voted"])


def main():
    for folder in ["data/03_watermarked", "data/04_compressed", "data/05_extracted", "results"]:
        Path(folder).mkdir(parents=True, exist_ok=True)
    total_start = time.perf_counter()

    with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as results_file:
        writer = csv.DictWriter(results_file, fieldnames=COLUMNS)
        writer.writeheader()

        for source in SOURCES:
            for method in METHODS:
                message = make_message(method["n_bits"])
                message_file = f"data/03_watermarked/{method['name']}_message.txt"

                with open(message_file, "w") as file:
                    file.write("".join(str(bit) for bit in message))
                common = {"content": source.stem, "method": method["name"]}

                # 1. nagranie bez znaku
                row = {**common, "stage": "bez_znaku", "codec": "brak", "crf": ""}
                save(writer, results_file, measure(method, source, None, message, row))

                # 2. znakowanie i kontrola bez kompresji
                marked = Path(f"data/03_watermarked/{source.stem}_{method['name']}.mkv")
                start = time.perf_counter()
                run_adapter(method, "embed", source, marked, message_file)
                embed_s = round(time.perf_counter() - start, 1)
                row = {**common, "stage": "znak_bez_kompresji", "codec": "brak", "crf": "", "embed_s": embed_s}
                save(writer, results_file, measure(method, marked, source, message, row))

                # 3. badana kompresja
                for codec, crf_values in CODECS.items():
                    for crf in crf_values:
                        compressed = Path(f"data/04_compressed/{source.stem}_{method['name']}_{codec}_crf{crf}.mp4")
                        compress_video(marked, compressed, codec, crf)
                        row = {**common, "stage": "po_kompresji", "codec": codec, "crf": crf}
                        save(writer, results_file, measure(method, compressed, source, message, row))

    print("Gotowe:", RESULTS_FILE)
    print("Czas całości:", round((time.perf_counter() - total_start) / 3600, 2), "h")


if __name__ == "__main__":
    main()