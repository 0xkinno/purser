"""
Captures real app video footage from http://localhost:3000 using Python Playwright.
Saves .webm footage into video/scenes/assets/.
"""

import os
import shutil
import time
from playwright.sync_api import sync_playwright

ASSETS_DIR = os.path.abspath("video/scenes/assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
BASE_URL = "http://localhost:3000"

def capture_clip(name: str, duration_sec: float, run_actions):
    raw_dir = os.path.join(ASSETS_DIR, f"_raw_{name}")
    os.makedirs(raw_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=raw_dir,
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        # Hide scrollbars
        page.add_style_tag(content="::-webkit-scrollbar { display: none; }")
        
        try:
            run_actions(page)
            time.sleep(duration_sec)
        except Exception as e:
            print(f"[{name}] Exception during capture:", e)
        finally:
            context.close()
            browser.close()
            
    # Find generated webm
    files = [f for f in os.listdir(raw_dir) if f.endswith(".webm")]
    if files:
        src = os.path.join(raw_dir, files[0])
        dst = os.path.join(ASSETS_DIR, f"{name}.webm")
        shutil.move(src, dst)
        print(f"Captured {dst}")
    shutil.rmtree(raw_dir, ignore_errors=True)

def action_w1(page):
    page.goto(BASE_URL, wait_until="networkidle")
    time.sleep(1.0)
    page.evaluate("window.scrollBy({ top: 350, behavior: 'smooth' })")
    time.sleep(2.0)
    page.evaluate("window.scrollBy({ top: 500, behavior: 'smooth' })")

def action_w3(page):
    page.goto(f"{BASE_URL}/app", wait_until="networkidle")
    time.sleep(1.0)
    page.evaluate("window.scrollBy({ top: 200, behavior: 'smooth' })")
    time.sleep(1.5)
    page.evaluate("window.scrollBy({ top: 250, behavior: 'smooth' })")

def action_w8(page):
    page.goto(f"{BASE_URL}/verify", wait_until="networkidle")
    time.sleep(1.0)
    # Click Load Sample
    load_btn = page.locator("button", has_text="Load Sample")
    if load_btn.count() > 0:
        load_btn.first.click()
        time.sleep(1.0)
    # Click Verify Batch
    verify_btn = page.locator("button", has_text="Verify Batch Manifest")
    if verify_btn.count() > 0:
        verify_btn.first.click()
        time.sleep(1.5)

if __name__ == "__main__":
    print("Capturing W1 (Landing)...")
    capture_clip("w1_landing", 6.0, action_w1)
    
    print("Capturing W3 (The Report)...")
    capture_clip("w3_report", 8.0, action_w3)
    
    print("Capturing W8 (Offline Verifier)...")
    capture_clip("w8_verify", 7.0, action_w8)
    
    print("All app clips captured.")
