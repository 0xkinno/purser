"""
Test automated checkout with Playwright for Dodo Payments test mode.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def create_and_pay():
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    
    # 1. Create checkout session
    print("Creating checkout session...")
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer={"email": "alice_test@example.com", "name": "Alice Cooper"},
        billing_address={
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zipcode": "10005",
            "country": "US"
        }
    )
    
    checkout_url = session.checkout_url
    print(f"Checkout URL: {checkout_url}")
    
    # 2. Use Playwright to complete checkout
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to checkout...")
        await page.goto(checkout_url, wait_until="networkidle")
        
        # Save screenshot for debugging if needed
        os.makedirs("evidence/discovery", exist_ok=True)
        await page.screenshot(path="evidence/discovery/checkout_page_initial.png")
        print("Saved initial screenshot.")
        
        # Wait for form elements
        # Check inputs on the page
        inputs = await page.query_selector_all("input")
        print(f"Found {len(inputs)} inputs on page.")
        for inp in inputs:
            name = await inp.get_attribute("name")
            placeholder = await inp.get_attribute("placeholder")
            inp_id = await inp.get_attribute("id")
            print(f"Input: name={name}, placeholder={placeholder}, id={inp_id}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(create_and_pay())
