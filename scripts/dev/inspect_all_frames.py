"""
Find all nested frames and input fields in the payment step.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def inspect_nested_frames():
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
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(8000)
        
        # Recursively print all frames
        for i, f in enumerate(page.frames):
            print(f"Frame #{i}: name='{f.name}', url='{f.url}'", flush=True)
            # Find all inputs in frame
            try:
                inputs = await f.query_selector_all("input")
                print(f"  Inputs in Frame #{i}: {len(inputs)}", flush=True)
                for inp in inputs:
                    name = await inp.get_attribute("name")
                    ph = await inp.get_attribute("placeholder")
                    auto = await inp.get_attribute("autocomplete")
                    inp_id = await inp.get_attribute("id")
                    print(f"    Input: id={inp_id}, name={name}, placeholder={ph}, autocomplete={auto}", flush=True)
            except Exception as e:
                print(f"  Error inspecting frame #{i}: {e}", flush=True)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_nested_frames())
