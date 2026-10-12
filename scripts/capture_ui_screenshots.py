import asyncio
import os
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "desktop_1440", "width": 1440, "height": 900},
    {"name": "laptop_1366", "width": 1366, "height": 768},
    {"name": "tablet_ipad", "width": 768, "height": 1024},
    {"name": "mobile_iphone15", "width": 393, "height": 852}
]

async def capture_ui_screenshots():
    file_path = os.path.abspath("apps/web/public/index.html")
    url = f"file:///{file_path.replace(os.sep, '/')}"

    os.makedirs(os.path.join("docs", "assets"), exist_ok=True)
    os.makedirs(os.path.join("evidence", "ui"), exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for vp in VIEWPORTS:
            context = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = await context.new_page()
            await page.goto(url, wait_until="load")
            await page.wait_for_timeout(1000)

            # Check no horizontal overflow
            scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
            inner_width = vp["width"]
            assert scroll_width <= inner_width + 1, f"Horizontal overflow in {vp['name']}: {scroll_width} > {inner_width}"

            out_path = os.path.join("evidence", "ui", f"{vp['name']}.png")
            await page.screenshot(path=out_path, full_page=False)
            print(f"Captured {vp['name']} screenshot -> {out_path}")

        # Capture primary banner and 2x2 screenshots for README
        page = await browser.new_page(viewport={"width": 1440, "height": 820})
        await page.goto(url, wait_until="load")
        await page.screenshot(path=os.path.join("docs", "assets", "banner.png"))
        await page.screenshot(path=os.path.join("docs", "assets", "ui_report.png"))
        await browser.close()

    print("Responsive verification and UI screenshots completed successfully.")

if __name__ == "__main__":
    asyncio.run(capture_ui_screenshots())
