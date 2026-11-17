#PSNR i VMAF liczone przez FFmpeg względem nagrania odniesienia
import os
import re
import subprocess


def run_metric(video, reference, metric):
    #porównuje dwa nagrania
    prepare = "format=yuv420p,settb=1/25,setpts=N"
    result = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostats",
        "-i", str(video), "-i", str(reference),
        "-lavfi", f"[0:v]{prepare}[a];[1:v]{prepare}[b];[a][b]{metric}",
        "-f", "null", "-",
    ], capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
    return result.stderr


def compute_psnr(video, reference):
    #PSNR w dB dla jasności Y i składowej koloru U
    output = run_metric(video, reference, "psnr=shortest=1")
    found = re.search(r"PSNR y:(\S+) u:(\S+)", output)
    return float(found.group(1)), float(found.group(2))


def compute_vmaf(video, reference):
    #Średni VMAF (0-100)
    output = run_metric(video, reference, f"libvmaf=shortest=1:n_threads={os.cpu_count()}")
    found = re.search(r"VMAF score: (\S+)", output)
    return float(found.group(1))