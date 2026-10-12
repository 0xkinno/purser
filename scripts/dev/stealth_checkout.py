"""
Run Playwright with stealth options to bypass Cloudflare challenge on Airwallex risk iframe.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def run_stealth_checkout():
    client = DodoPayments(bearer_token=os.getenv("DODO_PAYMENTS_API_KEY"), environment="test_mode")
    session = client.checkout_sessions.create(
        product_cart=[{"product_id": os.getenv("DODO_PRODUCT_ID"), "quantity": 1}],
        customer={"email": "stealth_buyer@example.com", "name": "Stealth Buyer"},
        billing_address={
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zipcode": "10005",
            "country": "US"
        }
    )
    print(f"Session URL: {session.checkout_url}", flush=True)
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        # Override navigator.webdriver
        await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
        
        await page.goto(session.checkout_url, wait_until="load")
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked Continue to Payment with stealth context. Waiting 10s...", flush=True)
        await page.wait_for_timeout(10000)
        
        await page.screenshot(path="evidence/discovery/stealth_step.png")
        print("Saved stealth_step.png", flush=True)
        
        # Check iframes and inputs
        for idx, f in enumerate(page.frames):
            inps = await f.query_selector_all("input")
            if inps:
                print(f"Frame #{idx} ('{f.name}') has {len(inps)} inputs. URL: {f.url[:60]}")
                for inp in inps:
                    print(f"   Input: placeholder={await inp.get_attribute('placeholder')}")
                    
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_stealth_checkout())
