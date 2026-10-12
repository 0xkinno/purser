"""
Captures HTML scenes s01 to s10 using Python Playwright.
Saves .webm takes into video/scenes/clips/ and records offsets.json.
"""

import os
import sys
import time
import json
import shutil
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENES_DIR = os.path.join(BASE_DIR, "scenes")
CLIPS_DIR = os.path.join(SCENES_DIR, "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

# [name, duration, start_time_t0] matching audio timeline.json
SCENES = [
    ("s01", 19.0, 0.0),
    ("s02", 16.1, 19.0),
    ("s03", 23.6, 35.1),
    ("s04", 13.7, 58.7),
    ("s05", 24.0, 72.4),
    ("s06", 23.1, 96.4),
    ("s07", 17.8, 119.5),
    ("s08", 19.2, 137.3),
    ("s09", 6.7, 156.5),
    ("s10", 6.8, 163.2)
]

offsets_file = os.path.join(CLIPS_DIR, "offsets.json")
offsets = json.load(open(offsets_file, "r")) if os.path.exists(offsets_file) else {}

only = sys.argv[1:]

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    
    for name, dur, t0 in SCENES:
        if only and name not in only:
            continue
            
        scene_html = os.path.join(SCENES_DIR, f"{name}.html")
        file_url = f"file:///{scene_html.replace(os.sep, '/')}?t0={t0}&dur={dur}"
        
        tmp_dir = os.path.join(CLIPS_DIR, f"_raw_{name}")
        os.makedirs(tmp_dir, exist_ok=True)
        
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=tmp_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = ctx.new_page()
        created = time.time()
        
        page.goto(file_url)
        page.evaluate("() => document.fonts.ready")
        time.sleep(0.6)
        
        go_at = time.time()
        page.evaluate("() => window.go()")
        offsets[name] = round(go_at - created, 3)
        
        # Wait for scene animation duration
        time.sleep(dur + 0.5)
        
        ctx.close()
        
        # Rename output webm
        files = [f for f in os.listdir(tmp_dir) if f.endswith(".webm")]
        if files:
            src = os.path.join(tmp_dir, files[0])
            dst = os.path.join(CLIPS_DIR, f"{name}.webm")
            shutil.move(src, dst)
            print(f"Captured {name}.webm (offset {offsets[name]}s)")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        
        with open(offsets_file, "w", encoding="utf-8") as f:
            json.dump(offsets, f, indent=2)
            
    browser.close()

print("All scenes captured successfully.")
