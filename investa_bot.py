import os
import asyncio
import random
from playwright.async_api import async_playwright

# Kukunin ang login sa GitHub Secrets para ligtas
INVESTA_USERNAME = os.environ.get("INVESTA_USERNAME")
INVESTA_PASSWORD = os.environ.get("INVESTA_PASSWORD")
STOCK_TICKER = "MER" 

async def run_trading_bot():
    if not INVESTA_USERNAME or not INVESTA_PASSWORD:
        print("❌ Error: Walang nakaset na Username o Password sa GitHub Secrets!")
        return

    async with async_playwright() as p:
        # headless=True dahil tatakbo ito sa background ng GitHub server
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("🤖 Bot: Binubuksan ang Investagrams...")
        await page.goto("https://www.investagrams.com/Login")

        # 1. Login Process
        await page.fill("input[name='Username']", INVESTA_USERNAME)
        await page.fill("input[name='Password']", INVESTA_PASSWORD)
        await page.click("button:has-text('Login')")
        await page.wait_for_timeout(5000)
        print("✅ Bot: Naka-log in na!")

        # 2. Pumunta sa Trading Page
        await page.goto(f"https://www.investagrams.com/Trading/Virtual/{STOCK_TICKER}")
        await page.wait_for_timeout(5000)

        # 3. I-scrape ang live price
        try:
            price_element = await page.locator(".stock-current-price").inner_text()
            live_price = float(price_element.replace(",", ""))
            print(f"📈 TOTOONG PRESYO NG {STOCK_TICKER}: ₱{live_price}")
        except Exception as e:
            print("❌ Error: Hindi makuha ang presyo sa screen.")
            await browser.close()
            return

        # 4. Ang Strategy Sim (Dito papasok yung bias ng calculator mo)
        bias_direction = random.choice(["BULLISH", "BEARISH"]) 
        print(f"📊 Signal Matrix Result: {bias_direction}")

        # 5. Execution
        if bias_direction == "BULLISH":
            print("🚀 SIGNAL BUY: Nag-ki-click na sa Virtual Trade...")
            await page.click("button:has-text('BUY')")
            await page.wait_for_timeout(1000)
            await page.fill("input[name='Shares']", "100")
            await page.fill("input[name='Price']", str(live_price))
            # I-uncomment ito kapag 100% ka na para mag-confirm ang order:
            # await page.click("button:has-text('Confirm Buy')")
            print("🎯 Order Sent!")
        else:
            print("⏳ SIGNAL BEARISH/HOLD: Walang trade na gagawin.")

        await browser.close()

asyncio.run(run_trading_bot())
