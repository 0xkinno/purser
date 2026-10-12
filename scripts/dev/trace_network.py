"""
Log every single network request and response during checkout.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def trace_all_network():
    client = DodoPayments(bearer_token=os.getenv("DODO_PAYMENTS_API_KEY"), environment="test_mode")
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": os.getenv("DODO_PRODUCT_ID"), "quantity": 1}],
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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("requestfailed", lambda req: print(f"REQ FAILED: {req.method} {req.url} - {req.failure}", flush=True))
        page.on("response", lambda res: print(f"RES {res.status}: {res.url[:80]}", flush=True) if res.status >= 300 else None)
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked Continue to Payment. Waiting 12s...", flush=True)
        await page.wait_for_timeout(12000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(trace_all_network())
