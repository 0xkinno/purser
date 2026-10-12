"""
Automated checkout completion with Playwright for Dodo Payments test mode.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def complete_test_checkout(customer_email="test_buyer_1@example.com", customer_name="Alice Smith"):
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    
    print(f"Creating checkout session for {customer_email}...", flush=True)
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer={"email": customer_email, "name": customer_name},
        billing_address={
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zipcode": "10005",
            "country": "US"
        }
    )
    
    checkout_url = session.checkout_url
    print(f"Checkout URL: {checkout_url}", flush=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(checkout_url, wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # Check buttons
        buttons = await page.query_selector_all("button")
        print(f"Found {len(buttons)} buttons:", flush=True)
        for b in buttons:
            txt = (await b.inner_text()).strip()
            print(f" - Button: '{txt}'", flush=True)
            
        # Check iframes
        frames = page.frames
        print(f"Found {len(frames)} frames.", flush=True)
        for idx, f in enumerate(frames):
            print(f" Frame {idx}: name='{f.name}', url='{f.url}'", flush=True)
            
        await page.screenshot(path="evidence/discovery/checkout_step1.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(complete_test_checkout())
