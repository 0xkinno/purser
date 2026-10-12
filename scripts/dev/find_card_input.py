"""
Find any frame with input elements and print their details.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def find_card_input():
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
    print(f"Session: {session.session_id}", flush=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked Continue to Payment. Polling frames for card inputs...", flush=True)
        
        for second in range(15):
            await page.wait_for_timeout(1000)
            for idx, frame in enumerate(page.frames):
                try:
                    card_inps = await frame.query_selector_all("input")
                    if card_inps:
                        print(f"Second {second}: Frame #{idx} ('{frame.name}') has {len(card_inps)} inputs! URL: {frame.url[:80]}", flush=True)
                        for inp in card_inps:
                            ph = await inp.get_attribute("placeholder")
                            nm = await inp.get_attribute("name")
                            auto = await inp.get_attribute("autocomplete")
                            print(f"   Input: name={nm}, placeholder={ph}, autocomplete={auto}", flush=True)
                except Exception:
                    pass
                    
        await page.screenshot(path="evidence/discovery/card_poll_screenshot.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(find_card_input())
