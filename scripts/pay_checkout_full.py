"""
Complete full automated test checkout in Dodo Payments test mode.
Robustly targets the iframe element directly and waits for inputs.
"""

import asyncio
import os
import dotenv
dotenv.load_dotenv()
from dodopayments import DodoPayments
from playwright.async_api import async_playwright

async def complete_test_payment(email="test_customer_funds@example.com", name="Alex Morgan"):
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
        
        await page.goto(session.checkout_url, wait_until="networkidle")
        
        btn = page.get_by_role("button", name="Continue to Payment")
        await btn.click()
        print("Clicked 'Continue to Payment'. Waiting for card iframe element...", flush=True)
        
        # Wait for iframe element in DOM
        await page.wait_for_selector("iframe#dodo-checkout-iframe-payment", state="attached", timeout=30000)
        
        # Ensure iframe is visible and has height
        await page.evaluate("""() => {
            const f = document.querySelector('iframe#dodo-checkout-iframe-payment');
            if (f) {
                f.style.height = '450px';
                f.style.display = 'block';
                f.style.visibility = 'visible';
            }
        }""")
        
        frame_element = await page.query_selector("iframe#dodo-checkout-iframe-payment")
        card_frame = await frame_element.content_frame()
        
        print("Waiting for card input in iframe...", flush=True)
        # Poll inside card frame
        card_inp = None
        for i in range(25):
            await page.wait_for_timeout(1000)
            try:
                card_inp = await card_frame.wait_for_selector("input[placeholder*='1234']", timeout=1000)
                if card_inp:
                    print(f"Found card input at second {i+1}!", flush=True)
                    break
            except Exception:
                pass
                
        if not card_inp:
            raise RuntimeError("Card input was not found in iframe!")
            
        await card_inp.fill("4242424242424242", force=True)
        print("Filled card number.", flush=True)
        await page.wait_for_timeout(500)
        
        exp_inp = await card_frame.wait_for_selector("input[placeholder*='YY']", timeout=3000)
        await exp_inp.fill("0632", force=True)
        print("Filled expiry.", flush=True)
        await page.wait_for_timeout(500)
        
        cvc_inp = await card_frame.wait_for_selector("input[placeholder*='CVC']", timeout=3000)
        await cvc_inp.fill("123", force=True)
        print("Filled CVC.", flush=True)
        await page.wait_for_timeout(1500)
        
        # Enable and click submit
        await page.evaluate("() => { const b = document.querySelector('button#submit'); if (b) b.removeAttribute('disabled'); }")
        pay_btn = page.locator("button#submit, button:has-text('Pay now')").first
        await pay_btn.click(force=True)
        print("Clicked 'Pay now'! Waiting for confirmation...", flush=True)
        
        await page.wait_for_timeout(10000)
        print(f"Final Page URL: {page.url}", flush=True)
        await browser.close()
        
    print("Checking payment status in Dodo API...", flush=True)
    payments = client.payments.list(page_size=5)
    for pay in payments.items:
        print(f" Payment: id={pay.payment_id}, status={pay.status}, amount={pay.total_amount}")
        
    return payments.items

if __name__ == "__main__":
    asyncio.run(complete_test_payment())
