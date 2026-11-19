#generator nagrań syntetycznych

import subprocess
from pathlib import Path

OUTPUT_DIR = Path("data/02_synthetic")
SIZE = "1920x1080"
FPS = 30
DURATION = 1
SLOW_DURATION = 3
NATURAL_VIDEO = "data/01_raw/sintel_dragons_1920x816_24fps_crf10.mp4"


def color(value, duration=DURATION):
    return f"color=c={value}:s={SIZE}:r={FPS}:d={duration}"


GENERATED = {
    # 1. jednolite kolory
    "1_solid_black": color("#000000"),
    "1_solid_white": color("#FFFFFF"),
    #"1_solid_red": color("#FF0000"),
    "1_solid_green": color("#00FF00"),
    #"1_solid_blue": color("#0000FF"),
    "1_solid_yellow": color("#FFFF00"),

    # 2. inne jasności
    "2_solid_gray": color("#808080"),
    "2_solid_dark_green": color("#008000"),
    "2_solid_dark_yellow": color("#808000"),
    #"2_solid_light_red": color("#FF8080"),
    #"2_solid_light_blue": color("#8080FF"),

    # 3. zmiana koloru
    "3_changing_color": color("red", SLOW_DURATION) + f",hue=h=t*360/{SLOW_DURATION},format=rgb24",

    # 4. zmiana jasności
    "4_changing_brightness": color("white", SLOW_DURATION) + f",fade=t=in:st=0:d={SLOW_DURATION}",

    # 5. szum czarno-biały i kolorowy
    "5_noise_bw": color("gray") + ",noise=c0s=100:c0f=t+u",
    "5_noise_color": color("gray") + ",format=rgb24,noise=alls=100:allf=t+u",
}


CHANNEL_MAPPINGS = {
    "r": "map0s=0:map0p=0:map1s=0:map1p=1:map2s=1:map2p=0",  # G, B z szumu, R z filmu
    "g": "map0s=1:map0p=0:map1s=0:map1p=1:map2s=0:map2p=2",  # G z filmu, B, R z szumu
    "b": "map0s=0:map0p=0:map1s=1:map1p=0:map2s=0:map2p=2",  # G z szumu, B z filmu, R z szumu
}


def channel_filter(channel):
    return (
        "split[a][b];"
        "[a]format=gray[film];"
        "[b]format=rgb24,lutrgb=r=128:g=128:b=128,noise=alls=100:allf=t+u,format=gbrp[noise];"
        f"[noise][film]mergeplanes={CHANNEL_MAPPINGS[channel]}:format=gbrp"
    )


def encode(input_args, name):
    output = OUTPUT_DIR / f"{name}.mp4"
    command = (["ffmpeg", "-y", "-v", "error"] + input_args + ["-c:v", "libx264", "-crf", "0", "-pix_fmt", "yuv420p", str(output)])
    subprocess.run(command, check=True)
    print(f"Gotowe: {output}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, source in GENERATED.items():
        encode(["-f", "lavfi", "-i", source], name)
    for channel in CHANNEL_MAPPINGS:
        encode(["-t", str(DURATION), "-i", NATURAL_VIDEO, "-vf", channel_filter(channel)], f"6_film_{channel}_noise")