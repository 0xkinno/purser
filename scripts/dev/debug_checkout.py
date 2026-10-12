"""
Capture console and network logs from Dodo checkout.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def debug_checkout_errors():
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
    
    print(f"Checkout URL: {session.checkout_url}", flush=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"Browser Console [{msg.type}]: {msg.text}", flush=True))
        page.on("pageerror", lambda err: print(f"Page Error: {err}", flush=True))
        page.on("response", lambda r: print(f"HTTP {r.status} {r.url[:70]}", flush=True) if r.status >= 400 else None)
        
        await page.goto(session.checkout_url, wait_until="networkidle")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Waiting 8s...", flush=True)
        await page.wait_for_timeout(8000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_checkout_errors())
