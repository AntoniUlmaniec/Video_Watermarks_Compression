#adapter metody StegaStamp

import os
import subprocess
import sys
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import cv2
import numpy as np
import tensorflow as tf

from adapter_common import get_frame_rate, read_bits

tf.get_logger().setLevel("ERROR")

#pobrane repozytorium StegaStamp, obok folderu projektu
MODEL_DIR = Path(__file__).resolve().parents[3] / "StegaStamp" / "saved_models" / "stegastamp_pretrained"
N_BITS = 100
MODEL_SIZE = 400


def load_model():
    tf.compat.v1.disable_eager_execution()
    session = tf.compat.v1.Session()
    model = tf.compat.v1.saved_model.loader.load(session, ["serve"], str(MODEL_DIR))
    signature = model.signature_def["serving_default"]
    graph = session.graph

    tensors = {
        "image": graph.get_tensor_by_name(signature.inputs["image"].name),
        "secret": graph.get_tensor_by_name(signature.inputs["secret"].name),
        "residual": graph.get_tensor_by_name(signature.outputs["residual"].name),
        "decoded": graph.get_tensor_by_name(signature.outputs["decoded"].name),
    }
    return session, tensors


def to_model_input(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (MODEL_SIZE, MODEL_SIZE), interpolation=cv2.INTER_AREA)
    return small.astype(np.float32) / 255


def embed(input_path, output_path, bits_path):
    bits = read_bits(bits_path)
    if len(bits) != N_BITS:
        raise ValueError(f"StegaStamp wymaga {N_BITS} bitów, a dostał {len(bits)}")
    message = np.array(bits, dtype=np.float32)

    video = cv2.VideoCapture(input_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = get_frame_rate(input_path)
    session, tensors = load_model()

    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{width}x{height}",
        "-r", frame_rate, "-i", "-",
        "-c:v", "ffv1", "-pix_fmt", "yuv420p", output_path,
    ], stdin=subprocess.PIPE)

    frame_count = 0
    while True:
        ok, frame = video.read()
        if not ok:
            break
        residual = session.run(tensors["residual"], {
            tensors["image"]: [to_model_input(frame)],
            tensors["secret"]: [message],
        })[0]
        residual = cv2.resize(residual, (width, height), interpolation=cv2.INTER_LINEAR)
        residual = residual[:, :, ::-1]
        marked = np.clip(frame / 255 + residual, 0, 1)
        ffmpeg.stdin.write(np.round(marked * 255).astype(np.uint8).tobytes())
        frame_count += 1

    video.release()
    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0 or frame_count == 0:
        raise RuntimeError(f"Znakowanie nie powiodło się: {input_path}")


def extract(video_path, output_path, n_bits):
    if n_bits != N_BITS:
        raise ValueError(f"StegaStamp ma {N_BITS} bitów, a podano {n_bits}")

    video = cv2.VideoCapture(video_path)
    session, tensors = load_model()

    frame_count = 0
    with open(output_path, "w") as file:
        while True:
            ok, frame = video.read()
            if not ok:
                break
            bits = session.run(tensors["decoded"], {tensors["image"]: [to_model_input(frame)]})[0]
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