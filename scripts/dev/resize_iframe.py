"""
Set iframe height and check if elements become visible.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def resize_iframe():
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
        
        # Resize iframe 0
        await page.evaluate("""() => {
            const iframes = document.querySelectorAll('iframe');
            for (let f of iframes) {
                if (f.src && f.src.includes('hs.dodopayments.com')) {
                    f.style.height = '600px';
                    f.style.display = 'block';
                    f.style.visibility = 'visible';
                }
            }
        }""")
        
        await page.wait_for_timeout(3000)
        await page.screenshot(path="evidence/discovery/resized_iframe.png")
        print("Saved resized_iframe.png", flush=True)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(resize_iframe())
