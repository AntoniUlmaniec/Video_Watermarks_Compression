#nagrania naturalne: .yuv -> .mp4

import subprocess

RAW_DIR = "data/01_raw"

CLIPS = [
    ("Sintel-Dragons_3840x1632_24fps_10bit_420.yuv", "3840x1632", "24", "yuv420p10le", "sintel_dragons_1920x816_24fps_crf10.mp4"),
]

if __name__ == "__main__":
    for yuv, size, fps, pix_fmt, output in CLIPS:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", pix_fmt, "-s", size, "-r", fps,
            "-i", f"{RAW_DIR}/{yuv}",
            "-t", "10",
            "-vf", "scale=1920:-2:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-crf", "10",
            f"{RAW_DIR}/{output}",
        ], check=True)
        print(f"Gotowe: {output}")