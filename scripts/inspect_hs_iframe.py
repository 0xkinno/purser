"""
Inspect content of dodo-checkout-iframe-payment
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def inspect_iframe_html():
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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(session.checkout_url, wait_until="networkidle")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(6000)
        
        for f in page.frames:
            if "hs.dodopayments.com" in f.url:
                print(f"Frame URL: {f.url}", flush=True)
                html = await f.content()
                print(f"Frame HTML length: {len(html)}", flush=True)
                print(f"Frame HTML snippet: {html[:500]}", flush=True)
                # Check elements inside frame
                all_elems = await f.query_selector_all("*")
                print(f"Elements in frame: {len(all_elems)}", flush=True)
                for el in all_elems[:20]:
                    tag = await el.evaluate("e => e.tagName")
                    cls = await el.get_attribute("class")
                    txt = (await el.inner_text()).strip()[:40] if tag != "BODY" else ""
                    print(f"  <{tag} class='{cls}'> {txt}", flush=True)
                    
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_iframe_html())
