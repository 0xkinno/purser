"""
Dump all elements with positions on the payment step.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def dump_elements():
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
        await page.wait_for_timeout(4000)
        
        # Check every iframe tag on page
        iframes = await page.query_selector_all("iframe")
        print(f"Iframe elements found on top page: {len(iframes)}", flush=True)
        for idx, ifr in enumerate(iframes):
            src = await ifr.get_attribute("src")
            name = await ifr.get_attribute("name")
            style = await ifr.get_attribute("style")
            bb = await ifr.bounding_box()
            print(f"Iframe {idx}: name='{name}', src='{src[:70]}', box={bb}", flush=True)
            
        # Check buttons
        buttons = await page.query_selector_all("button")
        for b in buttons:
            txt = (await b.inner_text()).strip()
            bb = await b.bounding_box()
            vis = await b.is_visible()
            en = await b.is_enabled()
            print(f"Button: text='{txt}', box={bb}, visible={vis}, enabled={en}", flush=True)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_elements())
