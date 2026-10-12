"""
Script to advance past 'Continue to Payment' and inspect card inputs.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def inspect_payment_step():
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer={"email": "alice_test@example.com", "name": "Alice Smith"},
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
        await page.wait_for_timeout(1000)
        
        # Click "Continue to Payment"
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Waiting for payment form...", flush=True)
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path="evidence/discovery/checkout_step2.png")
        print("Saved step2 screenshot.", flush=True)
        
        # Check frames and inputs
        for idx, f in enumerate(page.frames):
            print(f"Frame {idx}: name='{f.name}', url='{f.url}'", flush=True)
            inputs = await f.query_selector_all("input")
            for inp in inputs:
                placeholder = await inp.get_attribute("placeholder")
                name = await inp.get_attribute("name")
                inp_type = await inp.get_attribute("type")
                print(f"  Frame {idx} Input: name={name}, placeholder={placeholder}, type={inp_type}", flush=True)
                
        buttons = await page.query_selector_all("button")
        for b in buttons:
            txt = (await b.inner_text()).strip()
            if txt:
                print(f"Page button: '{txt}'", flush=True)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_payment_step())
