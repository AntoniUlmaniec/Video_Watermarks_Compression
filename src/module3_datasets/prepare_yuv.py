#nagrania naturalne: .yuv -> .mp4

import subprocess

RAW_DIR = "data/01_raw"

CLIPS = [
    ("Sintel-Dragons_3840x1632_24fps_10bit_420.yuv", "3840x1632", "24", "yuv420p10le", "sintel_dragons_1920x816_24fps_crf10.mp4"),
    ("Chimera-Freeway_3840x2160_2398fps_10bit_420.yuv", "3840x2160", "24000/1001", "yuv420p10le", "chimera_freeway_1920x1080_2398fps_crf10.mp4"),
    #("Chimera-WindAndNature_3840x2160_2997fps_10bit_420.yuv", "3840x2160", "30000/1001", "yuv420p10le", "chimera_windandnature_1920x1080_2997fps_crf10.mp4"),
    ("Chimera-DinnerScene_3840x2160_2997fps_10bit_420.yuv", "3840x2160", "30000/1001", "yuv420p10le", "chimera_dinnerscene_1920x1080_2997fps_crf10.mp4"),
    #("Chimera-BarScene1_3840x2160_2997fps_10bit_420.yuv", "3840x2160", "30000/1001", "yuv420p10le", "chimera_barscene1_1920x1080_2997fps_crf10.mp4"),
    ("ElFuente-FoodMarket_3840x2160_60fps_10bit_420.yuv", "3840x2160", "60", "yuv420p10le", "elfuente_foodmarket_1920x1080_60fps_crf10.mp4"),
    #("ElFuente-Tango_3840x2160_60fps_10bit_420.yuv", "3840x2160", "60", "yuv420p10le", "elfuente_tango_1920x1080_60fps_crf10.mp4"),
    ("Chimera-RollerCoasterPassengers_3840x2160_2997fps_10bit_420.yuv", "3840x2160", "30000/1001", "yuv420p10le", "chimera_rollercoasterpassengers_1920x1080_2997fps_crf10.mp4"),
    ("ElFuente-TunnelFlag_3840x2160_60fps_10bit_420.yuv", "3840x2160", "60", "yuv420p10le", "elfuente_tunnelflag_1920x1080_60fps_crf10.mp4"),
]

if __name__ == "__main__":
    for yuv, size, fps, pix_fmt, output in CLIPS:
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", pix_fmt, "-s", size, "-r", fps,
            "-i", f"{RAW_DIR}/{yuv}",
            "-t", "5",
            "-vf", "scale=1920:-2:flags=lanczos,format=yuv420p",
            "-c:v", "libx264", "-crf", "10",
            f"{RAW_DIR}/{output}",
        ], check=True)
        print(f"Gotowe: {output}")