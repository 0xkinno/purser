"""
Test clicking 'Pay now' on Dodo checkout.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def click_pay_now():
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
        
        await page.goto(session.checkout_url, wait_until="load")
        await page.wait_for_timeout(2000)
        
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'...", flush=True)
        await page.wait_for_timeout(5000)
        
        pay_btn = page.get_by_role("button", name="Pay now")
        print("Clicking 'Pay now'...", flush=True)
        await pay_btn.click()
        await page.wait_for_timeout(5000)
        
        print("Current URL after Pay now:", page.url, flush=True)
        await page.screenshot(path="evidence/discovery/after_pay_now.png")
        print("Saved after_pay_now.png", flush=True)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_pay_now())
