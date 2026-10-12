"""
Navigate directly to the Hyperswitch checkout URL to see its console and rendered page.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def inspect_direct_hs_url():
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
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(3000)
        
        hs_url = None
        for f in page.frames:
            if "hs.dodopayments.com" in f.url:
                hs_url = f.url
                break
                
        print(f"HS URL: {hs_url}", flush=True)
        
        if hs_url:
            page2 = await browser.new_page()
            page2.on("console", lambda m: print(f"[Page2 Console {m.type}]: {m.text}", flush=True))
            page2.on("pageerror", lambda e: print(f"[Page2 Error]: {e}", flush=True))
            await page2.goto(hs_url, wait_until="load")
            await page2.wait_for_timeout(5000)
            await page2.screenshot(path="evidence/discovery/direct_hs_page.png")
            print("Saved direct_hs_page.png", flush=True)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_direct_hs_url())
