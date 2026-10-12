"""
Wait for Hyperswitch SDK to load card elements and inspect.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def wait_for_card_elements():
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
        
        await page.goto(session.checkout_url, wait_until="networkidle")
        
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Waiting 10s for Hyperswitch SDK to load...", flush=True)
        await page.wait_for_timeout(10000)
        
        print("Frames present after 10s:")
        for idx, f in enumerate(page.frames):
            print(f"  Frame {idx}: name='{f.name}', url='{f.url[:80]}'")
            inputs = await f.query_selector_all("input")
            if inputs:
                print(f"    Inputs in Frame {idx}: {len(inputs)}")
                for inp in inputs:
                    ph = await inp.get_attribute("placeholder")
                    nm = await inp.get_attribute("name")
                    inp_id = await inp.get_attribute("id")
                    print(f"      - name={nm}, placeholder={ph}, id={inp_id}")
                    
        await page.screenshot(path="evidence/discovery/checkout_step4_10s.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(wait_for_card_elements())
