#adapter metody dwtDct (biblioteka invisible-watermark)

import subprocess
import sys

import cv2
from imwatermark import WatermarkDecoder, WatermarkEncoder

from adapter_common import get_frame_rate, read_bits


#wstawia znak do każdej klatki i zapisuje film bezstratnie
def embed(input_path, output_path, bits_path):
    encoder = WatermarkEncoder()
    encoder.set_watermark("bits", read_bits(bits_path))

    video = cv2.VideoCapture(input_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}",
        "-r", get_frame_rate(input_path), "-i", "-",
        "-c:v", "ffv1", "-pix_fmt", "yuv420p", output_path,
    ], stdin=subprocess.PIPE)

    frame_count = 0
    while True:
        ok, frame = video.read()
        if not ok:
            break
        marked = encoder.encode(frame, "dwtDct")
        ffmpeg.stdin.write(marked.tobytes())
        frame_count += 1

    video.release()
    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0 or frame_count == 0:
        raise RuntimeError(f"Znakowanie nie powiodło się: {input_path}")


#odczytuje znak z każdej klatki
def extract(video_path, output_path, n_bits):
    decoder = WatermarkDecoder("bits", n_bits)
    video = cv2.VideoCapture(video_path)

    frame_count = 0
    with open(output_path, "w") as file:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            bits = decoder.decode(frame, "dwtDct")
            file.write("".join(str(int(bit)) for bit in bits) + "\n")
            frame_count += 1

    video.release()
    if frame_count == 0:
        raise RuntimeError(f"Nie wczytano żadnej klatki: {video_path}")


if __name__ == "__main__":
    if sys.argv[1] == "embed":
        embed(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "extract":
        extract(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        raise SystemExit("Nieznane polecenie, użyj: embed albo extract")