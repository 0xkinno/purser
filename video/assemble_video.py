"""
Assembles the final Purser demo film:
1. Trims each scene webm by its recorded offset.
2. Normalizes to 1920x1080 30fps H.264.
3. Concatenates all scenes.
4. Muxes with voiceover_full.wav.
5. Generates QA contact sheet.
"""

import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(BASE_DIR, "scenes")
CLIPS_DIR = os.path.join(SCENES_DIR, "clips")
OUT_DIR = os.path.join(BASE_DIR, "out")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(OUT_DIR, exist_ok=True)

offsets_file = os.path.join(CLIPS_DIR, "offsets.json")
if not os.path.exists(offsets_file):
    print("Error: offsets.json not found in", CLIPS_DIR)
    exit(1)

offsets = json.load(open(offsets_file, "r"))

SCENES = [
    ("s01", 19.0),
    ("s02", 16.1),
    ("s03", 23.6),
    ("s04", 13.7),
    ("s05", 24.0),
    ("s06", 23.1),
    ("s07", 17.8),
    ("s08", 19.2),
    ("s09", 6.7),
    ("s10", 6.8)
]

def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Command failed:", " ".join(cmd))
        print("STDERR:", res.stderr[-1000:])
        raise RuntimeError("FFmpeg execution error")

print("Processing scene video clips...")
parts = []
for name, dur in SCENES:
    src_webm = os.path.join(CLIPS_DIR, f"{name}.webm")
    dst_mp4 = os.path.join(OUT_DIR, f"{name}.mp4")
    off = offsets.get(name, 0.6)
    
    print(f"  Rendering {name} (dur={dur}s, offset={off}s)...")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{off:.3f}",
        "-i", src_webm,
        "-vf", f"fps=30,tpad=stop_mode=clone:stop_duration=5,trim=duration={dur},setpts=PTS-STARTPTS,scale=1920:1080,format=yuv420p",
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "16",
        dst_mp4
    ]
    run(cmd)
    parts.append(dst_mp4)

# Create concat list
concat_list = os.path.join(OUT_DIR, "concat_list.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for p in parts:
        # Relative file name for safe concatenation
        basename = os.path.basename(p)
        f.write(f"file '{basename}'\n")

print("Concatenating video segments...")
silent_mp4 = os.path.join(OUT_DIR, "purser_silent.mp4")
run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_list,
    "-c", "copy",
    silent_mp4
])

vo_wav = os.path.join(AUDIO_DIR, "voiceover_full.wav")
final_mp4 = os.path.join(OUT_DIR, "purser_demo.mp4")

print("Muxing final video with master voiceover...")
run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", silent_mp4,
    "-i", vo_wav,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "320k",
    "-ar", "48000",
    "-movflags", "+faststart",
    "-shortest",
    final_mp4
])

print(f"Final demo video built: {final_mp4}")

# Generate QA contact sheet: frame every 17 seconds (10 frames)
print("Generating QA contact sheet...")
sheet_png = os.path.join(OUT_DIR, "contact_sheet.png")
run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", final_mp4,
    "-vf", "fps=1/17,scale=640:360,tile=5x2",
    sheet_png
])
print(f"Contact sheet saved to {sheet_png}")
