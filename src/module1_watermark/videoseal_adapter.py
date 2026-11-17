#adapter metody Video Seal 1.0 (Meta, repozytorium facebookresearch/videoseal)

import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

from adapter_common import get_frame_rate, read_bits

#pobrane repozytorium videoseal, obok folderu projektu
VIDEOSEAL_DIR = Path(__file__).resolve().parents[3] / "videoseal"
N_BITS = 256
CHUNK_SIZE = 32


def read_chunk(video):
    frames = []
    while len(frames) < CHUNK_SIZE:
        ok, frame = video.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if len(frames) == 0:
        return None
    return torch.from_numpy(np.stack(frames)).permute(0, 3, 1, 2).float() / 255


def load_model():
    os.chdir(VIDEOSEAL_DIR)
    sys.path.insert(0, str(VIDEOSEAL_DIR))
    import videoseal

    model = videoseal.load("videoseal")
    model.eval()
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.step_size = 1
    return model


def embed(input_path, output_path, bits_path):
    bits = read_bits(bits_path)
    if len(bits) != N_BITS:
        raise ValueError(f"Video Seal wymaga {N_BITS} bitów, a dostał {len(bits)}")
    message = torch.tensor([bits])

    video = cv2.VideoCapture(input_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = get_frame_rate(input_path)
    model = load_model()

    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
        "-r", frame_rate, "-i", "-",
        "-c:v", "ffv1", "-pix_fmt", "yuv420p", output_path,
    ], stdin=subprocess.PIPE)

    frame_count = 0
    while True:
        chunk = read_chunk(video)
        if chunk is None:
            break
        marked = model.embed(chunk, msgs=message, is_video=True)["imgs_w"]
        marked = (marked * 255).round().clamp(0, 255).byte().permute(0, 2, 3, 1)
        ffmpeg.stdin.write(marked.numpy().tobytes())
        frame_count += len(chunk)

    video.release()
    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0 or frame_count == 0:
        raise RuntimeError(f"Znakowanie nie powiodło się: {input_path}")


def extract(video_path, output_path, n_bits):
    if n_bits != N_BITS:
        raise ValueError(f"Video Seal ma {N_BITS} bitów, a podano {n_bits}")

    video = cv2.VideoCapture(video_path)
    model = load_model()

    frame_count = 0
    with open(output_path, "w") as file:
        while True:
            chunk = read_chunk(video)
            if chunk is None:
                break
            preds = model.detect(chunk, is_video=True)["preds"]
            bits = (preds[:, 1:] > 0).int()
            for frame_bits in bits:
                file.write("".join(str(bit) for bit in frame_bits.tolist()) + "\n")
            frame_count += len(chunk)

    video.release()
    if frame_count == 0:
        raise RuntimeError(f"Nie wczytano żadnej klatki: {video_path}")


if __name__ == "__main__":
    if sys.argv[1] == "embed":
        embed(os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]), os.path.abspath(sys.argv[4]))
    elif sys.argv[1] == "extract":
        extract(os.path.abspath(sys.argv[2]), os.path.abspath(sys.argv[3]), int(sys.argv[4]))
    else:
        raise SystemExit("Nieznane polecenie, użyj: embed albo extract")