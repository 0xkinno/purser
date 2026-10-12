"""
Check what URL is returning 403.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def check_403():
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
        
        async def on_response(response):
            if response.status == 403:
                print(f"403 URL: {response.url}", flush=True)
                try:
                    text = await response.text()
                    print(f"403 Body: {text[:400]}", flush=True)
                except Exception as e:
                    print(f"Error reading 403 body: {e}", flush=True)

        page.on("response", on_response)
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(8000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_403())
