"""
Test clicking the Test Card section on Dodo checkout.
"""

import asyncio
import os
from dotenv import load_dotenv
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

load_dotenv()

async def inspect_test_card_section():
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
        
        # Click Continue to Payment
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        await page.wait_for_timeout(3000)
        
        # Click "Test Card"
        test_card_section = page.get_by_text("Test Card", exact=False)
        print("Clicking 'Test Card'...", flush=True)
        await test_card_section.first.click()
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path="evidence/discovery/test_card_expanded.png")
        print("Saved test_card_expanded.png", flush=True)
        
        # Look for buttons or text inside test card section
        text = await page.inner_text("body")
        for line in text.splitlines():
            if any(k in line.lower() for k in ["card", "success", "visa", "mastercard", "fail", "4242"]):
                print(f"  Line: {line.strip()}", flush=True)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_test_card_section())
