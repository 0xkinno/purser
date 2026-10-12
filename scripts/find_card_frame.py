"""
Automate checkout payment in Dodo test mode via Playwright frame_locator.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def pay_test_session():
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
        
        # Click Continue to Payment
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Waiting for navigation/networkidle...", flush=True)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        print("Frames present:", [f.name for f in page.frames], flush=True)
        
        # Locate the card iframe
        # The frame might be identified by name or by URL containing 'checkout.html'
        card_frame = None
        for f in page.frames:
            if "checkout.html" in f.url or "dodo-checkout-iframe" in f.name:
                card_frame = f
                break
                
        if card_frame:
            print(f"Found card frame: {card_frame.name} url: {card_frame.url[:60]}...", flush=True)
            # List inputs in card frame
            inputs = await card_frame.query_selector_all("input")
            print(f"Inputs in card frame: {len(inputs)}", flush=True)
            for inp in inputs:
                p_holder = await inp.get_attribute("placeholder")
                nm = await inp.get_attribute("name")
                print(f"  Input: name={nm}, placeholder={p_holder}", flush=True)
        else:
            print("Card frame not found directly. Checking all frames' HTML length...", flush=True)
            for idx, f in enumerate(page.frames):
                print(f"Frame {idx}: name='{f.name}', url='{f.url[:60]}'", flush=True)
                
        await page.screenshot(path="evidence/discovery/checkout_step3.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(pay_test_session())
