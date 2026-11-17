#funkcje wspólne dla adapterów
import subprocess


def read_bits(path):
    with open(path) as file:
        return [int(char) for char in file.read().strip()]


def get_frame_rate(path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", path,
    ], capture_output=True, text=True, check=True)
    return result.stdout.strip()