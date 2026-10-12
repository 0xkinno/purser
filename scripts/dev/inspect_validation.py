"""
Inspect form validation state after clicking Continue to Payment.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def inspect_validation():
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
        await page.wait_for_timeout(2000)
        
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(2000)
        
        # Check for error text or invalid inputs
        invalid_inputs = await page.query_selector_all(":invalid")
        print(f"Invalid elements count: {len(invalid_inputs)}", flush=True)
        for el in invalid_inputs:
            nm = await el.get_attribute("name")
            ph = await el.get_attribute("placeholder")
            val_msg = await el.evaluate("e => e.validationMessage")
            print(f"  Invalid: name={nm}, placeholder={ph}, msg={val_msg}", flush=True)
            
        # Check text on page
        body_text = await page.inner_text("body")
        for line in body_text.splitlines():
            if any(k in line.lower() for k in ["error", "required", "please", "invalid"]):
                print(f"  Error message: {line.strip()}", flush=True)
                
        await page.screenshot(path="evidence/discovery/form_validation_check.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_validation())
