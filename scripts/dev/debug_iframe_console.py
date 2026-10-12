"""
Capture all console messages from all frames during checkout.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def debug_iframe_console():
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer={"email": "alice_buyer@example.com", "name": "Alice Buyer"},
        billing_address={
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zipcode": "10005",
            "country": "US"
        }
    )
    
    async with async_playwright() as p:
        # Launch with slow_mo and arguments
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--allow-running-insecure-content"]
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        # Log all console events from context
        context.on("page", lambda p: p.on("console", lambda msg: print(f"[{p.url[:30]}] Console: {msg.text}", flush=True)))
        page.on("console", lambda msg: print(f"[TopPage] Console: {msg.text}", flush=True))
        page.on("pageerror", lambda err: print(f"[TopPage] Error: {err}", flush=True))
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked Continue to Payment, waiting 10s...", flush=True)
        await page.wait_for_timeout(10000)
        
        # Check all frames again
        for f in page.frames:
            if "hs.dodopayments.com" in f.url:
                print("Checking HS frame elements...")
                app_div = await f.query_selector("#app")
                if app_div:
                    inner = await app_div.inner_html()
                    print(f"app_div innerHTML length: {len(inner)}, content: {inner[:300]}")
                    
        await page.screenshot(path="evidence/discovery/debug_iframe.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_iframe_console())
