"""
Automated payment submission with Playwright for Dodo Payments test mode.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def submit_test_payment(email="alice_test@example.com", name="Alice Cooper"):
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": product_id, "quantity": 1}],
        customer={"email": email, "name": name},
        billing_address={
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zipcode": "10005",
            "country": "US"
        }
    )
    
    print(f"Created checkout session: {session.session_id}")
    print(f"URL: {session.checkout_url}", flush=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(session.checkout_url, wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Click "Continue to Payment"
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'...", flush=True)
        
        # Wait for iframe to load
        iframe_element = await page.wait_for_selector("iframe[name='dodo-checkout-iframe-payment']", timeout=15000)
        frame = await iframe_element.content_frame()
        print("Payment iframe attached. Waiting for inputs inside iframe...", flush=True)
        await page.wait_for_timeout(3000)
        
        # Look inside iframe
        inputs = await frame.query_selector_all("input")
        print(f"Found {len(inputs)} inputs inside iframe:", flush=True)
        for inp in inputs:
            p_holder = await inp.get_attribute("placeholder")
            nm = await inp.get_attribute("name")
            inp_id = await inp.get_attribute("id")
            inp_type = await inp.get_attribute("type")
            print(f"  Iframe input: name={nm}, placeholder={p_holder}, id={inp_id}, type={inp_type}", flush=True)
            
        await page.screenshot(path="evidence/discovery/checkout_iframe_loaded.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(submit_test_payment())
