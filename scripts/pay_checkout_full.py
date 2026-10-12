"""
Complete full automated test checkout in Dodo Payments test mode.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def complete_test_payment(email="test_customer_1@example.com", name="Alex Morgan"):
    api_key = os.getenv("DODO_PAYMENTS_API_KEY")
    product_id = os.getenv("DODO_PRODUCT_ID")
    env = os.getenv("DODO_PAYMENTS_ENVIRONMENT", "test_mode")

    client = DodoPayments(bearer_token=api_key, environment=env)
    
    print(f"Creating checkout session for {email}...", flush=True)
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
    print(f"Session ID: {session.session_id}", flush=True)
    print(f"Checkout URL: {session.checkout_url}", flush=True)
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
        
        await page.goto(session.checkout_url, wait_until="load")
        
        # Click "Continue to Payment"
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Polling for Hyperswitch card frame...", flush=True)
        
        card_frame = None
        for i in range(20):
            await page.wait_for_timeout(1000)
            for f in page.frames:
                if "hs.dodopayments.com" in f.url:
                    try:
                        inps = await f.query_selector_all("input")
                        if len(inps) >= 3:
                            card_frame = f
                            break
                    except Exception:
                        pass
            if card_frame:
                print(f"Hyperswitch card frame ready at second {i+1}!", flush=True)
                break
                
        if not card_frame:
            raise RuntimeError("Hyperswitch card frame timed out!")
            
        # Give iframe height if needed
        await page.evaluate("""() => {
            const iframes = document.querySelectorAll('iframe');
            for (let f of iframes) {
                if (f.src && f.src.includes('hs.dodopayments.com')) {
                    f.style.height = '400px';
                    f.style.display = 'block';
                    f.style.visibility = 'visible';
                }
            }
        }""")
        
        # Fill inputs
        card_num_inp = card_frame.locator("input[placeholder*='1234']").first
        await card_num_inp.fill("4242424242424242", force=True)
        print("Filled card number.", flush=True)
        await page.wait_for_timeout(500)
        
        exp_inp = card_frame.locator("input[placeholder*='YY']").first
        await exp_inp.fill("0632", force=True)
        print("Filled expiry.", flush=True)
        await page.wait_for_timeout(500)
        
        cvc_inp = card_frame.locator("input[placeholder*='CVC']").first
        await cvc_inp.fill("123", force=True)
        print("Filled CVC.", flush=True)
        await page.wait_for_timeout(1500)
        
        await page.screenshot(path="evidence/discovery/card_filled.png")
        print("Saved card_filled.png screenshot.", flush=True)
        
        # Click "Pay now"
        pay_btn = page.locator("button#submit, button:has-text('Pay now')").first
        await page.evaluate("() => { const b = document.querySelector('button#submit'); if (b) b.removeAttribute('disabled'); }")
        await pay_btn.click(force=True)
        print("Clicked 'Pay now'! Waiting for confirmation...", flush=True)
        
        # Wait for redirect / confirmation
        await page.wait_for_timeout(10000)
        await page.screenshot(path="evidence/discovery/payment_success.png")
        print(f"Final Page URL: {page.url}", flush=True)
        
        await browser.close()
        
    print("Checking payment status in Dodo API...", flush=True)
    payments = client.payments.list(page_size=10)
    print(f"Total payments found: {len(payments.items)}")
    for pay in payments.items:
        print(f" Payment: id={pay.payment_id}, status={pay.status}, amount={pay.total_amount}, customer={pay.customer.email if pay.customer else None}")
        
    return payments.items

if __name__ == "__main__":
    asyncio.run(complete_test_payment())
