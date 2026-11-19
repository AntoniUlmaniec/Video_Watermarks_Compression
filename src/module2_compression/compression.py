#kompresja przez FFmpeg wybranym kodekiem i CRF
import subprocess


def compress_video(input_path, output_path, codec, crf):
    command = ["ffmpeg", "-y", "-v", "error", "-i", str(input_path),
               "-c:v", codec, "-crf", str(crf), "-pix_fmt", "yuv420p"]
    if codec == "libx265":
        command += ["-x265-params", "log-level=error"]
    subprocess.run(command + [str(output_path)], check=True)


def get_bitrate_kbps(video_path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=bit_rate", "-of", "csv=p=0",
        str(video_path),
    ], capture_output=True, text=True, check=True)
    return int(result.stdout) / 1000